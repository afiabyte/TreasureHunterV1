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


# Color Palette (High-Tech Tactical Cyberpunk)
COLOR_BG = (11, 15, 23)
COLOR_GRID_BG = (16, 22, 34)
COLOR_GRID_LINE = (28, 38, 56)
COLOR_WALL = (32, 45, 68)
COLOR_WALL_BORDER = (55, 140, 220)
COLOR_WALL_ACCENT = (70, 180, 255)

COLOR_PLAYER_CORE = (255, 255, 255)
COLOR_PLAYER_GLOW = (0, 225, 255)
COLOR_PLAYER_SHIELD = (0, 150, 200, 100)

COLOR_HUNTER_CORE = (255, 230, 230)
COLOR_HUNTER_BODY = (255, 45, 85)
COLOR_HUNTER_CONE = (255, 50, 50, 45)
COLOR_HUNTER_GLOW = (200, 20, 60)

COLOR_KEY_CORE = (255, 255, 200)
COLOR_KEY_GOLD = (255, 195, 25)
COLOR_KEY_GLOW = (255, 220, 50, 80)

COLOR_EXIT_CORE = (200, 255, 230)
COLOR_EXIT_PORTAL = (35, 230, 125)
COLOR_EXIT_GLOW = (20, 180, 90, 80)

COLOR_BREADCRUMB_RING = (40, 240, 120)
COLOR_BREADCRUMB_FILL = (20, 100, 50, 120)
COLOR_GUIDE_ARROW = (255, 220, 40)

COLOR_HUD_BG = (14, 18, 28)
COLOR_HUD_BORDER = (35, 50, 75)
COLOR_TEXT_PRIMARY = (235, 240, 250)
COLOR_TEXT_SECONDARY = (130, 145, 175)
COLOR_TEXT_MUTED = (85, 100, 125)
COLOR_TEXT_ACCENT_CYAN = (0, 220, 255)
COLOR_TEXT_ACCENT_GREEN = (40, 240, 120)
COLOR_TEXT_ACCENT_AMBER = (255, 185, 30)
COLOR_TEXT_ACCENT_RED = (255, 60, 90)

COLOR_BTN_NORMAL = (22, 30, 48)
COLOR_BTN_HOVER = (32, 45, 72)
COLOR_BTN_ACTIVE = (0, 120, 180)
COLOR_BTN_BORDER = (45, 65, 100)
COLOR_BTN_BORDER_HOVER = (0, 200, 255)


