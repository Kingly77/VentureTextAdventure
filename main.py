import abc
import enum

class CanCast(abc.ABC):
    @abc.abstractmethod
    def cast(self, target: 'RpgHero'):
        pass

class HoldComponent:
    def __init__(self):
        self._components = {}

    def add_component(self, name, component):
        """Adds a component to the holder by name."""
        if name in self._components:
            raise ValueError(f"Component '{name}' is already added.")
        if not isinstance(name, str) or not name.strip():
            raise TypeError("Component name must be a non-empty string.")
        self._components[name] = component

    def get_component(self, name):
        """Retrieves a component by name."""
        if name not in self._components:
            raise KeyError(f"Component '{name}' not found.")
        return self._components[name]

    def remove_component(self, name):
        """Removes a component by name."""
        if name not in self._components:
            raise KeyError(f"Component '{name}' not found.")
        del self._components[name]

    def all_components(self):
        """Returns all stored components."""
        return self._components.values()

    def has_component(self, name):
        """Checks if a component exists."""
        return name in self._components

    def __getitem__(self, name):
        """Enables dictionary-like access for components."""
        return self.get_component(name)

    def __repr__(self):
        """Returns readable class representation for debugging."""
        components = ', '.join(self._components.keys())
        return f"<HoldComponent with: {components}>"


class Effect(enum.Enum):
    HEAL =1
    DAMAGE = 2
    NONE = 3

class Item:
    def __init__(self, name, cost, is_usable=False, effect:Effect = Effect.NONE, effect_value = 0):
        self.name = name
        self.cost = cost
        self.quantity = 1
        self.is_usable = is_usable
        self.effect_type:Effect = effect
        self.effect_value = effect_value

    def cast(self,target: 'RpgHero'):
        if self.effect_type == Effect.HEAL:
            target.heal(self.effect_value)
        elif self.effect_type == Effect.DAMAGE:
            target.take_damage(self.effect_value)


    def __iadd__(self, quantity):
        self.quantity += quantity
        return self
    def __str__(self):
        return f"{self.name} x{self.quantity}"



class Inventory:
    def __init__(self):
        self.items = {}

    def add_item(self, item):
        if item.name in self.items:
            self.items[item.name] += 1
        else:
            self.items[item.name] = item

    def remove_item(self, item):
        if item.name in self.items:
            del self.items[item.name]

    def __getitem__(self, item_name: str):
        if item_name in self.items:
            return self.items[item_name]
        return None

    def __repr__(self):
        return f"<inventory with: {self.items}>"


class Spell(CanCast):
    def __init__(self, name, cost, caster: 'RpgHero', effect: callable):
        self.name = name
        self.cost = cost
        self.effect = effect
        self.caster = caster

    def cast(self, target: 'RpgHero'):
        if target is None or self.effect is None:
            return
        self.effect(target)


class Mana:
    def __init__(self, mana):
        self._mana = mana

    def consume(self, amount):
        self.mana = self.mana - amount

    @property
    def mana(self):
        return self._mana

    @mana.setter
    def mana(self, mana):
        if mana < 0:
            raise ValueError("Mana cannot be negative")
        self._mana = mana


class Health:
    def __init__(self, health):
        self._health = health

    def take_damage(self, damage):
        self.health -= damage

    def heal(self, amount):
        self.health += amount

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, health):
        if health < 0:
            self.health = 0
        else:
            self._health = health



class Goblin:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.xp_value = 100
        self.components = HoldComponent()
        self.components.add_component("health", Health(100))
        self.components.add_component("sword", Item("Sword", 25, True, effect=Effect.DAMAGE, effect_value=10))


    def get_health(self):
        return self.components["health"]

    def take_damage(self, damage):
        self.get_health().take_damage(damage)

    def is_alive(self):
        return self.get_health().health > 0

    @property
    def sword(self):
        return self.components["sword"]

    @property
    def health(self):
        return self.get_health().health

    def attacks(self, target: 'RpgHero' = None):
        if target is None:
            return
        self.sword.cast(target)


