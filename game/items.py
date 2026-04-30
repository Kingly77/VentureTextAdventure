from game.effects.item_effects.base import ItemEffect, Effect, make_effect
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
        effects: dict | None = None,
        stackable: bool | None = None,
        **kwargs,  # absorb legacy quantity= kwarg
    ):
        if not isinstance(name, str) or not name:
            raise ValueError("Item name must be a non-empty string.")
        if not isinstance(cost, int) or cost < 0:
            raise ValueError("Item cost must be a non-negative integer.")

        self.name = name
        self.cost = cost
        self.is_usable = is_usable
        self.effect_type: Effect = effect
        self.is_consumable = is_consumable
        self.is_equipment = is_equipment
        self.tags = set(tags or [])
        self.stackable = stackable if stackable is not None else not is_equipment

        if effects is not None:
            self.effects = dict(effects)
        else:
            self.effects = {}
            self.add_effect(make_effect(effect, self, effect_value), effect)

    def add_effect(self, value: ItemEffect, effect: Effect):
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

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Item('{self.name}', cost={self.cost}, usable={self.is_usable}, effect={self.effect_type.name})"

    def __eq__(self, other):
        if not isinstance(other, Item):
            return NotImplemented
        return (
            self.name == other.name
            and self.cost == other.cost
            and self.is_usable == other.is_usable
            and self.effect_type == other.effect_type
            and self.is_consumable == other.is_consumable
            and getattr(self, "is_equipment", False)
            == getattr(other, "is_equipment", False)
            and set(self.tags or []) == set(other.tags or [])
            and self.effects.keys() == other.effects.keys()
            and all(
                type(self.effects[k]) == type(other.effects[k])
                and self.effects[k] == other.effects[k]
                for k in self.effects.keys()
            )
        )

    def __hash__(self):
        return hash((self.name, self.cost, self.effect_type))
