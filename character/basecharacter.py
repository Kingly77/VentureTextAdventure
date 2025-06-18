from components.core_components import HoldComponent, Health
from interfaces.interface import Combatant


class BaseCharacter(Combatant):
    """Base class for all characters in the game."""
    def __init__(self, name: str, level: int, base_health: int, xp_value: int = 0):
        """Initialize a base character with common attributes.

        Args:
            name: Character's name
            level: Character's level
            base_health: Base health points
            xp_value: Experience points awarded when defeated
        """
        self.name = name
        self.level = level
        self.xp_value = xp_value
        self.components = HoldComponent()
        self.components.add_component("health", Health(base_health))

    def get_health_component(self) -> Health:
        """Get the health component of the character."""
        return self.components["health"]

    def take_damage(self, damage: int):
        """Take damage, reducing health."""
        self.get_health_component().take_damage(damage)

    def heal(self, amount: int):
        """Heal the character, increasing health."""
        self.get_health_component().heal(amount)

    def is_alive(self) -> bool:
        """Check if the character is alive."""
        return self.get_health_component().health > 0

    @property
    def health(self) -> int:
        """Get the current health value."""
        return self.get_health_component().health

    def attack(self, target: Combatant, weapon_name: str):
        """Generic attack method using a specified weapon component.

        Args:
            target: The target to attack
            weapon_name: The name of the weapon component to use

        Raises:
            ValueError: If target is None or weapon doesn't exist
        """
        if target is None:
            raise ValueError(f"{self.name} tried to attack, but no target was provided.")

        if not self.components.has_component(weapon_name):
            raise ValueError(f"{self.name} doesn't have a {weapon_name} to attack with.")

        self.components[weapon_name].cast(target)
