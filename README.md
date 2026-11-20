# Treasure Hunter // Tactical Evasion Game

A high-performance tactical evasion simulation built in **Python 3.10+**, **Pygame**, **SQLite3**, and the **google-genai SDK** (`gemini-2.5-flash` with `thinking_budget=0` for ultra-low-latency real-time decisions).

> **Architectural Constraint Compliant:**
> - Strictly **NO A\*** or classical pathfinding algorithms are used.
> - All Hunter pursuit decisions, coordinated flanking tactics, and player safe escape guidance are powered directly by **Google Gemini 2.5 Flash** via structured JSON outputs.
> - Zero I/O blocking: Background `threading.Thread(daemon=True)` workers ensure a silky smooth **60 FPS** loop at all times.
> - Lightweight greedy Manhattan-distance fallback is engaged ONLY if the API key is absent or a network timeout occurs so the game never crashes or freezes.

---

## 🎮 Mission Briefing & Tactical Directives

1. **Infiltration**: You deploy at Sector Origin `(0, 0)`.
2. **Key Acquisition**: Navigate through shifting barriers to locate and secure the **Golden Cipher Key [K]**.
3. **Extraction**: Proceed to the **Extraction Portal [E]** at `(N-1, N-1)` once the key has been collected.
4. **Evasion**: Autonomous **Hunter Drones [H]** stalk and flank you using Gemini 2.5 Flash neural directives. A single collision results in tactical casualty.

---

## 🕹️ Controls Reference

| Input | Action |
| :--- | :--- |
| **`W` / `A` / `S` / `D`** or **Arrow Keys** | Move Operative 1 grid cell cardinally |
| **`[P]` / `[SPACE]` / `[|| PAUSE]` Button** | Pause or Resume the mission at any time |
| **`[H]`** | Manually deploy a Hunter Drone reinforcement (up to 8 max) |
| **`[B]`** | Manually trigger a dynamic Barrier Shift (relocate walls safely) |
| **`[R]`** | Reset sector with a fresh procedural layout & fresh countdown |
| **`ESC`** | Pause tactical mission (or return to menu from pause overlay) |

---

## ⏱️ Tactical Standby & Pause System

1. **Anti-Rush Tactical Standby (Hut kre start hobe na)**:
   - When any mission starts or restarts, the game activates a **3-second Tactical Reconnaissance Standby**.
   - During this window, all Hunter drones and dynamic barrier shifting are completely **frozen** so you can calmly inspect the grid, note Key/Exit/Hunter positions, and plan your escape vector.
   - If you want to deploy immediately without waiting, pressing any movement key (`WASD`/Arrows) or `SPACE` instantly begins the action!
2. **Interactive Pause System (Sir Walkthrough & Demonstration Mode)**:
   - Click the on-screen **`|| PAUSE`** button (top-right corner) or press **`P`**, **`SPACE`**, or **`ESC`**.
   - **100% Unobstructed Grid View**: The center grid stays completely open so your teacher ("Sir") can inspect the board.
   - **On-Grid Educational Callouts**: Displays live pointers for `[ 👤 OPERATIVE ]`, `[ 🚨 HUNTER (Gemini AI) ]`, `[ 🔑 CIPHER KEY ]`, `[ 🚪 EXTRACTION ]`, and `[ 🟢 GEMINI SAFE PATH (NO A*) ]`.
   - **Left Dossier Card (Explain to Sir)**: Highlights core academic evaluation rubrics (`Gemini 2.5 Flash`, `budget=0`, `Strictly No A*`, `Daemon Threading`, `SQLite3`).
   - **Right Dossier Card (Controls & Mechanics)**: Allows resuming, restarting, viewing controls, and tracking simulation parameters.

---

## 🧭 HUD & Visual Navigation Aids

- **Human Operative (Gamer)**: Premium animated cyber-infiltrator operative featuring a dual-tone obsidian/cobalt exo-suit, glowing central Aegis chest crest, smart cybernetic retinal visor with an animated horizontal data-scanline, articulated gauntlets with wrist-PDA, animated combat boots with cyan heel stabilizer LEDs, multi-stage volumetric flashlight beam, and the secured Golden Key docked to their backpack.
- **Human Mercenary (Hunter)**: Heavily armored human juggernaut mercenary guards featuring ballistic combat helmets, menacing triple/dual glowing red Night-Vision Goggles (NVG) with hot laser cores, crimson heavy body armor with hazard warning stripes on shoulder pauldrons, combat boots with cadence stride, tactical assault carbine, and a **razor-sharp tactical red laser sight** projecting forward up to 1.5 grid cells with a pulsing target dot.
- **Cybernetic Blast Barriers (Blocks)**: 3D chiseled bevel plates with specular rim lights and ambient depth shadows, carbon-hull inset panels, 4 corner heavy metallic rivets/bolts, central glowing cyan diamond reactor nodes with circuit conduits, and an animated high-voltage amber hazard surge during wall relocation warnings.
- **Quantum Extraction Portal & Golden Cipher Key**: Concentric rotating quantum containment rings with 4 orbital focus nodes and a swirling emerald extraction vortex when unlocked. The Golden Key features a 3D faceted diamond relic with a rotating holographic particle ring and levitation bobbing.
- **Green Breadcrumbs**: Safe 3-step grid coordinates `[r, c]` computed in real time by Gemini 2.5 Flash, actively dodging Hunter lines of sight and exploiting blind spots behind their directional facing cones.
- **Pulsing Yellow Guide Arrow**: Dynamic navigation vector pointing from the operative to the current objective (Golden Key if uncollected, Extraction Portal if collected).
- **Directional Vision Cones**: Visualized sensors projecting from each Hunter drone indicating their active facing vector `(dr, dc)`.
- **Bottom HUD Console**: Displays current difficulty level, step counter, all-time best victory steps from SQLite, key acquisition badge, Gemini latency in milliseconds with pulsating LED status pip, and live Tactical Commander transmissions.

