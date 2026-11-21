"""
UIManager: Manages tactical UI rendering, HUD console, menus, and visual feedback.

This module renders:
- High-contrast cyber-tactical visuals with glowing neon accents.
- Home Screen (Player Name input, Grid Size selector, Level selector, How to Play button,
  Start Mission button, all-time best victory steps record from SQLite).
- How to Play Screen (detailed controls, objective, and visual HUD indicators).
- In-game Grid rendering dynamically scaled to fit any N x N dimension above the HUD.
- Entities: Player Operative, Hunter Drones with directional vision cones, Key, Exit, Walls.
- Visual navigation aids: Green Gemini safe-route breadcrumbs and pulsing yellow guide arrow.
- Dedicated bottom HUD console: Level, Step count, Best score, Key status,
  Gemini AI latency/status telemetry with LED indicators, and live Tactical Commander transmissions.
- Game Over overlays: VICTORY (with level progression) and DEFEAT screens.
"""

import math
import time
from typing import Tuple, List, Dict, Any, Optional
import pygame


# Color Palette (Ancient Temple & Lost Ruins Adventure)
COLOR_BG = (18, 20, 28)               # Deep subterranean sanctuary stone
COLOR_GRID_BG = (28, 33, 46)          # Ancient temple flagstone floor
COLOR_GRID_LINE = (48, 56, 75)        # Chiseled stone mortar line
COLOR_WALL = (38, 42, 56)             # Carved basalt / granite monolith
COLOR_WALL_BORDER = (225, 175, 55)    # Burnished Ancient Gold trim
COLOR_WALL_ACCENT = (235, 80, 50)     # Glowing Runic Amber-Ruby Inlay

COLOR_PLAYER_CORE = (255, 255, 255)
COLOR_PLAYER_GLOW = (255, 195, 45)    # Radiant Golden Torch Glow
COLOR_PLAYER_SHIELD = (255, 210, 60, 120)

COLOR_HUNTER_CORE = (255, 240, 220)
COLOR_HUNTER_BODY = (225, 45, 65)     # Armored Crimson Guardian Plate
COLOR_HUNTER_CONE = (240, 60, 40, 50) # Fiery Vigilance Sightline
COLOR_HUNTER_GLOW = (255, 75, 40)     # Blazing Guardian Golem Core

COLOR_KEY_CORE = (255, 255, 230)
COLOR_KEY_GOLD = (255, 210, 30)       # Gleaming Ancient Sun Gold
COLOR_KEY_GLOW = (255, 235, 80, 130)

COLOR_EXIT_CORE = (225, 255, 245)
COLOR_EXIT_PORTAL = (0, 245, 155)     # Luminous Mystic Emerald Gateway
COLOR_EXIT_GLOW = (0, 220, 130, 110)

COLOR_BREADCRUMB_RING = (45, 240, 150)# Mystical Rune Step Ring
COLOR_BREADCRUMB_FILL = (20, 120, 70, 140)
COLOR_GUIDE_ARROW = (255, 215, 35)    # Radiant Compass Needle

COLOR_HUD_BG = (19, 23, 34)           # Carved basalt command plinth
COLOR_HUD_BORDER = (65, 80, 110)      # Antique brass relief border
COLOR_TEXT_PRIMARY = (248, 250, 255)
COLOR_TEXT_SECONDARY = (175, 190, 220)
COLOR_TEXT_MUTED = (110, 125, 150)
COLOR_TEXT_ACCENT_CYAN = (65, 200, 255)   # Celestial Sapphire Blue
COLOR_TEXT_ACCENT_GREEN = (40, 240, 140)  # Mystic Emerald
COLOR_TEXT_ACCENT_AMBER = (255, 195, 40)  # Sun Amulet Gold
COLOR_TEXT_ACCENT_RED = (255, 70, 90)     # Guardian Ruby
COLOR_TEXT_ACCENT_MAGENTA = (235, 90, 160)# Arcane Amethyst
COLOR_TEXT_ACCENT_PURPLE = (185, 110, 255)# Mystic Violet

COLOR_BTN_NORMAL = (28, 35, 52)
COLOR_BTN_HOVER = (42, 55, 85)
COLOR_BTN_ACTIVE = (220, 165, 50)     # Antique Gold
COLOR_BTN_BORDER = (65, 85, 125)
COLOR_BTN_BORDER_HOVER = (255, 205, 50)


