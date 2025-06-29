from typing import Dict, Callable, runtime_checkable, Protocol

class RoomObject:
    """Represents an interactive object within a room (e.g., a door, a chest, a lever)."""
    def __init__(self, name: str, description: str , tags = None):
        self.name = name.lower()
        self.description = description
        # A dictionary where keys are item names, and values are functions
        # to execute when that item is used on this object.
        self.tags:set =  set(tags or [])
        self.interaction_events: Dict[str, Callable[['RpgHero',...], str]] = {}
        self.is_locked: bool = False # Example property for a door can be customized



    @runtime_checkable
    class InteractionEvent(Protocol):
        def __call__(self, item_name: str, user: 'RpgHero', *args) -> str: ...

    def change_description(self, new_description: str):
        """Changes the description of this object."""
        self.description = new_description

    def add_tag(self, tag: str):
        """Adds a tag to this object."""
        self.tags.add(tag)

    def remove_tag(self, tag: str):
        """Removes a tag from this object."""
        self.tags.remove(tag)

    def has_tag(self, tag: str):
        """Checks if this object has a specific tag."""
        return tag in self.tags

    def try_interact(self,verb, user, item = None,room = None):
        """
        Tries to interact with this object.
        Returns a message about the outcome.
        """
        if verb in self.interaction_events:
            return self.interaction_events[verb](user,item,room)
        else:
            return f"You cannot {verb} the {self.name}."

    def add_interaction(self, verb: str, event_function:InteractionEvent):
        """
        Adds an event that triggers when a specific item is used on this object.
        The event_function should take the RpgHero as an argument and return a message.
        """
        self.interaction_events[verb.lower()] = event_function

    def use_item_on_object(self, item_name: str, user: 'RpgHero', *args) -> str:
        """
        Attempts to use an item on this specific room object.
        Returns a message about the outcome.
        """
        item_name_lower = item_name.lower()
        if item_name_lower in self.interaction_events:
            return self.interaction_events[item_name_lower](user,*args)
        return f"Using {item_name} has no effect on the {self.name}."

