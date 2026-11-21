"""
UI Home Screen: Main menu with retro-pixel RPG parchment chassis,
difficulty segmented selector, player name input, grid size stones,
levels modal, and settings modal.
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

    def _draw_trophy_badge(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        text: str,
        font_badge: pygame.font.Font
    ) -> None:
        """Render wooden capsule trophy plaque."""
        pygame.draw.rect(surface, (56, 28, 10), rect.move(0, 2), border_radius=10)
        pygame.draw.rect(surface, (200, 146, 88), rect, border_radius=10)
        pygame.draw.rect(surface, (222, 178, 122), rect.inflate(-4, -4), border_radius=8)
        pygame.draw.rect(surface, (68, 34, 12), rect, width=2, border_radius=10)

        ic_x = rect.left + 20
        ic_y = rect.centery
        cup_pts = [(ic_x - 8, ic_y - 8), (ic_x + 8, ic_y - 8), (ic_x + 6, ic_y + 1), (ic_x - 6, ic_y + 1)]
        pygame.draw.polygon(surface, (246, 186, 42), cup_pts)
        pygame.draw.polygon(surface, (68, 34, 12), cup_pts, 1)
        pygame.draw.arc(surface, (68, 34, 12), pygame.Rect(ic_x - 12, ic_y - 8, 8, 8), 1.5, 4.5, 2)
        pygame.draw.arc(surface, (68, 34, 12), pygame.Rect(ic_x + 4, ic_y - 8, 8, 8), 4.8, 1.4, 2)
        pygame.draw.rect(surface, (246, 186, 42), (ic_x - 2, ic_y + 1, 4, 4))
        pygame.draw.rect(surface, (246, 186, 42), (ic_x - 7, ic_y + 5, 14, 3))
        pygame.draw.rect(surface, (68, 34, 12), (ic_x - 7, ic_y + 5, 14, 3), 1)

        lbl = font_badge.render(text, True, (48, 20, 6))
        surface.blit(lbl, (rect.left + 38, rect.centery - lbl.get_height() // 2))

    def _draw_difficulty_bar(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        level_buttons: List[UIButton],
        font_btn_bold: pygame.font.Font
    ) -> None:
        """Render segmented difficulty selector with active Emerald Ribbon banner."""
        pygame.draw.rect(surface, (68, 34, 12), rect, border_radius=8)
        pygame.draw.rect(surface, (202, 152, 96), rect.inflate(-4, -4), border_radius=6)

        for btn in level_buttons:
            if btn.is_selected:
                ribbon_rect = btn.rect.inflate(4, 6)
                pygame.draw.rect(surface, (16, 84, 44), ribbon_rect.move(0, 3), border_radius=6)
                pygame.draw.rect(surface, (34, 156, 88), ribbon_rect, border_radius=6)
                pygame.draw.rect(surface, (64, 200, 122), ribbon_rect.inflate(-4, -4), border_radius=4)
                pygame.draw.rect(surface, (28, 142, 78), ribbon_rect.inflate(-8, -8), border_radius=3)
                pygame.draw.rect(surface, (10, 58, 30), ribbon_rect, width=3, border_radius=6)

                notch_pts = [
                    (ribbon_rect.x + 2, ribbon_rect.bottom - 1),
                    (ribbon_rect.x + ribbon_rect.width // 2, ribbon_rect.bottom + 9),
                    (ribbon_rect.right - 2, ribbon_rect.bottom - 1),
                ]
                pygame.draw.polygon(surface, (28, 142, 78), notch_pts)
                pygame.draw.lines(surface, (10, 58, 30), False, notch_pts, 3)

                txt = font_btn_bold.render(btn.text, True, (255, 255, 255))
                txt_s = font_btn_bold.render(btn.text, True, (10, 58, 30))
                t_rc = txt.get_rect(center=ribbon_rect.center)
                surface.blit(txt_s, t_rc.move(0, 1))
                surface.blit(txt, t_rc)
            else:
                txt = font_btn_bold.render(btn.text, True, (54, 24, 6))
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
    ) -> None:
        """Render identical Main Menu matching retro-pixel RPG adventure parchment design."""
        cx = self.screen_width // 2
        card_w = 560
        card_h = 715
        card_x = cx - card_w // 2
        card_y = 30
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # 1. Dungeon brick wall background with torch ambiance
        draw_dungeon_background(surface, self.screen_width, self.screen_height)

        # 2. Main Parchment Sheet Chassis
        draw_parchment_chassis(surface, card_rect)

        # 3. Royal Crown & 3D Adventure Title
        draw_royal_crown(surface, cx, card_y + 14)
        draw_adventure_title(surface, "TREASURE", card_y + 40, font_title_top, cx)
        draw_adventure_title(surface, "HUNTER", card_y + 86, font_title_bot, cx)

        # 4. Trophies & Stats Badges
        best_text = f"BEST: {best_victory_steps} STEPS" if best_victory_steps is not None else "BEST: 14 STEPS"
        victories = user_stats.get("victories", 0) if user_stats else 11
        user_level = max(1, min(50, 1 + victories))
        level_text = f"LEVEL: {user_level} / 50"

        self._draw_trophy_badge(surface, pygame.Rect(cx - 225, card_y + 150, 220, 36), best_text, font_badge)
        self._draw_trophy_badge(surface, pygame.Rect(cx + 5, card_y + 150, 220, 36), level_text, font_badge)

        # 5. PLAYER NAME Section
        lbl_p = font_label.render("PLAYER NAME", True, (54, 24, 6))
        surface.blit(lbl_p, lbl_p.get_rect(center=(cx, card_y + 208)))
        input_player_name.draw(surface)

        # 6. GRID SIZE Section
        lbl_g = font_label.render("GRID SIZE", True, (54, 24, 6))
        surface.blit(lbl_g, lbl_g.get_rect(center=(cx, card_y + 292)))
        for btn in grid_buttons:
            btn.draw(surface)

        # 7. DIFFICULTY Section
        lbl_d = font_label.render("DIFFICULTY", True, (54, 24, 6))
        surface.blit(lbl_d, lbl_d.get_rect(center=(cx, card_y + 398)))
        self._draw_difficulty_bar(surface, pygame.Rect(cx - 225, card_y + 420, 450, 44), level_buttons, font_btn_bold)

        # 8. Primary CTA START MISSION Button
        btn_start_mission.draw(surface)

        # 9. Secondary Buttons Row 1: Levels & How To Play
        btn_levels.draw(surface)
        btn_how_to_play.draw(surface)

        # 10. Secondary Buttons Row 2: Settings & Exit
        btn_settings.draw(surface)
        btn_exit.draw(surface)

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