---

## 🏛️ Modular Code Architecture

```
AI Project Game/
├── main.py             # CLI entry point and engine runner
├── game_engine.py      # Core 60 FPS clock loop, state machine, input dispatch, LERP updates
├── ai_tactical.py      # GeminiTacticalAI (gemini-2.5-flash, thinking_budget=0, thread-safe JSON)
├── environment.py      # GridEnvironment (N x N matrix, dynamic walls, Hunter tracking & LERP)
├── database.py         # DatabaseManager (SQLite dungeon_records.db, match history, best steps)
├── ui_manager.py       # UIManager (Home screen, How to Play, dynamic scaling grid, HUD, overlays)
├── sound_effects.py    # SoundManager (Procedural synth audio feedback with NumPy)
├── test_suite.py       # Comprehensive automated test suite (12 headless integration tests)
└── dungeon_records.db  # SQLite database storing match history and records
```

### 1. `DatabaseManager` (`database.py`)
- SQLite database (`dungeon_records.db`).
- Table `game_history` (`id`, `player_name`, `steps`, `result`, `timestamp`).
- Methods for persisting match outcomes and querying minimum victory step counts.

### 2. `GeminiTacticalAI` (`ai_tactical.py`)
- Calls `gemini-2.5-flash` using `google-genai` SDK with `types.GenerateContentConfig` and `ThinkingConfig(thinking_budget=0)`.
- Pydantic structured output validation (`TacticalDecision`):
  1. `hunter_moves`: Next valid cardinal move (`UP`, `DOWN`, `LEFT`, `RIGHT`, `STAY`) for each active hunter to coordinate flanking and interception.
  2. `recommended_path`: Next 3 safe grid coordinates `[r, c]` guiding the player toward the Key or Exit.
  3. `commander_order`: A tense tactical transmission under 12 words.
- Asynchronous daemon worker thread with `threading.Lock` protects the 60 FPS loop.
- Lightweight greedy Manhattan-distance fallback strictly engaged ONLY if API key is missing or a network timeout occurs.

### 3. `GridEnvironment` (`environment.py`)
- Manages $N \times N$ matrix (`5x5`, `7x7`, `9x9`, `11x11`).
- Dynamic wall relocations (every 2.5s without overwriting entities: Player, Hunters, Key, Exit, Start).
- Hunter spawning (up to 8 hunters max, tracking discrete positions, continuous LERP visual coordinates, and directional facing vectors).
- Smooth visual LERP rendering: `visual = visual + (target - visual) * 0.28`.

### 4. `UIManager` & `GameEngine` (`ui_manager.py`, `game_engine.py`)
- Game states: `HOME`, `HOW_TO_PLAY`, `PLAYING`, `GAME_OVER`.
- Dynamic cell pixel scaling fitting any grid dimension cleanly above the HUD console.
- Interactive callsign input, grid dimension selector, and difficulty selector.
- Seamless Level Progression: Conquering a level advances from **Recruit** to **Tactical** to **Nightmare** with clean state resets and zero memory leaks.

---

## ⚡ Quickstart & Execution

### Prerequisites
- Python 3.10+
- Pygame (`pip install pygame`)
- Google GenAI SDK (`pip install google-genai`)
- Pydantic (`pip install pydantic`)
- NumPy (`pip install numpy`)

### Configuration (Optional Gemini API Key)
Set your Google Gemini API key:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-api-key-here"

# Or Linux / macOS
export GEMINI_API_KEY="your-api-key-here"
```
*(If no API key is provided, the game automatically runs with the greedy Manhattan fallback and informs you on the HUD).*

### Launching the Game
```bash
# Standard launch (Interactive Home Menu)
python main.py

# Launch with custom CLI arguments
python main.py --grid-size 7 --level 2 --player-name "CYBER-SPECTRE"
```

### Running the Test Suite
```bash
python test_suite.py
```
*(All 12 unit and integration tests run headlessly in under 0.5s).*
