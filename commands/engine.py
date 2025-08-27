from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Optional, List, Dict, Tuple

# Import existing command functions to adapt
from commands.command import (
    handle_inventory_command as _handle_inventory_command,
    use_command as _use_command,
    go_command as _go_command,
)


class TargetKind(Enum):
    NONE = auto()
    SELF = auto()
    ROOM = auto()
    OBJECT = auto()


@dataclass
class UseTarget:
    kind: TargetKind
    name: Optional[str] = None  # for OBJECT


@dataclass
class CommandRequest:
    raw: str
    action: str  # canonical, e.g., "take"
    arg: str  # the remainder after action
    tokens: List[str]  # tokenized arg (lowercased)
    use_target: Optional[UseTarget] = None


@dataclass
class CommandContext:
    game: "Game"
    hero: "RpgHero"
    room: "Room"


@dataclass
class CommandDef:
    name: str
    handler: Callable[[CommandRequest, CommandContext], None]
    aliases: List[str]
    help: str


class CommandRegistry:
    def __init__(self):
        self._commands: Dict[str, CommandDef] = {}
        self._alias_to_name: Dict[str, str] = {}

    def register(
        self,
        name: str,
        handler: Callable[[CommandRequest, CommandContext], None],
        help: str,
        aliases: Optional[List[str]] = None,
    ):
        aliases = aliases or []
        cmd = CommandDef(name=name, handler=handler, aliases=aliases, help=help)
        self._commands[name] = cmd
        for a in [name] + aliases:
            self._alias_to_name[a] = name

    def resolve(self, action: str) -> Optional[CommandDef]:
        canonical = self._alias_to_name.get(action)
        if not canonical:
            return None
        return self._commands.get(canonical)

    def help_text(self) -> str:
        lines = ["Available commands:"]
        for cmd in sorted(self._commands.values(), key=lambda c: c.name):
            alias_str = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
            lines.append(f"  {cmd.name}{alias_str} - {cmd.help}")
        return "\n".join(lines)


def parse_command_line(line: str) -> List[Tuple[str, str]]:
    # normalize and split chained commands by " and "
    parts = [p.strip() for p in line.strip().lower().split(" and ") if p.strip()]
    pairs: List[Tuple[str, str]] = []
    for part in parts:
        if " " in part:
            a, rest = part.split(" ", 1)
            pairs.append((a, rest.strip()))
        else:
            pairs.append((part, ""))
    return pairs


def maybe_gag(pairs: List[Tuple[str, str]]) -> Optional[str]:
    # Preserve the humorous special case from the legacy flow
    if len(pairs) == 2:
        (a1, x1), (a2, x2) = pairs
        if a1 == "take" and a2 == "drop" and x1 and x1 == x2:
            return f"You picked up and dropped the {x1}."
    return None


# Adapters: bridge unified handler signature to existing game methods/functions


def _handle_help(req: CommandRequest, ctx: CommandContext):
    print(ctx.game.registry.help_text())


def _handle_look(req: CommandRequest, ctx: CommandContext):
    # Call the Game's method directly to preserve formatting/behavior
    ctx.game._handle_look("")


def _handle_status(req: CommandRequest, ctx: CommandContext):
    ctx.game._handle_status("")


def _handle_inventory(req: CommandRequest, ctx: CommandContext):
    ctx.game._handle_inventory("")


def _handle_talk(req: CommandRequest, ctx: CommandContext):
    ctx.game._handle_talk(req.arg)


def _handle_quit(req: CommandRequest, ctx: CommandContext):
    ctx.game._handle_quit("")


def _handle_debug(req: CommandRequest, ctx: CommandContext):
    # If Game has a debug method, use it. Otherwise, do nothing.
    if hasattr(ctx.game, "_handle_debug"):
        ctx.game._handle_debug(req.arg)


def _handle_take(req: CommandRequest, ctx: CommandContext):
    _handle_inventory_command("take", req.arg, ctx.hero, ctx.room)


