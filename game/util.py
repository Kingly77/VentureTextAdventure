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
