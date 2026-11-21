"""
UI Art Helpers: Reusable procedural rendering routines for dungeon environment,
parchment scrolls, 3D adventure typography, royal crowns, and metal padlocks.
"""

from typing import List, Tuple
import pygame


def draw_dungeon_background(surface: pygame.Surface, screen_width: int, screen_height: int) -> None:
    """Render dark dungeon stone walls with warm torchlight ambient lighting."""
    surface.fill((20, 15, 17))
    brick_w, brick_h = 84, 42
    for row, y in enumerate(range(0, screen_height, brick_h)):
        offset = (brick_w // 2) if (row % 2 == 1) else 0
        for x in range(-offset, screen_width + brick_w, brick_w):
            rect = pygame.Rect(x, y, brick_w - 3, brick_h - 3)
            dist_x = abs((x + brick_w // 2) - screen_width // 2) / (screen_width // 2)
            dist_y = abs((y + brick_h // 2) - screen_height // 2) / (screen_height // 2)
            falloff = max(0.0, 1.0 - (dist_x * 0.5 + dist_y * 0.5))
            base_r = int(32 + 25 * falloff)
            base_g = int(24 + 16 * falloff)
            base_b = int(26 + 10 * falloff)
            v = ((x * 23 + y * 41) % 15) - 7
            pygame.draw.rect(surface, (base_r + v, base_g + v, base_b + v), rect, border_radius=3)
            pygame.draw.line(surface, (10, 8, 9), (x, y + brick_h - 3), (x + brick_w - 3, y + brick_h - 3), 2)
            pygame.draw.line(surface, (10, 8, 9), (x + brick_w - 3, y), (x + brick_w - 3, y + brick_h - 3), 2)
            pygame.draw.line(surface, (base_r + v + 16, base_g + v + 12, base_b + v + 10), (x + 2, y + 1), (x + brick_w - 5, y + 1), 1)


def draw_parchment_chassis(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Draw aged parchment scroll sheet with carved wood border and brass corner rivets."""
    # Drop shadow
    shadow_rect = rect.move(0, 8)
    pygame.draw.rect(surface, (12, 8, 8), shadow_rect, border_radius=14)

    # Aged parchment paper fill
    pygame.draw.rect(surface, (230, 195, 138), rect, border_radius=14)
    inner_rect = rect.inflate(-10, -10)
    pygame.draw.rect(surface, (240, 212, 162), inner_rect, border_radius=10)

    # Dark carved wood / leather contour outline
    pygame.draw.rect(surface, (72, 42, 18), rect, width=4, border_radius=14)
    # Inner decorative thin border
    pygame.draw.rect(surface, (200, 162, 110), inner_rect.inflate(-8, -8), width=1, border_radius=8)

    # 4 Golden Brass Bolts / Rivets in the corners
    rivet_offset = 22
    rivet_pts = [
        (rect.left + rivet_offset, rect.top + rivet_offset),
        (rect.right - rivet_offset, rect.top + rivet_offset),
        (rect.left + rivet_offset, rect.bottom - rivet_offset),
        (rect.right - rivet_offset, rect.bottom - rivet_offset),
    ]
    for rx, ry in rivet_pts:
        pygame.draw.circle(surface, (54, 30, 12), (rx, ry), 9)
        pygame.draw.circle(surface, (196, 142, 42), (rx, ry), 8)
        pygame.draw.circle(surface, (248, 196, 72), (rx, ry), 6)
        pygame.draw.circle(surface, (255, 248, 180), (rx - 2, ry - 2), 3)


def draw_royal_crown(surface: pygame.Surface, x: int, y: int) -> None:
    """Render golden royal crown with emerald and ruby gemstones."""
    pts = [
        (x - 34, y + 26),
        (x - 30, y + 6),
        (x - 16, y + 15),
        (x, y - 2),
        (x + 16, y + 15),
        (x + 30, y + 6),
        (x + 34, y + 26),
    ]
    shadow_pts = [(px, py + 3) for px, py in pts]
    pygame.draw.polygon(surface, (52, 24, 6), shadow_pts)
    pygame.draw.polygon(surface, (248, 182, 34), pts)
    pygame.draw.polygon(surface, (52, 24, 6), pts, 3)

    band_rect = pygame.Rect(x - 34, y + 20, 68, 10)
    pygame.draw.rect(surface, (218, 148, 24), band_rect, border_radius=3)
    pygame.draw.rect(surface, (52, 24, 6), band_rect, width=2, border_radius=3)

    pygame.draw.ellipse(surface, (46, 204, 113), pygame.Rect(x - 6, y + 22, 12, 7))
    pygame.draw.ellipse(surface, (20, 90, 45), pygame.Rect(x - 6, y + 22, 12, 7), 1)
    pygame.draw.circle(surface, (255, 255, 255), (x - 2, y + 24), 1)

    pygame.draw.circle(surface, (231, 76, 60), (x - 20, y + 25), 3)
    pygame.draw.circle(surface, (231, 76, 60), (x + 20, y + 25), 3)


def draw_adventure_title(surface: pygame.Surface, text: str, y_pos: int, font: pygame.font.Font, cx: int) -> None:
    """Render stacked 3D adventure typography with dark chocolate extrusion and gold gradient."""
    txt_surf = font.render(text, True, (250, 185, 45))
    tw, th = txt_surf.get_size()
    tx = cx - tw // 2

    for off_y in [6, 5, 4]:
        for ox in [-1, 0, 1]:
            s_surf = font.render(text, True, (46, 18, 5))
            surface.blit(s_surf, (tx + ox, y_pos + off_y))

    outline_surf = font.render(text, True, (46, 18, 5))
    for dx in [-3, -2, -1, 0, 1, 2, 3]:
        for dy in [-2, -1, 0, 1, 2]:
            surface.blit(outline_surf, (tx + dx, y_pos + dy))

    surface.blit(txt_surf, (tx, y_pos))


def draw_padlock(surface: pygame.Surface, center_x: int, center_y: int) -> None:
    """Render a crisp, metallic padlock icon on locked stone tiles."""
    sh_rect = pygame.Rect(center_x - 6, center_y - 9, 12, 11)
    pygame.draw.arc(surface, (50, 54, 62), sh_rect, 0, 3.1415, 3)
    pygame.draw.arc(surface, (200, 205, 215), sh_rect.move(0, -1), 0, 3.1415, 2)

    b_rect = pygame.Rect(center_x - 8, center_y, 16, 13)
    pygame.draw.rect(surface, (36, 32, 28), b_rect.move(0, 2), border_radius=3)
    pygame.draw.rect(surface, (138, 142, 150), b_rect, border_radius=3)
    pygame.draw.rect(surface, (196, 202, 212), b_rect.inflate(-2, -2), border_radius=2)
    pygame.draw.rect(surface, (120, 125, 134), b_rect.inflate(-4, -4), border_radius=1)
    pygame.draw.rect(surface, (48, 44, 40), b_rect, width=1, border_radius=3)

    pygame.draw.circle(surface, (32, 28, 24), (center_x, center_y + 4), 2)
    pygame.draw.rect(surface, (32, 28, 24), pygame.Rect(center_x - 1, center_y + 4, 2, 4))
