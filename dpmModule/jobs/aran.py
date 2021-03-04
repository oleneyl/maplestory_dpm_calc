from dpmModule.jobs.globalSkill import GlobalSkills, ONE_HIT, CAST, THREE_HIT, TWO_HIT, BUFF, WAVE, CANCEL, HOLDER

from ..kernel import core
from ..kernel.graph import DynamicVariableOperation
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import warriors
from ..execution.rules import ComplexConditionRule, RuleSet, InactiveRule, ConditionRule
from math import ceil
from typing import Any, Dict
from .globalSkill import PASSIVE

from localization.utilities import translator
_ = translator.gettext


# English skill information for Aran here https://maplestory.fandom.com/wiki/Aran/Skills
class AranSkills:
    # Beginner
    RegainedMemory = _("되찾은 기억")  # "Regained Memory"
    # 1st Job
    ComboAbility = _("콤보 어빌리티")  # "Combo Ability"
    SmashSwing = _("스매시 스윙")  # "Smash Swing"
    SmashWave = _("스매쉬 웨이브")  # "Smash Wave"
    PolearmBooster = _("폴암 부스터")  # "Polearm Booster"
    BodyPressure = _("바디 프레셔")  # "Body Pressure"
    # 2nd Job
    PolearmMastery = _("폴암 마스터리")  # "Polearm Mastery"
    FinalCharge = _("파이널 차지")  # "Final Charge"
    Drain = _("드레인")  # "Drain"
    SnowCharge = _("스노우 차지")  # "Snow Charge"
    PhysicalTraining = _("피지컬 트레이닝")  # "Physical Training"
    FinalAttack = _("파이널 어택")  # "Final Attack"
    FinalToss = _("파이널 토스")  # "Final Toss"
    RollingSpin = _("롤링 스핀")  # "Rolling Spin"
    CommandMasteryI = _("다이나믹 마스터리 Ⅰ")  # "Command Mastery I"
    SwingStudiesI = _("스윙 연구 Ⅰ")  # "Swing Studies I"
    # 3rd Job
    AdvancedComboAbility = _("어드밴스드 콤보 어빌리티")  # "Advanced Combo Ability"
    CleavingBlows = _("클리빙 어택")  # "Cleaving Blows"
    MahaBlessing = _("블레싱 마하")  # "Maha Blessing"
    AeroSwing = _("에어로 스윙")  # "Aero Swing"
    AdrenalineRush = _("아드레날린 부스트")  # "Adrenaline Rush"
    FinalBlow = _("파이널 블로우")  # "Final Blow"
    JudgmentDraw = _("저지먼트")  # "Judgment Draw"
    GatheringHook = _("게더링 캐쳐")  # "Gathering Hook"
    Might = _("마이트")  # "Might"
    # 4th Job
    HighMastery = _("하이 마스터리")  # "High Mastery"
    SuddenStrike = _("스위프트 무브")  # "Sudden Strike"
    AdvancedFinalAttack = _("어드밴스드 파이널 어택")  # "Advanced Final Attack"
    BeyondBlade = _("비욘더")  # "Beyond Blade"
    FinisherStormofFear = _("부스트 엔드-스톰 오브 피어")  # "Finisher - Storm of Fear"
    FinisherHuntersPrey = _("부스트 엔드-헌터즈 타겟팅")  # "Finisher - Hunter"s Prey"
    CommandMasteryII = _("다이나믹 마스터리 II")  # "Command Mastery II"
    SwingStudiesII = _("스윙 연구 II")  # "Swing Studies II"
    # Hypers
    MahasDomain = _("마하의 영역")  # "Maha's Domain"
    HeroicMemories = _("히어로즈 오쓰")  # "Heroic Memories"
    AdrenalineBurst = _("아드레날린 제네레이터")  # "Adrenaline Burst"
    # 5th Job
    MahasFury = _("인스톨 마하")  # "Maha's Fury"
    MahasCarnage = _("브랜디쉬 마하")  # "Maha's Carnage"
    FenrirCrash = _("펜릴 크래시")  # "Fenrir Crash"
    BlizzardTempest = _("블리자드 템페스트")  # "Blizzard Tempest"
    

