import abc
import enum

# --- Abstract Base Classes ---

class CanCast(abc.ABC):
    @abc.abstractmethod
    def cast(self, target: 'Combatant'):
        """Abstract method for casting an ability or item on a target."""
        pass

class Combatant(abc.ABC):
    """Abstract base class for any entity that can engage in combat."""
    @abc.abstractmethod
    def take_damage(self, damage: int):
        pass

    @abc.abstractmethod
    def heal(self, amount: int):
        pass

    @property
    @abc.abstractmethod
    def health(self) -> int:
        pass

    @abc.abstractmethod
    def is_alive(self) -> bool:
        pass


# --- Core Components ---

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


class UseItemError(Exception):
    def __init__(self):
        super().__init__("Item cannot be used.")


class Item(CanCast): # Inherit from CanCast
    def __init__(self, name: str, cost: int, is_usable: bool = False, effect: Effect = Effect.NONE, effect_value: int = 0):
        self.name = name
        self.cost = cost
        self.quantity = 1
        self.is_usable = is_usable
        self.effect_type: Effect = effect
        self.effect_value = effect_value

    def cast(self, target: Combatant):
        """Applies the item's effect to the target."""
        if self.effect_type == Effect.HEAL:
            target.heal(self.effect_value)
        elif self.effect_type == Effect.DAMAGE:
            target.take_damage(self.effect_value)
        else:
            print(f"Item {self.name} has no castable effect.")
            raise UseItemError()

    def __iadd__(self, quantity: int):
        self.quantity += quantity
        return self

    def __isub__(self, quantity: int): # Added for decrementing quantity
        self.quantity -= quantity
        return self

    def __str__(self):
        return f"{self.name} x{self.quantity}"

    def __repr__(self):
        return f"Item('{self.name}', cost={self.cost}, qty={self.quantity}, usable={self.is_usable}, effect={self.effect_type.name}, value={self.effect_value})"

class InventoryError(Exception):
    """Base exception for inventory-related errors."""
    pass


class ItemNotFoundError(InventoryError):
    """Exception raised when an item is not found in the inventory."""
    def __init__(self, item_name: str):
        self.item_name = item_name
        super().__init__(f"Item '{item_name}' not found in inventory.")


class InsufficientQuantityError(InventoryError):
    """Exception raised when trying to remove more items than available."""
    def __init__(self, item_name: str, requested: int, available: int):
        self.item_name = item_name
        self.requested = requested
        self.available = available
        super().__init__(
            f"Cannot remove {requested} of {item_name}, only {available} items are available."
        )


class Inventory:
    """Manages a collection of items for a character."""

    def __init__(self):
        """Initialize an empty inventory."""
        self.items: dict[str, Item] = {}

    def add_item(self, item: Item):
        """Adds an item to the inventory, stacking if it already exists.

        Args:
            item: The item to add to the inventory
        """
        if not isinstance(item, Item):
            raise TypeError("Can only add Item objects to inventory")

        if item.name in self.items:
            self.items[item.name] += item.quantity
        else:
            self.items[item.name] = item

    def remove_item(self, item_name: str, quantity: int = 1):
        """Removes a specified quantity of an item from the inventory.

        Args:
            item_name: The name of the item to remove
            quantity: The quantity to remove (default: 1)

        Raises:
            ItemNotFoundError: If the item is not in the inventory
            InsufficientQuantityError: If trying to remove more than available
            ValueError: If quantity is not positive
        """
        if quantity <= 0:
            raise ValueError("Quantity to remove must be positive")

        if item_name not in self.items:
            # Still print for user feedback but also raise exception for proper handling
            print(f"Item '{item_name}' not found in inventory.")
            raise ItemNotFoundError(item_name)

        current_item = self.items[item_name]
        if quantity > current_item.quantity:
            # Still print for user feedback but also raise exception for proper handling
            print(f"Cannot remove {quantity} of {item_name}, only {current_item.quantity} items are available.")
            raise InsufficientQuantityError(item_name, quantity, current_item.quantity)

        current_item -= quantity
        if current_item.quantity <= 0:
            print(f"Item '{item_name}' removed entirely from inventory.")
            del self.items[item_name]
        else:
            print(f"Removed {quantity} of {item_name}. Remaining: {current_item.quantity}")

    def __getitem__(self, item_name: str) -> Item | None:
        """Allows dictionary-like access to retrieve an item.

        Args:
            item_name: The name of the item to retrieve

        Returns:
            The item if found, None otherwise
        """
        return self.items.get(item_name)

    def __repr__(self) -> str:
        """Returns a string representation of the inventory.

        Returns:
            A string listing all items in the inventory
        """
        return f"<Inventory with: {list(self.items.values())}>"

    def has_component(self, item):
        if item in self.items:
            return True
        else:
            return False


