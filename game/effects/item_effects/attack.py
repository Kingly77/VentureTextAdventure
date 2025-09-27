from __future__ import annotations
from typing import TYPE_CHECKING

from .base import ItemEffect, Effect, register_effect

if TYPE_CHECKING:
    from game.items import Item


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

    def describe_use(self, actor, target) -> str:
        actor_name = getattr(actor, "name", "Someone")
        target_name = getattr(target, "name", "the target")
        item_name = getattr(self.item, "name", "an item")
        if actor is target:
            return f"{actor_name} brandishes {item_name} and looks a bit bruised."
        return f"{actor_name} strikes {target_name} with {item_name}, dealing {self.damage} damage."

    def __repr__(self) -> str:
        return f"ItemAttack(damage={self.damage}, item={self.item!r})"


def _make_item_attack(item: "Item", damage: int):
    return ItemAttack(item, damage)


# Register at import time
register_effect(Effect.DAMAGE, _make_item_attack)
