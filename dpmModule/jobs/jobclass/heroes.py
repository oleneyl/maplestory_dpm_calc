from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial


class FridWrapper(core.BuffSkillWrapper):
	# num1, num2
    def __init__(self, vEhc, num1, num2, invariant = True):
        super(FridWrapper, self).__init__(skill = core.BuffSkill("프리드의 가호(더미)", num1, num2).isV(vEhc, num1, num2))
        self.vlevel = vEhc.getV(num1, num2)
        vlevel = self.vlevel
        self.skillList = [core.BuffSkill("프리드의 가호(0스택)(더미)", 0, 30 * 1000),
                    core.BuffSkill("프리드의 가호(1스택)", 0, 30 * 1000),
                    core.BuffSkill("프리드의 가호(2스택)", 0, 30 * 1000),
                    core.BuffSkill("프리드의 가호(3스택)", 0, 30 * 1000, stat_main = vlevel+25, stat_sub = vlevel+25),
                    core.BuffSkill("프리드의 가호(4스택)", 0, 30 * 1000, stat_main = vlevel+25, stat_sub = vlevel+25, att = (10 + 0.5*vlevel)),
                    core.BuffSkill("프리드의 가호(5스택)", 0, 30 * 1000, stat_main = vlevel+25, stat_sub = vlevel+25, att = (10 + 0.5*vlevel), boss_pdamage = (10 + 0.5 * vlevel)),
                    core.BuffSkill("프리드의 가호(6스택)", 0, 30 * 1000, cooltime = 240 * 1000, stat_main = vlevel+25, stat_sub = vlevel+25, att = (10 + 0.5*vlevel), boss_pdamage = (10 + 0.5 * vlevel))]
        self.state = 0
        # 이 변수가 무슨 뜻인지 확인필요. 직업별 스크립트 중 에반에만 존재.
        self.modifierInvariantFlag = invariant

    def _use(self, skill_modifier) -> core.ResultObject:
        self.onoff = True
        self.state += 1
        if self.state > 6:
            self.state -= 6        
        self.skill = self.skillList[self.state]
        self.timeLeft = self.skill.remain * (1 + 0.01*skill_modifier.buff_rem * self.skill.rem)
        self.cooltimeLeft = self.skill.cooltime * (1 - 0.01*skill_modifier.pcooltime_reduce* self.skill.red)
        self.onoff = True
        if self.cooltimeLeft > 0:
            self.available = False
        delay = self.skill.delay
        mdf = self.get_modifier()
        return core.ResultObject(delay, mdf, 0, 0, sname = self._id, spec = 'buff', kwargs = {"remain" : self.skill.remain * (1+0.01*skill_modifier.buff_rem*self.skill.rem)})
        #return delay, mdf, 0, self.cascade





