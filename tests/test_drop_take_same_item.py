import pytest

from game.effects.item_effects.base import Effect
from game.items import Item
from game.room import Room
from game.rpg_adventure_game import Game
from character.hero import RpgHero


@pytest.fixture
def hero():
    h = RpgHero("SameItemTester", 1)
    h.gold = 0
    return h


@pytest.fixture
def room():
    return Room("Same Item Room", "Room for same-item tests")


@pytest.fixture
def game(hero, room):
    return Game(hero, room)


def _assert_same_item_props(a: Item, b: Item):
    assert a is not None and b is not None
    assert a.name == b.name
    assert a.cost == b.cost
    assert a.quantity == b.quantity
    assert a.is_usable == b.is_usable
    assert a.effect_type == b.effect_type
    # assert a.effect_value == b.effect_value
    assert a.is_consumable == b.is_consumable
    assert getattr(a, "is_equipment", False) == getattr(b, "is_equipment", False)
    assert set(a.tags or []) == set(b.tags or [])
    assert a.effects == b.effects


def _clone_item(src: Item) -> Item:
    return Item(
        name=src.name,
        cost=src.cost,
        is_usable=src.is_usable,
        effect=src.effect_type,
        # effect_value=src.effect_value,
        is_consumable=src.is_consumable,
        is_equipment=getattr(src, "is_equipment", False),
        tags=set(src.tags or []),
        quantity=src.quantity,
        effects=src.effects,
    )


def test_drop_then_take_preserves_item_properties(game: Game):
    # Arrange: put a rich item in hero inventory
    amulet = Item(
        name="amulet",
        cost=7,
        is_usable=True,
        effect=Effect.HEAL,
        effect_value=3,
        is_consumable=False,
        is_equipment=True,
        tags={"shiny", "quest"},
    )
    game.hero.inventory.add_item(amulet)

    # Drop it into the room
    game.parse_and_execute("drop amulet")

    # Capture the item as it exists in the room right after dropping
    assert game.current_room.inventory.has_component("amulet")
    room_item_after_drop = game.current_room.inventory["amulet"]
    # Snapshot the dropped item properties before any later mutations
    room_item_snapshot = _clone_item(room_item_after_drop)

    # Now take it back
    game.parse_and_execute("take amulet")

    # Capture the item now in hero inventory
    assert game.hero.inventory.has_component("amulet")
    hero_item_after_take = game.hero.inventory["amulet"]

    # Ensure the item picked up matches the one that was dropped (same properties)
    _assert_same_item_props(hero_item_after_take, room_item_snapshot)


def test_take_then_drop_preserves_item_properties(game: Game):
    # Arrange: put a rich item in the room first
    potion = Item(
        name="potion",
        cost=5,
        is_usable=True,
        effect=Effect.HEAL,
        effect_value=10,
        is_consumable=True,
        is_equipment=False,
        tags={"alchemical", "liquid"},
    )
    game.current_room.add_item(potion)

    # Take it into hero inventory
    game.parse_and_execute("take potion")

    # Capture the item as it exists in hero inventory right after taking
    assert game.hero.inventory.has_component("potion")
    hero_item_after_take = game.hero.inventory["potion"]
    # Snapshot the taken item properties before any later mutations
    hero_item_snapshot = _clone_item(hero_item_after_take)

    # Drop it back to the room
    game.parse_and_execute("drop potion")

    # Capture the item as it exists in the room after dropping
    assert game.current_room.inventory.has_component("potion")
    room_item_after_drop = game.current_room.inventory["potion"]

    # Ensure the item dropped matches the one that was picked up (same properties)
    _assert_same_item_props(room_item_after_drop, hero_item_snapshot)
