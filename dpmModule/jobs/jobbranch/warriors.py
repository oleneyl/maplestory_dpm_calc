from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

# 오라웨폰을 소환수로 변경하는 코드 (발동 딜레이 추가바람)

def AuraWeaponWrapper(vEhc, num1, num2):
    AuraWeapon = core.SummonSkill("오라웨폰", 0, 6000, (500 + 20 * vEhc.getV(num1, num2)), 6, (80 +2*vEhc.getV(num1, num2)) * 1000, cooltime = 180 * 1000, modifier = core.CharacterModifier(armor_ignore = 15, pdamage_indep = (vEhc.getV(num1, num2) // 5))).isV(vEhc, num1, num2).wrap(core.SummonSkillWrapper)
    return AuraWeapon