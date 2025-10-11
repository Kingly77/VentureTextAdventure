#!/usr/bin/env python3
"""Test that maze paths don't require going in opposite directions to progress."""
import pytest

from game.json_loader import load_world_from_path
from game.rooms.maze_room import MazeRoom
from collections import deque


def find_all_paths(start_room, goal_room, max_length=20):
    """Find all paths from start to goal using BFS, up to max_length."""
    queue = deque([(start_room, [])])
    visited_paths = set()
    all_paths = []

    while queue:
        current, path = queue.popleft()

        # Create a hashable representation of the path
        path_key = tuple((r, d) for d, r in path)
        if path_key in visited_paths:
            continue
        visited_paths.add(path_key)

        if current == goal_room:
            all_paths.append(path)
            continue

        if len(path) >= max_length:
            continue

        for direction, next_room in current.exits_to.items():
            # Don't go back to village square
            if not isinstance(next_room, MazeRoom):
                continue
            queue.append((next_room, path + [(direction, next_room)]))

    return all_paths


def check_opposite_directions(path):
    """Check if a path requires going in opposite directions consecutively."""
    opposites = {"north": "south", "south": "north", "east": "west", "west": "east"}

    issues = []
    for i in range(len(path) - 1):
        dir1 = path[i][0]
        dir2 = path[i + 1][0]

        # Check if the second direction is opposite to the first
        if opposites.get(dir1) == dir2:
            issues.append((i, dir1, dir2, path[i][1].name, path[i + 1][1].name))

    return issues


@pytest.mark.skip
def test_paths_no_opposite_directions():
    """Test that paths through the maze don't require opposite directions."""
    print("Testing paths for opposite-direction sequences...")
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

    print(f"Finding all paths from entrance to exit...")
    paths = find_all_paths(entrance, exit_room, max_length=15)
    print(f"Found {len(paths)} paths")

    if not paths:
        print("❌ No paths found!")
        return False

    # Check each path for opposite directions
    paths_with_issues = []
    for path in paths:
        issues = check_opposite_directions(path)
        if issues:
            paths_with_issues.append((path, issues))

    if paths_with_issues:
        print(
            f"\n❌ Found {len(paths_with_issues)} path(s) with opposite-direction sequences:"
        )
        for path, issues in paths_with_issues[:3]:  # Show first 3
            print(f"\n  Path length: {len(path)}")
            for step_idx, dir1, dir2, room1, room2 in issues:
                print(
                    f"    Step {step_idx+1}-{step_idx+2}: go {dir1} to {room1}, then go {dir2} to {room2}"
                )
                print(f"      ⚠ Going {dir2} is opposite of {dir1}!")
        return False
    else:
        print(f"\n✓ No paths require opposite-direction sequences!")
        print(f"\nShortest path ({len(paths[0])} steps):")
        print(f"  Start: {entrance.name}")
        for i, (direction, room) in enumerate(paths[0], 1):
            print(f"  {i}. go {direction} -> {room.name}")
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING FOR OPPOSITE-DIRECTION PATH REQUIREMENTS")
    print("=" * 60)
    print()

    try:
        success = test_paths_no_opposite_directions()
        print()
        print("=" * 60)
        if success:
            print("TEST PASSED!")
        else:
            print("TEST FAILED")
        print("=" * 60)
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
