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

    def __init__(self, name: str, cost: int, caster: 'RpgHero', effect: callable):
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


def main():
    """Main function to demonstrate the RPG game mechanics."""
    print("--- RPG Simulation Start ---")

    # Create characters
    hero_bob = RpgHero("Bob", 1)
    hero_john = RpgHero("John", 1)
    goblin = Goblin("Goblin", 1)
    troll = Troll("Troll", 1)

    # Demonstrate spell casting
    print("\n--- Spell Casting Demo ---")
    print(f"{hero_john.name} casts Magic Missile at {hero_bob.name}")
    try:
        hero_john.cast_spell("magic_missile", hero_bob)
        print(f"{hero_bob.name}'s health is now: {hero_bob.health}")
        print(f"{hero_john.name}'s mana is now: {hero_john.mana}")
    except RpgHero.SpellCastError as e:
        print(f"Spell casting failed: {e}")
    except NoTargetError as e:
        print(f"Spell casting failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # Demonstrate mana limitations
    print(f"\n{hero_bob.name} tries to cast Fireball at {hero_john.name}")
    hero_bob.get_mana_component().consume(99)  # Simulate low mana
    try:
        hero_bob.cast_spell("fireball", hero_john)  # Should fail due to insufficient mana
    except RpgHero.InsufficientManaError as e:
        print(f"Expected error: {e}")
    print(f"{hero_bob.name}'s Mana is now: {hero_bob.mana}")
    print(f"{hero_john.name}'s health is now: {hero_john.health}")

    # Demonstrate non-existent spell
    print(f"\n{hero_bob.name} tries to cast a non-existent spell")
    try:
        hero_bob.cast_spell("super_fireball", hero_john)  # Should fail - spell doesn't exist
    except RpgHero.SpellNotFoundError as e:
        print(f"Expected error: {e}")

    # Demonstrate combat with enemies
    print("\n--- Combat Demo ---")
    print(f"{hero_john.name} casts Fireball at the {goblin.name}")
    try:
        hero_john.cast_spell("fireball", goblin)
        print(f"{goblin.name}'s health is now: {goblin.health}")
    except Exception as e:
        print(f"Spell casting failed: {e}")

    print(f"\n{goblin.name} attacks {hero_bob.name}")
    goblin.attacks(hero_bob)
    print(f"{hero_bob.name}'s health is now: {hero_bob.health}")

    # Demonstrate troll abilities
    print("\n--- Troll Abilities Demo ---")
    print(f"{hero_bob.name} uses Fireball on {troll.name}")
    try:
        # Restore some mana for Bob to cast the spell
        hero_bob.get_mana_component().mana = 30
        hero_bob.cast_spell("fireball", troll)
        print(f"{troll.name}'s health is now: {troll.health}")
    except RpgHero.SpellCastError as e:
        print(f"Spell casting failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print(f"{troll.name} claws {hero_bob.name}")
    try:
        troll.attacks(hero_bob)
        print(f"{hero_bob.name}'s health is now: {hero_bob.health}")
    except ValueError as e:
        print(f"Attack failed: {e}")

    print(f"{hero_john.name} casts Fireball at the {troll.name}")
    try:
        hero_john.cast_spell("fireball", troll)
        print(f"{troll.name}'s health is now: {troll.health}")
    except RpgHero.SpellCastError as e:
        print(f"Spell casting failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    if troll.health < 250:
        troll.regenerate()
        print(f"{troll.name} health is now: {troll.health}")

    # Demonstrate inventory management
    print("\n--- Inventory Demo ---")
    print(f"{hero_john.name} adds a Sword to inventory")
    hero_john.inventory.add_item(Item("Sword", 10, True, Effect.DAMAGE, 10))
    print(f"{hero_john.name}'s inventory: {hero_john.inventory}")
    print(f"Getting 'Sword' from inventory: {hero_john.inventory['Sword']}")
    print(f"Getting 'Pike' from inventory (should be None): {hero_john.inventory['Pike']}")

    print(f"\n{hero_john.name} uses Sword on {hero_bob.name}")
    try:
        sword = hero_john.inventory["Sword"]
        if sword:
            sword.cast(hero_bob)
            print(f"{hero_bob.name}'s health is now: {hero_bob.health}")
        else:
            print(f"{hero_john.name} doesn't have a Sword")
    except UseItemError as e:
        print(f"Item use failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print(f"\n{hero_bob.name} adds a powerful Sword to inventory")
    try:
        hero_bob.inventory.add_item(Item("Greatsword", 100, True, Effect.DAMAGE, 100))
        print(f"{hero_bob.name}'s inventory: {hero_bob.inventory}")
    except TypeError as e:
        print(f"Error adding item: {e}")

    print(f"\n{hero_bob.name} attacks {goblin.name} with Greatsword")
    try:
        greatsword = hero_bob.inventory["Greatsword"]
        if greatsword:
            greatsword.cast(goblin)
            print(f"{goblin.name}'s health is now: {goblin.health}")
        else:
            print(f"{hero_bob.name} doesn't have a Greatsword")
    except UseItemError as e:
        print(f"Item use failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # Demonstrate combat resolution and XP
    print("\n--- Combat Resolution ---")
    if goblin.is_alive():
        print(f"{goblin.name} is still alive!")
    else:
        print(f"{goblin.name} is defeated!")
        hero_bob.add_xp(goblin.xp_value)

    print(f"\n{hero_bob.name}'s XP is now: {hero_bob.xp}")
    print(f"{hero_bob.name}'s level is now: {hero_bob.level}")
    print(f"{hero_bob.name}'s mana is now: {hero_bob.mana}")
    print(f"{hero_bob.name}'s health is now: {hero_bob.health}")

    # Demonstrate item quantity and removal
    print("\n--- Item Management Demo ---")
    print(f"{hero_john.name} adds another Sword")
    try:
        hero_john.inventory.add_item(Item("Sword", 10, True, Effect.DAMAGE, 10))
        print(f"{hero_john.name}'s inventory: {hero_john.inventory['Sword']}")
    except TypeError as e:
        print(f"Error adding item: {e}")

    print(f"Removing one Sword from {hero_john.name}'s inventory")
    try:
        hero_john.inventory.remove_item("Sword")
        print(f"Inventory after removal: {hero_john.inventory}")
    except ItemNotFoundError as e:
        print(f"Error: {e}")
    except InsufficientQuantityError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")

    print(f"Removing the last Sword from {hero_john.name}'s inventory")
    try:
        hero_john.inventory.remove_item("Sword")
        print(f"Inventory after second removal: {hero_john.inventory}")
    except ItemNotFoundError as e:
        print(f"Error: {e}")
    except InsufficientQuantityError as e:
        print(f"Error: {e}")

    # Demonstrate error handling
    print("\n--- Error Handling Demo ---")
    print("Trying to remove a non-existent item:")
    try:
        hero_john.inventory.remove_item("NonExistentItem")
    except ItemNotFoundError as e:
        print(f"Caught exception: {e}")

    print("\nTrying to remove an invalid quantity:")
    try:
        # First add an item to remove
        hero_john.inventory.add_item(Item("HealthPotion", 5, True, Effect.HEAL, 20))
        hero_john.inventory.remove_item("HealthPotion", -1)
    except ValueError as e:
        print(f"Caught exception: {e}")

    print("\nTrying to remove more than available:")
    try:
        # Make sure we have exactly one
        if hero_john.inventory["HealthPotion"]:
            hero_john.inventory.remove_item("HealthPotion", 2)
    except InsufficientQuantityError as e:
        print(f"Caught exception: {e}")

    print("\n--- RPG Simulation End ---")


if __name__ == '__main__':
    main()
