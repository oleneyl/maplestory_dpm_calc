from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ComplexConditionRule, RuleSet, ConditionRule
from . import globalSkill
from .jobbranch import thieves
from . import jobutils
from math import ceil
from typing import Any, Dict

# TODO: 왜 레투다는 5차값이 1,1인데 레투다 패시브는 2,2일까?


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "LUK2"
        self.jobname = "듀얼블레이드"
        self.ability_list = Ability_tool.get_ability_set(
            "boss_pdamage", "crit", "buff_rem"
        )
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=36, armor_ignore=47.7)

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        Karma = core.InformedCharacterModifier("카르마", att=30)
        PhisicalTraining = core.InformedCharacterModifier(
            "피지컬 트레이닝", stat_main=30, stat_sub=30
        )

        SornsEffect = core.InformedCharacterModifier("쏜즈 이펙트", att=30 + passive_level)
        DualBladeExpert = core.InformedCharacterModifier(
            "이도류 엑스퍼트",
            att=30 + passive_level,
            pdamage_indep=20 + passive_level // 2,
        )
        Sharpness = core.InformedCharacterModifier(
            "샤프니스",
            crit=35 + 3 * passive_level,
            crit_damage=13 + passive_level,
        )
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 2, 2)

        return [
            Karma,
            PhisicalTraining,
            SornsEffect,
            DualBladeExpert,
            Sharpness,
            ReadyToDiePassive,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=30)
        Mastery = core.InformedCharacterModifier(
            "숙련도", mastery=90 + ceil(passive_level / 2)
        )
        return [WeaponConstant, Mastery]

    def get_ruleset(self):
        def check_final_cut_time(final_cut):
            return final_cut.is_not_usable() and final_cut.is_cooltime_left(
                80 * 1000, 1
            )  # 파컷 직후 써레 1번만 쓰는게 더 효율적임

        def sync_burst_buff(burst_buff, blade_storm, ultimate_dark_sight):
            if blade_storm.is_usable():
                if (
                    ultimate_dark_sight.is_cooltime_left(80000, 1)
                    or ultimate_dark_sight.is_active()
                ):
                    return True
            return False

        ruleset = RuleSet()
        ruleset.add_rule(
            ConditionRule("써든레이드", "파이널 컷", check_final_cut_time), RuleSet.BASE
        )
        ruleset.add_rule(
            ConditionRule("아수라", "카르마 퓨리", lambda sk: sk.is_cooltime_left(6000, 1)),
            RuleSet.BASE,
        )  # TODO: 쿨감 4초기준 최적화, 쿨감 수치를 받아와서 처리해야 함
        ruleset.add_rule(
            ComplexConditionRule("레디 투 다이", ["블레이드 스톰", "얼티밋 다크 사이트"], sync_burst_buff),
            RuleSet.BASE,
        )
        ruleset.add_rule(
            ComplexConditionRule("소울 컨트랙트", ["블레이드 스톰", "얼티밋 다크 사이트"], sync_burst_buff),
            RuleSet.BASE,
        )
        ruleset.add_rule(
            ConditionRule(
                "블레이드 스톰",
                "얼티밋 다크 사이트",
                lambda sk: sk.is_active() or sk.is_cooltime_left(80000, 1),
            ),
            RuleSet.BASE,
        )
        ruleset.add_rule(
            ConditionRule(
                "메이플월드 여신의 축복",
                "얼티밋 다크 사이트",
                lambda sk: sk.is_active() or sk.is_usable(),
            ),
            RuleSet.BASE,
        )
        return ruleset

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        하이퍼 : 팬텀 블로우 - 리인포스, 이그노어 가드, 보너스 어택
        블레이드 퓨리 - 리인포스, 엑스트라 타겟

        아수라 41타
        블레이드 토네이도 5타

        코어 16개 유효 : 팬블 / 아수라 / 퓨리 -- 써든레이드 / 어센션 / 히든블레이드
        """
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        # Buff skills
        Booster = core.BuffSkill("부스터", 0, 180000, rem=True).wrap(core.BuffSkillWrapper)

        DarkSight = core.BuffSkill("다크 사이트", 0, 1, cooltime=-1).wrap(
            core.BuffSkillWrapper
        )  # , pdamage_indep = 20 + 10 + int(0.2*vEhc.getV(3,3))).wrap(core.BuffSkillWrapper)

        PhantomBlow = (
            core.DamageSkill(
                "팬텀 블로우",
                delay=540,
                damage=315 + 3 * self.combat,
                hit=6 + 1,
                modifier=core.CharacterModifier(armor_ignore=44, pdamage=20),
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        SuddenRaid = (
            core.DamageSkill(
                "써든레이드",
                delay=690,
                damage=494 + 5 * self.combat,
                hit=7,
                cooltime=(30 - 2 * (self.combat // 2)) * 1000,
                red=True,
            )
            .setV(vEhc, 2, 2, False)
            .wrap(core.DamageSkillWrapper)
        )  # 파컷의 남은 쿨타임 20% 감소
        SuddenRaidDOT = core.DotSkill(
            "써든레이드(도트)",
            summondelay=0,
            delay=1000,
            damage=210 + 4 * self.combat,
            hit=1,
            remain=10000,
            cooltime=-1,
        ).wrap(core.DotSkillWrapper)

        FinalCut = core.DamageSkill(
            "파이널 컷",
            delay=450,
            damage=2000 + 20 * self.combat,
            hit=1,
            cooltime=90000,
            red=True,
        ).wrap(core.DamageSkillWrapper)
        FinalCutBuff = core.BuffSkill(
            "파이널 컷(버프)",
            delay=0,
            remain=60000,
            rem=True,
            cooltime=-1,
            pdamage_indep=40 + self.combat,
        ).wrap(core.BuffSkillWrapper)

        EpicAdventure = core.BuffSkill(
            "에픽 어드벤처",
            delay=0,
            remain=60 * 1000,
            cooltime=120 * 1000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)

        FlashBang = core.DamageSkill(
            "플래시 뱅",
            delay=390,
            damage=250,
            hit=1,
            cooltime=60000,
            red=True,
        ).wrap(
            core.DamageSkillWrapper
        )  # 임의 딜레이.
        FlashBangDebuff = core.BuffSkill(
            "플래시 뱅(디버프)",
            delay=0,
            remain=50000 / 2,
            cooltime=-1,
            pdamage=10 * 0.9,
        ).wrap(core.BuffSkillWrapper)
        Venom = core.DotSkill(
            "페이탈 베놈",
            summondelay=0,
            dealy=1000,
            damage=160 + 5 * passive_level,
            hit=2 + (10 + passive_level) // 6,  # 3회 중첩
            remain=8000,
            cooltime=-1,
        ).wrap(core.DotSkillWrapper)

        HiddenBladeBuff = core.BuffSkill(
            "히든 블레이드(버프)",
            delay=0,
            remain=60000,
            cooltime=90000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)
        HiddenBlade = (
            core.DamageSkill("히든 블레이드", delay=0, damage=140, hit=1)
            .setV(vEhc, 5, 2, True)
            .wrap(core.DamageSkillWrapper)
        )

        Asura = core.DamageSkill(
            "아수라",
            delay=810,
            damage=0,
            hit=0,
            cooltime=60000,
        ).wrap(core.DamageSkillWrapper)
        AsuraTick = (
            core.DamageSkill(
                "아수라(틱)",
                delay=300,
                damage=420,
                hit=4,
                modifier=core.CharacterModifier(armor_ignore=100),
            )
            .setV(vEhc, 1, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        AsuraEnd = core.DamageSkill(
            "아수라(종료)", delay=360, damage=0, hit=0, cooltime=-1
        ).wrap(core.DamageSkillWrapper)

        UltimateDarksight = thieves.UltimateDarkSightWrapper(vEhc, 3, 3, 20)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 4, 4)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        BladeStorm = (
            core.DamageSkill(
                "블레이드 스톰",
                delay=120,
                damage=580 + 23 * vEhc.getV(0, 0),
                hit=7,
                red=True,
                cooltime=90000,
                modifier=core.CharacterModifier(armor_ignore=100),
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )
        BladeStormTick = (
            core.DamageSkill(
                "블레이드 스톰(틱)",
                delay=210,
                damage=350 + 10 * vEhc.getV(0, 0),
                hit=5,
                modifier=core.CharacterModifier(armor_ignore=100),
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )  # 10000/210 타
        BladeStormEnd = core.DamageSkill("블레이드 스톰(종료)", 120, 0, 0).wrap(
            core.DamageSkillWrapper
        )

        KarmaFury = (
            core.DamageSkill(
                "카르마 퓨리",
                delay=750,
                damage=400 + 16 * vEhc.getV(1, 1),
                hit=7 * 5,
                red=True,
                cooltime=10000,
                modifier=core.CharacterModifier(armor_ignore=30),
            )
            .isV(vEhc, 1, 1)
            .wrap(core.DamageSkillWrapper)
        )
        BladeTornado = (
            core.DamageSkill(
                "블레이드 토네이도",
                delay=540,
                damage=600 + 24 * vEhc.getV(2, 2),
                hit=7,
                red=True,
                cooltime=12000,
                modifier=core.CharacterModifier(armor_ignore=100),
            )
            .isV(vEhc, 2, 2)
            .wrap(core.DamageSkillWrapper)
        )
        BladeTornadoSummon = (
            core.SummonSkill(
                "블레이드 토네이도(소환)",
                summondelay=0,
                delay=3000 / 5,
                damage=400 + 16 * vEhc.getV(2, 2),
                hit=6,
                remain=3000 - 1,
                cooltime=-1,
                modifier=core.CharacterModifier(armor_ignore=100),
            )
            .isV(vEhc, 2, 2)
            .wrap(core.SummonSkillWrapper)
        )
        BladeTornadoSummonMirrorImaging = (
            core.SummonSkill(
                "블레이드 토네이도(소환)(미러이미징)",
                summondelay=0,
                delay=3000 / 5,
                damage=(400 + 16 * vEhc.getV(2, 2)) * 0.7,
                hit=6,
                remain=3000 - 1,
                cooltime=-1,
                modifier=core.CharacterModifier(armor_ignore=100),
            )
            .isV(vEhc, 2, 2)
            .wrap(core.SummonSkillWrapper)
        )

        HauntedEdge = (
            core.DamageSkill(
                "헌티드 엣지-나찰",
                delay=0,
                damage=200 + 8 * vEhc.getV(0, 0),
                hit=4 * 5,
                cooltime=14000,
                red=True,
                modifier=core.CharacterModifier(armor_ignore=30),
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )

        ######   Skill Wrapper   ######

        SuddenRaid.onAfter(SuddenRaidDOT)
        FinalCut.onAfter(FinalCutBuff)

        HiddenBladeOpt = core.OptionalElement(HiddenBladeBuff.is_active, HiddenBlade)

        FlashBang.onAfter(FlashBangDebuff)
        for sk in [
            FinalCut,
            PhantomBlow,
            SuddenRaid,
            FlashBang,
            AsuraTick,
            BladeStorm,
            BladeStormTick,
            BladeTornado,
            KarmaFury,
        ]:
            sk.onAfter(HiddenBladeOpt)

        for sk in [PhantomBlow, AsuraTick, BladeStormTick]:
            sk.onAfter(Venom)

        AsuraRepeat = core.RepeatElement(
            AsuraTick, 26
        )  # 최대 28회까지 가능하나, dpm 최적화를 위해 26회로 설정함.
        Asura.onAfter(AsuraRepeat)
        AsuraRepeat.onAfter(AsuraEnd)

        BladeStormRepeat = core.RepeatElement(BladeStormTick, 48)
        BladeStorm.onAfter(BladeStormRepeat)
        BladeStormRepeat.onAfter(BladeStormEnd)

        BladeTornado.onAfter(BladeTornadoSummon)
        BladeTornado.onAfter(BladeTornadoSummonMirrorImaging)

        SuddenRaid.onAfter(FinalCut.controller(0.2, "reduce_cooltime_p"))

        PhantomBlow.onAfter(
            core.OptionalElement(
                HauntedEdge.is_available, HauntedEdge, name="헌티드 엣지 쿨타임 체크"
            )
        )
        HauntedEdge.protect_from_running()

        for sk in [
            PhantomBlow,
            SuddenRaid,
            FinalCut,
            FlashBang,
            AsuraTick,
            BladeStorm,
            BladeStormTick,
            KarmaFury,
            BladeTornado,
            HiddenBlade,
            HauntedEdge,
        ]:
            jobutils.create_auxilary_attack(sk, 0.7, nametag="(미러이미징)")

        return (
            PhantomBlow,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                Booster,
                DarkSight,
                FinalCutBuff,
                EpicAdventure,
                FlashBangDebuff,
                HiddenBladeBuff,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                UltimateDarksight,
                ReadyToDie,
                globalSkill.soul_contract(),
            ]
            + [
                FinalCut,
                FlashBang,
                BladeTornado,
                SuddenRaid,
                KarmaFury,
                BladeStorm,
                Asura,
                MirrorBreak,
                MirrorSpider,
            ]
            + [
                SuddenRaidDOT,
                Venom,
                BladeTornadoSummon,
                BladeTornadoSummonMirrorImaging,
                HauntedEdge,
            ]
            + []
            + [PhantomBlow],
        )
