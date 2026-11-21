"""
UI Login Screen: Operative authentication, SQLite dossier connection, and registration.
"""

from typing import List, Dict, Any, Optional
import pygame

from .colors import (
    COLOR_BG,
    COLOR_KEY_GOLD,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_ACCENT_AMBER,
    COLOR_TEXT_ACCENT_GREEN,
)
from .widgets import UIButton, TextInputBox


class LoginScreenRenderer:
    """Renders the Operative Authentication and Dossier Registration screen."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

    def draw(
        self,
        surface: pygame.Surface,
        input_username: TextInputBox,
        btn_submit: UIButton,
        btn_guest: UIButton,
        font_badge: pygame.font.Font,
        font_title: pygame.font.Font,
        font_bold: pygame.font.Font,
        font_small: pygame.font.Font,
        recent_operatives: Optional[List[Dict[str, Any]]] = None,
        status_msg: str = "AWAITING CREDENTIALS"
    ) -> None:
        """Render the complete Login screen."""
        surface.fill(COLOR_BG)
        cx = self.screen_width // 2

        # 1. Subtle Background Grid
        for x in range(0, self.screen_width, 60):
            pygame.draw.line(surface, (14, 20, 32), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, 60):
            pygame.draw.line(surface, (14, 20, 32), (0, y), (self.screen_width, y), 1)

        # 2. Header
        cat_badge = font_badge.render("// EXPLORER GUILD DOSSIER :: REGISTRATION //", True, COLOR_TEXT_ACCENT_AMBER)
        surface.blit(cat_badge, cat_badge.get_rect(center=(cx, 32)))

        main_title = font_title.render("EXPLORER AUTHENTICATION", True, COLOR_KEY_GOLD)
        sh_title = font_title.render("EXPLORER AUTHENTICATION", True, (90, 60, 15))
        surface.blit(sh_title, sh_title.get_rect(center=(cx + 2, 68)))
        surface.blit(main_title, main_title.get_rect(center=(cx, 66)))

        sub_title = font_bold.render("LINK PERSISTENT EXPEDITION RECORDS & RELIC VICTORIES IN SQLITE ARCHIVES", True, (215, 205, 180))
        surface.blit(sub_title, sub_title.get_rect(center=(cx, 100)))

        # 3. Glassmorphic Chassis
        card_w = 540
        card_h = 350
        card_x = cx - card_w // 2
        card_y = 135
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        pygame.draw.rect(surface, (6, 8, 14), card_rect.move(0, 4), border_radius=8)
        glass_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        glass_surf.fill((16, 20, 30, 240))
        surface.blit(glass_surf, card_rect.topleft)

        pygame.draw.rect(surface, (65, 80, 110), card_rect, width=1, border_radius=8)
        pygame.draw.rect(surface, (225, 175, 55), card_rect.inflate(-4, -4), width=1, border_radius=6)

        t_sz = 12
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x, card_y), (card_x + t_sz, card_y), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x, card_y), (card_x, card_y + t_sz), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x + card_w - 1, card_y), (card_x + card_w - 1 - t_sz, card_y), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x + card_w - 1, card_y), (card_x + card_w - 1, card_y + t_sz), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x, card_y + card_h - 1), (card_x + t_sz, card_y + card_h - 1), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x, card_y + card_h - 1), (card_x, card_y + card_h - 1 - t_sz), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x + card_w - 1, card_y + card_h - 1), (card_x + card_w - 1 - t_sz, card_y + card_h - 1), 2)
        pygame.draw.line(surface, COLOR_KEY_GOLD, (card_x + card_w - 1, card_y + card_h - 1), (card_x + card_w - 1, card_y + card_h - 1 - t_sz), 2)

        pygame.draw.line(surface, (45, 55, 78), (card_x + 20, card_y + 34), (card_x + card_w - 20, card_y + 34), 1)
        ribbon_txt = font_badge.render("// GUILD ARCHIVES :: EXPEDITION REGISTRATION //", True, COLOR_TEXT_SECONDARY)
        surface.blit(ribbon_txt, (card_x + 24, card_y + 12))

        # Avatar Emblem
        avatar_cx = cx
        avatar_cy = card_y + 70
        pygame.draw.circle(surface, (25, 20, 24), (avatar_cx, avatar_cy), 24)
        pygame.draw.circle(surface, (225, 175, 55), (avatar_cx, avatar_cy), 24, 2)
        pygame.draw.ellipse(surface, (140, 85, 45), pygame.Rect(avatar_cx - 16, avatar_cy - 8, 32, 14))
        pygame.draw.ellipse(surface, (225, 175, 55), pygame.Rect(avatar_cx - 10, avatar_cy - 12, 20, 8))
        pygame.draw.circle(surface, (255, 255, 255), (avatar_cx - 4, avatar_cy - 2), 2)
        pygame.draw.circle(surface, (255, 255, 255), (avatar_cx + 4, avatar_cy - 2), 2)

        lbl = font_bold.render("ENTER EXPLORER CALLSIGN / NAME:", True, COLOR_TEXT_PRIMARY)
        surface.blit(lbl, lbl.get_rect(center=(cx, card_y + 116)))

        input_username.draw(surface)

        stat_color = COLOR_TEXT_ACCENT_GREEN if ("SUCCESS" in status_msg.upper() or "AUTHENTICATED" in status_msg.upper()) else COLOR_TEXT_MUTED
        st_surf = font_small.render(f"STATUS: {status_msg}", True, stat_color)
        surface.blit(st_surf, st_surf.get_rect(center=(cx, card_y + 195)))

        btn_submit.draw(surface)
        btn_guest.draw(surface)

        note_surf = font_small.render("[ All expedition progress is automatically saved to SQLite dungeon_records.db ]", True, COLOR_TEXT_MUTED)
        surface.blit(note_surf, note_surf.get_rect(center=(cx, self.screen_height - 35)))
