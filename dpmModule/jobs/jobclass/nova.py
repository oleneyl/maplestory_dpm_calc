from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

#TODO: 판테온 추가 4000%[(스킬 레벨*80+2000)%] 데미지로 10번 공격, 쿨타임 1200초

def NovaGoddessBlessWrapper(vEhc, num1, num2):
    #TODO: (40+0.5*스킬레벨)%, 소수점 아래로 버림. 확률로 재사용 대기시간 미적용, 최대 5회까지만 미적용 가능
    NovaGoddessBless = core.BuffSkill("그란디스 여신의 축복(노바)", 450, 40*1000, pdamage = 5+vEhc.getV(num1, num2), cooltime = 240*1000).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    return NovaGoddessBless