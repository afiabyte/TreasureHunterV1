"""
UI Game View: Interactive tactical grid renderer, dynamic walls,
relic key, exit gateway, safe-route breadcrumbs, directional guide arrow,
animated human player operative, and human mercenary hunters.
"""

import math
from typing import Tuple, List, Optional
import pygame

from .colors import (
    COLOR_GRID_LINE,
    COLOR_WALL_BORDER,
    COLOR_KEY_GOLD,
    COLOR_GUIDE_ARROW,
)


class GameViewRenderer:
    """Renders the in-game tactical labyrinth, entities, and visual navigation aids."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self._cached_cone_surf: Optional[pygame.Surface] = None

    def compute_grid_geometry(
        self,
        grid_size: int,
        hud_height: int = 140
    ) -> Tuple[float, float, float]:
        """
        Dynamically scale cell pixel sizes so the chosen N x N grid fits cleanly
        centered above the bottom HUD console.

        Returns:
            Tuple of (origin_x, origin_y, cell_size)
        """
        top_margin = 20
        bottom_limit = self.screen_height - hud_height - 20
        max_h = bottom_limit - top_margin
        max_w = self.screen_width - 40

        cell_size = math.floor(min(max_w / grid_size, max_h / grid_size))
        cell_size = max(cell_size, 32.0)

        grid_total_w = cell_size * grid_size
        grid_total_h = cell_size * grid_size

        origin_x = (self.screen_width - grid_total_w) / 2.0
        origin_y = top_margin + (max_h - grid_total_h) / 2.0

        return (origin_x, origin_y, float(cell_size))

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
        anim_time: float,
        font_bold: pygame.font.Font,
        font_badge: pygame.font.Font,
        font_small: pygame.font.Font,
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
        pygame.draw.rect(surface, (6, 8, 16), grid_rect.move(0, 5), border_radius=6)
        pygame.draw.rect(surface, (14, 18, 32), grid_rect, border_radius=6)

        # Alternating high-tech floor tiles for rich visual depth & color
        for r in range(grid_size):
            for c in range(grid_size):
                cell_rect = pygame.Rect(origin_x + c * cell_size, origin_y + r * cell_size, cell_size, cell_size)
                tile_col = (34, 40, 54) if (r + c) % 2 == 0 else (26, 30, 42)
                pygame.draw.rect(surface, tile_col, cell_rect)

                if (r, c) not in walls:
                    cx_t = origin_x + c * cell_size
                    cy_t = origin_y + r * cell_size
                    pin_col = (110, 100, 75)
                    pygame.draw.circle(surface, pin_col, (int(cx_t + 4), int(cy_t + 4)), 1)
                    pygame.draw.circle(surface, pin_col, (int(cx_t + cell_size - 4), int(cy_t + 4)), 1)
                    pygame.draw.circle(surface, pin_col, (int(cx_t + 4), int(cy_t + cell_size - 4)), 1)
                    pygame.draw.circle(surface, pin_col, (int(cx_t + cell_size - 4), int(cy_t + cell_size - 4)), 1)
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

        # Outer Tactical Grid Frame with Double Neon Rim (Cyan & Gold)
        pygame.draw.rect(surface, (225, 175, 55), grid_rect, width=2, border_radius=6)
        pygame.draw.rect(surface, (65, 175, 245), grid_rect.inflate(4, 4), width=1, border_radius=8)

        # 1. ENERGIZED BLAST BARRIERS (WALLS)
        for (wr, wc) in walls:
            wx = origin_x + wc * cell_size
            wy = origin_y + wr * cell_size
            pad = max(2.0, cell_size * 0.04)
            w_w = cell_size - pad * 2
            w_h = cell_size - pad * 2
            w_rect = pygame.Rect(wx + pad, wy + pad, w_w, w_h)

            shadow_rect = pygame.Rect(wx + pad, wy + pad + 3, w_w, w_h)
            pygame.draw.rect(surface, (6, 8, 14), shadow_rect, border_radius=4)
            pygame.draw.rect(surface, (38, 42, 56), w_rect, border_radius=4)

            # 3D Chiseled Bevel
            pygame.draw.line(surface, (120, 130, 155), (w_rect.left + 1, w_rect.top + 1), (w_rect.right - 2, w_rect.top + 1), 1)
            pygame.draw.line(surface, (120, 130, 155), (w_rect.left + 1, w_rect.top + 1), (w_rect.left + 1, w_rect.bottom - 2), 1)
            pygame.draw.line(surface, (10, 14, 22), (w_rect.left + 1, w_rect.bottom - 1), (w_rect.right - 1, w_rect.bottom - 1), 1)
            pygame.draw.line(surface, (10, 14, 22), (w_rect.right - 1, w_rect.top + 1), (w_rect.right - 1, w_rect.bottom - 1), 1)

            inset_m = max(3.0, cell_size * 0.14)
            inset_rect = pygame.Rect(wx + inset_m, wy + inset_m, cell_size - inset_m * 2, cell_size - inset_m * 2)
            pygame.draw.rect(surface, (25, 29, 40), inset_rect, border_radius=2)
            pygame.draw.rect(surface, (215, 165, 45), inset_rect, width=1, border_radius=2)

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

            c_cx = wx + cell_size / 2.0
            c_cy = wy + cell_size / 2.0
            core_half = max(3.0, cell_size * 0.14)

            if wall_shift_alert > 0:
                h_col = (255, 160, 30)
                v_col = (255, 100, 20)
                p_rate = 14.0
                p_core = (255, 160, 30)
                p_glow = (255, 240, 140)
            else:
                h_col = (235, 185, 50)
                v_col = (225, 75, 45)
                p_rate = 3.6
                p_core = (255, 195, 40)
                p_glow = (255, 245, 180)

            pygame.draw.line(surface, h_col, (c_cx - core_half * 1.5, c_cy), (c_cx + core_half * 1.5, c_cy), 1)
            pygame.draw.line(surface, v_col, (c_cx, c_cy - core_half * 1.5), (c_cx, c_cy + core_half * 1.5), 1)

            p_factor = 0.82 + 0.18 * math.sin(anim_time * p_rate + (wr * 3 + wc * 7))
            cur_r = core_half * p_factor

            core_pts = [
                (c_cx, c_cy - cur_r),
                (c_cx + cur_r, c_cy),
                (c_cx, c_cy + cur_r),
                (c_cx - cur_r, c_cy)
            ]
            pygame.draw.polygon(surface, p_core, core_pts)
            pygame.draw.circle(surface, (225, 175, 55), (int(c_cx), int(c_cy)), int(cur_r * 1.25), 1)
            hot_r = cur_r * 0.45
            hot_pts = [
                (c_cx, c_cy - hot_r),
                (c_cx + hot_r, c_cy),
                (c_cx, c_cy + hot_r),
                (c_cx - hot_r, c_cy)
            ]
            pygame.draw.polygon(surface, p_glow, hot_pts)

        # 2. EXTRACTION EXIT PORTAL (N-1, N-1)
        ex_x = origin_x + exit_pos[1] * cell_size + cell_size / 2.0
        ex_y = origin_y + exit_pos[0] * cell_size + cell_size / 2.0
        portal_radius = cell_size * 0.38
        pulse_scale = 1.0 + 0.08 * math.sin(anim_time * 4.0)
        p_r = int(portal_radius * pulse_scale)

        if has_key:
            pygame.draw.circle(surface, (35, 245, 135), (int(ex_x), int(ex_y)), p_r, width=2)
            for i in range(4):
                orb_angle = anim_time * 2.5 + i * (math.pi / 2.0)
                orb_x = ex_x + math.cos(orb_angle) * (p_r + 2)
                orb_y = ex_y + math.sin(orb_angle) * (p_r + 2)
                pygame.draw.circle(surface, (180, 255, 220), (int(orb_x), int(orb_y)), max(1, int(cell_size * 0.04)))

            core_r = max(2, int(portal_radius * 0.58))
            pygame.draw.circle(surface, (20, 180, 95), (int(ex_x), int(ex_y)), core_r)
            pygame.draw.circle(surface, (210, 255, 235), (int(ex_x), int(ex_y)), max(1, int(core_r * 0.4)))
            exit_label = font_bold.render("ESCAPE", True, (255, 255, 255))
        else:
            pygame.draw.circle(surface, (220, 140, 30), (int(ex_x), int(ex_y)), p_r, width=2)
            core_r = max(2, int(portal_radius * 0.52))
            pygame.draw.circle(surface, (45, 38, 25), (int(ex_x), int(ex_y)), core_r)
            exit_label = font_badge.render("SEALED", True, (255, 185, 45))

        surface.blit(exit_label, exit_label.get_rect(center=(int(ex_x), int(ex_y))))

        # 3. GOLDEN CIPHER ARTIFACT (KEY)
        if not has_key:
            kx = origin_x + key_pos[1] * cell_size + cell_size / 2.0
            ky = origin_y + key_pos[0] * cell_size + cell_size / 2.0
            k_pulse = 1.0 + 0.12 * math.sin(anim_time * 5.0)
            k_radius = cell_size * 0.28 * k_pulse
            k_bob = math.sin(anim_time * 4.0) * (cell_size * 0.05)
            ky += k_bob

            pygame.draw.circle(surface, (255, 205, 35), (int(kx), int(ky)), int(k_radius + 3), width=1)
            for i in range(3):
                p_ang = anim_time * 3.0 + i * (math.pi * 2.0 / 3.0)
                px_orb = kx + math.cos(p_ang) * (k_radius + 3)
                py_orb = ky + math.sin(p_ang) * (k_radius + 3)
                pygame.draw.circle(surface, (255, 245, 180), (int(px_orb), int(py_orb)), max(1, int(cell_size * 0.035)))

            d_half = k_radius * 0.65
            diamond_pts = [
                (kx, ky - d_half * 1.2),
                (kx + d_half, ky),
                (kx, ky + d_half * 1.2),
                (kx - d_half, ky)
            ]
            pygame.draw.polygon(surface, COLOR_KEY_GOLD, diamond_pts)
            facet_pts = [
                (kx, ky - d_half * 0.6),
                (kx + d_half * 0.5, ky),
                (kx, ky + d_half * 0.6),
                (kx - d_half * 0.5, ky)
            ]
            pygame.draw.polygon(surface, (255, 250, 180), facet_pts)
            k_lbl = font_badge.render("RELIC", True, (25, 20, 10))
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
                        pygame.draw.circle(surface, (40, 240, 120), (int(bx), int(by)), b_radius, width=2)
                        pygame.draw.circle(surface, (20, 90, 48), (int(bx), int(by)), max(2, b_radius - 3))
                        num_surf = font_bold.render(str(idx + 1), True, (220, 255, 230))
                        surface.blit(num_surf, num_surf.get_rect(center=(int(bx), int(by))))

        # 5. Pulsing Yellow Guide Arrow (pointing to current objective)
        target_pos = exit_pos if has_key else key_pos
        tg_x = origin_x + target_pos[1] * cell_size + cell_size / 2.0
        tg_y = origin_y + target_pos[0] * cell_size + cell_size / 2.0
        dx = tg_x - player_x
        dy = tg_y - player_y
        dist = math.hypot(dx, dy)
        if dist > cell_size * 0.5:
            nx, ny = dx / dist, dy / dist
            arrow_dist = cell_size * 0.42
            ax = player_x + nx * arrow_dist
            ay = player_y + ny * arrow_dist
            arrow_size = max(5, int(cell_size * 0.16))

            a_pulse = 1.0 + 0.15 * math.sin(anim_time * 6.0)
            perp_x, perp_y = -ny, nx

            p1 = (ax + nx * (arrow_size * a_pulse), ay + ny * (arrow_size * a_pulse))
            p2 = (ax - nx * (arrow_size * a_pulse) + perp_x * (arrow_size * 0.7),
                  ay - ny * (arrow_size * a_pulse) + perp_y * (arrow_size * 0.7))
            p3 = (ax - nx * (arrow_size * a_pulse) - perp_x * (arrow_size * 0.7),
                  ay - ny * (arrow_size * a_pulse) - perp_y * (arrow_size * 0.7))

            pygame.draw.polygon(surface, COLOR_GUIDE_ARROW, [p1, p2, p3])

        # 6. Human Mercenary Hunters
        for h in hunters:
            self._draw_human_hunter(surface, h.visual_x, h.visual_y, cell_size, h.facing_dr, h.facing_dc, h.hunter_id, anim_time, font_small)

        # 7. Human Player Operative
        self._draw_human_player(surface, player_x, player_y, cell_size, player_facing[0], player_facing[1], has_key, anim_time, font_small)

    def _draw_human_player(
        self,
        surface: pygame.Surface,
        px: float,
        py: float,
        cell_size: float,
        facing_dr: int,
        facing_dc: int,
        has_key: bool,
        anim_time: float,
        font_small: pygame.font.Font,
    ) -> None:
        """Render the Gamer/Player Operative as an ultra-premium animated humanoid character."""
        scale = max(0.55, cell_size / 64.0)

        if facing_dr == 0 and facing_dc == 0:
            angle = 0.0
        else:
            angle = math.atan2(facing_dr, facing_dc)

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        perp_x = -sin_a
        perp_y = cos_a

        # 1. Drop Shadow
        shadow_surf = pygame.Surface((int(36 * scale), int(24 * scale)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (5, 8, 14, 130), shadow_surf.get_rect())
        surface.blit(shadow_surf, shadow_surf.get_rect(center=(int(px), int(py + 4.5 * scale))))

        # 2. Tactician Tactical Aura Ring
        pulse = 1.0 + 0.08 * math.sin(anim_time * 5.0)
        ring_r = int(cell_size * 0.36 * pulse)
        pygame.draw.circle(surface, (255, 195, 45), (int(px), int(py)), ring_r, width=1)
        pygame.draw.circle(surface, (180, 130, 25), (int(px), int(py)), max(2, ring_r - 3), width=1)

        # 3. Animated Combat Boots
        walk_stride = math.sin(anim_time * 9.0) * (4.2 * scale)
        foot_spread = 5.8 * scale

        lfx = px + perp_x * (-foot_spread) + cos_a * walk_stride
        lfy = py + perp_y * (-foot_spread) + sin_a * walk_stride
        pygame.draw.circle(surface, (18, 25, 36), (int(lfx), int(lfy)), max(2, int(3.5 * scale)))
        pygame.draw.circle(surface, (215, 165, 45), (int(lfx - cos_a * (1.2 * scale)), int(lfy - sin_a * (1.2 * scale))), max(1, int(1.8 * scale)))

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

        pygame.draw.polygon(surface, (16, 22, 34), [p_l_shoulder, p_r_shoulder, p_r_hip, p_l_hip])

        p_bp1 = (px + perp_x * (-sh_w * 0.8) + cos_a * (chest_len * 0.85), py + perp_y * (-sh_w * 0.8) + sin_a * (chest_len * 0.85))
        p_bp2 = (px + perp_x * (sh_w * 0.8) + cos_a * (chest_len * 0.85), py + perp_y * (sh_w * 0.8) + sin_a * (chest_len * 0.85))
        p_bp3 = (px + perp_x * (hip_w * 0.75) - cos_a * (hip_back * 0.35), py + perp_y * (hip_w * 0.75) - sin_a * (hip_back * 0.35))
        p_bp4 = (px + perp_x * (-hip_w * 0.75) - cos_a * (hip_back * 0.35), py + perp_y * (-hip_w * 0.75) - sin_a * (hip_back * 0.35))
        pygame.draw.polygon(surface, (145, 85, 42), [p_bp1, p_bp2, p_bp3, p_bp4])
        pygame.draw.polygon(surface, (225, 175, 55), [p_bp1, p_bp2, p_bp3, p_bp4], width=1)

        pygame.draw.line(surface, (25, 40, 60), p_l_shoulder, p_r_hip, max(1, int(1.8 * scale)))
        pygame.draw.line(surface, (25, 40, 60), p_r_shoulder, p_l_hip, max(1, int(1.8 * scale)))

        crest_x = px + cos_a * (1.2 * scale)
        crest_y = py + sin_a * (1.2 * scale)
        crest_r = max(2, int(2.4 * scale))
        pygame.draw.circle(surface, (225, 175, 50), (int(crest_x), int(crest_y)), crest_r)
        pygame.draw.circle(surface, (255, 240, 160), (int(crest_x), int(crest_y)), max(1, int(crest_r * 0.5)))

        pygame.draw.circle(surface, (115, 65, 32), (int(p_l_shoulder[0]), int(p_l_shoulder[1])), max(2, int(3.2 * scale)))
        pygame.draw.circle(surface, (225, 175, 50), (int(p_l_shoulder[0]), int(p_l_shoulder[1])), max(1, int(1.8 * scale)))
        pygame.draw.circle(surface, (115, 65, 32), (int(p_r_shoulder[0]), int(p_r_shoulder[1])), max(2, int(3.2 * scale)))
        pygame.draw.circle(surface, (225, 175, 50), (int(p_r_shoulder[0]), int(p_r_shoulder[1])), max(1, int(1.8 * scale)))

        # 5. Articulated Arms
        arm_reach = 9.5 * scale
        hand_r_x = px + perp_x * (sh_w * 0.8) + cos_a * arm_reach
        hand_r_y = py + perp_y * (sh_w * 0.8) + sin_a * arm_reach
        hand_l_x = px + perp_x * (-sh_w * 0.8) + cos_a * (arm_reach * 0.65)
        hand_l_y = py + perp_y * (-sh_w * 0.8) + sin_a * (arm_reach * 0.65)

        pygame.draw.line(surface, (130, 75, 36), p_r_shoulder, (hand_r_x, hand_r_y), max(2, int(3.6 * scale)))
        pygame.draw.line(surface, (130, 75, 36), p_l_shoulder, (hand_l_x, hand_l_y), max(2, int(3.6 * scale)))

        pda_x = (p_l_shoulder[0] + hand_l_x) * 0.5
        pda_y = (p_l_shoulder[1] + hand_l_y) * 0.5
        pygame.draw.circle(surface, (225, 175, 50), (int(pda_x), int(pda_y)), max(1, int(2.2 * scale)))
        pygame.draw.circle(surface, (255, 245, 180), (int(pda_x), int(pda_y)), max(1, int(1.0 * scale)))

        pygame.draw.circle(surface, (245, 195, 158), (int(hand_r_x), int(hand_r_y)), max(1, int(2.5 * scale)))
        pygame.draw.circle(surface, (245, 195, 158), (int(hand_l_x), int(hand_l_y)), max(1, int(2.5 * scale)))

        scanner_tip_x = hand_r_x + cos_a * (5.0 * scale)
        scanner_tip_y = hand_r_y + sin_a * (5.0 * scale)
        pygame.draw.line(surface, (45, 58, 78), (hand_r_x, hand_r_y), (scanner_tip_x, scanner_tip_y), max(2, int(3.0 * scale)))
        pygame.draw.circle(surface, (255, 210, 50), (int(scanner_tip_x), int(scanner_tip_y)), max(1, int(2.2 * scale)))

        # Flashlight Beam
        light_len = cell_size * 0.85
        light_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        p_apex = (scanner_tip_x, scanner_tip_y)

        half_fov = math.radians(24)
        p_l = (scanner_tip_x + math.cos(angle - half_fov) * light_len, scanner_tip_y + math.sin(angle - half_fov) * light_len)
        p_r = (scanner_tip_x + math.cos(angle + half_fov) * light_len, scanner_tip_y + math.sin(angle + half_fov) * light_len)
        pygame.draw.polygon(light_surf, (255, 205, 60, 26), [p_apex, p_l, p_r])

        narrow_fov = math.radians(11)
        p_nl = (scanner_tip_x + math.cos(angle - narrow_fov) * (light_len * 1.05), scanner_tip_y + math.sin(angle - narrow_fov) * (light_len * 1.05))
        p_nr = (scanner_tip_x + math.cos(angle + narrow_fov) * (light_len * 1.05), scanner_tip_y + math.sin(angle + narrow_fov) * (light_len * 1.05))
        pygame.draw.polygon(light_surf, (255, 235, 130, 48), [p_apex, p_nl, p_nr])
        surface.blit(light_surf, (0, 0))

        # 6. Human Head & Fedora
        head_cx = px + cos_a * (1.8 * scale)
        head_cy = py + sin_a * (1.8 * scale)
        head_r = 7.2 * scale

        pygame.draw.circle(surface, (245, 198, 162), (int(head_cx), int(head_cy)), int(head_r))

        hair_surf = pygame.Surface((int(head_r * 2 + 6), int(head_r * 2 + 6)), pygame.SRCALPHA)
        pygame.draw.circle(hair_surf, (36, 26, 20), (int(head_r + 3), int(head_r + 3)), int(head_r + 0.5))
        face_cut_x = int(head_r + 3 + cos_a * (head_r * 0.45))
        face_cut_y = int(head_r + 3 + sin_a * (head_r * 0.45))
        pygame.draw.circle(hair_surf, (0, 0, 0, 0), (face_cut_x, face_cut_y), int(head_r * 0.78))
        surface.blit(hair_surf, (int(head_cx - head_r - 3), int(head_cy - head_r - 3)))

        brim_cx = head_cx + cos_a * (0.8 * scale)
        brim_cy = head_cy + sin_a * (0.8 * scale)
        brim_r = head_r * 1.15
        pygame.draw.circle(surface, (105, 60, 28), (int(brim_cx), int(brim_cy)), int(brim_r))

        crown_cx = head_cx - cos_a * (0.8 * scale)
        crown_cy = head_cy - sin_a * (0.8 * scale)
        pygame.draw.circle(surface, (145, 90, 45), (int(crown_cx), int(crown_cy)), int(head_r * 0.85))
        pygame.draw.circle(surface, (225, 175, 50), (int(crown_cx), int(crown_cy)), int(head_r * 0.85), width=1)

        # 7. Secured Key on Backpack
        if has_key:
            pack_x = px - cos_a * (8.0 * scale)
            pack_y = py - sin_a * (8.0 * scale)
            k_pulse = 1.0 + 0.15 * math.sin(anim_time * 6.0)
            pygame.draw.circle(surface, (255, 205, 30), (int(pack_x), int(pack_y)), int(5.0 * scale * k_pulse))
            pygame.draw.circle(surface, (255, 255, 220), (int(pack_x), int(pack_y)), max(1, int(2.5 * scale)))
            for i in range(2):
                sp_ang = anim_time * 4.0 + i * math.pi
                sp_x = pack_x + math.cos(sp_ang) * (7.0 * scale)
                sp_y = pack_y + math.sin(sp_ang) * (7.0 * scale)
                pygame.draw.circle(surface, (255, 240, 160), (int(sp_x), int(sp_y)), max(1, int(1.4 * scale)))

        # 8. Floating Operative Callsign Pill
        lbl = font_small.render("HUNTER", True, COLOR_KEY_GOLD)
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
        hunter_id: int,
        anim_time: float,
        font_small: pygame.font.Font,
    ) -> None:
        """Render the Hunter as an ultra-premium animated Tactical Mercenary Juggernaut."""
        scale = max(0.55, cell_size / 64.0)

        if facing_dr == 0 and facing_dc == 0:
            angle = math.pi / 2
        else:
            angle = math.atan2(facing_dr, facing_dc)

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        perp_x = -sin_a
        perp_y = cos_a

        # 1. Volumetric Infrared Cone
        cone_len = cell_size * 0.98
        if self._cached_cone_surf is None:
            self._cached_cone_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self._cached_cone_surf.fill((0, 0, 0, 0))
        p_apex = (hx, hy)

        half_fov = math.radians(28)
        p_left = (hx + math.cos(angle - half_fov) * cone_len, hy + math.sin(angle - half_fov) * cone_len)
        p_right = (hx + math.cos(angle + half_fov) * cone_len, hy + math.sin(angle + half_fov) * cone_len)
        pygame.draw.polygon(self._cached_cone_surf, (255, 35, 55, 35), [p_apex, p_left, p_right])

        core_fov = math.radians(14)
        p_cleft = (hx + math.cos(angle - core_fov) * (cone_len * 1.08), hy + math.sin(angle - core_fov) * (cone_len * 1.08))
        p_cright = (hx + math.cos(angle + core_fov) * (cone_len * 1.08), hy + math.sin(angle + core_fov) * (cone_len * 1.08))
        pygame.draw.polygon(self._cached_cone_surf, (255, 75, 95, 55), [p_apex, p_cleft, p_cright])
        surface.blit(self._cached_cone_surf, (0, 0))

        # 2. Heavy Drop Shadow
        shadow_surf = pygame.Surface((int(38 * scale), int(26 * scale)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (8, 4, 8, 140), shadow_surf.get_rect())
        surface.blit(shadow_surf, shadow_surf.get_rect(center=(int(hx), int(hy + 4.5 * scale))))

        # 3. Boots
        walk_stride = math.sin(anim_time * 8.0 + hunter_id * 1.5) * (4.0 * scale)
        foot_spread = 6.5 * scale

        lfx = hx + perp_x * (-foot_spread) + cos_a * walk_stride
        lfy = hy + perp_y * (-foot_spread) + sin_a * walk_stride
        pygame.draw.circle(surface, (20, 16, 20), (int(lfx), int(lfy)), max(2, int(3.8 * scale)))
        pygame.draw.circle(surface, (185, 25, 45), (int(lfx - cos_a * (1.2 * scale)), int(lfy - sin_a * (1.2 * scale))), max(1, int(2.0 * scale)))

        rfx = hx + perp_x * (foot_spread) - cos_a * walk_stride
        rfy = hy + perp_y * (foot_spread) - sin_a * walk_stride
        pygame.draw.circle(surface, (20, 16, 20), (int(rfx), int(rfy)), max(2, int(3.8 * scale)))
        pygame.draw.circle(surface, (185, 25, 45), (int(rfx - cos_a * (1.2 * scale)), int(rfy - sin_a * (1.2 * scale))), max(1, int(2.0 * scale)))

        # 4. Torso & Ballistic Vest
        sh_w = 9.8 * scale
        hip_w = 6.8 * scale
        chest_len = 5.8 * scale
        hip_back = 6.2 * scale

        p_l_shoulder = (hx + perp_x * (-sh_w) + cos_a * chest_len, hy + perp_y * (-sh_w) + sin_a * chest_len)
        p_r_shoulder = (hx + perp_x * (sh_w) + cos_a * chest_len, hy + perp_y * (sh_w) + sin_a * chest_len)
        p_r_hip = (hx + perp_x * (hip_w) - cos_a * hip_back, hy + perp_y * (hip_w) - sin_a * hip_back)
        p_l_hip = (hx + perp_x * (-hip_w) - cos_a * hip_back, hy + perp_y * (-hip_w) - sin_a * hip_back)

        pygame.draw.polygon(surface, (26, 20, 26), [p_l_shoulder, p_r_shoulder, p_r_hip, p_l_hip])

        plate_w = 7.0 * scale
        p_pl1 = (hx + perp_x * (-plate_w) + cos_a * (chest_len * 0.9), hy + perp_y * (-plate_w) + sin_a * (chest_len * 0.9))
        p_pl2 = (hx + perp_x * (plate_w) + cos_a * (chest_len * 0.9), hy + perp_y * (plate_w) + sin_a * (chest_len * 0.9))
        p_pl3 = (hx + perp_x * (plate_w * 0.8) - cos_a * (hip_back * 0.4), hy + perp_y * (plate_w * 0.8) - sin_a * (hip_back * 0.4))
        p_pl4 = (hx + perp_x * (-plate_w * 0.8) - cos_a * (hip_back * 0.4), hy + perp_y * (-plate_w * 0.8) - sin_a * (hip_back * 0.4))
        pygame.draw.polygon(surface, (205, 30, 52), [p_pl1, p_pl2, p_pl3, p_pl4])
        pygame.draw.polygon(surface, (140, 18, 35), [p_pl1, p_pl2, p_pl3, p_pl4], width=1)

        for sh_pt in (p_l_shoulder, p_r_shoulder):
            pygame.draw.circle(surface, (180, 26, 45), (int(sh_pt[0]), int(sh_pt[1])), max(2, int(3.8 * scale)))
            pygame.draw.circle(surface, (255, 185, 30), (int(sh_pt[0]), int(sh_pt[1])), max(1, int(1.8 * scale)))

        # 5. Weapon & Laser Sight
        arm_reach = 11.0 * scale
        hand_r_x = hx + perp_x * (sh_w * 0.78) + cos_a * arm_reach
        hand_r_y = hy + perp_y * (sh_w * 0.78) + sin_a * arm_reach
        hand_l_x = hx + perp_x * (-sh_w * 0.62) + cos_a * (arm_reach * 0.72)
        hand_l_y = hy + perp_y * (-sh_w * 0.62) + sin_a * (arm_reach * 0.72)

        pygame.draw.line(surface, (32, 24, 32), p_r_shoulder, (hand_r_x, hand_r_y), max(2, int(4.0 * scale)))
        pygame.draw.line(surface, (32, 24, 32), p_l_shoulder, (hand_l_x, hand_l_y), max(2, int(4.0 * scale)))
        pygame.draw.circle(surface, (18, 14, 18), (int(hand_r_x), int(hand_r_y)), max(1, int(2.6 * scale)))
        pygame.draw.circle(surface, (18, 14, 18), (int(hand_l_x), int(hand_l_y)), max(1, int(2.6 * scale)))

        barrel_x = hand_r_x + cos_a * (7.0 * scale)
        barrel_y = hand_r_y + sin_a * (7.0 * scale)
        pygame.draw.line(surface, (45, 45, 55), (hand_r_x, hand_r_y), (barrel_x, barrel_y), max(2, int(3.2 * scale)))
        pygame.draw.circle(surface, (255, 30, 50), (int(barrel_x), int(barrel_y)), max(1, int(2.2 * scale)))

        laser_len = cell_size * 1.4
        laser_end_x = barrel_x + cos_a * laser_len
        laser_end_y = barrel_y + sin_a * laser_len
        pygame.draw.line(surface, (255, 30, 50), (barrel_x, barrel_y), (laser_end_x, laser_end_y), 1)
        dot_pulse = 1.0 + 0.25 * math.sin(anim_time * 12.0)
        pygame.draw.circle(surface, (255, 30, 50), (int(laser_end_x), int(laser_end_y)), int(2.5 * dot_pulse))
        pygame.draw.circle(surface, (255, 235, 240), (int(laser_end_x), int(laser_end_y)), 1)

        # 6. Combat Helmet & NVG
        head_cx = hx + cos_a * (1.8 * scale)
        head_cy = hy + sin_a * (1.8 * scale)
        head_r = 7.8 * scale

        pygame.draw.circle(surface, (24, 18, 24), (int(head_cx), int(head_cy)), int(head_r + 0.5))
        pygame.draw.circle(surface, (42, 34, 44), (int(head_cx - cos_a * (1.5 * scale)), int(head_cy - sin_a * (1.5 * scale))), int(head_r * 0.95))
        pygame.draw.circle(surface, (22, 16, 24), (int(head_cx - cos_a * (1.5 * scale)), int(head_cy - sin_a * (1.5 * scale))), int(head_r * 0.95), width=1)

        nvg_dist = 3.0 * scale
        nvg_fwd = 3.8 * scale
        l_nvg_x = head_cx + perp_x * (-nvg_dist) + cos_a * nvg_fwd
        l_nvg_y = head_cy + perp_y * (-nvg_dist) + sin_a * nvg_fwd
        r_nvg_x = head_cx + perp_x * (nvg_dist) + cos_a * nvg_fwd
        r_nvg_y = head_cy + perp_y * (nvg_dist) + sin_a * nvg_fwd

        c_nvg_x = head_cx + cos_a * (nvg_fwd + 1.2 * scale)
        c_nvg_y = head_cy + sin_a * (nvg_fwd + 1.2 * scale)

        nvg_r = max(2, int(2.6 * scale))
        pygame.draw.circle(surface, (255, 25, 48), (int(l_nvg_x), int(l_nvg_y)), nvg_r)
        pygame.draw.circle(surface, (255, 25, 48), (int(r_nvg_x), int(r_nvg_y)), nvg_r)
        pygame.draw.circle(surface, (255, 25, 48), (int(c_nvg_x), int(c_nvg_y)), max(1, int(1.8 * scale)))

        pygame.draw.circle(surface, (255, 235, 240), (int(l_nvg_x), int(l_nvg_y)), max(1, int(1.2 * scale)))
        pygame.draw.circle(surface, (255, 235, 240), (int(r_nvg_x), int(r_nvg_y)), max(1, int(1.2 * scale)))
        pygame.draw.circle(surface, (255, 235, 240), (int(c_nvg_x), int(c_nvg_y)), 1)

        # 7. Hunter Callsign Pill
        h_tag = font_small.render(f"SENTINEL-0{hunter_id}", True, (255, 85, 95))
        h_rect = h_tag.get_rect(center=(int(hx), int(hy - cell_size * 0.44)))
        h_pill = h_rect.inflate(8, 2)
        pygame.draw.rect(surface, (24, 12, 16), h_pill, border_radius=3)
        pygame.draw.rect(surface, (200, 35, 55), h_pill, width=1, border_radius=3)
        surface.blit(h_tag, h_rect)
