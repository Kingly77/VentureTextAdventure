from components.core_components import Mana
from game.magic import Spell


class ManaMix:
    def __init__(self, *args, **kwargs):
        name, level = args
        super().__init__(*args, **kwargs)
        self.components.add_component(
            "mana", Mana(self.BASE_MANA + (level - 1) * self.MANA_PER_LEVEL)
        )
        self.components.add_component(
            "fireball",
            Spell("Fireball", 25, self, lambda target: target.take_damage(25)),
        )
        self.components.add_component(
            "magic_missile",
            Spell("Magic Missile", 5, self, lambda target: target.take_damage(5)),
        )

    def get_mana_component(self) -> Mana:
        """Get the mana component of the hero."""
        return self.components["mana"]

    @property
    def mana(self) -> int:
        """Current mana value from the mana component (provided by mixin)."""
        return self.get_mana_component().mana

    @property
    def max_mana(self) -> int:
        """Maximum mana value from the mana component (provided by mixin)."""
        return self.get_mana_component().max_mana
