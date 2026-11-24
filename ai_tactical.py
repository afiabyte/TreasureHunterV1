"""
GeminiTacticalAI: Non-blocking asynchronous AI coordinator powered by Google Gemini.

This module coordinates tactical decision-making using the google-genai SDK
with gemini-3.8-flash and ThinkingConfig(thinking_budget=0) for ultra-low-latency
inference. All Hunter pursuit decisions, flanking tactics, and player escape guidance
are derived directly from structured JSON outputs.

Per the architectural guidelines:
- Strictly NO A* or classical graph-search pathfinding algorithms are used.
- Background worker threads (daemon=True) prevent Pygame frame drops and keep 60 FPS intact.
- Thread-safe synchronization is enforced via threading.Lock.
- A lightweight greedy Manhattan-distance fallback is triggered ONLY if the API key
  is missing or an unexpected network timeout occurs.
"""

import os
import time
import json
import logging
import threading
from typing import List, Tuple, Dict, Any, Optional
# Pydantic schema imports
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def model_dump(self):
            return self.__dict__
    def Field(*args, **kwargs):
        return None

# google-genai SDK imports
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


logger = logging.getLogger(__name__)


class TacticalDecision(BaseModel):
    """
    Structured Pydantic schema for Gemini 3.8 Flash responses.
    Guarantees strict JSON schema compliance from the model.
    """
    hunter_moves: List[str] = Field(
        description="Next valid cardinal move (UP, DOWN, LEFT, RIGHT, STAY) for each active hunter in order."
    )
    recommended_path: List[List[int]] = Field(
        description="Next 3 safe grid coordinates [row, col] guiding player to Key or Exit while evading sightlines."
    )
    commander_order: str = Field(
        description="A tense, tactical commander transmission under 12 words."
    )


