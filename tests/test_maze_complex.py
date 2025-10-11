#!/usr/bin/env python3
"""Test that the complex maze is properly built from JSON."""

from game.json_loader import load_world_from_path
from game.rooms.maze_room import MazeRoom


def test_complex_maze_built():
    """Test that the complex maze is built with multiple rooms."""
    rooms, start_key, hero_cfg = load_world_from_path(
        "../game/worlds/default_world.json"
    )

    # Check that maze_entrance exists
    assert "maze_entrance" in rooms, "maze_entrance should exist"
    entrance = rooms["maze_entrance"]
    assert isinstance(entrance, MazeRoom), "maze_entrance should be a MazeRoom"
    assert entrance.is_entrance, "maze_entrance should be marked as entrance"

    # Check that maze rooms were added (complex maze has 17 rooms total including entrance and exit)
    # Keys should be: maze_entrance_room1, maze_entrance_room2, ..., maze_entrance_room15, maze_entrance_exit
    maze_room_keys = [k for k in rooms.keys() if k.startswith("maze_entrance_")]
    print(f"Found {len(maze_room_keys)} maze rooms: {sorted(maze_room_keys)}")

    # Complex maze should have: entrance + 15 intermediate rooms + exit = 17 total
    # In the rooms dict: entrance is "maze_entrance", others are "maze_entrance_room1" through "maze_entrance_room15" and "maze_entrance_exit"
    assert (
        len(maze_room_keys) >= 16
    ), f"Should have at least 16 additional maze rooms (found {len(maze_room_keys)})"

    # Check that the exit exists
    assert "maze_entrance_exit" in rooms, "maze_entrance_exit should exist"
    exit_room = rooms["maze_entrance_exit"]
    assert isinstance(exit_room, MazeRoom), "exit should be a MazeRoom"
    assert exit_room.is_exit, "exit room should be marked as exit"

    # Check that rooms are connected
    assert len(entrance.exits_to) > 0, "entrance should have exits"
    print(f"Entrance exits: {list(entrance.exits_to.keys())}")

    # Check a path through the maze exists
    # From entrance, we should be able to reach other rooms
    assert (
        "north" in entrance.exits_to or "east" in entrance.exits_to
    ), "entrance should have north or east exit"

    print("✓ Complex maze is properly built with multiple interconnected rooms")
    return True


def test_maze_navigation():
    """Test that we can navigate through the maze."""
    rooms, start_key, hero_cfg = load_world_from_path(
        "../game/worlds/default_world.json"
    )

    entrance = rooms["maze_entrance"]

    # Navigate from entrance
    if "north" in entrance.exits_to:
        next_room = entrance.exits_to["north"]
        print(f"From entrance, going north leads to: {next_room.name}")
        assert isinstance(
            next_room, MazeRoom
        ), "Connected room should also be a MazeRoom"
        assert len(next_room.exits_to) > 0, "Interior maze room should have exits"

    if "east" in entrance.exits_to:
        next_room = entrance.exits_to["east"]
        print(f"From entrance, going east leads to: {next_room.name}")
        assert isinstance(
            next_room, MazeRoom
        ), "Connected room should also be a MazeRoom"

    print("✓ Maze navigation works correctly")
    return True


def test_village_square_connection():
    """Test that village square is still connected to the maze entrance."""
    rooms, start_key, hero_cfg = load_world_from_path(
        "../game/worlds/default_world.json"
    )

    village_square = rooms["village_square"]
    assert "north" in village_square.exits_to, "village_square should have north exit"

    maze_entrance = village_square.exits_to["north"]
    assert (
        maze_entrance.name == "Maze Entrance"
    ), "north from village_square should lead to Maze Entrance"
    assert isinstance(maze_entrance, MazeRoom), "Should be a MazeRoom"

    # Check reverse connection
    assert (
        "south" in maze_entrance.exits_to
    ), "maze_entrance should have south exit back to village"
    assert (
        maze_entrance.exits_to["south"] == village_square
    ), "south should lead back to village_square"

    print("✓ Village square is properly connected to maze entrance")
    return True


if __name__ == "__main__":
    print("Testing complex maze building...")
    print()

    try:
        test_complex_maze_built()
        print()
        test_maze_navigation()
        print()
        test_village_square_connection()
        print()
        print("=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
