"""
UI Home Screen: Main menu with retro-pixel RPG parchment chassis,
difficulty segmented selector, player name input, grid size stones,
levels modal, settings modal, and 2x2 secondary navigation grid with centered exit.
Matches reference mockup media_1795249357223_64b6ffbf.jpg 1:1.
"""

from typing import List, Dict, Any, Optional
import pygame

from .art_helpers import (
    draw_dungeon_background,
    draw_parchment_chassis,
    draw_royal_crown,
    draw_adventure_title,
)
from .widgets import UIButton, TextInputBox


class HomeScreenRenderer:
    """Renders the retro-pixel RPG adventure Main Menu screen."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_version = pygame.font.SysFont("courier", 11)

    def _draw_trophy_badge(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        text: str,
        font_badge: pygame.font.Font
    ) -> None:
        """Render carved wood capsule trophy plaque matching mockup."""
        # Bottom drop shadow
        pygame.draw.rect(surface, (36, 18, 6), rect.move(0, 3), border_radius=10)

        # Wood base plate
        pygame.draw.rect(surface, (155, 96, 46), rect, border_radius=10)

        # Inner lighter wood face
        inner = rect.inflate(-4, -4)
        pygame.draw.rect(surface, (186, 122, 64), inner, border_radius=8)

        # Bevel highlight lines
        pygame.draw.line(surface, (215, 150, 90), (rect.left + 8, rect.top + 3), (rect.right - 8, rect.top + 3), 2)
        pygame.draw.line(surface, (108, 62, 26), (rect.left + 8, rect.bottom - 4), (rect.right - 8, rect.bottom - 4), 2)

        # Dark carved contour border
        pygame.draw.rect(surface, (45, 22, 10), rect, width=2, border_radius=10)

        # 3D Golden Trophy Cup icon
        ic_x = rect.left + 22
        ic_y = rect.centery

        # Handles
        pygame.draw.arc(surface, (50, 22, 6), pygame.Rect(ic_x - 12, ic_y - 7, 7, 9), 1.2, 4.8, 2)
        pygame.draw.arc(surface, (246, 186, 42), pygame.Rect(ic_x - 12, ic_y - 7, 7, 9), 1.4, 4.6, 1)
        pygame.draw.arc(surface, (50, 22, 6), pygame.Rect(ic_x + 5, ic_y - 7, 7, 9), 4.6, 1.8, 2)
        pygame.draw.arc(surface, (246, 186, 42), pygame.Rect(ic_x + 5, ic_y - 7, 7, 9), 4.8, 1.6, 1)

        # Chalice cup
        cup_pts = [(ic_x - 7, ic_y - 8), (ic_x + 7, ic_y - 8), (ic_x + 5, ic_y + 1), (ic_x - 5, ic_y + 1)]
        pygame.draw.polygon(surface, (50, 22, 6), [(px, py + 1) for px, py in cup_pts])
        pygame.draw.polygon(surface, (248, 186, 42), cup_pts)
        pygame.draw.polygon(surface, (255, 230, 110), [
            (ic_x - 5, ic_y - 7), (ic_x + 5, ic_y - 7), (ic_x + 3, ic_y), (ic_x - 3, ic_y)
        ])
        pygame.draw.polygon(surface, (50, 22, 6), cup_pts, 1)

        # Stem & Base
        pygame.draw.rect(surface, (50, 22, 6), pygame.Rect(ic_x - 2, ic_y + 1, 4, 4))
        pygame.draw.rect(surface, (248, 186, 42), pygame.Rect(ic_x - 2, ic_y + 1, 4, 3))
        base_pts = [(ic_x - 3, ic_y + 4), (ic_x + 3, ic_y + 4), (ic_x + 6, ic_y + 8), (ic_x - 6, ic_y + 8)]
        pygame.draw.polygon(surface, (50, 22, 6), [(px, py + 1) for px, py in base_pts])
        pygame.draw.polygon(surface, (215, 142, 22), base_pts)
        pygame.draw.polygon(surface, (255, 218, 80), [(ic_x - 2, ic_y + 5), (ic_x + 2, ic_y + 5), (ic_x + 4, ic_y + 7), (ic_x - 4, ic_y + 7)])
        pygame.draw.polygon(surface, (50, 22, 6), base_pts, 1)

        # Label text
        lbl = font_badge.render(text, True, (42, 18, 6))
        lbl_s = font_badge.render(text, True, (225, 165, 105))
        rc = lbl.get_rect(midleft=(rect.left + 38, rect.centery))
        surface.blit(lbl_s, rc.move(0, 1))
        surface.blit(lbl, rc)

    def _draw_difficulty_bar(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        level_buttons: List[UIButton],
        font_btn_bold: pygame.font.Font
    ) -> None:
        """Render segmented difficulty selector with active Emerald Ribbon banner."""
        # Drop shadow & track
        pygame.draw.rect(surface, (36, 18, 6), rect.move(0, 3), border_radius=8)
        pygame.draw.rect(surface, (68, 34, 12), rect, border_radius=8)
        pygame.draw.rect(surface, (186, 128, 76), rect.inflate(-4, -4), border_radius=6)
        pygame.draw.rect(surface, (140, 84, 38), rect.inflate(-8, -8), border_radius=4)
        pygame.draw.rect(surface, (45, 20, 8), rect, width=2, border_radius=8)

        for btn in level_buttons:
            if btn.is_selected:
                # Active Emerald Green Ribbon banner
                ribbon_rect = btn.rect.inflate(4, 6)
                pygame.draw.rect(surface, (10, 48, 24), ribbon_rect.move(0, 3), border_radius=6)
                pygame.draw.rect(surface, (28, 142, 78), ribbon_rect, border_radius=6)
                pygame.draw.rect(surface, (64, 204, 124), ribbon_rect.inflate(-4, -4), border_radius=4)
                pygame.draw.rect(surface, (22, 126, 68), ribbon_rect.inflate(-8, -8), border_radius=3)
                pygame.draw.rect(surface, (8, 45, 22), ribbon_rect, width=2, border_radius=6)

                # Hanging notched ribbon tail
                notch_pts = [
                    (ribbon_rect.x + 2, ribbon_rect.bottom - 1),
                    (ribbon_rect.x + ribbon_rect.width // 2, ribbon_rect.bottom + 9),
                    (ribbon_rect.right - 2, ribbon_rect.bottom - 1),
                ]
                pygame.draw.polygon(surface, (22, 126, 68), notch_pts)
                pygame.draw.lines(surface, (8, 45, 22), False, notch_pts, 2)

                txt = font_btn_bold.render(btn.text, True, (255, 255, 255))
                txt_s = font_btn_bold.render(btn.text, True, (8, 45, 22))
                t_rc = txt.get_rect(center=ribbon_rect.center)
                surface.blit(txt_s, t_rc.move(0, 1))
                surface.blit(txt, t_rc)
            else:
                txt = font_btn_bold.render(btn.text, True, (48, 22, 8))
                surface.blit(txt, txt.get_rect(center=btn.rect.center))

        for i in range(len(level_buttons) - 1):
            b1 = level_buttons[i]
            b2 = level_buttons[i + 1]
            if not b1.is_selected and not b2.is_selected:
                pygame.draw.line(surface, (116, 68, 28), (b1.rect.right, rect.top + 6), (b1.rect.right, rect.bottom - 6), 2)

    def draw_home_screen(
        self,
        surface: pygame.Surface,
        best_victory_steps: Optional[int],
        user_stats: Optional[Dict[str, Any]],
        input_player_name: TextInputBox,
        grid_buttons: List[UIButton],
        level_buttons: List[UIButton],
        btn_start_mission: UIButton,
        btn_levels: UIButton,
        btn_how_to_play: UIButton,
        btn_settings: UIButton,
        btn_exit: UIButton,
        font_title_top: pygame.font.Font,
        font_title_bot: pygame.font.Font,
        font_label: pygame.font.Font,
        font_badge: pygame.font.Font,
        font_btn_bold: pygame.font.Font,
        show_levels_modal: bool = False,
        show_settings_modal: bool = False,
        selected_chamber_level: int = 12,
        sound_enabled: bool = True,
        btn_close_modal: Optional[UIButton] = None,
        btn_toggle_sfx: Optional[UIButton] = None,
        btn_modal_switch_user: Optional[UIButton] = None,
        font_small: Optional[pygame.font.Font] = None,
        btn_history: Optional[UIButton] = None,
    ) -> None:
        """Render identical Main Menu matching retro-pixel RPG adventure parchment design."""
        cx = self.screen_width // 2
        card_w = 512
        card_h = 595
        card_x = cx - card_w // 2
        card_y = 104
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # 1. Dungeon brick wall background with torch ambiance
        draw_dungeon_background(surface, self.screen_width, self.screen_height)

        # 2. Main Parchment Sheet Chassis
        draw_parchment_chassis(surface, card_rect)

        # Add slotted screw rivets (-) to 4 corners
        rivet_offset = 22
        rivet_pts = [
            (card_rect.left + rivet_offset, card_rect.top + rivet_offset),
            (card_rect.right - rivet_offset, card_rect.top + rivet_offset),
            (card_rect.left + rivet_offset, card_rect.bottom - rivet_offset),
            (card_rect.right - rivet_offset, card_rect.bottom - rivet_offset),
        ]
        for rx, ry in rivet_pts:
            pygame.draw.line(surface, (54, 30, 12), (rx - 4, ry), (rx + 4, ry), 2)

        # Aged deckled notches along the outer borders of the parchment
        deckle_col = (18, 12, 14)
        notch_pts = [
            (card_rect.left, card_rect.top + 70),
            (card_rect.left, card_rect.top + 240),
            (card_rect.left, card_rect.top + 450),
            (card_rect.right, card_rect.top + 130),
            (card_rect.right, card_rect.top + 360),
            (card_rect.left + 140, card_rect.bottom),
            (card_rect.left + 360, card_rect.bottom),
        ]
        for nx, ny in notch_pts:
            pygame.draw.circle(surface, deckle_col, (nx, ny), 3)

        # 3. Royal Crown & 3D Adventure Title (Resting above / overlapping top border of parchment)
        draw_royal_crown(surface, cx, 46)
        draw_adventure_title(surface, "TREASURE", 70, font_title_top, cx)
        draw_adventure_title(surface, "HUNTER", 118, font_title_bot, cx)

        # 4. Trophies & Stats Badges (Side-by-side)
        best_text = f"BEST: {best_victory_steps} STEPS" if best_victory_steps is not None else "BEST: 14 STEPS"
        victories = user_stats.get("victories", 0) if user_stats else 11
        user_level = max(1, min(50, 1 + victories))
        level_text = f"LEVEL: {user_level} / 50"

        badge_w, badge_h = 180, 34
        badge_y = 172
        self._draw_trophy_badge(surface, pygame.Rect(cx - badge_w - 9, badge_y, badge_w, badge_h), best_text, font_badge)
        self._draw_trophy_badge(surface, pygame.Rect(cx + 9, badge_y, badge_w, badge_h), level_text, font_badge)

        # 5. PLAYER NAME Section
        lbl_p = font_label.render("PLAYER NAME", True, (48, 20, 6))
        surface.blit(lbl_p, lbl_p.get_rect(center=(cx, 218)))
        input_player_name.rect = pygame.Rect(cx - 185, 234, 370, 44)
        input_player_name.draw(surface)

        # 6. GRID SIZE Section
        lbl_g = font_label.render("GRID SIZE", True, (48, 20, 6))
        surface.blit(lbl_g, lbl_g.get_rect(center=(cx, 292)))
        btn_w, btn_h = 78, 54
        gap = 12
        start_x = cx - (4 * btn_w + 3 * gap) // 2
        for i, btn in enumerate(grid_buttons):
            btn.rect = pygame.Rect(start_x + i * (btn_w + gap), 308, btn_w, btn_h)
            btn.draw(surface)

        # 7. DIFFICULTY Section
        lbl_d = font_label.render("DIFFICULTY", True, (48, 20, 6))
        surface.blit(lbl_d, lbl_d.get_rect(center=(cx, 376)))
        diff_rect = pygame.Rect(cx - 190, 392, 380, 38)
        seg_w = diff_rect.width // len(level_buttons)
        for i, btn in enumerate(level_buttons):
            btn.rect = pygame.Rect(diff_rect.x + i * seg_w, diff_rect.y, seg_w, diff_rect.height)
        self._draw_difficulty_bar(surface, diff_rect, level_buttons, font_btn_bold)

        # 8. Primary CTA START MISSION Button
        btn_start_mission.rect = pygame.Rect(cx - 150, 448, 300, 48)
        btn_start_mission.draw(surface)

        # 9. 2x2 Secondary Buttons Grid
        # Row 1: LEVELS (1-50) & HOW TO PLAY
        btn_levels.rect = pygame.Rect(cx - 190, 512, 180, 42)
        btn_levels.draw(surface)

        btn_how_to_play.rect = pygame.Rect(cx + 10, 512, 180, 42)
        btn_how_to_play.draw(surface)

        # Row 2: HISTORY & SETTINGS
        if btn_history:
            btn_history.rect = pygame.Rect(cx - 190, 566, 180, 42)
            btn_history.draw(surface)

        btn_settings.rect = pygame.Rect(cx + 10, 566, 180, 42)
        btn_settings.draw(surface)

        # 10. Bottom Centered EXIT Button
        btn_exit.rect = pygame.Rect(cx - 85, 622, 170, 38)
        btn_exit.draw(surface)

        # Version watermark in bottom right corner
        v_surf = self.font_version.render("v1.2.0", True, (65, 55, 58))
        surface.blit(v_surf, (self.screen_width - 55, self.screen_height - 24))

        # 11. Optional Modal Dialogs (Levels Browser or Settings)
        if show_levels_modal and btn_close_modal and font_small:
            self._draw_levels_modal(surface, user_level, selected_chamber_level, btn_close_modal, font_label, font_small)
        elif show_settings_modal and btn_toggle_sfx and btn_modal_switch_user and btn_close_modal:
            self._draw_settings_modal(surface, sound_enabled, btn_toggle_sfx, btn_modal_switch_user, btn_close_modal, font_label)

    def _draw_levels_modal(
        self,
        surface: pygame.Surface,
        user_level: int,
        selected_chamber_level: int,
        btn_close_modal: UIButton,
        font_label: pygame.font.Font,
        font_small: pygame.font.Font
    ) -> None:
        """Render interactive Levels (1-50) Browser Modal."""
        dim_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 180))
        surface.blit(dim_surf, (0, 0))

        cx = self.screen_width // 2
        mw, mh = 500, 480
        mx, my = cx - mw // 2, 140
        modal_rect = pygame.Rect(mx, my, mw, mh)
        draw_parchment_chassis(surface, modal_rect)

        # Title
        t_surf = font_label.render("EXPEDITION CHAMBERS (LEVELS 1 - 50)", True, (54, 24, 6))
        surface.blit(t_surf, t_surf.get_rect(center=(cx, my + 30)))

        # 5x10 Chamber Grid
        cols = 10
        cell_sz = 38
        gap = 8
        grid_w = cols * cell_sz + (cols - 1) * gap
        grid_start_x = cx - grid_w // 2
        grid_start_y = my + 60

        for lvl in range(1, 51):
            idx = lvl - 1
            r = idx // cols
            c = idx % cols
            cell_x = grid_start_x + c * (cell_sz + gap)
            cell_y = grid_start_y + r * (cell_sz + gap)
            c_rect = pygame.Rect(cell_x, cell_y, cell_sz, cell_sz)

            is_unlocked = (lvl <= user_level)
            is_active = (lvl == selected_chamber_level)

            if is_active:
                pygame.draw.rect(surface, (250, 182, 52), c_rect, border_radius=6)
                pygame.draw.rect(surface, (92, 42, 6), c_rect, width=2, border_radius=6)
                txt = font_small.render(str(lvl), True, (52, 22, 4))
            elif is_unlocked:
                pygame.draw.rect(surface, (200, 150, 94), c_rect, border_radius=6)
                pygame.draw.rect(surface, (68, 34, 12), c_rect, width=1, border_radius=6)
                txt = font_small.render(str(lvl), True, (52, 22, 4))
            else:
                pygame.draw.rect(surface, (136, 126, 118), c_rect, border_radius=6)
                pygame.draw.rect(surface, (50, 44, 40), c_rect, width=1, border_radius=6)
                txt = font_small.render(str(lvl), True, (80, 72, 68))

            surface.blit(txt, txt.get_rect(center=c_rect.center))

        btn_close_modal.rect = pygame.Rect(cx - 70, my + mh - 50, 140, 36)
        btn_close_modal.draw(surface)

    def _draw_settings_modal(
        self,
        surface: pygame.Surface,
        sound_enabled: bool,
        btn_toggle_sfx: UIButton,
        btn_modal_switch_user: UIButton,
        btn_close_modal: UIButton,
        font_label: pygame.font.Font
    ) -> None:
        """Render Settings & Options Modal."""
        dim_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 180))
        surface.blit(dim_surf, (0, 0))

        cx = self.screen_width // 2
        mw, mh = 420, 300
        mx, my = cx - mw // 2, 220
        modal_rect = pygame.Rect(mx, my, mw, mh)
        draw_parchment_chassis(surface, modal_rect)

        t_surf = font_label.render("EXPEDITION SETTINGS", True, (54, 24, 6))
        surface.blit(t_surf, t_surf.get_rect(center=(cx, my + 35)))

        sfx_label = "AUDIO SFX: [ ON ]" if sound_enabled else "AUDIO SFX: [ MUTED ]"
        btn_toggle_sfx.text = sfx_label
        btn_toggle_sfx.rect = pygame.Rect(cx - 130, my + 80, 260, 42)
        btn_toggle_sfx.draw(surface)

        btn_modal_switch_user.rect = pygame.Rect(cx - 130, my + 138, 260, 42)
        btn_modal_switch_user.draw(surface)

        btn_close_modal.rect = pygame.Rect(cx - 70, my + mh - 54, 140, 36)
        btn_close_modal.draw(surface)
