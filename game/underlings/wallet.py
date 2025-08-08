from game.underlings.events import Events


class Wallet:
    def __init__(self, initial=0):
        self._balance = max(0, int(initial))

    @property
    def balance(self) -> int:
        return self._balance

    def can_afford(self, amount: int) -> bool:
        return amount >= 0 and self._balance >= amount

    def add(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        self._balance += amount
        Events.trigger_event(
            "gold_changed", owner=self, delta=amount, new_balance=self._balance
        )

    def spend(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        if not self.can_afford(amount):
            raise ValueError("Not enough gold")
        self._balance -= amount
        Events.trigger_event(
            "gold_changed", owner=self, delta=-amount, new_balance=self._balance
        )
