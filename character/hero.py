from character.basecharacter import BaseCharacter
from components.core_components import Mana, Effect
from components.inventory import Inventory, ItemNotFoundError
from components.quest_log import QuestLog
from game.magic import Spell, NoTargetError
from interfaces.interface import Combatant
from game.items import Item, UseItemError


class RpgHero(BaseCharacter):
    """Hero character class with spells, mana, and inventory."""
    BASE_XP_TO_NEXT_LEVEL = 100
    BASE_MANA = 100
    BASE_HEALTH = 100
    MANA_PER_LEVEL = 2
    HEALTH_PER_LEVEL = 5

    def __init__(self, name: str, level: int):
        """Initialize a hero with default attributes and abilities."""
        # Calculate health based on level
        health = self.BASE_HEALTH + (level - 1) * self.HEALTH_PER_LEVEL
        super().__init__(name, level, base_health=health)

        # Hero-specific initialization
        self.xp = 0
        self.xp_to_next_level = self._calculate_xp_to_next_level()

        # Add hero-specific components
        self.components.add_component("mana", Mana(self.BASE_MANA + (level - 1) * self.MANA_PER_LEVEL))
        self.components.add_component("fireball", Spell("Fireball", 25, self, lambda target: target.take_damage(25)))
        self.components.add_component("magic_missile", Spell("Magic Missile", 5, self, lambda target: target.take_damage(5)))
        self.components.add_component("quests",QuestLog())
        self._equipped = Item("fists", 0, True, effect=Effect.DAMAGE, effect_value=5)
        self.inventory.add_item(self._equipped)
        print(
            f"{self.name} is a level {self.level} hero with {self.xp} XP, "
            f"{self.mana} mana, and {self.inventory["fists"]} in their inventory."
        )

    def __str__(self):
        return f"{self.name} (Level {self.level}, XP {self.xp}, health {self.health}/{self.max_health}, mana {self.mana}/{self.max_mana})"

    def _calculate_xp_to_next_level(self) -> int:
        """Calculates the XP required for the next level."""
        return self.BASE_XP_TO_NEXT_LEVEL + (self.level * 50)

    def add_xp(self, xp: int):
        """Adds experience points to the hero and levels up if threshold reached."""
        if xp < 0:
            raise ValueError("XP cannot be negative.")
        self.xp += xp
        while self.xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self):
        """Increases hero's level and updates stats."""
        self.xp -= self.xp_to_next_level
        self.level += 1
        self.xp_to_next_level = self._calculate_xp_to_next_level()
        self.get_mana_component().max_mana = self.BASE_MANA + (self.level - 1) * self.MANA_PER_LEVEL
        self.get_health_component().max_health = self.BASE_HEALTH + (self.level - 1) * self.HEALTH_PER_LEVEL
        print(f"{self.name} leveled up to level {self.level}!")

    def get_mana_component(self) -> Mana:
        """Get the mana component of the hero."""
        return self.components["mana"]

    def get_spell(self, spell_name: str) -> Spell | None:
        """Retrieves a spell by name if it exists and is a Spell.

        Args:
            spell_name: The name of the spell to retrieve

        Returns:
            The spell object or None if not found
        """
        if self.components.has_component(spell_name):
            component = self.components[spell_name]
            if isinstance(component, Spell):
                return component
        return None

    class SpellCastError(Exception):
        """Exception raised when a spell cannot be cast."""
        pass

    class SpellNotFoundError(SpellCastError):
        """Exception raised when a spell is not found."""
        def __init__(self, spell_name: str):
            self.spell_name = spell_name
            super().__init__(f"Spell '{spell_name}' doesn't exist.")

    class InsufficientManaError(SpellCastError):
        """Exception raised when there is not enough mana to cast a spell."""
        def __init__(self, spell_name: str, cost: int, available: int):
            self.spell_name = spell_name
            self.cost = cost
            self.available = available
            super().__init__(f"Not enough mana for '{spell_name}'. Required: {cost}, Available: {available}")

    def cast_spell(self, spell_name: str, target: Combatant) -> bool:
        """Cast a spell on a target if the hero has enough mana.

        Args:
            spell_name: The name of the spell to cast
            target: The target to cast the spell on

        Returns:
            True if the spell was cast successfully, False otherwise

        Raises:
            SpellNotFoundError: If the spell doesn't exist
            InsufficientManaError: If there's not enough mana
            NoTargetError: If no target is provided
            Exception: Any exception that might be raised by the spell's effect
        """
        spell = self.get_spell(spell_name)
        if not spell:
            print(f"Spell '{spell_name}' doesn't exist.")
            raise self.SpellNotFoundError(spell_name)

        current_mana = self.get_mana_component().mana
        if current_mana < spell.cost:
            print(f"Not enough mana for '{spell_name}'.")
            raise self.InsufficientManaError(spell_name, spell.cost, current_mana)

        try:
            self.get_mana_component().consume(spell.cost)
            spell.cast(target)
            return True
        except NoTargetError as e:
            # Re-raise the exception after consuming mana
            # In a real game, you might want to refund the mana here
            print(f"Failed to cast {spell_name}: {e}")
            raise
        except Exception as e:
            # Handle any other exceptions from the spell cast
            print(f"Error occurred while casting {spell_name}: {e}")
            raise

    @property
    def max_mana(self) -> int:
        """Get the maximum mana value."""
        return self.get_mana_component().max_mana

    @property
    def quest_log(self) -> QuestLog:
        """Get the hero's quest log."""
        return self.components["quests"]

    @property
    def mana(self) -> int:
        """Get the current mana value."""
        return self.get_mana_component().mana

    @property
    def inventory(self) -> Inventory:
        """Get the hero's inventory."""
        return self.components["inventory"]


    def use_item(self, item_name: str, target=None):
        """Use an item from the hero's inventory.

        Args:
            item_name: The name of the item to use
            target: Optional target for the item (defaults to self)

        Raises:
            ItemNotFoundError: If the item is not in the inventory
            UseItemError: If the item cannot be used
        """
        if not self.inventory.has_component(item_name.lower()):
            raise ItemNotFoundError(item_name)

        item = self.inventory[item_name.lower()]
        if not item.is_usable:
            print(f"{item_name} cannot be used.")
            raise UseItemError()

        # Default target is self if none provided
        if target is None:
            target = self

        # Use the item on the target
        try:
            item.cast(target)
            print(f"{self.name} used {item_name} on {target.name if hasattr(target, 'name') else 'self'}.")

            # Remove one use of the item
            if item.is_consumable:
                self.inventory.remove_item(item_name.lower(), 1)
            return True
        except Exception as e:
            print(f"Error using {item_name}: {e}")
            raise
