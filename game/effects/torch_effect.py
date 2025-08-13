import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.items import Item
    from game.room import Room
    from character.hero import RpgHero
from game.effects.room_effects import RoomDiscEffect
from game.room_objs import RoomObject
from game.underlings.events import Events


class TorchEffect(RoomDiscEffect):

    def get_modified_description(self, base_description: str) -> str:
        return base_description

    def __init__(self, room: "Room"):
        super().__init__(room)
        self.forest_table = RoomObject(
            "table",
            "A massive stone table dominates the area, with a small wooden chair peculiarly placed on its surface. "
            "In the center of the table, a carefully constructed fire pit contains a neat pile of firewood, ready to be lit.",
        )
        room.add_object(self.forest_table)

    def handle_interaction(
        self,
        verb: str,
        target_name: Optional[str],
        val_hero: "RpgHero",
        item: Optional["Item"],
        room: "Room",
    ) -> Optional[str]:
        if verb != "use" or target_name != "table":
            return None

        if not item.has_tag("fire") and not self.forest_table.has_tag("lit"):
            print("You need a torch to properly light the table's fire pit.")
            return None

        self.forest_table.change_description(
            "A massive stone table dominates the area, with a small wooden chair on its surface. "
            "The fire pit in the center now blazes with dancing flames, casting flickering shadows across the stone."
        )
        try:
            Events.trigger_event("torch_on_table")
        except ValueError:
            logging.debug("Error: torch_on_table event not found.")
        self.forest_table.add_tag("lit")
        return (
            "You touch your torch to the prepared wood. The kindling catches immediately, "
            "and flames leap upward, illuminating the area with a warm, golden glow."
        )
