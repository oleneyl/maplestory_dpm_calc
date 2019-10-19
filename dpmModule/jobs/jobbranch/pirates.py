from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

#오버드라이브 (앱솔 가정)
#TODO: 템셋을 읽어서 무기별로 다른 수치 적용하도록 만들어야 함.

class OverDriveWrapper:
    def __init__(self, vEhc, weaponATT, num1, num2):
        self.OverdriveBuff = core.BuffSkill("오버드라이브", 540, 30*1000, cooltime = (70 - 0.2*vEhc.getV(num1, num2))*1000, att = 1.54*(20 + 2* vEhc.getV(num1, num2))).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
        self.OverdrivePenalty = core.BuffSkill("오버드라이브(페널티)", 0, (40 - 0.2*vEhc.getV(num1, num2))*1000, cooltime = -1, att = -15*1.54).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    def OverDrive(self):
        return self.OverdriveBuff
    def OverDrivePenalty(self):
        return self.OverdrivePenalty