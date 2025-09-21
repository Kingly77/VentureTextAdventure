from __future__ import annotations

import abc

from interfaces.room_effect_base import RoomDiscEffect
from game.room import Room


class EffectRoom(Room, RoomDiscEffect, abc.ABC):
    """
    A Room that is also an effect.

    This subclass makes the room itself implement the RoomDiscEffect interface so it
    can intercept interactions and modify descriptions just like any other effect.

    Minimal integration: we do not change other code. Upon initialization, the room
    instance registers itself as the first effect in its own effects list so all
    existing effect-dispatching code continues to work. Users can subclass
    EffectRoom and override RoomDiscEffect methods (e.g., handle_interaction,
    handle_item_use, get_modified_description, etc.) to define behavior.
    """

    def __init__(self, name: str, description: str, exits=None, link_to=None):
        # Initialize Room normally
        Room.__init__(self, name, description, exits=exits, link_to=link_to)
        # Initialize the RoomDiscEffect with this room instance
        RoomDiscEffect.__init__(self, self)
        # Ensure this effect (the room itself) runs first
        # Insert at the front to let the room intercept before other effects
        self.effects.insert(0, self)

    # The RoomDiscEffect base already provides no-op/default implementations for
    # all hooks. Users can override them in subclasses of EffectRoom as needed.

    def get_modified_description(self, base_description: str) -> str:
        """Default passthrough to preserve prior behavior in tests."""
        return base_description


class ExampleEffectRoom(EffectRoom):
    """A simple EffectRoom subclass to be used by JSON loader tests.

    It appends a suffix to the description and recognizes an interaction.
    """

    def get_modified_description(self, base_description: str) -> str:
        return base_description + " (An eerie aura lingers here.)"

    def handle_interaction(self, verb: str, target_name: str, val_hero, item, room):
        if verb == "examine" and target_name == "aura":
            return "The aura hums softly as you focus on it."
        return None
