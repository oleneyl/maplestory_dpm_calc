from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

import gettext
_ = gettext.gettext


class FloraSkills:
    GrandisGoddessBlessing = _("그란디스 여신의 축복")  # "Grandis Goddess's Blessing" Taken from https://maplestory.fandom.com/wiki/Grandis_Goddess%27s_Blessing
    ConversionOverdrive = _("매직 서킷 풀드라이브")  # "Conversion Overdrive" Taken from https://maplestory.fandom.com/wiki/Conversion_Overdrive


# Lef. 레프.
def FloraGoddessBlessWrapper(vEhc, num1, num2, WEAPON_ATT):
    # Equipment proportional increase is assumed to be the maximum. 장비 비례 증가 수치는 최대치로 가정.
    FloraGoddessBless = core.BuffSkill(_("{}(레프)").format(FloraSkills.GrandisGoddessBlessing), 480, 40*1000, att = 10 + 3 * vEhc.getV(num1, num2) + 1.5 * WEAPON_ATT, cooltime = 240*1000, red=True).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    return FloraGoddessBless


# Assuming the maximum mana is maintained, it is necessary to check how the number changes according to the ratio.
# In the event of a magical storm, the damage increase is not applied..
# 마나 최대치 유지 가정, 비율에 따라 수치가 어떻게 변동되는지 확인 필요.
# 마력 폭풍 발생 시 데미지 증가량 갱신 미적용중.
class MagicCircuitFullDriveBuilder():
    def __init__(self, vEhc, num1, num2, mana = 100):
        self.MANA = mana
        self.MagicCircuitFullDriveBuff = core.BuffSkill(_("{}(버프)").format(FloraSkills.ConversionOverdrive), 540, (30+vEhc.getV(num1, num2))*1000, cooltime=200*1000, red=True, pdamage=(20+vEhc.getV(num1, num2)) * (self.MANA/100)).wrap(core.BuffSkillWrapper)
        self.ManaStorm = core.DamageSkill(_("{}(마력 폭풍)").format(FloraSkills.ConversionOverdrive), 0, 500+20*vEhc.getV(num1, num2), 3, cooltime = 4000).wrap(core.DamageSkillWrapper)
        self.UseManaStorm = core.OptionalElement(lambda: self.MagicCircuitFullDriveBuff.is_active() and self.ManaStorm.is_available(), self.ManaStorm)
        self.ManaStorm.protect_from_running()
        
    def add_trigger(self, trigger_skill):
        if getattr(trigger_skill, 'is_periodic', False):
            trigger_skill.onTick(self.UseManaStorm)
        else:
            trigger_skill.onAfter(self.UseManaStorm)

    def get_skill(self):
        return self.MagicCircuitFullDriveBuff, self.ManaStorm
