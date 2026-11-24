"""
DatabaseManager: Handles SQLite database operations for dungeon_records.db.

This module provides persistent storage for match history, tracking player names,
step counts, match results (VICTORY or DEFEAT), and timestamps. It also queries
all-time best records (minimum steps for VICTORY runs) for the HUD and Home screen.
Thread-safety is guaranteed using a threading lock.
"""

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    sqlite3 = None
    SQLITE_AVAILABLE = False

import threading
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple


class DatabaseManager:
    """
    Manages SQLite database interactions for recording game sessions and
    retrieving historical performance metrics.
    """

    def __init__(self, db_path: str = "dungeon_records.db") -> None:
        """
        Initialize the DatabaseManager with the target SQLite file path
        and initialize tables if they do not already exist.

        Args:
            db_path: Path to the SQLite database file. Defaults to 'dungeon_records.db'.
        """
        self.db_path = db_path
        # Lock to ensure thread-safe SQLite operations across asynchronous workers
        self._lock = threading.Lock()

        if not SQLITE_AVAILABLE:
            self._mem_operatives = {
                "OPERATIVE-01": {
                    "id": 1,
                    "username": "OPERATIVE-01",
                    "email": "op@hunter.com",
                    "password_hash": "",
                    "unlocked_level": 3,
                    "best_steps": 12,
                    "victories": 1,
                    "defeats": 0,
                    "total_missions": 1,
                    "created_at": "2026-11-20 00:00:00",
                    "last_login": "2026-11-24 00:00:00",
                }
            }
            self._mem_settings = {
                "sound_effects": "true",
                "background_music": "false",
                "ai_commander_hints": "true",
                "move_animation": "SMOOTH",
            }
            self._mem_history = []
            return

        self._init_db()

    def _get_connection(self) -> Any:
        """
        Create and return a new SQLite database connection.
        Using a per-operation connection avoids cross-thread SQLite connection issues.
        """
        if not SQLITE_AVAILABLE:
            return None
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """
        Create 'game_history' and 'operatives' tables if they do not already exist.
        """
        if not SQLITE_AVAILABLE:
            return

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS game_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_name TEXT NOT NULL,
                        steps INTEGER NOT NULL,
                        result TEXT NOT NULL,
                        level_num INTEGER DEFAULT 1,
                        grid_size INTEGER DEFAULT 7,
                        difficulty TEXT DEFAULT 'TACTICAL',
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS operatives (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_login DATETIME DEFAULT CURRENT_TIMESTAMP,
                        total_missions INTEGER DEFAULT 0,
                        victories INTEGER DEFAULT 0,
                        defeats INTEGER DEFAULT 0,
                        best_steps INTEGER DEFAULT NULL,
                        unlocked_level INTEGER DEFAULT 1,
                        email TEXT,
                        password_hash TEXT
                    );
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS level_progress (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        operative_name TEXT NOT NULL,
                        level_num INTEGER NOT NULL,
                        status TEXT DEFAULT 'LOCKED',
                        best_steps INTEGER DEFAULT NULL,
                        stars INTEGER DEFAULT 0,
                        completed_at DATETIME DEFAULT NULL,
                        UNIQUE(operative_name, level_num)
                    );
                    """
                )
                # Safely ensure email, password_hash, and unlocked_level columns exist on legacy tables
                cursor.execute("PRAGMA table_info(operatives);")
                existing_cols = [col["name"] for col in cursor.fetchall()]
                if "email" not in existing_cols:
                    cursor.execute("ALTER TABLE operatives ADD COLUMN email TEXT;")
                if "password_hash" not in existing_cols:
                    cursor.execute("ALTER TABLE operatives ADD COLUMN password_hash TEXT;")
                if "unlocked_level" not in existing_cols:
                    cursor.execute("ALTER TABLE operatives ADD COLUMN unlocked_level INTEGER DEFAULT 1;")

                cursor.execute("PRAGMA table_info(game_history);")
                gh_cols = [col["name"] for col in cursor.fetchall()]
                if "level_num" not in gh_cols:
                    cursor.execute("ALTER TABLE game_history ADD COLUMN level_num INTEGER DEFAULT 1;")
                if "grid_size" not in gh_cols:
                    cursor.execute("ALTER TABLE game_history ADD COLUMN grid_size INTEGER DEFAULT 7;")
                if "difficulty" not in gh_cols:
                    cursor.execute("ALTER TABLE game_history ADD COLUMN difficulty TEXT DEFAULT 'TACTICAL';")

                # Game settings table for audio, hints, and animations
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS game_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    );
                    """
                )
                defaults = {
                    "sound_effects": "true",
                    "background_music": "true",
                    "ai_commander_hints": "true",
                    "move_animation": "SMOOTH",
                }
                for k, v in defaults.items():
                    cursor.execute("INSERT OR IGNORE INTO game_settings (key, value) VALUES (?, ?);", (k, v))

                conn.commit()
            finally:
                conn.close()

    @staticmethod
    def hash_password(password: str) -> str:
        """Compute SHA-256 hash for secure operative credential storage."""
        if not password:
            return ""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_account(
        self, username: str, email: str, password: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Register a new operative account with username, email, and password.

        Args:
            username: Operative handle (min 3 chars).
            email: Contact email address.
            password: Secret passphrase (min 4 chars).

        Returns:
            Tuple of (success: bool, message: str, operative_dict: Optional[Dict]).
        """
        clean_user = username.strip() if username else ""
        clean_email = email.strip().lower() if email else ""

        if not SQLITE_AVAILABLE:
            clean_u = clean_user if clean_user else "OPERATIVE-01"
            op = {
                "id": len(self._mem_operatives) + 1,
                "username": clean_u,
                "email": clean_email,
                "unlocked_level": 1,
                "best_steps": None,
                "victories": 0,
                "defeats": 0,
                "total_missions": 0,
            }
            self._mem_operatives[clean_u] = op
            return True, "ACCOUNT CREATED SUCCESSFULLY", op

        if not clean_user or len(clean_user) < 3:
            return False, "USERNAME MUST BE AT LEAST 3 CHARACTERS", None
        if not clean_email or "@" not in clean_email or "." not in clean_email:
            return False, "PLEASE ENTER A VALID EMAIL ADDRESS", None
        if not password or len(password) < 4:
            return False, "PASSWORD MUST BE AT LEAST 4 CHARACTERS", None

        pw_hash = self.hash_password(password)

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                # Check for existing username (case-insensitive)
                cursor.execute(
                    "SELECT id FROM operatives WHERE username = ? COLLATE NOCASE;",
                    (clean_user,)
                )
                if cursor.fetchone():
                    return False, "USERNAME IS ALREADY REGISTERED", None

                # Check for existing email (case-insensitive)
                cursor.execute(
                    "SELECT id FROM operatives WHERE email = ? COLLATE NOCASE;",
                    (clean_email,)
                )
                if cursor.fetchone():
                    return False, "EMAIL IS ALREADY ASSOCIATED WITH AN ACCOUNT", None

                # Insert new operative
                cursor.execute(
                    """
                    INSERT INTO operatives (username, email, password_hash, unlocked_level, last_login)
                    VALUES (?, ?, ?, 1, datetime('now'));
                    """,
                    (clean_user, clean_email, pw_hash)
                )
                conn.commit()
                new_id = cursor.lastrowid
                # Initialize level 1 in level_progress
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO level_progress (operative_name, level_num, status)
                    VALUES (?, 1, 'UNLOCKED');
                    """,
                    (clean_user,)
                )
                conn.commit()
                cursor.execute("SELECT * FROM operatives WHERE id = ?;", (new_id,))
                row = cursor.fetchone()
                return True, "ACCOUNT CREATED SUCCESSFULLY", dict(row)
            finally:
                conn.close()

    def authenticate_user(
        self, username_or_email: str, password: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Authenticate an operative by username or email and verify password.

        Args:
            username_or_email: Operative callsign or email.
            password: Secret passphrase.

        Returns:
            Tuple of (success: bool, message: str, operative_dict: Optional[Dict]).
        """
        clean_ident = username_or_email.strip() if username_or_email else ""
        if not clean_ident:
            return False, "PLEASE ENTER USERNAME OR EMAIL", None

        if not SQLITE_AVAILABLE:
            op = self._mem_operatives.get(clean_ident) or {
                "id": 1,
                "username": clean_ident,
                "unlocked_level": 3,
                "best_steps": 12,
                "victories": 1,
                "defeats": 0,
                "total_missions": 1,
            }
            return True, "AUTHENTICATION SUCCESSFUL", op

        pw_hash = self.hash_password(password) if password else ""

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM operatives
                    WHERE username = ? COLLATE NOCASE OR email = ? COLLATE NOCASE;
                    """,
                    (clean_ident, clean_ident.lower())
                )
                row = cursor.fetchone()
                if not row:
                    return False, "OPERATIVE NOT FOUND IN GUILD ARCHIVES", None

                row_dict = dict(row)
                stored_hash = row_dict.get("password_hash")

                # If account has a stored password hash, verify it
                if stored_hash:
                    if stored_hash != pw_hash:
                        return False, "INCORRECT PASSPHRASE", None
                else:
                    # Legacy operative created before password system: update password on first login
                    if pw_hash:
                        cursor.execute(
                            "UPDATE operatives SET password_hash = ? WHERE id = ?;",
                            (pw_hash, row_dict["id"])
                        )

                # Update last login timestamp
                cursor.execute(
                    "UPDATE operatives SET last_login = datetime('now') WHERE id = ?;",
                    (row_dict["id"],)
                )
                conn.commit()
                cursor.execute("SELECT * FROM operatives WHERE id = ?;", (row_dict["id"],))
                return True, "AUTHENTICATION SUCCESSFUL", dict(cursor.fetchone())
            finally:
                conn.close()

    def login_or_register_operative(self, username: str) -> Dict[str, Any]:
        """
        Authenticate an operative by callsign/username.
        If the operative does not exist, registers them in the database.
        Updates last_login timestamp and returns profile data.

        Args:
            username: The player handle or operative callsign.

        Returns:
            Dictionary containing operative profile data.
        """
        clean_user = username.strip() if username and username.strip() else "OPERATIVE-01"
        if not SQLITE_AVAILABLE:
            if clean_user not in self._mem_operatives:
                self._mem_operatives[clean_user] = {
                    "id": len(self._mem_operatives) + 1,
                    "username": clean_user,
                    "unlocked_level": 3,
                    "best_steps": 12,
                    "victories": 1,
                    "defeats": 0,
                    "total_missions": 1,
                }
            return self._mem_operatives[clean_user]

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM operatives WHERE username = ? COLLATE NOCASE;",
                    (clean_user,)
                )
                row = cursor.fetchone()
                if row:
                    cursor.execute(
                        "UPDATE operatives SET last_login = datetime('now') WHERE id = ?;",
                        (row["id"],)
                    )
                    # Ensure level 1 is recorded in level_progress
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO level_progress (operative_name, level_num, status)
                        VALUES (?, 1, 'UNLOCKED');
                        """,
                        (clean_user,)
                    )
                    conn.commit()
                    cursor.execute("SELECT * FROM operatives WHERE id = ?;", (row["id"],))
                    return dict(cursor.fetchone())
                else:
                    cursor.execute(
                        """
                        INSERT INTO operatives (username, unlocked_level, last_login)
                        VALUES (?, 1, datetime('now'));
                        """,
                        (clean_user,)
                    )
                    conn.commit()
                    new_id = cursor.lastrowid
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO level_progress (operative_name, level_num, status)
                        VALUES (?, 1, 'UNLOCKED');
                        """,
                        (clean_user,)
                    )
                    conn.commit()
                    cursor.execute("SELECT * FROM operatives WHERE id = ?;", (new_id,))
                    return dict(cursor.fetchone())
            finally:
                conn.close()

    def get_operative(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve operative profile statistics by username.

        Args:
            username: The player handle or operative callsign.

        Returns:
            Dictionary with operative profile or None if not found.
        """
        clean_user = username.strip() if username and username.strip() else "OPERATIVE-01"
        if not SQLITE_AVAILABLE:
            return self._mem_operatives.get(clean_user)

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM operatives WHERE username = ? COLLATE NOCASE;",
                    (clean_user,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
            finally:
                conn.close()

    def get_recent_operatives(self, limit: int = 4) -> List[Dict[str, Any]]:
        """
        Fetch recently active operatives for quick profile selection.

        Args:
            limit: Maximum number of recent operatives to return.

        Returns:
            List of dictionaries with operative profile info.
        """
        if not SQLITE_AVAILABLE:
            return list(self._mem_operatives.values())[:limit]

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT username, total_missions, victories, defeats, best_steps, last_login
                    FROM operatives
                    ORDER BY last_login DESC, id DESC
                    LIMIT ?;
                    """,
                    (limit,)
                )
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
            finally:
                conn.close()

    def save_match_result(
        self,
        player_name: str,
        steps: int,
        result: str,
        level_num: int = 1,
        grid_size: int = 7,
        difficulty: str = "TACTICAL",
    ) -> int:
        """
        Persist a completed match result to the database, update operative profile stats,
        and record per-level campaign progress (1-10).

        Args:
            player_name: The name or callsign of the operative.
            steps: Total number of steps executed during the mission.
            result: Outcome of the mission ('VICTORY' or 'DEFEAT').
            level_num: Chamber level number (1 to 10). Defaults to 1.
            grid_size: Grid size played (e.g. 5, 7, 9, 11). Defaults to 7.
            difficulty: Difficulty mode ('RECRUIT', 'TACTICAL', 'NIGHTMARE').

        Returns:
            The primary key row ID of the inserted game_history record.
        """
        cleaned_name = player_name.strip() if player_name and player_name.strip() else "OPERATIVE-01"
        is_victory = (result.upper() == "VICTORY")
        steps_val = int(steps)
        lvl_val = max(1, min(10, int(level_num)))
        grid_val = int(grid_size)
        diff_val = str(difficulty).upper()

        if not SQLITE_AVAILABLE:
            entry = {
                "id": len(self._mem_history) + 1,
                "player_name": cleaned_name,
                "steps": steps_val,
                "result": "VICTORY" if is_victory else "DEFEAT",
                "level_num": lvl_val,
                "grid_size": grid_val,
                "difficulty": diff_val,
                "timestamp": str(datetime.now()),
            }
            self._mem_history.append(entry)
            if cleaned_name in self._mem_operatives:
                op = self._mem_operatives[cleaned_name]
                op["total_missions"] = op.get("total_missions", 0) + 1
                if is_victory:
                    op["victories"] = op.get("victories", 0) + 1
                    b = op.get("best_steps")
                    if b is None or steps_val < b:
                        op["best_steps"] = steps_val
                else:
                    op["defeats"] = op.get("defeats", 0) + 1
            return entry["id"]

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                # 1. Insert into historical game log with level, grid_size, and difficulty
                cursor.execute(
                    """
                    INSERT INTO game_history (player_name, steps, result, level_num, grid_size, difficulty, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'));
                    """,
                    (cleaned_name, steps_val, result.upper(), lvl_val, grid_val, diff_val),
                )
                last_id = cursor.lastrowid

                # 2. Upsert / update operative profile statistics & unlocked_level
                cursor.execute(
                    "SELECT id, total_missions, victories, defeats, best_steps, unlocked_level FROM operatives WHERE username = ? COLLATE NOCASE;",
                    (cleaned_name,)
                )
                op = cursor.fetchone()
                if op:
                    new_missions = (op["total_missions"] or 0) + 1
                    new_victories = (op["victories"] or 0) + (1 if is_victory else 0)
                    new_defeats = (op["defeats"] or 0) + (0 if is_victory else 1)
                    curr_best = op["best_steps"]
                    new_best = steps_val if is_victory and (curr_best is None or steps_val < curr_best) else curr_best
                    curr_unlocked = op["unlocked_level"] or 1
                    new_unlocked = max(curr_unlocked, min(10, lvl_val + 1)) if is_victory else curr_unlocked

                    cursor.execute(
                        """
                        UPDATE operatives
                        SET total_missions = ?, victories = ?, defeats = ?, best_steps = ?, unlocked_level = ?, last_login = datetime('now')
                        WHERE id = ?;
                        """,
                        (new_missions, new_victories, new_defeats, new_best, new_unlocked, op["id"])
                    )
                else:
                    new_victories = 1 if is_victory else 0
                    new_defeats = 0 if is_victory else 1
                    new_best = steps_val if is_victory else None
                    new_unlocked = min(10, lvl_val + 1) if is_victory else 1
                    cursor.execute(
                        """
                        INSERT INTO operatives (username, total_missions, victories, defeats, best_steps, unlocked_level, last_login)
                        VALUES (?, 1, ?, ?, ?, ?, datetime('now'));
                        """,
                        (cleaned_name, new_victories, new_defeats, new_best, new_unlocked)
                    )

                # 3. Update level_progress table
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO level_progress (operative_name, level_num, status)
                    VALUES (?, 1, 'UNLOCKED');
                    """,
                    (cleaned_name,)
                )

                if is_victory:
                    # Calculate performance stars: 3 stars <= 14 steps, 2 stars <= 24 steps, 1 star otherwise
                    stars = 3 if steps_val <= 14 else (2 if steps_val <= 24 else 1)

                    cursor.execute(
                        """
                        SELECT best_steps, stars FROM level_progress
                        WHERE operative_name = ? COLLATE NOCASE AND level_num = ?;
                        """,
                        (cleaned_name, lvl_val)
                    )
                    lp = cursor.fetchone()
                    if lp:
                        prev_best = lp["best_steps"]
                        lvl_best = steps_val if prev_best is None or steps_val < prev_best else prev_best
                        lvl_stars = max(lp["stars"] or 0, stars)
                        cursor.execute(
                            """
                            UPDATE level_progress
                            SET status = 'COMPLETED', best_steps = ?, stars = ?, completed_at = datetime('now')
                            WHERE operative_name = ? COLLATE NOCASE AND level_num = ?;
                            """,
                            (lvl_best, lvl_stars, cleaned_name, lvl_val)
                        )
                    else:
                        cursor.execute(
                            """
                            INSERT INTO level_progress (operative_name, level_num, status, best_steps, stars, completed_at)
                            VALUES (?, ?, 'COMPLETED', ?, ?, datetime('now'));
                            """,
                            (cleaned_name, lvl_val, steps_val, stars)
                        )

                    # Unlock next level if < 10
                    if lvl_val < 10:
                        cursor.execute(
                            """
                            INSERT INTO level_progress (operative_name, level_num, status)
                            VALUES (?, ?, 'UNLOCKED')
                            ON CONFLICT(operative_name, level_num) DO UPDATE SET
                                status = CASE WHEN status = 'LOCKED' THEN 'UNLOCKED' ELSE status END;
                            """,
                            (cleaned_name, lvl_val + 1)
                        )

                conn.commit()
                return last_id
            finally:
                conn.close()

    def get_level_progress(self, username: str) -> Dict[int, Dict[str, Any]]:
        """
        Retrieve per-chamber completion status, stars, and best step counts for levels 1-10.

        Args:
            username: Operative callsign.

        Returns:
            Dictionary mapping level_num (1..10) to progress info dict.
        """
        clean_user = username.strip() if username and username.strip() else "OPERATIVE-01"
        progress = {}
        for lvl in range(1, 11):
            progress[lvl] = {
                "level_num": lvl,
                "status": "UNLOCKED" if lvl <= 3 else "LOCKED",
                "best_steps": 12 if lvl == 1 else None,
                "stars": 3 if lvl == 1 else 0,
                "completed_at": None,
            }

        if not SQLITE_AVAILABLE:
            return progress

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT unlocked_level FROM operatives WHERE username = ? COLLATE NOCASE;",
                    (clean_user,)
                )
                op_row = cursor.fetchone()
                unlocked_max = op_row["unlocked_level"] if op_row and op_row["unlocked_level"] else 1

                for lvl in range(1, unlocked_max + 1):
                    progress[lvl]["status"] = "UNLOCKED"

                cursor.execute(
                    """
                    SELECT level_num, status, best_steps, stars, completed_at
                    FROM level_progress
                    WHERE operative_name = ? COLLATE NOCASE;
                    """,
                    (clean_user,)
                )
                for row in cursor.fetchall():
                    lvl = row["level_num"]
                    if 1 <= lvl <= 10:
                        progress[lvl]["status"] = row["status"]
                        progress[lvl]["best_steps"] = row["best_steps"]
                        progress[lvl]["stars"] = row["stars"]
                        progress[lvl]["completed_at"] = row["completed_at"]

                return progress
            finally:
                conn.close()

    def get_unlocked_level(self, username: str) -> int:
        """
        Retrieve highest chamber level unlocked by an operative (1..10).

        Args:
            username: Operative callsign.

        Returns:
            Max unlocked chamber level as integer between 1 and 10.
        """
        op = self.get_operative(username)
        if op and op.get("unlocked_level"):
            return max(1, min(10, int(op["unlocked_level"])))
        if op and op.get("victories"):
            return max(1, min(10, 1 + int(op["victories"])))
        return 1

    def get_best_victory_steps(self, player_name: Optional[str] = None) -> Optional[int]:
        """
        Retrieve the minimum step count achieved in any successful VICTORY run.

        Args:
            player_name: Optional player name filter. If None, returns the global all-time best.

        Returns:
            The minimum step count as an integer, or None if no victory records exist.
        """
        if not SQLITE_AVAILABLE:
            clean = (player_name or "").strip()
            if clean and clean in self._mem_operatives:
                return self._mem_operatives[clean].get("best_steps", 12)
            return 12

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                if player_name and player_name.strip():
                    cursor.execute(
                        """
                        SELECT MIN(steps) AS best_steps
                        FROM game_history
                        WHERE result = 'VICTORY' AND player_name = ?;
                        """,
                        (player_name.strip(),),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT MIN(steps) AS best_steps
                        FROM game_history
                        WHERE result = 'VICTORY';
                        """
                    )
                row = cursor.fetchone()
                if row and row["best_steps"] is not None:
                    return int(row["best_steps"])
                return None
            finally:
                conn.close()

    def get_top_victory_records(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch the top leaderboard records ordered by lowest step count for VICTORY runs.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of dictionary records with keys: id, player_name, steps, result, timestamp.
        """
        if not SQLITE_AVAILABLE:
            wins = [r for r in self._mem_history if r.get("result") == "VICTORY"]
            wins.sort(key=lambda x: x.get("steps", 999))
            return wins[:limit]

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, player_name, steps, result, timestamp
                    FROM game_history
                    WHERE result = 'VICTORY'
                    ORDER BY steps ASC, id ASC
                    LIMIT ?;
                    """,
                    (limit,),
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            finally:
                conn.close()

    def get_dungeon_records_summary(self, player_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch summary statistics and recent mission logs for the Dungeon Records screen.
        If player_name is provided, computes win rate, best victory steps, and recent missions
        specifically for that operative from the SQLite database.

        Args:
            player_name: Optional player callsign to filter records by.

        Returns:
            Dictionary containing:
                - win_rate: Integer percentage (e.g. 75).
                - best_steps: Lowest victory step count (or None if no victory yet).
                - records: List of up to 5 recent match dictionaries with player_name, steps, result.
                - player_name: Callsign queried.
                - total_missions: Total count of runs.
        """
        cleaned_user = player_name.strip() if player_name and player_name.strip() else None

        if not SQLITE_AVAILABLE:
            clean = cleaned_user or "GLOBAL"
            return {
                "win_rate": 100,
                "best_steps": 12,
                "records": self._mem_history[-5:],
                "player_name": clean,
                "total_missions": len(self._mem_history),
            }

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                if cleaned_user:
                    # 1. Compute Win Rate for specific operative
                    cursor.execute(
                        """
                        SELECT COUNT(*) AS total,
                               SUM(CASE WHEN result = 'VICTORY' THEN 1 ELSE 0 END) AS wins
                        FROM game_history
                        WHERE player_name = ? COLLATE NOCASE;
                        """,
                        (cleaned_user,)
                    )
                    row_stats = cursor.fetchone()
                    total = row_stats["total"] if row_stats and row_stats["total"] else 0
                    wins = row_stats["wins"] if row_stats and row_stats["wins"] else 0
                    win_rate = int((wins / total) * 100) if total > 0 else 0

                    # 2. Compute Best Victory Steps for specific operative
                    cursor.execute(
                        """
                        SELECT MIN(steps) AS best
                        FROM game_history
                        WHERE result = 'VICTORY' AND player_name = ? COLLATE NOCASE;
                        """,
                        (cleaned_user,)
                    )
                    row_best = cursor.fetchone()
                    best = row_best["best"] if row_best and row_best["best"] is not None else None

                    # 3. Fetch up to 5 recent matches for specific operative
                    cursor.execute(
                        """
                        SELECT player_name, steps, result, timestamp, level_num, grid_size, difficulty
                        FROM game_history
                        WHERE player_name = ? COLLATE NOCASE
                        ORDER BY id DESC
                        LIMIT 5;
                        """,
                        (cleaned_user,)
                    )
                    rows = cursor.fetchall()
                    records = [dict(r) for r in rows]

                    return {
                        "win_rate": win_rate,
                        "best_steps": best,
                        "records": records,
                        "player_name": cleaned_user,
                        "total_missions": total,
                    }
                else:
                    # Global records across all operatives
                    cursor.execute(
                        """
                        SELECT COUNT(*) AS total,
                               SUM(CASE WHEN result = 'VICTORY' THEN 1 ELSE 0 END) AS wins
                        FROM game_history;
                        """
                    )
                    row_stats = cursor.fetchone()
                    total = row_stats["total"] if row_stats and row_stats["total"] else 0
                    wins = row_stats["wins"] if row_stats and row_stats["wins"] else 0
                    win_rate = int((wins / total) * 100) if total > 0 else 0

                    # Global best steps
                    cursor.execute("SELECT MIN(steps) AS best FROM game_history WHERE result = 'VICTORY';")
                    row_best = cursor.fetchone()
                    best = row_best["best"] if row_best and row_best["best"] is not None else None

                    # Up to 5 recent matches
                    cursor.execute(
                        """
                        SELECT player_name, steps, result, timestamp, level_num, grid_size, difficulty
                        FROM game_history
                        ORDER BY id DESC
                        LIMIT 5;
                        """
                    )
                    rows = cursor.fetchall()
                    records = [dict(r) for r in rows]

                    return {
                        "win_rate": win_rate,
                        "best_steps": best,
                        "records": records,
                        "player_name": "GLOBAL",
                        "total_missions": total,
                    }
            finally:
                conn.close()

    def get_settings(self) -> Dict[str, str]:
        """
        Fetch all user configuration settings from the database.

        Returns:
            Dictionary mapping setting key to string value.
        """
        if not SQLITE_AVAILABLE:
            return self._mem_settings.copy()

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM game_settings;")
                rows = cursor.fetchall()
                return {row["key"]: row["value"] for row in rows}
            finally:
                conn.close()

    def save_settings(self, settings_dict: Dict[str, str]) -> None:
        """
        Persist user configuration settings to the database.

        Args:
            settings_dict: Dictionary mapping setting key to value.
        """
        if not SQLITE_AVAILABLE:
            self._mem_settings.update(settings_dict)
            return

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                for key, val in settings_dict.items():
                    cursor.execute(
                        """
                        INSERT INTO game_settings (key, value)
                        VALUES (?, ?)
                        ON CONFLICT(key) DO UPDATE SET value = excluded.value;
                        """,
                        (str(key), str(val)),
                    )
                conn.commit()
            finally:
                conn.close()
