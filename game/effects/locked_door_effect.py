from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import functools

if TYPE_CHECKING:
    from interfaces.interface import Combatant
    from character.hero import RpgHero
    from game.items import Item
    from game.room import Room

from interfaces.room_effect_base import RoomDiscEffect
from game.room_objs import RoomObject
from game.underlings.events import Events, EventNotFoundError


class LockedDoorEffect(RoomDiscEffect):
    """
    Generic locked door effect that can be reused for any room-to-room doorway.

    Features:
    - Adds a door RoomObject to the source room with configurable name and descriptions.
    - Supports unlocking via:
      - Using a specific key item name (key_name), or
      - Bashing with any item tagged as 'weapon' (if allow_bash=True), or
      - External puzzle/event by triggering a provided unlock_event.
    - Reacts to the provided unlock_event (if any) to update door description.
    """

    def __init__(
        self,
        room: "Room",
        target_room: "Room",
        door_name: str = "door",
        locked_description: str | None = None,
        unlocked_description: str | None = None,
        key_name: Optional[str] = None,
        unlock_event: Optional[str] = None,
        allow_bash: bool = True,
    ):
        super().__init__(room)
        self.target_room = target_room
        self.door_name = (door_name or "door").lower()
        self.key_name = key_name.lower() if isinstance(key_name, str) else None
        self.unlock_event = unlock_event
        self.allow_bash = allow_bash

        # Create and register the door object in this room
        self.locked_description = (
            locked_description
            or f"A sturdy wooden {self.door_name} with a heavy lock. It doesn't budge."
        )
        self.unlocked_description = (
            unlocked_description or f"The {self.door_name} stands open, leading onward."
        )

        self.door = RoomObject(self.door_name, self._current_door_desc())
        room.add_object(self.door)

        # If there's an external event that unlocks this door, listen for it to update visuals.
        if self.unlock_event:
            # Update the door description when unlocked via event (one-time)
            Events.add_event(
                self.unlock_event,
                functools.partial(self._on_unlocked),
                True,
            )

    def _current_door_desc(self) -> str:
        return (
            self.unlocked_description
            if not self.target_room.is_locked
            else self.locked_description
        )

    # Event callback
    def _on_unlocked(self, *_, **__):
        # If an external event unlocked the target room elsewhere, just refresh the door description
        self.door.change_description(self.unlocked_description)

    def get_modified_description(self, base_description: str) -> str:
        # This effect does not change the room narrative text directly; door object handles visuals.
        return base_description

    def handle_item_use(self, verb: str, item_name: str, user: "Combatant") -> bool:
        # No room-wide item use for this effect; interactions are object-targeted.
        return False

    def handle_interaction(
        self,
        verb: str,
        target_name: Optional[str],
        val_hero: "RpgHero",
        item: Optional["Item"],
        room: "Room",
    ) -> Optional[str]:
        vb = (verb or "").strip().lower()
        tgt = (target_name or "").strip().lower()
        if tgt != self.door_name:
            return None

        # Simple verbs
        if vb in {"look", "examine", "inspect"}:
            return self.door.description

        if vb in {"open", "enter"}:
            if self.target_room.is_locked:
                return "It's locked."
            else:
                return f"The {self.door_name} is already open."

        if vb != "use":
            # Let default RoomObject interaction handle unknown verbs
            return None

        # From here, it's a 'use [item] on door' interaction
        if item is None:
            return f"You try to use your hands on the {self.door_name}, but that doesn't help."

        # If already unlocked, just give flavor
        if not self.target_room.is_locked:
            return f"You push the {self.door_name}; it's already unlocked and open."

        iname = item.name.lower()

        # Key-based unlocking
        if self.key_name and iname == self.key_name:
            self._unlock_via_event_or_direct()
            return (
                f"You unlock the {self.door_name} with the {item.name}. It clicks open."
            )

        # Bash-with-weapon option
        if self.allow_bash and hasattr(item, "has_tag") and item.has_tag("weapon"):
            self._unlock_via_event_or_direct()
            return (
                f"You use your {item.name} to bash the {self.door_name} open! "
                f"It swings wide with a heavy crash."
            )

        # Otherwise, no special effect
        return None

    def handle_help(self, user: "RpgHero"):
        key_hint = f" with the '{self.key_name}'" if self.key_name else ""
        bash_hint = " or bash it with a weapon" if self.allow_bash else ""
        event_hint = (
            " (it may also unlock after solving a puzzle)" if self.unlock_event else ""
        )
        return (
            f"- {self.door_name.title()}: Use a key{key_hint}{bash_hint}.{event_hint}\n"
            f"  Try: look {self.door_name}, open {self.door_name}, use <item> on {self.door_name}"
        )

    def _unlock_via_event_or_direct(self):
        if self.unlock_event:
            try:
                Events.trigger_event(self.unlock_event)
            except EventNotFoundError:
                # Fall back to direct unlock if event isn't registered for some reason
                self.target_room.unlock()
                self._on_unlocked()
        else:
            self.target_room.unlock()
            self._on_unlocked()