# Skill name modifiers only for Aran
COMBO = _("콤보")
SNOWSTORM = _("눈보라")
ICEBURG = _("빙산")
CURSE = _("저주")

# Advisor : Azir carry (croa). 아지르캐리(크로아)
# Assumes the lowest combo count of 500. 최저 콤보 카운트 500 가정
# TODO : If a skill other than Final Blow comes after the Penril Crash, a 30ms delay should be added. 펜릴 크래시 이후에 파이널 블로우가 아닌 다른 스킬이 오면 30ms 딜레이가 추가되어야 함
# TODO : Freed and Aura weapon delays must be canceled as a gathering catcher. 게더링 캐쳐로 프리드, 오라웨폰 딜레이도 캔슬해야 함.
class AdrenalineDamageWrapper(core.DamageSkillWrapper):
    def __init__(
        self,
        skill: core.DamageSkill,
        adrenaline: core.BuffSkillWrapper,
        activation: int = 1,  # handle random hit (final attack)
    ):
        super(AdrenalineDamageWrapper, self).__init__(skill)
        self.adrenaline = adrenaline
        self.activation = activation

    def get_hit(self) -> float:
        return (
            min(
                super(AdrenalineDamageWrapper, self).get_hit()
                + 2 * self.adrenaline.is_active(),
                15,
            )
            * self.activation
        )

    def get_damage(self) -> float:
        return (
            super(AdrenalineDamageWrapper, self).get_damage()
            + 150 * self.adrenaline.is_active()
        )

    def onAdrenalineAfter(self, skill: core.AbstractSkillWrapper):
        self.onAfter(core.OptionalElement(self.adrenaline.is_active, skill))


