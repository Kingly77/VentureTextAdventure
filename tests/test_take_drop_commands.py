import pytest
from character.hero import RpgHero
from game.items import Item
from game.room import Room
from game.rpg_adventure_game import Game


@pytest.fixture
def hero():
    h = RpgHero("CmdTester", 1)
    h.gold = 0
    return h


@pytest.fixture
def room():
    return Room("Cmd Test Room", "Room for command tests")


@pytest.fixture
def game(hero, room):
    # Fresh game instance per test
    return Game(hero, room)


def test_take_command_moves_item_to_inventory(game: Game):
    # Arrange: put an item in the room
    key = Item("key", 1, True)
    game.current_room.add_item(key)

    # Sanity: room has key, hero does not
    assert game.current_room.inventory.has_component("key")
    assert not game.hero.inventory.has_component("key")

    # Act: take the key via command parser/dispatcher
    game.parse_and_execute("take key")

    # Assert: key moved to hero's inventory
    assert game.hero.inventory.has_component("key")
    assert not game.current_room.inventory.has_component("key")


def test_drop_command_moves_item_to_room(game: Game):
    # Arrange: put an item in hero inventory
    key = Item("key", 1, True)
    game.hero.inventory.add_item(key)

    # Sanity: hero has key, room does not
    assert game.hero.inventory.has_component("key")
    assert not game.current_room.inventory.has_component("key")

    # Act: drop the key via command parser/dispatcher
    game.parse_and_execute("drop key")

    # Assert: key moved to room inventory
    assert not game.hero.inventory.has_component("key")
    assert game.current_room.inventory.has_component("key")
