from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial


class OverdriveWrapper:
    def __init__(self, vEhc, WEAPON_ATT, num1, num2):
        self.Overdrive = core.BuffSkill("오버드라이브", 540, 30*1000, cooltime = (70 - 0.2*vEhc.getV(num1, num2))*1000, att = WEAPON_ATT*0.01*(20 + 2* vEhc.getV(num1, num2))).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
        self.OverdrivePenalty = core.BuffSkill("오버드라이브(페널티)", 0, (40 - 0.2*vEhc.getV(num1, num2))*1000, cooltime = -1, att = -0.15 * WEAPON_ATT).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)

# 오버드라이브 함수 버전 (테스트 아직 안함)
def OverdirveWrapper2(vEhc, num1, num2, WEAPON_ATT):
    Overdrive = core.BuffSkill("오버드라이브", 540, 30*1000, cooltime = (70 - 0.2*vEhc.getV(num1, num2))*1000, att = WEAPON_ATT*0.01*(20 + 2* vEhc.getV(num1, num2))).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    OverdrivePenalty = core.BuffSkill("오버드라이브(페널티)", 0, (40 - 0.2*vEhc.getV(num1, num2))*1000, cooltime = -1, att = -0.15 * WEAPON_ATT).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    Overdrive.onAfter(OverdrivePenalty.controller(30*1000))
    return Overdrive

def LoadedDicePassiveWrapper(vEhc, num1, num2):
    LoadedDicePassive = core.InformedCharacterModifier("로디드 다이스(패시브)", att = vEhc.getV(num1, num2) + 10)
    return LoadedDicePassive