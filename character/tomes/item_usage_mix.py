from components.inventory import ItemNotFoundError
from game.items import UseItemError


class ItemUsageMix:
    """Mixin providing item usage behavior.

    Expects the concrete class to provide:
      - inventory: an inventory with dict-like access and remove_item
      - _normalize_name(name: str) -> str
      - name: for printing feedback
    """

    def use_item(self, item_name: str, target=None):
        """Use an item from the hero's inventory.

        Args:
            item_name: The name of the item to use
            target: Optional target for the item (defaults to self)

        Raises:
            ItemNotFoundError: If the item is not in the inventory
            UseItemError: If the item cannot be used
            TypeError: If item_name is not a string
        """
        if not isinstance(item_name, str):
            raise TypeError("Item name must be string")

        key = self._normalize_name(item_name)

        # Retrieve or raise ItemNotFoundError from inventory directly
        try:
            item = self.inventory[key]
        except ItemNotFoundError:
            raise

        if not item.is_usable:
            print(f"{item_name} cannot be used.")
            raise UseItemError()

        if target is None:
            target = self

        try:
            item.cast(target)
            print(f"{self.name} used {item_name} on {getattr(target, 'name', 'self')}.")

            if item.is_consumable:
                self.inventory.remove_item(key, 1)
            return True
        except Exception as e:
            print(f"Error using {item_name}: {e}")
            raise
