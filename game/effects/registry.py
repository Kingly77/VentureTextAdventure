from __future__ import annotations
from typing import Callable, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from game.room import Room

from game.effects.entry_effect import EntryEffect
from game.effects.locked_door_effect import LockedDoorEffect
from game.effects.torch_effect import TorchEffect
from game.effects.room_effects import DarkCaveLightingEffect
from game.effects.npc_effect import NPCDialogEffect
from game.effects.shop_effect import ShopEffect
from game.effects.smoke_effect import SmokeEffect

# Registry maps effect key -> factory(room, params, rooms_by_key) -> effect instance
_REGISTRY: Dict[str, Callable] = {}


def register_effect(
    key: str, factory: Callable[["Room", Dict[str, Any], Dict[str, "Room"]], object]
):
    """Register a custom effect that can be used in world JSON.

    Args:
        key: Effect identifier used in JSON "effects" list
        factory: Function(room, params, rooms_by_key) -> RoomDiscEffect

    Example:
        >>> register_effect("lever", lambda r, p, _: LeverEffect(r))
        >>> # Then in JSON: {"key": "lever", "params": {}}
    """
    lk = (key or "").strip().lower()
    if not lk:
        raise ValueError("Effect key must be a non-empty string")
    _REGISTRY[lk] = factory


def get_effect_factory(key: str) -> Callable | None:
    return _REGISTRY.get((key or "").strip().lower())


# Built-in effect factories


def _entery_effect_factory(room, params: Dict[str, Any], rooms_by_key):
    return EntryEffect(room, params.get("msg"))


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
    # Support basic NPC dialog plus optional quest parameters
    npc_name = params.get("npc_name", "Quest Giver")
    npc_desc = params.get("npc_description", "is here.")

    quest_cfg = params.get("quest") or None
    quest_factory = None
    if isinstance(quest_cfg, dict):
        # Lazy import inside factory creation to avoid circular imports
        def _factory():
            from game.quest import Quest, Objective  # local import

            name = quest_cfg.get("name", "goblin ear")
            description = quest_cfg.get(
                "description",
                "Collect the goblin ear to defeat the goblin foe.",
            )
            reward = int(quest_cfg.get("reward", 100))
            obj = quest_cfg.get("objective") or {}
            obj_type = obj.get("type", "collect")
            obj_target = obj.get("target", "goblin ear")
            obj_value = int(obj.get("value", 1))
            return Quest(
                name,
                description,
                reward,
                objective=Objective(obj_type, obj_target, obj_value),
            )

        quest_factory = _factory

    return NPCDialogEffect(
        room,
        npc_name=npc_name,
        npc_description=npc_desc,
        quest_factory=quest_factory,
    )


def _dark_cave_factory(room, params: Dict[str, Any], rooms_by_key):
    return DarkCaveLightingEffect(room)


def _shop_factory(room, params: Dict[str, Any], rooms_by_key):
    name = params.get("shopkeeper_name", "The Merchant")
    prices = params.get("prices") or {}
    return ShopEffect(room, shopkeeper_name=name, prices=prices)


def _smoke_factory(room, params: Dict[str, Any], rooms_by_key):
    intensity = int(params.get("intensity", 5))
    persistent = bool(params.get("persistent", True))
    return SmokeEffect(room, intensity=intensity, persistent=persistent)


# Register built-in keys
register_effect("locked_door", _locked_door_factory)
register_effect("torch_table", _torch_factory)
register_effect("npc_dialog", _npc_dialog_factory)
register_effect("dark_cave", _dark_cave_factory)
register_effect("shop", _shop_factory)
register_effect("entry", _entery_effect_factory)
register_effect("smoke", _smoke_factory)
