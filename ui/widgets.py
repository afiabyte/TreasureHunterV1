"""
UI Widgets: Interactive tactical buttons and text input fields.
"""

import math
from typing import Tuple, Optional
import pygame

from .colors import (
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_ACCENT_CYAN,
    COLOR_BTN_NORMAL,
    COLOR_BTN_HOVER,
    COLOR_BTN_BORDER,
    COLOR_BTN_BORDER_HOVER,
)


class UIButton:
    """Interactive tactical UI button with hover animations and click detection."""

    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font,
                 accent_color: Tuple[int, int, int] = COLOR_TEXT_ACCENT_CYAN,
                 tag: str = "",
                 style: str = "tactical") -> None:
        self.rect = rect
        self.text = text
        self.font = font
        self.accent_color = accent_color
        self.tag = tag
        self.style = style
        self.is_hovered = False
        self.is_selected = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True if clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Render button with style-specific borders, drop shadow, and state highlights."""
        if self.style == "stone":
            if self.is_selected:
                pygame.draw.rect(surface, (100, 48, 6), self.rect.move(0, 4), border_radius=10)
                pygame.draw.rect(surface, (250, 182, 52), self.rect, border_radius=10)
                pygame.draw.rect(surface, (255, 222, 118), self.rect.inflate(-4, -4), border_radius=8)
                pygame.draw.rect(surface, (246, 170, 40), self.rect.inflate(-8, -8), border_radius=6)
                pygame.draw.rect(surface, (92, 42, 6), self.rect, width=3, border_radius=10)
                txt = self.font.render(self.text, True, (52, 22, 4))
                surface.blit(txt, txt.get_rect(center=self.rect.center))
            else:
                bg = (148, 138, 130) if self.is_hovered else (136, 126, 118)
                pygame.draw.rect(surface, (54, 48, 44), self.rect.move(0, 4), border_radius=10)
                pygame.draw.rect(surface, bg, self.rect, border_radius=10)
                pygame.draw.rect(surface, (168, 158, 150), self.rect.inflate(-4, -4), border_radius=8)
                pygame.draw.rect(surface, (126, 116, 108), self.rect.inflate(-8, -8), border_radius=6)
                pygame.draw.rect(surface, (50, 44, 40), self.rect, width=2, border_radius=10)
                pygame.draw.line(surface, (84, 76, 70), (self.rect.x + 14, self.rect.bottom - 14), (self.rect.x + 26, self.rect.bottom - 22), 2)
                txt = self.font.render(self.text, True, (40, 34, 30))
                surface.blit(txt, txt.get_rect(center=self.rect.center))
            return

        elif self.style == "green_cta":
            c_shadow = (10, 48, 24)
            c_face = (46, 188, 104) if self.is_hovered else (39, 174, 96)
            c_light = (98, 224, 151)
            c_border = (10, 50, 26)
            pygame.draw.rect(surface, c_shadow, self.rect.move(0, 4), border_radius=12)
            pygame.draw.rect(surface, c_face, self.rect, border_radius=12)
            pygame.draw.rect(surface, c_light, self.rect.inflate(-4, -4), border_radius=10)
            pygame.draw.rect(surface, (30, 152, 84), self.rect.inflate(-8, -8), border_radius=8)
            pygame.draw.rect(surface, c_border, self.rect, width=3, border_radius=12)
            txt = self.font.render(self.text, True, (255, 255, 255))
            txt_s = self.font.render(self.text, True, (10, 50, 26))
            rc = txt.get_rect(center=self.rect.center)
            surface.blit(txt_s, rc.move(0, 2))
            surface.blit(txt, rc)
            return

        elif self.style == "blue_pill":
            c_shadow = (26, 38, 48)
            c_face = (84, 110, 128) if self.is_hovered else (72, 96, 112)
            c_light = (118, 144, 162)
            c_border = (18, 28, 36)
            pygame.draw.rect(surface, c_shadow, self.rect.move(0, 3), border_radius=10)
            pygame.draw.rect(surface, c_face, self.rect, border_radius=10)
            pygame.draw.rect(surface, c_light, self.rect.inflate(-4, -4), border_radius=8)
            pygame.draw.rect(surface, (60, 84, 100), self.rect.inflate(-8, -8), border_radius=6)
            pygame.draw.rect(surface, c_border, self.rect, width=2, border_radius=10)
            txt = self.font.render(self.text, True, (255, 250, 242))
            txt_s = self.font.render(self.text, True, c_border)
            rc = txt.get_rect(center=self.rect.center)
            surface.blit(txt_s, rc.move(0, 1))
            surface.blit(txt, rc)
            return

        elif self.style in ("wood_pill", "wood_gear_pill"):
            c_shadow = (68, 34, 12)
            c_face = (175, 105, 48) if self.is_hovered else (160, 94, 40)
            c_light = (206, 136, 76)
            c_border = (48, 24, 8)
            pygame.draw.rect(surface, c_shadow, self.rect.move(0, 3), border_radius=10)
            pygame.draw.rect(surface, c_face, self.rect, border_radius=10)
            pygame.draw.rect(surface, c_light, self.rect.inflate(-4, -4), border_radius=8)
            pygame.draw.rect(surface, (140, 80, 32), self.rect.inflate(-8, -8), border_radius=6)
            pygame.draw.rect(surface, c_border, self.rect, width=2, border_radius=10)

            txt = self.font.render(self.text, True, (255, 250, 242))
            txt_s = self.font.render(self.text, True, c_border)
            if self.style == "wood_gear_pill":
                total_w = txt.get_width() + 24
                tx = self.rect.centerx - total_w // 2
                ty = self.rect.centery - txt.get_height() // 2
                surface.blit(txt_s, (tx, ty + 1))
                surface.blit(txt, (tx, ty))
                gx = tx + txt.get_width() + 14
                gy = self.rect.centery
                pygame.draw.circle(surface, c_border, (gx, gy + 1), 7)
                pygame.draw.circle(surface, (245, 185, 55), (gx, gy), 6)
                pygame.draw.circle(surface, c_border, (gx, gy), 6, 2)
                pygame.draw.circle(surface, (140, 80, 32), (gx, gy), 2)
                for ang in range(0, 360, 60):
                    rad = math.radians(ang)
                    tx1 = int(gx + math.cos(rad) * 8)
                    ty1 = int(gy + math.sin(rad) * 8)
                    pygame.draw.circle(surface, (245, 185, 55), (tx1, ty1), 2)
            else:
                rc = txt.get_rect(center=self.rect.center)
                surface.blit(txt_s, rc.move(0, 1))
                surface.blit(txt, rc)
            return

        elif self.style == "red_pill":
            c_shadow = (72, 20, 16)
            c_face = (184, 60, 48) if self.is_hovered else (168, 52, 40)
            c_light = (220, 94, 80)
            c_border = (48, 14, 10)
            pygame.draw.rect(surface, c_shadow, self.rect.move(0, 3), border_radius=10)
            pygame.draw.rect(surface, c_face, self.rect, border_radius=10)
            pygame.draw.rect(surface, c_light, self.rect.inflate(-4, -4), border_radius=8)
            pygame.draw.rect(surface, (145, 42, 32), self.rect.inflate(-8, -8), border_radius=6)
            pygame.draw.rect(surface, c_border, self.rect, width=2, border_radius=10)
            txt = self.font.render(self.text, True, (255, 250, 242))
            txt_s = self.font.render(self.text, True, c_border)
            rc = txt.get_rect(center=self.rect.center)
            surface.blit(txt_s, rc.move(0, 1))
            surface.blit(txt, rc)
            return

        # Default Tactical Style
        if self.is_selected:
            bg_color = (15, 60, 95)
            border_color = self.accent_color
            border_width = 2
        elif self.is_hovered:
            bg_color = COLOR_BTN_HOVER
            border_color = COLOR_BTN_BORDER_HOVER
            border_width = 2
        else:
            bg_color = COLOR_BTN_NORMAL
            border_color = COLOR_BTN_BORDER
            border_width = 1

        pygame.draw.rect(surface, (6, 10, 16), self.rect.move(0, 2), border_radius=4)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)
        pygame.draw.rect(surface, border_color, self.rect, width=border_width, border_radius=4)

        pygame.draw.line(surface, (min(255, bg_color[0] + 35), min(255, bg_color[1] + 40), min(255, bg_color[2] + 55)),
                         (self.rect.left + 2, self.rect.top + 2), (self.rect.right - 3, self.rect.top + 2), 1)

        t_len = 5
        x, y, w, h = self.rect
        pygame.draw.line(surface, self.accent_color, (x, y), (x + t_len, y), 2)
        pygame.draw.line(surface, self.accent_color, (x, y), (x, y + t_len), 2)
        pygame.draw.line(surface, self.accent_color, (x + w - 1, y + h - 1), (x + w - 1 - t_len, y + h - 1), 2)
        pygame.draw.line(surface, self.accent_color, (x + w - 1, y + h - 1), (x + w - 1, y + h - 1 - t_len), 2)

        if self.is_selected:
            pygame.draw.circle(surface, self.accent_color, (self.rect.right - 7, self.rect.top + 7), 2)

        text_color = COLOR_TEXT_PRIMARY if (self.is_hovered or self.is_selected) else COLOR_TEXT_SECONDARY
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class TextInputBox:
    """Tactical text input field for player callsign input."""

    def __init__(self, rect: pygame.Rect, font: pygame.font.Font,
                 placeholder: str = "OPERATIVE-01",
                 style: str = "tactical") -> None:
        self.rect = rect
        self.font = font
        self.text = "OPERATIVE-01"
        self.placeholder = placeholder
        self.style = style
        self.is_active = False
        self.cursor_visible = True
        self.cursor_timer = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard typing and mouse focus events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                self.is_active = False
            else:
                if len(self.text) < 16 and (event.unicode.isalnum() or event.unicode in "-_ "):
                    self.text += event.unicode.upper()

    def update(self, dt: float) -> None:
        """Blink cursor every 0.5s."""
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0.0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surface: pygame.Surface) -> None:
        """Draw text input field with style-specific borders and prompt."""
        if self.style == "wood_recessed":
            pygame.draw.rect(surface, (54, 26, 10), self.rect, border_radius=8)
            pygame.draw.rect(surface, (148, 88, 42), self.rect.inflate(-4, -4), border_radius=6)
            pygame.draw.rect(surface, (216, 172, 116), self.rect.inflate(-6, -6), border_radius=5)
            if self.is_active:
                pygame.draw.rect(surface, (255, 215, 80), self.rect, width=2, border_radius=8)

            display_text = self.text if self.text else self.placeholder
            text_surf = self.font.render(display_text, True, (38, 16, 4))
            text_rc = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rc)

            if self.is_active and self.cursor_visible:
                cx = text_rc.right + 4
                cy = self.rect.y + 8
                ch = self.rect.height - 16
                pygame.draw.line(surface, (38, 16, 4), (cx, cy), (cx, cy + ch), 2)
            return

        border_color = COLOR_TEXT_ACCENT_CYAN if self.is_active else COLOR_BTN_BORDER
        bg_color = (18, 26, 42) if self.is_active else (14, 20, 32)

        pygame.draw.rect(surface, (6, 10, 16), self.rect.move(0, 2), border_radius=4)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)
        pygame.draw.rect(surface, border_color, self.rect, width=2 if self.is_active else 1, border_radius=4)

        prefix_surf = self.font.render(">", True, COLOR_TEXT_ACCENT_CYAN if self.is_active else COLOR_TEXT_MUTED)
        surface.blit(prefix_surf, (self.rect.x + 10, self.rect.y + (self.rect.height - prefix_surf.get_height()) // 2))

        display_text = self.text if self.text else self.placeholder
        text_color = COLOR_TEXT_PRIMARY if self.text else COLOR_TEXT_MUTED

        text_surf = self.font.render(display_text, True, text_color)
        surface.blit(text_surf, (self.rect.x + 24, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))

        if self.is_active and self.cursor_visible:
            cursor_x = self.rect.x + 24 + text_surf.get_width() + 2
            cursor_y = self.rect.y + 6
            cursor_h = self.rect.height - 12
            pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_h), 2)
