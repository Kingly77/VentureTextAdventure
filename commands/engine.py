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
from game.util import handle_spell_cast


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
    # Standalone: print current room description
    try:
        desc = ctx.room.get_description()
    except Exception:
        desc = str(getattr(ctx.room, "base_description", ""))
    if desc:
        print(desc)


def _handle_status(req: CommandRequest, ctx: CommandContext):
    hero = ctx.hero
    # Character stats section
    print("\n📊 Character Status:")
    print("=" * 40)
    try:
        print(
            f"🧙 {hero.name} | Level {hero.level} | XP: {getattr(hero, 'xp', 0)}/{getattr(hero, 'xp_to_next_level', 0)}"
        )
    except Exception:
        # Fallback if attributes missing
        print(f"🧙 {getattr(hero, 'name', 'Hero')}")
    if hasattr(hero, 'health') and hasattr(hero, 'max_health'):
        print(f"❤️  Health: {hero.health}/{hero.max_health}")
    if hasattr(hero, 'mana') and hasattr(hero, 'max_mana'):
        print(f"✨ Mana: {hero.mana}/{hero.max_mana}")
    if hasattr(hero, 'gold'):
        print(f"💰 Gold: {hero.gold}")

    # Quest log section
    ql = getattr(hero, 'quest_log', None)
    active_quests = list(getattr(ql, 'active_quests', {}).values()) if ql else []
    completed_quests = getattr(ql, 'completed_quests', []) if ql else []

    if active_quests or completed_quests:
        print("\n📜 Quest Log:")
        print("-" * 40)
        if active_quests:
            print("🔸 Active Quests:")
            for quest in active_quests:
                try:
                    print(
                        f"  • {quest.name} - {quest.description} ({quest.progress}/{quest.objective.value}) (ID: {quest.id})"
                    )
                except Exception:
                    print(f"  • {quest}")
        if completed_quests:
            print("\n🔹 Completed Quests:")
            for quest in completed_quests:
                print(f"  • {quest}")
    else:
        print("\n📜 Quest Log: No quests available")
    print("=" * 40)


def _handle_inventory(req: CommandRequest, ctx: CommandContext):
    hero = ctx.hero
    inventory = hero.inventory
    items = list(inventory.items.values())

    if not items or (len(items) == 1 and items[0].name == "gold"):
        print("\n📦 Your inventory is empty.")
        return

    print("\n📦 Inventory:")
    print("------------------------")

    usable_items = []
    equipment = []
    misc_items = []

    for item in items:
        if item.name.lower() == "gold":
            continue
        if hasattr(hero, "is_weapon") and hero.is_weapon(item):
            equipment.append(item)
        elif item.is_usable:
            usable_items.append(item)
        else:
            misc_items.append(item)

    if usable_items:
        print("🧪 Usable Items:")
        for item in usable_items:
            effect_text = ""
            if getattr(item.effect_type, "name", "") == "HEAL":
                effect_text = f" (Heals {item.effect_value})"
            elif getattr(item.effect_type, "name", "") == "DAMAGE":
                effect_text = f" (Damage {item.effect_value})"
            print(f"  • {item.name} x{item.quantity}{effect_text} - {item.cost} gold each")
        print()

    if equipment:
        print("⚔️ Equipment:")
        for item in equipment:
            marker = " [equipped]" if getattr(getattr(hero, "equipped", None), "name", None) == item.name else ""
            print(f"  • {item.name}{marker} x{item.quantity} - {item.cost} gold each")
        print()

    if misc_items:
        print("🔮 Other Items:")
        for item in misc_items:
            print(f"  • {item.name} x{item.quantity} - {item.cost} gold each")

    print("------------------------")
    print(f"💰 Gold: {hero.gold}")


def _handle_talk(req: CommandRequest, ctx: CommandContext):
    # Try to let the current room/effects handle the conversation
    try:
        msg = ctx.room.interact("talk", req.arg if req.arg else None, ctx.hero, None, ctx.room)
        if msg is not None:
            if isinstance(msg, str) and msg:
                print(msg)
            return
    except Exception:
        pass
    print("There is no one here to talk to.")
    return


