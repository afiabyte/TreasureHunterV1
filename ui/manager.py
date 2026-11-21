"""
UI Manager: Master coordinator for state views, grid rendering, HUD, and overlays.
Integrates all modular screen renderers in the ui package.
"""

import math
from typing import Tuple, List, Dict, Any, Optional
import pygame

from .colors import (
    COLOR_BG,
    COLOR_GRID_BG,
    COLOR_GRID_LINE,
    COLOR_WALL,
    COLOR_WALL_BORDER,
    COLOR_WALL_ACCENT,
    COLOR_PLAYER_CORE,
    COLOR_PLAYER_GLOW,
    COLOR_PLAYER_SHIELD,
    COLOR_HUNTER_CORE,
    COLOR_HUNTER_BODY,
    COLOR_HUNTER_CONE,
    COLOR_HUNTER_GLOW,
    COLOR_KEY_CORE,
    COLOR_KEY_GOLD,
    COLOR_KEY_GLOW,
    COLOR_EXIT_CORE,
    COLOR_EXIT_PORTAL,
    COLOR_EXIT_GLOW,
    COLOR_BREADCRUMB_RING,
    COLOR_BREADCRUMB_FILL,
    COLOR_GUIDE_ARROW,
    COLOR_HUD_BG,
    COLOR_HUD_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_ACCENT_CYAN,
    COLOR_TEXT_ACCENT_GREEN,
    COLOR_TEXT_ACCENT_AMBER,
    COLOR_TEXT_ACCENT_RED,
    COLOR_TEXT_ACCENT_MAGENTA,
    COLOR_TEXT_ACCENT_PURPLE,
    COLOR_BTN_NORMAL,
    COLOR_BTN_HOVER,
    COLOR_BTN_ACTIVE,
    COLOR_BTN_BORDER,
    COLOR_BTN_BORDER_HOVER,
)

from .widgets import UIButton, TextInputBox, UIToggleSwitch
from .art_helpers import (
    draw_dungeon_background,
    draw_parchment_chassis,
    draw_royal_crown,
    draw_adventure_title,
    draw_padlock,
)
from .splash_screen import SplashScreenRenderer
from .create_account_screen import CreateAccountScreenRenderer
from .login_screen import LoginScreenRenderer
from .home_screen import HomeScreenRenderer
from .level_select_screen import LevelSelectScreenRenderer
from .how_to_play_screen import HowToPlayScreenRenderer
from .settings_screen import SettingsScreenRenderer
from .history_screen import HistoryScreenRenderer
from .game_view import GameViewRenderer
from .hud_console import HUDConsoleRenderer
from .pause_screen import PauseScreenRenderer
from .victory_screen import VictoryScreenRenderer
from .overlays import OverlayRenderer


