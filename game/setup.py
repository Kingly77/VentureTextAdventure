import functools
from character.enemy import Goblin
from character.hero import RpgHero
from components.core_components import Effect
from game.items import Item
from game.quest import Quest, Objective
from game.room import Room, RoomObject
from game.room_effects import DarkCaveLightingEffect
from game.shop_effect import ShopEffect
from game.underlings.events import Events as Event
from game.util import handle_inventory_operation


def _initialize_game_world():
    # 1. Create Hero
    hero = RpgHero("Aidan", 1)
    goblin_ear = Quest("goblin ear", "Collect the goblin ear to defeat the goblin foe.",100,who=hero,objective=Objective("collect","goblin ear",1))
    hero.quest_log.add_quest(goblin_ear.id,goblin_ear)
    hero.inventory.add_item(Item("gold", 1, False, quantity=10))
    print(f"Welcome, {hero.name}, to the world of KingBase!")

    # 2. Create Rooms
    forest_clearing = Room("Forest Clearing", "A peaceful clearing in a dense forest. Sunlight filters through the leaves, and a stone table stands before you.")
    manor = Room("Manor", "A small manor with a large garden. The air is warm and the sun shines brightly.")
    foyer = Room("Foyer", "A cozy foyer with a large table and chair. There is a large glass door to the east.")
    dark_cave_entrance = Room("Dark Cave Entrance", "The air grows cold as you stand at the mouth of a dark, damp cave.")
    goblins_lair = Room("Goblin's Lair", "A small, squalid cave reeking of unwashed goblin. Bones litter the floor.")
    foyer.is_locked = True
    shack_shop = Room("Shack Shop", "A small, cozy shack with a large table and chair. There is a large glass door to the east.")
    shack_shop.add_effect(ShopEffect(shack_shop,"Maribel Tinkertop"))
    handle_inventory_operation(shack_shop.add_item, Item("marble ball", 1, False))
    handle_inventory_operation(shack_shop.add_item, Item("10 foot pole", 3, False))

    # Add events to unlock the door
    Event.add_event("unlock_foyer", foyer.unlock, True)

    # 3. Link Rooms
    forest_clearing.link_rooms("north", dark_cave_entrance, "south")
    forest_clearing.link_rooms("east", manor, "west")
    forest_clearing.link_rooms("south", shack_shop, "north")
    dark_cave_entrance.link_rooms("east", goblins_lair, "west") # Hidden path
    manor.link_rooms("north", foyer, "south")

    forest_table = RoomObject("table", "A large Stone table with a small wooden chair sitting on top.")
    forest_table.add_interaction("torch", lambda val_hero: "You light the torch and lite the table center with a flash of light.")

    manor_door = RoomObject("door",
                            "A sturdy wooden door with a heavy lock. It appears to be the entrance to the Foyer.")

    def use_sword_on_door(val_hero):
        if foyer.is_locked:  # Direct reference or through some getter
            try:
                Event.trigger_event("unlock_foyer")
                return "You use your sword to bash the door open! The door swings wide and a giant bashing sound is heard."
            except ValueError as e:
                return f"Error: {str(e)}"  # Better error message
        else:
            return "Door already unlocked and open."

    Event.add_event("unlock_foyer", functools.partial(manor_door.change_description, "The door is wide open, It appears to be the entrance to the Foyer."), True)

    manor_door.add_interaction("sword", use_sword_on_door)
    manor.add_object(manor_door)

    # 4. Apply Room Effects
    dark_cave_effect = DarkCaveLightingEffect(dark_cave_entrance)
    dark_cave_entrance.add_effect(dark_cave_effect)
    forest_clearing.add_object(forest_table)

    # 5. Populate Rooms with Items
    manor.add_item(Item("sword", 10, True, Effect.DAMAGE, 10,is_consumable=False))
    forest_clearing.add_item(Item("health potion", 10, True, Effect.HEAL, 20,is_consumable=True))
    dark_cave_entrance.add_item(Item("torch", 5, True,is_consumable=False)) # Essential for the cave!
    goblins_lair.add_item(Item("shiny coin", 1, False , is_consumable=True))
    goblins_lair.add_item(Item("rusty dagger", 5, True, Effect.DAMAGE, 5,is_consumable=False))

    # 6. Place Enemies
    goblin_foe = Goblin("Goblin Grunt", 1)
    goblin_foe.reward = Item("goblin ear", 1,False)
    goblin_foe.reward.quantity = 1
    goblins_lair.combatants = goblin_foe

    return hero, forest_clearing

def setup_game():
    hero, forest_clearing = _initialize_game_world()
    return hero, forest_clearing