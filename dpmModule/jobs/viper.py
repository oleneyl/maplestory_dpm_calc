from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import (
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


class EnergyChargeWrapper(core.StackSkillWrapper):
    def __init__(self, combat):
        skill = core.BuffSkill("에너지 차지", 0, 999999 * 1000)
        super(EnergyChargeWrapper, self).__init__(skill, 10000)
        self.stack = 0
        self.charged = False
        self.combat = combat
        self.drainCallback = None

    def charge(self, val, force):
        if (force or not self.charged) and val > 0:
            self.stack = min(self.stack + val, 10000)
        elif val < 0:
            self.stack = max(self.stack + val, 0)
        if self.charged and self.stack <= 0:
            self.charged = False
        elif (not self.charged) and self.stack >= 10000:
            self.charged = True
        if self.stack <= 0:
            self.drainCallback()  # 게이지 고갈시 서펜트 종료. 카데나와 같이 Taskholder에 체이닝해서 구현하는게 좋지만, 성능 문제로 이와 같이 해둠.
        return core.ResultObject(
            0,
            core.CharacterModifier(),
            0,
            0,
            sname=self.skill.name,
            spec="graph control",
        )

    def chargeController(self, val, force=False):
        task = core.Task(self, partial(self.charge, val, force))
        return core.TaskHolder(task, name=f"게이지 {val}")

    def get_modifier(self):
        if self.charged == 1:
            return core.CharacterModifier(att=50 + 2 * self.combat)
        else:
            return core.CharacterModifier(att=25 + 1 * self.combat)

    def isStateOn(self):
        return self.charged

    def isStateOff(self):
        return not self.charged


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
        ruleset.add_rule(
            ConditionRule("에너지 오브(더미)", "에너지 차지", lambda sk: sk.isStateOff()),
            RuleSet.BASE,
        )
        ruleset.add_rule(MutualRule("스티뮬레이트", "트랜스 폼"), RuleSet.BASE)
        ruleset.add_rule(
            ConditionRule(
                "스티뮬레이트", "에너지 차지", lambda sk: sk.judge(2000, -1) or sk.isStateOff()
            ),
            RuleSet.BASE,
        )
        ruleset.add_rule(
            ConditionRule(
                "유니티 오브 파워", "유니티 오브 파워(디버프)", lambda sk: sk.is_time_left(1000, -1)
            ),
            RuleSet.BASE,
        )
        # ruleset.add_rule(MutualRule('타임 리프', '소울 컨트랙트'), RuleSet.BASE)
        # ruleset.add_rule(InactiveRule('타임 리프', '소울 컨트랙트'), RuleSet.BASE)
        ruleset.add_rule(DisableRule("타임 리프"), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(
            pdamage=49, armor_ignore=15.3, crit_damage=39, patt=2.4
        )

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        CriticalRoar = core.InformedCharacterModifier("크리티컬 로어", crit=20, crit_damage=5)
        MentalClearity = core.InformedCharacterModifier("멘탈 클리어리티", att=30)
        PhisicalTraining = core.InformedCharacterModifier(
            "피지컬 트레이닝", stat_main=30, stat_sub=30
        )
        CriticalRage = core.InformedCharacterModifier(
            "크리티컬 레이지", crit=15, crit_damage=10  # 보스상대 추가 크확은 not_implied_skill_list
        )
        StimulatePassive = core.InformedCharacterModifier(
            "스티뮬레이트(패시브)", boss_pdamage=20
        )

        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 2, 3)

        return [
            CriticalRoar,
            MentalClearity,
            PhisicalTraining,
            CriticalRage,
            StimulatePassive,
            LoadedDicePassive,
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
        GuardCrush = core.InformedCharacterModifier(
            "가드 크러시", armor_ignore=40 + 2 * passive_level  # 40% 확률로 방무 100% 무시.
        )
        # CounterAttack = core.InformedCharacterModifier("카운터 어택",pdamage = 25 + 2*passive_level) # TODO: 적용 여부 결정해야함

        return [WeaponConstant, Mastery, CriticalRage, GuardCrush]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        울트라 차지 : 공격시 350충전, 보스공격시 2배 충전. 최대스택 10000.

        스티뮬레이트는 완충 상태가 아니거나 게이지 2000 이하일때 사용
        에너지 오브는 게이지 회복용으로 사용

        더블 럭키 다이스-인핸스
        피스트 인레이지-리인포스, 보스킬러, 보너스 어택
        에너지 블라스트-보너스 어택

        인레이지-노틸-드스-유니티
        """
        ######   Skill   ######
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        serverlag = 3
        TRANSFORM_HIT = 12

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

        # Damage Skill
        FistInrage = (
            core.DamageSkill(
                "피스트 인레이지",
                delay=600,
                damage=320 + 4 * self.combat,
                hit=8 + 1,
                modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20),
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        FistInrage_T = (
            core.DamageSkill(
                "피스트 인레이지(변신)",
                delay=600,
                damage=320 + 4 * self.combat,
                hit=8 + 1 + 2,
                modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20),
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        DragonStrike = (
            core.DamageSkill(
                "드래곤 스트라이크",
                delay=690,
                damage=300 + 4 * self.combat,
                hit=12,
                cooltime=15 * 1000,
                red=True,
            )
            .setV(vEhc, 2, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        DragonStrikeBuff = core.BuffSkill(
            "드래곤 스트라이크(디버프)",
            delay=0,
            remain=15 * 1000,
            cooltime=-1,
            pdamage_indep=20 + self.combat // 2,
        ).wrap(core.BuffSkillWrapper)

        Nautilus = (
            core.DamageSkill(
                "노틸러스",
                delay=690,
                damage=440 + 4 * self.combat,
                hit=7,
                cooltime=60 * 1000,
                red=True,
            )
            .setV(vEhc, 1, 2, True)
            .wrap(core.DamageSkillWrapper)
        )
        NautilusFinalAttack = (
            core.DamageSkill(
                "노틸러스(파이널 어택)", delay=0, damage=165 + 2 * self.combat, hit=2
            )
            .setV(vEhc, 1, 2, True)
            .wrap(core.DamageSkillWrapper)
        )

        # 타임 리프: 안 쓰는 게 더 셈
        TimeLeap = core.DamageSkill(
            "타임 리프", delay=1080, damage=0, hit=0, cooltime=180000
        ).wrap(core.DamageSkillWrapper)

        # Hyper
        Stimulate = core.BuffSkill(  # 에너지 주기적으로 800씩 증가, 미완충시 풀완충.
            "스티뮬레이트",
            delay=930,
            remain=120 * 1000,
            cooltime=240 * 1000,
            pdamage=20,
        ).wrap(core.BuffSkillWrapper)
        StimulateSummon = core.SummonSkill(
            "스티뮬레이트(게이지 증가 더미)",
            summondelay=0,
            delay=(5 + serverlag) * 1000,
            damage=0,
            hit=0,
            remain=120 * 1000,
            cooltime=-1,
        ).wrap(core.SummonSkillWrapper)

        UnityOfPower = (  # 완충시에만 사용 가능, 에너지 1500 소모.
            core.DamageSkill(
                "유니티 오브 파워",
                delay=690,
                damage=650,
                hit=5,
                cooltime=10000,
            )
            .setV(vEhc, 3, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        UnityOfPowerBuff = core.BuffSkill(
            "유니티 오브 파워(디버프)",
            delay=0,
            remain=90 * 1000,
            cooltime=-1,
            crit_damage=40,  # 4스택 가정.
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

        Transform = (
            core.BuffSkill(
                "트랜스 폼",
                delay=450,
                remain=(50 + vEhc.getV(1, 1)) * 1000,
                cooltime=180 * 1000,
                red=True,
                pdamage_indep=20 + vEhc.getV(1, 1) // 5,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.BuffSkillWrapper)
        )
        TransformEnergyOrbDummy = core.DamageSkill(
            "에너지 오브(더미)", 0, 0, 0, cooltime=-1
        ).wrap(core.DamageSkillWrapper)
        TransformEnergyOrb = (
            core.DamageSkill(
                "에너지 오브",
                delay=780,
                damage=450 + vEhc.getV(1, 1) * 18,
                hit=3 * TRANSFORM_HIT,
                modifier=core.CharacterModifier(crit=50, armor_ignore=50),
            )
            .isV(vEhc, 1, 1)
            .wrap(core.DamageSkillWrapper)
        )

        SerpentScrew = (
            core.SummonSkill(
                "서펜트 스크류",
                summondelay=600,
                delay=260,
                damage=360 + vEhc.getV(0, 0) * 14,
                hit=3,
                remain=99999 * 10000,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.SummonSkillWrapper)
        )
        SerpentScrewDummy = core.SummonSkill(
            "서펜트 스크류(지속)",
            summondelay=0,
            delay=1000,
            damage=0,
            hit=0,
            remain=99999 * 10000,
            cooltime=-1,
        ).wrap(core.SummonSkillWrapper)

        FuriousCharge = (
            core.DamageSkill(
                "퓨리어스 차지",
                delay=420,
                damage=600 + vEhc.getV(4, 4) * 24,
                hit=10,
                cooltime=10 * 1000,
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
                damage=525 + 21 * vEhc.getV(0, 0),
                hit=10 * 14,
                cooltime=-1,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )

        ######   Skill Wrapper   ######
        # Energy Charge
        EnergyCharge = EnergyChargeWrapper(passive_level)
        EnergyConstraint = core.ConstraintElement(
            "에너지 차지 상태에서만 사용 가능", EnergyCharge, EnergyCharge.isStateOn
        )

        Stimulate.onAfter(EnergyCharge.chargeController(10000, force=True))
        Transform.onAfter(EnergyCharge.chargeController(10000, force=True))
        TransformEnergyOrb.onAfter(EnergyCharge.chargeController(700 * TRANSFORM_HIT))
        StimulateSummon.onTick(EnergyCharge.chargeController(800, force=True))
        FistInrage.onAfter(EnergyCharge.chargeController(700))
        Nautilus.onAfter(EnergyCharge.chargeController(700))
        MirrorBreak.onAfter(EnergyCharge.chargeController(700))
        SerpentScrewDummy.onTick(EnergyCharge.chargeController(-60))
        SerpentScrew.onTick(EnergyCharge.chargeController(-85 * 0.3))
        FistInrage_T.onAfter(EnergyCharge.chargeController(-150))
        DragonStrike.onAfter(EnergyCharge.chargeController(-180))
        UnityOfPower.onAfter(EnergyCharge.chargeController(-1500))
        HowlingFistInit.onAfter(EnergyCharge.chargeController(-1750))

        # Basic Attack
        BasicAttack = core.OptionalElement(
            EnergyCharge.isStateOn, FistInrage_T, FistInrage, "에너지 완충"
        )
        BasicAttackWrapper = core.DamageSkill("기본 공격", 0, 0, 0).wrap(
            core.DamageSkillWrapper
        )
        BasicAttackWrapper.onAfter(BasicAttack)

        # Dragon Strike
        DragonStrike.onConstraint(EnergyConstraint)
        DragonStrike.onAfter(DragonStrikeBuff)

        # Final Attack
        FinalAttack = core.OptionalElement(
            lambda: not Nautilus.is_available(), NautilusFinalAttack, name="노틸러스 쿨타임"
        )
        FistInrage.onAfter(FinalAttack)
        FistInrage_T.onAfter(FinalAttack)
        FuriousCharge.onAfter(FinalAttack)

        # Stimulate
        Stimulate.onAfter(StimulateSummon)

        # Unity Of Power
        UnityOfPower.onConstraint(EnergyConstraint)
        UnityOfPower.onAfter(UnityOfPowerBuff)

        # Transform
        Transform.onAfter(TransformEnergyOrbDummy.controller(1))
        TransformEnergyOrbDummy.onConstraint(
            core.ConstraintElement("트랜스폼 상태에서만 사용가능", Transform, Transform.is_active)
        )
        TransformEnergyOrbDummy.onAfter(
            core.RepeatElement(TransformEnergyOrb, 2 + vEhc.getV(1, 1) // 30)
        )

        # Serpent Screw
        SerpentScrew.onConstraint(
            core.ConstraintElement(
                "에너지 100 이상", EnergyCharge, partial(EnergyCharge.judge, 100, 1)
            )
        )
        SerpentScrew.onAfter(SerpentScrewDummy)
        EnergyCharge.drainCallback = lambda: [
            SerpentScrew.set_disabled_and_time_left(1),
            SerpentScrewDummy.set_disabled_and_time_left(-1),
        ]

        # Howling Fist
        HowlingFistInit.onConstraint(
            core.ConstraintElement(
                "에너지 1750 이상", EnergyCharge, partial(EnergyCharge.judge, 1750, 1)
            )
        )
        HowlingFistInit.onAfter(core.RepeatElement(HowlingFistCharge, 8))
        HowlingFistInit.onAfter(HowlingFistFinal)

        SoulContract = globalSkill.soul_contract()

        TimeLeap.onAfter(SoulContract.controller(1.0, "reduce_cooltime_p"))
        TimeLeap.onAfter(Nautilus.controller(1.0, "reduce_cooltime_p"))
        TimeLeap.onAfter(DragonStrike.controller(1.0, "reduce_cooltime_p"))

        return (
            BasicAttackWrapper,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                LuckyDice,
                Viposition,
                Stimulate,
                EpicAdventure,
                PirateFlag,
                Overdrive,
                Transform,
                UnityOfPowerBuff,
                DragonStrikeBuff,
                EnergyCharge,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                SoulContract,
            ]
            + [
                UnityOfPower,
                HowlingFistInit,
                Nautilus,
                DragonStrike,
                FuriousCharge,
                TransformEnergyOrbDummy,
                MirrorBreak,
                MirrorSpider,
                TimeLeap,
            ]
            + [SerpentScrew, SerpentScrewDummy, StimulateSummon]
            + []
            + [BasicAttackWrapper],
        )