def _handle_quit(req: CommandRequest, ctx: CommandContext):
    # Standalone: mark the game as over
    try:
        ctx.game.game_over = True
    except Exception:
        pass


def _handle_debug(req: CommandRequest, ctx: CommandContext):
    # Standalone debug commands for development convenience
    arg = (req.arg or "").strip().lower()
    hero = ctx.hero
    if arg == "heal":
        if hasattr(hero, 'max_health'):
            hero.health = hero.max_health
        print(f"{getattr(hero, 'name', 'Hero')} fully healed.")
    elif arg == "mana":
        if hasattr(hero, 'max_mana'):
            hero.mana = hero.max_mana
        print(f"{getattr(hero, 'name', 'Hero')} restored mana.")
    elif arg == "xp":
        if hasattr(hero, 'add_xp'):
            hero.add_xp(100)
        print("Gained 100 XP.")
    elif arg == "gold":
        if hasattr(hero, 'add_gold'):
            hero.add_gold(100)
        elif hasattr(hero, 'gold'):
            hero.gold += 100
        print("Gained 100 gold.")
    elif arg == "hurt":
        if hasattr(hero, 'take_damage'):
            hero.take_damage(10)
        elif hasattr(hero, 'health'):
            hero.health = max(0, hero.health - 10)
        print(f"{getattr(hero, 'name', 'Hero')} was hurt for 10 HP.")
    else:
        print("Unknown debug command. Options: heal, mana, xp,gold")


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


def _handle_attack(req: CommandRequest, ctx: CommandContext):
    game = ctx.game
    hero = ctx.hero
    enemy = game.current_enemy
    if not game.in_combat or enemy is None:
        print("There's nothing to attack right now.")
        return
    try:
        hero.attack(enemy, req.arg or None)
    except ValueError:
        # List available weapons to help the player
        weapons = [
            name
            for name, item in hero.inventory.items.items()
            if getattr(item, "is_equipment", False)
        ]
        if weapons:
            print(f"Available weapons: {', '.join(weapons)}")
        else:
            print(
                "No weapons available. Use 'attack' without a weapon to fight bare-handed."
            )
        return
    print(
        f"{hero.name} attacks {enemy.name}! {enemy.name}'s health is now {enemy.health}."
    )
    if enemy.is_alive():
        enemy.attack(hero)
        print(f"{enemy.name} retaliates! {hero.name}'s health is now {hero.health}.")
        if not hero.is_alive():
            game._end_combat(False)
            return
    if not enemy.is_alive():
        game._end_combat(True)


def _handle_cast(req: CommandRequest, ctx: CommandContext):
    game = ctx.game
    hero = ctx.hero
    enemy = game.current_enemy
    if not game.in_combat or enemy is None:
        print("There's nothing to cast spells on right now.")
        return
    # Delegate to util, which handles exceptions and validations
    handle_spell_cast(hero, req.arg, enemy)
    if enemy.is_alive():
        enemy.attack(hero)
        print(f"{enemy.name} retaliates! {hero.name}'s health is now {hero.health}.")
        if not hero.is_alive():
            game._end_combat(False)
            return
    if not enemy.is_alive():
        game._end_combat(True)


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
    # Combat-related commands
    registry.register(
        "attack",
        _handle_attack,
        "Attack the current enemy (optionally specify a weapon: 'attack sword')",
    )
    registry.register(
        "cast",
        _handle_cast,
        "Cast a spell on the current enemy (usage: 'cast <spell>')",
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


# Test-friendly helper to execute a command line and capture output
# This allows tests to avoid patching builtins.print while exercising behavior.
# It is optional and does not change any runtime behavior.
from typing import List as _List
import io as _io
import contextlib as _contextlib


def execute_line(game: "Game", line: str) -> _List[str]:
    """
    Execute a command line through the game's parser/dispatcher and return
    the printed output as a list of lines. This is intended to make tests
    less reliant on patching builtins.print.
    """
    buf = _io.StringIO()
    with _contextlib.redirect_stdout(buf):
        game.parse_and_execute(line)
    output = buf.getvalue().splitlines()
    return output
