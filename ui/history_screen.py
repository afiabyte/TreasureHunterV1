"""
Dungeon Records Screen Renderer: Retro-pixel RPG Match History & Leaderboard screen.
Matches reference mockup media_1795247905616_e748fa1b.jpg 1:1.

Features:
- Dungeon stone wall background with warm torchlight ambiance.
- Golden 3D Trophy Cup emblem with emerald jewel and radiant highlights.
- 3D Adventure typography title: "DUNGEON" / "RECORDS".
- Wooden capsule stats plaque: "WIN RATE: 75% | BEST: 12 STEPS" with hanging brackets.
- Aged parchment scroll chassis with slotted brass screw rivets and deckled notches.
- Large carved wooden board / frame enclosing the records table with metal corner brackets.
- Clean 3-column table header: PLAYER, STEPS, RESULT.
- 5 data rows with numbered rank, player name, 2-digit steps, and VICTORY (emerald green) / DEFEAT (crimson red) badges.
- Warm 3D wooden "[ BACK TO MENU ]" action button.
"""

from typing import List, Dict, Any, Optional
import pygame

from .art_helpers import (
    draw_dungeon_background,
    draw_parchment_chassis,
    draw_adventure_title,
)
from .widgets import UIButton


class HistoryScreenRenderer:
    """Renders the authentic retro-pixel RPG adventure Dungeon Records screen."""

    def __init__(self, screen_width: int = 960, screen_height: int = 780) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Cached typography matching mockup aesthetics
        self.font_title = pygame.font.SysFont("georgia,timesnewroman,palatino", 48, bold=True)
        self.font_plaque = pygame.font.SysFont("trebuchetms,tahoma,arial", 17, bold=True)
        self.font_header = pygame.font.SysFont("trebuchetms,tahoma,arial", 20, bold=True)
        self.font_row = pygame.font.SysFont("trebuchetms,tahoma,arial", 23, bold=True)
        self.font_btn = pygame.font.SysFont("trebuchetms,tahoma,arial", 20, bold=True)
        self.font_version = pygame.font.SysFont("courier", 11)

    def draw_golden_trophy(self, surface: pygame.Surface, cx: int, cy: int) -> None:
        """
        Render 3D pixel golden trophy cup emblem matching the reference mockup.
        Features chalice, curved side handles, stem, pedestal base, and emerald jewel.
        """
        # Outer drop shadow
        pygame.draw.ellipse(surface, (14, 7, 3), pygame.Rect(cx - 26, cy + 24, 52, 12))

        # 1. Left & Right Ear Handles
        handle_dark = (48, 20, 6)
        handle_gold = (248, 186, 42)
        handle_hi = (255, 235, 120)

        # Left handle
        pygame.draw.arc(surface, handle_dark, pygame.Rect(cx - 28, cy - 9, 18, 22), 1.2, 4.8, 4)
        pygame.draw.arc(surface, handle_gold, pygame.Rect(cx - 28, cy - 9, 18, 22), 1.4, 4.6, 2)
        pygame.draw.arc(surface, handle_hi, pygame.Rect(cx - 27, cy - 8, 16, 20), 1.8, 3.8, 1)

        # Right handle
        pygame.draw.arc(surface, handle_dark, pygame.Rect(cx + 10, cy - 9, 18, 22), 4.6, 1.8, 4)
        pygame.draw.arc(surface, handle_gold, pygame.Rect(cx + 10, cy - 9, 18, 22), 4.8, 1.6, 2)
        pygame.draw.arc(surface, handle_hi, pygame.Rect(cx + 11, cy - 8, 16, 20), 5.2, 1.2, 1)

        # 2. Trophy Chalice Body (Trapezoid cup tapering down)
        cup_pts = [
            (cx - 18, cy - 10),
            (cx + 18, cy - 10),
            (cx + 13, cy + 10),
            (cx - 13, cy + 10)
        ]
        pygame.draw.polygon(surface, (48, 20, 6), [(px, py + 2) for px, py in cup_pts])
        pygame.draw.polygon(surface, (242, 175, 34), cup_pts)

        # Inner cup highlights & shading
        inner_pts = [
            (cx - 15, cy - 8),
            (cx + 15, cy - 8),
            (cx + 10, cy + 8),
            (cx - 10, cy + 8)
        ]
        pygame.draw.polygon(surface, (255, 225, 90), inner_pts)
        pygame.draw.polygon(surface, (230, 150, 22), [
            (cx - 12, cy - 4), (cx + 12, cy - 4), (cx + 8, cy + 7), (cx - 8, cy + 7)
        ])
        # Vertical bright shine glint
        pygame.draw.line(surface, (255, 255, 220), (cx - 5, cy - 7), (cx - 3, cy + 6), 2)
        pygame.draw.polygon(surface, (48, 20, 6), cup_pts, 2)

        # Center Chalice Emerald Gem
        pygame.draw.circle(surface, (48, 20, 6), (cx, cy + 1), 5)
        pygame.draw.circle(surface, (36, 185, 92), (cx, cy + 1), 4)
        pygame.draw.circle(surface, (120, 245, 165), (cx - 1, cy), 2)

        # Top Rim Opening
        rim_rect = pygame.Rect(cx - 18, cy - 13, 36, 7)
        pygame.draw.ellipse(surface, (48, 20, 6), rim_rect.move(0, 2))
        pygame.draw.ellipse(surface, (255, 235, 130), rim_rect)
        pygame.draw.ellipse(surface, (48, 20, 6), rim_rect, 2)

        # 3. Stem / Neck
        stem_rect = pygame.Rect(cx - 5, cy + 10, 10, 8)
        pygame.draw.rect(surface, (48, 20, 6), stem_rect.move(0, 1))
        pygame.draw.rect(surface, (242, 175, 34), stem_rect)
        pygame.draw.rect(surface, (255, 225, 90), stem_rect.inflate(-2, -2))
        pygame.draw.rect(surface, (48, 20, 6), stem_rect, 2)

        # 4. Pedestal Base
        base_pts = [
            (cx - 9, cy + 18),
            (cx + 9, cy + 18),
            (cx + 16, cy + 26),
            (cx - 16, cy + 26)
        ]
        pygame.draw.polygon(surface, (48, 20, 6), [(px, py + 2) for px, py in base_pts])
        pygame.draw.polygon(surface, (215, 142, 22), base_pts)
        pygame.draw.polygon(surface, (255, 218, 80), [
            (cx - 7, cy + 19), (cx + 7, cy + 19), (cx + 13, cy + 24), (cx - 13, cy + 24)
        ])
        pygame.draw.polygon(surface, (48, 20, 6), base_pts, 2)

    def draw_stats_plaque(self, surface: pygame.Surface, rect: pygame.Rect, text: str) -> None:
        """Render carved wood capsule trophy stats plaque with hanging brackets."""
        # Hanging brackets connecting to top
        bracket_col = (42, 20, 8)
        bracket_w = 4
        bracket_h = 10
        pygame.draw.rect(surface, bracket_col, pygame.Rect(rect.centerx - 70 - bracket_w // 2, rect.top - bracket_h, bracket_w, bracket_h))
        pygame.draw.rect(surface, bracket_col, pygame.Rect(rect.centerx + 70 - bracket_w // 2, rect.top - bracket_h, bracket_w, bracket_h))

        # Bottom drop shadow
        pygame.draw.rect(surface, (36, 18, 6), rect.move(0, 3), border_radius=12)

        # Wood base plate
        pygame.draw.rect(surface, (155, 96, 46), rect, border_radius=12)

        # Inner lighter wood face
        inner = rect.inflate(-4, -4)
        pygame.draw.rect(surface, (186, 122, 64), inner, border_radius=10)

        # Bevel highlight lines
        pygame.draw.line(surface, (215, 150, 90), (rect.left + 10, rect.top + 3), (rect.right - 10, rect.top + 3), 2)
        pygame.draw.line(surface, (108, 62, 26), (rect.left + 10, rect.bottom - 4), (rect.right - 10, rect.bottom - 4), 2)

        # Dark carved contour border
        pygame.draw.rect(surface, (45, 22, 10), rect, width=2, border_radius=12)

        # Text: WIN RATE: XX% | BEST: XX STEPS
        txt = self.font_plaque.render(text, True, (35, 16, 5))
        txt_s = self.font_plaque.render(text, True, (225, 165, 105))
        rc = txt.get_rect(center=rect.center)
        surface.blit(txt_s, rc.move(0, 1))
        surface.blit(txt, rc)

    def draw_records_table(self, surface: pygame.Surface, rect: pygame.Rect, records: List[Dict[str, Any]]) -> None:
        """Render inner wooden frame with light parchment cavity, corner brackets, header, and 5 data rows."""
        # 1. Outer Dark Wood Frame
        pygame.draw.rect(surface, (34, 16, 6), rect.move(0, 4), border_radius=10)
        pygame.draw.rect(surface, (120, 72, 34), rect, border_radius=10)
        pygame.draw.rect(surface, (148, 92, 48), rect.inflate(-4, -4), border_radius=8)
        pygame.draw.rect(surface, (98, 54, 22), rect.inflate(-8, -8), border_radius=6)
        pygame.draw.rect(surface, (45, 22, 8), rect, width=3, border_radius=10)

        # 4 Metal Corner Brackets
        cb_size = 14
        corners = [
            (rect.left + 3, rect.top + 3),
            (rect.right - 3 - cb_size, rect.top + 3),
            (rect.left + 3, rect.bottom - 3 - cb_size),
            (rect.right - 3 - cb_size, rect.bottom - 3 - cb_size),
        ]
        for cx, cy in corners:
            pygame.draw.rect(surface, (38, 20, 8), pygame.Rect(cx, cy, cb_size, cb_size), border_radius=2)
            pygame.draw.circle(surface, (175, 125, 45), (cx + cb_size // 2, cy + cb_size // 2), 2)

        # 2. Inner Light Parchment Board Fill
        inner_rect = rect.inflate(-22, -22)
        pygame.draw.rect(surface, (244, 224, 186), inner_rect, border_radius=4)
        pygame.draw.rect(surface, (168, 128, 82), inner_rect, width=2, border_radius=4)

        # 3. Header Row (Height: 46px)
        header_h = 46
        header_rect = pygame.Rect(inner_rect.x, inner_rect.y, inner_rect.width, header_h)
        pygame.draw.rect(surface, (230, 202, 156), header_rect, border_top_left_radius=4, border_top_right_radius=4)
        pygame.draw.line(surface, (140, 102, 60), (inner_rect.left, inner_rect.y + header_h), (inner_rect.right, inner_rect.y + header_h), 2)

        # Column Header Labels
        # Column 1: PLAYER (Left)
        col1_x = inner_rect.x + 38
        t_player = self.font_header.render("PLAYER", True, (35, 16, 5))
        surface.blit(t_player, (col1_x, header_rect.centery - t_player.get_height() // 2))

        # Column 2: STEPS (Center)
        col2_cx = inner_rect.x + int(inner_rect.width * 0.52)
        t_steps = self.font_header.render("STEPS", True, (35, 16, 5))
        surface.blit(t_steps, t_steps.get_rect(center=(col2_cx, header_rect.centery)))

        # Column 3: RESULT (Right)
        col3_cx = inner_rect.x + int(inner_rect.width * 0.81)
        t_result = self.font_header.render("RESULT", True, (35, 16, 5))
        surface.blit(t_result, t_result.get_rect(center=(col3_cx, header_rect.centery)))

        # 4. Data Rows (5 rows)
        rows_total_h = inner_rect.height - header_h
        row_h = rows_total_h / 5.0

        for i in range(5):
            row_y = inner_rect.y + header_h + int(i * row_h)
            row_cy = row_y + int(row_h // 2)

            # Horizontal dividing line between rows
            if i > 0:
                pygame.draw.line(surface, (216, 188, 146), (inner_rect.left + 8, row_y), (inner_rect.right - 8, row_y), 1)

            rec = records[i] if i < len(records) else None
            if not rec:
                continue

            rank_num = i + 1
            player_name = str(rec.get("player_name", "OPERATIVE"))
            steps_val = rec.get("steps", 0)
            steps_str = f"{steps_val:02d}" if isinstance(steps_val, int) else str(steps_val)
            result_str = str(rec.get("result", "VICTORY")).upper()
            is_victory = (result_str == "VICTORY")

            # Col 1: Rank + Player Name (e.g., "1. Bravo42")
            col1_str = f"{rank_num}. {player_name}"
            col1_surf = self.font_row.render(col1_str, True, (35, 16, 5))
            surface.blit(col1_surf, (col1_x, row_cy - col1_surf.get_height() // 2))

            # Col 2: Steps (e.g., "12", "09")
            steps_surf = self.font_row.render(steps_str, True, (35, 16, 5))
            surface.blit(steps_surf, steps_surf.get_rect(center=(col2_cx, row_cy)))

            # Col 3: Result (VICTORY: Emerald Green #147B3E, DEFEAT: Crimson Red #A8241C)
            res_color = (20, 123, 62) if is_victory else (168, 36, 28)
            res_surf = self.font_row.render(result_str, True, res_color)
            surface.blit(res_surf, res_surf.get_rect(center=(col3_cx, row_cy)))

    def draw_history_screen(
        self,
        surface: pygame.Surface,
        win_rate: int,
        best_steps: int,
        records: List[Dict[str, Any]],
        btn_back: UIButton,
    ) -> None:
        """Render complete Dungeon Records screen matching media_1795247905616_e748fa1b.jpg."""
        # 1. Dungeon stone background
        draw_dungeon_background(surface, self.screen_width, self.screen_height)

        cx = self.screen_width // 2

        # 2. Parchment Chassis
        card_w = 520
        card_h = 615
        card_x = cx - card_w // 2
        card_y = 142
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
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
            (card_rect.left, card_rect.top + 80),
            (card_rect.left, card_rect.top + 240),
            (card_rect.left, card_rect.top + 480),
            (card_rect.right, card_rect.top + 160),
            (card_rect.right, card_rect.top + 390),
            (card_rect.left + 150, card_rect.bottom),
            (card_rect.left + 350, card_rect.bottom),
        ]
        for nx, ny in notch_pts:
            pygame.draw.circle(surface, deckle_col, (nx, ny), 3)

        # 3. Golden Trophy Emblem at Top Center
        self.draw_golden_trophy(surface, cx, 48)

        # 4. 3D Adventure Typography Title: "DUNGEON" / "RECORDS"
        draw_adventure_title(surface, "DUNGEON", 68, self.font_title, cx)
        draw_adventure_title(surface, "RECORDS", 126, self.font_title, cx)

        # 5. Stats Plaque: "WIN RATE: 75% | BEST: 12 STEPS"
        plaque_w, plaque_h = 360, 36
        plaque_rect = pygame.Rect(cx - plaque_w // 2, 206, plaque_w, plaque_h)
        best_str = f"{best_steps} STEPS" if best_steps else "--"
        plaque_text = f"WIN RATE: {win_rate}%  |  BEST: {best_str}"
        self.draw_stats_plaque(surface, plaque_rect, plaque_text)

        # 6. Inner Carved Wood Frame / Records Table Board
        table_w = 444
        table_h = 360
        table_rect = pygame.Rect(cx - table_w // 2, 260, table_w, table_h)
        self.draw_records_table(surface, table_rect, records)

        # 7. Action Button: [ BACK TO MENU ]
        btn_back.rect = pygame.Rect(cx - 135, 642, 270, 48)
        btn_back.font = self.font_btn
        btn_back.style = "wood_pill"
        btn_back.draw(surface)

        # Version watermark in bottom right corner
        v_surf = self.font_version.render("v1.2.0", True, (65, 55, 58))
        surface.blit(v_surf, (self.screen_width - 55, self.screen_height - 24))
