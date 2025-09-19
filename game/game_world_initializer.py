import os

from character.hero import RpgHero
from game.room import Room
from game.underlings.leveling_system import LevelingSystem
from game.underlings.questing_system import QuestingSystem

HERO_NAME = "Aidan"
HERO_LEVEL = 1
STARTING_GOLD = 10
SHOP_KEEPER_NAME = "Maribel Tinkertop"


def setup_game(json_path: str | None = None) -> tuple[RpgHero, Room]:
    """Set up and return the complete game world.

    If json_path is provided, build the world from that JSON file instead of the default.
    If not provided, attempt to load the built-in default JSON world; if unavailable, fall back to code setup.
    """
    # _import_more()
    # Use default JSON world if no path provided
    if not json_path:
        default_path = os.path.join(
            os.path.dirname(__file__), "worlds", "default_world.json"
        )
        if os.path.exists(default_path):
            json_path = default_path

    if json_path:
        from game.json_loader import load_world_from_path

        rooms, start_key, hero_cfg = load_world_from_path(json_path)
        # Build the hero using config with sensible defaults
        name = hero_cfg.get("name", HERO_NAME)
        level = int(hero_cfg.get("level", HERO_LEVEL))
        hero = RpgHero(name, level)
        hero.gold = int(hero_cfg.get("gold", STARTING_GOLD))
        # Return the designated start room
        start_room = rooms[start_key]
        QuestingSystem()
        LevelingSystem()

        return hero, start_room

    raise ValueError("No JSON path provided.")
