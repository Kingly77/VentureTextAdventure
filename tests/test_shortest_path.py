#!/usr/bin/env python3
"""Test that the shortest path through the maze has no opposite directions."""

from game.json_loader import load_world_from_path
from game.rooms.maze_room import MazeRoom
from collections import deque


def find_shortest_path(start_room, goal_room):
    """Find the shortest path from start to goal using BFS."""
    queue = deque([(start_room, [])])
    visited = {start_room}

    while queue:
        current, path = queue.popleft()

        if current == goal_room:
            return path

        for direction, next_room in current.exits_to.items():
            if next_room not in visited:
                # Skip non-maze rooms (like village square)
                if not isinstance(next_room, MazeRoom):
                    continue
                visited.add(next_room)
                queue.append((next_room, path + [(direction, next_room)]))

    return None


def check_opposite_directions(path):
    """Check if a path has consecutive opposite directions."""
    opposites = {"north": "south", "south": "north", "east": "west", "west": "east"}

    issues = []
    for i in range(len(path) - 1):
        dir1 = path[i][0]
        dir2 = path[i + 1][0]

        if opposites.get(dir1) == dir2:
            issues.append((i, dir1, dir2, path[i][1].name, path[i + 1][1].name))

    return issues


def main():
    print("=" * 60)
    print("TESTING SHORTEST PATH FOR OPPOSITE DIRECTIONS")
    print("=" * 60)
    print()

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

    print("Finding shortest path from entrance to exit...")
    path = find_shortest_path(entrance, exit_room)

    if not path:
        print("❌ No path found!")
        return False

    print(f"✓ Shortest path found! Length: {len(path)} steps\n")
    print("Path:")
    print(f"  Start: {entrance.name}")
    for i, (direction, room) in enumerate(path, 1):
        print(f"  {i}. go {direction} -> {room.name}")

    print()
    print("Checking for opposite-direction sequences...")
    issues = check_opposite_directions(path)

    if issues:
        print(
            f"❌ Found {len(issues)} opposite-direction sequence(s) in shortest path:"
        )
        for step_idx, dir1, dir2, room1, room2 in issues:
            print(f"  Step {step_idx+1}: go {dir1} to {room1}")
            print(f"  Step {step_idx+2}: go {dir2} to {room2}")
            print(f"  ⚠ {dir2} is opposite of {dir1}!")
        print()
        print("=" * 60)
        print("TEST FAILED")
        print("=" * 60)
        return False
    else:
        print("✓ No opposite-direction sequences in shortest path!")
        print()
        print("=" * 60)
        print("TEST PASSED!")
        print("=" * 60)
        return True


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
