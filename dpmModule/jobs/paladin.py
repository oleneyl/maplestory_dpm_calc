from functools import partial
from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import ComplexConditionRule, ConditionRule, RuleSet
from . import globalSkill, jobutils
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict


# 4차 스킬은 컴뱃오더스 적용 기준으로 작성해야 함.
class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "STR"
        self.jobname = "팔라딘"
        self.ability_list = Ability_tool.get_ability_set(
            "boss_pdamage", "crit", "buff_rem"
        )
        self.preEmptiveSkills = 2

    def get_ruleset(self):
        def use_mighty_mjolnir(mjolnir, unity):
            if mjolnir.stack >= 2:
                return True
            if unity.is_not_active():
                return False
            return True

        ruleset = RuleSet()
        ruleset.add_rule(
            ComplexConditionRule("마이티 묠니르(시전)", ["홀리 유니티"], use_mighty_mjolnir),
            RuleSet.BASE,
        )
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(boss_pdamage=29, armor_ignore=18)

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level
        PhisicalTraining = core.InformedCharacterModifier(
            "피지컬 트레이닝", stat_main=30, stat_sub=30
        )
        ShieldMastery = core.InformedCharacterModifier("실드 마스터리", att=10)
        WeaponAccelation = core.InformedCharacterModifier("웨폰 엑셀레이션", stat_main=20)

        PaladinExpert = core.InformedCharacterModifier(
            "팔라딘 엑스퍼트(두손둔기)",
            crit_damage=5 + (32 + passive_level) // 3,
            pdamage_indep=42 + passive_level,
            crit=42 + passive_level,
            armor_ignore=15 + ceil((32 + passive_level) / 2),
        ) + core.ExtendedCharacterModifier(crit_damage=5, armor_ignore=10)
        PaladinExpert = core.InformedCharacterModifier.from_extended_modifier(
            "팔라딘 엑스퍼트(두손둔기)", PaladinExpert
        )
        return [PhisicalTraining, ShieldMastery, WeaponAccelation, PaladinExpert]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=34)
        Mastery = core.InformedCharacterModifier(
            "숙련도", mastery=90 + 1 + ceil(passive_level / 2)
        )  # 오더스 기본적용!

        HolyCharge = core.InformedCharacterModifier("홀리 차지", pdamage=25, att=60)
        ParashockGuard = core.InformedCharacterModifier("파라쇼크 가드", att=20)

        return [WeaponConstant, Mastery, HolyCharge, ParashockGuard]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        두손둔기

        블래-라차-디차-생츄-파택

        블레싱 아머 미적용.

        블래스트-리인포스, 보너스 어택 / 생츄어리-보너스 어택, 쿨타임 리듀스, 리인포스
        """
        buff_rem = chtr.get_base_modifier().buff_rem

        # Buff skills
        NobleDemand = core.BuffSkill(
            "노블 디맨드",
            delay=720,
            remain=80 * 1000,
            armor_ignore=50,
        ).wrap(core.BuffSkillWrapper)
        DivineBlessing = core.BuffSkill(
            "디바인 블레싱",
            delay=0,  # 펫버프
            remain=206 * 1000,
            pdamage_indep=21,
            rem=True,
        ).wrap(core.BuffSkillWrapper)

        EpicAdventure = core.BuffSkill(
            "에픽 어드벤처",
            delay=0,
            remain=60 * 1000,
            cooltime=120 * 1000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)

        HolyUnity = (
            core.BuffSkill(
                "홀리 유니티",
                delay=600,
                remain=(30 + vEhc.getV(0, 0) // 2) * 1000,
                cooltime=90 * 1000,
                red=True,
                pdamage_indep=60 + vEhc.getV(0, 0) // 2,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.BuffSkillWrapper)
        )

        # Damage Skills
        Sanctuary = (
            core.DamageSkill(
                "생츄어리",
                delay=750,
                damage=580,
                hit=8 + 2,
                cooltime=14 * 0.7 * 1000,
                red=True,
                modifier=core.CharacterModifier(boss_pdamage=30, pdamage=20),
            )
            .setV(vEhc, 3, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        Blast = (
            core.DamageSkill(
                "블래스트",
                delay=600,
                damage=291,
                hit=10 + 1 + 1,
                modifier=core.CharacterModifier(pdamage=20),
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        DivineJudgement = (
            core.DamageSkill(
                "디바인 저지먼트",
                delay=0,
                damage=506,
                hit=10,
                modifier=core.CharacterModifier(armor_ignore=20),
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        DivineJudgementStack = core.StackSkillWrapper(
            core.BuffSkill("신성 낙인", 0, 9999999), 5
        )

        MightyMjollnirInit = core.StackableDamageSkillWrapper(
            core.DamageSkill(
                "마이티 묠니르(시전)",
                delay=630,
                damage=0,
                hit=0,
                cooltime=15000,
            ).isV(vEhc, 0, 0),
            2,
        )
        MightyMjollnir = (
            core.DamageSkill(
                "마이티 묠니르",
                delay=0,
                damage=225 + 9 * vEhc.getV(0, 0),
                hit=6,
                cooltime=-1,
                modifier=core.CharacterModifier(crit=50),
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )
        MightyMjollnirWave = (
            core.DamageSkill(
                "마이티 묠니르(충격파)",
                delay=0,
                damage=250 + 10 * vEhc.getV(0, 0),
                hit=9,
                cooltime=-1,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )

        # Summon Skills
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        BlessedHammer = (
            core.SummonSkill(
                "블래스드 해머",
                summondelay=0,
                delay=600,
                damage=250 + vEhc.getV(1, 1) * 10,
                hit=2,
                remain=999999 * 10000,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.SummonSkillWrapper)
        )
        BlessedHammerActive = (
            core.SummonSkill(
                "블레스드 해머(활성화)",
                summondelay=360,
                delay=600,
                damage=525 + vEhc.getV(1, 1) * 21,
                hit=4,
                remain=30 * 1000,
                cooltime=60 * 1000,
                red=True,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.SummonSkillWrapper)
        )
        GrandCross = core.DamageSkill(
            "그랜드 크로스",
            delay=900,
            damage=0,
            hit=0,
            cooltime=180 * 1000,
            red=True,
        ).wrap(core.DamageSkillWrapper)
        GrandCrossSmallTick = (
            core.DamageSkill(
                "그랜드 크로스(작은)",
                delay=210,
                damage=270 + vEhc.getV(3, 3) * 13,
                hit=12,
                modifier=core.CharacterModifier(crit=100, armor_ignore=100),
            )
            .isV(vEhc, 3, 3)
            .wrap(core.DamageSkillWrapper)
        )
        GrandCrossLargeTick = (
            core.DamageSkill(
                "그랜드 크로스(강화)",
                delay=120,
                damage=490 + vEhc.getV(3, 3) * 22,
                hit=12,
                modifier=core.CharacterModifier(crit=100, armor_ignore=100),
            )
            .isV(vEhc, 3, 3)
            .wrap(core.DamageSkillWrapper)
        )
        GrandCrossEnd = core.DamageSkill(
            "그랜드 크로스(종료)", delay=450, damage=0, hit=0
        ).wrap(core.DamageSkillWrapper)

        FinalAttack = (
            core.DamageSkill("파이널 어택", 0, 80, 2 * 0.4)
            .setV(vEhc, 4, 5, True)
            .wrap(core.DamageSkillWrapper)
        )

        ######   Skill Wrapper   ######

        # Damage skill
        Blast.onAfter(FinalAttack)
        Sanctuary.onAfter(FinalAttack)

        GrandCrossSmallTick.onAfter(FinalAttack)
        GrandCrossLargeTick.onAfter(FinalAttack)
        GrandCross.onAfter(core.RepeatElement(GrandCrossSmallTick, 7))
        GrandCross.onAfter(core.RepeatElement(GrandCrossLargeTick, 31))
        GrandCross.onAfter(GrandCrossEnd)

        BlessedHammer.onTick(FinalAttack)
        BlessedHammerActive.onAfter(BlessedHammer.controller(99999999))
        BlessedHammerActive.onEventEnd(BlessedHammer)

        MightyMjollnirInit.onAfter(core.RepeatElement(MightyMjollnir, 4))
        MightyMjollnir.onAfter(MightyMjollnirWave)

        IncreaseJudgement = DivineJudgementStack.stackController(1)
        IncreaseJudgement.onJustAfter(core.OptionalElement(partial(DivineJudgementStack.judge, 5, 1), DivineJudgement))
        DivineJudgement.onJustAfter(DivineJudgementStack.stackController(-5))

        Blast.onJustAfter(IncreaseJudgement)

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 2)
        for sk in [
            Blast,
            Sanctuary,
            GrandCrossSmallTick,
            GrandCrossLargeTick,
            MightyMjollnirInit,
        ]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        return (
            Blast,
            [
                globalSkill.maple_heros(chtr.level, combat_level=2),
                globalSkill.useful_sharp_eyes(),
                NobleDemand,
                DivineBlessing,
                EpicAdventure,
                HolyUnity,
                AuraWeaponBuff,
                AuraWeapon,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, combat_level=2),
                globalSkill.soul_contract(),
            ]
            + [
                MightyMjollnirInit,
                GrandCross,
                Sanctuary,
                MirrorBreak,
                MirrorSpider,
            ]
            + [BlessedHammer, BlessedHammerActive]
            + [Blast],
        )