class Room:
    """
    Represents a single location or area in the game world.
    A room has a description and can contain items.
    """
    def __init__(self, name: str, description: str):
        """
        Initializes a new Room.

        Args:
            name: The name of the room (e.g., "Forest Clearing", "Dark Cave").
            description: A detailed description of the room.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Room name must be a non-empty string.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Room description must be a non-empty string.")

        self.name = name
        self.description = description
        self._components = HoldComponent()
        self._components.add_component("inventory", Inventory())

        # --- NEW: Internal state for lighting ---
        self._is_lit = False # Default state: room is not specifically lit by an in-room action
        # --- END NEW ---

    @property
    def inventory(self) -> Inventory:
        """
        Returns the Inventory component of the room, allowing access to items within it.
        """
        return self._components["inventory"]

    def add_item(self, item: Item):
        """
        Adds an item to the room's inventory.
        """
        self.inventory.add_item(item)
        print(f"[{self.name}] A {item.name} x{item.quantity} has appeared.")

    def remove_item(self, item_name: str, quantity: int = 1) -> Item:
        """
        Removes an item from the room's inventory.

        Args:
            item_name: The name of the item to remove.
            quantity: The quantity to remove (default: 1).

        Returns:
            The Item object that was removed (or a new Item object representing the quantity removed).
            Note: For simplicity, this returns a new Item instance with the removed quantity.
            You might want to refine this if precise object identity is crucial after removal.

        Raises:
            ItemNotFoundError: If the item is not found in the room.
            InsufficientQuantityError: If trying to remove more than available.
        """
        if not self.inventory.has_component(item_name):
            raise ItemNotFoundError(item_name)

        original_item = self.inventory[item_name]
        if quantity > original_item.quantity:
            raise InsufficientQuantityError(item_name, quantity, original_item.quantity)

        removed_item = Item(original_item.name, original_item.cost, original_item.is_usable,
                            original_item.effect_type, original_item.effect_value)
        removed_item.quantity = quantity

        self.inventory.remove_item(item_name, quantity)
        print(f"[{self.name}] Removed {quantity} of {item_name}.")

        # --- NEW: Check for torch removal impacting _is_lit state ---
        if item_name == "Torch" and original_item.quantity <= quantity:
            # If the last torch is removed, ensure the room isn't considered lit by it
            self._is_lit = False
            print(f"[{self.name}] The light source is gone, the area grows darker.")
        # --- END NEW ---

        return removed_item

    # --- NEW: Function to "use" an item in the room ---
    def use_item_in_room(self, item_name: str, user: 'Combatant'):
        """
        Simulates using an item that is currently in the room.
        This is for items that affect the room itself (like a torch).

        Args:
            item_name: The name of the item to use.
            user: The combatant using the item (e.g., the hero).
        Raises:
            ItemNotFoundError: If the item is not in the room.
            ValueError: If the item cannot be "used" in this context.
        """
        if not self.inventory.has_component(item_name):
            raise ItemNotFoundError(item_name)

        item_to_use = self.inventory[item_name]

        if item_name == "Torch":
            if self.name == "Dark Cave Entrance": # Only works in the dark cave for this example
                self._is_lit = True
                print(f"[{self.name}] {user.name} lights the Torch, illuminating a tiny area around you.")
            else:
                print(f"[{self.name}] Using the {item_name} here doesn't seem to have much effect.")
        else:
            # You can add logic for other usable items here
            print(f"[{self.name}] You try to use the {item_name}, but nothing happens yet.")
            raise ValueError(f"Item '{item_name}' cannot be used in this room.")
    # --- END NEW ---

    def get_description(self) -> str:
        """
        Returns the detailed description of the room, including its contents.
        The description can change based on certain items present or actions taken.
        """
        current_description = self.description

        if self.name == "Dark Cave Entrance":
            if self._is_lit:
                current_description = "The air is still cold, but the flickering light of the torch reveals a tiny, dusty area around you. Shadows dance at the edges of your vision."
            elif not self.inventory.has_component("Torch"): # If no torch is physically in the room
                current_description = "The cave entrance is now pitch black. You can barely see your hand in front of your face."
            else: # Torch is present but not used/lit
                current_description = "The air grows cold as you stand at the mouth of a dark, damp cave. You can dimly make out a torch lying on the ground."


        items_in_room = self.inventory.items.values()
        item_list_str = ""
        if items_in_room:
            item_list_str = "\n\nYou see here: " + ", ".join(str(item) for item in items_in_room)
        return f"{current_description}{item_list_str}"

    def __str__(self) -> str:
        return f"Room: {self.name}"

    def __repr__(self) -> str:
        return f"Room('{self.name}', '{self.description}')"



class SpellError(Exception):
    """Base exception for spell-related errors."""
    pass


class NoTargetError(SpellError):
    """Exception raised when attempting to cast a spell without a target."""
    def __init__(self, spell_name: str):
        self.spell_name = spell_name
        super().__init__(f"No target provided for spell '{spell_name}'.")


class Spell(CanCast):
    """Represents a magical spell that can be cast on a target."""

    def __init__(self, name: str, cost: int, caster: 'BaseCharacter', effect: callable):
        """Initialize a spell with a name, mana cost, caster, and effect.

        Args:
            name: The name of the spell
            cost: The mana cost to cast the spell
            caster: The character casting the spell
            effect: A callable that implements the spell's effect

        Raises:
            TypeError: If the effect is not callable
        """
        if not callable(effect):
            raise TypeError("Effect must be callable.")
        self.name = name
        self.cost = cost
        self.effect = effect
        self.caster = caster

    def cast(self, target: Combatant):
        """Casts the spell on the target.

        Args:
            target: The target to cast the spell on

        Raises:
            NoTargetError: If no target is provided
            Exception: Any exception that might be raised by the effect
        """
        if target is None:
            print(f"Error: No target provided for {self.name}.")
            raise NoTargetError(self.name)

        try:
            self.effect(target)
        except Exception as e:
            print(f"Error casting {self.name}: {e}")
            raise


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

# --- Character Classes ---

class BaseCharacter(Combatant):
    """Base class for all characters in the game."""
    def __init__(self, name: str, level: int, base_health: int, xp_value: int = 0):
        """Initialize a base character with common attributes.

        Args:
            name: Character's name
            level: Character's level
            base_health: Base health points
            xp_value: Experience points awarded when defeated
        """
        self.name = name
        self.level = level
        self.xp_value = xp_value
        self.components = HoldComponent()
        self.components.add_component("health", Health(base_health))

    def get_health_component(self) -> Health:
        """Get the health component of the character."""
        return self.components["health"]

    def take_damage(self, damage: int):
        """Take damage, reducing health."""
        self.get_health_component().take_damage(damage)

    def heal(self, amount: int):
        """Heal the character, increasing health."""
        self.get_health_component().heal(amount)

    def is_alive(self) -> bool:
        """Check if the character is alive."""
        return self.get_health_component().health > 0

    @property
    def health(self) -> int:
        """Get the current health value."""
        return self.get_health_component().health

    def attack(self, target: Combatant, weapon_name: str):
        """Generic attack method using a specified weapon component.

        Args:
            target: The target to attack
            weapon_name: The name of the weapon component to use

        Raises:
            ValueError: If target is None or weapon doesn't exist
        """
        if target is None:
            raise ValueError(f"{self.name} tried to attack, but no target was provided.")

        if not self.components.has_component(weapon_name):
            raise ValueError(f"{self.name} doesn't have a {weapon_name} to attack with.")

        self.components[weapon_name].cast(target)


class Goblin(BaseCharacter):
    """Goblin enemy class."""
    def __init__(self, name: str, level: int):
        """Initialize a goblin with default attributes."""
        super().__init__(name, level, base_health=100, xp_value=100)
        self.components.add_component("sword", Item("Rusty Sword", 25, True, effect=Effect.DAMAGE, effect_value=10))

    @property
    def sword(self) -> Item:
        """Returns the goblin's sword item."""
        return self.components["sword"]

    def attacks(self, target: Combatant):
        """Goblin attacks a target with its sword."""
        try:
            self.attack(target, "sword")
        except ValueError as e:
            print(str(e))