def _handle_drop(req: CommandRequest, ctx: CommandContext):
    _handle_inventory_command("drop", req.arg, ctx.hero, ctx.room)


def _handle_examine(req: CommandRequest, ctx: CommandContext):
    _handle_inventory_command("examine", req.arg, ctx.hero, ctx.room)


def _handle_use(req: CommandRequest, ctx: CommandContext):
    # Delegate to existing use_command for now to retain behavior
    _use_command("use", req.arg, ctx.hero, ctx.room)


def _handle_go(req: CommandRequest, ctx: CommandContext):
    _go_command("go", req.arg, ctx.hero, ctx.room, ctx.game)


def _handle_equip(req: CommandRequest, ctx: CommandContext):
    if not req.arg:
        print("What do you want to equip?")
        return
    ctx.hero.equip(req.arg)


def _handle_isweapon(req: CommandRequest, ctx: CommandContext):
    if not req.arg:
        print("Check which item? (usage: isweapon <item>)")
        return
    name = req.arg.strip().lower()
    item = None
    if ctx.hero.inventory.has_component(name):
        item = ctx.hero.inventory[name]
    elif hasattr(ctx.room, "inventory") and ctx.room.inventory.has_component(name):
        item = ctx.room.inventory[name]
    else:
        print(f"You don't see or have a '{req.arg}'.")
        return
    print(
        f"Yes, {item.name} is a weapon." if ctx.hero.is_weapon(item) else f"No, {item.name} is not a weapon."
    )


def register_default_commands(registry: CommandRegistry, game: "Game") -> None:
    # Register commands and aliases with short help texts
    registry.register("look", _handle_look, "Look around the room")
    registry.register("status", _handle_status, "Check your status", aliases=["stats"])
    registry.register(
        "inventory", _handle_inventory, "Check your inventory", aliases=["inv", "i"]
    )
    registry.register("debug", _handle_debug, "Debug mode")
    registry.register("take", _handle_take, "Pick up an item", aliases=["get", "grab"])
    registry.register("drop", _handle_drop, "Drop an item")
    registry.register("examine", _handle_examine, "Examine an item")
    registry.register("use", _handle_use, "Use an item (on self/room/object)")
    registry.register(
        "equip",
        _handle_equip,
        "Equip a weapon you own (e.g., 'equip sword')",
        aliases=["wield"],
    )
    registry.register(
        "isweapon",
        _handle_isweapon,
        "Check if an item is a weapon (e.g., 'isweapon sword')",
        aliases=["is-weapon"],
    )
    registry.register(
        "go",
        _handle_go,
        "Move in a direction (north/south/east/west)",
        aliases=["move"],
    )
    registry.register("talk", _handle_talk, "Talk to someone")
    registry.register("help", _handle_help, "Show this help", aliases=["?"])
    registry.register("quit", _handle_quit, "Exit the game", aliases=["exit"])


# Optional: future improvement to parse use arguments; not wired yet because we delegate to existing use_command
# Keeping here for completeness and potential migration without breaking behavior
SELF_WORDS = {"self", "me", "myself"}


def parse_use_arg(arg: str, hero_name: str, room: "Room") -> UseTarget:
    # Lightweight target detection; currently unused by adapters
    lower = arg.lower()
    target_part = None
    if " on " in lower:
        _, target_part = lower.split(" on ", 1)
    elif " in " in lower:
        _, target_part = lower.split(" in ", 1)
    if not target_part:
        return UseTarget(kind=TargetKind.NONE)
    target_part = target_part.strip()
    if target_part in SELF_WORDS or target_part == hero_name.lower():
        return UseTarget(kind=TargetKind.SELF)
    if target_part in {"room", "the room", "this room"}:
        return UseTarget(kind=TargetKind.ROOM)
    if hasattr(room, "objects") and target_part in getattr(room, "objects", {}):
        return UseTarget(kind=TargetKind.OBJECT, name=target_part)
    return UseTarget(kind=TargetKind.NONE)
