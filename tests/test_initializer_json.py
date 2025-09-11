import json
import pytest

from game.game_world_initializer import setup_game


def test_setup_game_with_json_overrides_world(tmp_path):
    data = {
        "hero": {"name": "JsonHero", "level": 3, "gold": 7},
        "start_room": "village",
        "rooms": {
            "village": {
                "name": "Village",
                "description": "A quiet village.",
                "links": [{"dir": "east", "to": "field", "back": "west"}],
                "items": [{"name": "bread", "value": 1}],
            },
            "field": {
                "name": "Field",
                "description": "A grassy field.",
                "items": [],
            },
        },
    }
    p = tmp_path / "world.json"
    p.write_text(json.dumps(data))

    # New API: setup_game(json_path=...)
    hero, start_room = setup_game(json_path=str(p))

    # Hero customized
    assert hero.name == "JsonHero"
    assert hero.level == 3
    assert hero.gold == 7

    # World customized
    assert start_room.name == "Village"
    assert start_room.inventory.has_component("bread")
    assert "east" in start_room.exits_to
    assert start_room.exits_to["east"].name == "Field"
