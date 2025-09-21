from __future__ import annotations
import random
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from interfaces.interface import Combatant
    from character.hero import RpgHero
    from game.items import Item
    from game.room import Room

from interfaces.room_effect_base import RoomDiscEffect
from game.underlings.events import Events


class SmokeEffect(RoomDiscEffect):
    """
    A room effect that creates thick smoke, reducing visibility and potentially causing
    coughing or other effects. The smoke can be cleared by certain actions or items.
    """

    def __init__(self, room: "Room", intensity: int = 5, persistent: bool = True):
        """
        Initialize the smoke effect.
        
        Args:
            room: The room this effect is applied to
            intensity: Smoke intensity level (1-10, higher = thicker smoke)
            persistent: Whether the smoke persists or can be cleared
        """
        super().__init__(room)
        self.intensity = max(1, min(10, intensity))  # Clamp between 1-10
        self.persistent = persistent
        self.is_cleared = False
        
        # Register event for automatic smoke level reduction
        self.event_name = f"smoke_reduce_{id(self)}"
        Events.add_event(self.event_name, self._handle_smoke_reduction)

    def get_modified_description(self, base_description: str) -> str:
        """
        Modifies the room description to include smoke effects.
        """
        if self.is_cleared:
            return base_description
        
        smoke_descriptions = {
            1: "A thin wisp of smoke drifts through the air.",
            2: "Light smoke hangs in the air, slightly obscuring your vision.",
            3: "Moderate smoke fills the area, making it harder to see clearly.",
            4: "Thick smoke clouds the room, significantly reducing visibility.",
            5: "Dense smoke fills the space, making it difficult to see more than a few feet ahead.",
            6: "Heavy smoke obscures most of the room, visibility is very poor.",
            7: "Thick, choking smoke makes it nearly impossible to see clearly.",
            8: "Dense, acrid smoke fills the air, severely limiting visibility.",
            9: "Overwhelming smoke makes it almost impossible to see or breathe clearly.",
            10: "The room is completely filled with thick, suffocating smoke."
        }
        
        smoke_desc = smoke_descriptions.get(self.intensity, smoke_descriptions[5])
        return f"{base_description}\n\n{smoke_desc}"

    def handle_enter(self, val_hero: "RpgHero"):
        """
        Called when a hero enters the smoky room.
        """
        if self.is_cleared:
            return False
            
        # Chance of coughing based on smoke intensity
        cough_chance = min(0.8, self.intensity * 0.1)
        if random.random() < cough_chance:
            cough_messages = [
                "You cough as the smoke irritates your throat.",
                "The thick smoke makes you cough and wheeze.",
                "You struggle to breathe in the smoky air.",
                "The acrid smoke causes you to cough violently.",
                "You choke on the dense smoke filling the room."
            ]
            return random.choice(cough_messages)
        
        return False

    def handle_interaction(
        self,
        verb: str,
        target_name: Optional[str],
        val_hero: "Combatant",
        item: Optional["Item"],
        room: "Room",
    ) -> Optional[str]:
        """
        Handles interactions that might clear or affect the smoke.
        """
        if self.is_cleared:
            return None
            
        # Check for actions that might clear smoke
        if verb == "wave" and (target_name is None or "smoke" in (target_name or "").lower()):
            if self.persistent:
                return "You wave your hands, but the smoke is too thick and persistent to clear this way."
            else:
                self.is_cleared = True
                return "You wave your hands vigorously, and the smoke begins to dissipate, clearing the air."

        # Check for items that might clear smoke
        if verb == "use" and item is not None:
            if item.has_tag("fan") or item.has_tag("wind"):
                if self.persistent:
                    self.intensity = max(1, self.intensity - 2)
                    return f"You use the {item.name} to blow away some of the smoke. The air becomes slightly clearer."
                else:
                    self.is_cleared = True
                    return f"You use the {item.name} to clear the smoke from the room."
            
            elif item.has_tag("water") or item.has_tag("extinguisher"):
                if self.persistent:
                    self.intensity = max(1, self.intensity - 3)
                    return f"You use the {item.name} to dampen the smoke. The air becomes noticeably clearer."
                else:
                    self.is_cleared = True
                    return f"You use the {item.name} to extinguish the source of the smoke."

        return None

    def handle_item_use(self, verb: str, item_name: str, user: "Combatant") -> bool:
        """
        Handles item usage that might affect the smoke.
        """
        if self.is_cleared:
            return False
            
        # Check if the item being used can clear smoke
        if verb.lower() == "use":
            # This would need to check the actual item, but we can't access it here
            # The handle_interaction method above handles this better
            pass
            
        return False

    def reduce_intensity(self, amount: int = 1):
        """
        Reduces the smoke intensity by the specified amount.
        """
        self.intensity = max(1, self.intensity - amount)
        if self.intensity <= 1 and not self.persistent:
            self.is_cleared = True

    def _handle_smoke_reduction(self):
        """
        Event handler that reduces smoke intensity over time.
        Called automatically by the event system.
        """
        if self.is_cleared:
            return
            
        # Reduce intensity by 1 every time the event is triggered
        if self.intensity > 1:
            self.intensity -= 1
            print(f"The smoke begins to dissipate slightly. Intensity: {self.intensity}")
        else:
            # If intensity reaches 1 and not persistent, clear the smoke
            if not self.persistent:
                self.clear_smoke()
                print("The smoke has completely cleared from the room.")

    def trigger_smoke_reduction(self):
        """
        Triggers the smoke reduction event.
        This can be called manually or by external systems.
        """
        if not self.is_cleared:
            Events.trigger_event(self.event_name)

    def clear_smoke(self):
        """
        Immediately clears the smoke from the room.
        """
        self.is_cleared = True
        self.intensity = 0
        
        # Clean up the event handler
        try:
            Events.remove_event(self.event_name, self._handle_smoke_reduction)
        except Exception:
            # Event might already be removed, ignore errors
            pass
