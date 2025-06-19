from character.hero import RpgHero
from components.inventory import ItemNotFoundError, InsufficientQuantityError
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
from character.hero import RpgHero
from components.inventory import ItemNotFoundError, InsufficientQuantityError
from game.items import UseItemError
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

def handle_item_use(hero, item_name, target=None, room=None):
    """Helper function to handle item usage with proper error handling.

    This function tries to use an item either directly on a target or in a room context.

    Args:
        hero: The hero using the item
        item_name: The name of the item to use
        target: Optional target for the item (defaults to hero if not in room context)
        room: Optional room context for environment-specific item usage

    Returns:
        True if the item was used successfully, False otherwise
    """
    try:
        # If a room is specified, try to use the item in room context
        if room is not None:
            room.use_item_in_room(item_name, hero)
            print(f"{hero.name} successfully used {item_name} in {room.name}.")
            return True
        # Otherwise use the item directly on the target
        else:
            return hero.use_item(item_name, target)
    except ItemNotFoundError as e:
        print(f"Cannot use item: {e}")
    except UseItemError as e:
        print(f"Item cannot be used: {e}")
    except ValueError as e:
        print(f"Error using item: {e}")
    except Exception as e:
        print(f"Unexpected error using item: {e}")
    return False
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
