from abc import ABC, abstractmethod
from typing import TYPE_CHECKING # For type hinting without circular imports

if TYPE_CHECKING:
    from game.room import Room
    from interfaces.interface import Combatant # Assuming Combatant is in interfaces/interface.py

class RoomDiscEffect(ABC):
    """
    Abstract base class for effects that can modify a Room's description
    or behavior.
    """
    def __init__(self, room: 'Room'):
        self.room = room

    @abstractmethod
    def get_modified_description(self, base_description: str) -> str:
        """
        Returns a description modified by this effect.
        """
        pass

    def handle_item_use(self, item_name: str, user: 'Combatant') -> bool:
        """
        Handles the effect of using an item within the room.
        Returns True if the item use was handled by this effect, False otherwise.
        """
        return False # By default, effects don't handle item use


class DarkCaveLightingEffect(RoomDiscEffect):
    """
    Handles dynamic descriptions and torch usage specifically for a dark cave.
    """
    def __init__(self, room: 'Room'):
        super().__init__(room)
        self._is_lit = False # This effect manages its own lighting state

    def get_modified_description(self, base_description: str) -> str:
        """
        Modifies the description based on whether the torch is lit or present.
        """
        if self._is_lit:
            return "The air is still cold, but the flickering light of the torch reveals a tiny, dusty area around you. Shadows dance at the edges of your vision."
        elif not self.room.inventory.has_component("torch"):
            return "The cave entrance is now pitch black. You can barely see your hand in front of your face."
        else: # Torch is present but not used/lit
            return base_description # Revert to original if not lit but torch is there

    def handle_item_use(self, item_name: str, user: 'Combatant') -> bool:
        """
        Handles torch usage in the dark cave.
        """
        if item_name.lower() == "torch":
            self._is_lit = True
            print(f"[{self.room.name}] {user.name} lights the torch, illuminating a tiny area around you.")
            return True # This effect handled the item use
        return False

    def on_item_removed(self, item_name: str):
        """Called when an item is removed from the room, to update state."""
        if item_name == "torch" and not self.room.inventory.has_component("torch"):
            self._is_lit = False
            print(f"[{self.room.name}] The light source is gone, the area grows darker.")




class BashDoorEffect(RoomDiscEffect):


    def __init__(self, room: 'Room'):
        super().__init__(room)
        self.door_is_open = False
        self._this_room = room


    def get_modified_description(self, base_description: str) -> str:
        if self.door_is_open:
            return base_description + "\n\nThe door is open and a giant bashing sound is heard."
        else:
            return base_description + "\n\nThe door is locked."


    def handle_item_use(self, item_name: str, user: 'Combatant') -> bool:
        if item_name.lower() == "sword":
            print(f"[{self.room.name}] The door swings open, and a giant bashing sound is heard.")
            self.door_is_open = True
            for exits in self._this_room.exits_to.values():
                if exits.name == "Foyer":
                    exits.is_locked = False
                    return True
        return False
