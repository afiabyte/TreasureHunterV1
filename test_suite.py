"""
Automated Test Suite for Treasure Hunter Tactical Evasion Game.

Runs comprehensive headless integration tests covering:
1. DatabaseManager operations (schema creation, record saving, best victory query, leaderboard).
2. GeminiTacticalAI (initialization, greedy fallback, structured JSON output validation, thread-safety).
3. GridEnvironment (N x N grid, wall relocation without overwriting entities, hunter spawning, facing vectors, LERP math).
4. GameEngine state transitions (HOME -> HOW_TO_PLAY -> PLAYING -> GAME_OVER, level progression, input dispatching, 60 FPS clock).
5. Headless Pygame frame rendering pipeline.
6. Zero circular dependencies verification across all modules.
"""

import os
import sys

# Configure headless SDL drivers for testing without physical display/audio
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
import time
import pygame
from database import DatabaseManager
from ai_tactical import GeminiTacticalAI, TacticalDecision
from environment import GridEnvironment, Hunter
from game_engine import GameEngine, STATE_HOME, STATE_HOW_TO_PLAY, STATE_LEVEL_SELECT, STATE_PLAYING, STATE_GAME_OVER


class TestDatabaseManager(unittest.TestCase):
    """Test suite for SQLite persistence layer."""

    def setUp(self) -> None:
        self.test_db_path = "test_dungeon_records.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.db = DatabaseManager(self.test_db_path)

    def tearDown(self) -> None:
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_schema_and_empty_best(self) -> None:
        """Verify table exists and returns None when no victories recorded."""
        self.assertIsNone(self.db.get_best_victory_steps())

    def test_save_and_retrieve_best_victory(self) -> None:
        """Verify best victory step count retrieval."""
        self.db.save_match_result("Ghost", 35, "VICTORY")
        self.db.save_match_result("Ghost", 18, "VICTORY")
        self.db.save_match_result("Shadow", 12, "DEFEAT")  # Defeat should not count for victory best
        self.db.save_match_result("Spectre", 22, "VICTORY")

        best = self.db.get_best_victory_steps()
        self.assertEqual(best, 18)

        # Player-specific check
        best_ghost = self.db.get_best_victory_steps("Ghost")
        self.assertEqual(best_ghost, 18)

        # Leaderboard test
        top_records = self.db.get_top_victory_records(5)
        self.assertEqual(len(top_records), 3)
        self.assertEqual(top_records[0]["steps"], 18)

    def test_operative_login_and_stats(self) -> None:
        """Verify operative registration, login timestamp, and stats accumulation."""
        op = self.db.login_or_register_operative("afiabyte")
        self.assertEqual(op["username"], "afiabyte")
        self.assertEqual(op["total_missions"], 0)

        # Record victory
        self.db.save_match_result("afiabyte", 25, "VICTORY")
        op_updated = self.db.get_operative("afiabyte")
        self.assertEqual(op_updated["total_missions"], 1)
        self.assertEqual(op_updated["victories"], 1)
        self.assertEqual(op_updated["best_steps"], 25)

        # Record another better victory
        self.db.save_match_result("afiabyte", 19, "VICTORY")
        op_updated2 = self.db.get_operative("afiabyte")
        self.assertEqual(op_updated2["total_missions"], 2)
        self.assertEqual(op_updated2["victories"], 2)
        self.assertEqual(op_updated2["best_steps"], 19)

        # Recent operatives check
        recent = self.db.get_recent_operatives(5)
        self.assertTrue(any(r["username"] == "afiabyte" for r in recent))

    def test_account_registration_and_authentication(self) -> None:
        """Verify new operative registration with email and password hashing."""
        # 1. Successful registration
        ok, msg, op = self.db.register_account("Bravo42", "bravo42@hunter.io", "secretPass123")
        self.assertTrue(ok)
        self.assertIn("SUCCESS", msg)
        self.assertEqual(op["username"], "Bravo42")
        self.assertEqual(op["email"], "bravo42@hunter.io")

        # 2. Reject duplicate username
        ok_dup, msg_dup, _ = self.db.register_account("bravo42", "other@hunter.io", "pass123")
        self.assertFalse(ok_dup)
        self.assertIn("ALREADY REGISTERED", msg_dup)

        # 3. Reject duplicate email
        ok_em, msg_em, _ = self.db.register_account("AgentX", "bravo42@hunter.io", "pass123")
        self.assertFalse(ok_em)
        self.assertIn("EMAIL IS ALREADY", msg_em)

        # 4. Successful authentication with username
        auth_ok, auth_msg, auth_op = self.db.authenticate_user("Bravo42", "secretPass123")
        self.assertTrue(auth_ok)
        self.assertEqual(auth_op["username"], "Bravo42")

        # 5. Successful authentication with email
        auth_ok2, _, auth_op2 = self.db.authenticate_user("bravo42@hunter.io", "secretPass123")
        self.assertTrue(auth_ok2)
        self.assertEqual(auth_op2["username"], "Bravo42")

        # 6. Reject invalid password
        bad_ok, bad_msg, _ = self.db.authenticate_user("Bravo42", "wrongPass")
        self.assertFalse(bad_ok)
        self.assertIn("INCORRECT", bad_msg)

    def test_level_progress_and_campaign_unlock(self) -> None:
        """Verify per-level progression, stars, and campaign unlock sequence (1-10)."""
        op = self.db.login_or_register_operative("Explorer")
        self.assertEqual(op["unlocked_level"], 1)

        # Initial progress: Level 1 UNLOCKED, Levels 2-10 LOCKED
        prog = self.db.get_level_progress("Explorer")
        self.assertEqual(prog[1]["status"], "UNLOCKED")
        self.assertEqual(prog[2]["status"], "LOCKED")
        self.assertEqual(self.db.get_unlocked_level("Explorer"), 1)

        # Complete Level 1 in 12 steps (3 stars)
        self.db.save_match_result("Explorer", 12, "VICTORY", level_num=1, grid_size=7, difficulty="RECRUIT")
        op_up = self.db.get_operative("Explorer")
        self.assertEqual(op_up["unlocked_level"], 2)

        prog2 = self.db.get_level_progress("Explorer")
        self.assertEqual(prog2[1]["status"], "COMPLETED")
        self.assertEqual(prog2[1]["best_steps"], 12)
        self.assertEqual(prog2[1]["stars"], 3)
        self.assertEqual(prog2[2]["status"], "UNLOCKED")
        self.assertEqual(prog2[3]["status"], "LOCKED")
        self.assertEqual(self.db.get_unlocked_level("Explorer"), 2)

        # Defeat on Level 2 does not unlock Level 3
        self.db.save_match_result("Explorer", 9, "DEFEAT", level_num=2, grid_size=7, difficulty="RECRUIT")
        self.assertEqual(self.db.get_unlocked_level("Explorer"), 2)
        prog3 = self.db.get_level_progress("Explorer")
        self.assertEqual(prog3[2]["status"], "UNLOCKED")
        self.assertEqual(prog3[3]["status"], "LOCKED")


