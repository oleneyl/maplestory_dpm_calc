from ..kernel import core


_SoulContract = core.BuffSkill("SoulContract", 600, 1000, cooltime = 9000, pdamage = 45)

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