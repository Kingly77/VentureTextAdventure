import pytest
from character.hero import RpgHero
from components.core_components import Health, Effect
from game.items import Item
from game.room import Room


@pytest.fixture
def test_hero():
    """Fixture that creates a test hero at level 1."""
    hero = RpgHero("Test Hero", 1)
    # Give the hero some starting gold
    hero.gold = 50
    return hero


@pytest.fixture
def test_items():
    """Fixture that creates some test items."""
    return {
        "health_potion": Item(
            "health potion",
            10,
            True,
            is_consumable=True,
            effect=Effect.HEAL,
            effect_value=20,
        ),
        "sword": Item(
            "sword", 25, True, is_equipment=True, effect=Effect.DAMAGE, effect_value=15
        ),
        "key": Item("rusty key", 0, False),
        "treasure": Item("gold coin", 1, False, quantity=10),
    }


@pytest.fixture
def two_room_world(test_items):
    """
    Fixture that creates a simple two-room world for testing.

    Room Layout:
    [Starting Room] <---> [Treasure Room]
    """
    # Create the rooms
    starting_room = Room("Starting Room", "A plain room with stone walls.")
    treasure_room = Room("Treasure Room", "A room filled with valuable treasures.")

    # Connect the rooms
    starting_room.add_exit("east", treasure_room)
    treasure_room.add_exit("west", starting_room)

    # Add items to the rooms
    starting_room.add_item(test_items["health_potion"])
    starting_room.add_item(test_items["sword"])
    treasure_room.add_item(test_items["treasure"])

    # Register rooms in a registry
    room_registry = {"starting_room": starting_room, "treasure_room": treasure_room}

    return {
        "starting_room": starting_room,
        "treasure_room": treasure_room,
        "registry": room_registry,
    }


@pytest.fixture
def game_setup(test_hero, two_room_world):
    """
    Fixture that sets up a complete game environment for testing.

    Returns:
        tuple: (hero, current_room, room_registry)
    """
    # Setup the hero's room registry
    test_hero.room_registry = two_room_world["registry"]

    # Return the hero and starting room
    return (test_hero, two_room_world["starting_room"])


def test_basic_setup(game_setup):
    """Test that the basic game setup works correctly."""
    hero, current_room = game_setup

    # Verify hero setup
    assert hero.name == "Test Hero"
    assert hero.level == 1
    assert hero.gold == 50

    # Verify room setup
    assert current_room.name == "Starting Room"
    assert "east" in current_room.exits_to
    assert current_room.exits_to["east"].name == "Treasure Room"

    # Test room navigation
    next_room = current_room.exits_to["east"]
    assert next_room.name == "Treasure Room"
    assert "west" in next_room.exits_to
    assert next_room.exits_to["west"].name == "Starting Room"


def test_item_pickup(game_setup, test_items):
    """Test that the hero can pick up items from a room."""
    hero, current_room = game_setup

    # Check initial inventory
    initial_item_count = len(hero.inventory.items)

    # Verify room has the health potion
    room_items = [item for item in current_room.inventory.items]
    assert "health potion" in room_items

    # Simulate picking up the potion
    potion = test_items["health_potion"]
    hero.inventory.add_item(potion)
    current_room.remove_item(potion.name)

    # Verify hero inventory has the potion now
    assert "health potion" in hero.inventory.items
    assert len(hero.inventory.items) == initial_item_count + 1

    # Verify room no longer has the potion
    room_items = [item for item in current_room.inventory.items]
    assert "health potion" not in room_items


def test_item_drop(game_setup, test_items):
    """Test that the hero can drop items into a room."""
    hero, current_room = game_setup

    # Add item to hero's inventory
    sword = test_items["sword"]
    key = test_items["key"]
    hero.inventory.add_item(key)

    # Verify initial states
    assert "rusty key" in hero.inventory.items
    initial_room_items = len(current_room.inventory.items)

    # Drop the item
    hero.inventory.remove_item("rusty key")
    current_room.add_item(key)

    # Verify final states
    assert "rusty key" not in hero.inventory.items
    assert len(current_room.inventory.items) == initial_room_items + 1
    assert any(item == "rusty key" for item in current_room.inventory.items)


def test_drop_multiple_items(game_setup, test_items):
    """Test dropping items with quantities."""
    hero, current_room = game_setup

    # Add treasure with quantity to hero's inventory
    treasure = test_items["treasure"]
    hero.inventory.add_item(treasure)

    # Drop part of the stack
    drop_quantity = 5
    dropped_item = hero.inventory.remove_item("gold coin", drop_quantity)
    current_room.add_item(dropped_item)

    # Verify quantities
    assert hero.inventory["gold coin"].quantity == 5  # Started with 10
    room_treasure = next(
        value
        for key, value in current_room.inventory.items.items()
        if key == "gold coin"
    )
    assert room_treasure.quantity == 5


def test_drop_nonexistent_item(game_setup):
    """Test dropping an item that doesn't exist in inventory."""
    hero, current_room = game_setup

    # Attempt to drop non-existent item
    with pytest.raises(Exception):
        hero.inventory.remove_item("nonexistent item")
