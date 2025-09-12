import functools
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from interfaces.interface import Combatant
    from character.hero import RpgHero
    from game.items import Item

from interfaces.room_effect_base import RoomDiscEffect
from game.room import Room
from game.room_objs import RoomObject
from game.underlings.events import EventNotFoundError, Events


class DoorEffectExpanded(RoomDiscEffect):

    def get_modified_description(self, base_description: str) -> str:
        return base_description

    def __init__(self, room, foyer: Room):
        super().__init__(room)
        self.foyer = foyer

        self.door = RoomObject(
            "door",
            "A sturdy wooden door with a heavy lock. It appears to be the entrance to the Foyer.",
        )
        room.add_object(self.door)

        Events.add_event(
            "unlock_foyer",
            functools.partial(
                self.door.change_description,
                "The door is wide open, It appears to be the entrance to the Foyer.",
            ),
            True,
        )

        def knock_door(user: "RpgHero", item: "Item", r: "Room", *args) -> str:
            if item.name == "stick":
                return "Knock"
            return ""

        self.door.add_interaction("use", knock_door)

    def handle_item_use(self, verb: str, item_name: str, user: "Combatant") -> bool:
        # This effect only responds to object-targeted 'use' via handle_interaction
        # Return False for room-wide item use
        return False

    def handle_interaction(
        self,
        verb: str,
        target_name: Optional[str],
        val_hero: "RpgHero",
        item: Optional["Item"],
        room: "Room",
    ) -> Optional[str]:
        if verb != "use" or target_name != "door":
            return None
        if item is None or not item.has_tag("weapon"):
            return None

        if self.foyer.is_locked:
            try:
                Events.trigger_event("unlock_foyer")
                return (
                    f"You use your {item.name} to bash the door open! "
                    f"The door swings wide and a giant bashing sound is heard."
                )

            except EventNotFoundError as e:
                return f"Error: {str(e)}"

        return None
