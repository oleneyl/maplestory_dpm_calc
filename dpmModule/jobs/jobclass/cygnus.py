from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

def PhalanxChargeWrapper(vEhc, num1, num2):
    PhalanxCharge = core.DamageSkill("시그너스 팔랑크스", 780, 450 + 18*vEhc.getV(num1, num2), 40 + vEhc.getV(num1, num2), cooltime = 30 * 1000).isV(vEhc, num1, num2).wrap(core.DamageSkillWrapper)
    return PhalanxCharge

# 인피니티와 유사한 매커니즘이므로 별도의 클래스 작성 필요
#세부값 확인해서 변경필요
#MP 500 소비, 45초 동안 데미지 25% 증가, 일정 시간마다 HP 4%씩 회복 및 데미지 3% 추가 증가, 시그너스의 축복으로 증가하는 데미지는 합 적용이며 최대 90%까지 증가
#MP 500 소비, 45초 동안 데미지 25% 증가 및 최대 HP의 일정 비율로 피해를 입히는 공격을 포함한 피격 데미지 5% 감소, 일정 시간마다 HP 7%씩 회복 및 데미지 5% 추가 증가, 시그너스의 축복으로 증가하는 데미지는 합 적용이며 최대 120%까지 증가

def CygnusBlessWrapper(vEhc, num1, num2, LEVEL):
    if LEVEL < 245:
        CygnusBless = core.BuffSkill("여제 시그너스의 축복", 450, (30+vEhc.getV(num1, num2)//2)*1000, pdamage = (30+vEhc.getV(num1, num2)//5) *1.2 + 20, cooltime = 240*1000).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    else:
        CygnusBless = core.BuffSkill("초월자 시그너스의 축복", 450, (30+vEhc.getV(num1, num2)//2)*1000, pdamage = (30+vEhc.getV(num1, num2)//5) *1.2 + 20, cooltime = 240*1000).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    return CygnusBless