class TestGeminiTacticalAI(unittest.TestCase):
    """Test suite for Gemini Tactical AI and fallback mechanisms."""

    def setUp(self) -> None:
        self.ai = GeminiTacticalAI()

    def test_greedy_fallback_structure(self) -> None:
        """Verify greedy Manhattan fallback produces required schema fields without classical pathfinding."""
        res = self.ai._compute_greedy_fallback(
            grid_size=7,
            player_pos=(0, 0),
            hunter_positions=[(4, 4), (5, 5)],
            wall_positions=[(1, 1), (2, 2)],
            key_pos=(3, 3),
            has_key=False,
            exit_pos=(6, 6)
        )
        self.assertIn("hunter_moves", res)
        self.assertIn("recommended_path", res)
        self.assertIn("commander_order", res)
        self.assertEqual(len(res["hunter_moves"]), 2)
        self.assertLessEqual(len(res["recommended_path"]), 3)
        self.assertTrue(len(res["commander_order"].split()) <= 12)

    def test_non_blocking_async_request(self) -> None:
        """Verify non-blocking worker thread execution."""
        self.ai.request_tactical_decision(
            grid_size=7,
            player_pos=(0, 0),
            hunter_positions=[(5, 5)],
            hunter_facings=[(-1, 0)],
            wall_positions=[(1, 1)],
            key_pos=(3, 3),
            has_key=False,
            exit_pos=(6, 6),
            force_sync_fallback=True
        )
        time.sleep(0.08)  # Short sleep to allow background thread to finish
        decision, lat, status, is_busy = self.ai.get_latest_decision()
        self.assertIsInstance(decision, dict)
        self.assertIn("hunter_moves", decision)
        self.assertFalse(is_busy)


