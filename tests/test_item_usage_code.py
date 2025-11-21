import pytest
from types import SimpleNamespace
from unittest.mock import patch

from commands.command_reg import CommandRequest, CommandContext
from game.game_world_initializer import setup_game
from commands.command import handle_use, handle_go


@pytest.fixture
def world():
    hero, start_room = setup_game()
    return hero, start_room


def make_ctx(hero, room):
    # Minimal game stub; handlers under test don't use game directly
    game = SimpleNamespace(registry=None)
    return CommandContext(game=game, hero=hero, room=room)


def build_req(action: str, arg: str) -> CommandRequest:
    raw = f"{action} {arg}".strip()
    tokens = [t for t in arg.lower().split() if t] if arg else []
    return CommandRequest(raw=raw, action=action.lower(), arg=arg.lower(), tokens=tokens)


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
        req = build_req("use", "sword on door")
        ctx = make_ctx(hero, manor)
        handle_use(req, ctx)

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
        req = build_req("use", "torch on room")
        ctx = make_ctx(hero, dark_cave)
        handle_use(req, ctx)

        # DarkCaveLightingEffect should print a message about lighting the torch
        assert any(
            "lights the torch" in str(args).lower()
            for args, _ in mock_print.call_args_list
        ), "Expected torch lighting message to be printed"
