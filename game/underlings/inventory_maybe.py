from typing import Optional, TYPE_CHECKING

from components.inventory import ItemNotFoundError, InsufficientQuantityError

if TYPE_CHECKING:
    from game.items import Item
    from components.inventory import Inventory
    from components.inventory_evil_cousin import QuestAwareInventory


def add_item(source: "Inventory", item: "Item") -> None:
    """Add an item to an inventory without extra helper layers."""
    source.add_item(item)


def remove_item(source: "Inventory", item_name: str, quantity: int = 1) -> "Item":
    """Remove an item directly from an inventory and return the removed item."""
    return source.remove_item(item_name, quantity)


def transfer(
    source: "Inventory",
    item_name: str,
    target: "Inventory | QuestAwareInventory",
    quantity: int = 1,
) -> Optional["Item"]:
    """Move a quantity of an item from one inventory to another.

    Returns the moved Item (with its quantity set to the amount moved) or None on failure.
    """
    try:
        moved: "Item" = source.remove_item(item_name, quantity)
        # Add the removed item instance (represents the moved quantity)
        target.add_item(moved)
        return moved
    except (ItemNotFoundError, InsufficientQuantityError, ValueError, TypeError):
        # Silently indicate failure via None; callers may print messages separately
        return None
