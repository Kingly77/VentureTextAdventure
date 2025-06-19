# In main.py
from character.enemy import Goblin
from character.hero import RpgHero
from components.inventory import ItemNotFoundError
from game.items import Item, UseItemError
from game.setup import _initialize_game_world
from game.util import handle_spell_cast, handle_inventory_operation


def handle_combat(hero: RpgHero, enemy: Goblin):
    """
    Simplified combat loop for the demo.
    In a real game, this would be much more elaborate.
    """
    print(f"\n--- COMBAT INITIATED: {hero.name} vs. {enemy.name} ---")
    while hero.is_alive() and enemy.is_alive():
        print(f"\n{hero.name} Health: {hero.health}/{hero.max_health} | Mana: {hero.mana}/{hero.max_mana}")
        print(f"{enemy.name} Health: {enemy.health}/{enemy.max_health}")

        action = input("What will you do? (attack, cast [spell_name]): ").lower().strip()

        if action == "attack":
            hero.attack(enemy)
            print(f"{hero.name} attacks {enemy.name}! {enemy.name}'s health is now {enemy.health}.")
        elif action.startswith("cast "):
            spell_name = action[5:].strip()
            handle_spell_cast(hero, spell_name, enemy)
            print(f"{hero.name} cast {spell_name}! {enemy.name}'s health is now {enemy.health}.")
        else:
            print("Invalid action. Try 'attack' or 'cast [spell_name]'.")
            continue # Let player try again

        if enemy.is_alive():
            enemy.attacks(hero)
            print(f"{enemy.name} retaliates! {hero.name}'s health is now {hero.health}.")

    if hero.is_alive():
        print(f"\n{hero.name} defeated {enemy.name}!")
        hero.add_xp(enemy.xp_value)
        print(f"{hero.name} gained {enemy.xp_value} XP. Total XP: {hero.xp}, Level: {hero.level}.")
        return True # Combat won
    else:
        print(f"\n{hero.name} has been defeated by {enemy.name}...")
        return False # Combat lost

