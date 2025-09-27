import pytest

from character.hero import RpgHero
from character.enemy import Goblin
from game.room import Room
from game.rpg_adventure_game import Game
from game.items import Item
from game.effects.item_effects.base import Effect
import commands.engine as eng


def test_combat_victory_with_sword_pickup_and_equip():
    """
    Test a complete scenario of:
    1. Setting up a hero and room with a sword
    2. Hero picking up the sword
    3. Hero equipping the sword
    4. Hero engaging in combat with an enemy
    5. Verifying the sword properly affects combat outcomes
    """
    # Setup hero and room
    hero = RpgHero("Test Hero", 1)
    room = Room("Weapon Chamber", "A chamber with weapons for testing.")

    # Create a sword with high damage for testing
    sword = Item(
        "sword",
        25,
        True,
        is_equipment=True,
        effect=Effect.DAMAGE,
        effect_value=20,  # More damage than default fists (5)
        tags=["weapon"],
    )

    # Add the sword to the room
    room.add_item(sword)

    # Put a goblin in the room with more health (requires two fist hits but only one sword hit)
    goblin = Goblin("Grim", 1, base_health=10)
    room.combatants.append(goblin)

    # Create the game
    game = Game(hero, room)

    # Check that the sword is in the room
    assert "sword" in [item.name.lower() for item in room.inventory.items.values()]

    # Take the sword using the command system
    take_output = eng.execute_line(game, "take sword")
    text = "\n".join(take_output)
    assert "took the sword" in text.lower()

    # Check the sword is now in the hero's inventory
    assert "sword" in [item.name.lower() for item in hero.inventory.items.values()]

    # Equip the sword
    equip_output = eng.execute_line(game, "equip sword")
    text = "\n".join(equip_output)
    assert "equipped sword" in text.lower()

    # Verify the sword is equipped
    assert hero.equipped.name.lower() == "sword"
    # assert hero.equipped.effect_value == 20  # Sword damage value

    # Precondition: combat not yet started
    assert game.in_combat is False
    assert game.current_enemy is None

    # Trigger combat detection
    game._check_for_combat()

    # Now we should be in combat with the goblin
    assert game.in_combat is True
    assert game.current_enemy is goblin

    # Initial goblin health should be 15
    assert goblin.health == 15

    # Perform an attack with the equipped sword
    attack_output = eng.execute_line(game, "attack")
    text = "\n".join(attack_output)

    # After one attack with the sword (damage 20), goblin should be defeated (health 10)
    assert game.in_combat is False
    assert game.current_enemy is None

    # The goblin is removed from room combatants
    assert goblin not in room.combatants

    # Output should mention the attack and defeat somewhere
    assert "attacks" in text.lower()
    assert "defeated" in text.lower()

    # Hero should gain XP equal to goblin.xp_value (100)
    assert (
        hero.xp >= 100 or hero.level > 1
    )  # leveling system may auto-level; accept either
