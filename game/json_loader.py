from __future__ import annotations

import json
import importlib
from typing import Dict, Tuple, Any

from game.room import Room
from game.items import Item
from game.effects.item_effects.item_effects import Effect


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

        # Decide which Room class to instantiate
        # 1) If 'room_class' provided, resolve it as a subclass of EffectRoom (preferred explicit form)
        # 2) If 'room_type' == 'effect' or 'is_effect_room': true, use base EffectRoom
        # 3) If 'room_type' is a non-empty string and not 'effect', try treating it as a class name
        # 4) Otherwise, use plain Room
        room = None
        room_class_spec = rd.get("room_class") or None
        room_type_spec_raw = rd.get("room_type")
        room_type_spec = (
            str(room_type_spec_raw).strip() if room_type_spec_raw is not None else ""
        )

        def _resolve_effect_room_class(spec: str):
            # Returns a class object for an EffectRoom subclass given a string spec
            # Supports fully qualified name (e.g., "my.mod.Class") or short name resolved in game.effect_room
            # EffectRooms go in game.rooms
            from game.rooms.effect_room import EffectRoom  # local import

            if not spec:
                return None
            spec = str(spec).strip()
            cls = None
            if "." in spec:
                mod_path, cls_name = spec.rsplit(".", 1)
                try:
                    mod = importlib.import_module(mod_path)
                    cls = getattr(mod, cls_name, None)
                except Exception:
                    cls = None
            else:
                try:
                    mod = importlib.import_module("game.rooms.effect_room")
                    cls = getattr(mod, spec, None)
                except Exception:
                    cls = None
            if cls is None:
                raise ValueError(f"Could not resolve EffectRoom subclass '{spec}'")
            # Validate subclass
            if not issubclass(cls, EffectRoom):
                raise ValueError(f"Class '{spec}' is not a subclass of EffectRoom")
            return cls

        # Case 1: explicit room_class
        if room_class_spec:
            Cls = _resolve_effect_room_class(room_class_spec)
            room = Cls(name, desc)
        else:
            # Case 2: flags for base EffectRoom
            is_effect_room_flag = (
                bool(rd.get("is_effect_room", False))
                or room_type_spec.lower() == "effect"
            )
            if is_effect_room_flag:
                from game.rooms.effect_room import EffectRoom  # local import

                room = EffectRoom(name, desc)
            else:
                # Case 3: room_type used as class name
                if room_type_spec and room_type_spec.lower() not in {
                    "",
                    "effect",
                    "room",
                }:
                    # attempt to resolve as EffectRoom subclass
                    Cls = _resolve_effect_room_class(room_type_spec)
                    room = Cls(name, desc)
                else:
                    room = Room(name, desc)

        room.is_locked = bool(rd.get("locked", False))
        rooms[key] = room

    # Import once for subsequent passes
    from character import enemy as enemy_mod
    from game.effects.registry import get_effect_factory
    from game.npc import NPC
    from game.underlings.events import Events as Event

    # Combined subsequent passes in a single traversal to reduce lookups/iterations
    for key, rd in rooms_data.items():
        room = rooms[key]

        # Items
        add_item = room.add_item
        for item_d in rd.get("items", ()) or ():
            add_item(_make_item(item_d))

        # Links (bidirectional if back is provided)
        add_exit = room.add_exit
        link_rooms = room.link_rooms
        for link in rd.get("links", ()) or ():
            direction = link["dir"]
            target_room = rooms[link["to"]]
            back = link.get("back")
            if back:
                link_rooms(direction, target_room, back)
            else:
                add_exit(direction, target_room)

        # Enemies
        combatants = room.combatants
        for ed in rd.get("enemies", ()) or ():
            etype = (ed.get("type") or "").strip()
            if not etype:
                raise ValueError("Enemy entry requires 'type'")
            tkey = etype.lower()
            cls_name = tkey.capitalize() if tkey in {"goblin", "troll"} else etype
            EnemyClass = getattr(enemy_mod, cls_name, None)
            if EnemyClass is None:
                raise ValueError(f"Unknown enemy type: {etype}")
            count = int(ed.get("count", 1))
            level = int(ed.get("level", 1))
            base_name = ed.get("name", cls_name)
            reward_cfg = ed.get("reward") or None
            # Localize for speed
            make_item = _make_item
            for i in range(count):
                name = base_name if count == 1 else f"{base_name} {i+1}"
                foe = EnemyClass(name, level)
                if isinstance(reward_cfg, dict) and reward_cfg:
                    foe.reward = make_item(reward_cfg)
                combatants.append(foe)

        # Effects via registry
        add_effect = room.add_effect
        for eff in rd.get("effects", ()) or ():
            eff_key = eff.get("key")
            params = eff.get("params", {}) or {}
            factory = get_effect_factory(eff_key)
            if factory is None:
                raise ValueError(f"Unknown effect key: {eff_key}")
            effect_instance = factory(room, params, rooms)
            add_effect(effect_instance)

        # Simple NPCs
        add_npc = room.add_npc
        for nd in rd.get("npcs", ()) or ():
            n = (nd.get("name") or "").strip()
            dsc = nd.get("description")
            if not n or not isinstance(dsc, str) or not dsc.strip():
                raise ValueError(
                    "NPC entries must include non-empty 'name' and 'description'"
                )
            add_npc(NPC(n, dsc))

    # Top-level events
    for ev in data.get("events", ()) or ():
        name = ev["name"]
        room_key = ev.get("room")
        action = ev.get("action")
        one_time = bool(ev.get("one_time", False))
        if room_key is None or action is None:
            raise ValueError("Event entries must include 'room' and 'action'")
        handler_room = rooms.get(room_key)
        if handler_room is None:
            raise ValueError(f"Event room key '{room_key}' not found")
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
