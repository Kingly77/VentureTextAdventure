import pytest
from unittest.mock import MagicMock

import commands.command_reg
import commands.engine as eng


def test_parse_command_line_and_gag_basic():

    # f"You picked up and dropped the {x1}. Why?"
    # Single command
    pairs = eng.parse_command_line("Look")
    assert pairs == [("look", "")]

    # Command with arg
    pairs = eng.parse_command_line("take Key")
    assert pairs == [("take", "key")]

    # Chained commands
    pairs = eng.parse_command_line("go north and look and take coin")
    assert pairs == [("go", "north"), ("look", ""), ("take", "coin")]

    # Gag triggers for take X and drop X
    gag = eng.maybe_gag([("take", "coin"), ("drop", "coin")])
    assert gag == f"You picked up and dropped the coin. Why?"

    # Gag does not trigger for different items
    assert eng.maybe_gag([("take", "coin"), ("drop", "key")]) is None


def test_command_registry_register_resolve_help():
    registry = commands.command_reg.CommandRegistry()

    called = {}

    def handler(
        req: commands.command_reg.CommandRequest,
        ctx: commands.command_reg.CommandContext,
    ):
        called["req"] = req
        called["ctx"] = ctx

    registry.register("ping", handler, help="Ping command", aliases=["pong", "p"])

    # Resolve canonical and aliases
    d0 = registry.resolve("ping")
    d1 = registry.resolve("pong")
    d2 = registry.resolve("p")
    assert d0 is d1 is d2
    assert d0 is not None and d0.name == "ping"

    # Help text contains aliases and description
    help_text = registry.help_text()
    assert "Available commands:" in help_text
    assert "ping (aliases: pong, p) - Ping command" in help_text

    # Execute handler through def
    ctx = commands.command_reg.CommandContext(
        game=MagicMock(), hero=MagicMock(), room=MagicMock()
    )
    req = commands.command_reg.CommandRequest(
        raw="ping server", action="ping", arg="server", tokens=["server"]
    )
    d0.handler(req, ctx)
    assert called["req"].arg == "server"
    assert called["ctx"].hero is ctx.hero


def test_registry_handlers_resolve_and_invoke():
    """Ensure handlers registered by register_default_commands are callable via registry."""
    registry = commands.command_reg.CommandRegistry()
    dummy_game = MagicMock()
    eng.register_default_commands(registry, dummy_game)

    # Build a context and simple request factory
    hero = MagicMock()
    room = MagicMock()
    ctx = commands.command_reg.CommandContext(game=dummy_game, hero=hero, room=room)

    def make_req(name, arg):
        return commands.command_reg.CommandRequest(
            raw=f"{name} {arg}".strip(),
            action=name,
            arg=arg,
            tokens=arg.split() if arg else [],
        )

    # Ensure key commands resolve and their handlers are callable without raising
    for name, arg in [
        ("look", ""),
        ("status", ""),
        ("inventory", ""),
        ("take", "coin"),
        ("drop", "coin"),
        ("examine", "torch"),
        ("use", "potion"),
        ("equip", "sword"),
        ("go", "north"),
        ("attack", ""),
        ("cast", ""),
        ("talk", ""),
    ]:
        d = registry.resolve(name)
        assert d is not None and d.name
        # Handlers may print or perform actions on ctx, ensure no exception
        d.handler(make_req(name, arg), ctx)


def test_register_default_commands_aliases_present():
    registry = commands.command_reg.CommandRegistry()
    eng.register_default_commands(registry, MagicMock())

    # Aliases map to canonical names
    assert registry.resolve("get").name == "take"
    assert registry.resolve("grab").name == "take"
    assert registry.resolve("move").name == "go"
    assert registry.resolve("exit").name == "quit"
    assert registry.resolve("?").name == "help"

    # Help text includes multiple commands
    help_text = registry.help_text()
    assert "look - Look around the room" in help_text
    assert "take (aliases: get, grab) - Pick up an item" in help_text
