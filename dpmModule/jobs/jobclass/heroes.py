from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

class FridWrapper(core.BuffSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        super(FridWrapper, self).__init__(core.BuffSkill("프리드의 가호(더미)", 810, 30*1000, red=True).isV(vEhc, num1, num2))
        vlevel = vEhc.getV(num1, num2)
        self.modifierList = [
            core.CharacterModifier(),
            core.CharacterModifier(),
            core.CharacterModifier(),
            core.CharacterModifier(stat_main = vlevel+25, stat_sub = vlevel+25),
            core.CharacterModifier(stat_main = vlevel+25, stat_sub = vlevel+25, att = (10 + vlevel // 2)),
            core.CharacterModifier(stat_main = vlevel+25, stat_sub = vlevel+25, att = (10 + vlevel // 2), boss_pdamage = (10 + vlevel // 2)),
            core.CharacterModifier(stat_main = vlevel+25, stat_sub = vlevel+25, att = (10 + vlevel // 2), boss_pdamage = (10 + vlevel // 2))
        ]
        self.state = 0
        self.modifierInvariantFlag = False
        self.uniqueFlag = False

    def get_cooltime(self):
        if self.state == 6:
            return 240 * 1000
        else:
            return 25 * 1000

    def _use(self, skill_modifier) -> core.ResultObject:
        result = super(FridWrapper, self)._use(skill_modifier)
        self.state += 1
        if self.state > 6:
            self.state = 0

        return result

    def get_modifier(self):
        return self.modifierList[self.state]