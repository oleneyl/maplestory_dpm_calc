from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial


class OverdriveWrapper:
    def __init__(self, vEhc, WEAPON_ATT, num1, num2):
        self.Overdrive = core.BuffSkill("오버드라이브", 540, 30*1000, cooltime = (70 - 0.2*vEhc.getV(num1, num2))*1000, att = WEAPON_ATT*0.01*(20 + 2* vEhc.getV(num1, num2))).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
        self.OverdrivePenalty = core.BuffSkill("오버드라이브(페널티)", 0, (40 - 0.2*vEhc.getV(num1, num2))*1000, cooltime = -1, att = -0.15 * WEAPON_ATT).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)