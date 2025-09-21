from character.hero import RpgHero
from game.room import Room
from interfaces.interface import Combatant
from interfaces.room_effect_base import RoomDiscEffect


class TrapEffect(RoomDiscEffect):
    """
    A specific RoomDiscEffect that represents a trap in the room.
    The trap gives the player a chance to notice and disarm it before it triggers.
    """

    def __init__(self, room: Room, damage: int, trap_message: str):
        super().__init__(room)
        self.damage = max(0, damage)
        self.trap_message = trap_message
        self.triggered = False  # True once the trap has gone off
        self.detected = False  # True once the player has noticed the trap
        self.disarmed = (
            self.damage == 0
        )  # True if damage is zero or explicitly disarmed

    def handle_enter(self, val_hero: RpgHero):
        # If already safe, do nothing special
        if self.disarmed:
            return False

        # First time entering: let the player notice the trap
        if not self.detected and not self.triggered:
            self.detected = True
            return f"{self.trap_message} The trap is armed. You notice it and have a chance to disarm it."

        # Second time (or re-entry) while still not disarmed: it triggers
        if not self.triggered:
            self.triggered = True
            val_hero.take_damage(self.damage)
            return f"{self.trap_message} You trigger the trap and take {self.damage} damage."

        # Already triggered and not disarmed: nothing else to do on further enters
        return False

    def handle_interaction(self, verb: str, target_name: str, val_hero: Combatant, item, room: Room):
        v = (verb or "").strip().lower()
        tgt = (target_name or "").strip().lower()

        # Allow disarming via a generic action
        if v == "disarm":
            if self.disarmed:
                return "The trap has already been disarmed."
            if self.triggered:
                return "Too late—the trap has already been triggered."
            self.disarmed = True
            self.damage = 0
            self.detected = True
            return "You carefully disarm the trap. It is now safe."

        # Or via using a specific tool
        if v == "use" and (tgt == "trap disarm kit" or (item and getattr(item, "name", "").lower() == "trap disarm kit")):
            if self.disarmed:
                return "There is no active trap to disarm."
            if self.triggered:
                return "Too late—the trap has already gone off."
            self.disarmed = True
            self.damage = 0
            self.detected = True
            return "You use the trap disarm kit to render the trap harmless."

        return None

    def handle_item_use(self, verb: str, item_name: str, user: Combatant) -> bool:
        v = (verb or "").strip().lower()
        it = (item_name or "").strip().lower()
        # Only support using a specific disarm tool within use_item_in_room flow
        if v == "use" and it == "trap disarm kit":
            if not self.disarmed and not self.triggered:
                # Disarm the trap
                self.disarmed = True
                self.damage = 0
                return True
        return False

    def get_modified_description(self, base_description: str) -> str:
        # Return only changes unless we must replace the whole description
        if self.disarmed:
            return None
        if self.detected and not self.triggered:
            return "You see a trap mechanism here."
        # If not detected yet, keep things vague
        return "There seems to be something dangerous here."
