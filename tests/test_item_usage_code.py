import pytest
from unittest.mock import patch

from game.game_world_initializer import setup_game
from commands.command import use_command, go_command


@pytest.fixture
def world():
    hero, start_room = setup_game()
    return hero, start_room


def test_use_room_item_on_object_unlocks_foyer(world):
    hero, start = world
    # Move to the Manor where the sword is and the door object exists
    manor = start.exits_to["east"]
    foyer = manor.exits_to["north"]

    # Precondition: foyer is locked and sword is in the room (not in inventory)
    assert foyer.is_locked is True
    assert manor.inventory.has_component("sword")
    assert not hero.inventory.has_component("sword")

    with patch("builtins.print") as mock_print:
        # Use the sword in the room on the door
        use_command("use", "sword on door", hero, manor)

        # Verify the success message was printed (coming from DoorEffectExpanded)
        assert any(
            "bash the door open" in str(args).lower()
            for args, _ in mock_print.call_args_list
        ), "Expected door bashing message to be printed"

    # The foyer should now be unlocked due to the triggered event
    assert foyer.is_locked is False


def test_use_room_item_in_room_context_lights_torch(world):
    hero, start = world
    # Move to the Dark Cave Entrance where a torch is present in the room inventory
    dark_cave = start.exits_to["north"]

    # Precondition: torch is in the room inventory and not with the hero
    assert dark_cave.inventory.has_component("torch")
    assert not hero.inventory.has_component("torch")

    with patch("builtins.print") as mock_print:
        use_command("use", "torch on room", hero, dark_cave)

        # DarkCaveLightingEffect should print a message about lighting the torch
        assert any(
            "lights the torch" in str(args).lower()
            for args, _ in mock_print.call_args_list
        ), "Expected torch lighting message to be printed"
