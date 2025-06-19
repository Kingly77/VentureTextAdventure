from character.basecharacter import BaseCharacter
from components.core_components import Effect
from game.items import Item
from game.magic import Spell
from interfaces.interface import Combatant


class Goblin(BaseCharacter):
    """Goblin enemy class."""
    def __init__(self, name: str, level: int):
        """Initialize a goblin with default attributes."""
        super().__init__(name, level, base_health=100, xp_value=100)
        self.components["inventory"].add_item(Item("sword", 0, True, effect=Effect.DAMAGE, effect_value=10))

    @property
    def sword(self) -> Item:
        """Returns the goblin's sword item."""
        return self.components["inventory"]["sword"]

    def attack(self, target: Combatant, weapon_name: str = "sword"):
        """Goblin attacks a target with its sword."""
        super().attack(target, weapon_name)


class Troll(BaseCharacter):
    """Troll enemy class with regeneration ability."""
    def __init__(self, name: str, level: int):
        """Initialize a troll with default attributes."""
        super().__init__(name, level, base_health=250, xp_value=150)
        # Trolls have natural regeneration and a different attack
        self.components.add_component("claws", Item("Troll Claws", 0, True, effect=Effect.DAMAGE, effect_value=20))
        # Special regeneration ability
        self.components.add_component("regeneration", Spell("Regenerate", 0, self, lambda target: target.heal(15)))

    @property
    def claws(self) -> Item:
        """Returns the troll's claws item."""
        return self.components["claws"]

    def attacks(self, target: Combatant):
        """Troll attacks a target with its claws."""
        try:
            self.attack(target, "claws")
        except ValueError as e:
            print(str(e))

    def regenerate(self):
        """Troll uses its regeneration ability to heal itself."""
        try:
            print(f"{self.name} regenerates some health!")
            self.attack(self, "regeneration")
        except ValueError as e:
            print(str(e))