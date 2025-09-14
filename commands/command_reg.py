from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List, Dict, Optional


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
class UseTarget:
    kind: TargetKind
    name: Optional[str] = None  # for OBJECT


class TargetKind(Enum):
    NONE = auto()
    SELF = auto()
    ROOM = auto()
    OBJECT = auto()
