import logging
from typing import Optional, TYPE_CHECKING
from character.basecharacter import BaseCharacter
from character.tomes import (
    ManaMix,
    XpMix,
    QuestMix,
    InventoryViewMix,
    WalletMix,
    SpellCastingMix,
    ItemUsageMix,
)
from components.core_components import Exp
from game.effects.item_effects.item_effects import Effect
from components.inventory import ItemNotFoundError
from components.inventory_evil_cousin import QuestAwareInventory
from components.quest_log import QuestLog
from components.tags import Tags
from components.wallet import Wallet
from game.items import Item, UseItemError
from game.magic import Spell, NoTargetError
from game.underlings.events import Events
from interfaces.interface import Combatant

if TYPE_CHECKING:
    from game.room import Room


class RpgHero(
    SpellCastingMix,
    ItemUsageMix,
    ManaMix,
    XpMix,
    QuestMix,
    InventoryViewMix,
    WalletMix,
    BaseCharacter,
):
    """Hero character class with spells, mana, and inventory."""

    BASE_MANA = 100
    BASE_HEALTH = 100
    MANA_PER_LEVEL = 2
    HEALTH_PER_LEVEL = 5

    def __init__(self, name: str, level: int):
        """Initialize a hero with default attributes and abilities."""
        # Calculate health based on level
        health = self.BASE_HEALTH + (level - 1) * self.HEALTH_PER_LEVEL
        self.rooms_vistited = set()

        super().__init__(name, level, base_health=health)
        # Cache a quest-aware inventory wrapper to avoid recreating it on each access
        self._inventory_wrapper = QuestAwareInventory(
            self.components["inventory"], self
        )

        Events.add_event("location_entered", self._on_location_entered)

        # Hero-specific initialization

        self.last_room: Optional[Room] = None

        self.components.add_component("quests", QuestLog())
        self.components.add_component("xp", Exp(0, 100))
        self.components.add_component("wallet", Wallet(0))
        self.components.add_component("tags", Tags(tags={"hero"}))
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
        print(
            f"{self.name} is a level {self.level} hero with {self.xp} XP, "
            f"{self.mana} mana, and {self.inventory['fists']} in their inventory."
        )

    def __str__(self):
        return f"{self.name} (Level {self.level}, XP {self.xp}, health {self.health}/{self.max_health}, mana {self.mana}/{self.max_mana})"

    def _on_location_entered(self, _, room: "Room"):
        """Handle the location_entered event by updating the set of rooms visited."""
        if room in self.rooms_vistited:
            return
        logging.info(f"{self.name} has entered {room}")
        self.rooms_vistited.add(room)

    @property
    def equipped(self) -> Item:
        return self._equipped

    def add_xp(self, xp: int):
        """Adds experience points by delegating to the Exp component."""
        self.xp_component.add_xp(self, xp)

    def _normalize_name(self, name: str) -> str:
        """Normalize entity names for consistent lookups."""
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        return name.strip().lower()

    def is_weapon(self, item: Item) -> bool:
        if item is None:
            return False
        # Consider as weapon if tagged, marked equipment, or deals DAMAGE
        return (
            getattr(item, "is_equipment", False)
            or item.has_tag("weapon")
            or getattr(item, "effect_type", None) == Effect.DAMAGE
        )

    def equip(self, item_name: str) -> bool:
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

    def attack(self, target: Combatant, weapon_name: str | None = None):
        """Attack using the currently equipped weapon. If a weapon name is provided, try to equip it first."""
        if target is None:
            raise ValueError(
                f"{self.name} tried to attack, but no target was provided."
            )

        # If a specific weapon name is given, attempt to equip it (keeps backwards compatibility)
        if weapon_name:
            self.equip(weapon_name)

        weapon = self._equipped
        if weapon is None:
            raise ValueError(f"{self.name} has no weapon equipped.")

        try:
            weapon.cast(target)
        except UseItemError:
            raise ValueError(f"{weapon.name} cannot be used to attack.")
