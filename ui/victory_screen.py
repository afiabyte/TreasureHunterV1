"""
UI Victory Screen: Retro-pixel RPG Victory Dialog Overlay.
Matches reference mockup media_1795264782719_5811a7f1.jpg 1:1.

Features:
- Dark semi-transparent gameplay dimming backdrop.
- Carved wood chassis with 4 outer golden brass corner brackets & rivets.
- Aged cream parchment sheet with distressed edge notches.
- Golden-brown inner frame with ornate scrolled corner loops & climbing ivy vines with bright green leaves.
- Grand arched crimson/ruby red ceremonial ribbon banner with gold trim and arched 3D "VICTORY!".
- Golden 5-pointed star badge with red ribbon loop and bold "NEW" / "RECORD!".
- 4-row structured stats table with horizontal dividing lines:
  - PLAYER: Bravo42
  - MODE:   7x7 TACTICAL
  - STEPS:  12
  - BEST:   12
- 3 stacked action buttons:
  1. "NEXT LEVEL" (emerald green)
  2. "PLAY AGAIN [R]" (slate blue)
  3. "MAIN MENU [ESC]" (warm wood/brown)
"""

import math
from typing import Optional, Tuple, List
import pygame

from .widgets import UIButton


class VictoryScreenRenderer:
    """Renders the retro-pixel RPG adventure victory dialog overlay."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

        if not pygame.font.get_init():
            pygame.font.init()

        # Cached typography matching mockup aesthetics
        self.font_title = pygame.font.SysFont("impact,georgia", 44)
        self.font_title_char = pygame.font.SysFont("impact,georgia", 46)
        self.font_star = pygame.font.SysFont("trebuchetms,tahoma,arial", 13, bold=True)
        self.font_stat_label = pygame.font.SysFont("trebuchetms,tahoma,arial", 25, bold=True)
        self.font_stat_val = pygame.font.SysFont("trebuchetms,tahoma,arial", 25, bold=True)
        self.font_btn = pygame.font.SysFont("trebuchetms,tahoma,arial", 21, bold=True)

    def draw_brass_bracket(self, surface: pygame.Surface, x: int, y: int, size: int, corner: str) -> None:
        """Render heavy carved brass metal corner bracket with golden dome rivets."""
        bracket_col = (130, 80, 36)
        bracket_hi = (195, 140, 68)
        bracket_dark = (50, 24, 8)
        rivet_gold = (245, 195, 55)
        rivet_hi = (255, 245, 160)
        rivet_sh = (40, 18, 4)

        thick = 11
        if corner == "tl":
            pts = [(x, y), (x + size, y), (x + size, y + thick), (x + thick, y + thick), (x + thick, y + size), (x, y + size)]
            r1 = (x + size - 8, y + thick // 2)
            r2 = (x + thick // 2, y + size - 8)
        elif corner == "tr":
            pts = [(x, y), (x - size, y), (x - size, y + thick), (x - thick, y + thick), (x - thick, y + size), (x, y + size)]
            r1 = (x - size + 8, y + thick // 2)
            r2 = (x - thick // 2, y + size - 8)
        elif corner == "bl":
            pts = [(x, y), (x + size, y), (x + size, y - thick), (x + thick, y - thick), (x + thick, y - size), (x, y - size)]
            r1 = (x + size - 8, y - thick // 2)
            r2 = (x + thick // 2, y - size + 8)
        else:  # br
            pts = [(x, y), (x - size, y), (x - size, y - thick), (x - thick, y - thick), (x - thick, y - size), (x, y - size)]
            r1 = (x - size + 8, y - thick // 2)
            r2 = (x - thick // 2, y - size + 8)

        pygame.draw.polygon(surface, bracket_dark, [(px, py + 1) for px, py in pts])
        pygame.draw.polygon(surface, bracket_col, pts)
        pygame.draw.polygon(surface, bracket_hi, pts, 1)

        # Draw the 2 brass dome rivets
        for rx, ry in (r1, r2):
            pygame.draw.circle(surface, rivet_sh, (rx, ry + 1), 4)
            pygame.draw.circle(surface, rivet_gold, (rx, ry), 3)
            pygame.draw.circle(surface, rivet_hi, (rx - 1, ry - 1), 1)

    def draw_pixel_leaf(self, surface: pygame.Surface, x: int, y: int, angle_deg: float, size: int = 10) -> None:
        """Render a crisp retro-pixel leaf with dark outline, emerald body, and light highlight."""
        rad = math.radians(angle_deg)
        dx = math.cos(rad) * size
        dy = math.sin(rad) * size
        pdx = -math.sin(rad) * (size * 0.55)
        pdy = math.cos(rad) * (size * 0.55)

        tip = (x + dx, y + dy)
        base = (x - dx * 0.4, y - dy * 0.4)
        side1 = (x + pdx, y + pdy)
        side2 = (x - pdx, y - pdy)
        pts = [tip, side1, base, side2]

        dark_outline = (28, 54, 18)
        leaf_emerald = (62, 134, 40)
        leaf_hi = (118, 192, 68)

        pygame.draw.polygon(surface, dark_outline, pts)
        pygame.draw.polygon(surface, leaf_emerald, [(px * 0.75 + x * 0.25, py * 0.75 + y * 0.25) for px, py in pts])
        pygame.draw.line(surface, leaf_hi, (x, y), tip, 1)

    def draw_corner_scrollwork(self, surface: pygame.Surface, frame_rect: pygame.Rect) -> None:
        """Render ornate scrollwork corner loops and climbing ivy vines matching crop_mockup_corner_bl.png."""
        col_vine = (168, 116, 68)
        col_dark = (74, 42, 22)
        col_hi = (216, 166, 114)

        # 1. Inner Golden-Brown Frame Border
        pygame.draw.rect(surface, col_dark, frame_rect.inflate(2, 2), width=1)
        pygame.draw.rect(surface, col_vine, frame_rect, width=2)
        pygame.draw.rect(surface, col_hi, frame_rect.inflate(-2, -2), width=1)

        # 2. Bottom-Left Corner Filigree & Loops
        bl_x = frame_rect.left
        bl_y = frame_rect.bottom

        # Detailed nested spirals in corner matching crop
        corner_spirals_bl = [
            (bl_x + 16, bl_y - 16, 14),
            (bl_x + 16, bl_y - 16, 8),
            (bl_x + 36, bl_y - 10, 11),
            (bl_x + 36, bl_y - 10, 6),
            (bl_x + 10, bl_y - 36, 11),
            (bl_x + 10, bl_y - 36, 6),
            (bl_x + 58, bl_y - 8, 9),
            (bl_x + 8, bl_y - 58, 9),
        ]
        for cx_s, cy_s, r in corner_spirals_bl:
            pygame.draw.circle(surface, col_dark, (cx_s, cy_s + 1), r, 2)
            pygame.draw.circle(surface, col_vine, (cx_s, cy_s), r, 2)
            pygame.draw.circle(surface, col_hi, (cx_s - 1, cy_s - 1), max(1, r - 2), 1)

        # Stalk crawling up left border
        left_vine_pts = [
            (bl_x + 8, bl_y - 58),
            (bl_x + 14, bl_y - 92),
            (bl_x + 6, bl_y - 128),
            (bl_x + 12, bl_y - 164),
            (bl_x + 7, bl_y - 200),
        ]
        pygame.draw.lines(surface, col_dark, False, [(px, py + 1) for px, py in left_vine_pts], 3)
        pygame.draw.lines(surface, col_vine, False, left_vine_pts, 2)

        # Leaves on Left Vine (pairs pointing outward and inward)
        self.draw_pixel_leaf(surface, bl_x + 16, bl_y - 75, -40, size=10)
        self.draw_pixel_leaf(surface, bl_x + 4, bl_y - 110, -140, size=10)
        self.draw_pixel_leaf(surface, bl_x + 16, bl_y - 146, -35, size=10)
        self.draw_pixel_leaf(surface, bl_x + 4, bl_y - 182, -145, size=9)

        # Stalk running across bottom border
        bot_vine_pts = [
            (bl_x + 58, bl_y - 8),
            (bl_x + 94, bl_y - 12),
            (bl_x + 130, bl_y - 6),
            (bl_x + 166, bl_y - 10),
        ]
        pygame.draw.lines(surface, col_dark, False, [(px, py + 1) for px, py in bot_vine_pts], 3)
        pygame.draw.lines(surface, col_vine, False, bot_vine_pts, 2)

        self.draw_pixel_leaf(surface, bl_x + 78, bl_y - 14, -80, size=9)
        self.draw_pixel_leaf(surface, bl_x + 112, bl_y - 4, 30, size=9)
        self.draw_pixel_leaf(surface, bl_x + 148, bl_y - 14, -85, size=9)

        # 3. Bottom-Right Corner Filigree & Loops
        br_x = frame_rect.right
        br_y = frame_rect.bottom

        corner_spirals_br = [
            (br_x - 16, br_y - 16, 14),
            (br_x - 16, br_y - 16, 8),
            (br_x - 36, br_y - 10, 11),
            (br_x - 36, br_y - 10, 6),
            (br_x - 10, br_y - 36, 11),
            (br_x - 10, br_y - 36, 6),
            (br_x - 58, br_y - 8, 9),
            (br_x - 8, br_y - 58, 9),
        ]
        for cx_s, cy_s, r in corner_spirals_br:
            pygame.draw.circle(surface, col_dark, (cx_s, cy_s + 1), r, 2)
            pygame.draw.circle(surface, col_vine, (cx_s, cy_s), r, 2)
            pygame.draw.circle(surface, col_hi, (cx_s - 1, cy_s - 1), max(1, r - 2), 1)

        right_vine_pts = [
            (br_x - 8, br_y - 58),
            (br_x - 14, br_y - 92),
            (br_x - 6, br_y - 128),
            (br_x - 12, br_y - 164),
            (br_x - 7, br_y - 200),
        ]
        pygame.draw.lines(surface, col_dark, False, [(px, py + 1) for px, py in right_vine_pts], 3)
        pygame.draw.lines(surface, col_vine, False, right_vine_pts, 2)

        self.draw_pixel_leaf(surface, br_x - 16, br_y - 75, -140, size=10)
        self.draw_pixel_leaf(surface, br_x - 4, br_y - 110, -40, size=10)
        self.draw_pixel_leaf(surface, br_x - 16, br_y - 146, -145, size=10)
        self.draw_pixel_leaf(surface, br_x - 4, br_y - 182, -35, size=9)

        bot_r_pts = [
            (br_x - 58, br_y - 8),
            (br_x - 94, br_y - 12),
            (br_x - 130, br_y - 6),
            (br_x - 166, br_y - 10),
        ]
        pygame.draw.lines(surface, col_dark, False, [(px, py + 1) for px, py in bot_r_pts], 3)
        pygame.draw.lines(surface, col_vine, False, bot_r_pts, 2)

        self.draw_pixel_leaf(surface, br_x - 78, br_y - 14, -100, size=9)
        self.draw_pixel_leaf(surface, br_x - 112, br_y - 4, 150, size=9)
        self.draw_pixel_leaf(surface, br_x - 148, br_y - 14, -95, size=9)

        # 4. Top-Left & Top-Right Ornate Corner Brackets matching crop_mockup_top.png
        tl_x = frame_rect.left
        tl_y = frame_rect.top
        for cx_pt, cy_pt in [(tl_x + 18, tl_y + 18), (frame_rect.right - 18, tl_y + 18)]:
            pygame.draw.circle(surface, col_dark, (cx_pt, cy_pt + 1), 14, 2)
            pygame.draw.circle(surface, col_vine, (cx_pt, cy_pt), 14, 2)
            pygame.draw.circle(surface, col_hi, (cx_pt, cy_pt), 9, 1)
            pygame.draw.circle(surface, col_dark, (cx_pt, cy_pt), 4)

    def draw_ribbon_banner(self, surface: pygame.Surface, cx: int, top_y: int, anim_time: float = 0.0) -> None:
        """Render grand arched crimson ceremonial ribbon banner matching crop_mockup_top.png 1:1."""
        banner_w = 440
        banner_h = 84
        bx = cx - banner_w // 2
        by = top_y

        # Under-ribbon leafy branches flanking left and right
        col_vine = (124, 82, 44)
        pygame.draw.line(surface, col_vine, (cx - 90, by + 70), (cx - 170, by + 76), 3)
        self.draw_pixel_leaf(surface, cx - 120, by + 72, -60, size=10)
        self.draw_pixel_leaf(surface, cx - 150, by + 74, -120, size=10)

        pygame.draw.line(surface, col_vine, (cx + 90, by + 70), (cx + 170, by + 76), 3)
        self.draw_pixel_leaf(surface, cx + 120, by + 72, -120, size=10)
        self.draw_pixel_leaf(surface, cx + 150, by + 74, -60, size=10)

        # 1. Left Swallowtail Ribbon End (folded behind)
        lt_poly = [
            (bx - 18, by + 28),
            (bx + 42, by + 22),
            (bx + 42, by + 66),
            (bx - 18, by + 72),
            (bx - 4, by + 50),
        ]
        pygame.draw.polygon(surface, (20, 8, 4), [(x, y + 4) for x, y in lt_poly])
        pygame.draw.polygon(surface, (116, 22, 28), lt_poly)
        pygame.draw.polygon(surface, (246, 192, 54), lt_poly, 2)

        # 2. Right Swallowtail Ribbon End (folded behind)
        rt_poly = [
            (bx + banner_w + 18, by + 28),
            (bx + banner_w - 42, by + 22),
            (bx + banner_w - 42, by + 66),
            (bx + banner_w + 18, by + 72),
            (bx + banner_w + 4, by + 50),
        ]
        pygame.draw.polygon(surface, (20, 8, 4), [(x, y + 4) for x, y in rt_poly])
        pygame.draw.polygon(surface, (116, 22, 28), rt_poly)
        pygame.draw.polygon(surface, (246, 192, 54), rt_poly, 2)

        # 3. Main Arched Center Ribbon Body
        top_curve = []
        bot_curve = []
        steps = 28
        span_w = banner_w - 56
        start_x = cx - span_w // 2

        for i in range(steps + 1):
            t = i / steps
            px = start_x + t * span_w
            # Parabolic upward arch: peak at center (t=0.5)
            arch_offset = -int(math.sin(t * math.pi) * 18)
            top_curve.append((px, by + 24 + arch_offset))
            bot_curve.append((px, by + 74 + arch_offset))

        ribbon_polygon = top_curve + list(reversed(bot_curve))

        # Ribbon shadow
        pygame.draw.polygon(surface, (24, 10, 6), [(px, py + 5) for px, py in ribbon_polygon])
        # Crimson base fill
        pygame.draw.polygon(surface, (168, 34, 44), ribbon_polygon)
        # Inner highlight sheen on upper half
        sheen_poly = top_curve + [(px, py - 20) for px, py in reversed(bot_curve)]
        pygame.draw.polygon(surface, (198, 44, 56), sheen_poly)
        # Ribbon dark outline
        pygame.draw.polygon(surface, (48, 14, 18), ribbon_polygon, 3)

        # Golden embroidered trim running along top and bottom curves
        pygame.draw.lines(surface, (246, 195, 54), False, top_curve, 3)
        pygame.draw.lines(surface, (255, 245, 160), False, top_curve, 1)

        pygame.draw.lines(surface, (246, 195, 54), False, bot_curve, 3)
        pygame.draw.lines(surface, (255, 245, 160), False, bot_curve, 1)

        # 4. Text "VICTORY!" arched along the ribbon curve
        title_str = "VICTORY!"
        num_chars = len(title_str)
        char_surfs = [self.font_title_char.render(ch, True, (255, 215, 65)) for ch in title_str]
        char_surfs_bot = [self.font_title_char.render(ch, True, (225, 140, 25)) for ch in title_str]
        char_surfs_sh = [self.font_title_char.render(ch, True, (48, 12, 6)) for ch in title_str]

        total_txt_w = sum(s.get_width() for s in char_surfs) + (num_chars - 1) * 3
        curr_x = cx - total_txt_w // 2

        for i, ch in enumerate(title_str):
            c_surf = char_surfs[i]
            c_surf_bot = char_surfs_bot[i]
            c_surf_sh = char_surfs_sh[i]
            cw = c_surf.get_width()
            ch_h = c_surf.get_height()

            t = (curr_x + cw // 2 - start_x) / span_w
            t = max(0.0, min(1.0, t))
            arch_offset = -int(math.sin(t * math.pi) * 18)
            cy_char = by + 47 + arch_offset

            char_rect = c_surf.get_rect(center=(curr_x + cw // 2, cy_char))

            # 3D Drop shadow and outline
            for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-1, 2), (1, 2), (0, 3)]:
                surface.blit(c_surf_sh, char_rect.move(ox, oy))

            # Dual-tone golden face
            surface.blit(c_surf_bot, char_rect)
            surface.blit(c_surf, char_rect, pygame.Rect(0, 0, cw, ch_h // 2))

            curr_x += cw + 3

    def draw_record_star(self, surface: pygame.Surface, cx: int, cy: int, is_new_record: bool = True) -> None:
        """Render golden 5-pointed star badge with red ribbon loop & 'NEW RECORD!'."""
        # Red ribbon hanger loop behind star top
        loop_poly = [(cx - 10, cy - 28), (cx + 10, cy - 28), (cx + 6, cy - 12), (cx - 6, cy - 12)]
        pygame.draw.polygon(surface, (140, 26, 32), loop_poly)
        pygame.draw.polygon(surface, (246, 192, 54), loop_poly, 1)

        r_outer = 32
        r_inner = 15
        star_pts = []
        for i in range(10):
            r = r_outer if i % 2 == 0 else r_inner
            ang = math.radians(-90 + i * 36)
            star_pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))

        # Star drop shadow
        pygame.draw.polygon(surface, (28, 12, 4), [(px, py + 3) for px, py in star_pts])
        # Star golden face
        pygame.draw.polygon(surface, (255, 205, 45), star_pts)
        # Inner golden facet highlight
        pygame.draw.polygon(surface, (255, 238, 130), [(px * 0.72 + cx * 0.28, py * 0.72 + cy * 0.28) for px, py in star_pts])
        # Dark contour
        pygame.draw.polygon(surface, (54, 24, 6), star_pts, 2)

        # Text inside star: "NEW RECORD!"
        t1 = self.font_star.render("NEW", True, (48, 16, 4))
        t2 = self.font_star.render("RECORD!", True, (48, 16, 4))
        r1 = t1.get_rect(center=(cx, cy - 6))
        r2 = t2.get_rect(center=(cx, cy + 8))
        surface.blit(t1, r1)
        surface.blit(t2, r2)

    def draw_action_button(self, surface: pygame.Surface, button: UIButton, style: str) -> None:
        """Render authentic pixel RPG action buttons matching crop_mockup_buttons.png."""
        rect = button.rect

        if style == "green_cta":
            c_shadow = (14, 38, 20)
            c_dark_rim = (22, 68, 36)
            c_face = (42, 172, 92) if button.is_hovered else (34, 152, 80)
            c_highlight = (82, 218, 132)
            c_inner_line = (28, 134, 68)
        elif style == "blue_pill":
            c_shadow = (16, 24, 34)
            c_dark_rim = (32, 50, 68)
            c_face = (82, 114, 142) if button.is_hovered else (70, 100, 126)
            c_highlight = (126, 164, 196)
            c_inner_line = (54, 80, 104)
        else:  # wood_pill
            c_shadow = (28, 14, 6)
            c_dark_rim = (62, 34, 14)
            c_face = (148, 86, 38) if button.is_hovered else (132, 74, 30)
            c_highlight = (194, 130, 68)
            c_inner_line = (104, 56, 22)

        # 1. Bottom drop shadow
        pygame.draw.rect(surface, c_shadow, rect.move(0, 4), border_radius=12)
        # 2. Outer dark rim
        pygame.draw.rect(surface, c_dark_rim, rect, border_radius=12)
        # 3. Main button face
        pygame.draw.rect(surface, c_face, rect.inflate(-4, -4), border_radius=10)
        # 4. Top highlight sheen border
        pygame.draw.rect(surface, c_highlight, rect.inflate(-6, -6), width=2, border_radius=8)
        # 5. Inner subtle groove
        pygame.draw.rect(surface, c_inner_line, rect.inflate(-10, -10), width=1, border_radius=6)
        # 6. Dark perimeter outline
        pygame.draw.rect(surface, (18, 10, 6), rect, width=2, border_radius=12)

        # Button Text
        txt_s = self.font_btn.render(button.text, True, (24, 12, 6))
        txt = self.font_btn.render(button.text, True, (255, 255, 255))
        rc = txt.get_rect(center=rect.center)
        # Multi-pass outline for high contrast retro typography
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (0, 2)]:
            surface.blit(txt_s, rc.move(ox, oy))
        surface.blit(txt, rc)

    def draw(
        self,
        surface: pygame.Surface,
        player_name: str,
        mode_str: str,
        steps: int,
        best_steps: int,
        is_new_record: bool,
        btn_next_level: UIButton,
        btn_play_again: UIButton,
        btn_menu: UIButton,
        anim_time: float = 0.0
    ) -> None:
        """Render the complete retro-pixel RPG victory dialog matching media_1795264782719_5811a7f1.jpg 1:1."""
        # 1. Dark Gameplay Dimming Backdrop
        dim_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_surf.fill((10, 8, 14, 185))
        surface.blit(dim_surf, (0, 0))

        cx = self.screen_width // 2

        # Card Dimensions matching mockup exact coordinates
        if self.screen_height >= 1000:
            card_w = min(578, self.screen_width - 32)
            card_h = 790
            card_y = 100
            ribbon_top = card_y + 35
            star_y = card_y + 140
            table_top = card_y + 205
            row_h = 55
            btn_w = 320
            btn_h = 56
            gap = 18
            start_btn_y = card_y + 495
        else:
            card_w = min(500, self.screen_width - 32)
            card_h = min(730, self.screen_height - 30)
            card_y = max(15, (self.screen_height - card_h) // 2)
            ribbon_top = card_y + 24
            star_y = card_y + 105
            table_top = card_y + 155
            row_h = 42
            btn_w = min(320, card_w - 60)
            btn_h = 48
            gap = 12
            start_btn_y = table_top + 4 * row_h + 20

        card_x = cx - card_w // 2
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # 2. Outer Wooden Frame Drop Shadow
        pygame.draw.rect(surface, (12, 6, 2), card_rect.move(0, 8), border_radius=6)

        # 3. Outer Carved Wood Chassis
        pygame.draw.rect(surface, (94, 52, 24), card_rect, border_radius=6)
        pygame.draw.rect(surface, (122, 70, 32), card_rect.inflate(-4, -4), border_radius=4)
        pygame.draw.rect(surface, (78, 42, 18), card_rect.inflate(-10, -10), border_radius=3)
        pygame.draw.rect(surface, (44, 22, 10), card_rect, width=3, border_radius=6)

        # Vertical wood grain lines
        for gx in range(card_rect.left + 8, card_rect.right - 8, 16):
            pygame.draw.line(surface, (78, 42, 18), (gx, card_rect.top + 4), (gx, card_rect.bottom - 4), 1)

        # 4 Heavy Brass Corner Metal Brackets with 2 Rivets each
        bracket_sz = 36
        self.draw_brass_bracket(surface, card_rect.left, card_rect.top, bracket_sz, "tl")
        self.draw_brass_bracket(surface, card_rect.right, card_rect.top, bracket_sz, "tr")
        self.draw_brass_bracket(surface, card_rect.left, card_rect.bottom, bracket_sz, "bl")
        self.draw_brass_bracket(surface, card_rect.right, card_rect.bottom, bracket_sz, "br")

        # 4. Inner Aged Parchment Sheet
        sheet_rect = card_rect.inflate(-40, -40)
        # Drop shadow behind sheet
        pygame.draw.rect(surface, (28, 14, 6), sheet_rect.move(0, 3), border_radius=3)
        # Aged cream paper base
        pygame.draw.rect(surface, (244, 228, 198), sheet_rect, border_radius=3)
        pygame.draw.rect(surface, (238, 220, 184), sheet_rect.inflate(-8, -8), border_radius=2)

        # Torn / distressed edge notches on left and right edges
        for ny in (sheet_rect.top + 90, sheet_rect.top + 240, sheet_rect.bottom - 110):
            pygame.draw.polygon(surface, (44, 22, 10), [(sheet_rect.left - 1, ny), (sheet_rect.left + 5, ny + 4), (sheet_rect.left - 1, ny + 8)])
        for ny in (sheet_rect.top + 140, sheet_rect.bottom - 160):
            pygame.draw.polygon(surface, (44, 22, 10), [(sheet_rect.right + 1, ny), (sheet_rect.right - 5, ny + 4), (sheet_rect.right + 1, ny + 8)])

        # 5. Golden-Brown Inner Frame with Ornate Scrolled Corner Loops & Climbing Ivy Vines
        inner_frame_rect = sheet_rect.inflate(-26, -26)
        self.draw_corner_scrollwork(surface, inner_frame_rect)

        # 6. Grand Arched Victory Ribbon Banner
        self.draw_ribbon_banner(surface, cx, ribbon_top, anim_time)

        # 7. Golden Star Badge with "NEW RECORD!"
        self.draw_record_star(surface, cx, star_y, is_new_record)

        # 8. Stats Table matching crop_mockup_stats.png 1:1
        # Rows:
        # PLAYER: Bravo42
        # MODE:   7x7 TACTICAL
        # STEPS:  12
        # BEST:   12
        table_w = inner_frame_rect.width - 50
        table_left = cx - table_w // 2

        stats = [
            ("PLAYER:", player_name),
            ("MODE:", mode_str),
            ("STEPS:", f"{steps:02d}"),
            ("BEST:", f"{best_steps:02d}")
        ]

        text_color = (66, 18, 0)
        div_color = (206, 168, 126)

        for i, (label, val) in enumerate(stats):
            ry = table_top + i * row_h

            # Label (Left aligned)
            lbl_surf = self.font_stat_label.render(label, True, text_color)
            surface.blit(lbl_surf, (table_left + 16, ry + 8))

            # Value (Left aligned with offset)
            val_x = table_left + 175
            val_surf = self.font_stat_val.render(val, True, text_color)
            surface.blit(val_surf, (val_x, ry + 8))

            # Horizontal divider line below each row
            line_y = ry + row_h - 4
            pygame.draw.line(surface, div_color, (table_left + 10, line_y), (table_left + table_w - 10, line_y), 2)

        # 9. 3 Stacked Action Buttons matching crop_mockup_buttons.png 1:1
        btn_x = cx - btn_w // 2

        # Button 1: NEXT LEVEL (Emerald Green)
        btn_next_level.rect = pygame.Rect(btn_x, start_btn_y, btn_w, btn_h)
        btn_next_level.text = "NEXT LEVEL"
        self.draw_action_button(surface, btn_next_level, "green_cta")

        # Button 2: PLAY AGAIN [R] (Slate Blue)
        btn_play_again.rect = pygame.Rect(btn_x, start_btn_y + btn_h + gap, btn_w, btn_h)
        btn_play_again.text = "PLAY AGAIN [R]"
        self.draw_action_button(surface, btn_play_again, "blue_pill")

        # Button 3: MAIN MENU [ESC] (Warm Wood/Brown)
        btn_menu.rect = pygame.Rect(btn_x, start_btn_y + (btn_h + gap) * 2, btn_w, btn_h)
        btn_menu.text = "MAIN MENU [ESC]"
        self.draw_action_button(surface, btn_menu, "wood_pill")
