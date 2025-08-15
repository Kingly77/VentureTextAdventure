from typing import TYPE_CHECKING
from game.magic import Spell, NoTargetError
from interfaces.interface import Combatant

if TYPE_CHECKING:
    from components.core_components import Mana


class SpellCastError(Exception):
    """Exception raised when a spell cannot be cast."""
    pass


class SpellNotFoundError(SpellCastError):
    """Exception raised when a spell is not found."""
    def __init__(self, spell_name: str):
        self.spell_name = spell_name
        super().__init__(f"Spell '{spell_name}' doesn't exist.")


class InsufficientManaError(SpellCastError):
    """Exception raised when there is not enough mana to cast a spell."""
    def __init__(self, spell_name: str, cost: int, available: int):
        self.spell_name = spell_name
        self.cost = cost
        self.available = available
        super().__init__(
            f"Not enough mana for '{spell_name}'. Required: {cost}, Available: {available}"
        )


class SpellCastingMix:
    """Mixin providing spell lookup and casting behavior.

    Expects the concrete class to provide:
      - components: a component registry/dict-like with has_component and __getitem__
      - _normalize_name(name: str) -> str
      - get_mana_component() -> Mana
    """

    def get_spell(self, spell_name: str) -> Spell | None:
        """Retrieves a spell by name if it exists and is a Spell.

        Args:
            spell_name: The name of the spell to retrieve

        Returns:
            The spell object or None if not found
        """
        key = self._normalize_name(spell_name)
        if self.components.has_component(key):
            component = self.components[key]
            if isinstance(component, Spell):
                return component
        return None

    def cast_spell(self, spell_name: str, target: Combatant) -> bool:
        """Cast a spell on a target if the hero has enough mana.

        Args:
            spell_name: The name of the spell to cast
            target: The target to cast the spell on

        Returns:
            True if the spell was cast successfully, False otherwise

        Raises:
            SpellNotFoundError: If the spell doesn't exist
            InsufficientManaError: If there's not enough mana
            NoTargetError: If no target is provided
            Exception: Any exception that might be raised by the spell's effect
        """
        spell = self.get_spell(spell_name)
        if not spell:
            print(f"Spell '{spell_name}' doesn't exist.")
            raise SpellNotFoundError(spell_name)

        mana_component = self.get_mana_component()
        current_mana = mana_component.mana
        if current_mana < spell.cost:
            print(f"Not enough mana for '{spell_name}'.")
            raise InsufficientManaError(spell_name, spell.cost, current_mana)

        try:
            # Cast first, then consume mana only if casting succeeds
            spell.cast(target)
            mana_component.consume(spell.cost)
            return True
        except NoTargetError as e:
            print(f"Failed to cast {spell_name}: {e}")
            raise
        except Exception as e:
            print(f"Error occurred while casting {spell_name}: {e}")
            raise
