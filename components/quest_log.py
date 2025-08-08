from typing import TYPE_CHECKING


class QuestLog:
    def __init__(self):
        self.active_quests = {}
        self.completed_quests = []

    def __str__(self):
        return f"Active quests: {self.active_quests}\nCompleted quests: {self.completed_quests}"

    def add_quest(self, title: str, quest: "Quest"):
        self.active_quests[title] = quest

    def check_quests(self, item):
        for quest in self.active_quests.values():
            if quest.check_item(item):
                return quest.id
        return None

    def complete_quest(self, quest, who: "RpgHero"):
        if quest in self.active_quests.keys():
            q = self.active_quests[quest]
            if q.complete(who):
                self.completed_quests.append(q.name)
                del self.active_quests[quest]
            else:
                print("Quest not completed.")
