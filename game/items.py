from components.core_components import Effect
from interfaces.interface import CanCast, Combatant


class UseItemError(Exception):
    def __init__(self):
        super().__init__("Item cannot be used.")


class Item(CanCast): # Inherit from CanCast
    def __init__(self, name: str, cost: int, is_usable: bool = False, effect: Effect = Effect.NONE, effect_value: int = 0, is_consumable: bool = False , **kwargs):
        self.name = name
        self.cost = cost
        self.quantity = kwargs.get("quantity", 1)
        self.is_usable = is_usable
        self.effect_type: Effect = effect
        self.effect_value = effect_value
        self.is_consumable = is_consumable

    def cast(self, target: Combatant):
        """Applies the item's effect to the target."""
        if self.effect_type == Effect.HEAL:
            target.heal(self.effect_value)
        elif self.effect_type == Effect.DAMAGE:
            target.take_damage(self.effect_value)
        else:
            print(f"Item {self.name} has no castable effect.")
            raise UseItemError()

    def __iadd__(self, quantity: int):
        self.quantity += quantity
        return self

    def __isub__(self, quantity: int): # Added for decrementing quantity
        self.quantity -= quantity
        return self

    def __str__(self):
        return f"{self.name} x{self.quantity}"

    def __repr__(self):
        return f"Item('{self.name}', cost={self.cost}, qty={self.quantity}, usable={self.is_usable}, effect={self.effect_type.name}, value={self.effect_value})"
