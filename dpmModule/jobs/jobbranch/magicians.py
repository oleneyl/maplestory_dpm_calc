from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

def OverloadManaWrapper(vEhc, num1, num2):
    OverloadMana = core.BuffSkill("오버로드 마나", 0, 99999 * 10000, pdamage_indep = 8+int(0.1*vEhc.getV(num1, num2))).isV(vEhc,num1, num2).wrap(core.BuffSkillWrapper)
    return OverloadMana