class AdrenalineSummonWrapper(core.SummonSkillWrapper):
    def __init__(
        self,
        skill: core.DamageSkill,
        adrenaline: core.BuffSkillWrapper,
    ):
        super(AdrenalineSummonWrapper, self).__init__(skill)
        self.adrenaline = adrenaline

    def get_damage(self) -> float:
        return (
            super(AdrenalineSummonWrapper, self).get_damage()
            + 150 * self.adrenaline.is_active()
        )


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "STR"
        self.jobname = _("아란")
        self.vEnhanceNum = 13
        self.ability_list = Ability_tool.get_ability_set(
            "boss_pdamage", "crit", "buff_rem"
        )
        self.preEmptiveSkills = 2

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=50, armor_ignore=20, patt=15)

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        RetrievedMemory = core.InformedCharacterModifier(AranSkills.RegainedMemory, patt=5)
        SnowChargePassive = core.InformedCharacterModifier(f"{AranSkills.SnowCharge}({PASSIVE})", pdamage=10)
        PhisicalTraining = core.InformedCharacterModifier(AranSkills.PhysicalTraining, stat_main=30, stat_sub=30)
        AdvancedComboAbilityPassive = core.InformedCharacterModifier(AranSkills.AdvancedComboAbility, att=10, crit=20, crit_damage=10)
        CleavingAttack = core.InformedCharacterModifier(AranSkills.CleavingBlows, armor_ignore=40, pdamage=10)
        Might = core.InformedCharacterModifier(AranSkills.Might, att=40)
        HighMastery = core.InformedCharacterModifier(AranSkills.HighMastery, att=30 + passive_level, crit_damage=8)
        AdvancedFinalAttackPassive = core.InformedCharacterModifier(f"{AranSkills.AdvancedFinalAttack}({PASSIVE})", att=30 + passive_level)

        return [
            RetrievedMemory,
            SnowChargePassive,
            PhisicalTraining,
            AdvancedComboAbilityPassive,
            CleavingAttack,
            Might,
            HighMastery,
            AdvancedFinalAttackPassive,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep=49)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90+ceil(passive_level / 2))
        ComboAbility = core.InformedCharacterModifier(f"{AranSkills.ComboAbility}({COMBO})", att=2 * 10)
        AdvancedComboAbility = core.InformedCharacterModifier(f"{AranSkills.AdvancedComboAbility}({COMBO})", att=2 * 10, crit=3 * 10)
        return [WeaponConstant, Mastery, ComboAbility, AdvancedComboAbility]

    def get_ruleset(self):
        def hunters_targeting_rule(hunters, adrenaline, soul_contract):
            if soul_contract.is_active():
                return True
            if soul_contract.cooltimeLeft < adrenaline.timeLeft:
                return False
            return True

        ruleset = RuleSet()
        ruleset.add_rule(InactiveRule(f"{AranSkills.MahasCarnage}({HOLDER})", AranSkills.AdrenalineRush), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(GlobalSkills.DecentSharpEyes, AranSkills.AdrenalineRush), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(GlobalSkills.DecentCombatOrders, AranSkills.AdrenalineRush), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(GlobalSkills.TermsAndConditions, AranSkills.AdrenalineRush, lambda sk: sk.is_time_left(10 * 1000, 1)),RuleSet.BASE)
        ruleset.add_rule(ComplexConditionRule(f"{AranSkills.FinisherHuntersPrey}({HOLDER})", [AranSkills.AdrenalineRush, GlobalSkills.TermsAndConditions],hunters_targeting_rule), RuleSet.BASE)

        return ruleset

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Hyper: Beyond (3 types)
        Swing-Remain Time Reinforce
        Adrenaline Boost-Persist

        Core Enhancement Order Apa-Pavel-Beyonder-Hunters Targeting-Smashing Wing

        Brandish Mach / Install Mach / Mach's Area: Canceled by Gathering Catcher (600ms)
        Do not use the following during adrenaline boost: Brandish Mach, Heroes Oth, Worthy Sharp Eyes
        Soul contract is used if adrenaline boost is 10 seconds or more left.

        하이퍼 : 비욘더(3종)
        스윙 - 리메인타임 리인포스
        아드레날린 부스트 - 퍼시스트

        코어강화 순서 어파-파블-비욘더-헌터즈타겟팅-스매시스윙

        브랜디쉬 마하 / 인스톨 마하 / 마하의 영역 : 게더링 캐쳐로 캔슬(30ms + 570ms)
        아드레날린 부스트 도중에 다음을 사용하지 않음 : 브랜디쉬 마하, 쓸만한 샤프 아이즈
        소울 컨트랙트는 아드레날린 부스트가 10초 이상 남았다면 사용함
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        BOOST_END_HUNTERS_TARGETING_DELAY = 600
        ADRENALINE_BOOST_REMAIN = (20 + 3) * 1000
        ADRENALINE_BOOST_PASSIVE = 100
        SWIFT_MOVE = 60 + 2 * passive_level
        DYNAMIC_MASTERY = 20 + passive_level

        # reinforce: hyper skill reinforce
        def get_beyonder_pdamage(excess_target, reinforce=True):
            return (1.06 ** excess_target - 1) * 100 + reinforce * 20

        BEYONDER_PDAMAGE = get_beyonder_pdamage(5)
        PENRIL_PDAMAGE = get_beyonder_pdamage(9)

        # Pet buff. 펫버프
        Booster = core.BuffSkill(AranSkills.PolearmBooster, 0, 180 * 1000, rem=True).wrap(core.BuffSkillWrapper)
        SnowCharge = core.BuffSkill(AranSkills.SnowCharge, 0, 200 * 1000, pdamage=10).wrap(core.BuffSkillWrapper)
        BlessingMaha = core.BuffSkill(AranSkills.MahaBlessing, 0, 200 * 1000, att=30).wrap(core.BuffSkillWrapper)

        AdrenalineBoost = core.BuffSkill(AranSkills.AdrenalineRush, delay=0, remain=ADRENALINE_BOOST_REMAIN).wrap(core.BuffSkillWrapper)

        SmashSwing = AdrenalineDamageWrapper(
            core.DamageSkill(
                AranSkills.SmashSwing,
                delay=360,
                damage=150
                + 200
                + 100
                + (250 + 50 * passive_level)
                + ADRENALINE_BOOST_PASSIVE
                + DYNAMIC_MASTERY,
                hit=2,
            ).setV(vEhc, 4, 2, False),
            AdrenalineBoost,
        )
        SmashSwingIncr = core.BuffSkill(
            f"{AranSkills.SwingStudiesII}({BUFF})",
            delay=0,
            remain=5000 + 3000,
            pdamage_indep=15 + passive_level,
            pdamage=20,
            cooltime=-1,
        ).wrap(core.BuffSkillWrapper)
        SmashSwingIllusion = AdrenalineDamageWrapper(
            core.DamageSkill(
                AranSkills.SwingStudiesII,
                delay=0,
                damage=280 + 40 * passive_level + ADRENALINE_BOOST_PASSIVE,
                hit=5,
            ),  # No core enhancement. 코어 강화 받지 않음
            AdrenalineBoost,
        )

        FinalBlow = AdrenalineDamageWrapper(
            core.DamageSkill(
                AranSkills.FinalBlow,
                delay=420,
                damage=285 + ADRENALINE_BOOST_PASSIVE + SWIFT_MOVE + DYNAMIC_MASTERY,
                hit=5,
                modifier=core.CharacterModifier(armor_ignore=15),
            ).setV(vEhc, 1, 2, False),
            AdrenalineBoost,
        )
        AdrenalineFinalBlowWave = (
            core.DamageSkill(
                f"{AranSkills.FinalBlow}({WAVE})",
                delay=0,
                damage=350 + ADRENALINE_BOOST_PASSIVE,
                hit=4,
                cooltime=-1,
            )
            .setV(vEhc, 1, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        FinalAttack = AdrenalineDamageWrapper(  # Adrenaline boost perdem, at-bat effects applied. 아드레날린 부스트의 퍼뎀, 타수 효과 적용됨
            core.DamageSkill(
                AranSkills.AdvancedFinalAttack,
                delay=0,
                damage=85 + passive_level + ADRENALINE_BOOST_PASSIVE,
                hit=3,
            ).setV(vEhc, 0, 2, True),
            AdrenalineBoost,
            activation=0.01 * (60 + passive_level),
        )

        BeyonderFirst = AdrenalineDamageWrapper(
            core.DamageSkill(
                f"{AranSkills.BeyondBlade}({ONE_HIT})",
                delay=420,
                damage=285 + 10 * ceil(self.combat / 3) + ADRENALINE_BOOST_PASSIVE,
                hit=5 + 1,
                modifier=core.CharacterModifier(
                    pdamage=BEYONDER_PDAMAGE, armor_ignore=44, crit=100
                ),
            ).setV(vEhc, 2, 2, False),
            AdrenalineBoost,
        )
        BeyonderSecond = AdrenalineDamageWrapper(
            core.DamageSkill(
                f"{AranSkills.BeyondBlade}({TWO_HIT})",
                delay=360,
                damage=300 + 10 * ceil(self.combat / 3) + ADRENALINE_BOOST_PASSIVE,
                hit=5 + 1,
                modifier=core.CharacterModifier(
                    pdamage=BEYONDER_PDAMAGE, armor_ignore=44, crit=100
                ),
            ).setV(vEhc, 2, 2, False),
            AdrenalineBoost,
        )
        BeyonderThird = AdrenalineDamageWrapper(
            core.DamageSkill(
                f"{AranSkills.BeyondBlade}({THREE_HIT})",
                delay=420,
                damage=315 + 10 * ceil(self.combat / 3) + ADRENALINE_BOOST_PASSIVE,
                hit=5 + 1,
                modifier=core.CharacterModifier(
                    pdamage=BEYONDER_PDAMAGE, armor_ignore=44, crit=100
                ),
            ).setV(vEhc, 2, 2, False),
            AdrenalineBoost,
        )
        AdrenalineBeyonderWave = (
            core.DamageSkill(
                f"{AranSkills.BeyondBlade}({WAVE})",
                delay=0,
                damage=400 + ADRENALINE_BOOST_PASSIVE,
                hit=5,
                cooltime=-1,
            )
            .setV(vEhc, 2, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        BoostEndHuntersTargetingHolder = core.DamageSkill(
            f"{AranSkills.FinisherHuntersPrey}({HOLDER})", BOOST_END_HUNTERS_TARGETING_DELAY, 0, 0, cooltime=-1
        ).wrap(core.DamageSkillWrapper)
        BoostEndHuntersTargeting = (
            core.DamageSkill(
                AranSkills.FinisherHuntersPrey,
                delay=0,
                damage=1070
                + 10 * self.combat
                + ADRENALINE_BOOST_PASSIVE
                + DYNAMIC_MASTERY,
                hit=15,
                cooltime=-1,
            )
            .setV(vEhc, 3, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        GatheringCatcher = (
            core.DamageSkill(
                f"{AranSkills.GatheringHook}({CANCEL})",
                delay=570,
                damage=170 + DYNAMIC_MASTERY + ADRENALINE_BOOST_PASSIVE,
                hit=2,
            )
            .setV(vEhc, 5, 3, False)
            .wrap(core.DamageSkillWrapper)
        )

        # Hyper Skills
        AdrenalineGenerator = core.BuffSkill(
            AranSkills.AdrenalineBurst, 0, 0, cooltime=240 * 1000
        ).wrap(core.BuffSkillWrapper)

        MahaRegionInit = AdrenalineDamageWrapper(
            core.DamageSkill(
                f"{AranSkills.MahasDomain}({CAST})",
                delay=30,  # Gathering Catcher Cancel: 1680 -> 30. 게더링캐쳐 캔슬 : 1680 -> 30
                damage=800 + ADRENALINE_BOOST_PASSIVE,
                hit=5,
                cooltime=150 * 1000,
            ).setV(vEhc, 5, 2, True),
            AdrenalineBoost,
        )
        MahaRegion = AdrenalineSummonWrapper(
            core.SummonSkill(
                AranSkills.MahasDomain,
                summondelay=0,
                delay=1000,
                damage=500 + ADRENALINE_BOOST_PASSIVE,
                hit=3,
                remain=10 * 1000,
                cooltime=-1,
            ).setV(vEhc, 5, 2, True),
            AdrenalineBoost,
        )

        HerosOath = core.BuffSkill(
            AranSkills.HeroicMemories,
            delay=0,
            remain=60 * 1000,
            cooltime=120 * 1000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)

        # V Skills
        InstallMaha = (
            core.BuffSkill(
                AranSkills.MahasFury,
                delay=30,  # Gathering Catcher Cancel: 960 -> 30. 게더링캐쳐 캔슬 : 960 -> 30
                remain=(30 + vEhc.getV(1, 1)) * 1000,
                patt=5 + vEhc.getV(1, 1),
                cooltime=150 * 1000,
                red=True,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.BuffSkillWrapper)
        )
        InstallMahaBlizzard = (
            core.SummonSkill(
                f"{AranSkills.MahasFury}({SNOWSTORM})",
                summondelay=0,
                delay=3000,
                damage=450 + 18 * vEhc.getV(1, 1) + ADRENALINE_BOOST_PASSIVE,
                hit=5,
                remain=(30 + vEhc.getV(1, 1)) * 1000,
                cooltime=-1,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.SummonSkillWrapper)
        )

        BrandishMahaHolder = (
            core.DamageSkill(
                f"{AranSkills.MahasCarnage}({HOLDER})",
                delay=30,  # Gathering Catcher Cancel: 720 -> 30. 게더링캐쳐 캔슬 : 720 -> 30
                damage=0,
                hit=0,
                cooltime=20 * 1000,
                red=True,
            )
            .isV(vEhc, 2, 2)
            .wrap(core.DamageSkillWrapper)
        )
        BrandishMaha = AdrenalineDamageWrapper(
            core.DamageSkill(
                AranSkills.MahasCarnage,
                delay=0,
                damage=600
                + vEhc.getV(2, 2) * 24
                + DYNAMIC_MASTERY
                + ADRENALINE_BOOST_PASSIVE,
                hit=15,
                cooltime=-1,
                modifier=core.CharacterModifier(boss_pdamage=20),
            ).isV(vEhc, 2, 2),
            AdrenalineBoost,
        )

        PenrilCrash = AdrenalineDamageWrapper(
            core.DamageSkill(
                AranSkills.FenrirCrash,
                delay=420,
                damage=500 + vEhc.getV(3, 3) * 5 + ADRENALINE_BOOST_PASSIVE,
                hit=6 + vEhc.getV(3, 3) // 30 + 1,
                modifier=core.CharacterModifier(
                    crit=100, armor_ignore=60, pdamage=PENRIL_PDAMAGE
                ),
            )
            .setV(vEhc, 2, 2, False)
            .isV(vEhc, 3, 3),
            AdrenalineBoost,
        )
        PenrilCrashIceburg = (
            core.DamageSkill(
                f"{AranSkills.FenrirCrash}({ICEBURG})",
                delay=0,
                damage=500 + vEhc.getV(3, 3) * 5 + ADRENALINE_BOOST_PASSIVE,
                hit=6,
                cooltime=-1,
            )
            .setV(vEhc, 2, 2, False)
            .isV(vEhc, 3, 3)
            .wrap(core.DamageSkillWrapper)
        )

        # TODO: It operates as a final attack that increases the number of strokes, but the list of skills that increase the stack is not revealed. 타수가 늘어나는 파이널 어택으로 동작하지만, 스택을 늘리는 스킬 목록이 밝혀지지 않아 일단 총 423타가 나오게 평균으로 해둠
        BlizzardTempest = (
            core.DamageSkill(
                AranSkills.BlizzardTempest,
                delay=750,
                damage=800 + 32 * vEhc.getV(0, 0) + ADRENALINE_BOOST_PASSIVE,
                hit=8,
                cooltime=180 * 1000,
                red=True,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )
        BlizzardTempestAura = (
            core.SummonSkill(
                f"{AranSkills.BlizzardTempest}({CURSE})",
                summondelay=0,
                delay=425,
                damage=475 + 19 * vEhc.getV(0, 0) + ADRENALINE_BOOST_PASSIVE,
                hit=9,
                remain=20000,
                cooltime=-1,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.SummonSkillWrapper)
        )

        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        ### Skill Wrapper ###

        Combo = core.BuffSkill(_("아란(콤보)"), 0, 99999999)
        Combo = core.StackSkillWrapper(Combo, 1000)
        Combo.set_name_style(_("콤보 %d만큼 증가"))


        # 헌터즈 타게팅
        BoostEndHuntersTargetingHolder.onAfter(core.RepeatElement(BoostEndHuntersTargeting, 7))

        # Mahas Domain. 마하의 영역
        MahaRegionInit.onAfter(MahaRegion)

        # Install Maha. 인스톨 마하.
        InstallMaha.onAfter(InstallMahaBlizzard)
        InstallMaha.onAfter(Combo.stackController(100))

        # Mahas Carnage. 브랜디쉬 마하
        BrandishMahaHolder.onAfter(core.RepeatElement(BrandishMaha, 2))
        BrandishMahaHolder.onJustAfter(core.OptionalElement(InstallMaha.is_active, BrandishMahaHolder.controller(0.5, "reduce_cooltime_p")))

        # Combo calculation, weapon aura. 콤보 계산, 오라 웨폰.
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 1)
        for sk in [
            SmashSwing,
            FinalBlow,
            MahaRegionInit,
            GatheringCatcher,
            BeyonderFirst,
            BeyonderSecond,
            BeyonderThird,
            PenrilCrash,
            BrandishMaha,
            BoostEndHuntersTargeting,
        ]:
            sk.onAfter(
                Combo.stackController(
                    DynamicVariableOperation.reveal_argument(sk.skill.hit)
                )
            )
            auraweapon_builder.add_aura_weapon(sk)

        MahaRegion.onTick(
            Combo.stackController(
                DynamicVariableOperation.reveal_argument(MahaRegion.skill.hit)
            )
        )

        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        # Final Attack. 파이널 어택
        for sk in [
            SmashSwing,
            FinalBlow,
            BeyonderFirst,
            BeyonderSecond,
            BeyonderThird,
            BoostEndHuntersTargetingHolder,
            BrandishMahaHolder,
            PenrilCrash,
        ]:
            sk.onJustAfter(FinalAttack)


        # Blizzard Tempest. 블리자드 템페스트.
        BlizzardTempest.onAfter(BlizzardTempestAura)

        # 기본 공격
        FinalBlow.onAdrenalineAfter(AdrenalineFinalBlowWave)
        FinalBlow.onAfter(BeyonderFirst)

        BeyonderFirst.onAdrenalineAfter(AdrenalineBeyonderWave)
        BeyonderSecond.onAdrenalineAfter(AdrenalineBeyonderWave)
        BeyonderThird.onAdrenalineAfter(AdrenalineBeyonderWave)
        BeyonderFirst.onAfter(BeyonderSecond)
        BeyonderSecond.onAfter(BeyonderThird)
        BeyonderThird.onAfter(PenrilCrash)

        PenrilCrash.onAdrenalineAfter(PenrilCrashIceburg)

        # Smash Swing. 스매시 스윙
        SmashSwing.onAfter(SmashSwingIncr)
        SmashSwing.onAfter(SmashSwingIllusion)
        SmashSwing.onConstraint(
            core.ConstraintElement(
                _("스윙 연구가 없을때"), SmashSwingIncr, SmashSwingIncr.is_not_active
            )
        )

        # 게캐 캔슬
        BrandishMahaHolder.onAfter(GatheringCatcher)
        MahaRegionInit.onAfter(GatheringCatcher)
        InstallMaha.onAfter(GatheringCatcher)

        Combo.set_stack(0)

        # Adrenaline. 아드레날린
        AdrenalineBoost.onConstraint(
            core.ConstraintElement(_("콤보가 1000이상"), Combo, partial(Combo.judge, 1000, 1))
        )
        AdrenalineBoost.onAfter(Combo.stackController(-999999999, dtype="set"))
        AdrenalineBoost.onAfter(BoostEndHuntersTargetingHolder.controller(1))
        AdrenalineBoost.onEventEnd(Combo.stackController(500, dtype="set"))
        AdrenalineGenerator.onConstraint(
            core.ConstraintElement(
                _("아드레날린 부스트가 불가능할때"), AdrenalineBoost, AdrenalineBoost.is_not_active
            )
        )
        AdrenalineGenerator.onAfter(AdrenalineBoost)

        # Scheduling
        Combo.set_stack(900)  # start with 900 combo

        return (
            FinalBlow,
            [
                Combo,
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                Booster,
                SnowCharge,
                BlessingMaha,
                HerosOath,
                AuraWeaponBuff,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                InstallMaha,
                AdrenalineBoost,
                AdrenalineGenerator,
                globalSkill.soul_contract(),
            ]
            + [
                MahaRegionInit,
                SmashSwing,
                BrandishMahaHolder,
                BoostEndHuntersTargetingHolder,
                BlizzardTempest,
                MirrorBreak,
            ]
            + [
                MahaRegion,
                SmashSwingIncr,
                AuraWeapon,
                InstallMahaBlizzard,
                BlizzardTempestAura,
                MirrorSpider,
            ]  # Not used from scheduler
            + [FinalBlow],
        )
