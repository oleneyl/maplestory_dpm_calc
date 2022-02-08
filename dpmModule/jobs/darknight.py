from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict

# TODO: 비홀더스 리벤지 메인 효과 추가


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = (7, 7)
        self.jobtype = "STR"
        self.jobname = "다크나이트"
        self.vEnhanceNum = 9
        self.ability_list = Ability_tool.get_ability_set(
            "buff_rem", "reuse", "boss_pdamage"
        )
        self.preEmptiveSkills = 2

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(boss_pdamage=60, armor_ignore=44)

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponMastery = core.InformedCharacterModifier("웨폰 마스터리", pdamage=5)
        PhisicalTraining = core.InformedCharacterModifier(
            "피지컬 트레이닝", stat_main=30, stat_sub=30
        )
        WeaponAccelation = core.InformedCharacterModifier("웨폰 엑셀레이션", stat_main=20)

        LordOfDarkness = core.InformedCharacterModifier(
            "로드 오브 다크니스", crit=30, crit_damage=8
        )

        AdvancedWeaponMastery = core.InformedCharacterModifier(
            "어드밴스드 웨폰 마스터리", att=30 + passive_level, crit_damage=15 + passive_level // 3
        )
        ReincarnationBuff = core.InformedCharacterModifier(
            "리인카네이션(패시브)",
            pdamage_indep=30 + passive_level + 5,
            crit=10 + ceil(passive_level / 3) + 20,
            crit_damage=15 + passive_level // 3,
        )

        DarkResonancePassive = core.InformedCharacterModifier(
            "다크 레조넌스(패시브)", armor_ignore=30 + self.combat
        )
        CrossoverChainPassive = core.InformedCharacterModifier(
            "크로스 오버 체인(패시브)", pdamage_indep=50
        )
        return [
            WeaponMastery,
            PhisicalTraining,
            WeaponAccelation,
            LordOfDarkness,
            AdvancedWeaponMastery,
            ReincarnationBuff,
            DarkResonancePassive,
            CrossoverChainPassive,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=49)
        Mastery = core.InformedCharacterModifier(
            "숙련도", mastery=90 + ceil(passive_level / 2)
        )
        BiholdersBuff = core.InformedCharacterModifier("비홀더스 버프", att=40, crit=10)

        return [WeaponConstant, Mastery, BiholdersBuff]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        창 사용
        크오체 HP >= 50%
        비홀더 - 리인포스
        리인카네이션 - 데미지, 크리티컬 레이트
        궁그닐 - 리인포스, 이그노어 가드

        비홀더 임팩트 9타
        피어스 사이클론 25타
        다크 스피어 10히트
        """
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        HP_RATE = options.get("hp_rate", 100)

        # Buff skills
        CrossoverChain = core.BuffSkill(
            "크로스 오버 체인",
            delay=0,  # 펫버프
            remain=200 * 1000,
            pdamage_indep=20 * min(HP_RATE, 50) / 50,
        ).wrap(core.BuffSkillWrapper)
        FinalAttack = (
            core.DamageSkill("파이널 어택", delay=0, damage=80, hit=2 * 0.4)
            .setV(vEhc, 3, 4, True)
            .wrap(core.DamageSkillWrapper)
        )
        BiholderDominant = (
            core.SummonSkill(
                "비홀더 도미넌트",
                summondelay=0,
                delay=10000,
                damage=210,
                hit=1,
                remain=99999 * 10000,
                modifier=core.CharacterModifier(pdamage=150),
            )
            .setV(vEhc, 2, 3, False)
            .wrap(core.SummonSkillWrapper)
        )
        BiholderShock = (
            core.DamageSkill(
                "비홀더 쇼크",
                delay=0,
                damage=370 + 3 * passive_level,
                hit=6,
                cooltime=10000,
                red=True,
                modifier=core.CharacterModifier(pdamage=150),
            )
            .setV(vEhc, 2, 3, False)
            .wrap(core.DamageSkillWrapper)
        )
        BiholderShockTandem = (
            core.DamageSkill(
                "비홀더 쇼크(암흑 투기)",
                delay=0,
                damage=350 + 5 * passive_level,
                hit=3,
                cooltime=-1,
                modifier=core.CharacterModifier(pdamage=150),
            )
            .setV(vEhc, 2, 3, False)
            .wrap(core.DamageSkillWrapper)
        )
        BiholderRevenge = (
            core.DamageSkill(
                "비홀더스 리벤지",
                delay=0,
                damage=182 + 2 * passive_level,
                hit=5,
                cooltime=5000,
                red=True,
                modifier=core.CharacterModifier(pdamage=150),
            )
            .setV(vEhc, 2, 3, False)
            .wrap(core.DamageSkillWrapper)
        )

        GOUNGNIL_MODIFIER = core.CharacterModifier(
            armor_ignore=30 + self.combat
        ) + core.CharacterModifier(armor_ignore=20, pdamage=20)
        GoungnilDescent = (
            core.DamageSkill(
                "궁니르 디센트",
                delay=600,
                damage=225 + self.combat,
                hit=12,
                modifier=GOUNGNIL_MODIFIER,
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        DarkResonance = core.BuffSkill(
            "다크 레조넌스",
            delay=960,
            remain=(30 + self.combat // 2) * 1000,
            rem=True,
            red=True,
            cooltime=70000,
            armor_ignore=10 + ceil(self.combat / 3),
            boss_pdamage=10 + ceil(self.combat / 3),
            pdamage_indep=2 + ceil((30 + self.combat) / 4),
        ).wrap(core.BuffSkillWrapper)

        # 하이퍼
        DarkThurst = core.BuffSkill(
            "다크 서스트",
            delay=900,
            remain=30000,
            cooltime=120 * 1000,
            att=80,
        ).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill(
            "에픽 어드벤처",
            delay=0,
            remain=60 * 1000,
            cooltime=120 * 1000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)

        # 5차
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        DarkSpear = (
            core.DamageSkill(
                "다크 스피어",
                delay=750,
                damage=325 + 13 * vEhc.getV(1, 0),
                hit=7 * 10,
                cooltime=10000,
                red=True,
                modifier=core.CharacterModifier(crit=100, armor_ignore=50),
            )
            .isV(vEhc, 1, 0)
            .wrap(core.DamageSkillWrapper)
        )
        BiholderImpact = (
            core.SummonSkill(
                "비홀더 임팩트",
                summondelay=0,
                delay=270,
                damage=100 + vEhc.getV(0, 2),
                hit=6,
                remain=2880,
                cooltime=20000,
                red=True,
                modifier=core.CharacterModifier(pdamage=150, armor_ignore=20),
            )
            .setV(vEhc, 2, 3, False)
            .isV(vEhc, 0, 2)
            .wrap(core.SummonSkillWrapper)
        )  # onTick으로 0.3초씩
        PierceCyclone = core.DamageSkill(
            "피어스 사이클론(더미)",
            delay=90,
            damage=0,
            hit=0,
            cooltime=180 * 1000,
            red=True,
        ).wrap(core.DamageSkillWrapper)
        PierceCycloneTick = (
            core.DamageSkill(
                "피어스 사이클론",
                delay=180,
                damage=470 + 19 * vEhc.getV(3, 3),
                hit=12,
                modifier=core.CharacterModifier(crit=100, armor_ignore=50),
            )
            .isV(vEhc, 3, 3)
            .wrap(core.DamageSkillWrapper)
        )  # 25회 반복
        PierceCycloneEnd = (
            core.DamageSkill(
                "피어스 사이클론(종료)",
                delay=900,
                damage=360 + 14 * vEhc.getV(3, 3),
                hit=15 * 5,
                modifier=core.CharacterModifier(crit=100, armor_ignore=50),
            )
            .isV(vEhc, 3, 3)
            .wrap(core.DamageSkillWrapper)
        )
        DarknessAura = (
            core.SummonSkill(
                "다크니스 오라",
                summondelay=600,
                delay=1530,
                damage=400 + 16 * vEhc.getV(0, 0),
                hit=5,
                remain=40000,
                cooltime=180 * 1000,
                red=True,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.SummonSkillWrapper)
        )
        DarknessAuraFinal = (
            core.DamageSkill(
                "다크니스 오라(폭발)",
                delay=0,
                damage=675 + 26 * vEhc.getV(0, 0),
                hit=13 * (1 + 15 // 3),
                cooltime=-1,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )  # 생명력 3마다 폭발 1회 추가, 생명력 최대 15

        ######   Skill Wrapper   ######

        # Damage skill
        GoungnilDescent.onAfter(FinalAttack)

        PierceCycloneTick.onAfter(FinalAttack)
        PierceCycloneEnd.onAfter(core.RepeatElement(FinalAttack, 5))
        PierceCyclone_ = core.RepeatElement(PierceCycloneTick, 25)
        PierceCyclone_.onAfter(PierceCycloneEnd)
        PierceCyclone.onAfter(PierceCyclone_)

        DarknessAura.onEventEnd(DarknessAuraFinal)

        BiholderShock.onAfter(BiholderShockTandem)

        UseBiholderRevenge = core.OptionalElement(
            BiholderRevenge.is_available, BiholderRevenge
        )
        ReduceDarkResonance = DarkResonance.controller(350, "reduce_cooltime")
        for sk in [
            GoungnilDescent,
            DarkSpear,
            PierceCyclone,
            PierceCycloneEnd,
        ]:
            sk.onAfter(UseBiholderRevenge)
            sk.onAfter(ReduceDarkResonance)

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 1)
        for sk in [
            GoungnilDescent,
            DarkSpear,
            PierceCycloneEnd,
        ]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        BiholderRevenge.protect_from_running()

        return (
            GoungnilDescent,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                CrossoverChain,
                DarkResonance,
                EpicAdventure,
                DarkThurst,
                AuraWeaponBuff,
                AuraWeapon,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                globalSkill.soul_contract(),
            ]
            + [
                DarknessAura,
                DarknessAuraFinal,
                BiholderShock,
                DarkSpear,
                PierceCyclone,
                MirrorBreak,
                MirrorSpider,
            ]
            + [BiholderDominant, BiholderImpact, BiholderRevenge]
            + [GoungnilDescent],
        )
