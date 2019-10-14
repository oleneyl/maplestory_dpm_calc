from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial
from ...status.ability import Ability_tool
from .. import globalSkill

class FridWrapper(core.BuffSkillWrapper):
	# num1, num2
    def __init__(self, vEhc, num1, num2):
        super(FridWrapper, self).__init__(skill = core.BuffSkill("프리드의 가호 더미", 0,0).isV(vEhc,0,0))
        self.vlevel = vEhc.getV(0,0)
        vlevel = vEhc.getV(0,0)
        self.skillList = [core.BuffSkill("프리드의 가호 0스택(더미)", 0, 30 * 1000),
                    core.BuffSkill("프리드의 가호 1스택", 0, 30 * 1000),
                    core.BuffSkill("프리드의 가호 2스택", 0, 30 * 1000),
                    core.BuffSkill("프리드의 가호 3스택", 0, 30 * 1000, stat_main = vlevel+25, stat_sub = vlevel+25),
                    core.BuffSkill("프리드의 가호 4스택", 0, 30 * 1000, stat_main = vlevel+25, stat_sub = vlevel+25, att = (10 + 0.5*vlevel)),
                    core.BuffSkill("프리드의 가호 5스택", 0, 30 * 1000, stat_main = vlevel+25, stat_sub = vlevel+25, att = (10 + 0.5*vlevel), boss_pdamage = (10 + 0.5 * vlevel)),
                    core.BuffSkill("프리드의 가호 6스택", 0, 30 * 1000, cooltime = 240 * 1000, stat_main = vlevel+25, stat_sub = vlevel+25, att = (10 + 0.5*vlevel), boss_pdamage = (10 + 0.5 * vlevel))]
        self.state = 0
        self.modifierInvariantFlag = False

    def _use(self, rem = 0, red = 0) -> core.ResultObject:
        self.onoff = True
        self.state += 1
        if self.state > 6:
            self.state -= 6        
        self.skill = self.skillList[self.state]
        self.timeLeft = self.skill.remain * (1 + 0.01*rem * self.skill.rem)
        self.cooltimeLeft = self.skill.cooltime * (1 - 0.01*red* self.skill.red)
        self.onoff = True
        if self.cooltimeLeft > 0:
            self.available = False
        delay = self.skill.delay
        mdf = self.get_modifier()
        return core.ResultObject(delay, mdf, 0, sname = self._id, spec = 'buff', kwargs = {"remain" : self.skill.remain * (1+0.01*rem*self.skill.rem)})
        #return delay, mdf, 0, self.cascade