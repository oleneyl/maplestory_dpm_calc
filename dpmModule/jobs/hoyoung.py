"""Advisor : 아니마님아
"""
from typing import List

from .globalSkill import GlobalSkills
from .jobbranch.thieves import ThiefSkills
from .jobclass.flora import FloraSkills
from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ConcurrentRunRule, ConditionRule, DisableRule, RuleSet
from . import globalSkill, jobutils
from .jobbranch import thieves
from math import ceil
from typing import Any, Dict

import gettext
_ = gettext.gettext

'''
TODO: Reorder in a similar style to other professions. 다른 직업들과 비슷한 스타일로 순서 재정리.
'''


# English skill information for Hoyoung here https://maplestory.fandom.com/wiki/Hoyoung/Skills
class HoyoungSkills:
    # Link Skill
    Bravado = _("자신감")  # "Bravado"
    # Beginner
    ExclusiveSpell = _("익스클루시브 스펠")  # "Exclusive Spell"
    SpiritAffinity = _("정령친화")  # "Spirit Affinity"
    FiendSeal = _("괴이봉인")  # "Fiend Seal"
    # 1st Job
    TalismanEnergy = _("부적 도력")  # "Talisman Energy"
    HumanityAsYouWillFan = _("여의선 : 인")  # "Humanity: As-You-Will Fan"
    TalismanEvilSealingGourd = _("마봉 호로부")  # "Talisman: Evil-Sealing Gourd"
    GracefulFlight = _("초상비")  # "Graceful Flight"
    NimbusCloud = _("근두운")  # "Nimbus Cloud"
    LightSteps = _("경공")  # "Light Steps"
    ShroudingMist = _("무중")  # "Shrouding Mist"
    # 2nd Job
    EarthGroundShatteringWave = _("토파류 : 지")  # "Earth: Ground-Shattering Wave"
    GroundShatteringWaveCloneTrue = _("토파류 : 허/실")  # "Ground-Shattering Wave (Clone/True)"
    TalismanClone = _("환영 분신부")  # "Talisman: Clone"
    RitualFanAcceleration = _("부채 가속")  # "Ritual Fan Acceleration"
    RitualFanMastery = _("부채 숙련")  # "Ritual Fan Mastery"
    OutofSight = _("암행")  # "Out of Sight"
    ThirdEye = _("심안")  # "Third Eye"
    HeavenlyBody = _("운신")  # "Heavenly Body"
    FortuneFitness = _("신체 단련")  # "Fortune Fitness"
    # 3rd Job
    ScrollEnergy = _("두루마리 도력")  # "Scroll Energy"
    HeavenIronFanGale = _("파초풍 : 천")  # "Heaven: Iron Fan Gale"
    IronFanGaleCloneTrue = _("파초풍 : 허/실")  # "Iron Fan Gale (Clone/True)"
    EarthStoneTremor = _("지진쇄 : 지")  # "Earth: Stone Tremor"
    StoneTremorCloneTrue = _("지진쇄 : 허/실")  # "Stone Tremor (Clone／True)"
    TalismanSeekingGhostFlame = _("추적 귀화부")  # "Talisman: Seeking Ghost Flame"
    ScrollDegeneration = _("권술 : 미생강변")  # "Scroll: Degeneration"
    Attainment = _("득의")  # "Attainment"
    Asura = _("수라")  # "Asura"
    DiamondBody = _("금강")  # "Diamond Body"
    BalancedBreath = _("조식")  # "Balanced Breath"
    # 4th Job
    HeavenConsumingFlames = _("멸화염 : 천")  # "Heaven: Consuming Flames"
    ConsumingFlamesCloneTrue = _("멸화염 : 허/실")  # "Consuming Flames (Clone/True)"
    HumanityGoldBandedCudgel = _("금고봉 : 인")  # "Humanity: Gold-Banded Cudgel"
    ThousandTonStone = _("둔갑 천근석")  # "Thousand-Ton Stone"
    TalismanWarpGate = _("왜곡 축지부")  # "Talisman: Warp Gate"
    ScrollStarVortex = _("권술 : 흡성와류")  # "Scroll: Star Vortex"
    ScrollButterflyDream = _("권술 : 호접지몽")  # "Scroll: Butterfly Dream"
    AnimaWarrior = _("아니마의 용사")  # "Anima Warrior"
    AdvancedRitualFanMastery = _("고급 부채 숙련")  # "Advanced Ritual Fan Mastery"
    Enlightenment = _("득도")  # "Enlightenment"
    DragonsEye = _("점정")  # "Dragon's Eye"
    # Hypers
    SageTaiYusMiracleTonic = _("선기 : 영약 태을선단")  # "Sage: Tai Yu's Miracle Tonic"
    SageDreamofShangriLa = _("선기: 몽유도원")  # "Sage: Dream of Shangri-La"
    SageTaiYuClone = _("선기 : 분신 둔갑 태을선인")  # "Sage: Tai Yu Clone"
    # 5th Job
    SageCloneRampage = _("선기 : 극대 분신난무")  # "Sage: Clone Rampage"
    ScrollTigerofSongyu = _("권술 : 산령소환")  # "Scroll: Tiger of Songyu"
    SageWrathofGods = _("선기 : 강림 괴력난신")  # "Sage: Wrath of Gods"
    SageThreePathsApparition = _("선기 : 천지인 환영")  # "Sage: Three Paths Apparition"


