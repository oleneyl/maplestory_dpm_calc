from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, MutualRule, ConcurrentRunRule, ReservationRule
from . import globalSkill, jobutils
from .jobbranch import bowmen
from .jobclass import adventurer
from math import ceil
from typing import Any, Dict


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "DEX"
        self.jobname = "신궁"
        self.ability_list = Ability_tool.get_ability_set(
            "boss_pdamage", "crit", "buff_rem"
        )
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore=25, boss_pdamage=17, crit_damage=25)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(MutualRule("스플릿 애로우", "트루 스나이핑"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("에픽 어드벤처", "크리티컬 리인포스"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("불스아이", "크리티컬 리인포스"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("소울 컨트랙트", "크리티컬 리인포스"), RuleSet.BASE)
        ruleset.add_rule(ReservationRule("크리티컬 리인포스", "스플릿 애로우"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("스플릿 애로우", "소울 컨트랙트"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("리피팅 크로스보우 카트리지", "소울 컨트랙트"), RuleSet.BASE)

        return ruleset

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        CriticalShot = core.InformedCharacterModifier("크리티컬 샷", crit=40)
        CrossbowAccelation = core.InformedCharacterModifier("크로스보우 엑셀레이션", stat_main=20)
        PhisicalTraining = core.InformedCharacterModifier(
            "피지컬 트레이닝", stat_main=30, stat_sub=30
        )
        SoulArrow = core.InformedCharacterModifier("소울 애로우 : 석궁", att=30)
        CrossBowMastery = core.InformedCharacterModifier("크로스보우 마스터리", pdamage_indep=20)
        MarkmanShip = core.InformedCharacterModifier(
            "마크맨쉽", armor_ignore=25, pdamage=15
        )
        CrossBowExpert = core.InformedCharacterModifier(
            "크로스보우 엑스퍼트", att=30 + passive_level, crit_damage=15
        )
        ElusionStep = core.InformedCharacterModifier(
            "일루젼 스탭", stat_main=80 + passive_level * 2
        )
        AdditionalBolt = core.InformedCharacterModifier(
            "어디셔널 볼트", pdamage_indep=15 + passive_level
        )
        AdvancedEnhanceArrow = core.InformedCharacterModifier(
            "어드밴스드 인핸스 애로우(패시브)", pdamage_indep=8, armor_ignore=20
        )
        ArrowIllusion = core.InformedCharacterModifier(
            "애로우 일루전(패시브)", armor_ignore=30 + self.combat
        )
        LastmanStanding = core.InformedCharacterModifier(
            "라스트맨 스탠딩", pdamage_indep=10 + passive_level
        )

        return [
            CriticalShot,
            CrossbowAccelation,
            PhisicalTraining,
            SoulArrow,
            CrossBowMastery,
            MarkmanShip,
            CrossBowExpert,
            ElusionStep,
            AdditionalBolt,
            AdvancedEnhanceArrow,
            ArrowIllusion,
            LastmanStanding,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=35)
        Mastery = core.InformedCharacterModifier(
            "숙련도", mastery=85 + ceil(passive_level / 2)
        )

        MortalBlow = core.InformedCharacterModifier("모탈 블로우", pdamage=2)
        ExtremeArchery = core.InformedCharacterModifier("익스트림 아처리:석궁", crit_damage=20)

        return [WeaponConstant, Mastery, MortalBlow, ExtremeArchery]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """ """
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        MORTAL_BLOW = core.CharacterModifier(pdamage=2)
        ADDITIONAL_BOLT = 1

        # Buff skills
        SharpEyes = core.BuffSkill(
            name="샤프 아이즈",
            delay=0,  # 펫버프
            remain=(300 + 10 * self.combat) * 1000,
            crit=20 + ceil(self.combat / 2),
            crit_damage=15 + ceil(self.combat / 2),
            rem=True,
        ).wrap(core.BuffSkillWrapper)

        FocusOn = core.BuffSkill(
            name="포커스 온", delay=0, remain=15000, pdamage_indep=4, armor_ignore=13
        ).wrap(core.BuffSkillWrapper)

        BoolsEye = core.BuffSkill(
            name="불스아이",
            delay=960,
            remain=30 * 1000,
            cooltime=90 * 1000,
            crit=20,
            crit_damage=10,
            armor_ignore=20,
            pdamage=20,
        ).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill(
            name="에픽 어드벤처",
            delay=0,
            remain=60 * 1000,
            cooltime=120 * 1000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)

        EnhanceStack = core.StackSkillWrapper(core.BuffSkill("인핸스 중첩", 0, 9999999), 3)
        EnhanceSnipingTarget = core.BuffSkill(
            "인핸스 스나이핑(표식)", delay=0, remain=5000, cooltime=-1
        ).wrap(core.BuffSkillWrapper)

        # Damage Skills
        SNIPING_MODIFIER = (
            core.CharacterModifier(
                crit=100,
                armor_ignore=25 + ceil(self.combat // 3) * 2,
                pdamage=20,
                boss_pdamage=10,
            )
            + MORTAL_BLOW
        )
        Sniping = (
            core.DamageSkill(
                name="스나이핑",
                delay=600,
                damage=465 + self.combat * 5,
                hit=9 + 1 + ADDITIONAL_BOLT,
                modifier=SNIPING_MODIFIER + MORTAL_BLOW,
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        EnhanceSniping = (
            core.DamageSkill(
                name="인핸스 스나이핑",
                delay=630,
                damage=510 + passive_level * 7,
                hit=10 + 1 + ADDITIONAL_BOLT,
                modifier=SNIPING_MODIFIER + MORTAL_BLOW,
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        EnhanceSnipingTargetBonus = (
            core.DamageSkill(
                name="인핸스 스나이핑(추가타)",
                delay=0,
                damage=250 + passive_level * 2,
                hit=5 + ADDITIONAL_BOLT,
                modifier=SNIPING_MODIFIER + MORTAL_BLOW,
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        TrueSnipingTick = (
            core.DamageSkill(
                name="트루 스나이핑(타격)",
                delay=690,
                damage=950 + vEhc.getV(2, 2) * 30,
                hit=14 + ADDITIONAL_BOLT,
                modifier=core.CharacterModifier(pdamage=100, armor_ignore=100)
                + MORTAL_BLOW,
            )
            .isV(vEhc, 2, 2)
            .wrap(core.DamageSkillWrapper)
        )
        TrueSniping = (
            core.DamageSkill("트루 스나이핑", 120, 0, 0, cooltime=180 * 1000, red=True)
            .isV(vEhc, 2, 2)
            .wrap(core.DamageSkillWrapper)
        )

        ChargedArrow = (
            core.DamageSkill(
                name="차지드 애로우",
                delay=0,
                damage=750 + vEhc.getV(1, 1) * 30,
                hit=10 + ADDITIONAL_BOLT,
                cooltime=-1,
                modifier=MORTAL_BLOW,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.DamageSkillWrapper)
        )
        ChargedArrowHold = (
            core.SummonSkill("차지드 애로우(더미)", 0, 10000, 0, 0, 9999999, cooltime=-1)
            .isV(vEhc, 1, 1)
            .wrap(core.SummonSkillWrapper)
        )  # TODO: 공격 주기에 쿨감 적용해야 함

        # Summon Skills
        Freezer = (
            core.SummonSkill(
                name="프리저",
                summondelay=0,
                delay=1710,
                damage=390,
                hit=1,
                remain=220 * 1000,
            )
            .setV(vEhc, 3, 3, False)
            .wrap(core.SummonSkillWrapper)
        )  # 이볼브 종료시 자동소환되므로 딜레이 0
        Evolve = adventurer.EvolveWrapper(vEhc, 5, 5, Freezer)

        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 4, 4, modifier=MORTAL_BLOW)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(
            vEhc, 0, 0, break_modifier=MORTAL_BLOW
        )

        SplitArrow = (
            core.DamageSkill(
                name="스플릿 애로우(공격)",
                delay=0,
                damage=600 + vEhc.getV(0, 0) * 24,
                hit=5 + ADDITIONAL_BOLT,
                modifier=MORTAL_BLOW,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )
        SplitArrowBuff = (
            core.BuffSkill(
                name="스플릿 애로우",
                delay=810,
                remain=72 * 1000,
                cooltime=120 * 1000,
                red=True,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.BuffSkillWrapper)
        )

        RepeatingCartrige = (
            core.BuffSkill(
                name="리피팅 크로스보우 카트리지",
                delay=510,
                remain=60000,
                cooltime=120 * 1000,
                red=True,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.BuffSkillWrapper)
        )
        CartrigeStack = core.StackSkillWrapper(core.BuffSkill("카트리지", 0, 99999999), 8)
        FullBurstShot = (
            core.DamageSkill(
                name="풀버스트 샷",
                delay=810,
                damage=300 + 12 * vEhc.getV(0, 0),
                hit=(9 + ADDITIONAL_BOLT) * 4,
                cooltime=-1,
                modifier=MORTAL_BLOW,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )

        FinalAttack = (
            core.DamageSkill(
                name="파이널 어택",
                delay=0,
                damage=150,
                hit=0.4,
            )
            .setV(vEhc, 4, 2, True)
            .wrap(core.DamageSkillWrapper)
        )

        ######   Skill Wrapper   ######

        CriticalReinforce = bowmen.CriticalReinforceWrapper(
            vEhc, chtr, 3, 3, 20 + 20 + ceil(self.combat / 2)
        )  # 샤프 아이즈 20 + 불스아이 20. 불스아이를 항상 크리인에 맞춰쓰므로 가동률 고려 X

        Sniping.onAfter(
            core.OptionalElement(
                EnhanceSnipingTarget.is_active, EnhanceSnipingTargetBonus
            )
        )
        Sniping.onAfter(EnhanceStack.stackController(1))
        EnhanceSniping.onAfter(EnhanceSnipingTarget)
        EnhanceSniping.onAfter(EnhanceStack.stackController(-3))
        EnhanceSnipingTargetBonus.onJustAfter(
            EnhanceSnipingTarget.controller(0, "set_disabled")
        )

        SplitArrowOption = core.OptionalElement(
            SplitArrowBuff.is_active, SplitArrow, name="스플릿 애로우 여부 확인"
        )
        Sniping.onAfter(SplitArrowOption)
        EnhanceSniping.onAfter(SplitArrowOption)
        FullBurstShot.onAfter(core.RepeatElement(SplitArrowOption, 4))

        TrueSnipingDeal = core.RepeatElement(TrueSnipingTick, 7)
        TrueSniping.onBefore(ChargedArrowHold.controller(10000, name="차징 유예"))
        TrueSniping.onAfter(TrueSnipingDeal)

        # TODO: 차지드 캔슬 구현할것 / 딜레이 중간에 끊는게 구현되기 전까지 어려움
        ChargedArrowHold.onTick(
            core.OptionalElement(partial(CartrigeStack.judge, 0, -1), ChargedArrow)
        )  # 풀버스트샷 도중에는 차지드 동시발사가 안됨

        for sk in [EnhanceSniping, TrueSnipingTick, ChargedArrow, FullBurstShot]:
            sk.onAfter(FocusOn)

        for sk in [Sniping, EnhanceSniping, TrueSnipingTick, ChargedArrow]:
            sk.onAfter(FinalAttack)
        FullBurstShot.onAfter(core.RepeatElement(FinalAttack, 4))

        ChargedArrowHold.set_disabled_and_time_left(3000)  # 최초 차징 시간

        RepeatingCartrige.onAfter(CartrigeStack.stackController(8))
        FullBurstShot.onAfter(CartrigeStack.stackController(-1))

        BasicAttack = core.DamageSkill("기본 공격", 0, 0, 0).wrap(core.DamageSkillWrapper)
        BasicAttack.onAfter(
            core.OptionalElement(
                partial(CartrigeStack.judge, 1, 1),
                FullBurstShot,
                core.OptionalElement(
                    partial(EnhanceStack.judge, 3, 1), EnhanceSniping, Sniping
                ),
            )
        )

        return (
            BasicAttack,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_combat_orders(),
                SharpEyes,
                BoolsEye,
                EpicAdventure,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                CriticalReinforce,
                RepeatingCartrige,
                SplitArrowBuff,
                globalSkill.soul_contract(),
            ]
            + [TrueSniping, ChargedArrowHold, ChargedArrow]
            + [Freezer, Evolve, GuidedArrow, MirrorBreak, MirrorSpider]
            + [EnhanceSnipingTarget, FocusOn]
            + [BasicAttack],
        )
