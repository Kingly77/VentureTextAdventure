from components.core_components import Exp


class XpMix:
    """Mixin exposing XP-related properties backed by the Exp component."""

    @property
    def xp_component(self) -> Exp:
        return self.components["xp"]

    @property
    def xp_to_next_level(self):
        return self.xp_component.next_lvl

    @xp_to_next_level.setter
    def xp_to_next_level(self, value):
        self.xp_component.next_lvl = value

    @property
    def xp(self) -> int:
        return self.components["xp"].exp

    @xp.setter
    def xp(self, value: int):
        self.components["xp"].exp = value
