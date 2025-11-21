import pytest
from types import SimpleNamespace
from unittest.mock import patch

from commands.command_reg import CommandRequest, CommandContext
from game.game_world_initializer import setup_game
from commands.command import handle_use as use_command
from game.items import Item
from game.effects.item_effects.base import Effect


@pytest.fixture
def world():
    hero, start_room = setup_game()
    return hero, start_room


def make_ctx(hero, room):
    game = SimpleNamespace(registry=None)
    return CommandContext(game=game, hero=hero, room=room)


def build_req(action: str, arg: str) -> CommandRequest:
    raw = f"{action} {arg}".strip()
    tokens = [t for t in arg.lower().split() if t] if arg else []
    return CommandRequest(raw=raw, action=action.lower(), arg=arg.lower(), tokens=tokens)


def test_use_item_on_self_heals_and_consumes(world):
    hero, room = world

    # Ensure we can observe healing by lowering health first
    hero.take_damage(30)
    start_health = hero.health

    # Give the hero a healing potion
    potion = Item(
        name="health potion",
        cost=10,
        is_usable=True,
        effect=Effect.HEAL,
        effect_value=20,
        is_consumable=True,
    )
    hero.inventory.add_item(potion)

    assert hero.inventory.has_component("health potion")

    with patch("builtins.print") as mock_print:
        # Use item on self via the use command
        req = build_req("use", "health potion on self")
        ctx = make_ctx(hero, room)
        use_command(req, ctx)

        # Verify a usage message was printed by ItemUsageMix
        assert any(
            "used health potion on" in str(args).lower()
            for args, _ in mock_print.call_args_list
        ), "Expected a usage message to be printed"

    # Health should have increased by up to 20 (clamped by max health handled in heal)
    assert hero.health > start_health

    # Since it is consumable, it should be removed from inventory
    assert not hero.inventory.has_component("health potion")


def test_use_item_on_named_hero_variant(world):
    hero, room = world

    # Lower health to observe healing
    hero.take_damage(10)
    start_health = hero.health

    # Another potion
    potion = Item(
        name="minor potion",
        cost=5,
        is_usable=True,
        effect=Effect.HEAL,
        effect_value=5,
        is_consumable=True,
    )
    hero.inventory.add_item(potion)

    # Use the variant that targets by hero name
    req = build_req("use", f"minor potion on {hero.name}")
    ctx = make_ctx(hero, room)
    use_command(req, ctx)

    assert hero.health > start_health
    assert not hero.inventory.has_component("minor potion")
