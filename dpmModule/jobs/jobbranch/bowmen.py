from ...kernel import core
from ...character import characterKernel as ck


# 보마 = 22.5 (샤프 아이즈 + 샤프 아이즈-크리티컬 레이트)
# 메르 = 10 (쓸만한 샤프 아이즈)
# 패파 = 20 (샤프 아이즈)
# 신궁 = 20+20 (샤프 아이즈 + 불스아이)
# 와헌 = 20 (샤프 아이즈)
# 윈브 = 55 (샤프 아이즈, 실프스 에이드, 알바트로스 맥시멈)
# bonus = 직업별 보정 수치. self.char.get_modifier()가 패시브만 적용된 수치를 반환하므로, 버프 스킬로 오르는 크확을 따로 표시해줘야 한다.
class CriticalReinforceWrapper(core.BuffSkillWrapper):
    def __init__(self, vEhc, character: ck.AbstractCharacter, num1, num2, bonus):
        skill = core.BuffSkill(
            "크리티컬 리인포스",
            delay=600,
            remain=30 * 1000,
            cooltime=120 * 1000,
            red=True,
        ).isV(vEhc, num1, num2)
        super(CriticalReinforceWrapper, self).__init__(skill)
        self.char = character
        self.inhancer = (20 + vEhc.getV(num1, num2)) * 0.01
        self.bonus = bonus

    def get_modifier(self):
        if self.is_active():
            return core.CharacterModifier(
                crit_damage=self.inhancer
                * max(0, self.char.get_modifier().crit + self.bonus)
            )
        else:
            return self.disabledModifier


class GuidedArrowWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2, modifier=core.CharacterModifier()):
        skill = core.SummonSkill(
            "가이디드 애로우",
            summondelay=0,
            delay=510,
            damage=400 + 16 * vEhc.getV(num1, num2),
            hit=1,
            remain=9999999,
            red=True,
            modifier=modifier,
        ).isV(vEhc, num1, num2)
        super(GuidedArrowWrapper, self).__init__(skill)
