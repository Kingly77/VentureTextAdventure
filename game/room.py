from components.core_components import HoldComponent
from components.inventory import Inventory, InsufficientQuantityError, ItemNotFoundError
from game.items import Item
from typing import List, Optional, Dict
from interfaces.interface import Combatant # Import Combatant
from .room_effects import RoomEffect # Import the new RoomEffect base class

class Room:
    """
    Represents a single location or area in the game world.
    A room has a description and can contain items and effects.
    """
    def __init__(self, name: str, description: str):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Room name must be a non-empty string.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Room description must be a non-empty string.")

        self.name = name
        self.base_description = description # Store original description
        self._components = HoldComponent()
        self._components.add_component("inventory", Inventory())
        self.effects: List[RoomEffect] = [] # List to hold RoomEffect instances

    @property
    def inventory(self) -> Inventory:
        return self._components["inventory"]

    def add_effect(self, effect: RoomEffect):
        """Adds a RoomEffect to this room."""
        self.effects.append(effect)

    def add_item(self, item: Item):
        self.inventory.add_item(item)
        print(f"[{self.name}] A {item.name} x{item.quantity} has appeared.")

    def remove_item(self, item_name: str, quantity: int = 1) -> Item:
        # ... (existing remove_item logic) ...
        if not self.inventory.has_component(item_name):
            raise ItemNotFoundError(item_name)

        original_item = self.inventory[item_name]
        if quantity > original_item.quantity:
            raise InsufficientQuantityError(item_name, quantity, original_item.quantity)

        removed_item = Item(original_item.name, original_item.cost, original_item.is_usable,
                            original_item.effect_type, original_item.effect_value)
        removed_item.quantity = quantity

        self.inventory.remove_item(item_name, quantity)
        print(f"[{self.name}] Removed {quantity} of {item_name}.")

        # Notify effects about item removal
        for effect in self.effects:
            if hasattr(effect, 'on_item_removed'): # Check if effect has this method
                effect.on_item_removed(item_name) # Call the method

        return removed_item

    def use_item_in_room(self, item_name: str, user: 'Combatant'):
        """
        Delegates item usage to attached RoomEffects.
        """
        if not self.inventory.has_component(item_name):
            raise ItemNotFoundError(item_name)

        handled_by_effect = False
        for effect in self.effects:
            if effect.handle_item_use(item_name, user):
                handled_by_effect = True
                break # Assume only one effect can "handle" a specific item use

        if not handled_by_effect:
            # If no specific effect handled it, maybe a generic message or error
            print(f"[{self.name}] You try to use the {item_name}, but nothing happens here.")
            raise ValueError(f"Item '{item_name}' cannot be used in this room.")


    def get_description(self) -> str:
        """
        Applies all active room effects to the base description.
        """
        current_description = self.base_description
        for effect in self.effects:
            current_description = effect.get_modified_description(current_description)

        items_in_room = self.inventory.items.values()
        item_list_str = ""
        if items_in_room:
            item_list_str = "\n\nYou see here: " + ", ".join(str(item) for item in items_in_room)
        return f"{current_description}{item_list_str}"

    def __str__(self) -> str:
        return f"Room: {self.name}"

    def __repr__(self) -> str:
        return f"Room('{self.name}', '{self.base_description}')"