class UIButton:
    """Interactive tactical UI button with hover animations and click detection."""

    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font,
                 accent_color: Tuple[int, int, int] = COLOR_TEXT_ACCENT_CYAN,
                 tag: str = "") -> None:
        self.rect = rect
        self.text = text
        self.font = font
        self.accent_color = accent_color
        self.tag = tag
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
        """Render button with tactical borders, drop shadow, and state highlights."""
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
                 placeholder: str = "OPERATIVE-01") -> None:
        self.rect = rect
        self.font = font
        self.text = "OPERATIVE-01"
        self.placeholder = placeholder
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
        """Draw text input field with tactical borders, drop shadow, and prompt."""
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
        self.font_badge = pygame.font.SysFont("consolas,couriernew,monospace", 12, bold=True)

        # Pulse animation counter for glow and arrows
        self.anim_time = 0.0

        # HUD console dimensions
        self.hud_height = 155
        self.hud_rect = pygame.Rect(0, self.screen_height - self.hud_height, self.screen_width, self.hud_height)

        # Home Screen widgets
        self.input_player_name = TextInputBox(pygame.Rect(380, 200, 260, 36), self.font_body)
        self._init_home_buttons()
        self._init_overlay_buttons()

    def _init_home_buttons(self) -> None:
        """Initialize interactive buttons for the Home Screen."""
        # Grid Size selector buttons (5x5, 7x7 default, 9x9, 11x11)
        self.grid_buttons: List[UIButton] = []
        sizes = [5, 7, 9, 11]
        start_x = 380
        for i, s in enumerate(sizes):
            label = f"{s}x{s}"
            btn = UIButton(pygame.Rect(start_x + i * 68, 255, 60, 34), label, self.font_badge, tag=str(s))
            if s == 7:
                btn.is_selected = True
            self.grid_buttons.append(btn)

        # Level selector buttons (Level 1: Recruit, Level 2: Tactical, Level 3: Nightmare)
        self.level_buttons: List[UIButton] = []
        levels = [(1, "L1: Recruit"), (2, "L2: Tactical"), (3, "L3: Nightmare")]
        for i, (lvl, label) in enumerate(levels):
            accent = COLOR_TEXT_ACCENT_GREEN if lvl == 1 else (COLOR_TEXT_ACCENT_AMBER if lvl == 2 else COLOR_TEXT_ACCENT_RED)
            btn = UIButton(pygame.Rect(380 + i * 115, 310, 108, 34), label, self.font_badge, accent_color=accent, tag=str(lvl))
            if lvl == 2:
                btn.is_selected = True
            self.level_buttons.append(btn)

        # Main Home Action Buttons (Polished labels)
        self.btn_how_to_play = UIButton(pygame.Rect(230, 415, 220, 46), "HOW TO PLAY", self.font_header)
        self.btn_start_mission = UIButton(pygame.Rect(490, 415, 250, 46), ">> START MISSION <<", self.font_header,
                                          accent_color=COLOR_TEXT_ACCENT_GREEN)

        # In-Game Top-Right Quick Pause Button
        self.btn_pause = UIButton(pygame.Rect(self.screen_width - 130, 16, 110, 32), "|| PAUSE", self.font_badge,
                                  accent_color=COLOR_TEXT_ACCENT_AMBER)

        # How to Play back button
        self.btn_back_to_menu = UIButton(pygame.Rect(self.screen_width // 2 - 110, 680, 220, 42),
                                         "<< RETURN", self.font_header)

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

        # Tactical Pause / Sir Presentation Overlay (Placed in the right margin card to leave the entire grid 100% visible)
        self.btn_pause_resume = UIButton(pygame.Rect(785, 42, 159, 36), "▶ RESUME (P)", self.font_header,
                                         accent_color=COLOR_TEXT_ACCENT_GREEN)
        self.btn_pause_restart = UIButton(pygame.Rect(785, 84, 159, 36), "⟳ RESTART (R)", self.font_header,
                                          accent_color=COLOR_TEXT_ACCENT_CYAN)
        self.btn_pause_help = UIButton(pygame.Rect(785, 126, 159, 34), "📖 CONTROLS", self.font_body)
        self.btn_pause_menu = UIButton(pygame.Rect(785, 166, 159, 34), "✕ HOME MENU", self.font_body,
                                       accent_color=COLOR_TEXT_ACCENT_RED)

    def update(self, dt: float) -> None:
        """Update animation timers and interactive text fields."""
        self.anim_time += dt
        self.input_player_name.update(dt)

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
    # HOME SCREEN RENDERING
    # =========================================================================
    def draw_home_screen(self, surface: pygame.Surface, best_victory_steps: Optional[int]) -> None:
        """Render the complete interactive Home Screen with ultra-premium cybernetics."""
        surface.fill(COLOR_BG)

        # 1. Background cybernetic coordinate grid
        for x in range(0, self.screen_width, 40):
            pygame.draw.line(surface, (18, 26, 40), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, 40):
            pygame.draw.line(surface, (18, 26, 40), (0, y), (self.screen_width, y), 1)

        # Ambient central atmospheric glow
        glow_surf = pygame.Surface((720, 320), pygame.SRCALPHA)
        glow_surf.fill((0, 110, 180, 16))
        surface.blit(glow_surf, (120, 172))

        # 2. UPGRADED TOP HEADER ("upur a likha cng kro")
        # Academic & AI Simulation Category Badge
        cat_badge = self.font_badge.render("// ADVANCED AGENTIC AI :: ACADEMIC RESEARCH PROJECT //", True, COLOR_TEXT_ACCENT_CYAN)
        cat_rect = cat_badge.get_rect(center=(self.screen_width // 2, 24))
        surface.blit(cat_badge, cat_rect)

        # Grand Title with 3D drop-shadow
        title_text = "TREASURE HUNTER // TACTICAL EVASION"
        shadow_title = self.font_title.render(title_text, True, (0, 60, 100))
        main_title = self.font_title.render(title_text, True, (0, 230, 255))
        title_x = self.screen_width // 2 - main_title.get_width() // 2
        surface.blit(shadow_title, (title_x + 2, 50))
        surface.blit(main_title, (title_x, 48))

        # High-Impact Subtitle (Academic Architecture)
        sub_text = "AUTONOMOUS NEURAL MULTI-AGENT PURSUIT // ZERO A* PATHFINDING ARCHITECTURE"
        sub_surf = self.font_bold.render(sub_text, True, (155, 180, 215))
        surface.blit(sub_surf, (self.screen_width // 2 - sub_surf.get_width() // 2, 88))

        # Cyber Divider Line with Pulsing Center Diamond
        pygame.draw.line(surface, (38, 70, 110), (140, 114), (self.screen_width - 140, 114), 1)
        p_cx = self.screen_width // 2
        p_cy = 114
        p_pts = [(p_cx, p_cy - 4), (p_cx + 5, p_cy), (p_cx, p_cy + 4), (p_cx - 5, p_cy)]
        pygame.draw.polygon(surface, (0, 210, 255), p_pts)

        # Upgraded All-Time Best Victory Record Badge
        rec_val = f"{best_victory_steps} STEPS" if best_victory_steps is not None else "UNCLAIMED (NO RECORD YET)"
        rec_text = f"[RECORD] ALL-TIME BEST VICTORY: {rec_val}"
        rec_surf = self.font_bold.render(rec_text, True, COLOR_KEY_GOLD)
        rw = rec_surf.get_width() + 32
        rh = 30
        rx = self.screen_width // 2 - rw // 2
        ry = 126
        rec_bg = pygame.Rect(rx, ry, rw, rh)
        pygame.draw.rect(surface, (26, 22, 14), rec_bg, border_radius=4)
        pygame.draw.rect(surface, COLOR_KEY_GOLD, rec_bg, width=1, border_radius=4)
        # Specular glint
        pygame.draw.circle(surface, (255, 250, 200), (rx + 10, ry + 10), 2)
        surface.blit(rec_surf, (rx + 16, ry + 6))

        # 3. PREMIUM GLASSMORPHIC COMMAND CONSOLE CHASSIS ("eta premium kro")
        chassis_x = 120
        chassis_y = 172
        chassis_w = 720
        chassis_h = 310
        chassis_rect = pygame.Rect(chassis_x, chassis_y, chassis_w, chassis_h)

        # Outer chassis drop-shadow
        pygame.draw.rect(surface, (6, 10, 16), chassis_rect.move(0, 4), border_radius=8)

        # Translucent glassmorphic deck fill
        deck_glass = pygame.Surface((chassis_w, chassis_h), pygame.SRCALPHA)
        deck_glass.fill((13, 19, 32, 235))
        surface.blit(deck_glass, chassis_rect.topleft)

        # Double-line cyber borders
        pygame.draw.rect(surface, (36, 60, 95), chassis_rect, width=1, border_radius=8)
        pygame.draw.rect(surface, (0, 180, 240, 110), chassis_rect.inflate(-4, -4), width=1, border_radius=6)

        # 4 Tactical Corner L-Brackets with Glowing Tick Marks
        t_sz = 14
        # Top-Left
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (chassis_x, chassis_y), (chassis_x + t_sz, chassis_y), 2)
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (chassis_x, chassis_y), (chassis_x, chassis_y + t_sz), 2)
        # Top-Right
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (chassis_x + chassis_w - 1, chassis_y), (chassis_x + chassis_w - 1 - t_sz, chassis_y), 2)
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (chassis_x + chassis_w - 1, chassis_y), (chassis_x + chassis_w - 1, chassis_y + t_sz), 2)
        # Bottom-Left
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (chassis_x, chassis_y + chassis_h - 1), (chassis_x + t_sz, chassis_y + chassis_h - 1), 2)
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (chassis_x, chassis_y + chassis_h - 1), (chassis_x, chassis_y + chassis_h - 1 - t_sz), 2)
        # Bottom-Right
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (chassis_x + chassis_w - 1, chassis_y + chassis_h - 1), (chassis_x + chassis_w - 1 - t_sz, chassis_y + chassis_h - 1), 2)
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (chassis_x + chassis_w - 1, chassis_y + chassis_h - 1), (chassis_x + chassis_w - 1, chassis_y + chassis_h - 1 - t_sz), 2)

        # Chassis Top Ribbon
        ribbon_rect = pygame.Rect(chassis_x + 8, chassis_y + 8, chassis_w - 16, 24)
        pygame.draw.rect(surface, (18, 27, 44), ribbon_rect, border_radius=4)
        ribbon_txt = self.font_badge.render("// SECTOR DEPLOYMENT CONSOLE // MISSION CONFIGURATION", True, COLOR_TEXT_SECONDARY)
        surface.blit(ribbon_txt, (ribbon_rect.x + 12, ribbon_rect.y + 4))
        # Status LED
        pygame.draw.circle(surface, COLOR_TEXT_ACCENT_GREEN, (ribbon_rect.right - 20, ribbon_rect.centery), 4)
        led_txt = self.font_small.render("ONLINE", True, COLOR_TEXT_ACCENT_GREEN)
        surface.blit(led_txt, (ribbon_rect.right - 68, ribbon_rect.y + 5))

        # Animated Subtle Cyan Scanline traveling down the console
        scan_offset = int((self.anim_time * 65.0) % (chassis_h - 40))
        scan_y = chassis_y + 35 + scan_offset
        scan_surf = pygame.Surface((chassis_w - 16, 2), pygame.SRCALPHA)
        scan_surf.fill((0, 220, 255, 28))
        surface.blit(scan_surf, (chassis_x + 8, scan_y))

        # Form Section Labels
        lbl_name = self.font_bold.render("[01] OPERATIVE CALLSIGN:", True, COLOR_TEXT_PRIMARY)
        surface.blit(lbl_name, (150, 208))
        self.input_player_name.draw(surface)

        lbl_grid = self.font_bold.render("[02] ARENA GRID MATRIX:", True, COLOR_TEXT_PRIMARY)
        surface.blit(lbl_grid, (150, 262))
        for btn in self.grid_buttons:
            btn.draw(surface)

        lbl_lvl = self.font_bold.render("[03] THREAT DIFFICULTY:", True, COLOR_TEXT_PRIMARY)
        surface.blit(lbl_lvl, (150, 318))
        for btn in self.level_buttons:
            btn.draw(surface)

        # Chassis Interior Dividing Rule
        pygame.draw.line(surface, (28, 45, 70), (chassis_x + 20, 375), (chassis_x + chassis_w - 20, 375), 1)

        # Action Buttons
        self.btn_how_to_play.draw(surface)

        # Primary Start Mission CTA with animated pulse ring
        cta_pulse = 1.0 + 0.05 * math.sin(self.anim_time * 6.0)
        cta_rect = self.btn_start_mission.rect
        pygame.draw.rect(surface, (40, 240, 120), cta_rect.inflate(int(4 * cta_pulse), int(4 * cta_pulse)), width=1, border_radius=6)
        self.btn_start_mission.draw(surface)

        # 4. UPGRADED BOTTOM STATUS DOCK ("niche likha gula cng kro")
        dock_w = 880
        dock_h = 58
        dock_x = (self.screen_width - dock_w) // 2
        dock_y = self.screen_height - dock_h - 18
        dock_rect = pygame.Rect(dock_x, dock_y, dock_w, dock_h)

        # Glass fill
        dock_glass = pygame.Surface((dock_w, dock_h), pygame.SRCALPHA)
        dock_glass.fill((12, 17, 28, 235))
        surface.blit(dock_glass, dock_rect.topleft)

        # Top illuminated neon border
        pygame.draw.rect(surface, (35, 75, 120), dock_rect, width=1, border_radius=6)
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (dock_x + 20, dock_y), (dock_x + dock_w - 20, dock_y), 2)

        # Line 1: Technical Architecture Telemetry (Cleanly spaced)
        tech_line = "[ AI: GEMINI 2.5 FLASH ]   |   [ LATENCY: 0 THINKING BUDGET ]   |   [ STRICTLY NO A* ]   |   [ FPS: 60 ]"
        t_line_surf = self.font_bold.render(tech_line, True, COLOR_TEXT_ACCENT_GREEN)
        surface.blit(t_line_surf, t_line_surf.get_rect(center=(self.screen_width // 2, dock_y + 18)))

        # Line 2: Academic Presentation Signature
        sig_line = "ACADEMIC AI EVALUATION SUITE  •  SQLITE3 REPOSITORY CONNECTED  •  NON-BLOCKING DAEMON THREADS"
        s_line_surf = self.font_small.render(sig_line, True, COLOR_TEXT_MUTED)
        surface.blit(s_line_surf, s_line_surf.get_rect(center=(self.screen_width // 2, dock_y + 40)))

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

        # Grid Base Background
        grid_rect = pygame.Rect(origin_x, origin_y, grid_w, grid_h)
        pygame.draw.rect(surface, (13, 18, 28), grid_rect)

        # High-Tech Floor Seam Markers & Registration Ticks on walkable cells
        cross_len = max(2, int(cell_size * 0.08))
        for r in range(grid_size):
            for c in range(grid_size):
                if (r, c) not in walls:
                    cx = origin_x + c * cell_size
                    cy = origin_y + r * cell_size
                    # Floor plate subtle seam dots at cell corners
                    pygame.draw.circle(surface, (22, 32, 48), (int(cx + 4), int(cy + 4)), 1)
                    pygame.draw.circle(surface, (22, 32, 48), (int(cx + cell_size - 4), int(cy + 4)), 1)
                    pygame.draw.circle(surface, (22, 32, 48), (int(cx + 4), int(cy + cell_size - 4)), 1)
                    pygame.draw.circle(surface, (22, 32, 48), (int(cx + cell_size - 4), int(cy + cell_size - 4)), 1)

        # Dynamic Wall Relocation Visual Pulse Alert
        if wall_shift_alert > 0:
            alpha = int(min(1.0, wall_shift_alert * 2.0) * 85)
            alert_surf = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
            alert_surf.fill((0, 210, 255, alpha))
            surface.blit(alert_surf, (origin_x, origin_y))

        # Grid Coordinate Lines
        for r in range(grid_size + 1):
            py = origin_y + r * cell_size
            pygame.draw.line(surface, COLOR_GRID_LINE, (origin_x, py), (origin_x + grid_w, py), 1)
        for c in range(grid_size + 1):
            px = origin_x + c * cell_size
            pygame.draw.line(surface, COLOR_GRID_LINE, (px, origin_y), (px, origin_y + grid_h), 1)

        # Outer Tactical Grid Frame with Specular Rim
        pygame.draw.rect(surface, (45, 110, 180), grid_rect, width=2)
        pygame.draw.rect(surface, (18, 30, 48), grid_rect.inflate(4, 4), width=1)

        # 1. PREMIUM CYBERNETIC BLAST BARRIERS (WALLS)
        for (wr, wc) in walls:
            wx = origin_x + wc * cell_size
            wy = origin_y + wr * cell_size
            pad = max(2.0, cell_size * 0.04)
            w_w = cell_size - pad * 2
            w_h = cell_size - pad * 2
            w_rect = pygame.Rect(wx + pad, wy + pad, w_w, w_h)

            # Ambient drop shadow under barrier
            shadow_rect = pygame.Rect(wx + pad, wy + pad + 3, w_w, w_h)
            pygame.draw.rect(surface, (8, 12, 18), shadow_rect, border_radius=4)

            # Heavy carbon composite hull plate
            pygame.draw.rect(surface, (22, 28, 42), w_rect, border_radius=4)

            # 3D Chiseled Bevel:
            # Top & Left specular highlight line
            pygame.draw.line(surface, (68, 96, 138), (w_rect.left + 1, w_rect.top + 1), (w_rect.right - 2, w_rect.top + 1), 1)
            pygame.draw.line(surface, (68, 96, 138), (w_rect.left + 1, w_rect.top + 1), (w_rect.left + 1, w_rect.bottom - 2), 1)
            # Bottom & Right dark ambient occlusion shadow
            pygame.draw.line(surface, (10, 14, 22), (w_rect.left + 1, w_rect.bottom - 1), (w_rect.right - 1, w_rect.bottom - 1), 1)
            pygame.draw.line(surface, (10, 14, 22), (w_rect.right - 1, w_rect.top + 1), (w_rect.right - 1, w_rect.bottom - 1), 1)

            # Inset reinforced armor plate
            inset_m = max(3.0, cell_size * 0.14)
            inset_rect = pygame.Rect(wx + inset_m, wy + inset_m, cell_size - inset_m * 2, cell_size - inset_m * 2)
            pygame.draw.rect(surface, (16, 21, 32), inset_rect, border_radius=2)
            pygame.draw.rect(surface, (38, 54, 80), inset_rect, width=1, border_radius=2)

            # 4 Corner Heavy Industrial Rivets/Bolts with Specular Gleam
            r_inset = inset_m * 0.52
            rivet_r = max(1.5, cell_size * 0.035)
            for rx, ry in [
                (wx + pad + r_inset, wy + pad + r_inset),
                (wx + cell_size - pad - r_inset, wy + pad + r_inset),
                (wx + pad + r_inset, wy + cell_size - pad - r_inset),
                (wx + cell_size - pad - r_inset, wy + cell_size - pad - r_inset)
            ]:
                pygame.draw.circle(surface, (8, 12, 18), (int(rx + 0.5), int(ry + 0.5)), int(rivet_r + 0.5))
                pygame.draw.circle(surface, (130, 160, 195), (int(rx), int(ry)), int(rivet_r))
                pygame.draw.circle(surface, (220, 240, 255), (int(rx - 0.5), int(ry - 0.5)), max(1, int(rivet_r * 0.5)))

            # Central Cybernetic Reactor Node
            c_cx = wx + cell_size / 2.0
            c_cy = wy + cell_size / 2.0
            core_half = max(3.0, cell_size * 0.14)

            # Circuit Conduits (connecting core to armor edge midpoints)
            trace_col = (255, 140, 20) if wall_shift_alert > 0 else (36, 62, 92)
            pygame.draw.line(surface, trace_col, (c_cx - core_half * 1.5, c_cy), (c_cx + core_half * 1.5, c_cy), 1)
            pygame.draw.line(surface, trace_col, (c_cx, c_cy - core_half * 1.5), (c_cx, c_cy + core_half * 1.5), 1)

            # Dynamic Reactor Core Pulse
            if wall_shift_alert > 0:
                p_rate = 14.0
                p_core = (255, 160, 30)
                p_glow = (255, 230, 120)
            else:
                p_rate = 3.6
                p_core = (0, 215, 255)
                p_glow = (220, 250, 255)

            p_factor = 0.82 + 0.18 * math.sin(self.anim_time * p_rate + (wr * 3 + wc * 7))
            cur_r = core_half * p_factor

            # Chamfered / Diamond Energy Core
            core_pts = [
                (c_cx, c_cy - cur_r),
                (c_cx + cur_r, c_cy),
                (c_cx, c_cy + cur_r),
                (c_cx - cur_r, c_cy)
            ]
            pygame.draw.polygon(surface, p_core, core_pts)
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
            exit_label = self.font_bold.render("EXTRACT", True, (255, 255, 255))
        else:
            # Standby Locked Security Grid (Amber / Slate)
            pygame.draw.circle(surface, (220, 140, 30), (int(ex_x), int(ex_y)), p_r, width=2)
            core_r = max(2, int(portal_radius * 0.52))
            pygame.draw.circle(surface, (45, 38, 25), (int(ex_x), int(ex_y)), core_r)
            exit_label = self.font_badge.render("LOCKED", True, (255, 190, 60))

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
            k_lbl = self.font_badge.render("KEY", True, (25, 20, 10))
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
        pygame.draw.circle(surface, (0, 220, 255), (int(px), int(py)), ring_r, width=1)
        # Inner subtle stealth ring
        pygame.draw.circle(surface, (0, 140, 190), (int(px), int(py)), max(2, ring_r - 3), width=1)

        # 3. Animated Combat Boots with Cyan Heel Stabilizer LEDs
        walk_stride = math.sin(self.anim_time * 9.0) * (4.2 * scale)
        foot_spread = 5.8 * scale

        # Left Foot
        lfx = px + perp_x * (-foot_spread) + cos_a * walk_stride
        lfy = py + perp_y * (-foot_spread) + sin_a * walk_stride
        pygame.draw.circle(surface, (18, 25, 36), (int(lfx), int(lfy)), max(2, int(3.5 * scale)))
        pygame.draw.circle(surface, (0, 180, 235), (int(lfx - cos_a * (1.2 * scale)), int(lfy - sin_a * (1.2 * scale))), max(1, int(1.8 * scale)))

        # Right Foot
        rfx = px + perp_x * (foot_spread) - cos_a * walk_stride
        rfy = py + perp_y * (foot_spread) - sin_a * walk_stride
        pygame.draw.circle(surface, (18, 25, 36), (int(rfx), int(rfy)), max(2, int(3.5 * scale)))
        pygame.draw.circle(surface, (0, 180, 235), (int(rfx - cos_a * (1.2 * scale)), int(rfy - sin_a * (1.2 * scale))), max(1, int(1.8 * scale)))

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
        pygame.draw.polygon(surface, (0, 135, 195), [p_bp1, p_bp2, p_bp3, p_bp4])
        pygame.draw.polygon(surface, (0, 205, 255), [p_bp1, p_bp2, p_bp3, p_bp4], width=1)

        # Tactical harness straps & ammo webbing
        pygame.draw.line(surface, (25, 40, 60), p_l_shoulder, p_r_hip, max(1, int(1.8 * scale)))
        pygame.draw.line(surface, (25, 40, 60), p_r_shoulder, p_l_hip, max(1, int(1.8 * scale)))

        # Central Aegis Operative Chest Crest (Pulsing Cyan Emissive Node)
        crest_x = px + cos_a * (1.2 * scale)
        crest_y = py + sin_a * (1.2 * scale)
        crest_r = max(2, int(2.4 * scale))
        pygame.draw.circle(surface, (0, 220, 255), (int(crest_x), int(crest_y)), crest_r)
        pygame.draw.circle(surface, (220, 250, 255), (int(crest_x), int(crest_y)), max(1, int(crest_r * 0.5)))

        # Armored shoulder pauldrons with cyan trim
        pygame.draw.circle(surface, (0, 110, 165), (int(p_l_shoulder[0]), int(p_l_shoulder[1])), max(2, int(3.2 * scale)))
        pygame.draw.circle(surface, (0, 220, 255), (int(p_l_shoulder[0]), int(p_l_shoulder[1])), max(1, int(1.8 * scale)))
        pygame.draw.circle(surface, (0, 110, 165), (int(p_r_shoulder[0]), int(p_r_shoulder[1])), max(2, int(3.2 * scale)))
        pygame.draw.circle(surface, (0, 220, 255), (int(p_r_shoulder[0]), int(p_r_shoulder[1])), max(1, int(1.8 * scale)))

        # 5. Articulated Arms, Left Wrist PDA & Right Hand Tactical Scanner
        arm_reach = 9.5 * scale
        hand_r_x = px + perp_x * (sh_w * 0.8) + cos_a * arm_reach
        hand_r_y = py + perp_y * (sh_w * 0.8) + sin_a * arm_reach
        hand_l_x = px + perp_x * (-sh_w * 0.8) + cos_a * (arm_reach * 0.65)
        hand_l_y = py + perp_y * (-sh_w * 0.8) + sin_a * (arm_reach * 0.65)

        # Arm sleeves
        pygame.draw.line(surface, (0, 125, 185), p_r_shoulder, (hand_r_x, hand_r_y), max(2, int(3.6 * scale)))
        pygame.draw.line(surface, (0, 125, 185), p_l_shoulder, (hand_l_x, hand_l_y), max(2, int(3.6 * scale)))

        # Left Wrist Holographic Comms PDA
        pda_x = (p_l_shoulder[0] + hand_l_x) * 0.5
        pda_y = (p_l_shoulder[1] + hand_l_y) * 0.5
        pygame.draw.circle(surface, (0, 240, 255), (int(pda_x), int(pda_y)), max(1, int(2.0 * scale)))

        # Human Skin Hands with tactical fingerless gloves
        pygame.draw.circle(surface, (245, 195, 158), (int(hand_r_x), int(hand_r_y)), max(1, int(2.5 * scale)))
        pygame.draw.circle(surface, (245, 195, 158), (int(hand_l_x), int(hand_l_y)), max(1, int(2.5 * scale)))

        # Handheld Tactical Scanner / Flashlight Device
        scanner_tip_x = hand_r_x + cos_a * (5.0 * scale)
        scanner_tip_y = hand_r_y + sin_a * (5.0 * scale)
        pygame.draw.line(surface, (45, 58, 78), (hand_r_x, hand_r_y), (scanner_tip_x, scanner_tip_y), max(2, int(3.0 * scale)))
        pygame.draw.circle(surface, (0, 240, 255), (int(scanner_tip_x), int(scanner_tip_y)), max(1, int(2.2 * scale)))

        # Multi-Stage Volumetric Flashlight Beam
        light_len = cell_size * 0.85
        light_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        p_apex = (scanner_tip_x, scanner_tip_y)

        # Broad ambient beam
        half_fov = math.radians(24)
        p_l = (scanner_tip_x + math.cos(angle - half_fov) * light_len, scanner_tip_y + math.sin(angle - half_fov) * light_len)
        p_r = (scanner_tip_x + math.cos(angle + half_fov) * light_len, scanner_tip_y + math.sin(angle + half_fov) * light_len)
        pygame.draw.polygon(light_surf, (0, 220, 255, 20), [p_apex, p_l, p_r])

        # Focused core penetrating beam
        narrow_fov = math.radians(11)
        p_nl = (scanner_tip_x + math.cos(angle - narrow_fov) * (light_len * 1.05), scanner_tip_y + math.sin(angle - narrow_fov) * (light_len * 1.05))
        p_nr = (scanner_tip_x + math.cos(angle + narrow_fov) * (light_len * 1.05), scanner_tip_y + math.sin(angle + narrow_fov) * (light_len * 1.05))
        pygame.draw.polygon(light_surf, (140, 245, 255, 45), [p_apex, p_nl, p_nr])
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

        # SMART CYBERNETIC RETINAL VISOR (Glowing Cyan with Animated Scanline)
        v_dist = 3.6 * scale
        v_span = 4.2 * scale
        v_left = (head_cx + perp_x * (-v_span) + cos_a * v_dist, head_cy + perp_y * (-v_span) + sin_a * v_dist)
        v_right = (head_cx + perp_x * (v_span) + cos_a * v_dist, head_cy + perp_y * (v_span) + sin_a * v_dist)

        # Visor outer neon glow
        pygame.draw.line(surface, (0, 240, 255), v_left, v_right, max(2, int(3.2 * scale)))
        # Visor core laser streak
        pygame.draw.line(surface, (220, 255, 255), v_left, v_right, max(1, int(1.6 * scale)))

        # Animated mini scanline traveling across visor
        scan_t = (math.sin(self.anim_time * 6.0) + 1.0) * 0.5
        scan_x = v_left[0] + (v_right[0] - v_left[0]) * scan_t
        scan_y = v_left[1] + (v_right[1] - v_left[1]) * scan_t
        pygame.draw.circle(surface, (255, 255, 255), (int(scan_x), int(scan_y)), max(1, int(1.8 * scale)))

        # Tactical Headset Comms with Boom Microphone
        ear_x = head_cx + perp_x * (-head_r * 0.95)
        ear_y = head_cy + perp_y * (-head_r * 0.95)
        pygame.draw.circle(surface, (0, 240, 255), (int(ear_x), int(ear_y)), max(1, int(2.2 * scale)))
        mic_tip_x = ear_x + cos_a * (head_r * 0.8) + perp_x * (head_r * 0.4)
        mic_tip_y = ear_y + sin_a * (head_r * 0.8) + perp_y * (head_r * 0.4)
        pygame.draw.line(surface, (40, 50, 65), (ear_x, ear_y), (mic_tip_x, mic_tip_y), max(1, int(1.5 * scale)))

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
        lbl = self.font_small.render("OPERATIVE", True, (0, 220, 255))
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
        h_tag = self.font_small.render(f"HUNTER-0{hunter_id}", True, (255, 80, 100))
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
        best_str = f"BEST RECORD: {best_steps} STEPS" if best_steps is not None else "BEST RECORD: NONE"
        surface.blit(self.font_small.render(best_str, True, COLOR_TEXT_ACCENT_AMBER), (c1_rect.x, y))
        y += 22
        # Key Status Badge
        key_label = "KEY: SECURED [EXIT OPEN]" if has_key else "KEY: NOT SECURED"
        key_color = COLOR_TEXT_ACCENT_GREEN if has_key else COLOR_TEXT_ACCENT_RED
        k_surf = self.font_bold.render(key_label, True, key_color)
        k_bg = pygame.Rect(c1_rect.x, y, k_surf.get_width() + 10, 22)
        pygame.draw.rect(surface, (20, 28, 38), k_bg, border_radius=3)
        pygame.draw.rect(surface, key_color, k_bg, width=1, border_radius=3)
        surface.blit(k_surf, (c1_rect.x + 5, y + 2))

        # ---------------------------------------------------------------------
        # COLUMN 2: NEURAL AI TELEMETRY
        # ---------------------------------------------------------------------
        h2 = self.font_badge.render("// GEMINI NEURAL TELEMETRY", True, COLOR_TEXT_ACCENT_CYAN)
        surface.blit(h2, (c2_rect.x, c2_rect.y))

        y2 = c2_rect.y + 22
        model_str = "ENGINE: gemini-2.5-flash"
        surface.blit(self.font_small.render(model_str, True, COLOR_TEXT_SECONDARY), (c2_rect.x, y2))
        y2 += 18

        lat_color = COLOR_TEXT_ACCENT_GREEN if ai_latency_ms < 600 else COLOR_TEXT_ACCENT_AMBER
        lat_str = f"INFERENCE: {ai_latency_ms} ms (budget=0)"
        surface.blit(self.font_body.render(lat_str, True, lat_color), (c2_rect.x, y2))
        y2 += 22

        # Status indicator with LED pip
        led_color = COLOR_TEXT_ACCENT_GREEN if "ONLINE" in ai_status else COLOR_TEXT_ACCENT_AMBER
        led_pulse = 1.0 + 0.2 * math.sin(self.anim_time * 8.0)
        pygame.draw.circle(surface, led_color, (c2_rect.x + 8, y2 + 8), int(5 * led_pulse))

        status_txt = f"STATUS: {ai_status}"
        surface.blit(self.font_bold.render(status_txt, True, led_color), (c2_rect.x + 22, y2))
        y2 += 22

        path_note = self.font_small.render("PATHFINDING: 100% LLM (NO A*)", True, COLOR_TEXT_MUTED)
        surface.blit(path_note, (c2_rect.x, y2))

        # ---------------------------------------------------------------------
        # COLUMN 3: LIVE TACTICAL COMMANDER TRANSMISSION
        # ---------------------------------------------------------------------
        h3 = self.font_badge.render("// TACTICAL COMMAND TRANSMISSION", True, COLOR_TEXT_ACCENT_AMBER)
        surface.blit(h3, (c3_rect.x, c3_rect.y))

        # Transmission Terminal Box
        box_rect = pygame.Rect(c3_rect.x, c3_rect.y + 20, c3_rect.width, self.hud_height - 50)
        pygame.draw.rect(surface, (18, 24, 36), box_rect, border_radius=4)
        pygame.draw.rect(surface, (38, 52, 76), box_rect, width=1, border_radius=4)

        # Terminal Comms Header
        radio_icon = self.font_small.render("[COMMS ACTIVE]", True, COLOR_TEXT_ACCENT_GREEN)
        surface.blit(radio_icon, (box_rect.x + 8, box_rect.y + 6))

        # Order Content (Tense transmission under 12 words)
        clean_order = commander_order.strip() if commander_order else "Observing battlefield telemetry..."
        order_surf = self.font_header.render(f'"{clean_order}"', True, COLOR_TEXT_PRIMARY)
        surface.blit(order_surf, (box_rect.x + 8, box_rect.y + 28))

        # Subtext / Instruction hint
        hint_surf = self.font_small.render("[WASD: Move | P/ESC: Pause | H: Spawn | B: Shift Barrier]", True, COLOR_TEXT_MUTED)
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
            title_text = "MISSION ACCOMPLISHED"
            sub_text = f"Operative successfully extracted in {steps} steps!"
            title_color = COLOR_TEXT_ACCENT_GREEN
        else:
            title_text = "TACTICAL CASUALTY"
            sub_text = f"Operative intercepted by Hunter Drone after {steps} steps."
            title_color = COLOR_TEXT_ACCENT_RED

        t_surf = self.font_title.render(title_text, True, title_color)
        surface.blit(t_surf, t_surf.get_rect(center=(cx, cy - 120)))

        s_surf = self.font_body.render(sub_text, True, COLOR_TEXT_PRIMARY)
        surface.blit(s_surf, s_surf.get_rect(center=(cx, cy - 80)))

        if is_victory and is_new_best:
            rec_surf = self.font_header.render("★ NEW BEST VICTORY RECORD! ★", True, COLOR_TEXT_ACCENT_AMBER)
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
        Render tactical pause demonstration & walkthrough overlay.
        Allows the student to clearly explain the game and AI architecture to Sir/instructor:
        - 100% unobstructed view of the game board (center grid is completely clear).
        - On-grid callout badges pointing out Player, Hunters, Key, Exit, and Gemini Safe Path.
        - Left Dossier Panel: Academic AI Architecture & Zero A* rule.
        - Right Dossier Panel: Interactive Controls and Simulation Mechanics.
        """
        hunters = hunters or []
        recommended_path = recommended_path or []

        # 1. Very light background tint (alpha=25) so grid and entities remain 100% vivid
        dim_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_surf.fill((8, 12, 18, 28))
        surface.blit(dim_surf, (0, 0))

        # 2. Top Presentation Header Bar
        top_w = 580
        top_h = 28
        top_x = (self.screen_width - top_w) // 2
        top_rect = pygame.Rect(top_x, 8, top_w, top_h)
        top_glass = pygame.Surface((top_w, top_h), pygame.SRCALPHA)
        top_glass.fill((12, 18, 28, 200))
        surface.blit(top_glass, top_rect.topleft)
        pygame.draw.rect(surface, COLOR_TEXT_ACCENT_AMBER, top_rect, width=1, border_radius=4)

        head_txt = self.font_badge.render("⏸ TACTICAL PAUSE // SIR PROJECT DEMONSTRATION & WALKTHROUGH MODE", True, COLOR_TEXT_ACCENT_AMBER)
        surface.blit(head_txt, head_txt.get_rect(center=(self.screen_width // 2, 22)))

        # 3. Helper for drawing on-grid explanatory callouts
        def draw_callout_badge(label_text: str, tx: float, ty: float, color: Tuple[int, int, int]) -> None:
            lbl_surf = self.font_small.render(label_text, True, color)
            lw = lbl_surf.get_width() + 10
            lh = 18
            bx = int(tx - lw / 2)
            by = int(ty - 24)

            # Keep callout within screen bounds
            bx = max(195, min(bx, self.screen_width - 195 - lw))
            by = max(38, min(by, self.hud_rect.y - 22))

            # Translucent callout pill
            pill_surf = pygame.Surface((lw, lh), pygame.SRCALPHA)
            pill_surf.fill((10, 16, 26, 215))
            surface.blit(pill_surf, (bx, by))
            pygame.draw.rect(surface, color, pygame.Rect(bx, by, lw, lh), width=1, border_radius=3)
            surface.blit(lbl_surf, (bx + 5, by + 2))

            # Small downward pointer line
            pygame.draw.line(surface, color, (int(tx), by + lh), (int(tx), int(ty - 4)), 1)

        # Draw callouts on active board entities
        if player_x > 0 and player_y > 0:
            draw_callout_badge("👤 OPERATIVE (Human Player)", player_x, player_y - cell_size * 0.35, COLOR_TEXT_ACCENT_CYAN)

        for h in hunters:
            draw_callout_badge(f"🚨 HUNTER #{h.hunter_id} (Gemini 2.5 Flash)", h.visual_x, h.visual_y - cell_size * 0.35, COLOR_TEXT_ACCENT_RED)

        if not has_key and cell_size > 0:
            kx = origin_x + key_pos[1] * cell_size + cell_size / 2.0
            ky = origin_y + key_pos[0] * cell_size + cell_size / 2.0
            draw_callout_badge("🔑 CIPHER KEY (Objective 1)", kx, ky - cell_size * 0.32, COLOR_KEY_GOLD)

        if cell_size > 0:
            ex_x = origin_x + exit_pos[1] * cell_size + cell_size / 2.0
            ex_y = origin_y + exit_pos[0] * cell_size + cell_size / 2.0
            exit_stat = "EXTRACTION (UNLOCKED!)" if has_key else "EXTRACTION (LOCKED: Need Key)"
            draw_callout_badge(f"🚪 {exit_stat}", ex_x, ex_y - cell_size * 0.38, COLOR_EXIT_PORTAL)

        if recommended_path and cell_size > 0 and len(recommended_path[0]) >= 2:
            bx = origin_x + recommended_path[0][1] * cell_size + cell_size / 2.0
            by = origin_y + recommended_path[0][0] * cell_size + cell_size / 2.0
            draw_callout_badge("🟢 SAFE PATH (No A*)", bx, by - cell_size * 0.22, COLOR_TEXT_ACCENT_GREEN)

        # ---------------------------------------------------------------------
        # 4. LEFT DOSSIER PANEL: ACADEMIC AI ARCHITECTURE (FOR SIR)
        # ---------------------------------------------------------------------
        left_rect = pygame.Rect(8, 10, 174, 598)
        left_glass = pygame.Surface((left_rect.width, left_rect.height), pygame.SRCALPHA)
        left_glass.fill((12, 18, 28, 215))
        surface.blit(left_glass, left_rect.topleft)
        pygame.draw.rect(surface, COLOR_TEXT_ACCENT_CYAN, left_rect, width=1, border_radius=6)

        ly = left_rect.y + 10
        surface.blit(self.font_badge.render("// SIR EVALUATION", True, COLOR_TEXT_ACCENT_AMBER), (left_rect.x + 8, ly))
        ly += 16
        surface.blit(self.font_bold.render("AI ARCHITECTURE", True, COLOR_TEXT_ACCENT_CYAN), (left_rect.x + 8, ly))
        ly += 18
        pygame.draw.line(surface, (35, 55, 80), (left_rect.x + 8, ly), (left_rect.right - 8, ly), 1)
        ly += 10

        ai_details = [
            ("AI MODEL:", "gemini-2.5-flash", COLOR_TEXT_ACCENT_GREEN),
            ("THINKING BUDGET:", "0 (Low latency)", COLOR_TEXT_PRIMARY),
            ("PATHFINDING:", "STRICTLY NO A*", COLOR_TEXT_ACCENT_RED),
            ("AI DIRECTIVE:", "100% LLM JSON", COLOR_TEXT_ACCENT_CYAN),
            ("PURSUIT LOGIC:", "Flank & Intercept", COLOR_TEXT_PRIMARY),
            ("PLAYER ADVICE:", "3 Safe Steps [r,c]", COLOR_TEXT_ACCENT_GREEN),
            ("SIGHTLINE EVASION:", "Exploits blind spots", COLOR_TEXT_SECONDARY),
            ("SAFETY FALLBACK:", "Greedy Manhattan", COLOR_TEXT_ACCENT_AMBER),
            ("CONCURRENCY:", "daemon=True Thread", COLOR_TEXT_PRIMARY),
            ("FRAME TIMING:", "60 FPS (Zero Lag)", COLOR_TEXT_ACCENT_GREEN),
            ("DATA STORAGE:", "SQLite3 DB Record", COLOR_TEXT_SECONDARY),
        ]

        for heading, val, col in ai_details:
            surface.blit(self.font_small.render(heading, True, COLOR_TEXT_MUTED), (left_rect.x + 8, ly))
            ly += 14
            surface.blit(self.font_bold.render(val, True, col), (left_rect.x + 8, ly))
            ly += 18

        # ---------------------------------------------------------------------
        # 5. RIGHT DOSSIER PANEL: CONTROLS & PROJECT MECHANICS (FOR SIR)
        # ---------------------------------------------------------------------
        right_rect = pygame.Rect(778, 10, 174, 598)
        right_glass = pygame.Surface((right_rect.width, right_rect.height), pygame.SRCALPHA)
        right_glass.fill((12, 18, 28, 215))
        surface.blit(right_glass, right_rect.topleft)
        pygame.draw.rect(surface, COLOR_TEXT_ACCENT_AMBER, right_rect, width=1, border_radius=6)

        ry = right_rect.y + 10
        surface.blit(self.font_badge.render("// ACTIONS & CONTROLS", True, COLOR_TEXT_ACCENT_AMBER), (right_rect.x + 8, ry))
        ry += 22

        # Draw action buttons inside right dossier card
        self.btn_pause_resume.draw(surface)
        self.btn_pause_restart.draw(surface)
        self.btn_pause_help.draw(surface)
        self.btn_pause_menu.draw(surface)

        ry = 210
        pygame.draw.line(surface, (60, 45, 25), (right_rect.x + 8, ry), (right_rect.right - 8, ry), 1)
        ry += 10

        surface.blit(self.font_badge.render("// SECTOR MECHANICS", True, COLOR_TEXT_ACCENT_CYAN), (right_rect.x + 8, ry))
        ry += 18

        mechanics = [
            ("CURRENT LEVEL:", level_name.upper(), COLOR_TEXT_ACCENT_AMBER),
            ("DYNAMIC WALLS:", "Shifts every 2.5s", COLOR_TEXT_ACCENT_CYAN),
            ("OVERWRITE SHIELD:", "Entities protected", COLOR_TEXT_PRIMARY),
            ("HUNTER UNITS:", f"{len(hunters)} / 8 Max Drones", COLOR_TEXT_ACCENT_RED),
            ("FACING VECTORS:", "Directional [dr, dc]", COLOR_TEXT_SECONDARY),
            ("LERP INTERPOLATION:", "speed = 0.28 (Smooth)", COLOR_TEXT_ACCENT_GREEN),
            ("MISSION OBJECTIVE:", "Key [K] -> Exit [E]", COLOR_KEY_GOLD),
        ]

        for heading, val, col in mechanics:
            surface.blit(self.font_small.render(heading, True, COLOR_TEXT_MUTED), (right_rect.x + 8, ry))
            ry += 14
            surface.blit(self.font_bold.render(val, True, col), (right_rect.x + 8, ry))
            ry += 18

        hint_unpause = self.font_small.render("[P / SPACE to Resume]", True, COLOR_TEXT_MUTED)
        surface.blit(hint_unpause, (right_rect.x + 14, right_rect.bottom - 22))

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
