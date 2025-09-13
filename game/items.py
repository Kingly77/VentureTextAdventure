from game.effects.item_effects.item_effects import ItemEffect, Effect, make_effect
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
        # self.effect_value: int = effect_value
        self.is_consumable = is_consumable
        self.is_equipment = is_equipment
        self.tags = set(tags or [])
        self.effects = {}
        # Only add effect if a concrete ItemEffect is created
        self.add_effect(make_effect(effect, self, effect_value), effect)

    def add_effect(self, value: ItemEffect, effect: Effect):
        # Ignore None to avoid unusable entries for NONE/unknown effects
        if value is None:
            return
        self.effects[effect] = value

    def add_tag(self, tag: str):
        self.tags.add(tag)

    def has_tag(self, tag: str):
        return tag in self.tags

    def cast(self, target: Combatant):
        """Applies the item's effect to the target."""

        effect_impl = self.effects.get(self.effect_type)
        if effect_impl is None:
            print(f"Item {self.name} has no castable effect.")
            raise UseItemError()

        effect_impl.apply_to(target)

    def __iadd__(self, quantity: int):
        self.quantity += quantity
        return self

    def __isub__(self, quantity: int):  # Added for decrementing quantity
        self.quantity -= quantity
        return self

    def __str__(self):
        return f"{self.name} x{self.quantity}"

    def __repr__(self):
        return f"Item('{self.name}', cost={self.cost}, qty={self.quantity}, usable={self.is_usable}, effect={self.effect_type.name})"
