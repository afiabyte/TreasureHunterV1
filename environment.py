"""
GridEnvironment: Manages the N x N tactical grid matrix, entities, and dynamics.

This module coordinates:
- The N x N grid matrix (5x5, 7x7 default, 9x9, 11x11).
- Infiltration Start (0, 0), Key K, and Extraction Exit (N-1, N-1).
- Dynamic wall relocations (every 2.5s without overwriting entities).
- Hunter entity tracking: up to 8 hunters tracking position, LERP visual coordinates,
  and directional facing vectors.
- LERP interpolation math (speed = 0.28) for buttery smooth 60 FPS visual rendering.
"""

import math
import random
from typing import List, Tuple, Set, Optional, Dict, Any


# Cardinal movement vectors: (dr, dc)
MOVE_VECTORS: Dict[str, Tuple[int, int]] = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
    "STAY": (0, 0),
}


class Hunter:
    """
    Represents an autonomous tactical hunter drone.
    Tracks discrete grid coordinates, continuous visual LERP coordinates,
    and directional facing vectors.
    """

    def __init__(self, hunter_id: int, grid_r: int, grid_c: int) -> None:
        """
        Initialize a hunter drone.

        Args:
            hunter_id: Unique numeric identifier for the hunter.
            grid_r: Initial grid row coordinate.
            grid_c: Initial grid column coordinate.
        """
        self.hunter_id = hunter_id
        self.r = grid_r
        self.c = grid_c

        # Directional facing vector (dr, dc) - default facing DOWN (+1, 0)
        self.facing_dr = 1
        self.facing_dc = 0

        # Visual floating-point pixel coordinates for smooth LERP animation
        self.visual_x = 0.0
        self.visual_y = 0.0

        # Target pixel coordinates to interpolate toward
        self.target_x = 0.0
        self.target_y = 0.0

    @property
    def pos(self) -> Tuple[int, int]:
        """Return discrete (row, col) tuple."""
        return (self.r, self.c)

    @property
    def facing(self) -> Tuple[int, int]:
        """Return directional facing vector (dr, dc)."""
        return (self.facing_dr, self.facing_dc)

    def set_grid_pos(self, r: int, c: int) -> None:
        """
        Update the discrete grid position and calculate new facing vector.

        Args:
            r: New grid row.
            c: New grid column.
        """
        dr = r - self.r
        dc = c - self.c
        # Only update facing direction if actual movement occurred
        if dr != 0 or dc != 0:
            self.facing_dr = 1 if dr > 0 else (-1 if dr < 0 else 0)
            self.facing_dc = 1 if dc > 0 else (-1 if dc < 0 else 0)

        self.r = r
        self.c = c

    def update_lerp(self, speed: float = 0.28) -> None:
        """
        Perform Linear Interpolation (LERP) toward the target pixel coordinates.
        Formula: visual = visual + (target - visual) * speed

        Args:
            speed: Interpolation rate (0.28 as mandated by spec).
        """
        self.visual_x += (self.target_x - self.visual_x) * speed
        self.visual_y += (self.target_y - self.visual_y) * speed