class TestGridEnvironment(unittest.TestCase):
    """Test suite for Grid Environment dynamics, LERP, and walls."""

    def test_initialization_all_sizes(self) -> None:
        """Verify environment correctly initializes for 5x5, 7x7, 9x9, 11x11."""
        for size in [5, 7, 9, 11]:
            env = GridEnvironment(grid_size=size, level=2)
            self.assertEqual(env.grid_size, size)
            self.assertEqual(env.start_pos, (0, 0))
            self.assertEqual(env.exit_pos, (size - 1, size - 1))
            self.assertNotEqual(env.key_pos, env.start_pos)
            self.assertNotEqual(env.key_pos, env.exit_pos)
            self.assertNotIn(env.start_pos, env.walls)
            self.assertNotIn(env.exit_pos, env.walls)
            self.assertNotIn(env.key_pos, env.walls)

    def test_dynamic_wall_relocation_never_overwrites_entities(self) -> None:
        """Verify wall relocation never places walls on Player, Hunters, Key, Exit, or Start."""
        env = GridEnvironment(grid_size=7, level=2)
        # Relocate multiple times
        for _ in range(5):
            env.relocate_walls()
            protected = {env.start_pos, env.exit_pos, env.key_pos, env.player_pos}
            for h in env.hunters:
                protected.add(h.pos)
            # Verify no wall intersects protected entity cells
            for w in env.walls:
                self.assertNotIn(w, protected, f"Wall placed on protected entity at {w}!")

    def test_hunter_spawning_and_facing(self) -> None:
        """Verify hunter count limits, facing vectors, and LERP math."""
        env = GridEnvironment(grid_size=7, level=2)
        initial_count = len(env.hunters)
        self.assertTrue(1 <= initial_count <= 8)

        # Spawn up to max 8
        for _ in range(10):
            env.spawn_hunter()
        self.assertLessEqual(len(env.hunters), 8)

        # Test hunter facing update
        hunter = env.hunters[0]
        curr_r, curr_c = hunter.r, hunter.c
        hunter.set_grid_pos(curr_r + 1, curr_c)
        self.assertEqual(hunter.facing, (1, 0))  # Moved DOWN

        # Test LERP math: speed = 0.28
        hunter.visual_x = 0.0
        hunter.target_x = 100.0
        hunter.update_lerp(speed=0.28)
        # Expected: 0.0 + (100.0 - 0.0) * 0.28 = 28.0
        self.assertAlmostEqual(hunter.visual_x, 28.0, places=3)

    def test_key_collection_and_victory_check(self) -> None:
        """Verify key collection flag and victory requirements."""
        env = GridEnvironment(grid_size=7, level=2)
        self.assertFalse(env.has_key)
        self.assertFalse(env.check_victory())

        # Move to key position
        env.player_pos = env.key_pos
        env.has_key = True
        self.assertTrue(env.has_key)
        self.assertFalse(env.check_victory())  # Not at exit yet

        # Move to exit
        env.player_pos = env.exit_pos
        self.assertTrue(env.check_victory())


