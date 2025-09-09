import importlib

from character.enemy import Goblin
from character.hero import RpgHero
from components.core_components import Effect
from game.effects.locked_door_effect import LockedDoorEffect
from game.items import Item
from game.quest import Quest, Objective
from game.room import Room
from game.effects.room_effects import DarkCaveLightingEffect, NPCDialogEffect
from game.effects.shop_effect import ShopEffect
from game.effects.torch_effect import TorchEffect
from game.underlings.events import Events as Event
from game.underlings.leveling_system import LevelingSystem
from game.underlings.questing_system import QuestingSystem
from game.underlings.inventory_maybe import add_item as inv_add_item


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

    # Add starting inventory
    hero.gold = STARTING_GOLD

    print(f"Welcome, {hero.name}, to the world of KingBase!")
    return hero


def _create_rooms() -> dict[str, Room]:
    """Create all game rooms and set up their basic properties, returning a dict of rooms."""
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
    # New 5-room goblin dungeon (use inline link_to for clarity)
    dungeon_cell_1 = Room(
        "Goblin Dungeon - Cell 1",
        "A cramped stone cell with rusted bars. Scratches mark the walls.",
        link_to=[("west", goblins_lair, "east")],
    )
    dungeon_cell_2 = Room(
        "Goblin Dungeon - Cell 2",
        "The damp air smells of mold. You hear faint chittering ahead.",
        link_to=[("west", dungeon_cell_1, "east")],
    )
    dungeon_cell_3 = Room(
        "Goblin Dungeon - Cell 3",
        "Bones crunch underfoot. Shapes flit just out of sight.",
        link_to=[("west", dungeon_cell_2, "east")],
    )
    dungeon_cell_4 = Room(
        "Goblin Dungeon - Cell 4",
        "Water drips from the ceiling into a shallow, murky puddle.",
        link_to=[("west", dungeon_cell_3, "east")],
    )
    dungeon_cell_5 = Room(
        "Goblin Dungeon - Cell 5",
        "A wider chamber lit by a guttering torch. Something watches you.",
        link_to=[("west", dungeon_cell_4, "east")],
    )
    shack_shop = Room(
        "Shack Shop",
        "A small, cozy shack with a large table and chair. There is a large glass door to the east.",
    )
    village_square = Room(
        "Village Square",
        "A quaint village square with a stone well and a few benches. Villagers pass by, chatting quietly.",
    )

    # Set room properties
    foyer.is_locked = True

    # Build and return a dictionary of rooms for easier access by name
    return {
        "forest_clearing": forest_clearing,
        "manor": manor,
        "foyer": foyer,
        "dark_cave_entrance": dark_cave_entrance,
        "goblins_lair": goblins_lair,
        "dungeon_cell_1": dungeon_cell_1,
        "dungeon_cell_2": dungeon_cell_2,
        "dungeon_cell_3": dungeon_cell_3,
        "dungeon_cell_4": dungeon_cell_4,
        "dungeon_cell_5": dungeon_cell_5,
        "shack_shop": shack_shop,
        "village_square": village_square,
    }


def _link_rooms(rooms: dict[str, Room]) -> None:
    """Connect all rooms with their directional links using the provided rooms dict."""
    forest_clearing = rooms["forest_clearing"]
    manor = rooms["manor"]
    foyer = rooms["foyer"]
    dark_cave_entrance = rooms["dark_cave_entrance"]
    goblins_lair = rooms["goblins_lair"]
    shack_shop = rooms["shack_shop"]
    village_square = rooms["village_square"]

    # Preserve the exact same connections as before
    forest_clearing.link_rooms("north", dark_cave_entrance, "south")
    forest_clearing.link_rooms("east", manor, "west")
    forest_clearing.link_rooms("south", shack_shop, "north")
    forest_clearing.link_rooms("west", village_square, "east")
    dark_cave_entrance.link_rooms("east", goblins_lair, "west")
    manor.link_rooms("north", foyer, "south")

    # The dungeon chain is linked inline during room construction via link_to for clarity.


def _setup_forest_table(forest_clearing: Room) -> None:
    """Create and configure the forest table with its interactions."""
    forest_clearing.add_effect(TorchEffect(forest_clearing))


def _setup_manor_door(manor: Room, foyer: Room) -> None:
    """Create and configure the manor door with its interactions."""
    manor.add_effect(LockedDoorEffect(manor, foyer, door_name="door", unlock_event="unlock_foyer", allow_bash=True))


