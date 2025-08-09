from components.wallet import Wallet


class WalletMix:
    """Mixin exposing wallet and gold-related helpers backed by Wallet component."""

    @property
    def wallet(self) -> Wallet:
        if not self.components.has_component("wallet"):
            raise ValueError("Hero has no wallet. WHY?")
        return self.components["wallet"]

    @property
    def gold(self) -> int:
        return self.wallet.balance

    @gold.setter
    def gold(self, value: int):
        self.wallet._balance = value

    def add_gold(self, amount: int):
        self.wallet.add(amount)

    def spend_gold(self, amount: int):
        self.wallet.spend(amount)