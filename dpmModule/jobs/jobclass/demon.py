from ...kernel import core
from math import ceil

import gettext
_ = gettext.gettext


class DemonSkills:
    DefenderoftheDemon = _("콜 마스테마")  # "Defender of the Demon" Taken from https://maplestory.fandom.com/wiki/Defender_of_the_Demon
    OtherworldGoddessBlessing = _("이계 여신의 축복")  # "Otherworld Goddess's Blessing" Taken from https://maplestory.fandom.com/wiki/Otherworld_Goddess%27s_Blessing


def CallMastemaWrapper(vEhc, num1, num2):
    # Assume that Masterma Claw is cast every cooldown. 마스테마 클로우를 쿨타임마다 시전한다고 가정.
    claw_chance = 1
    CallMastema = core.SummonSkill(DemonSkills.DefenderoftheDemon, 690, 5000/claw_chance, 500+20*vEhc.getV(num1, num2), 8, (30+vEhc.getV(4, 4))*1000, cooltime=150*1000, red=True).isV(vEhc, num1, num2).wrap(core.SummonSkillWrapper)
    return CallMastema


def AnotherWorldWrapper(vEhc, num1, num2):
    # Assume that the Void of the Second World, the blessing of recovery, the blessing of shield, and the blessing of protection are activated every 4 seconds.
    # 이계의 공허, 회복의 축복, 방패의 축복, 보호의 축복이 4초마다 돌아가면서 발동되는 것으로 가정.
    void_delay = 4000
    void_chance = 0.25
    AnotherGoddessBuff = core.BuffSkill(DemonSkills.OtherworldGoddessBlessing, 480, 40000, cooltime=120000, red=True, pdamage_indep=5+ceil(vEhc.getV(num1, num2)/5)).wrap(core.BuffSkillWrapper)
    AnotherVoid = core.SummonSkill(_("이계의 공허"), 0, void_delay/void_chance, 1200+48*vEhc.getV(num1, num2), 12, 40000, cooltime=-1).isV(vEhc, num1, num2).wrap(core.SummonSkillWrapper)
    AnotherGoddessBuff.onAfter(AnotherVoid)
    return AnotherGoddessBuff, AnotherVoid
