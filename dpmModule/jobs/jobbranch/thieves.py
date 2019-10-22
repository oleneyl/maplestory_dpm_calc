from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

# 직업별 스크립트 완전히 파악되면 통합 필요
def ReadyToDieWrapper(vEhc, num1, num2):
    ReadyToDie = core.BuffSkill("레디 투 다이", 780, 15*1000, cooltime = (90-int(0.5*vEhc.getV(num1, num2)))*1000, pdamage_indep = 30+int(0.2*vEhc.getV(num1, num2))).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    return ReadyToDie

def ReadyToDiePassiveWrapper(vEhc, num1, num2):
    ReadyToDiePassive = core.InformedCharacterModifier("레디 투 다이(패시브)",att = vEhc.getV(num1, num2))
    return ReadyToDiePassive