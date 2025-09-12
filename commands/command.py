from __future__ import annotations

from character.hero import RpgHero
from commands import engine
from game.items import Item
from game.room import Room
from game.underlings.events import Events
from game.util import handle_item_use
from game.underlings.inventory_maybe import transfer
from game.display import display


def handle_inventory_command(
    action: str, arg: str, hero: "RpgHero", current_room: "Room"
):
    if not arg:
        display.write(f"What do you want to {action}?")
        return
    room_inv = current_room.inventory
    hero_inv = hero.inventory
    # Check hero's inventory first
    hero_has_item = hero_inv.has_component(arg)
    try:
        if action in ["take", "get", "grab"]:

            for effect in current_room.effects:
                if hasattr(effect, "handle_take"):
                    if effect.handle_take(hero, arg):
                        return

            if room_inv.has_component(arg):
                moved = transfer(current_room, arg, hero_inv)
                if moved:
                    display.write(f"You took the {arg}.")
                else:
                    display.write(f"You couldn't take the {arg}.")
            else:
                display.write(f"There is no {arg} here to take.")

        elif action == "drop" and hero_has_item:

            for effect in current_room.effects:
                if hasattr(effect, "handle_drop") and effect.handle_drop(hero, arg):
                    return

            quantity = 1  # Default to dropping 1
            moved = transfer(hero_inv, arg, current_room, quantity)
            if moved:
                display.write(
                    f"You dropped the {moved.name} with quantity {moved.quantity} in the {current_room.name}."
                )
            else:
                display.write(f"You couldn't drop the {arg}.")

        elif action == "examine":
            item: Item = None
            if hero_has_item:
                item = hero_inv[arg]
            elif room_inv.has_component(arg):
                item = room_inv[arg]
            else:
                display.write(f"There is no {arg} here to examine.")
                return

            display.write(f"You examine the {item.name}:")
            display.write(f"  Quantity: {item.quantity}")
            display.write(f"  Value: {item.cost} gold")
            if item.is_usable:
                effect_desc = "No effect"
                if item.effect_type.name == "HEAL":
                    effect_desc = f"Heals for {item.effect_value} health"
                elif item.effect_type.name == "DAMAGE":
                    effect_desc = f"Deals {item.effect_value} damage"
                display.write(f"  Effect: {effect_desc}")

        elif not hero_has_item:
            display.write(f"You don't have a {arg} to {action}.")

    except Exception as e:
        display.error(f"An error occurred: {e}")


def use_command(_, arg: str, hero: "RpgHero" = None, current_room: "Room" = None):
    """
    Use an item either from the hero's inventory or from the room.
    Examples:
    - use [item]
    - use [item] on [target]
    - use [item] on room / in room
    """
    if not arg:
        display.write("What do you want to use?")
        return

    if not hero or not current_room:
        display.write("Invalid game state.")
        return

    item_name, target_str = _parse_use_arguments(arg)
    what: engine.UseTarget = engine.parse_use_arg(arg, hero.name, current_room)

    # Decide where the item is and delegate accordingly
    item_location = _find_item_location(item_name, hero, current_room)
    _handle_item_usage(
        item_name, target_str, hero, current_room, what, source=item_location
    )


def _parse_use_arguments(arg: str) -> tuple[str, str | None]:
    """Parse use command arguments into item name and target."""
    # Split argument into item name and target (if provided)
    # Support both "use X on Y" and "use X in Y" patterns
    if " on " in arg:
        parts = arg.split(" on ", 1)
    elif " in " in arg:
        parts = arg.split(" in ", 1)
    else:
        parts = [arg]

    item_name = parts[0].strip().lower()
    target_str = parts[1].strip().lower() if len(parts) > 1 else None

    return item_name, target_str


def _find_item_location(item_name: str, hero: RpgHero, current_room: Room) -> str:
    """Determine where the item is located (hero inventory, room, or nowhere)."""
    if hero.inventory.has_component(item_name):
        return "hero"
    elif current_room.inventory.has_component(item_name):
        return "room"
    else:
        return "none"


