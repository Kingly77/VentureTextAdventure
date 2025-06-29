from components.core_components import HoldComponent
from components.inventory import Inventory, InsufficientQuantityError, ItemNotFoundError
from game.items import Item
from typing import List, Callable, Dict, Protocol, runtime_checkable

from game.room_objs import RoomObject
from interfaces.interface import Combatant # Import Combatant
from game.room_effects import RoomDiscEffect # Import the new RoomEffect base class


class Room:
    """
    Represents a single location or area in the game world.
    A room has a description and can contain items and effects.
    """
    def __init__(self, name: str, description: str , exits = None):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Room name must be a non-empty string.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Room description must be a non-empty string.")

        self.name = name
        self.base_description = description # Store original description
        self._components = HoldComponent()
        self._components.add_component("inventory", Inventory())
        self.effects: List[RoomDiscEffect] = [] # List to hold RoomEffect instances
        self.objects: Dict[str, RoomObject] = {}
        self.exits_to = exits if exits else {}
        self.is_locked = False
        self._combatants = []


    def add_exit(self, direction: str, target_room: 'Room'):
        """Adds a ONE-WAY exit from THIS room to a TARGET room."""
        if not isinstance(direction, str) or not direction.strip():
            raise ValueError("Exit direction must be a non-empty string.")
        if not isinstance(target_room, Room):
            raise TypeError("Target room must be a Room instance.")
        self.exits_to[direction] = target_room

    def link_rooms(self, direction_from_self: str, other_room: 'Room', direction_from_other: str):
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
            raise ValueError(f"Object '{room_object.name}' is already added to this room.")

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
        self.effects.append(effect)

    def add_item(self, item: Item):
        self.inventory.add_item(item)
        print(f"[{self.name}] A {item.name} x{item.quantity} has appeared.")

    def remove_item(self, item_name: str, quantity: int = 1) -> Item:
        if not self.inventory.has_component(item_name):
            raise ItemNotFoundError(item_name)

        removed_item = self.inventory.remove_item(item_name, quantity)
        print(f"[{self.name}] Removed {quantity} of {item_name}.")

        # Notify effects of item removal
        for effect in self.effects:
            if hasattr(effect, 'on_item_removed'): # Check if the effect has this method
                effect.on_item_removed(item_name) # Call the method

        return removed_item

    def use_item_in_room(self, item, user: 'RpgHero'):
        """
        Tries to use an item from hero's inventory within the room context.
        These could be items that affect the room (like a torch or key).

        Args:
            item_name: The name of the item to use
            user: The hero using the item

        Raises:
            ItemNotFoundError: If the item is not in the inventory
            ValueError: If the item cannot be used in this room
        """
        # Check if the item is in the hero's inventory
        item_name = item.name.lower()

        if not user.inventory.has_component(item_name):
            raise ItemNotFoundError(item_name)

        # Try to let room effects handle the item usage
        handled_by_effect = False
        for effect in self.effects:
            if effect.handle_item_use(item_name, user):
                # Item successfully used by a room effect
                handled_by_effect = True
                # Remove the item if it was used (consumable)
                if user.inventory.has_component(item_name) and user.inventory[item_name].is_consumable:
                    user.inventory.remove_item(item_name, 1)
                break

        if not handled_by_effect:
            # If no specific effect handled it
            print(f"[{self.name}] {user.name} tries to use the {item_name}, but nothing special happens in this room.")
            raise ValueError(f"Item '{item_name}' cannot be used in this particular room.")
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
            item_list_str = "\n\nYou see here: " + ", ".join(str(item) for item in items_in_room)
        
        # Add information about objects in the room
        objects_in_room = self.objects.values()
        object_list_str = ""
        if objects_in_room:
            object_descriptions = []
            for obj in objects_in_room:
                object_descriptions.append(f"{obj.name}: {obj.description}")
            object_list_str = "\n\nObjects in the room:\n" + "\n".join(object_descriptions)
        
        return f"{current_description}{item_list_str}{object_list_str}"

    def __str__(self) -> str:
        return f"Room: {self.name}"

    def __repr__(self) -> str:
        return f"Room('{self.name}', '{self.base_description}')"