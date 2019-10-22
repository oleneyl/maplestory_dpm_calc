from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

def PhalanxChargeWrapper(vEhc, num1, num2):
    PhalanxCharge = core.DamageSkill("시그너스 팔랑크스", 780, 450 + 18*vEhc.getV(num1, num2), 40 + vEhc.getV(num1, num2), cooltime = 30 * 1000).isV(vEhc, num1, num2).wrap(core.DamageSkillWrapper)
    return PhalanxCharge

#세부값 확인해서 변경필요
def CygnusBlessWrapper(vEhc, num1, num2, LEVEL)
    if LEVEL < 245:
        CygnusBless = core.BuffSkill("여제 시그너스의 축복", 450, (30+vEhc.getV(num1, num2)//2)*1000, pdamage = (30+vEhc.getV(num1, num2)//5) *1.2 + 20, cooltime = 240*1000).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    else:
        CygnusBless = core.BuffSkill("초월자 시그너스의 축복", 450, (30+vEhc.getV(num1, num2)//2)*1000, pdamage = (30+vEhc.getV(num1, num2)//5) *1.2 + 20, cooltime = 240*1000).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    return CygnusBless