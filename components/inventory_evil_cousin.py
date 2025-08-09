from components.inventory import Inventory
from game.items import Item
from game.underlings.events import Events


class QuestAwareInventory:
    """Inventory wrapper that handles quest checking."""

    def __init__(self, inventory: Inventory, hero: "RpgHero"):
        self._inventory = inventory
        self._hero = hero

    def add_item(self, item: Item):
        """Add an item and trigger quest-related events.

        Returns the list of event handler results (if any), allowing callers/UI to decide how to display them.
        """
        # Add to the underlying inventory first
        self._inventory.add_item(item)
        # Then trigger item_collected so quests can react. Do not print here.
        Events.trigger_event("item_collected", self._hero, item)

    def __getattr__(self, name):
        """Delegate everything else to the real inventory."""
        return getattr(self._inventory, name)

    def __getitem__(self, item_name: str) -> Item:
        """Handle dictionary-style access like inventory['fists']."""
        return self._inventory[item_name]

    def __repr__(self):
        """Delegate string representation."""
        return repr(self._inventory)
