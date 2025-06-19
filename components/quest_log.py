from typing import TYPE_CHECKING


class QuestLog:
    def __init__(self):
        self.active_quests = {}
        self.completed_quests = []

    def __str__(self):
        return f"Active quests: {self.active_quests}\nCompleted quests: {self.completed_quests}"

    def add_quest(self, title:str, quest:'Quest'):
        self.active_quests[title] = quest

    def complete_quest(self, quest):
        if quest in self.active_quests.keys():
            q = self.active_quests[quest]
            if q.complete():
                self.completed_quests.append(q.name)
                del self.active_quests[quest]
            else:
                print("Quest not completed.")
