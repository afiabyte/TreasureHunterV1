"""
UI HUD Console: Dedicated bottom dashboard partition showing mission metrics,
sensor telemetry with pulsing LED indicator, and live tactical commander dispatches.
"""

import math
from typing import Optional
import pygame

from .colors import (
    COLOR_HUD_BG,
    COLOR_WALL_BORDER,
    COLOR_HUD_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_ACCENT_CYAN,
    COLOR_TEXT_ACCENT_GREEN,
    COLOR_TEXT_ACCENT_AMBER,
    COLOR_TEXT_ACCENT_RED,
    COLOR_TEXT_ACCENT_MAGENTA,
    COLOR_KEY_GOLD,
)


class HUDConsoleRenderer:
    """Renders the high-contrast cyber-tactical bottom HUD telemetry dashboard."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780, hud_height: int = 140) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hud_height = hud_height
        self.hud_rect = pygame.Rect(0, self.screen_height - self.hud_height, self.screen_width, self.hud_height)

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
        """Render the dedicated bottom HUD console with metrics, telemetry, and transmissions."""
        pygame.draw.rect(surface, COLOR_HUD_BG, self.hud_rect)
        pygame.draw.line(surface, COLOR_WALL_BORDER, (0, self.hud_rect.y), (self.screen_width, self.hud_rect.y), 2)

        col1_w = 260
        col2_w = 260
        col3_w = self.screen_width - col1_w - col2_w

        c1_rect = pygame.Rect(10, self.hud_rect.y + 10, col1_w - 20, self.hud_height - 20)
        c2_rect = pygame.Rect(col1_w, self.hud_rect.y + 10, col2_w - 20, self.hud_height - 20)
        c3_rect = pygame.Rect(col1_w + col2_w, self.hud_rect.y + 10, col3_w - 20, self.hud_height - 20)

        pygame.draw.line(surface, COLOR_HUD_BORDER, (col1_w - 5, self.hud_rect.y + 10), (col1_w - 5, self.screen_height - 10), 1)
        pygame.draw.line(surface, COLOR_HUD_BORDER, (col1_w + col2_w - 5, self.hud_rect.y + 10), (col1_w + col2_w - 5, self.screen_height - 10), 1)

        # COLUMN 1: MISSION METRICS
        h1 = font_badge.render("// MISSION METRICS", True, COLOR_TEXT_ACCENT_CYAN)
        surface.blit(h1, (c1_rect.x, c1_rect.y))

        y = c1_rect.y + 22
        lvl_str = f"LEVEL: {level_name.upper()}"
        surface.blit(font_small.render(lvl_str, True, COLOR_TEXT_SECONDARY), (c1_rect.x, y))
        y += 18
        step_str = f"STEPS EXECUTED: {steps:03d}"
        surface.blit(font_body.render(step_str, True, COLOR_TEXT_PRIMARY), (c1_rect.x, y))
        y += 20
        best_str = f"BEST RECORD: {best_steps} STEPS" if best_steps is not None else "★ BEST RECORD: UNCLAIMED"
        surface.blit(font_small.render(best_str, True, COLOR_KEY_GOLD), (c1_rect.x, y))
        y += 22
        key_label = "RELIC: SECURED [GATEWAY OPEN]" if has_key else "RELIC: REQUIRED [EXPLORING]"
        key_color = COLOR_TEXT_ACCENT_GREEN if has_key else COLOR_TEXT_ACCENT_RED
        k_bg_fill = (16, 42, 28) if has_key else (38, 16, 24)
        k_surf = font_bold.render(key_label, True, key_color)
        k_bg = pygame.Rect(c1_rect.x, y, k_surf.get_width() + 10, 22)
        pygame.draw.rect(surface, k_bg_fill, k_bg, border_radius=3)
        pygame.draw.rect(surface, key_color, k_bg, width=1, border_radius=3)
        surface.blit(k_surf, (c1_rect.x + 5, y + 2))

        # COLUMN 2: TACTICAL SENSOR TELEMETRY
        h2 = font_badge.render("// SENSOR TELEMETRY", True, COLOR_TEXT_ACCENT_MAGENTA)
        surface.blit(h2, (c2_rect.x, c2_rect.y))

        y2 = c2_rect.y + 22
        surface.blit(font_small.render("SANCTUARY RADAR: MULTI-CHAMBER ACTIVE", True, COLOR_TEXT_ACCENT_CYAN), (c2_rect.x, y2))
        y2 += 18

        surface.blit(font_body.render("ESCAPE ROUTE: COMPUTED", True, COLOR_TEXT_ACCENT_GREEN), (c2_rect.x, y2))
        y2 += 22

        led_color = COLOR_TEXT_ACCENT_GREEN
        led_pulse = 1.0 + 0.25 * math.sin(anim_time * 8.0)
        pygame.draw.circle(surface, led_color, (c2_rect.x + 8, y2 + 8), int(5 * led_pulse))

        surface.blit(font_bold.render("SENTINEL TRACKING: ACTIVE (60 FPS)", True, led_color), (c2_rect.x + 22, y2))
        y2 += 22

        surface.blit(font_small.render("GUARDIAN EVASION: ENGAGED", True, COLOR_TEXT_MUTED), (c2_rect.x, y2))

        # COLUMN 3: LIVE TACTICAL COMMANDER TRANSMISSION
        h3 = font_badge.render("// EXPEDITION COMMAND DISPATCH", True, COLOR_TEXT_ACCENT_AMBER)
        surface.blit(h3, (c3_rect.x, c3_rect.y))

        box_rect = pygame.Rect(c3_rect.x, c3_rect.y + 20, c3_rect.width, self.hud_height - 50)
        pygame.draw.rect(surface, (18, 24, 36), box_rect, border_radius=4)
        pygame.draw.rect(surface, (45, 68, 105), box_rect, width=1, border_radius=4)

        radio_icon = font_small.render("[DISPATCH ACTIVE]", True, COLOR_TEXT_ACCENT_GREEN)
        surface.blit(radio_icon, (box_rect.x + 8, box_rect.y + 6))

        clean_order = commander_order.strip() if commander_order else "Observing sanctuary chamber telemetry..."
        order_surf = font_header.render(f'"{clean_order}"', True, COLOR_TEXT_PRIMARY)
        surface.blit(order_surf, (box_rect.x + 8, box_rect.y + 28))

        hint_surf = font_small.render("[WASD: Move | P/ESC: Pause | H: Summon Sentinel | B: Shift Walls]", True, COLOR_TEXT_MUTED)
        surface.blit(hint_surf, (box_rect.x + 8, box_rect.y + 62))
