"""
DatabaseManager: Handles SQLite database operations for dungeon_records.db.

This module provides persistent storage for match history, tracking player names,
step counts, match results (VICTORY or DEFEAT), and timestamps. It also queries
all-time best records (minimum steps for VICTORY runs) for the HUD and Home screen.
Thread-safety is guaranteed using a threading lock.
"""

import sqlite3
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
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """
        Create and return a new SQLite database connection.
        Using a per-operation connection avoids cross-thread SQLite connection issues.
        """
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """
        Create 'game_history' and 'operatives' tables if they do not already exist.
        Schema:
            game_history:
                id: INTEGER PRIMARY KEY AUTOINCREMENT
                player_name: TEXT (Player handle)
                steps: INTEGER (Total moves taken in the run)
                result: TEXT ('VICTORY' or 'DEFEAT')
                timestamp: DATETIME (UTC timestamp of record creation)
            operatives:
                id: INTEGER PRIMARY KEY AUTOINCREMENT
                username: TEXT UNIQUE NOT NULL
                created_at: DATETIME (Account creation timestamp)
                last_login: DATETIME (Last authentication timestamp)
                total_missions: INTEGER (Total runs deployed)
                victories: INTEGER (Total successful extractions)
                defeats: INTEGER (Total casualties)
                best_steps: INTEGER (Minimum steps for victory)
        """
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
                        email TEXT,
                        password_hash TEXT
                    );
                    """
                )
                # Safely ensure email and password_hash columns exist on legacy tables
                cursor.execute("PRAGMA table_info(operatives);")
                existing_cols = [col["name"] for col in cursor.fetchall()]
                if "email" not in existing_cols:
                    cursor.execute("ALTER TABLE operatives ADD COLUMN email TEXT;")
                if "password_hash" not in existing_cols:
                    cursor.execute("ALTER TABLE operatives ADD COLUMN password_hash TEXT;")
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
                    INSERT INTO operatives (username, email, password_hash, last_login)
                    VALUES (?, ?, ?, datetime('now'));
                    """,
                    (clean_user, clean_email, pw_hash)
                )
                conn.commit()
                new_id = cursor.lastrowid
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
                    conn.commit()
                    cursor.execute("SELECT * FROM operatives WHERE id = ?;", (row["id"],))
                    return dict(cursor.fetchone())
                else:
                    cursor.execute(
                        """
                        INSERT INTO operatives (username, last_login)
                        VALUES (?, datetime('now'));
                        """,
                        (clean_user,)
                    )
                    conn.commit()
                    new_id = cursor.lastrowid
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

    def save_match_result(self, player_name: str, steps: int, result: str) -> int:
        """
        Persist a completed match result to the database and update operative profile stats.

        Args:
            player_name: The name or callsign of the operative.
            steps: Total number of steps executed during the mission.
            result: Outcome of the mission ('VICTORY' or 'DEFEAT').

        Returns:
            The primary key row ID of the inserted game_history record.
        """
        cleaned_name = player_name.strip() if player_name and player_name.strip() else "OPERATIVE-01"
        is_victory = (result.upper() == "VICTORY")
        steps_val = int(steps)
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                # 1. Insert into historical game log
                cursor.execute(
                    """
                    INSERT INTO game_history (player_name, steps, result, timestamp)
                    VALUES (?, ?, ?, datetime('now'));
                    """,
                    (cleaned_name, steps_val, result.upper()),
                )
                last_id = cursor.lastrowid

                # 2. Upsert / update operative profile statistics
                cursor.execute(
                    "SELECT id, total_missions, victories, defeats, best_steps FROM operatives WHERE username = ? COLLATE NOCASE;",
                    (cleaned_name,)
                )
                op = cursor.fetchone()
                if op:
                    new_missions = (op["total_missions"] or 0) + 1
                    new_victories = (op["victories"] or 0) + (1 if is_victory else 0)
                    new_defeats = (op["defeats"] or 0) + (0 if is_victory else 1)
                    curr_best = op["best_steps"]
                    new_best = steps_val if is_victory and (curr_best is None or steps_val < curr_best) else curr_best
                    cursor.execute(
                        """
                        UPDATE operatives
                        SET total_missions = ?, victories = ?, defeats = ?, best_steps = ?, last_login = datetime('now')
                        WHERE id = ?;
                        """,
                        (new_missions, new_victories, new_defeats, new_best, op["id"])
                    )
                else:
                    new_victories = 1 if is_victory else 0
                    new_defeats = 0 if is_victory else 1
                    new_best = steps_val if is_victory else None
                    cursor.execute(
                        """
                        INSERT INTO operatives (username, total_missions, victories, defeats, best_steps, last_login)
                        VALUES (?, 1, ?, ?, ?, datetime('now'));
                        """,
                        (cleaned_name, new_victories, new_defeats, new_best)
                    )

                conn.commit()
                return last_id
            finally:
                conn.close()

    def get_best_victory_steps(self, player_name: Optional[str] = None) -> Optional[int]:
        """
        Retrieve the minimum step count achieved in any successful VICTORY run.

        Args:
            player_name: Optional player name filter. If None, returns the global all-time best.

        Returns:
            The minimum step count as an integer, or None if no victory records exist.
        """
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
