import pytest
from unittest.mock import MagicMock, patch

from character.hero import RpgHero
from game.items import Item
from game.room import Room
from game.rpg_adventure_game import Game
from game.effects.item_effects.item_effects import Effect
import commands.engine as eng


@pytest.fixture
def test_hero():
    """Fixture that creates a test hero at level 1."""
    hero = RpgHero("Test Hero", 1)
    hero.gold = 50
    return hero


@pytest.fixture
def test_items():
    """Fixture that creates test items for parser testing."""
    return {
        "key": Item("key", 5, True, tags=["key"]),
        "torch": Item("torch", 3, True, tags=["light-source"]),
        "sword": Item(
            "sword",
            25,
            True,
            is_equipment=True,
            effect=Effect.DAMAGE,
            effect_value=15,
            tags=["weapon"],
        ),
        "potion": Item(
            "health potion",
            10,
            True,
            is_consumable=True,
            effect=Effect.HEAL,
            effect_value=20,
            tags=["potion"],
        ),
        "gold": Item("gold coins", 1, False, quantity=10),
    }


@pytest.fixture
def test_room(test_items):
    """Fixture that creates a test room with items."""
    room = Room("Test Room", "A simple room for testing the parser.")

    # Add some items to the room
    room.add_item(test_items["key"])
    room.add_item(test_items["gold"])

    return room


@pytest.fixture
def test_game(test_hero, test_room):
    """Fixture that creates a game instance with a hero and room."""
    # Add some items to hero's inventory
    test_hero.inventory.add_item(Item("torch", 3, True, tags=["light-source"]))
    test_hero.inventory.add_item(
        Item(
            "health potion",
            10,
            True,
            is_consumable=True,
            effect=Effect.HEAL,
            effect_value=20,
            tags=["potion"],
        )
    )

    # Create the game instance
    game = Game(test_hero, test_room)

    # Mock the _update_turn method to prevent the game loop from running
    game._update_turn = MagicMock()

    return game


def test_parse_command():
    """Test the parsing using the public engine.parse_command_line function."""
    # Test basic command parsing
    pairs = eng.parse_command_line("go north")
    assert pairs == [("go", "north")]

    # Test command with no arguments
    pairs = eng.parse_command_line("inventory")
    assert pairs == [("inventory", "")]

    # Test command with multiple word arguments
    pairs = eng.parse_command_line("use health potion")
    assert pairs == [("use", "health potion")]

    # Test command with target
    pairs = eng.parse_command_line("use key on chest")
    assert pairs == [("use", "key on chest")]


def test_dispatch_command_methods():
    """Test dispatching via public parse_and_execute and assert observable behavior via execute_line."""
    # Create a simple game instance
    game = Game(MagicMock(), MagicMock())
    out = eng.execute_line(game, "look")
    assert len(out) > 0

    out = eng.execute_line(game, "inventory")
    # Should print inventory header or empty message
    assert len(out) > 0


def test_parse_and_execute(test_game):
    """Test parse_and_execute end-to-end using public behavior."""
    # Check that 'look' produces some output
    out = eng.execute_line(test_game, "look")
    assert len(out) > 0

    # Take key should move item from room to inventory
    # Precondition
    assert "key" in test_game.current_room.inventory.items
    assert "key" not in test_game.hero.inventory.items

    test_game.parse_and_execute("take key")

    assert "key" in test_game.hero.inventory.items
    assert "key" not in test_game.current_room.inventory.items


def test_integration_with_game_object(test_game):
    """Test integration of parser with actual game object."""
    # Test inventory command
    out = eng.execute_line(test_game, "inventory")
    assert len(out) > 0

    # Test look command and ensure room description appears
    out = eng.execute_line(test_game, "look")
    assert any("simple room for testing" in line.lower() for line in out)

    # Test take command and verify key was added to inventory
    test_game.parse_and_execute("take key")
    assert "key" in test_game.hero.inventory.items

    # Test use command and check health-related output
    out = eng.execute_line(test_game, "use health potion")
    assert any("health" in line.lower() for line in out)


def test_unknown_command(test_game):
    """Test handling of unknown commands."""
    out = eng.execute_line(test_game, "dance")
    text = "\n".join(out)
    assert "Unknown command. Try 'help' for a list of commands." in text


def test_complex_commands(test_game):
    """Test more complex command scenarios."""
    # Test use item on target
    out = eng.execute_line(test_game, "use torch on room")
    assert len(out) > 0

    # Test examine item
    out = eng.execute_line(test_game, "examine torch")
    text = "\n".join(out).lower()
    assert "torch" in text
