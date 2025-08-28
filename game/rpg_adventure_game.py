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
from game.util import handle_spell_cast
from game.underlings.inventory_maybe import add_item as inv_add_item


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
                    inv_add_item(self.hero.inventory, defeated_enemy.reward)
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