class Troll(BaseCharacter):
    """Troll enemy class with regeneration ability."""
    def __init__(self, name: str, level: int):
        """Initialize a troll with default attributes."""
        super().__init__(name, level, base_health=250, xp_value=150)
        # Trolls have natural regeneration and a different attack
        self.components.add_component("claws", Item("Troll Claws", 0, True, effect=Effect.DAMAGE, effect_value=20))
        # Special regeneration ability
        self.components.add_component("regeneration", Spell("Regenerate", 0, self, lambda target: target.heal(15)))

    @property
    def claws(self) -> Item:
        """Returns the troll's claws item."""
        return self.components["claws"]

    def attacks(self, target: Combatant):
        """Troll attacks a target with its claws."""
        try:
            self.attack(target, "claws")
        except ValueError as e:
            print(str(e))

    def regenerate(self):
        """Troll uses its regeneration ability to heal itself."""
        try:
            print(f"{self.name} regenerates some health!")
            self.attack(self, "regeneration")
        except ValueError as e:
            print(str(e))

class RpgHero(BaseCharacter):
    """Hero character class with spells, mana, and inventory."""
    BASE_XP_TO_NEXT_LEVEL = 100
    BASE_MANA = 100
    BASE_HEALTH = 100
    MANA_PER_LEVEL = 2
    HEALTH_PER_LEVEL = 5

    def __init__(self, name: str, level: int):
        """Initialize a hero with default attributes and abilities."""
        # Calculate health based on level
        health = self.BASE_HEALTH + (level - 1) * self.HEALTH_PER_LEVEL
        super().__init__(name, level, base_health=health)

        # Hero-specific initialization
        self.xp = 0
        self.xp_to_next_level = self._calculate_xp_to_next_level()

        # Add hero-specific components
        self.components.add_component("mana", Mana(self.BASE_MANA + (level - 1) * self.MANA_PER_LEVEL))
        self.components.add_component("fireball", Spell("Fireball", 25, self, lambda target: target.take_damage(10)))
        self.components.add_component("magic_missile", Spell("Magic Missile", 5, self, lambda target: target.take_damage(1)))
        self.components.add_component("inventory", Inventory())

    def _calculate_xp_to_next_level(self) -> int:
        """Calculates the XP required for the next level."""
        return self.BASE_XP_TO_NEXT_LEVEL + (self.level * 50)

    def add_xp(self, xp: int):
        """Adds experience points to the hero and levels up if threshold reached."""
        if xp < 0:
            raise ValueError("XP cannot be negative.")
        self.xp += xp
        while self.xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self):
        """Increases hero's level and updates stats."""
        self.xp -= self.xp_to_next_level
        self.level += 1
        self.xp_to_next_level = self._calculate_xp_to_next_level()
        self.components["mana"].mana = self.BASE_MANA + self.level * self.MANA_PER_LEVEL
        self.components["health"].health = self.BASE_HEALTH + self.level * self.HEALTH_PER_LEVEL
        print(f"{self.name} leveled up to level {self.level}!")

    def get_mana_component(self) -> Mana:
        """Get the mana component of the hero."""
        return self.components["mana"]

    def get_spell(self, spell_name: str) -> Spell | None:
        """Retrieves a spell by name if it exists and is a Spell.

        Args:
            spell_name: The name of the spell to retrieve

        Returns:
            The spell object or None if not found
        """
        if self.components.has_component(spell_name):
            component = self.components[spell_name]
            if isinstance(component, Spell):
                return component
        return None

    class SpellCastError(Exception):
        """Exception raised when a spell cannot be cast."""
        pass

    class SpellNotFoundError(SpellCastError):
        """Exception raised when a spell is not found."""
        def __init__(self, spell_name: str):
            self.spell_name = spell_name
            super().__init__(f"Spell '{spell_name}' doesn't exist.")

    class InsufficientManaError(SpellCastError):
        """Exception raised when there is not enough mana to cast a spell."""
        def __init__(self, spell_name: str, cost: int, available: int):
            self.spell_name = spell_name
            self.cost = cost
            self.available = available
            super().__init__(f"Not enough mana for '{spell_name}'. Required: {cost}, Available: {available}")

    def cast_spell(self, spell_name: str, target: Combatant) -> bool:
        """Cast a spell on a target if the hero has enough mana.

        Args:
            spell_name: The name of the spell to cast
            target: The target to cast the spell on

        Returns:
            True if the spell was cast successfully, False otherwise

        Raises:
            SpellNotFoundError: If the spell doesn't exist
            InsufficientManaError: If there's not enough mana
            NoTargetError: If no target is provided
            Exception: Any exception that might be raised by the spell's effect
        """
        spell = self.get_spell(spell_name)
        if not spell:
            print(f"Spell '{spell_name}' doesn't exist.")
            raise self.SpellNotFoundError(spell_name)

        current_mana = self.get_mana_component().mana
        if current_mana < spell.cost:
            print(f"Not enough mana for '{spell_name}'.")
            raise self.InsufficientManaError(spell_name, spell.cost, current_mana)

        try:
            self.get_mana_component().consume(spell.cost)
            spell.cast(target)
            return True
        except NoTargetError as e:
            # Re-raise the exception after consuming mana
            # In a real game, you might want to refund the mana here
            print(f"Failed to cast {spell_name}: {e}")
            raise
        except Exception as e:
            # Handle any other exceptions from the spell cast
            print(f"Error occurred while casting {spell_name}: {e}")
            raise

    @property
    def mana(self) -> int:
        """Get the current mana value."""
        return self.get_mana_component().mana

    @property
    def inventory(self) -> Inventory:
        """Get the hero's inventory."""
        return self.components["inventory"]


