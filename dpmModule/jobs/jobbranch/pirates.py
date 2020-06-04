from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

# 오버드라이브 함수 버전
# 직업 소스에서 chtr.itemlist["weapon"].att 으로 무기 공격력 접근이 가능하나 강화 후 공격력이 나옴
def OverdriveWrapper(vEhc, num1, num2, WEAPON_ATT):
    Overdrive = core.BuffSkill("오버 드라이브", 540, 30*1000, cooltime = (70 - 0.2*vEhc.getV(num1, num2))*1000, att = WEAPON_ATT*0.01*(20 + 2* vEhc.getV(num1, num2))).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    OverdrivePenalty = core.BuffSkill("오버 드라이브(페널티)", 0, (40 - 0.2*vEhc.getV(num1, num2))*1000, cooltime = -1, att = -0.15 * WEAPON_ATT).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    Overdrive.onAfter(OverdrivePenalty.controller(30*1000))
    OverdrivePenalty.set_disabled_and_time_left(-1)
    return Overdrive, OverdrivePenalty

def LoadedDicePassiveWrapper(vEhc, num1, num2):
    LoadedDicePassive = core.InformedCharacterModifier("로디드 다이스(패시브)", att = vEhc.getV(num1, num2) + 10)
    return LoadedDicePassive