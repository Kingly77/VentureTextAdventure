from __future__ import annotations

import json
from typing import Dict, Tuple, Any

from game.room import Room
from game.items import Item
from components.core_components import Effect


def _make_item(d: dict) -> Item:
    """Create an Item from a simple dict.

    Expected fields (all optional except name and value):
      - name: str
      - value: int (mapped to Item.cost)
      - is_usable: bool
      - effect: str in {"NONE","HEAL","DAMAGE"}
      - effect_value: int
      - is_consumable: bool
      - is_equipment: bool
      - tags: list[str]
      - quantity: int
    """
    name = d["name"]
    cost = int(d.get("value", 0))
    is_usable = bool(d.get("is_usable", False))
    effect_name = str(d.get("effect", "NONE")).upper()
    effect = getattr(Effect, effect_name, Effect.NONE)
    effect_value = int(d.get("effect_value", 0))
    is_consumable = bool(d.get("is_consumable", False))
    is_equipment = bool(d.get("is_equipment", False))
    tags = d.get("tags", [])
    quantity = int(d.get("quantity", 1))
    return Item(
        name,
        cost,
        is_usable,
        effect,
        effect_value,
        is_consumable=is_consumable,
        is_equipment=is_equipment,
        tags=tags,
        quantity=quantity,
    )


def load_world(data: Dict[str, Any]) -> Tuple[Dict[str, Room], str, Dict[str, Any]]:
    """Load a world from a JSON-like dict.

    Returns (rooms_by_key, start_room_key, hero_cfg)
    """
    if "rooms" not in data:
        raise KeyError("rooms")
    if "start_room" not in data:
        raise KeyError("start_room")

    rooms_data: Dict[str, dict] = data["rooms"]

    # First pass: create all Room objects
    rooms: Dict[str, Room] = {}
    for key, rd in rooms_data.items():
        name = rd.get("name")
        desc = rd.get("description")
        if not name or not desc:
            raise ValueError(f"Room '{key}' must have name and description")
        room = Room(name, desc)
        room.is_locked = bool(rd.get("locked", False))
        rooms[key] = room

    # Second pass: items
    for key, rd in rooms_data.items():
        room = rooms[key]
        for item_d in rd.get("items", []) or []:
            room.add_item(_make_item(item_d))

    # Third pass: links (bidirectional if back is provided)
    for key, rd in rooms_data.items():
        room = rooms[key]
        for link in rd.get("links", []) or []:
            direction = link["dir"]
            target_key = link["to"]
            target_room = rooms[target_key]
            back = link.get("back")
            if back:
                room.link_rooms(direction, target_room, back)
            else:
                room.add_exit(direction, target_room)

    # Fourth pass: effects via registry
    from game.effects.registry import get_effect_factory
    for key, rd in rooms_data.items():
        room = rooms[key]
        for eff in rd.get("effects", []) or []:
            eff_key = eff.get("key")
            params = eff.get("params", {}) or {}
            factory = get_effect_factory(eff_key)
            if factory is None:
                raise ValueError(f"Unknown effect key: {eff_key}")
            effect_instance = factory(room, params, rooms)
            # Room.add_effect performs its own validation
            room.add_effect(effect_instance)

    # Top-level events
    from game.underlings.events import Events as Event
    for ev in data.get("events", []) or []:
        name = ev["name"]
        room_key = ev.get("room")
        action = ev.get("action")
        one_time = bool(ev.get("one_time", False))
        if room_key is None or action is None:
            raise ValueError("Event entries must include 'room' and 'action'")
        if room_key not in rooms:
            raise ValueError(f"Event room key '{room_key}' not found")
        handler_room = rooms[room_key]
        handler = getattr(handler_room, action)
        Event.add_event(name, handler, one_time)

    hero_cfg = data.get("hero", {}) or {}
    start_key = data["start_room"]
    if start_key not in rooms:
        raise ValueError("start_room must reference an existing room key")

    return rooms, start_key, hero_cfg


essential_keys = ("rooms", "start_room")


def load_world_from_path(path: str) -> Tuple[Dict[str, Room], str, Dict[str, Any]]:
    """Open a JSON file and call load_world."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return load_world(data)
