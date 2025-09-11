# Venture — Text Adventure RPG

A lightweight Python text-based RPG where you explore rooms, interact with objects and NPCs, battle enemies, and manage your hero via typed commands.

This repository contains the game engine, example content, and a small test suite.

## Overview
- Command-driven gameplay (type look, take coin, use potion on self, go north, etc.)
- Modular game systems: inventory, items/effects, rooms/objects, quests, and a simple combat loop
- Built-in help and a small world to get you started

## Tech stack
- Language: Python (CLI application)
- Package manager: pip via requirements.txt
- Testing: pytest (+ pytest-cov optional)
- Formatting: black

> TODO: Confirm the minimum supported Python version. Code uses modern typing and should work on 3.10+, but the exact floor hasn’t been verified.

## Requirements
- Python 3.x
- A virtual environment tool (venv, virtualenv, or similar)

## Installation
1. Clone the repository
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Create and activate a virtual environment
   ```bash
   python -m venv .venv
   # Linux/Mac
   source .venv/bin/activate
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Run the game
Run from the repository root:
```bash
python game/main.py
```
Notes:
- The entry point is game/main.py, which initializes the world and starts the loop.
- Using python -m game.main is not supported by default because game/main.py imports sibling modules using simple imports (e.g., from rpg_adventure_game import Game). Prefer the command above.

## Commands (in-game)
Type help at any time for a list of commands. Examples:
- look — describe the current room
- inventory — show your items
- take coin and drop coin — pick up or drop items
- use potion on self — use an item on yourself (or on an object/NPC when applicable)
- go north — move between rooms
- talk — speak to an NPC when available
- status — show hero status
- quit — exit the game

## Scripts and tooling
- Count Python lines (totals or per-file):
  ```bash
  python tools/count_lines.py . --per-file --relative
  ```
- Generate a Mermaid dependency graph of imports (writes Mermaid text to stdout):
  ```bash
  python tools/mermaid_dependency_graph.py --help
  # Example (only internal modules, compact labels):
  python tools/mermaid_dependency_graph.py . --only-internal --max-label-len 28 > docs/diagram.mmd
  ```

## Environment variables
No environment variables are required for normal gameplay.

> TODO: If any optional environment flags are desired (e.g., DEBUG levels or feature toggles), document them here.

## Running tests
This project uses pytest.
```bash
pytest -q
```
With coverage:
```bash
pytest --cov --cov-report=term-missing
```

## Project structure
Abridged layout of key modules:
```
Venture/
├── game/
│   ├── main.py                 # Entry point (python game/main.py)
│   ├── rpg_adventure_game.py   # Game loop and command dispatch wiring
│   ├── game_world_initializer.py# Builds the starter world (rooms, items, NPCs, enemies)
│   ├── items.py, magic.py      # Items, effects, spells
│   ├── room.py, room_objs.py   # Rooms and interactive objects
│   ├── effects/                # Room and object effects
│   └── underlings/             # Systems: events, leveling, questing, inventory helpers
├── character/                  # Hero and enemies
├── commands/engine.py          # Parser, command registry, and handlers
├── components/                 # Core components and inventory
├── tests/                      # Pytest test suite
├── tools/                      # Dev utilities (count lines, mermaid graph)
├── requirements.txt
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## Changelog
See CHANGELOG.md for notable changes over time.

## License
This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Contributing
Issues and pull requests are welcome.
> TODO: Add contribution guidelines and code style rules if needed.