from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

# 보마 = 20
# 메르 = 0
# 패파 = 20
# 신궁 = 20+6.6
# 와헌 = 20
# 윈브 = 55
# bonus = 직업별 보정 수치. 정확한 원리는 모름.
class CriticalReinforceWrapper(core.BuffSkillWrapper):
    def __init__(self, vEhc, character : ck.AbstractCharacter, num1, num2, bonus):
        skill = core.BuffSkill("크리티컬 리인포스", 780, 30 * 1000, cooltime = 120 * 1000).isV(vEhc, num1, num2)
        super(CriticalReinforceWrapper, self).__init__(skill)
        self.char = character
        self.inhancer = (20 + vEhc.getV(num1, num2))*0.01
        self.bonus = bonus
        
    def get_modifier(self):
        if self.onoff:
            return core.CharacterModifier(crit_damage = self.inhancer * max(0,self.char.get_modifier().crit+self.bonus))
        else:
            return self.disabledModifier