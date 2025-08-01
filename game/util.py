from typing import Optional

from character.hero import RpgHero
from components.inventory import ItemNotFoundError, InsufficientQuantityError
from game.items import UseItemError, Item
from game.magic import NoTargetError


def handle_inventory_operation(operation_func, *args, **kwargs):
    """Helper function to handle common inventory operation exceptions.

    Args:
        operation_func: The inventory operation function to execute
        *args, **kwargs: Arguments to pass to the operation function

    Returns:
        The result of the operation function if successful, None if an exception occurred

    Raises:
        Any exceptions not caught by this handler
    """
    try:
        return operation_func(*args, **kwargs)
    except ItemNotFoundError as e:
        print(f"Error: {e}")
        return None
    except InsufficientQuantityError as e:
        print(f"Error: {e}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None
    except TypeError as e:
        print(f"Error adding item: {e}")
        return None
    except Exception as e:
        print(f"Unexpected inventory error: {e}")
        return None


def handle_spell_cast(hero, spell_name, target):
    """Helper function to handle common spell casting exceptions.

    Args:
        hero: The hero casting the spell
        spell_name: The name of the spell to cast
        target: The target of the spell

    Returns:
        True if the spell was cast successfully, False otherwise
    """
    try:
        return hero.cast_spell(spell_name, target)
    except RpgHero.SpellCastError as e:
        print(f"Spell casting failed: {e}")
    except NoTargetError as e:
        print(f"Spell casting failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return False


def handle_item_use(
    hero: RpgHero, item: Item, target: Optional[any], room: Optional["Room"]
):
    try:
        if room is not None:
            # Handle case where there's no target - use item in room
            if target is None:
                room.use_item_in_room(item, hero)
                return True

            # First try room-object based interactions
            for obj in room.objects.values():
                if obj.name != target.name:
                    continue
                if "use" in obj.interaction_events:
                    result = obj.try_interact("use", hero, item, room)
                    if result:
                        print(result)
                        return True

            # Then try generic tag matches
            for obj in room.objects.values():
                if obj.has_tag("flammable") and item.has_tag("light-source"):
                    obj.change_description("A smoldering pile of ash.")
                    print(
                        "You set fire to the object. It burns with surprising intensity!"
                    )
                    return True

            # Fallback: nothing happened
            print(f"Nothing happens when you use the {item.name} in this room.")
            return False

        else:
            # Use item directly (on self or target)
            return hero.use_item(item.name, target)

    except (ItemNotFoundError, UseItemError, ValueError) as e:
        print(f"Error using item: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return False
