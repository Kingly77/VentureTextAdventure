from typing import Optional

from game.items import Item


class Reward:
    def __init__(self):
        self.reward: Optional[Item] = None
