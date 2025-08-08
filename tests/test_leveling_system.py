import pytest

from character.hero import RpgHero
from game.underlings.leveling_system import LevelingSystem
from game.underlings.events import Events


def setup_module(module):
    # Ensure events are cleared before tests in this module
    Events.clear_all_events()


def test_level_up_via_event_handler_single_level():
    # Arrange: hero at level 1
    hero = RpgHero("Tester", 1)
    ls = LevelingSystem()
    ls.setup_events()

    base_next = hero.xp_to_next_level
    # Act: give exactly enough XP to level once
    hero.add_xp(base_next)

    # Assert: level increased, xp reset to 0, thresholds and stats updated
    assert hero.level == 2
    assert hero.xp == 0
    assert hero.xp_to_next_level == LevelingSystem.calculate_xp_to_next_level(hero.level)
    assert hero.max_mana == hero.BASE_MANA + (hero.level - 1) * hero.MANA_PER_LEVEL
    assert hero.max_health == hero.BASE_HEALTH + (hero.level - 1) * hero.HEALTH_PER_LEVEL


def test_level_up_via_event_handler_multiple_levels():
    # Arrange
    Events.clear_all_events()
    hero = RpgHero("Tester", 1)
    ls = LevelingSystem()
    ls.setup_events()

    # Act: level up twice via two separate XP gains (due to XP capping at threshold)
    first = hero.xp_to_next_level
    hero.add_xp(first)
    second = hero.xp_to_next_level
    hero.add_xp(second)

    # Assert: at level 3, XP should be reset to 0 due to capping behavior
    assert hero.level == 3
    assert hero.xp == 0
    assert hero.xp_to_next_level == LevelingSystem.calculate_xp_to_next_level(hero.level)
    # stats reflect level 3
    assert hero.max_mana == hero.BASE_MANA + (hero.level - 1) * hero.MANA_PER_LEVEL
    assert hero.max_health == hero.BASE_HEALTH + (hero.level - 1) * hero.HEALTH_PER_LEVEL
