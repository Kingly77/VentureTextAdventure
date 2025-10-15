from __future__ import annotations
from typing import TYPE_CHECKING

from .base import ItemEffect, Effect, register_effect

if TYPE_CHECKING:
    from game.items import Item


class ItemHealth(ItemEffect):
    def __init__(self, item, amount):
        super().__init__(item)
        self.amount = int(amount)

    def apply_to(self, target):
        amt = max(0, self.amount)
        if hasattr(target, "heal") and callable(getattr(target, "heal")):
            target.heal(amt)
        else:
            # It's better to raise an error than to bypass the intended method.
            raise TypeError(f"Target {target} does not have a heal method.")

    def describe_use(self, actor, target) -> str:
        actor_name = getattr(actor, "name", "Someone")
        item_name = getattr(self.item, "name", "an item")
        if actor is target:
            return f"{actor_name} drinks {item_name} and feels rejuvenated."
        return f"{actor_name} uses {item_name} to restore health to {getattr(target, 'name', 'the target')}."

    def __repr__(self) -> str:
        return f"ItemHealth(amount={self.amount}, item={self.item!r})"

    def __eq__(self, other):
        """Compare ItemHealth effects by their properties."""
        if not isinstance(other, ItemHealth):
            return NotImplemented
        return self.amount == other.amount and self.item == other.item


def _make_item_health(item: "Item", amount: int):
    return ItemHealth(item, amount)


# Register at import time
register_effect(Effect.HEAL, _make_item_health)
