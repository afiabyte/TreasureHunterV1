"""
UI Overlays: Victory screen, Defeat screen, right-docked tactical inspection
pause overlay, and mission countdown standby banner.
"""

import math
from typing import Tuple, List, Optional
import pygame

from .colors import (
    COLOR_HUD_BG,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_ACCENT_CYAN,
    COLOR_TEXT_ACCENT_GREEN,
    COLOR_TEXT_ACCENT_AMBER,
    COLOR_TEXT_ACCENT_RED,
    COLOR_KEY_GOLD,
)
from .widgets import UIButton


class OverlayRenderer:
    """Renders game-over overlays, pause menu dock, and standby banner."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

    def draw_game_over_overlay(
        self,
        surface: pygame.Surface,
        is_victory: bool,
        steps: int,
        is_new_best: bool,
        current_level: int,
        btn_next_level: UIButton,
        btn_victory_replay: UIButton,
        btn_victory_menu: UIButton,
        btn_retry_level: UIButton,
        btn_defeat_menu: UIButton,
        font_title: pygame.font.Font,
        font_header: pygame.font.Font,
        font_body: pygame.font.Font,
        font_small: pygame.font.Font,
    ) -> None:
        """Render the victory or defeat modal overlay on top of the game screen."""
        dim_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_surf.fill((8, 12, 18, 190))
        surface.blit(dim_surf, (0, 0))

        cx = self.screen_width // 2
        cy = self.screen_height // 2

        modal_rect = pygame.Rect(cx - 240, cy - 180, 480, 360)
        pygame.draw.rect(surface, COLOR_HUD_BG, modal_rect, border_radius=8)

        accent_color = COLOR_TEXT_ACCENT_GREEN if is_victory else COLOR_TEXT_ACCENT_RED
        pygame.draw.rect(surface, accent_color, modal_rect, width=2, border_radius=8)

        if is_victory:
            title_text = "EXPEDITION ACCOMPLISHED"
            sub_text = f"Treasure Hunter successfully extracted in {steps} steps!"
            title_color = COLOR_TEXT_ACCENT_GREEN
        else:
            title_text = "SANCTUARY CASUALTY"
            sub_text = f"Explorer intercepted by Temple Sentinel after {steps} steps."
            title_color = COLOR_TEXT_ACCENT_RED

        t_surf = font_title.render(title_text, True, title_color)
        surface.blit(t_surf, t_surf.get_rect(center=(cx, cy - 120)))

        s_surf = font_body.render(sub_text, True, COLOR_TEXT_PRIMARY)
        surface.blit(s_surf, s_surf.get_rect(center=(cx, cy - 80)))

        if is_victory and is_new_best:
            rec_surf = font_header.render("NEW BEST EXPEDITION RECORD!", True, COLOR_TEXT_ACCENT_AMBER)
            surface.blit(rec_surf, rec_surf.get_rect(center=(cx, cy - 45)))
        elif is_victory:
            adv_txt = "Next difficulty available for selection." if current_level < 3 else "Maximum difficulty conquered!"
            adv_surf = font_small.render(adv_txt, True, COLOR_TEXT_SECONDARY)
            surface.blit(adv_surf, adv_surf.get_rect(center=(cx, cy - 45)))
        else:
            tip_surf = font_small.render("Tip: Follow Gemini green breadcrumbs to exploit hunter blind spots.", True, COLOR_TEXT_SECONDARY)
            surface.blit(tip_surf, tip_surf.get_rect(center=(cx, cy - 45)))

        if is_victory:
            if current_level < 3:
                btn_next_level.draw(surface)
            btn_victory_replay.draw(surface)
            btn_victory_menu.draw(surface)
        else:
            btn_retry_level.draw(surface)
            btn_defeat_menu.draw(surface)

    def draw_pause_overlay(
        self,
        surface: pygame.Surface,
        btn_pause_resume: UIButton,
        btn_pause_restart: UIButton,
        btn_pause_help: UIButton,
        btn_pause_menu: UIButton,
        has_key: bool,
        level_name: str,
        font_bold: pygame.font.Font,
        font_badge: pygame.font.Font,
        font_small: pygame.font.Font,
    ) -> None:
        """Render tactical right-margin pause dock leaving central grid 100% visible."""
        dim_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_surf.fill((4, 8, 16, 25))
        surface.blit(dim_surf, (0, 0))

        top_w = 400
        top_h = 32
        top_x = self.screen_width // 2 - top_w // 2
        top_y = 12
        top_rect = pygame.Rect(top_x, top_y, top_w, top_h)

        top_glass = pygame.Surface((top_w, top_h), pygame.SRCALPHA)
        top_glass.fill((10, 16, 28, 220))
        surface.blit(top_glass, top_rect.topleft)
        pygame.draw.rect(surface, (0, 180, 230), top_rect, width=1, border_radius=4)

        banner_title = font_bold.render("PAUSED // TEMPLE EXPEDITION INSPECTION MODE", True, COLOR_KEY_GOLD)
        surface.blit(banner_title, banner_title.get_rect(center=(self.screen_width // 2, top_y + 16)))

        dock_x = 778
        dock_y = 48
        dock_w = 174
        dock_h = 256
        dock_rect = pygame.Rect(dock_x, dock_y, dock_w, dock_h)

        pygame.draw.rect(surface, (5, 8, 14), dock_rect.move(0, 3), border_radius=6)
        dock_glass = pygame.Surface((dock_w, dock_h), pygame.SRCALPHA)
        dock_glass.fill((12, 18, 30, 235))
        surface.blit(dock_glass, dock_rect.topleft)
        pygame.draw.rect(surface, (36, 60, 95), dock_rect, width=1, border_radius=6)
        pygame.draw.rect(surface, (0, 180, 230), dock_rect.inflate(-4, -4), width=1, border_radius=4)

        dock_title = font_badge.render("// EXPEDITION PAUSED", True, COLOR_KEY_GOLD)
        surface.blit(dock_title, (dock_x + 12, dock_y + 10))
        pygame.draw.line(surface, (28, 48, 75), (dock_x + 10, dock_y + 26), (dock_x + dock_w - 10, dock_y + 26), 1)

        btn_pause_resume.draw(surface)
        btn_pause_restart.draw(surface)
        btn_pause_help.draw(surface)
        btn_pause_menu.draw(surface)

        info_y = dock_y + 188
        pygame.draw.line(surface, (28, 48, 75), (dock_x + 10, info_y), (dock_x + dock_w - 10, info_y), 1)
        info_y += 6
        sec_surf = font_small.render(f"LEVEL: {level_name.upper()}", True, COLOR_TEXT_SECONDARY)
        surface.blit(sec_surf, (dock_x + 12, info_y))
        info_y += 16
        k_txt = "RELIC: SECURED" if has_key else "RELIC: REQUIRED"
        k_col = COLOR_TEXT_ACCENT_GREEN if has_key else COLOR_KEY_GOLD
        key_info = font_badge.render(k_txt, True, k_col)
        surface.blit(key_info, (dock_x + 12, info_y))
        info_y += 18
        hint_surf = font_small.render("[P / SPACE to Resume]", True, COLOR_TEXT_MUTED)
        surface.blit(hint_surf, (dock_x + 12, info_y))

    def draw_standby_banner(
        self,
        surface: pygame.Surface,
        seconds_remaining: float,
        anim_time: float,
        font_header: pygame.font.Font,
        font_bold: pygame.font.Font,
    ) -> None:
        """Render prominent tactical reconnaissance banner on mission start."""
        count = max(1, int(math.ceil(seconds_remaining)))
        pulse = 1.0 + 0.08 * math.sin(anim_time * 8.0)

        bw = 560
        bh = 76
        bx = (self.screen_width - bw) // 2
        by = 85

        b_rect = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(surface, (14, 20, 32), b_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_TEXT_ACCENT_CYAN, b_rect, width=2, border_radius=6)

        t_len = 8
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (bx, by), (bx + t_len, by), 2)
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (bx, by), (bx, by + t_len), 2)
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (bx + bw - 1, by + bh - 1), (bx + bw - 1 - t_len, by + bh - 1), 2)
        pygame.draw.line(surface, COLOR_TEXT_ACCENT_CYAN, (bx + bw - 1, by + bh - 1), (bx + bw - 1, by + bh - 1 - t_len), 2)

        title_str = f"TACTICAL STANDBY // DEPLOYING IN: {count}s"
        t_surf = font_header.render(title_str, True, COLOR_TEXT_ACCENT_AMBER)
        surface.blit(t_surf, t_surf.get_rect(center=(self.screen_width // 2, by + 24)))

        sub_str = "Hunters stationary. Press [WASD / Arrows] or [SPACE] to engage now!"
        s_surf = font_bold.render(sub_str, True, COLOR_TEXT_ACCENT_GREEN)
        surface.blit(s_surf, s_surf.get_rect(center=(self.screen_width // 2, by + 52)))
