from game.items import Item


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

