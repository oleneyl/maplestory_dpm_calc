from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

def NovaGoddessBlessWrapper(vEhc, num1, num2):
    #TODO: (40+0.5*스킬레벨)%, 소수점 아래로 버림. 확률로 재사용 대기시간 미적용, 최대 5회까지만 미적용 가능
    NovaGoddessBless = core.BuffSkill("그란디스 여신의 축복(노바)", 450, 40*1000, pdamage = 5+vEhc.getV(num1, num2), cooltime = 240*1000).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    return NovaGoddessBless

def PantheonWrapper(vEhc, num1, num2):
    Pantheon = core.DamageSkill("판테온", 510, 2000 + 80 * vEhc.getV(num1, num2), 10, cooltime = 1200*1000).wrap(core.DamageSkillWrapper)
    return Pantheon