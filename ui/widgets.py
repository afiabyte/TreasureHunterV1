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
                bg = (152, 142, 134) if self.is_hovered else (138, 128, 120)
                pygame.draw.rect(surface, (54, 48, 44), self.rect.move(0, 4), border_radius=10)
                pygame.draw.rect(surface, bg, self.rect, border_radius=10)
                pygame.draw.rect(surface, (172, 162, 154), self.rect.inflate(-4, -4), border_radius=8)
                pygame.draw.rect(surface, (122, 112, 104), self.rect.inflate(-8, -8), border_radius=6)
                pygame.draw.rect(surface, (48, 42, 38), self.rect, width=2, border_radius=10)
                txt = self.font.render(self.text, True, (38, 32, 28))
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

        elif self.style == "amber_glow":
            if self.is_selected:
                # Golden amber selected button with warm glow
                pygame.draw.rect(surface, (100, 48, 6), self.rect.move(0, 3), border_radius=10)
                pygame.draw.rect(surface, (250, 182, 52), self.rect, border_radius=10)
                pygame.draw.rect(surface, (255, 225, 120), self.rect.inflate(-4, -4), border_radius=8)
                pygame.draw.rect(surface, (242, 160, 32), self.rect.inflate(-8, -8), border_radius=6)
                pygame.draw.rect(surface, (92, 42, 6), self.rect, width=3, border_radius=10)

                txt = self.font.render(self.text, True, (52, 22, 4))
                txt_s = self.font.render(self.text, True, (255, 230, 140))
                rc = txt.get_rect(center=self.rect.center)
                surface.blit(txt_s, rc.move(0, 1))
                surface.blit(txt, rc)
            else:
                # Unselected stone button
                bg = (110, 104, 100) if self.is_hovered else (96, 90, 86)
                pygame.draw.rect(surface, (40, 36, 34), self.rect.move(0, 3), border_radius=10)
                pygame.draw.rect(surface, bg, self.rect, border_radius=10)
                pygame.draw.rect(surface, (135, 128, 122), self.rect.inflate(-4, -4), border_radius=8)
                pygame.draw.rect(surface, (84, 78, 74), self.rect.inflate(-8, -8), border_radius=6)
                pygame.draw.rect(surface, (36, 32, 30), self.rect, width=2, border_radius=10)

                txt = self.font.render(self.text, True, (35, 30, 28))
                rc = txt.get_rect(center=self.rect.center)
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

        elif self.style == "history_pill":
            c_shadow = (22, 14, 26)
            c_face = (60, 44, 66) if self.is_hovered else (48, 34, 54)
            c_light = (86, 64, 94)
            c_inner = (36, 24, 42)
            c_border = (212, 158, 48)  # Rich golden border
            c_dark_outline = (32, 18, 10)

            # Drop shadow
            pygame.draw.rect(surface, c_shadow, self.rect.move(0, 3), border_radius=10)
            # Golden outer rim
            pygame.draw.rect(surface, c_border, self.rect, border_radius=10)
            # Dark outer contour
            pygame.draw.rect(surface, c_dark_outline, self.rect, width=1, border_radius=10)
            # Body fill
            pygame.draw.rect(surface, c_face, self.rect.inflate(-4, -4), border_radius=8)
            pygame.draw.rect(surface, c_light, self.rect.inflate(-6, -6), width=1, border_radius=7)
            pygame.draw.rect(surface, c_inner, self.rect.inflate(-10, -10), border_radius=6)

            txt = self.font.render(self.text, True, (255, 248, 238))
            txt_s = self.font.render(self.text, True, (16, 8, 20))

            # Render Scroll Icon on Left & Clock Icon on Right
            tw = txt.get_width()
            total_w = 20 + 8 + tw + 8 + 18
            start_x = self.rect.centerx - total_w // 2
            cy = self.rect.centery

            # 1. Left Scroll Icon
            sx = start_x
            sy = cy - 8
            pygame.draw.rect(surface, (238, 214, 166), pygame.Rect(sx + 2, sy + 2, 14, 12))
            pygame.draw.rect(surface, (72, 38, 12), pygame.Rect(sx + 2, sy + 2, 14, 12), 1)
            pygame.draw.rect(surface, (148, 92, 42), pygame.Rect(sx, sy, 18, 4), border_radius=2)
            pygame.draw.rect(surface, (54, 24, 8), pygame.Rect(sx, sy, 18, 4), 1, border_radius=2)
            pygame.draw.rect(surface, (148, 92, 42), pygame.Rect(sx, sy + 12, 18, 4), border_radius=2)
            pygame.draw.rect(surface, (54, 24, 8), pygame.Rect(sx, sy + 12, 18, 4), 1, border_radius=2)
            pygame.draw.line(surface, (150, 110, 70), (sx + 5, sy + 6), (sx + 13, sy + 6), 1)
            pygame.draw.line(surface, (150, 110, 70), (sx + 5, sy + 9), (sx + 11, sy + 9), 1)

            # 2. Text in Middle
            tx = start_x + 28
            ty = cy - txt.get_height() // 2
            surface.blit(txt_s, (tx, ty + 1))
            surface.blit(txt, (tx, ty))

            # 3. Right Clock Icon
            cx_icon = start_x + 28 + tw + 14
            pygame.draw.circle(surface, (48, 24, 8), (cx_icon, cy + 1), 8)
            pygame.draw.circle(surface, (235, 175, 48), (cx_icon, cy), 8)
            pygame.draw.circle(surface, (255, 248, 235), (cx_icon, cy), 6)
            pygame.draw.circle(surface, (48, 24, 8), (cx_icon, cy), 6, 1)
            pygame.draw.line(surface, (48, 24, 8), (cx_icon, cy), (cx_icon - 2, cy - 4), 2)
            pygame.draw.line(surface, (48, 24, 8), (cx_icon, cy), (cx_icon + 3, cy), 2)
            return

        elif self.style == "red_pill":
            c_shadow = (54, 16, 14)
            c_face = (156, 52, 44) if self.is_hovered else (138, 44, 38)
            c_light = (188, 76, 68)
            c_border = (42, 12, 10)
            pygame.draw.rect(surface, c_shadow, self.rect.move(0, 3), border_radius=10)
            pygame.draw.rect(surface, c_face, self.rect, border_radius=10)
            pygame.draw.rect(surface, c_light, self.rect.inflate(-4, -4), border_radius=8)
            pygame.draw.rect(surface, (118, 34, 28), self.rect.inflate(-8, -8), border_radius=6)
            pygame.draw.rect(surface, c_border, self.rect, width=2, border_radius=10)
            txt = self.font.render(self.text, True, (255, 250, 242))
            txt_s = self.font.render(self.text, True, c_border)
            rc = txt.get_rect(center=self.rect.center)
            surface.blit(txt_s, rc.move(0, 1))
            surface.blit(txt, rc)
            return

        elif self.style == "link":
            color = (195, 65, 18) if self.is_hovered else (42, 24, 10)
            txt = self.font.render(self.text, True, color)
            rc = txt.get_rect(center=self.rect.center)
            surface.blit(txt, rc)
            if self.is_hovered:
                pygame.draw.line(surface, color, (rc.left, rc.bottom), (rc.right, rc.bottom), 1)
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
    """Tactical and retro-pixel text input field with password masking and recessed styling."""

    def __init__(self, rect: pygame.Rect, font: pygame.font.Font,
                 placeholder: str = "OPERATIVE-01",
                 style: str = "tactical",
                 initial_text: Optional[str] = None,
                 is_password: bool = False,
                 text_align: str = "left",
                 max_length: int = 32,
                 allow_lower: bool = False,
                 allow_symbols: bool = False) -> None:
        self.rect = rect
        self.font = font
        if initial_text is not None:
            self.text = initial_text
        elif placeholder == "OPERATIVE-01":
            self.text = "OPERATIVE-01"
        else:
            self.text = ""
        self.placeholder = placeholder
        self.style = style
        self.is_password = is_password
        self.text_align = text_align
        self.max_length = max_length
        self.allow_lower = allow_lower
        self.allow_symbols = allow_symbols
        self.is_active = False
        self.cursor_visible = True
        self.cursor_timer = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard typing, character validation, and mouse focus events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                self.is_active = False
            elif event.key == pygame.K_TAB:
                # Tab signals switching active focus
                pass
            else:
                char = event.unicode
                if not char:
                    return

                # Check character allowance
                is_valid = False
                if char.isalnum() or char in "-_ ":
                    is_valid = True
                elif (self.allow_symbols or self.is_password) and char in "@.+!#$%&*?=":
                    is_valid = True

                if is_valid and len(self.text) < self.max_length:
                    if self.allow_lower or self.is_password or self.allow_symbols:
                        self.text += char
                    else:
                        self.text += char.upper()

    def update(self, dt: float) -> None:
        """Blink cursor every 0.5s."""
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0.0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surface: pygame.Surface) -> None:
        """Draw text input field with style-specific borders and prompt."""
        if self.style == "wood_recessed":
            # Outer drop shadow underneath
            pygame.draw.rect(surface, (38, 20, 8), self.rect.move(0, 3), border_radius=10)
            # Recessed cavity plate
            pygame.draw.rect(surface, (186, 142, 98), self.rect, border_radius=10)
            # Inner bevel: top/left shadow, bottom/right highlight
            pygame.draw.rect(surface, (148, 108, 68), self.rect.inflate(-4, -4), width=2, border_radius=8)
            # Outer dark carved wood frame
            pygame.draw.rect(surface, (54, 28, 12), self.rect, width=3, border_radius=10)
            # Golden active focus ring
            if self.is_active:
                pygame.draw.rect(surface, (246, 186, 42), self.rect, width=2, border_radius=10)

            # Draw text or placeholder
            if not self.text:
                txt_surf = self.font.render(self.placeholder, True, (96, 68, 42))
                if self.text_align == "center":
                    rc = txt_surf.get_rect(center=self.rect.center)
                    surface.blit(txt_surf, rc)
                    if self.is_active and self.cursor_visible:
                        cx = self.rect.centerx
                        cy = self.rect.y + 8
                        ch = self.rect.height - 16
                        pygame.draw.line(surface, (45, 22, 10), (cx, cy), (cx, cy + ch), 2)
                else:
                    surface.blit(txt_surf, (self.rect.x + 16, self.rect.y + (self.rect.height - txt_surf.get_height()) // 2))
                    if self.is_active and self.cursor_visible:
                        cx = self.rect.x + 16
                        cy = self.rect.y + 8
                        ch = self.rect.height - 16
                        pygame.draw.line(surface, (45, 22, 10), (cx, cy), (cx, cy + ch), 2)
            elif self.is_password:
                # Masked solid round dots
                dot_count = len(self.text)
                spacing = 14
                total_w = dot_count * spacing
                if self.text_align == "center":
                    start_x = self.rect.centerx - total_w // 2 + spacing // 2
                    cy = self.rect.centery
                    for d in range(dot_count):
                        dx = start_x + d * spacing
                        pygame.draw.circle(surface, (35, 18, 6), (dx, cy), 4)
                    if self.is_active and self.cursor_visible:
                        cx = start_x + (dot_count - 1) * spacing + 10
                        pygame.draw.line(surface, (45, 22, 10), (cx, cy - 8), (cx, cy + 8), 2)
                else:
                    start_x = self.rect.x + 18
                    cy = self.rect.centery
                    for d in range(dot_count):
                        dx = start_x + d * spacing
                        pygame.draw.circle(surface, (35, 18, 6), (dx, cy), 4)
                    if self.is_active and self.cursor_visible:
                        cx = start_x + dot_count * spacing + 4
                        pygame.draw.line(surface, (45, 22, 10), (cx, cy - 8), (cx, cy + 8), 2)
            else:
                txt_surf = self.font.render(self.text, True, (35, 18, 6))
                if self.text_align == "center":
                    rc = txt_surf.get_rect(center=self.rect.center)
                    surface.blit(txt_surf, rc)
                    if self.is_active and self.cursor_visible:
                        cx = rc.right + 4
                        cy = self.rect.y + 8
                        ch = self.rect.height - 16
                        pygame.draw.line(surface, (45, 22, 10), (cx, cy), (cx, cy + ch), 2)
                else:
                    surface.blit(txt_surf, (self.rect.x + 16, self.rect.y + (self.rect.height - txt_surf.get_height()) // 2))
                    if self.is_active and self.cursor_visible:
                        cx = self.rect.x + 16 + txt_surf.get_width() + 4
                        cy = self.rect.y + 8
                        ch = self.rect.height - 16
                        pygame.draw.line(surface, (45, 22, 10), (cx, cy), (cx, cy + ch), 2)
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


class UIToggleSwitch:
    """
    Retro-pixel RPG toggle switch with ON/OFF sliding track and 3D beveled knob.
    Matches the settings toggle switch in the reference mockup.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        is_on: bool = True,
        font: Optional[pygame.font.Font] = None,
        tag: str = ""
    ) -> None:
        self.rect = rect
        self.is_on = is_on
        self.font = font
        self.tag = tag
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse hover and click events. Returns True if toggled."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_on = not self.is_on
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Render the toggle switch with 3D bevels, track text, and sliding knob."""
        rx, ry, rw, rh = self.rect
        knob_w = rh - 8
        knob_h = rh - 8

        if self.is_on:
            # Green ON State
            c_track_shadow = (10, 48, 24)
            c_track_face = (30, 138, 72)
            c_track_light = (60, 180, 105)
            c_track_border = (12, 54, 28)

            pygame.draw.rect(surface, c_track_shadow, self.rect.move(0, 3), border_radius=12)
            pygame.draw.rect(surface, c_track_face, self.rect, border_radius=12)
            pygame.draw.rect(surface, c_track_light, self.rect.inflate(-4, -4), border_radius=10)
            pygame.draw.rect(surface, (24, 115, 60), self.rect.inflate(-8, -8), border_radius=8)
            pygame.draw.rect(surface, c_track_border, self.rect, width=3, border_radius=12)

            # "ON" text on left
            if self.font:
                txt = self.font.render("ON", True, (255, 255, 255))
                txt_s = self.font.render("ON", True, (10, 48, 24))
                tx = rx + 16
                ty = ry + (rh - txt.get_height()) // 2
                surface.blit(txt_s, (tx, ty + 1))
                surface.blit(txt, (tx, ty))

            # Knob on Right
            kx = rx + rw - knob_w - 4
            ky = ry + 4
            knob_rect = pygame.Rect(kx, ky, knob_w, knob_h)

            pygame.draw.rect(surface, (10, 48, 24), knob_rect.move(0, 2), border_radius=8)
            pygame.draw.rect(surface, (46, 204, 113), knob_rect, border_radius=8)
            pygame.draw.rect(surface, (115, 235, 160), knob_rect.inflate(-4, -4), border_radius=6)
            pygame.draw.rect(surface, (36, 170, 94), knob_rect.inflate(-8, -8), border_radius=4)
            pygame.draw.rect(surface, (10, 48, 24), knob_rect, width=2, border_radius=8)

        else:
            # Grey OFF State
            c_track_shadow = (22, 24, 26)
            c_track_face = (62, 68, 72)
            c_track_light = (85, 92, 98)
            c_track_border = (26, 30, 32)

            pygame.draw.rect(surface, c_track_shadow, self.rect.move(0, 3), border_radius=12)
            pygame.draw.rect(surface, c_track_face, self.rect, border_radius=12)
            pygame.draw.rect(surface, c_track_light, self.rect.inflate(-4, -4), border_radius=10)
            pygame.draw.rect(surface, (50, 55, 58), self.rect.inflate(-8, -8), border_radius=8)
            pygame.draw.rect(surface, c_track_border, self.rect, width=3, border_radius=12)

            # "OFF" text on right
            if self.font:
                txt = self.font.render("OFF", True, (175, 180, 184))
                txt_s = self.font.render("OFF", True, (24, 28, 30))
                tx = rx + rw - txt.get_width() - 14
                ty = ry + (rh - txt.get_height()) // 2
                surface.blit(txt_s, (tx, ty + 1))
                surface.blit(txt, (tx, ty))

            # Knob on Left
            kx = rx + 4
            ky = ry + 4
            knob_rect = pygame.Rect(kx, ky, knob_w, knob_h)

            pygame.draw.rect(surface, (20, 22, 24), knob_rect.move(0, 2), border_radius=8)
            pygame.draw.rect(surface, (98, 105, 110), knob_rect, border_radius=8)
            pygame.draw.rect(surface, (140, 148, 154), knob_rect.inflate(-4, -4), border_radius=6)
            pygame.draw.rect(surface, (80, 86, 90), knob_rect.inflate(-8, -8), border_radius=4)
            pygame.draw.rect(surface, (26, 30, 32), knob_rect, width=2, border_radius=8)

