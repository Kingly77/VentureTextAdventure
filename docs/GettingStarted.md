# Getting Started with Venture

Welcome! This guide will help you run the game, understand the code layout, and make simple changes (like adding items, rooms, and effects). If you prefer a high‑level overview first, see the Features section in the README.


## 1) Run the game locally

Prerequisites:
- Python 3.10+ recommended (earlier 3.x may work, but is not guaranteed)
- A virtual environment tool (venv is built in)

Steps:
1. Clone the repository and enter the folder.
2. Create and activate a virtualenv.
3. Install dependencies.
4. Run the game.

Commands:
```
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

python game/main.py
```

Tips:
- Type "help" in the game to list commands.
- The default starter world loads from game/worlds/default_world.json if present; otherwise the code builds a minimal world.


## 2) Quick project tour

Top-level areas you’ll touch most often:
- game/ — Gameplay loop, world data, effects, and primary models (rooms, items, spells).
- character/ — Hero and enemies (stats, leveling, combat behaviors).
- commands/ — Command parser/engine and command handlers.
- components/ — Reusable building blocks (inventory, quest log, wallet, effects core, etc.).
- tests/ — Pytest tests that cover core systems and interactions.

Entry points and wiring:
- game/main.py — Starts the game: builds/loads the world and begins the loop.
- game/rpg_adventure_game.py — Game loop and dispatch to command handlers.
- commands/engine.py — Parses input and routes to the correct command implementation.


## 3) How rooms, items, effects, and enemies fit together

- Rooms (game/room.py) hold items, links to other rooms, effects, and optional enemies/NPCs.
- Items (game/items.py) can be picked up, used, consumed, and in some cases equipped.
- Effects are modular behaviors attached to rooms/objects. The registry in game/effects/registry.py maps string keys to effect classes so they can be referenced from JSON.
- Enemies live under character/, with shared behavior in character/basecharacter.py.


## 4) Using the JSON world loader

The entire world can be defined in JSON and loaded at startup. See:
- game/json_loader.py — parses the JSON data and builds Python objects.
- game/game_world_initializer.py — selects JSON vs in-code world initialization.
- game/worlds/default_world.json — a small example world used by default if present.

Start by copying game/worlds/default_world.json and editing it. Key schemas:
- rooms[] define name, description, links, items, effects, enemies, and npcs.
- effects[] are [{ "key": "locked_door", "params": { ... } }] and hook into the effect registry.
- items[] support fields like is_usable, effect (HEAL/DAMAGE), effect_value, is_consumable, is_equipment, tags, quantity.

Once edited, just run python game/main.py again.


## 5) Adding a new effect (code + JSON)

1) Implement the effect:
- Create a class in game/effects/ that derives from RoomEffectBase (see game/effects/room_effect_base.py).
- Implement the hooks you need (on_enter, on_command, describe, etc.). Keep it small and stateless when possible.

2) Register the effect:
- Open game/effects/registry.py and add an entry mapping a string key (e.g., "mysterious_fog") to your class.

3) Reference it from JSON:
```
"effects": [
  { "key": "mysterious_fog", "params": { "intensity": 2 } }
]
```


## 6) Adding a new command

- Parser and dispatch live in commands/engine.py and commands/command.py.
- Add a new Command subclass and register it in the engine.
- Aim to keep parsing (what the player typed) separate from action logic (changing the game state).


## 7) Working with items and inventory

- Item model is in game/items.py.
- Inventory logic lives in components/inventory.py and related helpers.
- Many tests cover inventory behavior (tests/test_take_drop_commands.py, tests/test_drop_take_same_item.py, etc.). Run the tests after changes.


## 8) Testing

This project uses pytest. Basic usage:
```
pytest -q
```
With coverage:
```
pytest --cov --cov-report=term-missing
```
Focus tests to a file while iterating:
```
pytest tests/test_commands.py -q
```


## 9) Debugging tips

- If the game fails to load your JSON world, ensure required fields are present and effect keys exist in the registry.
- Use print statements sparingly inside effects or command handlers while developing.
- Run smaller subsets of tests to narrow down failures quickly.


## 10) Contributing checklist

- Run formatting (black) if configured in your editor/CI.
- Ensure tests pass (or add new tests for your feature).
- Keep effects small and composable; prefer the registry for pluggability.
- Update README and this guide when you add developer-facing features.


## Appendix: Common directories and files

- game/effects/registry.py — list of effect keys and bindings.
- game/json_loader.py — how JSON maps to runtime objects.
- game/room.py — room model.
- game/items.py — item model.
- character/hero.py — the main player character.
- commands/engine.py — command parser and router.
- components/inventory.py — inventory behavior.
- tests/ — runnable test suite demonstrating typical interactions.
