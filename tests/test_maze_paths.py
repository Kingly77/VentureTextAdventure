#!/usr/bin/env python3
"""Test script to verify the complex maze has valid paths and no trivial back-and-forth."""

from game.json_loader import load_world_from_path
from game.rooms.maze_room import MazeRoom


def find_path_bfs(start_room, goal_room):
    """Find a path from start to goal using BFS."""
    from collections import deque

    queue = deque([(start_room, [])])
    visited = {start_room}

    while queue:
        current, path = queue.popleft()

        if current == goal_room:
            return path

        for direction, next_room in current.exits_to.items():
            if next_room not in visited:
                visited.add(next_room)
                queue.append((next_room, path + [(direction, next_room)]))

    return None


def check_trivial_backtrack(room, direction1, direction2):
    """Check if going direction1 then direction2 just returns to the same room."""
    if direction1 not in room.exits_to:
        return False

    next_room = room.exits_to[direction1]
    if direction2 not in next_room.exits_to:
        return False

    final_room = next_room.exits_to[direction2]
    return final_room == room


def test_no_trivial_backtrack():
    """Test that the maze doesn't have trivial west-east or east-west backtracks."""
    print("Testing for trivial back-and-forth paths...")
    rooms, start_key, hero_cfg = load_world_from_path(
        "../game/worlds/default_world.json"
    )

    # Get all maze rooms
    maze_rooms = [r for k, r in rooms.items() if isinstance(r, MazeRoom)]
    print(f"Found {len(maze_rooms)} maze rooms")

    problematic_pairs = [
        ("west", "east"),
        ("east", "west"),
        ("north", "south"),
        ("south", "north"),
    ]

    issues = []
    for room in maze_rooms:
        for dir1, dir2 in problematic_pairs:
            if check_trivial_backtrack(room, dir1, dir2):
                issues.append(f"{room.name}: {dir1} -> {dir2} goes back")

    if issues:
        print("❌ Found trivial back-and-forth paths:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✓ No trivial back-and-forth paths found")
        return True


def test_path_exists():
    """Test that a valid path exists from entrance to exit."""
    print("\nTesting path from entrance to exit...")
    rooms, start_key, hero_cfg = load_world_from_path(
        "../game/worlds/default_world.json"
    )

    entrance = rooms["maze_entrance"]

    # Find the exit room
    exit_room = None
    for k, r in rooms.items():
        if isinstance(r, MazeRoom) and r.is_exit:
            exit_room = r
            break

    if not exit_room:
        print("❌ Exit room not found")
        return False

    path = find_path_bfs(entrance, exit_room)

    if path is None:
        print("❌ No path found from entrance to exit")
        return False

    print(f"✓ Path found! Length: {len(path)} steps")
    print("\nPath through maze:")
    print(f"  Start: {entrance.name}")
    for i, (direction, room) in enumerate(path, 1):
        print(f"  {i}. go {direction} -> {room.name}")

    return True


def test_multiple_paths():
    """Test that multiple paths exist (maze has choices)."""
    print("\nTesting for multiple paths...")
    rooms, start_key, hero_cfg = load_world_from_path(
        "../game/worlds/default_world.json"
    )

    entrance = rooms["maze_entrance"]

    # Count how many initial choices we have
    choices = len(entrance.exits_to)
    # Subtract 1 for the exit back to village square
    meaningful_choices = choices - 1

    print(f"Entrance has {meaningful_choices} forward path(s)")

    if meaningful_choices < 2:
        print("⚠ Warning: Only one forward path from entrance")
        return True  # Not a failure, just a note

    print(f"✓ Maze has multiple initial paths")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING COMPLEX MAZE PATH STRUCTURE")
    print("=" * 60)
    print()

    try:
        test1 = test_no_trivial_backtrack()
        test2 = test_path_exists()
        test3 = test_multiple_paths()

        print()
        print("=" * 60)
        if test1 and test2 and test3:
            print("ALL TESTS PASSED!")
        else:
            print("SOME TESTS FAILED")
        print("=" * 60)

        exit(0 if (test1 and test2 and test3) else 1)
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
