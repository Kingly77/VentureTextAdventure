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


def make_effect(
    effect_type: Effect | None, item: "Item", amount: int
) -> Optional["ItemEffect"]:
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

    # New: user-facing description for when this effect is used
    def describe_use(self, actor, target) -> str:
        """Return a user-facing description of using this effect.

        Default is a generic message; concrete effects can override to
        provide richer feedback. The actor/target are typically characters
        with a 'name' attribute.
        """
        actor_name = getattr(actor, "name", "Someone")
        target_name = getattr(target, "name", "the target")
        item_name = getattr(self.item, "name", "an item")
        if actor is target:
            return f"{actor_name} uses {item_name}."
        return f"{actor_name} uses {item_name} on {target_name}."

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.item!r})"
