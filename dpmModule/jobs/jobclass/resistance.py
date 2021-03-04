from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

from localization.utilities import translator
_ = translator.gettext


class ResistanceSkills:
    ResistanceInfantry = _("레지스탕스 라인 인팬트리")  # "Resistance Infantry" Taken from https://maplestory.fandom.com/wiki/Resistance_Infantry


def ResistanceLineInfantryWrapper(vEhc, num1, num2, arg_modifier = core.CharacterModifier()):
    ResistanceLineInfantry = core.SummonSkill(ResistanceSkills.ResistanceInfantry, 360, 1000, 215+8*vEhc.getV(num1, num2), 9, 10*1000, cooltime = 25000, red=True, modifier = arg_modifier).isV(vEhc,num1, num2).wrap(core.SummonSkillWrapper)
    return ResistanceLineInfantry