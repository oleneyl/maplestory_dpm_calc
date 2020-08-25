from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

class AuraWeaponBuilder():
    def __init__(self, enhancer, skill_importance, enhance_importance, modifier=core.CharacterModifier(), hit=6):
        self.AuraWeaponBuff = core.BuffSkill(
            "오라 웨폰(버프)", 720, (80 +2*enhancer.getV(skill_importance,enhance_importance)) * 1000, 
            cooltime = 180 * 1000, armor_ignore = 15, pdamage_indep = (enhancer.getV(skill_importance, enhance_importance) // 5)
        ).isV(enhancer, skill_importance, enhance_importance).wrap(core.BuffSkillWrapper)  #두 스킬 syncronize 할 것!
        self.target_skill = core.DamageSkill("오라웨폰(파동)", 0, 500 + 20 * enhancer.getV(skill_importance,enhance_importance), hit, modifier=modifier, cooltime = 5000).wrap(core.DamageSkillWrapper)
        self.optional_skill = core.OptionalElement(lambda : (self.target_skill.is_available() and self.AuraWeaponBuff.is_active()), self.target_skill)

    def add_aura_weapon(self, origin_skill):
        origin_skill.onAfter(self.optional_skill)

    def get_buff(self):
        return self.AuraWeaponBuff