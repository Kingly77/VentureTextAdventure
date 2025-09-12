from __future__ import annotations

from typing import Optional, Callable

from character.hero import RpgHero
from game.effects.room_effect_base import RoomDiscEffect
from game.items import Item
from game.npc import NPC
from game.quest import Quest
from game.room import Room


class NPCDialogEffect(RoomDiscEffect):
    """
    A generic NPC dialog effect that can grant and turn in a provided quest.

    Usage:
      - Adds an NPC presence to the room description.
      - Handles the command: talk [npc name|npc]
      - Provides a dialog to accept or turn-in the provided quest.
    """

    def __init__(
        self,
        room: "Room",
        npc_name: str = "Quest Giver",
        npc_description: str = "leans on a walking stick, ready to chat.",
        quest: Optional["Quest"] = None,
        quest_factory: Optional[Callable[[], Quest]] = None,
    ):
        """
        Create an NPC dialog.

        Parameters:
        - npc_name: The display name of the NPC.
        - quest: A Quest instance to be offered by this NPC. If provided, it will be used.
        - quest_factory: A callable that returns a new Quest instance when called. Used if `quest` is not given.

        Backward compatibility: if neither quest nor quest_factory is provided,
        a default "Goblin Ear" quest will be created when needed (matching previous behavior).
        """
        super().__init__(room)
        self.npc_name = npc_name
        self._quest: Optional[Quest] = quest
        self._quest_factory = quest_factory
        room.add_npc(NPC(npc_name, npc_description))

    def _ensure_quest(self) -> Quest:
        # Lazy import to avoid circular dependencies
        if self._quest is not None:
            return self._quest
        if self._quest_factory is not None:
            self._quest = self._quest_factory()
            return self._quest
        # Fallback to legacy default quest
        from game.quest import Quest, Objective

        self._quest = Quest(
            "goblin ear",
            "Collect the goblin ear to defeat the goblin foe.",
            100,
            objective=Objective("collect", "goblin ear", 1),
        )
        return self._quest

    def get_modified_description(self, base_description: str) -> str:
        return base_description

    def handle_interaction(
        self,
        verb: str,
        target_name: Optional[str],
        val_hero: "RpgHero",
        item: Optional["Item"],
        room: "Room",
    ) -> Optional[str]:
        vb = (verb or "").strip().lower()
        tgt = (target_name or "").strip().lower()
        if vb != "talk":
            return None

        # Only handle if target is empty or matches npc
        if tgt and tgt not in {self.npc_name.lower(), "npc", "villager", "quest giver"}:
            return None

        quest = self._ensure_quest()

        print(f"\nYou approach {self.npc_name}.")
        while True:
            print("\nDialogue:")
            print(f"  1) Get the quest: '{quest.name.title()}'")
            print(f"  2) Turn in the '{quest.name.title()}' quest")
            print("  3) Leave")
            choice = input("Choose 1, 2, or 3: ").strip()

            if choice == "1":
                # Check if this quest is already active
                existing = None
                # Prefer matching by id if present
                if quest.id in val_hero.quest_log.active_quests:
                    existing = val_hero.quest_log.active_quests[quest.id]
                else:
                    for q in val_hero.quest_log.active_quests.values():
                        if q.name.lower() == quest.name.lower():
                            existing = q
                            break
                if existing:
                    print(f"You already have the {quest.name.title()} quest.")
                else:
                    # If a factory is provided we may want a fresh quest instance for the hero
                    if self._quest_factory is not None:
                        quest = self._quest_factory()
                        self._quest = quest
                    val_hero.quest_log.add_quest(quest.id, quest)
                    print(
                        f"Quest accepted! ({quest.id}) {quest.name} - {quest.description}"
                    )
            elif choice == "2":
                # Find the quest if active
                target_id = None
                if quest.id in val_hero.quest_log.active_quests:
                    target_id = quest.id
                else:
                    for qid, q in val_hero.quest_log.active_quests.items():
                        if q.name.lower() == quest.name.lower():
                            target_id = qid
                            break
                if not target_id:
                    print(f"You do not have the {quest.name.title()} quest active.")
                else:
                    val_hero.quest_log.complete_quest(target_id, val_hero)
            elif choice == "3":
                print("You end the conversation.")
                return "You step away from the conversation."
            else:
                print("Please choose 1, 2, or 3.")

        # Unreachable, but for signature completeness
        # return None
