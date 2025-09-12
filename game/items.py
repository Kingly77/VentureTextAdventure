from game.effects.item_effects.item_effects import ItemEffect, Effect
from interfaces.interface import CanCast, Combatant


class UseItemError(Exception):
    def __init__(self):
        super().__init__("Item cannot be used.")


class Item(CanCast):  # Inherit from CanCast
    def __init__(
        self,
        name: str,
        cost: int,
        is_usable: bool = False,
        effect: Effect = Effect.NONE,
        effect_value: int = 0,
        is_consumable: bool = False,
        is_equipment: bool = False,
        tags=None,
        **kwargs,
    ):
        if not isinstance(name, str) or not name:
            raise ValueError("Item name must be a non-empty string.")
        quantity = kwargs.get("quantity", 1)
        if quantity:
            if not isinstance(quantity, int) or quantity < 0:
                raise ValueError("Item quantity must be a non-negative integer.")

        if not isinstance(cost, int) or cost < 0:
            raise ValueError("Item cost must be a non-negative integer.")

        self.name = name
        self.cost = cost
        self.quantity = quantity
        self.is_usable = is_usable
        self.effect_type: Effect = effect
        self.effect_value: int = effect_value
        self.is_consumable = is_consumable
        self.is_equipment = is_equipment
        self.tags = set(tags or [])
        self.effects = {}

    def add_effect(self, effect: Effect, value: ItemEffect):
        self.effects[effect] = value

    def add_tag(self, tag: str):
        self.tags.add(tag)

    def has_tag(self, tag: str):
        return tag in self.tags

    def cast(self, target: Combatant):
        """Applies the item's effect to the target."""

        if self.effect_type == Effect.HEAL:
            target.heal(self.effect_value)
        elif self.effect_type == Effect.DAMAGE:
            target.take_damage(self.effect_value)
        else:
            print(f"Item {self.name} has no castable effect.")
            raise UseItemError()

        # if self.effect_type not in self.effects:
        #     print(f"Item {self.name} has no castable effect.")
        #     raise UseItemError()
        #
        # self.effects[self.effect_type].apply(target)

    def __iadd__(self, quantity: int):
        self.quantity += quantity
        return self

    def __isub__(self, quantity: int):  # Added for decrementing quantity
        self.quantity -= quantity
        return self

    def __str__(self):
        return f"{self.name} x{self.quantity}"

    def __repr__(self):
        return f"Item('{self.name}', cost={self.cost}, qty={self.quantity}, usable={self.is_usable}, effect={self.effect_type.name}, value={self.effect_value})"