class UIManager:
    """Coordinates UI state views, grid rendering, HUD, and tactical overlays."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Fonts
        pygame.font.init()
        self.font_title = pygame.font.SysFont("consolas,couriernew,monospace", 28, bold=True)
        self.font_header = pygame.font.SysFont("consolas,couriernew,monospace", 20, bold=True)
        self.font_body = pygame.font.SysFont("consolas,couriernew,monospace", 14)
        self.font_bold = pygame.font.SysFont("consolas,couriernew,monospace", 14, bold=True)
        self.font_small = pygame.font.SysFont("consolas,couriernew,monospace", 11)
        self.font_badge = pygame.font.SysFont("trebuchetms,tahoma,arial", 14, bold=True)

        # Fantasy Adventure Main Menu Fonts
        self.font_title_top = pygame.font.SysFont("georgia,timesnewroman,palatino", 48, bold=True)
        self.font_title_bot = pygame.font.SysFont("georgia,timesnewroman,palatino", 54, bold=True)
        self.font_subtitle = pygame.font.SysFont("georgia,timesnewroman,palatino", 24, bold=True)
        self.font_pixel_med = pygame.font.SysFont("consolas,couriernew,monospace", 20, bold=True)
        self.font_prompt = pygame.font.SysFont("consolas,couriernew,monospace", 22, bold=True)
        self.font_btn_bold = pygame.font.SysFont("trebuchetms,tahoma,arial", 16, bold=True)
        self.font_btn_lg = pygame.font.SysFont("trebuchetms,tahoma,arial", 22, bold=True)
        self.font_label = pygame.font.SysFont("trebuchetms,tahoma,arial", 18, bold=True)
        self.font_input = pygame.font.SysFont("trebuchetms,tahoma,arial", 22, bold=True)

        # Modal Dialog State Flags
        self.show_levels_modal: bool = False
        self.show_settings_modal: bool = False
        self.sound_enabled: bool = True
        self.selected_chamber_level: int = 12

        # Modal Action Buttons
        self.btn_close_modal = UIButton(pygame.Rect(0, 0, 140, 38), "CLOSE", self.font_btn_bold, style="wood_pill")
        self.btn_toggle_sfx = UIButton(pygame.Rect(0, 0, 260, 42), "AUDIO SFX: ON", self.font_btn_bold, style="blue_pill")
        self.btn_modal_switch_user = UIButton(pygame.Rect(0, 0, 260, 42), "SWITCH USER", self.font_btn_bold, style="wood_pill")

        # Pulse animation counter for glow and arrows
        self.anim_time = 0.0

        # HUD console dimensions
        self.hud_height = 155
        self.hud_rect = pygame.Rect(0, self.screen_height - self.hud_height, self.screen_width, self.hud_height)

        # Home Screen widgets
        self.input_player_name = TextInputBox(pygame.Rect(380, 200, 260, 36), self.font_body)
        self.btn_logout = UIButton(pygame.Rect(655, 201, 135, 34), "SWITCH USER", self.font_small,
                                   accent_color=COLOR_TEXT_ACCENT_AMBER)

        # Login Screen widgets (matching media_1795243874550_0f52c903.jpg)
        cx = self.screen_width // 2
        card_y = 224
        bx = cx - 205
        bw = 410
        bh = 44
        self.input_login_username = TextInputBox(
            pygame.Rect(bx, card_y + 44, bw, bh), self.font_input, placeholder="Enter username...",
            style="wood_recessed", text_align="center", allow_lower=True, allow_symbols=True, max_length=24
        )
        self.input_login_username.text = "afiabyte"
        self.input_login_username.is_active = True
        self.input_login_password = TextInputBox(
            pygame.Rect(bx, card_y + 136, bw, bh), self.font_input, placeholder="••••••••",
            style="wood_recessed", text_align="center", is_password=True, allow_lower=True, allow_symbols=True, max_length=24
        )
        self.btn_login_submit = UIButton(pygame.Rect(cx - 150, card_y + 210, 300, 48), "LOG IN", self.font_btn_bold, style="green_cta")
        self.btn_login_switch_to_register = UIButton(pygame.Rect(cx - 150, card_y + 272, 300, 42), "CREATE ACCOUNT", self.font_btn_bold, style="blue_pill")
        self.btn_forgot_password = UIButton(pygame.Rect(cx - 110, card_y + 328, 220, 24), "FORGOT PASSWORD?", self.font_badge, style="link")
        self.btn_login_guest = UIButton(pygame.Rect(cx - 150, 712, 300, 36), "GUEST ACCESS", self.font_btn_bold, style="wood_pill")

        # Create Account Screen widgets
        card_y = 224
        bx = cx - 205
        bw = 410
        bh = 42
        self.input_reg_username = TextInputBox(
            pygame.Rect(bx, card_y + 38, bw, bh), self.font_input, placeholder="Enter username...",
            style="wood_recessed", text_align="center", allow_lower=True, allow_symbols=True, max_length=20
        )
        self.input_reg_username.is_active = True
        self.input_reg_email = TextInputBox(
            pygame.Rect(bx, card_y + 116, bw, bh), self.font_input, placeholder="Enter email...",
            style="wood_recessed", text_align="center", allow_lower=True, allow_symbols=True, max_length=32
        )
        self.input_reg_password = TextInputBox(
            pygame.Rect(bx, card_y + 194, bw, bh), self.font_input, placeholder="••••••••",
            style="wood_recessed", text_align="center", is_password=True, allow_lower=True, allow_symbols=True, max_length=24
        )
        self.input_reg_confirm_password = TextInputBox(
            pygame.Rect(bx, card_y + 272, bw, bh), self.font_input, placeholder="••••••••",
            style="wood_recessed", text_align="center", is_password=True, allow_lower=True, allow_symbols=True, max_length=24
        )
        self.btn_register = UIButton(pygame.Rect(cx - 150, 624, 300, 48), "REGISTER", self.font_btn_bold, style="green_cta")
        self.btn_back_to_login = UIButton(pygame.Rect(cx - 150, 684, 300, 42), "BACK TO LOGIN", self.font_btn_bold, style="blue_pill")

        # Settings Screen widgets (matching media_1795244853028_f736cb43.jpg)
        card_w = 510
        card_x = cx - card_w // 2
        card_y = 125
        self.toggle_sfx = UIToggleSwitch(pygame.Rect(card_x + 338, card_y + 44, 138, 46), is_on=True, font=self.font_btn_bold, tag="sfx")
        self.toggle_bgm = UIToggleSwitch(pygame.Rect(card_x + 338, card_y + 110, 138, 46), is_on=False, font=self.font_btn_bold, tag="bgm")
        self.toggle_ai_hints = UIToggleSwitch(pygame.Rect(card_x + 338, card_y + 176, 138, 46), is_on=True, font=self.font_btn_bold, tag="ai_hints")
        self.btn_anim_smooth = UIButton(pygame.Rect(card_x + 252, card_y + 246, 110, 46), "SMOOTH", self.font_btn_bold, style="amber_glow")
        self.btn_anim_fast = UIButton(pygame.Rect(card_x + 368, card_y + 246, 108, 46), "FAST", self.font_btn_bold, style="amber_glow")
        self.btn_settings_save = UIButton(pygame.Rect(cx - 145, card_y + 406, 290, 48), "SAVE & APPLY", self.font_btn_bold, style="green_cta")
        self.btn_settings_back = UIButton(pygame.Rect(cx - 145, card_y + 472, 290, 48), "BACK TO MENU", self.font_btn_bold, style="wood_pill")

        # Dungeon Records Screen widgets
        self.btn_history_back = UIButton(pygame.Rect(cx - 135, 642, 270, 48), "BACK TO MENU", self.font_btn_bold, style="wood_pill")

        self._init_home_buttons()
        self._init_overlay_buttons()
        self._init_level_select_ui()

        # Modular Screen Renderers
        self.splash_renderer = SplashScreenRenderer(self.screen_width, self.screen_height)
        self.create_account_renderer = CreateAccountScreenRenderer(self.screen_width, self.screen_height)
        self.login_renderer = LoginScreenRenderer(self.screen_width, self.screen_height)
        self.home_renderer = HomeScreenRenderer(self.screen_width, self.screen_height)
        self.level_select_renderer = LevelSelectScreenRenderer(self.screen_width, self.screen_height)
        self.how_to_play_renderer = HowToPlayScreenRenderer(self.screen_width, self.screen_height)
        self.settings_renderer = SettingsScreenRenderer(self.screen_width, self.screen_height)
        self.history_renderer = HistoryScreenRenderer(self.screen_width, self.screen_height)
        self.game_view_renderer = GameViewRenderer(self.screen_width, self.screen_height)
        self.hud_renderer = HUDConsoleRenderer(self.screen_width, self.screen_height, self.hud_height)
        self.pause_renderer = PauseScreenRenderer(self.screen_width, self.screen_height)
        self.victory_renderer = VictoryScreenRenderer(self.screen_width, self.screen_height)
        self.overlay_renderer = OverlayRenderer(self.screen_width, self.screen_height)

    def _init_home_buttons(self) -> None:
        """Initialize interactive buttons for the Main Menu parchment scroll."""
        cx = self.screen_width // 2

        self.input_player_name = TextInputBox(
            pygame.Rect(cx - 185, 234, 370, 44),
            self.font_input,
            placeholder="Bravo42",
            style="wood_recessed",
            text_align="center"
        )
        self.input_player_name.text = "afiabyte"

        self.grid_buttons: List[UIButton] = []
        sizes = [5, 7, 9, 11]
        btn_w, btn_h = 78, 54
        gap = 12
        start_x = cx - (4 * btn_w + 3 * gap) // 2
        for i, s in enumerate(sizes):
            label = f"{s}x{s}"
            btn = UIButton(pygame.Rect(start_x + i * (btn_w + gap), 308, btn_w, btn_h),
                           label, self.font_btn_bold, tag=str(s), style="amber_glow" if s == 7 else "stone")
            if s == 7:
                btn.is_selected = True
            self.grid_buttons.append(btn)

        self.level_buttons: List[UIButton] = []
        diff_w = 380
        diff_h = 38
        seg_w = diff_w // 3
        levels = [(1, "RECRUIT"), (2, "TACTICAL"), (3, "NIGHTMARE")]
        for i, (lvl, label) in enumerate(levels):
            seg_x = cx - 190 + i * seg_w
            btn = UIButton(pygame.Rect(seg_x, 392, seg_w, diff_h),
                           label, self.font_btn_bold, tag=str(lvl))
            if lvl == 1:
                btn.is_selected = True
            self.level_buttons.append(btn)

        self.btn_start_mission = UIButton(
            pygame.Rect(cx - 150, 448, 300, 48),
            "START MISSION", self.font_btn_lg, style="green_cta"
        )
        self.btn_levels = UIButton(
            pygame.Rect(cx - 190, 512, 180, 42),
            "LEVELS (1-50)", self.font_btn_bold, style="blue_pill"
        )
        self.btn_how_to_play = UIButton(
            pygame.Rect(cx + 10, 512, 180, 42),
            "HOW TO PLAY", self.font_btn_bold, style="wood_pill"
        )
        self.btn_history = UIButton(
            pygame.Rect(cx - 190, 566, 180, 42),
            "HISTORY", self.font_btn_bold, style="history_pill"
        )
        self.btn_settings = UIButton(
            pygame.Rect(cx + 10, 566, 180, 42),
            "SETTINGS", self.font_btn_bold, style="wood_gear_pill"
        )
        self.btn_exit = UIButton(
            pygame.Rect(cx - 85, 622, 170, 38),
            "EXIT", self.font_btn_bold, style="red_pill"
        )
        self.btn_logout = UIButton(pygame.Rect(cx - 190, 622, 180, 38), "SWITCH USER", self.font_small,
                                   accent_color=COLOR_TEXT_ACCENT_AMBER)
        self.btn_pause = UIButton(pygame.Rect(self.screen_width - 130, 16, 110, 32), "|| PAUSE", self.font_badge,
                                  accent_color=COLOR_TEXT_ACCENT_AMBER)
        self.btn_back_to_menu = UIButton(pygame.Rect(self.screen_width // 2 - 110, 680, 220, 42),
                                         "<< RETURN", self.font_header)

    def _init_level_select_ui(self) -> None:
        """Initialize widgets for the 1-50 Select Level Screen."""
        cx = self.screen_width // 2
        card_y = 30
        self.selected_chamber_level: int = 12

        self.level_tile_buttons: List[UIButton] = []
        cols = 5
        rows = 7
        btn_w = 72
        btn_h = 54
        gap_x = 18
        gap_y = 12
        grid_w = cols * btn_w + (cols - 1) * gap_x
        start_grid_x = cx - grid_w // 2
        start_grid_y = card_y + 115

        for r in range(rows):
            for c in range(cols):
                bx = start_grid_x + c * (btn_w + gap_x)
                by = start_grid_y + r * (btn_h + gap_y)
                btn = UIButton(pygame.Rect(bx, by, btn_w, btn_h), "", self.font_btn_bold)
                self.level_tile_buttons.append(btn)

        st_y = start_grid_y + rows * (btn_h + gap_y) + 8
        btn_play_w = 260
        btn_back_w = 160
        btn_act_h = 48
        btn_gap = 18
        total_btn_w = btn_play_w + btn_back_w + btn_gap
        btn_start_x = cx - total_btn_w // 2
        btn_act_y = st_y + 24

        self.btn_level_play = UIButton(
            pygame.Rect(btn_start_x, btn_act_y, btn_play_w, btn_act_h),
            f"PLAY LEVEL {self.selected_chamber_level}",
            self.font_btn_lg,
            style="green_cta"
        )
        self.btn_level_back = UIButton(
            pygame.Rect(btn_start_x + btn_play_w + btn_gap, btn_act_y, btn_back_w, btn_act_h),
            "BACK",
            self.font_btn_lg,
            style="wood_pill"
        )

    def _init_overlay_buttons(self) -> None:
        """Initialize buttons for VICTORY, DEFEAT, and PAUSE states."""
        cx = self.screen_width // 2

        btn_vic_w, btn_vic_h = 320, 52
        btn_vic_x = cx - btn_vic_w // 2
        self.btn_next_level = UIButton(pygame.Rect(btn_vic_x, 560, btn_vic_w, btn_vic_h), "NEXT LEVEL", self.font_btn_bold,
                                       style="green_cta")
        self.btn_victory_replay = UIButton(pygame.Rect(btn_vic_x, 630, btn_vic_w, btn_vic_h), "PLAY AGAIN [R]", self.font_btn_bold,
                                         style="blue_pill")
        self.btn_victory_menu = UIButton(pygame.Rect(btn_vic_x, 700, btn_vic_w, btn_vic_h), "MAIN MENU [ESC]", self.font_btn_bold,
                                       style="wood_pill")

        self.btn_retry_level = UIButton(pygame.Rect(cx - 210, 440, 195, 42), "RETRY MISSION", self.font_header,
                                        accent_color=COLOR_TEXT_ACCENT_RED)
        self.btn_defeat_menu = UIButton(pygame.Rect(cx + 15, 440, 195, 42), "HOME MENU", self.font_header)

        btn_w, btn_h = 295, 48
        btn_x = cx - btn_w // 2
        self.btn_pause_resume = UIButton(pygame.Rect(btn_x, 370, btn_w, btn_h), "RESUME GAME", self.font_btn_bold, style="green_cta")
        self.btn_pause_restart = UIButton(pygame.Rect(btn_x, 434, btn_w, btn_h), "RESTART LEVEL [R]", self.font_btn_bold, style="blue_pill")
        self.btn_pause_settings = UIButton(pygame.Rect(btn_x, 498, btn_w, btn_h), "SETTINGS", self.font_btn_bold, style="wood_pill")
        self.btn_pause_help = self.btn_pause_settings  # alias for backward-compatibility
        self.btn_pause_menu = UIButton(pygame.Rect(btn_x, 562, btn_w, btn_h), "QUIT TO MENU", self.font_btn_bold, style="burgundy")

    def update(self, dt: float) -> None:
        """Update animation timers and interactive text fields."""
        self.anim_time += dt
        self.input_player_name.update(dt)
        self.input_login_username.update(dt)

    def compute_grid_geometry(self, grid_size: int) -> Tuple[float, float, float]:
        """Dynamically scale cell pixel sizes so grid fits cleanly centered above HUD."""
        return self.game_view_renderer.compute_grid_geometry(grid_size, self.hud_height)

    # -------------------------------------------------------------------------
    # Screen Render Delegations
    # -------------------------------------------------------------------------
    def draw_splash_screen(self, surface: pygame.Surface, splash_timer: float, splash_duration: float = 2.5) -> None:
        """Render the cinematic Retro-Pixel RPG adventure intro splash screen."""
        self.splash_renderer.draw(
            surface,
            splash_timer,
            splash_duration,
            self.anim_time,
            self.font_title_bot,
            self.font_subtitle,
            self.font_pixel_med,
            self.font_prompt,
            font_title_top=self.font_title_top
        )

    def draw_login_screen(
        self,
        surface: pygame.Surface,
        recent_operatives: Optional[List[Dict[str, Any]]] = None,
        status_msg: str = "AWAITING CREDENTIALS"
    ) -> None:
        """Render the exact retro-pixel RPG adventure Log In screen matching reference mockup."""
        self.login_renderer.draw(
            surface,
            self.input_login_username,
            self.btn_login_submit,
            self.btn_login_guest,
            self.font_badge,
            self.font_title_top,
            self.font_bold,
            self.font_small,
            recent_operatives,
            status_msg,
            btn_switch_to_register=self.btn_login_switch_to_register,
            input_password=self.input_login_password,
            btn_forgot_password=self.btn_forgot_password,
            anim_time=self.anim_time
        )

    def draw_create_account_screen(
        self,
        surface: pygame.Surface,
        status_msg: str = "",
        is_status_error: bool = False
    ) -> None:
        """Render the exact retro-pixel RPG adventure Create Account screen."""
        self.create_account_renderer.draw(
            surface,
            self.input_reg_username,
            self.input_reg_email,
            self.input_reg_password,
            self.input_reg_confirm_password,
            self.btn_register,
            self.btn_back_to_login,
            self.font_title_top,
            self.font_subtitle,
            self.font_label,
            status_msg=status_msg,
            is_status_error=is_status_error,
            anim_time=self.anim_time
        )

    def draw_home_screen(
        self,
        surface: pygame.Surface,
        best_victory_steps: Optional[int],
        user_stats: Optional[Dict[str, Any]] = None
    ) -> None:
        """Render identical Main Menu matching retro-pixel RPG adventure parchment design."""
        self.home_renderer.draw_home_screen(
            surface,
            best_victory_steps,
            user_stats,
            self.input_player_name,
            self.grid_buttons,
            self.level_buttons,
            self.btn_start_mission,
            self.btn_levels,
            self.btn_how_to_play,
            self.btn_settings,
            self.btn_exit,
            self.font_title_top,
            self.font_title_bot,
            self.font_label,
            self.font_badge,
            self.font_btn_bold,
            self.show_levels_modal,
            self.show_settings_modal,
            self.selected_chamber_level,
            self.sound_enabled,
            self.btn_close_modal,
            self.btn_toggle_sfx,
            self.btn_modal_switch_user,
            self.font_small,
            btn_history=self.btn_history
        )

    def draw_level_select_screen(
        self,
        surface: pygame.Surface,
        user_stats: Optional[Dict[str, Any]] = None
    ) -> None:
        """Render the exact retro-pixel RPG Select Level parchment screen."""
        self.level_select_renderer.draw_level_select_screen(
            surface,
            self.level_tile_buttons,
            self.btn_level_play,
            self.btn_level_back,
            self.selected_chamber_level,
            user_stats,
            self.font_title_top,
            self.font_label,
            self.font_input
        )

    def draw_how_to_play_screen(self, surface: pygame.Surface) -> None:
        """Render the tactical instruction briefing screen."""
        self.how_to_play_renderer.draw(
            surface,
            self.btn_back_to_menu,
            self.font_title_top,
            self.font_header,
            self.font_bold,
            anim_time=self.anim_time,
            font_btn_bold=self.font_btn_bold,
            font_key=self.font_btn_bold
        )

    def draw_settings_screen(
        self,
        surface: pygame.Surface,
        is_smooth_selected: bool = True,
        is_api_connected: bool = True,
        status_message: str = "",
    ) -> None:
        """Render the authentic retro-pixel RPG adventure Settings screen matching reference mockup."""
        self.settings_renderer.draw_settings_screen(
            surface,
            toggle_sfx=self.toggle_sfx,
            toggle_bgm=self.toggle_bgm,
            toggle_ai_hints=self.toggle_ai_hints,
            btn_anim_smooth=self.btn_anim_smooth,
            btn_anim_fast=self.btn_anim_fast,
            is_smooth_selected=is_smooth_selected,
            is_api_connected=is_api_connected,
            btn_save=self.btn_settings_save,
            btn_back=self.btn_settings_back,
            anim_time=self.anim_time,
            status_message=status_message,
        )

    def draw_history_screen(
        self,
        surface: pygame.Surface,
        win_rate: int = 75,
        best_steps: int = 12,
        records: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Render the exact retro-pixel RPG Dungeon Records screen."""
        self.history_renderer.draw_history_screen(
            surface,
            win_rate=win_rate,
            best_steps=best_steps,
            records=records or [],
            btn_back=self.btn_history_back,
        )

    def draw_grid_environment(
        self,
        surface: pygame.Surface,
        grid_size: int,
        origin_x: float,
        origin_y: float,
        cell_size: float,
        walls: set,
        player_x: float,
        player_y: float,
        player_pos: Tuple[int, int],
        has_key: bool,
        key_pos: Tuple[int, int],
        exit_pos: Tuple[int, int],
        hunters: list,
        recommended_path: List[List[int]],
        wall_shift_alert: float = 0.0,
        player_facing: Tuple[int, int] = (0, 1)
    ) -> None:
        """Render the tactical grid board, walls, key, exit portal, breadcrumbs, guide arrow, and entities."""
        self.game_view_renderer.draw_grid_environment(
            surface,
            grid_size,
            origin_x,
            origin_y,
            cell_size,
            walls,
            player_x,
            player_y,
            player_pos,
            has_key,
            key_pos,
            exit_pos,
            hunters,
            recommended_path,
            self.anim_time,
            self.font_bold,
            self.font_badge,
            self.font_small,
            wall_shift_alert,
            player_facing
        )

    def _draw_human_player(
        self,
        surface: pygame.Surface,
        px: float,
        py: float,
        cell_size: float,
        facing_dr: int,
        facing_dc: int,
        has_key: bool
    ) -> None:
        """Render the Gamer/Player Operative."""
        self.game_view_renderer._draw_human_player(
            surface, px, py, cell_size, facing_dr, facing_dc, has_key, self.anim_time, self.font_small
        )

    def _draw_human_hunter(
        self,
        surface: pygame.Surface,
        hx: float,
        hy: float,
        cell_size: float,
        facing_dr: int,
        facing_dc: int,
        hunter_id: int
    ) -> None:
        """Render the Hunter as a tactical juggernaut."""
        self.game_view_renderer._draw_human_hunter(
            surface, hx, hy, cell_size, facing_dr, facing_dc, hunter_id, self.anim_time, self.font_small
        )

    def draw_hud_console(
        self,
        surface: pygame.Surface,
        level_name: str,
        steps: int,
        best_steps: Optional[int],
        has_key: bool,
        ai_latency_ms: int,
        ai_status: str,
        is_gemini_active: bool,
        commander_order: str
    ) -> None:
        """Render the dedicated bottom HUD console with metrics and telemetry."""
        self.hud_renderer.draw(
            surface,
            level_name,
            steps,
            best_steps,
            has_key,
            ai_latency_ms,
            ai_status,
            is_gemini_active,
            commander_order,
            self.anim_time,
            self.font_badge,
            self.font_header,
            self.font_body,
            self.font_bold,
            self.font_small
        )

    def draw_game_over_overlay(
        self,
        surface: pygame.Surface,
        is_victory: bool,
        steps: int,
        is_new_best: bool,
        current_level: int,
        player_name: str = "Bravo42",
        mode_str: str = "7x7 TACTICAL",
        best_steps: int = 12
    ) -> None:
        """Render the victory or defeat modal overlay."""
        if is_victory:
            self.victory_renderer.draw(
                surface=surface,
                player_name=player_name,
                mode_str=mode_str,
                steps=steps,
                best_steps=best_steps,
                is_new_record=is_new_best,
                btn_next_level=self.btn_next_level,
                btn_play_again=self.btn_victory_replay,
                btn_menu=self.btn_victory_menu,
                anim_time=self.anim_time
            )
        else:
            self.overlay_renderer.draw_game_over_overlay(
                surface,
                is_victory,
                steps,
                is_new_best,
                current_level,
                self.btn_next_level,
                self.btn_victory_replay,
                self.btn_victory_menu,
                self.btn_retry_level,
                self.btn_defeat_menu,
                self.font_title,
                self.font_header,
                self.font_body,
                self.font_small
            )

    def draw_pause_overlay(
        self,
        surface: pygame.Surface,
        origin_x: float = 0.0,
        origin_y: float = 0.0,
        cell_size: float = 64.0,
        player_x: float = 0.0,
        player_y: float = 0.0,
        has_key: bool = False,
        hunters: list = None,
        key_pos: Tuple[int, int] = (0, 0),
        exit_pos: Tuple[int, int] = (0, 0),
        recommended_path: List[List[int]] = None,
        ai_latency_ms: int = 0,
        ai_status: str = "ONLINE",
        level_name: str = "Tactical",
        level_num: int = 12
    ) -> None:
        """Render exact retro-pixel RPG pause dialog matching media_1795263510678_20cb89ba.jpg."""
        self.pause_renderer.draw(
            surface=surface,
            btn_resume=self.btn_pause_resume,
            btn_restart=self.btn_pause_restart,
            btn_settings=self.btn_pause_settings,
            btn_quit=self.btn_pause_menu,
            level_num=level_num,
            difficulty_name=level_name,
            anim_time=self.anim_time,
        )

    def draw_standby_banner(self, surface: pygame.Surface, seconds_remaining: float) -> None:
        """Render prominent tactical reconnaissance banner on mission start."""
        self.overlay_renderer.draw_standby_banner(
            surface,
            seconds_remaining,
            self.anim_time,
            self.font_header,
            self.font_bold
        )

    # -------------------------------------------------------------------------
    # Backward-compatible Helper Aliases
    # -------------------------------------------------------------------------
    def _draw_dungeon_background(self, surface: pygame.Surface) -> None:
        draw_dungeon_background(surface, self.screen_width, self.screen_height)

    def _draw_parchment_chassis(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        draw_parchment_chassis(surface, rect)

    def _draw_royal_crown(self, surface: pygame.Surface, x: int, y: int) -> None:
        draw_royal_crown(surface, x, y)

    def _draw_adventure_title(self, surface: pygame.Surface, text: str, y_pos: int, font: pygame.font.Font, cx: int) -> None:
        draw_adventure_title(surface, text, y_pos, font, cx)

    def _draw_padlock(self, surface: pygame.Surface, center_x: int, center_y: int) -> None:
        draw_padlock(surface, center_x, center_y)

    def _draw_level_tile(self, surface: pygame.Surface, rect: pygame.Rect, lvl_num: int, state: str) -> None:
        self.level_select_renderer._draw_level_tile(surface, rect, lvl_num, state, self.font_input)

    def _draw_trophy_badge(self, surface: pygame.Surface, rect: pygame.Rect, text: str) -> None:
        self.home_renderer._draw_trophy_badge(surface, rect, text, self.font_badge)

    def _draw_difficulty_bar(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        self.home_renderer._draw_difficulty_bar(surface, rect, self.level_buttons, self.font_btn_bold)

    def _draw_levels_modal(self, surface: pygame.Surface, user_level: int) -> None:
        self.home_renderer._draw_levels_modal(
            surface, user_level, self.selected_chamber_level, self.btn_close_modal, self.font_label, self.font_small
        )

    def _draw_settings_modal(self, surface: pygame.Surface) -> None:
        self.home_renderer._draw_settings_modal(
            surface, self.sound_enabled, self.btn_toggle_sfx, self.btn_modal_switch_user, self.btn_close_modal, self.font_label
        )

    def _draw_splash_moss_clump(self, surface: pygame.Surface, mx: int, my: int, spread_w: int = 24, spread_h: int = 35) -> None:
        self.splash_renderer._draw_moss_clump(surface, mx, my, spread_w, spread_h)

    def _draw_splash_wall_torch(self, surface: pygame.Surface, tx: int, ty: int, flame_seed: float = 0.0) -> None:
        self.splash_renderer._draw_wall_torch(surface, tx, ty, self.anim_time, flame_seed)

    def _draw_splash_shadow_monster(self, surface: pygame.Surface, mcx: int, mcy: int) -> None:
        self.splash_renderer._draw_shadow_monster(surface, mcx, mcy, self.anim_time)

    def _draw_splash_skeleton(self, surface: pygame.Surface, sx: int, sy: int) -> None:
        self.splash_renderer._draw_skeleton(surface, sx, sy)

    def _draw_splash_relic_chest(self, surface: pygame.Surface, bx: int, by: int) -> None:
        self.splash_renderer._draw_relic_chest(surface, bx, by, self.anim_time)

    def _draw_splash_hero(self, surface: pygame.Surface, hx: int, hy: int) -> None:
        self.splash_renderer._draw_hero(surface, hx, hy, self.anim_time)
