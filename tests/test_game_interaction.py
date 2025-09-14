import pytest

from character.hero import RpgHero
from game.items import Item
from game.room import Room
from game.room_objs import RoomObject
from game.effects.item_effects.item_effects import Effect
from interfaces.room_effect_base import RoomDiscEffect


@pytest.fixture
def test_hero():
    """Fixture that creates a test hero at level 1."""
    hero = RpgHero("Test Hero", 1)
    hero.gold = 50
    return hero


@pytest.fixture
def test_items():
    """Fixture that creates test items for interaction testing."""
    return {
        "key": Item("key", 5, True, tags=["key"]),
        "torch": Item("torch", 3, True, tags=["light-source"]),
        "sword": Item(
            "sword",
            25,
            True,
            is_equipment=True,
            effect=Effect.DAMAGE,
            effect_value=15,
            tags=["weapon"],
        ),
        "water": Item("water flask", 2, True, tags=["liquid"]),
        "matches": Item("matches", 1, True, tags=["fire-starter"]),
    }


@pytest.fixture
def test_room_objects():
    """Fixture that creates room objects (no direct interactions)."""

    # Create a locked chest
    chest = RoomObject(
        "chest", "A locked wooden chest with gold trim.", tags=["container", "locked"]
    )

    # Create a torch holder
    torch_holder = RoomObject(
        "torch holder", "An empty metal bracket on the wall.", tags=["fixture"]
    )

    # Create a dried plant that can catch fire
    plant = RoomObject(
        "dried plant", "A withered plant that looks very dry.", tags=["flammable"]
    )

    return {"chest": chest, "torch_holder": torch_holder, "plant": plant}


class RoomInteractionEffectHelper(RoomDiscEffect):
    def get_modified_description(self, base_description: str) -> str:
        return base_description

    def handle_interaction(self, verb, target_name, val_hero, item, room):
        if not target_name:
            return None
        tgt = target_name.lower()
        vb = (verb or "").lower().strip()

        if vb == "examine" and tgt == "plant":
            return "You examine the plant, but it's too dry to interact with."

        # Chest interactions: use/open/unlock with a key
        if tgt == "chest" and vb in {"use", "open", "unlock"}:
            chest = room.objects.get("chest")
            if not chest:
                return None
            if not item or "key" not in (item.tags or set()):
                return "This chest requires a proper key to unlock."
            if chest.has_tag("locked"):
                chest.remove_tag("locked")
                chest.add_tag("unlocked")
                chest.change_description(
                    "An unlocked wooden chest with gold trim. It's open and ready for looting."
                )
                treasure = Item("gold coins", 50, False, quantity=20)
                room.add_item(treasure)
                return "You unlock the chest with the key! Inside you find a pile of gold coins."
            return "The chest is already unlocked."

        # Torch holder interactions: use/place/light with a light source
        if tgt == "torch holder" and vb in {"use", "place", "light"}:
            holder = room.objects.get("torch holder")
            if not holder:
                return None
            if not item or "light-source" not in (item.tags or set()):
                return "You need something that provides light."
            holder.change_description(
                "A metal bracket holding a lit torch, illuminating the area."
            )
            room.change_description(
                room.base_description + " The room is now well lit."
            )
            return (
                "You place the torch in the holder, brightening the room considerably."
            )

        # Dried plant interactions: use/burn/ignite/light with fire; use/water/splash/pour with liquid
        if tgt == "dried plant" and vb in {
            "use",
            "burn",
            "ignite",
            "light",
            "water",
            "splash",
            "pour",
        }:
            plant = room.objects.get("dried plant")
            if not plant:
                return None
            if not item:
                return "You need something to interact with the plant."
            if ("fire-starter" in (item.tags or set())) or (
                "light-source" in (item.tags or set())
            ):
                plant.change_description("A pile of ashes where a plant once stood.")
                plant.remove_tag("flammable")
                plant.add_tag("burnt")
                return "The dried plant catches fire immediately and burns to ashes!"
            elif "liquid" in (item.tags or set()):
                plant.change_description("A slightly damp withered plant.")
                return "You pour some liquid on the plant, making it damp."
            return "That doesn't seem to affect the plant."

        return None