class ChunJiInWrapper(core.GraphElement):
    def __init__(self):
        super(ChunJiInWrapper, self).__init__(_("천지인"))

        self.ChunJiIn = {
            _("천"): False,
            _("지"): False,
            _("인"): False
        }
        self.seed = 0
        self.prev_element = None

    def _choice(self, arr):
        # return random.choice(arr)
        idx = self.seed % len(arr)
        self.seed += 1
        return arr[idx]

    def _add_element(self, el):
        self.prev_element = el
        if not self.ChunJiIn[el]:
            self.ChunJiIn[el] = True
        return self._result_object_cache

    def add_element(self, el):
        task = core.Task(self, partial(self._add_element, el))
        return core.TaskHolder(task, name=el)

    def count_elements(self):
        return (int(self.ChunJiIn[_("천")]) + int(self.ChunJiIn[_("지")]) + int(self.ChunJiIn[_("인")]))

    def is_stack(self, stack):
        return self.count_elements() == stack

    def _reset_elements(self):
        for el in self.ChunJiIn.keys():
            self.ChunJiIn[el] = False
        return self._result_object_cache

    def reset_elements(self):
        task = core.Task(self, self._reset_elements)
        return core.TaskHolder(task, name=_("천지인 초기화"))

    def _fill_element(self):
        fillable = [x for x in [_("천"), _("지"), _("인")] if not self.ChunJiIn[x]]
        toFill = self._choice(fillable)
        self.ChunJiIn[toFill] = True
        return self._result_object_cache

    def fill_element(self):
        task = core.Task(self, self._fill_element)
        return core.TaskHolder(task, name=_("속성 연계 완성"))

    def _choice_reset(self, skills: List[core.DamageSkillWrapper]):
        resetable = [x for x in skills if not x.is_available()]
        if len(resetable) == 0:
            resetable = skills
        toReset = self._choice(resetable)
        toReset.reduce_cooltime_p(1)
        return self._result_object_cache

    def choice_reset(self, skills: List[core.DamageSkillWrapper]):
        task = core.Task(self, partial(self._choice_reset, skills))
        return core.TaskHolder(task, name=_("속성 도술 쿨타임 초기화"))

    def check_modifier(self, element):
        if self.prev_element is None:
            return core.CharacterModifier()

        if self.prev_element != element:
            return core.CharacterModifier(pdamage_indep=5)
        else:
            return core.CharacterModifier()


