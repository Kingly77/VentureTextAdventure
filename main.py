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

    def __iadd__(self, quantity: int):
        self.quantity += quantity
        return self

    def __isub__(self, quantity: int): # Added for decrementing quantity
        self.quantity -= quantity
        return self

    def __str__(self):
        return f"{self.name} x{self.quantity}"

class Inventory:
    def __init__(self):
        self.items: dict[str, Item] = {}

    def add_item(self, item: Item):
        """Adds an item to the inventory, stacking if it already exists."""
        if item.name in self.items:
            self.items[item.name] += item.quantity # Use += for existing item
        else:
            self.items[item.name] = item

    def remove_item(self, item_name: str, quantity: int = 1):
        """Removes a specified quantity of an item from the inventory.
        Removes the item entirely if quantity reaches zero."""
        if item_name not in self.items:
            raise KeyError(f"Item '{item_name}' not found in inventory.")

        current_item = self.items[item_name]
        current_item -= quantity # Use -= to decrement quantity

        if current_item.quantity <= 0:
            del self.items[item_name]
        print(f"Removed {quantity} of {item_name}. Remaining: {self.items.get(item_name)}")


    def __getitem__(self, item_name: str) -> Item | None:
        """Allows dictionary-like access to retrieve an item."""
        return self.items.get(item_name) # Use .get to return None if not found

    def __repr__(self):
        return f"<Inventory with: {list(self.items.values())}>" # More descriptive repr


class Spell(CanCast):
    def __init__(self, name: str, cost: int, caster: 'RpgHero', effect: callable):
        self.name = name
        self.cost = cost
        self.effect = effect
        self.caster = caster

    def cast(self, target: Combatant): # Changed type hint to Combatant
        """Casts the spell on the target."""
        if target is None:
            print(f"Error: No target provided for {self.name}.")
            return
        self.effect(target)


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

class Goblin(Combatant): # Inherit from Combatant
    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level
        self.xp_value = 100
        self.components = HoldComponent()
        self.components.add_component("health", Health(100))
        self.components.add_component("sword", Item("Rusty Sword", 25, True, effect=Effect.DAMAGE, effect_value=10))

    def get_health_component(self) -> Health: # Renamed for clarity
        return self.components["health"]

    def take_damage(self, damage: int):
        self.get_health_component().take_damage(damage)

    def heal(self, amount: int):
        self.get_health_component().heal(amount)

    def is_alive(self) -> bool:
        return self.get_health_component().health > 0

    @property
    def sword(self) -> Item:
        """Returns the goblin's sword item."""
        return self.components["sword"]

    @property
    def health(self) -> int:
        return self.get_health_component().health

    def attacks(self, target: Combatant): # Changed type hint to Combatant
        """Goblin attacks a target with its sword."""
        if target is None:
            print(f"{self.name} tried to attack, but no target was provided.")
            return
        self.sword.cast(target)


class RpgHero(Combatant): # Inherit from Combatant
    BASE_XP_TO_NEXT_LEVEL = 100
    BASE_MANA = 100
    BASE_HEALTH = 100
    MANA_PER_LEVEL = 2
    HEALTH_PER_LEVEL = 5

    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level
        self.xp = 0
        self.xp_to_next_level = self._calculate_xp_to_next_level()
        self.components = HoldComponent()
        self.components.add_component("mana", Mana(self.BASE_MANA + (level - 1) * self.MANA_PER_LEVEL))
        self.components.add_component("health", Health(self.BASE_HEALTH + (level - 1) * self.HEALTH_PER_LEVEL))
        self.components.add_component("fireball", Spell("Fireball", 25, self, lambda target: target.take_damage(10)))
        self.components.add_component("magic_missile", Spell("Magic Missile", 5, self, lambda target: target.take_damage(1)))
        self.components.add_component("inventory", Inventory())

    def _calculate_xp_to_next_level(self) -> int:
        """Calculates the XP required for the next level."""
        # A more common formula for XP scaling, avoiding the potential for huge jumps:
        # self.xp_to_next_level = self.BASE_XP_TO_NEXT_LEVEL * (self.level * (self.level + 1)) // 2
        # A simpler, more linear or slightly exponential scaling might be better for an RPG progression feel.
        return self.BASE_XP_TO_NEXT_LEVEL + (self.level * 50) # Example: linear increase

    def add_xp(self, xp: int):
        """Adds experience points to the hero."""
        if xp < 0:
            raise ValueError("XP cannot be negative.")
        self.xp += xp
        while self.xp >= self.xp_to_next_level: # Use while to handle multiple level-ups
            self.level_up()

    def level_up(self):
        """Increases hero's level and updates stats."""
        self.xp -= self.xp_to_next_level
        self.level += 1
        self.xp_to_next_level = self._calculate_xp_to_next_level()
        self.components["mana"].mana = self.BASE_MANA + self.level * self.MANA_PER_LEVEL
        self.components["health"].health = self.BASE_HEALTH + self.level * self.HEALTH_PER_LEVEL
        print(f"{self.name} leveled up to level {self.level}!")


    def get_mana_component(self) -> Mana: # Renamed for clarity
        return self.components["mana"]

    def get_health_component(self) -> Health: # Renamed for clarity
        return self.components["health"]

    def take_damage(self, damage: int):
        self.get_health_component().take_damage(damage)

    def heal(self, amount: int):
        self.get_health_component().heal(amount)

    def is_alive(self) -> bool:
        return self.get_health_component().health > 0

    def get_spell(self, spell_name: str) -> Spell | None: # Renamed for clarity
        """Retrieves a spell by name if it exists and is a Spell."""
        if self.components.has_component(spell_name):
            component = self.components[spell_name]
            if isinstance(component, Spell):
                return component
        return None

    def cast_spell(self, spell_name: str, target: Combatant): # Changed to take spell_name
        """Casts a spell on a target by its name."""
        spell = self.get_spell(spell_name)
        if spell is None:
            print(f"{self.name} tried to cast '{spell_name}' but it doesn't exist or isn't a spell.")
            return
        if target is None:
            print(f"{self.name} tried to cast {spell.name} but no target was provided.")
            return

        if self.get_mana_component().mana < spell.cost:
            print(f"{self.name} doesn't have enough mana to cast {spell.name}! (Needs {spell.cost}, has {self.mana})")
            return

        self.get_mana_component().consume(spell.cost)
        spell.cast(target)
        print(f"{self.name} cast {spell.name} on {target.name}.")


    @property
    def mana(self) -> int:
        return self.get_mana_component().mana

    @property
    def health(self) -> int:
        return self.get_health_component().health

    @property
    def inventory(self) -> Inventory:
        return self.components["inventory"]


