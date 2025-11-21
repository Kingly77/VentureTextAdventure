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
    registry.register(
        "take", _wrap_inventory, "Pick up an item", aliases=["get", "grab"]
    )
    registry.register("drop", _wrap_inventory, "Drop an item from your inventory")
    registry.register(
        "examine", _wrap_inventory, "Examine an item in detail", aliases=["inspect"]
    )

    # Item usage (wrapped for adapter hook)
    registry.register(
        "use", _wrap_use, "Use an item (syntax: use <item> [on <target>])"
    )
    registry.register("equip", handle_equip, "Equip a weapon", aliases=["wield"])

    # Movement (wrapped for adapter hook)
    registry.register(
        "go",
        _wrap_go,
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


# ---------------------------------------------------------------------------
# Backward-compatibility helpers for tests and legacy integrations
# ---------------------------------------------------------------------------


def _capture_display_and_stdout():
    """
    Internal context manager that captures all output written via the shared
    display object as well as plain print() calls to stdout. Returns a tuple
    of (context_manager, buffer) so that the caller can use it in a 'with' block
    and then read buffer.getvalue().
    """
    buf = io.StringIO()

    class _Ctx:
        def __enter__(self):
            # Save current display streams
            self._prev_out = display._out
            self._prev_err = display._err
            # Route display to our buffer
            display.set_streams(out=buf)
            # Redirect print() to the same buffer
            self._redir = contextlib.redirect_stdout(buf)
            self._redir.__enter__()
            return buf

        def __exit__(self, exc_type, exc, tb):
            # Restore stdout redirection
            try:
                self._redir.__exit__(exc_type, exc, tb)
            finally:
                # Restore display streams
                display.set_streams(out=self._prev_out, err=self._prev_err)

    return _Ctx(), buf


def execute_line(game: "Game", line: str) -> List[str]:
    """
    Execute a single command line against the provided game instance and
    return the emitted output as a list of lines. This is a thin wrapper
    around the Game.parse_and_execute method intended for tests.
    """
    ctx, buf = _capture_display_and_stdout()
    with ctx:
        try:
            game.parse_and_execute(line)
        except Exception as e:
            # Ensure exceptions surface as text for tests expecting messages
            print(f"Error: {e}")
    # Split while preserving non-empty diagnostics
    text = buf.getvalue()
    # Normalize line endings and strip trailing spaces per line
    lines = [ln.rstrip("\r") for ln in text.splitlines()]
    return lines


def parse_use_arg(arg: str, hero_name: str, room) -> UseTarget:
    """Legacy helper used by tests: parse a 'use' argument into a UseTarget.

    Examples:
      - "potion on self" -> SELF
      - "torch in room" -> ROOM
      - "key on door" -> OBJECT(name="door") if room.objects has "door"
      - otherwise -> NONE
    """
    arg_lower = (arg or "").strip().lower()
    # Identify target segment
    target_part = None
    if " on " in arg_lower:
        _, target_part = arg_lower.split(" on ", 1)
    elif " in " in arg_lower:
        _, target_part = arg_lower.split(" in ", 1)

    if not target_part:
        return UseTarget(kind=TargetKind.NONE)

    target_part = target_part.strip()
    hero_name_lower = (hero_name or "").strip().lower()

    if target_part in {"self", "me", "myself", hero_name_lower}:
        return UseTarget(kind=TargetKind.SELF)

    if target_part in {"room", "the room", "this room", "here"}:
        return UseTarget(kind=TargetKind.ROOM)

    # Room object target
    try:
        room_objects = getattr(room, "objects", {}) or {}
    except Exception:
        room_objects = {}
    if target_part in room_objects:
        return UseTarget(kind=TargetKind.OBJECT, name=target_part)

    return UseTarget(kind=TargetKind.NONE)


# ---------------------------------------------------------------------------
# Adapter hooks expected by tests; by default they are no-ops but test code
# patches them to assert delegation happens.
# ---------------------------------------------------------------------------


def _handle_inventory_command(
    action: str, arg: str, hero, room
) -> None:  # pragma: no cover
    pass


def _use_command(action: str, arg: str, hero, room) -> None:  # pragma: no cover
    pass


def _go_command(action: str, arg: str, hero, room, game) -> None:  # pragma: no cover
    pass


# Wrapped handlers that invoke adapter hooks then delegate to actual handlers


def _wrap_inventory(req: CommandRequest, ctx: CommandContext) -> None:
    try:
        _handle_inventory_command(req.action, req.arg, ctx.hero, ctx.room)
    except Exception:
        # Adapter is best-effort; continue to actual behavior
        pass
    # Dispatch to the concrete handler based on action
    if req.action == "take":
        return handle_take(req, ctx)
    if req.action == "drop":
        return handle_drop(req, ctx)
    # default to examine
    return handle_examine(req, ctx)


def _wrap_use(req: CommandRequest, ctx: CommandContext) -> None:
    try:
        _use_command(req.action, req.arg, ctx.hero, ctx.room)
    except Exception:
        pass
    return handle_use(req, ctx)


def _wrap_go(req: CommandRequest, ctx: CommandContext) -> None:
    try:
        _go_command(req.action, req.arg, ctx.hero, ctx.room, ctx.game)
    except Exception:
        pass
    return handle_go(req, ctx)
