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
from components.core_components import Effect, Exp
from components.inventory import ItemNotFoundError
from components.inventory_evil_cousin import QuestAwareInventory
from components.quest_log import QuestLog
from components.wallet import Wallet
from game.items import Item, UseItemError
from game.magic import Spell, NoTargetError
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

        super().__init__(name, level, base_health=health)
        # Cache a quest-aware inventory wrapper to avoid recreating it on each access
        self._inventory_wrapper = QuestAwareInventory(
            self.components["inventory"], self
        )

        # Hero-specific initialization

        self.last_room: Optional[Room] = None

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
