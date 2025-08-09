from components.inventory_evil_cousin import QuestAwareInventory


class InventoryViewMix:
    """Mixin exposing a quest-aware inventory wrapper if present.

    Note: It expects self._inventory_wrapper to be set by the concrete class's __init__.
    """

    @property
    def inventory(self) -> QuestAwareInventory:
        return self._inventory_wrapper
