from typing import Union
from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

class OverloadManaBuilder():
    def __init__(self, vEhc, num1, num2) -> None:
        self.skill = core.BuffSkill("오버로드 마나", 0, 99999 * 10000).isV(vEhc,num1, num2).wrap(core.BuffSkillWrapper)
        self.final_damage = 8 + vEhc.getV(num1, num2) // 10

    def add_skill(self, skill: Union[core.DamageSkillWrapper, core.SummonSkillWrapper]):
        skill.add_runtime_modifier(self.skill, lambda sk: core.CharacterModifier(final_damage = sk.is_active() * self.final_damage))

    def get_buff(self):
        return self.skill
