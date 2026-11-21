"""
UI Level Select Screen: 1-50 chamber selector with completed emerald tiles,
glowing selected gold tile, locked stone tiles with metallic padlock,
and responsive pagination.
"""

from typing import List, Dict, Any, Optional
import pygame

from .art_helpers import (
    draw_dungeon_background,
    draw_parchment_chassis,
    draw_royal_crown,
    draw_adventure_title,
    draw_padlock,
)
from .widgets import UIButton


class LevelSelectScreenRenderer:
    """Renders the 1-50 Expedition Chamber Select Level screen."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

    def _draw_level_tile(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        lvl_num: int,
        state: str,
        font_input: pygame.font.Font
    ) -> None:
        """Draw an individual level tile: green completed, golden glowing selected, or locked stone with padlock."""
        if state == "selected":
            pygame.draw.rect(surface, (100, 48, 6), rect.move(0, 3), border_radius=8)
            pygame.draw.rect(surface, (250, 182, 52), rect, border_radius=8)
            pygame.draw.rect(surface, (255, 222, 118), rect.inflate(-4, -4), border_radius=6)
            pygame.draw.rect(surface, (246, 170, 40), rect.inflate(-6, -6), border_radius=5)
            pygame.draw.rect(surface, (92, 42, 6), rect, width=3, border_radius=8)
            txt = font_input.render(str(lvl_num), True, (48, 18, 4))
            surface.blit(txt, txt.get_rect(center=rect.center))

        elif state == "completed":
            pygame.draw.rect(surface, (12, 54, 28), rect.move(0, 3), border_radius=8)
            pygame.draw.rect(surface, (34, 148, 82), rect, border_radius=8)
            pygame.draw.rect(surface, (60, 188, 112), rect.inflate(-4, -4), border_radius=6)
            pygame.draw.rect(surface, (28, 136, 74), rect.inflate(-6, -6), border_radius=5)
            pygame.draw.rect(surface, (10, 50, 26), rect, width=2, border_radius=8)

            txt = font_input.render(str(lvl_num), True, (255, 218, 88))
            txt_s = font_input.render(str(lvl_num), True, (10, 50, 26))
            rc = txt.get_rect(center=rect.center)
            surface.blit(txt_s, rc.move(0, 1))
            surface.blit(txt, rc)

        else:
            # Drop shadow
            pygame.draw.rect(surface, (42, 38, 34), rect.move(0, 3), border_radius=8)
            # Stone body with bevel
            pygame.draw.rect(surface, (132, 122, 114), rect, border_radius=8)
            pygame.draw.rect(surface, (162, 152, 144), rect.inflate(-4, -4), border_radius=6)
            pygame.draw.rect(surface, (118, 108, 100), rect.inflate(-6, -6), border_radius=5)
            pygame.draw.rect(surface, (48, 42, 38), rect, width=2, border_radius=8)

            # Authentic stone fissure cracks
            pygame.draw.line(surface, (78, 70, 64), (rect.x + 8, rect.bottom - 10), (rect.x + 18, rect.bottom - 18), 1)
            pygame.draw.line(surface, (78, 70, 64), (rect.right - 10, rect.y + 10), (rect.right - 18, rect.y + 18), 1)

            # Carved stone number
            txt = font_input.render(str(lvl_num), True, (56, 48, 42))
            txt_shadow = font_input.render(str(lvl_num), True, (176, 168, 160))
            num_rc = txt.get_rect(center=(rect.centerx, rect.y + 17))
            surface.blit(txt_shadow, num_rc.move(0, 1))
            surface.blit(txt, num_rc)

            # Padlock icon
            draw_padlock(surface, rect.centerx, rect.bottom - 14)

    def draw_level_select_screen(
        self,
        surface: pygame.Surface,
        level_tile_buttons: List[UIButton],
        btn_level_play: UIButton,
        btn_level_back: UIButton,
        selected_chamber_level: int,
        user_stats: Optional[Dict[str, Any]],
        font_title_top: pygame.font.Font,
        font_label: pygame.font.Font,
        font_input: pygame.font.Font
    ) -> None:
        """Render the exact retro-pixel RPG Select Level parchment screen."""
        cx = self.screen_width // 2
        card_w = 560
        card_h = 715
        card_x = cx - card_w // 2
        card_y = 30
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # 1. Dark dungeon stone brick wall background
        draw_dungeon_background(surface, self.screen_width, self.screen_height)

        # 2. Main Parchment Sheet Chassis
        draw_parchment_chassis(surface, card_rect)

        # 3. Royal Crown & 3D Title "SELECT LEVEL"
        draw_royal_crown(surface, cx, card_y + 26)
        draw_adventure_title(surface, "SELECT LEVEL", card_y + 48, font_title_top, cx)

        # Calculate max unlocked level from user stats
        victories = user_stats.get("victories", 0) if user_stats else 11
        unlocked_max = max(1, min(50, 1 + victories))

        # Check page offset based on selected level
        base_offset = 15 if selected_chamber_level > 35 else 0

        # Draw the 35 level tiles (5x7)
        for i, btn in enumerate(level_tile_buttons):
            lvl = base_offset + i + 1
            btn.tag = str(lvl)

            if lvl == selected_chamber_level:
                st = "selected"
            elif lvl <= unlocked_max:
                st = "completed"
            else:
                st = "locked"

            self._draw_level_tile(surface, btn.rect, lvl, st, font_input)

        # 4. Status Footer: "UNLOCKED: {unlocked_max} / 50"
        st_y = card_y + 115 + 7 * 66 + 8
        status_txt = font_label.render(f"UNLOCKED: {unlocked_max} / 50", True, (54, 24, 6))
        surface.blit(status_txt, status_txt.get_rect(center=(cx, st_y)))

        # 5. Bottom Action Buttons: [ PLAY LEVEL {N} ] and [ BACK ]
        btn_level_play.text = f"PLAY LEVEL {selected_chamber_level}"
        btn_level_play.draw(surface)
        btn_level_back.draw(surface)