def _use_item_on_self(item: Item, item_name: str, hero: RpgHero):
    """Use an item on the hero themselves."""
    if not item.is_usable:
        display.write(
            f"The {item_name} cannot be used on yourself. It may be used on a room instead."
        )
        return

    old_health = hero.health
    handle_item_use(hero, item, None, None)
    display.write(f"{hero.name} used {item_name} on themselves.")

    # Display effect based on what happened
    if hero.health > old_health:
        display.write(f"You feel refreshed! Health increased to {hero.health}.")
    elif hero.health < old_health:
        display.write(f"Ouch! That hurt. Health decreased to {hero.health}.")


def _use_item_on_room(item: Item, hero: RpgHero, current_room: Room):
    """Use an item in the room context."""
    try:
        handle_item_use(hero, item, target=None, room=current_room)
        display.write(f"You used the {item.name} in the {current_room.name}.")
    except ValueError as e:
        display.write(f"{e}")


def _use_item_on_object(
    item: Item, target_str: str, hero: RpgHero, current_room: Room, vb="use"
):
    """Use an item on a specific object in the room."""
    obj = current_room.objects[target_str]

    try:
        msg = current_room.interact(vb, target_str, hero, item, current_room)
        if msg is not None:
            display.write(msg)
        else:
            # Fall back to the general item use handler
            handle_item_use(hero, item, target=obj, room=current_room)
            display.write(f"You used the {item.name} on the {obj.name}.")
    except Exception as e:
        display.error(f"Cannot use {item.name} on {obj.name}: {e}")


def go_command(
    _, direction: str, hero: RpgHero = None, current_room: Room = None, game=None
):
    """Handles the 'go' command to move the player to another room.

    Note: Requires the `game` instance to update current_room/last_room.
    The function keeps the original behavior from Game._handle_go.
    """
    if game is None or hero is None or current_room is None:
        display.write("Invalid game state.")
        return

    next_room = current_room.exits_to.get(direction)
    if not next_room:
        display.write("You can't go that way.")
        return

    if next_room and not next_room.is_locked:
        hero.last_room = game.current_room
        game.current_room = next_room
        Events.trigger_event("location_entered", hero, next_room.name)
        display.write(f"You go {direction}.")
        if hasattr(game.current_room, "on_enter"):
            game.current_room.on_enter(hero)

    elif direction == "back":
        if hero.last_room is None:
            display.write("You can't go back any further.")
            return
        temp = game.current_room
        game.current_room = hero.last_room
        hero.last_room = temp
        display.write("You go back.")

    elif next_room.is_locked:
        display.write("The door is locked.")
    else:
        display.write("You can't go that way.")


def _handle_item_usage(
    item_name: str,
    target_str: str | None,
    hero: "RpgHero",
    current_room: "Room",
    what: engine.UseTarget,
    source: str,
):
    """Unified item usage handler for both hero and room sources.

    - source: "hero" or "room"
    - Respects TargetKind from engine.parse_use_arg
    - Preserves behavior that room-sourced items cannot be used on self without taking them first.
    """
    from .engine import TargetKind

    # Acquire the item from the appropriate inventory
    try:
        if source == "hero":
            item = hero.inventory[item_name]
        else:
            item = current_room.inventory[item_name]
    except Exception as e:
        display.error(f"Failed to use {item_name}: {e}")
        return

    if what is None:
        # Fallback: if parsing failed for some reason, behave like room handler used to
        # This path is unlikely with current parser usage.
        if source == "room" and (
            target_str is None or target_str in ["room", "the room", "this room"]
        ):
            _use_item_on_room(item, hero, current_room)
            return

    if what.kind == TargetKind.SELF:
        if source == "hero":
            _use_item_on_self(item, item_name, hero)
        else:
            display.write(
                f"You must take the {item_name} first before using it on yourself."
            )
    elif what.kind == TargetKind.ROOM:
        _use_item_on_room(item, hero, current_room)
    elif what.kind == TargetKind.OBJECT:
        # target_str is the normalized object key per parse_use_arg
        _use_item_on_object(item, target_str, hero, current_room, vb="use")
    else:
        display.write(f"You don't see '{target_str}' to use the {item_name} on.")
