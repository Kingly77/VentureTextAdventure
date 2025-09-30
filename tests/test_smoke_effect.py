# tests/test_smoke_effect.py
import pytest
from unittest.mock import Mock, patch, call
import random

from character.hero import RpgHero
from game.rooms.effect_room import EffectRoom
from game.effects.smoke_effect import SmokeEffect
from game.items import Item
from game.underlings.events import Events


@pytest.fixture
def test_room():
    """Fixture that creates a test EffectRoom."""
    return EffectRoom(
        "Smoky Chamber",
        "A stone chamber with ancient markings.",
        exits={"north": "Next Room"},
    )


@pytest.fixture
def test_hero():
    """Fixture that creates a test hero at level 1."""
    hero = RpgHero("Test Hero", 1)
    hero.gold = 50
    return hero


@pytest.fixture
def mock_item():
    """Fixture that creates a mock item."""
    item = Mock(spec=Item)
    item.name = "Test Item"
    item.has_tag.return_value = False
    return item


@pytest.fixture
def fan_item():
    """Fixture that creates a mock fan item."""
    item = Mock(spec=Item)
    item.name = "Hand Fan"
    item.has_tag.side_effect = lambda tag: tag in ["fan", "wind"]
    return item


@pytest.fixture
def water_item():
    """Fixture that creates a mock water item."""
    item = Mock(spec=Item)
    item.name = "Water Bucket"
    item.has_tag.side_effect = lambda tag: tag in ["water", "extinguisher"]
    return item


class TestSmokeEffectInitialization:
    """Test smoke effect initialization and basic properties."""

    def test_smoke_effect_initialization_default(self, test_room):
        """Test SmokeEffect initializes with default parameters."""
        smoke = SmokeEffect(test_room)

        assert smoke.room == test_room
        assert smoke.intensity == 5  # default
        assert smoke.persistent is True  # default
        assert smoke.is_cleared is False
        assert hasattr(smoke, 'event_name')
        assert smoke.event_name.startswith('smoke_reduce_')

    def test_smoke_effect_initialization_custom(self, test_room):
        """Test SmokeEffect initializes with custom parameters."""
        smoke = SmokeEffect(test_room, intensity=8, persistent=False)

        assert smoke.intensity == 8
        assert smoke.persistent is False
        assert smoke.is_cleared is False

    def test_smoke_effect_intensity_clamping(self, test_room):
        """Test that intensity is clamped between 1-10."""
        smoke_low = SmokeEffect(test_room, intensity=-5)
        smoke_high = SmokeEffect(test_room, intensity=15)

        assert smoke_low.intensity == 1
        assert smoke_high.intensity == 10

    @patch('game.underlings.events.Events.add_event')
    def test_event_registration(self, mock_add_event, test_room):
        """Test that smoke effect registers event handler on initialization."""
        smoke = SmokeEffect(test_room)

        mock_add_event.assert_called_once_with(
            smoke.event_name,
            smoke._handle_smoke_reduction
        )


class TestSmokeEffectDescriptionModification:
    """Test smoke effect description modification functionality."""

    def test_get_modified_description_various_intensities(self, test_room):
        """Test description modification for different smoke intensities."""
        base_desc = "A simple stone chamber."

        # Test different intensities
        intensities_and_keywords = [
            (1, "thin wisp"),
            (3, "moderate smoke"),
            (5, "dense smoke"),
            (8, "dense, acrid smoke"),
            (10, "suffocating smoke"),
        ]

        for intensity, keyword in intensities_and_keywords:
            smoke = SmokeEffect(test_room, intensity=intensity)
            modified_desc = smoke.get_modified_description(base_desc)

            assert modified_desc is not None
            assert keyword.lower() in modified_desc.lower()

    def test_get_modified_description_cleared_smoke(self, test_room):
        """Test that cleared smoke returns None for description modification."""
        smoke = SmokeEffect(test_room)
        smoke.is_cleared = True

        modified_desc = smoke.get_modified_description("Base description")
        assert modified_desc is None

    def test_get_modified_description_invalid_intensity(self, test_room):
        """Test description for edge case intensities."""
        smoke = SmokeEffect(test_room)
        smoke.intensity = 99  # Invalid intensity

        modified_desc = smoke.get_modified_description("Base description")
        # Should fallback to intensity 5 description
        assert "dense smoke" in modified_desc.lower()


