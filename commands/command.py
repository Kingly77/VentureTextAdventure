"""
Clean command handlers using the unified CommandRequest/CommandContext system.
No legacy adapters, no duplicate parsing, just straightforward command logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from commands.command_reg import CommandRequest, CommandContext, UseTarget, TargetKind
from game.display import display
from game.underlings.inventory_maybe import transfer
from game.underlings.events import Events
from game.util import handle_item_use, handle_spell_cast

if TYPE_CHECKING:
    from game.items import Item


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def _find_item_in_inventories(
    item_name: str, ctx: CommandContext
) -> tuple[Item | None, str | None]:
    """
    Find an item in hero or room inventory.

    Returns:
        (Item, location) where location is "hero", "room", or None if not found
    """
    if ctx.hero.inventory.has_component(item_name):
        return ctx.hero.inventory[item_name], "hero"
    elif ctx.room.inventory.has_component(item_name):
        return ctx.room.inventory[item_name], "room"
    return None, None


def _parse_use_target(arg: str, ctx: CommandContext) -> tuple[str, UseTarget]:
    """
    Parse a use command argument into item name and target.

    Examples:
        "torch" -> ("torch", UseTarget(NONE))
        "potion on me" -> ("potion", UseTarget(SELF))
        "key on door" -> ("key", UseTarget(OBJECT, "door"))
        "torch in room" -> ("torch", UseTarget(ROOM))

    Returns:
        (item_name, UseTarget)
    """
    arg_lower = arg.lower()

    # Check for " on " or " in " patterns
    if " on " in arg_lower:
        item_name, target_part = arg_lower.split(" on ", 1)
    elif " in " in arg_lower:
        item_name, target_part = arg_lower.split(" in ", 1)
    else:
        # No target specified
        return arg_lower.strip(), UseTarget(kind=TargetKind.NONE)

    item_name = item_name.strip()
    target_part = target_part.strip()

    # Determine target type
    hero_name_lower = ctx.hero.name.lower()

    if target_part in {"self", "me", "myself", hero_name_lower}:
        return item_name, UseTarget(kind=TargetKind.SELF)

    if target_part in {"room", "the room", "this room", "here"}:
        return item_name, UseTarget(kind=TargetKind.ROOM)

    # Check if it's an object in the room
    if target_part in ctx.room.objects:
        return item_name, UseTarget(kind=TargetKind.OBJECT, name=target_part)

    # Unknown target
    return item_name, UseTarget(kind=TargetKind.NONE)


# ============================================================================
# INFORMATION COMMANDS
# ============================================================================


def handle_help(req: CommandRequest, ctx: CommandContext):
    """Show available commands."""
    display.write(ctx.game.registry.help_text())

    # Allow room effects to add help text
    try:
        extra = ctx.room.interact("help", req.arg, ctx.hero, None, ctx.room)
        if extra:
            display.write(extra)
    except Exception:
        pass


def handle_look(req: CommandRequest, ctx: CommandContext):
    """Look around the current room."""
    try:
        display.write(ctx.room.get_full_description())
    except Exception as e:
        display.error(f"Error looking around: {e}")


def handle_status(req: CommandRequest, ctx: CommandContext):
    """Show character status, including health, mana, XP, and quests."""
    hero = ctx.hero

    display.write("\n📊 Character Status:")
    display.write("=" * 40)

    # Basic stats
    display.write(f"🧙 {hero.name} | Level {hero.level}")
    if hasattr(hero, "xp") and hasattr(hero, "xp_to_next_level"):
        display.write(f"📈 XP: {hero.xp}/{hero.xp_to_next_level}")

    if hasattr(hero, "health") and hasattr(hero, "max_health"):
        display.write(f"❤️  Health: {hero.health}/{hero.max_health}")

    if hasattr(hero, "mana") and hasattr(hero, "max_mana"):
        display.write(f"✨ Mana: {hero.mana}/{hero.max_mana}")

    if hasattr(hero, "gold"):
        display.write(f"💰 Gold: {hero.gold}")

    # Quest log
    quest_log = getattr(hero, "quest_log", None)
    if quest_log:
        active = list(quest_log.active_quests.values())
        completed = quest_log.completed_quests

        if active or completed:
            display.write("\n📜 Quest Log:")
            display.write("-" * 40)

            if active:
                display.write("🔸 Active Quests:")
                for quest in active:
                    try:
                        display.write(
                            f"  • {quest.name} - {quest.description} ({quest.progress}/{quest.objective.value})"
                        )
                    except Exception:
                        display.write(f"  • {quest.name}")

            if completed:
                display.write("\n🔹 Completed Quests:")
                for quest in completed:
                    display.write(f"  • {quest}")
        else:
            display.write("\n📜 Quest Log: No quests available")

    display.write("=" * 40)


def handle_inventory(req: CommandRequest, ctx: CommandContext):
    """Show inventory contents."""
    hero = ctx.hero
    items = list(hero.inventory.items.values())

    # Filter out gold (handled separately)
    items = [item for item in items if item.name.lower() != "gold"]

    if not items:
        display.write("\n📦 Your inventory is empty.")
        return

    display.write("\n📦 Inventory:")
    display.write("------------------------")

    # Categorize items
    usable_items = []
    equipment = []
    misc_items = []

    for item in items:
        if hasattr(hero, "is_weapon") and hero.is_weapon(item):
            equipment.append(item)
        elif item.is_usable:
            usable_items.append(item)
        else:
            misc_items.append(item)

    # Display categorized items
    if usable_items:
        display.write("🧪 Usable Items:")
        for item in usable_items:
            effect_text = ""
            if hasattr(item, "effect_type") and hasattr(item.effect_type, "name"):
                if item.effect_type.name == "HEAL":
                    effect_text = f" (Heals {item.effect_value})"
                elif item.effect_type.name == "DAMAGE":
                    effect_text = f" (Damage {item.effect_value})"
            display.write(
                f"  • {item.name} x{item.quantity}{effect_text} - {item.cost} gold each"
            )
        display.write()

    if equipment:
        display.write("⚔️ Equipment:")
        for item in equipment:
            equipped_marker = ""
            if (
                hasattr(hero, "equipped")
                and hero.equipped
                and hero.equipped.name == item.name
            ):
                equipped_marker = " [equipped]"
            display.write(
                f"  • {item.name}{equipped_marker} x{item.quantity} - {item.cost} gold each"
            )
        display.write()

    if misc_items:
        display.write("🔮 Other Items:")
        for item in misc_items:
            display.write(f"  • {item.name} x{item.quantity} - {item.cost} gold each")

    display.write("------------------------")
    if hasattr(hero, "gold"):
        display.write(f"💰 Gold: {hero.gold}")


# ============================================================================
# INVENTORY COMMANDS
# ============================================================================


def handle_take(req: CommandRequest, ctx: CommandContext):
    """Take an item from the room."""
    if not req.arg:
        display.write("What do you want to take?")
        return

    item_name = req.arg.strip().lower()

    # Check if room effects handle this
    for effect in ctx.room.effects:
        if hasattr(effect, "handle_take"):
            if effect.handle_take(ctx.hero, item_name):
                return

    # Try to take from room inventory
    if not ctx.room.inventory.has_component(item_name):
        display.write(f"There is no {item_name} here to take.")
        return

    moved = transfer(ctx.room.inventory, item_name, ctx.hero.inventory)
    if moved:
        display.write(f"You took the {item_name}.")
    else:
        display.write(f"You couldn't take the {item_name}.")


def handle_drop(req: CommandRequest, ctx: CommandContext):
    """Drop an item from inventory into the room."""
    if not req.arg:
        display.write("What do you want to drop?")
        return

    item_name = req.arg.strip().lower()

    if not ctx.hero.inventory.has_component(item_name):
        display.write(f"You don't have a {item_name} to drop.")
        return

    # Check if room effects handle this
    for effect in ctx.room.effects:
        if hasattr(effect, "handle_drop"):
            if effect.handle_drop(ctx.hero, item_name):
                return

    # Try to drop into room inventory
    moved = transfer(ctx.hero.inventory, item_name, ctx.room.inventory, quantity=1)
    if moved:
        display.write(f"You dropped the {moved.name} in the {ctx.room.name}.")
    else:
        display.write(f"You couldn't drop the {item_name}.")


def handle_examine(req: CommandRequest, ctx: CommandContext):
    """Examine an item in detail."""
    if not req.arg:
        display.write("What do you want to examine?")
        return

    item_name = req.arg.strip().lower()

    # Check if room effects handle this
    for effect in ctx.room.effects:
        if hasattr(effect, "handle_interaction"):
            try:
                result = effect.handle_interaction(
                    "examine", item_name, ctx.hero, None, ctx.room
                )
                if result:
                    display.write(result)
                    return
            except Exception:
                pass

    # Find the item
    item, location = _find_item_in_inventories(item_name, ctx)

    if item is None:
        display.write(f"There is no {item_name} here to examine.")
        return

    # Display item details
    display.write(f"You examine the {item.name}:")
    display.write(f"  Quantity: {item.quantity}")
    display.write(f"  Value: {item.cost} gold")

    if item.is_usable and hasattr(item, "effect_type"):
        effect_desc = "No effect"
        if hasattr(item.effect_type, "name"):
            if item.effect_type.name == "HEAL":
                effect_desc = f"Heals for {item.effect_value} health"
            elif item.effect_type.name == "DAMAGE":
                effect_desc = f"Deals {item.effect_value} damage"
        display.write(f"  Effect: {effect_desc}")


# ============================================================================
# ITEM USAGE COMMANDS
# ============================================================================


def handle_use(req: CommandRequest, ctx: CommandContext):
    """
    Use an item from inventory or room.

    Syntax:
        use <item>              - Use item (context-dependent)
        use <item> on me        - Use item on self
        use <item> in room      - Use item in/on room
        use <item> on <object>  - Use item on specific object
    """
    if not req.arg:
        display.write("What do you want to use?")
        return

    # Parse the command
    item_name, target = _parse_use_target(req.arg, ctx)

    # Find the item
    item, location = _find_item_in_inventories(item_name, ctx)

    if item is None:
        display.write(f"You don't have or see a '{item_name}'.")
        return

    # Handle based on target type
    if target.kind == TargetKind.SELF:
        # Use on self
        if location == "room":
            display.write(
                f"You must take the {item_name} first before using it on yourself."
            )
            return

        if not item.is_usable:
            display.write(f"The {item_name} cannot be used on yourself.")
            return

        try:
            success = handle_item_use(ctx.hero, item, None, None)
            if success:
                display.write(f"{ctx.hero.name} used {item_name} on themselves.")
        except Exception as e:
            display.error(f"Error using {item_name}: {e}")

    elif target.kind == TargetKind.ROOM:
        # Use in/on room
        try:
            handle_item_use(ctx.hero, item, target=None, room=ctx.room)
            display.write(f"You used the {item.name} in the {ctx.room.name}.")
        except Exception as e:
            display.error(f"{e}")

    elif target.kind == TargetKind.OBJECT:
        # Use on specific object
        if target.name not in ctx.room.objects:
            display.write(f"There is no {target.name} here.")
            return

        obj = ctx.room.objects[target.name]

        try:
            msg = ctx.room.interact("use", target.name, ctx.hero, item, ctx.room)
            if msg:
                display.write(msg)
            else:
                handle_item_use(ctx.hero, item, target=obj, room=ctx.room)
                display.write(f"You used the {item.name} on the {obj.name}.")
        except Exception as e:
            display.error(f"Cannot use {item.name} on {obj.name}: {e}")

    else:
        # No target specified - try to infer
        if item.is_usable:
            display.write(f"Use {item_name} on what? (yourself, room, or an object)")
        else:
            display.write(
                f"The {item_name} cannot be used directly. Try using it on something."
            )


def handle_equip(req: CommandRequest, ctx: CommandContext):
    """Equip a weapon from inventory."""
    if not req.arg:
        display.write("What do you want to equip?")
        return

    item_name = req.arg.strip().lower()

    if not ctx.hero.inventory.has_component(item_name):
        display.write(f"You don't have a '{item_name}'.")
        return

    try:
        success = ctx.hero.equip(item_name)
        if not success:
            display.write(f"'{item_name}' is not a weapon.")
    except Exception as e:
        display.error(f"Error equipping {item_name}: {e}")


# ============================================================================
# MOVEMENT COMMANDS
# ============================================================================


def handle_go(req: CommandRequest, ctx: CommandContext):
    """Move to another room in the specified direction."""
    if not req.arg:
        display.write("Go where? (north, south, east, west, back)")
        return

    direction = req.arg.strip().lower()

    # Handle "back" specially
    if direction == "back":
        if ctx.hero.last_room is None:
            display.write("You can't go back any further.")
            return

        # Swap current and last room
        temp = ctx.game.current_room
        ctx.game.current_room = ctx.hero.last_room
        ctx.hero.last_room = temp
        display.write("You go back.")

        # Trigger room entry
        if hasattr(ctx.game.current_room, "on_enter"):
            ctx.game.current_room.on_enter(ctx.hero)
        return

    # Check if direction is valid
    next_room = ctx.room.exits_to.get(direction)

    if not next_room:
        display.write("You can't go that way.")
        return

    if next_room.is_locked:
        display.write("The door is locked.")
        return

    # Move to the new room
    ctx.hero.last_room = ctx.game.current_room
    ctx.game.current_room = next_room

    Events.trigger_event("location_entered", ctx.hero, next_room.name)
    display.write(f"You go {direction}.")

    # Trigger room entry effects
    if hasattr(next_room, "on_enter"):
        next_room.on_enter(ctx.hero)


# ============================================================================
# COMBAT COMMANDS
# ============================================================================


def handle_attack(req: CommandRequest, ctx: CommandContext):
    """Attack the current enemy."""
    game = ctx.game
    hero = ctx.hero
    enemy = game.current_enemy

    if not game.in_combat or enemy is None:
        display.write("There's nothing to attack right now.")
        return

    weapon_name = req.arg.strip().lower() if req.arg else None

    try:
        hero.attack(enemy, weapon_name)
    except ValueError as e:
        # Show available weapons
        weapons = [
            name
            for name, item in hero.inventory.items.items()
            if hasattr(item, "is_equipment") and item.is_equipment
        ]
        if weapons:
            display.write(f"Available weapons: {', '.join(weapons)}")
        else:
            display.write(
                "No weapons available. Use 'attack' without a weapon to fight with your fists."
            )
        return

    display.write(
        f"{hero.name} attacks {enemy.name}! {enemy.name}'s health is now {enemy.health}."
    )

    # Enemy counterattack if still alive
    if enemy.is_alive():
        enemy.attack(hero)
        display.write(
            f"{enemy.name} retaliates! {hero.name}'s health is now {hero.health}."
        )

        if not hero.is_alive():
            game._end_combat(False)
            return

    # Check if enemy defeated
    if not enemy.is_alive():
        game._end_combat(True)


def handle_cast(req: CommandRequest, ctx: CommandContext):
    """Cast a spell on the current enemy."""
    game = ctx.game
    hero = ctx.hero
    enemy = game.current_enemy

    if not game.in_combat or enemy is None:
        display.write("There's nothing to cast spells on right now.")
        return

    if not req.arg:
        display.write("Cast which spell?")
        return

    spell_name = req.arg.strip().lower()

    # Use the spell
    handle_spell_cast(hero, spell_name, enemy)

    # Enemy counterattack if still alive
    if enemy.is_alive():
        enemy.attack(hero)
        display.write(
            f"{enemy.name} retaliates! {hero.name}'s health is now {hero.health}."
        )

        if not hero.is_alive():
            game._end_combat(False)
            return

    # Check if enemy defeated
    if not enemy.is_alive():
        game._end_combat(True)


# ============================================================================
# INTERACTION COMMANDS
# ============================================================================


def handle_talk(req: CommandRequest, ctx: CommandContext):
    """Talk to NPCs or interact with room elements."""
    try:
        msg = ctx.room.interact(
            "talk", req.arg if req.arg else None, ctx.hero, None, ctx.room
        )
        if msg:
            display.write(msg)
        else:
            display.write("There is no one here to talk to.")
    except Exception:
        display.write("There is no one here to talk to.")


# ============================================================================
# SYSTEM COMMANDS
# ============================================================================


def handle_quit(req: CommandRequest, ctx: CommandContext):
    """Exit the game."""
    ctx.game.game_over = True
    display.write("Thanks for playing!")


def handle_debug(req: CommandRequest, ctx: CommandContext):
    """Debug commands for testing."""
    if not req.arg:
        display.write("Debug options: heal, mana, xp, gold, hurt")
        return

    command = req.arg.strip().lower()
    hero = ctx.hero

    if command == "heal":
        if hasattr(hero, "max_health"):
            hero.health = hero.max_health
            display.write(f"{hero.name} fully healed.")

    elif command == "mana":
        if hasattr(hero, "max_mana"):
            hero.mana = hero.max_mana
            display.write(f"{hero.name} restored mana.")

    elif command == "xp":
        if hasattr(hero, "add_xp"):
            hero.add_xp(100)
            display.write("Gained 100 XP.")

    elif command == "gold":
        if hasattr(hero, "add_gold"):
            hero.add_gold(100)
        elif hasattr(hero, "gold"):
            hero.gold += 100
        display.write("Gained 100 gold.")

    elif command == "hurt":
        if hasattr(hero, "take_damage"):
            hero.take_damage(10)
        elif hasattr(hero, "health"):
            hero.health = max(0, hero.health - 10)
        display.write(f"{hero.name} was hurt for 10 HP.")

    else:
        display.write("Unknown debug command. Options: heal, mana, xp, gold, hurt")
