"""
DatabaseManager: Handles SQLite database operations for dungeon_records.db.

This module provides persistent storage for match history, tracking player names,
step counts, match results (VICTORY or DEFEAT), and timestamps. It also queries
all-time best records (minimum steps for VICTORY runs) for the HUD and Home screen.
Thread-safety is guaranteed using a threading lock.
"""

import sqlite3
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any


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
        Create the 'game_history' table if it does not already exist.
        Schema:
            id: INTEGER PRIMARY KEY AUTOINCREMENT
            player_name: TEXT (Player handle)
            steps: INTEGER (Total moves taken in the run)
            result: TEXT ('VICTORY' or 'DEFEAT')
            timestamp: DATETIME (UTC timestamp of record creation)
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
                conn.commit()
            finally:
                conn.close()

    def save_match_result(self, player_name: str, steps: int, result: str) -> int:
        """
        Persist a completed match result to the database.

        Args:
            player_name: The name or callsign of the operative.
            steps: Total number of steps executed during the mission.
            result: Outcome of the mission ('VICTORY' or 'DEFEAT').

        Returns:
            The primary key row ID of the inserted record.
        """
        cleaned_name = player_name.strip() if player_name and player_name.strip() else "OPERATIVE"
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO game_history (player_name, steps, result, timestamp)
                    VALUES (?, ?, ?, datetime('now'));
                    """,
                    (cleaned_name, int(steps), result.upper()),
                )
                conn.commit()
                return cursor.lastrowid
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
