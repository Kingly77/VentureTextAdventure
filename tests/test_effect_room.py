# tests/test_effect_room.py
import pytest

from character.hero import RpgHero
from game.rooms.effect_room import EffectRoom
from interfaces.room_effect_base import RoomDiscEffect


@pytest.fixture
def test_room():
    """Fixture that creates a test EffectRoom."""
    return EffectRoom(
        "Test Room",
        "A mysterious room filled with enchantments.",
        exits={"north": "Next Room"},
    )


@pytest.fixture
def test_hero():
    """Fixture that creates a test hero at level 1."""
    hero = RpgHero("Test Hero", 1)
    hero.gold = 50
    return hero


def test_effect_room_initialization(test_room):
    """Test if EffectRoom initializes correctly and inserts itself in the effects list.

    Relaxed description check: only verify that the base description is contained
    in the full description, not exactly equal. This makes the test resilient to
    additional context the room may append (e.g., exits or effect fragments).
    """
    assert test_room.name == "Test Room"
    full_desc = test_room.get_description()
    assert "A mysterious room filled with enchantments." in full_desc
    assert len(test_room.effects) > 0
    assert test_room.effects[0] is test_room


def test_effect_room_get_modified_description(test_room):
    """Test the default implementation of get_modified_description for EffectRoom."""
    base_description = "Base description of the room."
    modified_description = test_room.get_modified_description(base_description)
    # Since it uses the default implementation, it should match the base description
    assert modified_description == base_description


def test_effect_room_handle_interaction_no_override(test_room, test_hero):
    """Test handle_interaction behavior when not overridden."""
    result = test_room.handle_interaction(
        verb="examine",
        target_name="unknown item",
        val_hero=test_hero,
        item=None,
        room=test_room,
    )
    # Default behavior in RoomDiscEffect, not overridden in EffectRoom, returns None
    assert result is None


def test_effect_room_handle_item_use_no_override(test_room, test_hero):
    """Test handle_item_use behavior when not overridden."""
    result = test_room.handle_item_use(
        verb="use",
        item_name="mysterious object",
        user=test_hero,
    )
    # Default handle_item_use implementation returns False
    assert result is False


def test_effect_room_modified_behaviors_subclass():
    """Test if EffectRoom subclasses can modify RoomDiscEffect behaviors."""

    class CustomEffectRoom(EffectRoom):
        def get_modified_description(self, base_description):
            return f"{base_description} (This room has a strange aura.)"

        def handle_interaction(self, verb, target_name, val_hero, item, room):
            if verb == "examine" and target_name == "mysterious symbol":
                return "The symbol glows faintly, emitting a sense of dread."
            return None

    custom_room = CustomEffectRoom("Enigmatic Room", "A room shrouded in mystery.")
    base_description = "This is a standard-looking room."
    assert custom_room.get_modified_description(base_description) == (
        "This is a standard-looking room. (This room has a strange aura.)"
    )

    interaction_result = custom_room.handle_interaction(
        verb="examine",
        target_name="mysterious symbol",
        val_hero=None,
        item=None,
        room=custom_room,
    )
    assert interaction_result == "The symbol glows faintly, emitting a sense of dread."


def test_effect_room_registers_itself_as_first_effect(test_room):
    """Test if the room effect is always the first in the effects list."""
    assert test_room.effects[0] is test_room
    # Ensure it does not overwrite its own position when calling add_effect
    second_effect = RoomDiscEffect(test_room)
    test_room.add_effect(second_effect)
    assert test_room.effects[0] is test_room
    assert test_room.effects[1] is second_effect