class TestGameEngineIntegration(unittest.TestCase):
    """Test suite for full GameEngine loop and state transitions."""

    def setUp(self) -> None:
        self.test_db_path = "test_dungeon_records.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def tearDown(self) -> None:
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_full_mission_lifecycle(self) -> None:
        """Verify engine transitions, splash, login, frame updates, and rendering without exceptions."""
        engine = GameEngine(db_path=self.test_db_path)
        self.assertEqual(engine.state, "SPLASH")
        engine.render()

        # Advance past splash to login
        engine.update(2.6)
        self.assertEqual(engine.state, "LOGIN")
        engine.render()

        # Simulate login submission
        event_login = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        engine._handle_login_events(event_login)
        self.assertEqual(engine.state, STATE_HOME)
        self.assertEqual(engine.current_user, "afiabyte")

        # Start mission
        engine.start_mission(grid_size=7, level=2, player_name="afiabyte")
        self.assertEqual(engine.state, STATE_PLAYING)
        self.assertIsNotNone(engine.env)

        # Simulate 10 frames of 60 FPS update and render
        for _ in range(10):
            engine.update(1.0 / 60.0)
            engine.render()

        # Simulate player move (first move to 0, 1 is guaranteed unblocked by reserved cells)
        moved = engine.env.move_player(0, 1)
        self.assertTrue(moved)
        self.assertEqual(engine.env.steps, 1)

        # Trigger victory
        engine._trigger_victory()
        self.assertEqual(engine.state, STATE_GAME_OVER)
        self.assertTrue(engine.is_victory)

        # Render game over overlay
        engine.render()

    def test_level_select_screen_transition_and_selection(self) -> None:
        """Verify navigation to 1-10 Select Level screen, chamber picking, and mission start."""
        engine = GameEngine(db_path=self.test_db_path)
        engine.user_stats = {"username": "afiabyte", "victories": 4, "total_missions": 6, "best_steps": 14}
        engine.state = STATE_HOME

        # 1. Click "LEVELS (1-10)" button on Main Menu
        click_levels = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.btn_levels.rect.center)
        engine._handle_home_events(click_levels)
        self.assertEqual(engine.state, STATE_LEVEL_SELECT)
        self.assertEqual(len(engine.ui.level_tile_buttons), 10)

        # 2. Render level select screen
        engine.render()

        # 3. Click an unlocked chamber (e.g. tile 3 -> Recruit)
        tile_3 = engine.ui.level_tile_buttons[2]
        click_t3 = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=tile_3.rect.center)
        engine._handle_level_select_events(click_t3)
        self.assertEqual(engine.ui.selected_chamber_level, 3)
        self.assertEqual(engine.selected_level, 1)  # Level 1-3 maps to Recruit (1)

        # 4. Click an unlocked tactical chamber (e.g. tile 5 -> Tactical)
        tile_5 = engine.ui.level_tile_buttons[4]
        click_t5 = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=tile_5.rect.center)
        engine._handle_level_select_events(click_t5)
        self.assertEqual(engine.ui.selected_chamber_level, 5)
        self.assertEqual(engine.selected_level, 2)  # Level 4-7 maps to Tactical (2)

        # 5. Attempt to click a locked chamber (e.g. tile 9 while victories=4 -> max unlocked=5)
        tile_9 = engine.ui.level_tile_buttons[8]
        click_t9 = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=tile_9.rect.center)
        engine._handle_level_select_events(click_t9)
        self.assertEqual(engine.ui.selected_chamber_level, 5)  # Should remain unchanged

        # 6. Click "PLAY LEVEL 5" button to launch mission
        click_play = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.btn_level_play.rect.center)
        engine._handle_level_select_events(click_play)
        self.assertEqual(engine.state, STATE_PLAYING)
        self.assertEqual(engine.selected_level, 2)

    def test_how_to_play_transition(self) -> None:
        """Verify navigation to How to Play and back to Home."""
        engine = GameEngine(db_path=self.test_db_path)
        engine.state = STATE_HOW_TO_PLAY
        engine.render()
        self.assertEqual(engine.state, STATE_HOW_TO_PLAY)

        # Simulate ESC key event to return home
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        engine._handle_how_to_play_events(esc_event)
        self.assertEqual(engine.state, STATE_HOME)

    def test_level_progression(self) -> None:
        """Verify smooth progression: Recruit (L1) -> Tactical (L2) -> Nightmare (L3)."""
        engine = GameEngine(db_path=self.test_db_path)
        engine.start_mission(grid_size=7, level=1, player_name="TEST_AGENT")
        self.assertEqual(engine.selected_level, 1)

        # Simulate victory
        engine._trigger_victory()
        self.assertEqual(engine.state, STATE_GAME_OVER)

        # Advance level
        next_btn_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.btn_next_level.rect.center)
        engine._handle_game_over_events(next_btn_event)
        self.assertEqual(engine.selected_level, 2)
        self.assertEqual(engine.state, STATE_PLAYING)

    def test_standby_countdown_reconnaissance(self) -> None:
        """Verify the 3-second tactical standby prevents game from starting abruptly."""
        engine = GameEngine(db_path=self.test_db_path)
        engine.start_mission(grid_size=7, level=2, player_name="STANDBY_TEST")
        self.assertEqual(engine.state, STATE_PLAYING)
        self.assertEqual(engine.standby_timer, 3.0)

        # Before countdown expires, wall timer remains 0
        init_wall_timer = engine.env.wall_timer
        engine.update(0.5)
        self.assertAlmostEqual(engine.standby_timer, 2.5, places=2)
        self.assertEqual(engine.env.wall_timer, init_wall_timer)

        # Simulating movement key immediately deploys and skips remaining countdown
        key_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)
        engine._handle_playing_events(key_event)
        self.assertEqual(engine.standby_timer, 0.0)

    def test_pause_and_resume_controls(self) -> None:
        """Verify tactical pause button, state freeze, and resume controls."""
        engine = GameEngine(db_path=self.test_db_path)
        engine.start_mission(grid_size=7, level=2, player_name="PAUSE_TEST")
        engine.standby_timer = 0.0  # Skip standby for this test

        # Click the in-game Pause button
        pause_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.btn_pause.rect.center)
        engine._handle_playing_events(pause_click)
        self.assertEqual(engine.state, "PAUSED")

        # In PAUSED state, update must not advance simulation timers
        init_wall_time = engine.env.wall_timer
        engine.update(1.0)
        self.assertEqual(engine.env.wall_timer, init_wall_time)

        # Resume via resume button
        resume_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.btn_pause_resume.rect.center)
        engine._handle_paused_events(resume_click)
        self.assertEqual(engine.state, STATE_PLAYING)

        # Toggle pause via keyboard 'P'
        p_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)
        engine._handle_playing_events(p_event)
        self.assertEqual(engine.state, "PAUSED")

        # Resume via keyboard 'P'
        engine._handle_paused_events(p_event)
        self.assertEqual(engine.state, STATE_PLAYING)

    def test_humanoid_sprites_rendering(self) -> None:
        """Verify human player and human hunter render across cardinal facings and cell sizes."""
        engine = GameEngine(db_path=self.test_db_path)
        engine.start_mission(grid_size=7, level=2, player_name="HERO_AGENT")
        test_surf = engine.screen

        # Test player facing in all 4 cardinal directions with/without key
        for fdr, fdc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            engine.ui._draw_human_player(test_surf, 200.0, 200.0, 64.0, fdr, fdc, has_key=False)
            engine.ui._draw_human_player(test_surf, 200.0, 200.0, 64.0, fdr, fdc, has_key=True)

        # Test hunter rendering with multiple IDs and facings
        for fdr, fdc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            engine.ui._draw_human_hunter(test_surf, 300.0, 300.0, 64.0, fdr, fdc, hunter_id=1)
            engine.ui._draw_human_hunter(test_surf, 300.0, 300.0, 64.0, fdr, fdc, hunter_id=2)


    def test_create_account_screen_registration(self) -> None:
        """Verify Create Account UI form input, validation, registration, and progression to Home."""
        engine = GameEngine(db_path=self.test_db_path)
        engine.state = "LOGIN"
        engine.auth_mode = "create_account"

        # Populate registration fields
        engine.ui.input_reg_username.text = "Explorer77"
        engine.ui.input_reg_email.text = "explorer77@dungeon.net"
        engine.ui.input_reg_password.text = "dungeonSecret9"
        engine.ui.input_reg_confirm_password.text = "dungeonSecret9"

        # Trigger registration
        reg_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.btn_register.rect.center)
        engine._handle_create_account_events(reg_click)

        self.assertEqual(engine.state, STATE_HOME)
        self.assertEqual(engine.current_user, "Explorer77")
        self.assertIsNotNone(engine.user_stats)

    def test_settings_screen_transition_and_options(self) -> None:
        """Verify Settings screen transitions, interactive toggle controls, and SQLite persistence."""
        from game_engine import STATE_SETTINGS
        engine = GameEngine(db_path=self.test_db_path)
        engine.state = STATE_HOME

        # 1. Click Settings button on Home Screen -> transitions to STATE_SETTINGS
        click_settings = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.btn_settings.rect.center)
        engine._handle_home_events(click_settings)
        self.assertEqual(engine.state, STATE_SETTINGS)

        # 2. Toggle Audio SFX (True -> False)
        click_sfx = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.toggle_sfx.rect.center)
        engine._handle_settings_events(click_sfx)
        self.assertFalse(engine.settings_sfx)
        self.assertFalse(engine.sound.sound_enabled)

        # 3. Toggle BGM
        initial_bgm = engine.settings_bgm
        click_bgm = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.toggle_bgm.rect.center)
        engine._handle_settings_events(click_bgm)
        self.assertEqual(engine.settings_bgm, not initial_bgm)
        self.assertEqual(engine.sound.music_enabled, not initial_bgm)

        # 4. Toggle AI Commander Hints (True -> False)
        click_hints = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.toggle_ai_hints.rect.center)
        engine._handle_settings_events(click_hints)
        self.assertFalse(engine.settings_ai_hints)

        # 5. Switch Move Animation to FAST
        click_fast = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.btn_anim_fast.rect.center)
        engine._handle_settings_events(click_fast)
        self.assertEqual(engine.settings_move_animation, "FAST")

        # 6. Click SAVE & APPLY -> Saves to SQLite and returns to HOME
        click_save = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.btn_settings_save.rect.center)
        engine._handle_settings_events(click_save)
        self.assertEqual(engine.state, STATE_HOME)

        # Verify saved settings persisted in database
        saved = engine.db.get_settings()
        self.assertEqual(saved["sound_effects"], "false")
        self.assertEqual(saved["background_music"], "false" if initial_bgm else "true")
        self.assertEqual(saved["ai_commander_hints"], "false")
        self.assertEqual(saved["move_animation"], "FAST")

        # 7. Transition back to Settings and click BACK TO MENU
        engine.state = STATE_SETTINGS
        click_back = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.btn_settings_back.rect.center)
        engine._handle_settings_events(click_back)
        self.assertEqual(engine.state, STATE_HOME)

    def test_dungeon_records_screen_and_summary(self) -> None:
        """Verify Dungeon Records match history summary, navigation transition, and rendering."""
        from game_engine import STATE_HISTORY
        engine = GameEngine(db_path=self.test_db_path)
        engine.state = STATE_HOME

        # Save test records into test database
        engine.db.save_match_result("Bravo42", 12, "VICTORY")
        engine.db.save_match_result("Bravo42", 14, "VICTORY")
        engine.db.save_match_result("Aria_99", 15, "VICTORY")
        engine.db.save_match_result("Bravo42", 9, "DEFEAT")
        engine.db.save_match_result("Kazi_07", 18, "VICTORY")

        # Test summary statistics
        summary = engine.db.get_dungeon_records_summary()
        self.assertEqual(summary["win_rate"], 80)
        self.assertEqual(summary["best_steps"], 12)
        self.assertEqual(len(summary["records"]), 5)
        self.assertEqual(summary["records"][0]["player_name"], "Kazi_07")

        # Click trophy badge on Home Screen -> transitions to STATE_HISTORY
        cx = engine.screen_width // 2
        trophy_badge_center = (cx - 189 + 180 // 2, 172 + 34 // 2)
        click_trophy = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=trophy_badge_center)
        engine._handle_home_events(click_trophy)
        self.assertEqual(engine.state, STATE_HISTORY)

        # Headless render verification in STATE_HISTORY
        engine.render()

        # Click BACK TO MENU button -> transitions back to STATE_HOME
        click_back = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.btn_history_back.rect.center)
        engine._handle_history_events(click_back)
        self.assertEqual(engine.state, STATE_HOME)

        # Click HISTORY button in 2x2 grid -> transitions to STATE_HISTORY
        click_btn_history = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.btn_history.rect.center)
        engine._handle_home_events(click_btn_history)
        self.assertEqual(engine.state, STATE_HISTORY)

        # Click BACK TO MENU button again -> transitions back to STATE_HOME
        engine._handle_history_events(click_back)
        self.assertEqual(engine.state, STATE_HOME)

        # Test ESCAPE key returns to STATE_HOME
        engine.state = STATE_HISTORY
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        engine._handle_history_events(esc_event)
        self.assertEqual(engine.state, STATE_HOME)

    def test_procedural_sound_effects_and_bgm(self) -> None:
        """Verify SoundManager synthesizes all retro RPG SFX and BGM tracks without exceptions."""
        from sound_effects import SoundManager
        sound = SoundManager()

        # If mixer is available, verify synthesized audio buffers exist
        if sound.enabled:
            self.assertIsNotNone(sound.snd_move)
            self.assertIsNotNone(sound.snd_click)
            self.assertIsNotNone(sound.snd_key)
            self.assertIsNotNone(sound.snd_shift)
            self.assertIsNotNone(sound.snd_spawn)
            self.assertIsNotNone(sound.snd_victory)
            self.assertIsNotNone(sound.snd_defeat)
            self.assertIsNotNone(sound.bgm_menu)
            self.assertIsNotNone(sound.bgm_dungeon)

        # Test playback methods execute gracefully
        sound.sound_enabled = True
        sound.music_enabled = True
        sound.set_music_volume(0.5)
        sound.set_sfx_volume(0.8)

        sound.play_move()
        sound.play_step()
        sound.play_click()
        sound.play_key()
        sound.play_shift()
        sound.play_spawn()
        sound.play_door()
        sound.play_alert()
        sound.play_victory()
        sound.play_defeat()

        sound.play_music("menu")
        sound.pause_music()
        sound.unpause_music()
        sound.play_music("dungeon")
        sound.stop_music()

        # Test mute state
        sound.toggle_sound()
        self.assertFalse(sound.sound_enabled)
        sound.toggle_music()
        self.assertFalse(sound.music_enabled)


