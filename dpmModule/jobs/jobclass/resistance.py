from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial
import adventurer

def ResistanceLineInfantryWrapper(vEhc, num1, num2):
    ResistanceLineInfantry = core.SummonSkill("레지스탕스 라인 인팬트리", 360, 1000, 215+8*vEhc.getV(num1, num2), 9, 10*1000, cooltime = 25000).isV(vEhc,num1, num2).wrap(core.SummonSkillWrapper)
    return ResistanceLineInfantry

# 메용2는 모험가 파일에 맡김. 더 나은 방법 있으면 수정 필요.
def MapleHeroes2Wrapper(vEhc, num1, num2):
    adventurer.MapleHeroes2Wrapper(vEhc, num1, num2)