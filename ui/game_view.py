"""
UI Game View: Interactive tactical dungeon labyrinth renderer.
Matches reference mockup media_1795251761856_5273e794.jpg 1:1.

Features:
- Ancient dungeon stone tile floor with mortar grooves, intersection junction dots, moss, and star sparkles.
- Outer thick carved stone chamber frame.
- Ornate emerald green ceremonial "START" carpet at (0, 0) with golden fringe tassels on left/right.
- 3D ancient carved stone monument wall blocks ("W") with metal straps, brass rivets, runes, and moss.
- Glowing golden dungeon key ("K") tilted at 45 degrees with aura and diamond sparkles.
- Safe-route breadcrumb glowing neon green capsule dots.
- Human player operative (cloaked adventurer with leather hood, boots, holding lantern, with yellow guide arrows).
- Knight sentinel hunters ("H") with steel visored greathelms, red cape, lantern, vision cones, and floating "H" badge.
- Exit portal ("EXIT") with carved stone lintel, iron portcullis bars, and centered padlock.
"""

import math
from typing import Tuple, List, Optional
import pygame

from .art_helpers import draw_dungeon_background, draw_padlock


class GameViewRenderer:
    """Renders the in-game tactical labyrinth, entities, and visual navigation aids."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self._cached_cone_surf: Optional[pygame.Surface] = None
        self._cached_light_surf: Optional[pygame.Surface] = None

        # Typography
        self.font_start = pygame.font.SysFont("impact", 24)
        self.font_exit = pygame.font.SysFont("impact", 20)
        self.font_badge = pygame.font.SysFont("impact", 22)
        self.font_small = pygame.font.SysFont("trebuchetms,tahoma,arial", 13, bold=True)
        self.font_icon = pygame.font.SysFont("impact", 22)

    def compute_grid_geometry(
        self,
        grid_size: int,
        hud_height: int = 220
    ) -> Tuple[float, float, float]:
        """
        Dynamically scale cell pixel sizes so the chosen N x N grid fits cleanly
        centered above the bottom HUD console with generous margins.
        """
        top_margin = 52
        bottom_limit = self.screen_height - hud_height - 18
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
        Render the complete retro-pixel RPG dungeon chamber matching media_1795251761856_5273e794.jpg.
        """
        grid_w = cell_size * grid_size
        grid_h = cell_size * grid_size
        grid_rect = pygame.Rect(origin_x, origin_y, grid_w, grid_h)

        # 1. Outer Dark Dungeon Stone Background
        draw_dungeon_background(surface, self.screen_width, self.screen_height)

        # 2. Chamber Shadow & Outer Stone Frame
        pygame.draw.rect(surface, (14, 10, 6), grid_rect.move(0, 6), border_radius=4)
        # Heavy outer carved sandstone chamber boundary
        pygame.draw.rect(surface, (72, 58, 38), grid_rect.inflate(14, 14), border_radius=4)
        pygame.draw.rect(surface, (105, 86, 58), grid_rect.inflate(8, 8), border_radius=3)
        pygame.draw.rect(surface, (45, 34, 22), grid_rect.inflate(14, 14), width=3, border_radius=4)
        pygame.draw.rect(surface, (36, 26, 16), grid_rect, width=2)

        # 3. Ancient Sandstone Cobblestone Floor Tiles matching mockup crops
        for r in range(grid_size):
            for c in range(grid_size):
                cell_rect = pygame.Rect(origin_x + c * cell_size, origin_y + r * cell_size, cell_size, cell_size)

                # Base sandstone colors matching mockup crops
                base_col = (152, 134, 92) if (r + c) % 2 == 0 else (142, 124, 82)
                pygame.draw.rect(surface, base_col, cell_rect)

                # Subtle top/left bevel highlight and bottom/right shadow
                pygame.draw.line(surface, (178, 158, 114), (cell_rect.left + 2, cell_rect.top + 2), (cell_rect.right - 3, cell_rect.top + 2), 2)
                pygame.draw.line(surface, (178, 158, 114), (cell_rect.left + 2, cell_rect.top + 2), (cell_rect.left + 2, cell_rect.bottom - 3), 2)
                pygame.draw.line(surface, (108, 92, 58), (cell_rect.left + 2, cell_rect.bottom - 2), (cell_rect.right - 2, cell_rect.bottom - 2), 2)
                pygame.draw.line(surface, (108, 92, 58), (cell_rect.right - 2, cell_rect.top + 2), (cell_rect.right - 2, cell_rect.bottom - 2), 2)

                # Mortar grout line
                pygame.draw.rect(surface, (48, 36, 22), cell_rect, width=2)

                # Organic lichen & moss clusters (deterministic pseudo-random based on grid coordinate)
                moss_seed = (r * 19 + c * 37) % 17
                if moss_seed in (2, 5, 8, 12):
                    mx = cell_rect.left + int(cell_size * (0.2 + (moss_seed % 5) * 0.12))
                    my = cell_rect.top + int(cell_size * (0.2 + ((moss_seed * 3) % 5) * 0.12))
                    pygame.draw.circle(surface, (82, 122, 58), (mx, my), 3)
                    pygame.draw.circle(surface, (54, 88, 38), (mx + 2, my + 1), 2)
                    pygame.draw.circle(surface, (102, 142, 72), (mx - 2, my + 1), 2)

                # Golden sparkles / dust specks
                sparkle_seed = (r * 31 + c * 23) % 19
                if sparkle_seed in (3, 7, 14):
                    sx = cell_rect.left + int(cell_size * (0.3 + (sparkle_seed % 4) * 0.15))
                    sy = cell_rect.top + int(cell_size * (0.3 + ((sparkle_seed * 2) % 4) * 0.15))
                    # 4-point diamond star sparkle matching crop_key.png
                    pygame.draw.line(surface, (255, 235, 120), (sx - 4, sy), (sx + 4, sy), 2)
                    pygame.draw.line(surface, (255, 235, 120), (sx, sy - 4), (sx, sy + 4), 2)
                    pygame.draw.circle(surface, (255, 255, 225), (sx, sy), 1)

        # Draw rounded dark mortar junction dots at tile intersection corners
        dot_r = max(3, int(cell_size * 0.045))
        for r in range(grid_size + 1):
            for c in range(grid_size + 1):
                jx = int(origin_x + c * cell_size)
                jy = int(origin_y + r * cell_size)
                pygame.draw.circle(surface, (36, 26, 14), (jx, jy), dot_r)

        # Dynamic Wall Relocation Visual Pulse Alert
        if wall_shift_alert > 0:
            alpha = int(min(1.0, wall_shift_alert * 2.0) * 85)
            alert_surf = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
            alert_surf.fill((255, 200, 50, alpha))
            surface.blit(alert_surf, (origin_x, origin_y))

        # 4. START TILE (0, 0): Ornate Emerald Green Ceremonial Rug matching crop_start.png
        start_rect = pygame.Rect(origin_x + 8, origin_y + 8, cell_size - 16, cell_size - 16)
        # Drop shadow
        pygame.draw.rect(surface, (16, 10, 5), start_rect.move(0, 3), border_radius=3)

        # Golden Fringe Tassels along Left and Right edges matching crop_start.png
        num_fringes = 12
        f_gap = start_rect.height / (num_fringes + 1)
        for i in range(1, num_fringes + 1):
            fy = int(start_rect.top + i * f_gap)
            # Left tassel
            pygame.draw.line(surface, (45, 24, 8), (start_rect.left - 5, fy), (start_rect.left, fy), 3)
            pygame.draw.line(surface, (240, 195, 55), (start_rect.left - 4, fy), (start_rect.left, fy), 2)
            # Right tassel
            pygame.draw.line(surface, (45, 24, 8), (start_rect.right, fy), (start_rect.right + 5, fy), 3)
            pygame.draw.line(surface, (240, 195, 55), (start_rect.right, fy), (start_rect.right + 4, fy), 2)

        # Emerald green rug body
        pygame.draw.rect(surface, (24, 108, 62), start_rect, border_radius=3)
        pygame.draw.rect(surface, (14, 62, 34), start_rect, width=2, border_radius=3)

        # Inner decorative emerald border with corner fleurons
        inner_rug = start_rect.inflate(-10, -10)
        pygame.draw.rect(surface, (42, 162, 92), inner_rug, width=2, border_radius=2)
        # Corner accent flecks
        for cx_pt, cy_pt in [
            (inner_rug.left + 4, inner_rug.top + 4),
            (inner_rug.right - 4, inner_rug.top + 4),
            (inner_rug.left + 4, inner_rug.bottom - 4),
            (inner_rug.right - 4, inner_rug.bottom - 4)
        ]:
            pygame.draw.rect(surface, (85, 215, 140), pygame.Rect(cx_pt - 2, cy_pt - 2, 4, 4))

        # Text: "START"
        start_txt = self.font_start.render("START", True, (255, 250, 195))
        start_txt_s = self.font_start.render("START", True, (14, 10, 8))
        s_rc = start_txt.get_rect(center=start_rect.center)
        # Bold outline
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1)]:
            surface.blit(start_txt_s, s_rc.move(ox, oy))
        surface.blit(start_txt, s_rc)

        # 5. ANCIENT STONE MONUMENT WALL BLOCKS ("W") matching crop_wall.png
        for (wr, wc) in walls:
            wx = origin_x + wc * cell_size
            wy = origin_y + wr * cell_size
            pad = max(2.0, cell_size * 0.04)
            w_w = cell_size - pad * 2
            w_h = cell_size - pad * 2
            block_rect = pygame.Rect(wx + pad, wy + pad, w_w, w_h)

            # Drop shadow
            pygame.draw.rect(surface, (16, 10, 6), block_rect.move(0, 4), border_radius=3)

            # 3D Extrusion: Top face (ledge) and Front face
            top_h = int(w_h * 0.28)
            front_h = int(w_h * 0.72)
            top_rect = pygame.Rect(block_rect.left, block_rect.top, w_w, top_h)
            front_rect = pygame.Rect(block_rect.left, block_rect.top + top_h, w_w, front_h)

            # Shading
            pygame.draw.rect(surface, (165, 145, 110), top_rect, border_top_left_radius=3, border_top_right_radius=3)
            pygame.draw.rect(surface, (120, 104, 76), front_rect, border_bottom_left_radius=3, border_bottom_right_radius=3)
            pygame.draw.rect(surface, (42, 30, 18), block_rect, width=2, border_radius=3)

            # Top ledge crack detail
            pygame.draw.line(surface, (75, 62, 42), (top_rect.centerx - 6, top_rect.top + 2), (top_rect.centerx + 4, top_rect.bottom - 2), 2)

            # Recessed front panel
            inset_front = front_rect.inflate(-10, -8)
            pygame.draw.rect(surface, (102, 88, 60), inset_front, border_radius=2)
            pygame.draw.rect(surface, (54, 42, 28), inset_front, width=2, border_radius=2)

            # In mockup: wall at (1, 1) has pure carved glyph, others have iron straps with rivets
            has_straps = not (wr == 1 and wc == 1)
            if has_straps:
                strap1_x = int(block_rect.left + w_w * 0.22)
                strap2_x = int(block_rect.left + w_w * 0.72)
                strap_w = max(5, int(cell_size * 0.08))
                for sx in (strap1_x, strap2_x):
                    s_rect = pygame.Rect(sx, block_rect.top, strap_w, w_h)
                    pygame.draw.rect(surface, (48, 42, 38), s_rect)
                    pygame.draw.line(surface, (84, 76, 70), (sx + 1, block_rect.top), (sx + 1, block_rect.bottom), 1)
                    pygame.draw.rect(surface, (28, 24, 20), s_rect, width=1)
                    # Brass rivets
                    pygame.draw.circle(surface, (28, 22, 16), (sx + strap_w // 2, block_rect.top + 5), 3)
                    pygame.draw.circle(surface, (245, 205, 55), (sx + strap_w // 2, block_rect.top + 5), 2)
                    pygame.draw.circle(surface, (28, 22, 16), (sx + strap_w // 2, block_rect.bottom - 6), 3)
                    pygame.draw.circle(surface, (245, 205, 55), (sx + strap_w // 2, block_rect.bottom - 6), 2)
            else:
                # Carved glyph on rune wall
                cx_block = inset_front.centerx
                cy_block = inset_front.centery
                rune_r = int(cell_size * 0.16)
                pygame.draw.arc(surface, (48, 36, 22), pygame.Rect(cx_block - rune_r, cy_block - rune_r, rune_r * 2, rune_r * 2), 0.5, 4.5, 3)
                pygame.draw.arc(surface, (48, 36, 22), pygame.Rect(cx_block - rune_r // 2, cy_block - rune_r // 2, rune_r, rune_r), 3.5, 7.5, 2)

            # Green moss hanging from ledge
            pygame.draw.circle(surface, (68, 112, 48), (block_rect.left + 8, top_rect.bottom), 4)
            pygame.draw.circle(surface, (48, 82, 34), (block_rect.left + 12, top_rect.bottom + 3), 3)

            # Floating stylized golden 'W' label on wall at (0, 5) or top wall
            if (wr, wc) == (0, 5):
                w_lbl = self.font_icon.render("W", True, (255, 235, 120))
                w_lbl_s = self.font_icon.render("W", True, (32, 18, 8))
                w_rc = w_lbl.get_rect(center=(block_rect.centerx, block_rect.top - 12))
                for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    surface.blit(w_lbl_s, w_rc.move(ox, oy))
                surface.blit(w_lbl, w_rc)

        # 6. EXIT GATEWAY: Carved Stone Archway matching reference media_1795391199225_787dcc85.png 1:1
        ex_x = origin_x + exit_pos[1] * cell_size
        ex_y = origin_y + exit_pos[0] * cell_size
        cell_exit_rect = pygame.Rect(ex_x + 3, ex_y + 3, cell_size - 6, cell_size - 6)

        # Lintel stone height (approx 40% of the cell)
        lintel_h = max(20, int(cell_size * 0.40))
        lintel_rect = pygame.Rect(cell_exit_rect.left, cell_exit_rect.top, cell_exit_rect.width, lintel_h)
        gate_rect = pygame.Rect(cell_exit_rect.left, cell_exit_rect.top + lintel_h, cell_exit_rect.width, cell_exit_rect.height - lintel_h)

        # Stone archway outer boundary with rounded top corners
        pygame.draw.rect(surface, (120, 102, 74), lintel_rect, border_top_left_radius=4, border_top_right_radius=4)
        pygame.draw.rect(surface, (148, 130, 98), lintel_rect.inflate(-4, -4), border_top_left_radius=3, border_top_right_radius=3)
        pygame.draw.rect(surface, (42, 30, 18), lintel_rect, width=2, border_top_left_radius=4, border_top_right_radius=4)

        # "EXIT" carved text matching reference: cream/yellow bold Impact font with dark outline
        font_exit_sz = max(11, min(22, int(lintel_h * 0.65)))
        font_exit_dynamic = pygame.font.SysFont("impact", font_exit_sz)
        exit_col = (251, 231, 158)
        exit_txt = font_exit_dynamic.render("EXIT", True, exit_col)
        exit_txt_s = font_exit_dynamic.render("EXIT", True, (24, 16, 10))
        e_rc = exit_txt.get_rect(center=lintel_rect.center)
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-2, 0), (2, 0), (0, -2), (0, 2)]:
            surface.blit(exit_txt_s, e_rc.move(ox, oy))
        surface.blit(exit_txt, e_rc)

        # Dark dungeon chamber pit behind gate
        pygame.draw.rect(surface, (14, 12, 16), gate_rect)
        pygame.draw.rect(surface, (42, 30, 18), gate_rect, width=2)

        # 5 Vertical iron portcullis bars matching reference
        num_bars = 5
        bar_gap = gate_rect.width / (num_bars + 1)
        bar_h = gate_rect.height if not has_key else max(4, int(gate_rect.height * 0.25))

        for i in range(1, num_bars + 1):
            bx = int(gate_rect.left + i * bar_gap)
            pygame.draw.line(surface, (24, 25, 28), (bx, gate_rect.top), (bx, gate_rect.top + bar_h), 4)
            pygame.draw.line(surface, (68, 72, 82), (bx, gate_rect.top), (bx, gate_rect.top + bar_h), 3)
            pygame.draw.line(surface, (130, 138, 150), (bx - 1, gate_rect.top), (bx - 1, gate_rect.top + bar_h), 1)

        # When key collected: gate is open with subtle warm escape radiance
        if has_key:
            p_glow = 1.0 + 0.15 * math.sin(anim_time * 5.0)
            glow_surf = pygame.Surface((gate_rect.width, gate_rect.height), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 225, 100, int(65 * p_glow)), (gate_rect.width // 2, gate_rect.height // 2), int(gate_rect.width * 0.4))
            surface.blit(glow_surf, gate_rect.topleft)

        # 7. GOLDEN DUNGEON KEY ("K") matching crop_key.png
        if not has_key:
            kx = origin_x + key_pos[1] * cell_size + cell_size / 2.0
            ky = origin_y + key_pos[0] * cell_size + cell_size / 2.0
            k_bob = math.sin(anim_time * 4.5) * (cell_size * 0.05)
            ky += k_bob

            # Concentric soft translucent golden aura
            k_pulse = 1.0 + 0.15 * math.sin(anim_time * 5.0)
            aura_surf = pygame.Surface((int(cell_size * 1.6), int(cell_size * 1.6)), pygame.SRCALPHA)
            aura_cx = aura_surf.get_width() // 2
            aura_cy = aura_surf.get_height() // 2
            pygame.draw.circle(aura_surf, (255, 220, 80, 50), (aura_cx, aura_cy), int(cell_size * 0.38 * k_pulse))
            pygame.draw.circle(aura_surf, (255, 240, 130, 90), (aura_cx, aura_cy), int(cell_size * 0.22 * k_pulse))
            surface.blit(aura_surf, aura_surf.get_rect(center=(int(kx), int(ky))))

            # 4 Diamond sparkle glints around the key matching crop_key.png
            for i in range(4):
                sp_ang = anim_time * 2.8 + i * (math.pi / 2.0)
                sp_dist = cell_size * 0.36
                sp_x = kx + math.cos(sp_ang) * sp_dist
                sp_y = ky + math.sin(sp_ang) * sp_dist
                pygame.draw.line(surface, (255, 245, 160), (sp_x - 4, sp_y), (sp_x + 4, sp_y), 2)
                pygame.draw.line(surface, (255, 245, 160), (sp_x, sp_y - 4), (sp_x, sp_y + 4), 2)
                pygame.draw.circle(surface, (255, 255, 230), (sp_x, sp_y), 1)

            # Golden Key Sprite tilted at 45 degrees
            kw = int(cell_size * 0.40)
            # Bow ring at top-right
            ring_cx = kx + kw * 0.30
            ring_cy = ky - kw * 0.30
            ring_r = max(9, int(cell_size * 0.13))
            pygame.draw.circle(surface, (45, 22, 8), (int(ring_cx), int(ring_cy)), ring_r + 2)
            pygame.draw.circle(surface, (255, 215, 45), (int(ring_cx), int(ring_cy)), ring_r)
            pygame.draw.circle(surface, (255, 250, 190), (int(ring_cx - 1), int(ring_cy - 1)), int(ring_r * 0.75))
            pygame.draw.circle(surface, (45, 22, 8), (int(ring_cx), int(ring_cy)), int(ring_r * 0.45))

            # Stem pointing towards bottom-left
            p_start = (ring_cx - int(ring_r * 0.6), ring_cy + int(ring_r * 0.6))
            p_end = (kx - kw * 0.38, ky + kw * 0.38)
            pygame.draw.line(surface, (45, 22, 8), p_start, p_end, 9)
            pygame.draw.line(surface, (255, 215, 45), p_start, p_end, 6)
            pygame.draw.line(surface, (255, 250, 190), p_start, p_end, 2)

            # Two key teeth at bottom-left
            t1_s = (p_end[0] + 6, p_end[1] - 6)
            t1_e = (t1_s[0] - 8, t1_s[1] - 8)
            pygame.draw.line(surface, (45, 22, 8), t1_s, t1_e, 6)
            pygame.draw.line(surface, (255, 215, 45), t1_s, t1_e, 4)

            t2_s = (p_end[0] + 12, p_end[1] - 12)
            t2_e = (t2_s[0] - 6, t2_s[1] - 6)
            pygame.draw.line(surface, (45, 22, 8), t2_s, t2_e, 6)
            pygame.draw.line(surface, (255, 215, 45), t2_s, t2_e, 4)

            # Floating golden "K" label
            k_lbl = self.font_icon.render("K", True, (255, 235, 120))
            k_lbl_s = self.font_icon.render("K", True, (38, 18, 6))
            k_rc = k_lbl.get_rect(center=(int(kx), int(ky - cell_size * 0.42)))
            for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                surface.blit(k_lbl_s, k_rc.move(ox, oy))
            surface.blit(k_lbl, k_rc)

        # 8. SAFE-ROUTE BREADCRUMBS: 5 Glowing Green Capsule Dots
        if recommended_path and len(recommended_path) >= 1:
            target_pt = recommended_path[0]
            tr, tc = target_pt[0], target_pt[1]
            t_center_x = origin_x + tc * cell_size + cell_size / 2.0
            t_center_y = origin_y + tr * cell_size + cell_size / 2.0

            dx = t_center_x - player_x
            dy = t_center_y - player_y
            total_dist = math.hypot(dx, dy)

            if total_dist > 8.0:
                num_dots = 5
                for step_idx in range(1, num_dots + 1):
                    frac = step_idx / (num_dots + 1)
                    dot_x = player_x + dx * frac
                    dot_y = player_y + dy * frac

                    # Glowing green pill / capsule dot
                    dot_w = max(14, int(cell_size * 0.16))
                    dot_h = max(8, int(cell_size * 0.09))
                    d_rect = pygame.Rect(int(dot_x - dot_w // 2), int(dot_y - dot_h // 2), dot_w, dot_h)

                    # Soft green halo
                    halo_rect = d_rect.inflate(8, 6)
                    halo_surf = pygame.Surface((halo_rect.width, halo_rect.height), pygame.SRCALPHA)
                    pygame.draw.ellipse(halo_surf, (50, 255, 130, 85), halo_surf.get_rect())
                    surface.blit(halo_surf, halo_rect)

                    # Bright neon emerald core
                    pygame.draw.ellipse(surface, (54, 255, 125), d_rect)
                    pygame.draw.ellipse(surface, (210, 255, 230), d_rect.inflate(-4, -2))

        # 9. HUMAN SENTINEL HUNTERS ("H") with Lantern Vision Cones matching crop_hunter.png
        for h in hunters:
            self._draw_human_hunter(surface, h.visual_x, h.visual_y, cell_size, h.facing_dr, h.facing_dc, h.hunter_id, anim_time, font_small)

        # 10. HUMAN PLAYER OPERATIVE (Cloaked Adventurer) & Directional Yellow Guide Arrows matching crop_player.png
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
        """Render the Cloaked Adventurer Operative matching crop_player.png."""
        scale = max(0.65, cell_size / 60.0)

        # 1. Drop shadow
        shadow_rect = pygame.Rect(int(px - 16 * scale), int(py + 10 * scale), int(32 * scale), int(14 * scale))
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (16, 10, 6, 150), shadow_surf.get_rect())
        surface.blit(shadow_surf, shadow_rect)

        # 2. Localized Warm Lantern Light Glow on player's tile
        lantern_x = px + 15 * scale
        lantern_y = py + 4 * scale
        glow_r = int(cell_size * 0.42)
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 225, 110, 50), (glow_r, glow_r), glow_r)
        glow_inner = int(glow_r * 0.45)
        pygame.draw.circle(glow_surf, (255, 245, 160, 90), (glow_r, glow_r), glow_inner)
        surface.blit(glow_surf, glow_surf.get_rect(center=(int(lantern_x), int(lantern_y))))

        # 3. Cloaked Adventurer Body
        # Leather hood & head
        hood_cx = px - 2 * scale
        hood_cy = py - 7 * scale
        hood_r = int(12 * scale)
        # Hood back peak
        peak_pts = [(hood_cx - 10 * scale, hood_cy - 4 * scale), (hood_cx - 15 * scale, hood_cy - 8 * scale), (hood_cx - 6 * scale, hood_cy - 12 * scale)]
        pygame.draw.polygon(surface, (36, 20, 10), peak_pts)
        pygame.draw.polygon(surface, (132, 86, 50), peak_pts)
        # Main hood dome
        pygame.draw.circle(surface, (36, 20, 10), (int(hood_cx), int(hood_cy)), hood_r + 2)
        pygame.draw.circle(surface, (132, 86, 50), (int(hood_cx), int(hood_cy)), hood_r)
        pygame.draw.circle(surface, (165, 112, 68), (int(hood_cx - 2 * scale), int(hood_cy - 2 * scale)), int(hood_r * 0.65))

        # Face opening
        face_rect = pygame.Rect(int(hood_cx - 2 * scale), int(hood_cy - 4 * scale), int(12 * scale), int(10 * scale))
        pygame.draw.ellipse(surface, (250, 205, 172), face_rect)
        # Hair bangs
        pygame.draw.arc(surface, (85, 48, 25), face_rect, 0.5, 2.8, int(3 * scale))
        # Two cute eye pixels
        pygame.draw.rect(surface, (32, 18, 10), pygame.Rect(int(hood_cx + 2 * scale), int(hood_cy - 1 * scale), max(2, int(2 * scale)), max(2, int(2 * scale))))
        pygame.draw.rect(surface, (32, 18, 10), pygame.Rect(int(hood_cx + 7 * scale), int(hood_cy - 1 * scale), max(2, int(2 * scale)), max(2, int(2 * scale))))

        # Leather tunic & straps
        body_rect = pygame.Rect(int(px - 11 * scale), int(py + 3 * scale), int(20 * scale), int(15 * scale))
        pygame.draw.rect(surface, (36, 20, 10), body_rect.inflate(2, 2), border_radius=2)
        pygame.draw.rect(surface, (105, 68, 38), body_rect, border_radius=2)
        # Belts & straps
        pygame.draw.line(surface, (65, 38, 18), (body_rect.left, body_rect.top + 5 * scale), (body_rect.right, body_rect.top + 5 * scale), 2)
        pygame.draw.line(surface, (65, 38, 18), (body_rect.left, body_rect.top + 10 * scale), (body_rect.right, body_rect.top + 10 * scale), 2)

        # Boots
        pygame.draw.rect(surface, (48, 30, 16), pygame.Rect(int(px - 9 * scale), int(py + 16 * scale), int(7 * scale), int(6 * scale)), border_radius=2)
        pygame.draw.rect(surface, (48, 30, 16), pygame.Rect(int(px + 2 * scale), int(py + 16 * scale), int(7 * scale), int(6 * scale)), border_radius=2)

        # 4. Outstretched Hand & Hanging Lantern
        pygame.draw.line(surface, (105, 68, 38), (px + 6 * scale, py + 5 * scale), (lantern_x, lantern_y), max(2, int(2.5 * scale)))
        l_rect = pygame.Rect(int(lantern_x - 4 * scale), int(lantern_y - 4 * scale), int(9 * scale), int(12 * scale))
        pygame.draw.rect(surface, (48, 34, 20), l_rect, border_radius=2)
        pygame.draw.rect(surface, (255, 225, 95), l_rect.inflate(-2, -2), border_radius=1)
        pygame.draw.rect(surface, (255, 255, 220), pygame.Rect(int(lantern_x - 1 * scale), int(lantern_y - 2 * scale), int(3 * scale), int(6 * scale)))
        pygame.draw.rect(surface, (218, 165, 45), l_rect, width=1, border_radius=2)

        # 5. Golden Directional Navigation Arrows (East and South) matching crop_player.png
        arrow_dist = cell_size * 0.44
        a_pulse = 1.0 + 0.10 * math.sin(anim_time * 6.0)

        # Arrow Right (East: >)
        ar_cx = px + arrow_dist
        ar_cy = py
        ar_w = int(14 * scale * a_pulse)
        ar_h = int(18 * scale * a_pulse)
        ar_pts = [(ar_cx + ar_w // 2, ar_cy), (ar_cx - ar_w // 2, ar_cy - ar_h // 2), (ar_cx - ar_w // 2, ar_cy + ar_h // 2)]
        pygame.draw.polygon(surface, (48, 24, 8), [(x, y + 2) for x, y in ar_pts])
        pygame.draw.polygon(surface, (255, 215, 55), ar_pts)
        pygame.draw.polygon(surface, (255, 248, 175), [(ar_cx + ar_w // 4, ar_cy), (ar_cx - ar_w // 3, ar_cy - ar_h // 3), (ar_cx - ar_w // 3, ar_cy + ar_h // 3)])
        pygame.draw.polygon(surface, (48, 24, 8), ar_pts, 2)

        # Arrow Down (South: v)
        ad_cx = px
        ad_cy = py + arrow_dist
        ad_w = int(18 * scale * a_pulse)
        ad_h = int(14 * scale * a_pulse)
        ad_pts = [(ad_cx, ad_cy + ad_h // 2), (ad_cx - ad_w // 2, ad_cy - ad_h // 2), (ad_cx + ad_w // 2, ad_cy - ad_h // 2)]
        pygame.draw.polygon(surface, (48, 24, 8), [(x, y + 2) for x, y in ad_pts])
        pygame.draw.polygon(surface, (255, 215, 55), ad_pts)
        pygame.draw.polygon(surface, (255, 248, 175), [(ad_cx, ad_cy + ad_h // 4), (ad_cx - ad_w // 3, ad_cy - ad_h // 3), (ad_cx + ad_w // 3, ad_cy - ad_h // 3)])
        pygame.draw.polygon(surface, (48, 24, 8), ad_pts, 2)

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
        """Render Knight Sentinel Hunter with greathelm, red cape, lantern, and beam cone matching crop_hunter.png."""
        scale = max(0.65, cell_size / 60.0)

        # Facing angle
        if facing_dr == 0 and facing_dc == 0:
            angle = 0.0
        else:
            angle = math.atan2(facing_dr, facing_dc)

        # 1. Lantern Vision Light Cone (Flashlight Beam)
        lantern_off_x = hx + (15 * scale if facing_dc >= 0 else -15 * scale)
        lantern_off_y = hy + 4 * scale

        cone_len = cell_size * 2.3
        if self._cached_cone_surf is None:
            self._cached_cone_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self._cached_cone_surf.fill((0, 0, 0, 0))

        p_apex = (lantern_off_x, lantern_off_y)
        half_fov = math.radians(22)
        p_left = (lantern_off_x + math.cos(angle - half_fov) * cone_len, lantern_off_y + math.sin(angle - half_fov) * cone_len)
        p_right = (lantern_off_x + math.cos(angle + half_fov) * cone_len, lantern_off_y + math.sin(angle + half_fov) * cone_len)

        # Smooth warm flashlight beam
        pygame.draw.polygon(self._cached_cone_surf, (255, 235, 160, 38), [p_apex, p_left, p_right])
        # Core beam
        core_fov = math.radians(11)
        p_cleft = (lantern_off_x + math.cos(angle - core_fov) * (cone_len * 1.05), lantern_off_y + math.sin(angle - core_fov) * (cone_len * 1.05))
        p_cright = (lantern_off_x + math.cos(angle + core_fov) * (cone_len * 1.05), lantern_off_y + math.sin(angle + core_fov) * (cone_len * 1.05))
        pygame.draw.polygon(self._cached_cone_surf, (255, 245, 190, 75), [p_apex, p_cleft, p_cright])
        surface.blit(self._cached_cone_surf, (0, 0))

        # 2. Drop Shadow
        shadow_rect = pygame.Rect(int(hx - 16 * scale), int(hy + 10 * scale), int(32 * scale), int(14 * scale))
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (15, 8, 6, 150), shadow_surf.get_rect())
        surface.blit(shadow_surf, shadow_rect)

        # 3. Flowing Crimson Red Warrior Cape
        cape_dir = 1 if facing_dc <= 0 else -1
        cape_pts = [
            (hx - 14 * scale, hy - 4 * scale),
            (hx + 14 * scale, hy - 4 * scale),
            (hx + 16 * scale + cape_dir * 4 * scale, hy + 16 * scale),
            (hx - 16 * scale + cape_dir * 4 * scale, hy + 16 * scale)
        ]
        pygame.draw.polygon(surface, (45, 12, 12), [(x, y + 2) for x, y in cape_pts])
        pygame.draw.polygon(surface, (188, 38, 38), cape_pts)
        pygame.draw.polygon(surface, (225, 60, 54), [
            (hx - 10 * scale, hy - 2 * scale),
            (hx + 10 * scale, hy - 2 * scale),
            (hx + 11 * scale, hy + 14 * scale),
            (hx - 11 * scale, hy + 14 * scale)
        ])
        pygame.draw.polygon(surface, (54, 14, 14), cape_pts, 2)

        # 4. Steel Armored Chest & Boots
        pygame.draw.rect(surface, (45, 42, 50), pygame.Rect(int(hx - 10 * scale), int(hy + 15 * scale), int(8 * scale), int(6 * scale)), border_radius=2)
        pygame.draw.rect(surface, (45, 42, 50), pygame.Rect(int(hx + 2 * scale), int(hy + 15 * scale), int(8 * scale), int(6 * scale)), border_radius=2)

        chest_rect = pygame.Rect(int(hx - 9 * scale), int(hy - 2 * scale), int(18 * scale), int(16 * scale))
        pygame.draw.rect(surface, (142, 140, 150), chest_rect, border_radius=2)
        pygame.draw.rect(surface, (180, 178, 190), chest_rect.inflate(-4, -4), border_radius=2)
        pygame.draw.rect(surface, (45, 42, 50), chest_rect, width=2, border_radius=2)
        # Gold belt buckle
        pygame.draw.rect(surface, (220, 175, 45), pygame.Rect(int(hx - 3 * scale), int(hy + 9 * scale), int(6 * scale), int(4 * scale)))

        # 5. Heavy Steel Visored Knight Greathelm
        helm_cx = hx
        helm_cy = hy - 9 * scale
        helm_r = int(11 * scale)
        pygame.draw.circle(surface, (32, 28, 34), (int(helm_cx), int(helm_cy + 1)), helm_r + 2)
        pygame.draw.circle(surface, (120, 118, 128), (int(helm_cx), int(helm_cy)), helm_r)
        # Metallic dome highlight
        pygame.draw.circle(surface, (185, 182, 195), (int(helm_cx - 2 * scale), int(helm_cy - 3 * scale)), int(helm_r * 0.55))
        pygame.draw.circle(surface, (32, 28, 34), (int(helm_cx), int(helm_cy)), helm_r, 2)

        # Horizontal Dark Visor Slit with glowing red/amber eye gleam
        slit_rect = pygame.Rect(int(helm_cx - 7 * scale), int(helm_cy), int(14 * scale), int(4 * scale))
        pygame.draw.rect(surface, (20, 12, 14), slit_rect, border_radius=1)
        # Glowing eye slit
        glow_x = helm_cx + (2 if facing_dc >= 0 else -2) * scale
        pygame.draw.line(surface, (255, 80, 50), (glow_x - 3 * scale, helm_cy + 2 * scale), (glow_x + 3 * scale, helm_cy + 2 * scale), 2)
        pygame.draw.line(surface, (255, 215, 100), (glow_x - 1 * scale, helm_cy + 2 * scale), (glow_x + 1 * scale, helm_cy + 2 * scale), 1)

        # 6. Hand-held Dungeon Lantern
        pygame.draw.line(surface, (120, 118, 128), (hx + (7 if facing_dc >= 0 else -7) * scale, hy + 3 * scale), (lantern_off_x, lantern_off_y), max(2, int(2.5 * scale)))
        l_rect = pygame.Rect(int(lantern_off_x - 4 * scale), int(lantern_off_y - 4 * scale), int(9 * scale), int(12 * scale))
        pygame.draw.rect(surface, (45, 34, 20), l_rect, border_radius=2)
        pygame.draw.rect(surface, (255, 225, 105), l_rect.inflate(-2, -2), border_radius=1)
        pygame.draw.rect(surface, (255, 255, 220), pygame.Rect(int(lantern_off_x - 1 * scale), int(lantern_off_y - 2 * scale), int(3 * scale), int(6 * scale)))
        pygame.draw.rect(surface, (218, 165, 45), l_rect, width=1, border_radius=2)

        # 7. Floating Coral/Red "H" Badge matching crop_hunter.png
        h_lbl = self.font_icon.render("H", True, (250, 85, 75))
        h_lbl_s = self.font_icon.render("H", True, (28, 8, 8))
        h_rc = h_lbl.get_rect(center=(int(hx), int(hy - cell_size * 0.44)))
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            surface.blit(h_lbl_s, h_rc.move(ox, oy))
        surface.blit(h_lbl, h_rc)
