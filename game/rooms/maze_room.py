from __future__ import annotations

from game.rooms.effect_room import EffectRoom
from typing import Dict, List, Optional


class MazeRoom(EffectRoom):
    """A room that is part of a maze.
    
    MazeRoom extends EffectRoom to provide specialized behavior for maze navigation.
    Players navigate through the maze using normal go commands (north, south, east, west).
    """

    def __init__(self, name: str, description: str, exits=None, link_to=None, is_entrance=False, is_exit=False):
        """Initialize a MazeRoom.
        
        Args:
            name: Name of the room
            description: Description of the room
            exits: Optional pre-populated exits
            link_to: Optional bidirectional links
            is_entrance: Whether this is the maze entrance
            is_exit: Whether this is the maze exit
        """
        super().__init__(name, description, exits=exits, link_to=link_to)
        self.is_entrance = is_entrance
        self.is_exit = is_exit

    def get_modified_description(self, base_description: str) -> str:
        """Add hints about the maze location."""
        if self.is_entrance:
            return base_description + " You can sense this is where the maze begins."
        elif self.is_exit:
            return base_description + " There's a feeling of relief here - an exit must be nearby."
        else:
            return base_description + " The twisting passages all look alike."

    def on_enter(self, hero):
        """Called when hero enters this maze room."""
        super().on_enter(hero)
        
        if self.is_entrance:
            print("You have entered the maze. Find your way through!")
        elif self.is_exit:
            print("You sense you're close to the exit!")


def create_simple_maze() -> Dict[str, MazeRoom]:
    """Creates a simple maze with multiple interconnected rooms.
    
    The maze layout:
        [Entrance] -> [Junction1] -> [DeadEnd1]
            |              |
            v              v
        [Junction2] -> [Center] -> [DeadEnd2]
            |              |
            v              v
        [DeadEnd3]     [Exit]
    
    Returns:
        Dictionary mapping room names to MazeRoom instances
    """
    # Create all the maze rooms
    entrance = MazeRoom(
        "Maze Entrance",
        "A stone archway marks the entrance to a confusing maze.",
        is_entrance=True
    )
    
    junction1 = MazeRoom(
        "North Junction",
        "Stone corridors branch off in multiple directions."
    )
    
    junction2 = MazeRoom(
        "West Junction",
        "The passages twist and turn here."
    )
    
    center = MazeRoom(
        "Maze Center",
        "A circular chamber with passages leading in all directions."
    )
    
    dead_end1 = MazeRoom(
        "Dead End",
        "The passage comes to an abrupt end at a solid wall."
    )
    
    dead_end2 = MazeRoom(
        "Another Dead End",
        "You've hit another dead end. The wall is covered in ancient marks."
    )
    
    dead_end3 = MazeRoom(
        "Third Dead End",
        "Yet another passage that leads nowhere."
    )
    
    exit_room = MazeRoom(
        "Maze Exit",
        "Light streams in from ahead - you can see the way out!",
        is_exit=True
    )
    
    # Connect the rooms to form the maze
    # Entrance connections
    entrance.link_rooms("north", junction1, "south")
    entrance.link_rooms("west", junction2, "east")
    
    # Junction1 connections
    junction1.link_rooms("east", dead_end1, "west")
    junction1.link_rooms("west", center, "north")
    
    # Junction2 connections
    junction2.link_rooms("north", center, "west")
    junction2.link_rooms("south", dead_end3, "north")
    
    # Center connections (already connected to junction1 and junction2)
    center.link_rooms("east", dead_end2, "west")
    center.link_rooms("south", exit_room, "north")
    
    # Return dictionary of all rooms for easy access
    return {
        "entrance": entrance,
        "junction1": junction1,
        "junction2": junction2,
        "center": center,
        "dead_end1": dead_end1,
        "dead_end2": dead_end2,
        "dead_end3": dead_end3,
        "exit": exit_room
    }


def create_complex_maze() -> Dict[str, MazeRoom]:
    """Creates a more complex maze with more rooms and twisting paths.
    
    Returns:
        Dictionary mapping room names to MazeRoom instances
    """
    # Create maze rooms
    entrance = MazeRoom(
        "Maze Entrance",
        "You stand before the entrance to a vast, complex maze.",
        is_entrance=True
    )
    
    rooms = [entrance]
    
    # Create a grid of rooms (4x4 maze)
    for i in range(1, 16):
        room = MazeRoom(
            f"Maze Room {i}",
            "Stone walls surround you on all sides, with passages leading away."
        )
        rooms.append(room)
    
    # The exit is the last room
    exit_room = MazeRoom(
        "Maze Exit",
        "You can see daylight ahead - freedom is within reach!",
        is_exit=True
    )
    rooms.append(exit_room)
    
    # Connect rooms in a complex pattern (not a simple grid)
    # This creates a more challenging maze with multiple paths
    # Main path from entrance
    entrance.link_rooms("north", rooms[1], "south")
    entrance.link_rooms("east", rooms[2], "west")
    
    # Primary path branches
    rooms[1].link_rooms("north", rooms[3], "south")
    rooms[1].link_rooms("east", rooms[4], "west")
    
    rooms[2].link_rooms("north", rooms[5], "south")
    
    # Middle sections with choices
    rooms[3].link_rooms("east", rooms[6], "west")
    rooms[4].link_rooms("north", rooms[7], "south")
    rooms[5].link_rooms("east", rooms[7], "west")
    
    rooms[6].link_rooms("north", rooms[8], "south")
    rooms[7].link_rooms("east", rooms[9], "west")
    
    # Upper sections converging
    rooms[8].link_rooms("east", rooms[10], "west")
    rooms[9].link_rooms("north", rooms[11], "south")
    
    rooms[10].link_rooms("north", rooms[12], "south")
    rooms[11].link_rooms("east", rooms[13], "west")
    
    # Final approach to exit
    rooms[12].link_rooms("east", rooms[14], "west")
    rooms[13].link_rooms("north", rooms[14], "south")
    
    rooms[14].link_rooms("north", rooms[15], "south")
    rooms[15].link_rooms("east", exit_room, "west")
    
    # Add some cross-connections for loops and alternative routes
    # These should not require going in opposite directions
    rooms[4].link_rooms("east", rooms[9], "south")  # Skip from 4 to 9
    rooms[6].link_rooms("east", rooms[11], "west")  # Skip from 6 to 11
    rooms[12].link_rooms("south", rooms[13], "north")  # Connect 12 to 13
    
    # Build return dictionary
    result = {"entrance": entrance, "exit": exit_room}
    for i, room in enumerate(rooms[1:-1], 1):
        result[f"room{i}"] = room
    
    return result
