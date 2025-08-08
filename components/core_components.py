import enum


class Mana:
    def __init__(self, mana: int):
        self._mana = mana
        self._max_mana = mana

    def consume(self, amount: int):
        """Consumes a specified amount of mana."""
        if amount < 0:
            raise ValueError("Mana consumption cannot be negative.")
        self.mana -= amount  # Use the setter to ensure validation

    @property
    def mana(self) -> int:
        return self._mana

    @mana.setter
    def mana(self, mana: int):
        if mana < 0:
            self._mana = 0  # Direct assignment to avoid recursion
            # You might want to log a warning here if mana goes below zero
        elif mana > self._max_mana:
            self._mana = self._max_mana  # Cap mana at max_mana
        else:
            self._mana = mana

    @property
    def max_mana(self) -> int:
        return self._max_mana

    @max_mana.setter
    def max_mana(self, value: int):
        if value <= 0:
            raise ValueError("Maximum mana must be positive.")
        self._max_mana = value
        # If current mana exceeds new max, adjust it
        if self._mana > value:
            self._mana = value


class Health:
    def __init__(self, health: int):
        self._health = health
        self._max_health = health

    def take_damage(self, damage: int):
        """Reduces health by the specified damage amount."""
        if damage < 0:
            raise ValueError("Damage cannot be negative.")
        self.health -= damage  # Use the setter to ensure validation

    def heal(self, amount: int):
        """Increases health by the specified amount, up to max_health."""
        if amount < 0:
            raise ValueError("Healing amount cannot be negative.")
        self.health += (
            amount  # Use the setter to ensure validation (which will cap at max_health)
        )

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, health: int):
        if health < 0:
            self._health = 0  # Direct assignment to avoid recursion
        elif health > self._max_health:
            self._health = self._max_health  # Cap health at max_health
        else:
            self._health = health

    @property
    def max_health(self) -> int:
        return self._max_health

    @max_health.setter
    def max_health(self, value: int):
        if value <= 0:
            raise ValueError("Maximum health must be positive.")
        self._max_health = value
        # If current health exceeds new max, adjust it
        if self._health > value:
            self._health = value


class Exp:
    def __init__(self, exp: int):
        self._exp = exp
        self._max_exp = exp
        self._level = 1

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
        components = ", ".join(self._components.keys())
        return f"<HoldComponent with: {components}>"


class Effect(enum.Enum):
    HEAL = 1
    DAMAGE = 2
    NONE = 3
