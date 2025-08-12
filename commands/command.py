from __future__ import annotations

from commands import engine
from game.items import Item
from game.util import handle_item_use, handle_inventory_operation


def handle_inventory_command(
    action: str, arg: str, hero: "RpgHero", current_room: "Room"
):
    if not arg:
        print(f"What do you want to {action}?")
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
                item = handle_inventory_operation(current_room.remove_item, arg)
                handle_inventory_operation(hero_inv.add_item, item)
                print(f"You took the {arg}.")
            else:
                print(f"There is no {arg} here to take.")

        elif action == "drop" and hero_has_item:

            for effect in current_room.effects:
                if hasattr(effect, "handle_drop") and effect.handle_drop(hero, arg):
                    return

            quantity = 1  # Default to dropping 1
            # Remove from hero's inventory
            dropped_item = handle_inventory_operation(
                hero_inv.remove_item, arg, quantity
            )
            handle_inventory_operation(current_room.add_item, dropped_item)
            print(
                f"You dropped the {dropped_item.name} with quantity {dropped_item.quantity} in the {current_room.name}."
            )

        elif action == "examine":
            item: Item = None
            if hero_has_item:
                item = hero_inv[arg]
            elif room_inv.has_component(arg):
                item = room_inv[arg]
            else:
                print(f"There is no {arg} here to examine.")
                return

            print(f"You examine the {item.name}:")
            print(f"  Quantity: {item.quantity}")
            print(f"  Value: {item.cost} gold")
            if item.is_usable:
                effect_desc = "No effect"
                if item.effect_type.name == "HEAL":
                    effect_desc = f"Heals for {item.effect_value} health"
                elif item.effect_type.name == "DAMAGE":
                    effect_desc = f"Deals {item.effect_value} damage"
                print(f"  Effect: {effect_desc}")

        elif not hero_has_item:
            print(f"You don't have a {arg} to {action}.")

    except Exception as e:
        print(f"An error occurred: {e}")


def use_command(_, arg: str, hero: "RpgHero" = None, current_room: "Room" = None):
    """
    Use an item either from the hero's inventory or from the room.
    Examples:
    - use [item]
    - use [item] on [target]
    - use [item] on room / in room
    """
    if not arg:
        print("What do you want to use?")
        return

    if not hero or not current_room:
        print("Invalid game state.")
        return

    item_name, target_str = _parse_use_arguments(arg)
    what: engine.UseTarget = engine.parse_use_arg(arg, hero.name, current_room)

    # Decide where the item is and delegate accordingly
    item_location = _find_item_location(item_name, hero, current_room)
    _handle_item_usage(
        item_name, target_str, hero, current_room, what, source=item_location
    )

    # if item_location == "hero":
    #     _handle_hero_item_usage(item_name, target_str, hero, current_room, what)
    # elif item_location == "room":
    #     _handle_room_item_usage(item_name, hero, current_room, target_str, what)
    # else:
    #     print(f"You don't see or have a '{item_name}'.")


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


def _find_item_location(item_name: str, hero: "RpgHero", current_room: "Room") -> str:
    """Determine where the item is located (hero inventory, room, or nowhere)."""
    if hero.inventory.has_component(item_name):
        return "hero"
    elif current_room.inventory.has_component(item_name):
        return "room"
    else:
        return "none"


def _handle_hero_item_usage(
    item_name: str,
    target_str: str,
    hero: "RpgHero",
    current_room: "Room",
    what: engine.UseTarget,
):
    """Combined handler (hero source): delegates to _handle_item_usage."""
    _handle_item_usage(item_name, target_str, hero, current_room, what, source="hero")


def _handle_room_item_usage(
    item_name: str, hero: "RpgHero", current_room: "Room", target_str: str | None, what
):
    """Combined handler (room source): delegates to _handle_item_usage."""
    _handle_item_usage(item_name, target_str, hero, current_room, what, source="room")


def _use_item_on_self(item: "Item", item_name: str, hero: "RpgHero"):
    """Use an item on the hero themselves."""
    if not item.is_usable:
        print(
            f"The {item_name} cannot be used on yourself. It may be used on a room instead."
        )
        return

    old_health = hero.health
    handle_item_use(hero, item, None, None)
    print(f"{hero.name} used {item_name} on themselves.")

    # Display effect based on what happened
    if hero.health > old_health:
        print(f"You feel refreshed! Health increased to {hero.health}.")
    elif hero.health < old_health:
        print(f"Ouch! That hurt. Health decreased to {hero.health}.")


def _use_item_on_room(item: "Item", hero: "RpgHero", current_room: "Room"):
    """Use an item in the room context."""
    try:
        handle_item_use(hero, item, target=None, room=current_room)
        print(f"You used the {item.name} in the {current_room.name}.")
    except ValueError as e:
        print(f"{e}")


def _use_item_on_object(
    item: "Item", target_str: str, hero: "RpgHero", current_room: "Room"
):
    """Use an item on a specific object in the room."""
    obj = current_room.objects[target_str]

    try:
        msg = current_room.interact("use", target_str, hero, item, current_room)
        if msg is not None:
            print(msg)
        else:
            # Fall back to the general item use handler
            handle_item_use(hero, item, target=obj, room=current_room)
            print(f"You used the {item.name} on the {obj.name}.")
    except Exception as e:
        print(f"Cannot use {item.name} on {obj.name}: {e}")


def go_command(
    _, direction: str, hero: "RpgHero" = None, current_room: "Room" = None, game=None
):
    """Handles the 'go' command to move the player to another room.

    Note: Requires the `game` instance to update current_room/last_room.
    The function keeps the original behavior from Game._handle_go.
    """
    if game is None or hero is None or current_room is None:
        print("Invalid game state.")
        return

    next_room = current_room.exits_to.get(direction)
    if not next_room:
        print("You can't go that way.")
        return

    if next_room and not next_room.is_locked:
        hero.last_room = game.current_room
        game.current_room = next_room
        print(f"You go {direction}.")
        if hasattr(game.current_room, "on_enter"):
            game.current_room.on_enter(hero)

    elif direction == "back":
        if hero.last_room is None:
            print("You can't go back any further.")
            return
        temp = game.current_room
        game.current_room = hero.last_room
        hero.last_room = temp
        print("You go back.")

    elif next_room.is_locked:
        print("The door is locked.")
    else:
        print("You can't go that way.")


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
        print(f"Failed to use {item_name}: {e}")
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
            print(f"You must take the {item_name} first before using it on yourself.")
    elif what.kind == TargetKind.ROOM:
        _use_item_on_room(item, hero, current_room)
    elif what.kind == TargetKind.OBJECT:
        # target_str is the normalized object key per parse_use_arg
        _use_item_on_object(item, target_str, hero, current_room)
    else:
        print(f"You don't see '{target_str}' to use the {item_name} on.")
