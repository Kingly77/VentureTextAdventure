from __future__ import annotations
import logging
from typing import List, Dict, Optional, TYPE_CHECKING
from components.core_components import HoldComponent
from components.inventory import Inventory, ItemNotFoundError
from game.items import Item
from game.effects.room_effects import (
    RoomDiscEffect,
    NPCDialogEffect,
)  # Import the new RoomEffect base class
from game.room_objs import RoomObject
from interfaces.interface import Combatant  # Import Combatant
from game.npc import NPC

if TYPE_CHECKING:
    from character.hero import RpgHero


class Room:
    """
    Represents a single location or area in the game world.
    A room has a description and can contain items, effects, objects, and NPCs.
    """

    def __init__(self, name: str, description: str, exits=None, link_to=None):
        """
        Initialize a Room.

        Args:
            name: Room name.
            description: Base description for the room.
            exits: Optional pre-populated one-way exits dict, mapping direction -> Room.
            link_to: Optional convenience for declaring bidirectional links at construction time.
                Accepts either:
                  - list/tuple of 3-tuples: [(dir_from_self, other_room, dir_from_other), ...]
                  - dict mapping dir_from_self -> (other_room, dir_from_other)
                This will call link_rooms for each entry.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Room name must be a non-empty string.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Room description must be a non-empty string.")

        self.name = name
        self.base_description = description  # Store original description
        self._components = HoldComponent()
        self._components.add_component("inventory", Inventory())
        self.effects: List[RoomDiscEffect] = []  # List to hold RoomEffect instances
        self.objects: Dict[str, RoomObject] = {}
        self.exits_to = exits if exits else {}
        self.is_locked = False
        self._combatants = []
        # NPCs present in the room, mapped by lowercased name
        self.npcs: Dict[str, NPC] = {}

        # Optionally set up bidirectional links declared at construction time
        if link_to:
            # Support both dict and iterable of triples
            if isinstance(link_to, dict):
                items = [(d, v[0], v[1]) for d, v in link_to.items()]
            else:
                items = list(link_to)
            for entry in items:
                if not isinstance(entry, (list, tuple)) or len(entry) != 3:
                    raise ValueError(
                        "Each link_to entry must be a 3-tuple: (dir_from_self, other_room, dir_from_other)"
                    )
                dir_from_self, other_room, dir_from_other = entry
                # Reuse existing API for validation and linking
                self.link_rooms(str(dir_from_self), other_room, str(dir_from_other))

    def change_description(self, new_description: str):
        """Changes the description of the room."""
        self.base_description = new_description

    def add_exit(self, direction: str, target_room: Room):
        """Adds a ONE-WAY exit from THIS room to a TARGET room."""
        if not isinstance(direction, str) or not direction.strip():
            raise ValueError("Exit direction must be a non-empty string.")
        if not isinstance(target_room, Room):
            raise TypeError("Target room must be a Room instance.")
        self.exits_to[direction] = target_room

    def link_rooms(
        self, direction_from_self: str, other_room: Room, direction_from_other: str
    ):
        """
        Links two rooms bidirectionally.

        Args:
            direction_from_self: The direction to go from THIS room to the OTHER room (e.g., "north").
            other_room: The other Room instance to link to.
            direction_from_other: The direction to go from the OTHER room back to THIS room (e.g., "south").

        Example:
            forest_clearing.link_rooms("north", dark_cave, "south")
            This means:
            - From forest_clearing, going "north" leads to dark_cave.
            - From dark_cave, going "south" leads back to forest_clearing.
        """
        # Create the exit from the current room (self) to the other room
        self.add_exit(direction_from_self, other_room)

        # Create the exit from the other room back to the current room (self)
        other_room.add_exit(direction_from_other, self)

    def unlock(self):
        """Unlocks the room."""
        if self.is_locked:
            self.is_locked = False
        else:
            print(f"[{self.name}] The door is already unlocked.")

    def add_object(self, room_object: RoomObject):
        """Adds an object to this room."""
        if not isinstance(room_object, RoomObject):
            raise TypeError("Only RoomObject instances can be added to a room.")
        if room_object.name in self.objects:
            raise ValueError(
                f"Object '{room_object.name}' is already added to this room."
            )

        self.objects[room_object.name] = room_object

    @property
    def combatants(self) -> List[Combatant]:
        return self._combatants

    @combatants.setter
    def combatants(self, value: Combatant):
        if not isinstance(value, Combatant):
            raise TypeError("Only Combatant instances can be added to a room.")
        self._combatants.append(value)

    @property
    def inventory(self) -> Inventory:
        return self._components["inventory"]

    def add_effect(self, effect: RoomDiscEffect):
        """Adds a RoomEffect to this room."""
        if isinstance(effect, NPCDialogEffect):
            if effect.npc_name in self.npcs:
                raise ValueError(
                    f"The NPC '{effect.npc_name}' is already present in this room."
                )

        self.effects.append(effect)

    def add_npc(self, npc: NPC):
        """Adds an NPC reference to this room."""
        if not isinstance(npc, NPC):
            raise TypeError("Only NPC instances can be added to a room.")
        self.npcs[npc.key()] = npc

    def add_item(self, item: Item):
        self.inventory.add_item(item)
        print(f"[{self.name}] A {item.name} x{item.quantity} has appeared.")

    def remove_item(self, item_name: str, quantity: int = 1) -> Item:
        if not self.inventory.has_component(item_name):
            raise ItemNotFoundError(item_name)

        removed_item = self.inventory.remove_item(item_name, quantity)
        logging.debug(f"[{self.name}] Removed {quantity} of {item_name}.")

        # Notify effects of item removal
        for effect in self.effects:
            if hasattr(
                effect, "on_item_removed"
            ):  # Check if the effect has this method
                effect.on_item_removed(item_name)  # Call the method

        return removed_item

    def interact(
        self,
        verb: str,
        target_name: Optional[str],
        user: RpgHero,
        item: Optional[Item] = None,
        room: Room = None,
    ) -> Optional[str]:
        """
        Tries to interact with this room.
        Returns a message about the outcome.
        """
        vb = (verb or "").lower().strip()
        tgt = (target_name or "").lower().strip()
        for effect in self.effects:
            handler = getattr(effect, f"handle_interaction", None)
            if callable(handler):
                result = handler(vb, tgt, user, item, room)
                if result is not None:
                    return result

        if tgt in self.objects:
            return self.objects[tgt].try_interact(vb, user, item, room)

        if tgt:
            print(f"You try to {vb} the {tgt}, but nothing special happens.")
            return None

        print(f"You try to {vb}, but nothing special happens.")
        return None

    def use_item_in_room(self, item, user: "RpgHero"):
        """
        Tries to use an item within the room context.
        These could be items that affect the room (like a torch or key).

        Args:
            item: The item object to use (can be from hero inventory or the room)
            user: The hero using the item

        Raises:
            ValueError: If the item cannot be used in this room
        """
        item_name = item.name.lower()

        # Determine where the item currently is (hero or room) for potential consumption
        inv_to_consume_from = None
        if user.inventory.has_component(item_name):
            inv_to_consume_from = user.inventory
        elif self.inventory.has_component(item_name):
            inv_to_consume_from = self.inventory

        # Try to let room effects handle the item usage
        handled_by_effect = False
        for effect in self.effects:
            if effect.handle_item_use(item_name, user):
                # Item successfully used by a room effect
                handled_by_effect = True
                # Remove the item if it was used (consumable)
                if (
                    inv_to_consume_from is not None
                    and inv_to_consume_from.has_component(item_name)
                    and inv_to_consume_from[item_name].is_consumable
                ):
                    inv_to_consume_from.remove_item(item_name, 1)
                break

        if not handled_by_effect:
            # If no specific effect handled it
            print(
                f"[{self.name}] {user.name} tries to use the {item_name}, but nothing special happens in this room."
            )
            raise ValueError(
                f"Item '{item_name}' cannot be used in this particular room."
            )
        return False

    def get_description(self) -> str:
        """
        Applies all active room effects to the base description.
        Also includes descriptions of items and objects in the room.
        """
        current_description = self.base_description
        for effect in self.effects:
            current_description = effect.get_modified_description(current_description)

        # Add information about items in the room
        items_in_room = self.inventory.items.values()
        item_list_str = ""
        if items_in_room:
            item_list_str = "\n\nYou see here: " + ", ".join(
                str(item) for item in items_in_room
            )

        # Add information about objects in the room
        objects_in_room = self.objects.values()
        object_list_str = ""
        if objects_in_room:
            object_descriptions = []
            for obj in objects_in_room:
                object_descriptions.append(f"{obj.name}: {obj.description}")
            object_list_str = "\n\nObjects in the room:\n" + "\n".join(
                object_descriptions
            )

        # Add information about NPCs present
        npc_list_str = ""
        if self.npcs:
            npc_descriptions = [
                f"{npc.name}: {npc.short_description}" for npc in self.npcs.values()
            ]
            npc_list_str = "\n\nPeople here:\n" + "\n".join(npc_descriptions)

        return f"{current_description}{item_list_str}{object_list_str}{npc_list_str}"

    def __str__(self) -> str:
        return f"Room: {self.name}"

    def __repr__(self) -> str:
        return f"Room('{self.name}', '{self.base_description}')"
