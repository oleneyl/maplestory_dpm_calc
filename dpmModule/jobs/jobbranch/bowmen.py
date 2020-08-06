from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

# 보마 = 20 (샤프 아이즈)
# 메르 = 10 (쓸만한 샤프 아이즈)
# 패파 = 20 (샤프 아이즈)
# 신궁 = 20+20 (샤프 아이즈 + 불스아이)
# 와헌 = 20 (샤프 아이즈)
# 윈브 = 55 (샤프 아이즈, 실프스 에이드, 알바트로스 맥시멈)
# bonus = 직업별 보정 수치. self.char.get_modifier()가 패시브만 적용된 수치를 반환하므로, 버프 스킬로 오르는 크확을 따로 표시해줘야 한다.
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

def GuidedArrowWrapper(vEhc, num1, num2):
    GuidedArrow = core.SummonSkill("가이디드 애로우", 720, 330, 400+16*vEhc.getV(num1, num2), 1, 30 * 1000, cooltime = 60 * 1000).isV(vEhc,num1, num2).wrap(core.SummonSkillWrapper)
    return GuidedArrow