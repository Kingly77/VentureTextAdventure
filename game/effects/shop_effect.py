from character.hero import RpgHero
from components.wallet import Wallet
from game.items import Item
from interfaces.room_effect_base import RoomDiscEffect
from game.room import Room
from game.underlings.inventory_maybe import transfer


class ShopEffect(RoomDiscEffect):
    def __init__(self, room: Room, shopkeeper_name="The Merchant", prices=None):
        super().__init__(room)
        room._components.add_component("wallet", Wallet(1000))
        self.shopkeeper_name = shopkeeper_name
        self.prices = prices or {}  # item.name -> price override

    def get_modified_description(self, base_description: str) -> str:
        # Provide only shop info as a fragment; Room will append it.
        items = self.room.inventory.items.values()
        lines = [f"{self.shopkeeper_name}'s shop:"]
        for item in items:
            price = self.get_price(item)
            lines.append(f" - {item.name} ({price}g)")
        return "\n".join(lines)

    def get_price(self, item: Item) -> int:
        return self.prices.get(item.name, item.cost)

    def get_sell_price(self, item: Item) -> int:
        return self.get_price(item) // 2

    def can_buy(self, item: Item) -> bool:
        return True

    def can_sell(self, item: Item) -> bool:
        return getattr(item, "sellable", True)

    def handle_take(self, hero: RpgHero, item_name: str) -> bool:
        inv = self.room.inventory

        if not inv.has_component(item_name):
            return False

        item = inv[item_name]

        if item is None:
            return False

        price = self.get_price(item)

        if hero.gold < price:
            print(f"{self.shopkeeper_name} says: 'You can't afford that.'")
            return True  # handled: do not fall through to default
        if not self.can_buy(item):
            print(f"{self.shopkeeper_name} says: 'That one's not for sale.'")
            return True

        hero.spend_gold(price)
        # self.room.remove_item(item_name)
        # handle_inventory_operation(hero.inventory.add_item, item)

        transfer(inv, item_name, hero.inventory)

        print(f"{self.shopkeeper_name} sells you the {item.name} for {price} gold.")
        return True

    def handle_drop(self, hero: RpgHero, item_name: str) -> bool:
        if not hero.inventory.has_component(item_name):
            return False

        item = hero.inventory[item_name]
        if not self.can_sell(item):
            print(f"{self.shopkeeper_name} says: 'I’m not buying that.'")
            return True

        moved = transfer(hero.inventory, item_name, self.room, 1)
        if not moved:
            print("how did you get here?")
            return False

        gold = self.get_sell_price(item)
        hero.add_gold(gold)
        print(f"{self.shopkeeper_name} gives you {gold} gold for the {item.name}.")
        return True
