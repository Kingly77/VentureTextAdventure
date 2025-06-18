import enum
from interfaces.interface import CanCast, Combatant


class Mana:
    def __init__(self, mana: int):
        self._mana = mana

    def consume(self, amount: int):
        """Consumes a specified amount of mana."""
        if amount < 0:
            raise ValueError("Mana consumption cannot be negative.")
        self.mana -= amount # Use the setter to ensure validation

    @property
    def mana(self) -> int:
        return self._mana

    @mana.setter
    def mana(self, mana: int):
        if mana < 0:
            self._mana = 0 # Direct assignment to avoid recursion
            # You might want to log a warning here if mana goes below zero
        else:
            self._mana = mana


class Health:
    def __init__(self, health: int):
        self._health = health

    def take_damage(self, damage: int):
        """Reduces health by the specified damage amount."""
        if damage < 0:
            raise ValueError("Damage cannot be negative.")
        self.health -= damage # Use the setter to ensure validation

    def heal(self, amount: int):
        """Increases health by the specified amount."""
        if amount < 0:
            raise ValueError("Healing amount cannot be negative.")
        self.health += amount # Use the setter to ensure validation

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, health: int):
        if health < 0:
            self._health = 0 # Direct assignment to avoid recursion
        else:
            self._health = health


class HoldComponent:
    def __init__(self):
        self._components = {}

    def add_component(self, name: str, component):
        """Adds a component to the holder by name."""
        if not isinstance(name, str) or not name.strip():
            raise TypeError("Component name must be a non-empty string.")
        if name in self._components:
            raise ValueError(f"Component '{name}' is already added.")
        self._components[name] = component

    def get_component(self, name: str):
        """Retrieves a component by name."""
        if name not in self._components:
            raise KeyError(f"Component '{name}' not found.")
        return self._components[name]

    def remove_component(self, name: str):
        """Removes a component by name."""
        if name not in self._components:
            raise KeyError(f"Component '{name}' not found.")
        del self._components[name]

    def all_components(self):
        """Returns all stored components."""
        return self._components.values()

    def has_component(self, name: str) -> bool:
        """Checks if a component exists."""
        return name in self._components

    def __getitem__(self, name: str):
        """Enables dictionary-like access for components."""
        return self.get_component(name)

    def __repr__(self):
        """Returns readable class representation for debugging."""
        components = ', '.join(self._components.keys())
        return f"<HoldComponent with: {components}>"


class Effect(enum.Enum):
    HEAL = 1
    DAMAGE = 2
    NONE = 3


class UseItemError(Exception):
    def __init__(self):
        super().__init__("Item cannot be used.")


class Item(CanCast): # Inherit from CanCast
    def __init__(self, name: str, cost: int, is_usable: bool = False, effect: Effect = Effect.NONE, effect_value: int = 0):
        self.name = name
        self.cost = cost
        self.quantity = 1
        self.is_usable = is_usable
        self.effect_type: Effect = effect
        self.effect_value = effect_value

    def cast(self, target: Combatant):
        """Applies the item's effect to the target."""
        if self.effect_type == Effect.HEAL:
            target.heal(self.effect_value)
        elif self.effect_type == Effect.DAMAGE:
            target.take_damage(self.effect_value)
        else:
            print(f"Item {self.name} has no castable effect.")
            raise UseItemError()

    def __iadd__(self, quantity: int):
        self.quantity += quantity
        return self

    def __isub__(self, quantity: int): # Added for decrementing quantity
        self.quantity -= quantity
        return self

    def __str__(self):
        return f"{self.name} x{self.quantity}"

    def __repr__(self):
        return f"Item('{self.name}', cost={self.cost}, qty={self.quantity}, usable={self.is_usable}, effect={self.effect_type.name}, value={self.effect_value})"

class InventoryError(Exception):
    """Base exception for inventory-related errors."""
    pass


class ItemNotFoundError(InventoryError):
    """Exception raised when an item is not found in the inventory."""
    def __init__(self, item_name: str):
        self.item_name = item_name
        super().__init__(f"Item '{item_name}' not found in inventory.")


class InsufficientQuantityError(InventoryError):
    """Exception raised when trying to remove more items than available."""
    def __init__(self, item_name: str, requested: int, available: int):
        self.item_name = item_name
        self.requested = requested
        self.available = available
        super().__init__(
            f"Cannot remove {requested} of {item_name}, only {available} items are available."
        )


class Inventory:
    """Manages a collection of items for a character."""

    def __init__(self):
        """Initialize an empty inventory."""
        self.items: dict[str, Item] = {}

    def add_item(self, item: Item):
        """Adds an item to the inventory, stacking if it already exists.

        Args:
            item: The item to add to the inventory
        """
        if not isinstance(item, Item):
            raise TypeError("Can only add Item objects to inventory")

        if item.name in self.items:
            self.items[item.name] += item.quantity
        else:
            self.items[item.name] = item

    def remove_item(self, item_name: str, quantity: int = 1):
        """Removes a specified quantity of an item from the inventory.

        Args:
            item_name: The name of the item to remove
            quantity: The quantity to remove (default: 1)

        Raises:
            ItemNotFoundError: If the item is not in the inventory
            InsufficientQuantityError: If trying to remove more than available
            ValueError: If quantity is not positive
        """
        if quantity <= 0:
            raise ValueError("Quantity to remove must be positive")

        if item_name not in self.items:
            # Still print for user feedback but also raise exception for proper handling
            print(f"Item '{item_name}' not found in inventory.")
            raise ItemNotFoundError(item_name)

        current_item = self.items[item_name]
        if quantity > current_item.quantity:
            # Still print for user feedback but also raise exception for proper handling
            print(f"Cannot remove {quantity} of {item_name}, only {current_item.quantity} items are available.")
            raise InsufficientQuantityError(item_name, quantity, current_item.quantity)

        current_item -= quantity
        if current_item.quantity <= 0:
            print(f"Item '{item_name}' removed entirely from inventory.")
            del self.items[item_name]
        else:
            print(f"Removed {quantity} of {item_name}. Remaining: {current_item.quantity}")

    def __getitem__(self, item_name: str) -> Item | None:
        """Allows dictionary-like access to retrieve an item.

        Args:
            item_name: The name of the item to retrieve

        Returns:
            The item if found, None otherwise
        """
        return self.items.get(item_name)

    def __repr__(self) -> str:
        """Returns a string representation of the inventory.

        Returns:
            A string listing all items in the inventory
        """
        return f"<Inventory with: {list(self.items.values())}>"

    def has_component(self, item):
        if item in self.items:
            return True
        else:
            return False