class TestSmokeEffectHeroEnter:
    """Test smoke effect behavior when hero enters room."""

    def test_handle_enter_cleared_smoke(self, test_room, test_hero):
        """Test that cleared smoke doesn't affect hero entrance."""
        smoke = SmokeEffect(test_room)
        smoke.is_cleared = True

        result = smoke.handle_enter(test_hero)
        assert result is False

    @patch('random.random')
    def test_handle_enter_no_coughing(self, mock_random, test_room, test_hero):
        """Test hero entering without coughing effect."""
        mock_random.return_value = 0.9  # Higher than cough chance
        smoke = SmokeEffect(test_room, intensity=1)  # Low intensity = low cough chance

        result = smoke.handle_enter(test_hero)
        assert result is False

    @patch('random.random')
    @patch('random.choice')
    def test_handle_enter_with_coughing(self, mock_choice, mock_random, test_room, test_hero):
        """Test hero entering with coughing effect."""
        mock_random.return_value = 0.1  # Lower than cough chance
        mock_choice.return_value = "You cough as the smoke irritates your throat."

        smoke = SmokeEffect(test_room, intensity=10)  # High intensity = high cough chance

        result = smoke.handle_enter(test_hero)
        assert result == "You cough as the smoke irritates your throat."
        mock_choice.assert_called_once()

    def test_handle_enter_cough_chance_scaling(self, test_room, test_hero):
        """Test that cough chance scales with intensity."""
        # Test with different intensities and verify probability ranges
        with patch('random.random') as mock_random:
            # Low intensity
            mock_random.return_value = 0.05  # 5%
            smoke_low = SmokeEffect(test_room, intensity=1)
            # Cough chance = min(0.8, 1 * 0.1) = 0.1 (10%)
            # 5% < 10%, should cough

            # High intensity
            smoke_high = SmokeEffect(test_room, intensity=10)
            # Cough chance = min(0.8, 10 * 0.1) = 0.8 (80%)
            # 5% < 80%, should cough

            # Both should trigger coughing with 5% roll
            with patch('random.choice', return_value="cough"):
                assert smoke_low.handle_enter(test_hero) == "cough"
                assert smoke_high.handle_enter(test_hero) == "cough"


class TestSmokeEffectInteractions:
    """Test smoke effect interaction handling."""

    def test_handle_interaction_cleared_smoke(self, test_room, test_hero):
        """Test interactions with cleared smoke return None."""
        smoke = SmokeEffect(test_room)
        smoke.is_cleared = True

        result = smoke.handle_interaction("wave", None, test_hero, None, test_room)
        assert result is None

    def test_handle_interaction_wave_persistent_smoke(self, test_room, test_hero):
        """Test waving at persistent smoke."""
        smoke = SmokeEffect(test_room, persistent=True)

        result = smoke.handle_interaction("wave", None, test_hero, None, test_room)
        assert result is not None
        assert "too thick and persistent" in result
        assert not smoke.is_cleared

    def test_handle_interaction_wave_non_persistent_smoke(self, test_room, test_hero):
        """Test waving clears non-persistent smoke."""
        smoke = SmokeEffect(test_room, persistent=False)

        result = smoke.handle_interaction("wave", None, test_hero, None, test_room)
        assert result is not None
        assert "smoke begins to dissipate" in result
        assert smoke.is_cleared

    def test_handle_interaction_wave_with_smoke_target(self, test_room, test_hero):
        """Test waving specifically at smoke."""
        smoke = SmokeEffect(test_room, persistent=False)

        result = smoke.handle_interaction("wave", "smoke", test_hero, None, test_room)
        assert result is not None
        assert "smoke begins to dissipate" in result
        assert smoke.is_cleared

    def test_handle_interaction_use_fan_persistent(self, test_room, test_hero, fan_item):
        """Test using fan item on persistent smoke."""
        smoke = SmokeEffect(test_room, intensity=5, persistent=True)
        original_intensity = smoke.intensity

        result = smoke.handle_interaction("use", None, test_hero, fan_item, test_room)
        assert result is not None
        assert fan_item.name in result
        assert "blow away some of the smoke" in result
        assert smoke.intensity == max(1, original_intensity - 2)
        assert not smoke.is_cleared

    def test_handle_interaction_use_fan_non_persistent(self, test_room, test_hero, fan_item):
        """Test using fan item on non-persistent smoke."""
        smoke = SmokeEffect(test_room, persistent=False)

        result = smoke.handle_interaction("use", None, test_hero, fan_item, test_room)
        assert result is not None
        assert fan_item.name in result
        assert "clear the smoke" in result
        assert smoke.is_cleared

    def test_handle_interaction_use_water_persistent(self, test_room, test_hero, water_item):
        """Test using water item on persistent smoke."""
        smoke = SmokeEffect(test_room, intensity=6, persistent=True)
        original_intensity = smoke.intensity

        result = smoke.handle_interaction("use", None, test_hero, water_item, test_room)
        assert result is not None
        assert water_item.name in result
        assert "dampen the smoke" in result
        assert smoke.intensity == max(1, original_intensity - 3)
        assert not smoke.is_cleared

    def test_handle_interaction_use_water_non_persistent(self, test_room, test_hero, water_item):
        """Test using water item on non-persistent smoke."""
        smoke = SmokeEffect(test_room, persistent=False)

        result = smoke.handle_interaction("use", None, test_hero, water_item, test_room)
        assert result is not None
        assert water_item.name in result
        assert "extinguish the source" in result
        assert smoke.is_cleared

    def test_handle_interaction_use_regular_item(self, test_room, test_hero, mock_item):
        """Test using regular item has no effect."""
        smoke = SmokeEffect(test_room)

        result = smoke.handle_interaction("use", None, test_hero, mock_item, test_room)
        assert result is None
        assert not smoke.is_cleared

    def test_handle_interaction_other_verbs(self, test_room, test_hero):
        """Test that other verbs return None."""
        smoke = SmokeEffect(test_room)

        result = smoke.handle_interaction("examine", "smoke", test_hero, None, test_room)
        assert result is None


