import json
import pytest

from game.game_world_initializer import setup_game
from game.room import Room
from game.effects.locked_door_effect import LockedDoorEffect
from game.underlings.events import Events as Event


def test_json_declares_events_and_effects(tmp_path):
    # Clear previous events in case test order interferes
    Event.clear_all_events()

    data = {
        "hero": {"name": "JsonHero", "level": 1, "gold": 0},
        "start_room": "manor",
        "rooms": {
            "manor": {
                "name": "Manor",
                "description": "A small manor.",
                "links": [{"dir": "north", "to": "foyer", "back": "south"}],
                # Add a locked door effect via registry
                "effects": [
                    {
                        "key": "locked_door",
                        "params": {
                            "door_name": "door",
                            "target": "foyer",
                            "unlock_event": "unlock_foyer",
                            "allow_bash": True,
                        },
                    }
                ],
            },
            "foyer": {"name": "Foyer", "description": "A cozy foyer.", "locked": True},
        },
        # Declare an event that calls foyer.unlock
        "events": [
            {"name": "unlock_foyer", "room": "foyer", "action": "unlock", "one_time": True}
        ],
    }

    p = tmp_path / "world.json"
    p.write_text(json.dumps(data))

    hero, start_room = setup_game(json_path=str(p))

    # Event should be registered
    assert "unlock_foyer" in Event.list_events()

    # Effect should be attached to the manor room
    assert isinstance(start_room, Room)
    manor = start_room
    assert any(isinstance(e, LockedDoorEffect) for e in manor.effects)

    # Target room exists and is locked initially
    foyer = manor.exits_to["north"]
    assert foyer.name == "Foyer"
    assert foyer.is_locked is True
