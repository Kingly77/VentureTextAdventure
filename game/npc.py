from dataclasses import dataclass


@dataclass(frozen=True)
class NPC:
    """
    A simple non-player character placeholder used for room descriptions.
    This is not responsible for dialogue or interactions, just visibility.
    """
    name: str
    short_description: str

    def key(self) -> str:
        """Lowercased key for storage in dicts."""
        return self.name.lower()
