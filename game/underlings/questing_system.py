from character.hero import RpgHero
from game.underlings.events import Events


class QuestingSystem:
    def __init__(self):
        Events.add_event("item_collected", self.on_item_collected)

    # progress handling
    def on_item_collected(self, val_hero: "RpgHero", item):
        q_id = val_hero.quest_log.check_quests(item)
        if q_id:
            quest = val_hero.quest_log.active_quests[q_id]
            quest.progress += 1
            if quest.check_progress():
                results = Events.trigger_event(quest.event_name, val_hero)
                # Print the first result if available, otherwise print a default completion message
                if results and len(results) > 0 and results[0]:
                    print(results[0])
                else:
                    print(f"{val_hero.name} completed the quest: {quest.name}")
            else:
                print(f"{val_hero.name} made progress in {quest.name}")
        # Always return None to indicate side-effect (printing) only
        return None
