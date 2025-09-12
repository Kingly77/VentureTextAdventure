from game.display import display
from interfaces.room_effect_base import RoomDiscEffect
from game.underlings.events import Events


class EntryEffect(RoomDiscEffect):

    def get_modified_description(self, base_description: str) -> str:
        return base_description

    def __init__(self, room, first_time_message: str = None):
        super().__init__(room)
        self.first_time_message = first_time_message
        self.has_been_displayed = False
        Events.add_event("location_entered", self._sub_location_entered)

    def _sub_location_entered(self, val_hero: "RpgHero", room: "Room"):
        pass

    def handle_enter(self, val_hero: "RpgHero"):
        if self.first_time_message and not self.has_been_displayed:
            display.write(self.first_time_message)
            self.has_been_displayed = True
            return True
        return False
