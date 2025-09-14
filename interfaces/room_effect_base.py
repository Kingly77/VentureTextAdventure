from __future__ import annotations
from abc import ABC
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from interfaces.interface import Combatant
    from character.hero import RpgHero
    from game.items import Item
    from game.room import Room


class RoomDiscEffect(ABC):
    """
    Abstract base class for effects that can modify a Room's description
    or behavior, split into its own file to avoid circular imports.
    """

    def __init__(self, room: "Room"):
        self.room = room

    def get_modified_description(self, base_description: str) -> str:
        """
        Returns a description modified by this effect.
        """
        return base_description

    # Optional hooks; default no-op/False
    def handle_take(self, hero: "RpgHero", item_name: str):
        return False

    def handle_drop(self, hero: "RpgHero", item_name: str):
        return False

    def handle_item_use(self, verb: str, item_name: str, user: "Combatant") -> bool:
        return False

    def handle_enter(self, val_hero: "RpgHero"):
        return False

    def handle_help(self, val_hero: "RpgHero"):
        return "No help available for this room."

    def handle_interaction(
        self,
        verb: str,
        target_name: Optional[str],
        val_hero: "Combatant",
        item: Optional["Item"],
        room: "Room",
    ) -> Optional[str]:
        return None
