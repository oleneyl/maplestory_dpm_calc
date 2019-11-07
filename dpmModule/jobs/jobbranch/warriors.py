from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

class AuraWeaponBuilder():
    def __init__(self, enhancer, skill_importance, enhance_importance):
        self.AuraWeaponBuff = core.BuffSkill(
            "오라웨폰 버프", 0, (80 +2*enhancer.getV(skill_importance,enhance_importance)) * 1000, 
            cooltime = 180 * 1000, armor_ignore = 15, pdamage_indep = (enhancer.getV(skill_importance, enhance_importance) // 5)
        ).isV(enhancer, skill_importance, enhance_importance).wrap(core.BuffSkillWrapper)  #두 스킬 syncronize 할 것!
        self.AuraWeaponCooltimeDummy = core.BuffSkill("오라웨폰(딜레이 더미)", 0, 5000, cooltime = -1).wrap(core.BuffSkillWrapper)   # 한 번 발동된 이후에는 4초간 발동되지 않도록 합니다.
        self.target_skill = core.DamageSkill("오라웨폰(파동)", 0, 500 + 20 * enhancer.getV(skill_importance,enhance_importance), 6).wrap(core.DamageSkillWrapper)
        self.target_skill.onAfter(self.AuraWeaponCooltimeDummy)
        self.optional_skill = core.OptionalElement(lambda : (self.AuraWeaponCooltimeDummy.is_not_active() and self.AuraWeaponBuff.is_active()), self.target_skill)

    def add_aura_weapon(self, origin_skill):
        origin_skill.onAfter(self.optional_skill)

    def get_buff(self):
        return self.AuraWeaponBuff, self.AuraWeaponCooltimeDummy