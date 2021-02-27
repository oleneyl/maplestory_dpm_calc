from ...kernel import core

import gettext
_ = gettext.gettext


class NovaSkills:
    GrandisGoddessBlessing = _("그란디스 여신의 축복")  # "Grandis Goddess's Blessing" Taken from https://maplestory.fandom.com/wiki/Grandis_Goddess%27s_Blessing
    MightoftheNova = _("판테온")  # "Might of the Nova" Taken from https://maplestory.fandom.com/wiki/Might_of_the_Nova


# TODO: (40+0.5*skill level)%, rounded down to the decimal point. Chances are, cooldown is not applied, and can only be applied up to 5 times. (40+0.5*스킬레벨)%, 소수점 아래로 버림. 확률로 재사용 대기시간 미적용, 최대 5회까지만 미적용 가능.
class NovaGoddessBlessWrapper(core.BuffSkillWrapper):
    def __init__(self, vEhc, num1, num2, morph_gauge=None):
        skill = core.BuffSkill(
            _("{}(노바)").format(NovaSkills.GrandisGoddessBlessing),
            delay=480,
            remain=40 * 1000,
            pdamage=5 + vEhc.getV(num1, num2),
            cooltime=240 * 1000,
            red=True,
        ).isV(vEhc, num1, num2)
        super(NovaGoddessBlessWrapper, self).__init__(skill)
        self.morph_gauge = morph_gauge

    def get_modifier(self):
        if self.is_active():
            if self.morph_gauge is None:
                return self.skill.get_modifier()
            else:
                return self.skill.get_modifier() + core.CharacterModifier(
                    pdamage=self.morph_gauge.get_morph_level() * 10
                )
        else:
            return self.disabledModifier


def PantheonWrapper(vEhc, num1: int, num2: int):
    Pantheon = (
        core.DamageSkill(
            NovaSkills.MightoftheNova,
            delay=390,  # base delay 510, AS applied
            damage=2000 + 80 * vEhc.getV(num1, num2),
            hit=10,
            cooltime=1200 * 1000,
            red=True,
        )
        .isV(vEhc, num1, num2)
        .wrap(core.DamageSkillWrapper)
    )
    return Pantheon
