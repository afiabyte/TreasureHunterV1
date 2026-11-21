"""
UI Package: Modular retro-pixel RPG adventure user interface components.

Provides:
- Colors: Subterranean, Lost Ruins, and neon-cyber palette constants.
- Widgets: UIButton and TextInputBox interactive controls.
- Art Helpers: Dungeon background, parchment chassis, royal crown, adventure titles.
- Screen Renderers:
    - SplashScreenRenderer
    - LoginScreenRenderer
    - HomeScreenRenderer
    - LevelSelectScreenRenderer
    - HowToPlayScreenRenderer
    - GameViewRenderer
    - HUDConsoleRenderer
    - OverlayRenderer
- UIManager: Unified facade coordinating all screens and interactive states.
"""

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
from .overlays import OverlayRenderer
from .manager import UIManager

__all__ = [
    # Colors
    "COLOR_BG",
    "COLOR_GRID_BG",
    "COLOR_GRID_LINE",
    "COLOR_WALL",
    "COLOR_WALL_BORDER",
    "COLOR_WALL_ACCENT",
    "COLOR_PLAYER_CORE",
    "COLOR_PLAYER_GLOW",
    "COLOR_PLAYER_SHIELD",
    "COLOR_HUNTER_CORE",
    "COLOR_HUNTER_BODY",
    "COLOR_HUNTER_CONE",
    "COLOR_HUNTER_GLOW",
    "COLOR_KEY_CORE",
    "COLOR_KEY_GOLD",
    "COLOR_KEY_GLOW",
    "COLOR_EXIT_CORE",
    "COLOR_EXIT_PORTAL",
    "COLOR_EXIT_GLOW",
    "COLOR_BREADCRUMB_RING",
    "COLOR_BREADCRUMB_FILL",
    "COLOR_GUIDE_ARROW",
    "COLOR_HUD_BG",
    "COLOR_HUD_BORDER",
    "COLOR_TEXT_PRIMARY",
    "COLOR_TEXT_SECONDARY",
    "COLOR_TEXT_MUTED",
    "COLOR_TEXT_ACCENT_CYAN",
    "COLOR_TEXT_ACCENT_GREEN",
    "COLOR_TEXT_ACCENT_AMBER",
    "COLOR_TEXT_ACCENT_RED",
    "COLOR_TEXT_ACCENT_MAGENTA",
    "COLOR_TEXT_ACCENT_PURPLE",
    "COLOR_BTN_NORMAL",
    "COLOR_BTN_HOVER",
    "COLOR_BTN_ACTIVE",
    "COLOR_BTN_BORDER",
    "COLOR_BTN_BORDER_HOVER",
    # Widgets
    "UIButton",
    "TextInputBox",
    "UIToggleSwitch",
    # Art Helpers
    "draw_dungeon_background",
    "draw_parchment_chassis",
    "draw_royal_crown",
    "draw_adventure_title",
    "draw_padlock",
    # Renderers
    "SplashScreenRenderer",
    "CreateAccountScreenRenderer",
    "LoginScreenRenderer",
    "HomeScreenRenderer",
    "LevelSelectScreenRenderer",
    "HowToPlayScreenRenderer",
    "SettingsScreenRenderer",
    "HistoryScreenRenderer",
    "GameViewRenderer",
    "HUDConsoleRenderer",
    "OverlayRenderer",
    "UIManager",
]
