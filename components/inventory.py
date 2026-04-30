import logging
from typing import Optional, TYPE_CHECKING
from copy import deepcopy

from game.items import Item


if TYPE_CHECKING:
    from character.basecharacter import BaseCharacter


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
    """Manages a collection of items for a character.

    Stackable items (item.stackable=True) are tracked as (canonical_item, count) pairs
    keyed by name. Non-stackable items (equipment) are stored as individual instances.
    """

    def __init__(self, owner: Optional["BaseCharacter"] = None):
        self._stacks: dict[str, tuple[Item, int]] = {}  # name → (item, count)
        self._separate: list[Item] = []  # non-stackable individual items
        self.owner = owner

    @property
    def items(self) -> dict[str, Item]:
        """Backward-compatible view: returns dict of canonical items keyed by name."""
        result = {name: item for name, (item, _) in self._stacks.items()}
        for item in self._separate:
            result.setdefault(item.name, item)
        return result

    def count(self, item_name: str) -> int:
        """Return the total count of an item by name."""
        if item_name in self._stacks:
            return self._stacks[item_name][1]
        return sum(1 for item in self._separate if item.name == item_name)

    def add_item(self, item: Item, quantity: int = 1):
        """Add item(s) to the inventory. Stackable items merge; non-stackable are kept separate."""
        if not isinstance(item, Item):
            raise TypeError("Can only add Item objects to inventory")
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")

        if item.stackable:
            if item.name in self._stacks:
                canonical, current = self._stacks[item.name]
                self._stacks[item.name] = (canonical, current + quantity)
            else:
                self._stacks[item.name] = (deepcopy(item), quantity)
        else:
            for _ in range(quantity):
                self._separate.append(deepcopy(item))

        if self.owner and hasattr(self.owner, "trigger_item_collected"):
            self.owner.trigger_item_collected(item, quantity)
        elif self.owner:
            try:
                from game.underlings.events import Events
                Events.trigger_event("item_collected", self.owner, item, quantity=quantity)
            except (ImportError, AttributeError):
                pass

    def remove_item(self, item_name: str, quantity: int = 1) -> Item:
        """Remove a quantity of an item; returns the canonical item instance."""
        if quantity <= 0:
            raise ValueError("Quantity to remove must be positive")

        if item_name in self._stacks:
            canonical, current = self._stacks[item_name]
            if quantity > current:
                print(f"Cannot remove {quantity} of {item_name}, only {current} items are available.")
                raise InsufficientQuantityError(item_name, quantity, current)
            if quantity == current:
                del self._stacks[item_name]
                logging.debug(f"Item '{item_name}' removed entirely from inventory.")
            else:
                self._stacks[item_name] = (canonical, current - quantity)
                print(f"Removed {quantity} of {item_name}. Remaining: {current - quantity}")
            return canonical

        matches = [item for item in self._separate if item.name == item_name]
        if not matches:
            print(f"Item '{item_name}' not found in inventory.")
            raise ItemNotFoundError(item_name)
        item = matches[0]
        self._separate.remove(item)
        return item

    def __getitem__(self, item_name: str) -> Item | None:
        if item_name in self._stacks:
            return self._stacks[item_name][0]
        for item in self._separate:
            if item.name == item_name:
                return item
        return None

    def __repr__(self) -> str:
        stacks = [(name, count) for name, (_, count) in self._stacks.items()]
        sep = [item.name for item in self._separate]
        return f"<Inventory stacks={stacks} separate={sep}>"

    def transfer(
        self, item_name: str, target: "Inventory", quantity: int = 1
    ) -> Optional[Item]:
        """Move a quantity of an item from this inventory to another."""
        try:
            item = self.remove_item(item_name, quantity)
            target.add_item(item, quantity)
            return item
        except (ItemNotFoundError, InsufficientQuantityError, ValueError, TypeError):
            return None

    def has_component(self, item_name: str) -> bool:
        return item_name in self._stacks or any(i.name == item_name for i in self._separate)
