"""
GameEngine: Core coordinator for Treasure Hunter tactical evasion simulation.

Manages:
- Game states: HOME, HOW_TO_PLAY, PLAYING, GAME_OVER.
- 60 FPS clock cycle with zero I/O blocking.
- Linear Interpolation (LERP) rendering math at speed = 0.28 for fluid entity movement.
- Input dispatching (WASD/Arrows, [H] hunter spawn, [B] barrier shift, [R] reset, ESC return).
- Non-blocking coordination with GeminiTacticalAI worker threads.
- SQLite match persistence via DatabaseManager.
- Procedural audio feedback integration via SoundManager.
"""

import sys
import time
from typing import Optional, Dict, Any, List, Tuple
import pygame

from database import DatabaseManager
from ai_tactical import GeminiTacticalAI
from environment import GridEnvironment
from ui_manager import UIManager
from sound_effects import SoundManager


# Game State Identifiers
STATE_SPLASH = "SPLASH"
STATE_LOGIN = "LOGIN"
STATE_HOME = "HOME"
STATE_HOW_TO_PLAY = "HOW_TO_PLAY"
STATE_PLAYING = "PLAYING"
STATE_PAUSED = "PAUSED"
STATE_GAME_OVER = "GAME_OVER"


class GameEngine:
    """
    Main Game Engine driving the 60 FPS event loop, state machine,
    rendering pipeline, and AI thread communication.
    """

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        """
        Initialize Pygame, display surfaces, sound mixer, and modular sub-components.

        Args:
            screen_width: Window width in pixels (default: 960).
            screen_height: Window height in pixels (default: 780).
        """
        # Initialize Pygame core modules
        pygame.init()
        pygame.display.set_caption("Treasure Hunter // Tactical Evasion")

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.is_running = True

        # State Machine Initialization (Begins with Splash Intro, then User Login)
        self.state = STATE_SPLASH
        self.return_state = STATE_HOME
        self.splash_timer: float = 0.0
        self.splash_duration: float = 2.5
        self.current_user: str = "afiabyte"
        self.user_stats: Optional[Dict[str, Any]] = None
        self.login_status: str = "AWAITING CREDENTIALS"
        self.recent_operatives: List[Dict[str, Any]] = []

        # Subsystem Managers (Clean zero-circular dependency architecture)
        self.db = DatabaseManager("dungeon_records.db")
        self.ai = GeminiTacticalAI()
        self.ui = UIManager(self.screen_width, self.screen_height)
        self.sound = SoundManager()

        # Query recent operatives from SQLite
        self.recent_operatives = self.db.get_recent_operatives(3)

        # Configurable Game Parameters (set from Home screen)
        self.selected_grid_size: int = 7
        self.selected_level: int = 2
        self.player_name: str = "afiabyte"

        # Active Environment Simulation
        self.env: Optional[GridEnvironment] = None

        # Standby Reconnaissance Phase (prevents game starting abruptly)
        self.standby_timer: float = 0.0

        # Game Over Status Tracking
        self.is_victory: bool = False
        self.is_new_best_record: bool = False
        self.best_victory_steps: Optional[int] = self.db.get_best_victory_steps()

        # Visual Grid Geometry Cache (origin_x, origin_y, cell_size)
        self.origin_x: float = 0.0
        self.origin_y: float = 0.0
        self.cell_size: float = 64.0

        # AI Dispatch Throttling & Telemetry
        self.ai_request_timer: float = 0.0
        self.ai_request_interval: float = 0.35  # Poll/refresh interval for AI guidance
        self.cached_recommended_path: List[List[int]] = []
        self.cached_commander_order: str = "Mission initialized. Commencing tactical evasion."
        self.cached_hunter_moves: List[str] = []

    def start_mission(self, grid_size: int, level: int, player_name: str) -> None:
        """
        Transition from HOME to PLAYING state.
        Instantiates a fresh GridEnvironment with zero memory leaks.

        Args:
            grid_size: Chosen N dimension (5, 7, 9, 11).
            level: Chosen difficulty tier (1: Recruit, 2: Tactical, 3: Nightmare).
            player_name: Operative callsign string.
        """
        self.selected_grid_size = grid_size
        self.selected_level = level
        self.player_name = player_name.strip() if player_name.strip() else "OPERATIVE-01"

        # Instantiate fresh procedural environment
        self.env = GridEnvironment(grid_size=self.selected_grid_size, level=self.selected_level)

        # Compute dynamic visual geometry to ensure grid scales above HUD
        self.origin_x, self.origin_y, self.cell_size = self.ui.compute_grid_geometry(self.selected_grid_size)

        # Synchronize pixel coordinates and snap entities into position
        self.env.sync_pixel_targets(self.origin_x, self.origin_y, self.cell_size)
        self.env.snap_visuals_to_targets()

        # Query all-time best score from SQLite for HUD display
        self.best_victory_steps = self.db.get_best_victory_steps()

        # Reset AI caches and timers
        self.cached_recommended_path = []
        self.cached_commander_order = "Objective: Infiltrate, acquire Key, evade Hunter drones."
        self.cached_hunter_moves = []
        self.ai_request_timer = 0.0

        # Standby Reconnaissance Phase (3.0s buffer so game never starts abruptly)
        self.standby_timer = 3.0

        # Transition state
        self.state = STATE_PLAYING

        # Dispatch immediate tactical query to background worker
        self._dispatch_ai_query()

    def _dispatch_ai_query(self) -> None:
        """
        Package the current N x N grid telemetry and dispatch a non-blocking
        asynchronous request to GeminiTacticalAI.
        """
        if not self.env:
            return

        hunter_positions = [h.pos for h in self.env.hunters]
        hunter_facings = [h.facing for h in self.env.hunters]
        wall_positions = list(self.env.walls)

        # Non-blocking async invocation via background worker thread
        self.ai.request_tactical_decision(
            grid_size=self.env.grid_size,
            player_pos=self.env.player_pos,
            hunter_positions=hunter_positions,
            hunter_facings=hunter_facings,
            wall_positions=wall_positions,
            key_pos=self.env.key_pos,
            has_key=self.env.has_key,
            exit_pos=self.env.exit_pos,
        )

    def _trigger_victory(self) -> None:
        """Handle mission victory state transition and database persistence."""
        self.is_victory = True
        self.sound.play_victory()

        # Save match result to SQLite on the basis of active operative
        steps_taken = self.env.steps if self.env else 0
        self.db.save_match_result(self.player_name, steps_taken, "VICTORY")
        self.user_stats = self.db.get_operative(self.player_name)

        # Evaluate if this run sets a new personal best record
        prev_best = self.best_victory_steps
        if prev_best is None or steps_taken < prev_best:
            self.is_new_best_record = True
            self.best_victory_steps = steps_taken
        else:
            self.is_new_best_record = False

        self.state = STATE_GAME_OVER

    def _trigger_defeat(self) -> None:
        """Handle mission defeat (hunter interception) and database persistence."""
        self.is_victory = False
        self.is_new_best_record = False
        self.sound.play_defeat()

        # Save match result to SQLite on the basis of active operative
        steps_taken = self.env.steps if self.env else 0
        self.db.save_match_result(self.player_name, steps_taken, "DEFEAT")
        self.user_stats = self.db.get_operative(self.player_name)

        self.state = STATE_GAME_OVER

    # =========================================================================
    # EVENT HANDLING & INPUT DISPATCHING
    # =========================================================================
    def handle_events(self) -> None:
        """Poll and handle all Pygame input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
                return

            if self.state == STATE_SPLASH:
                self._handle_splash_events(event)
            elif self.state == STATE_LOGIN:
                self._handle_login_events(event)
            elif self.state == STATE_HOME:
                self._handle_home_events(event)
            elif self.state == STATE_HOW_TO_PLAY:
                self._handle_how_to_play_events(event)
            elif self.state == STATE_PLAYING:
                self._handle_playing_events(event)
            elif self.state == STATE_PAUSED:
                self._handle_paused_events(event)
            elif self.state == STATE_GAME_OVER:
                self._handle_game_over_events(event)

    def _handle_splash_events(self, event: pygame.event.Event) -> None:
        """Handle inputs on the Splash Screen (Space/Enter/Click transitions to Login)."""
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            self.state = STATE_LOGIN
            self.ui.input_login_username.is_active = True
            self.recent_operatives = self.db.get_recent_operatives(3)

    def _handle_login_events(self, event: pygame.event.Event) -> None:
        """Handle inputs on the Operative Login Screen."""
        self.ui.input_login_username.handle_event(event)

        # 1. Check quick-select click on recent operatives in card
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            card_x = self.screen_width // 2 - 280
            card_y = 125
            if self.recent_operatives and len(self.recent_operatives) > 0:
                ry = card_y + 372
                for op in self.recent_operatives[:3]:
                    op_rect = pygame.Rect(card_x + 25, ry - 2, 500, 20)
                    if op_rect.collidepoint(mx, my):
                        self.ui.input_login_username.text = op["username"]
                        self.login_status = f"SELECTED: {op['username']}"
                        break
                    ry += 20

        # 2. Check Login Submit button or Enter Key
        do_login = False
        target_name = self.ui.input_login_username.text.strip()

        if self.ui.btn_login_submit.handle_event(event):
            do_login = True
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            do_login = True

        if do_login:
            if not target_name:
                target_name = "afiabyte"
            op = self.db.login_or_register_operative(target_name)
            self.current_user = op["username"]
            self.player_name = self.current_user
            self.ui.input_player_name.text = self.current_user
            self.user_stats = op
            self.best_victory_steps = self.db.get_best_victory_steps(self.current_user)
            self.sound.play_key()
            self.state = STATE_HOME
            return

        # 3. Check Guest Login Button
        if self.ui.btn_login_guest.handle_event(event):
            op = self.db.login_or_register_operative("GUEST-01")
            self.current_user = op["username"]
            self.player_name = self.current_user
            self.ui.input_player_name.text = self.current_user
            self.user_stats = op
            self.best_victory_steps = self.db.get_best_victory_steps(self.current_user)
            self.sound.play_key()
            self.state = STATE_HOME
            return

    def _handle_home_events(self, event: pygame.event.Event) -> None:
        """Handle inputs on the Home Screen."""
        # Text input field for player callsign
        self.ui.input_player_name.handle_event(event)

        # Switch User / Logout button returns to Login screen
        if self.ui.btn_logout.handle_event(event):
            self.recent_operatives = self.db.get_recent_operatives(3)
            self.login_status = f"SWITCHING FROM {self.current_user}"
            self.ui.input_login_username.is_active = True
            self.state = STATE_LOGIN
            return

        # Grid size selector buttons (5x5, 7x7 default, 9x9, 11x11)
        for btn in self.ui.grid_buttons:
            if btn.handle_event(event):
                for b in self.ui.grid_buttons:
                    b.is_selected = False
                btn.is_selected = True
                self.selected_grid_size = int(btn.tag)

        # Level selector buttons (1: Recruit, 2: Tactical, 3: Nightmare)
        for btn in self.ui.level_buttons:
            if btn.handle_event(event):
                for b in self.ui.level_buttons:
                    b.is_selected = False
                btn.is_selected = True
                self.selected_level = int(btn.tag)

        # "How to Play" button
        if self.ui.btn_how_to_play.handle_event(event):
            self.return_state = STATE_HOME
            self.state = STATE_HOW_TO_PLAY

        # "Start Mission" button
        if self.ui.btn_start_mission.handle_event(event):
            callsign = self.ui.input_player_name.text.strip()
            if not callsign:
                callsign = self.current_user
            self.start_mission(
                grid_size=self.selected_grid_size,
                level=self.selected_level,
                player_name=callsign,
            )

    def _handle_how_to_play_events(self, event: pygame.event.Event) -> None:
        """Handle inputs on the How to Play Screen."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = self.return_state
            return

        if self.ui.btn_back_to_menu.handle_event(event):
            self.state = self.return_state

    def _handle_playing_events(self, event: pygame.event.Event) -> None:
        """Handle in-game inputs during active mission."""
        if not self.env:
            return

        # Check Click on Top-Right Pause Button
        if self.ui.btn_pause.handle_event(event):
            self.state = STATE_PAUSED
            return

        if event.type == pygame.KEYDOWN:
            # P, ESC, or Pause key: Toggle tactical pause
            if event.key in (pygame.K_p, pygame.K_PAUSE, pygame.K_ESCAPE):
                self.state = STATE_PAUSED
                return

            # SPACE: Skip standby if active, or toggle pause
            if event.key == pygame.K_SPACE:
                if self.standby_timer > 0:
                    self.standby_timer = 0.0
                else:
                    self.state = STATE_PAUSED
                return

            # [R]: Reset mission with clean layout and fresh standby buffer
            if event.key == pygame.K_r:
                self.env.reset_environment()
                self.env.sync_pixel_targets(self.origin_x, self.origin_y, self.cell_size)
                self.env.snap_visuals_to_targets()
                self.standby_timer = 3.0
                self._dispatch_ai_query()
                return

            # [H]: Manually deploy a hunter drone reinforcement (up to 8 max)
            if event.key == pygame.K_h:
                if len(self.env.hunters) < 8:
                    spawned = self.env.spawn_hunter()
                    if spawned:
                        self.env.sync_pixel_targets(self.origin_x, self.origin_y, self.cell_size)
                        self.sound.play_spawn()
                        self._dispatch_ai_query()
                return

            # [B]: Manually trigger dynamic barrier shift
            if event.key == pygame.K_b:
                self.env.relocate_walls()
                self.sound.play_shift()
                self._dispatch_ai_query()
                return

            # Player Cardinal Movement (WASD / Arrow Keys)
            dr, dc = 0, 0
            if event.key in (pygame.K_w, pygame.K_UP):
                dr, dc = -1, 0
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                dr, dc = 1, 0
            elif event.key in (pygame.K_a, pygame.K_LEFT):
                dr, dc = 0, -1
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                dr, dc = 0, 1

            if dr != 0 or dc != 0:
                # If moving during standby, immediately commence active mission
                if self.standby_timer > 0:
                    self.standby_timer = 0.0

                was_key_secured = self.env.has_key
                moved = self.env.move_player(dr, dc)
                if moved:
                    self.sound.play_move()
                    # Play sound when Key is collected
                    if not was_key_secured and self.env.has_key:
                        self.sound.play_key()

                    # Update player target pixel center
                    self.env.sync_pixel_targets(self.origin_x, self.origin_y, self.cell_size)

                    # Check defeat (stepped directly onto a hunter)
                    if self.env.check_defeat():
                        self._trigger_defeat()
                        return

                    # Check victory (reached exit with key)
                    if self.env.check_victory():
                        self._trigger_victory()
                        return

                    # Trigger fresh AI decision request for the new position
                    self._dispatch_ai_query()

    def _handle_paused_events(self, event: pygame.event.Event) -> None:
        """Handle inputs while the game is in Tactical Pause state."""
        # Top-right button or Resume button resumes gameplay
        if self.ui.btn_pause.handle_event(event) or self.ui.btn_pause_resume.handle_event(event):
            self.state = STATE_PLAYING
            return

        if event.type == pygame.KEYDOWN and event.key in (pygame.K_p, pygame.K_ESCAPE, pygame.K_SPACE):
            self.state = STATE_PLAYING
            return

        # Restart sector
        if self.ui.btn_pause_restart.handle_event(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_r):
            self.start_mission(self.selected_grid_size, self.selected_level, self.player_name)
            return

        # Controls & Help
        if self.ui.btn_pause_help.handle_event(event):
            self.return_state = STATE_PAUSED
            self.state = STATE_HOW_TO_PLAY
            return

        # Return to Home Menu
        if self.ui.btn_pause_menu.handle_event(event):
            self.best_victory_steps = self.db.get_best_victory_steps()
            self.state = STATE_HOME
            return

    def _handle_game_over_events(self, event: pygame.event.Event) -> None:
        """Handle inputs on the Victory and Defeat overlays."""
        if self.is_victory:
            # Advance to Next Level (Seamless progression: Recruit -> Tactical -> Nightmare)
            if self.selected_level < 3 and self.ui.btn_next_level.handle_event(event):
                next_lvl = self.selected_level + 1
                self.selected_level = next_lvl
                # Update level button highlights on home screen
                for b in self.ui.level_buttons:
                    b.is_selected = (int(b.tag) == next_lvl)
                self.start_mission(self.selected_grid_size, next_lvl, self.player_name)
                return

            # Replay current level
            if self.ui.btn_victory_replay.handle_event(event):
                self.start_mission(self.selected_grid_size, self.selected_level, self.player_name)
                return

            # Return to Home Menu
            if self.ui.btn_victory_menu.handle_event(event):
                self.best_victory_steps = self.db.get_best_victory_steps()
                self.state = STATE_HOME
                return
        else:
            # Retry level on defeat
            if self.ui.btn_retry_level.handle_event(event):
                self.start_mission(self.selected_grid_size, self.selected_level, self.player_name)
                return

            # Return to Home Menu
            if self.ui.btn_defeat_menu.handle_event(event):
                self.best_victory_steps = self.db.get_best_victory_steps()
                self.state = STATE_HOME
                return

    # =========================================================================
    # SIMULATION UPDATE & LERP ANIMATION (60 FPS)
    # =========================================================================
    def update(self, dt: float) -> None:
        """
        Advance simulation timers, execute LERP coordinate updates,
        and synchronize with background AI decisions.

        Args:
            dt: Delta time elapsed since last frame in seconds.
        """
        self.ui.update(dt)

        if self.state == STATE_SPLASH:
            self.splash_timer += dt
            if self.splash_timer >= self.splash_duration:
                self.state = STATE_LOGIN
                self.ui.input_login_username.is_active = True
                self.recent_operatives = self.db.get_recent_operatives(3)
            return

        if self.state == STATE_LOGIN:
            return

        if self.state == STATE_PAUSED:
            # Complete simulation freeze while paused
            return

        if self.state == STATE_PLAYING and self.env:
            # Standby reconnaissance phase: allows player to inspect board before enemies move
            if self.standby_timer > 0:
                self.standby_timer = max(0.0, self.standby_timer - dt)
                # Keep LERP visual coordinates smoothly aligned
                self.env.update_lerp_all(speed=0.28)
                return

            # 1. Update Environment Timers (Dynamic walls, Hunter spawn, Hunter move)
            wall_relocated, hunter_spawned, hunter_move_triggered = self.env.update_timers(dt)

            if wall_relocated:
                self.sound.play_shift()
                self._dispatch_ai_query()

            if hunter_spawned:
                self.sound.play_spawn()
                self.env.sync_pixel_targets(self.origin_x, self.origin_y, self.cell_size)
                self._dispatch_ai_query()

            # 2. Fetch Latest Asynchronous AI Decision (Non-blocking)
            decision, latency_ms, status_text, is_busy = self.ai.get_latest_decision()
            if decision.get("recommended_path"):
                self.cached_recommended_path = decision["recommended_path"]
            if decision.get("commander_order"):
                self.cached_commander_order = decision["commander_order"]
            if decision.get("hunter_moves"):
                self.cached_hunter_moves = decision["hunter_moves"]

            # 3. Hunter Movement Cadence Tick
            if hunter_move_triggered:
                # Apply latest AI hunter moves
                if self.cached_hunter_moves:
                    self.env.apply_hunter_moves(self.cached_hunter_moves)
                else:
                    # Emergency fallback if no moves queued
                    self.env.apply_hunter_moves(["STAY"] * len(self.env.hunters))

                # Update target pixel positions for LERP
                self.env.sync_pixel_targets(self.origin_x, self.origin_y, self.cell_size)

                # Check if any hunter intercepted the player
                if self.env.check_defeat():
                    self._trigger_defeat()
                    return

                # Request fresh moves for the next tick
                self._dispatch_ai_query()

            # 4. Periodic AI Refresh Timer (keeps telemetry and breadcrumbs fresh)
            self.ai_request_timer += dt
            if self.ai_request_timer >= self.ai_request_interval:
                self.ai_request_timer = 0.0
                if not is_busy:
                    self._dispatch_ai_query()

            # 5. Entity LERP Visual Updates (speed = 0.28)
            # visual = visual + (target - visual) * 0.28
            self.env.update_lerp_all(speed=0.28)

    # =========================================================================
    # RENDERING PIPELINE
    # =========================================================================
    def render(self) -> None:
        """Render the complete scene based on the current state."""
        self.screen.fill((11, 15, 23))

        if self.state == STATE_SPLASH:
            self.ui.draw_splash_screen(self.screen, self.splash_timer, self.splash_duration)

        elif self.state == STATE_LOGIN:
            self.ui.draw_login_screen(self.screen, self.recent_operatives, self.login_status)

        elif self.state == STATE_HOME:
            self.ui.draw_home_screen(self.screen, self.best_victory_steps, self.user_stats)

        elif self.state == STATE_HOW_TO_PLAY:
            self.ui.draw_how_to_play_screen(self.screen)

        elif self.state in (STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER) and self.env:
            # 1. Draw Grid Area and Entities
            self.ui.draw_grid_environment(
                surface=self.screen,
                grid_size=self.env.grid_size,
                origin_x=self.origin_x,
                origin_y=self.origin_y,
                cell_size=self.cell_size,
                walls=self.env.walls,
                player_x=self.env.player_visual_x,
                player_y=self.env.player_visual_y,
                player_pos=self.env.player_pos,
                has_key=self.env.has_key,
                key_pos=self.env.key_pos,
                exit_pos=self.env.exit_pos,
                hunters=self.env.hunters,
                recommended_path=self.cached_recommended_path,
                wall_shift_alert=self.env.wall_shift_alert,
                player_facing=(self.env.player_facing_dr, self.env.player_facing_dc),
            )

            # 2. Draw Bottom HUD Console
            decision, latency_ms, status_text, _ = self.ai.get_latest_decision()
            level_name = self.env.config["name"]
            self.ui.draw_hud_console(
                surface=self.screen,
                level_name=level_name,
                steps=self.env.steps,
                best_steps=self.best_victory_steps,
                has_key=self.env.has_key,
                ai_latency_ms=latency_ms,
                ai_status=status_text,
                is_gemini_active=self.ai.is_gemini_active,
                commander_order=self.cached_commander_order,
            )

            # 3. Draw Quick Pause Button (visible during active mission & pause)
            self.ui.btn_pause.draw(self.screen)

            # 4. Draw Standby Banner if in reconnaissance countdown
            if self.state == STATE_PLAYING and self.standby_timer > 0:
                self.ui.draw_standby_banner(self.screen, self.standby_timer)

            # 5. Draw Tactical Pause Overlay (Sir Demonstration & Walkthrough Mode)
            if self.state == STATE_PAUSED:
                self.ui.draw_pause_overlay(
                    surface=self.screen,
                    origin_x=self.origin_x,
                    origin_y=self.origin_y,
                    cell_size=self.cell_size,
                    player_x=self.env.player_visual_x,
                    player_y=self.env.player_visual_y,
                    has_key=self.env.has_key,
                    hunters=self.env.hunters,
                    key_pos=self.env.key_pos,
                    exit_pos=self.env.exit_pos,
                    recommended_path=self.cached_recommended_path,
                    ai_latency_ms=latency_ms,
                    ai_status=status_text,
                    level_name=level_name,
                )

            # 6. Draw Game Over Overlay if in GAME_OVER state
            if self.state == STATE_GAME_OVER:
                self.ui.draw_game_over_overlay(
                    surface=self.screen,
                    is_victory=self.is_victory,
                    steps=self.env.steps,
                    is_new_best=self.is_new_best_record,
                    current_level=self.selected_level,
                )

        pygame.display.flip()

    # =========================================================================
    # MAIN LOOP ENTRY POINT
    # =========================================================================
    def run(self) -> None:
        """Execute the primary 60 FPS game loop."""
        while self.is_running:
            # Enforce strict 60 FPS clock cycle
            dt = self.clock.tick(60) / 1000.0
            # Cap dt to prevent physics tunneling on OS lag spikes
            dt = min(dt, 0.05)

            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()
        sys.exit()
