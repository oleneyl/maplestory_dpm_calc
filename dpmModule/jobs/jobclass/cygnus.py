from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

def PhalanxChargeWrapper(vEhc, num1, num2):
    PhalanxCharge = core.DamageSkill("시그너스 팔랑크스", 780, 450 + 18*vEhc.getV(num1, num2), 40 + vEhc.getV(num1, num2), cooltime = 30 * 1000).isV(vEhc, num1, num2).wrap(core.DamageSkillWrapper)
    return PhalanxCharge