class GeminiTacticalAI:
    """
    Asynchronous Tactical AI manager handling non-blocking Gemini API calls,
    latency tracking, thread safety, and emergency greedy fallbacks.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the Gemini Tactical AI coordinator.

        Args:
            api_key: Optional Google Gemini API key. If omitted, checks GEMINI_API_KEY env var
                     or reads from local .env if available.
        """
        # Resolve API Key from argument, environment, or .env file
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            self.api_key = self._load_key_from_env_file()

        # Thread synchronization locks
        self._lock = threading.Lock()
        self._is_worker_busy = False

        # Status and telemetry
        self.latency_ms: int = 0
        self.ai_status: str = "INITIALIZING"
        self.is_gemini_active: bool = False
        self.model_name: str = "gemini-3.6-flash"
        self.candidate_models: List[str] = [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-flash-latest",
            "gemini-3.7-flash",
            "gemini-3.8-flash",
        ]

        # Latest cached decision
        self.latest_decision: Dict[str, Any] = {
            "hunter_moves": [],
            "recommended_path": [],
            "commander_order": "System online. Standing by for tactical telemetry."
        }

        # Initialize the google-genai Client if possible
        self.client: Optional[Any] = None
        self._init_client()

    def _load_key_from_env_file(self) -> Optional[str]:
        """
        Attempt to read GEMINI_API_KEY from a local .env file if present.
        Avoids external dependency on python-dotenv.
        """
        env_paths = [".env", os.path.join(os.path.dirname(__file__), ".env")]
        for p in env_paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("GEMINI_API_KEY="):
                                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                                if key:
                                    os.environ["GEMINI_API_KEY"] = key
                                    return key
                except Exception:
                    pass
        return None

    def _init_client(self) -> None:
        """
        Initialize the google.genai Client with the configured API key.
        """
        if not GENAI_AVAILABLE:
            self.ai_status = "OFFLINE (SDK Missing)"
            self.is_gemini_active = False
            return

        if not self.api_key:
            self.ai_status = "OFFLINE (No API Key)"
            self.is_gemini_active = False
            return

        try:
            # Instantiate google-genai client
            self.client = genai.Client(api_key=self.api_key)
            self.ai_status = f"ONLINE [{self.model_name}]"
            self.is_gemini_active = True
        except Exception as e:
            logger.warning(f"Failed to initialize google-genai Client: {e}")
            self.ai_status = f"OFFLINE ({type(e).__name__})"
            self.is_gemini_active = False

    def set_api_key(self, key: str) -> bool:
        """
        Dynamically update or set the Gemini API key at runtime.

        Args:
            key: New API key string.

        Returns:
            True if initialization succeeded, False otherwise.
        """
        with self._lock:
            self.api_key = key.strip()
            if self.api_key:
                os.environ["GEMINI_API_KEY"] = self.api_key
            self._init_client()
            return self.is_gemini_active

    def request_tactical_decision(
        self,
        grid_size: int,
        player_pos: Tuple[int, int],
        hunter_positions: List[Tuple[int, int]],
        hunter_facings: List[Tuple[int, int]],
        wall_positions: List[Tuple[int, int]],
        key_pos: Tuple[int, int],
        has_key: bool,
        exit_pos: Tuple[int, int],
        force_sync_fallback: bool = False
    ) -> None:
        """
        Initiate an asynchronous background tactical calculation.
        Spawns a daemon thread calling gemini-3.8-flash without blocking the main 60 FPS loop.

        Args:
            grid_size: Dimension N of the N x N grid.
            player_pos: Current player (row, col).
            hunter_positions: List of active hunter (row, col) coordinates.
            hunter_facings: Directional facing vector (dr, dc) for each hunter.
            wall_positions: List of active obstacle (row, col) coordinates.
            key_pos: Golden Key (row, col).
            has_key: True if player has acquired the Key.
            exit_pos: Extraction portal (row, col).
            force_sync_fallback: If True, executes fallback immediately.
        """
        with self._lock:
            if self._is_worker_busy:
                # A request is already in-flight; avoid stacking background threads
                return
            self._is_worker_busy = True

        # If Gemini is disabled or unconfigured, execute fallback on worker thread
        target_func = self._run_gemini_worker if (self.is_gemini_active and not force_sync_fallback) else self._run_fallback_worker

        thread = threading.Thread(
            target=target_func,
            args=(grid_size, player_pos, hunter_positions, hunter_facings, wall_positions, key_pos, has_key, exit_pos),
            daemon=True
        )
        thread.start()

    def _run_gemini_worker(
        self,
        grid_size: int,
        player_pos: Tuple[int, int],
        hunter_positions: List[Tuple[int, int]],
        hunter_facings: List[Tuple[int, int]],
        wall_positions: List[Tuple[int, int]],
        key_pos: Tuple[int, int],
        has_key: bool,
        exit_pos: Tuple[int, int]
    ) -> None:
        """
        Background worker thread executing the Gemini 2.5 Flash API call.
        Uses response_mime_type="application/json" and ThinkingConfig(thinking_budget=0).
        """
        t_start = time.perf_counter()
        success = False

        try:
            # Build tactical system prompt and context
            target_name = "Exit Portal" if has_key else "Golden Key"
            target_coords = list(exit_pos) if has_key else list(key_pos)

            prompt = f"""
You are the Tactical Neural Core for an evasion simulation on an {grid_size}x{grid_size} grid (0-indexed [row, col]).
Current Grid State:
- Player position: {list(player_pos)}
- Hunter positions: {[list(hp) for hp in hunter_positions]}
- Hunter facing vectors [dr, dc]: {[list(hf) for hf in hunter_facings]}
- Wall positions: {[list(w) for w in wall_positions]}
- Key position: {list(key_pos)}
- Player has key: {has_key}
- Exit position: {list(exit_pos)}
- Current Player Target: {target_name} at {target_coords}

Tactical Directive:
1. hunter_moves: Next valid cardinal move (UP, DOWN, LEFT, RIGHT, STAY) for each active hunter to coordinate flanking and interception.
   - UP: [-1, 0], DOWN: [1, 0], LEFT: [0, -1], RIGHT: [0, 1], STAY: [0, 0]
   - Hunters CANNOT move through walls or exit grid [0, {grid_size-1}].
   - Coordinate flanking: one hunter pursues directly while others intercept potential escape corridors.
2. recommended_path: List of the next 3 safe consecutive grid coordinates [row, col] guiding the player toward the {target_name}.
   - The path must avoid Hunter vision cones (line-of-sight based on facing vector) and exploit blind spots behind Hunters.
   - Must avoid walls and stay within bounds.
3. commander_order: A tense tactical commander transmission strictly under 12 words.
"""

            # Configure ultra-low-latency generation with thinking_budget=0 and AFC disabled to suppress warning
            afc_config = (
                types.AutomaticFunctionCallingConfig(disable=True)
                if hasattr(types, "AutomaticFunctionCallingConfig")
                else None
            )
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TacticalDecision,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                temperature=0.2,
                automatic_function_calling=afc_config,
            )

            # Direct SDK call to Gemini model with dynamic candidate fallback
            response = None
            last_err = None
            models_to_try = [self.model_name] + [m for m in self.candidate_models if m != self.model_name]

            for cand_model in models_to_try:
                try:
                    response = self.client.models.generate_content(
                        model=cand_model,
                        contents=prompt,
                        config=config,
                    )
                    if cand_model != self.model_name:
                        logger.info(f"Switched active Gemini model from {self.model_name} to {cand_model}")
                        self.model_name = cand_model
                    break
                except Exception as ex:
                    last_err = ex
                    err_str = str(ex).lower()
                    # Check for recoverable model errors: 404 (Not Found/Deprecated),
                    # 503 (Unavailable / High Demand), 429 (Resource Exhausted / Rate Limit),
                    # 500 (Internal Server Error)
                    is_recoverable = any(k in err_str for k in [
                        "404", "not_found", "not found",
                        "503", "unavailable", "high demand", "overloaded",
                        "504", "deadline", "timed out",
                        "429", "resource_exhausted", "quota", "rate limit",
                        "500", "internal", "service unavailable"
                    ])
                    if is_recoverable:
                        logger.warning(f"Model {cand_model} failed with: {ex}. Trying next candidate model...")
                        continue
                    else:
                        raise ex

            if response is None:
                if last_err:
                    raise last_err
                raise RuntimeError("No candidate Gemini model succeeded.")

            # Parse structured JSON output
            raw_text = response.text or "{}"
            clean_text = raw_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            data = json.loads(clean_text)

            # Validate against Pydantic schema
            decision_obj = TacticalDecision(**data)
            elapsed_ms = int((time.perf_counter() - t_start) * 1000)

            with self._lock:
                self.latest_decision = decision_obj.model_dump()
                self.latency_ms = elapsed_ms
                self.ai_status = f"ONLINE ({elapsed_ms}ms)"
                success = True

        except Exception as e:
            err_msg = str(e)
            logger.warning(f"Gemini API worker encountered error: {err_msg}. Falling back to greedy.")
            # Trigger greedy Manhattan fallback on network failure or timeout
            fallback_res = self._compute_greedy_fallback(
                grid_size, player_pos, hunter_positions, wall_positions, key_pos, has_key, exit_pos
            )
            elapsed_ms = int((time.perf_counter() - t_start) * 1000)

            err_lower = err_msg.lower()
            if "503" in err_lower or "unavailable" in err_lower or "high demand" in err_lower:
                status_label = "FALLBACK (Server Busy - 503)"
            elif "429" in err_lower or "quota" in err_lower or "exhausted" in err_lower:
                status_label = "FALLBACK (Rate Limit - 429)"
            elif "404" in err_lower:
                status_label = "FALLBACK (Model Not Found)"
            else:
                status_label = "FALLBACK (Network Error)"

            with self._lock:
                self.latest_decision = fallback_res
                self.latency_ms = elapsed_ms
                self.ai_status = status_label

        finally:
            with self._lock:
                self._is_worker_busy = False

    def _run_fallback_worker(
        self,
        grid_size: int,
        player_pos: Tuple[int, int],
        hunter_positions: List[Tuple[int, int]],
        hunter_facings: List[Tuple[int, int]],
        wall_positions: List[Tuple[int, int]],
        key_pos: Tuple[int, int],
        has_key: bool,
        exit_pos: Tuple[int, int]
    ) -> None:
        """
        Background worker thread executing the greedy Manhattan fallback
        when Gemini API key is missing or disabled.
        """
        t_start = time.perf_counter()
        try:
            fallback_res = self._compute_greedy_fallback(
                grid_size, player_pos, hunter_positions, wall_positions, key_pos, has_key, exit_pos
            )
            elapsed_ms = int((time.perf_counter() - t_start) * 1000)

            with self._lock:
                self.latest_decision = fallback_res
                self.latency_ms = elapsed_ms
                self.ai_status = "FALLBACK (Greedy Offline)"
        finally:
            with self._lock:
                self._is_worker_busy = False

    def _compute_greedy_fallback(
        self,
        grid_size: int,
        player_pos: Tuple[int, int],
        hunter_positions: List[Tuple[int, int]],
        wall_positions: List[Tuple[int, int]],
        key_pos: Tuple[int, int],
        has_key: bool,
        exit_pos: Tuple[int, int]
    ) -> Dict[str, Any]:
        """
        Lightweight greedy Manhattan-distance fallback.
        Strictly does NOT use A* or classical graph search.
        Evaluates immediate cardinal neighbors only.

        Returns:
            Dictionary matching TacticalDecision structure.
        """
        wall_set = set(wall_positions)
        hunter_set = set(hunter_positions)
        pr, pc = player_pos
        target = exit_pos if has_key else key_pos
        tr, tc = target

        cardinals = [
            ("UP", (-1, 0)),
            ("DOWN", (1, 0)),
            ("LEFT", (0, -1)),
            ("RIGHT", (0, 1)),
        ]

        # 1. Greedy Hunter moves: minimize Manhattan distance to player
        hunter_moves = []
        for hr, hc in hunter_positions:
            best_move = "STAY"
            min_dist = abs(hr - pr) + abs(hc - pc)

            for move_name, (dr, dc) in cardinals:
                nr, nc = hr + dr, hc + dc
                # Check grid boundaries
                if 0 <= nr < grid_size and 0 <= nc < grid_size:
                    # Check walls and other hunter collisions
                    if (nr, nc) not in wall_set and ((nr, nc) not in hunter_set or (nr, nc) == (hr, hc)):
                        dist = abs(nr - pr) + abs(nc - pc)
                        if dist < min_dist:
                            min_dist = dist
                            best_move = move_name
            hunter_moves.append(best_move)

        # 2. Greedy Player safe path: next 3 safe steps toward target
        recommended_path = []
        curr_r, curr_c = pr, pc
        visited = {(curr_r, curr_c)}

        for _ in range(3):
            best_next = None
            best_score = float("inf")

            for _, (dr, dc) in cardinals:
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < grid_size and 0 <= nc < grid_size:
                    if (nr, nc) not in wall_set and (nr, nc) not in visited:
                        # Danger penalty if adjacent to any hunter
                        danger_penalty = 0
                        for hr, hc in hunter_positions:
                            h_dist = abs(nr - hr) + abs(nc - hc)
                            if h_dist <= 1:
                                danger_penalty += 100

                        dist_to_target = abs(nr - tr) + abs(nc - tc)
                        score = dist_to_target + danger_penalty

                        if score < best_score:
                            best_score = score
                            best_next = [nr, nc]

            if best_next:
                recommended_path.append(best_next)
                visited.add((best_next[0], best_next[1]))
                curr_r, curr_c = best_next[0], best_next[1]
            else:
                break

        # 3. Terse military commander order under 12 words
        if has_key:
            commander_order = "Key secured. Extraction portal open. Evade interceptors!"
        else:
            commander_order = "Locate golden cipher key. Maintain radar stealth."

        return {
            "hunter_moves": hunter_moves,
            "recommended_path": recommended_path,
            "commander_order": commander_order,
        }

    def get_latest_decision(self) -> Tuple[Dict[str, Any], int, str, bool]:
        """
        Thread-safe query for the most recent AI decision and performance telemetry.

        Returns:
            Tuple of:
            - latest_decision (dict)
            - latency_ms (int)
            - ai_status (str)
            - is_busy (bool)
        """
        with self._lock:
            return (
                dict(self.latest_decision),
                self.latency_ms,
                self.ai_status,
                self._is_worker_busy
            )
