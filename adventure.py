from typing import TYPE_CHECKING

from character.enemy import Goblin
from character.hero import RpgHero
from game.setup import setup_game
from game.util import handle_spell_cast,handle_inventory_operation
from commands.command import help_command, use_command


def handle_combat(hero: RpgHero, enemy: Goblin):
    """
    Simplified combat loop for the demo.
    In a real game, this would be much more elaborate.
    """
    print(f"\n--- COMBAT INITIATED: {hero.name} vs. {enemy.name} ---")
    while hero.is_alive() and enemy.is_alive():
        print(f"\n{hero.name} Health: {hero.health}/{hero.max_health} | Mana: {hero.mana}/{hero.max_mana}")
        print(f"{enemy.name} Health: {enemy.health}/{enemy.max_health}")

        command = input("What will you do? (attack, cast [spell_name]): ").lower().strip()
        action = command.split(' ', 1)[0] if ' ' in command else command
        arg = command.split(' ', 1)[1] if ' ' in command else ""

        if action == "attack":
            if not arg:
                hero.attack(enemy)
            else:
                try:
                    hero.attack(enemy,arg)
                except ValueError as e:
                    print(f"{e}")
                    continue
            print(f"{hero.name} attacks {enemy.name}! {enemy.name}'s health is now {enemy.health}.")
        elif action.startswith("cast "):
            spell_name = action[5:].strip()
            handle_spell_cast(hero, spell_name, enemy)
            print(f"{hero.name} cast {spell_name}! {enemy.name}'s health is now {enemy.health}.")
        else:
            print("Invalid action. Try 'attack' or 'cast [spell_name]'.")
            continue # Let player try again

        if enemy.is_alive():
            enemy.attack(hero)
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
    hero, forest, cave, goblin_lair, goblin_foe = setup_game()
    current_room = forest # Start in the forest

    print("\n" + "="*50)
    print("THE QUEST FOR THE GOBLIN EAR")
    print("="*50 + "\n")

    # Game State Variables
    game_over = False

    while not game_over:
        print(f"\n--- You are in the {current_room.name} ---")
        print(current_room.get_description())

        # Display available exits
        if current_room.exits_to:
            exits_str = ", ".join(current_room.exits_to.keys())
            print(f"\nExits: {exits_str}")

        if len(current_room.combatants) > 0:
            print(f"\n{current_room.combatants[0].name} is here!")
            if handle_combat(hero, current_room.combatants[0]):
                beat = current_room.combatants.pop(0)
                print(f"you defeated {beat.name}.")
                # Add a "Goblin Ear" item to the hero's inventory after defeat
                if hasattr(beat,"reward"):
                    handle_inventory_operation(hero.inventory.add_item, beat.reward)
                    print(f"{hero.name} collected a trophy: {beat.reward.name} x{beat.reward.quantity}!")
            else:
                game_over = True


        if game_over:
            print("\nGame Over! Thanks for playing.")
            break

        command = input("\nWhat will you do? ").lower().strip().split(' ', 1) # Split into command and argument

        action = command[0]
        arg = command[1] if len(command) > 1 else ""

        if action == "go":
            next_room = current_room.exits_to.get(arg)
            if next_room and not next_room.is_locked:
                current_room = next_room
                print(f"You go {arg}.")
            else:
                print("You can't go that way.")
        elif action == "look":
            # Already printed at the top of the loop, but good for explicit command
            print(current_room.get_description())
        elif action == "status":
            print(hero)
            for quest in hero.quest_log.active_quests.values():
                print(f"Quest: {quest.name} - {quest.description} (ID {quest.id})")
            for quest in hero.quest_log.completed_quests:
                print(f"Quest Completed: {quest}")

        elif action == "turn-in":
            hero.quest_log.complete_quest(arg,hero)

        elif action == "inventory":
            print(hero.inventory)

        elif action == "use":
           use_command(arg,hero,current_room)

        elif action in ["take", "get"]:
            if not arg:
                print("What do you want to take?")
            else:
                try:
                    if current_room.inventory.has_component(arg):
                        item = handle_inventory_operation(current_room.remove_item, arg)
                        handle_inventory_operation(hero.inventory.add_item, item)
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
                        quantity = 1  # Default to dropping 1
                        # Remove from hero's inventory
                        dropped_item = handle_inventory_operation(hero.inventory.remove_item, arg,quantity)
                        # Add to room
                        handle_inventory_operation(current_room.add_item, dropped_item)
                        print(f"You dropped the {dropped_item.name} with quantity {dropped_item.quantity} in the {current_room.name}.")
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
            help_command()
        elif action == "quit":
            game_over = True
        else:
            print("Unknown command. Try 'help' for a list of commands.")

    print("\nAdventure End.")


if __name__ == '__main__':
    main_game_loop()
