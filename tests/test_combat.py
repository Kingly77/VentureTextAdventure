import pytest

from character.hero import RpgHero
from character.enemy import Goblin
from game.room import Room
from game.rpg_adventure_game import Game
from tests.helpers import run_cmd


def test_combat_victory_with_attack():
    # Setup hero and room
    hero = RpgHero("Test Hero", 1)
    room = Room("Arena", "A sparse arena for testing.")

    # Put a goblin in the room and construct the game
    goblin = Goblin("Grim", 1, base_health=1)
    room.combatants.append(goblin)

    game = Game(hero, room)

    # Precondition: combat not yet started
    assert game.in_combat is False
    assert game.current_enemy is None

    # Trigger combat detection
    game._check_for_combat()

    # Now we should be in combat with the goblin
    assert game.in_combat is True
    assert game.current_enemy is goblin

    # Perform an attack via the command engine (end-to-end path)
    out = run_cmd(game, "attack")

    # After one attack, goblin should be defeated (base health 1, fists deal 5)
    assert game.in_combat is False
    assert game.current_enemy is None

    # The goblin is removed from room combatants
    assert goblin not in room.combatants

    # Hero should gain XP equal to goblin.xp_value (100)
    assert (
        hero.xp >= 100 or hero.level > 1
    )  # leveling system may auto-level; accept either

    # Output should mention the attack and defeat somewhere
    text = "\n".join(out)
    assert "attacks" in text.lower()
    assert "defeated" in text.lower()
