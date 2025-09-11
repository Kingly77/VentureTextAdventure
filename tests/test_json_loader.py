import json
import pytest

from game.room import Room

# We will import the loader once implemented; for now expect it to exist
from game.json_loader import load_world_from_path


@pytest.fixture
def simple_world_json(tmp_path):
    data = {
        "hero": {"name": "JsonHero", "level": 2, "gold": 42},
        "start_room": "start",
        "rooms": {
            "start": {
                "name": "Start",
                "description": "Start room",
                "links": [
                    {"dir": "north", "to": "cave", "back": "south"}
                ],
                "items": [
                    {"name": "apple", "value": 1, "is_consumable": True}
                ],
            },
            "cave": {
                "name": "Cave",
                "description": "Dark cave",
                "locked": False,
                "items": [
                    {"name": "torch", "value": 5, "is_equipment": True, "tags": ["fire"]}
                ],
            },
        },
    }
    p = tmp_path / "world.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_load_world_builds_rooms_and_links(simple_world_json):
    rooms, start_name, hero_cfg = load_world_from_path(simple_world_json)

    # start room exists and is a Room instance
    assert isinstance(rooms[start_name], Room)
    start = rooms[start_name]

    # start room links north to cave and back link exists
    assert "north" in start.exits_to
    cave = start.exits_to["north"]
    assert isinstance(cave, Room)
    assert cave.name == "Cave"
    assert cave.exits_to.get("south") is start

    # items loaded
    assert start.inventory.has_component("apple")
    assert cave.inventory.has_component("torch")

    # hero cfg propagated
    assert hero_cfg["name"] == "JsonHero"
    assert hero_cfg["level"] == 2
    assert hero_cfg["gold"] == 42


def test_loader_validates_required_fields(tmp_path):
    # missing start_room
    bad = {"rooms": {}}
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad))

    with pytest.raises((KeyError, ValueError)):
        load_world_from_path(str(p))
