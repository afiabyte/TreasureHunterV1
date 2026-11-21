"""
UI How to Play Screen: Mission briefing, tactical controls guide,
objective explanation, and visual navigation aids.
"""

import pygame
from .colors import (
    COLOR_BG,
    COLOR_HUD_BG,
    COLOR_HUD_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_ACCENT_CYAN,
    COLOR_TEXT_ACCENT_AMBER,
    COLOR_TEXT_ACCENT_GREEN,
)
from .widgets import UIButton


class HowToPlayScreenRenderer:
    """Renders the mission briefing and tactical controls guide screen."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

    def draw(
        self,
        surface: pygame.Surface,
        btn_back_to_menu: UIButton,
        font_title: pygame.font.Font,
        font_header: pygame.font.Font,
        font_body: pygame.font.Font,
    ) -> None:
        """Render the tactical instruction briefing screen."""
        surface.fill(COLOR_BG)

        # Header
        title = font_title.render("MISSION BRIEFING // HOW TO PLAY", True, COLOR_TEXT_ACCENT_CYAN)
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, 40))

        # Panel Box
        panel_rect = pygame.Rect(120, 95, self.screen_width - 240, 560)
        pygame.draw.rect(surface, COLOR_HUD_BG, panel_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_HUD_BORDER, panel_rect, width=1, border_radius=6)

        y = 120
        # Section 1: Objectives
        h1 = font_header.render("[ 1. PRIMARY OBJECTIVES ]", True, COLOR_TEXT_ACCENT_AMBER)
        surface.blit(h1, (150, y))
        y += 30
        lines1 = [
            "• INFILTRATION: You enter the sector at Start coordinate (0, 0).",
            "• KEY ACQUISITION: Locate and collect the Golden Cipher Key [K] on the grid.",
            "• EXTRACTION: Reach the Exit Portal [E] at (N-1, N-1) only AFTER securing the key.",
            "• EVASION: Evade Gemini-controlled Hunter Drones [H]. One collision results in casualty."
        ]
        for line in lines1:
            txt = font_body.render(line, True, COLOR_TEXT_PRIMARY)
            surface.blit(txt, (160, y))
            y += 24

        y += 15
        # Section 2: Controls
        h2 = font_header.render("[ 2. TACTICAL CONTROLS ]", True, COLOR_TEXT_ACCENT_CYAN)
        surface.blit(h2, (150, y))
        y += 30
        lines2 = [
            "• WASD / Arrow Keys : Move Operative one grid cell in cardinal direction.",
            "• [P] / [SPACE] / ||: Pause or Resume the mission at any time.",
            "• [H]               : Manually deploy a Hunter Drone reinforcement (up to 8 max).",
            "• [B]               : Trigger dynamic Barrier Shift (relocate walls safely).",
            "• [R]               : Reset mission with fresh procedural layout.",
            "• [ESC]             : Pause mission (or return to menu)."
        ]
        for line in lines2:
            txt = font_body.render(line, True, COLOR_TEXT_PRIMARY)
            surface.blit(txt, (160, y))
            y += 24

        y += 15
        # Section 3: Visual Guidance
        h3 = font_header.render("[ 3. HUD VISUAL GUIDANCE ]", True, COLOR_TEXT_ACCENT_GREEN)
        surface.blit(h3, (150, y))
        y += 30
        lines3 = [
            "• GREEN BREADCRUMBS : Next 3 safe coordinates computed by Gemini 2.5 Flash, dodging",
            "                      Hunter visual cones and exploiting blind spots behind them.",
            "• PULSING YELLOW ARROW : Dynamic directional beacon pointing to current objective.",
            "• DYNAMIC BARRIERS  : Obstacles shift dynamically every 2.5s (scaled by difficulty)."
        ]
        for line in lines3:
            txt = font_body.render(line, True, COLOR_TEXT_PRIMARY)
            surface.blit(txt, (160, y))
            y += 24

        # Back Button
        btn_back_to_menu.draw(surface)