class TestSmokeEffectIntensityManagement:
    """Test smoke effect intensity reduction and management."""

    def test_reduce_intensity_basic(self, test_room):
        """Test basic intensity reduction."""
        smoke = SmokeEffect(test_room, intensity=5)

        smoke.reduce_intensity(2)
        assert smoke.intensity == 3
        assert not smoke.is_cleared

    def test_reduce_intensity_minimum_clamp(self, test_room):
        """Test intensity cannot go below 1."""
        smoke = SmokeEffect(test_room, intensity=2)

        smoke.reduce_intensity(5)
        assert smoke.intensity == 1
        assert not smoke.is_cleared

    def test_reduce_intensity_non_persistent_clearing(self, test_room):
        """Test that non-persistent smoke clears when intensity reaches 1."""
        smoke = SmokeEffect(test_room, intensity=2, persistent=False)

        smoke.reduce_intensity(1)  # Intensity becomes 1
        assert smoke.intensity == 1
        assert smoke.is_cleared

    def test_reduce_intensity_persistent_no_clearing(self, test_room):
        """Test that persistent smoke doesn't clear when intensity reaches 1."""
        smoke = SmokeEffect(test_room, intensity=2, persistent=True)

        smoke.reduce_intensity(1)  # Intensity becomes 1
        assert smoke.intensity == 1
        assert not smoke.is_cleared

    def test_clear_smoke_immediate(self, test_room):
        """Test immediate smoke clearing."""
        smoke = SmokeEffect(test_room, intensity=5)

        with patch.object(Events, 'remove_event') as mock_remove:
            smoke.clear_smoke()

            assert smoke.is_cleared
            assert smoke.intensity == 0
            mock_remove.assert_called_once_with(
                smoke.event_name,
                smoke._handle_smoke_reduction
            )

    def test_clear_smoke_event_removal_error(self, test_room):
        """Test smoke clearing handles event removal errors gracefully."""
        smoke = SmokeEffect(test_room)

        with patch.object(Events, 'remove_event', side_effect=Exception("Event error")):
            # Should not raise exception
            smoke.clear_smoke()
            assert smoke.is_cleared
            assert smoke.intensity == 0


