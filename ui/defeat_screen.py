"""
UI Defeat Screen: Retro-pixel RPG Defeat Dialog Overlay.
Matches reference mockup media_1795266586234_bdcc9382.jpg 1:1.

Features:
- Dark semi-transparent gameplay dimming backdrop.
- Carved wood chassis with brass (left) and dark iron (right) corner plates with central dome rivets.
- Aged cream parchment sheet with distressed edge notches.
- Golden-brown inner frame with concave rivet insets & corner scrollwork fleurons.
- Climbing ivy vines with green leaves on outer posts and bottom border.
- Grand arched crimson ceremonial ribbon banner with arched 3D "DEFEAT!".
- Crossed swords badge ("⚔") beneath ribbon dip.
- Terracotta plaque banner with swallowtail ends: "CAPTURED BY HUNTER".
- 4-row structured stats table with horizontal dividing lines & right-aligned values:
  - PLAYER:      Bravo42
  - MODE:        7x7 TACTICAL
  - SURVIVED:    09 STEPS
  - KEY STATUS:  MISSED (or COLLECTED)
- 2 stacked action buttons:
  1. "RETRY LEVEL (R)" (golden amber glow)
  2. "MAIN MENU (ESC)" (warm wood/brown)
"""

import math
from typing import Optional, Tuple, List
import pygame

from .widgets import UIButton


