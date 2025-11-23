"""
Clean command engine using the unified CommandRequest/CommandContext system.
"""

from __future__ import annotations

from typing import List, Tuple, Optional
import io
import contextlib

from commands.command_reg import (
    CommandRegistry,
    CommandRequest,
    CommandContext,
    UseTarget,
    TargetKind,
)
from commands.command import (
    handle_help,
    handle_look,
    handle_status,
    handle_inventory,
    handle_take,
    handle_drop,
    handle_examine,
    handle_use,
    handle_equip,
    handle_go,
    handle_attack,
    handle_cast,
    handle_talk,
    handle_quit,
    handle_debug,
)
from game.display import display


def parse_command_line(line: str) -> List[Tuple[str, str]]:
    """
    Parse a command line into action/argument pairs.

    Supports chaining commands with " and ":
        "take sword and examine sword" -> [("take", "sword"), ("examine", "sword")]

    Returns:
        List of (action, argument) tuples
    """
    parts = [p.strip() for p in line.strip().lower().split(" and ") if p.strip()]
    pairs: List[Tuple[str, str]] = []

    for part in parts:
        if " " in part:
            action, arg = part.split(" ", 1)
            pairs.append((action, arg.strip()))
        else:
            pairs.append((part, ""))

    return pairs


def maybe_gag(pairs: List[Tuple[str, str]]) -> Optional[str]:
    """
    Special case: if someone does "take X and drop X", be funny about it.

    Returns:
        A humorous message if the gag applies, None otherwise
    """
    if len(pairs) == 2:
        (a1, x1), (a2, x2) = pairs
        if a1 == "take" and a2 == "drop" and x1 and x1 == x2:
            return f"You picked up and dropped the {x1}. Why?"
    return None


def register_default_commands(registry: CommandRegistry, game: "Game") -> None:
    """Register all standard game commands with the registry."""

    # Information commands
    registry.register("help", handle_help, "Show this help message", aliases=["?"])
    registry.register("look", handle_look, "Look around the room")
    registry.register(
        "status", handle_status, "Check your character status", aliases=["stats"]
    )
    registry.register(
        "inventory", handle_inventory, "Show your inventory", aliases=["inv", "i"]
    )

    # Inventory commands (wrapped to invoke adapter hook for tests)
    registry.register("take", handle_take, "Pick up an item", aliases=["get", "grab"])
    registry.register("drop", handle_drop, "Drop an item from your inventory")
    registry.register(
        "examine", handle_examine, "Examine an item in detail", aliases=["inspect"]
    )

    # Item usage (wrapped for adapter hook)
    registry.register(
        "use", handle_use, "Use an item (syntax: use <item> [on <target>])"
    )
    registry.register("equip", handle_equip, "Equip a weapon", aliases=["wield"])

    # Movement (wrapped for adapter hook)
    registry.register(
        "go",
        handle_go,
        "Move in a direction (north/south/east/west/back)",
        aliases=["move"],
    )

    # Combat
    registry.register("attack", handle_attack, "Attack the current enemy [with weapon]")
    registry.register("cast", handle_cast, "Cast a spell on the current enemy")

    # Interaction
    registry.register(
        "talk", handle_talk, "Talk to someone or something", aliases=["speak"]
    )

    # System
    registry.register("quit", handle_quit, "Exit the game", aliases=["exit"])
    registry.register(
        "debug", handle_debug, "Debug commands (heal, mana, xp, gold, hurt)"
    )
