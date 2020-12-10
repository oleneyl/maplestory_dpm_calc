from dpmModule.character.characterKernel import AbstractCharacter
from ..kernel import core
import math


def usefulSkillRemain(slevel=1): return (180+slevel*3)*1000


def passiveStat(slevel=1): return (slevel+4)/5


def soul_contract():
    return core.BuffSkill("소울 컨트랙트", 900, 10*1000, cooltime=90000, pdamage=45, rem=True, red=True).wrap(core.BuffSkillWrapper)


# combat_level: 제로 = 0, 팔라딘 = 2, 이외 직업은 self.combat 입력
def maple_heros(level, name="메이플 용사", combat_level=0):
    return core.BuffSkill(name, 0, (900+15*combat_level)*1000,
                          stat_main=math.ceil(15+combat_level/2)*0.01*(25+level*5), rem=True
                          ).wrap(core.BuffSkillWrapper)


# 1레벨 고정 (레벨당 보너스가 내성이므로)
def useful_combat_orders():
    return core.BuffSkill("쓸만한 컴뱃 오더스", 1500, usefulSkillRemain(), rem=False).wrap(core.BuffSkillWrapper)


def useful_sharp_eyes(slevel=1):
    return core.BuffSkill("쓸만한 샤프 아이즈", 900, usefulSkillRemain(slevel), rem=False, crit=10, crit_damage=8,
                          stat_main=passiveStat(slevel), stat_sub=passiveStat(slevel)).wrap(core.BuffSkillWrapper)


def useful_wind_booster(slevel=1):
    return core.BuffSkill("쓸만한 윈드 부스터", 900, usefulSkillRemain(slevel), rem=False,
                          stat_main=passiveStat(slevel), stat_sub=passiveStat(slevel)
                          ).wrap(core.BuffSkillWrapper)


# TODO: 제논, 데몬어벤져용 각각 분리
def useful_advanced_bless(slevel=1):
    return core.BuffSkill("쓸만한 어드밴스드 블레스", 600, usefulSkillRemain(slevel), rem=False, att=20).wrap(core.BuffSkillWrapper)


class MirrorBreakWrapper(core.DamageSkillWrapper):
    def __init__(self, vEhc, num1, num2, modifier) -> None:
        skill = core.DamageSkill("스파이더 인 미러(공간 붕괴)", 720, 450+18*vEhc.getV(num1, num2), 15, cooltime=250*1000, red=True, modifier=modifier)
        super(MirrorBreakWrapper, self).__init__(skill)

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return chtr.level >= 235


class MirrorSpiderWrapper(core.SummonSkillWrapper):
    # 5번 연속 공격 후 종료, 재돌입 대기시간 3초
    def __init__(self, vEhc, num1, num2, modifier) -> None:
        self.delays = [900, 850, 750, 650, 5730]  # 400001039.summonedSequenceAttack에서 가져온 딜레이, 5회째 공격 후 눈 감고뜨는 시간 5730ms
        self.hit_count = 0
        skill = core.SummonSkill("스파이더 인 미러(거울 속의 거미)", 0, 900, 175+7*vEhc.getV(num1, num2), 8, 50*1000, cooltime=-1, modifier=modifier)
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


# 모험가, 영웅, 레지스탕스가 사용
def MapleHeroes2Wrapper(vEhc, num1, num2, level, combat_level):
    return core.BuffSkill("메이플월드 여신의 축복", 450, 60*1000,
                          stat_main=(2+vEhc.getV(num1, num2)/10)*math.ceil(15+combat_level/2)*0.01*(25+level*5),
                          pdamage=5+vEhc.getV(num1, num2)//2, cooltime=180*1000, red=True
                          ).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)


class TandadianRuinWrapper(core.BuffSkillWrapper):
    def __init__(self) -> None:
        skill = core.BuffSkill("파괴의 얄다바오트", 0, 30000, cooltime=90000, pdamage_indep=15, rem=False, red=False)
        super(TandadianRuinWrapper, self).__init__(skill)

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return False


class AeonianRiseWrapper(core.DamageSkillWrapper):
    def __init__(self) -> None:
        skill = core.DamageSkill("창조의 아이온", 0, 1500, 7, cooltime=180000, red=False)
        super(AeonianRiseWrapper, self).__init__(skill)

    def ensure(self, chtr: AbstractCharacter) -> bool:
        return False


def GenesisSkillBuilder():
    return TandadianRuinWrapper(), AeonianRiseWrapper()


# 미완성 코드
def useful_hyper_body_demonavenger(slevel=1):
    # 딜레이 클라기준
    return core.BuffSkill("쓸만한 하이퍼 바디 (데몬어벤져)", 600, usefulSkillRemain(slevel),
                          pstat_main=40, stat_sub=passiveStat(slevel), rem=False
                          ).wrap(core.BuffSkillWrapper)


def useful_hyper_body_xenon(slevel=1):
    # 마나뻥 처리는 직업코드에서
    return core.BuffSkill("쓸만한 하이퍼 바디 (제논)", 600, usefulSkillRemain(slevel),
                          stat_main=passiveStat(slevel), stat_sub=passiveStat(slevel), rem=False
                          ).wrap(core.BuffSkillWrapper)