class DefeatScreenRenderer:
    """Renders the retro-pixel RPG adventure defeat dialog overlay."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

        if not pygame.font.get_init():
            pygame.font.init()

        # Cached typography matching mockup aesthetics
        self.font_title_char = pygame.font.SysFont("impact,georgia", 52)
        self.font_plaque = pygame.font.SysFont("trebuchetms,tahoma,arial", 17, bold=True)
        self.font_stat_label = pygame.font.SysFont("trebuchetms,tahoma,arial", 25, bold=True)
        self.font_stat_val = pygame.font.SysFont("trebuchetms,tahoma,arial", 25, bold=True)
        self.font_btn = pygame.font.SysFont("trebuchetms,tahoma,arial", 22, bold=True)

    def draw_metal_plate(self, surface: pygame.Surface, cx: int, cy: int, size: int, is_brass: bool = True) -> None:
        """Render square corner metal plate with 1 central dome rivet and 4 corner studs."""
        rect = pygame.Rect(cx - size // 2, cy - size // 2, size, size)

        if is_brass:
            col_dark = (42, 22, 8)
            col_rim = (128, 82, 38)
            col_face = (182, 128, 62)
            col_hi = (226, 178, 102)
            dome_gold = (246, 196, 68)
            dome_hi = (255, 246, 168)
            dome_sh = (54, 28, 10)
        else:  # Dark steel/iron
            col_dark = (18, 18, 22)
            col_rim = (56, 56, 66)
            col_face = (84, 84, 98)
            col_hi = (128, 128, 144)
            dome_gold = (112, 114, 130)
            dome_hi = (168, 172, 190)
            dome_sh = (28, 28, 36)

        # Drop shadow
        pygame.draw.rect(surface, (14, 8, 4), rect.move(0, 3), border_radius=4)
        # Outer dark perimeter
        pygame.draw.rect(surface, col_dark, rect, border_radius=4)
        # Outer rim
        pygame.draw.rect(surface, col_rim, rect.inflate(-2, -2), border_radius=3)
        # Face
        pygame.draw.rect(surface, col_face, rect.inflate(-6, -6), border_radius=2)
        # Top-left highlight bevel
        pygame.draw.line(surface, col_hi, (rect.left + 3, rect.top + 3), (rect.right - 4, rect.top + 3), 1)
        pygame.draw.line(surface, col_hi, (rect.left + 3, rect.top + 3), (rect.left + 3, rect.bottom - 4), 1)

        # 4 Corner Studs
        stud_inset = 6
        stud_pts = [
            (rect.left + stud_inset, rect.top + stud_inset),
            (rect.right - stud_inset, rect.top + stud_inset),
            (rect.left + stud_inset, rect.bottom - stud_inset),
            (rect.right - stud_inset, rect.bottom - stud_inset),
        ]
        for sx, sy in stud_pts:
            pygame.draw.circle(surface, col_dark, (sx, sy + 1), 2)
            pygame.draw.circle(surface, dome_gold, (sx, sy), 2)
            pygame.draw.circle(surface, dome_hi, (sx - 1, sy - 1), 1)

        # Central Large Dome Rivet
        dome_r = size // 4
        pygame.draw.circle(surface, dome_sh, (cx, cy + 2), dome_r + 1)
        pygame.draw.circle(surface, dome_gold, (cx, cy), dome_r)
        pygame.draw.circle(surface, dome_hi, (cx - 2, cy - 2), max(1, dome_r // 2))

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

    def draw_corner_scroll_fleuron(self, surface: pygame.Surface, cx: int, cy: int, corner: str) -> None:
        """Render small decorative corner scroll fleuron in inner frame."""
        col_vine = (168, 116, 68)
        col_dark = (74, 42, 22)

        dx = 1 if "r" in corner else -1
        dy = 1 if "b" in corner else -1

        pts = [
            (cx, cy + dy * 14),
            (cx + dx * 6, cy + dy * 10),
            (cx + dx * 10, cy + dy * 6),
            (cx + dx * 14, cy),
        ]
        pygame.draw.lines(surface, col_dark, False, [(px, py + 1) for px, py in pts], 3)
        pygame.draw.lines(surface, col_vine, False, pts, 2)
        pygame.draw.circle(surface, col_vine, (cx + dx * 6, cy + dy * 6), 3)

    def draw_inner_border_with_arcs(self, surface: pygame.Surface, rect: pygame.Rect, inset_r: int = 22) -> None:
        """Render inner hairline border with concave corner arcs curving around rivets."""
        col_dark = (74, 42, 22)
        col_line = (182, 136, 88)
        col_hi = (220, 180, 130)

        pygame.draw.line(surface, col_dark, (rect.left + inset_r, rect.top + 1), (rect.right - inset_r, rect.top + 1), 3)
        pygame.draw.line(surface, col_line, (rect.left + inset_r, rect.top), (rect.right - inset_r, rect.top), 2)
        pygame.draw.line(surface, col_hi, (rect.left + inset_r, rect.top - 1), (rect.right - inset_r, rect.top - 1), 1)

        pygame.draw.line(surface, col_dark, (rect.left + inset_r, rect.bottom + 1), (rect.right - inset_r, rect.bottom + 1), 3)
        pygame.draw.line(surface, col_line, (rect.left + inset_r, rect.bottom), (rect.right - inset_r, rect.bottom), 2)

        pygame.draw.line(surface, col_dark, (rect.left + 1, rect.top + inset_r), (rect.left + 1, rect.bottom - inset_r), 3)
        pygame.draw.line(surface, col_line, (rect.left, rect.top + inset_r), (rect.left, rect.bottom - inset_r), 2)

        pygame.draw.line(surface, col_dark, (rect.right + 1, rect.top + inset_r), (rect.right + 1, rect.bottom - inset_r), 3)
        pygame.draw.line(surface, col_line, (rect.right, rect.top + inset_r), (rect.right, rect.bottom - inset_r), 2)

        for cx_c, cy_c, start_ang, end_ang in [
            (rect.left + inset_r, rect.top + inset_r, math.pi, 1.5 * math.pi),
            (rect.right - inset_r, rect.top + inset_r, 1.5 * math.pi, 2 * math.pi),
            (rect.left + inset_r, rect.bottom - inset_r, 0.5 * math.pi, math.pi),
            (rect.right - inset_r, rect.bottom - inset_r, 0, 0.5 * math.pi),
        ]:
            arc_pts = []
            for step in range(8):
                ang = start_ang + (end_ang - start_ang) * (step / 7.0)
                arc_pts.append((cx_c + math.cos(ang) * inset_r, cy_c + math.sin(ang) * inset_r))
            pygame.draw.lines(surface, col_dark, False, [(px, py + 1) for px, py in arc_pts], 3)
            pygame.draw.lines(surface, col_line, False, arc_pts, 2)

    def draw_ribbon_banner(self, surface: pygame.Surface, cx: int, top_y: int, anim_time: float = 0.0) -> None:
        """Render grand arched crimson ceremonial ribbon banner matching crop_defeat_top.png 1:1."""
        banner_w = 470
        banner_h = 100
        bx = cx - banner_w // 2
        by = top_y

        # 1. Left Swallowtail Ribbon End (folded behind)
        lt_poly = [
            (bx - 22, by + 34),
            (bx + 48, by + 28),
            (bx + 48, by + 76),
            (bx - 22, by + 82),
            (bx - 8, by + 58),
        ]
        pygame.draw.polygon(surface, (20, 8, 4), [(x, y + 4) for x, y in lt_poly])
        pygame.draw.polygon(surface, (126, 32, 38), lt_poly)
        pygame.draw.polygon(surface, (42, 14, 18), lt_poly, 2)

        # 2. Right Swallowtail Ribbon End (folded behind)
        rt_poly = [
            (bx + banner_w + 22, by + 34),
            (bx + banner_w - 48, by + 28),
            (bx + banner_w - 48, by + 76),
            (bx + banner_w + 22, by + 82),
            (bx + banner_w + 8, by + 58),
        ]
        pygame.draw.polygon(surface, (20, 8, 4), [(x, y + 4) for x, y in rt_poly])
        pygame.draw.polygon(surface, (126, 32, 38), rt_poly)
        pygame.draw.polygon(surface, (42, 14, 18), rt_poly, 2)

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
            arch_offset = -int(math.sin(t * math.pi) * 20)
            top_curve.append((px, by + 26 + arch_offset))
            bot_curve.append((px, by + 86 + arch_offset))

        ribbon_polygon = top_curve + list(reversed(bot_curve))

        # Ribbon shadow
        pygame.draw.polygon(surface, (24, 10, 6), [(px, py + 5) for px, py in ribbon_polygon])
        # Crimson base fill
        pygame.draw.polygon(surface, (164, 40, 48), ribbon_polygon)
        # Inner highlight sheen on upper half
        sheen_poly = top_curve + [(px, py - 26) for px, py in reversed(bot_curve)]
        pygame.draw.polygon(surface, (196, 58, 66), sheen_poly)
        # Ribbon dark outline
        pygame.draw.polygon(surface, (48, 14, 18), ribbon_polygon, 3)

        # 4. Text "DEFEAT!" arched along the ribbon curve
        title_str = "DEFEAT!"
        num_chars = len(title_str)
        char_surfs = [self.font_title_char.render(ch, True, (238, 154, 142)) for ch in title_str]
        char_surfs_bot = [self.font_title_char.render(ch, True, (196, 92, 84)) for ch in title_str]
        char_surfs_sh = [self.font_title_char.render(ch, True, (46, 12, 16)) for ch in title_str]

        total_txt_w = sum(s.get_width() for s in char_surfs) + (num_chars - 1) * 4
        curr_x = cx - total_txt_w // 2

        for i, ch in enumerate(title_str):
            c_surf = char_surfs[i]
            c_surf_bot = char_surfs_bot[i]
            c_surf_sh = char_surfs_sh[i]
            cw = c_surf.get_width()
            ch_h = c_surf.get_height()

            t = (curr_x + cw // 2 - start_x) / span_w
            t = max(0.0, min(1.0, t))
            arch_offset = -int(math.sin(t * math.pi) * 20)
            cy_char = by + 54 + arch_offset

            char_rect = c_surf.get_rect(center=(curr_x + cw // 2, cy_char))

            # 3D Drop shadow and outline
            for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-1, 2), (1, 2), (0, 3)]:
                surface.blit(c_surf_sh, char_rect.move(ox, oy))

            surface.blit(c_surf_bot, char_rect)
            surface.blit(c_surf, char_rect, pygame.Rect(0, 0, cw, ch_h // 2))

            curr_x += cw + 4

    def draw_crossed_swords(self, surface: pygame.Surface, cx: int, cy: int) -> None:
        """Render two crossed knight swords matching crop_defeat_top.png."""
        col_blade = (212, 220, 232)
        col_blade_sh = (136, 150, 168)
        col_dark = (36, 20, 16)
        col_hilt = (168, 108, 54)
        col_guard = (122, 74, 32)

        for flip in (-1, 1):
            bx, by = cx + flip * 22, cy - 22
            hx, hy = cx - flip * 18, cy + 18

            # Shadow
            pygame.draw.line(surface, col_dark, (hx, hy + 2), (bx, by + 2), 6)

            # Blade
            pygame.draw.line(surface, col_blade_sh, (hx, hy), (bx, by), 5)
            pygame.draw.line(surface, col_blade, (hx, hy), (bx, by), 2)

            # Crossguard perpendicular to blade
            gx, gy = cx - flip * 4, cy + 4
            pdx = -1 * flip
            pdy = -1
            pygame.draw.line(surface, col_dark, (gx - pdx * 9, gy - pdy * 9 + 1), (gx + pdx * 9, gy + pdy * 9 + 1), 6)
            pygame.draw.line(surface, col_guard, (gx - pdx * 8, gy - pdy * 8), (gx + pdx * 8, gy + pdy * 8), 5)
            pygame.draw.line(surface, col_hilt, (gx - pdx * 4, gy - pdy * 4), (gx + pdx * 4, gy + pdy * 4), 2)

            # Pommel
            px_pt, py_pt = cx - flip * 18, cy + 18
            pygame.draw.circle(surface, col_dark, (px_pt, py_pt + 1), 5)
            pygame.draw.circle(surface, col_hilt, (px_pt, py_pt), 4)

    def draw_captured_plaque(self, surface: pygame.Surface, cx: int, cy: int, text: str = "CAPTURED BY HUNTER") -> None:
        """Render terracotta plaque ribbon banner with swallowtail cuts matching crop_defeat_top.png."""
        pw = 400
        ph = 42
        px = cx - pw // 2
        py = cy - ph // 2

        # Plaque swallowtail ends
        tail_w = 24
        left_tail = [(px, py + 4), (px - tail_w, py - 2), (px - tail_w + 8, py + ph // 2), (px - tail_w, py + ph + 2), (px, py + ph - 4)]
        right_tail = [(px + pw, py + 4), (px + pw + tail_w, py - 2), (px + pw + tail_w - 8, py + ph // 2), (px + pw + tail_w, py + ph + 2), (px + pw, py + ph - 4)]

        # Drop shadow
        pygame.draw.polygon(surface, (20, 8, 6), [(x, y + 3) for x, y in left_tail])
        pygame.draw.polygon(surface, (20, 8, 6), [(x, y + 3) for x, y in right_tail])
        pygame.draw.rect(surface, (20, 8, 6), pygame.Rect(px, py + 3, pw, ph), border_radius=4)

        # Swallowtails fill
        pygame.draw.polygon(surface, (132, 64, 52), left_tail)
        pygame.draw.polygon(surface, (48, 20, 16), left_tail, 2)
        pygame.draw.polygon(surface, (132, 64, 52), right_tail)
        pygame.draw.polygon(surface, (48, 20, 16), right_tail, 2)

        # Center Plaque Body
        plaque_rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(surface, (168, 86, 70), plaque_rect, border_radius=4)
        pygame.draw.rect(surface, (198, 114, 98), plaque_rect.inflate(-4, -4), width=1, border_radius=3)
        pygame.draw.rect(surface, (48, 20, 16), plaque_rect, width=2, border_radius=4)

        # Plaque Text: "CAPTURED BY HUNTER"
        txt_s = self.font_plaque.render(text, True, (48, 18, 16))
        txt = self.font_plaque.render(text, True, (24, 10, 10))
        rc = txt.get_rect(center=plaque_rect.center)
        surface.blit(txt_s, rc.move(0, 1))
        surface.blit(txt, rc)

    def draw_action_button(self, surface: pygame.Surface, button: UIButton, style: str) -> None:
        """Render authentic pixel RPG action buttons matching crop_defeat_buttons.png."""
        rect = button.rect

        if style == "amber_glow":
            c_shadow = (28, 14, 4)
            c_dark_rim = (58, 28, 8)
            c_face = (248, 174, 56) if button.is_hovered else (236, 158, 46)
            c_highlight = (255, 226, 116)
            c_inner_line = (204, 128, 32)
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
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (0, 2)]:
            surface.blit(txt_s, rc.move(ox, oy))
        surface.blit(txt, rc)

    def draw(
        self,
        surface: pygame.Surface,
        player_name: str,
        mode_str: str,
        survived_steps: int,
        has_key: bool,
        btn_retry: UIButton,
        btn_menu: UIButton,
        defeat_cause: str = "CAPTURED BY HUNTER",
        anim_time: float = 0.0
    ) -> None:
        """Render the complete retro-pixel RPG defeat dialog matching media_1795266586234_bdcc9382.jpg 1:1."""
        # 1. Dark Gameplay Dimming Backdrop with subtle red tint
        dim_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_surf.fill((14, 8, 10, 185))
        surface.blit(dim_surf, (0, 0))

        cx = self.screen_width // 2

        # Card Dimensions matching mockup exact coordinates
        if self.screen_height >= 1000:
            card_w = min(580, self.screen_width - 32)
            card_h = 810
            card_y = 95
            ribbon_top = card_y + 30
            swords_y = card_y + 135
            plaque_y = card_y + 175
            table_top = card_y + 230
            row_h = 58
            btn_w = 355
            btn_h = 56
            gap = 18
            start_btn_y = card_y + 550
        else:
            card_w = min(500, self.screen_width - 32)
            card_h = min(730, self.screen_height - 30)
            card_y = max(15, (self.screen_height - card_h) // 2)
            ribbon_top = card_y + 20
            swords_y = card_y + 104
            plaque_y = card_y + 140
            table_top = card_y + 185
            row_h = 44
            btn_w = min(340, card_w - 60)
            btn_h = 48
            gap = 14
            start_btn_y = table_top + 4 * row_h + 24

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

        # 4 Heavy Metal Corner Plates: Brass on Left, Dark Iron on Right
        plate_sz = 38
        self.draw_metal_plate(surface, card_rect.left + 16, card_rect.top + 16, plate_sz, is_brass=True)
        self.draw_metal_plate(surface, card_rect.right - 16, card_rect.top + 16, plate_sz, is_brass=False)
        self.draw_metal_plate(surface, card_rect.left + 16, card_rect.bottom - 16, plate_sz, is_brass=True)
        self.draw_metal_plate(surface, card_rect.right - 16, card_rect.bottom - 16, plate_sz, is_brass=False)

        # 4. Climbing Ivy Vines on Outer Wooden Posts
        for vy in (card_rect.top + 60, card_rect.top + 100, card_rect.bottom - 120, card_rect.bottom - 70):
            self.draw_pixel_leaf(surface, card_rect.left + 10, vy, -45, size=9)
            self.draw_pixel_leaf(surface, card_rect.left + 2, vy + 15, -135, size=8)

        for vy in (card_rect.top + 60, card_rect.top + 100, card_rect.bottom - 120, card_rect.bottom - 70):
            self.draw_pixel_leaf(surface, card_rect.right - 10, vy, -135, size=9)
            self.draw_pixel_leaf(surface, card_rect.right - 2, vy + 15, -45, size=8)

        # 5. Inner Aged Parchment Sheet
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

        # 4 Inner Golden Rivets on Parchment Corners
        rivet_inset = 22
        inner_rivets = [
            (sheet_rect.left + rivet_inset, sheet_rect.top + rivet_inset),
            (sheet_rect.right - rivet_inset, sheet_rect.top + rivet_inset),
            (sheet_rect.left + rivet_inset, sheet_rect.bottom - rivet_inset),
            (sheet_rect.right - rivet_inset, sheet_rect.bottom - rivet_inset),
        ]
        for rx, ry in inner_rivets:
            pygame.draw.circle(surface, (48, 22, 8), (rx, ry + 2), 6)
            pygame.draw.circle(surface, (236, 188, 64), (rx, ry), 5)
            pygame.draw.circle(surface, (255, 245, 160), (rx - 1, ry - 1), 2)

        # 6. Inner Border with Concave Arcs around Rivets
        inner_frame_rect = sheet_rect.inflate(-26, -26)
        self.draw_inner_border_with_arcs(surface, inner_frame_rect, inset_r=22)

        # Corner scroll fleurons
        self.draw_corner_scroll_fleuron(surface, inner_frame_rect.left + 22, inner_frame_rect.top + 22, "tl")
        self.draw_corner_scroll_fleuron(surface, inner_frame_rect.right - 22, inner_frame_rect.top + 22, "tr")

        # Bottom horizontal vine
        col_vine = (142, 92, 46)
        bot_y = inner_frame_rect.bottom - 8
        pygame.draw.line(surface, col_vine, (cx - 150, bot_y), (cx + 150, bot_y), 2)
        self.draw_pixel_leaf(surface, cx - 90, bot_y - 4, -45, size=8)
        self.draw_pixel_leaf(surface, cx - 40, bot_y + 2, 35, size=8)
        self.draw_pixel_leaf(surface, cx + 40, bot_y - 4, -135, size=8)
        self.draw_pixel_leaf(surface, cx + 90, bot_y + 2, 145, size=8)

        # 7. Grand Arched Defeat Ribbon Banner
        self.draw_ribbon_banner(surface, cx, ribbon_top, anim_time)

        # 8. Crossed Swords Badge ("⚔")
        self.draw_crossed_swords(surface, cx, swords_y)

        # 9. Plaque Banner: "CAPTURED BY HUNTER"
        self.draw_captured_plaque(surface, cx, plaque_y, defeat_cause)

        # 10. Stats Table matching crop_defeat_stats.png 1:1
        # Rows:
        # PLAYER:     Bravo42
        # MODE:       7x7 TACTICAL
        # SURVIVED:   09 STEPS
        # KEY STATUS: MISSED (or COLLECTED)
        table_w = inner_frame_rect.width - 50
        table_left = cx - table_w // 2
        table_right = table_left + table_w

        key_status_str = "COLLECTED" if has_key else "MISSED"

        stats = [
            ("PLAYER:", player_name),
            ("MODE:", mode_str),
            ("SURVIVED:", f"{survived_steps:02d} STEPS"),
            ("KEY STATUS:", key_status_str)
        ]

        text_color = (48, 18, 12)
        div_color = (206, 168, 126)

        for i, (label, val) in enumerate(stats):
            ry = table_top + i * row_h

            # Label (Left aligned)
            lbl_surf = self.font_stat_label.render(label, True, text_color)
            surface.blit(lbl_surf, (table_left + 16, ry + 8))

            # Value (Right aligned matching crop_defeat_stats.png)
            val_surf = self.font_stat_val.render(val, True, text_color)
            val_x = table_right - val_surf.get_width() - 16
            surface.blit(val_surf, (val_x, ry + 8))

            # Horizontal divider line below each row
            line_y = ry + row_h - 4
            pygame.draw.line(surface, div_color, (table_left + 10, line_y), (table_right - 10, line_y), 2)

        # 11. 2 Stacked Action Buttons matching crop_defeat_buttons.png 1:1
        btn_x = cx - btn_w // 2

        # Button 1: RETRY LEVEL (R) (Warm Golden Amber Glow)
        btn_retry.rect = pygame.Rect(btn_x, start_btn_y, btn_w, btn_h)
        btn_retry.text = "RETRY LEVEL (R)"
        self.draw_action_button(surface, btn_retry, "amber_glow")

        # Button 2: MAIN MENU (ESC) (Dark Roasted Wood Brown)
        btn_menu.rect = pygame.Rect(btn_x, start_btn_y + btn_h + gap, btn_w, btn_h)
        btn_menu.text = "MAIN MENU (ESC)"
        self.draw_action_button(surface, btn_menu, "wood_pill")
