import uuid

from character.hero import RpgHero
from game.underlings.events import Events


class Objective:
    def __init__(self, type_str: str, target: str, value: int):
        self.type = type_str
        self.target = target
        self.value = value


class Quest:
    def __init__(
        self, name, description: str, reward: int, objective: Objective = None
    ):
        self.id = str(uuid.uuid4())[:8]
        self.name: str = name
        self.description = description
        self.reward = reward
        self.objective = objective
        self.tentative_complete = False
        self.event_name = f"complete_{self.name.replace(' ','_')}"
        self.progress = 0

        if objective is None:
            raise ValueError("Objective must be provided.")
        if objective.value <= 0:
            raise ValueError("Objective value must be positive.")

        def event_handler(val_hero, *_):
            self.tentative_complete = True
            return f"{val_hero.name} completed the quest: {self.name}"

        Events.add_event(self.event_name, event_handler, True)

    def check_item(self, item):
        return self.objective.type == "collect" and item.name == self.objective.target

    def check_progress(self):
        return self.progress >= self.objective.value

    def __str__(self):
        return f"({self.id}) {self.name}: {self.description}"

    def __repr__(self):
        return f"Quest('{self.id}', '{self.name}', '{self.description}', reward={self.reward})"

    def complete(self, who: RpgHero):
        if self.objective.type == "collect":
            if who.inventory.has_component(self.objective.target):
                if (
                    who.inventory[self.objective.target].quantity
                    >= self.objective.value
                ):
                    who.inventory.remove_item(
                        self.objective.target, self.objective.value
                    )
                    who.add_xp(self.reward)
                    print(f"Quest complete: {self.description}")
                    print(
                        f"You earned {self.reward} experience points. XP remaining until next level: {who.xp_to_next_level}"
                    )

                    return True

        return False
