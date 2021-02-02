from enum import Enum
from typing import Union
from ...kernel import core


class MagicianSkills(Enum):
    ManaOverload = 'Mana Overload | 오버로드 마나'  # Taken from https://maplestory.fandom.com/wiki/Mana_Overload


class OverloadManaBuilder:
    def __init__(self, vEhc, num1, num2) -> None:
        self.skill = (
            core.BuffSkill(MagicianSkills.ManaOverload.value, 0, 99999 * 10000)  # Mana Overlord
            .isV(vEhc, num1, num2)
            .wrap(core.BuffSkillWrapper)
        )
        self.pdamage_indep = 8 + vEhc.getV(num1, num2) // 10

    def add_skill(self, skill: Union[core.DamageSkillWrapper, core.SummonSkillWrapper]):
        skill.add_runtime_modifier(
            self.skill,
            lambda sk: core.CharacterModifier(
                pdamage_indep=sk.is_active() * self.pdamage_indep
            ),
        )

    def get_buff(self):
        return self.skill
