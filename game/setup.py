from character.enemy import Goblin
from character.hero import RpgHero
from components.core_components import Effect
from game.items import Item
from game.quest import Quest, Objective
from game.room import Room, RoomObject
from game.room_effects import DarkCaveLightingEffect, BashDoorEffect
from game.util import handle_inventory_operation


def _initialize_game_world():
    # 1. Create Hero
    hero = RpgHero("Aidan", 1)
    goblin_ear = Quest("goblin ear", "Collect the goblin ear to defeat the goblin foe.",100,who=hero,objective=Objective("collect","goblin ear",1))
    hero.quest_log.add_quest(goblin_ear.id,goblin_ear)
    #hero.inventory.add_item(Item("goblin ear", 1,False))
    print(f"Welcome, {hero.name}, to the world of KingBase!")

    # 2. Create Rooms
    forest_clearing = Room("Forest Clearing", "A peaceful clearing in a dense forest. Sunlight filters through the leaves, and a stone table stands before you.")
    manor = Room("Manor", "A small manor with a large garden. The air is warm and the sun shines brightly.")
    foyer = Room("Foyer", "A cozy foyer with a large table and chair. There is a large glass door to the east.")
    dark_cave_entrance = Room("Dark Cave Entrance", "The air grows cold as you stand at the mouth of a dark, damp cave.")
    goblins_lair = Room("Goblin's Lair", "A small, squalid cave reeking of unwashed goblin. Bones litter the floor.")
    foyer.is_locked = True


    # 3. Link Rooms
    forest_clearing.link_rooms("north", dark_cave_entrance, "south")
    forest_clearing.link_rooms("east", manor, "west")
    dark_cave_entrance.link_rooms("east", goblins_lair, "west") # Hidden path
    manor.link_rooms("north", foyer, "south")

    forest_table = RoomObject("table", "A large Stone table with a small wooden chair sitting on top.")
    forest_table.add_interaction("torch", lambda val_hero: "You light the torch and lite the table center with a flash of light.")
    # 4. Apply Room Effects
    dark_cave_effect = DarkCaveLightingEffect(dark_cave_entrance)
    dark_cave_entrance.add_effect(dark_cave_effect)
    manor.add_effect(BashDoorEffect(manor))
    forest_clearing.objects["table"] = forest_table

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