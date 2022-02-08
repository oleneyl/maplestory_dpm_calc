from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule, ComplexConditionRule
from . import globalSkill, jobutils
from .jobbranch import bowmen
from .jobclass import cygnus
from math import ceil
from typing import Any, Dict


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "DEX"
        self.jobname = "윈드브레이커"
        self.ability_list = Ability_tool.get_ability_set(
            "boss_pdamage", "crit", "buff_rem"
        )

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule("소울 컨트랙트", "크리티컬 리인포스"), RuleSet.BASE)

        def howling_gale_rule(howling_gale, critical_reinforce):
            if critical_reinforce.is_active():
                return True
            if howling_gale.judge(1, -1) and critical_reinforce.is_cooltime_left(
                25000, -1
            ):
                return False
            return True

        ruleset.add_rule(
            ComplexConditionRule("하울링 게일", ["크리티컬 리인포스"], howling_gale_rule),
            RuleSet.BASE,
        )
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=45, armor_ignore=15)

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트", patt=10)
        ElementalHarmony = core.InformedCharacterModifier(
            "엘리멘탈 하모니", stat_main=chtr.level // 2
        )

        WhisperOfWind = core.InformedCharacterModifier("위스퍼 오브 윈드", att=20)
        PhisicalTraining = core.InformedCharacterModifier(
            "피지컬 트레이닝", stat_main=30, stat_sub=30
        )

        Albatross = core.InformedCharacterModifier(
            "알바트로스", att=20, crit=10
        )

        WindBlessingPassive = core.InformedCharacterModifier(
            "윈드 블레싱(패시브)",
            pstat_main=15 + passive_level // 3,
            patt=10 + ceil(passive_level / 3),
        )
        BowExpert = core.InformedCharacterModifier(
            "보우 엑스퍼트",
            att=30 + passive_level,
            crit_damage=20 + passive_level // 2,
            pdamage_indep=35 + passive_level // 3,
            boss_pdamage=40 + passive_level,
        )
        AlbatrossMaximum = core.InformedCharacterModifier(
            "알바트로스 맥시멈",
            att=30 + passive_level,
            pdamage=25 + 2 * (passive_level // 3),
            armor_ignore=15 + passive_level // 3,
            crit=15 + passive_level // 3,
        )
        SylphsAid = core.InformedCharacterModifier(
            "실프스 에이드", att=20, crit=10,
        )
        return [
            ElementalExpert,
            ElementalHarmony,
            WhisperOfWind,
            PhisicalTraining,
            Albatross,
            BowExpert,
            WindBlessingPassive,
            AlbatrossMaximum,
            SylphsAid,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=30)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=85+ceil(passive_level / 2))

        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        코강 순서:
        천노-윔-브링어

        하이퍼:
        트라이플링 윔-리인포스, 인핸스, 더블찬스
        천공의 노래-리인포스, 보스 킬러

        하울링게일 58회, 볼텍스 스피어 17회 타격

        트라이플링 윔 평균치로 계산

        """
        base_modifier = chtr.get_base_modifier()
        passive_level = base_modifier.passive_level + self.combat
        # Buff skills
        Storm = core.BuffSkill(
            "엘리멘트(스톰)", delay=0, remain=core.infinite_time(), pdamage=10
        ).wrap(core.BuffSkillWrapper)
        EmeraldFlower = core.BuffSkill(
            "에메랄드 플라워", delay=900, remain=60000 * (1 + base_modifier.summon_rem / 100), armor_ignore=10,
        ).wrap(core.BuffSkillWrapper)
        SharpEyes = core.BuffSkill(
            "샤프 아이즈",
            delay=0,
            remain=(300 + 10 * self.combat) * 1000,
            crit=20 + ceil(self.combat / 2),
            crit_damage=15 + ceil(self.combat / 2),
            rem=True,
        ).wrap(core.BuffSkillWrapper)
        GloryOfGuardians = core.BuffSkill(
            name="글로리 오브 가디언즈",
            delay=0,
            remain=60 * 1000,
            cooltime=120 * 1000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)

        StormBringerDummy = core.BuffSkill(
            "스톰 브링어(버프)",
            delay=0,  # 딜레이 계산 필요
            remain=200 * 1000,
        ).wrap(core.BuffSkillWrapper)

        # 하이퍼: 데미지 증가, 확률 10% 증가, 타수 증가
        whim_proc = (50 + 10 + passive_level // 2) * 0.01
        advanced_proc = (20 + passive_level // 3) * 0.01
        TriflingWhim = (
            core.DamageSkill(
                "트라이플링 윔",
                delay=0,
                damage=(290 + passive_level * 3) * (1 - advanced_proc)
                + (390 + passive_level * 3) * advanced_proc,
                hit=2 * whim_proc,
                modifier=core.CharacterModifier(pdamage=20),
            )
            .setV(vEhc, 1, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        StormBringer = (
            core.DamageSkill("스톰 브링어", delay=0, damage=500, hit=0.3)
            .setV(vEhc, 2, 2, True)
            .wrap(core.DamageSkillWrapper)
        )

        # 핀포인트 피어스
        PinPointPierce = core.DamageSkill(
            "핀포인트 피어스",
            delay=690,
            damage=340,
            hit=2,
            cooltime=60 * 1000,
        ).wrap(core.DamageSkillWrapper)
        PinPointPierceDebuff = core.BuffSkill(
            "핀포인트 피어스(버프)",
            delay=0,
            remain=60 * 1000,
            cooltime=-1,
            pdamage=15,
            armor_ignore=15,
        ).wrap(core.BuffSkillWrapper)

        # Damage Skills
        # 하이퍼: 데미지 증가, 보스 데미지 증가
        target_pdamage = ((120 + self.combat // 2) / 100) ** 3 * 100 - 100
        SongOfHeaven = (
            core.DamageSkill(
                "천공의 노래",
                delay=120,
                damage=345 + self.combat * 3,
                hit=1,
                modifier=core.CharacterModifier(
                    pdamage=target_pdamage + 20, boss_pdamage=30
                ),
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        CygnusPhalanx = cygnus.PhalanxChargeWrapper(vEhc, 0, 0)

        IdleWhim = (
            core.DamageSkill(
                "아이들 윔",
                delay=600,
                damage=(500 + 22 * vEhc.getV(4, 4)) * 0.865,  # (1 + 0.85 * 9) / 10 = 0.865
                hit=10 * 3,
                cooltime=10 * 1000,
                red=True,
            )
            .isV(vEhc, 4, 4)
            .wrap(core.DamageSkillWrapper)
        )
        MercilesswindDOT = core.DotSkill(
            "아이들 윔(도트)",
            summondelay=0,
            delay=1000,
            damage=500 + 20 * vEhc.getV(4, 4),
            hit=1,
            remain=9000,
            cooltime=-1,
        ).wrap(core.DotSkillWrapper)

        # Summon Skills
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 5, 5)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        HowlingGail = core.StackableSummonSkillWrapper(
            core.SummonSkill(
                "하울링 게일",
                summondelay=630,
                delay=150,
                damage=325 + 13 * vEhc.getV(1, 1),
                hit=3,
                remain=150 * 61 - 1,  # 61타
                cooltime=20 * 1000,
            ).isV(vEhc, 1, 1),
            max_stack=2,
        )
        WindWall = (
            core.SummonSkill(
                "윈드 월",
                summondelay=720,
                delay=2000,
                damage=550 + vEhc.getV(2, 2) * 22,
                hit=5 * 3,
                remain=45 * 1000,
                cooltime=90 * 1000,
                red=True,
                modifier=core.CharacterModifier(pdamage_indep=-50),
            )
            .isV(vEhc, 2, 2)
            .wrap(core.SummonSkillWrapper)
        )
        VortexSphere = (
            core.SummonSkill(
                "볼텍스 스피어",
                summondelay=720,
                delay=180,
                damage=400 + 16 * vEhc.getV(0, 0),
                hit=6,
                remain=180 * 20 - 1,
                cooltime=30000,
                red=True,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.SummonSkillWrapper)
        )  # 17타

        ######   Skill Wrapper   #####

        CriticalReinforce = bowmen.CriticalReinforceWrapper(
            vEhc, chtr, 3, 3, 10 + 25 + passive_level // 2 + 20 + ceil(self.combat / 2)
        )  # 실프스 에이드 + 알바트로스 맥시멈 + 샤프 아이즈

        # Damage
        SongOfHeaven.onAfters([TriflingWhim, StormBringer])
        PinPointPierce.onAfters([PinPointPierceDebuff, TriflingWhim, StormBringer])
        MirrorBreak.onAfters([TriflingWhim, StormBringer])
        # Summon
        CygnusPhalanx.onTicks([TriflingWhim, StormBringer])
        HowlingGail.onTicks([TriflingWhim, StormBringer])
        VortexSphere.onTicks([TriflingWhim, StormBringer])

        IdleWhim.onAfter(MercilesswindDOT)

        return (
            SongOfHeaven,
            [
                globalSkill.maple_heros(
                    chtr.level, name="시그너스 나이츠", combat_level=self.combat
                ),
                globalSkill.useful_combat_orders(),
                Storm,
                SharpEyes,
                EmeraldFlower,
                StormBringerDummy,
                cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level),
                GloryOfGuardians,
                CriticalReinforce,
                globalSkill.soul_contract(),
            ]
            + [
                GuidedArrow,
                CygnusPhalanx,
                HowlingGail,
                VortexSphere,
                WindWall,
            ]
            + [
                MirrorBreak,
                IdleWhim,
                PinPointPierce,
            ]
            + [
                PinPointPierceDebuff,
                MirrorSpider,
                MercilesswindDOT,
            ]  # Not used from scheduler
            + [SongOfHeaven],
        )
