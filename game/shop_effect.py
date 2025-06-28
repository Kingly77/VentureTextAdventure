from character.hero import RpgHero
from game.items import Item
from game.room_effects import RoomDiscEffect


class ShopEffect(RoomDiscEffect):
    def __init__(self, room: 'Room', shopkeeper_name="The Merchant", prices=None):
        super().__init__(room)
        self.shopkeeper_name = shopkeeper_name
        self.prices = prices or {}  # item.id -> price override

    def get_modified_description(self, base_description: str) -> str:
        # Append shop info to room description
        items = self.room.inventory.items.values()
        lines = [f"{base_description}", f"\n{self.shopkeeper_name}'s shop:"]
        for item in items:
            price = self.get_price(item)
            lines.append(f" - {item.name} ({price}g)")
        return "\n".join(lines)

    def get_price(self, item: 'Item') -> int:
        return self.prices.get(item.name, item.cost)

    def get_sell_price(self, item: 'Item') -> int:
        return self.get_price(item) // 2

    def can_buy(self, item: 'Item') -> bool:
        return True

    def can_sell(self, item: 'Item') -> bool:
        return getattr(item, "sellable", True)

    def handle_take(self, hero: 'RpgHero', item_name: str) -> bool:
        inv = self.room.inventory
        if not inv.has_component(item_name):
            return False

        item = inv[item_name]
        price = self.get_price(item)

        if hero.gold < price:
            print(f"{self.shopkeeper_name} says: 'You can't afford that.'")
            return True  # handled: do not fall through to default
        if not self.can_buy(item):
            print(f"{self.shopkeeper_name} says: 'That one's not for sale.'")
            return True

        hero.gold -= price
        self.room.remove_item(item_name)
        hero.inventory.add_item(item)
        print(f"{self.shopkeeper_name} sells you the {item.name} for {price} gold.")
        return True