from __future__ import annotations
import abc


class CanCast(abc.ABC):
    @abc.abstractmethod
    def cast(self, target: "Combatant"):
        """Abstract method for casting an ability or item on a target."""
        pass


class Combatant(abc.ABC):
    """Abstract base class for any entity that can engage in combat."""

    @abc.abstractmethod
    def take_damage(self, damage: int):
        pass

    @abc.abstractmethod
    def heal(self, amount: int):
        pass

    @property
    @abc.abstractmethod
    def health(self) -> int:
        pass

    @abc.abstractmethod
    def is_alive(self) -> bool:
        pass
