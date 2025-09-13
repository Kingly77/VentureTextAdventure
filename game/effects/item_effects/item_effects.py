from __future__ import annotations
import abc
import enum
from typing import Callable, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.items import Item


class Effect(enum.Enum):
    HEAL = 1
    DAMAGE = 2
    NONE = 3


# Registry mapping effect kinds to factories
_effect_reg: Dict[Effect, Callable[["Item", int], "ItemEffect"]] = {}


def register_effect(kind: Effect, factory: Callable[["Item", int], "ItemEffect"]):
    """Register a factory for an item effect kind."""
    _effect_reg[kind] = factory


def make_effect(effect_type: Effect | None, item: "Item", amount: int) -> Optional["ItemEffect"]:
    """Create an ItemEffect instance, or None if not applicable.

    - Returns None for Effect.NONE or unknown kinds to signal 'no effect'.
    - Avoids raising KeyError for unregistered kinds.
    """
    if effect_type is None or effect_type == Effect.NONE:
        return None
    factory = _effect_reg.get(effect_type)
    if factory is None:
        return None
    return factory(item, amount)


class ItemEffect(abc.ABC):
    def __init__(self, item: "Item"):
        self.item = item

    @abc.abstractmethod
    def apply_to(self, target):
        """Apply this effect to the target."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.item!r})"


class ItemAttack(ItemEffect):
    def __init__(self, item: "Item", amount: int):
        super().__init__(item)
        self.damage = int(amount)

    def apply_to(self, target):
        dmg = max(0, self.damage)
        # Prefer a typed API if available
        if hasattr(target, "take_damage") and callable(getattr(target, "take_damage")):
            target.take_damage(dmg)
        elif hasattr(target, "health"):
            # Fallback to directly adjusting health when no API exists
            try:
                target.health -= dmg
            except Exception:
                # Best-effort fallback; ignore if unsupported
                pass

    def __repr__(self) -> str:
        return f"ItemAttack(damage={self.damage}, item={self.item!r})"


class ItemHealth(ItemEffect):
    def __init__(self, item, amount):
        super().__init__(item)
        self.amount = int(amount)

    def apply_to(self, target):
        amt = max(0, self.amount)
        if hasattr(target, "heal") and callable(getattr(target, "heal")):
            target.heal(amt)
        elif hasattr(target, "health"):
            try:
                target.health += amt
            except Exception:
                pass

    def __repr__(self) -> str:
        return f"ItemHealth(amount={self.amount}, item={self.item!r})"


def _make_item_attack(item: "Item", damage: int):
    return ItemAttack(item, damage)


def _make_item_health(item: "Item", amount: int):
    return ItemHealth(item, amount)


register_effect(Effect.HEAL, _make_item_health)
register_effect(Effect.DAMAGE, _make_item_attack)
