import enum

class Mana:
    def __init__(self, mana: int):
        self._mana = mana

    def consume(self, amount: int):
        """Consumes a specified amount of mana."""
        if amount < 0:
            raise ValueError("Mana consumption cannot be negative.")
        self.mana -= amount # Use the setter to ensure validation

    @property
    def mana(self) -> int:
        return self._mana

    @mana.setter
    def mana(self, mana: int):
        if mana < 0:
            self._mana = 0 # Direct assignment to avoid recursion
            # You might want to log a warning here if mana goes below zero
        else:
            self._mana = mana


class Health:
    def __init__(self, health: int):
        self._health = health

    def take_damage(self, damage: int):
        """Reduces health by the specified damage amount."""
        if damage < 0:
            raise ValueError("Damage cannot be negative.")
        self.health -= damage # Use the setter to ensure validation

    def heal(self, amount: int):
        """Increases health by the specified amount."""
        if amount < 0:
            raise ValueError("Healing amount cannot be negative.")
        self.health += amount # Use the setter to ensure validation

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, health: int):
        if health < 0:
            self._health = 0 # Direct assignment to avoid recursion
        else:
            self._health = health


class HoldComponent:
    def __init__(self):
        self._components = {}

    def add_component(self, name: str, component):
        """Adds a component to the holder by name."""
        if not isinstance(name, str) or not name.strip():
            raise TypeError("Component name must be a non-empty string.")
        if name in self._components:
            raise ValueError(f"Component '{name}' is already added.")
        self._components[name] = component

    def get_component(self, name: str):
        """Retrieves a component by name."""
        if name not in self._components:
            raise KeyError(f"Component '{name}' not found.")
        return self._components[name]

    def remove_component(self, name: str):
        """Removes a component by name."""
        if name not in self._components:
            raise KeyError(f"Component '{name}' not found.")
        del self._components[name]

    def all_components(self):
        """Returns all stored components."""
        return self._components.values()

    def has_component(self, name: str) -> bool:
        """Checks if a component exists."""
        return name in self._components

    def __getitem__(self, name: str):
        """Enables dictionary-like access for components."""
        return self.get_component(name)

    def __repr__(self):
        """Returns readable class representation for debugging."""
        components = ', '.join(self._components.keys())
        return f"<HoldComponent with: {components}>"


class Effect(enum.Enum):
    HEAL = 1
    DAMAGE = 2
    NONE = 3

