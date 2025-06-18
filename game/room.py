from components.core_components import HoldComponent
from components.inventory import Inventory, InsufficientQuantityError, ItemNotFoundError
from game.items import Item
from interfaces.interface import Combatant


class Room:
    """
    Represents a single location or area in the game world.
    A room has a description and can contain items.
    """
    def __init__(self, name: str, description: str):
        """
        Initializes a new Room.

        Args:
            name: The name of the room (e.g., "Forest Clearing", "Dark Cave").
            description: A detailed description of the room.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Room name must be a non-empty string.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Room description must be a non-empty string.")

        self.name = name
        self.description = description
        self._components = HoldComponent()
        self._components.add_component("inventory", Inventory())

        # --- NEW: Internal state for lighting ---
        self._is_lit = False # Default state: room is not specifically lit by an in-room action
        # --- END NEW ---

    @property
    def inventory(self) -> Inventory:
        """
        Returns the Inventory component of the room, allowing access to items within it.
        """
        return self._components["inventory"]

    def add_item(self, item: Item):
        """
        Adds an item to the room's inventory.
        """
        self.inventory.add_item(item)
        print(f"[{self.name}] A {item.name} x{item.quantity} has appeared.")

    def remove_item(self, item_name: str, quantity: int = 1) -> Item:
        """
        Removes an item from the room's inventory.

        Args:
            item_name: The name of the item to remove.
            quantity: The quantity to remove (default: 1).

        Returns:
            The Item object that was removed (or a new Item object representing the quantity removed).
            Note: For simplicity, this returns a new Item instance with the removed quantity.
            You might want to refine this if precise object identity is crucial after removal.

        Raises:
            ItemNotFoundError: If the item is not found in the room.
            InsufficientQuantityError: If trying to remove more than available.
        """
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

        # --- NEW: Check for torch removal impacting _is_lit state ---
        if item_name == "Torch" and original_item.quantity <= quantity:
            # If the last torch is removed, ensure the room isn't considered lit by it
            self._is_lit = False
            print(f"[{self.name}] The light source is gone, the area grows darker.")
        # --- END NEW ---

        return removed_item

    # --- NEW: Function to "use" an item in the room ---
    def use_item_in_room(self, item_name: str, user: 'Combatant'):
        """
        Simulates using an item currently in the room.
        This is for items that affect the room itself (like a torch).

        Args:
            item_name: The name of the item to use.
            user: The combatant using the item (e.g., the hero).
        Raises:
            ItemNotFoundError: If the item is not in the room.
            ValueError: If the item cannot be "used" in this context.
        """
        if not self.inventory.has_component(item_name):
            raise ItemNotFoundError(item_name)

        item_to_use = self.inventory[item_name]

        if item_name == "Torch":
            if self.name == "Dark Cave Entrance": # Only works in the dark cave for this example
                self._is_lit = True
                print(f"[{self.name}] {user.name} lights the Torch, illuminating a tiny area around you.")
            else:
                print(f"[{self.name}] Using the {item_name} here doesn't seem to have much effect.")
        else:
            # You can add logic for other usable items here
            print(f"[{self.name}] You try to use the {item_name}, but nothing happens yet.")
            raise ValueError(f"Item '{item_name}' cannot be used in this room.")
    # --- END NEW ---

    def get_description(self) -> str:
        """
        Returns the detailed description of the room, including its contents.
        The description can change based on certain items present or actions taken.
        """
        current_description = self.description

        if self.name == "Dark Cave Entrance":
            if self._is_lit:
                current_description = "The air is still cold, but the flickering light of the torch reveals a tiny, dusty area around you. Shadows dance at the edges of your vision."
            elif not self.inventory.has_component("Torch"): # If no torch is physically in the room
                current_description = "The cave entrance is now pitch black. You can barely see your hand in front of your face."
            else: # Torch is present but not used/lit
                current_description = "The air grows cold as you stand at the mouth of a dark, damp cave. You can dimly make out a torch lying on the ground."


        items_in_room = self.inventory.items.values()
        item_list_str = ""
        if items_in_room:
            item_list_str = "\n\nYou see here: " + ", ".join(str(item) for item in items_in_room)
        return f"{current_description}{item_list_str}"

    def __str__(self) -> str:
        return f"Room: {self.name}"

    def __repr__(self) -> str:
        return f"Room('{self.name}', '{self.description}')"
