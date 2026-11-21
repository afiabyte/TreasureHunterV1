"""
Settings Screen Renderer: Retro-pixel RPG Settings screen matching reference mockup 1:1.

Features:
- Dungeon stone wall background with warm torchlight ambiance.
- 5-point golden royal crown with emerald jewel.
- 3D Adventure typography title: "SETTINGS".
- Aged parchment scroll card with carved wood border and 4 golden brass rivets.
- Wood recessed label plates for each configuration setting.
- Interactive retro-pixel ON/OFF toggle switches for Audio SFX, BGM, and AI Commander Hints.
- Move Animation selector (SMOOTH vs FAST) with glowing pixel lantern on the active choice.
- API Key Status emerald ribbon with swallowtail dovetail notch.
- "SAVE & APPLY" (Green CTA) and "BACK TO MENU" (Wood) action buttons.
"""

import math
from typing import Optional
import pygame

from .art_helpers import (
    draw_dungeon_background,
    draw_parchment_chassis,
    draw_royal_crown,
    draw_adventure_title,
)
from .widgets import UIButton, UIToggleSwitch


class SettingsScreenRenderer:
    """Renders the authentic retro-pixel RPG adventure Settings screen."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Cached fonts for performance and typography consistency
        self.font_title = pygame.font.SysFont("impact", 54)
        self.font_plate = pygame.font.SysFont("impact", 18)
        self.font_toggle = pygame.font.SysFont("impact", 19)
        self.font_btn = pygame.font.SysFont("impact", 22)
        self.font_ribbon = pygame.font.SysFont("impact", 18)
        self.font_version = pygame.font.SysFont("courier", 11)

        # Pre-cached radial lantern glow surface
        self._glow_radius = 42
        self._lantern_glow = pygame.Surface((self._glow_radius * 2, self._glow_radius * 2), pygame.SRCALPHA)
        for r in range(self._glow_radius, 0, -2):
            alpha = int(55 * (1.0 - (r / self._glow_radius) ** 1.4))
            pygame.draw.circle(
                self._lantern_glow,
                (255, 205, 45, alpha),
                (self._glow_radius, self._glow_radius),
                r
            )

    def draw_wood_plate(self, surface: pygame.Surface, rect: pygame.Rect, text: str) -> None:
        """Render carved wood-recessed plate matching the reference mockup."""
        # Bottom drop shadow
        pygame.draw.rect(surface, (36, 18, 6), rect.move(0, 3), border_radius=9)

        # Wood base plate (warm dark oak)
        pygame.draw.rect(surface, (148, 90, 42), rect, border_radius=9)

        # Inner lighter wood face
        inner = rect.inflate(-4, -4)
        pygame.draw.rect(surface, (178, 114, 58), inner, border_radius=7)

        # Top recessed shadow line
        pygame.draw.line(surface, (100, 56, 22), (rect.left + 8, rect.top + 3), (rect.right - 8, rect.top + 3), 2)
        # Bottom bevel highlight line
        pygame.draw.line(surface, (215, 150, 90), (rect.left + 8, rect.bottom - 4), (rect.right - 8, rect.bottom - 4), 2)

        # Dark carved contour border
        pygame.draw.rect(surface, (45, 22, 10), rect, width=3, border_radius=9)

        # Carved text with highlight shadow
        txt = self.font_plate.render(text, True, (35, 16, 5))
        txt_s = self.font_plate.render(text, True, (215, 155, 96))
        rc = txt.get_rect(center=rect.center)
        surface.blit(txt_s, rc.move(0, 1))
        surface.blit(txt, rc)

    def draw_lantern(self, surface: pygame.Surface, center_x: int, top_y: int, anim_time: float = 0.0) -> None:
        """
        Render the golden glowing pixel-art lantern sitting atop the selected animation mode button.
        Matches the lantern in media_1795244853028_f736cb43.jpg.
        """
        # Soft warm flickering glow halo
        gx = center_x - self._glow_radius
        gy = top_y + 12 - self._glow_radius
        surface.blit(self._lantern_glow, (gx, gy))

        # Top iron ring handle
        pygame.draw.circle(surface, (38, 20, 10), (center_x, top_y - 4), 7, 2)
        pygame.draw.circle(surface, (185, 120, 50), (center_x, top_y - 5), 5, 1)

        # Bronze lantern chimney / cap
        cap_pts = [
            (center_x - 14, top_y + 5),
            (center_x + 14, top_y + 5),
            (center_x + 8, top_y - 2),
            (center_x - 8, top_y - 2)
        ]
        pygame.draw.polygon(surface, (38, 20, 10), [(px, py + 2) for px, py in cap_pts])
        pygame.draw.polygon(surface, (168, 102, 38), cap_pts)
        pygame.draw.polygon(surface, (38, 20, 10), cap_pts, 2)

        # Glass chamber
        glass_w, glass_h = 24, 24
        glass_rect = pygame.Rect(center_x - glass_w // 2, top_y + 6, glass_w, glass_h)
        pygame.draw.rect(surface, (38, 20, 10), glass_rect.move(0, 1), border_radius=4)
        # Warm golden illuminated glass fill
        pygame.draw.rect(surface, (255, 215, 50), glass_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 242, 130), glass_rect.inflate(-4, -4), border_radius=3)

        # Inner flickering flame core
        flame_h = int(10 + 2 * math.sin(anim_time * 10.0))
        flame_rect = pygame.Rect(center_x - 4, top_y + 17 - flame_h // 2, 8, flame_h)
        pygame.draw.ellipse(surface, (255, 120, 15), flame_rect.inflate(5, 3))
        pygame.draw.ellipse(surface, (255, 255, 215), flame_rect)

        # Dark vertical glass struts & frame
        pygame.draw.rect(surface, (45, 24, 10), glass_rect, width=2, border_radius=4)
        pygame.draw.line(surface, (45, 24, 10), (center_x - 5, glass_rect.top), (center_x - 5, glass_rect.bottom), 1)
        pygame.draw.line(surface, (45, 24, 10), (center_x + 5, glass_rect.top), (center_x + 5, glass_rect.bottom), 1)

        # Bronze lantern base / foot resting on the button
        base_rect = pygame.Rect(center_x - 14, top_y + 29, 28, 5)
        pygame.draw.rect(surface, (38, 20, 10), base_rect.move(0, 1), border_radius=2)
        pygame.draw.rect(surface, (160, 95, 35), base_rect, border_radius=2)
        pygame.draw.rect(surface, (38, 20, 10), base_rect, width=2, border_radius=2)

    def draw_api_ribbon(self, surface: pygame.Surface, rect: pygame.Rect, is_connected: bool) -> None:
        """Render Emerald Ribbon banner with swallowtail notch for API KEY STATUS."""
        ribbon_text = "CONNECTED" if is_connected else "NOT SET"

        if is_connected:
            c_shadow = (10, 48, 24)
            c_face = (30, 138, 72)
            c_light = (60, 180, 105)
            c_inner = (24, 115, 60)
            c_border = (10, 50, 26)
        else:
            c_shadow = (24, 26, 28)
            c_face = (65, 72, 78)
            c_light = (90, 98, 104)
            c_inner = (52, 58, 62)
            c_border = (26, 30, 32)

        # Drop shadow
        pygame.draw.rect(surface, c_shadow, rect.move(0, 3), border_radius=6)
        # Main ribbon body
        pygame.draw.rect(surface, c_face, rect, border_radius=6)
        pygame.draw.rect(surface, c_light, rect.inflate(-4, -4), border_radius=4)
        pygame.draw.rect(surface, c_inner, rect.inflate(-8, -8), border_radius=3)
        pygame.draw.rect(surface, c_border, rect, width=3, border_radius=6)

        # Swallowtail / Dovetail notch at the bottom edge
        notch_pts = [
            (rect.x + 2, rect.bottom - 1),
            (rect.centerx, rect.bottom + 11),
            (rect.right - 2, rect.bottom - 1),
        ]
        pygame.draw.polygon(surface, c_inner, notch_pts)
        pygame.draw.lines(surface, c_border, False, notch_pts, 3)

        # Text
        txt = self.font_ribbon.render(ribbon_text, True, (255, 255, 255))
        txt_s = self.font_ribbon.render(ribbon_text, True, c_border)
        t_rc = txt.get_rect(center=rect.center)
        surface.blit(txt_s, t_rc.move(0, 1))
        surface.blit(txt, t_rc)

    def draw_parchment_with_screws(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render aged parchment scroll chassis with slotted brass screw rivets."""
        draw_parchment_chassis(surface, rect)

        # Add screw slots (-) to the 4 corner rivets
        rivet_offset = 22
        rivet_pts = [
            (rect.left + rivet_offset, rect.top + rivet_offset),
            (rect.right - rivet_offset, rect.top + rivet_offset),
            (rect.left + rivet_offset, rect.bottom - rivet_offset),
            (rect.right - rivet_offset, rect.bottom - rivet_offset),
        ]
        for rx, ry in rivet_pts:
            pygame.draw.line(surface, (54, 30, 12), (rx - 4, ry), (rx + 4, ry), 2)

    def draw_settings_screen(
        self,
        surface: pygame.Surface,
        toggle_sfx: UIToggleSwitch,
        toggle_bgm: UIToggleSwitch,
        toggle_ai_hints: UIToggleSwitch,
        btn_anim_smooth: UIButton,
        btn_anim_fast: UIButton,
        is_smooth_selected: bool,
        is_api_connected: bool,
        btn_save: UIButton,
        btn_back: UIButton,
        anim_time: float = 0.0,
        status_message: str = ""
    ) -> None:
        """Draw complete Settings screen matching reference mockup media_1795244853028_f736cb43.jpg."""
        # 1. Dungeon stone background
        draw_dungeon_background(surface, self.screen_width, self.screen_height)

        cx = self.screen_width // 2

        # 2. Golden Royal Crown & Title "SETTINGS"
        draw_royal_crown(surface, cx, 40)
        draw_adventure_title(surface, "SETTINGS", 70, self.font_title, cx)

        # 3. Parchment Card
        card_w = 510
        card_h = 575
        card_x = cx - card_w // 2
        card_y = 125
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        self.draw_parchment_with_screws(surface, card_rect)

        # 4. Row 1: SOUND EFFECTS
        plate_sfx_rect = pygame.Rect(card_x + 34, card_y + 44, 290, 46)
        self.draw_wood_plate(surface, plate_sfx_rect, "SOUND EFFECTS")
        toggle_sfx.rect = pygame.Rect(card_x + 338, card_y + 44, 138, 46)
        toggle_sfx.font = self.font_toggle
        toggle_sfx.draw(surface)

        # 5. Row 2: BACKGROUND MUSIC
        plate_bgm_rect = pygame.Rect(card_x + 34, card_y + 110, 290, 46)
        self.draw_wood_plate(surface, plate_bgm_rect, "BACKGROUND MUSIC")
        toggle_bgm.rect = pygame.Rect(card_x + 338, card_y + 110, 138, 46)
        toggle_bgm.font = self.font_toggle
        toggle_bgm.draw(surface)

        # 6. Row 3: AI COMMANDER HINTS
        plate_hints_rect = pygame.Rect(card_x + 34, card_y + 176, 290, 46)
        self.draw_wood_plate(surface, plate_hints_rect, "AI COMMANDER HINTS")
        toggle_ai_hints.rect = pygame.Rect(card_x + 338, card_y + 176, 138, 46)
        toggle_ai_hints.font = self.font_toggle
        toggle_ai_hints.draw(surface)

        # 7. Row 4: MOVE ANIMATION (SMOOTH vs FAST)
        plate_anim_rect = pygame.Rect(card_x + 34, card_y + 246, 206, 46)
        self.draw_wood_plate(surface, plate_anim_rect, "MOVE ANIMATION")

        btn_anim_smooth.rect = pygame.Rect(card_x + 252, card_y + 246, 110, 46)
        btn_anim_fast.rect = pygame.Rect(card_x + 368, card_y + 246, 108, 46)

        btn_anim_smooth.is_selected = is_smooth_selected
        btn_anim_fast.is_selected = not is_smooth_selected

        btn_anim_smooth.draw(surface)
        btn_anim_fast.draw(surface)

        # Draw glowing lantern on selected option
        active_btn = btn_anim_smooth if is_smooth_selected else btn_anim_fast
        lantern_cx = active_btn.rect.centerx
        lantern_top_y = active_btn.rect.top - 18
        self.draw_lantern(surface, lantern_cx, lantern_top_y, anim_time)

        # 8. Row 5: API KEY STATUS
        plate_api_rect = pygame.Rect(card_x + 34, card_y + 318, 258, 46)
        self.draw_wood_plate(surface, plate_api_rect, "API KEY STATUS")

        ribbon_rect = pygame.Rect(card_x + 304, card_y + 318, 172, 46)
        self.draw_api_ribbon(surface, ribbon_rect, is_api_connected)

        # Status feedback banner (if any)
        if status_message:
            st_col = (30, 138, 72) if "APPLIED" in status_message or "SAVED" in status_message else (180, 50, 30)
            st_surf = self.font_plate.render(status_message, True, st_col)
            surface.blit(st_surf, st_surf.get_rect(center=(cx, card_y + 380)))

        # 9. Button 1: SAVE & APPLY
        btn_save.rect = pygame.Rect(cx - 145, card_y + 406, 290, 48)
        btn_save.font = self.font_btn
        btn_save.draw(surface)

        # 10. Button 2: BACK TO MENU
        btn_back.rect = pygame.Rect(cx - 145, card_y + 472, 290, 48)
        btn_back.font = self.font_btn
        btn_back.draw(surface)

        # Version watermark in bottom right corner
        v_surf = self.font_version.render("v1.2.0", True, (65, 55, 58))
        surface.blit(v_surf, (self.screen_width - 55, self.screen_height - 24))
