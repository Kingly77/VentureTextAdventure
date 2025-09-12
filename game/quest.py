import uuid

from character.hero import RpgHero
from game.underlings.events import Events


class Objective:
    def __init__(self, type_str: str, target: str, value: int):
        self.type = type_str
        self.target = target
        self.value = int(value)

    def __repr__(self):
        return f"Objective(type='{self.type}', target='{self.target}', value={self.value})"


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

    def handle_event(self, event_name: str, **kwargs) -> None:
        """
        Update quest progress based on emitted events.
        This is additive and does not change existing item handling behavior.
        Supported:
          - item_collected(hero, item)
          - enemy_killed(hero, enemy_type, count=1)
          - location_entered(hero, location_name)
        """
        # Collect objective (matches existing flow)
        if self.objective.type == "collect" and event_name == "item_collected":
            item = kwargs.get("item")
            if item and getattr(item, "name", None) == self.objective.target:
                qty = getattr(item, "quantity", 1) or 1
                self.progress = min(
                    self.objective.value, self.progress + int(qty)
                )
                return

        # Kill objective
        if self.objective.type == "kill" and event_name == "enemy_killed":
            if kwargs.get("enemy_type") == self.objective.target:
                self.progress = min(
                    self.objective.value, self.progress + max(1, int(kwargs.get("count", 1)))
                )
                return

        # Visit objective
        if self.objective.type == "visit" and event_name == "location_entered":
            if kwargs.get("location_name") == self.objective.target:
                # Mark as complete by reaching required value
                self.progress = max(self.progress, self.objective.value)
                return

    def check_item(self, item):
        return (
            self.objective.type == "collect"
            and item is not None
            and getattr(item, "name", None) == self.objective.target
        )

    def check_progress(self):
        return self.progress >= self.objective.value

    @property
    def is_complete(self) -> bool:
        return self.check_progress()

    @property
    def progress_remaining(self) -> int:
        return max(0, self.objective.value - self.progress)

    @property
    def progress_fraction(self) -> float:
        if self.objective.value <= 0:
            return 1.0
        return min(1.0, self.progress / float(self.objective.value))

    def __str__(self):
        return f"({self.id}) {self.name}: {self.description}"

    def __repr__(self):
        return f"Quest('{self.id}', '{self.name}', '{self.description}', reward={self.reward})"

    def complete(self, who: RpgHero):
        # Collect-type quests consume items when completing
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
                    # Trigger completion event for observers
                    Events.trigger_event(self.event_name, who)
                    return True
            return False

        # For non-collect objectives, completing depends purely on tracked progress
        if self.check_progress():
            who.add_xp(self.reward)
            print(f"Quest complete: {self.description}")
            print(
                f"You earned {self.reward} experience points. XP remaining until next level: {who.xp_to_next_level}"
            )
            Events.trigger_event(self.event_name, who)
            return True

        return False

    # Simple serialization helpers
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "reward": self.reward,
            "objective": {
                "type": self.objective.type,
                "target": self.objective.target,
                "value": self.objective.value,
            },
            "progress": self.progress,
        }

    @staticmethod
    def from_dict(data: dict) -> "Quest":
        obj = Objective(
            data["objective"]["type"], data["objective"]["target"], data["objective"]["value"]
        )
        q = Quest(data["name"], data["description"], data["reward"], obj)
        # Preserve id/progress if provided
        if "id" in data:
            q.id = data["id"]
        q.progress = int(data.get("progress", 0))
        q.progress = min(q.progress, q.objective.value)
        return q
