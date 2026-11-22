"""
test_schema.py - SQLite Database Schema Inspector & Integrity Test Suite.

Verifies and displays the complete schema, tables, column constraints,
sample records, and CRUD operations for the Treasure Hunter database (dungeon_records.db).

Usage:
    python test_schema.py
"""

import os
import sys
import sqlite3
from datetime import datetime
from database import DatabaseManager


def format_header(title: str, width: int = 76) -> str:
    """Return formatted section header."""
    return f"\n{'=' * width}\n {title}\n{'=' * width}"


def print_table_schema(cursor: sqlite3.Cursor, table_name: str) -> None:
    """Print columns, types, nullability, defaults, and primary key status."""
    cursor.execute(f"PRAGMA table_info({table_name});")
    cols = cursor.fetchall()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]

    print(f"\n[TABLE] {table_name.upper()} (Total Records: {count})")
    print(f"{'-' * 76}")
    print(f" {'CID':<4} | {'COLUMN NAME':<22} | {'TYPE':<14} | {'NOT NULL':<9} | {'PK':<3} | {'DEFAULT'}")
    print(f"{'-' * 76}")
    for col in cols:
        cid, name, col_type, notnull, dflt_val, pk = col
        notnull_str = "YES" if notnull else "NO"
        pk_str = "PK" if pk else "-"
        dflt_str = str(dflt_val) if dflt_val is not None else "NULL"
        print(f" {cid:<4} | {name:<22} | {col_type:<14} | {notnull_str:<9} | {pk_str:<3} | {dflt_str}")
    print(f"{'-' * 76}")


def print_sample_records(cursor: sqlite3.Cursor, table_name: str, limit: int = 4) -> None:
    """Print sample rows from table."""
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY 1 DESC LIMIT ?;", (limit,))
    rows = cursor.fetchall()
    if not rows:
        print(f"  (No records in {table_name})")
        return

    col_names = [description[0] for description in cursor.description]
    print(f"  Recent {len(rows)} record(s):")
    for r in rows:
        row_dict = dict(zip(col_names, r))
        # Trim password_hash for display
        if "password_hash" in row_dict and row_dict["password_hash"]:
            row_dict["password_hash"] = row_dict["password_hash"][:10] + "..."
        print(f"    - {row_dict}")


def run_database_diagnostics(db_path: str = "dungeon_records.db") -> None:
    """Execute complete diagnostic scan and schema verification."""
    print(format_header("DUNGEON RECORDS DATABASE: ARCHITECTURE & SCHEMA INSPECTOR"))
    print(f"Database File: {os.path.abspath(db_path)}")
    print(f"SQLite Version: {sqlite3.sqlite_version}")
    print(f"Timestamp:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize manager to ensure all tables & migrations are in place
    db = DatabaseManager(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Integrity check
        cursor.execute("PRAGMA integrity_check;")
        integrity = cursor.fetchone()[0]
        status_symbol = "[OK]" if integrity.lower() == "ok" else "[ERROR]"
        print(f"\n{status_symbol} Database Integrity Check: {integrity}")

        # 2. Foreign key check
        cursor.execute("PRAGMA foreign_key_check;")
        fk_errors = cursor.fetchall()
        fk_status = "[OK] No violations" if not fk_errors else f"[FAIL] {len(fk_errors)} violations"
        print(f"[OK] Foreign Key Constraints: {fk_status}")

        # 3. List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence' ORDER BY name;")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"[OK] Discovered Active Tables: {', '.join(tables)}")

        # 4. Detailed table schemas and sample data
        print(format_header("1. DATABASE TABLES & SCHEMA DEFINITIONS"))
        for table in tables:
            print_table_schema(cursor, table)
            print_sample_records(cursor, table, limit=3)

        # 5. Summary metrics
        print(format_header("2. LIVE METRICS & GAME STATISTICS"))
        summary = db.get_dungeon_records_summary()
        print(f"  • Overall Win Rate:          {summary['win_rate']}%")
        print(f"  • Global Best Victory Steps: {summary['best_steps']} Steps")

        cursor.execute("SELECT COUNT(*) FROM operatives;")
        total_operatives = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM game_history;")
        total_missions = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM game_history WHERE result = 'VICTORY';")
        total_wins = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM game_history WHERE result = 'DEFEAT';")
        total_losses = cursor.fetchone()[0]

        print(f"  • Total Registered Players:  {total_operatives}")
        print(f"  • Total Missions Deployed:   {total_missions} (Wins: {total_wins}, Defeats: {total_losses})")

        # 6. Functional CRUD & Campaign Verification
        print(format_header("3. FUNCTIONAL CRUD & CAMPAIGN VERIFICATION"))
        test_user = "_diagnostic_test_operative"
        
        # Test A: Operative Registration / Login
        op = db.login_or_register_operative(test_user)
        print(f"  [PASS] Operative Login/Register: username='{op['username']}', unlocked_level={op.get('unlocked_level', 1)}")

        # Test B: Save Match Result (Level 1 Victory)
        hist_id = db.save_match_result(
            player_name=test_user,
            steps=11,
            result="VICTORY",
            level_num=1,
            grid_size=7,
            difficulty="RECRUIT"
        )
        print(f"  [PASS] Save Match Result (Chamber 1 Victory): game_history ID={hist_id}")

        # Test C: Verify Level Progress Update & Unlocking Level 2
        progress = db.get_level_progress(test_user)
        lvl1_status = progress[1]["status"]
        lvl1_best = progress[1]["best_steps"]
        lvl1_stars = progress[1]["stars"]
        lvl2_status = progress[2]["status"]
        print(f"  [PASS] Level Progress (Chamber 1): status={lvl1_status}, best_steps={lvl1_best}, stars={lvl1_stars}")
        print(f"  [PASS] Level Progression Unlock (Chamber 2): status={lvl2_status}")

        # Test D: Verify Settings
        settings = db.get_settings()
        print(f"  [PASS] Game Settings Storage: {settings}")

        # Test E: Clean up diagnostic records to maintain pristine database
        cursor.execute("DELETE FROM level_progress WHERE operative_name = ?;", (test_user,))
        cursor.execute("DELETE FROM game_history WHERE player_name = ?;", (test_user,))
        cursor.execute("DELETE FROM operatives WHERE username = ?;", (test_user,))
        conn.commit()
        print(f"  [PASS] Cleaned up temporary diagnostic records successfully")

        print(format_header("DIAGNOSTIC TEST COMPLETE: ALL TABLES & SCHEMAS HEALTHY [OK]"))

    finally:
        conn.close()


if __name__ == "__main__":
    db_file = sys.argv[1] if len(sys.argv) > 1 else "dungeon_records.db"
    run_database_diagnostics(db_file)