def main_game_loop():
    hero, forest, cave, goblin_lair, goblin_foe = _initialize_game_world()
    current_room = forest # Start in the forest

    print("\n" + "="*50)
    print("THE QUEST FOR THE GOBLIN EAR")
    print("="*50 + "\n")

    # Game State Variables
    game_over = False
    goblin_defeated = False

    while not game_over:
        print(f"\n--- You are in the {current_room.name} ---")
        print(current_room.get_description())

        # Display available exits
        if current_room.exits_to:
            exits_str = ", ".join(current_room.exits_to.keys())
            print(f"\nExits: {exits_str}")

        # Check for goblin encounter
        if current_room == goblin_lair and not goblin_defeated:
            print(f"\nA snarling {goblin_foe.name} blocks your path!")
            if handle_combat(hero, goblin_foe):
                goblin_defeated = True
                print("You can now explore the lair freely.")
                # Add a "Goblin Ear" item to the hero's inventory after defeat
                hero.inventory.add_item(Item("Goblin Ear", 1, False))
                print(f"{hero.name} collected a trophy: a Goblin Ear!")
            else:
                game_over = True # Hero defeated

        if game_over:
            print("\nGame Over! Thanks for playing.")
            break

        command = input("\nWhat will you do? ").lower().strip().split(' ', 1) # Split into command and argument

        action = command[0]
        arg = command[1] if len(command) > 1 else ""

        if action == "go":
            next_room = current_room.exits_to.get(arg)
            if next_room:
                current_room = next_room
                print(f"You go {arg}.")
            else:
                print("You can't go that way.")
        elif action == "look":
            # Already printed at the top of the loop, but good for explicit command
            print(current_room.get_description())
        elif action == "equip":
            hero.equip_item(arg)

        elif action == "inventory":
            print(hero.inventory)
        elif action == "use":
            if not arg:
                print("What do you want to use?")
                continue

            # Split argument into item name and target (if provided)
            # Support both "use X on Y" and "use X in Y" patterns
            if " on " in arg:
                parts = arg.split(" on ", 1)
            elif " in " in arg:
                parts = arg.split(" in ", 1)
            else:
                parts = [arg]

            item_name = parts[0].strip().lower()
            target_str = parts[1].strip().lower() if len(parts) > 1 else None

            try:
                # First, check if the item is in the hero's inventory
                if hero.inventory.has_component(item_name):
                    item = hero.inventory[item_name]

                    # If the player specified "on room" or "in room", try room context usage
                    if target_str in ["room", "the room", "this room"]:
                        try:
                            current_room.use_item_in_room(item_name, hero)
                            print(f"{hero.name} used {item_name} in the {current_room.name}.")
                            # Item removal is handled by the room effect
                        except ValueError as e:
                            print(f"{e}")
                    # If it's a usable item but no specific target, use on self by default
                    elif target_str is None or target_str in ["self", "me", "myself", hero.name.lower()]:
                        if not item.is_usable:
                            print(f"The {item_name} cannot be used on yourself.")
                            continue

                        # Use item on hero
                        old_health = hero.health
                        item.cast(hero)  # Apply effect to hero
                        hero.inventory.remove_item(item_name, 1)  # Consume one use

                        print(f"{hero.name} used {item_name} on {hero.name}.")

                        # Display effect based on what happened
                        if hero.health > old_health:
                            print(f"You feel refreshed! Health increased to {hero.health}.")
                        elif hero.health < old_health:
                            print(f"Ouch! That hurt. Health decreased to {hero.health}.")
                    else:
                        print(f"You don't see '{target_str}' to use the {item_name} on.")

                # If item is in the room, try to use it directly
                elif current_room.inventory.has_component(item_name):
                    try:
                        current_room.use_item_in_room(item_name, hero)
                        print(f"{hero.name} used the {item_name} in the {current_room.name}.")
                    except Exception as e:
                        print(f"Failed to use {item_name}: {e}")
                else:
                    print(f"You don't see or have a '{item_name}'.")

            except ItemNotFoundError as e:
                print(f"Item not found: {e}")
            except UseItemError as e:
                print(f"Cannot use this item: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        elif action in ["take", "get"]:
            if not arg:
                print("What do you want to take?")
            else:
                try:
                    if current_room.inventory.has_component(arg):
                        item = current_room.remove_item(arg)
                        hero.inventory.add_item(item)
                        print(f"You took the {arg}.")
                    else:
                        print(f"There is no {arg} here to take.")
                except Exception as e:
                    print(f"Failed to take item: {e}")
        elif action == "drop":
            if not arg:
                print("What do you want to drop?")
            else:
                try:
                    if hero.inventory.has_component(arg):
                        item = hero.inventory[arg]
                        quantity = 1  # Default to dropping 1

                        # Create a new item with the same properties but quantity of 1
                        dropped_item = Item(item.name, item.cost, item.is_usable, 
                                           item.effect_type, item.effect_value)
                        dropped_item.quantity = quantity

                        # Remove from hero's inventory
                        hero.inventory.remove_item(arg, quantity)

                        # Add to room
                        current_room.add_item(dropped_item)
                        print(f"You dropped the {arg}.")
                    else:
                        print(f"You don't have a {arg} to drop.")
                except Exception as e:
                    print(f"Failed to drop item: {e}")
        elif action == "examine":
            if not arg:
                print("What do you want to examine?")
            else:
                # Check hero's inventory first
                if hero.inventory.has_component(arg):
                    item = hero.inventory[arg]
                    print(f"You examine the {item.name}:")
                    print(f"  Quantity: {item.quantity}")
                    print(f"  Value: {item.cost} gold")
                    if item.is_usable:
                        effect_desc = "No effect"
                        if item.effect_type.name == "HEAL":
                            effect_desc = f"Heals for {item.effect_value} health"
                        elif item.effect_type.name == "DAMAGE":
                            effect_desc = f"Deals {item.effect_value} damage"
                        print(f"  Effect: {effect_desc}")
                # Then check room inventory
                elif current_room.inventory.has_component(arg):
                    item = current_room.inventory[arg]
                    print(f"You examine the {item.name}:")
                    print(f"  Quantity: {item.quantity}")
                    print(f"  It looks like it's worth about {item.cost} gold.")
                    if item.is_usable:
                        print("  It looks like you could use this item.")
                else:
                    print(f"You don't see a {arg} here.")
        elif action == "help":
            print("\nAvailable commands:")
            print("  go [direction] - Move in a direction (north, south, east, west)")
            print("  look - Look around the room")
            print("  inventory - Check your inventory")
            print("  take/get [item] - Pick up an item")
            print("  drop [item] - Drop an item")
            print("  use [item] - Use an item on yourself")
            print("  use [item] on room - Use an item in the current room")
            print("  use [item] on [target] - Use an item on a specific target")
            print("  examine [item] - Examine an item in detail")
            print("  quit - Exit the game")
        elif action == "quit":
            game_over = True
        else:
            print("Unknown command. Try 'help' for a list of commands.")

    print("\nAdventure End.")

if __name__ == '__main__':
    main_game_loop()
