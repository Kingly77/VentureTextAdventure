#!/usr/bin/env python3
"""Test script to verify treasure chamber connection to maze exit."""

from game.json_loader import load_world_from_path
from game.rooms.maze_room import MazeRoom


def test_treasure_chamber_connection():
    """Test that the treasure chamber is connected to the maze exit."""
    print("Loading world from JSON...")
    rooms, start_key, hero_cfg = load_world_from_path(
        "../game/worlds/default_world.json"
    )

    print(f"✓ World loaded successfully")
    print(f"  Total rooms: {len(rooms)}")

    # Check if treasure_chamber exists
    if "treasure_chamber" not in rooms:
        print("✗ FAIL: treasure_chamber not found in loaded rooms")
        return False

    treasure_chamber = rooms["treasure_chamber"]
    print(f"✓ treasure_chamber found")
    print(f"  Name: {treasure_chamber.name}")
    print(f"  Description: {treasure_chamber.base_description}")

    # Check if maze_entrance_exit exists
    if "maze_entrance_exit" not in rooms:
        print("✗ FAIL: maze_entrance_exit not found in loaded rooms")
        return False

    maze_exit = rooms["maze_entrance_exit"]
    print(f"✓ maze_entrance_exit found")
    print(f"  Name: {maze_exit.name}")

    # Check that it's a MazeRoom
    if not isinstance(maze_exit, MazeRoom):
        print(f"✗ FAIL: maze_exit is {type(maze_exit).__name__}, not MazeRoom")
        return False

    print(f"✓ maze_exit is a MazeRoom instance")

    # Check the link from maze exit to treasure chamber
    if "east" not in maze_exit.exits_to:
        print("✗ FAIL: maze_exit has no east exit")
        print(f"  Available exits: {list(maze_exit.exits_to.keys())}")
        return False

    if maze_exit.exits_to["east"] != treasure_chamber:
        print("✗ FAIL: maze_exit east exit doesn't point to treasure_chamber")
        print(f"  Points to: {maze_exit.exits_to['east'].name}")
        return False

    print(f"✓ maze_exit -> east -> treasure_chamber link verified")

    # Check the back link from treasure chamber to maze exit
    if "west" not in treasure_chamber.exits_to:
        print("✗ FAIL: treasure_chamber has no west exit")
        print(f"  Available exits: {list(treasure_chamber.exits_to.keys())}")
        return False

    if treasure_chamber.exits_to["west"] != maze_exit:
        print("✗ FAIL: treasure_chamber west exit doesn't point to maze_exit")
        print(f"  Points to: {treasure_chamber.exits_to['west'].name}")
        return False

    print(f"✓ treasure_chamber -> west -> maze_exit link verified")

    print("\n✓ ALL TESTS PASSED!")
    print("\nSummary:")
    print("  - Treasure chamber is properly created")
    print("  - Maze exit links east to treasure chamber")
    print("  - Treasure chamber links west back to maze exit")
    print(
        "  - Players can navigate: maze -> ... -> maze exit -> east -> treasure chamber"
    )
    return True


if __name__ == "__main__":
    try:
        success = test_treasure_chamber_connection()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ EXCEPTION: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
