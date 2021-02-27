from dpmModule.character.characterKernel import AbstractCharacter
from ..kernel import core
import math

import gettext
_ = gettext.gettext


class GlobalSkills:
    TermsAndConditions = _('소울 컨트랙트')  # 'Terms and Conditions' Taken from https://maplestory.fandom.com/wiki/Terms_and_Conditions
    MapleWarrior = _('메이플 용사')  # 'Maple Warrior' Taken from https://maplestory.fandom.com/wiki/Maple_Warrior
    DecentCombatOrders = _('쓸만한 컴뱃 오더스')  # 'Decent Combat Orders' Taken from https://maplestory.fandom.com/wiki/Decent_Combat_Orders
    DecentSharpEyes = _('쓸만한 샤프 아이즈')  # 'Decent Sharp Eyes' Taken from https://maplestory.fandom.com/wiki/Decent_Sharp_Eyes
    DecentSpeedInfusion = _('쓸만한 윈드 부스터')  # 'Decent Speed Infusion' Taken from https://maplestory.fandom.com/wiki/Decent_Speed_Infusion
    DecentHyperBody = _('쓸만한 하이퍼 바디')  # 'Decent Hyper Body' Taken from https://maplestory.fandom.com/wiki/Decent_Hyper_Body
    DecentAdvancedBlessing = _('쓸만한 어드밴스드 블레스')  # 'Decent Advanced Blessing' Taken from https://maplestory.fandom.com/wiki/Decent_Advanced_Blessing
    MapleWorldGoddessBlessing = _('메이플월드 여신의 축복')  # 'Maple World Goddess' Blessing' Taken from https://maplestory.fandom.com/wiki/Maple_World_Goddess%27s_Blessing
    TrueArachnidReflection = _('스파이더 인 미러')  # 'True Arachnid Reflection' Taken from https://maplestory.fandom.com/wiki/True_Arachnid_Reflection
    TanadianRuin = _('파괴의 얄다바오트')  # 'Tanadian Ruin' Taken from https://maplestory.fandom.com/wiki/Tanadian_Ruin_(Skill)
    AeonianRise = _('창조의 아이온')  # 'Aeonian Rise' Taken from https://maplestory.fandom.com/wiki/Aeonian_Rise_(Skill)
    MitraFlame = _('크레스트 오브 더 솔라')  # 'Mitra Flame?' Taken from


def usefulSkillRemain(slevel=1): return (180+slevel*3)*1000


def passiveStat(slevel=1): return (slevel+4)/5

# Angelic Buster Link Skill
def soul_contract():
    return core.BuffSkill(GlobalSkills.TermsAndConditions, 900, 10 * 1000, cooltime=90000, pdamage=45, rem=True, red=True).wrap(core.BuffSkillWrapper)


# combat_level: Zero = 0, Paladin = 2, for other jobs, enter self.combat. 제로 = 0, 팔라딘 = 2, 이외 직업은 self.combat 입력.
def maple_heros(level, name=GlobalSkills.MapleWarrior, combat_level=0):
    return core.BuffSkill(name, 0, (900+15*combat_level)*1000,
                          stat_main=math.ceil(15+combat_level/2)*0.01*(25+level*5), rem=True
                          ).wrap(core.BuffSkillWrapper)


# Decent Combat Orders
# Fixed level 1 (since the bonus per level is resistant). 1레벨 고정 (레벨당 보너스가 내성이므로).
def useful_combat_orders():
    return core.BuffSkill(GlobalSkills.DecentCombatOrders, 1500, usefulSkillRemain(), rem=False).wrap(core.BuffSkillWrapper)


def useful_sharp_eyes(slevel=1):
    return core.BuffSkill(GlobalSkills.DecentSharpEyes, 900, usefulSkillRemain(slevel), rem=False, crit=10, crit_damage=8,
                          stat_main=passiveStat(slevel), stat_sub=passiveStat(slevel)).wrap(core.BuffSkillWrapper)


def useful_wind_booster(slevel=1):
    return core.BuffSkill(GlobalSkills.DecentSpeedInfusion, 900, usefulSkillRemain(slevel), rem=False,
                          stat_main=passiveStat(slevel), stat_sub=passiveStat(slevel)
                          ).wrap(core.BuffSkillWrapper)


# TODO: Separate each for Xenon and Demon Avenger. 제논, 데몬어벤져용 각각 분리.
def useful_advanced_bless(slevel=1):
    return core.BuffSkill(GlobalSkills.DecentAdvancedBlessing, 600, usefulSkillRemain(slevel), rem=False, att=20).wrap(core.BuffSkillWrapper)

# Will Node Cast
class MirrorBreakWrapper(core.DamageSkillWrapper):
    def __init__(self, vEhc, num1, num2, modifier) -> None:
        skill = core.DamageSkill(_('{}(공간 붕괴)').format(GlobalSkills.TrueArachnidReflection), 720, 450 + 18 * vEhc.getV(num1, num2), 15, cooltime=250 * 1000, red=True, modifier=modifier).isV(vEhc, num1, num2)
        super(MirrorBreakWrapper, self).__init__(skill)

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return chtr.level >= 235