class PausableBuffSkillWrapper(core.BuffSkillWrapper):
    def __init__(self, skill):
        super(PausableBuffSkillWrapper, self).__init__(skill)
        self.pausing_element: core.AbstractSkillWrapper = None

    def spend_time(self, time):
        if self.pausing_element.is_active():
            self.cooltimeLeft -= time
        else:
            return super(PausableBuffSkillWrapper, self).spend_time(time)

    def is_active(self):
        if self.pausing_element.is_active():
            return False
        else:
            return super(PausableBuffSkillWrapper, self).is_active()

    def is_usable(self):
        if self.pausing_element.is_active():
            return False
        else:
            return super(PausableBuffSkillWrapper, self).is_usable()

    def pauseWhile(self, el):
        self.pausing_element = el


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "LUK"
        self.jobname = _("호영")
        self.ability_list = Ability_tool.get_ability_set('passive_level', 'buff_rem', 'mess')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore=20, pdamage=40)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        SpiritAffinity = core.InformedCharacterModifier(HoyoungSkills.SpiritAffinity, summon_rem=10)
        FiendSeal = core.InformedCharacterModifier(HoyoungSkills.FiendSeal, patt=10, pdamage_indep=10)
        RitualFanMastery = core.InformedCharacterModifier(HoyoungSkills.RitualFanMastery, att=25)
        ThirdEye = core.InformedCharacterModifier(HoyoungSkills.ThirdEye, crit=30, crit_damage=10)
        FortuneFitness = core.InformedCharacterModifier(HoyoungSkills.FortuneFitness, stat_main=60)
        Asura = core.InformedCharacterModifier(HoyoungSkills.Asura, att=50, crit=10, crit_damage=20, boss_pdamage=20, armor_ignore=10)
        AdvancedRitualFanMastery = core.InformedCharacterModifier(HoyoungSkills.AdvancedRitualFanMastery, att=40 + passive_level, pdamage_indep=25 + passive_level // 2)
        Enlightenment = core.InformedCharacterModifier(HoyoungSkills.Enlightenment, pdamage=10 + ceil(passive_level/2))
        DragonsEye = core.InformedCharacterModifier(HoyoungSkills.DragonsEye, att=10 + passive_level, pdamage_indep=10 + passive_level, crit=10 + passive_level, crit_damage=10 + passive_level, armor_ignore=10 + passive_level)

        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 0, 0)

        return [SpiritAffinity, FiendSeal, RitualFanMastery, ThirdEye, FortuneFitness, Asura, AdvancedRitualFanMastery, Enlightenment, DragonsEye, ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep=30)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90 + ceil(passive_level / 2))
        return [WeaponConstant, Mastery]

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(DisableRule(HoyoungSkills.HeavenConsumingFlames), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(HoyoungSkills.ScrollDegeneration, HoyoungSkills.ScrollStarVortex, lambda sk: sk.is_time_left(2000, 1)), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(GlobalSkills.TermsAndConditions, HoyoungSkills.SageThreePathsApparition), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(ThiefSkills.LastResort, HoyoungSkills.SageThreePathsApparition), RuleSet.BASE)
        return ruleset

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        """
        Hyper: Heaven and Earth Reinforcement & Boss Killer, Hunting Naturalization Heist, Hypnotic Vortex Heist, Illusion Reinforcement Ignor Guard

        하이퍼 : 천지인 리인포스 & 보스 킬러, 추적 귀화부 헤이스트, 흡성와류 헤이스트, 환영 분신부 이그노어 가드
        """

        passive_level = chtr.get_base_modifier().passive_level + self.combat
        BASIC_HYPER = core.CharacterModifier(pdamage=10, boss_pdamage=15)

        # Primary. 1차.
        ChunJiIn = ChunJiInWrapper()
        TalismanEnergy = core.StackSkillWrapper(core.BuffSkill(HoyoungSkills.TalismanEnergy, 0, 99999999), 100)
        TalismanEnergy.set_name_style("%+d")
        # Assuming a debt blow. 부채 타격 가정.
        YeoUiSeon = core.DamageSkill(HoyoungSkills.HumanityAsYouWillFan, 540 + 30, 560 + 5*passive_level, 5, modifier=BASIC_HYPER + core.CharacterModifier(pdamage_indep=5)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Mabong = core.DamageSkill(HoyoungSkills.TalismanEvilSealingGourd, 360+210, 1000 + 10 * passive_level, 6, modifier=core.CharacterModifier(boss_pdamage=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)  # Absorption 360 Attack 210. 흡수 360 공격 210.

        # Secondary. 2차.
        Topa = core.DamageSkill(HoyoungSkills.EarthGroundShatteringWave, 540 + 30, 385 + 5*passive_level, 4, modifier=BASIC_HYPER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Topa_Clone = core.DamageSkill(HoyoungSkills.GroundShatteringWaveCloneTrue, 0, 385 + 5*passive_level, 4, cooltime=-1, modifier=BASIC_HYPER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Topa.onAfter(Topa_Clone)

        # Both vegetation & pet duration apply. 벞지 & 소환수 지속시간 둘다 적용.
        Talisman_Clone = core.BuffSkill(HoyoungSkills.TalismanClone, 900, 200*1000, rem=True).wrap(PausableBuffSkillWrapper)
        Talisman_Clone_Attack = core.DamageSkill(_("{}(공격)").format(HoyoungSkills.TalismanClone), 0, 60 + 60 + 110 + 2*passive_level, 4 * 3, cooltime=1500, modifier=core.CharacterModifier(armor_ignore=25)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Talisman_Clone_Attack_Opt = core.OptionalElement(lambda : Talisman_Clone.is_active() and Talisman_Clone_Attack.is_available(), Talisman_Clone_Attack)
        Talisman_Clone_Attack.protect_from_running()

        Booster = core.BuffSkill(HoyoungSkills.RitualFanAcceleration, 0, 200*1000, rem=True).wrap(core.BuffSkillWrapper)  # Pet buff. 펫버프.

        # 3rd. 3차.
        ScrollEnergy = core.StackSkillWrapper(core.BuffSkill(HoyoungSkills.ScrollEnergy, 0, 99999999), 900)
        ScrollEnergy.set_name_style("%+d")
        Pacho = core.DamageSkill(HoyoungSkills.HeavenIronFanGale, 510 + 60, 265 + 2*passive_level, 5, modifier=BASIC_HYPER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Pacho_Clone = core.DamageSkill(HoyoungSkills.IronFanGaleCloneTrue, 0, 265 + 2*passive_level, 5, modifier=BASIC_HYPER, cooltime=-1).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Pacho.onAfter(Pacho_Clone)

        EarthQuake = core.DamageSkill(HoyoungSkills.EarthStoneTremor, 510 + 30, 390 + 5*passive_level, 6, modifier=BASIC_HYPER, cooltime=6000, red=True).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        EarthQuake_Clone = core.DamageSkill(HoyoungSkills.StoneTremorCloneTrue, 0, 390 + 5*passive_level, 6, modifier=BASIC_HYPER, cooltime=-1).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        EarthQuake.onAfter(EarthQuake_Clone)

        Talisman_Seeker = core.SummonSkill(HoyoungSkills.TalismanSeekingGhostFlame, 630, 1800 * 0.75, 390 + 5*passive_level, 5, 40*1000, rem=True).setV(vEhc, 0, 2, True).wrap(core.SummonSkillWrapper)

        Misaeng = core.DamageSkill(HoyoungSkills.ScrollDegeneration, 540, 850 + 4*self.combat, 8, modifier=core.CharacterModifier(boss_pdamage=20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Misaeng_Debuff = core.BuffSkill(_("{}(디버프)").format(HoyoungSkills.ScrollDegeneration), 0, 60*1000, armor_ignore=20, cooltime=-1).wrap(core.BuffSkillWrapper)
        Misaeng.onAfter(Misaeng_Debuff)

        # 4th. 4차.
        Flames = core.DamageSkill(HoyoungSkills.HeavenConsumingFlames, 420 + 60, 340 + self.combat, 6, modifier=BASIC_HYPER, cooltime=8000, red=True).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Flames_Clone = core.DamageSkill(HoyoungSkills.ConsumingFlamesCloneTrue, 0, 340 + self.combat, 6, modifier=BASIC_HYPER, cooltime=-1).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Flames.onAfter(Flames_Clone)

        GeumGoBong = core.DamageSkill(_("{}(1타)").format(HoyoungSkills.HumanityGoldBandedCudgel), 330 + 30, 260 + 3*self.combat, 10, cooltime=11000, red=True, modifier=BASIC_HYPER + core.CharacterModifier(boss_pdamage=30)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        GeumGoBong_2 = core.DamageSkill(_("{}(2타)").format(HoyoungSkills.HumanityGoldBandedCudgel), 300 + 30, 420 + self.combat, 8, cooltime=-1, modifier=BASIC_HYPER + core.CharacterModifier(boss_pdamage=30)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        GeumGoBong.onAfter(GeumGoBong_2)

        # Estimated delay (frame analysis from jump to complete loss of effect). 추정치 딜레이 (점프부터 이펙트 완전소멸까지 프레임 분석).
        Thousand_Ton_Stone = core.DamageSkill(HoyoungSkills.ThousandTonStone, 1530, 275 + 3*self.combat, 6, cooltime=500).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Thousand_Ton_Stone_DOT = core.DotSkill(_("{}(출혈)").format(HoyoungSkills.ThousandTonStone), 0, 1000, 270 + self.combat, 1, 10000, cooltime=-1).setV(vEhc, 0, 2, False).wrap(core.DotSkillWrapper)
        Thousand_Ton_Stone.onAfter(Thousand_Ton_Stone_DOT)

        Waryu = core.SummonSkill(HoyoungSkills.ScrollStarVortex, 990, 1000 * 0.8, 240 + 4*self.combat, 6, 40000, rem=True).setV(vEhc, 0, 2, True).wrap(core.SummonSkillWrapper)

        Butterfly_Dream = core.BuffSkill(HoyoungSkills.ScrollButterflyDream, 600, 100*1000, rem=True, pdamage_indep=10).wrap(core.BuffSkillWrapper)
        Butterfly_Dream_Attack = core.DamageSkill(_("{}(공격)").format(HoyoungSkills.ScrollButterflyDream), 0, 275 + 3 * self.combat, 5, cooltime=1000).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Butterfly_Dream_Attack_Opt = core.OptionalElement(Butterfly_Dream_Attack.is_available, Butterfly_Dream_Attack)
        Butterfly_Dream_Attack.protect_from_running()

        # Hyper Active. 하이퍼 액티브.
        Miracle_Tonic = core.BuffSkill(HoyoungSkills.SageTaiYusMiracleTonic, 540, 12*1000, cooltime=100*1000).wrap(core.BuffSkillWrapper)
        Miracle_Tonic_Charge = core.SummonSkill(_("{}(회복)").format(HoyoungSkills.SageTaiYusMiracleTonic), 0, 1000, 0, 0, 12*1000, cooltime=-1).wrap(core.SummonSkillWrapper)
        Miracle_Tonic.onAfter(Miracle_Tonic_Charge)

        CloneBinding = core.DamageSkill(HoyoungSkills.SageTaiYuClone, 540, 800, 8, cooltime=200000).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)

        # 5th common (Venom burst omitted). 5차 공용 (베놈 버스트 생략).
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 0, 0)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # Goddess Grandis' blessing (no). 그란디스 여신의 축복 (아니마).
        # Anima Make public code when a new job appears. 아니마 신직업 등장시 공용코드화 할것.
        AnimaGoddessBless = core.BuffSkill(_("{}(아니마)").format(FloraSkills.GrandisGoddessBlessing), 0, 40*1000, cooltime=240*1000, red=True, pdamage=10 + vEhc.getV(0, 0)).isV(vEhc, 0, 0).wrap(core.BuffSkillWrapper)

        # A skill that replaces the phantom alter ego (algorithm implementation required). 환영 분신부를 대체하는 스킬 (알고리즘 구현 필요).
        # Can only be used during the duration of the illusionist, and the duration of the illusionist is not reduced while active. 환영 분신부 지속중에만 사용가능, 발동 중에는 환영 분신부의 지속시간이 감소하지 않음.
        Clone_Rampage = core.BuffSkill(HoyoungSkills.SageCloneRampage, 900, 30*1000, cooltime=200*1000, red=True).wrap(core.BuffSkillWrapper)
        Clone_Rampage_Attack = core.DamageSkill(_("{}(공격)").format(HoyoungSkills.SageCloneRampage), 0, 60 + 60 + 110 + 2*passive_level + 200 + vEhc.getV(0, 0) * 8, 4 * 10, cooltime=1500, modifier=core.CharacterModifier(armor_ignore=25)).setV(vEhc, 0, 2, True).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        Clone_Rampage_Attack_Opt = core.OptionalElement(lambda : Clone_Rampage.is_active() and Clone_Rampage_Attack.is_available(), Clone_Rampage_Attack)
        Clone_Rampage_Attack.protect_from_running()

        Summon_Sanryung = core.SummonSkill(HoyoungSkills.ScrollTigerofSongyu, 900, 3000, 0, 0, (vEhc.getV(0, 0)//2 + 45)*1000, cooltime=200*1000, red=True).wrap(core.SummonSkillWrapper)
        Summon_Sanryung_Normal = core.DamageSkill(_("{}(일반)").format(HoyoungSkills.ScrollTigerofSongyu), 0, vEhc.getV(0, 0)*36 + 900, 8, cooltime=-1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Summon_Sanryung_Roar = core.DamageSkill(_("{}(포효)").format(HoyoungSkills.ScrollTigerofSongyu), 0, vEhc.getV(0, 0)*14 + 350, 7*4, cooltime=-1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)  # 7 reps of 4 strokes. 4타씩 7회.
        Summon_Sanryung_Check = core.StackSkillWrapper(core.BuffSkill(_("{}(포효 가능)").format(HoyoungSkills.ScrollTigerofSongyu), 0, 99999999), 1)

        Nansin = core.BuffSkill(HoyoungSkills.SageWrathofGods, 900, 30*1000, cooltime=200*1000, red=True, pdamage=vEhc.getV(0, 0)*2+20).wrap(core.BuffSkillWrapper)
        Nansin_Stack = core.StackSkillWrapper(core.BuffSkill(_("{}(스택)").format(HoyoungSkills.SageWrathofGods), 0, 99999999), 12)
        Nansin_Attack = core.DamageSkill(_("{}(신들의 일격)").format(HoyoungSkills.SageWrathofGods), 0, vEhc.getV(0, 0)*34 + 850, 8, cooltime=1500).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Nansin_Final = core.DamageSkill(_("{}(신들의 강림)").format(HoyoungSkills.SageWrathofGods), 2850, vEhc.getV(0, 0)*40+1000, 15*6, cooltime=-1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Nansin_Final_Buff = core.BuffSkill(_("{}(신들의 강림)(버프)").format(HoyoungSkills.SageWrathofGods), 0, 30000, cooltime=-1).wrap(core.BuffSkillWrapper)

        Nansin_Attack_Opt = core.OptionalElement(lambda: Nansin_Stack.judge(12, 1), Nansin_Attack)
        Nansin_Attack.protect_from_running()

        Elemental_Clone_Passive = core.DamageSkill(_("{}(패시브)").format(HoyoungSkills.SageThreePathsApparition), 0, 625 + 25*vEhc.getV(0, 0), 6, cooltime=5000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Elemental_Clone_Passive_Opt = core.OptionalElement(Elemental_Clone_Passive.is_available, Elemental_Clone_Passive)
        Elemental_Clone_Passive.protect_from_running()

        Elemental_Clone = core.BuffSkill(HoyoungSkills.SageThreePathsApparition, 540, 30*1000, cooltime=100*1000, red=True).wrap(core.BuffSkillWrapper)
        Elemental_Clone_Active = core.DamageSkill(_("{}(액티브)").format(HoyoungSkills.SageThreePathsApparition), 0, 625 + 25*vEhc.getV(0, 0), 6, cooltime=2000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Elemental_Clone_Active_Stack = core.StackSkillWrapper(core.BuffSkill(_("{}(재등장 스택)").format(HoyoungSkills.SageThreePathsApparition), 0, 99999999), 2)
        Elemental_Clone.onAfter(Elemental_Clone_Active_Stack.stackController(2))

        Elemental_Clone_Active_Opt = core.OptionalElement(Elemental_Clone_Active.is_available, Elemental_Clone_Active)
        Elemental_Clone_Active.protect_from_running()

        Elemental_Clone_Opt = core.OptionalElement(Elemental_Clone.is_active, Elemental_Clone_Active_Opt, Elemental_Clone_Passive_Opt)

        ### Skill Wrapper ###
        # Goddess Grandis' blessing (no). 그란디스 여신의 축복(아니마).
        def gainEnergy(energy: core.StackSkillWrapper, stack):
            return core.OptionalElement(
                AnimaGoddessBless.is_active,
                energy.stackController(stack*0.01*(100+45+vEhc.getV(0, 0))),
                energy.stackController(stack),
                name=_("그여축(도력 충전량)")
            )

        # Connection with Heaven and Earth. 천지인 연계.
        AddChun = ChunJiIn.add_element(_("천"))
        AddJi = ChunJiIn.add_element(_("지"))
        AddIn = ChunJiIn.add_element(_("인"))
        FillElement = ChunJiIn.fill_element()
        GainScroll = gainEnergy(ScrollEnergy, 15)
        GainTalisman1 = core.OptionalElement(partial(ChunJiIn.is_stack, 1), gainEnergy(TalismanEnergy, 10), name=_("1속성"))
        GainTalisman2 = core.OptionalElement(partial(ChunJiIn.is_stack, 2), gainEnergy(TalismanEnergy, 15), name=_("2속성"))
        GainTalisman3 = core.OptionalElement(partial(ChunJiIn.is_stack, 3), gainEnergy(TalismanEnergy, 20), name=_("3속성"))
        TriggerSanryung = core.OptionalElement(partial(ChunJiIn.is_stack, 3), Summon_Sanryung_Check.stackController(1))
        ElementalCloneReset = core.OptionalElement(
            partial(ChunJiIn.is_stack, 3),
            core.OptionalElement(Elemental_Clone.is_active, ChunJiIn.choice_reset([EarthQuake, Flames, GeumGoBong]))
        )
        ChunJiInReset = core.OptionalElement(partial(ChunJiIn.is_stack, 3), ChunJiIn.reset_elements(), name=_("3속성 초기화"))
        for el in [AddChun, AddJi, AddIn, FillElement]:
            el.onAfter(GainScroll)
            el.onAfter(GainTalisman1)
            el.onAfter(GainTalisman2)
            el.onAfter(GainTalisman3)
            el.onAfter(TriggerSanryung)
            el.onAfter(ElementalCloneReset)
            el.onAfter(ChunJiInReset)

        for sk in [Pacho, Flames]:
            sk.onAfter(AddChun)

        for sk in [Pacho, Pacho_Clone, Flames, Flames_Clone]:
            sk.add_runtime_modifier(ChunJiIn, lambda sk: sk.check_modifier("천"))

        for sk in [Topa, EarthQuake]:
            sk.onAfter(AddJi)

        for sk in [Topa, Topa_Clone, EarthQuake, EarthQuake_Clone]:
            sk.add_runtime_modifier(ChunJiIn, lambda sk: sk.check_modifier("지"))

        for sk in [YeoUiSeon, GeumGoBong]:
            sk.onAfter(AddIn)

        for sk in [YeoUiSeon, GeumGoBong, GeumGoBong_2]:
            sk.add_runtime_modifier(ChunJiIn, lambda sk: sk.check_modifier(_("인")))

        # Amulet swordsmanship. 부적 도술.
        TalismanConstraint = core.ConstraintElement(f"{HoyoungSkills.TalismanEnergy} 100", TalismanEnergy, partial(TalismanEnergy.judge, 100, 1))
        TalismanConsume = TalismanEnergy.stackController(-100)
        TalismanConsume.onAfter(gainEnergy(ScrollEnergy, 200))
        for sk in [Mabong, Talisman_Clone, Talisman_Seeker]:
            sk.onConstraint(TalismanConstraint)
            sk.onAfter(TalismanConsume)

        # Scroll swordsmanship. 두루마리 도술.
        ScrollConstraint = core.ConstraintElement(f"{HoyoungSkills.ScrollEnergy} 900", ScrollEnergy, partial(ScrollEnergy.judge, 900, 1))
        ScrollConsume = ScrollEnergy.stackController(-900)
        for sk in [Misaeng, Waryu, Butterfly_Dream, Summon_Sanryung]:
            sk.onConstraint(ScrollConstraint)
            sk.onAfter(ScrollConsume)

        # Taeeul Seondan. 태을선단.
        Miracle_Tonic_Charge.onTick(gainEnergy(TalismanEnergy, 35))
        Miracle_Tonic_Charge.onTick(gainEnergy(ScrollEnergy, 350))

        # The greatest self-immolation. 극대 분신난무.
        Clone_Rampage.onConstraint(core.ConstraintElement(_("환영 분신부 지속중"), Talisman_Clone, Talisman_Clone.is_active))
        Clone_Rampage.onAfter(Talisman_Clone.controller(1))
        Talisman_Clone.pauseWhile(Clone_Rampage)

        # Superpowerful god. 괴력난신.
        Nansin.onAfter(Nansin_Final.controller(30*1000-1))  # Last hit just before the buff ends. 버프 종료 직전에 막타 발동.
        Nansin.onAfter(Nansin_Stack.stackController(-12))
        Nansin_Attack.onAfter(Nansin_Stack.stackController(-12))
        AddNansinStack = core.OptionalElement(Nansin.is_active, Nansin_Stack.stackController(1))
        AddNansinStack.onAfter(Nansin_Attack_Opt)
        Nansin_Final.onAfter(Nansin_Final_Buff)

        # Summon mountain spirit. 산령소환.
        Summon_Sanryung.onTick(core.OptionalElement(
            partial(Summon_Sanryung_Check.judge, 1, 1),
            Summon_Sanryung_Roar,
            Summon_Sanryung_Normal
        ))
        Summon_Sanryung_Roar.onAfter(Summon_Sanryung_Check.stackController(-1))

        # Welcome to Heaven and Earth. 천지인 환영.
        Elemental_Clone_Passive.onAfter(FillElement)
        Elemental_Clone_Active.onAfter(FillElement)

        Elemental_Clone_Active_Reset = Elemental_Clone_Active.controller(1, "reduce_cooltime_p")
        Elemental_Clone_Active.onAfter(core.OptionalElement(partial(Elemental_Clone_Active_Stack.judge, 1, 1), Elemental_Clone_Active_Reset))
        Elemental_Clone_Active_Reset.onAfter(Elemental_Clone_Active_Stack.stackController(-1))

        # For 30 seconds after the advent of the gods, the damage of the thousand/ji/in attribute skills and heo/sil skills increases by 20%. 신들의 강림 후 30초동안 천/지/인 속성 스킬 및 허/실 스킬의 데미지 20% 증가.
        ELEMENT_SKILLS = [YeoUiSeon, Topa, Topa_Clone, Pacho, Pacho_Clone, EarthQuake, EarthQuake_Clone, Flames, Flames_Clone, GeumGoBong, GeumGoBong_2]
        for sk in ELEMENT_SKILLS:
            sk.add_runtime_modifier(Nansin_Final_Buff, lambda sk: core.CharacterModifier(pdamage=20*sk.is_active()))

        # Welcoming spontaneous bride, maximal spontaneous frenzy, Phalaenopsis dream, celestial spirit phantom, supernatural power. 환영 분신부, 극대 분신난무, 호접지몽, 천지인 환영, 괴력난신.
        for base in ELEMENT_SKILLS + [Mabong, Misaeng, CloneBinding]:
            for opt in [Talisman_Clone_Attack_Opt, Clone_Rampage_Attack_Opt, Butterfly_Dream_Attack_Opt, Elemental_Clone_Opt, AddNansinStack]:
                base.onAfter(opt)

        # Extra strokes are counted for the superpowers. 추가타가 괴력난신 카운트에 들어감.
        for sk, stack in [(Talisman_Clone_Attack, 3), (Clone_Rampage_Attack, 10), (Butterfly_Dream_Attack, 5), (Elemental_Clone_Active, 1), (Elemental_Clone_Passive, 1)]:
            sk.onAfter(core.OptionalElement(Nansin.is_active, Nansin_Stack.stackController(stack)))
            sk.onAfter(Nansin_Attack_Opt)

        # Pacho Wind-Annihilation Flame-Inskill (Topa cannot be cast in the air). 파초풍-멸화염-인스킬(토파류 공중시전 불가).
        Flames.onBefore(Pacho)
        Flames.onAfter(core.OptionalElement(GeumGoBong.is_available, GeumGoBong, YeoUiSeon))

        # scheduling - start with full gauge
        TalismanEnergy.vary(100)
        ScrollEnergy.vary(900)

        return (
            Topa,
            [
                globalSkill.maple_heros(chtr.level, name=HoyoungSkills.AnimaWarrior, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                Booster,
                Talisman_Clone,
                Butterfly_Dream,
                Clone_Rampage,
                Nansin,
                Elemental_Clone,
                Miracle_Tonic,
                AnimaGoddessBless,
                ReadyToDie,
                globalSkill.soul_contract()
            ]
            + [Talisman_Seeker, Waryu, Summon_Sanryung]
            + [Nansin_Final]  # reserved task, use early as possible
            + [GeumGoBong, EarthQuake, Flames, Mabong, Misaeng, CloneBinding, MirrorBreak, MirrorSpider]
            + [
                Miracle_Tonic_Charge,
                Nansin_Final_Buff,
                Misaeng_Debuff,
                Talisman_Clone_Attack,
                Butterfly_Dream_Attack,
                Clone_Rampage_Attack,
                Elemental_Clone_Active,
                Elemental_Clone_Passive,
                Nansin_Attack,
            ]  # Not used from scheduler
            + [Topa]
        )
