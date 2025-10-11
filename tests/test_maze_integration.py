#!/usr/bin/env python3
"""Test script to verify MazeRoom integration with JSON loader."""

from game.json_loader import load_world_from_path
from game.rooms.maze_room import MazeRoom


def test_maze_room_loading():
    """Test that the maze room loads correctly from JSON."""
    print("Loading world from JSON...")
    rooms, start_key, hero_cfg = load_world_from_path(
        "../game/worlds/default_world.json"
    )

    print(f"✓ World loaded successfully")
    print(f"  Start room: {start_key}")
    print(f"  Total rooms: {len(rooms)}")

    # Check if maze_entrance exists
    if "maze_entrance" not in rooms:
        print("✗ FAIL: maze_entrance not found in loaded rooms")
        return False

    maze_room = rooms["maze_entrance"]
    print(f"✓ maze_entrance found")

    # Check if it's an instance of MazeRoom
    if not isinstance(maze_room, MazeRoom):
        print(f"✗ FAIL: maze_entrance is {type(maze_room).__name__}, not MazeRoom")
        return False

    print(f"✓ maze_entrance is a MazeRoom instance")

    # Check room properties
    print(f"  Name: {maze_room.name}")
    print(f"  Description: {maze_room.base_description}")

    # Check that it's linked to village_square
    village_square = rooms.get("village_square")
    if not village_square:
        print("✗ FAIL: village_square not found")
        return False

    # Check the link from village_square to maze
    if "north" not in village_square.exits_to:
        print("✗ FAIL: village_square has no north exit")
        return False

    if village_square.exits_to["north"] != maze_room:
        print("✗ FAIL: village_square north exit doesn't point to maze_entrance")
        return False

    print(f"✓ village_square -> north -> maze_entrance link verified")

    # Check the back link from maze to village_square
    if "south" not in maze_room.exits_to:
        print("✗ FAIL: maze_entrance has no south exit")
        return False

    if maze_room.exits_to["south"] != village_square:
        print("✗ FAIL: maze_entrance south exit doesn't point to village_square")
        return False

    print(f"✓ maze_entrance -> south -> village_square link verified")

    # Test the modified description method
    desc = maze_room.get_description()
    print(f"✓ Description method works")
    print(f"  Full description: {desc[:100]}...")

    print("\n✓ ALL TESTS PASSED!")
    return True


if __name__ == "__main__":
    try:
        success = test_maze_room_loading()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ EXCEPTION: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
