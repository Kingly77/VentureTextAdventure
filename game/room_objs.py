from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class RoomObject:
    """Represents a simple object within a room (e.g., a door, a chest, a lever).

    Note: RoomObjects no longer handle interactions directly. All interactions are
    processed by Room effects (RoomDiscEffect implementations).
    """

    name: str
    description: str
    tags: set[str] = field(default_factory=set)
    is_locked: bool = False  # Example property for a door can be customized

    def __post_init__(self):
        # Normalize name and ensure tags is a set copy
        self.name = (self.name or "").lower()
        if not isinstance(self.tags, set):
            self.tags = set(self.tags or [])
        else:
            self.tags = set(self.tags)  # copy to avoid aliasing

    # ---- simple convenience constructors that keep previous API semantics ----
    def with_tagset(self, tagset: set[str]):
        """Returns a copy of this object with a different tagset."""
        return RoomObject(self.name, self.description, set(tagset))

    def with_added_tags(self, *tags):
        new_tags = set(self.tags)
        new_tags.update(tags)
        return RoomObject(self.name, self.description, new_tags)

    def change_description(self, new_description: str):
        """Changes the description of this object."""
        self.description = new_description

    def add_tag(self, tag: str):
        """Adds a tag to this object."""
        self.tags.add(tag)

    def remove_tag(self, tag: str):
        """Removes a tag from this object."""
        if tag in self.tags:
            self.tags.remove(tag)

    def has_tag(self, tag: str):
        """Checks if this object has a specific tag."""
        return tag in self.tags