def handle_inventory_operation(operation_func, *args, **kwargs):
    """Helper function to handle common inventory operation exceptions.

    Args:
        operation_func: The inventory operation function to execute
        *args, **kwargs: Arguments to pass to the operation function

    Returns:
        The result of the operation function if successful, None if an exception occurred

    Raises:
        Any exceptions not caught by this handler
    """
    try:
        return operation_func(*args, **kwargs)
    except ItemNotFoundError as e:
        print(f"Error: {e}")
        return None
    except InsufficientQuantityError as e:
        print(f"Error: {e}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None
    except TypeError as e:
        print(f"Error adding item: {e}")
        return None

def handle_spell_cast(hero, spell_name, target):
    """Helper function to handle common spell casting exceptions.

    Args:
        hero: The hero casting the spell
        spell_name: The name of the spell to cast
        target: The target of the spell

    Returns:
        True if the spell was cast successfully, False otherwise
    """
    try:
        return hero.cast_spell(spell_name, target)
    except RpgHero.SpellCastError as e:
        print(f"Spell casting failed: {e}")
    except NoTargetError as e:
        print(f"Spell casting failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return False

def main():
    """Main function to demonstrate the RPG game mechanics."""
    print("Once upon a time in the land of KingBase...")

    # Create characters
    hero_bob = RpgHero("Bob", 1)
    hero_john = RpgHero("John", 1)
    goblin = Goblin("Goblin", 1)
    troll = Troll("Troll", 1)

    # --- Room Demonstration ---
    print("\nChapter 1: The Adventure Begins")
    starting_room = Room("Forest Clearing",
                         "A peaceful clearing in a dense forest. Sunlight filters through the leaves.")
    dark_cave = Room("Dark Cave Entrance", "The air grows cold as you stand at the mouth of a dark, damp cave.")

    # Add items to rooms
    starting_room.add_item(Item("Health Potion", 10, True, Effect.HEAL, 20))
    starting_room.add_item(Item("Shiny Coin", 1, False))
    starting_room.add_item(Item("Wooden Shield", 50, False))

    # Add a torch to the dark cave
    dark_cave.add_item(Item("Torch", 5, True))
    dark_cave.add_item(Item("Goblin Ear", 1, False))

    print(f"\nOur heroes ventured forth from the Forest Clearing and arrived at the {dark_cave.name}.")
    print("As they peered into the darkness, this is what they saw:")
    print(dark_cave.get_description())  # Will show "You can dimly make out a torch"

    # Hero "uses" the torch in the room
    print(f"\nBrave {hero_john.name} stepped forward and attempted to light the Torch within the {dark_cave.name}.")
    try:
        dark_cave.use_item_in_room("Torch", hero_john)
        print("With the torch now illuminating the cave, they could see:")
        print(dark_cave.get_description())  # Will show the "tiny, dusty area" description
    except ItemNotFoundError as e:
        print(f"Failed to use item: {e}")
    except ValueError as e:
        print(f"Failed to use item: {e}")

    # Hero picks up the torch
    print(f"\n'We might need this later,' said {hero_john.name} as he reached for the Torch in the {dark_cave.name}.")
    try:
        torch = dark_cave.remove_item("Torch")
        hero_john.inventory.add_item(torch)
        print(f"{hero_john.name} added the torch to his belongings: {hero_john.inventory}")
    except (ItemNotFoundError, InsufficientQuantityError) as e:
        print(f"Failed to pick up item: {e}")

    print("\nWith the torch now in John's possession, the cave returned to darkness:")
    print(dark_cave.get_description())  # Will now show the "pitch black" description

    # Demonstrate spell casting
    print("\nChapter 2: Magical Mishaps")
    print(f"Suddenly, {hero_john.name} lost his temper and cast Magic Missile at {hero_bob.name}!")
    if handle_spell_cast(hero_john, "magic_missile", hero_bob):
        print(f"{hero_bob.name} winced in pain, his health dropping to {hero_bob.health}.")
        print(f"{hero_john.name} felt his magical energy drain to {hero_john.mana}.")

    # Demonstrate mana limitations
    print(f"\nEnraged, {hero_bob.name} attempted to retaliate with a Fireball at {hero_john.name}.")
    hero_bob.get_mana_component().consume(99)  # Simulate low mana
    try:
        hero_bob.cast_spell("fireball", hero_john)  # Should fail due to insufficient mana
    except RpgHero.InsufficientManaError as e:
        print(f"But alas! {e}")
    print(f"{hero_bob.name} was exhausted, his magical reserves depleted to {hero_bob.mana}.")
    print(f"{hero_john.name} remained standing with {hero_john.health} health, untouched by Bob's failed spell.")

    # Demonstrate non-existent spell
    print(f"\nIn desperation, {hero_bob.name} tried to remember a legendary spell from ancient texts...")
    try:
        hero_bob.cast_spell("super_fireball", hero_john)  # Should fail - spell doesn't exist
    except RpgHero.SpellNotFoundError as e:
        print(f"But the words escaped him: {e}")

    # Demonstrate combat with enemies
    print("\nChapter 3: Monsters Emerge")
    print(f"Their argument was interrupted by a snarling {goblin.name} emerging from the shadows!")
    print(f"{hero_john.name} quickly gathered his wits and hurled a Fireball at the creature.")
    if handle_spell_cast(hero_john, "fireball", goblin):
        print(f"The {goblin.name} shrieked as flames engulfed it, reducing its health to {goblin.health}.")

    print(f"\nThough wounded, the {goblin.name} lunged at {hero_bob.name} with its jagged dagger!")
    goblin.attacks(hero_bob)
    print(f"Blood trickled down {hero_bob.name}'s arm as his health fell to {hero_bob.health}.")

    # Demonstrate troll abilities
    print("\nChapter 4: The Troll's Lair")
    print(f"As they ventured deeper into the cave, a massive {troll.name} blocked their path!")
    print(f"Remembering his magical training, {hero_bob.name} summoned a Fireball against the {troll.name}.")
    # Restore some mana for Bob to cast the spell
    hero_bob.get_mana_component().mana = 30
    if handle_spell_cast(hero_bob, "fireball", troll):
        print(f"The {troll.name} roared in pain, its thick hide scorched to {troll.health} health.")

    print(f"\nThe enraged {troll.name} swung its massive claws toward {hero_bob.name}!")
    try:
        troll.attacks(hero_bob)
        print(f"{hero_bob.name} barely dodged the full force of the blow, but his health dropped to {hero_bob.health}.")
    except ValueError as e:
        print(f"Attack failed: {e}")

    print(f"\n'Stand back!' shouted {hero_john.name} as he conjured another Fireball at the {troll.name}.")
    if handle_spell_cast(hero_john, "fireball", troll):
        print(f"The {troll.name} staggered backward, its health reduced to {troll.health}.")

    if troll.health < 250:
        troll.regenerate()
        print(f"To their horror, the {troll.name}'s wounds began to close before their eyes, its health rising to {troll.health}!")

    # Demonstrate inventory management
    print("\nChapter 5: Weapons of Destiny")
    print(f"Amidst the chaos, {hero_john.name} spotted an abandoned Sword gleaming in the corner of the cave.")
    handle_inventory_operation(hero_john.inventory.add_item, Item("Sword", 10, True, Effect.DAMAGE, 10))
    print(f"{hero_john.name} added the weapon to his collection: {hero_john.inventory}")
    print(f"He examined the Sword closely: {hero_john.inventory['Sword']}")
    print(f"He wished he had a Pike as well, but found none: {hero_john.inventory['Pike']}")

    print(f"\nStill angry about the earlier magical attack, {hero_john.name} swung his new Sword at {hero_bob.name}!")
    try:
        sword = hero_john.inventory["Sword"]
        if sword:
            sword.cast(hero_bob)
            print(f"{hero_bob.name} stumbled backward, his health now at a dangerous {hero_bob.health}.")
        else:
            print(f"{hero_john.name} reached for a Sword that wasn't there.")
    except UseItemError as e:
        print(f"Item use failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print(f"\nDesperate to defend himself, {hero_bob.name} discovered an ancient Greatsword embedded in the cave wall.")
    handle_inventory_operation(hero_bob.inventory.add_item, Item("Greatsword", 100, True, Effect.DAMAGE, 100))
    print(f"With trembling hands, he added it to his possessions: {hero_bob.inventory}")

    print(f"\nWith newfound courage, {hero_bob.name} turned to face the wounded {goblin.name}, Greatsword raised high!")
    try:
        greatsword = hero_bob.inventory["Greatsword"]
        if greatsword:
            greatsword.cast(goblin)
            print(f"The mighty blade cleaved through the {goblin.name}, leaving it with just {goblin.health} health.")
        else:
            print(f"{hero_bob.name} reached for a weapon that wasn't there.")
    except UseItemError as e:
        print(f"Item use failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # Demonstrate combat resolution and XP
    print("\nChapter 6: Victory and Growth")
    if goblin.is_alive():
        print(f"Despite their efforts, the {goblin.name} still stood, wounded but defiant!")
    else:
        print(f"With a final groan, the {goblin.name} collapsed to the ground, defeated!")
        hero_bob.add_xp(goblin.xp_value)

    print(f"\n{hero_bob.name} felt stronger from the battle, his experience growing to {hero_bob.xp}.")
    print(f"He could feel the power coursing through him as he reached level {hero_bob.level}.")
    print(f"His magical reserves settled at {hero_bob.mana}, while his wounds left him with {hero_bob.health} health.")

    # Demonstrate item quantity and removal
    print("\nChapter 7: The Journey Continues")
    print(f"As they prepared to leave the cave, {hero_john.name} found another Sword among the goblin's belongings.")
    handle_inventory_operation(hero_john.inventory.add_item, Item("Sword", 10, True, Effect.DAMAGE, 10))
    print(f"He now had {hero_john.inventory['Sword']} in his collection.")

    print(f"\n'This one is poorly balanced,' muttered {hero_john.name}, tossing one Sword aside.")
    handle_inventory_operation(hero_john.inventory.remove_item, "Sword")
    print(f"His remaining equipment: {hero_john.inventory}")

    print(f"\n'The other is no better,' he sighed, discarding his last Sword.")
    handle_inventory_operation(hero_john.inventory.remove_item, "Sword")
    print(f"With empty hands, he surveyed what remained: {hero_john.inventory}")

    # Demonstrate error handling
    print("\nChapter 8: Lessons Learned")
    print(f"{hero_john.name} frantically searched his pack for his lucky charm, but it was nowhere to be found:")
    result = handle_inventory_operation(hero_john.inventory.remove_item, "NonExistentItem")

    print(f"\nBefore leaving the cave, {hero_john.name} discovered a HealthPotion and tucked it away.")
    # First add an item to remove
    handle_inventory_operation(hero_john.inventory.add_item, Item("HealthPotion", 5, True, Effect.HEAL, 20))
    print(f"But when he tried to give away negative portions of the potion, strange things happened:")
    result = handle_inventory_operation(hero_john.inventory.remove_item, "HealthPotion", -1)

    print(f"\n'I need two potions for our journey,' declared {hero_john.name}, but reality had other plans:")
    # Make sure we have exactly one
    if hero_john.inventory["HealthPotion"]:
        result = handle_inventory_operation(hero_john.inventory.remove_item, "HealthPotion", 2)

    print("\nAnd thus, our heroes' adventure in the cave came to an end, with many lessons learned and battles won.")


if __name__ == '__main__':
    main()
