# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [0.1.0] - 2025-09-09

Suggested semantic version bump: minor

### Added
- Combat system with attack and spell-casting commands. ([8778134](https://github.com/Kingly77/VentureTextAdventure/commit/877813467eea8a564ef8a080728fb89e05441e9d))
- Equip and weapon-check commands to support gear usage. ([89624c5](https://github.com/Kingly77/VentureTextAdventure/commit/89624c58a141660d1633394c1ef6f1da50f64ce5))
- `LockedDoorEffect` for flexible locked door interactions supporting keys, bashing, and external events. ([5faaf59](https://github.com/Kingly77/VentureTextAdventure/commit/5faaf59a37f4316bef3afb50b4c9d5116bf94d66))
- `RoomCondition` for checking whether rooms are locked. ([5faaf59](https://github.com/Kingly77/VentureTextAdventure/commit/5faaf59a37f4316bef3afb50b4c9d5116bf94d66))

### Changed
- Improved `handle_item_use` and `handle_interaction` across effects for better verb support. ([5faaf59](https://github.com/Kingly77/VentureTextAdventure/commit/5faaf59a37f4316bef3afb50b4c9d5116bf94d66))
- Improved item tags and quantity handling in inventory, including fallback logic for tag merging. ([5faaf59](https://github.com/Kingly77/VentureTextAdventure/commit/5faaf59a37f4316bef3afb50b4c9d5116bf94d66))
- Replaced `DoorEffectExpanded` with `LockedDoorEffect` in world initialization for clearer behavior. ([5faaf59](https://github.com/Kingly77/VentureTextAdventure/commit/5faaf59a37f4316bef3afb50b4c9d5116bf94d66))
- Updated `Room` interaction handling to simplify effect coordination and improve consistency. ([5faaf59](https://github.com/Kingly77/VentureTextAdventure/commit/5faaf59a37f4316bef3afb50b4c9d5116bf94d66))


## Full Git History

- 2025-09-09 - [5faaf59](https://github.com/Kingly77/VentureTextAdventure/commit/5faaf59) - - Add `LockedDoorEffect` for flexible locked door interactions, supporting keys, bashing, and external events. - Introduce `RoomCondition` for checking if rooms are locked. - Add `mermaid_dependency_graph.py` for generating module dependency diagrams. - Refactor `handle_item_use` and `handle_interaction` across effects for better verb support. - Improve item tags and quantity handling in inventory with fallback logic for tag merging. - Replace `DoorEffectExpanded` with `LockedDoorEffect` in `game_world_initializer`. - Update `Room` interaction handling to simplify effect coordination.
- 2025-08-29 - [8778134](https://github.com/Kingly77/VentureTextAdventure/commit/8778134) - Add combat system with attack and spell-casting commands:
- 2025-08-28 - [38fb2de](https://github.com/Kingly77/VentureTextAdventure/commit/38fb2de) - Refactor command handlers to remove game-specific dependencies:
- 2025-08-28 - [43509eb](https://github.com/Kingly77/VentureTextAdventure/commit/43509eb) - Add helper for test execution and refactor parser tests for clarity:
- 2025-08-27 - [89624c5](https://github.com/Kingly77/VentureTextAdventure/commit/89624c5) - Add equip and weapon-check commands, improve item classification and hero weapon logic:
- 2025-08-27 - [83b9aae](https://github.com/Kingly77/VentureTextAdventure/commit/83b9aae) - Refactor `RoomDiscEffect` structure, enhance NPC dialog effect handling, and add dependency management:
- 2025-08-15 - [5595943](https://github.com/Kingly77/VentureTextAdventure/commit/5595943) - Refactor dungeon room linking and error handling:
- 2025-08-15 - [4097b9d](https://github.com/Kingly77/VentureTextAdventure/commit/4097b9d) - Introduce item usage and spell casting mixins, refactor inventory handling:
- 2025-08-15 - [d0c24ec](https://github.com/Kingly77/VentureTextAdventure/commit/d0c24ec) - Refactor code for consistency and readability:
- 2025-08-13 - [812a6e6](https://github.com/Kingly77/VentureTextAdventure/commit/812a6e6) - Refactor type hints and improve code consistency:
- 2025-08-13 - [5fe5e14](https://github.com/Kingly77/VentureTextAdventure/commit/5fe5e14) - Update type hints across modules and improve code consistency:
- 2025-08-12 - [4825ae4](https://github.com/Kingly77/VentureTextAdventure/commit/4825ae4) - Add 5-room Goblin Dungeon with linked rooms, enemies, and magic stick quest:
- 2025-08-12 - [4d3f7ec](https://github.com/Kingly77/VentureTextAdventure/commit/4d3f7ec) - Refactor room creation and linking logic:
- 2025-08-12 - [ae60213](https://github.com/Kingly77/VentureTextAdventure/commit/ae60213) - Refactor effects module structure and improve NPC interaction handling:
- 2025-08-11 - [98b7f62](https://github.com/Kingly77/VentureTextAdventure/commit/98b7f62) - Refactor command registration and item usage handling:
- 2025-08-11 - [dcb7a66](https://github.com/Kingly77/VentureTextAdventure/commit/dcb7a66) - Introduce unified command engine with registry:
- 2025-08-11 - [348b896](https://github.com/Kingly77/VentureTextAdventure/commit/348b896) - Refactor questing system for event-driven updates:
- 2025-08-11 - [6b50c00](https://github.com/Kingly77/VentureTextAdventure/commit/6b50c00) - Introduce NPC framework and Village Square enhancements:
- 2025-08-10 - [ec490fa](https://github.com/Kingly77/VentureTextAdventure/commit/ec490fa) - Simplify `use_command` logic and improve code clarity.
- 2025-08-10 - [111c5ea](https://github.com/Kingly77/VentureTextAdventure/commit/111c5ea) - Add tests for room item usage effects and refactor item handling logic:
- 2025-08-09 - [4fe5ac3](https://github.com/Kingly77/VentureTextAdventure/commit/4fe5ac3) - Enhance interactions and items:
- 2025-08-09 - [bfde57b](https://github.com/Kingly77/VentureTextAdventure/commit/bfde57b) - Enhance interactions and items:
- 2025-08-09 - [c21931f](https://github.com/Kingly77/VentureTextAdventure/commit/c21931f) - Refactor room effects for modular interaction handling:
- 2025-08-09 - [9e90000](https://github.com/Kingly77/VentureTextAdventure/commit/9e90000) - Remove obsolete `manamix.py` and update imports for mixin usage in `hero.py`.
- 2025-08-09 - [7160134](https://github.com/Kingly77/VentureTextAdventure/commit/7160134) - Modularize hero mixins for enhanced reusability:
- 2025-08-09 - [0bc77e2](https://github.com/Kingly77/VentureTextAdventure/commit/0bc77e2) - Switch to `logging` for inventory and room actions:
- 2025-08-09 - [b011c78](https://github.com/Kingly77/VentureTextAdventure/commit/b011c78) - Refactor quest and mana systems for modularity:
- 2025-08-08 - [74655d6](https://github.com/Kingly77/VentureTextAdventure/commit/74655d6) - Remove obsolete documentation files: `items.md` and `TODO.md`.
- 2025-08-08 - [914d412](https://github.com/Kingly77/VentureTextAdventure/commit/914d412) - Update `.gitignore` to exclude `.junie` files
- 2025-08-08 - [0a6a23d](https://github.com/Kingly77/VentureTextAdventure/commit/0a6a23d) - Introduce QuestingSystem and integrate with event-driven framework:
- 2025-08-08 - [f8cd33c](https://github.com/Kingly77/VentureTextAdventure/commit/f8cd33c) - Refactor Wallet module and enhance functionality:
- 2025-08-08 - [40c5b24](https://github.com/Kingly77/VentureTextAdventure/commit/40c5b24) - Introduce Wallet system and refactor gold management:
- 2025-08-08 - [12ecc30](https://github.com/Kingly77/VentureTextAdventure/commit/12ecc30) - Add tests for LevelingSystem integration and refactor leveling logic:
- 2025-08-07 - [339ddbc](https://github.com/Kingly77/VentureTextAdventure/commit/339ddbc) - Add experience tracking and line counting utility:
- 2025-08-07 - [e3c49f8](https://github.com/Kingly77/VentureTextAdventure/commit/e3c49f8) - Merge remote-tracking branch 'origin/master'
- 2025-08-07 - [d86972d](https://github.com/Kingly77/VentureTextAdventure/commit/d86972d) - Add leveling system and XP integration for heroes
- 2025-08-03 - [e061cdb](https://github.com/Kingly77/VentureTextAdventure/commit/e061cdb) - Update LICENSE
- 2025-08-01 - [9f14b8e](https://github.com/Kingly77/VentureTextAdventure/commit/9f14b8e) - Create LICENSE
- 2025-08-01 - [6b4cdf9](https://github.com/Kingly77/VentureTextAdventure/commit/6b4cdf9) - Refactor: Improve code readability and formatting across multiple files.
- 2025-08-01 - [92d52d0](https://github.com/Kingly77/VentureTextAdventure/commit/92d52d0) - Add test suite for validating event system improvements: - Cover return value collection, exception handling, enhanced handler functionality, and debugging support. - Test one-time handler removal and error handling mechanisms in event handlers. - Ensure comprehensive coverage of new and existing event features.
- 2025-08-01 - [14c6605](https://github.com/Kingly77/VentureTextAdventure/commit/14c6605) - Add logging support and implement code style improvements: - Integrate basic logging setup in `main.py` for debug-level messages. - Refactor to remove redundant comments, trim excess newlines, and ensure consistent formatting across files. - Introduce `QuestAwareInventory` for enhanced quest-related inventory handling. - Update `.idea/misc.xml` with new Black configuration. - Adjust multi-line formatting for better readability.
- 2025-08-01 - [57a45dc](https://github.com/Kingly77/VentureTextAdventure/commit/57a45dc) - Enhance error handling and functionality across the codebase: - Add custom exceptions (`EventNotFoundError`, `HandlerNotFoundError`) for better event error management. - Refactor `use_command` for improved structure, context awareness, and detailed usage flows. - Update quest progression and event triggering to provide more informative responses. - Improve event management with detailed logging, information retrieval, and cleanup methods. - Fix import paths in `test_parser` and improve test mock setups. - Minor adjustments to `hero` and `adventure_game` for better handling of edge cases and unexpected errors.
- 2025-07-18 - [e65177e](https://github.com/Kingly77/VentureTextAdventure/commit/e65177e) - Merge remote-tracking branch 'origin/master'
- 2025-07-18 - [375be82](https://github.com/Kingly77/VentureTextAdventure/commit/375be82) - fixed running
- 2025-07-18 - [420f45b](https://github.com/Kingly77/VentureTextAdventure/commit/420f45b) - Introduce modular game world setup and restructure main entry point: add `game_world_initializer.py` to initialize hero, rooms, and interactions; update main script to use the modular setup; adjust README usage instructions accordingly.
- 2025-07-10 - [04bd0bc](https://github.com/Kingly77/VentureTextAdventure/commit/04bd0bc) - Remove redundant comments and clean up unused lines: simplify `RoomObject`, refine `handle_item_use` logic, update calls with explicit arguments, and remove extra newline in `setup.py`.
- 2025-07-03 - [2f5bb77](https://github.com/Kingly77/VentureTextAdventure/commit/2f5bb77) - git ignore added
- 2025-07-03 - [22a9bbb](https://github.com/Kingly77/VentureTextAdventure/commit/22a9bbb) - Add initial README.md outlining game description, features, installation steps, and usage instructions.
- 2025-07-03 - [b93fc07](https://github.com/Kingly77/VentureTextAdventure/commit/b93fc07) - Improve game logic and usability: fix item quantity initialization, enhance multi-command processing, update debug commands with item addition, and clean up redundant comments.
- 2025-07-02 - [c4b6fd5](https://github.com/Kingly77/VentureTextAdventure/commit/c4b6fd5) - Add "go back" functionality and enhance room and quest interactions: track hero's last room for backtracking, improve quest progress display, refine setup logic, and update `RoomObject` with dynamic interaction and tag methods.
- 2025-06-30 - [55f0913](https://github.com/Kingly77/VentureTextAdventure/commit/55f0913) - Removed misleading comments
- 2025-06-30 - [3afcaa6](https://github.com/Kingly77/VentureTextAdventure/commit/3afcaa6) - Remove unnecessary newline in the main entry point.
- 2025-06-30 - [7c2fead](https://github.com/Kingly77/VentureTextAdventure/commit/7c2fead) - Refactor and enhance room object interactions: update `RoomObject` to support dynamic tags and refined item usage, introduce stricter type hints, improve `Room` and `Item` integrations, and add logging for error handling and event triggering.
- 2025-06-29 - [099bbbf](https://github.com/Kingly77/VentureTextAdventure/commit/099bbbf) - Add `test_parser.py` for comprehensive parser tests: includes fixtures for game setup, tests for command parsing, dispatching methods and functions, integration with the `Game` object, and handling of complex and unknown commands.
- 2025-06-29 - [565697c](https://github.com/Kingly77/VentureTextAdventure/commit/565697c) - Refactor `Game` initialization and command parsing: update `Game` to accept `hero` and `room` as arguments, streamline command parsing with `parse_and_execute` method, and adjust `setup_game` usage in the main entry point.
- 2025-06-29 - [d872edc](https://github.com/Kingly77/VentureTextAdventure/commit/d872edc) - Add comprehensive test coverage for commands and game interactions: introduce `test_commands.py` to validate hero actions, room navigation, and item handling, and `test_game_interaction.py` for interactive room object behavior, item-object interactions, and state transitions.
- 2025-06-29 - [150d26a](https://github.com/Kingly77/VentureTextAdventure/commit/150d26a) - Refactor `RoomObject` logic: move `RoomObject` class to a separate module, enhance functionality with tags and interaction events, update room interactions to support object-based item usage, and integrate `tags` into `Item` for dynamic interactions.
- 2025-06-28 - [9678c89](https://github.com/Kingly77/VentureTextAdventure/commit/9678c89) - Introduce quest progress and event system: enhance `Quest` class with progress and completion tracking via `Events`, integrate quest item handling into `RpgHero`, update `Events` system to improve handler management, and refine shop item pricing logic.
- 2025-06-28 - [91127e7](https://github.com/Kingly77/VentureTextAdventure/commit/91127e7) - Enhance item validation, inventory handling, and gold mechanics: introduce stricter validation for `Item` attributes, add `add_gold` and `spend_gold` methods to `RpgHero`, improve inventory display formatting, and extend shop interactions with updated buy/sell logic and new `Shack Shop` room.
- 2025-06-28 - [8a6b6c2](https://github.com/Kingly77/VentureTextAdventure/commit/8a6b6c2) - Add main game logic encapsulation: introduce `Game` class with command processing and game loop, enhance room and combat interactions, and update item usage to return success status.
- 2025-06-27 - [8cf2895](https://github.com/Kingly77/VentureTextAdventure/commit/8cf2895) - Improve inventory handling and room interactions: add exception handling for inventory operations, introduce `handle_take` and `handle_drop` effects, and update `ShopEffect` with enhanced buy/sell logic.
- 2025-06-27 - [846f09e](https://github.com/Kingly77/VentureTextAdventure/commit/846f09e) - Add `gold` property to `RpgHero`, enhance `Item` with flexible `**kwargs`, improve item usage messaging, fix room effect imports, and introduce `ShopEffect` for shop interactions.
- 2025-06-27 - [8e6348d](https://github.com/Kingly77/VentureTextAdventure/commit/8e6348d) - Enhance room functionality and game setup: add `unlock` and `change_description` methods to `Room`, improve command registration with new actions (e.g., "grab"), streamline event handling with `functools.partial`, and introduce `requirements.txt` for dependencies.
- 2025-06-27 - [e5b49b3](https://github.com/Kingly77/VentureTextAdventure/commit/e5b49b3) - Refactor event handling in `setup_game`: replace `event` with `Event` for clarity, remove unused imports, and streamline foyer unlocking logic.
- 2025-06-27 - [a88e78e](https://github.com/Kingly77/VentureTextAdventure/commit/a88e78e) - Add `add_object` method to `Room`: enhance room functionality to support `RoomObject` management, update room description logic to include objects, extend `Events` system with one-time event handling, and integrate new objects and interactions into game setup (e.g., unlocking Foyer door).
- 2025-06-27 - [bc7fed6](https://github.com/Kingly77/VentureTextAdventure/commit/bc7fed6) - Introduce `RoomObject` class for interactive room elements: add functionality to handle item interactions with objects (e.g., doors, tables), update room logic to support these objects, enhance `setup_game` with example `RoomObject`, and clean up imports.
- 2025-06-20 - [1c1bb82](https://github.com/Kingly77/VentureTextAdventure/commit/1c1bb82) - Refactor game setup and main loop: simplify `setup_game` by reducing returned values, clean up input handling in `main_game_loop`, and remove unused variables and imports.
- 2025-06-20 - [435bee8](https://github.com/Kingly77/VentureTextAdventure/commit/435bee8) - Add TODO file to outline future changes: include note for making questing use events.
- 2025-06-20 - [46b2d92](https://github.com/Kingly77/VentureTextAdventure/commit/46b2d92) - Add event handling system: introduce `Handler` abstract base class and `_Event` for managing event registration, removal, and triggering. Update project SDK to Python 3.13.
- 2025-06-20 - [4eb4fc2](https://github.com/Kingly77/VentureTextAdventure/commit/4eb4fc2) - Remove unused commands and legacy logic in `adventure.py`, consolidate deprecated functionality into `save_incase.py`, refactor `help_command` with reusable `HELP_TEXT`, and improve inventory handling in `command.py`.
- 2025-06-20 - [dee9be1](https://github.com/Kingly77/VentureTextAdventure/commit/dee9be1) - Refactor inventory handling: centralize inventory commands into `handle_inventory_command`, streamline command registration in `adventure.py`, and clean up unused legacy logic. Update project SDK to Python 3.14.
- 2025-06-19 - [9e3dbd5](https://github.com/Kingly77/VentureTextAdventure/commit/9e3dbd5) - Clean up imports and exclude unnecessary virtual environment folders in project configuration.
- 2025-06-19 - [125b78b](https://github.com/Kingly77/VentureTextAdventure/commit/125b78b) - Refactor and enhance game mechanics: abstract `help` and `use` commands into dedicated methods, introduce `is_locked` property for rooms to support locked doors, add `BashDoorEffect` for unlocking mechanisms, and update `setup_game` with new room and connection logic. Clean up and reorganize project files.
- 2025-06-19 - [ad0f923](https://github.com/Kingly77/VentureTextAdventure/commit/ad0f923) - Remove unused `completed_quest` method from `hero.py` to clean up obsolete logic.
- 2025-06-19 - [9d4b71e](https://github.com/Kingly77/VentureTextAdventure/commit/9d4b71e) - Introduce quest system: add `Quest` and `Objective` classes, implement `QuestLog` for managing active and completed quests, integrate quests into hero setup, update inventory and reward mechanics, and add `status` and `turn-in` commands in `adventure.py`.
- 2025-06-19 - [0b2d0f8](https://github.com/Kingly77/VentureTextAdventure/commit/0b2d0f8) - Refactor RoomEffect system and enhance room setup: rename `RoomEffect` to `RoomDiscEffect`, update associated methods and effects, add new `manor` room with items and connections, and improve hero inventory and component handling.
- 2025-06-19 - [e3db1bf](https://github.com/Kingly77/VentureTextAdventure/commit/e3db1bf) - Add combatants system to rooms: introduce `combatants` property in `Room` to manage entities like enemies, update goblin interactions with rewards, streamline combat logic in `adventure.py`, and clean up import structure.
- 2025-06-18 - [e1f3bcb](https://github.com/Kingly77/VentureTextAdventure/commit/e1f3bcb) - Refactor combat input handling: improve `attack` method logic with argument parsing and exception handling, fix typo in `goblin.attack`, and clean up unused imports.
- 2025-06-18 - [04f965c](https://github.com/Kingly77/VentureTextAdventure/commit/04f965c) - Refactor inventory and item handling: add `is_consumable` attribute to `Item`, improve `remove_item` method to return removed items, streamline `attack` logic across characters, enhance enemy and room interactions, and optimize `adventure.py` inventory flows.
- 2025-06-18 - [807ad90](https://github.com/Kingly77/VentureTextAdventure/commit/807ad90) - Refactor util functions: remove redundant inventory and spell handling logic, streamline exception handling with `handle_item_use`, update dependencies in `adventure.py`, and add `setup_game` for cleaner initialization.
- 2025-06-18 - [8d971a6](https://github.com/Kingly77/VentureTextAdventure/commit/8d971a6) - Add item usage handlers: centralize exception handling for inventory, spells, and items across hero and room interactions, expand `adventure.py` with item-based commands, and improve item usage flow with contextual handling.
- 2025-06-18 - [17b5d20](https://github.com/Kingly77/VentureTextAdventure/commit/17b5d20) - Enhance RPG elements: introduce max health and max mana mechanics, implement health/mana capping on updates, add setters/getters, improve room navigation with new helper methods, and establish initial adventure flow in `adventure.py`.
- 2025-06-18 - [4d73964](https://github.com/Kingly77/VentureTextAdventure/commit/4d73964) - Introduce room connections: Add `exits_to` property to `Room` class, enable bi-directional navigation between rooms, and update `main.py` to demonstrate new mechanics.
- 2025-06-18 - [1fda76f](https://github.com/Kingly77/VentureTextAdventure/commit/1fda76f) - Enhance room mechanics: introduce `RoomEffect` system for dynamic descriptions and behaviors, refactor `Room` class methods, and add `DarkCaveLightingEffect`.
- 2025-06-18 - [3f4dc70](https://github.com/Kingly77/VentureTextAdventure/commit/3f4dc70) - Refactor inventory system: extract `Item` and `Inventory` into dedicated modules, improve organization, and enhance error handling.
- 2025-06-18 - [0df9064](https://github.com/Kingly77/VentureTextAdventure/commit/0df9064) - Split Main many ways
- 2025-06-18 - [4322623](https://github.com/Kingly77/VentureTextAdventure/commit/4322623) - Add project configuration files for IDE and package dependencies
- 2025-06-18 - [ead88cc](https://github.com/Kingly77/VentureTextAdventure/commit/ead88cc) - Enhance RPG mechanics: implement specialized exceptions for inventory and spells, refactor character hierarchy, improve error handling, and add new features for inventory management and combat resolution.
- 2025-06-18 - [27818ba](https://github.com/Kingly77/VentureTextAdventure/commit/27818ba) - Refactor RPG core: improve abstractions, type safety, and functionality for spells, items, inventory, and combat mechanics.
- 2025-06-18 - [e728210](https://github.com/Kingly77/VentureTextAdventure/commit/e728210) - Initialize project with core structure, IDE configurations, and a basic RPG game implementation.