# Will Node Summon
class MirrorSpiderWrapper(core.SummonSkillWrapper):
    # Ends after 5 consecutive attacks, 3 seconds waiting time for re-entry. 5번 연속 공격 후 종료, 재돌입 대기시간 3초.
    def __init__(self, vEhc, num1, num2, modifier) -> None:
        self.delays = [900, 850, 750, 650, 5730]  # 400001039. Delay taken from summonedSequenceAttack, 5730ms of open eyes after 5th attack. 400001039.summonedSequenceAttack에서 가져온 딜레이, 5회째 공격 후 눈 감고뜨는 시간 5730ms.
        self.hit_count = 0
        skill = core.SummonSkill(_('{}(거울 속의 거미)').format(GlobalSkills.TrueArachnidReflection), 0, 900, 175 + 7 * vEhc.getV(num1, num2), 8, 50 * 1000, cooltime=-1, modifier=modifier).isV(vEhc, num1, num2)
        super(MirrorSpiderWrapper, self).__init__(skill)

    def _useTick(self) -> core.ResultObject:
        result = super(MirrorSpiderWrapper, self)._useTick()
        self.hit_count = (self.hit_count + 1) % 5
        return result

    def get_delay(self) -> float:
        return self.delays[self.hit_count]

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return chtr.level >= 235


def SpiderInMirrorBuilder(enhancer, skill_importance, enhance_importance, break_modifier=core.CharacterModifier(), spider_modifier=core.CharacterModifier()):
    MirrorBreak = MirrorBreakWrapper(enhancer, skill_importance, enhance_importance, break_modifier)
    MirrorSpider = MirrorSpiderWrapper(enhancer, skill_importance, enhance_importance, spider_modifier)
    MirrorBreak.onEventElapsed(MirrorSpider, 3000)
    return MirrorBreak, MirrorSpider

# 5th job Maple Warrior
# Used by adventurers, heroes, and resistance. 모험가, 영웅, 레지스탕스가 사용.
def MapleHeroes2Wrapper(vEhc, num1, num2, level, combat_level):
    return core.BuffSkill(GlobalSkills.MapleWorldGoddessBlessing, 450, 60 * 1000,
                          stat_main=(2+vEhc.getV(num1, num2)/10)*math.ceil(15+combat_level/2)*0.01*(25+level*5),
                          pdamage=5+vEhc.getV(num1, num2)//2, cooltime=180*1000, red=True
                          ).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)


# Genesis Weapon Skill
class TandadianRuinWrapper(core.BuffSkillWrapper):
    def __init__(self) -> None:
        skill = core.BuffSkill(GlobalSkills.TanadianRuin, 0, 30000, cooltime=90000, pdamage_indep=15, rem=False, red=False)
        super(TandadianRuinWrapper, self).__init__(skill)

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return chtr.gear_list["weapon"].name.startswith("제네시스")

# Genesis Weapon Skill
class AeonianRiseWrapper(core.DamageSkillWrapper):
    def __init__(self) -> None:
        skill = core.DamageSkill(GlobalSkills.AeonianRise, 0, 1500, 7, cooltime=180000, red=True)
        super(AeonianRiseWrapper, self).__init__(skill)

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return chtr.gear_list["weapon"].name.startswith("제네시스")


def GenesisSkillBuilder():
    return TandadianRuinWrapper(), AeonianRiseWrapper()

# Seren Node Cast
class MitraFlameWrapper(core.DamageSkillWrapper):
    def __init__(self, vEhc, num1, num2, modifier) -> None:
        skill = core.DamageSkill(_('{}(미트라의 불꽃)').format(GlobalSkills.MitraFlame), 870, 750 + 30 * vEhc.getV(num1, num2), 12, cooltime=250 * 1000, red=True, modifier=modifier).isV(vEhc, num1, num2)
        super(MitraFlameWrapper, self).__init__(skill)

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return chtr.level >= 265

# Seren Node Summon
class FlamePatternWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2, modifier) -> None:
        skill = core.SummonSkill(_('{}(불꽃의 문양)').format(GlobalSkills.MitraFlame), 0, 2100, 275 + 11 * vEhc.getV(num1, num2), 6, 51 * 1000, cooltime=-1, modifier=modifier).isV(vEhc, num1, num2)
        super(FlamePatternWrapper, self).__init__(skill)

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return chtr.level >= 265

def CrestOfTheSolarBuilder(enhancer, skill_importance, enhance_importance, modifier=core.CharacterModifier()):
    MitraFlame = MitraFlameWrapper(enhancer, skill_importance, enhance_importance, modifier)
    FlamePattern = FlamePatternWrapper(enhancer, skill_importance, enhance_importance, modifier)
    MitraFlame.onAfter(FlamePattern)
    return MitraFlame, FlamePattern


# Unfinished code. 미완성 코드.
def useful_hyper_body_demonavenger(slevel=1):
    # Based on delay clas. 딜레이 클라기준.
    return core.BuffSkill(_('{}(데몬어벤져)').format(GlobalSkills.DecentHyperBody), 600, usefulSkillRemain(slevel),
                          pstat_main=40, stat_sub=passiveStat(slevel), rem=False
                          ).wrap(core.BuffSkillWrapper)


def useful_hyper_body_xenon(slevel=1):
    # Manapup treatment in the job code. 마나뻥 처리는 직업코드에서.
    return core.BuffSkill(_('{}(제논)').format(GlobalSkills.DecentHyperBody), 600, usefulSkillRemain(slevel),
                          stat_main=passiveStat(slevel), stat_sub=passiveStat(slevel), rem=False
                          ).wrap(core.BuffSkillWrapper)
