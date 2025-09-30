import logging
from typing import Optional, TYPE_CHECKING, Set

from character.basecharacter import BaseCharacter
from character.tomes import (
    ManaMix,
    XpMix,
    QuestMix,
    InventoryViewMix,
    WalletMix,
    SpellCastingMix,
    ItemUsageMix,
    SpellCastError,
    SpellNotFoundError,
    InsufficientManaError,
)
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


class RpgHero(
    ManaMix,
    XpMix,
    QuestMix,
    InventoryViewMix,
    WalletMix,
    SpellCastingMix,
    ItemUsageMix,
    BaseCharacter,
):
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
    def equipped(self) -> Item:
        """Get the currently equipped weapon."""
        return self._equipped

    # ========== EXPERIENCE SYSTEM ==========

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
