from components.inventory import ItemNotFoundError
from game.items import UseItemError
from game.util import handle_item_use, handle_inventory_operation


def help_command():
    print("\nAvailable commands:")
    print("  go [direction] - Move in a direction (north, south, east, west)")
    print("  look - Look around the room")
    print("  inventory - Check your inventory")
    print("  take/get [item] - Pick up an item")
    print("  drop [item] - Drop an item")
    print("  use [item] - Use an item on yourself")
    print("  use [item] on room - Use an item in the current room")
    print("  use [item] on [target] - Use an item on a specific target")
    print("  status - Check your status")
    print("  turn-in [quest id] - Complete a quest")
    print("  examine [item] - Examine an item in detail")
    print("  quit - Exit the game")


def handle_inventory_command(action:str, arg:str, hero:'RpgHero',current_room:'Room'):
    if not arg:
        print(f"What do you want to {action}?")
        return
    room_inv = current_room.inventory
    hero_inv = hero.inventory
    # Check hero's inventory first
    hero_has_item = hero_inv.has_component(arg)
    try:
        if action in ["take", "get"]:
            if room_inv.has_component(arg):
                item = handle_inventory_operation(current_room.remove_item, arg)
                handle_inventory_operation( hero_inv.add_item, item)
                print(f"You took the {arg}.")
            else:
                print(f"There is no {arg} here to take.")

        elif action == "drop" and hero_has_item:
            quantity = 1  # Default to dropping 1
            # Remove from hero's inventory
            dropped_item = handle_inventory_operation(hero_inv.remove_item, arg, quantity)
            handle_inventory_operation(current_room.add_item, dropped_item)
            print(
                f"You dropped the {dropped_item.name} with quantity {dropped_item.quantity} in the {current_room.name}.")

        elif action == "examine":
            item:'Item' = None
            if hero_has_item:
                item = hero_inv[arg]
            elif room_inv.has_component(arg):
                item = room_inv[arg]
            else:
                print(f"There is no {item.name} here to examine.")
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
            # Then check room inventory

        elif not hero_has_item:
            print(f"You don't have a {arg} to {action}.")

    except Exception as e:
        print(f"An error occurred: {e}")





def use_command(_ , arg: str, hero:'RpgHero'=None, current_room:'Room'=None):
    if not arg:
        print("What do you want to use?")
        return

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

    try:
        # First, check if the item is in the hero's inventory
        if hero.inventory.has_component(item_name):
            item = hero.inventory[item_name]

            # If the player specified "on room" or "in room", try room context usage
            if target_str in ["room", "the room", "this room"]:
                try:
                    handle_item_use(hero, item_name, room=current_room)
                    # Item removal is handled by the room effect
                except ValueError as e:
                    print(f"{e}")
            # If it's a usable item but no specific target, use on self by default
            elif target_str is None or target_str in ["self", "me", "myself", hero.name.lower()]:
                if not item.is_usable:
                    print(f"The {item_name} cannot be used on yourself.")
                    return

                # Use item on hero
                old_health = hero.health
                handle_item_use(hero, item_name)

                print(f"{hero.name} used {item_name} on {hero.name}.")

                # Display effect based on what happened
                if hero.health > old_health:
                    print(f"You feel refreshed! Health increased to {hero.health}.")
                elif hero.health < old_health:
                    print(f"Ouch! That hurt. Health decreased to {hero.health}.")
            else:
                print(f"You don't see '{target_str}' to use the {item_name} on.")

        # If item is in the room, try to use it directly
        elif current_room.inventory.has_component(item_name):
            try:
                current_room.use_item_in_room(item_name, hero)
                print(f"{hero.name} used the {item_name} in the {current_room.name}.")
            except Exception as e:
                print(f"Failed to use {item_name}: {e}")
        else:
            print(f"You don't see or have a '{item_name}'.")

    except ItemNotFoundError as e:
        print(f"Item not found: {e}")
    except UseItemError as e:
        print(f"Cannot use this item: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")