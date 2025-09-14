from __future__ import annotations
import logging
from typing import Callable, TYPE_CHECKING
from interfaces.interface import Combatant, CanCast

if TYPE_CHECKING:
    from character.basecharacter import BaseCharacter

logger = logging.getLogger(__name__)


class SpellError(Exception):
    """Base exception for spell-related errors."""

    pass


class NoTargetError(SpellError):
    """Exception raised when attempting to cast a spell without a target."""

    def __init__(self, spell_name: str):
        self.spell_name = spell_name
        super().__init__(f"No target provided for spell '{spell_name}'.")


class Spell(CanCast):
    """Represents a magical spell that can be cast on a target."""

    def __init__(
        self,
        name: str,
        cost: int,
        caster: "BaseCharacter",
        effect: Callable[[Combatant], None],
    ):
        """Initialize a spell with a name, mana cost, caster, and effect.

        Args:
            name: The name of the spell
            cost: The mana cost to cast the spell
            caster: The character casting the spell
            effect: A callable that implements the spell's effect

        Raises:
            TypeError: If the effect is not callable
        """
        if not callable(effect):
            raise TypeError("Effect must be callable.")
        self.name = name
        self.cost = cost
        self.effect = effect
        self.caster = caster

    def cast(self, target: Combatant) -> None:
        """Casts the spell on the target.

        Args:
            target: The target to cast the spell on

        Raises:
            NoTargetError: If no target is provided,
            Exception: Any exception that might be raised by the effect
        """
        if target is None:
            # Keep raising the same domain error, but log instead of printing
            logger.error("No target provided for %s.", self.name)
            raise NoTargetError(self.name)

        try:
            self.effect(target)
        except Exception as e:
            # Re-raise after logging so upstream handlers can decide
            logger.exception("Error casting %s: %s", self.name, e)
            raise
