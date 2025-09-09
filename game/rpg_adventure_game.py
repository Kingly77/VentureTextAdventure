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

from game.underlings.inventory_maybe import add_item as inv_add_item


class Game:

    def __init__(self, hero, room):
        """Initializes the game, setting up the hero, world, and command handlers."""
        self.hero, self.current_room = hero, room
        self.game_over = False
        # Combat state
        self.in_combat = False
        self.current_enemy = None

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
        if self.in_combat or self.game_over:
            return
        if self.current_room.combatants:
            enemy = self.current_room.combatants[0]
            self._begin_combat(enemy)

    def _parse_command(self, command_str: str):
        """Splits a command string into (action, arg)."""
        parts = command_str.strip().split(" ", 1)
        return parts[0], parts[1] if len(parts) > 1 else ""

    # New combat lifecycle helpers to integrate with normal command flow
    def _begin_combat(self, enemy: Goblin):
        self.in_combat = True
        self.current_enemy = enemy
        hero = self.hero
        print(f"\n--- COMBAT INITIATED: {hero.name} vs. {enemy.name} ---")
        print(
            f"\n{hero.name} Health: {hero.health}/{hero.max_health} | Mana: {hero.mana}/{hero.max_mana}"
        )
        print(f"{enemy.name} Health: {enemy.health}/{enemy.max_health}")

    def _end_combat(self, victory: bool):
        enemy = self.current_enemy
        hero = self.hero
        if enemy is None:
            # Nothing to end
            self.in_combat = False
            return
        if victory:
            print(f"\n{hero.name} defeated {enemy.name}!")
            hero.add_xp(enemy.xp_value)
            print(
                f"{hero.name} gained {enemy.xp_value} XP. Total XP: {hero.xp}, Level: {hero.level}."
            )
            # Remove the defeated enemy from the room if present at front
            if (
                self.current_room.combatants
                and self.current_room.combatants[0] is enemy
            ):
                defeated_enemy = self.current_room.combatants.pop(0)
                print(f"You defeated {defeated_enemy.name}.")
                if hasattr(defeated_enemy, "reward"):
                    inv_add_item(self.hero.inventory, defeated_enemy.reward)
                    print(
                        f"{self.hero.name} collected a trophy: {defeated_enemy.reward.name} x{defeated_enemy.reward.quantity}!"
                    )
        else:
            print(f"\n{hero.name} has been defeated by {enemy.name}...")
            self.game_over = True
        # Clear combat state
        self.in_combat = False
        self.current_enemy = None

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

        # Unknown verb: give room/effects a chance to handle it
        try:
            msg = self.current_room.interact(action, arg or None, self.hero, None, self.current_room)
            if msg is not None:
                if isinstance(msg, str) and msg:
                    print(msg)
                return
        except Exception:
            # If room/effects can't handle or raise, fall back to unknown command message
            pass

        print("Unknown command. Try 'help' for a list of commands.")

    def _process_input(self):
        """Gets and processes player input using the unified parser/dispatcher."""
        prompt = (
            "\nWhat will you do? " if not self.in_combat else "\n(Combat) Your move: "
        )
        command_input = input(prompt)
        self.parse_and_execute(command_input)
