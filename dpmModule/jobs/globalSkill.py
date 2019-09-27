from ..kernel import core


#_SoulContract = core.BuffSkill("SoulContract", 600, 1000, cooltime = 9000, pdamage = 45)

def soul_contract():
    SoulContract = core.BuffSkill("소울 컨트랙트", 600, 10*1000, cooltime = 90*1000, pdamage = 45, rem = True).wrap(core.BuffSkillWrapper)
    return SoulContract

def maple_heros(level):
    MapleHeros = core.BuffSkill("메이플 용사", 0, 900*1000, stat_main = 0.15*(25 + level * 5), rem = True).wrap(core.BuffSkillWrapper)
    return MapleHeros

def useful_combat_orders():
    UsefulCombatOrders = core.BuffSkill("쓸만한 컴뱃 오더스", 1350, 183*1000, rem = False).wrap(core.BuffSkillWrapper)
    return UsefulCombatOrders
    
def useful_sharp_eyes():
    UsefulSharpEyes = core.BuffSkill("쓸만한 샤프 아이즈", 1080, 183 * 1000, rem = False, crit = 10, crit_damage = 8).wrap(core.BuffSkillWrapper)
    return UsefulSharpEyes
    
def useful_wind_booster():
    UsefulWindBooster = core.BuffSkill("쓸만한 윈드 부스터", 1080, 183*1000, rem = False).wrap(core.BuffSkillWrapper)
    return UsefulWindBooster

class AuraWeaponBuilder():
    def __init__(self, enhancer, skill_importance, enhance_importance):
        self.AuraWeaponBuff = core.BuffSkill(
            "오라웨폰 버프", 0, (80 +2*enhancer.getV(skill_importance,enhance_importance)) * 1000, 
            cooltime = 180 * 1000, armor_ignore = 15, pdamage_indep = (enhancer.getV(skill_importance, enhance_importance) // 5)
        ).isV(enhancer, skill_importance, enhance_importance).wrap(core.BuffSkillWrapper)  #두 스킬 syncronize 할 것!
        self.AuraWeaponCooltimeDummy = core.BuffSkill("오라웨폰(딜레이 더미)", 0, 7000, cooltime = -1).wrap(core.BuffSkillWrapper)   # 한 번 발동된 이후에는 4초간 발동되지 않도록 합니다.
        self.target_skill = core.DamageSkill("오라웨폰(파동)", 0, 500 + 20 * enhancer.getV(skill_importance,enhance_importance), 6).wrap(core.DamageSkillWrapper)
        self.target_skill.onAfter(self.AuraWeaponCooltimeDummy)
        self.optional_skill = core.OptionalElement(lambda : (self.AuraWeaponCooltimeDummy.is_not_active() and self.AuraWeaponBuff.is_active()), self.target_skill)

    def add_aura_weapon(self, origin_skill):
        origin_skill.onAfter(self.optional_skill)

    def get_buff(self):
        return self.AuraWeaponBuff, self.AuraWeaponCooltimeDummy