class GridEnvironment:
    """
    Manages the tactical evasion simulation matrix, dynamic walls, key, exit,
    and active hunter entities.
    """

    # Difficulty Level Presets
    LEVEL_CONFIGS: Dict[int, Dict[str, Any]] = {
        1: {
            "name": "Recruit",
            "wall_relocation_interval": 3.5,  # Slower wall shifts
            "hunter_spawn_interval": 14.0,    # Infrequent hunter reinforcements
            "initial_hunters": 1,             # Mild initial pressure
            "wall_density": 0.14,
            "hunter_move_interval": 1.10,     # Slower hunter stalking ticks
        },
        2: {
            "name": "Tactical",
            "wall_relocation_interval": 2.5,  # Standard 2.5s dynamic wall shift
            "hunter_spawn_interval": 8.0,     # Regular reinforcements
            "initial_hunters": 2,             # Balanced tactical challenge
            "wall_density": 0.18,
            "hunter_move_interval": 0.85,     # Tense pacing
        },
        3: {
            "name": "Nightmare",
            "wall_relocation_interval": 1.7,  # Rapid shifting maze
            "hunter_spawn_interval": 5.0,     # Aggressive hunter swarming
            "initial_hunters": 4,             # High initial danger
            "wall_density": 0.22,
            "hunter_move_interval": 0.65,     # Relentless interception
        },
    }

    def __init__(self, grid_size: int = 7, level: int = 2) -> None:
        """
        Initialize the grid environment.

        Args:
            grid_size: Dimension N of the N x N grid (5, 7, 9, 11).
            level: Difficulty tier (1: Recruit, 2: Tactical, 3: Nightmare).
        """
        self.grid_size = grid_size
        self.level = level
        self.config = self.LEVEL_CONFIGS.get(level, self.LEVEL_CONFIGS[2])

        # Core Coordinates
        self.start_pos: Tuple[int, int] = (0, 0)
        self.exit_pos: Tuple[int, int] = (self.grid_size - 1, self.grid_size - 1)
        self.key_pos: Tuple[int, int] = (0, 0)
        self.player_pos: Tuple[int, int] = (0, 0)
        self.player_facing_dr: int = 0
        self.player_facing_dc: int = 1
        self.has_key: bool = False
        self.steps: int = 0

        # Player smooth LERP visual coordinates
        self.player_visual_x: float = 0.0
        self.player_visual_y: float = 0.0
        self.player_target_x: float = 0.0
        self.player_target_y: float = 0.0

        # Environmental Walls
        self.walls: Set[Tuple[int, int]] = set()

        # Hunter Entities (up to 8 max)
        self.hunters: List[Hunter] = []
        self._next_hunter_id: int = 1

        # Timers (in seconds)
        self.wall_timer: float = 0.0
        self.spawn_timer: float = 0.0
        self.hunter_move_timer: float = 0.0

        # Visual FX trigger flags
        self.wall_shift_alert: float = 0.0  # Duration for visual barrier shift pulse

        # Setup initial board state
        self.reset_environment()

    def reset_environment(self) -> None:
        """
        Reset and generate a fresh procedural grid matrix, resetting player,
        key, walls, and hunter squad with zero residual state leaks.
        """
        self.player_pos = self.start_pos
        self.player_facing_dr = 0
        self.player_facing_dc = 1
        self.has_key = False
        self.steps = 0
        self.wall_timer = 0.0
        self.spawn_timer = 0.0
        self.hunter_move_timer = 0.0
        self.wall_shift_alert = 0.0

        # Place Key at a strategic location away from Start and Exit
        self._place_key()

        # Generate procedural wall layout
        self._generate_walls()

        # Spawn initial hunters per difficulty level
        self.hunters.clear()
        self._next_hunter_id = 1
        initial_count = min(self.config["initial_hunters"], 8)
        for _ in range(initial_count):
            self.spawn_hunter()

    def _place_key(self) -> None:
        """
        Place the Key on an empty cell distinct from Start (0, 0) and Exit (N-1, N-1).
        Prefers the central / opposing quadrant for balanced gameplay.
        """
        valid_cells = []
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if (r, c) != self.start_pos and (r, c) != self.exit_pos:
                    # Prefer cells at least Manhattan distance >= 3 from start
                    if abs(r - self.start_pos[0]) + abs(c - self.start_pos[1]) >= 2:
                        valid_cells.append((r, c))

        if valid_cells:
            self.key_pos = random.choice(valid_cells)
        else:
            self.key_pos = (self.grid_size // 2, self.grid_size // 2)

    def _generate_walls(self) -> None:
        """
        Generate initial wall configuration based on the level's wall density.
        Ensures critical cells (Start, Exit, Key, and immediate infiltration/extraction paths)
        are never blocked.
        """
        self.walls.clear()
        total_cells = self.grid_size * self.grid_size
        num_walls = int(total_cells * self.config["wall_density"])

        # Reserved cells: Start, Exit, Key, and initial infiltration clearance
        reserved_cells = {
            self.start_pos,
            (0, 1),
            (1, 0),
            self.exit_pos,
            (self.grid_size - 2, self.grid_size - 1),
            (self.grid_size - 1, self.grid_size - 2),
            self.key_pos
        }

        candidate_cells = [
            (r, c)
            for r in range(self.grid_size)
            for c in range(self.grid_size)
            if (r, c) not in reserved_cells
        ]
        random.shuffle(candidate_cells)

        for cell in candidate_cells[:num_walls]:
            self.walls.add(cell)

    def relocate_walls(self) -> None:
        """
        Dynamically relocate walls without overwriting any entities.
        Strictly protects:
        - Player position
        - All active Hunter positions
        - Key position
        - Exit position
        - Start position
        """
        # Collect all active entity positions to guarantee they are never overwritten
        protected_cells: Set[Tuple[int, int]] = {
            self.start_pos,
            self.exit_pos,
            self.key_pos,
            self.player_pos,
        }
        for hunter in self.hunters:
            protected_cells.add(hunter.pos)

        # Relocate ~35-50% of existing walls to new valid empty positions
        if not self.walls:
            return

        walls_list = list(self.walls)
        relocate_count = max(1, len(walls_list) // 3)
        walls_to_move = random.sample(walls_list, relocate_count)

        # Remove chosen walls
        for w in walls_to_move:
            self.walls.remove(w)

        # Identify candidate empty cells
        empty_cells = [
            (r, c)
            for r in range(self.grid_size)
            for c in range(self.grid_size)
            if (r, c) not in self.walls and (r, c) not in protected_cells
        ]
        random.shuffle(empty_cells)

        # Re-add walls at new positions
        for cell in empty_cells[:relocate_count]:
            self.walls.add(cell)

        # Trigger visual alert pulse
        self.wall_shift_alert = 0.5

    def spawn_hunter(self) -> bool:
        """
        Spawn a new hunter drone on a valid empty cell.
        Enforces a minimum Manhattan distance of 3 (or 2 on small grids) from player
        to prevent unfair immediate ambushes. Maximum 8 active hunters.

        Returns:
            True if a hunter was successfully spawned, False otherwise.
        """
        if len(self.hunters) >= 8:
            return False

        occupied_cells: Set[Tuple[int, int]] = set(self.walls)
        occupied_cells.add(self.player_pos)
        occupied_cells.add(self.key_pos)
        occupied_cells.add(self.exit_pos)
        for h in self.hunters:
            occupied_cells.add(h.pos)

        min_dist = 2 if self.grid_size <= 5 else 3
        candidates = []
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if (r, c) not in occupied_cells:
                    dist_to_player = abs(r - self.player_pos[0]) + abs(c - self.player_pos[1])
                    if dist_to_player >= min_dist:
                        candidates.append((r, c))

        if not candidates:
            # Fallback: any unoccupied cell
            candidates = [
                (r, c)
                for r in range(self.grid_size)
                for c in range(self.grid_size)
                if (r, c) not in occupied_cells
            ]

        if not candidates:
            return False

        spawn_pos = random.choice(candidates)
        hunter = Hunter(self._next_hunter_id, spawn_pos[0], spawn_pos[1])
        self._next_hunter_id += 1
        self.hunters.append(hunter)
        return True

    def move_player(self, dr: int, dc: int) -> bool:
        """
        Attempt to move the player by cardinal delta (dr, dc).

        Args:
            dr: Row offset (-1, 0, 1).
            dc: Column offset (-1, 0, 1).

        Returns:
            True if the move succeeded, False if blocked by boundary or wall.
        """
        nr = self.player_pos[0] + dr
        nc = self.player_pos[1] + dc

        # Check bounds
        if not (0 <= nr < self.grid_size and 0 <= nc < self.grid_size):
            return False

        # Check walls
        if (nr, nc) in self.walls:
            return False

        # Move is valid
        if dr != 0 or dc != 0:
            self.player_facing_dr = dr
            self.player_facing_dc = dc

        self.player_pos = (nr, nc)
        self.steps += 1

        # Check Key collection
        if not self.has_key and self.player_pos == self.key_pos:
            self.has_key = True

        return True

    def apply_hunter_moves(self, moves: List[str]) -> None:
        """
        Apply a list of cardinal moves to active hunters.
        Enforces wall collisions and grid boundaries.

        Args:
            moves: List of move strings ("UP", "DOWN", "LEFT", "RIGHT", "STAY")
                   corresponding to active hunters.
        """
        occupied_cells = set(self.walls)
        # Note: Hunters can pass through key and exit, but not walls

        for i, hunter in enumerate(self.hunters):
            move_cmd = moves[i] if i < len(moves) else "STAY"
            dr, dc = MOVE_VECTORS.get(move_cmd.upper(), (0, 0))

            target_r = hunter.r + dr
            target_c = hunter.c + dc

            # Check validity
            if 0 <= target_r < self.grid_size and 0 <= target_c < self.grid_size:
                if (target_r, target_c) not in occupied_cells:
                    hunter.set_grid_pos(target_r, target_c)
                else:
                    # Move blocked by wall
                    hunter.set_grid_pos(hunter.r, hunter.c)
            else:
                # Out of bounds
                hunter.set_grid_pos(hunter.r, hunter.c)

    def update_timers(self, dt: float) -> Tuple[bool, bool, bool]:
        """
        Advance environment timers by delta time dt (in seconds).

        Args:
            dt: Frame delta time in seconds.

        Returns:
            Tuple of booleans: (wall_relocated, hunter_spawned, hunter_move_triggered)
        """
        wall_relocated = False
        hunter_spawned = False
        hunter_move_triggered = False

        # Decrease visual alert effect
        if self.wall_shift_alert > 0:
            self.wall_shift_alert = max(0.0, self.wall_shift_alert - dt)

        # Dynamic Wall Relocation Timer
        self.wall_timer += dt
        if self.wall_timer >= self.config["wall_relocation_interval"]:
            self.wall_timer = 0.0
            self.relocate_walls()
            wall_relocated = True

        # Periodic Hunter Reinforcement Timer (up to 8 hunters max)
        self.spawn_timer += dt
        if self.spawn_timer >= self.config["hunter_spawn_interval"]:
            self.spawn_timer = 0.0
            if len(self.hunters) < 8:
                spawned = self.spawn_hunter()
                if spawned:
                    hunter_spawned = True

        # Hunter Movement Cadence Timer
        self.hunter_move_timer += dt
        if self.hunter_move_timer >= self.config["hunter_move_interval"]:
            self.hunter_move_timer = 0.0
            hunter_move_triggered = True

        return (wall_relocated, hunter_spawned, hunter_move_triggered)

    def sync_pixel_targets(self, origin_x: float, origin_y: float, cell_size: float) -> None:
        """
        Update target pixel coordinates for player and hunters based on their grid positions.

        Args:
            origin_x: Left pixel offset of the grid area.
            origin_y: Top pixel offset of the grid area.
            cell_size: Size in pixels of each grid cell.
        """
        half = cell_size / 2.0

        # Player target pixel center
        self.player_target_x = origin_x + self.player_pos[1] * cell_size + half
        self.player_target_y = origin_y + self.player_pos[0] * cell_size + half

        # Hunter target pixel centers
        for h in self.hunters:
            h.target_x = origin_x + h.c * cell_size + half
            h.target_y = origin_y + h.r * cell_size + half

    def update_lerp_all(self, speed: float = 0.28) -> None:
        """
        Interpolate visual coordinates for all dynamic entities (Player and Hunters)
        using speed = 0.28 for smooth 60 FPS animation.

        Formula: pos = pos + (target - pos) * speed
        """
        # Interpolate player visual coordinates
        self.player_visual_x += (self.player_target_x - self.player_visual_x) * speed
        self.player_visual_y += (self.player_target_y - self.player_visual_y) * speed

        # Interpolate all hunters
        for h in self.hunters:
            h.update_lerp(speed)

    def snap_visuals_to_targets(self) -> None:
        """Immediately snap all visual coordinates to target positions (e.g. on reset)."""
        self.player_visual_x = self.player_target_x
        self.player_visual_y = self.player_target_y
        for h in self.hunters:
            h.visual_x = h.target_x
            h.visual_y = h.target_y

    def check_victory(self) -> bool:
        """
        Check if victory condition is satisfied:
        Player has secured the key and reached the extraction exit portal.
        """
        return self.has_key and (self.player_pos == self.exit_pos)

    def check_defeat(self) -> bool:
        """
        Check if defeat condition is satisfied:
        Any hunter occupies the same grid cell as the player.
        """
        for h in self.hunters:
            if h.pos == self.player_pos:
                return True
        return False