class RpgHero:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.xp = 0
        self.xp_to_next_level = 100
        self.components = HoldComponent()
        self.components.add_component("mana", Mana(100))
        self.components.add_component("health", Health(100))
        self.components.add_component("fireball", Spell("Fireball", 25, self, lambda target: target.take_damage(10)))
        self.components.add_component("magic_missile", Spell("Magic Missile", 5, self, lambda target: target.take_damage(1)))
        self.components.add_component("inventory", Inventory())

    def add_xp(self, xp):
        self.xp += xp
        if self.xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self):
        self.xp -= self.xp_to_next_level
        self.level += 1
        self.xp_to_next_level = 200 * (self.level * (self.level + 1)) // 2
        self.components["mana"].mana = 100 + self.level * 2
        self.components["health"].health = 100 + self.level * 5


    def get_mana(self):
        return self.components["mana"]

    def get_health(self):
        return self.components["health"]

    def take_damage(self, damage):
        self.get_health().take_damage(damage)

    def heal(self, amount):
        self.get_health().heal(amount)



    def get_spells(self, name: str = None):
        if isinstance(self.components.get_component(name), Spell) and self.components.get_component(name) is not None:
            return self.components.get_component(name)
        else:
            return None

    def cast_spell(self, spell, target: 'RpgHero' = None):
        if spell is None:
            print(f"{self.name} tried to cast a spell that doesn't exist!")
            return
        if target is None:
            print(f"{self.name} tried to cast {spell.name} but no target was provided.")
            return

        if self.get_mana().mana < spell.cost:
            print(f"{self.name} doesn't have enough mana to cast {spell.name}!")
            return

        self.get_mana().consume(spell.cost)
        spell.cast(target)

    @property
    def mana(self):
        return self.get_mana().mana

    @property
    def health(self):
        return self.get_health().health


def main():
    hero_bob = RpgHero("Bob", 1)
    hero = RpgHero("John", 1)
    goblin = Goblin("Goblin", 1)

    print("John casts Magic Missile at Bob")
    hero.cast_spell(hero.get_spells("magic_missile"), hero_bob)
    print("Bob's health is now: ", hero_bob.health)
    print("Bob casts Fireball at John")
    hero_bob.get_mana().consume(99)
    hero_bob.cast_spell(hero.get_spells("fireball"), hero)
    print("Bob's Mana is now: ", hero_bob.mana)
    print("John's health is now: ", hero.health)
    print("John Fireballs the goblin")
    hero.cast_spell(hero.get_spells("fireball"), goblin)
    print("goblin's health is now: ", goblin.health)
    print("goblin attacks Bob")
    goblin.attacks(hero_bob)
    print("Bob's health is now: ", hero_bob.health)
    hero.components["inventory"].add_item(Item("Sword", 10,True, Effect.DAMAGE, 10))
    print(hero.components["inventory"]["Sword"])
    print(hero.components["inventory"]["Pike"])
    hero.components["inventory"]["Sword"].cast(hero_bob)
    print("bobs health is" ,hero_bob.health)
    hero_bob.components["inventory"].add_item(Item("Sword", 10,True, Effect.DAMAGE, 100))
    print("Bob attacks goblin")
    hero_bob.components["inventory"]["Sword"].cast(goblin)
    print("goblin's health is now: ", goblin.health)

    if goblin.is_alive():
        print("Goblin is alive")
    else:
        print("Goblin is dead")
        hero_bob.add_xp(goblin.xp_value)

    print("Bob's xp is now: ", hero_bob.xp)
    print("Bob level is now: ", hero_bob.level)
    print("Bob's mana is now: ", hero_bob.mana)
    print("Bob's health is now: ", hero_bob.health)


if __name__ == '__main__':
    main()