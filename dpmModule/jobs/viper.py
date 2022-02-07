from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import (
    ConcurrentRunRule,
    DisableRule,
    RuleSet,
    ConditionRule,
    MutualRule,
)
from . import globalSkill
from .jobbranch import pirates
from .jobclass import adventurer
from . import jobutils
from math import ceil
from typing import Any, Dict


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "STR"
        self.jobname = "바이퍼"
        self.ability_list = Ability_tool.get_ability_set(
            "boss_pdamage", "crit", "buff_rem"
        )
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule("메이플월드 여신의 축복", "스티뮬레이트"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("라이트닝 폼", "스티뮬레이트"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("하울링 피스트(개시)", "소울 컨트랙트"), RuleSet.BASE)
        ruleset.add_rule(
            ConditionRule(
                "소울 컨트랙트",
                "스티뮬레이트",
                lambda sk: sk.is_active() or sk.is_cooltime_left(80000, 1),
            ),
            RuleSet.BASE,
        )
        ruleset.add_rule(DisableRule("타임 리프"), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(
            pdamage=49, armor_ignore=15.3, crit_damage=39, patt=2.4
        )

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        base_modifier = chtr.get_base_modifier()
        passive_level = base_modifier.passive_level + self.combat
        CriticalRoar = core.InformedCharacterModifier("크리티컬 로어", crit=20, crit_damage=5)
        KnuckleAccelation = core.InformedCharacterModifier("너클 액셀레이션", stat_main=20)
        MentalClearity = core.InformedCharacterModifier("멘탈 클리어리티", att=30)
        PhisicalTraining = core.InformedCharacterModifier(
            "피지컬 트레이닝", stat_main=30, stat_sub=30
        )
        CriticalRage = core.InformedCharacterModifier(
            "크리티컬 레이지",
            crit=15,
            crit_damage=10,
            att=30,  # 보스상대 추가 크확은 not_implied_skill_list
        )
        StimulatePassive = core.InformedCharacterModifier(
            "스티뮬레이트(패시브)", boss_pdamage=20
        )
        GuardCrush = core.InformedCharacterModifier(
            "가드 크러시",
            armor_ignore=40 + 2 * passive_level,
            att=30 + passive_level,
        )

        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 2, 3)

        return [
            CriticalRoar,
            KnuckleAccelation,
            MentalClearity,
            PhisicalTraining,
            CriticalRage,
            StimulatePassive,
            LoadedDicePassive,
            GuardCrush,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=70)
        Mastery = core.InformedCharacterModifier(
            "숙련도", mastery=90 + ceil(self.combat / 2)
        )

        CriticalRage = core.InformedCharacterModifier(
            "크리티컬 레이지(보스)", crit=20  # 보스상대 추가+20% 크리율
        )
        GroggyMastery = core.InformedCharacterModifier(
            "그로기 마스터리", crit=60, crit_damage=15
        )
        OffenseForm = core.InformedCharacterModifier("오펜스 폼", pdamage=25)  # 상시유지 가정
        SerpentMark = core.InformedCharacterModifier(
            "서펜트 마크", pdamage_indep=20
        )  # 상시유지 가정

        return [
            WeaponConstant,
            Mastery,
            CriticalRage,
            GroggyMastery,
            OffenseForm,
            SerpentMark,
        ]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        더블 럭키 다이스-인핸스, 원모어찬스
        피스트 인레이지-리인포스, 보스킬러, 보너스 어택
        """
        ######   Skill   ######
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        ENERGY_ORB_HIT = 12

        # Buff Skill
        DICE_WEIGHT = 22
        DICE_POOL = 115
        DICE_PROC = DICE_WEIGHT / DICE_POOL  # 더블 럭키 다이스 - 인핸스
        LuckyDice = (
            core.BuffSkill(
                "로디드 다이스",
                delay=990,
                remain=180 * 1000,
                pdamage=20
                + 10 * DICE_PROC
                + 10
                * DICE_PROC
                * ((1 - DICE_PROC) + DICE_WEIGHT / (DICE_POOL * 2 - DICE_WEIGHT))
                * (10 * (5 + passive_level) * 0.01),
            )
            .isV(vEhc, 2, 2)
            .wrap(core.BuffSkillWrapper)
        )
        Viposition = core.BuffSkill(
            "바이퍼지션",
            delay=0,
            remain=(180 + 4 * self.combat) * 1000,
            patt=30 + self.combat,
        ).wrap(core.BuffSkillWrapper)

        SerpentStone = core.StackSkillWrapper(core.BuffSkill("서펜트 스톤", 0, 9999999), 5)

        # Damage Skill
        FistEnrage = (
            core.DamageSkill(
                "피스트 인레이지",
                delay=600,
                damage=320 + 4 * self.combat,
                hit=10 + 1,
                modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20),
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        SeaSerpentEnrage = (
            core.DamageSkill(
                "씨 서펜트 인레이지",
                delay=0,
                damage=430 + 5 * self.combat,
                hit=6,
                cooltime=4000,
                red=True,
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        SerpentAssultEnrage = (
            core.SummonSkill(
                "서펜트 어썰트 인레이지",
                summondelay=0,
                delay=240,
                damage=240 + 2 * self.combat,
                hit=4,
                remain=240 * 15 - 1,
                cooltime=-1,
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.SummonSkillWrapper)
        )

        NautilusFinalAttack = (
            core.DamageSkill(
                "노틸러스(파이널 어택)",
                delay=0,
                damage=165 + 2 * self.combat,
                hit=2,
            )
            .setV(vEhc, 1, 2, True)
            .wrap(core.DamageSkillWrapper)
        )

        # 타임 리프: 안 쓰는 게 더 셈
        TimeLeap = core.DamageSkill(
            "타임 리프", delay=1080, damage=0, hit=0, cooltime=180000
        ).wrap(core.DamageSkillWrapper)

        # Hyper
        Stimulate = core.BuffSkill(
            "스티뮬레이트",
            delay=930,
            remain=90 * 1000,
            cooltime=180 * 1000,
            pdamage=20,
        ).wrap(core.BuffSkillWrapper)
        SerpentSpirit = core.BuffSkill(
            "서펜트 스피릿",
            delay=900,
            remain=90000,
            crit_damage=5 * 5,  # 상시 5스택 가정,
            cooltime=60000,
        ).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill(
            "에픽 어드벤처",
            delay=0,
            remain=60 * 1000,
            cooltime=120 * 1000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)

        # 5th
        PirateFlag = adventurer.PirateFlagWrapper(vEhc, 3, 2, chtr.level)

        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        LightningForm = (
            core.BuffSkill(
                "라이트닝 폼",
                delay=450,
                remain=(50 + vEhc.getV(1, 1)) * 1000,
                cooltime=180 * 1000,
                red=True,
                pdamage_indep=20 + vEhc.getV(1, 1) // 5,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.BuffSkillWrapper)
        )
        LightningFormEnergyOrbDummy = core.DamageSkill(
            "에너지 오브(더미)", 0, 0, 0, cooltime=-1
        ).wrap(core.DamageSkillWrapper)
        LightningFormEnergyOrb = (
            core.DamageSkill(
                "에너지 오브",
                delay=780,
                damage=360 + vEhc.getV(1, 1) * 14,
                hit=5 * ENERGY_ORB_HIT,
                modifier=core.CharacterModifier(crit=50, armor_ignore=50),
            )
            .isV(vEhc, 1, 1)
            .wrap(core.DamageSkillWrapper)
        )

        SerpentScrew = (
            core.SummonSkill(
                "서펜트 스크류",
                summondelay=0,
                delay=240,
                damage=360 + vEhc.getV(0, 0) * 14,
                hit=3,
                remain=99999 * 10000,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.SummonSkillWrapper)
        )

        FuriousCharge = (
            core.DamageSkill(
                "퓨리어스 차지",
                delay=420,
                damage=600 + vEhc.getV(4, 4) * 24,
                hit=10,
                cooltime=8 * 1000,
                modifier=core.CharacterModifier(boss_pdamage=30),
            )
            .isV(vEhc, 4, 4)
            .wrap(core.DamageSkillWrapper)
        )

        HowlingFistInit = (
            core.DamageSkill(
                "하울링 피스트(개시)",
                delay=240,
                damage=0,
                hit=0,
                cooltime=90000,
                red=True,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )
        HowlingFistCharge = (
            core.DamageSkill(
                "하울링 피스트(충전)",
                delay=240,
                damage=425 + 17 * vEhc.getV(0, 0),
                hit=6,
                cooltime=-1,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )
        HowlingFistFinal = (
            core.DamageSkill(
                "하울링 피스트(막타)",
                delay=1950,
                damage=695 + 17 * vEhc.getV(0, 0),
                hit=10 * 14,
                cooltime=-1,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )

        ######   Skill Wrapper   ######
        # Serpent Enrage
        FistEnrage.onAfter(
            core.OptionalElement(
                partial(SerpentStone.judge, 5, 1),
                SerpentAssultEnrage,
                core.OptionalElement(SeaSerpentEnrage.is_available, SeaSerpentEnrage),
            )
        )
        SeaSerpentEnrage.onJustAfter(
            core.OptionalElement(
                Stimulate.is_active,
                SeaSerpentEnrage.controller(0.5, "reduce_cooltime_p"),
            )
        )
        SeaSerpentEnrage.onAfter(SerpentStone.stackController(1))
        SerpentAssultEnrage.onAfter(SerpentStone.stackController(-5))

        # Final Attack
        FistEnrage.onAfter(NautilusFinalAttack)
        FuriousCharge.onAfter(NautilusFinalAttack)
        HowlingFistCharge.onAfter(NautilusFinalAttack)
        HowlingFistFinal.onAfter(core.RepeatElement(NautilusFinalAttack, 14))

        # LightningForm
        LightningForm.onAfter(LightningFormEnergyOrbDummy.controller(1))
        LightningFormEnergyOrbDummy.onConstraint(
            core.ConstraintElement(
                "라이트닝 폼 상태에서만 사용가능", LightningForm, LightningForm.is_active
            )
        )
        LightningFormEnergyOrbDummy.onAfter(
            core.RepeatElement(LightningFormEnergyOrb, 2 + vEhc.getV(1, 1) // 30)
        )

        # Howling Fist
        HowlingFistInit.onAfter(core.RepeatElement(HowlingFistCharge, 8))
        HowlingFistInit.onAfter(HowlingFistFinal)

        SoulContract = globalSkill.soul_contract()

        TimeLeap.onAfter(SoulContract.controller(1.0, "reduce_cooltime_p"))

        SeaSerpentEnrage.protect_from_running()

        return (
            FistEnrage,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                LuckyDice,
                Viposition,
                Stimulate,
                SerpentSpirit,
                EpicAdventure,
                PirateFlag,
                Overdrive,
                LightningForm,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                SoulContract,
            ]
            + [
                HowlingFistInit,
                FuriousCharge,
                LightningFormEnergyOrbDummy,
                MirrorBreak,
                MirrorSpider,
                TimeLeap,
            ]
            + [SerpentScrew]
            + [SeaSerpentEnrage, SerpentAssultEnrage]
            + [FistEnrage],
        )
