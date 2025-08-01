import pytest
from unittest.mock import MagicMock, patch

from character.hero import RpgHero
from game.items import Item
from game.room import Room
from game.rpg_adventure_game import Game
from components.core_components import Effect


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
    """Test the _parse_command method of the Game class."""
    game = Game(MagicMock(), MagicMock())

    # Test basic command parsing
    action, arg = game._parse_command("go north")
    assert action == "go"
    assert arg == "north"

    # Test command with no arguments
    action, arg = game._parse_command("inventory")
    assert action == "inventory"
    assert arg == ""

    # Test command with multiple word arguments
    action, arg = game._parse_command("use health potion")
    assert action == "use"
    assert arg == "health potion"

    # Test command with target
    action, arg = game._parse_command("use key on chest")
    assert action == "use"
    assert arg == "key on chest"


def test_dispatch_command_methods():
    """Test the _dispatch_command method with internal method handlers."""
    # Use patch to mock the methods
    with patch("game.rpg_adventure_game.Game._handle_look") as mock_look:
        with patch("game.rpg_adventure_game.Game._handle_inventory") as mock_inventory:
            with patch("game.rpg_adventure_game.Game._handle_go") as mock_go:
                # Create a game instance with the patched methods
                game = Game(MagicMock(), MagicMock())

                # Test dispatching to method handlers
                game._dispatch_command("look", "")
                mock_look.assert_called_once_with("")

                game._dispatch_command("inventory", "")
                mock_inventory.assert_called_once_with("")

                game._dispatch_command("go", "north")
                mock_go.assert_called_once_with("north")


def test_dispatch_command_functions():
    """Test the _dispatch_command method with external function handlers."""
    # Create mock functions
    mock_use = MagicMock()
    mock_inventory = MagicMock()
    mock_help = MagicMock()

    # Create a game instance with mocked functions
    hero = MagicMock()
    room = MagicMock()
    game = Game(hero, room)

    # Replace the function handlers with mocks
    game._function_handlers = {
        "use": mock_use,
        "take": mock_inventory,
        "help": mock_help,
    }

    # Test dispatching to function handlers
    game._dispatch_command("use", "torch")
    mock_use.assert_called_once_with("use", "torch", hero, room)

    game._dispatch_command("take", "key")
    mock_inventory.assert_called_once_with("take", "key", hero, room)

    game._dispatch_command("help", "")
    mock_help.assert_called_once_with("help", "", hero, room)


def test_parse_and_execute(test_game):
    """Test the parse_and_execute method of the Game class."""
    # Mock the _dispatch_command method
    test_game._dispatch_command = MagicMock()

    # Test parse_and_execute with various commands
    test_game.parse_and_execute("go north")
    test_game._dispatch_command.assert_called_once_with("go", "north")
    test_game._dispatch_command.reset_mock()

    test_game.parse_and_execute("look")
    test_game._dispatch_command.assert_called_once_with("look", "")
    test_game._dispatch_command.reset_mock()

    test_game.parse_and_execute("use health potion")
    test_game._dispatch_command.assert_called_once_with("use", "health potion")
    test_game._dispatch_command.reset_mock()

    test_game.parse_and_execute("take key")
    test_game._dispatch_command.assert_called_once_with("take", "key")


def test_integration_with_game_object(test_game):
    """Test integration of parser with actual game object."""
    # Mock print to capture output
    with patch("builtins.print") as mock_print:
        # Test inventory command
        test_game.parse_and_execute("inventory")
        # Check that inventory was displayed (at least one call to print)
        assert mock_print.call_count > 0
        mock_print.reset_mock()

        # Test look command
        test_game.parse_and_execute("look")
        # Check that room description was displayed
        assert any(
            "simple room for testing" in str(args).lower()
            for args, _ in mock_print.call_args_list
        )
        mock_print.reset_mock()

        # Test take command
        test_game.parse_and_execute("take key")
        # Verify key was added to inventory
        assert "key" in test_game.hero.inventory.items
        mock_print.reset_mock()

        # Test use command
        test_game.parse_and_execute("use health potion")
        # Check that potion was used (health message displayed)
        assert any(
            "health" in str(args).lower() for args, _ in mock_print.call_args_list
        )


def test_unknown_command(test_game):
    """Test handling of unknown commands."""
    # Mock print to capture output
    with patch("builtins.print") as mock_print:
        test_game.parse_and_execute("dance")
        # Check that unknown command message was displayed
        mock_print.assert_called_with(
            "Unknown command. Try 'help' for a list of commands."
        )


def test_complex_commands(test_game):
    """Test more complex command scenarios."""
    # Mock print to capture output
    with patch("builtins.print") as mock_print:
        # Test use item on target
        test_game.parse_and_execute("use torch on room")
        # Check that command was processed
        assert mock_print.call_count > 0
        mock_print.reset_mock()

        # Test examine item
        test_game.parse_and_execute("examine torch")
        # Check that item details were displayed
        assert any(
            "torch" in str(args).lower() for args, _ in mock_print.call_args_list
        )
