import logging

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
            existing = self.items[item.name]
            # Increase quantity and preserve union of tags
            existing += item.quantity
            try:
                existing.tags.update(item.tags)
            except Exception:
                # Be resilient if tags aren't sets/lists for some reason
                try:
                    existing.tags = set(existing.tags or []) | set(item.tags or [])
                except Exception:
                    pass
        else:
            # Store a cloned copy to avoid sharing the same Item instance across inventories
            cloned = Item(
                name=item.name,
                cost=item.cost,
                is_usable=item.is_usable,
                effect=item.effect_type,
                effect_value=item.effect_value,
                is_consumable=item.is_consumable,
                is_equipment=getattr(item, "is_equipment", False),
                tags=set(item.tags or []),
            )
            cloned.quantity = item.quantity
            self.items[item.name] = cloned

    def remove_item(self, item_name: str, quantity: int = 1) -> Item:
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
            print(
                f"Cannot remove {quantity} of {item_name}, only {current_item.quantity} items are available."
            )
            raise InsufficientQuantityError(item_name, quantity, current_item.quantity)

        current_item -= quantity

        # Create a new Item instance representing the removed quantity.
        # Use keyword args to avoid parameter misalignment and ensure tags transfer.
        removed_item = Item(
            name=current_item.name,
            cost=current_item.cost,
            is_usable=current_item.is_usable,
            effect=current_item.effect_type,
            effect_value=current_item.effect_value,
            is_consumable=current_item.is_consumable,
            is_equipment=current_item.is_equipment if hasattr(current_item, "is_equipment") else False,
            tags=set(current_item.tags or []),
        )
        logging.debug(f"{current_item.tags} {removed_item.tags} ")
        removed_item.quantity = quantity

        if current_item.quantity <= 0:
            logging.debug(f"Item '{item_name}' removed entirely from inventory.")
            del self.items[item_name]
        else:
            print(
                f"Removed {quantity} of {item_name}. Remaining: {current_item.quantity}"
            )
        return removed_item

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
