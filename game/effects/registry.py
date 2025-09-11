from __future__ import annotations
from typing import Callable, Dict, Any

from game.effects.locked_door_effect import LockedDoorEffect
from game.effects.torch_effect import TorchEffect
from game.effects.room_effects import NPCDialogEffect, DarkCaveLightingEffect

# Registry maps effect key -> factory(room, params, rooms_by_key) -> effect instance
_REGISTRY: Dict[str, Callable] = {}


def register_effect(key: str, factory: Callable[["Room", Dict[str, Any], Dict[str, "Room"]], object]):
    lk = (key or "").strip().lower()
    if not lk:
        raise ValueError("Effect key must be a non-empty string")
    _REGISTRY[lk] = factory


def get_effect_factory(key: str) -> Callable | None:
    return _REGISTRY.get((key or "").strip().lower())


# Built-in effect factories

def _locked_door_factory(room, params: Dict[str, Any], rooms_by_key):
    target_key = params.get("target")
    if not target_key:
        raise ValueError("locked_door effect requires 'target' room key in params")
    target_room = rooms_by_key[target_key]
    return LockedDoorEffect(
        room,
        target_room,
        door_name=params.get("door_name", "door"),
        locked_description=params.get("locked_description"),
        unlocked_description=params.get("unlocked_description"),
        key_name=params.get("key_name"),
        unlock_event=params.get("unlock_event"),
        allow_bash=bool(params.get("allow_bash", True)),
    )


def _torch_factory(room, params: Dict[str, Any], rooms_by_key):
    # TorchEffect doesn't use params
    return TorchEffect(room)


def _npc_dialog_factory(room, params: Dict[str, Any], rooms_by_key):
    # Minimal support: npc_name and npc_description
    return NPCDialogEffect(
        room,
        npc_name=params.get("npc_name", "Quest Giver"),
        npc_description=params.get("npc_description", "is here."),
    )


def _dark_cave_factory(room, params: Dict[str, Any], rooms_by_key):
    return DarkCaveLightingEffect(room)


# Register built-in keys
register_effect("locked_door", _locked_door_factory)
register_effect("torch_table", _torch_factory)
register_effect("npc_dialog", _npc_dialog_factory)
register_effect("dark_cave", _dark_cave_factory)
