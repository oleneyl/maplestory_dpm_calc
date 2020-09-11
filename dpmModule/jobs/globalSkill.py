from ..kernel import core
import math

#_SoulContract = core.BuffSkill("SoulContract", 600, 1000, cooltime = 9000, pdamage = 45)

usefulSkillRemain = lambda slevel = 1: (180 + slevel * 3) * 1000
passiveStat = lambda slevel = 1: (slevel + 4) // 5

# 미완성 코드
def useful_hyper_body_demonavenger(slevel = 1):
    # 딜레이 클라기준
    UsefulHyperBody = core.BuffSkill("쓸만한 하이퍼 바디 (데몬어벤져)", 600, usefulSkillRemain(slevel), pstat_main = 40, stat_sub = passiveStat(slevel), rem = False).wrap(core.BuffSkillWrapper)
    return UsefulHyperBody

def useful_hyper_body_zenon(slevel = 1):
    # 마나뻥 처리는 직업코드에서
    UsefulHyperBody = core.BuffSkill("쓸만한 하이퍼 바디 (제논)", 600, usefulSkillRemain(slevel), stat_main = passiveStat(slevel), stat_sub = passiveStat(slevel), rem = False).wrap(core.BuffSkillWrapper)
    return UsefulHyperBody

# 기본 90초, 직업별 딜사이클에 따라 쿨타임 조절가능
def soul_contract(Cool = 90*1000):
    SoulContract = core.BuffSkill("소울 컨트랙트", 900, 10*1000, cooltime = Cool, pdamage = 45, rem = True, red = True).wrap(core.BuffSkillWrapper)
    return SoulContract

# 쓸컴뱃 = 1, 팔라딘 = 2
def maple_heros(level, name = "메이플 용사", combat_level = 0):
    MapleHeros = core.BuffSkill(name, 0, (900+15*combat_level)*1000, stat_main = math.ceil(15 + 0.5 * combat_level)*0.01*(25 + level * 5), rem = True).wrap(core.BuffSkillWrapper)
    return MapleHeros

# 1레벨
def useful_combat_orders():
    UsefulCombatOrders = core.BuffSkill("쓸만한 컴뱃 오더스", 1500, usefulSkillRemain(), rem = False).wrap(core.BuffSkillWrapper)
    return UsefulCombatOrders
    
def useful_sharp_eyes(slevel = 1):
    UsefulSharpEyes = core.BuffSkill("쓸만한 샤프 아이즈", 900, usefulSkillRemain(slevel), rem = False, crit = 10, crit_damage = 8, stat_main = passiveStat(slevel), stat_sub = passiveStat(slevel)).wrap(core.BuffSkillWrapper)
    return UsefulSharpEyes
    
def useful_wind_booster(slevel = 1):
    UsefulWindBooster = core.BuffSkill("쓸만한 윈드 부스터", 900, usefulSkillRemain(slevel), rem = False, stat_main = passiveStat(slevel), stat_sub = passiveStat(slevel)).wrap(core.BuffSkillWrapper)
    return UsefulWindBooster

def useful_advanced_bless(slevel = 1, useHP = False):
    # TODO: HP, MP 475 증가 반영
    UsefulAdvancedBless = core.BuffSkill("쓸만한 어드밴스드 블레스", usefulSkillRemain(slevel), rem = False, att = 20, stat_main = 475 * useHP).wrap(core.BuffSkillWrapper)

class SpiderInMirrorBuilder():
    def __init__(self, enhancer, skill_importance, enhance_importance, chtr_level):
        self.MirrorBreak = core.DamageSkill(
            "스파이더 인 미러(공간 붕괴)", 960, 450+18*enhancer.getV(skill_importance, enhance_importance), 15, cooltime = 250*1000, red = True
        ).wrap(core.DamageSkillWrapper)
        # 5번 연속 공격 후 종료, 재돌입 대기시간 3초
        self.MirrorSpider = core.SummonSkill(
            "스파이더 인 미러(거울 속의 거미)", 0, 3000, 175+17*enhancer.getV(skill_importance, enhance_importance), 8, 15*1000, cooltime = -1
        ).wrap(core.SummonSkillWrapper)
        self.MirrorBreak.onAfter(self.MirrorSpider.controller(3000))
        self.SpiderInMirror = core.OptionalElement(cthr_level >= 235, MirrorBreak)

    def get_skill(self):
        return self.SpiderInMirror

# 모험가, 영웅, 레지스탕스가 사용
def MapleHeroes2Wrapper(vEhc, num1, num2, level):
    MapleHeroes2 = core.BuffSkill("메이플월드 여신의 축복", 450, 60*1000, stat_main = 0.01 * (100 + 10 * vEhc.getV(num1, num2)) * (25 + level * 5), pdamage = 5 + vEhc.getV(num1, num2) // 2, cooltime = 180*1000, red = True).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    return MapleHeroes2

# 창조의 아이온 (즉시 재시전)
def genesis_aeonian_rise():
    AeonianRise = core.DamageSkill("창조의 아이온", 0, 1500, 7, cooltime = 180000).wrap(core.DamageSkillWrapper)
    return AeonianRise

# 파괴의 얄다바오트
def genesis_tanadian_ruin():
    TandadianRuin = core.BuffSkill("파괴의 얄다바오트", 0, 30000, cooltime = 120000, pdamage_indep = 15, rem = False, red = False).wrap(core.BuffSkillWrapper)
    return TandadianRuin