# Venture — Text Adventure RPG

A lightweight Python text-based RPG where you explore rooms, interact with objects and NPCs, battle enemies, and manage your hero via typed commands.

This repository contains the game engine, example content, and a small test suite.

If you are new to this codebase, start with docs/GettingStarted.md.

## Features
- Command-driven gameplay: look, take/drop items, use items on self or objects/NPCs, movement (go north/south/etc.), talk, status, help
- Modular systems: inventory, items with effects, rooms and interactive objects, quests, simple but extensible combat
- JSON world loader: define rooms, links, items, effects, enemies, and NPCs entirely in JSON
- Effect registry: plug room/object behaviors by key (e.g., locked doors, dark caves, NPC dialog, shops, torches)
- Enemies and combat: basic turn-based combat, enemy definitions with optional rewards
- Leveling and XP: simple progression system for the hero
- NPCs and dialog: basic NPC visibility and optional quest hooks via effects
- Shop support: configurable prices and simple buy/sell loop via an effect
- Tests included: pytest suite covers commands, parser, items, effects registry, leveling, and more
- Developer utilities: count lines, generate a Mermaid dependency graph of imports

## Tech stack
- Language: Python (CLI application)
- Package manager: pip via requirements.txt
- Testing: pytest (+ pytest-cov optional)
- Formatting: black

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
- By default, the game attempts to load the built-in JSON world at game/worlds/default_world.json; if not found, it falls back to the code-initialized world.
- Using python -m game.main is not supported by default because game/main.py imports sibling modules using simple imports (e.g., from rpg_adventure_game import Game). Prefer the command above.

## JSON world loader
You can define the entire world in JSON and load it without changing code.

Two ways to use it:
- Built-in default: Simply run the game (see above). If game/worlds/default_world.json exists, it will be used automatically.
- Custom file in your own script:
  ```python
  from game.game_world_initializer import setup_game
  from game.rpg_adventure_game import Game

  hero, start_room = setup_game(json_path="/path/to/world.json")
  game = Game(hero, start_room)
  game.run()
  ```

Schema highlights (top-level keys):
- hero: { name, level, gold }
- start_room: string key of the starting room
- rooms: object mapping room_key -> room definition
- events: optional array of global event declarations

Room definition fields (all optional unless noted):
- name (required), description (required), locked (bool)
- links: [{ dir, to, back? }] where back adds the reverse link automatically
- items: [{ name, value, is_usable?, effect?, effect_value?, is_consumable?, is_equipment?, tags?, quantity? }]
- effects: [{ key, params? }] via the effect registry (see below)
- enemies: [{ type, name?, level?, count?, reward? }]
  - type maps to an enemy class (e.g., "Goblin", "Troll").
  - reward may be an item object (same schema as above).
- npcs: [{ name, description }] simple visible NPCs that appear in room descriptions

Effect registry keys available from JSON:
- locked_door: params { target (room key, required), door_name?, locked_description?, unlocked_description?, key_name?, unlock_event?, allow_bash? }
- torch_table: no params
- npc_dialog: params { npc_name?, npc_description?, quest? { name?, description?, reward?, objective { type, target, value } } }
- dark_cave: no params
- shop: params { shopkeeper_name?, prices? { item_name: price } }

Example snippet:
```json
{
  "start_room": "forest_clearing",
  "rooms": {
    "forest_clearing": {
      "name": "Forest Clearing",
      "description": "Sunlight filters through the leaves.",
      "links": [{"dir": "north", "to": "cave", "back": "south"}],
      "effects": [{"key": "torch_table"}],
      "items": [{"name": "health potion", "value": 10, "is_usable": true, "effect": "HEAL", "effect_value": 20, "is_consumable": true}]
    },
    "cave": {
      "name": "Dark Cave Entrance",
      "description": "The air grows cold...",
      "effects": [{"key": "dark_cave"}],
      "enemies": [{"type": "Goblin", "name": "Goblin Grunt", "level": 1, "count": 1}]
    }
  }
}
```

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
- Code formatting with black:
  ```bash
  black .            # format in-place
  black --check .    # verify formatting
  ```
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
│   ├── main.py                   # Entry point (python game/main.py)
│   ├── rpg_adventure_game.py     # Game loop and command dispatch wiring
│   ├── game_world_initializer.py # Builds the starter world (rooms, items, NPCs, enemies) or loads JSON
│   ├── json_loader.py            # JSON world loader (rooms, links, items, effects, enemies, npcs, events)
│   ├── worlds/
│   │   └── default_world.json    # Default JSON world used automatically if present
│   ├── items.py, magic.py        # Items, effects, spells
│   ├── room.py, room_objs.py     # Rooms and interactive objects
│   ├── effects/                  # Room and object effects (see effects/registry.py for keys)
│   ├── underlings/               # Systems: events, leveling, questing, inventory helpers
|   └── rooms/                    # All subclasses of Room (e.g., Room, EffectRoom, ShopRoom)
|       ├── effect_room.py        # Base class for effect rooms
├── character/                    # Hero and enemies
├── commands/engine.py            # Parser, command registry, and handlers
├── components/                   # Core components and inventory
├── tests/                        # Pytest test suite
├── tools/                        # Dev utilities (count lines, mermaid graph)
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
See CONTRIBUTING.md for guidelines and docs/GettingStarted.md for a tour of the codebase.
