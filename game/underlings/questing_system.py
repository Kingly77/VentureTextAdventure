from game.underlings.events import Events


class QuestingSystem:
    def __init__(self):
        Events.add_event("item_collected", self.on_item_collected)
        # New: hook additional events (optional, safe if unused)
        Events.add_event("enemy_killed", self.on_enemy_killed)
        Events.add_event("location_entered", self.on_location_entered)

    def _advance_quests(self, val_hero: "RpgHero", event_name: str, **payload):
        """
        Shared progress/completion handler for any quest-affecting event.
        Preserves existing print/trigger behavior.
        """
        progressed_any = False
        for quest in list(val_hero.quest_log.active_quests.values()):
            before = quest.progress
            quest.handle_event(event_name, **payload)
            if quest.progress != before:
                progressed_any = True
                if quest.check_progress():
                    results = Events.trigger_event(quest.event_name, val_hero)
                    if results and len(results) > 0 and results[0]:
                        print(results[0])
                    else:
                        print(f"{val_hero.name} completed the quest: {quest.name}")
                else:
                    print(f"{val_hero.name} made progress in {quest.name}")
        # Always return None to indicate side effect (printing) only
        return None

    # Existing flow now delegates to the shared handler
    def on_item_collected(self, val_hero: "RpgHero", item):
        # Keep legacy path working while using unified progress logic
        return self._advance_quests(val_hero, "item_collected", item=item)

    # New handlers (optional to emit in your game)
    def on_enemy_killed(self, val_hero: "RpgHero", enemy_type: str, count: int = 1):
        return self._advance_quests(
            val_hero, "enemy_killed", enemy_type=enemy_type, count=count
        )

    def on_location_entered(self, val_hero: "RpgHero", location_name: str):
        return self._advance_quests(
            val_hero, "location_entered", location_name=location_name
        )
