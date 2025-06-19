import uuid

from character.hero import RpgHero


class Objective:
    def __init__(self, type:str, target:str, value:int):
        self.type = type
        self.target = target
        self.value = value


class Quest:
    def __init__(self, name, description, reward:int ,who = None, objective:Objective = None):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.description = description
        self.reward = reward
        self.objective = objective

    def __str__(self):
        return f"({self.id}) {self.name}: {self.description}"

    def __repr__(self):
        return f"Quest('{self.id}', '{self.name}', '{self.description}', reward={self.reward})"

    def complete(self,who:RpgHero):
        if self.objective.type == "collect":
            if who.inventory.has_component(self.objective.target):
                if who.inventory[self.objective.target].quantity >= self.objective.value:
                    who.inventory.remove_item(self.objective.target, self.objective.value)
                    who.add_xp(self.reward)
                    print(f"Quest complete: {self.description}")
                    print(f"You earned {self.reward} experience points. and have {who.xp} Remaining experience points")
                    return True

        return False