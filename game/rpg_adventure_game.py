import logging

from character.enemy import Goblin

from commands.engine import (
    CommandRegistry,
    CommandContext,
    CommandRequest,
    parse_command_line,
    maybe_gag,
    register_default_commands,
)
from components.core_components import Effect
from game.items import Item
from game.util import handle_spell_cast, handle_inventory_operation


class Game:

    def __init__(self, hero, room):
        """Initializes the game, setting up the hero, world, and command handlers."""
        self.hero, self.current_room = hero, room
        self.game_over = False

        # New unified command registry and parser-based dispatcher
        self.registry = CommandRegistry()
        register_default_commands(self.registry, self)

    def run(self):
        """Starts and runs the main game loop."""
        print("\n" + "=" * 50)
        print("THE QUEST FOR THE GOBLIN EAR")
        print("=" * 50 + "\n")
        logging.debug(f"Hero: {self.hero}")
        while not self.game_over:
            self._update_turn()

        print("\nAdventure End.")

    def _update_turn(self):
        """Processes a single turn of the game."""
        self._print_room_info()
        self._check_for_combat()

        if self.game_over:
            print("\nGame Over! Thanks for playing.")
            return

        self._process_input()

    def _print_room_info(self):
        """Prints the description and exits of the current room."""
        print(f"\n--- You are in the {self.current_room.name} ---")
        print(self.current_room.get_description())

        if self.current_room.exits_to:
            exits_str = ", ".join(self.current_room.exits_to.keys())
            print(f"\nExits: {exits_str}")

    def _check_for_combat(self):
        """Checks for and initiates combat if enemies are in the room."""
        while self.current_room.combatants and not self.game_over:
            enemy = self.current_room.combatants[0]
            print(f"\n{enemy.name} is here!")
            if self._handle_combat(enemy):
                defeated_enemy = self.current_room.combatants.pop(0)
                print(f"You defeated {defeated_enemy.name}.")
                if hasattr(defeated_enemy, "reward"):
                    handle_inventory_operation(
                        self.hero.inventory.add_item, defeated_enemy.reward
                    )
                    print(
                        f"{self.hero.name} collected a trophy: {defeated_enemy.reward.name} x{defeated_enemy.reward.quantity}!"
                    )
            else:
                self.game_over = True

    def _parse_command(self, command_str: str):
        """Splits a command string into (action, arg)."""
        parts = command_str.strip().split(" ", 1)
        return parts[0], parts[1] if len(parts) > 1 else ""

    def parse_and_execute(self, command_str: str):
        """Parses a line and routes commands through _dispatch_command (registry-backed)."""
        pairs = parse_command_line(command_str)
        gag = maybe_gag(pairs)
        if gag:
            print(gag)
            return
        for action_raw, arg in pairs:
            self._dispatch_command(action_raw, arg)

    def _dispatch_command(self, action: str, arg: str):
        """Routes the input command to the appropriate handler, preferring legacy handlers for test compatibility."""
        # use the unified registry
        cmd_def = self.registry.resolve(action)
        if cmd_def is not None:
            ctx = CommandContext(self, self.hero, self.current_room)
            req = CommandRequest(
                raw=f"{action} {arg}".strip(),
                action=cmd_def.name,
                arg=arg,
                tokens=arg.split() if arg else [],
            )
            try:
                cmd_def.handler(req, ctx)
            except Exception as e:
                print(f"An error occurred: {e}")
            return

        print("Unknown command. Try 'help' for a list of commands.")

    def _process_input(self):
        """Gets and processes player input using the unified parser/dispatcher."""
        command_input = input("\nWhat will you do? ")
        self.parse_and_execute(command_input)

    def _handle_look(self, _):
        """Handles the 'look' command to re-display the room description."""
        print(self.current_room.get_description())

    def _handle_status(self, _):
        """Handles the 'status' command to display player and quest status."""
        # Character stats section
        print("\n📊 Character Status:")
        print("=" * 40)
        print(
            f"🧙 {self.hero.name} | Level {self.hero.level} | XP: {self.hero.xp}/{self.hero.xp_to_next_level}"
        )
        print(f"❤️  Health: {self.hero.health}/{self.hero.max_health}")
        print(f"✨ Mana: {self.hero.mana}/{self.hero.max_mana}")
        print(f"💰 Gold: {self.hero.gold}")

        # Quest log section
        active_quests = list(self.hero.quest_log.active_quests.values())
        completed_quests = self.hero.quest_log.completed_quests

        if active_quests or completed_quests:
            print("\n📜 Quest Log:")
            print("-" * 40)

            # Show active quests
            if active_quests:
                print("🔸 Active Quests:")
                for quest in active_quests:
                    print(
                        f"  • {quest.name} - {quest.description} ({quest.progress}/{quest.objective.value}) (ID: {quest.id})"
                    )

            # Show completed quests
            if completed_quests:
                print("\n🔹 Completed Quests:")
                for quest in completed_quests:
                    print(f"  • {quest}")
        else:
            print("\n📜 Quest Log: No quests available")

        print("=" * 40)

    def _handle_talk(self, arg: str):
        """Talk to someone in the current room. Delegates to room effects if available."""
        # First, try to let the current room handle the conversation via its effects
        try:
            msg = self.current_room.interact(
                "talk", arg if arg else None, self.hero, None, self.current_room
            )
            if msg is not None:
                if isinstance(msg, str) and msg:
                    print(msg)
                return
        except Exception as _e:
            logging.debug(f"Error in Talking: {_e}")
            pass

        print("There is no one here to talk to.")
        return

    def _handle_inventory(self, _):
        """Handles the 'inventory' command."""
        inventory = self.hero.inventory
        items = list(inventory.items.values())

        if not items or (len(items) == 1 and items[0].name == "gold"):
            print("\n📦 Your inventory is empty.")
            return

        print("\n📦 Inventory:")
        print("------------------------")

        # Group items by type for better organization
        usable_items = []
        equipment = []
        misc_items = []

        for item in items:
            # Skip gold as it will be displayed separately
            if item.name.lower() == "gold":
                continue

            if item.is_usable:
                usable_items.append(item)
            elif hasattr(item, "is_equipment") and item.is_equipment:
                equipment.append(item)
            else:
                misc_items.append(item)

        # Print usable items
        if usable_items:
            print("🧪 Usable Items:")
            for item in usable_items:
                effect_text = ""
                if item.effect_type.name == "HEAL":
                    effect_text = f" (Heals {item.effect_value})"
                elif item.effect_type.name == "DAMAGE":
                    effect_text = f" (Damage {item.effect_value})"

                print(
                    f"  • {item.name} x{item.quantity}{effect_text} - {item.cost} gold each"
                )
            print()

        # Print equipment
        if equipment:
            print("⚔️ Equipment:")
            for item in equipment:
                print(f"  • {item.name} x{item.quantity} - {item.cost} gold each")
            print()

        # Print misc items
        if misc_items:
            print("🔮 Other Items:")
            for item in misc_items:
                print(f"  • {item.name} x{item.quantity} - {item.cost} gold each")

        print("------------------------")
        print(f"💰 Gold: {self.hero.gold}")

    def _handle_quit(self, _):
        """Handles the 'quit' and 'exit' commands."""
        self.game_over = True

    def _handle_debug(self, arg: str):
        """Debug-only commands for development purposes. Half do nothing. :)"""
        if arg == "heal":
            self.hero.health = self.hero.max_health
            print(f"{self.hero.name} fully healed.")
        elif arg == "mana":
            self.hero.mana = self.hero.max_mana
            print(f"{self.hero.name} restored mana.")
        elif arg == "xp":
            self.hero.add_xp(100)
            print("Gained 100 XP.")
        elif arg == "gold":
            self.hero.add_gold(100)
            print("Gained 100 gold.")
        elif arg == "hurt":
            self.hero.take_damage(10)
            print(f"{self.hero.name} was hurt for 10 HP.")

        elif arg == "add":
            item_name = input("Enter item name: ")
            item_quantity = int(input("Enter item quantity: "))
            item_cost = int(input("Enter item cost: "))
            item_effect_type = input("Enter effect type (HEAL/DAMAGE/NONE): ")
            if item_effect_type.upper() not in ["HEAL", "DAMAGE", "NONE"]:
                print("Invalid effect type. Must be HEAL, DAMAGE, or NONE.")
                return
            item_effect_value = input("Enter effect value: ")
            try:
                int(item_effect_value)
            except ValueError:
                print("Effect value must be an integer.")
                return

            item_is_usable = input("Is item usable? (y/n): ").lower() == "y"
            item_is_consumable = input("Is item consumable? (y/n): ").lower() == "n"
            self.hero.inventory.add_item(
                Item(
                    name=item_name,
                    cost=item_cost,
                    is_usable=True if item_is_usable == "y" else False,
                    effect=Effect[item_effect_type.upper()],
                    effect_value=int(item_effect_value),
                    is_consumable=True if item_is_consumable == "y" else False,
                ),
                quantity=item_quantity,
            )
        else:
            print("Unknown debug command. Options: heal, mana, xp,gold")

    def _handle_combat(self, enemy: Goblin) -> bool:
        """
        Manages the combat sequence between the hero and an enemy.
        Returns True if the hero wins, False otherwise.
        """
        hero = self.hero
        print(f"\n--- COMBAT INITIATED: {hero.name} vs. {enemy.name} ---")
        while hero.is_alive() and enemy.is_alive():
            print(
                f"\n{hero.name} Health: {hero.health}/{hero.max_health} | Mana: {hero.mana}/{hero.max_mana}"
            )
            print(f"{enemy.name} Health: {enemy.health}/{enemy.max_health}")

            command = input(
                "What will you do? (attack [weapon], cast [spell]): "
            ).lower()
            action, arg = self._parse_command(command)

            if action == "attack":
                try:
                    hero.attack(enemy, arg or None)
                except ValueError as e:

                    logging.debug(f"{e}")
                    weapons = [
                        name
                        for name, item in hero.inventory.items.items()
                        if hasattr(item, "is_equipment") and item.is_equipment
                    ]
                    if weapons:
                        print(f"Available weapons: {', '.join(weapons)}")
                    else:
                        print(
                            "No weapons available. Use 'attack' without a weapon to fight bare-handed."
                        )
                    continue
                print(
                    f"{hero.name} attacks {enemy.name}! {enemy.name}'s health is now {enemy.health}."
                )
            elif action == "cast":
                handle_spell_cast(hero, arg, enemy)
            else:
                print("Invalid action. Try 'attack [weapon]' or 'cast [spell]'.")
                continue

            if enemy.is_alive():
                enemy.attack(hero)
                print(
                    f"{enemy.name} retaliates! {hero.name}'s health is now {hero.health}."
                )

        if hero.is_alive():
            print(f"\n{hero.name} defeated {enemy.name}!")
            hero.add_xp(enemy.xp_value)
            print(
                f"{hero.name} gained {enemy.xp_value} XP. Total XP: {hero.xp}, Level: {hero.level}."
            )
            return True
        else:
            print(f"\n{hero.name} has been defeated by {enemy.name}...")
            return False
