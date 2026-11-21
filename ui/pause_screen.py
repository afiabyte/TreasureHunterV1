"""
UI Pause Screen: Retro-pixel RPG Pause Dialog Overlay.
Matches reference mockup media_1795263510678_20cb89ba.jpg 1:1.

Features:
- Dark semi-transparent gameplay dimming backdrop.
- Carved wood chassis with 4 outer golden brass corner rivets.
- Aged cream parchment sheet with torn edge notches and 4 inner corner rivets.
- Hanging dungeon lantern at top center with glowing amber flame.
- Stacked 3D title: "GAME PAUSED" with gold/amber gradient and dark outline.
- Recessed wood plaque: "LEVEL {num} - {DIFFICULTY}".
- 4 stacked action buttons matching reference mockup:
  1. "RESUME GAME" (vibrant emerald green)
  2. "RESTART LEVEL [R]" (slate blue)
  3. "SETTINGS ⚙" (warm wood with gear icon)
  4. "QUIT TO MENU" (crimson red)
"""

import math
from typing import Optional
import pygame

from .widgets import UIButton


class PauseScreenRenderer:
    """Renders the retro-pixel RPG adventure pause dialog overlay."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

        if not pygame.font.get_init():
            pygame.font.init()

        # Cached typography matching mockup aesthetics
        self.font_title = pygame.font.SysFont("impact", 38)
        self.font_badge = pygame.font.SysFont("trebuchetms,tahoma,arial", 16, bold=True)
        self.font_btn = pygame.font.SysFont("impact", 20)
        self.font_small = pygame.font.SysFont("trebuchetms,tahoma,arial", 13, bold=True)

    def draw_corner_rivet(self, surface: pygame.Surface, x: int, y: int, radius: int = 5) -> None:
        """Draw 3D golden brass rivet with highlight and shadow."""
        # Shadow
        pygame.draw.circle(surface, (26, 12, 4), (x, y + 1), radius + 1)
        # Gold body
        pygame.draw.circle(surface, (218, 168, 48), (x, y), radius)
        # Highlight
        pygame.draw.circle(surface, (255, 235, 130), (x - 1, y - 1), max(1, radius // 2))
        # Center indent
        pygame.draw.circle(surface, (54, 28, 8), (x, y), max(1, radius // 3))

    def draw_hanging_lantern(self, surface: pygame.Surface, cx: int, top_y: int, anim_time: float = 0.0) -> None:
        """Render the detailed hanging dungeon lantern atop the wooden frame matching crop_pause_lantern.png."""
        # Warm ambient glow halo behind the lantern
        glow_pulse = 1.0 + 0.08 * math.sin(anim_time * 5.0)
        glow_r = int(32 * glow_pulse)
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 200, 70, 65), (glow_r, glow_r), glow_r)
        pygame.draw.circle(glow_surf, (255, 235, 140, 115), (glow_r, glow_r), int(glow_r * 0.55))
        surface.blit(glow_surf, glow_surf.get_rect(center=(cx, top_y + 44)))

        # 1. Hanging Iron Ring/Loop
        pygame.draw.circle(surface, (24, 16, 20), (cx, top_y + 10), 8)
        pygame.draw.circle(surface, (72, 64, 76), (cx, top_y + 10), 6)
        pygame.draw.circle(surface, (24, 16, 20), (cx, top_y + 10), 3)

        # 2. Pyramidal Lantern Cap / Roof
        roof_pts = [(cx - 18, top_y + 24), (cx + 18, top_y + 24), (cx + 10, top_y + 14), (cx - 10, top_y + 14)]
        pygame.draw.polygon(surface, (20, 14, 18), [(x, y + 1) for x, y in roof_pts])
        pygame.draw.polygon(surface, (68, 58, 68), roof_pts)
        pygame.draw.polygon(surface, (98, 88, 98), [(cx - 8, top_y + 15), (cx + 8, top_y + 15), (cx + 15, top_y + 23), (cx - 15, top_y + 23)])
        pygame.draw.polygon(surface, (24, 16, 20), roof_pts, 2)

        # 3. Glass Chamber & Glowing Flame
        glass_rect = pygame.Rect(cx - 16, top_y + 24, 32, 30)
        pygame.draw.rect(surface, (24, 16, 20), glass_rect)
        # Glowing amber/yellow glass body
        pygame.draw.rect(surface, (255, 185, 45), glass_rect.inflate(-2, -2))
        # Center white-hot flame
        pygame.draw.rect(surface, (255, 248, 190), pygame.Rect(cx - 6, top_y + 28, 12, 22))
        pygame.draw.rect(surface, (255, 255, 240), pygame.Rect(cx - 3, top_y + 32, 6, 14))

        # Vertical iron bars on lantern
        pygame.draw.line(surface, (36, 28, 36), (cx - 6, top_y + 24), (cx - 6, top_y + 54), 2)
        pygame.draw.line(surface, (36, 28, 36), (cx + 6, top_y + 24), (cx + 6, top_y + 54), 2)
        pygame.draw.rect(surface, (36, 28, 36), glass_rect, width=2)

        # 4. Iron Base Ledge
        base_rect = pygame.Rect(cx - 18, top_y + 54, 36, 7)
        pygame.draw.rect(surface, (20, 14, 18), base_rect.move(0, 1), border_radius=1)
        pygame.draw.rect(surface, (68, 58, 68), base_rect, border_radius=1)
        pygame.draw.rect(surface, (24, 16, 20), base_rect, width=1, border_radius=1)

    def draw(
        self,
        surface: pygame.Surface,
        btn_resume: UIButton,
        btn_restart: UIButton,
        btn_settings: UIButton,
        btn_quit: UIButton,
        level_num: int = 12,
        difficulty_name: str = "TACTICAL",
        anim_time: float = 0.0
    ) -> None:
        """Render the complete retro-pixel RPG pause dialog matching media_1795263510678_20cb89ba.jpg."""
        # 1. Dark Gameplay Dimming Backdrop
        dim_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_surf.fill((10, 8, 12, 175))
        surface.blit(dim_surf, (0, 0))

        cx = self.screen_width // 2

        # Card Dimensions matching mockup exact coordinates (196 to 804, w=472, h=608)
        card_w = min(472, self.screen_width - 32)
        card_h = 608
        card_x = cx - card_w // 2

        if self.screen_height >= 1000:
            card_y = 196
        else:
            card_y = max(16, (self.screen_height - card_h) // 2)

        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # 2. Outer Wooden Frame Drop Shadow
        pygame.draw.rect(surface, (12, 6, 2), card_rect.move(0, 8), border_radius=6)

        # 3. Outer Carved Wood Chassis
        pygame.draw.rect(surface, (88, 48, 20), card_rect, border_radius=6)
        pygame.draw.rect(surface, (115, 66, 30), card_rect.inflate(-4, -4), border_radius=4)
        pygame.draw.rect(surface, (72, 38, 16), card_rect.inflate(-10, -10), border_radius=3)
        pygame.draw.rect(surface, (42, 20, 8), card_rect, width=3, border_radius=6)

        # 4 Corner Wooden Blocks with Golden Rivets
        corner_sz = 26
        for bx, by in [
            (card_rect.left, card_rect.top),
            (card_rect.right - corner_sz, card_rect.top),
            (card_rect.left, card_rect.bottom - corner_sz),
            (card_rect.right - corner_sz, card_rect.bottom - corner_sz)
        ]:
            c_rect = pygame.Rect(bx, by, corner_sz, corner_sz)
            pygame.draw.rect(surface, (98, 54, 24), c_rect, border_radius=3)
            pygame.draw.rect(surface, (42, 20, 8), c_rect, width=2, border_radius=3)
            self.draw_corner_rivet(surface, c_rect.centerx, c_rect.centery, radius=5)

        # 4. Inner Aged Parchment Sheet
        sheet_rect = card_rect.inflate(-36, -36)
        # Drop shadow behind sheet
        pygame.draw.rect(surface, (28, 14, 6), sheet_rect.move(0, 3), border_radius=3)
        # Aged cream paper base
        pygame.draw.rect(surface, (245, 230, 202), sheet_rect, border_radius=3)
        pygame.draw.rect(surface, (236, 218, 180), sheet_rect.inflate(-6, -6), border_radius=2)

        # Torn / distressed edge notches on left and bottom edges matching mockup
        for ny in (sheet_rect.top + 70, sheet_rect.top + 180, sheet_rect.bottom - 75):
            pygame.draw.polygon(surface, (42, 20, 8), [(sheet_rect.left - 1, ny), (sheet_rect.left + 5, ny + 4), (sheet_rect.left - 1, ny + 8)])
        for nx in (sheet_rect.left + 90, sheet_rect.left + 240):
            pygame.draw.polygon(surface, (42, 20, 8), [(nx, sheet_rect.bottom - 1), (nx + 4, sheet_rect.bottom - 5), (nx + 8, sheet_rect.bottom - 1)])

        # Inner dark brown hairline border
        inner_border = sheet_rect.inflate(-18, -18)
        pygame.draw.rect(surface, (92, 50, 20), inner_border, width=2, border_radius=2)

        # 4 Golden Rivets on Parchment Corners
        for rx, ry in [
            (inner_border.left + 5, inner_border.top + 5),
            (inner_border.right - 5, inner_border.top + 5),
            (inner_border.left + 5, inner_border.bottom - 5),
            (inner_border.right - 5, inner_border.bottom - 5)
        ]:
            self.draw_corner_rivet(surface, rx, ry, radius=4)

        # 5. Hanging Dungeon Lantern at Top Center
        self.draw_hanging_lantern(surface, cx, card_rect.top - 10, anim_time)

        # 6. Title: "GAME PAUSED"
        title_y = card_y + 118
        t_text = "GAME PAUSED"
        t_surf_top = self.font_title.render(t_text, True, (255, 188, 48))
        t_surf_bot = self.font_title.render(t_text, True, (212, 122, 22))
        t_surf_sh = self.font_title.render(t_text, True, (36, 16, 4))
        t_rc = t_surf_top.get_rect(center=(cx, title_y))

        # 3D multi-pass outline & drop shadow
        for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-1, 2), (1, 2), (0, 3)]:
            surface.blit(t_surf_sh, t_rc.move(ox, oy))
        half_h = t_rc.height // 2
        surface.blit(t_surf_bot, t_rc)
        top_crop_rect = pygame.Rect(0, 0, t_rc.width, half_h)
        surface.blit(t_surf_top, t_rc, top_crop_rect)

        # 7. Sub-badge / Level Plaque: "LEVEL 12 - TACTICAL"
        plaque_w = 295
        plaque_h = 42
        plaque_y = title_y + 52
        plaque_rect = pygame.Rect(cx - plaque_w // 2, plaque_y, plaque_w, plaque_h)

        # Recessed wood shading
        pygame.draw.rect(surface, (26, 12, 4), plaque_rect.move(0, 2), border_radius=10)
        pygame.draw.rect(surface, (150, 110, 60), plaque_rect, border_radius=10)
        pygame.draw.rect(surface, (178, 134, 78), plaque_rect.inflate(-4, -4), border_radius=8)
        pygame.draw.rect(surface, (48, 24, 8), plaque_rect, width=2, border_radius=10)

        # Plaque text
        level_str = f"LEVEL {level_num} - {difficulty_name.upper()}"
        lvl_txt = self.font_badge.render(level_str, True, (46, 20, 4))
        lvl_txt_hi = self.font_badge.render(level_str, True, (255, 238, 195))
        lvl_rc = lvl_txt.get_rect(center=plaque_rect.center)
        surface.blit(lvl_txt_hi, lvl_rc.move(0, 1))
        surface.blit(lvl_txt, lvl_rc)

        # 8. 4 Stacked Action Buttons matching mockup exact coordinates
        btn_w = 320
        btn_h = 52
        btn_x = cx - btn_w // 2
        start_btn_y = plaque_y + 68
        gap = 18

        # Button 1: RESUME GAME
        btn_resume.rect = pygame.Rect(btn_x, start_btn_y, btn_w, btn_h)
        btn_resume.text = "RESUME GAME"
        btn_resume.style = "green_cta"
        btn_resume.draw(surface)

        # Button 2: RESTART LEVEL [R]
        btn_restart.rect = pygame.Rect(btn_x, start_btn_y + btn_h + gap, btn_w, btn_h)
        btn_restart.text = "RESTART LEVEL [R]"
        btn_restart.style = "blue_pill"
        btn_restart.draw(surface)

        # Button 3: SETTINGS ⚙
        btn_settings.rect = pygame.Rect(btn_x, start_btn_y + (btn_h + gap) * 2, btn_w, btn_h)
        btn_settings.text = "SETTINGS"
        btn_settings.style = "wood_gear_pill"
        btn_settings.draw(surface)

        # Button 4: QUIT TO MENU
        btn_quit.rect = pygame.Rect(btn_x, start_btn_y + (btn_h + gap) * 3, btn_w, btn_h)
        btn_quit.text = "QUIT TO MENU"
        btn_quit.style = "red_pill"
        btn_quit.draw(surface)
