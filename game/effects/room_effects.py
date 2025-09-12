from __future__ import annotations
import logging
from typing import (
    TYPE_CHECKING,
)

from interfaces.room_effect_base import RoomDiscEffect

if TYPE_CHECKING:
    from game.room import Room
    from interfaces.interface import Combatant
    from character.hero import RpgHero


class DarkCaveLightingEffect(RoomDiscEffect):
    """
    Handles dynamic descriptions and torch usage specifically for a dark cave.
    """

    def __init__(self, room: "Room"):
        super().__init__(room)
        self._is_lit = False  # This effect manages its own lighting state

    def handle_enter(self, hero: "RpgHero"):
        """Called when the hero enters the cave."""
        pass

    def get_modified_description(self, base_description: str) -> str:
        """
        Modifies the description based on whether the torch is lit or present.
        """
        if self._is_lit:
            return "The air is still cold, but the flickering light of the torch reveals a tiny, dusty area around you. Shadows dance at the edges of your vision."
        elif not self.room.inventory.has_component("torch"):
            return "The cave entrance is now pitch black. You can barely see your hand in front of your face."
        else:  # Torch is present but not used/lit
            return base_description  # Revert to original if not lit but torch is there

    def handle_item_use(self, verb: str, item_name: str, user: "Combatant") -> bool:
        """
        Handles torch usage in the dark cave.
        """
        if (verb or "").strip().lower() != "use":
            return False
        if item_name.lower() == "torch":
            self._is_lit = True
            print(
                f"[{self.room.name}] {user.name} lights the torch, illuminating a tiny area around you."
            )
            return True  # This effect handled the item use
        return False

    def on_item_removed(self, item_name: str):
        """Called when an item is removed from the room, to update state."""
        logging.debug(f"Item {item_name} removed from room {self.room.name}.")
        if item_name == "torch":
            self._is_lit = False
            print(
                f"[{self.room.name}] The light source is gone, the area grows darker."
            )
