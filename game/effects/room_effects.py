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

    def get_new_description(self, base_description: str) -> str | None:
        """
        Provide a full replacement description when it's too dark to see or
        when lighting reveals the original base description.
        """
        # If no torch is present and it's not lit, override with darkness
        if not self._is_lit and not self.room.inventory.has_component("torch"):
            return "It is pitch black here. You can barely see your hand in front of your face."

        # If a torch has been lit, we reveal the base description (no total override)
        if self._is_lit:
            return base_description

        # Otherwise, keep the base description untouched
        return None

    def get_modified_description(self, base_description: str) -> str | None:
        """
        Add descriptive fragments based on the lighting state.
        """
        # Torch lit: add a lighting fragment to enrich the base description
        if self._is_lit:
            return (
                "The air is still cold, but the flickering light of the torch reveals a tiny, "
                "dusty area around you. Shadows dance at the edges of your vision."
            )

        # When dark due to no torch, we've already fully overridden via get_new_description
        return None

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