@pytest.fixture
def interactive_room(test_room_objects):
    """Create a room with interactive objects."""
    room = Room("Test Chamber", "A stone chamber with various objects for testing.")

    # Add objects to the room
    for obj in test_room_objects.values():
        room.add_object(obj)

    # Add a room effect that handles interactions for multiple verbs
    room.add_effect(RoomInteractionEffectHelper(room))

    return room


@pytest.fixture
def game_setup_with_objects(test_hero, test_items, interactive_room):
    """Set up a game environment with a hero, items, and an interactive room."""
    # Add some items to hero's inventory
    test_hero.inventory.add_item(test_items["key"])
    test_hero.inventory.add_item(test_items["torch"])

    # Add some items to the room
    interactive_room.add_item(test_items["water"])
    interactive_room.add_item(test_items["matches"])

    return (test_hero, interactive_room)


def test_object_presence(game_setup_with_objects, test_room_objects):
    """Test that objects are properly added to the room."""
    _, room = game_setup_with_objects

    # Check that objects exist in the room
    assert "chest" in room.objects
    assert "torch holder" in room.objects
    assert "dried plant" in room.objects

    # Check object properties
    assert room.objects["chest"].has_tag("locked")
    assert room.objects["torch holder"].has_tag("fixture")
    assert room.objects["dried plant"].has_tag("flammable")


def test_item_interaction_with_object(game_setup_with_objects, test_items):
    """Test using an item on a room object."""
    hero, room = game_setup_with_objects

    # Use the key on the chest
    chest = room.objects["chest"]
    key = test_items["key"]

    # Initial state
    assert chest.has_tag("locked")

    # Interact with chest using key
    result = room.interact("use", "chest", hero, key, room)

    # Check the result
    assert "unlock the chest with the key" in result
    assert not chest.has_tag("locked")
    assert chest.has_tag("unlocked")

    # Check that a reward was added to the room
    assert "gold coins" in [item for item in room.inventory.items]


def test_object_state_changes(game_setup_with_objects, test_items):
    """Test that object states change appropriately after interactions."""
    hero, room = game_setup_with_objects

    # Initial state of torch holder
    torch_holder = room.objects["torch holder"]
    original_description = torch_holder.description

    # Use torch on the torch holder
    result = room.interact("use", "torch holder", hero, test_items["torch"], room)

    # Check results
    assert "place the torch in the holder" in result
    assert torch_holder.description != original_description
    assert "now well lit" in room.base_description


def test_multiple_interaction_options(game_setup_with_objects, test_items):
    """Test an object that reacts differently to different items."""
    hero, room = game_setup_with_objects

    plant = room.objects["dried plant"]
    original_description = plant.description

    # First, try water on the plant
    result = room.interact("water", "dried plant", hero, test_items["water"], room)
    assert "damp" in result
    assert "damp" in plant.description
    assert plant.has_tag("flammable")  # Still flammable

    # Then, try matches on the plant
    result = room.interact("burn", "dried plant", hero, test_items["matches"], room)
    assert "catches fire" in result
    assert "ashes" in plant.description
    assert not plant.has_tag("flammable")
    assert plant.has_tag("burnt")


def test_invalid_interactions(game_setup_with_objects, test_items):
    """Test using items that don't work with objects."""
    hero, room = game_setup_with_objects

    # Try to use sword on chest
    chest = room.objects["chest"]
    result = room.interact("use", "chest", hero, test_items["sword"], room)

    # Should get a message about needing a key
    assert "requires a proper key" in result
    assert chest.has_tag("locked")  # Still locked

    # Try an invalid verb
    result = room.interact("break", "chest", hero, test_items["sword"], room)
    assert "cannot break" in result


def test_object_tag_system(game_setup_with_objects):
    """Test the tag system for objects."""
    _, room = game_setup_with_objects

    chest = room.objects["chest"]

    # Test has_tag method
    assert chest.has_tag("locked")
    assert chest.has_tag("container")
    assert not chest.has_tag("open")

    # Test add_tag method
    chest.add_tag("valuable")
    assert chest.has_tag("valuable")

    # Test remove_tag method
    chest.remove_tag("locked")
    assert not chest.has_tag("locked")
