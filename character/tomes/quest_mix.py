from components.quest_log import QuestLog


class QuestMix:
    """Mixin exposing quest log property backed by QuestLog component."""

    @property
    def quest_log(self) -> QuestLog:
        return self.components["quests"]