def main():
    print("--- RPG Simulation Start ---")

    hero_bob = RpgHero("Bob", 1)
    hero_john = RpgHero("John", 1)
    goblin = Goblin("Goblin", 1)

    print(f"\n{hero_john.name} casts Magic Missile at {hero_bob.name}")
    hero_john.cast_spell("magic_missile", hero_bob)
    print(f"{hero_bob.name}'s health is now: {hero_bob.health}")
    print(f"{hero_john.name}'s mana is now: {hero_john.mana}")


    print(f"\n{hero_bob.name} casts Fireball at {hero_john.name}")
    # Simulate Bob running low on mana to test the check
    hero_bob.get_mana_component().consume(99)
    hero_bob.cast_spell("fireball", hero_john) # This should print "not enough mana"
    print(f"{hero_bob.name}'s Mana is now: {hero_bob.mana}")
    print(f"{hero_john.name}'s health is now: {hero_john.health}")

    print(f"\n{hero_john.name} Fireballs the {goblin.name}")
    hero_john.cast_spell("fireball", goblin)
    print(f"{goblin.name}'s health is now: {goblin.health}")

    print(f"\n{goblin.name} attacks {hero_bob.name}")
    goblin.attacks(hero_bob)
    print(f"{hero_bob.name}'s health is now: {hero_bob.health}")

    print(f"\n{hero_john.name} adds a Sword to inventory.")
    hero_john.inventory.add_item(Item("Sword", 10, True, Effect.DAMAGE, 10))
    print(f"{hero_john.name}'s inventory: {hero_john.inventory}")
    print(f"Attempting to get 'Sword' from {hero_john.name}'s inventory: {hero_john.inventory['Sword']}")
    print(f"Attempting to get 'Pike' from {hero_john.name}'s inventory: {hero_john.inventory['Pike']}") # Should be None

    print(f"\n{hero_john.name} uses Sword on {hero_bob.name}")
    if hero_john.inventory["Sword"]:
        hero_john.inventory["Sword"].cast(hero_bob)
    print(f"{hero_bob.name}'s health is now: {hero_bob.health}")

    print(f"\n{hero_bob.name} adds a powerful Sword to inventory.")
    hero_bob.inventory.add_item(Item("Greatsword", 100, True, Effect.DAMAGE, 100))
    print(f"{hero_bob.name}'s inventory: {hero_bob.inventory}")

    print(f"\n{hero_bob.name} attacks {goblin.name} with Greatsword")
    if hero_bob.inventory["Greatsword"]:
        hero_bob.inventory["Greatsword"].cast(goblin)
    print(f"{goblin.name}'s health is now: {goblin.health}")

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

    # Test item quantity and removal
    print(f"\n{hero_john.name} adds another Sword.")
    hero_john.inventory.add_item(Item("Sword", 10, True, Effect.DAMAGE, 10))
    print(f"{hero_john.name}'s inventory: {hero_john.inventory['Sword']}")
    hero_john.inventory.remove_item("Sword")
    print(f"{hero_john.name}'s inventory after removal: {hero_john.inventory}")
    hero_john.inventory.remove_item("Sword") # This will remove the last one
    print(f"{hero_john.name}'s inventory after second removal: {hero_john.inventory}")


    print("\n--- RPG Simulation End ---")


if __name__ == '__main__':
    main()