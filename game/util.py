import logging
import typing
from typing import Optional

from character.hero import RpgHero
from components.inventory import ItemNotFoundError, InsufficientQuantityError
from game.items import UseItemError, Item
from game.magic import NoTargetError
from character.tomes.spell_casting_mix import SpellCastError
from game.display import display

if typing.TYPE_CHECKING:
    from game.room import Room


# def handle_inventory_operation(operation_func, *args, **kwargs):
#     """Helper function to handle common inventory operation exceptions.
#
#     Args:
#         operation_func: The inventory operation function to execute
#         *args, **kwargs: Arguments to pass to the operation function
#
#     Returns:
#         The result of the operation function if successful, None if an exception occurred
#
#     Raises:
#         Any exceptions not caught by this handler
#     """
#     try:
#         return operation_func(*args, **kwargs)
#     except ItemNotFoundError as e:
#         logging.error(f"Error: {e}")
#         return None
#     except InsufficientQuantityError as e:
#         logging.error(f"Error: {e}")
#         return None
#     except ValueError as e:
#         logging.error(f"Error: {e}")
#         return None
#     except TypeError as e:
#         logging.error(f"Error adding item: {e}")
#         return None
#     except Exception as e:
#         logging.error(f"Unexpected inventory error: {e}")
#         return None


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
    except SpellCastError as e:
        logging.error(f"Spell casting failed: {e}")
    except NoTargetError as e:
        logging.error(f"Spell casting failed: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    return False


def handle_item_use(
    hero: RpgHero, item: Item, target: Optional[typing.Any], room: Optional["Room"]
):
    try:
        if room is not None:
            # Handle case where there's no target - use item in room
            if target is None:
                room.use_item_in_room(item, hero)
                return True

            # Delegate targeted interactions to Room effects only
            msg = room.interact("use", getattr(target, "name", None), hero, item, room)
            if msg:
                display.write(msg)
                return True

            # Fallback: nothing happened
            display.write(f"Nothing happens when you use the {item.name} in this room.")
            return False

        else:
            # Use item directly (on self or target)
            return hero.use_item(item.name, target)

    except (ItemNotFoundError, UseItemError, ValueError) as e:
        display.error(f"Error using item: {e}")
    except Exception as e:
        display.error(f"Unexpected error: {e}")
    return False
