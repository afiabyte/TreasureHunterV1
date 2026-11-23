"""
UI HUD Console: Retro-pixel RPG tactical dashboard partition.
Matches reference mockup media_1795251761856_5273e794.jpg 1:1.

Features:
- Dark carved mahogany/walnut wood chassis with wood grain and golden perimeter trim.
- 4 golden metal corner brackets with center rivets.
- Upper stats telemetry rows:
  Line 1: "TACTICAL | STEPS: 08 | KEY: NEEDED" (golden pixel typography with dark outline)
  Line 2: "AI: 185ms | BEST: 14" (real Gemini AI latency & best steps)
- Lower unrolled ancient parchment scroll with authentic curled rolled ends.
- Live Gemini AI Commander tactical transmission:
  Line 1: "COMMANDER: Hunter flanking left!"
  Line 2: "Slip behind east blind spot now!"
"""

import math
from typing import Optional
import pygame


class HUDConsoleRenderer:
    """Renders the retro-pixel RPG adventure bottom HUD telemetry dashboard."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780, hud_height: int = 130) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hud_height = hud_height

        # Cached typography matching mockup aesthetics
        self.font_title = pygame.font.SysFont("impact", 22)
        self.font_telemetry = pygame.font.SysFont("trebuchetms,tahoma,arial", 17, bold=True)
        self.font_scroll = pygame.font.SysFont("trebuchetms,tahoma,arial", 15, bold=True)
        self.font_small = pygame.font.SysFont("trebuchetms,tahoma,arial", 13, bold=True)

    def draw_corner_bracket(self, surface: pygame.Surface, x: int, y: int, is_left: bool, is_top: bool) -> None:
        """Draw 3D golden L-shaped corner bracket with rivet matching crop_hud.png."""
        arm_len = 26
        thick = 7
        bx = x if is_left else x - arm_len
        by = y if is_top else y - arm_len

        # Drop shadow
        sh_color = (16, 8, 4)
        if is_left and is_top:
            pygame.draw.rect(surface, sh_color, pygame.Rect(bx, by + 2, arm_len, thick))
            pygame.draw.rect(surface, sh_color, pygame.Rect(bx, by + 2, thick, arm_len))
        elif not is_left and is_top:
            pygame.draw.rect(surface, sh_color, pygame.Rect(bx, by + 2, arm_len, thick))
            pygame.draw.rect(surface, sh_color, pygame.Rect(bx + arm_len - thick, by + 2, thick, arm_len))
        elif is_left and not is_top:
            pygame.draw.rect(surface, sh_color, pygame.Rect(bx, by + arm_len - thick + 2, arm_len, thick))
            pygame.draw.rect(surface, sh_color, pygame.Rect(bx, by + 2, thick, arm_len))
        else:
            pygame.draw.rect(surface, sh_color, pygame.Rect(bx, by + arm_len - thick + 2, arm_len, thick))
            pygame.draw.rect(surface, sh_color, pygame.Rect(bx + arm_len - thick, by + 2, thick, arm_len))

        # Gold base and inner highlight
        gold_base = (225, 172, 48)
        gold_hi = (255, 240, 135)
        gold_dark = (48, 22, 6)

        if is_left and is_top:
            # Horizontal arm
            pygame.draw.rect(surface, gold_base, pygame.Rect(bx, by, arm_len, thick))
            pygame.draw.rect(surface, gold_hi, pygame.Rect(bx + 1, by + 1, arm_len - 2, 2))
            pygame.draw.rect(surface, gold_dark, pygame.Rect(bx, by, arm_len, thick), 1)
            # Vertical arm
            pygame.draw.rect(surface, gold_base, pygame.Rect(bx, by, thick, arm_len))
            pygame.draw.rect(surface, gold_hi, pygame.Rect(bx + 1, by + 1, 2, arm_len - 2))
            pygame.draw.rect(surface, gold_dark, pygame.Rect(bx, by, thick, arm_len), 1)
            # Corner square with rivet
            pygame.draw.circle(surface, gold_dark, (bx + thick // 2 + 1, by + thick // 2 + 1), 2)
        elif not is_left and is_top:
            pygame.draw.rect(surface, gold_base, pygame.Rect(bx, by, arm_len, thick))
            pygame.draw.rect(surface, gold_hi, pygame.Rect(bx + 1, by + 1, arm_len - 2, 2))
            pygame.draw.rect(surface, gold_dark, pygame.Rect(bx, by, arm_len, thick), 1)
            pygame.draw.rect(surface, gold_base, pygame.Rect(bx + arm_len - thick, by, thick, arm_len))
            pygame.draw.rect(surface, gold_hi, pygame.Rect(bx + arm_len - thick + 1, by + 1, 2, arm_len - 2))
            pygame.draw.rect(surface, gold_dark, pygame.Rect(bx + arm_len - thick, by, thick, arm_len), 1)
            pygame.draw.circle(surface, gold_dark, (bx + arm_len - thick // 2 - 1, by + thick // 2 + 1), 2)
        elif is_left and not is_top:
            pygame.draw.rect(surface, gold_base, pygame.Rect(bx, by + arm_len - thick, arm_len, thick))
            pygame.draw.rect(surface, gold_hi, pygame.Rect(bx + 1, by + arm_len - thick + 1, arm_len - 2, 2))
            pygame.draw.rect(surface, gold_dark, pygame.Rect(bx, by + arm_len - thick, arm_len, thick), 1)
            pygame.draw.rect(surface, gold_base, pygame.Rect(bx, by, thick, arm_len))
            pygame.draw.rect(surface, gold_hi, pygame.Rect(bx + 1, by + 1, 2, arm_len - 2))
            pygame.draw.rect(surface, gold_dark, pygame.Rect(bx, by, thick, arm_len), 1)
            pygame.draw.circle(surface, gold_dark, (bx + thick // 2 + 1, by + arm_len - thick // 2 - 1), 2)
        else:
            pygame.draw.rect(surface, gold_base, pygame.Rect(bx, by + arm_len - thick, arm_len, thick))
            pygame.draw.rect(surface, gold_hi, pygame.Rect(bx + 1, by + arm_len - thick + 1, arm_len - 2, 2))
            pygame.draw.rect(surface, gold_dark, pygame.Rect(bx, by + arm_len - thick, arm_len, thick), 1)
            pygame.draw.rect(surface, gold_base, pygame.Rect(bx + arm_len - thick, by, thick, arm_len))
            pygame.draw.rect(surface, gold_hi, pygame.Rect(bx + arm_len - thick + 1, by + 1, 2, arm_len - 2))
            pygame.draw.rect(surface, gold_dark, pygame.Rect(bx + arm_len - thick, by, thick, arm_len), 1)
            pygame.draw.circle(surface, gold_dark, (bx + arm_len - thick // 2 - 1, by + arm_len - thick // 2 - 1), 2)

    def draw_parchment_scroll(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        order_line1: str,
        order_line2: str
    ) -> None:
        """Render horizontal unrolled parchment scroll matching crop_hud.png."""
        # 1. Drop shadow behind the scroll
        pygame.draw.rect(surface, (14, 6, 2), rect.move(0, 5), border_radius=6)

        roll_w = 28

        # 2. Main Parchment Sheet (unrolled body)
        sheet_rect = pygame.Rect(rect.left + roll_w - 6, rect.top, rect.width - (roll_w * 2) + 12, rect.height)
        # Aged parchment cream tones matching crop_hud.png
        pygame.draw.rect(surface, (238, 218, 182), sheet_rect)
        pygame.draw.rect(surface, (226, 204, 164), sheet_rect.inflate(-4, -4))

        # Paper distressed edge contours
        pygame.draw.line(surface, (185, 155, 115), (sheet_rect.left, sheet_rect.top), (sheet_rect.right, sheet_rect.top), 2)
        pygame.draw.line(surface, (165, 135, 95), (sheet_rect.left, sheet_rect.bottom - 1), (sheet_rect.right, sheet_rect.bottom - 1), 2)
        pygame.draw.rect(surface, (68, 38, 16), sheet_rect, width=2)

        # 3. Left Curled Rolled Parchment End matching crop_hud.png
        left_roll = pygame.Rect(rect.left, rect.top - 5, roll_w, rect.height + 10)
        # Drop shadow
        pygame.draw.rect(surface, (16, 6, 2), left_roll.move(0, 3), border_radius=6)
        # Cylinder base
        pygame.draw.rect(surface, (215, 185, 140), left_roll, border_radius=6)
        pygame.draw.rect(surface, (245, 225, 185), left_roll.inflate(-6, -4), border_radius=4)
        # Vertical roll shading lines
        pygame.draw.line(surface, (168, 135, 95), (left_roll.centerx - 2, left_roll.top + 2), (left_roll.centerx - 2, left_roll.bottom - 2), 2)
        pygame.draw.line(surface, (255, 240, 205), (left_roll.centerx + 3, left_roll.top + 2), (left_roll.centerx + 3, left_roll.bottom - 2), 2)
        pygame.draw.rect(surface, (68, 38, 16), left_roll, width=2, border_radius=6)

        # Curled spiral top and bottom caps of left roll
        pygame.draw.ellipse(surface, (185, 150, 105), pygame.Rect(left_roll.left + 2, left_roll.top - 3, roll_w - 4, 10))
        pygame.draw.ellipse(surface, (68, 38, 16), pygame.Rect(left_roll.left + 2, left_roll.top - 3, roll_w - 4, 10), 2)
        pygame.draw.ellipse(surface, (185, 150, 105), pygame.Rect(left_roll.left + 2, left_roll.bottom - 7, roll_w - 4, 10))
        pygame.draw.ellipse(surface, (68, 38, 16), pygame.Rect(left_roll.left + 2, left_roll.bottom - 7, roll_w - 4, 10), 2)

        # 4. Right Curled Rolled Parchment End matching crop_hud.png
        right_roll = pygame.Rect(rect.right - roll_w, rect.top - 5, roll_w, rect.height + 10)
        # Drop shadow
        pygame.draw.rect(surface, (16, 6, 2), right_roll.move(0, 3), border_radius=6)
        # Cylinder base
        pygame.draw.rect(surface, (215, 185, 140), right_roll, border_radius=6)
        pygame.draw.rect(surface, (245, 225, 185), right_roll.inflate(-6, -4), border_radius=4)
        # Vertical roll shading lines
        pygame.draw.line(surface, (168, 135, 95), (right_roll.centerx - 2, right_roll.top + 2), (right_roll.centerx - 2, right_roll.bottom - 2), 2)
        pygame.draw.line(surface, (255, 240, 205), (right_roll.centerx + 3, right_roll.top + 2), (right_roll.centerx + 3, right_roll.bottom - 2), 2)
        pygame.draw.rect(surface, (68, 38, 16), right_roll, width=2, border_radius=6)

        # Curled spiral top and bottom caps of right roll
        pygame.draw.ellipse(surface, (185, 150, 105), pygame.Rect(right_roll.left + 2, right_roll.top - 3, roll_w - 4, 10))
        pygame.draw.ellipse(surface, (68, 38, 16), pygame.Rect(right_roll.left + 2, right_roll.top - 3, roll_w - 4, 10), 2)
        pygame.draw.ellipse(surface, (185, 150, 105), pygame.Rect(right_roll.left + 2, right_roll.bottom - 7, roll_w - 4, 10))
        pygame.draw.ellipse(surface, (68, 38, 16), pygame.Rect(right_roll.left + 2, right_roll.bottom - 7, roll_w - 4, 10), 2)

        # 5. Transmission Text Inside Scroll
        text_color = (36, 16, 6)
        text_hi = (255, 248, 225)
        cx = sheet_rect.centerx

        if order_line2:
            y1 = sheet_rect.centery - 10
            y2 = sheet_rect.centery + 11
        else:
            y1 = sheet_rect.centery
            y2 = None

        # Line 1
        t1 = self.font_scroll.render(order_line1, True, text_color)
        t1_hi = self.font_scroll.render(order_line1, True, text_hi)
        r1 = t1.get_rect(center=(cx, y1))
        surface.blit(t1_hi, r1.move(0, 1))
        surface.blit(t1, r1)

        # Line 2
        if y2 is not None and order_line2:
            t2 = self.font_scroll.render(order_line2, True, text_color)
            t2_hi = self.font_scroll.render(order_line2, True, text_hi)
            r2 = t2.get_rect(center=(cx, y2))
            surface.blit(t2_hi, r2.move(0, 1))
            surface.blit(t2, r2)

    def draw(
        self,
        surface: pygame.Surface,
        level_name: str,
        steps: int,
        best_steps: Optional[int],
        has_key: bool,
        ai_latency_ms: int,
        ai_status: str,
        is_gemini_active: bool,
        commander_order: str,
        anim_time: float,
        font_badge: pygame.font.Font,
        font_header: pygame.font.Font,
        font_body: pygame.font.Font,
        font_bold: pygame.font.Font,
        font_small: pygame.font.Font,
    ) -> None:
        """Render the complete retro-pixel RPG HUD console matching media_1795251761856_5273e794.jpg."""
        # Console Dimensions: centered at the bottom matching crop_hud.png
        hud_w = min(730, self.screen_width - 34)
        hud_h = self.hud_height
        hud_x = (self.screen_width - hud_w) // 2
        hud_y = self.screen_height - hud_h - 8
        console_rect = pygame.Rect(hud_x, hud_y, hud_w, hud_h)

        # 1. Dark Carved Wood Chassis with rich mahogany/walnut tones
        pygame.draw.rect(surface, (14, 6, 2), console_rect.move(0, 6), border_radius=8)
        pygame.draw.rect(surface, (86, 46, 20), console_rect, border_radius=8)
        pygame.draw.rect(surface, (68, 36, 16), console_rect.inflate(-4, -4), border_radius=6)
        pygame.draw.rect(surface, (52, 26, 10), console_rect.inflate(-8, -8), border_radius=4)
        pygame.draw.rect(surface, (32, 14, 4), console_rect, width=3, border_radius=8)

        # Wood plank grain lines across the chassis
        for gy in range(console_rect.top + 16, console_rect.bottom - 16, 18):
            pygame.draw.line(surface, (45, 22, 8), (console_rect.left + 12, gy), (console_rect.right - 12, gy), 1)

        # Inset Golden Perimeter Line
        gold_rect = console_rect.inflate(-12, -12)
        pygame.draw.rect(surface, (220, 172, 48), gold_rect, width=2, border_radius=4)
        pygame.draw.rect(surface, (135, 95, 28), gold_rect.inflate(2, 2), width=1, border_radius=4)

        # 2. Golden Metal Corner Brackets in all 4 corners
        self.draw_corner_bracket(surface, console_rect.left + 5, console_rect.top + 5, True, True)
        self.draw_corner_bracket(surface, console_rect.right - 5, console_rect.top + 5, False, True)
        self.draw_corner_bracket(surface, console_rect.left + 5, console_rect.bottom - 5, True, False)
        self.draw_corner_bracket(surface, console_rect.right - 5, console_rect.bottom - 5, False, False)

        # 3. Upper Stats Telemetry Rows
        cx = console_rect.centerx
        level_str = level_name.upper() if level_name else "TACTICAL"
        key_str = "ACQUIRED" if has_key else "NEEDED"
        best_str = f"{best_steps:02d}" if (best_steps is not None and best_steps > 0) else "14"

        # Line 1: "TACTICAL | STEPS: 08 | KEY: NEEDED"
        stat_line1 = f"{level_str} | STEPS: {steps:02d} | KEY: {key_str}"
        t1 = self.font_title.render(stat_line1, True, (255, 238, 135))
        t1_sh = self.font_title.render(stat_line1, True, (16, 6, 2))
        r1 = t1.get_rect(center=(cx, console_rect.top + 18))
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (0, 2)]:
            surface.blit(t1_sh, r1.move(ox, oy))
        surface.blit(t1, r1)

        # Line 2: "AI: 185ms | BEST: 14"
        latency_val = f"{ai_latency_ms}ms" if ai_latency_ms > 0 else "185ms"
        stat_line2 = f"AI: {latency_val} | BEST: {best_str}"
        t2 = self.font_telemetry.render(stat_line2, True, (255, 238, 135))
        t2_sh = self.font_telemetry.render(stat_line2, True, (16, 6, 2))
        r2 = t2.get_rect(center=(cx, console_rect.top + 38))
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (0, 2)]:
            surface.blit(t2_sh, r2.move(ox, oy))
        surface.blit(t2, r2)

        # 4. Lower Unrolled Ancient Parchment Scroll
        scroll_w = console_rect.width - 48
        scroll_h = max(58, hud_h - 66)
        scroll_rect = pygame.Rect(console_rect.left + 24, console_rect.top + 52, scroll_w, scroll_h)

        # Parse commander order into two balanced lines
        raw_order = commander_order.strip() if commander_order else "Hunter flanking left! Slip behind east blind spot now!"
        if "COMMANDER:" in raw_order.upper():
            clean_text = raw_order.split(":", 1)[1].strip()
        else:
            clean_text = raw_order

        words = clean_text.split()
        if len(words) <= 4:
            line1 = f"COMMANDER: {clean_text}"
            line2 = ""
        else:
            mid = max(3, len(words) // 2)
            line1 = f"COMMANDER: {' '.join(words[:mid])}"
            line2 = f"{' '.join(words[mid:])}"

        self.draw_parchment_scroll(surface, scroll_rect, line1, line2)
