from __future__ import annotations
from character.enemy import Goblin, Troll
from character.hero import RpgHero
from components.core_components import Effect
from components.inventory import ItemNotFoundError, InsufficientQuantityError
from game.items import Item, UseItemError
from game.room import Room
from game.util import handle_inventory_operation, handle_spell_cast, handle_item_use
from game.room_effects import DarkCaveLightingEffect

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
                         "A peaceful clearing in a dense forest. Sunlight filters through the leaves." , exits={})
    dark_cave = Room("Dark Cave Entrance", "The air grows cold as you stand at the mouth of a dark, damp cave.",exits={})

    starting_room.exits_to["north"] = dark_cave
    dark_cave.exits_to["south"] = starting_room

    # Add items to rooms
    starting_room.add_item(Item("Health Potion", 10, True, Effect.HEAL, 20))
    starting_room.add_item(Item("Shiny Coin", 1, False))
    starting_room.add_item(Item("Wooden Shield", 50, False))

    # Add a torch to the dark cave
    dark_cave.add_item(Item("Torch", 5, True))
    dark_cave.add_item(Item("Goblin Ear", 1, False))
    dark_cave.add_effect(DarkCaveLightingEffect(dark_cave))

    if not dark_cave in starting_room.exits_to.values():
        print("Error: Dark cave not added to starting room.")
        return

    print(f"\nOur heroes looking at a map seeing the {dark_cave.name} to the north of the forest, they decided to venture towards the {dark_cave.name}")

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

    # Demonstrate using items on self vs. in room
    print("\nChapter 6.5: The Healing and the Light")

    # Give Bob a health potion and demonstrate using it on self
    hero_bob.inventory.add_item(Item("Health Potion", 10, True, Effect.HEAL, 20))
    print(f"{hero_bob.name} found a Health Potion and decides to use it on himself.")
    if handle_item_use(hero_bob, "Health Potion"):
        print(f"{hero_bob.name}'s wounds begin to close, his health rising to {hero_bob.health}!")

    # Have John use his torch in the dark cave
    print(f"\nReturning to the {dark_cave.name}, {hero_john.name} decides to light his torch.")
    if handle_item_use(hero_john, "Torch", room=dark_cave):
        print(f"The {dark_cave.name} is now illuminated! They can see:")
        print(dark_cave.get_description())

    # Try to use the torch in the forest (should fail)
    print(f"\nBack in the {starting_room.name}, {hero_john.name} tries to use the torch again.")
    if not handle_item_use(hero_john, "Torch", room=starting_room):
        print(f"The bright sunlight makes the torch unnecessary here.")

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
    # First, add an item to remove
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
