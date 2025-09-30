import logging
from typing import Optional, TYPE_CHECKING, Set

from character.basecharacter import BaseCharacter
from components.core_components import Exp, Mana
from components.inventory_evil_cousin import QuestAwareInventory
from components.quest_log import QuestLog
from components.tags import Tags
from components.wallet import Wallet
from game.effects.item_effects.base import Effect
from game.items import Item, UseItemError
from game.magic import Spell, NoTargetError
from game.underlings.events import Events
from interfaces.interface import Combatant

if TYPE_CHECKING:
    from game.room import Room


class RpgHero(BaseCharacter):
    """
    Hero character class with spells, mana, and inventory.

    A powerful character that can cast spells, manage quests, handle inventory,
    and track their progression through the game world.

    Attributes:
        BASE_MANA (int): Base mana points for a level 1 hero
        BASE_HEALTH (int): Base health points for a level 1 hero
        MANA_PER_LEVEL (int): Additional mana gained per level
        HEALTH_PER_LEVEL (int): Additional health gained per level
    """

    BASE_MANA = 100
    BASE_HEALTH = 100
    MANA_PER_LEVEL = 2
    HEALTH_PER_LEVEL = 5

    class SpellCastError(Exception):
        """Base exception for spell casting errors."""
        pass

    class SpellNotFoundError(SpellCastError):
        """Raised when attempting to cast a non-existent spell."""
        def __init__(self, spell_name: str):
            self.spell_name = spell_name
            super().__init__(f"Spell '{spell_name}' doesn't exist.")

    class InsufficientManaError(SpellCastError):
        """Raised when there's not enough mana to cast a spell."""
        def __init__(self, spell_name: str, cost: int, available: int):
            self.spell_name = spell_name
            self.cost = cost
            self.available = available
            super().__init__(
                f"Not enough mana for '{spell_name}'. Required: {cost}, Available: {available}"
            )

    def __init__(self, name: str, level: int):
        """
        Initialize a hero with default attributes and abilities.

        Args:
            name: The hero's name
            level: The hero's starting level (affects health and mana)

        Raises:
            ValueError: If name is empty or level is less than 1
        """
        if not name or not name.strip():
            raise ValueError("Hero name cannot be empty")
        if level < 1:
            raise ValueError("Hero level must be at least 1")

        # Calculate health based on level
        health = self.BASE_HEALTH + (level - 1) * self.HEALTH_PER_LEVEL

        # Initialize tracking attributes
        self.rooms_visited: Set["Room"] = set()
        self.last_room: Optional["Room"] = None

        # Initialize base character
        super().__init__(name, level, base_health=health)

        # Set up inventory wrapper (cached for performance)
        self._inventory_wrapper = QuestAwareInventory(
            self.components["inventory"], self
        )

        # Register for location events
        Events.add_event("location_entered", self._on_location_entered)

        # Initialize core hero components
        self._initialize_components(level)

        # Set up default equipment
        self._initialize_equipment()

        # Welcome message
        logging.info(
            f"{self.name} is a level {self.level} hero with {self.xp} XP, "
            f"{self.mana} mana, and {self.inventory['fists']} in their inventory."
        )

    def _initialize_components(self, level: int) -> None:
        """Initialize hero-specific components."""
        # Core progression components
        self.components.add_component("quests", QuestLog())
        self.components.add_component("xp", Exp(0, 100))
        self.components.add_component("wallet", Wallet(0))
        self.components.add_component("tags", Tags(tags={"hero"}))

        # Mana system
        base_mana = self.BASE_MANA + (level - 1) * self.MANA_PER_LEVEL
        self.components.add_component("mana", Mana(base_mana))

        # Starter spells
        self._initialize_spells()

    def _initialize_spells(self) -> None:
        """Initialize the hero's starting spells."""
        self.components.add_component(
            "fireball",
            Spell("Fireball", 25, self, lambda target: target.take_damage(25)),
        )
        self.components.add_component(
            "magic_missile",
            Spell("Magic Missile", 5, self, lambda target: target.take_damage(5)),
        )

    def _initialize_equipment(self) -> None:
        """Initialize the hero's default equipment."""
        self._equipped = Item(
            "fists",
            0,
            True,
            effect=Effect.DAMAGE,
            effect_value=5,
            is_equipment=True,
            tags=["weapon"],
        )
        self.inventory.add_item(self._equipped)

    # ========== PROPERTIES ==========

    @property
    def inventory(self) -> QuestAwareInventory:
        """Get the hero's quest-aware inventory."""
        return self._inventory_wrapper

    @property
    def equipped(self) -> Item:
        """Get the currently equipped weapon."""
        return self._equipped

    # ========== EXPERIENCE SYSTEM ==========

    @property
    def xp_component(self) -> Exp:
        """Get the experience component."""
        return self.components["xp"]

    @property
    def xp_to_next_level(self) -> int:
        """Get experience points needed for next level."""
        return self.xp_component.next_lvl

    @xp_to_next_level.setter
    def xp_to_next_level(self, value: int) -> None:
        """Set experience points needed for next level."""
        self.xp_component.next_lvl = value

    @property
    def xp(self) -> int:
        """Get current experience points."""
        return self.components["xp"].exp

    @xp.setter
    def xp(self, value: int) -> None:
        """Set current experience points."""
        if value < 0:
            raise ValueError("Experience points cannot be negative")
        self.components["xp"].exp = value

    def add_xp(self, xp: int) -> None:
        """
        Add experience points to the hero.

        Args:
            xp: Amount of experience to add (must be positive)

        Raises:
            ValueError: If xp is negative
        """
        if xp < 0:
            raise ValueError("Cannot add negative experience points")
        self.xp_component.add_xp(self, xp)

    # ========== MANA SYSTEM ==========

    def get_mana_component(self) -> Mana:
        """Get the mana component."""
        return self.components["mana"]

    @property
    def mana(self) -> int:
        """Get current mana points."""
        return self.get_mana_component().mana

    @property
    def max_mana(self) -> int:
        """Get maximum mana points."""
        return self.get_mana_component().max_mana

    # ========== QUEST SYSTEM ==========

    @property
    def quest_log(self) -> QuestLog:
        """Get the hero's quest log."""
        return self.components["quests"]

    # ========== CURRENCY SYSTEM ==========

    @property
    def wallet(self) -> Wallet:
        """Get the hero's wallet."""
        if not self.components.has_component("wallet"):
            raise ValueError("Hero has no wallet component")
        return self.components["wallet"]

    @property
    def gold(self) -> int:
        """Get current gold amount."""
        return self.wallet.balance

    @gold.setter
    def gold(self, value: int) -> None:
        """Set gold amount directly (use with caution)."""
        if value < 0:
            raise ValueError("Gold amount cannot be negative")
        self.wallet._balance = value

    def add_gold(self, amount: int) -> None:
        """
        Add gold to the hero's wallet.

        Args:
            amount: Amount of gold to add

        Raises:
            ValueError: If amount is negative
        """
        if amount < 0:
            raise ValueError("Cannot add negative gold")
        self.wallet.add(amount)

    def spend_gold(self, amount: int) -> None:
        """
        Spend gold from the hero's wallet.

        Args:
            amount: Amount of gold to spend

        Raises:
            ValueError: If amount is negative or exceeds available gold
        """
        if amount < 0:
            raise ValueError("Cannot spend negative gold")
        self.wallet.spend(amount)

    # ========== UTILITY METHODS ==========

    def __str__(self) -> str:
        """Return a string representation of the hero."""
        return (
            f"{self.name} (Level {self.level}, XP {self.xp}, "
            f"health {self.health}/{self.max_health}, mana {self.mana}/{self.max_mana})"
        )

    def _normalize_name(self, name: str) -> str:
        """
        Normalize entity names for consistent lookups.

        Args:
            name: The name to normalize

        Returns:
            Normalized name (lowercase and stripped)

        Raises:
            TypeError: If name is not a string
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        return name.strip().lower()

    def _on_location_entered(self, _, room: "Room") -> None:
        """
        Handle the location_entered event by updating the set of rooms visited.

        Args:
            _: Unused event parameter
            room: The room that was entered
        """
        if room in self.rooms_visited:
            return
        logging.info(f"{self.name} has entered {room}")
        self.rooms_visited.add(room)

    # ========== ITEM USAGE ==========

    def use_item(self, item_name: str, target: Optional[Combatant] = None) -> bool:
        """
        Use an item from inventory on a target.

        Args:
            item_name: Name of the item to use
            target: Target to use the item on (defaults to self)

        Returns:
            True if item was used successfully

        Raises:
            TypeError: If item_name is not a string
            ItemNotFoundError: If item is not in inventory
            UseItemError: If item cannot be used
        """
        from components.inventory import ItemNotFoundError

        if not isinstance(item_name, str):
            raise TypeError("Item name must be string")

        key = self._normalize_name(item_name)
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

    # ========== SPELL CASTING ==========

    def get_spell(self, spell_name: str) -> Optional[Spell]:
        """
        Get a spell by name.

        Args:
            spell_name: Name of the spell to retrieve

        Returns:
            The spell component if found, None otherwise
        """
        key = self._normalize_name(spell_name)
        if self.components.has_component(key):
            component = self.components[key]
            if isinstance(component, Spell):
                return component
        return None

    def cast_spell(self, spell_name: str, target: Combatant) -> bool:
        """
        Cast a spell on a target.

        Args:
            spell_name: Name of the spell to cast
            target: Target to cast the spell on

        Returns:
            True if spell was cast successfully

        Raises:
            SpellNotFoundError: If spell doesn't exist
            InsufficientManaError: If not enough mana
            NoTargetError: If target is invalid
        """
        spell = self.get_spell(spell_name)
        if not spell:
            print(f"Spell '{spell_name}' doesn't exist.")
            raise RpgHero.SpellNotFoundError(spell_name)

        mana_component = self.get_mana_component()
        current_mana = mana_component.mana
        if current_mana < spell.cost:
            print(f"Not enough mana for '{spell_name}'.")
            raise RpgHero.InsufficientManaError(spell_name, spell.cost, current_mana)

        try:
            spell.cast(target)
            mana_component.consume(spell.cost)
            return True
        except NoTargetError as e:
            print(f"Failed to cast {spell_name}: {e}")
            raise
        except Exception as e:
            print(f"Error occurred while casting {spell_name}: {e}")
            raise

    # ========== COMBAT SYSTEM ==========

    def is_weapon(self, item: Item) -> bool:
        """
        Check if an item can be used as a weapon.

        Args:
            item: Item to check

        Returns:
            True if the item can be used as a weapon
        """
        if item is None:
            return False
        return (
            getattr(item, "is_equipment", False)
            or item.has_tag("weapon")
            or getattr(item, "effect_type", None) == Effect.DAMAGE
        )

    def equip(self, item_name: str) -> bool:
        """
        Equip a weapon from inventory.

        Args:
            item_name: Name of the weapon to equip

        Returns:
            True if weapon was equipped successfully
        """
        name = self._normalize_name(item_name)
        if not self.inventory.has_component(name):
            print(f"You don't have a '{item_name}'.")
            return False

        item = self.inventory[name]
        if not self.is_weapon(item):
            print(f"'{item_name}' is not a weapon.")
            return False

        self._equipped = item
        print(f"Equipped {item.name}.")
        return True

    def attack(self, target: Combatant, weapon_name: Optional[str] = None) -> None:
        """
        Attack a target using the equipped weapon.

        Args:
            target: Target to attack
            weapon_name: Optional weapon to equip before attacking

        Raises:
            ValueError: If target is None or no weapon is equipped
        """
        if target is None:
            raise ValueError(f"{self.name} tried to attack, but no target was provided.")

        # If a specific weapon name is given, attempt to equip it
        if weapon_name:
            self.equip(weapon_name)

        weapon = self._equipped
        if weapon is None:
            raise ValueError(f"{self.name} has no weapon equipped.")

        try:
            weapon.cast(target)
        except UseItemError:
            raise ValueError(f"{weapon.name} cannot be used to attack.")
