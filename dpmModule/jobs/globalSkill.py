from enum import Enum

from dpmModule.character.characterKernel import AbstractCharacter
from ..kernel import core
from ..kernel.core.utilities import Language
import math


class GlobalSkills(Enum):
    TermsAndConditions = Language('Terms and Conditions', '소울 컨트랙트')  # Taken from https://maplestory.fandom.com/wiki/Terms_and_Conditions
    MapleWarrior = Language('Maple Warrior', '메이플 용사')  # Taken from https://maplestory.fandom.com/wiki/Maple_Warrior
    DecentCombatOrders = Language('Decent Combat Orders', '쓸만한 컴뱃 오더스')  # Taken from https://maplestory.fandom.com/wiki/Decent_Combat_Orders
    DecentSharpEyes = Language('Decent Sharp Eyes', '쓸만한 샤프 아이즈')  # Taken from https://maplestory.fandom.com/wiki/Decent_Sharp_Eyes
    DecentSpeedInfusion = Language('Decent Speed Infusion', '쓸만한 윈드 부스터')  # Taken from https://maplestory.fandom.com/wiki/Decent_Speed_Infusion
    DecentHyperBody = Language('Decent Hyper Body', '쓸만한 하이퍼 바디')  # Taken from https://maplestory.fandom.com/wiki/Decent_Hyper_Body
    DecentAdvancedBlessing = Language('Decent Advanced Blessing')  # Taken from https://maplestory.fandom.com/wiki/Decent_Advanced_Blessing
    MapleWorldGoddessBlessing = Language('Maple World Goddess\' Blessing', '메이플월드 여신의 축복')  # Taken from https://maplestory.fandom.com/wiki/Maple_World_Goddess%27s_Blessing
    TrueArachnidReflection = Language('True Arachnid Reflection', '스파이더 인 미러')  # Taken from https://maplestory.fandom.com/wiki/True_Arachnid_Reflection
    TanadianRuin = Language('Tanadian Ruin', '파괴의 얄다바오트')  # Taken from https://maplestory.fandom.com/wiki/Tanadian_Ruin_(Skill)
    AeonianRise = Language('Aeonian Rise', '창조의 아이온')  # Taken from https://maplestory.fandom.com/wiki/Aeonian_Rise_(Skill)
    MitraFlame = Language('Mitra Flame?', '크레스트 오브 더 솔라')  # Taken from


def usefulSkillRemain(slevel=1): return (180+slevel*3)*1000


def passiveStat(slevel=1): return (slevel+4)/5

# Angelic Buster Link Skill
def soul_contract(lang='ko'):
    return core.BuffSkill(GlobalSkills.TermsAndConditions.value[lang], 900, 10 * 1000, cooltime=90000, pdamage=45, rem=True, red=True).wrap(core.BuffSkillWrapper)


# combat_level: Zero = 0, Paladin = 2, for other jobs, enter self.combat. 제로 = 0, 팔라딘 = 2, 이외 직업은 self.combat 입력.
def maple_heros(level, name=None, combat_level=0, lang='ko'):
    if not name:
        name = GlobalSkills.MapleWarrior.value[lang]
    return core.BuffSkill(name, 0, (900+15*combat_level)*1000,
                          stat_main=math.ceil(15+combat_level/2)*0.01*(25+level*5), rem=True
                          ).wrap(core.BuffSkillWrapper)


# Decent Combat Orders
# Fixed level 1 (since the bonus per level is resistant). 1레벨 고정 (레벨당 보너스가 내성이므로).
def useful_combat_orders(lang='ko'):
    return core.BuffSkill(GlobalSkills.DecentCombatOrders.value[lang], 1500, usefulSkillRemain(), rem=False).wrap(core.BuffSkillWrapper)


def useful_sharp_eyes(slevel=1, lang='ko'):
    return core.BuffSkill(GlobalSkills.DecentSharpEyes.value[lang], 900, usefulSkillRemain(slevel), rem=False, crit=10, crit_damage=8,
                          stat_main=passiveStat(slevel), stat_sub=passiveStat(slevel)).wrap(core.BuffSkillWrapper)


def useful_wind_booster(slevel=1, lang='ko'):
    return core.BuffSkill(GlobalSkills.DecentSpeedInfusion.value[lang], 900, usefulSkillRemain(slevel), rem=False,
                          stat_main=passiveStat(slevel), stat_sub=passiveStat(slevel)
                          ).wrap(core.BuffSkillWrapper)


# TODO: Separate each for Xenon and Demon Avenger. 제논, 데몬어벤져용 각각 분리.
def useful_advanced_bless(slevel=1, lang='ko'):
    return core.BuffSkill(GlobalSkills.DecentAdvancedBlessing.value[lang], 600, usefulSkillRemain(slevel), rem=False, att=20).wrap(core.BuffSkillWrapper)

# Will Node Cast
class MirrorBreakWrapper(core.DamageSkillWrapper):
    def __init__(self, vEhc, num1, num2, modifier, lang='ko') -> None:
        skill = core.DamageSkill(f"{GlobalSkills.TrueArachnidReflection.value[lang]}(Space Collapse | 공간 붕괴)", 720, 450 + 18 * vEhc.getV(num1, num2), 15, cooltime=250 * 1000, red=True, modifier=modifier).isV(vEhc, num1, num2)
        super(MirrorBreakWrapper, self).__init__(skill)

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return chtr.level >= 235

