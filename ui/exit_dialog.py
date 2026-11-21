"""
UI Exit Dialog: Retro-pixel RPG Exit Game Confirmation Modal.
Matches reference mockup media_1795269760039_d384587c.jpg 1:1.

Features:
- Dark semi-transparent gameplay / menu dimming backdrop.
- Carved wood chassis with 4 outer dark steel/iron L-brackets & brass dome rivets.
- Top header plaque with animated flickering torch on the left.
- 3D Golden title: "EXIT GAME?".
- Aged cream parchment sheet with distressed edge notches and hairline border.
- Two-line prompt: "ARE YOU SURE YOU" / "WANT TO QUIT?".
- 2 side-by-side action buttons:
  1. "YES, EXIT" (crimson/ruby red button)
  2. "CANCEL" (emerald green button)
"""

import math
from typing import Optional, Tuple
import pygame

from .widgets import UIButton


class ExitDialogRenderer:
    """Renders the retro-pixel RPG adventure exit game confirmation modal."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

        if not pygame.font.get_init():
            pygame.font.init()

        # Cached typography matching mockup aesthetics
        self.font_title = pygame.font.SysFont("impact,georgia", 40)
        self.font_prompt = pygame.font.SysFont("trebuchetms,tahoma,arial", 27, bold=True)
        self.font_btn = pygame.font.SysFont("trebuchetms,tahoma,arial", 21, bold=True)

    def draw_metal_bracket(self, surface: pygame.Surface, x: int, y: int, size: int, corner: str) -> None:
        """Render heavy dark steel L-shaped corner bracket with golden dome rivet."""
        col_dark = (24, 22, 28)
        col_rim = (62, 58, 70)
        col_face = (92, 86, 100)
        col_hi = (138, 132, 146)
        rivet_gold = (236, 186, 62)
        rivet_hi = (255, 242, 160)
        rivet_sh = (44, 22, 10)

        thick = 12
        if corner == "tl":
            pts = [(x, y), (x + size, y), (x + size, y + thick), (x + thick, y + thick), (x + thick, y + size), (x, y + size)]
            r_pt = (x + thick // 2 + 3, y + thick // 2 + 3)
        elif corner == "tr":
            pts = [(x, y), (x - size, y), (x - size, y + thick), (x - thick, y + thick), (x - thick, y + size), (x, y + size)]
            r_pt = (x - thick // 2 - 3, y + thick // 2 + 3)
        elif corner == "bl":
            pts = [(x, y), (x + size, y), (x + size, y - thick), (x + thick, y - thick), (x + thick, y - size), (x, y - size)]
            r_pt = (x + thick // 2 + 3, y - thick // 2 - 3)
        else:  # br
            pts = [(x, y), (x - size, y), (x - size, y - thick), (x - thick, y - thick), (x - thick, y - size), (x, y - size)]
            r_pt = (x - thick // 2 - 3, y - thick // 2 - 3)

        pygame.draw.polygon(surface, col_dark, [(px, py + 1) for px, py in pts])
        pygame.draw.polygon(surface, col_face, pts)
        pygame.draw.polygon(surface, col_rim, pts, 1)
        pygame.draw.line(surface, col_hi, pts[0], pts[1], 1)
        pygame.draw.line(surface, col_hi, pts[0], pts[5], 1)

        # Single corner brass dome rivet with 3D highlight
        rx, ry = r_pt
        pygame.draw.circle(surface, rivet_sh, (rx, ry + 1), 5)
        pygame.draw.circle(surface, rivet_gold, (rx, ry), 4)
        pygame.draw.circle(surface, rivet_hi, (rx - 1, ry - 1), 2)

    def draw_mounted_torch(self, surface: pygame.Surface, cx: int, cy: int, anim_time: float = 0.0) -> None:
        """Render mounted torch with flickering bright campfire flame matching mockup."""
        # Diagonal wood torch handle pointing up-right: from (cx - 22, cy + 22) to (cx + 4, cy - 4)
        col_wood = (104, 58, 28)
        col_wood_hi = (148, 86, 44)
        col_dark = (36, 18, 10)
        col_metal = (68, 62, 72)
        col_metal_hi = (112, 106, 118)

        hx1, hy1 = cx - 24, cy + 24
        hx2, hy2 = cx + 2, cy - 2

        # Torch handle shadow & body
        pygame.draw.line(surface, col_dark, (hx1, hy1 + 2), (hx2, hy2 + 2), 7)
        pygame.draw.line(surface, col_wood, (hx1, hy1), (hx2, hy2), 5)
        pygame.draw.line(surface, col_wood_hi, (hx1 - 1, hy1 - 1), (hx2 - 1, hy2 - 1), 1)

        # Metal torch cup/bracket at top of handle
        cup_rect = pygame.Rect(hx2 - 7, hy2 - 7, 14, 12)
        pygame.draw.rect(surface, col_dark, cup_rect.move(0, 1), border_radius=2)
        pygame.draw.rect(surface, col_metal, cup_rect, border_radius=2)
        pygame.draw.rect(surface, col_metal_hi, cup_rect, width=1, border_radius=2)

        # Animated flickering flame above cup
        flame_cx = hx2
        flame_cy = hy2 - 14

        # Wave offsets for dynamic flickering
        flicker1 = math.sin(anim_time * 12.0) * 1.5
        flicker2 = math.cos(anim_time * 18.0) * 1.2

        # 1. Outer flame (Crimson / Orange)
        outer_pts = [
            (flame_cx, flame_cy - 18 + flicker1),
            (flame_cx + 10 + flicker2, flame_cy - 6),
            (flame_cx + 8, flame_cy + 4),
            (flame_cx - 8, flame_cy + 4),
            (flame_cx - 10 - flicker2, flame_cy - 6),
        ]
        pygame.draw.polygon(surface, (238, 76, 22), outer_pts)

        # 2. Middle flame (Golden Amber)
        mid_pts = [
            (flame_cx, flame_cy - 14 + flicker2),
            (flame_cx + 6 + flicker1, flame_cy - 4),
            (flame_cx + 5, flame_cy + 3),
            (flame_cx - 5, flame_cy + 3),
            (flame_cx - 6 - flicker1, flame_cy - 4),
        ]
        pygame.draw.polygon(surface, (255, 178, 32), mid_pts)

        # 3. Inner core (Bright Yellow/White)
        core_pts = [
            (flame_cx, flame_cy - 8 + flicker1 * 0.5),
            (flame_cx + 3, flame_cy - 1),
            (flame_cx + 3, flame_cy + 2),
            (flame_cx - 3, flame_cy + 2),
            (flame_cx - 3, flame_cy - 1),
        ]
        pygame.draw.polygon(surface, (255, 248, 168), core_pts)

        # Sparks / embers floating upward
        spark_y1 = (flame_cy - 22 - int(anim_time * 30) % 24)
        spark_y2 = (flame_cy - 20 - int(anim_time * 40 + 10) % 24)
        pygame.draw.circle(surface, (255, 196, 48), (int(flame_cx - 4 + flicker1), spark_y1), 1)
        pygame.draw.circle(surface, (255, 160, 32), (int(flame_cx + 5 + flicker2), spark_y2), 1)

    def draw_action_button(self, surface: pygame.Surface, button: UIButton, style: str) -> None:
        """Render authentic pixel RPG action button matching crop_exit_buttons.png."""
        rect = button.rect

        if style == "red_exit":
            c_shadow = (24, 10, 12)
            c_dark_rim = (58, 20, 24)
            c_face = (176, 52, 60) if button.is_hovered else (160, 44, 52)
            c_highlight = (220, 102, 110)
            c_inner_line = (142, 34, 42)
            text_sh = (36, 12, 16)
        else:  # green_cancel
            c_shadow = (12, 28, 18)
            c_dark_rim = (18, 64, 34)
            c_face = (42, 158, 90) if button.is_hovered else (36, 142, 80)
            c_highlight = (92, 212, 138)
            c_inner_line = (28, 122, 68)
            text_sh = (10, 42, 22)

        # 1. Drop shadow
        pygame.draw.rect(surface, c_shadow, rect.move(0, 4), border_radius=10)
        # 2. Outer dark rim
        pygame.draw.rect(surface, c_dark_rim, rect, border_radius=10)
        # 3. Main face
        pygame.draw.rect(surface, c_face, rect.inflate(-4, -4), border_radius=8)
        # 4. Top highlight sheen border
        pygame.draw.rect(surface, c_highlight, rect.inflate(-6, -6), width=2, border_radius=7)
        # 5. Inner subtle groove
        pygame.draw.rect(surface, c_inner_line, rect.inflate(-10, -10), width=1, border_radius=5)
        # 6. Dark perimeter outline
        pygame.draw.rect(surface, (18, 10, 6), rect, width=2, border_radius=10)

        # Button Text
        txt_s = self.font_btn.render(button.text, True, text_sh)
        txt = self.font_btn.render(button.text, True, (255, 255, 255))
        rc = txt.get_rect(center=rect.center)
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (0, 2)]:
            surface.blit(txt_s, rc.move(ox, oy))
        surface.blit(txt, rc)

    def draw(
        self,
        surface: pygame.Surface,
        btn_exit_confirm: UIButton,
        btn_exit_cancel: UIButton,
        anim_time: float = 0.0
    ) -> None:
        """Render the complete retro-pixel RPG exit confirmation modal matching reference mockup."""
        # 1. Dark Gameplay / Menu Dimming Backdrop
        dim_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_surf.fill((10, 8, 12, 185))
        surface.blit(dim_surf, (0, 0))

        cx = self.screen_width // 2

        # Card Dimensions matching mockup exact coordinates (w=564, h=388)
        card_w = min(564, self.screen_width - 32)
        card_h = 388

        if self.screen_height >= 1000:
            card_y = 318
        else:
            card_y = max(16, (self.screen_height - card_h) // 2)

        card_x = cx - card_w // 2
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # 2. Outer Wooden Frame Drop Shadow
        pygame.draw.rect(surface, (12, 6, 2), card_rect.move(0, 8), border_radius=8)

        # 3. Outer Carved Wood Chassis
        pygame.draw.rect(surface, (94, 52, 24), card_rect, border_radius=8)
        pygame.draw.rect(surface, (122, 70, 32), card_rect.inflate(-4, -4), border_radius=6)
        pygame.draw.rect(surface, (78, 42, 18), card_rect.inflate(-10, -10), border_radius=5)
        pygame.draw.rect(surface, (44, 22, 10), card_rect, width=3, border_radius=8)

        # 4. Top Wooden Header Plaque Bar
        header_h = 82
        header_rect = pygame.Rect(card_x, card_y, card_w, header_h)
        pygame.draw.rect(surface, (132, 78, 38), header_rect.inflate(-8, -8), border_radius=5)
        pygame.draw.rect(surface, (158, 98, 48), header_rect.inflate(-12, -12), border_radius=4)
        pygame.draw.rect(surface, (88, 48, 22), header_rect.inflate(-16, -16), border_radius=3)
        pygame.draw.rect(surface, (44, 22, 10), header_rect, width=3, border_radius=8)
        # Separator line between header and parchment
        pygame.draw.line(surface, (44, 22, 10), (card_x, card_y + header_h), (card_x + card_w, card_y + header_h), 3)

        # 5. Mounted Torch on the Left of Header
        torch_cx = card_x + 58
        torch_cy = card_y + 44
        self.draw_mounted_torch(surface, torch_cx, torch_cy, anim_time)

        # 6. Header Title: "EXIT GAME?"
        txt_title = self.font_title.render("EXIT GAME?", True, (255, 218, 70))
        txt_title_bot = self.font_title.render("EXIT GAME?", True, (236, 148, 32))
        txt_title_sh = self.font_title.render("EXIT GAME?", True, (48, 16, 6))

        title_rc = txt_title.get_rect(center=(cx + 8, card_y + 43))
        # Bold 3D shadow and outline
        for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-1, 2), (1, 2), (0, 3)]:
            surface.blit(txt_title_sh, title_rc.move(ox, oy))
        surface.blit(txt_title_bot, title_rc)
        surface.blit(txt_title, title_rc, pygame.Rect(0, 0, title_rc.width, title_rc.height // 2))

        # 7. Inner Aged Parchment Sheet
        parch_rect = pygame.Rect(card_x + 6, card_y + header_h + 1, card_w - 12, card_h - header_h - 7)
        # Drop shadow behind sheet
        pygame.draw.rect(surface, (28, 14, 6), parch_rect.move(0, 2), border_radius=3)
        # Aged cream paper base
        pygame.draw.rect(surface, (244, 228, 198), parch_rect, border_radius=3)
        pygame.draw.rect(surface, (238, 220, 184), parch_rect.inflate(-6, -6), border_radius=2)

        # Distressed edge notches on left and right edges
        for ny in (parch_rect.top + 50, parch_rect.top + 130, parch_rect.bottom - 40):
            pygame.draw.polygon(surface, (44, 22, 10), [(parch_rect.left - 1, ny), (parch_rect.left + 5, ny + 4), (parch_rect.left - 1, ny + 8)])
        for ny in (parch_rect.top + 70, parch_rect.bottom - 60):
            pygame.draw.polygon(surface, (44, 22, 10), [(parch_rect.right + 1, ny), (parch_rect.right - 5, ny + 4), (parch_rect.right + 1, ny + 8)])

        # Inner brown hairline border
        inner_border = parch_rect.inflate(-16, -16)
        pygame.draw.rect(surface, (132, 88, 52), inner_border, width=2, border_radius=2)

        # 8. 4 Steel/Iron Corner Metal Brackets on Card Frame
        bracket_sz = 34
        self.draw_metal_bracket(surface, card_rect.left, card_rect.top, bracket_sz, "tl")
        self.draw_metal_bracket(surface, card_rect.right, card_rect.top, bracket_sz, "tr")
        self.draw_metal_bracket(surface, card_rect.left, card_rect.bottom, bracket_sz, "bl")
        self.draw_metal_bracket(surface, card_rect.right, card_rect.bottom, bracket_sz, "br")

        # 9. Prompt Text inside Parchment
        prompt_line1 = "ARE YOU SURE YOU"
        prompt_line2 = "WANT TO QUIT?"

        p1_surf = self.font_prompt.render(prompt_line1, True, (42, 18, 12))
        p2_surf = self.font_prompt.render(prompt_line2, True, (42, 18, 12))

        prompt_cy = (parch_rect.top + card_rect.bottom - 78) // 2
        p1_rc = p1_surf.get_rect(center=(cx, prompt_cy - 18))
        p2_rc = p2_surf.get_rect(center=(cx, prompt_cy + 18))

        surface.blit(p1_surf, p1_rc)
        surface.blit(p2_surf, p2_rc)

        # 10. 2 Action Buttons Side-by-Side matching crop_exit_buttons.png
        btn_w = 200
        btn_h = 52
        btn_gap = 22
        total_w = btn_w * 2 + btn_gap
        start_x = cx - total_w // 2
        btn_y = card_rect.bottom - 78

        # Left Button: YES, EXIT (Red)
        btn_exit_confirm.rect = pygame.Rect(start_x, btn_y, btn_w, btn_h)
        btn_exit_confirm.text = "YES, EXIT"
        self.draw_action_button(surface, btn_exit_confirm, "red_exit")

        # Right Button: CANCEL (Green)
        btn_exit_cancel.rect = pygame.Rect(start_x + btn_w + btn_gap, btn_y, btn_w, btn_h)
        btn_exit_cancel.text = "CANCEL"
        self.draw_action_button(surface, btn_exit_cancel, "green_cancel")
