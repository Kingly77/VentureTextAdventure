from typing import Optional
from typing import TYPE_CHECKING

from components.inventory import ItemNotFoundError, InsufficientQuantityError
from game.util import handle_inventory_operation

if TYPE_CHECKING:
    from game.items import Item
    from components.inventory import Inventory
    from components.inventory_evil_cousin import QuestAwareInventory


def add_item(source: "Inventory", item: "Item") -> None:
    """Add an item to an inventory."""
    handle_inventory_operation(source.add_item, item)


def remove_item(source: "Inventory", item_name: str, quantity: int = 1) -> "Item":
    return handle_inventory_operation(source.remove_item, item_name, quantity)


def handle_transfer(
    source: "Inventory",
    item_name: str,
    target: "Inventory | QuestAwareInventory",
    quantity: int = 1,
) -> Optional["Item"]:
    return handle_inventory_operation(transfer, source, item_name, target, quantity)


def transfer(
    source: "Inventory",
    item_name: str,
    target: "Inventory",
    quantity: int = 1,
) -> Optional["Item"]:
    """Move a quantity of an item from one inventory to another.

    Args:
        source: Inventory to remove the item from.
        item_name: Name of the item to transfer.
        target: Inventory to receive the item.
        quantity: How many to transfer (default 1).

    Returns:
        The Item that was moved (with its quantity set to the amount moved),
        or None if the transfer could not be completed.
    """
    try:
        moved: "Item" = remove_item(source, item_name, quantity)
        # Add the removed item instance (represents the moved quantity)
        add_item(target, moved)
        return moved
    except (ItemNotFoundError, InsufficientQuantityError, ValueError, TypeError):
        # Silently indicate failure via None; callers may print messages separately
        return None
