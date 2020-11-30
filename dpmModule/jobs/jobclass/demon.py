from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial
from math import ceil

# 마스테마 클로우를 쿨타임마다 시전한다고 가정
def CallMastemaWrapper(vEhc, num1, num2):
    claw_chance = 1
    CallMastema = core.SummonSkill("콜 마스테마", 690, 5000 / claw_chance, 500+20*vEhc.getV(num1, num2), 8, (30+vEhc.getV(4,4))*1000, cooltime = 150*1000, red=True).isV(vEhc,num1,num2).wrap(core.SummonSkillWrapper)
    return CallMastema

def AnotherWorldWrapper(vEhc, num1, num2):
    # 이계의 공허, 회복의 축복, 방패의 축복, 보호의 축복이 4초마다 돌아가면서 발동되는 것으로 가정
    void_delay = 4000
    void_chance = 0.25
    AnotherGoddessBuff = core.BuffSkill("이계 여신의 축복", 480, 40000, cooltime = 120000, red=True, pdamage_indep=5+ceil(vEhc.getV(num1, num2)/5)).wrap(core.BuffSkillWrapper)
    AnotherVoid = core.SummonSkill("이계의 공허", 0, void_delay / void_chance, 1200+48*vEhc.getV(num1, num2), 12, 40000, cooltime = -1).isV(vEhc,num1,num2).wrap(core.SummonSkillWrapper)
    AnotherGoddessBuff.onAfter(AnotherVoid)
    return AnotherGoddessBuff, AnotherVoid