class TestSmokeEffectEventSystem:
    """Test smoke effect integration with event system."""

    def test_handle_smoke_reduction_cleared(self, test_room):
        """Test smoke reduction handler when smoke is already cleared."""
        smoke = SmokeEffect(test_room)
        smoke.is_cleared = True
        original_intensity = smoke.intensity

        with patch('builtins.print') as mock_print:
            smoke._handle_smoke_reduction()

            assert smoke.intensity == original_intensity  # No change
            mock_print.assert_not_called()

    def test_handle_smoke_reduction_intensity_decrease(self, test_room):
        """Test smoke reduction decreases intensity."""
        smoke = SmokeEffect(test_room, intensity=5)

        with patch('builtins.print') as mock_print:
            smoke._handle_smoke_reduction()

            assert smoke.intensity == 4
            assert not smoke.is_cleared
            mock_print.assert_called_once_with("The smoke begins to dissipate slightly. Intensity: 4")

    def test_handle_smoke_reduction_persistent_minimum(self, test_room):
        """Test smoke reduction with persistent smoke at minimum intensity."""
        smoke = SmokeEffect(test_room, intensity=1, persistent=True)

        with patch('builtins.print') as mock_print:
            smoke._handle_smoke_reduction()

            assert smoke.intensity == 1  # Should stay at 1
            assert not smoke.is_cleared  # Persistent smoke doesn't clear
            mock_print.assert_not_called()

    def test_handle_smoke_reduction_non_persistent_clearing(self, test_room):
        """Test smoke reduction clears non-persistent smoke at intensity 1."""
        smoke = SmokeEffect(test_room, intensity=1, persistent=False)

        with patch('builtins.print') as mock_print, \
             patch.object(smoke, 'clear_smoke') as mock_clear:

            smoke._handle_smoke_reduction()

            mock_clear.assert_called_once()
            mock_print.assert_called_with("The smoke has completely cleared from the room.")

    @patch.object(Events, 'trigger_event')
    def test_trigger_smoke_reduction_active(self, mock_trigger, test_room):
        """Test manually triggering smoke reduction when active."""
        smoke = SmokeEffect(test_room)

        smoke.trigger_smoke_reduction()

        mock_trigger.assert_called_once_with(smoke.event_name)

    @patch.object(Events, 'trigger_event')
    def test_trigger_smoke_reduction_cleared(self, mock_trigger, test_room):
        """Test manually triggering smoke reduction when cleared."""
        smoke = SmokeEffect(test_room)
        smoke.is_cleared = True

        smoke.trigger_smoke_reduction()

        mock_trigger.assert_not_called()


class TestSmokeEffectItemUseHandler:
    """Test smoke effect item use handler."""

    def test_handle_item_use_cleared_smoke(self, test_room, test_hero):
        """Test handle_item_use returns False for cleared smoke."""
        smoke = SmokeEffect(test_room)
        smoke.is_cleared = True

        result = smoke.handle_item_use("use", "test_item", test_hero)
        assert result is False

    def test_handle_item_use_active_smoke(self, test_room, test_hero):
        """Test handle_item_use returns False for active smoke (uses handle_interaction)."""
        smoke = SmokeEffect(test_room)

        result = smoke.handle_item_use("use", "test_item", test_hero)
        assert result is False

    def test_handle_item_use_non_use_verb(self, test_room, test_hero):
        """Test handle_item_use with non-use verbs."""
        smoke = SmokeEffect(test_room)

        result = smoke.handle_item_use("examine", "test_item", test_hero)
        assert result is False


class TestSmokeEffectIntegration:
    """Integration tests for smoke effect with room system."""

    def test_smoke_effect_in_room_description(self, test_room):
        """Test smoke effect integration with room description system."""
        smoke = SmokeEffect(test_room, intensity=3)
        test_room.add_effect(smoke)

        full_description = test_room.get_description()
        assert "moderate smoke" in full_description.lower()

    def test_smoke_effect_room_interaction_flow(self, test_room, test_hero, fan_item):
        """Test complete interaction flow with room system."""
        smoke = SmokeEffect(test_room, intensity=4, persistent=False)
        test_room.add_effect(smoke)

        # Hero enters room - might cough
        with patch('random.random', return_value=0.1), \
             patch('random.choice', return_value="You cough."):
            enter_result = smoke.handle_enter(test_hero)
            assert enter_result == "You cough."

        # Use fan to clear smoke
        interaction_result = smoke.handle_interaction("use", None, test_hero, fan_item, test_room)
        assert "clear the smoke" in interaction_result
        assert smoke.is_cleared

        # Description should no longer include smoke
        modified_desc = smoke.get_modified_description("Base description")
        assert modified_desc is None

    def test_multiple_smoke_effects_different_intensities(self, test_room):
        """Test multiple smoke effects with different intensities."""
        smoke1 = SmokeEffect(test_room, intensity=2)
        smoke2 = SmokeEffect(test_room, intensity=8)

        desc1 = smoke1.get_modified_description("Base")
        desc2 = smoke2.get_modified_description("Base")

        assert "light smoke" in desc1.lower()
        assert "dense" in desc2.lower()
        assert desc1 != desc2