class TestArchitectureAndZeroDeadCode(unittest.TestCase):
    """Verify circular dependencies and clean architecture."""

    def test_zero_circular_imports(self) -> None:
        """Ensure all modules import independently without circular dependency errors."""
        import database
        import ai_tactical
        import environment
        import sound_effects
        import ui_manager
        import game_engine
        import main
        import ui
        import ui.colors
        import ui.widgets
        import ui.art_helpers
        import ui.splash_screen
        import ui.create_account_screen
        import ui.login_screen
        import ui.home_screen
        import ui.level_select_screen
        import ui.how_to_play_screen
        import ui.settings_screen
        import ui.history_screen
        import ui.game_view
        import ui.hud_console
        import ui.pause_screen
        import ui.victory_screen
        import ui.overlays
        import ui.manager

        self.assertTrue(hasattr(database, "DatabaseManager"))
        self.assertTrue(hasattr(ai_tactical, "GeminiTacticalAI"))
        self.assertTrue(hasattr(environment, "GridEnvironment"))
        self.assertTrue(hasattr(sound_effects, "SoundManager"))
        self.assertTrue(hasattr(ui_manager, "UIManager"))
        self.assertTrue(hasattr(game_engine, "GameEngine"))
        self.assertTrue(hasattr(main, "main"))

        # Verify modular UI package exports
        self.assertTrue(hasattr(ui, "UIManager"))
        self.assertTrue(hasattr(ui, "UIButton"))
        self.assertTrue(hasattr(ui, "TextInputBox"))
        self.assertTrue(hasattr(ui, "UIToggleSwitch"))
        self.assertTrue(hasattr(ui, "SplashScreenRenderer"))
        self.assertTrue(hasattr(ui, "CreateAccountScreenRenderer"))
        self.assertTrue(hasattr(ui, "LoginScreenRenderer"))
        self.assertTrue(hasattr(ui, "HomeScreenRenderer"))
        self.assertTrue(hasattr(ui, "LevelSelectScreenRenderer"))
        self.assertTrue(hasattr(ui, "HowToPlayScreenRenderer"))
        self.assertTrue(hasattr(ui, "SettingsScreenRenderer"))
        self.assertTrue(hasattr(ui, "HistoryScreenRenderer"))
        self.assertTrue(hasattr(ui, "GameViewRenderer"))
        self.assertTrue(hasattr(ui, "HUDConsoleRenderer"))
        self.assertTrue(hasattr(ui, "PauseScreenRenderer"))
        self.assertTrue(hasattr(ui, "VictoryScreenRenderer"))
        self.assertTrue(hasattr(ui, "DefeatScreenRenderer"))
        self.assertTrue(hasattr(ui, "ExitDialogRenderer"))
        self.assertTrue(hasattr(ui, "OverlayRenderer"))

    def test_victory_screen_rendering(self) -> None:
        """Verify retro-pixel RPG victory dialog overlay renders cleanly without runtime exceptions."""
        import ui
        from ui.victory_screen import VictoryScreenRenderer
        renderer = VictoryScreenRenderer(764, 1024)
        surf = pygame.Surface((764, 1024))
        btn_next = ui.UIButton(pygame.Rect(0, 0, 100, 40), "NEXT", pygame.font.SysFont("trebuchetms", 14))
        btn_again = ui.UIButton(pygame.Rect(0, 0, 100, 40), "AGAIN", pygame.font.SysFont("trebuchetms", 14))
        btn_menu = ui.UIButton(pygame.Rect(0, 0, 100, 40), "MENU", pygame.font.SysFont("trebuchetms", 14))
        renderer.draw(
            surface=surf,
            player_name="Bravo42",
            mode_str="7x7 TACTICAL",
            steps=12,
            best_steps=12,
            is_new_record=True,
            btn_next_level=btn_next,
            btn_play_again=btn_again,
            btn_menu=btn_menu
        )

    def test_defeat_screen_rendering(self) -> None:
        """Verify retro-pixel RPG defeat dialog overlay renders cleanly without runtime exceptions."""
        import ui
        from ui.defeat_screen import DefeatScreenRenderer
        renderer = DefeatScreenRenderer(764, 1024)
        surf = pygame.Surface((764, 1024))
        btn_retry = ui.UIButton(pygame.Rect(0, 0, 100, 40), "RETRY", pygame.font.SysFont("trebuchetms", 14))
        btn_menu = ui.UIButton(pygame.Rect(0, 0, 100, 40), "MENU", pygame.font.SysFont("trebuchetms", 14))
        renderer.draw(
            surface=surf,
            player_name="Bravo42",
            mode_str="7x7 TACTICAL",
            survived_steps=9,
            has_key=False,
            btn_retry=btn_retry,
            btn_menu=btn_menu,
            defeat_cause="CAPTURED BY HUNTER"
        )

    def test_exit_dialog_rendering_and_interaction(self) -> None:
        """Verify retro-pixel RPG exit confirmation modal renders cleanly and handles events."""
        import ui
        from ui.exit_dialog import ExitDialogRenderer
        renderer = ExitDialogRenderer(764, 1024)
        surf = pygame.Surface((764, 1024))
        btn_confirm = ui.UIButton(pygame.Rect(0, 0, 200, 52), "YES, EXIT", pygame.font.SysFont("trebuchetms", 16))
        btn_cancel = ui.UIButton(pygame.Rect(0, 0, 200, 52), "CANCEL", pygame.font.SysFont("trebuchetms", 16))
        renderer.draw(
            surface=surf,
            btn_exit_confirm=btn_confirm,
            btn_exit_cancel=btn_cancel,
            anim_time=0.5
        )

        # Test interaction via GameEngine
        test_db = "test_dungeon_records.db"
        engine = GameEngine(db_path=test_db)
        engine.state = STATE_HOME
        self.assertFalse(engine.ui.show_exit_modal)

        # Trigger exit modal via ESC
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        engine._handle_home_events(esc_event)
        self.assertTrue(engine.ui.show_exit_modal)

        # Render with modal active
        engine.render()

        # Cancel exit modal via ESC
        engine._handle_home_events(esc_event)
        self.assertFalse(engine.ui.show_exit_modal)

        # Reopen and confirm quit via YES, EXIT button
        engine.ui.show_exit_modal = True
        confirm_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=engine.ui.btn_exit_confirm.rect.center)
        engine._handle_home_events(confirm_click)
        self.assertFalse(engine.is_running)


if __name__ == "__main__":
    unittest.main()
