from character.enemy import Goblin
from character.hero import RpgHero
from components.core_components import Effect
from game.items import Item
from game.room import Room
from game.room_effects import DarkCaveLightingEffect


def _initialize_game_world():
    # 1. Create Hero
    hero = RpgHero("Aidan", 1)
    print(f"Welcome, {hero.name}, to the world of KingBase!")

    # 2. Create Rooms
    forest_clearing = Room("Forest Clearing", "A peaceful clearing in a dense forest. Sunlight filters through the leaves.")
    dark_cave_entrance = Room("Dark Cave Entrance", "The air grows cold as you stand at the mouth of a dark, damp cave.")
    goblins_lair = Room("Goblin's Lair", "A small, squalid cave reeking of unwashed goblin. Bones litter the floor.")

    # 3. Link Rooms
    forest_clearing.link_rooms("north", dark_cave_entrance, "south")
    dark_cave_entrance.link_rooms("east", goblins_lair, "west") # Hidden path

    # 4. Apply Room Effects
    dark_cave_effect = DarkCaveLightingEffect(dark_cave_entrance)
    dark_cave_entrance.add_effect(dark_cave_effect)

    # 5. Populate Rooms with Items
    forest_clearing.add_item(Item("health potion", 10, True, Effect.HEAL, 20))
    dark_cave_entrance.add_item(Item("torch", 5, True)) # Essential for the cave!
    goblins_lair.add_item(Item("shiny coin", 1, False))
    goblins_lair.add_item(Item("rusty dagger", 5, True, Effect.DAMAGE, 5))

    # 6. Place Enemies
    goblin_foe = Goblin("Goblin Grunt", 1)
    # The goblin isn't "in the room's inventory," but is a separate entity that exists in the room
    # We might add a list of NPCs/monsters to the Room class, or simply manage it in the game state.
    # For now, let's return it with the rooms and hero.

    return hero, forest_clearing, dark_cave_entrance, goblins_lair, goblin_foe

def setup_game():
    hero, forest_clearing, dark_cave_entrance, goblins_lair, goblin_foe = _initialize_game_world()
    return hero, forest_clearing, dark_cave_entrance, goblins_lair, goblin_foe