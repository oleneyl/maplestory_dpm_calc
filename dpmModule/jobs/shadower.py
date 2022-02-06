from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import (
    ConcurrentRunRule,
    ConditionRule,
    InactiveRule,
    RuleSet,
)
from . import globalSkill
from .jobbranch import thieves
from . import jobutils
from math import ceil
from typing import Any, Dict


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "LUK2"
        self.jobname = "섀도어"
        self.ability_list = Ability_tool.get_ability_set(
            "boss_pdamage", "crit", "buff_rem"
        )
        self.preEmptiveSkills = 2

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=20, armor_ignore=26.8, crit_damage=5)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule("레디 투 다이", "소울 컨트랙트"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("메이플월드 여신의 축복", "얼티밋 다크 사이트"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("멸귀참영진", "소울 컨트랙트"), RuleSet.BASE)
        ruleset.add_rule(InactiveRule("베일 오브 섀도우", "어드밴스드 다크 사이트"), RuleSet.BASE)
        ruleset.add_rule(InactiveRule("연막탄", "어드밴스드 다크 사이트"), RuleSet.BASE)
        ruleset.add_rule(
            ConditionRule(
                "소울 컨트랙트",
                "얼티밋 다크 사이트",
                lambda sk: sk.is_active() or sk.is_cooltime_left(80000, 1),
            ),
            RuleSet.BASE,
        )
        ruleset.add_rule(
            ConditionRule(
                "소닉 블로우",
                "소울 컨트랙트",
                lambda sk: sk.is_active() or sk.is_cooltime_left(30000, 1),
            ),
            RuleSet.BASE,
        )
        return ruleset

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        NimbleBody = core.InformedCharacterModifier("님블 바디", stat_main=20)
        Karma = core.InformedCharacterModifier("카르마", att=30)
        PhisicalTraining = core.InformedCharacterModifier(
            "피지컬 트레이닝", stat_main=30, stat_sub=30
        )
        DaggerAccelation = core.InformedCharacterModifier(
            "대거 액셀레이션",
            stat_main=20,
        )
        SheildMastery = core.InformedCharacterModifier("실드 마스터리", att=15)
        Grid = core.InformedCharacterModifier("그리드", att=25)

        CriticalEdge = core.InformedCharacterModifier("크리티컬 엣지", crit=25, crit_damage=5)

        CruelPassive = core.InformedCharacterModifier(
            "크루얼 스텝(패시브)", pdamage_indep=25 + 2 * (self.combat // 3)
        )
        BloodyPocketPassive = core.InformedCharacterModifier(
            "블러디 파킷(패시브)",
            stat_main=10 ,
            crit_damage=20,
        )
        ShadowerInstinct = core.InformedCharacterModifier(
            "섀도어 인스팅트",
            att=50 + passive_level * 2,
            armor_ignore=20 + passive_level,
            pdamage_indep=15 + ceil(passive_level / 2),
        )
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 2, 2)

        DaggerExpert = core.InformedCharacterModifier(
            "대거 엑스퍼트", att=40 + passive_level, crit_damage=15 + passive_level // 3
        )
        return [
            NimbleBody,
            Karma,
            PhisicalTraining,
            DaggerAccelation,
            SheildMastery,
            Grid,
            CriticalEdge,
            CruelPassive,
            BloodyPocketPassive,
            ShadowerInstinct,
            ReadyToDiePassive,
            DaggerExpert,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=30)
        Mastery = core.InformedCharacterModifier(
            "숙련도", mastery=90 + ceil(passive_level / 2)
        )
        FlipTheCoin = core.InformedCharacterModifier(
            "플립 더 코인",
            pdamage=25,
            crit=25,
        )
        return [WeaponConstant, Mastery, FlipTheCoin]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        일반 다크사이트는 깡으로 사용하지 않음.

        쉐도우 파트너는 절개, 암살, 소닉 블로우에만 적용.

        하이퍼 : 메익 인핸스, 암살 리인포스 / 보킬 / 이그노어 가드.

        암살-닼플-메익-배오섀
        """

        ######   Skill   ######
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        LINK_DELAY = 30

        # Buff skills
        ShadowPartner = core.BuffSkill(
            "섀도우 파트너",
            delay=0,
            remain=2000 * 1000,
            rem=True,
        ).wrap(core.BuffSkillWrapper)

        Assasinate1 = (
            core.DamageSkill(
                "암살(1타)",
                delay=540,
                damage=270 + 3 * self.combat,
                hit=6,
                modifier=core.CharacterModifier(
                    pdamage=20,
                    boss_pdamage=20,
                    armor_ignore=10,
                ),
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        Assasinate2 = (
            core.DamageSkill(
                "암살(2타)",
                delay=270 + LINK_DELAY,
                damage=490 + 5 * self.combat,
                hit=6,
                modifier=core.CharacterModifier(
                    pdamage=20,
                    boss_pdamage=20,
                    armor_ignore=10,
                    pdamage_indep=50,  # 살의 버프
                ),
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        MesoStack = core.StackSkillWrapper(core.BuffSkill("픽파킷", 0, 9999999), 20)
        MesoExplosion = core.StackDamageSkillWrapper(
            core.DamageSkill(
                "메소 익스플로전",
                delay=0,
                damage=100 + 20,
                hit=2,
                modifier=core.CharacterModifier(boss_pdamage=30),
            ).setV(vEhc, 2, 3, False),
            MesoStack,
            lambda skill: skill.stack,
        )

        BailOfShadow = (
            core.SummonSkill(
                "베일 오브 섀도우",
                summondelay=900 + 120,  # 다크 사이트 딜레이 합산
                delay=12000 / 14,
                damage=800,
                hit=1 * 1.8,  # 쉐도우 파트너 적용
                remain=12 * 1000,
                cooltime=60000,
            )
            .setV(vEhc, 3, 2, False)
            .wrap(core.SummonSkillWrapper)
        )

        DarkFlare = (
            core.SummonSkill(
                "다크 플레어",
                summondelay=600,
                delay=60000 / 62,
                damage=360,
                hit=1,
                remain=60 * 1000,
                cooltime=60000,
                red=True,
                rem=True,
            )
            .setV(vEhc, 1, 3, False)
            .wrap(core.SummonSkillWrapper)
        )

        Smoke = core.BuffSkill(
            "연막탄",
            delay=810 + 120,  # 다크 사이트 딜레이 합산
            remain=30000,
            cooltime=(150 - 2 * self.combat) * 1000,
            crit_damage=20 + ceil(self.combat / 3),
            red=True,
        ).wrap(core.BuffSkillWrapper)
        Venom = core.DotSkill(
            "페이탈 베놈",
            summondelay=0,
            delay=1000,
            damage=160 + 5 * passive_level,
            hit=2 + (10 + passive_level) // 6,
            remain=89999 * 1000,
        ).wrap(core.DotSkillWrapper)

        AdvancedDarkSight = core.BuffSkill(
            "어드밴스드 다크 사이트",
            delay=0,
            remain=10000,
            cooltime=-1,
            pdamage_indep=15,
        ).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill(
            "에픽 어드벤처",
            delay=0,
            remain=60 * 1000,
            cooltime=120 * 1000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)

        UltimateDarksight = (
            core.BuffSkill(
                "얼티밋 다크 사이트",
                delay=750,
                remain=30000,
                cooltime=(220 - vEhc.getV(3, 3)) * 1000,
                pdamage_indep=(100 + 15 + 10 + vEhc.getV(3, 3) // 5) / (100 + 15) * 100
                - 100,  # (얼닼사 + 어닼사) - (어닼사) 최종뎀 연산
                red=True,
            )
            .isV(vEhc, 3, 3)
            .wrap(core.BuffSkillWrapper)
        )

        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 2, 2)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        Eviscerate = (
            core.DamageSkill(
                "절개",
                delay=720 + 300 - (270 + LINK_DELAY),  # 암살 2타에서 메익연계 대신 절개연계시 딜레이 변동 보정
                damage=675 + 27 * vEhc.getV(0, 0),
                hit=7 * 5,
                modifier=core.CharacterModifier(crit=100, armor_ignore=100),
                cooltime=20000,
                red=True,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )

        SonicBlow = (
            core.DamageSkill(
                "소닉 블로우",
                delay=900,
                damage=0,
                hit=0,
                cooltime=45 * 1000,
                red=True,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.DamageSkillWrapper)
        )
        SonicBlowTick = (
            core.DamageSkill(
                "소닉 블로우(틱)",
                delay=107,
                damage=500 + 20 * vEhc.getV(1, 1),
                hit=7,
                modifier=core.CharacterModifier(armor_ignore=100),
            )
            .isV(vEhc, 1, 1)
            .wrap(core.DamageSkillWrapper, name="소닉 블로우(사용)")
        )  # 7 * 15

        ShadowFormation = (
            core.SummonSkill(
                "멸귀참영진",
                summondelay=0,
                delay=8000 / 12,
                damage=425 + 17 * vEhc.getV(0, 0),
                hit=8,
                remain=8000 - 1,
                cooltime=90000,
                red=True,
                modifier=core.CharacterModifier(armor_ignore=100),
            )
            .isV(vEhc, 0, 0)
            .wrap(core.SummonSkillWrapper)
        )
        ShadowFormationFinal = (
            core.DamageSkill(
                "멸귀참영진(우두머리)",
                delay=0,
                damage=625 + 25 * vEhc.getV(0, 0),
                hit=15 * 4,
                cooltime=-1,
                modifier=core.CharacterModifier(armor_ignore=100),
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )

        ### build graph relationships
        AdvancedDarkSight.set_disabled_and_time_left(-1)
        MesoExplosion.onJustAfter(MesoStack.stackController(-20, name="메소 제거"))

        Assasinate2.onAfter(
            MesoStack.stackController(6 * 2 * 0.4, name="메소 생성"),
        )
        Assasinate2.onAfter(MesoExplosion)
        Assasinate1.onAfter(MesoStack.stackController(6 * 2 * 0.4, name="메소 생성"))
        Assasinate1.onAfter(Assasinate2)

        BailOfShadow.onTick(MesoStack.stackController(2 * 0.4, name="메소 생성"))
        BailOfShadow.onAfter(
            AdvancedDarkSight.controller(12000, "set_enabled_and_time_left")
        )

        Smoke.onAfter(AdvancedDarkSight.controller(30000, "set_enabled_and_time_left"))

        UltimateDarksight.onAfter(
            AdvancedDarkSight.controller(30000, "set_enabled_and_time_left")
        )

        SonicBlowTick.onAfter(MesoStack.stackController(7 * 2 * 0.4, name="메소 생성"))
        SonicBlow.onAfter(core.RepeatElement(SonicBlowTick, 15))

        UseEviscerate = core.OptionalElement(
            Eviscerate.is_available, Eviscerate, name="절개 연계 여부"
        )
        Assasinate2.onAfter(UseEviscerate)
        Eviscerate.onAfter(MesoStack.stackController(7 * 2 * 0.4, name="메소 생성"))
        Eviscerate.protect_from_running()

        ShadowFormation.onEventEnd(ShadowFormationFinal)

        for sk in [
            Assasinate1,
            Assasinate2,
            Eviscerate,
            SonicBlowTick,
        ]:
            jobutils.create_auxilary_attack(sk, 0.7, nametag="(쉐도우파트너)")

        return (
            Assasinate1,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                ShadowPartner,
                AdvancedDarkSight,
                EpicAdventure,
                UltimateDarksight,
                Smoke,
                MesoStack,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                ReadyToDie,
                globalSkill.soul_contract(),
            ]
            + [
                ShadowFormation,
                ShadowFormationFinal,
                Eviscerate,
                SonicBlow,
                BailOfShadow,
                DarkFlare,
                MirrorBreak,
                MirrorSpider,
            ]
            + [Venom]
            + [Assasinate1],
        )
