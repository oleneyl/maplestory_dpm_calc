from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import ConcurrentRunRule, ReservationRule, RuleSet, InactiveRule
from . import globalSkill
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict


class ComboAttackWrapper(core.StackSkillWrapper):
    def __init__(
        self,
        skill,
        deathfault_buff: core.BuffSkillWrapper,
        instinct_buff: core.BuffSkillWrapper,
        vEhc: core.AbstractVEnhancer,
        combat: int,
    ):
        super(ComboAttackWrapper, self).__init__(skill, 10)
        self.deathfault_buff = deathfault_buff
        self.instinct_buff = instinct_buff
        self.vEhc = vEhc
        self.combat = combat
        self.stack = 10
        self.pdamage_indep_tick = 12 + ceil(self.combat / 6)

    def get_modifier(self):
        multiplier = 1 + self.instinct_buff.is_active() * 0.01 * (
            5 + 0.5 * self.vEhc.getV(1, 1)
        )
        return core.CharacterModifier(
            pdamage=2 * self.stack * multiplier,
            pdamage_indep=self.pdamage_indep_tick
            * (self.stack + self.deathfault_buff.is_active() * 6)
            * multiplier,
            att=2 * self.stack * multiplier,
        )


######   Passive Skill   ######
class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "STR"
        self.jobname = "히어로"
        self.ability_list = Ability_tool.get_ability_set("boss_pdamage", "crit", "mess")
        self.preEmptiveSkills = 2

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(InactiveRule("레이지 업라이징", "콤보 인스팅트"), RuleSet.BASE)
        ruleset.add_rule(ReservationRule("메이플월드 여신의 축복", "발할라"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("콤보 인스팅트", "소드 오브 버닝 소울"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("소울 컨트랙트", "소드 오브 버닝 소울"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("소드 오브 버닝 소울", "발할라"), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponMastery = core.InformedCharacterModifier(
            "웨폰 마스터리(두손도끼)",
            pdamage_indep=10,
            pdamage=5,
        )
        WeaponAccelation = core.InformedCharacterModifier(
            "웨폰 액셀레이션",
            stat_main=10,
        )
        PhisicalTraining = core.InformedCharacterModifier(
            "피지컬 트레이닝",
            stat_main=30,
            stat_sub=30,
        )

        ChanceAttack = core.InformedCharacterModifier("찬스 어택", crit=20)

        CombatMastery = core.InformedCharacterModifier(
            "컴뱃 마스터리", armor_ignore=50 + passive_level
        )
        AdvancedFinalAttack = core.InformedCharacterModifier(
            "어드밴스드 파이널 어택(패시브)", att=30 + passive_level
        )

        return [
            WeaponMastery,
            WeaponAccelation,
            PhisicalTraining,
            ChanceAttack,
            CombatMastery,
            AdvancedFinalAttack,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=44)
        Mastery = core.InformedCharacterModifier(
            "숙련도", mastery=90 + (passive_level // 2)
        )
        Enrage = core.InformedCharacterModifier(
            "인레이지",
            pdamage_indep=25 + self.combat // 2,
            crit_damage=20 + self.combat // 3,
        )
        ChanceAttack = core.InformedCharacterModifier("찬스 어택(디버프)", pdamage_indep=25)

        return [WeaponConstant, Mastery, Enrage, ChanceAttack]

    def get_modifier_optimization_hint(self) -> core.CharacterModifier:
        return core.CharacterModifier(boss_pdamage=65)

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        두손도끼

        어드밴스드 콤보-리인포스, 보스 킬러 / 어드밴스드 파이널 어택-보너스 찬스 / 레이징 블로우-리인포스, 보너스 어택

        120초마다 발할라, 소오버, 소울컨트랙트 사용
        240초마다 콤보 인스팅트 사용
        """
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        ######   Skill   ######
        # Buff skills
        SpiritBlade = core.BuffSkill(
            "스피릿 블레이드",
            delay=0,
            remain=200 * 1000,
            att=30,
            rem=True,
        ).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill(
            "에픽 어드벤처",
            delay=0,
            remain=60 * 1000,
            cooltime=120 * 1000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)

        RagingBlowEnrage = (
            core.DamageSkill(
                "레이징 블로우(인레이지)",
                delay=600,
                damage=215 + 3 * self.combat,
                hit=5 + 1,
                modifier=core.CharacterModifier(pdamage=20),
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        RagingBlowEnrageFinalizer = (
            core.DamageSkill(
                "레이징 블로우(인레이지)(최종타)",
                delay=0,
                damage=215 + 3 * self.combat,
                hit=2,
                modifier=core.CharacterModifier(pdamage=20, crit=100),
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        Incising = (
            core.DamageSkill("인사이징", delay=660, damage=400 + 3 * self.combat, hit=4)
            .setV(vEhc, 4, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        IncisingBuff = core.BuffSkill(
            "인사이징(버프)",
            delay=0,
            remain=(60 + self.combat // 2) * 1000,
            cooltime=-1,
            pdamage=25 + ceil(self.combat / 2),
        ).wrap(core.BuffSkillWrapper)
        IncisingDot = core.DotSkill(
            "인사이징(도트)",
            summondelay=0,
            delay=2000,
            damage=165 + 3 * self.combat,
            hit=1,
            remain=(60 + self.combat // 2) * 1000,
            cooltime=-1,
        ).wrap(core.DotSkillWrapper)

        AdvancedFinalAttack = (
            core.DamageSkill(
                "어드밴스드 파이널 어택",
                delay=0,
                damage=170 + 2 * passive_level,
                hit=3 * 0.01 * (60 + ceil(passive_level / 2) + 15),
            )
            .setV(vEhc, 1, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        RisingRage = (
            core.DamageSkill(
                "레이지 업라이징",
                delay=690,
                damage=500,
                hit=8,
                cooltime=10 * 1000,
            )
            .setV(vEhc, 2, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        Valhalla = core.BuffSkill(
            "발할라",
            delay=900,
            remain=30 * 1000,
            cooltime=120 * 1000,
            crit=30,
            att=50,
        ).wrap(core.BuffSkillWrapper)
        ValhallaSummon = (
            core.SummonSkill(
                "발할라(검격)",
                summondelay=0,
                delay=900,
                damage=370,
                hit=2 * 3,
                remain=900 * 12 - 1,
                cooltime=-1,
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.SummonSkillWrapper)
        )

        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        SwordOfBurningSoul = (
            core.SummonSkill(
                "소드 오브 버닝 소울",
                summondelay=810,
                delay=1000,
                damage=(315 + 12 * vEhc.getV(0, 0)),
                hit=6,
                remain=(60 + vEhc.getV(0, 0) // 2) * 1000,
                cooltime=120 * 1000,
                red=True,
                modifier=core.CharacterModifier(crit=50),
            )
            .isV(vEhc, 0, 0)
            .wrap(core.SummonSkillWrapper)
        )

        ComboDeathFault = (
            core.DamageSkill(
                "콤보 데스폴트",
                delay=1260,
                damage=400 + 16 * vEhc.getV(2, 3),
                hit=14,
                cooltime=20 * 1000,
                red=True,
            )
            .isV(vEhc, 2, 3)
            .wrap(core.DamageSkillWrapper)
        )
        ComboDeathFaultBuff = (
            core.BuffSkill("콤보 데스폴트(버프)", delay=0, remain=5 * 1000, cooltime=-1)
            .isV(vEhc, 2, 3)
            .wrap(core.BuffSkillWrapper)
        )

        ComboInstinct = (
            core.BuffSkill(
                "콤보 인스팅트",
                delay=360,
                remain=30 * 1000,
                cooltime=240 * 1000,
                red=True,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.BuffSkillWrapper)
        )
        ComboInstinctFringe = (
            core.DamageSkill(
                "콤보 인스팅트(균열)",
                delay=0,
                damage=200 + 8 * vEhc.getV(1, 1),
                hit=18,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.DamageSkillWrapper)
        )

        SwordIllusionInit = core.DamageSkill(
            "소드 일루전(시전)",
            delay=660,
            damage=0,
            hit=0,
            cooltime=30000,
            red=True,
        ).wrap(core.DamageSkillWrapper)
        SwordIllusion = core.DamageSkill(
            "소드 일루전",
            delay=0,
            damage=125 + 5 * vEhc.getV(0, 0),
            hit=4,
            cooltime=-1,
        ).wrap(core.DamageSkillWrapper)
        SwordIllusionFinal = core.DamageSkill(
            "소드 일루전(최종)",
            delay=0,
            damage=250 + 10 * vEhc.getV(0, 0),
            hit=5,
            cooltime=-1,
        ).wrap(core.DamageSkillWrapper)

        ######   Skill Wrapper   ######
        ComboAttack = ComboAttackWrapper(
            core.BuffSkill("콤보어택", 0, 999999 * 1000),
            ComboDeathFaultBuff,
            ComboInstinct,
            vEhc,
            passive_level,
        )

        # Final attack type
        InstinctFringeUse = core.OptionalElement(
            ComboInstinct.is_active, ComboInstinctFringe, name="콤보 인스팅트 여부"
        )

        # 레이징 블로우
        RagingBlowEnrage.onAfters(
            [
                InstinctFringeUse,
                RagingBlowEnrageFinalizer,
                AdvancedFinalAttack,
            ]
        )

        RisingRage.onAfter(AdvancedFinalAttack)

        Incising.onAfters([IncisingBuff, IncisingDot, AdvancedFinalAttack])

        Valhalla.onAfter(ValhallaSummon)

        ComboDeathFault.onAfter(ComboDeathFaultBuff)
        ComboDeathFault.onAfter(AdvancedFinalAttack)

        SwordIllusionInit.onAfter(core.RepeatElement(SwordIllusion, 12))
        SwordIllusionInit.onAfter(core.RepeatElement(SwordIllusionFinal, 5))
        SwordIllusion.onAfter(AdvancedFinalAttack)
        SwordIllusionFinal.onAfter(AdvancedFinalAttack)

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 3, 2)
        for sk in [RagingBlowEnrageFinalizer, ComboDeathFault, Incising, RisingRage]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        # Schedule
        Incising.onConstraint(
            core.ConstraintElement("인사이징 OFF", IncisingBuff, IncisingBuff.is_not_active)
        )

        return (
            RagingBlowEnrage,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                ComboAttack,
                SpiritBlade,
                EpicAdventure,
                Valhalla,
                ValhallaSummon,
                IncisingBuff,
                IncisingDot,
                AuraWeaponBuff,
                AuraWeapon,
                ComboDeathFaultBuff,
                ComboInstinct,
                globalSkill.soul_contract(),
            ]
            + [Incising, ComboDeathFault, SwordIllusionInit, RisingRage]
            + [SwordOfBurningSoul, MirrorBreak, MirrorSpider]
            + [RagingBlowEnrage],
        )
