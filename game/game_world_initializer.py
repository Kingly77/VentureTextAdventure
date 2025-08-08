import functools
import importlib
import logging

from character.enemy import Goblin
from character.hero import RpgHero
from components.core_components import Effect
from game.items import Item
from game.quest import Quest, Objective
from game.room import Room, RoomObject
from game.room_effects import DarkCaveLightingEffect
from game.shop_effect import ShopEffect
from game.underlings.events import Events as Event, EventNotFoundError
from game.underlings.leveling_system import LevelingSystem
from game.underlings.questing_system import QuestingSystem
from game.util import handle_inventory_operation

# Game configuration constants
HERO_NAME = "Aidan"
HERO_LEVEL = 1
STARTING_GOLD = 10
SHOP_KEEPER_NAME = "Maribel Tinkertop"


def _import_more():
    ev = importlib.import_module("game.events")
    ev.import_events()


def _create_hero() -> RpgHero:
    """Create and initialize the hero character with starting inventory and quests."""
    hero = RpgHero(HERO_NAME, HERO_LEVEL)

    # Add a starting quest
    goblin_ear_quest = Quest(
        "goblin ear",
        "Collect the goblin ear to defeat the goblin foe.",
        100,
        objective=Objective("collect", "goblin ear", 1),
    )

    # foo_quest = Quest(
    #     "foo",
    #     "Collect the foo to defeat the foo foe.",
    #     reward=1,
    #     objective=Objective("collect", "foo", 1),
    # )

    hero.quest_log.add_quest(goblin_ear_quest.id, goblin_ear_quest)
    # hero.quest_log.add_quest(foo_quest.id, foo_quest)

    # Add starting inventory
    hero.inventory.add_item(Item("gold", 1, False, quantity=STARTING_GOLD))

    print(f"Welcome, {hero.name}, to the world of KingBase!")
    return hero


def _create_rooms() -> tuple[Room, Room, Room, Room, Room, Room]:
    """Create all game rooms and set up their basic properties."""
    forest_clearing = Room(
        "Forest Clearing",
        "A peaceful clearing in a dense forest. Sunlight filters through the leaves, and a stone table stands before you.",
    )
    manor = Room(
        "Manor",
        "A small manor with a large garden. The air is warm and the sun shines brightly.",
    )
    foyer = Room(
        "Foyer",
        "A cozy foyer with a large table and chair. There is a large glass door to the east.",
    )
    dark_cave_entrance = Room(
        "Dark Cave Entrance",
        "The air grows cold as you stand at the mouth of a dark, damp cave.",
    )
    goblins_lair = Room(
        "Goblin's Lair",
        "A small, squalid cave reeking of unwashed goblin. Bones litter the floor.",
    )
    shack_shop = Room(
        "Shack Shop",
        "A small, cozy shack with a large table and chair. There is a large glass door to the east.",
    )

    # Set room properties
    foyer.is_locked = True

    return forest_clearing, manor, foyer, dark_cave_entrance, goblins_lair, shack_shop


def _link_rooms(
    forest_clearing: Room,
    manor: Room,
    foyer: Room,
    dark_cave_entrance: Room,
    goblins_lair: Room,
    shack_shop: Room,
) -> None:
    """Connect all rooms with their directional links."""
    forest_clearing.link_rooms("north", dark_cave_entrance, "south")
    forest_clearing.link_rooms("east", manor, "west")
    forest_clearing.link_rooms("south", shack_shop, "north")
    dark_cave_entrance.link_rooms("east", goblins_lair, "west")
    manor.link_rooms("north", foyer, "south")


def _create_torch_interaction(forest_table: RoomObject) -> callable:
    """Create the torch interaction function for the forest table."""

    def torch_on_table(val_hero, item: Item, *args):
        if forest_table.has_tag("lit"):
            return "The table is already lit."

        if not item.has_tag("fire") and not forest_table.has_tag("lit"):
            return "You need a torch to properly light the table's fire pit."

        forest_table.change_description(
            "A massive stone table dominates the area, with a small wooden chair on its surface. "
            "The fire pit in the center now blazes with dancing flames, casting flickering shadows across the stone."
        )
        try:
            Event.trigger_event("torch_on_table")
        except ValueError:
            logging.debug("Error: torch_on_table event not found.")

        forest_table.add_tag("lit")
        return (
            "You touch your torch to the prepared wood. The kindling catches immediately, "
            "and flames leap upward, illuminating the area with a warm, golden glow."
        )

    return torch_on_table


