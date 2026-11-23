"""
Main: Entry point for the Treasure Hunter Tactical Evasion game.

Launches the GameEngine with full Pygame 60 FPS loop, SQLite persistence,
and Google Gemini 3.8 Flash neural guidance.
Compatible with desktop execution and WebAssembly / Pygbag browser hosting.
"""

import sys
import argparse
import asyncio
from game_engine import GameEngine


async def main() -> None:
    """Parse command-line arguments and start the game engine."""
    parser = argparse.ArgumentParser(description="Treasure Hunter: Tactical Evasion Game")
    parser.add_argument("--grid-size", type=int, choices=[5, 7, 9, 11], default=7,
                        help="Initial grid size (default: 7)")
    parser.add_argument("--level", type=int, choices=[1, 2, 3], default=2,
                        help="Initial difficulty level (1: Recruit, 2: Tactical, 3: Nightmare)")
    parser.add_argument("--player-name", type=str, default="OPERATIVE-01",
                        help="Player callsign (default: OPERATIVE-01)")
    parser.add_argument("--api-key", type=str, default=None,
                        help="Optional Google Gemini API key (or set GEMINI_API_KEY env var)")

    args = parser.parse_args()

    engine = GameEngine()
    if args.api_key:
        engine.ai.set_api_key(args.api_key)

    # Set initial parameters
    engine.selected_grid_size = args.grid_size
    engine.selected_level = args.level
    engine.player_name = args.player_name

    # Start main game loop (async yields control to browser event loop in WASM)
    await engine.run_async()


if __name__ == "__main__":
    asyncio.run(main())