# Will Node Summon
class MirrorSpiderWrapper(core.SummonSkillWrapper):
    # Ends after 5 consecutive attacks, 3 seconds waiting time for re-entry. 5번 연속 공격 후 종료, 재돌입 대기시간 3초.
    def __init__(self, vEhc, num1, num2, modifier, lang='ko') -> None:
        self.delays = [900, 850, 750, 650, 5730]  # 400001039. Delay taken from summonedSequenceAttack, 5730ms of open eyes after 5th attack. 400001039.summonedSequenceAttack에서 가져온 딜레이, 5회째 공격 후 눈 감고뜨는 시간 5730ms.
        self.hit_count = 0
        skill = core.SummonSkill(f"{GlobalSkills.TrueArachnidReflection.value[lang]}(Spider Legs | 거울 속의 거미)", 0, 900, 175 + 7 * vEhc.getV(num1, num2), 8, 50 * 1000, cooltime=-1, modifier=modifier).isV(vEhc, num1, num2)
        super(MirrorSpiderWrapper, self).__init__(skill)

    def _useTick(self) -> core.ResultObject:
        result = super(MirrorSpiderWrapper, self)._useTick()
        self.hit_count = (self.hit_count + 1) % 5
        return result

    def get_delay(self) -> float:
        return self.delays[self.hit_count]

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return chtr.level >= 235


def SpiderInMirrorBuilder(enhancer, skill_importance, enhance_importance, break_modifier=core.CharacterModifier(), spider_modifier=core.CharacterModifier(), lang='ko'):
    MirrorBreak = MirrorBreakWrapper(enhancer, skill_importance, enhance_importance, break_modifier, lang=lang)
    MirrorSpider = MirrorSpiderWrapper(enhancer, skill_importance, enhance_importance, spider_modifier, lang=lang)
    MirrorBreak.onEventElapsed(MirrorSpider, 3000)
    return MirrorBreak, MirrorSpider

# 5th job Maple Warrior
# Used by adventurers, heroes, and resistance. 모험가, 영웅, 레지스탕스가 사용.
def MapleHeroes2Wrapper(vEhc, num1, num2, level, combat_level, lang='ko'):
    return core.BuffSkill(GlobalSkills.MapleWorldGoddessBlessing.value[lang], 450, 60 * 1000,
                          stat_main=(2+vEhc.getV(num1, num2)/10)*math.ceil(15+combat_level/2)*0.01*(25+level*5),
                          pdamage=5+vEhc.getV(num1, num2)//2, cooltime=180*1000, red=True
                          ).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)


# Genesis Weapon Skill
class TandadianRuinWrapper(core.BuffSkillWrapper):
    def __init__(self, lang='ko') -> None:
        skill = core.BuffSkill(GlobalSkills.TanadianRuin.value[lang], 0, 30000, cooltime=90000, pdamage_indep=15, rem=False, red=False)
        super(TandadianRuinWrapper, self).__init__(skill)

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return chtr.gear_list["weapon"].name.startswith("제네시스")

# Genesis Weapon Skill
class AeonianRiseWrapper(core.DamageSkillWrapper):
    def __init__(self, lang='ko') -> None:
        skill = core.DamageSkill(GlobalSkills.AeonianRise.value[lang], 0, 1500, 7, cooltime=180000, red=True)
        super(AeonianRiseWrapper, self).__init__(skill)

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return chtr.gear_list["weapon"].name.startswith("제네시스")


def GenesisSkillBuilder():
    return TandadianRuinWrapper(), AeonianRiseWrapper()

# Seren Node Cast
class MitraFlameWrapper(core.DamageSkillWrapper):
    def __init__(self, vEhc, num1, num2, modifier, lang='ko') -> None:
        skill = core.DamageSkill(f"{GlobalSkills.MitraFlame.value[lang]}(미트라의 불꽃)", 870, 750 + 30 * vEhc.getV(num1, num2), 12, cooltime=250 * 1000, red=True, modifier=modifier).isV(vEhc, num1, num2)
        super(MitraFlameWrapper, self).__init__(skill)

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return chtr.level >= 265

# Seren Node Summon
class FlamePatternWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2, modifier, lang='ko') -> None:
        skill = core.SummonSkill(f"{GlobalSkills.MitraFlame.value[lang]}(불꽃의 문양)", 0, 2100, 275 + 11 * vEhc.getV(num1, num2), 6, 51 * 1000, cooltime=-1, modifier=modifier).isV(vEhc, num1, num2)
        super(FlamePatternWrapper, self).__init__(skill)

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return chtr.level >= 265

def CrestOfTheSolarBuilder(enhancer, skill_importance, enhance_importance, modifier=core.CharacterModifier(), lang='ko'):
    MitraFlame = MitraFlameWrapper(enhancer, skill_importance, enhance_importance, modifier, lang=lang)
    FlamePattern = FlamePatternWrapper(enhancer, skill_importance, enhance_importance, modifier, lang=lang)
    MitraFlame.onAfter(FlamePattern)
    return MitraFlame, FlamePattern


# Unfinished code. 미완성 코드.
def useful_hyper_body_demonavenger(slevel=1, lang='ko'):
    # Based on delay clas. 딜레이 클라기준.
    return core.BuffSkill(f"{GlobalSkills.DecentHyperBody.value[lang]} (Demon Avenger | 데몬어벤져)", 600, usefulSkillRemain(slevel),
                          pstat_main=40, stat_sub=passiveStat(slevel), rem=False
                          ).wrap(core.BuffSkillWrapper)


def useful_hyper_body_xenon(slevel=1, lang='ko'):
    # Manapup treatment in the job code. 마나뻥 처리는 직업코드에서.
    return core.BuffSkill(f"{GlobalSkills.DecentHyperBody.value[lang]} (Xenon | 제논)", 600, usefulSkillRemain(slevel),
                          stat_main=passiveStat(slevel), stat_sub=passiveStat(slevel), rem=False
                          ).wrap(core.BuffSkillWrapper)
