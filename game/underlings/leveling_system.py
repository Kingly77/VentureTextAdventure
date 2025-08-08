from character.hero import RpgHero
from game.underlings.events import Events

class LevelingSystem:
    BASE_XP_TO_NEXT_LEVEL = 100

    def __init__(self):
        pass
    
    @staticmethod
    def calculate_xp_to_next_level(level: int) -> int:
        return LevelingSystem.BASE_XP_TO_NEXT_LEVEL + (level * 50)

    def level_up(self, player: RpgHero, amount: int):
        """Handles leveling up the player when enough XP is accumulated.
        This function is registered on the 'xp_gained' event and expects:
        - player: the RpgHero gaining XP
        - amount: the XP gained (not used directly here aside from semantics)
        """
        # Continue leveling while player has enough XP
        leveled = False
        while player.xp >= player.xp_to_next_level:
            # Deduct XP for this level and increase level
            player.xp -= player.xp_to_next_level
            player.level += 1
            # Recalculate XP required for next level using the system
            player.xp_to_next_level = LevelingSystem.calculate_xp_to_next_level(player.level)
            # Update derived stats based on new level
            player.get_mana_component().max_mana = (
                player.BASE_MANA + (player.level - 1) * player.MANA_PER_LEVEL
            )
            player.get_health_component().max_health = (
                player.BASE_HEALTH + (player.level - 1) * player.HEALTH_PER_LEVEL
            )
            print(f"{player.name} leveled up to level {player.level}!")
            leveled = True
        return leveled


    def setup_events(self):
        # Register to listen for XP gains; when XP changes we evaluate level ups
        Events.add_event("xp_gained", self.level_up)