def _create_door_interaction(foyer: Room, manor_door: RoomObject) -> callable:
    """Create the door interaction function for the manor door."""

    def use_sword_on_door(val_hero: RpgHero, item: Item, *args):
        if not item.has_tag("weapon"):
            return "You do not have a weapon to use on the door."

        if foyer.is_locked:
            try:
                Event.trigger_event("unlock_foyer")
                return (
                    f"You use your {item.name} to bash the door open! "
                    f"The door swings wide and a giant bashing sound is heard."
                )
            except EventNotFoundError as e:
                return f"Error: {str(e)}"
        else:
            return "Door already unlocked and open."

    return use_sword_on_door


def _setup_forest_table(forest_clearing: Room) -> None:
    """Create and configure the forest table with its interactions."""
    forest_table = RoomObject(
        "table",
        "A massive stone table dominates the area, with a small wooden chair peculiarly placed on its surface. "
        "In the center of the table, a carefully constructed fire pit contains a neat pile of firewood, ready to be lit.",
    )

    torch_interaction = _create_torch_interaction(forest_table)
    forest_table.add_interaction("use", torch_interaction)
    forest_clearing.add_object(forest_table)


def _setup_manor_door(manor: Room, foyer: Room) -> None:
    """Create and configure the manor door with its interactions."""
    manor_door = RoomObject(
        "door",
        "A sturdy wooden door with a heavy lock. It appears to be the entrance to the Foyer.",
    )

    door_interaction = _create_door_interaction(foyer, manor_door)
    manor_door.add_interaction("use", door_interaction)
    manor.add_object(manor_door)

    # Set up the door unlock event
    Event.add_event(
        "unlock_foyer",
        functools.partial(
            manor_door.change_description,
            "The door is wide open, It appears to be the entrance to the Foyer.",
        ),
        True,
    )


def _setup_shop(shack_shop: Room) -> None:
    """Configure the shop with its effect and inventory."""
    shack_shop.add_effect(ShopEffect(shack_shop, SHOP_KEEPER_NAME))
    handle_inventory_operation(shack_shop.add_item, Item("marble ball", 1, False))
    handle_inventory_operation(shack_shop.add_item, Item("10 foot pole", 3, False))


def _populate_room_items(
    forest_clearing: Room, manor: Room, dark_cave_entrance: Room, goblins_lair: Room
) -> None:
    """Add items to each room."""
    manor.add_item(
        Item("sword", 10, True, Effect.DAMAGE, 10, is_consumable=False, tags=["weapon"])
    )
    forest_clearing.add_item(
        Item("health potion", 10, True, Effect.HEAL, 20, is_consumable=True)
    )
    dark_cave_entrance.add_item(
        Item("torch", 5, True, is_consumable=False, tags=["fire"])
    )  # Essential for the cave!
    goblins_lair.add_item(Item("shiny coin", 1, False, is_consumable=True))
    goblins_lair.add_item(
        Item("rusty dagger", 5, True, Effect.DAMAGE, 5, is_consumable=False)
    )


def _setup_cave_lighting(dark_cave_entrance: Room) -> None:
    """Configure the dark cave lighting effect."""
    dark_cave_effect = DarkCaveLightingEffect(dark_cave_entrance)
    dark_cave_entrance.add_effect(dark_cave_effect)


def _setup_goblin_enemy(goblins_lair: Room) -> None:
    """Create and configure the goblin enemy."""
    goblin_foe = Goblin("Goblin Grunt", 1)
    goblin_foe.reward = Item("goblin ear", 1, False)
    goblin_foe.reward.quantity = 1
    goblins_lair.combatants = goblin_foe


def _setup_events(foyer: Room, **kwargs) -> None:
    """Set up game events."""
    Event.add_event("unlock_foyer", foyer.unlock, True)
    kwargs["ls"].setup_events()


def _initialize_game_world() -> tuple[RpgHero, Room]:
    """Initialize the complete game world with hero, rooms, and all game objects."""
    # Create a hero
    hero = _create_hero()
    ls = LevelingSystem()
    QuestingSystem()
    # Create rooms
    forest_clearing, manor, foyer, dark_cave_entrance, goblins_lair, shack_shop = (
        _create_rooms()
    )

    # Link rooms together
    _link_rooms(
        forest_clearing, manor, foyer, dark_cave_entrance, goblins_lair, shack_shop
    )

    # Set up events
    _setup_events(foyer, ls=ls)

    # Set up room objects and interactions
    _setup_forest_table(forest_clearing)
    _setup_manor_door(manor, foyer)

    # Set up shop
    _setup_shop(shack_shop)

    # Set up room effects
    _setup_cave_lighting(dark_cave_entrance)

    # Populate rooms with items
    _populate_room_items(forest_clearing, manor, dark_cave_entrance, goblins_lair)

    # Set up enemies
    _setup_goblin_enemy(goblins_lair)

    return hero, forest_clearing


def setup_game() -> tuple[RpgHero, Room]:
    """Set up and return the complete game world."""
    # _import_more()

    hero, forest_clearing = _initialize_game_world()
    return hero, forest_clearing
