from character.hero import RpgHero
from game.underlings.events import Events

class LevelingSystem:
    def __init__(self):
        pass
    
    def level_up(self, player: RpgHero, amount: int):
        """Handles leveling up the player."""
        pass


    def setup_events(self):
        Events.add_event("xp_gained", self.level_up)
