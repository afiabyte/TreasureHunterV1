"""
UI Splash Screen: Retro-Pixel RPG adventure splash sequence renderer.
Renders dungeon archway, explorer hero, relic chest, shadow monster,
royal crown title, and recessed wooden progress bar.
"""

import math
from typing import Optional
import pygame
from .art_helpers import draw_royal_crown, draw_adventure_title


class SplashScreenRenderer:
    """Renders the cinematic Retro-Pixel RPG adventure intro splash screen."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self._glow_surf: Optional[pygame.Surface] = None
        self._chest_glow: Optional[pygame.Surface] = None
        self._sm_surf: Optional[pygame.Surface] = None

    def _draw_moss_clump(self, surface: pygame.Surface, mx: int, my: int, spread_w: int = 24, spread_h: int = 35) -> None:
        moss_colors = [(52, 92, 36), (68, 120, 48), (38, 70, 26), (82, 142, 58)]
        for i in range(16):
            rx = mx + int(math.sin(i * 1.7 + mx) * (spread_w // 2))
            ry = my + int(abs(math.cos(i * 2.3 + my)) * spread_h)
            rad = 3 + (i % 5)
            col = moss_colors[i % len(moss_colors)]
            pygame.draw.circle(surface, col, (rx, ry), rad)

    def _draw_wall_torch(self, surface: pygame.Surface, tx: int, ty: int, anim_time: float, flame_seed: float = 0.0) -> None:
        if self._glow_surf is None:
            self._glow_surf = pygame.Surface((300, 300), pygame.SRCALPHA)
            for rad in range(150, 20, -15):
                alpha = int(36 * (1.0 - rad / 150.0))
                pygame.draw.circle(self._glow_surf, (255, 145, 30, alpha), (150, 150), rad)
        surface.blit(self._glow_surf, (tx - 150, ty - 150))

        pygame.draw.rect(surface, (16, 10, 8), (tx - 14, ty + 12, 28, 36), border_radius=3)
        pygame.draw.rect(surface, (48, 38, 34), (tx - 11, ty + 15, 22, 30), border_radius=2)
        pygame.draw.circle(surface, (16, 10, 8), (tx, ty + 24), 4)

        pts = [(tx - 9, ty + 10), (tx + 9, ty + 10), (tx + 5, ty + 50), (tx - 5, ty + 50)]
        pygame.draw.polygon(surface, (92, 54, 26), pts)
        pygame.draw.polygon(surface, (35, 18, 8), pts, 2)
        pygame.draw.rect(surface, (38, 32, 30), (tx - 11, ty + 6, 22, 8), border_radius=2)

        flicker1 = math.sin(anim_time * 14.0 + flame_seed) * 5
        flicker2 = math.cos(anim_time * 16.0 + flame_seed) * 6
        flame_outer = [
            (tx - 12, ty + 6),
            (tx - 16, ty - 12),
            (tx - 8, ty - 34 + int(flicker1)),
            (tx, ty - 50 + int(flicker2)),
            (tx + 8, ty - 32 + int(flicker1)),
            (tx + 16, ty - 12),
            (tx + 12, ty + 6),
        ]
        pygame.draw.polygon(surface, (225, 65, 12), flame_outer)

        flame_mid = [
            (tx - 8, ty + 4),
            (tx - 10, ty - 10),
            (tx - 4, ty - 26 + int(flicker1 * 0.7)),
            (tx, ty - 36 + int(flicker2 * 0.7)),
            (tx + 4, ty - 24 + int(flicker1 * 0.7)),
            (tx + 10, ty - 10),
            (tx + 8, ty + 4),
        ]
        pygame.draw.polygon(surface, (255, 175, 20), flame_mid)
        pygame.draw.ellipse(surface, (255, 245, 180), pygame.Rect(tx - 5, ty - 16, 10, 20))

    def _draw_shadow_monster(self, surface: pygame.Surface, mcx: int, mcy: int) -> None:
        if self._sm_surf is None:
            sm_surf = pygame.Surface((340, 280), pygame.SRCALPHA)
            scx = 170
            scy = 135

            m_pts = [
                (scx - 55, scy + 110),
                (scx - 68, scy + 40),
                (scx - 105, scy + 25),
                (scx - 135, scy - 10),
                (scx - 152, scy - 45),
                (scx - 165, scy - 72),
                (scx - 148, scy - 56),
                (scx - 150, scy - 82),
                (scx - 136, scy - 60),
                (scx - 128, scy - 78),
                (scx - 118, scy - 48),
                (scx - 85, scy + 5),
                (scx - 52, scy - 25),
                (scx - 52, scy - 80),
                (scx - 34, scy - 50),
                (scx - 14, scy - 65),
                (scx, scy - 52),
                (scx + 14, scy - 65),
                (scx + 34, scy - 50),
                (scx + 52, scy - 80),
                (scx + 52, scy - 25),
                (scx + 85, scy + 5),
                (scx + 118, scy - 48),
                (scx + 128, scy - 78),
                (scx + 136, scy - 60),
                (scx + 150, scy - 82),
                (scx + 148, scy - 56),
                (scx + 165, scy - 72),
                (scx + 152, scy - 45),
                (scx + 135, scy - 10),
                (scx + 105, scy + 25),
                (scx + 68, scy + 40),
                (scx + 55, scy + 110),
            ]
            pygame.draw.polygon(sm_surf, (14, 8, 12, 130), m_pts, 14)
            pygame.draw.polygon(sm_surf, (18, 10, 14, 225), m_pts)

            ey = scy - 22
            pygame.draw.polygon(sm_surf, (255, 140, 20), [(scx - 32, ey - 4), (scx - 16, ey + 4), (scx - 26, ey + 9)])
            pygame.draw.polygon(sm_surf, (255, 230, 60), [(scx - 29, ey - 1), (scx - 18, ey + 4), (scx - 24, ey + 7)])

            pygame.draw.polygon(sm_surf, (255, 140, 20), [(scx + 32, ey - 4), (scx + 16, ey + 4), (scx + 26, ey + 9)])
            pygame.draw.polygon(sm_surf, (255, 230, 60), [(scx + 29, ey - 1), (scx + 18, ey + 4), (scx + 24, ey + 7)])

            mouth = [
                (scx - 34, scy + 12),
                (scx - 22, scy + 18),
                (scx - 14, scy + 13),
                (scx - 5, scy + 20),
                (scx + 5, scy + 13),
                (scx + 14, scy + 20),
                (scx + 22, scy + 14),
                (scx + 34, scy + 12),
                (scx + 24, scy + 28),
                (scx + 12, scy + 22),
                (scx + 3, scy + 30),
                (scx - 6, scy + 22),
                (scx - 16, scy + 30),
                (scx - 26, scy + 22),
            ]
            pygame.draw.polygon(sm_surf, (255, 140, 20), mouth)
            pygame.draw.polygon(sm_surf, (255, 225, 70), [(px, py + 1) for px, py in mouth[1:7] + mouth[8:13]])

            self._sm_surf = sm_surf

        surface.blit(self._sm_surf, (mcx - 125, mcy - 125))

    def _draw_skeleton(self, surface: pygame.Surface, sx: int, sy: int) -> None:
        bone_color = (220, 212, 198)
        shadow_color = (18, 10, 8)
        dark_socket = (26, 16, 12)

        pygame.draw.circle(surface, shadow_color, (sx, sy + 3), 19)
        pygame.draw.circle(surface, bone_color, (sx, sy), 18)
        pygame.draw.rect(surface, bone_color, (sx - 10, sy + 10, 20, 13), border_radius=3)
        pygame.draw.rect(surface, shadow_color, (sx - 10, sy + 10, 20, 13), width=2, border_radius=3)
        pygame.draw.ellipse(surface, dark_socket, pygame.Rect(sx - 12, sy - 3, 9, 11))
        pygame.draw.ellipse(surface, dark_socket, pygame.Rect(sx + 3, sy - 3, 9, 11))
        pygame.draw.polygon(surface, dark_socket, [(sx, sy + 6), (sx - 3, sy + 12), (sx + 3, sy + 12)])
        for tx in [-7, -3, 1, 5]:
            pygame.draw.line(surface, dark_socket, (sx + tx, sy + 15), (sx + tx, sy + 21), 2)

        fem1_pts = [(sx + 14, sy + 18), (sx + 45, sy - 18)]
        pygame.draw.line(surface, shadow_color, (sx + 14, sy + 20), (sx + 45, sy - 16), 8)
        pygame.draw.line(surface, bone_color, fem1_pts[0], fem1_pts[1], 6)
        for bx, by in [fem1_pts[0], fem1_pts[1]]:
            pygame.draw.circle(surface, bone_color, (bx - 3, by), 5)
            pygame.draw.circle(surface, bone_color, (bx + 3, by), 5)

        fem2_pts = [(sx - 48, sy + 44), (sx + 38, sy + 42)]
        pygame.draw.line(surface, shadow_color, (sx - 48, sy + 46), (sx + 38, sy + 44), 8)
        pygame.draw.line(surface, bone_color, fem2_pts[0], fem2_pts[1], 6)
        for bx, by in [fem2_pts[0], fem2_pts[1]]:
            pygame.draw.circle(surface, bone_color, (bx, by - 4), 5)
            pygame.draw.circle(surface, bone_color, (bx, by + 4), 5)

    def _draw_relic_chest(self, surface: pygame.Surface, bx: int, by: int) -> None:
        cw = 310
        ch = 165

        pygame.draw.ellipse(surface, (14, 8, 8), pygame.Rect(bx - 25, by + ch - 18, cw + 50, 46))

        lid_poly = [
            (bx + 15, by + 26),
            (bx + 52, by - 62),
            (bx + cw - 28, by - 62),
            (bx + cw, by + 34),
        ]
        pygame.draw.polygon(surface, (16, 10, 8), [(px, py + 7) for px, py in lid_poly])
        pygame.draw.polygon(surface, (126, 64, 28), lid_poly)
        inner_lid = [
            (bx + 34, by + 20),
            (bx + 66, by - 46),
            (bx + cw - 42, by - 46),
            (bx + cw - 18, by + 28),
        ]
        pygame.draw.polygon(surface, (48, 22, 10), inner_lid)
        pygame.draw.line(surface, (78, 38, 16), (bx + 85, by - 58), (bx + 60, by + 22), 2)
        pygame.draw.line(surface, (78, 38, 16), (bx + cw - 65, by - 58), (bx + cw - 40, by + 28), 2)
        pygame.draw.polygon(surface, (244, 188, 52), lid_poly, 9)
        pygame.draw.polygon(surface, (255, 230, 115), lid_poly, 3)

        box_rect = pygame.Rect(bx + 20, by + 30, cw - 40, ch - 30)
        pygame.draw.rect(surface, (122, 62, 28), box_rect, border_radius=6)
        for py in range(box_rect.y + 26, box_rect.bottom - 10, 26):
            pygame.draw.line(surface, (68, 30, 12), (box_rect.x, py), (box_rect.right, py), 2)
            pygame.draw.line(surface, (150, 82, 40), (box_rect.x, py + 1), (box_rect.right, py + 1), 1)

        pygame.draw.rect(surface, (244, 188, 52), (box_rect.x, box_rect.y, 22, box_rect.height), border_radius=4)
        pygame.draw.rect(surface, (244, 188, 52), (box_rect.right - 22, box_rect.y, 22, box_rect.height), border_radius=4)
        pygame.draw.rect(surface, (244, 188, 52), (box_rect.x, box_rect.y, box_rect.width, 18), border_radius=4)
        pygame.draw.rect(surface, (244, 188, 52), (box_rect.x, box_rect.bottom - 18, box_rect.width, 18), border_radius=4)
        pygame.draw.rect(surface, (255, 232, 124), (box_rect.x + 2, box_rect.y + 2, box_rect.width - 4, 4))
        pygame.draw.rect(surface, (44, 20, 8), box_rect, width=3, border_radius=6)

        riv_col = (72, 36, 10)
        for ry in [box_rect.y + 36, box_rect.y + 68, box_rect.y + 100]:
            pygame.draw.circle(surface, riv_col, (box_rect.x + 11, ry), 3)
            pygame.draw.circle(surface, riv_col, (box_rect.right - 11, ry), 3)

        kh_rect = pygame.Rect(box_rect.centerx - 18, box_rect.y + 12, 36, 44)
        pygame.draw.rect(surface, (244, 188, 52), kh_rect, border_radius=5)
        pygame.draw.rect(surface, (44, 20, 8), kh_rect, width=2, border_radius=5)
        pygame.draw.circle(surface, (30, 14, 6), (kh_rect.centerx, kh_rect.y + 16), 5)
        pygame.draw.polygon(surface, (30, 14, 6), [
            (kh_rect.centerx - 4, kh_rect.y + 16),
            (kh_rect.centerx + 4, kh_rect.y + 16),
            (kh_rect.centerx + 5, kh_rect.y + 32),
            (kh_rect.centerx - 5, kh_rect.y + 32),
        ])

        h_cx = box_rect.right - 46
        h_cy = box_rect.y + 68
        pygame.draw.circle(surface, (244, 188, 52), (h_cx, h_cy), 15, 4)
        pygame.draw.circle(surface, (44, 20, 8), (h_cx, h_cy), 17, 2)

        if self._chest_glow is None:
            self._chest_glow = pygame.Surface((cw, 110), pygame.SRCALPHA)
            for rad in range(50, 10, -10):
                pygame.draw.ellipse(self._chest_glow, (255, 220, 70, 30), pygame.Rect(30, 20, cw - 60, 70))
        surface.blit(self._chest_glow, (bx + 10, by - 30))

        for i in range(140):
            rnd_x = bx + 48 + int((math.sin(i * 1.83) * 0.5 + 0.5) * (cw - 96))
            dist_from_center = abs(rnd_x - (bx + cw // 2)) / float(cw // 2 - 30)
            mound_h = math.sqrt(max(0.0, 1.0 - dist_from_center**2)) * 34
            rnd_y = by + 18 + int((math.cos(i * 2.41) * 0.5 + 0.5) * 22) - int(mound_h)
            pygame.draw.circle(surface, (216, 148, 18), (rnd_x, rnd_y + 1), 5)
            pygame.draw.circle(surface, (255, 218, 52), (rnd_x, rnd_y), 5)
            pygame.draw.circle(surface, (255, 246, 170), (rnd_x - 1, rnd_y - 1), 2)

        dg_x = bx + cw - 74
        dg_y = by - 18
        pygame.draw.line(surface, (235, 240, 248), (dg_x, dg_y + 18), (dg_x + 12, dg_y - 24), 5)
        pygame.draw.line(surface, (244, 188, 52), (dg_x + 3, dg_y - 8), (dg_x + 22, dg_y - 2), 5)
        pygame.draw.circle(surface, (244, 188, 52), (dg_x + 14, dg_y - 28), 4)

        pygame.draw.polygon(surface, (225, 28, 58), [(bx + 130, by + 12), (bx + 146, by - 3), (bx + 162, by + 12), (bx + 146, by + 26)])
        pygame.draw.polygon(surface, (255, 125, 145), [(bx + 137, by + 5), (bx + 146, by), (bx + 152, by + 7), (bx + 144, by + 15)])

        pygame.draw.polygon(surface, (28, 205, 82), [(bx + 94, by + 16), (bx + 108, by + 3), (bx + 122, by + 16), (bx + 108, by + 28)])
        pygame.draw.polygon(surface, (145, 255, 185), [(bx + 100, by + 12), (bx + 108, by + 6), (bx + 114, by + 14)])

        pygame.draw.polygon(surface, (28, 132, 238), [(bx + 205, by + 20), (bx + 220, by + 6), (bx + 234, by + 20), (bx + 220, by + 32)])
        pygame.draw.polygon(surface, (150, 215, 255), [(bx + 210, by + 15), (bx + 220, by + 9), (bx + 226, by + 17)])

        def draw_glint(gx: int, gy: int, size: int = 8) -> None:
            pygame.draw.line(surface, (255, 255, 240), (gx - size, gy), (gx + size, gy), 2)
            pygame.draw.line(surface, (255, 255, 240), (gx, gy - size), (gx, gy + size), 2)
            pygame.draw.circle(surface, (255, 242, 130), (gx, gy), 3)

        draw_glint(bx + 75, by - 8, size=7)
        draw_glint(bx + 152, by - 16, size=9)
        draw_glint(bx + 225, by - 4, size=6)

        floor_spills = [
            (bx - 12, by + ch - 12), (bx + 6, by + ch - 8), (bx - 24, by + ch - 4),
            (bx + 28, by + ch - 4), (bx + 48, by + ch + 3), (bx + cw + 12, by + ch - 8),
            (bx + cw + 30, by + ch - 4), (bx + cw - 14, by + ch + 5), (bx + cw + 22, by + ch + 6)
        ]
        for sp_x, sp_y in floor_spills:
            pygame.draw.circle(surface, (216, 148, 18), (sp_x, sp_y + 1), 5)
            pygame.draw.circle(surface, (255, 218, 52), (sp_x, sp_y), 5)
            pygame.draw.circle(surface, (255, 246, 170), (sp_x - 1, sp_y - 1), 2)

        pygame.draw.polygon(surface, (28, 205, 82), [(bx - 6, by + ch + 4), (bx + 4, by + ch - 4), (bx + 12, by + ch + 4)])
        pygame.draw.polygon(surface, (225, 28, 58), [(bx + cw + 14, by + ch + 8), (bx + cw + 24, by + ch), (bx + cw + 32, by + ch + 8)])

    def _draw_hero(self, surface: pygame.Surface, hx: int, hy: int, anim_time: float) -> None:
        pygame.draw.ellipse(surface, (14, 8, 8), pygame.Rect(hx - 65, hy - 10, 130, 26))

        bp_rect = pygame.Rect(hx - 66, hy - 150, 36, 62)
        pygame.draw.rect(surface, (92, 54, 28), bp_rect, border_radius=6)
        pygame.draw.rect(surface, (35, 18, 8), bp_rect, width=2, border_radius=6)
        br_rect = pygame.Rect(hx - 70, hy - 172, 44, 24)
        pygame.draw.rect(surface, (126, 134, 112), br_rect, border_radius=8)
        pygame.draw.rect(surface, (42, 48, 36), br_rect, width=2, border_radius=8)
        pygame.draw.line(surface, (35, 18, 8), (hx - 58, hy - 172), (hx - 58, hy - 148), 2)
        pygame.draw.line(surface, (35, 18, 8), (hx - 38, hy - 172), (hx - 38, hy - 148), 2)

        pygame.draw.polygon(surface, (68, 74, 62), [(hx - 34, hy - 72), (hx - 14, hy - 72), (hx - 22, hy - 25), (hx - 46, hy - 25)])
        pygame.draw.polygon(surface, (78, 44, 22), [(hx - 48, hy - 25), (hx - 20, hy - 25), (hx - 24, hy + 2), (hx - 64, hy + 2)])
        pygame.draw.polygon(surface, (35, 18, 8), [(hx - 48, hy - 25), (hx - 20, hy - 25), (hx - 24, hy + 2), (hx - 64, hy + 2)], 3)

        pygame.draw.polygon(surface, (68, 74, 62), [(hx - 4, hy - 72), (hx + 20, hy - 72), (hx + 34, hy - 25), (hx + 10, hy - 25)])
        pygame.draw.polygon(surface, (78, 44, 22), [(hx + 8, hy - 25), (hx + 36, hy - 25), (hx + 46, hy + 2), (hx + 6, hy + 2)])
        pygame.draw.polygon(surface, (35, 18, 8), [(hx + 8, hy - 25), (hx + 36, hy - 25), (hx + 46, hy + 2), (hx + 6, hy + 2)], 3)

        torso = pygame.Rect(hx - 30, hy - 140, 60, 72)
        pygame.draw.rect(surface, (230, 224, 212), torso, border_radius=4)
        pygame.draw.polygon(surface, (242, 192, 158), [(hx - 10, hy - 140), (hx + 10, hy - 140), (hx, hy - 120)])

        pygame.draw.rect(surface, (120, 68, 32), (hx - 30, hy - 140, 20, 65), border_radius=4)
        pygame.draw.rect(surface, (120, 68, 32), (hx + 10, hy - 140, 20, 65), border_radius=4)
        pygame.draw.rect(surface, (45, 22, 10), (hx - 30, hy - 140, 20, 65), width=2, border_radius=4)
        pygame.draw.rect(surface, (45, 22, 10), (hx + 10, hy - 140, 20, 65), width=2, border_radius=4)

        pygame.draw.rect(surface, (48, 24, 10), (hx - 30, hy - 76, 60, 14))
        bkl = pygame.Rect(hx - 9, hy - 78, 18, 18)
        pygame.draw.rect(surface, (244, 188, 52), bkl, border_radius=3)
        pygame.draw.rect(surface, (45, 22, 10), bkl, width=2, border_radius=3)

        pygame.draw.rect(surface, (242, 192, 158), (hx - 8, hy - 150, 16, 14))
        head = pygame.Rect(hx - 24, hy - 196, 48, 48)
        pygame.draw.rect(surface, (242, 192, 158), head, border_radius=10)
        pygame.draw.rect(surface, (64, 34, 16), (hx - 26, hy - 200, 52, 20), border_radius=6)
        pygame.draw.polygon(surface, (64, 34, 16), [(hx - 26, hy - 188), (hx - 26, hy - 170), (hx - 18, hy - 182)])

        pygame.draw.line(surface, (48, 22, 10), (hx - 14, hy - 176), (hx - 3, hy - 174), 3)
        pygame.draw.line(surface, (48, 22, 10), (hx + 4, hy - 174), (hx + 16, hy - 176), 3)
        pygame.draw.rect(surface, (35, 18, 8), (hx - 12, hy - 171, 7, 7), border_radius=1)
        pygame.draw.rect(surface, (35, 18, 8), (hx + 6, hy - 171, 7, 7), border_radius=1)
        pygame.draw.circle(surface, (255, 255, 255), (hx - 10, hy - 170), 2)
        pygame.draw.circle(surface, (255, 255, 255), (hx + 8, hy - 170), 2)
        pygame.draw.line(surface, (210, 152, 120), (hx - 1, hy - 166), (hx + 3, hy - 160), 2)
        pygame.draw.line(surface, (155, 80, 60), (hx - 6, hy - 154), (hx + 5, hy - 154), 2)

        brim = [
            (hx - 54, hy - 194),
            (hx - 22, hy - 202),
            (hx + 22, hy - 202),
            (hx + 54, hy - 194),
            (hx + 48, hy - 186),
            (hx - 48, hy - 186),
        ]
        pygame.draw.polygon(surface, (132, 78, 40), brim)
        pygame.draw.polygon(surface, (48, 24, 10), brim, 2)
        crown_rect = pygame.Rect(hx - 26, hy - 224, 52, 28)
        pygame.draw.rect(surface, (132, 78, 40), crown_rect, border_top_left_radius=12, border_top_right_radius=12)
        pygame.draw.line(surface, (88, 50, 24), (hx - 18, hy - 224), (hx + 18, hy - 224), 5)
        pygame.draw.rect(surface, (48, 22, 10), (hx - 26, hy - 202, 52, 10))

        pygame.draw.polygon(surface, (230, 224, 212), [(hx + 20, hy - 134), (hx + 44, hy - 114), (hx + 52, hy - 124), (hx + 28, hy - 142)])
        pygame.draw.polygon(surface, (242, 192, 158), [(hx + 44, hy - 114), (hx + 72, hy - 126), (hx + 76, hy - 136), (hx + 52, hy - 124)])
        pygame.draw.circle(surface, (242, 192, 158), (hx + 74, hy - 130), 8)

        htx = hx + 84
        hty = hy - 162
        pygame.draw.line(surface, (105, 60, 28), (hx + 68, hy - 116), (htx, hty + 18), 7)
        pygame.draw.line(surface, (45, 22, 10), (hx + 68, hy - 116), (htx, hty + 18), 2)

        h_flicker = math.sin(anim_time * 18.0) * 4
        h_flame_pts = [
            (htx - 10, hty + 14),
            (htx - 14, hty - 4),
            (htx - 6, hty - 22 + int(h_flicker)),
            (htx + 2, hty - 34 + int(h_flicker * 1.2)),
            (htx + 8, hty - 20),
            (htx + 14, hty - 4),
            (htx + 10, hty + 14),
        ]
        pygame.draw.polygon(surface, (235, 70, 12), h_flame_pts)
        pygame.draw.polygon(surface, (255, 195, 30), [(px, py + 4) for px, py in h_flame_pts[1:6]])
        pygame.draw.circle(surface, (255, 248, 185), (htx, hty), 6)

        pygame.draw.polygon(surface, (230, 224, 212), [(hx - 20, hy - 134), (hx - 40, hy - 106), (hx - 48, hy - 115), (hx - 28, hy - 142)])
        pygame.draw.polygon(surface, (242, 192, 158), [(hx - 40, hy - 106), (hx - 20, hy - 78), (hx - 14, hy - 85), (hx - 48, hy - 115)])
        pygame.draw.circle(surface, (242, 192, 158), (hx - 16, hy - 80), 8)

        shx = hx - 16
        shy = hy - 80
        pygame.draw.line(surface, (88, 54, 24), (shx - 14, shy - 14), (shx + 4, shy + 4), 6)
        pygame.draw.circle(surface, (244, 188, 52), (shx - 16, shy - 16), 5)
        pygame.draw.line(surface, (244, 188, 52), (shx - 8, shy + 14), (shx + 16, shy - 8), 6)
        pygame.draw.circle(surface, (244, 188, 52), (shx - 8, shy + 14), 4)
        pygame.draw.circle(surface, (244, 188, 52), (shx + 16, shy - 8), 4)
        b_pts = [
            (shx + 4, shy + 4),
            (shx + 92, hy - 20),
            (shx + 102, hy - 14),
            (shx + 6, shy + 8),
        ]
        pygame.draw.polygon(surface, (225, 235, 248), b_pts)
        pygame.draw.polygon(surface, (155, 170, 188), b_pts, 2)
        pygame.draw.line(surface, (255, 255, 255), (shx + 8, shy + 6), (shx + 90, hy - 17), 2)

    def draw(self, surface: pygame.Surface, splash_timer: float, splash_duration: float,
             anim_time: float, font_title_bot: pygame.font.Font, font_subtitle: pygame.font.Font,
             font_pixel_med: pygame.font.Font, font_prompt: pygame.font.Font,
             font_title_top: Optional[pygame.font.Font] = None) -> None:
        """Render complete Retro-Pixel RPG adventure splash scene."""
        cx = self.screen_width // 2
        progress = min(1.0, max(0.0, splash_timer / splash_duration))

        # 1. Warm Stone Dungeon Wall
        surface.fill((30, 20, 18))
        brick_w = 64
        brick_h = 30
        cols = self.screen_width // brick_w + 2
        rows = self.screen_height // brick_h + 2

        for r in range(rows):
            off_x = (brick_w // 2) if (r % 2 == 1) else 0
            by = r * brick_h
            for c in range(cols):
                bx = c * brick_w - off_x
                var = ((r * 37 + c * 19) % 19) - 9
                br = max(38, min(80, 56 + var))
                bg = max(26, min(64, 44 + var))
                bb = max(22, min(54, 36 + var))
                b_rect = pygame.Rect(bx, by, brick_w, brick_h)
                pygame.draw.rect(surface, (br, bg, bb), b_rect)
                pygame.draw.rect(surface, (18, 10, 8), b_rect, width=2)
                pygame.draw.line(surface, (br + 14, bg + 12, bb + 8), (bx + 2, by + 2), (bx + brick_w - 3, by + 2), 1)

        # 2. Dungeon Stone Floor
        floor_y = 575
        pygame.draw.rect(surface, (28, 18, 16), pygame.Rect(0, floor_y, self.screen_width, self.screen_height - floor_y))
        pygame.draw.rect(surface, (16, 8, 6), pygame.Rect(0, floor_y - 4, self.screen_width, 6))

        for r in range(7):
            fy = floor_y + r * 30
            f_off = (45 if r % 2 == 1 else 0)
            for c in range(self.screen_width // 90 + 3):
                fx = c * 90 - f_off
                var = ((r * 23 + c * 41) % 15) - 7
                fr = max(34, min(70, 48 + var + r * 2))
                fg = max(24, min(56, 38 + var + r * 2))
                fb = max(20, min(46, 32 + var + r * 2))
                f_rect = pygame.Rect(fx, fy, 90, 30)
                pygame.draw.rect(surface, (fr, fg, fb), f_rect)
                pygame.draw.rect(surface, (16, 10, 8), f_rect, width=2)
                pygame.draw.line(surface, (fr + 15, fg + 12, fb + 10), (fx + 2, fy + 2), (fx + 88, fy + 2), 1)

        for x in [30, 80, 160, 240, 380, 580, 720, 840, 920]:
            self._draw_moss_clump(surface, x, 0, spread_w=35, spread_h=40)
        for x in [140, 420, 560, 820]:
            self._draw_moss_clump(surface, x, 180, spread_w=25, spread_h=28)

        # 3. Dungeon Archway
        arch_cx = 285
        arch_w = 200
        arch_h = 345
        arch_top_y = floor_y - arch_h

        num_blocks = 15
        for i in range(num_blocks):
            ang = math.pi * (i / float(num_blocks - 1))
            vx = arch_cx - int(math.cos(ang) * (arch_w // 2 + 18))
            vy = arch_top_y + (arch_w // 2) - int(math.sin(ang) * (arch_w // 2 + 18))
            pygame.draw.circle(surface, (18, 12, 10), (vx, vy), 24)
            pygame.draw.circle(surface, (58, 44, 38), (vx, vy), 21)
            pygame.draw.circle(surface, (82, 64, 56), (vx, vy), 16)
            pygame.draw.circle(surface, (24, 16, 14), (vx, vy), 22, 2)

        pygame.draw.rect(surface, (58, 44, 38), (arch_cx - arch_w // 2 - 30, arch_top_y + arch_w // 2 - 10, 34, arch_h - arch_w // 2 + 10))
        pygame.draw.rect(surface, (58, 44, 38), (arch_cx + arch_w // 2 - 4, arch_top_y + arch_w // 2 - 10, 34, arch_h - arch_w // 2 + 10))
        pygame.draw.rect(surface, (20, 12, 10), (arch_cx - arch_w // 2 - 30, arch_top_y + arch_w // 2 - 10, 34, arch_h - arch_w // 2 + 10), 3)
        pygame.draw.rect(surface, (20, 12, 10), (arch_cx + arch_w // 2 - 4, arch_top_y + arch_w // 2 - 10, 34, arch_h - arch_w // 2 + 10), 3)

        inner_r = arch_w // 2
        pygame.draw.circle(surface, (10, 6, 8), (arch_cx, arch_top_y + inner_r), inner_r)
        pygame.draw.rect(surface, (10, 6, 8), (arch_cx - inner_r, arch_top_y + inner_r, arch_w, arch_h - inner_r))
        pygame.draw.circle(surface, (18, 10, 12), (arch_cx, arch_top_y + inner_r), inner_r, 4)

        self._draw_moss_clump(surface, arch_cx - arch_w // 2 - 12, arch_top_y + 40, spread_w=20, spread_h=80)
        self._draw_moss_clump(surface, arch_cx + arch_w // 2 + 14, arch_top_y + 60, spread_w=20, spread_h=90)
        self._draw_moss_clump(surface, arch_cx, arch_top_y - 12, spread_w=40, spread_h=20)

        # 4. Wall Torches
        self._draw_wall_torch(surface, 115, 360, anim_time, flame_seed=0.5)
        self._draw_wall_torch(surface, 905, 350, anim_time, flame_seed=2.8)

        # 5. Terrifying Shadow Monster
        self._draw_shadow_monster(surface, 710, 330)

        # 6. Skeleton Remains on Floor Left
        self._draw_skeleton(surface, 115, 570)

        # 7. Relic Treasure Chest
        self._draw_relic_chest(surface, 545, 425)

        # 8. Adventurer Hero Character
        self._draw_hero(surface, 345, 575, anim_time)

        # 9. Top Royal Crown & 3D Title "TREASURE HUNTER"
        top_y = 36
        draw_royal_crown(surface, cx, top_y + 12)
        draw_adventure_title(surface, "TREASURE HUNTER", top_y + 44, font_title_bot, cx)

        # Subtitle: "A Roguelike Adventure"
        sub_str = "A Roguelike Adventure"
        sub_surf = font_subtitle.render(sub_str, True, (238, 192, 132))
        sub_sh = font_subtitle.render(sub_str, True, (36, 12, 4))
        sub_x = cx - sub_surf.get_width() // 2
        sub_y = top_y + 110
        surface.blit(sub_sh, (sub_x + 2, sub_y + 2))
        surface.blit(sub_surf, (sub_x, sub_y))

        # Top "LOADING..." text
        top_load = font_pixel_med.render("LOADING...", True, (218, 172, 115))
        surface.blit(top_load, top_load.get_rect(center=(cx, sub_y + 36)))

        # 10. Bottom Loading Bar Section
        bot_load = font_pixel_med.render("LOADING...", True, (218, 172, 115))
        surface.blit(bot_load, bot_load.get_rect(center=(cx, 638)))

        bar_w = 540
        bar_h = 36
        bar_x = cx - bar_w // 2
        bar_y = 658
        bar_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)

        pygame.draw.rect(surface, (28, 12, 6), bar_rect.move(0, 3), border_radius=8)
        pygame.draw.rect(surface, (105, 55, 24), bar_rect, border_radius=8)
        pygame.draw.rect(surface, (142, 80, 38), bar_rect.inflate(-4, -4), border_radius=6)
        pygame.draw.rect(surface, (38, 16, 6), bar_rect, width=3, border_radius=8)

        slot_rect = bar_rect.inflate(-10, -10)
        pygame.draw.rect(surface, (22, 14, 10), slot_rect, border_radius=5)
        pygame.draw.rect(surface, (12, 6, 4), slot_rect, width=1, border_radius=5)

        fill_w = int(slot_rect.width * progress)
        if fill_w > 0:
            fill_rect = pygame.Rect(slot_rect.x, slot_rect.y, fill_w, slot_rect.height)
            pygame.draw.rect(surface, (46, 204, 113), fill_rect, border_radius=4)
            pygame.draw.rect(surface, (115, 238, 160), (fill_rect.x, fill_rect.y, fill_rect.width, fill_rect.height // 2), border_top_left_radius=4, border_top_right_radius=4)
            pygame.draw.rect(surface, (26, 134, 72), (fill_rect.x, fill_rect.bottom - 4, fill_rect.width, 4), border_bottom_left_radius=4, border_bottom_right_radius=4)

        pulse = (math.sin(anim_time * 5.0) + 1.0) * 0.5
        pr_col = (int(220 + 35 * pulse), int(180 + 38 * pulse), int(50 + 30 * pulse))
        pr_str = "PRESS START OR TAP TO PLAY"
        pr_surf = font_prompt.render(pr_str, True, pr_col)
        pr_sh = font_prompt.render(pr_str, True, (38, 14, 4))
        pr_x = cx - pr_surf.get_width() // 2
        pr_y = 718

        surface.blit(pr_sh, (pr_x + 2, pr_y + 2))
        surface.blit(pr_surf, (pr_x, pr_y))

    draw_splash_screen = draw

