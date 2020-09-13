from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

class OverdriveWrapper(core.BuffSkillWrapper):
    def __init__(self, vEhc, num1, num2, WEAPON_ATT):
        skill = core.BuffSkill("오버 드라이브", 420, 30*1000, cooltime = (70 - vEhc.getV(num1, num2) // 5)*1000, red=True, att = WEAPON_ATT*0.01*(20 + 2* vEhc.getV(num1, num2))).isV(vEhc, num1, num2)
        self.penaltyModifier = core.CharacterModifier(att = -0.15 * WEAPON_ATT)
        super(OverdriveWrapper, self).__init__(skill)

    def get_modifier(self) -> core.CharacterModifier:
        if self.onoff:
            return self.skill.get_modifier()
        elif not self.is_available():
            return self.penaltyModifier
        else:
            return self.disabledModifier

def LoadedDicePassiveWrapper(vEhc, num1, num2):
    LoadedDicePassive = core.InformedCharacterModifier("로디드 다이스(패시브)", att = vEhc.getV(num1, num2) + 10)
    return LoadedDicePassive