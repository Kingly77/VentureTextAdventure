from __future__ import annotations
import abc
import enum


class Effect(enum.Enum):
    HEAL = 1
    DAMAGE = 2
    NONE = 3


effect_reg = {}


class ItemEffect(abc.ABC):
    def __init__(self, item: "Item"):
        self.item = item


class ItemAttack:
    def __init__(self, item: "Item", amount: int):
        super().__init__(item)
        self.damage = amount

    def apply_to(self, target):
        target.take_damage(self.damage)


class ItemHealth(ItemEffect):
    def __init__(self, item, amount):
        super().__init__(item)
        self.amount = amount

    def apply_to(self, target):
        target.health += self.amount


def _make_item_attack(item: int, damage: int):
    return ItemAttack(damage)
    pass


effect_reg[Effect.HEAL] = ItemHealth
effect_reg[Effect.DAMAGE] = _make_item_attack
