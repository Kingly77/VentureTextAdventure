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



def test_loader_reads_npcs(tmp_path):
    data = {
        "hero": {"name": "JsonHero", "level": 1, "gold": 0},
        "start_room": "plaza",
        "rooms": {
            "plaza": {
                "name": "Plaza",
                "description": "A bustling plaza.",
                "npcs": [
                    {"name": "Guide", "description": "waves cheerfully."}
                ],
            }
        },
    }
    p = tmp_path / "world.json"
    p.write_text(json.dumps(data))

    rooms, start_name, _ = load_world_from_path(str(p))
    start = rooms[start_name]
    text = start.get_description()
    assert "People here:" in text
    assert "Guide: waves cheerfully." in text

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



def test_loader_reads_npcs(tmp_path):
    data = {
        "hero": {"name": "JsonHero", "level": 1, "gold": 0},
        "start_room": "plaza",
        "rooms": {
            "plaza": {
                "name": "Plaza",
                "description": "A bustling plaza.",
                "npcs": [
                    {"name": "Guide", "description": "waves cheerfully."}
                ],
            }
        },
    }
    p = tmp_path / "world.json"
    p.write_text(json.dumps(data))

    rooms, start_name, _ = load_world_from_path(str(p))
    start = rooms[start_name]
    text = start.get_description()
    assert "People here:" in text
    assert "Guide: waves cheerfully." in text


def test_loader_supports_effect_rooms_via_room_class(tmp_path):
    # Ensure the loader can instantiate an EffectRoom subclass and that it behaves as an effect
    data = {
        "hero": {"name": "JsonHero", "level": 1, "gold": 0},
        "start_room": "mystic",
        "rooms": {
            "mystic": {
                "name": "Mystic Chamber",
                "description": "A silent hall.",
                # Use fully-qualified class path for robustness
                "room_class": "game.rooms.effect_room.ExampleEffectRoom",
            }
        },
    }
    p = tmp_path / "world.json"
    p.write_text(json.dumps(data))

    rooms, start_key, _ = load_world_from_path(str(p))
    mystic = rooms[start_key]

    # Description should be modified by the room effect
    desc = mystic.get_description()
    assert "A silent hall." in desc
    assert "An eerie aura lingers here." in desc

    # Interaction should be handled by the room effect
    result = mystic.interact("examine", "aura", user=None, item=None, room=mystic)
    assert isinstance(result, str)
    assert "hums softly" in result
