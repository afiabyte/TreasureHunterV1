"""
UI Login Screen: Authentic retro-pixel RPG adventure operative authentication.
Renders aged parchment scroll with 3D adventure typography, royal crown,
recessed wood input fields (Username, Password), chunky emerald [LOG IN] button,
steel-blue [CREATE ACCOUNT] button, "FORGOT PASSWORD?" link,
hero adventurer sprite on the lower left, and relic treasure chest on the lower right.
Matches media_1795243874550_0f52c903.jpg exactly (1:1).
"""

import math
from typing import List, Dict, Any, Optional
import pygame

from .art_helpers import draw_dungeon_background, draw_royal_crown
from .widgets import UIButton, TextInputBox


class LoginScreenRenderer:
    """Renders the authentic retro-pixel RPG adventure Operative Login screen."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self._t_font: Optional[pygame.font.Font] = None
        self._sub_font: Optional[pygame.font.Font] = None
        self._lbl_font: Optional[pygame.font.Font] = None
        self._link_font: Optional[pygame.font.Font] = None

    def _draw_screw(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Render metallic brass screw rivet with dark rim and slot."""
        pygame.draw.circle(surface, (45, 30, 18), (x, y + 1), 7)
        pygame.draw.circle(surface, (215, 165, 60), (x, y), 6)
        pygame.draw.circle(surface, (250, 215, 120), (x - 1, y - 1), 3)
        pygame.draw.circle(surface, (50, 32, 16), (x, y), 2)
        pygame.draw.line(surface, (40, 24, 12), (x - 3, y - 1), (x + 3, y + 1), 1)

    def _draw_wall_torch(self, surface: pygame.Surface, x: int, y: int, anim_time: float = 0.0) -> None:
        """Render left wall sconce and burning torch with animated flame flicker."""
        pygame.draw.rect(surface, (18, 14, 16), (x - 8, y + 8, 16, 26), border_radius=2)
        pygame.draw.rect(surface, (55, 48, 50), (x - 6, y + 10, 12, 22), border_radius=2)
        pygame.draw.line(surface, (28, 22, 24), (x, y + 25), (x, y + 60), 4)
        pygame.draw.ellipse(surface, (55, 48, 50), pygame.Rect(x - 10, y + 14, 20, 8))
        pygame.draw.ellipse(surface, (18, 14, 16), pygame.Rect(x - 10, y + 14, 20, 8), 2)
        pygame.draw.line(surface, (88, 50, 22), (x, y + 20), (x, y - 12), 8)
        pygame.draw.line(surface, (42, 22, 8), (x, y + 20), (x, y - 12), 2)
        flicker = math.sin(anim_time * 16.0) * 3
        flame_pts = [
            (x - 10, y - 8),
            (x - 14, y - 24),
            (x - 6, y - 44 + int(flicker)),
            (x + 2, y - 60 + int(flicker * 1.3)),
            (x + 8, y - 40),
            (x + 14, y - 22),
            (x + 10, y - 8),
        ]
        pygame.draw.polygon(surface, (235, 70, 12), flame_pts)
        pygame.draw.polygon(surface, (255, 195, 30), [(px, py + 5) for px, py in flame_pts[1:6]])
        pygame.draw.circle(surface, (255, 248, 185), (x, y - 22), 7)

    def _draw_skeleton(self, surface: pygame.Surface, sx: int, sy: int) -> None:
        """Render skull and bones on stone floor."""
        bone = (215, 208, 192)
        sh = (18, 10, 8)
        dark = (26, 16, 12)
        pygame.draw.circle(surface, sh, (sx, sy + 2), 16)
        pygame.draw.circle(surface, bone, (sx, sy), 15)
        pygame.draw.rect(surface, bone, (sx - 8, sy + 7, 16, 11), border_radius=2)
        pygame.draw.rect(surface, sh, (sx - 8, sy + 7, 16, 11), width=1, border_radius=2)
        pygame.draw.ellipse(surface, dark, pygame.Rect(sx - 10, sy - 3, 7, 10))
        pygame.draw.ellipse(surface, dark, pygame.Rect(sx + 3, sy - 3, 7, 10))
        pygame.draw.circle(surface, dark, (sx, sy + 5), 2)
        for tx in [-5, -2, 2, 5]:
            pygame.draw.line(surface, dark, (sx + tx, sy + 11), (sx + tx, sy + 16), 1)
        f1 = (sx - 30, sy + 28)
        f2 = (sx + 36, sy + 24)
        pygame.draw.line(surface, sh, (f1[0], f1[1] + 2), (f2[0], f2[1] + 2), 6)
        pygame.draw.line(surface, bone, f1, f2, 5)
        for bx, by in [f1, f2]:
            pygame.draw.circle(surface, bone, (bx, by - 3), 4)
            pygame.draw.circle(surface, bone, (bx, by + 3), 4)

    def _draw_hero(self, surface: pygame.Surface, hx: int, hy: int) -> None:
        """Render hero adventurer sprite on bottom left."""
        pygame.draw.ellipse(surface, (14, 8, 8), pygame.Rect(hx - 55, hy - 6, 110, 22))
        bp_rect = pygame.Rect(hx - 55, hy - 114, 28, 52)
        pygame.draw.rect(surface, (92, 54, 28), bp_rect, border_radius=5)
        pygame.draw.rect(surface, (35, 18, 8), bp_rect, width=2, border_radius=5)
        br_rect = pygame.Rect(hx - 58, hy - 132, 34, 20)
        pygame.draw.rect(surface, (126, 134, 112), br_rect, border_radius=6)
        pygame.draw.rect(surface, (42, 48, 36), br_rect, width=2, border_radius=6)

        pygame.draw.polygon(surface, (68, 74, 62), [(hx - 28, hy - 58), (hx - 12, hy - 58), (hx - 18, hy - 18), (hx - 38, hy - 18)])
        pygame.draw.polygon(surface, (78, 44, 22), [(hx - 40, hy - 18), (hx - 16, hy - 18), (hx - 20, hy + 2), (hx - 52, hy + 2)])
        pygame.draw.polygon(surface, (35, 18, 8), [(hx - 40, hy - 18), (hx - 16, hy - 18), (hx - 20, hy + 2), (hx - 52, hy + 2)], 2)

        pygame.draw.polygon(surface, (68, 74, 62), [(hx - 2, hy - 58), (hx + 16, hy - 58), (hx + 28, hy - 18), (hx + 8, hy - 18)])
        pygame.draw.polygon(surface, (78, 44, 22), [(hx + 6, hy - 18), (hx + 30, hy - 18), (hx + 38, hy + 2), (hx + 4, hy + 2)])
        pygame.draw.polygon(surface, (35, 18, 8), [(hx + 6, hy - 18), (hx + 30, hy - 18), (hx + 38, hy + 2), (hx + 4, hy + 2)], 2)

        torso = pygame.Rect(hx - 26, hy - 108, 52, 58)
        pygame.draw.rect(surface, (230, 224, 212), torso, border_radius=3)
        pygame.draw.polygon(surface, (242, 192, 158), [(hx - 8, hy - 108), (hx + 8, hy - 108), (hx, hy - 92)])
        pygame.draw.rect(surface, (120, 68, 32), (hx - 26, hy - 108, 17, 52), border_radius=3)
        pygame.draw.rect(surface, (120, 68, 32), (hx + 9, hy - 108, 17, 52), border_radius=3)
        pygame.draw.rect(surface, (45, 22, 10), (hx - 26, hy - 108, 17, 52), width=2, border_radius=3)
        pygame.draw.rect(surface, (45, 22, 10), (hx + 9, hy - 108, 17, 52), width=2, border_radius=3)

        pygame.draw.rect(surface, (48, 24, 10), (hx - 26, hy - 60, 52, 11))
        bkl = pygame.Rect(hx - 7, hy - 62, 15, 15)
        pygame.draw.rect(surface, (244, 188, 52), bkl, border_radius=2)
        pygame.draw.rect(surface, (45, 22, 10), bkl, width=2, border_radius=2)

        pygame.draw.rect(surface, (242, 192, 158), (hx - 7, hy - 118, 14, 14))
        head = pygame.Rect(hx - 20, hy - 152, 40, 38)
        pygame.draw.rect(surface, (242, 192, 158), head, border_radius=8)
        pygame.draw.rect(surface, (64, 34, 16), (hx - 22, hy - 156, 44, 16), border_radius=5)
        pygame.draw.line(surface, (48, 22, 10), (hx - 11, hy - 138), (hx - 3, hy - 136), 2)
        pygame.draw.line(surface, (48, 22, 10), (hx + 3, hy - 136), (hx + 11, hy - 138), 2)
        pygame.draw.rect(surface, (35, 18, 8), (hx - 10, hy - 134, 6, 6))
        pygame.draw.rect(surface, (35, 18, 8), (hx + 4, hy - 134, 6, 6))
        pygame.draw.circle(surface, (255, 255, 255), (hx - 9, hy - 133), 1)
        pygame.draw.circle(surface, (255, 255, 255), (hx + 5, hy - 133), 1)

        brim = [(hx - 46, hy - 150), (hx - 18, hy - 156), (hx + 18, hy - 156), (hx + 46, hy - 150), (hx + 40, hy - 144), (hx - 40, hy - 144)]
        pygame.draw.polygon(surface, (132, 78, 40), brim)
        pygame.draw.polygon(surface, (48, 24, 10), brim, 2)
        pygame.draw.rect(surface, (132, 78, 40), (hx - 22, hy - 176, 44, 24), border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.line(surface, (88, 50, 24), (hx - 15, hy - 176), (hx + 15, hy - 176), 4)
        pygame.draw.rect(surface, (48, 22, 10), (hx - 22, hy - 156, 44, 9))

        pygame.draw.polygon(surface, (230, 224, 212), [(hx - 20, hy - 104), (hx - 34, hy - 80), (hx - 26, hy - 76), (hx - 14, hy - 100)])
        pygame.draw.circle(surface, (242, 192, 158), (hx - 28, hy - 72), 6)
        pygame.draw.polygon(surface, (230, 224, 212), [(hx + 20, hy - 104), (hx + 34, hy - 80), (hx + 26, hy - 76), (hx + 14, hy - 100)])
        pygame.draw.circle(surface, (242, 192, 158), (hx + 28, hy - 72), 6)

    def _draw_chest(self, surface: pygame.Surface, bx: int, by: int) -> None:
        """Render relic treasure chest on bottom right."""
        cw = 195
        ch = 115
        pygame.draw.ellipse(surface, (14, 8, 8), pygame.Rect(bx - 18, by + ch - 12, cw + 36, 34))
        lid_poly = [(bx + 8, by + 18), (bx + 30, by - 44), (bx + cw - 20, by - 44), (bx + cw, by + 24)]
        pygame.draw.polygon(surface, (16, 10, 8), [(px, py + 5) for px, py in lid_poly])
        pygame.draw.polygon(surface, (126, 64, 28), lid_poly)
        inner_lid = [(bx + 22, by + 14), (bx + 40, by - 32), (bx + cw - 30, by - 32), (bx + cw - 12, by + 20)]
        pygame.draw.polygon(surface, (48, 22, 10), inner_lid)
        pygame.draw.polygon(surface, (244, 188, 52), lid_poly, 6)
        pygame.draw.polygon(surface, (255, 230, 115), lid_poly, 2)

        box_rect = pygame.Rect(bx + 12, by + 20, cw - 24, ch - 20)
        pygame.draw.rect(surface, (122, 62, 28), box_rect, border_radius=4)
        pygame.draw.rect(surface, (244, 188, 52), (box_rect.x, box_rect.y, 15, box_rect.height), border_radius=3)
        pygame.draw.rect(surface, (244, 188, 52), (box_rect.right - 15, box_rect.y, 15, box_rect.height), border_radius=3)
        pygame.draw.rect(surface, (244, 188, 52), (box_rect.x, box_rect.y, box_rect.width, 13), border_radius=3)
        pygame.draw.rect(surface, (244, 188, 52), (box_rect.x, box_rect.bottom - 13, box_rect.width, 13), border_radius=3)
        pygame.draw.rect(surface, (44, 20, 8), box_rect, width=2, border_radius=4)

        kh_rect = pygame.Rect(box_rect.centerx - 12, box_rect.y + 8, 24, 30)
        pygame.draw.rect(surface, (244, 188, 52), kh_rect, border_radius=3)
        pygame.draw.rect(surface, (44, 20, 8), kh_rect, width=2, border_radius=3)
        pygame.draw.circle(surface, (30, 14, 6), (kh_rect.centerx, kh_rect.y + 10), 4)
        pygame.draw.polygon(surface, (30, 14, 6), [(kh_rect.centerx - 3, kh_rect.y + 10), (kh_rect.centerx + 3, kh_rect.y + 10), (kh_rect.centerx + 4, kh_rect.y + 22), (kh_rect.centerx - 4, kh_rect.y + 22)])

        for i in range(80):
            rx = bx + 32 + int((math.sin(i * 1.83) * 0.5 + 0.5) * (cw - 64))
            dist = abs(rx - (bx + cw // 2)) / float(cw // 2 - 20)
            mh = math.sqrt(max(0.0, 1.0 - dist**2)) * 24
            ry = by + 12 + int((math.cos(i * 2.41) * 0.5 + 0.5) * 18) - int(mh)
            pygame.draw.circle(surface, (216, 148, 18), (rx, ry + 1), 4)
            pygame.draw.circle(surface, (255, 218, 52), (rx, ry), 4)
            pygame.draw.circle(surface, (255, 246, 170), (rx - 1, ry - 1), 1)

        pygame.draw.polygon(surface, (225, 28, 58), [(bx + 85, by + 8), (bx + 96, by - 3), (bx + 107, by + 8), (bx + 96, by + 19)])
        pygame.draw.polygon(surface, (28, 205, 82), [(bx + 62, by + 10), (bx + 72, by + 1), (bx + 82, by + 10), (bx + 72, by + 19)])
        pygame.draw.polygon(surface, (28, 132, 238), [(bx + 125, by + 12), (bx + 135, by + 2), (bx + 145, by + 12), (bx + 135, by + 21)])

        dg_x = bx + cw - 48
        dg_y = by - 12
        pygame.draw.line(surface, (235, 240, 248), (dg_x, dg_y + 14), (dg_x + 9, dg_y - 18), 4)
        pygame.draw.line(surface, (244, 188, 52), (dg_x + 2, dg_y - 7), (dg_x + 15, dg_y - 3), 4)
        pygame.draw.circle(surface, (244, 188, 52), (dg_x + 11, dg_y - 21), 3)

        for sx, sy in [(bx - 12, by + ch - 8), (bx + 5, by + ch - 5), (bx - 20, by + ch - 2), (bx + cw + 10, by + ch - 5), (bx + cw + 22, by + ch - 2)]:
            pygame.draw.circle(surface, (216, 148, 18), (sx, sy + 1), 4)
            pygame.draw.circle(surface, (255, 218, 52), (sx, sy), 4)

    def draw(
        self,
        surface: pygame.Surface,
        input_username: TextInputBox,
        btn_submit: UIButton,
        btn_guest: UIButton,
        font_badge: Optional[pygame.font.Font] = None,
        font_title: Optional[pygame.font.Font] = None,
        font_bold: Optional[pygame.font.Font] = None,
        font_small: Optional[pygame.font.Font] = None,
        recent_operatives: Optional[List[Dict[str, Any]]] = None,
        status_msg: str = "AWAITING CREDENTIALS",
        btn_switch_to_register: Optional[UIButton] = None,
        input_password: Optional[TextInputBox] = None,
        btn_forgot_password: Optional[UIButton] = None,
        anim_time: float = 0.0,
    ) -> None:
        """
        Render the authentic retro-pixel RPG adventure Log In screen matching reference mockup.
        Parchment card encloses Username, Password, [LOG IN], [CREATE ACCOUNT], and FORGOT PASSWORD?
        """
        cx = self.screen_width // 2

        # 1. Dark dungeon stone background & torch
        draw_dungeon_background(surface, self.screen_width, self.screen_height)
        self._draw_wall_torch(surface, 90, 310, anim_time)

        # 2. Golden Royal Crown centered above title
        y_start = 74
        draw_royal_crown(surface, cx, y_start - 30)

        # 3. 3D Adventure Title Logo: "TREASURE" / "HUNTER"
        if font_title:
            t_font = font_title
        else:
            if self._t_font is None:
                self._t_font = pygame.font.SysFont("trebuchetms,impact,arial", 44, bold=True)
            t_font = self._t_font

        for idx, text in enumerate(["TREASURE", "HUNTER"]):
            ty = y_start + idx * 46
            txt_surf = t_font.render(text, True, (250, 185, 45))
            tx = cx - txt_surf.get_width() // 2
            for off_y in [5, 4, 3, 2]:
                for ox in [-1, 0, 1]:
                    s = t_font.render(text, True, (46, 18, 5))
                    surface.blit(s, (tx + ox, ty + off_y))
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    b = t_font.render(text, True, (246, 186, 42))
                    surface.blit(b, (tx + dx, ty + dy))
            f = t_font.render(text, True, (255, 212, 60))
            surface.blit(f, (tx, ty))

        # Subtitle: "LOG IN TO START THE HUNT"
        sub_text = "LOG IN TO START THE HUNT"
        if self._sub_font is None:
            self._sub_font = pygame.font.SysFont("trebuchetms,impact,arial", 16, bold=True)
        sub_font = self._sub_font
        sub_s = sub_font.render(sub_text, True, (36, 14, 4))
        sub_f = sub_font.render(sub_text, True, (245, 182, 55))
        rc = sub_f.get_rect(center=(cx, y_start + 104))
        surface.blit(sub_s, rc.move(0, 2))
        surface.blit(sub_f, rc)

        # 4. Center Parchment Card (Encloses form, buttons, and forgot password)
        card_w = 510
        card_h = 435
        card_x = cx - card_w // 2
        card_y = 224
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        pygame.draw.rect(surface, (16, 10, 8), card_rect.move(0, 6), border_radius=8)
        pygame.draw.rect(surface, (228, 204, 160), card_rect, border_radius=8)
        pygame.draw.rect(surface, (192, 162, 118), card_rect.inflate(-16, -16), width=1, border_radius=6)
        pygame.draw.rect(surface, (56, 36, 18), card_rect, width=2, border_radius=8)

        # 4 Corner screws
        self._draw_screw(surface, card_x + 18, card_y + 18)
        self._draw_screw(surface, card_x + card_w - 18, card_y + 18)
        self._draw_screw(surface, card_x + 18, card_y + card_h - 18)
        self._draw_screw(surface, card_x + card_w - 18, card_y + card_h - 18)

        # 5. Form Fields inside Parchment Card
        bx = cx - 205
        bw = 410
        bh = 44

        if self._lbl_font is None:
            self._lbl_font = pygame.font.SysFont("trebuchetms,impact,arial", 16, bold=True)
        lbl_font = self._lbl_font

        # USERNAME
        l1 = lbl_font.render("USERNAME", True, (42, 24, 10))
        surface.blit(l1, l1.get_rect(center=(cx, card_y + 26)))

        input_username.rect = pygame.Rect(bx, card_y + 44, bw, bh)
        input_username.style = "wood_recessed"
        input_username.text_align = "center"
        input_username.placeholder = "Enter username..."
        input_username.draw(surface)

        # PASSWORD
        l2 = lbl_font.render("PASSWORD", True, (42, 24, 10))
        surface.blit(l2, l2.get_rect(center=(cx, card_y + 118)))

        if input_password:
            input_password.rect = pygame.Rect(bx, card_y + 136, bw, bh)
            input_password.style = "wood_recessed"
            input_password.text_align = "center"
            input_password.is_password = True
            input_password.placeholder = "••••••••"
            input_password.draw(surface)

        # 6. Action Buttons INSIDE Parchment Card (Matching reference mockup exactly)
        btn_w = 300
        btn_submit.rect = pygame.Rect(cx - btn_w // 2, card_y + 210, btn_w, 48)
        btn_submit.text = "LOG IN"
        btn_submit.style = "green_cta"
        btn_submit.draw(surface)

        if btn_switch_to_register:
            btn_switch_to_register.rect = pygame.Rect(cx - btn_w // 2, card_y + 272, btn_w, 42)
            btn_switch_to_register.text = "CREATE ACCOUNT"
            btn_switch_to_register.style = "blue_pill"
            btn_switch_to_register.draw(surface)

        # 7. "FORGOT PASSWORD?" link inside parchment card
        if btn_forgot_password:
            btn_forgot_password.rect = pygame.Rect(cx - 110, card_y + 328, 220, 24)
            btn_forgot_password.draw(surface)
        else:
            if self._link_font is None:
                self._link_font = pygame.font.SysFont("trebuchetms,impact,arial", 15, bold=True)
            fp_surf = self._link_font.render("FORGOT PASSWORD?", True, (42, 24, 10))
            surface.blit(fp_surf, fp_surf.get_rect(center=(cx, card_y + 340)))

        # Status / Feedback Message
        if status_msg and status_msg != "AWAITING CREDENTIALS":
            is_err = "NOT FOUND" in status_msg or "INVALID" in status_msg or "ERROR" in status_msg or "INCORRECT" in status_msg
            col = (200, 30, 20) if is_err else (20, 140, 50)
            st_font = pygame.font.SysFont("trebuchetms,impact,arial", 13, bold=True)
            st_surf = st_font.render(status_msg, True, col)
            surface.blit(st_surf, st_surf.get_rect(center=(cx, card_y + 372)))

        # 8. Foreground Characters
        self._draw_hero(surface, 180, 670)
        self._draw_skeleton(surface, 110, 690)
        self._draw_chest(surface, 690, 545)

        # 9. Watermark: v1.2.0
        ver_surf = pygame.font.SysFont("trebuchetms,arial", 14).render("v1.2.0", True, (95, 80, 65))
        surface.blit(ver_surf, (self.screen_width - 55, self.screen_height - 24))
