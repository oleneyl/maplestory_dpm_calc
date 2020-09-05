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

    def _use(self, skill_modifier) -> core.ResultObject:
        self.state += 1
        if self.state > 6:
            self.state = 0
        
        self.timeLeft = self.skill.remain * (1 + 0.01*skill_modifier.buff_rem * self.skill.rem)
        if self.state == 0:
            self.cooltimeLeft = self.calculate_cooltime(240*1000, skill_modifier)
        else:
            self.cooltimeLeft = self.calculate_cooltime(25*1000, skill_modifier)
        self.onoff = True
        if self.cooltimeLeft > 0:
            self.available = False
        delay = self.get_delay()
        return core.ResultObject(delay, core.CharacterModifier(), 0, 0, sname = self.skill.name, spec = self.skill.spec, kwargs = {"remain" : self.skill.remain * (1+0.01*skill_modifier.buff_rem*self.skill.rem)})

    def get_modifier(self):
        return self.modifierList[self.state]