def _setup_shop(shack_shop: Room) -> None:
    """Configure the shop with its effect and inventory."""
    shack_shop.add_effect(ShopEffect(shack_shop, SHOP_KEEPER_NAME))
    inv_add_item(shack_shop, Item("marble ball", 1, False))
    inv_add_item(shack_shop, Item("10 foot pole", 3, False))


def _setup_village_npc(village_square: Room) -> None:
    """Place an NPC with a dialog tree in the Village Square and add a visible NPC reference."""

    # Prepare a quest to pass into the NPC dialog effect, making it generic
    def goblin_ear_quest_factory():
        return Quest(
            "goblin ear",
            "Collect the goblin ear to defeat the goblin foe.",
            100,
            objective=Objective("collect", "goblin ear", 1),
        )

    # Add interactive dialog effect
    village_square.add_effect(
        NPCDialogEffect(
            village_square,
            "Old Villager",
            "leans on a walking stick, ready to chat.",
            quest_factory=goblin_ear_quest_factory,
        )
    )

    # Also add a simple NPC reference so the description shows someone to talk to


def _setup_dungeon_end_npc(final_dungeon_room: Room) -> None:
    """Place an NPC at the end of the dungeon who offers a 'magic stick' quest."""

    def magic_stick_quest_factory():
        return Quest(
            "magic stick",
            "Retrieve the enchanted magic stick hidden deep in the goblin dungeon.",
            200,
            objective=Objective("collect", "magic stick", 1),
        )

    final_dungeon_room.add_effect(
        NPCDialogEffect(
            final_dungeon_room,
            "Dungeon Hermit",
            "whispers about an enchanted stick and offers you a quest.",
            quest_factory=magic_stick_quest_factory,
        )
    )


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
    forest_clearing.add_item(Item("stick", 1, False, is_consumable=False))

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


def _setup_dungeon_goblins(*rooms: Room) -> None:
    """Populate given rooms with goblins guarding the dungeon."""
    i = 1
    for room in rooms:
        gob = Goblin(f"Goblin Guard {i}", 1)
        gob.reward = Item("goblin ear", 1, False)
        gob.reward.quantity = 1
        room.combatants = gob
        i += 1


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
    # Create rooms as a dict
    rooms = _create_rooms()

    # Extract frequently used rooms for clarity
    forest_clearing = rooms["forest_clearing"]
    manor = rooms["manor"]
    foyer = rooms["foyer"]
    dark_cave_entrance = rooms["dark_cave_entrance"]
    goblins_lair = rooms["goblins_lair"]
    shack_shop = rooms["shack_shop"]
    village_square = rooms["village_square"]
    # Dungeon cells
    dungeon_cell_1 = rooms["dungeon_cell_1"]
    dungeon_cell_2 = rooms["dungeon_cell_2"]
    dungeon_cell_3 = rooms["dungeon_cell_3"]
    dungeon_cell_4 = rooms["dungeon_cell_4"]
    dungeon_cell_5 = rooms["dungeon_cell_5"]

    # Link rooms together
    _link_rooms(rooms)

    # Set up events
    _setup_events(foyer, ls=ls)

    # Set up room objects and interactions
    _setup_forest_table(forest_clearing)
    _setup_manor_door(manor, foyer)

    # Set up shop
    _setup_shop(shack_shop)

    # Set up room effects
    _setup_cave_lighting(dark_cave_entrance)

    # Set up the village NPC
    _setup_village_npc(village_square)

    # Populate rooms with items
    _populate_room_items(forest_clearing, manor, dark_cave_entrance, goblins_lair)

    # Set up enemies
    _setup_goblin_enemy(goblins_lair)
    _setup_dungeon_goblins(
        dungeon_cell_1,
        dungeon_cell_2,
        dungeon_cell_3,
        dungeon_cell_4,
        dungeon_cell_5,
    )

    # Place the quest item in the final dungeon room and set up the quest-giver NPC
    dungeon_cell_5.add_item(Item("magic stick", 1, False, is_consumable=False))
    _setup_dungeon_end_npc(dark_cave_entrance)

    return hero, forest_clearing


def setup_game() -> tuple[RpgHero, Room]:
    """Set up and return the complete game world."""
    # _import_more()

    hero, forest_clearing = _initialize_game_world()
    return hero, forest_clearing
