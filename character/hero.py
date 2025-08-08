from typing import Optional
from character.basecharacter import BaseCharacter
from components.core_components import Mana, Effect, Exp
from components.inventory import Inventory, ItemNotFoundError
from components.quest_log import QuestLog
from game.magic import Spell, NoTargetError
from components.wallet import Wallet
from game.underlings.events import Events
from interfaces.interface import Combatant
from game.items import Item, UseItemError


class QuestAwareInventory:
    """Inventory wrapper that handles quest checking."""

    def __init__(self, inventory: Inventory, hero: "RpgHero"):
        self._inventory = inventory
        self._hero = hero

    def add_item(self, item: Item):
        """Add an item and trigger quest-related events.

        Returns the list of event handler results (if any), allowing callers/UI to decide how to display them.
        """
        # Add to the underlying inventory first
        self._inventory.add_item(item)
        # Then trigger item_collected so quests can react. Do not print here.
        Events.trigger_event("item_collected", self._hero, item)

    def __getattr__(self, name):
        """Delegate everything else to the real inventory."""
        return getattr(self._inventory, name)

    def __getitem__(self, item_name: str) -> Item:
        """Handle dictionary-style access like inventory['fists']."""
        return self._inventory[item_name]

    def __repr__(self):
        """Delegate string representation."""
        return repr(self._inventory)


class RpgHero(BaseCharacter):
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
        # self.xp = 0

        self.last_room: Optional["Room"] = None

        # Add hero-specific components
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

    def get_mana_component(self) -> Mana:
        """Get the mana component of the hero."""
        return self.components["mana"]

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

    @property
    def xp_component(self) -> Exp:
        """Get the hero's experience component."""
        return self.components["xp"]

    @property
    def xp_to_next_level(self):
        return self.xp_component.next_lvl

    @xp_to_next_level.setter
    def xp_to_next_level(self, value):
        self.xp_component.next_lvl = value

    @property
    def xp(self) -> int:
        """Get the hero's experience points."""
        return self.components["xp"].exp

    @xp.setter
    def xp(self, value: int):
        """Set the hero's experience points."""
        self.components["xp"].exp = value

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
    def inventory(self) -> QuestAwareInventory:
        """Get quest-aware inventory."""
        return self._inventory_wrapper

    @property
    def wallet(self) -> Wallet:
        """Get the hero's wallet."""
        if not self.components.has_component("wallet"):
            raise ValueError("Hero has no wallet. WHY?")
        return self.components["wallet"]

    @property
    def gold(self) -> int:
        """Get the hero's gold."""
        return self.wallet.balance

    @gold.setter
    def gold(self, value: int):
        """Set the hero's gold."""
        self.wallet._balance = value

    def add_gold(self, amount: int):
        self.wallet.add(amount)

    def spend_gold(self, amount: int):
        self.wallet.spend(amount)