class UIButton:
    """Interactive tactical UI button with hover animations and click detection."""

    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font,
                 accent_color: Tuple[int, int, int] = COLOR_TEXT_ACCENT_CYAN,
                 tag: str = "",
                 style: str = "tactical") -> None:
        self.rect = rect
        self.text = text
        self.font = font
        self.accent_color = accent_color
        self.tag = tag
        self.style = style
        self.is_hovered = False
        self.is_selected = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True if clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Render button with style-specific borders, drop shadow, and state highlights."""
        if self.style == "stone":
            # Dungeon stone button (gray or radiant golden amber if selected)
            if self.is_selected:
                pygame.draw.rect(surface, (100, 48, 6), self.rect.move(0, 4), border_radius=10)
                pygame.draw.rect(surface, (250, 182, 52), self.rect, border_radius=10)
                pygame.draw.rect(surface, (255, 222, 118), self.rect.inflate(-4, -4), border_radius=8)
                pygame.draw.rect(surface, (246, 170, 40), self.rect.inflate(-8, -8), border_radius=6)
                pygame.draw.rect(surface, (92, 42, 6), self.rect, width=3, border_radius=10)
                txt = self.font.render(self.text, True, (52, 22, 4))
                surface.blit(txt, txt.get_rect(center=self.rect.center))
            else:
                bg = (148, 138, 130) if self.is_hovered else (136, 126, 118)
                pygame.draw.rect(surface, (54, 48, 44), self.rect.move(0, 4), border_radius=10)
                pygame.draw.rect(surface, bg, self.rect, border_radius=10)
                pygame.draw.rect(surface, (168, 158, 150), self.rect.inflate(-4, -4), border_radius=8)
                pygame.draw.rect(surface, (126, 116, 108), self.rect.inflate(-8, -8), border_radius=6)
                pygame.draw.rect(surface, (50, 44, 40), self.rect, width=2, border_radius=10)
                # Chiseled stone crack
                pygame.draw.line(surface, (84, 76, 70), (self.rect.x + 14, self.rect.bottom - 14), (self.rect.x + 26, self.rect.bottom - 22), 2)
                txt = self.font.render(self.text, True, (40, 34, 30))
                surface.blit(txt, txt.get_rect(center=self.rect.center))
            return

        elif self.style == "green_cta":
            # Large Emerald Green CTA button
            c_shadow = (10, 48, 24)
            c_face = (46, 188, 104) if self.is_hovered else (39, 174, 96)
            c_light = (98, 224, 151)
            c_border = (10, 50, 26)
            pygame.draw.rect(surface, c_shadow, self.rect.move(0, 4), border_radius=12)
            pygame.draw.rect(surface, c_face, self.rect, border_radius=12)
            pygame.draw.rect(surface, c_light, self.rect.inflate(-4, -4), border_radius=10)
            pygame.draw.rect(surface, (30, 152, 84), self.rect.inflate(-8, -8), border_radius=8)
            pygame.draw.rect(surface, c_border, self.rect, width=3, border_radius=12)
            txt = self.font.render(self.text, True, (255, 255, 255))
            txt_s = self.font.render(self.text, True, (10, 50, 26))
            rc = txt.get_rect(center=self.rect.center)
            surface.blit(txt_s, rc.move(0, 2))
            surface.blit(txt, rc)
            return

        elif self.style == "blue_pill":
            c_shadow = (26, 38, 48)
            c_face = (84, 110, 128) if self.is_hovered else (72, 96, 112)
            c_light = (118, 144, 162)
            c_border = (18, 28, 36)
            pygame.draw.rect(surface, c_shadow, self.rect.move(0, 3), border_radius=10)
            pygame.draw.rect(surface, c_face, self.rect, border_radius=10)
            pygame.draw.rect(surface, c_light, self.rect.inflate(-4, -4), border_radius=8)
            pygame.draw.rect(surface, (60, 84, 100), self.rect.inflate(-8, -8), border_radius=6)
            pygame.draw.rect(surface, c_border, self.rect, width=2, border_radius=10)
            txt = self.font.render(self.text, True, (255, 250, 242))
            txt_s = self.font.render(self.text, True, c_border)
            rc = txt.get_rect(center=self.rect.center)
            surface.blit(txt_s, rc.move(0, 1))
            surface.blit(txt, rc)
            return

        elif self.style in ("wood_pill", "wood_gear_pill"):
            c_shadow = (68, 34, 12)
            c_face = (175, 105, 48) if self.is_hovered else (160, 94, 40)
            c_light = (206, 136, 76)
            c_border = (48, 24, 8)
            pygame.draw.rect(surface, c_shadow, self.rect.move(0, 3), border_radius=10)
            pygame.draw.rect(surface, c_face, self.rect, border_radius=10)
            pygame.draw.rect(surface, c_light, self.rect.inflate(-4, -4), border_radius=8)
            pygame.draw.rect(surface, (140, 80, 32), self.rect.inflate(-8, -8), border_radius=6)
            pygame.draw.rect(surface, c_border, self.rect, width=2, border_radius=10)

            txt = self.font.render(self.text, True, (255, 250, 242))
            txt_s = self.font.render(self.text, True, c_border)
            if self.style == "wood_gear_pill":
                total_w = txt.get_width() + 24
                tx = self.rect.centerx - total_w // 2
                ty = self.rect.centery - txt.get_height() // 2
                surface.blit(txt_s, (tx, ty + 1))
                surface.blit(txt, (tx, ty))
                # Custom pixel-art golden gear
                gx = tx + txt.get_width() + 14
                gy = self.rect.centery
                pygame.draw.circle(surface, c_border, (gx, gy + 1), 7)
                pygame.draw.circle(surface, (245, 185, 55), (gx, gy), 6)
                pygame.draw.circle(surface, c_border, (gx, gy), 6, 2)
                pygame.draw.circle(surface, (140, 80, 32), (gx, gy), 2)
                for ang in range(0, 360, 60):
                    rad = math.radians(ang)
                    tx1 = int(gx + math.cos(rad) * 8)
                    ty1 = int(gy + math.sin(rad) * 8)
                    pygame.draw.circle(surface, (245, 185, 55), (tx1, ty1), 2)
            else:
                rc = txt.get_rect(center=self.rect.center)
                surface.blit(txt_s, rc.move(0, 1))
                surface.blit(txt, rc)
            return

        elif self.style == "red_pill":
            c_shadow = (72, 20, 16)
            c_face = (184, 60, 48) if self.is_hovered else (168, 52, 40)
            c_light = (220, 94, 80)
            c_border = (48, 14, 10)
            pygame.draw.rect(surface, c_shadow, self.rect.move(0, 3), border_radius=10)
            pygame.draw.rect(surface, c_face, self.rect, border_radius=10)
            pygame.draw.rect(surface, c_light, self.rect.inflate(-4, -4), border_radius=8)
            pygame.draw.rect(surface, (145, 42, 32), self.rect.inflate(-8, -8), border_radius=6)
            pygame.draw.rect(surface, c_border, self.rect, width=2, border_radius=10)
            txt = self.font.render(self.text, True, (255, 250, 242))
            txt_s = self.font.render(self.text, True, c_border)
            rc = txt.get_rect(center=self.rect.center)
            surface.blit(txt_s, rc.move(0, 1))
            surface.blit(txt, rc)
            return

        # Default Tactical Style
        if self.is_selected:
            bg_color = (15, 60, 95)
            border_color = self.accent_color
            border_width = 2
        elif self.is_hovered:
            bg_color = COLOR_BTN_HOVER
            border_color = COLOR_BTN_BORDER_HOVER
            border_width = 2
        else:
            bg_color = COLOR_BTN_NORMAL
            border_color = COLOR_BTN_BORDER
            border_width = 1

        # Drop shadow beneath button
        pygame.draw.rect(surface, (6, 10, 16), self.rect.move(0, 2), border_radius=4)

        # Background fill
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)
        # Border outline
        pygame.draw.rect(surface, border_color, self.rect, width=border_width, border_radius=4)

        # Top inner specular bevel line
        pygame.draw.line(surface, (min(255, bg_color[0] + 35), min(255, bg_color[1] + 40), min(255, bg_color[2] + 55)),
                         (self.rect.left + 2, self.rect.top + 2), (self.rect.right - 3, self.rect.top + 2), 1)

        # Subtle corner tick marks for tactical look
        t_len = 5
        x, y, w, h = self.rect
        pygame.draw.line(surface, self.accent_color, (x, y), (x + t_len, y), 2)
        pygame.draw.line(surface, self.accent_color, (x, y), (x, y + t_len), 2)
        pygame.draw.line(surface, self.accent_color, (x + w - 1, y + h - 1), (x + w - 1 - t_len, y + h - 1), 2)
        pygame.draw.line(surface, self.accent_color, (x + w - 1, y + h - 1), (x + w - 1, y + h - 1 - t_len), 2)

        # If selected, add an active glowing indicator pip
        if self.is_selected:
            pygame.draw.circle(surface, self.accent_color, (self.rect.right - 7, self.rect.top + 7), 2)

        # Centered text
        text_color = COLOR_TEXT_PRIMARY if (self.is_hovered or self.is_selected) else COLOR_TEXT_SECONDARY
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class TextInputBox:
    """Tactical text input field for player callsign input."""

    def __init__(self, rect: pygame.Rect, font: pygame.font.Font,
                 placeholder: str = "OPERATIVE-01",
                 style: str = "tactical") -> None:
        self.rect = rect
        self.font = font
        self.text = "OPERATIVE-01"
        self.placeholder = placeholder
        self.style = style
        self.is_active = False
        self.cursor_visible = True
        self.cursor_timer = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard typing and mouse focus events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                self.is_active = False
            else:
                # Limit length to 16 alphanumeric characters
                if len(self.text) < 16 and (event.unicode.isalnum() or event.unicode in "-_ "):
                    self.text += event.unicode.upper()

    def update(self, dt: float) -> None:
        """Blink cursor every 0.5s."""
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0.0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surface: pygame.Surface) -> None:
        """Draw text input field with style-specific borders and prompt."""
        if self.style == "wood_recessed":
            # Carved wooden tray recessed into parchment
            pygame.draw.rect(surface, (54, 26, 10), self.rect, border_radius=8)
            pygame.draw.rect(surface, (148, 88, 42), self.rect.inflate(-4, -4), border_radius=6)
            pygame.draw.rect(surface, (216, 172, 116), self.rect.inflate(-6, -6), border_radius=5)
            if self.is_active:
                pygame.draw.rect(surface, (255, 215, 80), self.rect, width=2, border_radius=8)

            display_text = self.text if self.text else self.placeholder
            text_surf = self.font.render(display_text, True, (38, 16, 4))
            text_rc = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rc)

            # Blinking wooden cursor
            if self.is_active and self.cursor_visible:
                cx = text_rc.right + 4
                cy = self.rect.y + 8
                ch = self.rect.height - 16
                pygame.draw.line(surface, (38, 16, 4), (cx, cy), (cx, cy + ch), 2)
            return

        border_color = COLOR_TEXT_ACCENT_CYAN if self.is_active else COLOR_BTN_BORDER
        bg_color = (18, 26, 42) if self.is_active else (14, 20, 32)

        # Ambient drop shadow
        pygame.draw.rect(surface, (6, 10, 16), self.rect.move(0, 2), border_radius=4)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)
        pygame.draw.rect(surface, border_color, self.rect, width=2 if self.is_active else 1, border_radius=4)

        # Terminal prompt prefix indicator
        prefix_surf = self.font.render(">", True, COLOR_TEXT_ACCENT_CYAN if self.is_active else COLOR_TEXT_MUTED)
        surface.blit(prefix_surf, (self.rect.x + 10, self.rect.y + (self.rect.height - prefix_surf.get_height()) // 2))

        display_text = self.text if self.text else self.placeholder
        text_color = COLOR_TEXT_PRIMARY if self.text else COLOR_TEXT_MUTED

        text_surf = self.font.render(display_text, True, text_color)
        surface.blit(text_surf, (self.rect.x + 24, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))

        # Blinking cursor
        if self.is_active and self.cursor_visible:
            cursor_x = self.rect.x + 24 + text_surf.get_width() + 2
            cursor_y = self.rect.y + 6
            cursor_h = self.rect.height - 12
            pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_h), 2)


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

        # Login Screen widgets
        cx = self.screen_width // 2
        self.input_login_username = TextInputBox(pygame.Rect(cx - 160, 265, 320, 42), self.font_body)
        self.input_login_username.text = "afiabyte"
        self.input_login_username.is_active = True
        self.btn_login_submit = UIButton(pygame.Rect(cx - 160, 345, 320, 44), ">> ENTER SANCTUARY <<", self.font_header,
                                         accent_color=COLOR_KEY_GOLD)
        self.btn_login_guest = UIButton(pygame.Rect(cx - 160, 400, 320, 38), "EXPLORE AS GUEST", self.font_body,
                                        accent_color=COLOR_TEXT_SECONDARY)

        self._init_home_buttons()
        self._init_overlay_buttons()
        self._init_level_select_ui()

    def _init_home_buttons(self) -> None:
        """Initialize interactive buttons for the Main Menu parchment scroll."""
        cx = self.screen_width // 2
        card_y = 30

        # Player Name Recessed Wooden Input Field
        self.input_player_name = TextInputBox(
            pygame.Rect(cx - 225, card_y + 228, 450, 44),
            self.font_input,
            placeholder="Bravo42",
            style="wood_recessed"
        )
        self.input_player_name.text = "afiabyte"

        # Grid Size selector stone buttons (5x5, 7x7 default, 9x9, 11x11)
        self.grid_buttons: List[UIButton] = []
        sizes = [5, 7, 9, 11]
        btn_w, btn_h = 98, 62
        start_x = cx - (4 * btn_w + 3 * 18) // 2
        for i, s in enumerate(sizes):
            label = f"{s}x{s}"
            btn = UIButton(pygame.Rect(start_x + i * (btn_w + 18), card_y + 314, btn_w, btn_h),
                           label, self.font_btn_lg, tag=str(s), style="stone")
            if s == 7:
                btn.is_selected = True
            self.grid_buttons.append(btn)

        # Difficulty Segmented Bar Buttons (1: Recruit, 2: Tactical, 3: Nightmare)
        self.level_buttons: List[UIButton] = []
        diff_w = 450
        diff_h = 44
        seg_w = diff_w // 3
        levels = [(1, "RECRUIT"), (2, "TACTICAL"), (3, "NIGHTMARE")]
        for i, (lvl, label) in enumerate(levels):
            seg_x = cx - 225 + i * seg_w
            btn = UIButton(pygame.Rect(seg_x, card_y + 420, seg_w, diff_h),
                           label, self.font_btn_bold, tag=str(lvl))
            if lvl == 1:
                btn.is_selected = True
            self.level_buttons.append(btn)

        # Primary Start Mission Emerald CTA Button
        self.btn_start_mission = UIButton(
            pygame.Rect(cx - 180, card_y + 486, 360, 54),
            "START MISSION", self.font_btn_lg, style="green_cta"
        )

        # Secondary Action Buttons Row 1: Levels & How To Play
        self.btn_levels = UIButton(
            pygame.Rect(cx - 225, card_y + 558, 220, 42),
            "LEVELS (1-50)", self.font_btn_bold, style="blue_pill"
        )
        self.btn_how_to_play = UIButton(
            pygame.Rect(cx + 5, card_y + 558, 220, 42),
            "HOW TO PLAY", self.font_btn_bold, style="wood_pill"
        )

        # Secondary Action Buttons Row 2: Settings & Exit
        self.btn_settings = UIButton(
            pygame.Rect(cx - 225, card_y + 616, 220, 42),
            "SETTINGS", self.font_btn_bold, style="wood_gear_pill"
        )
        self.btn_exit = UIButton(
            pygame.Rect(cx + 5, card_y + 616, 220, 42),
            "EXIT", self.font_btn_bold, style="red_pill"
        )

        # Switch User / Logout button maintained for state transitions
        self.btn_logout = UIButton(pygame.Rect(cx - 225, card_y + 616, 220, 42), "SWITCH USER", self.font_small,
                                   accent_color=COLOR_TEXT_ACCENT_AMBER)

        # In-Game Top-Right Quick Pause Button
        self.btn_pause = UIButton(pygame.Rect(self.screen_width - 130, 16, 110, 32), "|| PAUSE", self.font_badge,
                                  accent_color=COLOR_TEXT_ACCENT_AMBER)

        # How to Play back button
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

    def _draw_padlock(self, surface: pygame.Surface, center_x: int, center_y: int) -> None:
        """Render a crisp, metallic padlock icon on locked stone tiles."""
        # Shackle (silver metallic arch)
        sh_rect = pygame.Rect(center_x - 6, center_y - 9, 12, 11)
        pygame.draw.arc(surface, (50, 54, 62), sh_rect, 0, 3.1415, 3)
        pygame.draw.arc(surface, (200, 205, 215), sh_rect.move(0, -1), 0, 3.1415, 2)

        # Body (carved metal padlock body with bevel and keyhole)
        b_rect = pygame.Rect(center_x - 8, center_y, 16, 13)
        pygame.draw.rect(surface, (36, 32, 28), b_rect.move(0, 2), border_radius=3)
        pygame.draw.rect(surface, (138, 142, 150), b_rect, border_radius=3)
        pygame.draw.rect(surface, (196, 202, 212), b_rect.inflate(-2, -2), border_radius=2)
        pygame.draw.rect(surface, (120, 125, 134), b_rect.inflate(-4, -4), border_radius=1)
        pygame.draw.rect(surface, (48, 44, 40), b_rect, width=1, border_radius=3)

        # Dark keyhole
        pygame.draw.circle(surface, (32, 28, 24), (center_x, center_y + 4), 2)
        pygame.draw.rect(surface, (32, 28, 24), pygame.Rect(center_x - 1, center_y + 4, 2, 4))

    def _draw_level_tile(self, surface: pygame.Surface, rect: pygame.Rect, lvl_num: int, state: str) -> None:
        """Draw an individual level tile: green completed, golden glowing selected, or locked stone with padlock."""
        if state == "selected":
            pygame.draw.rect(surface, (100, 48, 6), rect.move(0, 3), border_radius=8)
            pygame.draw.rect(surface, (250, 182, 52), rect, border_radius=8)
            pygame.draw.rect(surface, (255, 222, 118), rect.inflate(-4, -4), border_radius=6)
            pygame.draw.rect(surface, (246, 170, 40), rect.inflate(-6, -6), border_radius=5)
            pygame.draw.rect(surface, (92, 42, 6), rect, width=3, border_radius=8)
            txt = self.font_input.render(str(lvl_num), True, (48, 18, 4))
            surface.blit(txt, txt.get_rect(center=rect.center))

        elif state == "completed":
            pygame.draw.rect(surface, (12, 54, 28), rect.move(0, 3), border_radius=8)
            pygame.draw.rect(surface, (34, 148, 82), rect, border_radius=8)
            pygame.draw.rect(surface, (60, 188, 112), rect.inflate(-4, -4), border_radius=6)
            pygame.draw.rect(surface, (28, 136, 74), rect.inflate(-6, -6), border_radius=5)
            pygame.draw.rect(surface, (10, 50, 26), rect, width=2, border_radius=8)

            txt = self.font_input.render(str(lvl_num), True, (255, 218, 88))
            txt_s = self.font_input.render(str(lvl_num), True, (10, 50, 26))
            rc = txt.get_rect(center=rect.center)
            surface.blit(txt_s, rc.move(0, 1))
            surface.blit(txt, rc)

        else:
            # Drop shadow
            pygame.draw.rect(surface, (42, 38, 34), rect.move(0, 3), border_radius=8)
            # Stone body with bevel
            pygame.draw.rect(surface, (132, 122, 114), rect, border_radius=8)
            pygame.draw.rect(surface, (162, 152, 144), rect.inflate(-4, -4), border_radius=6)
            pygame.draw.rect(surface, (118, 108, 100), rect.inflate(-6, -6), border_radius=5)
            pygame.draw.rect(surface, (48, 42, 38), rect, width=2, border_radius=8)

            # Authentic stone fissure cracks
            pygame.draw.line(surface, (78, 70, 64), (rect.x + 8, rect.bottom - 10), (rect.x + 18, rect.bottom - 18), 1)
            pygame.draw.line(surface, (78, 70, 64), (rect.right - 10, rect.y + 10), (rect.right - 18, rect.y + 18), 1)

            # Carved stone number
            txt = self.font_input.render(str(lvl_num), True, (56, 48, 42))
            txt_shadow = self.font_input.render(str(lvl_num), True, (176, 168, 160))
            num_rc = txt.get_rect(center=(rect.centerx, rect.y + 17))
            surface.blit(txt_shadow, num_rc.move(0, 1))
            surface.blit(txt, num_rc)

            # Padlock icon
            self._draw_padlock(surface, rect.centerx, rect.bottom - 14)

    def draw_level_select_screen(
        self,
        surface: pygame.Surface,
        user_stats: Optional[Dict[str, Any]] = None
    ) -> None:
        """Render the exact retro-pixel RPG Select Level parchment screen."""
        cx = self.screen_width // 2
        card_w = 560
        card_h = 715
        card_x = cx - card_w // 2
        card_y = 30
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # 1. Dark dungeon stone brick wall background
        self._draw_dungeon_background(surface)

        # 2. Main Parchment Sheet Chassis
        self._draw_parchment_chassis(surface, card_rect)

        # 3. Royal Crown & 3D Title "SELECT LEVEL"
        self._draw_royal_crown(surface, cx, card_y + 26)
        self._draw_adventure_title(surface, "SELECT LEVEL", card_y + 48, self.font_title_top, cx)

        # Calculate max unlocked level from user stats
        victories = user_stats.get("victories", 0) if user_stats else 11
        unlocked_max = max(1, min(50, 1 + victories))

        # Check page offset based on selected level
        base_offset = 15 if self.selected_chamber_level > 35 else 0

        # Draw the 35 level tiles (5x7)
        for i, btn in enumerate(self.level_tile_buttons):
            lvl = base_offset + i + 1
            btn.tag = str(lvl)

            if lvl == self.selected_chamber_level:
                st = "selected"
            elif lvl <= unlocked_max:
                st = "completed"
            else:
                st = "locked"

            self._draw_level_tile(surface, btn.rect, lvl, st)

        # 4. Status Footer: "UNLOCKED: {unlocked_max} / 50"
        st_y = card_y + 115 + 7 * 66 + 8
        status_txt = self.font_label.render(f"UNLOCKED: {unlocked_max} / 50", True, (54, 24, 6))
        surface.blit(status_txt, status_txt.get_rect(center=(cx, st_y)))

        # 5. Bottom Action Buttons: [ PLAY LEVEL {N} ] and [ BACK ]
        self.btn_level_play.text = f"PLAY LEVEL {self.selected_chamber_level}"
        self.btn_level_play.draw(surface)
        self.btn_level_back.draw(surface)

    def _init_overlay_buttons(self) -> None:
        """Initialize buttons for VICTORY, DEFEAT, and PAUSE states."""
        cx = self.screen_width // 2
        cy = self.screen_height // 2

        # Victory Overlay
        self.btn_next_level = UIButton(pygame.Rect(cx - 210, 430, 195, 42), "NEXT LEVEL >>", self.font_header,
                                       accent_color=COLOR_TEXT_ACCENT_GREEN)
        self.btn_victory_replay = UIButton(pygame.Rect(cx + 15, 430, 195, 42), "REPLAY LEVEL", self.font_header)
        self.btn_victory_menu = UIButton(pygame.Rect(cx - 100, 490, 200, 38), "HOME MENU", self.font_body)

        # Defeat Overlay
        self.btn_retry_level = UIButton(pygame.Rect(cx - 210, 440, 195, 42), "RETRY MISSION", self.font_header,
                                        accent_color=COLOR_TEXT_ACCENT_RED)
        self.btn_defeat_menu = UIButton(pygame.Rect(cx + 15, 440, 195, 42), "HOME MENU", self.font_header)

        # Tactical Pause Overlay (Right margin dock leaves entire center grid 100% visible for explanation)
        self.btn_pause_resume = UIButton(pygame.Rect(785, 82, 160, 34), "RESUME", self.font_header,
                                         accent_color=COLOR_TEXT_ACCENT_GREEN)
        self.btn_pause_restart = UIButton(pygame.Rect(785, 122, 160, 34), "RESTART", self.font_header,
                                          accent_color=COLOR_TEXT_ACCENT_CYAN)
        self.btn_pause_help = UIButton(pygame.Rect(785, 162, 160, 32), "CONTROLS", self.font_body)
        self.btn_pause_menu = UIButton(pygame.Rect(785, 198, 160, 32), "MAIN MENU", self.font_body,
                                       accent_color=COLOR_TEXT_ACCENT_RED)

    def update(self, dt: float) -> None:
        """Update animation timers and interactive text fields."""
        self.anim_time += dt
        self.input_player_name.update(dt)
        self.input_login_username.update(dt)

    def compute_grid_geometry(self, grid_size: int) -> Tuple[float, float, float]:
        """
        Dynamically scale cell pixel sizes so the chosen N x N grid fits cleanly
        centered above the bottom HUD console.

        Returns:
            Tuple of (origin_x, origin_y, cell_size)
        """
        top_margin = 20
        bottom_limit = self.screen_height - self.hud_height - 20
        max_h = bottom_limit - top_margin
        max_w = self.screen_width - 40

        cell_size = math.floor(min(max_w / grid_size, max_h / grid_size))
        # Ensure cell size has a minimum readable dimension
        cell_size = max(cell_size, 32.0)

        grid_total_w = cell_size * grid_size
        grid_total_h = cell_size * grid_size

        origin_x = (self.screen_width - grid_total_w) / 2.0
        origin_y = top_margin + (max_h - grid_total_h) / 2.0

        return (origin_x, origin_y, float(cell_size))

    # =========================================================================
    # SPLASH & LOGIN SCREEN RENDERING
    # =========================================================================
    def draw_splash_screen(self, surface: pygame.Surface, splash_timer: float, splash_duration: float = 2.5) -> None:
        """
        Render the cinematic sci-fi intro splash screen.
        Displays an animated boot sequence, pulsing logo, and system loading progress bar.
        """
        surface.fill(COLOR_BG)
        cx = self.screen_width // 2
        cy = self.screen_height // 2

        # 1. Dark Blueprint Background Grid
        for x in range(0, self.screen_width, 48):
            pygame.draw.line(surface, (14, 22, 34), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, 48):
            pygame.draw.line(surface, (14, 22, 34), (0, y), (self.screen_width, y), 1)

        # Sweeping cyan radar beam
        beam_y = int((self.anim_time * 180.0) % self.screen_height)
        beam_surf = pygame.Surface((self.screen_width, 3), pygame.SRCALPHA)
        beam_surf.fill((255, 200, 50, 40))
        surface.blit(beam_surf, (0, beam_y))

        # 2. Central Tactical Crest / Logo
        pulse_r = int(54 + 4 * math.sin(self.anim_time * 5.0))
        logo_y = cy - 130

        # Outer pulsing rings
        pygame.draw.circle(surface, (120, 85, 25), (cx, logo_y), pulse_r + 14, 1)
        pygame.draw.circle(surface, (225, 175, 55), (cx, logo_y), pulse_r, 2)
        pygame.draw.circle(surface, (25, 28, 38), (cx, logo_y), pulse_r - 2)

        # Tactical Crosshairs
        pygame.draw.line(surface, (225, 175, 55), (cx - pulse_r - 12, logo_y), (cx + pulse_r + 12, logo_y), 1)
        pygame.draw.line(surface, (225, 175, 55), (cx, logo_y - pulse_r - 12), (cx, logo_y + pulse_r + 12), 1)

        # Central Golden Diamond (Treasure Key symbol)
        kd_sz = 16
        k_pts = [(cx, logo_y - kd_sz), (cx + kd_sz, logo_y), (cx, logo_y + kd_sz), (cx - kd_sz, logo_y)]
        pygame.draw.polygon(surface, COLOR_KEY_GOLD, k_pts)
        pygame.draw.polygon(surface, (255, 240, 140), k_pts, 2)
        pygame.draw.circle(surface, (255, 255, 255), (cx, logo_y), 3)

        # 3. Main Titles
        cat_badge = self.font_badge.render("// THE LOST TEMPLE EXPEDITION //", True, COLOR_TEXT_ACCENT_AMBER)
        surface.blit(cat_badge, cat_badge.get_rect(center=(cx, logo_y + pulse_r + 26)))

        main_title = self.font_title.render("TREASURE HUNTER", True, COLOR_KEY_GOLD)
        sh_title = self.font_title.render("TREASURE HUNTER", True, (90, 60, 15))
        surface.blit(sh_title, sh_title.get_rect(center=(cx + 2, logo_y + pulse_r + 58)))
        surface.blit(main_title, main_title.get_rect(center=(cx, logo_y + pulse_r + 56)))

        sub_title = self.font_bold.render("ANCIENT SANCTUARY & RELIC EXTRACTION PROTOCOL", True, (215, 205, 180))
        surface.blit(sub_title, sub_title.get_rect(center=(cx, logo_y + pulse_r + 86)))

        # 4. Animated Boot Sequence Console
        boot_box = pygame.Rect(cx - 250, cy + 80, 500, 120)
        pygame.draw.rect(surface, (8, 12, 20), boot_box, border_radius=6)
        pygame.draw.rect(surface, (30, 48, 72), boot_box, width=1, border_radius=6)
        pygame.draw.rect(surface, (220, 165, 50), (boot_box.x, boot_box.y, 500, 20), border_radius=4)
        surface.blit(self.font_small.render("EXPEDITION JOURNAL & SUBSYSTEM INITIALIZATION", True, (18, 20, 28)), (boot_box.x + 10, boot_box.y + 3))

        boot_logs = [
            (0.2, "[01] EXPEDITION ENGINE & NUMPY SYNTHESIZER ... [ READY ]", COLOR_TEXT_PRIMARY),
            (0.7, "[02] SQLITE3 GUILD DOSSIER ARCHIVE ......... [ CONNECTED ]", COLOR_TEXT_ACCENT_GREEN),
            (1.2, "[03] CELESTIAL COMPASS & CHAMBER MATRIX ..... [ CALIBRATED ]", COLOR_TEXT_ACCENT_CYAN),
            (1.7, "[04] TEMPLE GUARDIAN EVASION TRACKER ....... [ ONLINE ]", COLOR_TEXT_ACCENT_AMBER),
        ]
        log_y = boot_box.y + 28
        for threshold, text, color in boot_logs:
            if splash_timer >= threshold:
                surface.blit(self.font_small.render(text, True, color), (boot_box.x + 14, log_y))
            else:
                surface.blit(self.font_small.render("...", True, COLOR_TEXT_MUTED), (boot_box.x + 14, log_y))
            log_y += 20

        # 5. Cyber Loading Progress Bar
        pct = min(1.0, max(0.0, splash_timer / splash_duration))
        bar_w = 460
        bar_h = 14
        bar_x = cx - bar_w // 2
        bar_y = cy + 218

        pygame.draw.rect(surface, (12, 18, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        pygame.draw.rect(surface, (36, 60, 95), (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=3)
        fill_w = int(bar_w * pct)
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_x + 1, bar_y + 1, fill_w - 2, bar_h - 2)
            pygame.draw.rect(surface, (245, 195, 45), fill_rect, border_radius=2)
            pygame.draw.circle(surface, (255, 255, 255), (bar_x + fill_w - 2, bar_y + bar_h // 2), 3)

        prog_txt = self.font_small.render(f"INITIALIZING EXPEDITION ... {int(pct * 100)}%", True, COLOR_TEXT_SECONDARY)
        surface.blit(prog_txt, prog_txt.get_rect(center=(cx, bar_y + 24)))

        # 6. Pulsing Skip/Continue Prompt
        blink = (math.sin(self.anim_time * 6.0) + 1.0) * 0.5
        col = (int(100 + 155 * blink), int(160 + 95 * blink), int(200 + 55 * blink))
        cont_surf = self.font_bold.render(">> PRESS SPACE / ENTER OR CLICK TO COMMENCE EXPEDITION <<", True, col)
        surface.blit(cont_surf, cont_surf.get_rect(center=(cx, self.screen_height - 35)))

    def draw_login_screen(
        self,
        surface: pygame.Surface,
        recent_operatives: List[Dict[str, Any]] = None,
        status_msg: str = "AWAITING CREDENTIALS"
    ) -> None:
        """
        Render the Operative Authentication and Login screen.
        All match outcomes and telemetry are persisted based on this identity.
        """
        surface.fill(COLOR_BG)
        cx = self.screen_width // 2

        # 1. Subtle Background Grid
        for x in range(0, self.screen_width, 60):
            pygame.draw.line(surface, (14, 20, 32), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, 60):
            pygame.draw.line(surface, (14, 20, 32), (0, y), (self.screen_width, y), 1)

        # 2. Header
        cat_badge = self.font_badge.render("// EXPLORER GUILD DOSSIER :: REGISTRATION //", True, COLOR_TEXT_ACCENT_AMBER)
        surface.blit(cat_badge, cat_badge.get_rect(center=(cx, 32)))

        main_title = self.font_title.render("EXPLORER AUTHENTICATION", True, COLOR_KEY_GOLD)
        sh_title = self.font_title.render("EXPLORER AUTHENTICATION", True, (90, 60, 15))
        surface.blit(sh_title, sh_title.get_rect(center=(cx + 2, 68)))
        surface.blit(main_title, main_title.get_rect(center=(cx, 66)))

        sub_title = self.font_bold.render("LINK PERSISTENT EXPEDITION RECORDS & RELIC VICTORIES IN SQLITE ARCHIVES", True, (215, 205, 180))
        surface.blit(sub_title, sub_title.get_rect(center=(cx, 100)))

        # 3. Main Glassmorphic Login Dossier Chassis (Focused & Clean without profile lists)
        card_w = 540
        card_h = 350
        card_x = cx - card_w // 2
        card_y = 135
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # Drop shadow & Translucent Glass
        pygame.draw.rect(surface, (6, 8, 14), card_rect.move(0, 4), border_radius=8)
        glass_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        glass_surf.fill((16, 20, 30, 240))
        surface.blit(glass_surf, card_rect.topleft)

        # Ancient Gold & Stone borders
        pygame.draw.rect(surface, (65, 80, 110), card_rect, width=1, border_radius=8)
        pygame.draw.rect(surface, (225, 175, 55), card_rect.inflate(-4, -4), width=1, border_radius=6)

        # Corner ticks
        t_sz = 12
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x, card_y), (card_x + t_sz, card_y), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x, card_y), (card_x, card_y + t_sz), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x + card_w - 1, card_y), (card_x + card_w - 1 - t_sz, card_y), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x + card_w - 1, card_y), (card_x + card_w - 1, card_y + t_sz), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x, card_y + card_h - 1), (card_x + t_sz, card_y + card_h - 1), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x, card_y + card_h - 1), (card_x, card_y + card_h - 1 - t_sz), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x + card_w - 1, card_y + card_h - 1), (card_x + card_w - 1 - t_sz, card_y + card_h - 1), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x + card_w - 1, card_y + card_h - 1), (card_x + card_w - 1, card_y + card_h - 1 - t_sz), 2)

        # Top Card Ribbon
        pygame.draw.line(surface, (45, 55, 78), (card_x + 20, card_y + 34), (card_x + card_w - 20, card_y + 34), 1)
        ribbon_txt = self.font_badge.render("// GUILD ARCHIVES :: EXPEDITION REGISTRATION //", True, COLOR_TEXT_SECONDARY)
        surface.blit(ribbon_txt, (card_x + 24, card_y + 12))

        # Explorer Fedora Emblem in Card
        avatar_cx = cx
        avatar_cy = card_y + 70
        pygame.draw.circle(surface, (25, 20, 24), (avatar_cx, avatar_cy), 24)
        pygame.draw.circle(surface, (225, 175, 55), (avatar_cx, avatar_cy), 24, 2)
        # Fedora / Explorer Headgear
        pygame.draw.ellipse(surface, (140, 85, 45), pygame.Rect(avatar_cx - 16, avatar_cy - 8, 32, 14))
        pygame.draw.ellipse(surface, (225, 175, 55), pygame.Rect(avatar_cx - 10, avatar_cy - 12, 20, 8))
        pygame.draw.circle(surface, (255, 255, 255), (avatar_cx - 4, avatar_cy - 2), 2)
        pygame.draw.circle(surface, (255, 255, 255), (avatar_cx + 4, avatar_cy - 2), 2)

        # Prompt
        lbl = self.font_bold.render("ENTER EXPLORER CALLSIGN / NAME:", True, COLOR_TEXT_PRIMARY)
        surface.blit(lbl, lbl.get_rect(center=(cx, card_y + 116)))

        # Text Input Box
        self.input_login_username.draw(surface)

        # Status text below input
        stat_color = COLOR_TEXT_ACCENT_GREEN if "SUCCESS" in status_msg.upper() or "AUTHENTICATED" in status_msg.upper() else COLOR_TEXT_MUTED
        st_surf = self.font_small.render(f"STATUS: {status_msg}", True, stat_color)
        surface.blit(st_surf, st_surf.get_rect(center=(cx, card_y + 195)))

        # Action Buttons
        self.btn_login_submit.draw(surface)
        self.btn_login_guest.draw(surface)

        # Bottom Dock Note
        note_surf = self.font_small.render("[ All expedition progress is automatically saved to SQLite dungeon_records.db ]", True, COLOR_TEXT_MUTED)
        surface.blit(note_surf, note_surf.get_rect(center=(cx, self.screen_height - 35)))

    # =========================================================================
    # HOME SCREEN RENDERING (AUTHENTIC PARCHMENT SCROLL & DUNGEON WALLS)
    # =========================================================================
    def _draw_dungeon_background(self, surface: pygame.Surface) -> None:
        """Render dark dungeon stone walls with warm torchlight ambient lighting."""
        surface.fill((20, 15, 17))
        brick_w, brick_h = 84, 42
        for row, y in enumerate(range(0, self.screen_height, brick_h)):
            offset = (brick_w // 2) if (row % 2 == 1) else 0
            for x in range(-offset, self.screen_width + brick_w, brick_w):
                rect = pygame.Rect(x, y, brick_w - 3, brick_h - 3)
                dist_x = abs((x + brick_w // 2) - self.screen_width // 2) / (self.screen_width // 2)
                dist_y = abs((y + brick_h // 2) - self.screen_height // 2) / (self.screen_height // 2)
                falloff = max(0.0, 1.0 - (dist_x * 0.5 + dist_y * 0.5))
                base_r = int(32 + 25 * falloff)
                base_g = int(24 + 16 * falloff)
                base_b = int(26 + 10 * falloff)
                v = ((x * 23 + y * 41) % 15) - 7
                pygame.draw.rect(surface, (base_r + v, base_g + v, base_b + v), rect, border_radius=3)
                pygame.draw.line(surface, (10, 8, 9), (x, y + brick_h - 3), (x + brick_w - 3, y + brick_h - 3), 2)
                pygame.draw.line(surface, (10, 8, 9), (x + brick_w - 3, y), (x + brick_w - 3, y + brick_h - 3), 2)
                pygame.draw.line(surface, (base_r + v + 16, base_g + v + 12, base_b + v + 10), (x + 2, y + 1), (x + brick_w - 5, y + 1), 1)

    def _draw_parchment_chassis(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw aged parchment scroll sheet with carved wood border and brass corner rivets."""
        # Drop shadow
        shadow_rect = rect.move(0, 10)
        shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        shadow_surf.fill((6, 4, 6, 200))
        surface.blit(shadow_surf, shadow_rect.topleft)

        # Aged parchment paper fill
        pygame.draw.rect(surface, (230, 195, 138), rect, border_radius=14)
        inner_rect = rect.inflate(-10, -10)
        pygame.draw.rect(surface, (240, 212, 162), inner_rect, border_radius=10)

        # Dark carved wood / leather contour outline
        pygame.draw.rect(surface, (72, 42, 18), rect, width=4, border_radius=14)
        # Inner decorative thin border
        pygame.draw.rect(surface, (200, 162, 110), inner_rect.inflate(-8, -8), width=1, border_radius=8)

        # 4 Golden Brass Bolts / Rivets in the corners
        rivet_offset = 22
        rivet_pts = [
            (rect.left + rivet_offset, rect.top + rivet_offset),
            (rect.right - rivet_offset, rect.top + rivet_offset),
            (rect.left + rivet_offset, rect.bottom - rivet_offset),
            (rect.right - rivet_offset, rect.bottom - rivet_offset),
        ]
        for rx, ry in rivet_pts:
            pygame.draw.circle(surface, (54, 30, 12), (rx, ry), 9)
            pygame.draw.circle(surface, (196, 142, 42), (rx, ry), 8)
            pygame.draw.circle(surface, (248, 196, 72), (rx, ry), 6)
            pygame.draw.circle(surface, (255, 248, 180), (rx - 2, ry - 2), 3)

    def _draw_royal_crown(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Render golden royal crown with emerald and ruby gemstones."""
        pts = [
            (x - 34, y + 26),
            (x - 30, y + 6),
            (x - 16, y + 15),
            (x, y - 2),
            (x + 16, y + 15),
            (x + 30, y + 6),
            (x + 34, y + 26),
        ]
        shadow_pts = [(px, py + 3) for px, py in pts]
        pygame.draw.polygon(surface, (52, 24, 6), shadow_pts)
        pygame.draw.polygon(surface, (248, 182, 34), pts)
        pygame.draw.polygon(surface, (52, 24, 6), pts, 3)

        band_rect = pygame.Rect(x - 34, y + 20, 68, 10)
        pygame.draw.rect(surface, (218, 148, 24), band_rect, border_radius=3)
        pygame.draw.rect(surface, (52, 24, 6), band_rect, width=2, border_radius=3)

        pygame.draw.ellipse(surface, (46, 204, 113), pygame.Rect(x - 6, y + 22, 12, 7))
        pygame.draw.ellipse(surface, (20, 90, 45), pygame.Rect(x - 6, y + 22, 12, 7), 1)
        pygame.draw.circle(surface, (255, 255, 255), (x - 2, y + 24), 1)

        pygame.draw.circle(surface, (231, 76, 60), (x - 20, y + 25), 3)
        pygame.draw.circle(surface, (231, 76, 60), (x + 20, y + 25), 3)

    def _draw_adventure_title(self, surface: pygame.Surface, text: str, y_pos: int, font: pygame.font.Font, cx: int) -> None:
        """Render stacked 3D adventure typography with dark chocolate extrusion and gold gradient."""
        txt_surf = font.render(text, True, (250, 185, 45))
        tw, th = txt_surf.get_size()
        tx = cx - tw // 2

        for off_y in [6, 5, 4]:
            for ox in [-1, 0, 1]:
                s_surf = font.render(text, True, (46, 18, 5))
                surface.blit(s_surf, (tx + ox, y_pos + off_y))

        outline_surf = font.render(text, True, (46, 18, 5))
        for dx in [-3, -2, -1, 0, 1, 2, 3]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    surface.blit(outline_surf, (tx + dx, y_pos + dy))

        for ox in [-1, 0, 1]:
            surface.blit(txt_surf, (tx + ox, y_pos))

        glint_surf = font.render(text, True, (255, 246, 170))
        surface.blit(glint_surf, (tx, y_pos - 1))

    def _draw_trophy_badge(self, surface: pygame.Surface, rect: pygame.Rect, text: str) -> None:
        """Render wooden capsule trophy plaque."""
        pygame.draw.rect(surface, (56, 28, 10), rect.move(0, 2), border_radius=10)
        pygame.draw.rect(surface, (200, 146, 88), rect, border_radius=10)
        pygame.draw.rect(surface, (222, 178, 122), rect.inflate(-4, -4), border_radius=8)
        pygame.draw.rect(surface, (68, 34, 12), rect, width=2, border_radius=10)

        ic_x = rect.left + 20
        ic_y = rect.centery
        cup_pts = [(ic_x - 8, ic_y - 8), (ic_x + 8, ic_y - 8), (ic_x + 6, ic_y + 1), (ic_x - 6, ic_y + 1)]
        pygame.draw.polygon(surface, (246, 186, 42), cup_pts)
        pygame.draw.polygon(surface, (68, 34, 12), cup_pts, 1)
        pygame.draw.arc(surface, (68, 34, 12), pygame.Rect(ic_x - 12, ic_y - 8, 8, 8), 1.5, 4.5, 2)
        pygame.draw.arc(surface, (68, 34, 12), pygame.Rect(ic_x + 4, ic_y - 8, 8, 8), 4.8, 1.4, 2)
        pygame.draw.rect(surface, (246, 186, 42), (ic_x - 2, ic_y + 1, 4, 4))
        pygame.draw.rect(surface, (246, 186, 42), (ic_x - 7, ic_y + 5, 14, 3))
        pygame.draw.rect(surface, (68, 34, 12), (ic_x - 7, ic_y + 5, 14, 3), 1)

        lbl = self.font_badge.render(text, True, (48, 20, 6))
        surface.blit(lbl, (rect.left + 38, rect.centery - lbl.get_height() // 2))

    def _draw_difficulty_bar(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render segmented difficulty selector with active Emerald Ribbon banner."""
        pygame.draw.rect(surface, (68, 34, 12), rect, border_radius=8)
        pygame.draw.rect(surface, (202, 152, 96), rect.inflate(-4, -4), border_radius=6)

        for btn in self.level_buttons:
            if btn.is_selected:
                ribbon_rect = btn.rect.inflate(4, 6)
                pygame.draw.rect(surface, (16, 84, 44), ribbon_rect.move(0, 3), border_radius=6)
                pygame.draw.rect(surface, (34, 156, 88), ribbon_rect, border_radius=6)
                pygame.draw.rect(surface, (64, 200, 122), ribbon_rect.inflate(-4, -4), border_radius=4)
                pygame.draw.rect(surface, (28, 142, 78), ribbon_rect.inflate(-8, -8), border_radius=3)
                pygame.draw.rect(surface, (10, 58, 30), ribbon_rect, width=3, border_radius=6)

                notch_pts = [
                    (ribbon_rect.x + 2, ribbon_rect.bottom - 1),
                    (ribbon_rect.x + ribbon_rect.width // 2, ribbon_rect.bottom + 9),
                    (ribbon_rect.right - 2, ribbon_rect.bottom - 1),
                ]
                pygame.draw.polygon(surface, (28, 142, 78), notch_pts)
                pygame.draw.lines(surface, (10, 58, 30), False, notch_pts, 3)

                txt = self.font_btn_bold.render(btn.text, True, (255, 255, 255))
                txt_s = self.font_btn_bold.render(btn.text, True, (10, 58, 30))
                t_rc = txt.get_rect(center=ribbon_rect.center)
                surface.blit(txt_s, t_rc.move(0, 1))
                surface.blit(txt, t_rc)
            else:
                txt = self.font_btn_bold.render(btn.text, True, (54, 24, 6))
                surface.blit(txt, txt.get_rect(center=btn.rect.center))

        # Vertical separator lines between unselected items
        for i in range(len(self.level_buttons) - 1):
            b1 = self.level_buttons[i]
            b2 = self.level_buttons[i + 1]
            if not b1.is_selected and not b2.is_selected:
                pygame.draw.line(surface, (116, 68, 28), (b1.rect.right, rect.top + 6), (b1.rect.right, rect.bottom - 6), 2)

    def draw_home_screen(
        self,
        surface: pygame.Surface,
        best_victory_steps: Optional[int],
        user_stats: Optional[Dict[str, Any]] = None
    ) -> None:
        """Render identical Main Menu matching retro-pixel RPG adventure parchment design."""
        cx = self.screen_width // 2
        card_w = 560
        card_h = 715
        card_x = cx - card_w // 2
        card_y = 30
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # 1. Dungeon brick wall background with torch ambiance
        self._draw_dungeon_background(surface)

        # 2. Main Parchment Sheet Chassis
        self._draw_parchment_chassis(surface, card_rect)

        # 3. Royal Crown & 3D Adventure Title
        self._draw_royal_crown(surface, cx, card_y + 14)
        self._draw_adventure_title(surface, "TREASURE", card_y + 40, self.font_title_top, cx)
        self._draw_adventure_title(surface, "HUNTER", card_y + 86, self.font_title_bot, cx)

        # 4. Trophies & Stats Badges
        best_text = f"BEST: {best_victory_steps} STEPS" if best_victory_steps is not None else "BEST: 14 STEPS"
        victories = user_stats.get("victories", 0) if user_stats else 11
        user_level = max(1, min(50, 1 + victories))
        level_text = f"LEVEL: {user_level} / 50"

        self._draw_trophy_badge(surface, pygame.Rect(cx - 225, card_y + 150, 220, 36), best_text)
        self._draw_trophy_badge(surface, pygame.Rect(cx + 5, card_y + 150, 220, 36), level_text)

        # 5. PLAYER NAME Section
        lbl_p = self.font_label.render("PLAYER NAME", True, (54, 24, 6))
        surface.blit(lbl_p, lbl_p.get_rect(center=(cx, card_y + 208)))
        self.input_player_name.draw(surface)

        # 6. GRID SIZE Section
        lbl_g = self.font_label.render("GRID SIZE", True, (54, 24, 6))
        surface.blit(lbl_g, lbl_g.get_rect(center=(cx, card_y + 292)))
        for btn in self.grid_buttons:
            btn.draw(surface)

        # 7. DIFFICULTY Section
        lbl_d = self.font_label.render("DIFFICULTY", True, (54, 24, 6))
        surface.blit(lbl_d, lbl_d.get_rect(center=(cx, card_y + 398)))
        self._draw_difficulty_bar(surface, pygame.Rect(cx - 225, card_y + 420, 450, 44))

        # 8. Primary CTA START MISSION Button
        self.btn_start_mission.draw(surface)

        # 9. Secondary Buttons Row 1: Levels & How To Play
        self.btn_levels.draw(surface)
        self.btn_how_to_play.draw(surface)

        # 10. Secondary Buttons Row 2: Settings & Exit
        self.btn_settings.draw(surface)
        self.btn_exit.draw(surface)

        # 11. Optional Modal Dialogs (Levels Browser or Settings)
        if self.show_levels_modal:
            self._draw_levels_modal(surface, user_level)
        elif self.show_settings_modal:
            self._draw_settings_modal(surface)

    def _draw_levels_modal(self, surface: pygame.Surface, user_level: int) -> None:
        """Render interactive Levels (1-50) Browser Modal."""
        dim_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 180))
        surface.blit(dim_surf, (0, 0))

        cx = self.screen_width // 2
        mw, mh = 500, 480
        mx, my = cx - mw // 2, 140
        modal_rect = pygame.Rect(mx, my, mw, mh)
        self._draw_parchment_chassis(surface, modal_rect)

        # Title
        t_surf = self.font_label.render("EXPEDITION CHAMBERS (LEVELS 1 - 50)", True, (54, 24, 6))
        surface.blit(t_surf, t_surf.get_rect(center=(cx, my + 30)))

        # 5x10 Chamber Grid
        cols = 10
        cell_sz = 38
        gap = 8
        grid_w = cols * cell_sz + (cols - 1) * gap
        grid_start_x = cx - grid_w // 2
        grid_start_y = my + 60

        for lvl in range(1, 51):
            idx = lvl - 1
            r = idx // cols
            c = idx % cols
            cell_x = grid_start_x + c * (cell_sz + gap)
            cell_y = grid_start_y + r * (cell_sz + gap)
            c_rect = pygame.Rect(cell_x, cell_y, cell_sz, cell_sz)

            is_unlocked = (lvl <= user_level)
            is_active = (lvl == self.selected_chamber_level)

            if is_active:
                pygame.draw.rect(surface, (250, 182, 52), c_rect, border_radius=6)
                pygame.draw.rect(surface, (92, 42, 6), c_rect, width=2, border_radius=6)
                txt = self.font_small.render(str(lvl), True, (52, 22, 4))
            elif is_unlocked:
                pygame.draw.rect(surface, (200, 150, 94), c_rect, border_radius=6)
                pygame.draw.rect(surface, (68, 34, 12), c_rect, width=1, border_radius=6)
                txt = self.font_small.render(str(lvl), True, (52, 22, 4))
            else:
                pygame.draw.rect(surface, (136, 126, 118), c_rect, border_radius=6)
                pygame.draw.rect(surface, (50, 44, 40), c_rect, width=1, border_radius=6)
                txt = self.font_small.render(str(lvl), True, (80, 72, 68))

            surface.blit(txt, txt.get_rect(center=c_rect.center))

        # Close Button
        self.btn_close_modal.rect = pygame.Rect(cx - 70, my + mh - 50, 140, 36)
        self.btn_close_modal.draw(surface)

    def _draw_settings_modal(self, surface: pygame.Surface) -> None:
        """Render Settings & Options Modal."""
        dim_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 180))
        surface.blit(dim_surf, (0, 0))

        cx = self.screen_width // 2
        mw, mh = 420, 300
        mx, my = cx - mw // 2, 220
        modal_rect = pygame.Rect(mx, my, mw, mh)
        self._draw_parchment_chassis(surface, modal_rect)

        t_surf = self.font_label.render("EXPEDITION SETTINGS", True, (54, 24, 6))
        surface.blit(t_surf, t_surf.get_rect(center=(cx, my + 35)))

        # Audio toggle button
        sfx_label = "AUDIO SFX: [ ON ]" if self.sound_enabled else "AUDIO SFX: [ MUTED ]"
        self.btn_toggle_sfx.text = sfx_label
        self.btn_toggle_sfx.rect = pygame.Rect(cx - 130, my + 80, 260, 42)
        self.btn_toggle_sfx.draw(surface)

        # Switch user button
        self.btn_modal_switch_user.rect = pygame.Rect(cx - 130, my + 138, 260, 42)
        self.btn_modal_switch_user.draw(surface)

        # Close button
        self.btn_close_modal.rect = pygame.Rect(cx - 70, my + mh - 54, 140, 36)
        self.btn_close_modal.draw(surface)
    # =========================================================================
    # HOW TO PLAY SCREEN RENDERING
    # =========================================================================
    def draw_how_to_play_screen(self, surface: pygame.Surface) -> None:
        """Render the tactical instruction briefing screen."""
        surface.fill(COLOR_BG)

        # Header
        title = self.font_title.render("MISSION BRIEFING // HOW TO PLAY", True, COLOR_TEXT_ACCENT_CYAN)
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, 40))

        # Panel Box
        panel_rect = pygame.Rect(120, 95, self.screen_width - 240, 560)
        pygame.draw.rect(surface, COLOR_HUD_BG, panel_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_HUD_BORDER, panel_rect, width=1, border_radius=6)

        y = 120
        # Section 1: Objectives
        h1 = self.font_header.render("[ 1. PRIMARY OBJECTIVES ]", True, COLOR_TEXT_ACCENT_AMBER)
        surface.blit(h1, (150, y))
        y += 30
        lines1 = [
            "• INFILTRATION: You enter the sector at Start coordinate (0, 0).",
            "• KEY ACQUISITION: Locate and collect the Golden Cipher Key [K] on the grid.",
            "• EXTRACTION: Reach the Exit Portal [E] at (N-1, N-1) only AFTER securing the key.",
            "• EVASION: Evade Gemini-controlled Hunter Drones [H]. One collision results in casualty."
        ]
        for line in lines1:
            txt = self.font_body.render(line, True, COLOR_TEXT_PRIMARY)
            surface.blit(txt, (160, y))
            y += 24

        y += 15
        # Section 2: Controls
        h2 = self.font_header.render("[ 2. TACTICAL CONTROLS ]", True, COLOR_TEXT_ACCENT_CYAN)
        surface.blit(h2, (150, y))
        y += 30
        lines2 = [
            "• WASD / Arrow Keys : Move Operative one grid cell in cardinal direction.",
            "• [P] / [SPACE] / ||: Pause or Resume the mission at any time.",
            "• [H]               : Manually deploy a Hunter Drone reinforcement (up to 8 max).",
            "• [B]               : Trigger dynamic Barrier Shift (relocate walls safely).",
            "• [R]               : Reset mission with fresh procedural layout.",
            "• [ESC]             : Pause mission (or return to menu)."
        ]
        for line in lines2:
            txt = self.font_body.render(line, True, COLOR_TEXT_PRIMARY)
            surface.blit(txt, (160, y))
            y += 24

        y += 15
        # Section 3: Visual Guidance
        h3 = self.font_header.render("[ 3. HUD VISUAL GUIDANCE ]", True, COLOR_TEXT_ACCENT_GREEN)
        surface.blit(h3, (150, y))
        y += 30
        lines3 = [
            "• GREEN BREADCRUMBS : Next 3 safe coordinates computed by Gemini 2.5 Flash, dodging",
            "                      Hunter visual cones and exploiting blind spots behind them.",
            "• PULSING YELLOW ARROW : Dynamic directional beacon pointing to current objective.",
            "• DYNAMIC BARRIERS  : Obstacles shift dynamically every 2.5s (scaled by difficulty)."
        ]
        for line in lines3:
            txt = self.font_body.render(line, True, COLOR_TEXT_PRIMARY)
            surface.blit(txt, (160, y))
            y += 24

        # Back Button
        self.btn_back_to_menu.draw(surface)

    # =========================================================================
    # IN-GAME GRID & ENTITY RENDERING
    # =========================================================================
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
        """
        Render the tactical grid board, walls, key, exit portal, breadcrumbs,
        pulsing yellow guide arrow, human player operative, and human mercenary hunters.
        """
        grid_w = cell_size * grid_size
        grid_h = cell_size * grid_size

        # Grid Base Background (Rich Alternating Cyberpunk Techno Tiles)
        grid_rect = pygame.Rect(origin_x, origin_y, grid_w, grid_h)
        # Drop shadow for whole grid
        pygame.draw.rect(surface, (6, 8, 16), grid_rect.move(0, 5), border_radius=6)
        pygame.draw.rect(surface, (14, 18, 32), grid_rect, border_radius=6)

        # Alternating high-tech floor tiles for rich visual depth & color
        for r in range(grid_size):
            for c in range(grid_size):
                cell_rect = pygame.Rect(origin_x + c * cell_size, origin_y + r * cell_size, cell_size, cell_size)
                # Alternating color between deep cyber blue-indigo and dark obsidian
                tile_col = (34, 40, 54) if (r + c) % 2 == 0 else (26, 30, 42)
                pygame.draw.rect(surface, tile_col, cell_rect)

                if (r, c) not in walls:
                    cx_t = origin_x + c * cell_size
                    cy_t = origin_y + r * cell_size
                    # Floor plate illuminated neon corner pins
                    pin_col = (110, 100, 75)
                    pygame.draw.circle(surface, pin_col, (int(cx_t + 4), int(cy_t + 4)), 1)
                    pygame.draw.circle(surface, pin_col, (int(cx_t + cell_size - 4), int(cy_t + 4)), 1)
                    pygame.draw.circle(surface, pin_col, (int(cx_t + 4), int(cy_t + cell_size - 4)), 1)
                    pygame.draw.circle(surface, pin_col, (int(cx_t + cell_size - 4), int(cy_t + cell_size - 4)), 1)
                    # Subtle center micro-crosshair
                    c_mid_x = int(cx_t + cell_size / 2)
                    c_mid_y = int(cy_t + cell_size / 2)
                    pygame.draw.circle(surface, (85, 75, 55), (c_mid_x, c_mid_y), 1)

        # Dynamic Wall Relocation Visual Pulse Alert
        if wall_shift_alert > 0:
            alpha = int(min(1.0, wall_shift_alert * 2.0) * 95)
            alert_surf = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
            alert_surf.fill((0, 230, 255, alpha))
            surface.blit(alert_surf, (origin_x, origin_y))

        # Grid Coordinate Lines (Electric Blueprint)
        for r in range(grid_size + 1):
            py = origin_y + r * cell_size
            pygame.draw.line(surface, COLOR_GRID_LINE, (origin_x, py), (origin_x + grid_w, py), 1)
        for c in range(grid_size + 1):
            px = origin_x + c * cell_size
            pygame.draw.line(surface, COLOR_GRID_LINE, (px, origin_y), (px, origin_y + grid_h), 1)

        # Outer Tactical Grid Frame with Double Neon Rim (Cyan & Magenta)
        pygame.draw.rect(surface, (225, 175, 55), grid_rect, width=2, border_radius=6)
        pygame.draw.rect(surface, (65, 175, 245), grid_rect.inflate(4, 4), width=1, border_radius=8)

        # 1. PREMIUM CYBERNETIC ENERGIZED BLAST BARRIERS (WALLS)
        for (wr, wc) in walls:
            wx = origin_x + wc * cell_size
            wy = origin_y + wr * cell_size
            pad = max(2.0, cell_size * 0.04)
            w_w = cell_size - pad * 2
            w_h = cell_size - pad * 2
            w_rect = pygame.Rect(wx + pad, wy + pad, w_w, w_h)

            # Ambient drop shadow under barrier
            shadow_rect = pygame.Rect(wx + pad, wy + pad + 3, w_w, w_h)
            pygame.draw.rect(surface, (6, 8, 14), shadow_rect, border_radius=4)

            # Heavy energized obsidian composite hull plate
            pygame.draw.rect(surface, (38, 42, 56), w_rect, border_radius=4)

            # 3D Chiseled Bevel:
            # Top & Left specular highlight line (Cyan tint)
            pygame.draw.line(surface, (120, 130, 155), (w_rect.left + 1, w_rect.top + 1), (w_rect.right - 2, w_rect.top + 1), 1)
            pygame.draw.line(surface, (120, 130, 155), (w_rect.left + 1, w_rect.top + 1), (w_rect.left + 1, w_rect.bottom - 2), 1)
            # Bottom & Right dark ambient occlusion shadow
            pygame.draw.line(surface, (10, 14, 22), (w_rect.left + 1, w_rect.bottom - 1), (w_rect.right - 1, w_rect.bottom - 1), 1)
            pygame.draw.line(surface, (10, 14, 22), (w_rect.right - 1, w_rect.top + 1), (w_rect.right - 1, w_rect.bottom - 1), 1)

            # Inset reinforced armor plate (Deep Indigo)
            inset_m = max(3.0, cell_size * 0.14)
            inset_rect = pygame.Rect(wx + inset_m, wy + inset_m, cell_size - inset_m * 2, cell_size - inset_m * 2)
            pygame.draw.rect(surface, (25, 29, 40), inset_rect, border_radius=2)
            pygame.draw.rect(surface, (215, 165, 45), inset_rect, width=1, border_radius=2)

            # 4 Corner Heavy Industrial Rivets with Specular Gleams
            r_inset = inset_m * 0.52
            rivet_r = max(1.5, cell_size * 0.035)
            for rx, ry in [
                (wx + pad + r_inset, wy + pad + r_inset),
                (wx + cell_size - pad - r_inset, wy + pad + r_inset),
                (wx + pad + r_inset, wy + cell_size - pad - r_inset),
                (wx + cell_size - pad - r_inset, wy + cell_size - pad - r_inset)
            ]:
                pygame.draw.circle(surface, (8, 12, 18), (int(rx + 0.5), int(ry + 0.5)), int(rivet_r + 0.5))
                pygame.draw.circle(surface, (225, 175, 55), (int(rx), int(ry)), int(rivet_r))
                pygame.draw.circle(surface, (255, 235, 160), (int(rx - 0.5), int(ry - 0.5)), max(1, int(rivet_r * 0.5)))

            # Central Cybernetic Plasma Node & Conduits
            c_cx = wx + cell_size / 2.0
            c_cy = wy + cell_size / 2.0
            core_half = max(3.0, cell_size * 0.14)

            # Vibrant Multi-Color Circuit Conduits
            if wall_shift_alert > 0:
                h_col = (255, 160, 30)
                v_col = (255, 100, 20)
            else:
                h_col = (235, 185, 50)    # Glowing Ancient Gold Rune
                v_col = (225, 75, 45)     # Glowing Ruby Arcane Rune

            pygame.draw.line(surface, h_col, (c_cx - core_half * 1.5, c_cy), (c_cx + core_half * 1.5, c_cy), 1)
            pygame.draw.line(surface, v_col, (c_cx, c_cy - core_half * 1.5), (c_cx, c_cy + core_half * 1.5), 1)

            # Dynamic Plasma Core Pulse
            if wall_shift_alert > 0:
                p_rate = 14.0
                p_core = (255, 160, 30)
                p_glow = (255, 240, 140)
            else:
                p_rate = 3.6
                p_core = (255, 195, 40)
                p_glow = (255, 245, 180)

            p_factor = 0.82 + 0.18 * math.sin(self.anim_time * p_rate + (wr * 3 + wc * 7))
            cur_r = core_half * p_factor

            # Chamfered / Diamond Energy Crystal Core
            core_pts = [
                (c_cx, c_cy - cur_r),
                (c_cx + cur_r, c_cy),
                (c_cx, c_cy + cur_r),
                (c_cx - cur_r, c_cy)
            ]
            pygame.draw.polygon(surface, p_core, core_pts)
            # Outer neon corona ring
            pygame.draw.circle(surface, (225, 175, 55), (int(c_cx), int(c_cy)), int(cur_r * 1.25), 1)
            # Hotspot Core
            hot_r = cur_r * 0.45
            hot_pts = [
                (c_cx, c_cy - hot_r),
                (c_cx + hot_r, c_cy),
                (c_cx, c_cy + hot_r),
                (c_cx - hot_r, c_cy)
            ]
            pygame.draw.polygon(surface, p_glow, hot_pts)

        # 2. PREMIUM EXTRACTION EXIT PORTAL (N-1, N-1)
        ex_x = origin_x + exit_pos[1] * cell_size + cell_size / 2.0
        ex_y = origin_y + exit_pos[0] * cell_size + cell_size / 2.0
        portal_radius = cell_size * 0.38
        pulse_scale = 1.0 + 0.08 * math.sin(self.anim_time * 4.0)
        p_r = int(portal_radius * pulse_scale)

        if has_key:
            # Active Quantum Warp Extraction Vortex (Green)
            pygame.draw.circle(surface, (35, 245, 135), (int(ex_x), int(ex_y)), p_r, width=2)
            # Rotating orbital containment nodes
            for i in range(4):
                orb_angle = self.anim_time * 2.5 + i * (math.pi / 2.0)
                orb_x = ex_x + math.cos(orb_angle) * (p_r + 2)
                orb_y = ex_y + math.sin(orb_angle) * (p_r + 2)
                pygame.draw.circle(surface, (180, 255, 220), (int(orb_x), int(orb_y)), max(1, int(cell_size * 0.04)))

            # Inner swirling event horizon
            core_r = max(2, int(portal_radius * 0.58))
            pygame.draw.circle(surface, (20, 180, 95), (int(ex_x), int(ex_y)), core_r)
            pygame.draw.circle(surface, (210, 255, 235), (int(ex_x), int(ex_y)), max(1, int(core_r * 0.4)))
            exit_label = self.font_bold.render("ESCAPE", True, (255, 255, 255))
        else:
            # Standby Locked Security Grid (Amber / Slate)
            pygame.draw.circle(surface, (220, 140, 30), (int(ex_x), int(ex_y)), p_r, width=2)
            core_r = max(2, int(portal_radius * 0.52))
            pygame.draw.circle(surface, (45, 38, 25), (int(ex_x), int(ex_y)), core_r)
            exit_label = self.font_badge.render("SEALED", True, (255, 185, 45))

        surface.blit(exit_label, exit_label.get_rect(center=(int(ex_x), int(ex_y))))

        # 3. PREMIUM GOLDEN CIPHER ARTIFACT (KEY)
        if not has_key:
            kx = origin_x + key_pos[1] * cell_size + cell_size / 2.0
            ky = origin_y + key_pos[0] * cell_size + cell_size / 2.0
            k_pulse = 1.0 + 0.12 * math.sin(self.anim_time * 5.0)
            k_radius = cell_size * 0.28 * k_pulse
            k_bob = math.sin(self.anim_time * 4.0) * (cell_size * 0.05)
            ky += k_bob

            # Rotating holographic orbit ring with spinning cipher particles
            pygame.draw.circle(surface, (255, 205, 35), (int(kx), int(ky)), int(k_radius + 3), width=1)
            for i in range(3):
                p_ang = self.anim_time * 3.0 + i * (math.pi * 2.0 / 3.0)
                px_orb = kx + math.cos(p_ang) * (k_radius + 3)
                py_orb = ky + math.sin(p_ang) * (k_radius + 3)
                pygame.draw.circle(surface, (255, 245, 180), (int(px_orb), int(py_orb)), max(1, int(cell_size * 0.035)))

            # 3D Diamond Cipher Relic
            d_half = k_radius * 0.65
            diamond_pts = [
                (kx, ky - d_half * 1.2),
                (kx + d_half, ky),
                (kx, ky + d_half * 1.2),
                (kx - d_half, ky)
            ]
            pygame.draw.polygon(surface, COLOR_KEY_GOLD, diamond_pts)
            # Inner bright gold facet
            facet_pts = [
                (kx, ky - d_half * 0.6),
                (kx + d_half * 0.5, ky),
                (kx, ky + d_half * 0.6),
                (kx - d_half * 0.5, ky)
            ]
            pygame.draw.polygon(surface, (255, 250, 180), facet_pts)
            k_lbl = self.font_badge.render("RELIC", True, (25, 20, 10))
            surface.blit(k_lbl, k_lbl.get_rect(center=(int(kx), int(ky))))

        # 4. Green Gemini Safe-Route Breadcrumbs (Strictly No A*)
        if recommended_path:
            for idx, pt in enumerate(recommended_path[:3]):
                if len(pt) >= 2:
                    br, bc = pt[0], pt[1]
                    if 0 <= br < grid_size and 0 <= bc < grid_size:
                        bx = origin_x + bc * cell_size + cell_size / 2.0
                        by = origin_y + br * cell_size + cell_size / 2.0
                        b_radius = max(4, int(cell_size * 0.20))
                        # Dual concentric green rings
                        pygame.draw.circle(surface, (40, 240, 120), (int(bx), int(by)), b_radius, width=2)
                        pygame.draw.circle(surface, (20, 90, 48), (int(bx), int(by)), max(2, b_radius - 3))
                        # Step number badge inside breadcrumb
                        num_surf = self.font_bold.render(str(idx + 1), True, (220, 255, 230))
                        surface.blit(num_surf, num_surf.get_rect(center=(int(bx), int(by))))

        # 5. Pulsing Yellow Guide Arrow (pointing to current objective)
        target_pos = exit_pos if has_key else key_pos
        tg_x = origin_x + target_pos[1] * cell_size + cell_size / 2.0
        tg_y = origin_y + target_pos[0] * cell_size + cell_size / 2.0
        dx = tg_x - player_x
        dy = tg_y - player_y
        dist = math.hypot(dx, dy)
        if dist > cell_size * 0.5:
            # Normalize vector
            nx, ny = dx / dist, dy / dist
            arrow_dist = cell_size * 0.42
            ax = player_x + nx * arrow_dist
            ay = player_y + ny * arrow_dist
            arrow_size = max(5, int(cell_size * 0.16))

            # Pulsing alpha / scale
            a_pulse = 1.0 + 0.15 * math.sin(self.anim_time * 6.0)
            perp_x, perp_y = -ny, nx

            p1 = (ax + nx * (arrow_size * a_pulse), ay + ny * (arrow_size * a_pulse))
            p2 = (ax - nx * (arrow_size * a_pulse) + perp_x * (arrow_size * 0.7),
                  ay - ny * (arrow_size * a_pulse) + perp_y * (arrow_size * 0.7))
            p3 = (ax - nx * (arrow_size * a_pulse) - perp_x * (arrow_size * 0.7),
                  ay - ny * (arrow_size * a_pulse) - perp_y * (arrow_size * 0.7))

            pygame.draw.polygon(surface, COLOR_GUIDE_ARROW, [p1, p2, p3])

        # 6. Human Mercenary Hunters (with helmet, NVG goggles, ballistic armor, weapon & searchlight)
        for h in hunters:
            self._draw_human_hunter(surface, h.visual_x, h.visual_y, cell_size, h.facing_dr, h.facing_dc, h.hunter_id)

        # 7. Human Gamer / Player Operative (human head, hair, eyes, tactical vest, boots, gadget & key)
        self._draw_human_player(surface, player_x, player_y, cell_size, player_facing[0], player_facing[1], has_key)

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
        """
        Render the Gamer/Player Operative as an ultra-premium animated humanoid character.
        Features:
        - Sleek cyber-infiltrator exo-suit with dual-tone obsidian/cobalt armor plates.
        - Smart cybernetic retinal visor glowing neon cyan with animated horizontal scanline.
        - Central glowing Aegis Operative Crest on chest.
        - Animated high-mobility combat boots with cyan heel stabilizer LEDs.
        - Multi-stage volumetric tactical flashlight beam.
        - Left wrist holographic PDA/scanner terminal.
        - Golden cipher artifact docked on backpack with orbiting particle beacon when collected.
        """
        scale = max(0.55, cell_size / 64.0)

        # Facing angle (radians)
        if facing_dr == 0 and facing_dc == 0:
            angle = 0.0  # default facing right
        else:
            angle = math.atan2(facing_dr, facing_dc)

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        perp_x = -sin_a
        perp_y = cos_a

        # 1. Multi-Layer Directional Soft Drop Shadow
        shadow_surf = pygame.Surface((int(36 * scale), int(24 * scale)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (5, 8, 14, 130), shadow_surf.get_rect())
        surface.blit(shadow_surf, shadow_surf.get_rect(center=(int(px), int(py + 4.5 * scale))))

        # 2. Tactician Tactical Aura Ring (Cyan pulse)
        pulse = 1.0 + 0.08 * math.sin(self.anim_time * 5.0)
        ring_r = int(cell_size * 0.36 * pulse)
        pygame.draw.circle(surface, (255, 195, 45), (int(px), int(py)), ring_r, width=1)
        # Inner golden aura
        pygame.draw.circle(surface, (180, 130, 25), (int(px), int(py)), max(2, ring_r - 3), width=1)

        # 3. Animated Combat Boots with Cyan Heel Stabilizer LEDs
        walk_stride = math.sin(self.anim_time * 9.0) * (4.2 * scale)
        foot_spread = 5.8 * scale

        # Left Foot
        lfx = px + perp_x * (-foot_spread) + cos_a * walk_stride
        lfy = py + perp_y * (-foot_spread) + sin_a * walk_stride
        pygame.draw.circle(surface, (18, 25, 36), (int(lfx), int(lfy)), max(2, int(3.5 * scale)))
        pygame.draw.circle(surface, (215, 165, 45), (int(lfx - cos_a * (1.2 * scale)), int(lfy - sin_a * (1.2 * scale))), max(1, int(1.8 * scale)))

        # Right Foot
        rfx = px + perp_x * (foot_spread) - cos_a * walk_stride
        rfy = py + perp_y * (foot_spread) - sin_a * walk_stride
        pygame.draw.circle(surface, (18, 25, 36), (int(rfx), int(rfy)), max(2, int(3.5 * scale)))
        pygame.draw.circle(surface, (215, 165, 45), (int(rfx - cos_a * (1.2 * scale)), int(rfy - sin_a * (1.2 * scale))), max(1, int(1.8 * scale)))

        # 4. Human Torso & Tactical Operative Exo-Armor
        sh_w = 8.8 * scale
        hip_w = 5.8 * scale
        chest_len = 5.2 * scale
        hip_back = 5.8 * scale

        p_l_shoulder = (px + perp_x * (-sh_w) + cos_a * chest_len, py + perp_y * (-sh_w) + sin_a * chest_len)
        p_r_shoulder = (px + perp_x * (sh_w) + cos_a * chest_len, py + perp_y * (sh_w) + sin_a * chest_len)
        p_r_hip = (px + perp_x * (hip_w) - cos_a * hip_back, py + perp_y * (hip_w) - sin_a * hip_back)
        p_l_hip = (px + perp_x * (-hip_w) - cos_a * hip_back, py + perp_y * (-hip_w) - sin_a * hip_back)

        # Base obsidian undersuit
        pygame.draw.polygon(surface, (16, 22, 34), [p_l_shoulder, p_r_shoulder, p_r_hip, p_l_hip])

        # Dual-tone cobalt armor breastplate
        p_bp1 = (px + perp_x * (-sh_w * 0.8) + cos_a * (chest_len * 0.85), py + perp_y * (-sh_w * 0.8) + sin_a * (chest_len * 0.85))
        p_bp2 = (px + perp_x * (sh_w * 0.8) + cos_a * (chest_len * 0.85), py + perp_y * (sh_w * 0.8) + sin_a * (chest_len * 0.85))
        p_bp3 = (px + perp_x * (hip_w * 0.75) - cos_a * (hip_back * 0.35), py + perp_y * (hip_w * 0.75) - sin_a * (hip_back * 0.35))
        p_bp4 = (px + perp_x * (-hip_w * 0.75) - cos_a * (hip_back * 0.35), py + perp_y * (-hip_w * 0.75) - sin_a * (hip_back * 0.35))
        pygame.draw.polygon(surface, (145, 85, 42), [p_bp1, p_bp2, p_bp3, p_bp4])
        pygame.draw.polygon(surface, (225, 175, 55), [p_bp1, p_bp2, p_bp3, p_bp4], width=1)

        # Tactical harness straps & ammo webbing
        pygame.draw.line(surface, (25, 40, 60), p_l_shoulder, p_r_hip, max(1, int(1.8 * scale)))
        pygame.draw.line(surface, (25, 40, 60), p_r_shoulder, p_l_hip, max(1, int(1.8 * scale)))

        # Explorer Leather Harness Buckle & Golden Amulet Medallion
        crest_x = px + cos_a * (1.2 * scale)
        crest_y = py + sin_a * (1.2 * scale)
        crest_r = max(2, int(2.4 * scale))
        pygame.draw.circle(surface, (225, 175, 50), (int(crest_x), int(crest_y)), crest_r)
        pygame.draw.circle(surface, (255, 240, 160), (int(crest_x), int(crest_y)), max(1, int(crest_r * 0.5)))

        # Sturdy explorer leather shoulder pauldrons with brass rivets
        pygame.draw.circle(surface, (115, 65, 32), (int(p_l_shoulder[0]), int(p_l_shoulder[1])), max(2, int(3.2 * scale)))
        pygame.draw.circle(surface, (225, 175, 50), (int(p_l_shoulder[0]), int(p_l_shoulder[1])), max(1, int(1.8 * scale)))
        pygame.draw.circle(surface, (115, 65, 32), (int(p_r_shoulder[0]), int(p_r_shoulder[1])), max(2, int(3.2 * scale)))
        pygame.draw.circle(surface, (225, 175, 50), (int(p_r_shoulder[0]), int(p_r_shoulder[1])), max(1, int(1.8 * scale)))

        # 5. Articulated Arms, Left Wrist Compass & Right Hand Explorer Lantern/Torch
        arm_reach = 9.5 * scale
        hand_r_x = px + perp_x * (sh_w * 0.8) + cos_a * arm_reach
        hand_r_y = py + perp_y * (sh_w * 0.8) + sin_a * arm_reach
        hand_l_x = px + perp_x * (-sh_w * 0.8) + cos_a * (arm_reach * 0.65)
        hand_l_y = py + perp_y * (-sh_w * 0.8) + sin_a * (arm_reach * 0.65)

        # Explorer canvas sleeves
        pygame.draw.line(surface, (130, 75, 36), p_r_shoulder, (hand_r_x, hand_r_y), max(2, int(3.6 * scale)))
        pygame.draw.line(surface, (130, 75, 36), p_l_shoulder, (hand_l_x, hand_l_y), max(2, int(3.6 * scale)))

        # Left Wrist Golden Expedition Compass
        pda_x = (p_l_shoulder[0] + hand_l_x) * 0.5
        pda_y = (p_l_shoulder[1] + hand_l_y) * 0.5
        pygame.draw.circle(surface, (225, 175, 50), (int(pda_x), int(pda_y)), max(1, int(2.2 * scale)))
        pygame.draw.circle(surface, (255, 245, 180), (int(pda_x), int(pda_y)), max(1, int(1.0 * scale)))

        # Human Skin Hands with tactical fingerless gloves
        pygame.draw.circle(surface, (245, 195, 158), (int(hand_r_x), int(hand_r_y)), max(1, int(2.5 * scale)))
        pygame.draw.circle(surface, (245, 195, 158), (int(hand_l_x), int(hand_l_y)), max(1, int(2.5 * scale)))

        # Handheld Tactical Scanner / Flashlight Device
        scanner_tip_x = hand_r_x + cos_a * (5.0 * scale)
        scanner_tip_y = hand_r_y + sin_a * (5.0 * scale)
        pygame.draw.line(surface, (45, 58, 78), (hand_r_x, hand_r_y), (scanner_tip_x, scanner_tip_y), max(2, int(3.0 * scale)))
        pygame.draw.circle(surface, (255, 210, 50), (int(scanner_tip_x), int(scanner_tip_y)), max(1, int(2.2 * scale)))

        # Multi-Stage Volumetric Flashlight Beam
        light_len = cell_size * 0.85
        light_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        p_apex = (scanner_tip_x, scanner_tip_y)

        # Broad ambient beam
        half_fov = math.radians(24)
        p_l = (scanner_tip_x + math.cos(angle - half_fov) * light_len, scanner_tip_y + math.sin(angle - half_fov) * light_len)
        p_r = (scanner_tip_x + math.cos(angle + half_fov) * light_len, scanner_tip_y + math.sin(angle + half_fov) * light_len)
        pygame.draw.polygon(light_surf, (255, 205, 60, 26), [p_apex, p_l, p_r])

        # Focused core penetrating beam
        narrow_fov = math.radians(11)
        p_nl = (scanner_tip_x + math.cos(angle - narrow_fov) * (light_len * 1.05), scanner_tip_y + math.sin(angle - narrow_fov) * (light_len * 1.05))
        p_nr = (scanner_tip_x + math.cos(angle + narrow_fov) * (light_len * 1.05), scanner_tip_y + math.sin(angle + narrow_fov) * (light_len * 1.05))
        pygame.draw.polygon(light_surf, (255, 235, 130, 48), [p_apex, p_nl, p_nr])
        surface.blit(light_surf, (0, 0))

        # 6. Human Head, Modern Hairstyle & Smart Cybernetic Retinal Visor
        head_cx = px + cos_a * (1.8 * scale)
        head_cy = py + sin_a * (1.8 * scale)
        head_r = 7.2 * scale

        # Human Skin Face & Jawline
        pygame.draw.circle(surface, (245, 198, 162), (int(head_cx), int(head_cy)), int(head_r))

        # Stylish Modern Cropped Stealth Haircut (Obsidian Brown)
        hair_surf = pygame.Surface((int(head_r * 2 + 6), int(head_r * 2 + 6)), pygame.SRCALPHA)
        pygame.draw.circle(hair_surf, (36, 26, 20), (int(head_r + 3), int(head_r + 3)), int(head_r + 0.5))
        # Mask face area for haircut
        face_cut_x = int(head_r + 3 + cos_a * (head_r * 0.45))
        face_cut_y = int(head_r + 3 + sin_a * (head_r * 0.45))
        pygame.draw.circle(hair_surf, (0, 0, 0, 0), (face_cut_x, face_cut_y), int(head_r * 0.78))
        surface.blit(hair_surf, (int(head_cx - head_r - 3), int(head_cy - head_r - 3)))

        # CLASSIC EXPLORER FEDORA HAT & HEADGEAR
        # Hat brim (wide leather brim)
        brim_cx = head_cx + cos_a * (0.8 * scale)
        brim_cy = head_cy + sin_a * (0.8 * scale)
        brim_r = head_r * 1.15
        pygame.draw.circle(surface, (105, 60, 28), (int(brim_cx), int(brim_cy)), int(brim_r))

        # Hat crown (tan felt)
        crown_cx = head_cx - cos_a * (0.8 * scale)
        crown_cy = head_cy - sin_a * (0.8 * scale)
        pygame.draw.circle(surface, (145, 90, 45), (int(crown_cx), int(crown_cy)), int(head_r * 0.85))

        # Golden hat ribbon band
        pygame.draw.circle(surface, (225, 175, 50), (int(crown_cx), int(crown_cy)), int(head_r * 0.85), width=1)

        # 7. Secured Golden Cipher Artifact on Backpack (if collected)
        if has_key:
            pack_x = px - cos_a * (8.0 * scale)
            pack_y = py - sin_a * (8.0 * scale)
            k_pulse = 1.0 + 0.15 * math.sin(self.anim_time * 6.0)
            # Golden aura & orbiting energy bits
            pygame.draw.circle(surface, (255, 205, 30), (int(pack_x), int(pack_y)), int(5.0 * scale * k_pulse))
            pygame.draw.circle(surface, (255, 255, 220), (int(pack_x), int(pack_y)), max(1, int(2.5 * scale)))
            # Orbiting micro-sparks
            for i in range(2):
                sp_ang = self.anim_time * 4.0 + i * math.pi
                sp_x = pack_x + math.cos(sp_ang) * (7.0 * scale)
                sp_y = pack_y + math.sin(sp_ang) * (7.0 * scale)
                pygame.draw.circle(surface, (255, 240, 160), (int(sp_x), int(sp_y)), max(1, int(1.4 * scale)))

        # 8. Floating Tactical Operative Callsign Pill
        lbl = self.font_small.render("HUNTER", True, COLOR_KEY_GOLD)
        pill_rect = lbl.get_rect(center=(int(px), int(py - cell_size * 0.44)))
        pill_bg = pill_rect.inflate(8, 2)
        pygame.draw.rect(surface, (10, 16, 26), pill_bg, border_radius=3)
        pygame.draw.rect(surface, (0, 180, 230), pill_bg, width=1, border_radius=3)
        surface.blit(lbl, pill_rect)

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
        """
        Render the Hunter as an ultra-premium animated Tactical Mercenary Juggernaut.
        Features:
        - Heavy ceramic ballistic armor with crimson plates and hazard warning stripes.
        - Advanced Multi-Optic Predator NVG (Night-Vision Goggles) with laser core glow.
        - Razor-sharp tactical red laser sight projecting forward from assault carbine.
        - Volumetric infrared sweeping searchlight cone with dual atmospheric layers.
        - High-traction heavy combat boots with cadence stride.
        - Floating high-tech designation tag [ HUNTER #{hunter_id} (GEMINI AI) ].
        """
        scale = max(0.55, cell_size / 64.0)

        # Facing angle
        if facing_dr == 0 and facing_dc == 0:
            angle = math.pi / 2  # default facing down
        else:
            angle = math.atan2(facing_dr, facing_dc)

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        perp_x = -sin_a
        perp_y = cos_a

        # 1. Volumetric Infrared Sweeping Cone (Atmospheric Wash + Core)
        cone_len = cell_size * 0.98
        cone_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        p_apex = (hx, hy)

        # Outer wide atmospheric infrared beam
        half_fov = math.radians(28)
        p_left = (hx + math.cos(angle - half_fov) * cone_len, hy + math.sin(angle - half_fov) * cone_len)
        p_right = (hx + math.cos(angle + half_fov) * cone_len, hy + math.sin(angle + half_fov) * cone_len)
        pygame.draw.polygon(cone_surf, (255, 35, 55, 35), [p_apex, p_left, p_right])

        # Inner focused high-intensity infrared searchlight
        core_fov = math.radians(14)
        p_cleft = (hx + math.cos(angle - core_fov) * (cone_len * 1.08), hy + math.sin(angle - core_fov) * (cone_len * 1.08))
        p_cright = (hx + math.cos(angle + core_fov) * (cone_len * 1.08), hy + math.sin(angle + core_fov) * (cone_len * 1.08))
        pygame.draw.polygon(cone_surf, (255, 75, 95, 55), [p_apex, p_cleft, p_cright])
        surface.blit(cone_surf, (0, 0))

        # 2. Heavy Drop Shadow
        shadow_surf = pygame.Surface((int(38 * scale), int(26 * scale)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (8, 4, 8, 140), shadow_surf.get_rect())
        surface.blit(shadow_surf, shadow_surf.get_rect(center=(int(hx), int(hy + 4.5 * scale))))

        # 3. Heavy Mercenary Armored Boots (Cadence Stride)
        walk_stride = math.sin(self.anim_time * 8.0 + hunter_id * 1.5) * (4.0 * scale)
        foot_spread = 6.5 * scale

        # Left Foot
        lfx = hx + perp_x * (-foot_spread) + cos_a * walk_stride
        lfy = hy + perp_y * (-foot_spread) + sin_a * walk_stride
        pygame.draw.circle(surface, (20, 16, 20), (int(lfx), int(lfy)), max(2, int(3.8 * scale)))
        pygame.draw.circle(surface, (185, 25, 45), (int(lfx - cos_a * (1.2 * scale)), int(lfy - sin_a * (1.2 * scale))), max(1, int(2.0 * scale)))

        # Right Foot
        rfx = hx + perp_x * (foot_spread) - cos_a * walk_stride
        rfy = hy + perp_y * (foot_spread) - sin_a * walk_stride
        pygame.draw.circle(surface, (20, 16, 20), (int(rfx), int(rfy)), max(2, int(3.8 * scale)))
        pygame.draw.circle(surface, (185, 25, 45), (int(rfx - cos_a * (1.2 * scale)), int(rfy - sin_a * (1.2 * scale))), max(1, int(2.0 * scale)))

        # 4. Human Mercenary Torso & Heavy Ballistic Juggernaut Vest
        sh_w = 9.8 * scale
        hip_w = 6.8 * scale
        chest_len = 5.8 * scale
        hip_back = 6.2 * scale

        p_l_shoulder = (hx + perp_x * (-sh_w) + cos_a * chest_len, hy + perp_y * (-sh_w) + sin_a * chest_len)
        p_r_shoulder = (hx + perp_x * (sh_w) + cos_a * chest_len, hy + perp_y * (sh_w) + sin_a * chest_len)
        p_r_hip = (hx + perp_x * (hip_w) - cos_a * hip_back, hy + perp_y * (hip_w) - sin_a * hip_back)
        p_l_hip = (hx + perp_x * (-hip_w) - cos_a * hip_back, hy + perp_y * (-hip_w) - sin_a * hip_back)

        # Vest base (matte obsidian)
        pygame.draw.polygon(surface, (26, 20, 26), [p_l_shoulder, p_r_shoulder, p_r_hip, p_l_hip])

        # Crimson heavy breastplate
        plate_w = 7.0 * scale
        p_pl1 = (hx + perp_x * (-plate_w) + cos_a * (chest_len * 0.9), hy + perp_y * (-plate_w) + sin_a * (chest_len * 0.9))
        p_pl2 = (hx + perp_x * (plate_w) + cos_a * (chest_len * 0.9), hy + perp_y * (plate_w) + sin_a * (chest_len * 0.9))
        p_pl3 = (hx + perp_x * (plate_w * 0.8) - cos_a * (hip_back * 0.4), hy + perp_y * (plate_w * 0.8) - sin_a * (hip_back * 0.4))
        p_pl4 = (hx + perp_x * (-plate_w * 0.8) - cos_a * (hip_back * 0.4), hy + perp_y * (-plate_w * 0.8) - sin_a * (hip_back * 0.4))
        pygame.draw.polygon(surface, (205, 30, 52), [p_pl1, p_pl2, p_pl3, p_pl4])
        pygame.draw.polygon(surface, (140, 18, 35), [p_pl1, p_pl2, p_pl3, p_pl4], width=1)

        # Reinforced shoulder pauldrons with hazard warning stripes
        for sh_pt in (p_l_shoulder, p_r_shoulder):
            pygame.draw.circle(surface, (180, 26, 45), (int(sh_pt[0]), int(sh_pt[1])), max(2, int(3.8 * scale)))
            pygame.draw.circle(surface, (255, 185, 30), (int(sh_pt[0]), int(sh_pt[1])), max(1, int(1.8 * scale)))

        # 5. Armored Arms & Hunter Weapon with Tactical Red Laser Sight
        arm_reach = 11.0 * scale
        hand_r_x = hx + perp_x * (sh_w * 0.78) + cos_a * arm_reach
        hand_r_y = hy + perp_y * (sh_w * 0.78) + sin_a * arm_reach
        hand_l_x = hx + perp_x * (-sh_w * 0.62) + cos_a * (arm_reach * 0.72)
        hand_l_y = hy + perp_y * (-sh_w * 0.62) + sin_a * (arm_reach * 0.72)

        # Arm sleeves & combat gloves
        pygame.draw.line(surface, (32, 24, 32), p_r_shoulder, (hand_r_x, hand_r_y), max(2, int(4.0 * scale)))
        pygame.draw.line(surface, (32, 24, 32), p_l_shoulder, (hand_l_x, hand_l_y), max(2, int(4.0 * scale)))
        pygame.draw.circle(surface, (18, 14, 18), (int(hand_r_x), int(hand_r_y)), max(1, int(2.6 * scale)))
        pygame.draw.circle(surface, (18, 14, 18), (int(hand_l_x), int(hand_l_y)), max(1, int(2.6 * scale)))

        # Hunter Tactical Assault Carbine Silhouette
        barrel_x = hand_r_x + cos_a * (7.0 * scale)
        barrel_y = hand_r_y + sin_a * (7.0 * scale)
        pygame.draw.line(surface, (45, 45, 55), (hand_r_x, hand_r_y), (barrel_x, barrel_y), max(2, int(3.2 * scale)))
        # Red Targeting Diode on weapon muzzle
        pygame.draw.circle(surface, (255, 30, 50), (int(barrel_x), int(barrel_y)), max(1, int(2.2 * scale)))

        # TACTICAL RED LASER TARGETING SIGHT (High-Intensity Line + Target Dot)
        laser_len = cell_size * 1.4
        laser_end_x = barrel_x + cos_a * laser_len
        laser_end_y = barrel_y + sin_a * laser_len
        pygame.draw.line(surface, (255, 30, 50), (barrel_x, barrel_y), (laser_end_x, laser_end_y), 1)
        # Pulsing Laser Target Dot at termination
        dot_pulse = 1.0 + 0.25 * math.sin(self.anim_time * 12.0)
        pygame.draw.circle(surface, (255, 30, 50), (int(laser_end_x), int(laser_end_y)), int(2.5 * dot_pulse))
        pygame.draw.circle(surface, (255, 235, 240), (int(laser_end_x), int(laser_end_y)), 1)

        # 6. Combat Helmet & Glowing Red Multi-Optic NVG Lenses
        head_cx = hx + cos_a * (1.8 * scale)
        head_cy = hy + sin_a * (1.8 * scale)
        head_r = 7.8 * scale

        # Balaclava / Neck guard
        pygame.draw.circle(surface, (24, 18, 24), (int(head_cx), int(head_cy)), int(head_r + 0.5))
        # Heavy Ballistic Combat Helmet
        pygame.draw.circle(surface, (42, 34, 44), (int(head_cx - cos_a * (1.5 * scale)), int(head_cy - sin_a * (1.5 * scale))), int(head_r * 0.95))
        pygame.draw.circle(surface, (22, 16, 24), (int(head_cx - cos_a * (1.5 * scale)), int(head_cy - sin_a * (1.5 * scale))), int(head_r * 0.95), width=1)

        # ADVANCED MULTI-OPTIC PREDATOR NVG ARRAY (Vivid Crimson Lenses with Hot Laser Core)
        nvg_dist = 3.0 * scale
        nvg_fwd = 3.8 * scale
        l_nvg_x = head_cx + perp_x * (-nvg_dist) + cos_a * nvg_fwd
        l_nvg_y = head_cy + perp_y * (-nvg_dist) + sin_a * nvg_fwd
        r_nvg_x = head_cx + perp_x * (nvg_dist) + cos_a * nvg_fwd
        r_nvg_y = head_cy + perp_y * (nvg_dist) + sin_a * nvg_fwd

        # Central mini optic lens (Triple-optic predator configuration)
        c_nvg_x = head_cx + cos_a * (nvg_fwd + 1.2 * scale)
        c_nvg_y = head_cy + sin_a * (nvg_fwd + 1.2 * scale)

        # Outer glowing ruby lenses
        nvg_r = max(2, int(2.6 * scale))
        pygame.draw.circle(surface, (255, 25, 48), (int(l_nvg_x), int(l_nvg_y)), nvg_r)
        pygame.draw.circle(surface, (255, 25, 48), (int(r_nvg_x), int(r_nvg_y)), nvg_r)
        pygame.draw.circle(surface, (255, 25, 48), (int(c_nvg_x), int(c_nvg_y)), max(1, int(1.8 * scale)))

        # Hot-white laser diode cores in lenses
        pygame.draw.circle(surface, (255, 235, 240), (int(l_nvg_x), int(l_nvg_y)), max(1, int(1.2 * scale)))
        pygame.draw.circle(surface, (255, 235, 240), (int(r_nvg_x), int(r_nvg_y)), max(1, int(1.2 * scale)))
        pygame.draw.circle(surface, (255, 235, 240), (int(c_nvg_x), int(c_nvg_y)), 1)

        # 7. Floating Tactical Hunter Callsign Pill
        h_tag = self.font_small.render(f"SENTINEL-0{hunter_id}", True, (255, 85, 95))
        h_rect = h_tag.get_rect(center=(int(hx), int(hy - cell_size * 0.44)))
        h_pill = h_rect.inflate(8, 2)
        pygame.draw.rect(surface, (24, 12, 16), h_pill, border_radius=3)
        pygame.draw.rect(surface, (200, 35, 55), h_pill, width=1, border_radius=3)
        surface.blit(h_tag, h_rect)

    # =========================================================================
    # BOTTOM HUD CONSOLE RENDERING
    # =========================================================================
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
        """
        Render the dedicated bottom HUD console with metrics, telemetry, and transmissions.
        """
        # Background Glassmorphism Panel
        pygame.draw.rect(surface, COLOR_HUD_BG, self.hud_rect)
        pygame.draw.line(surface, COLOR_WALL_BORDER, (0, self.hud_rect.y), (self.screen_width, self.hud_rect.y), 2)

        # Three Column Partitions
        col1_w = 260
        col2_w = 260
        col3_w = self.screen_width - col1_w - col2_w

        c1_rect = pygame.Rect(10, self.hud_rect.y + 10, col1_w - 20, self.hud_height - 20)
        c2_rect = pygame.Rect(col1_w, self.hud_rect.y + 10, col2_w - 20, self.hud_height - 20)
        c3_rect = pygame.Rect(col1_w + col2_w, self.hud_rect.y + 10, col3_w - 20, self.hud_height - 20)

        # Partition Divider Lines
        pygame.draw.line(surface, COLOR_HUD_BORDER, (col1_w - 5, self.hud_rect.y + 10), (col1_w - 5, self.screen_height - 10), 1)
        pygame.draw.line(surface, COLOR_HUD_BORDER, (col1_w + col2_w - 5, self.hud_rect.y + 10), (col1_w + col2_w - 5, self.screen_height - 10), 1)

        # ---------------------------------------------------------------------
        # COLUMN 1: MISSION METRICS
        # ---------------------------------------------------------------------
        h1 = self.font_badge.render("// MISSION METRICS", True, COLOR_TEXT_ACCENT_CYAN)
        surface.blit(h1, (c1_rect.x, c1_rect.y))

        y = c1_rect.y + 22
        # Level
        lvl_str = f"LEVEL: {level_name.upper()}"
        surface.blit(self.font_small.render(lvl_str, True, COLOR_TEXT_SECONDARY), (c1_rect.x, y))
        y += 18
        # Step Count
        step_str = f"STEPS EXECUTED: {steps:03d}"
        surface.blit(self.font_body.render(step_str, True, COLOR_TEXT_PRIMARY), (c1_rect.x, y))
        y += 20
        # Best Record
        best_str = f"BEST RECORD: {best_steps} STEPS" if best_steps is not None else "★ BEST RECORD: UNCLAIMED"
        surface.blit(self.font_small.render(best_str, True, COLOR_KEY_GOLD), (c1_rect.x, y))
        y += 22
        # Key Status Badge
        key_label = "RELIC: SECURED [GATEWAY OPEN]" if has_key else "RELIC: REQUIRED [EXPLORING]"
        key_color = COLOR_TEXT_ACCENT_GREEN if has_key else COLOR_TEXT_ACCENT_RED
        k_bg_fill = (16, 42, 28) if has_key else (38, 16, 24)
        k_surf = self.font_bold.render(key_label, True, key_color)
        k_bg = pygame.Rect(c1_rect.x, y, k_surf.get_width() + 10, 22)
        pygame.draw.rect(surface, k_bg_fill, k_bg, border_radius=3)
        pygame.draw.rect(surface, key_color, k_bg, width=1, border_radius=3)
        surface.blit(k_surf, (c1_rect.x + 5, y + 2))

        # ---------------------------------------------------------------------
        # COLUMN 2: TACTICAL SENSOR TELEMETRY
        # ---------------------------------------------------------------------
        h2 = self.font_badge.render("// SENSOR TELEMETRY", True, COLOR_TEXT_ACCENT_MAGENTA)
        surface.blit(h2, (c2_rect.x, c2_rect.y))

        y2 = c2_rect.y + 22
        surface.blit(self.font_small.render("SANCTUARY RADAR: MULTI-CHAMBER ACTIVE", True, COLOR_TEXT_ACCENT_CYAN), (c2_rect.x, y2))
        y2 += 18

        surface.blit(self.font_body.render("ESCAPE ROUTE: COMPUTED", True, COLOR_TEXT_ACCENT_GREEN), (c2_rect.x, y2))
        y2 += 22

        # Status indicator with LED pip
        led_color = COLOR_TEXT_ACCENT_GREEN
        led_pulse = 1.0 + 0.25 * math.sin(self.anim_time * 8.0)
        pygame.draw.circle(surface, led_color, (c2_rect.x + 8, y2 + 8), int(5 * led_pulse))

        surface.blit(self.font_bold.render("SENTINEL TRACKING: ACTIVE (60 FPS)", True, led_color), (c2_rect.x + 22, y2))
        y2 += 22

        surface.blit(self.font_small.render("GUARDIAN EVASION: ENGAGED", True, COLOR_TEXT_MUTED), (c2_rect.x, y2))

        # ---------------------------------------------------------------------
        # COLUMN 3: LIVE TACTICAL COMMANDER TRANSMISSION
        # ---------------------------------------------------------------------
        h3 = self.font_badge.render("// EXPEDITION COMMAND DISPATCH", True, COLOR_TEXT_ACCENT_AMBER)
        surface.blit(h3, (c3_rect.x, c3_rect.y))

        # Transmission Terminal Box
        box_rect = pygame.Rect(c3_rect.x, c3_rect.y + 20, c3_rect.width, self.hud_height - 50)
        pygame.draw.rect(surface, (18, 24, 36), box_rect, border_radius=4)
        pygame.draw.rect(surface, (45, 68, 105), box_rect, width=1, border_radius=4)

        # Terminal Comms Header
        radio_icon = self.font_small.render("[DISPATCH ACTIVE]", True, COLOR_TEXT_ACCENT_GREEN)
        surface.blit(radio_icon, (box_rect.x + 8, box_rect.y + 6))

        # Order Content (Tense transmission under 12 words)
        clean_order = commander_order.strip() if commander_order else "Observing sanctuary chamber telemetry..."
        order_surf = self.font_header.render(f'"{clean_order}"', True, COLOR_TEXT_PRIMARY)
        surface.blit(order_surf, (box_rect.x + 8, box_rect.y + 28))

        # Subtext / Instruction hint
        hint_surf = self.font_small.render("[WASD: Move | P/ESC: Pause | H: Summon Sentinel | B: Shift Walls]", True, COLOR_TEXT_MUTED)
        surface.blit(hint_surf, (box_rect.x + 8, box_rect.y + 62))

    # =========================================================================
    # GAME OVER OVERLAYS (VICTORY & DEFEAT)
    # =========================================================================
    def draw_game_over_overlay(
        self,
        surface: pygame.Surface,
        is_victory: bool,
        steps: int,
        is_new_best: bool,
        current_level: int
    ) -> None:
        """
        Render the victory or defeat modal overlay on top of the game screen.
        """
        # Dim background
        dim_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_surf.fill((8, 12, 18, 190))
        surface.blit(dim_surf, (0, 0))

        cx = self.screen_width // 2
        cy = self.screen_height // 2

        modal_rect = pygame.Rect(cx - 240, cy - 180, 480, 360)
        pygame.draw.rect(surface, COLOR_HUD_BG, modal_rect, border_radius=8)

        accent_color = COLOR_TEXT_ACCENT_GREEN if is_victory else COLOR_TEXT_ACCENT_RED
        pygame.draw.rect(surface, accent_color, modal_rect, width=2, border_radius=8)

        if is_victory:
            title_text = "EXPEDITION ACCOMPLISHED"
            sub_text = f"Treasure Hunter successfully extracted in {steps} steps!"
            title_color = COLOR_TEXT_ACCENT_GREEN
        else:
            title_text = "SANCTUARY CASUALTY"
            sub_text = f"Explorer intercepted by Temple Sentinel after {steps} steps."
            title_color = COLOR_TEXT_ACCENT_RED

        t_surf = self.font_title.render(title_text, True, title_color)
        surface.blit(t_surf, t_surf.get_rect(center=(cx, cy - 120)))

        s_surf = self.font_body.render(sub_text, True, COLOR_TEXT_PRIMARY)
        surface.blit(s_surf, s_surf.get_rect(center=(cx, cy - 80)))

        if is_victory and is_new_best:
            rec_surf = self.font_header.render("NEW BEST EXPEDITION RECORD!", True, COLOR_TEXT_ACCENT_AMBER)
            surface.blit(rec_surf, rec_surf.get_rect(center=(cx, cy - 45)))
        elif is_victory:
            adv_txt = "Next difficulty available for selection." if current_level < 3 else "Maximum difficulty conquered!"
            adv_surf = self.font_small.render(adv_txt, True, COLOR_TEXT_SECONDARY)
            surface.blit(adv_surf, adv_surf.get_rect(center=(cx, cy - 45)))
        else:
            tip_surf = self.font_small.render("Tip: Follow Gemini green breadcrumbs to exploit hunter blind spots.", True, COLOR_TEXT_SECONDARY)
            surface.blit(tip_surf, tip_surf.get_rect(center=(cx, cy - 45)))

        # Draw Action Buttons
        if is_victory:
            if current_level < 3:
                self.btn_next_level.draw(surface)
            self.btn_victory_replay.draw(surface)
            self.btn_victory_menu.draw(surface)
        else:
            self.btn_retry_level.draw(surface)
            self.btn_defeat_menu.draw(surface)

    # =========================================================================
    # TACTICAL PAUSE & SIR DEMONSTRATION / WALKTHROUGH OVERLAYS
    # =========================================================================
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
        level_name: str = "Tactical"
    ) -> None:
        """
        Render a clean, professional, authentic in-game pause dock.
        Leaves the entire center grid 100% visible and bright with minimal dimming
        so the player can inspect all entities and clearly explain the game to Sir.
        """
        # 1. Subtle atmospheric tint (leaves the maze, player, hunters, and walls 100% clear and bright)
        dim_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_surf.fill((4, 8, 16, 25))
        surface.blit(dim_surf, (0, 0))

        # 2. Sleek Tactical Top Status Banner (Centered at top margin, leaves entire grid clear)
        top_w = 400
        top_h = 32
        top_x = self.screen_width // 2 - top_w // 2
        top_y = 12
        top_rect = pygame.Rect(top_x, top_y, top_w, top_h)

        top_glass = pygame.Surface((top_w, top_h), pygame.SRCALPHA)
        top_glass.fill((10, 16, 28, 220))
        surface.blit(top_glass, top_rect.topleft)
        pygame.draw.rect(surface, (0, 180, 230), top_rect, width=1, border_radius=4)

        banner_title = self.font_bold.render("PAUSED // TEMPLE EXPEDITION INSPECTION MODE", True, COLOR_KEY_GOLD)
        surface.blit(banner_title, banner_title.get_rect(center=(self.screen_width // 2, top_y + 16)))

        # 3. Right-Margin Control Dock (x=778 to 952 - leaves 100% of the game arena open)
        dock_x = 778
        dock_y = 48
        dock_w = 174
        dock_h = 256
        dock_rect = pygame.Rect(dock_x, dock_y, dock_w, dock_h)

        # Drop shadow & translucent glass fill
        pygame.draw.rect(surface, (5, 8, 14), dock_rect.move(0, 3), border_radius=6)
        dock_glass = pygame.Surface((dock_w, dock_h), pygame.SRCALPHA)
        dock_glass.fill((12, 18, 30, 235))
        surface.blit(dock_glass, dock_rect.topleft)
        pygame.draw.rect(surface, (36, 60, 95), dock_rect, width=1, border_radius=6)
        pygame.draw.rect(surface, (0, 180, 230), dock_rect.inflate(-4, -4), width=1, border_radius=4)

        # Header Title in dock
        dock_title = self.font_badge.render("// EXPEDITION PAUSED", True, COLOR_KEY_GOLD)
        surface.blit(dock_title, (dock_x + 12, dock_y + 10))
        pygame.draw.line(surface, (28, 48, 75), (dock_x + 10, dock_y + 26), (dock_x + dock_w - 10, dock_y + 26), 1)

        # Action Buttons (Cleanly docked inside right margin)
        self.btn_pause_resume.draw(surface)
        self.btn_pause_restart.draw(surface)
        self.btn_pause_help.draw(surface)
        self.btn_pause_menu.draw(surface)

        # Bottom info in dock
        info_y = dock_y + 188
        pygame.draw.line(surface, (28, 48, 75), (dock_x + 10, info_y), (dock_x + dock_w - 10, info_y), 1)
        info_y += 6
        sec_surf = self.font_small.render(f"LEVEL: {level_name.upper()}", True, COLOR_TEXT_SECONDARY)
        surface.blit(sec_surf, (dock_x + 12, info_y))
        info_y += 16
        k_txt = "RELIC: SECURED" if has_key else "RELIC: REQUIRED"
        k_col = COLOR_TEXT_ACCENT_GREEN if has_key else COLOR_KEY_GOLD
        key_info = self.font_badge.render(k_txt, True, k_col)
        surface.blit(key_info, (dock_x + 12, info_y))
        info_y += 18
        hint_surf = self.font_small.render("[P / SPACE to Resume]", True, COLOR_TEXT_MUTED)
        surface.blit(hint_surf, (dock_x + 12, info_y))
    def draw_standby_banner(self, surface: pygame.Surface, seconds_remaining: float) -> None:
        """
        Render a prominent tactical reconnaissance banner on mission start.
        Prevents the simulation from starting abruptly without player preparation.
        """
        count = max(1, int(math.ceil(seconds_remaining)))
        pulse = 1.0 + 0.08 * math.sin(self.anim_time * 8.0)

        bw = 560
        bh = 76
        bx = (self.screen_width - bw) // 2
        by = 85

        b_rect = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(surface, (14, 20, 32), b_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_TEXT_ACCENT_CYAN, b_rect, width=2, border_radius=6)

        # Tactical corner brackets
        t_len = 8
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (bx, by), (bx + t_len, by), 2)
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (bx, by), (bx, by + t_len), 2)
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (bx + bw - 1, by + bh - 1), (bx + bw - 1 - t_len, by + bh - 1), 2)
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (bx + bw - 1, by + bh - 1), (bx + bw - 1, by + bh - 1 - t_len), 2)

        # Title & Countdown
        title_str = f"TACTICAL STANDBY // DEPLOYING IN: {count}s"
        t_surf = self.font_header.render(title_str, True, COLOR_TEXT_ACCENT_AMBER)
        surface.blit(t_surf, t_surf.get_rect(center=(self.screen_width // 2, by + 24)))

        sub_str = "Hunters stationary. Press [WASD / Arrows] or [SPACE] to engage now!"
        s_surf = self.font_bold.render(sub_str, True, COLOR_TEXT_ACCENT_GREEN)
        surface.blit(s_surf, s_surf.get_rect(center=(self.screen_width // 2, by + 52)))
