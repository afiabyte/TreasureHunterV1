"""
UI How to Play Screen: Authentic retro-pixel RPG adventure mission guide.
Renders aged parchment scroll with rustic timber frame, dark iron corner brackets,
and three recessed wooden panels:
1. OBJECTIVE: Start hero, Hunter assassin, Golden Key, Exit Door with flow arrows.
2. CONTROLS: Stone keyboard keycaps (WASD, Arrows, B, R, H, ESC) and actions.
3. TACTICS: Glowing Green Path Dots, Golden Compass Arrow, Crimson Hunter Sight Cone.
"""

import math
from typing import Optional
import pygame

from .art_helpers import draw_dungeon_background
from .widgets import UIButton


class HowToPlayScreenRenderer:
    """Renders the authentic retro-pixel RPG adventure How To Play screen."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

    def _draw_iron_corner_bracket(self, surface: pygame.Surface, x: int, y: int, corner: str) -> None:
        """Render heavy dark iron corner bracket with metallic bevel and rivets."""
        size = 36
        thickness = 13
        col_face = (52, 48, 50)
        col_bevel = (78, 72, 76)
        col_border = (20, 16, 18)

        if corner == "TL":
            rect1 = pygame.Rect(x, y, size, thickness)
            rect2 = pygame.Rect(x, y, thickness, size)
            rivets = [(x + 8, y + 8), (x + 25, y + 6), (x + 6, y + 25)]
        elif corner == "TR":
            rect1 = pygame.Rect(x - size, y, size, thickness)
            rect2 = pygame.Rect(x - thickness, y, thickness, size)
            rivets = [(x - 8, y + 8), (x - 25, y + 6), (x - 6, y + 25)]
        elif corner == "BL":
            rect1 = pygame.Rect(x, y - thickness, size, thickness)
            rect2 = pygame.Rect(x, y - size, thickness, size)
            rivets = [(x + 8, y - 8), (x + 25, y - 6), (x + 6, y - 25)]
        else:  # "BR"
            rect1 = pygame.Rect(x - size, y - thickness, size, thickness)
            rect2 = pygame.Rect(x - thickness, y - size, thickness, size)
            rivets = [(x - 8, y - 8), (x - 25, y - 6), (x - 6, y - 25)]

        pygame.draw.rect(surface, col_face, rect1)
        pygame.draw.rect(surface, col_face, rect2)
        pygame.draw.rect(surface, col_bevel, rect1.inflate(-2, -2))
        pygame.draw.rect(surface, col_bevel, rect2.inflate(-2, -2))
        pygame.draw.rect(surface, col_border, rect1, width=2)
        pygame.draw.rect(surface, col_border, rect2, width=2)

        for rx, ry in rivets:
            pygame.draw.circle(surface, (20, 16, 18), (rx, ry + 1), 4)
            pygame.draw.circle(surface, (175, 180, 190), (rx, ry), 3)
            pygame.draw.circle(surface, (240, 245, 255), (rx - 1, ry - 1), 1)

    def _draw_parchment_chassis(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render parchment chassis with carved timber border and dark iron corners."""
        # 1. Drop Shadow
        pygame.draw.rect(surface, (10, 6, 6), rect.move(0, 8), border_radius=8)

        # 2. Outer Wood Timber Frame
        pygame.draw.rect(surface, (76, 42, 20), rect, border_radius=8)
        pygame.draw.rect(surface, (108, 60, 28), rect.inflate(-4, -4), border_radius=6)
        pygame.draw.rect(surface, (54, 28, 12), rect.inflate(-8, -8), border_radius=5)

        # Wood grain lines
        for fy in [rect.top + 5, rect.bottom - 6]:
            pygame.draw.line(surface, (42, 20, 8), (rect.left + 50, fy), (rect.right - 50, fy), 1)
        for fx in [rect.left + 5, rect.right - 6]:
            pygame.draw.line(surface, (42, 20, 8), (fx, rect.top + 50), (fx, rect.bottom - 50), 1)

        # 3. Parchment Paper Sheet
        paper_rect = rect.inflate(-24, -24)
        pygame.draw.rect(surface, (226, 192, 138), paper_rect, border_radius=4)
        pygame.draw.rect(surface, (244, 218, 168), paper_rect.inflate(-8, -8), border_radius=4)
        pygame.draw.rect(surface, (195, 158, 105), paper_rect.inflate(-16, -16), width=1, border_radius=3)

        # 4. 4 Heavy Iron Corner Brackets
        self._draw_iron_corner_bracket(surface, rect.left, rect.top, "TL")
        self._draw_iron_corner_bracket(surface, rect.right, rect.top, "TR")
        self._draw_iron_corner_bracket(surface, rect.left, rect.bottom, "BL")
        self._draw_iron_corner_bracket(surface, rect.right, rect.bottom, "BR")

    def _draw_sub_panel(self, surface: pygame.Surface, rect: pygame.Rect, title: str, font_badge: pygame.font.Font) -> None:
        """Render recessed dark wooden container panel with 4 corner rivets and header capsule."""
        pygame.draw.rect(surface, (115, 85, 52), rect.move(0, 3), border_radius=8)

        # Recessed wood background
        pygame.draw.rect(surface, (120, 68, 34), rect, border_radius=8)
        # Inner drop shadow
        pygame.draw.line(surface, (58, 30, 14), (rect.left + 3, rect.top + 3), (rect.right - 3, rect.top + 3), 3)
        pygame.draw.line(surface, (58, 30, 14), (rect.left + 3, rect.top + 3), (rect.left + 3, rect.bottom - 3), 3)
        # Inner bottom highlight
        pygame.draw.line(surface, (148, 88, 46), (rect.left + 3, rect.bottom - 2), (rect.right - 3, rect.bottom - 2), 2)
        pygame.draw.line(surface, (148, 88, 46), (rect.right - 2, rect.top + 3), (rect.right - 2, rect.bottom - 2), 2)

        # Dark chocolate outer border
        pygame.draw.rect(surface, (44, 20, 8), rect, width=3, border_radius=8)

        # 4 Metal Corner Screws / Rivets
        for rx, ry in [
            (rect.left + 10, rect.top + 10),
            (rect.right - 10, rect.top + 10),
            (rect.left + 10, rect.bottom - 10),
            (rect.right - 10, rect.bottom - 10)
        ]:
            pygame.draw.circle(surface, (36, 18, 8), (rx, ry + 1), 3)
            pygame.draw.circle(surface, (155, 160, 170), (rx, ry), 2)
            pygame.draw.circle(surface, (235, 240, 250), (rx - 1, ry - 1), 1)

        # Top Center Header Pill
        pill_w = 164
        pill_h = 32
        pill_rect = pygame.Rect(rect.centerx - pill_w // 2, rect.top - pill_h // 2, pill_w, pill_h)

        pygame.draw.rect(surface, (44, 20, 8), pill_rect.move(0, 2), border_radius=8)
        pygame.draw.rect(surface, (40, 16, 6), pill_rect, border_radius=8)
        pygame.draw.rect(surface, (138, 78, 32), pill_rect, width=3, border_radius=8)
        pygame.draw.rect(surface, (244, 182, 48), pill_rect.inflate(-4, -4), width=1, border_radius=6)

        t_surf = font_badge.render(title, True, (255, 242, 215))
        t_shadow = font_badge.render(title, True, (22, 6, 2))
        rc = t_surf.get_rect(center=pill_rect.center)
        surface.blit(t_shadow, rc.move(0, 1))
        surface.blit(t_surf, rc)

    def _draw_flow_arrow(self, surface: pygame.Surface, cx: int, cy: int) -> None:
        """Render chunky pixel arrow pointing right."""
        col_fill = (244, 218, 168)
        col_border = (48, 24, 10)
        col_shadow = (34, 16, 6)

        pts = [
            (cx - 10, cy - 3),
            (cx + 2, cy - 3),
            (cx + 2, cy - 8),
            (cx + 12, cy),
            (cx + 2, cy + 8),
            (cx + 2, cy + 3),
            (cx - 10, cy + 3),
        ]
        s_pts = [(px, py + 2) for px, py in pts]
        pygame.draw.polygon(surface, col_shadow, s_pts)
        pygame.draw.polygon(surface, col_fill, pts)
        pygame.draw.polygon(surface, col_border, pts, 2)

    def _draw_keycap(self, surface: pygame.Surface, x: int, y: int, w: int, h: int, text: str, font: Optional[pygame.font.Font], text_color: tuple = (48, 24, 10)) -> None:
        """Render authentic stone keyboard keycap with drop shadow and carved label."""
        rect = pygame.Rect(x, y, w, h)

        # Shadow
        pygame.draw.rect(surface, (44, 22, 8), rect.move(0, 3), border_radius=6)
        # Face
        pygame.draw.rect(surface, (224, 214, 198), rect, border_radius=6)
        # Top bevel highlight
        pygame.draw.rect(surface, (245, 238, 226), (rect.x + 2, rect.y + 2, rect.width - 4, rect.height // 2), border_top_left_radius=5, border_top_right_radius=5)
        # Bottom bevel shade
        pygame.draw.rect(surface, (182, 168, 152), (rect.x + 2, rect.bottom - 4, rect.width - 4, 3), border_bottom_left_radius=4, border_bottom_right_radius=4)
        # Border
        pygame.draw.rect(surface, (44, 22, 8), rect, width=2, border_radius=6)

        # Text
        if font and text:
            txt = font.render(text, True, text_color)
            surface.blit(txt, txt.get_rect(center=rect.center))

    def _draw_arrow_keycap(self, surface: pygame.Surface, x: int, y: int, w: int, h: int, direction: str) -> None:
        """Render stone arrow keycap with crisp dark triangle."""
        self._draw_keycap(surface, x, y, w, h, "", None)
        cx = x + w // 2
        cy = y + h // 2
        col = (48, 24, 10)

        if direction == "UP":
            pts = [(cx, cy - 6), (cx + 6, cy + 5), (cx - 6, cy + 5)]
        elif direction == "DOWN":
            pts = [(cx, cy + 6), (cx + 6, cy - 5), (cx - 6, cy - 5)]
        elif direction == "LEFT":
            pts = [(cx - 6, cy), (cx + 5, cy - 6), (cx + 5, cy + 6)]
        else:  # "RIGHT"
            pts = [(cx + 6, cy), (cx - 5, cy - 6), (cx - 5, cy + 6)]

        pygame.draw.polygon(surface, col, pts)

    def _draw_objective_items(self, surface: pygame.Surface, panel_rect: pygame.Rect, font_label: pygame.font.Font, anim_time: float) -> None:
        """Render the 4 objective flow steps: Start, Hunter, Key, Exit."""
        cy = panel_rect.centery - 4
        c1 = panel_rect.left + 65
        c2 = panel_rect.left + 175
        c3 = panel_rect.left + 300
        c4 = panel_rect.left + 425

        # Flow arrows between items
        self._draw_flow_arrow(surface, (c1 + c2) // 2 + 3, cy)
        self._draw_flow_arrow(surface, (c2 + c3) // 2 - 3, cy)
        self._draw_flow_arrow(surface, (c3 + c4) // 2 - 5, cy)

        # -------------------------------------------------------------
        # 1. START HERO
        # -------------------------------------------------------------
        tile_w, tile_h = 52, 26
        t_rect1 = pygame.Rect(c1 - tile_w // 2, cy + 4, tile_w, tile_h)
        pygame.draw.rect(surface, (20, 68, 28), t_rect1.move(0, 3), border_radius=6)
        pygame.draw.rect(surface, (68, 168, 76), t_rect1, border_radius=6)
        pygame.draw.rect(surface, (115, 215, 125), t_rect1.inflate(-4, -4), border_radius=4)
        pygame.draw.rect(surface, (20, 68, 28), t_rect1, width=2, border_radius=6)

        s_badge = pygame.Rect(c1 - 10, cy + 11, 20, 18)
        pygame.draw.rect(surface, (18, 56, 24), s_badge.move(0, 1), border_radius=3)
        pygame.draw.rect(surface, (46, 204, 113), s_badge, border_radius=3)
        pygame.draw.rect(surface, (16, 48, 20), s_badge, width=1, border_radius=3)
        s_txt = font_label.render("S", True, (255, 255, 255))
        surface.blit(s_txt, s_txt.get_rect(center=s_badge.center))

        hx = c1
        hy = cy - 14
        pygame.draw.ellipse(surface, (28, 14, 6, 150), (hx - 11, hy + 13, 22, 8))
        # Boots
        pygame.draw.rect(surface, (64, 34, 16), (hx - 7, hy + 8, 6, 9), border_radius=2)
        pygame.draw.rect(surface, (64, 34, 16), (hx + 1, hy + 8, 6, 9), border_radius=2)
        # Blue tunic & explorer vest
        pygame.draw.rect(surface, (54, 136, 160), (hx - 8, hy - 4, 16, 14), border_radius=3)
        pygame.draw.rect(surface, (148, 86, 40), (hx - 7, hy - 3, 14, 12), border_radius=2)
        pygame.draw.line(surface, (44, 22, 8), (hx - 7, hy + 7), (hx + 7, hy + 7), 2)
        pygame.draw.circle(surface, (244, 186, 42), (hx, hy + 7), 2)
        # Head / skin
        pygame.draw.circle(surface, (245, 198, 162), (hx, hy - 12), 7)
        pygame.draw.rect(surface, (48, 24, 12), (hx - 4, hy - 13, 2, 2))
        pygame.draw.rect(surface, (48, 24, 12), (hx + 2, hy - 13, 2, 2))
        pygame.draw.circle(surface, (105, 58, 26), (hx - 1, hy - 14), 7)
        # Fedora
        pygame.draw.rect(surface, (88, 48, 20), (hx - 11, hy - 15, 22, 4), border_radius=2)
        pygame.draw.rect(surface, (120, 68, 32), (hx - 7, hy - 20, 14, 6), border_radius=2)

        lbl1 = font_label.render("START", True, (48, 24, 10))
        surface.blit(lbl1, lbl1.get_rect(center=(c1, panel_rect.bottom - 15)))

        # -------------------------------------------------------------
        # 2. HUNTER ASSASSIN
        # -------------------------------------------------------------
        t_rect2 = pygame.Rect(c2 - tile_w // 2, cy + 4, tile_w, tile_h)
        pygame.draw.rect(surface, (88, 14, 22), t_rect2.move(0, 3), border_radius=6)
        pygame.draw.rect(surface, (205, 42, 54), t_rect2, border_radius=6)
        pygame.draw.rect(surface, (245, 96, 108), t_rect2.inflate(-4, -4), border_radius=4)
        pygame.draw.rect(surface, (88, 14, 22), t_rect2, width=2, border_radius=6)

        h_badge = pygame.Rect(c2 - 10, cy + 11, 20, 18)
        pygame.draw.rect(surface, (68, 10, 16), h_badge.move(0, 1), border_radius=3)
        pygame.draw.rect(surface, (231, 76, 60), h_badge, border_radius=3)
        pygame.draw.rect(surface, (50, 8, 12), h_badge, width=1, border_radius=3)
        h_txt = font_label.render("H", True, (255, 255, 255))
        surface.blit(h_txt, h_txt.get_rect(center=h_badge.center))

        ux = c2
        uy = cy - 14
        pygame.draw.ellipse(surface, (28, 14, 6, 150), (ux - 11, uy + 13, 22, 8))
        pygame.draw.rect(surface, (36, 32, 40), (ux - 7, uy + 7, 14, 10), border_radius=2)
        c_pts = [(ux - 10, uy - 4), (ux + 10, uy - 4), (ux + 13, uy + 14), (ux - 13, uy + 14)]
        pygame.draw.polygon(surface, (185, 30, 42), c_pts)
        pygame.draw.polygon(surface, (108, 14, 22), c_pts, 1)
        pygame.draw.circle(surface, (185, 30, 42), (ux, uy - 12), 8)
        pygame.draw.rect(surface, (220, 225, 235), (ux - 5, uy - 13, 10, 6), border_radius=2)
        pygame.draw.circle(surface, (255, 30, 50), (ux - 2, uy - 10), 1)
        pygame.draw.circle(surface, (255, 30, 50), (ux + 2, uy - 10), 1)
        pygame.draw.line(surface, (78, 48, 24), (ux + 10, uy - 20), (ux + 10, uy + 16), 2)
        pygame.draw.circle(surface, (180, 185, 195), (ux + 10, uy - 20), 3)

        lbl2 = font_label.render("HUNTER", True, (48, 24, 10))
        surface.blit(lbl2, lbl2.get_rect(center=(c2, panel_rect.bottom - 15)))

        # -------------------------------------------------------------
        # 3. GOLDEN CIPHER KEY
        # -------------------------------------------------------------
        kx = c3
        ky = cy - 9
        sparkle_phase = anim_time * 6.0
        for i in range(8):
            ang = i * (math.pi / 4.0) + sparkle_phase * 0.4
            dist = 18 + 3 * math.sin(sparkle_phase + i)
            sx = kx + math.cos(ang) * dist
            sy = ky + math.sin(ang) * dist
            r_sp = 2 if i % 2 == 0 else 1
            pygame.draw.circle(surface, (255, 235, 120), (int(sx), int(sy)), r_sp)

        k_angle = math.radians(-38)
        cos_k, sin_k = math.cos(k_angle), math.sin(k_angle)
        ring_cx = kx + cos_k * 11
        ring_cy = ky + sin_k * 11
        pygame.draw.circle(surface, (115, 68, 10), (int(ring_cx), int(ring_cy + 1)), 9)
        pygame.draw.circle(surface, (255, 215, 45), (int(ring_cx), int(ring_cy)), 8)
        pygame.draw.circle(surface, (255, 245, 175), (int(ring_cx), int(ring_cy)), 6)
        pygame.draw.circle(surface, (115, 68, 10), (int(ring_cx), int(ring_cy)), 3)

        s_end_x = kx - cos_k * 14
        s_end_y = ky - sin_k * 14
        pygame.draw.line(surface, (115, 68, 10), (ring_cx, ring_cy + 1), (s_end_x, s_end_y + 1), 4)
        pygame.draw.line(surface, (255, 215, 45), (ring_cx, ring_cy), (s_end_x, s_end_y), 3)
        pygame.draw.line(surface, (255, 250, 195), (ring_cx, ring_cy - 1), (s_end_x, s_end_y - 1), 1)
        pygame.draw.line(surface, (255, 215, 45), (s_end_x, s_end_y), (s_end_x - 3, s_end_y + 6), 2)
        pygame.draw.line(surface, (255, 215, 45), (s_end_x + 5, s_end_y), (s_end_x + 2, s_end_y + 5), 2)

        k_badge = pygame.Rect(c3 - 10, cy + 11, 20, 18)
        pygame.draw.rect(surface, (96, 48, 8), k_badge.move(0, 1), border_radius=3)
        pygame.draw.rect(surface, (250, 185, 42), k_badge, border_radius=3)
        pygame.draw.rect(surface, (78, 36, 6), k_badge, width=1, border_radius=3)
        k_txt = font_label.render("K", True, (48, 22, 6))
        surface.blit(k_txt, k_txt.get_rect(center=k_badge.center))

        lbl3 = font_label.render("KEY", True, (48, 24, 10))
        surface.blit(lbl3, lbl3.get_rect(center=(c3, panel_rect.bottom - 15)))

        # -------------------------------------------------------------
        # 4. EXIT PORTAL DOORWAY
        # -------------------------------------------------------------
        ex = c4
        ey = cy - 9
        t_rect4 = pygame.Rect(ex - tile_w // 2, cy + 4, tile_w, tile_h)
        pygame.draw.rect(surface, (50, 44, 40), t_rect4.move(0, 3), border_radius=6)
        pygame.draw.rect(surface, (148, 142, 138), t_rect4, border_radius=6)
        pygame.draw.rect(surface, (185, 178, 172), t_rect4.inflate(-4, -4), border_radius=4)
        pygame.draw.rect(surface, (44, 38, 34), t_rect4, width=2, border_radius=6)

        e_badge = pygame.Rect(ex - 10, cy + 11, 20, 18)
        pygame.draw.rect(surface, (44, 38, 34), e_badge.move(0, 1), border_radius=3)
        pygame.draw.rect(surface, (200, 194, 188), e_badge, border_radius=3)
        pygame.draw.rect(surface, (32, 28, 24), e_badge, width=1, border_radius=3)
        e_txt = font_label.render("E", True, (48, 42, 38))
        surface.blit(e_txt, e_txt.get_rect(center=e_badge.center))

        arch_rect = pygame.Rect(ex - 16, ey - 22, 32, 40)
        pygame.draw.rect(surface, (42, 26, 16), arch_rect, border_top_left_radius=16, border_top_right_radius=16)
        inner_cavity = pygame.Rect(ex - 13, ey - 19, 26, 37)
        pygame.draw.rect(surface, (246, 218, 162), inner_cavity, border_top_left_radius=13, border_top_right_radius=13)

        door_poly = [
            (ex - 12, ey - 16),
            (ex + 4, ey - 14),
            (ex + 4, ey + 18),
            (ex - 12, ey + 18),
        ]
        pygame.draw.polygon(surface, (160, 94, 42), door_poly)
        pygame.draw.polygon(surface, (185, 116, 56), door_poly, 1)
        pygame.draw.line(surface, (48, 28, 14), (ex - 11, ey - 7), (ex - 2, ey - 6), 2)
        pygame.draw.line(surface, (48, 28, 14), (ex - 11, ey + 10), (ex - 2, ey + 11), 2)
        pygame.draw.circle(surface, (250, 196, 45), (ex + 1, ey + 3), 2)
        pygame.draw.rect(surface, (72, 42, 20), arch_rect, width=2, border_top_left_radius=16, border_top_right_radius=16)

        lbl4 = font_label.render("EXIT", True, (48, 24, 10))
        surface.blit(lbl4, lbl4.get_rect(center=(c4, panel_rect.bottom - 15)))

    def _draw_controls_panel(self, surface: pygame.Surface, panel_rect: pygame.Rect, font_key: pygame.font.Font, font_label: pygame.font.Font) -> None:
        """Render stone keycaps and descriptions matching the mockup layout."""
        kw, kh = 34, 34
        gap = 8

        # -------------------------------------------------------------
        # Row 1: [W] [A] [S] [D] : MOVE       [H] SPAWN HUNTER
        # -------------------------------------------------------------
        r1_y = panel_rect.top + 28
        x_w = panel_rect.left + 26
        x_a = x_w + kw + gap
        x_s = x_a + kw + gap
        x_d = x_s + kw + gap

        self._draw_keycap(surface, x_w, r1_y, kw, kh, "W", font_key)
        self._draw_keycap(surface, x_a, r1_y, kw, kh, "A", font_key)
        self._draw_keycap(surface, x_s, r1_y, kw, kh, "S", font_key)
        self._draw_keycap(surface, x_d, r1_y, kw, kh, "D", font_key, text_color=(120, 100, 85))

        lbl_mv1 = font_label.render(": MOVE", True, (48, 24, 10))
        surface.blit(lbl_mv1, (x_d + kw + 10, r1_y + 8))

        # Right side: [H] SPAWN HUNTER (aligned with ESC below)
        x_h = panel_rect.left + 332
        self._draw_keycap(surface, x_h, r1_y, kw, kh, "H", font_key)
        lbl_h1 = font_label.render("SPAWN", True, (48, 24, 10))
        lbl_h2 = font_label.render("HUNTER", True, (48, 24, 10))
        surface.blit(lbl_h1, (x_h + kw + 10, r1_y - 1))
        surface.blit(lbl_h2, (x_h + kw + 10, r1_y + 17))

        # -------------------------------------------------------------
        # Row 2: [▲] [◄] [▼] [►] MOVE
        # -------------------------------------------------------------
        r2_y = r1_y + kh + 14
        self._draw_arrow_keycap(surface, x_w, r2_y, kw, kh, "UP")
        self._draw_arrow_keycap(surface, x_a, r2_y, kw, kh, "LEFT")
        self._draw_arrow_keycap(surface, x_s, r2_y, kw, kh, "DOWN")
        self._draw_arrow_keycap(surface, x_d, r2_y, kw, kh, "RIGHT")

        lbl_mv2 = font_label.render("MOVE", True, (48, 24, 10))
        surface.blit(lbl_mv2, (x_d + kw + 16, r2_y + 8))

        # -------------------------------------------------------------
        # Row 3: [B] SHIFT WALLS    [R] RESET    [ESC] MENU
        # -------------------------------------------------------------
        r3_y = r2_y + kh + 14
        self._draw_keycap(surface, x_w, r3_y, kw, kh, "B", font_key)
        lbl_b1 = font_label.render("SHIFT", True, (48, 24, 10))
        lbl_b2 = font_label.render("WALLS", True, (48, 24, 10))
        surface.blit(lbl_b1, (x_w + kw + 10, r3_y - 1))
        surface.blit(lbl_b2, (x_w + kw + 10, r3_y + 17))

        # [R] RESET
        x_r = panel_rect.left + 192
        self._draw_keycap(surface, x_r, r3_y, kw, kh, "R", font_key)
        lbl_rst = font_label.render("RESET", True, (48, 24, 10))
        surface.blit(lbl_rst, (x_r + kw + 10, r3_y + 8))

        # [ESC] MENU (aligned with H above)
        x_esc = panel_rect.left + 332
        esc_w = 56
        self._draw_keycap(surface, x_esc, r3_y, esc_w, kh, "ESC", font_key)
        lbl_menu = font_label.render("MENU", True, (48, 24, 10))
        surface.blit(lbl_menu, (x_esc + esc_w + 10, r3_y + 8))

    def _draw_tactics_panel(self, surface: pygame.Surface, panel_rect: pygame.Rect, font_label: pygame.font.Font, anim_time: float) -> None:
        """Render the 3 tactics guidance columns: Green Dots, Compass Arrow, Hunter Sight Cone."""
        c1 = panel_rect.left + 80
        c2 = panel_rect.left + 248
        c3 = panel_rect.left + 414
        vis_y = panel_rect.top + 44

        # -------------------------------------------------------------
        # Column 1: GREEN PATH DOTS
        # -------------------------------------------------------------
        pts_wave = [
            (c1 - 42, vis_y + 10),
            (c1 - 30, vis_y + 3),
            (c1 - 18, vis_y - 8),
            (c1 - 6, vis_y - 3),
            (c1 + 6, vis_y + 7),
            (c1 + 18, vis_y + 12),
            (c1 + 30, vis_y + 4),
            (c1 + 42, vis_y - 6),
        ]
        pulse = 0.85 + 0.15 * math.sin(anim_time * 6.0)
        for dx, dy in pts_wave:
            r_glow = int(6 * pulse)
            pygame.draw.circle(surface, (36, 168, 82), (int(dx), int(dy)), r_glow)
            pygame.draw.circle(surface, (72, 245, 138), (int(dx), int(dy)), max(2, int(4 * pulse)))
            pygame.draw.circle(surface, (230, 255, 240), (int(dx), int(dy)), 2)

        lbl_gp1 = font_label.render("GREEN PATH", True, (48, 24, 10))
        lbl_gp2 = font_label.render("DOTS", True, (48, 24, 10))
        surface.blit(lbl_gp1, lbl_gp1.get_rect(center=(c1, panel_rect.bottom - 28)))
        surface.blit(lbl_gp2, lbl_gp2.get_rect(center=(c1, panel_rect.bottom - 12)))

        # -------------------------------------------------------------
        # Column 2: COMPASS ARROW
        # -------------------------------------------------------------
        ax = c2
        ay = vis_y + 2
        p_bracket = 1.0 + 0.12 * math.sin(anim_time * 5.0)
        b_rad = int(24 * p_bracket)
        b_rect = pygame.Rect(ax - b_rad, ay - b_rad, b_rad * 2, b_rad * 2)
        pygame.draw.arc(surface, (246, 186, 42), b_rect, 0.4, 1.8, 3)
        pygame.draw.arc(surface, (246, 186, 42), b_rect, 3.5, 5.0, 3)

        arr_pts = [
            (ax + 14, ay - 14),
            (ax - 12, ay - 4),
            (ax - 2, ay + 2),
            (ax + 4, ay + 12),
        ]
        pygame.draw.polygon(surface, (68, 38, 10), [(px, py + 2) for px, py in arr_pts])
        pygame.draw.polygon(surface, (252, 214, 54), arr_pts)
        pygame.draw.polygon(surface, (255, 248, 180), [arr_pts[0], arr_pts[1], arr_pts[2]])
        pygame.draw.polygon(surface, (48, 24, 8), arr_pts, 2)

        lbl_cp1 = font_label.render("COMPASS", True, (48, 24, 10))
        lbl_cp2 = font_label.render("ARROW", True, (48, 24, 10))
        surface.blit(lbl_cp1, lbl_cp1.get_rect(center=(c2, panel_rect.bottom - 28)))
        surface.blit(lbl_cp2, lbl_cp2.get_rect(center=(c2, panel_rect.bottom - 12)))

        # -------------------------------------------------------------
        # Column 3: HUNTER SIGHT CONE (Triangle pointing left)
        # -------------------------------------------------------------
        cx_c = c3
        cy_c = vis_y + 2
        cone_pts = [
            (cx_c - 36, cy_c),      # Apex on left
            (cx_c + 32, cy_c - 20), # Top-right
            (cx_c + 32, cy_c + 20), # Bottom-right
        ]
        pygame.draw.polygon(surface, (54, 14, 18), [(px, py + 2) for px, py in cone_pts])
        pygame.draw.polygon(surface, (196, 46, 56), cone_pts)
        pygame.draw.polygon(surface, (230, 84, 94), [(cx_c - 34, cy_c), (cx_c + 30, cy_c - 18), (cx_c + 30, cy_c + 18)], 1)
        pygame.draw.polygon(surface, (48, 12, 16), cone_pts, 2)

        lbl_sc1 = font_label.render("HUNTER", True, (48, 24, 10))
        lbl_sc2 = font_label.render("SIGHT CONE", True, (48, 24, 10))
        surface.blit(lbl_sc1, lbl_sc1.get_rect(center=(c3, panel_rect.bottom - 28)))
        surface.blit(lbl_sc2, lbl_sc2.get_rect(center=(c3, panel_rect.bottom - 12)))

    def draw(
        self,
        surface: pygame.Surface,
        btn_back_to_menu: UIButton,
        font_title: pygame.font.Font,
        font_header: pygame.font.Font,
        font_body: pygame.font.Font,
        anim_time: float = 0.0,
        font_btn_bold: Optional[pygame.font.Font] = None,
        font_key: Optional[pygame.font.Font] = None,
    ) -> None:
        """Render the exact retro-pixel RPG adventure How To Play screen."""
        cx = self.screen_width // 2
        card_w = 580
        card_h = 730
        card_x = cx - card_w // 2
        card_y = 24
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # 1. Dark dungeon stone background
        draw_dungeon_background(surface, self.screen_width, self.screen_height)

        # 2. Main Parchment Sheet with wood timber border & iron corners
        self._draw_parchment_chassis(surface, card_rect)

        # 3. 3D Adventure Title "HOW TO PLAY"
        title_y = card_y + 18
        title_text = "HOW TO PLAY"
        t_font = pygame.font.SysFont("trebuchetms,impact,arial", 38, bold=True)
        tx = cx - t_font.size(title_text)[0] // 2

        # 3D Drop Shadow
        for off_y in [4, 3, 2]:
            sh = t_font.render(title_text, True, (44, 16, 4))
            surface.blit(sh, (tx, title_y + off_y))
        # Gold Bevel Outline
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                border = t_font.render(title_text, True, (246, 186, 42))
                surface.blit(border, (tx + dx, title_y + dy))
        # Inner Face
        txt_face = t_font.render(title_text, True, (196, 60, 24))
        surface.blit(txt_face, (tx, title_y))

        # Fonts for panels
        f_badge = font_btn_bold if font_btn_bold else font_header
        f_key = font_key if font_key else font_header
        f_lbl = font_body

        panel_w = 516
        panel_x = cx - panel_w // 2

        # 4. Panel 1: OBJECTIVE
        p1_rect = pygame.Rect(panel_x, card_y + 84, panel_w, 142)
        self._draw_sub_panel(surface, p1_rect, "OBJECTIVE", f_badge)
        self._draw_objective_items(surface, p1_rect, f_lbl, anim_time)

        # 5. Panel 2: CONTROLS
        p2_rect = pygame.Rect(panel_x, card_y + 248, panel_w, 188)
        self._draw_sub_panel(surface, p2_rect, "CONTROLS", f_badge)
        self._draw_controls_panel(surface, p2_rect, f_key, f_lbl)

        # 6. Panel 3: TACTICS
        p3_rect = pygame.Rect(panel_x, card_y + 458, panel_w, 148)
        self._draw_sub_panel(surface, p3_rect, "TACTICS", f_badge)
        self._draw_tactics_panel(surface, p3_rect, f_lbl, anim_time)

        # 7. Action Button: [ BACK TO MENU ]
        btn_back_to_menu.text = "BACK TO MENU"
        btn_back_to_menu.style = "wood_pill"
        btn_back_to_menu.rect = pygame.Rect(cx - 140, card_y + 636, 280, 48)
        btn_back_to_menu.draw(surface)
