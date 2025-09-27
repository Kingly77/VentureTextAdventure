import logging
from typing import Optional, TYPE_CHECKING

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
    """Hero character class with spells, mana, and inventory. Simplified hierarchy with composition."""

    BASE_MANA = 100
    BASE_HEALTH = 100
    MANA_PER_LEVEL = 2
    HEALTH_PER_LEVEL = 5

    class SpellCastError(Exception):
        pass

    class SpellNotFoundError(SpellCastError):
        def __init__(self, spell_name: str):
            self.spell_name = spell_name
            super().__init__(f"Spell '{spell_name}' doesn't exist.")

    class InsufficientManaError(SpellCastError):
        def __init__(self, spell_name: str, cost: int, available: int):
            self.spell_name = spell_name
            self.cost = cost
            self.available = available
            super().__init__(
                f"Not enough mana for '{spell_name}'. Required: {cost}, Available: {available}"
            )

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

        # Core components
        self.components.add_component("quests", QuestLog())
        self.components.add_component("xp", Exp(0, 100))
        self.components.add_component("wallet", Wallet(0))
        self.components.add_component("tags", Tags(tags={"hero"}))

        # Mana and starter spells (was in ManaMix)
        base_mana = self.BASE_MANA + (level - 1) * self.MANA_PER_LEVEL
        self.components.add_component("mana", Mana(base_mana))
        self.components.add_component(
            "fireball",
            Spell("Fireball", 25, self, lambda target: target.take_damage(25)),
        )
        self.components.add_component(
            "magic_missile",
            Spell("Magic Missile", 5, self, lambda target: target.take_damage(5)),
        )

        # Default equipped weapon
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

    # Inventory view wrapper (InventoryViewMix)
    @property
    def inventory(self) -> QuestAwareInventory:
        return self._inventory_wrapper

    # XP properties (XpMix)
    @property
    def xp_component(self) -> Exp:
        return self.components["xp"]

    @property
    def xp_to_next_level(self):
        return self.xp_component.next_lvl

    @xp_to_next_level.setter
    def xp_to_next_level(self, value):
        self.xp_component.next_lvl = value

    @property
    def xp(self) -> int:
        return self.components["xp"].exp

    @xp.setter
    def xp(self, value: int):
        self.components["xp"].exp = value

    def add_xp(self, xp: int):
        """Adds experience points by delegating to the Exp component."""
        self.xp_component.add_xp(self, xp)

    # Mana helpers (ManaMix)
    def get_mana_component(self) -> Mana:
        return self.components["mana"]

    @property
    def mana(self) -> int:
        return self.get_mana_component().mana

    @property
    def max_mana(self) -> int:
        return self.get_mana_component().max_mana

    # Quest log (QuestMix)
    @property
    def quest_log(self) -> QuestLog:
        return self.components["quests"]

    # Wallet helpers (WalletMix)
    @property
    def wallet(self) -> Wallet:
        if not self.components.has_component("wallet"):
            raise ValueError("Hero has no wallet. WHY?")
        return self.components["wallet"]

    @property
    def gold(self) -> int:
        return self.wallet.balance

    @gold.setter
    def gold(self, value: int):
        self.wallet._balance = value

    def add_gold(self, amount: int):
        self.wallet.add(amount)

    def spend_gold(self, amount: int):
        self.wallet.spend(amount)

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

    def _normalize_name(self, name: str) -> str:
        """Normalize entity names for consistent lookups."""
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        return name.strip().lower()

    # Item usage (ItemUsageMix)
    def use_item(self, item_name: str, target=None):
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

    # Spells (SpellCastingMix)
    def get_spell(self, spell_name: str) -> Spell | None:
        key = self._normalize_name(spell_name)
        if self.components.has_component(key):
            component = self.components[key]
            if isinstance(component, Spell):
                return component
        return None

    def cast_spell(self, spell_name: str, target: Combatant) -> bool:
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
