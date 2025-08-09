from typing import Optional
from character.basecharacter import BaseCharacter
from character.tomes.manamix import ManaMix, XpMix, QuestMix, InventoryViewMix, WalletMix
from components.core_components import Effect, Exp
from components.inventory import ItemNotFoundError
from components.inventory_evil_cousin import QuestAwareInventory
from components.quest_log import QuestLog
from components.wallet import Wallet
from game.items import Item, UseItemError
from game.magic import Spell, NoTargetError
from interfaces.interface import Combatant


class RpgHero(ManaMix, XpMix, QuestMix, InventoryViewMix, WalletMix, BaseCharacter):
    """Hero character class with spells, mana, and inventory."""

    BASE_MANA = 100
    BASE_HEALTH = 100
    MANA_PER_LEVEL = 2
    HEALTH_PER_LEVEL = 5

    def __init__(self, name: str, level: int):
        """Initialize a hero with default attributes and abilities."""
        # Calculate health based on level
        health = self.BASE_HEALTH + (level - 1) * self.HEALTH_PER_LEVEL

        super().__init__(name, level, base_health=health)
        # Cache a quest-aware inventory wrapper to avoid recreating it on each access
        self._inventory_wrapper = QuestAwareInventory(
            self.components["inventory"], self
        )

        # Hero-specific initialization

        self.last_room: Optional["Room"] = None

        self.components.add_component("quests", QuestLog())
        self.components.add_component("xp", Exp(0, 100))
        self.components.add_component("wallet", Wallet(0))
        self._equipped = Item("fists", 0, True, effect=Effect.DAMAGE, effect_value=5)
        self.inventory.add_item(self._equipped)
        print(
            f"{self.name} is a level {self.level} hero with {self.xp} XP, "
            f"{self.mana} mana, and {self.inventory['fists']} in their inventory."
        )
        # Note: initial xp_to_next_level is provided by the Exp component default (100) for level 1

    def __str__(self):
        return f"{self.name} (Level {self.level}, XP {self.xp}, health {self.health}/{self.max_health}, mana {self.mana}/{self.max_mana})"

    def add_xp(self, xp: int):
        """Adds experience points by delegating to the Exp component."""
        self.xp_component.add_xp(self, xp)

    def _normalize_name(self, name: str) -> str:
        """Normalize entity names for consistent lookups."""
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        return name.strip().lower()

    def get_spell(self, spell_name: str) -> Spell | None:
        """Retrieves a spell by name if it exists and is a Spell.

        Args:
            spell_name: The name of the spell to retrieve

        Returns:
            The spell object or None if not found
        """
        key = self._normalize_name(spell_name)
        if self.components.has_component(key):
            component = self.components[key]
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
            super().__init__(
                f"Not enough mana for '{spell_name}'. Required: {cost}, Available: {available}"
            )

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

        mana_component = self.get_mana_component()
        current_mana = mana_component.mana
        if current_mana < spell.cost:
            print(f"Not enough mana for '{spell_name}'.")
            raise self.InsufficientManaError(spell_name, spell.cost, current_mana)

        try:
            # Cast first, then consume mana only if casting succeeds
            spell.cast(target)
            mana_component.consume(spell.cost)
            return True
        except NoTargetError as e:
            print(f"Failed to cast {spell_name}: {e}")
            raise
        except Exception as e:
            print(f"Error occurred while casting {spell_name}: {e}")
            raise

    def use_item(self, item_name: str, target=None):
        """Use an item from the hero's inventory.

        Args:
            item_name: The name of the item to use
            target: Optional target for the item (defaults to self)

        Raises:
            ItemNotFoundError: If the item is not in the inventory
            UseItemError: If the item cannot be used
            TypeError: If item_name is not a string
        """
        if not isinstance(item_name, str):
            raise TypeError("Item name must be string")

        key = self._normalize_name(item_name)

        # Retrieve or raise ItemNotFoundError from inventory directly
        try:
            item = self.inventory[key]
        except ItemNotFoundError:
            raise

        if not item.is_usable:
            print(f"{item_name} cannot be used.")
            raise UseItemError()

        if target is None:
            target = self

        try:
            item.cast(target)
            print(f"{self.name} used {item_name} on {getattr(target, 'name', 'self')}.")

            if item.is_consumable:
                self.inventory.remove_item(key, 1)
            return True
        except Exception as e:
            print(f"Error using {item_name}: {e}")
            raise

