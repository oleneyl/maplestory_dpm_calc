from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ConditionRule, RuleSet, ConcurrentRunRule
from . import globalSkill
from .jobbranch import pirates
from .jobclass import adventurer
from . import jobutils
from math import ceil
from typing import Any, Dict


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "DEX"
        self.jobname = "캡틴"
        self.vEnhanceNum = 14
        self.ability_list = Ability_tool.get_ability_set(
            "boss_pdamage", "buff_rem", "crit"
        )
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=28, armor_ignore=22)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule('노틸러스', '노틸러스 어썰트', lambda sk: sk.is_cooltime_left(8000, 1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule('소울 컨트랙트', '노틸러스 어썰트', lambda sk: sk.is_usable() or sk.is_cooltime_left(70000, 1)), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('노틸러스 어썰트', '소울 컨트랙트'), RuleSet.BASE)

        return ruleset

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        CriticalRoar = core.InformedCharacterModifier("크리티컬 로어", crit=20, crit_damage=5)
        PhisicalTraining = core.InformedCharacterModifier(
            "피지컬 트레이닝", stat_main=30, stat_sub=30
        )
        HalopointBullet = core.InformedCharacterModifier("할로포인트 불릿", att=60)
        FullMetaJacket = core.InformedCharacterModifier(
            "풀 메탈 재킷", pdamage_indep=20, crit=30, armor_ignore=20
        )
        ContinualAimingPassive = core.InformedCharacterModifier(
            "컨티뉴얼 에이밍(패시브)", crit_damage=20 + self.combat
        )
        CaptainDignityPassive = core.InformedCharacterModifier(
            "캡틴 디그니티(패시브)", att=30 + passive_level
        )
        CrueCommandership = core.InformedCharacterModifier(
            "크루 커맨더쉽", crit_damage=25 + passive_level
        )

        UnwierdingNectar = core.InformedCharacterModifier("언위어링 넥타", crit=10)

        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 1, 2)

        return [
            CriticalRoar,
            PhisicalTraining,
            HalopointBullet,
            ContinualAimingPassive,
            FullMetaJacket,
            CaptainDignityPassive,
            CrueCommandership,
            UnwierdingNectar,
            LoadedDicePassive,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=50)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=85+ceil(passive_level / 2))

        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        ----정보---
        크루 커멘더쉽 : 최종뎀 15%
        무라트 : 500 크뎀5
        발레리 : 560 크리15
        잭 : 320
        스토너 : 480
        두명 소환

        하이퍼
        래피드파이어 - 보스킬러, 리인포스, 애드레인지
        헤드샷 - 보너스 어택, 리인포스

        데드아이 조준률 3배

        퀵 드로우 : 사용 가능하면 헤드샷, 스트레인지 봄, 데드아이 전에 사용

        서먼 크루 분당 17타, 평균 퍼뎀 465
        봄버 평균 데미지 600ms당 297%x3

        카운터 어택 미발동

        5차 강화
        래피드 / 퍼실 / 디그니티
        헤드샷 / 배틀쉽 / 옥타
        서먼크루 / 스트봄 / 노틸러스
        """
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        DEADEYEACC = 3
        DEADEYEAIM = 3480
        BULLET_PARTY_TICK = 150
        CONTINUAL_AIMING = core.CharacterModifier(pdamage_indep=25 + 2 * self.combat)
        BULLET_ATT = core.CharacterModifier(att=22)  # 자이언트 불릿

        ######   Skill   ######
        # Buff skills
        PirateStyle = core.BuffSkill(
            "파이렛 스타일",
            delay=0,
            remain=(180 + 6 * self.combat) * 1000,
            rem=True,
            patt=20 + self.combat,
        ).wrap(core.BuffSkillWrapper)
        LuckyDice = (
            core.BuffSkill(
                "로디드 다이스",
                delay=990,
                remain=180 * 1000,
                pdamage=20
                + 10 / 6
                + 10 / 6 * (5 / 6 + 1 / 11) * (10 * (5 + passive_level) * 0.01),
            )
            .isV(vEhc, 1, 2)
            .wrap(core.BuffSkillWrapper)
        )
        QuickDraw = core.BuffSkill(
            "퀵 드로우",
            delay=0,  # 래피드/불파 도중 사용가능
            remain=core.infinite_time(),
            cooltime=-1,
        ).wrap(core.BuffSkillWrapper)
        QuickDrawStack = core.StackSkillWrapper(
            core.BuffSkill("퀵 드로우(준비)", 0, core.infinite_time()), 1
        )

        # Summon Skills
        OctaQuaterdeck = (
            core.SummonSkill(
                "옥타 쿼터덱",
                summondelay=630,
                delay=60000 / 110,
                damage=300,
                hit=1,
                remain=30000,
                rem=True,
                cooltime=10000,
            )
            .setV(vEhc, 5, 2, True)
            .wrap(core.SummonSkillWrapper)
        )
        SummonCrew = (
            core.SummonSkill(
                "서먼 크루",
                summondelay=900,
                delay=60000 / 17,  # 분당 17타
                damage=465,  # 평균 퍼뎀 465
                hit=2,
                remain=120000,
                modifier=core.CharacterModifier(pdamage_indep=15 + passive_level),
                rem=True,
            )
            .setV(vEhc, 6, 2, True)
            .wrap(core.SummonSkillWrapper)
        )
        SummonCrewBuff = core.BuffSkill(
            "서먼 크루(버프)",
            delay=0,
            remain=120000,
            cooltime=-1,
            crit=10 + passive_level // 3,
            crit_damage=5,
            att=45 + 3 * passive_level,
        ).wrap(core.BuffSkillWrapper)

        """
        돈틀레스 : 330 보통 13/22 타수3 600
        블랙바크 : 445 느림 15/18 타수3 810
        슈린츠 : 200 빠름   15/27 타수3 570
        조나단 : 320 보통   12/20 타수3 600
        평균 데미지 600ms당 297
        """
        BB_AVERAGE = (
            (330 + 3 * self.combat)
            + (445 + 3 * self.combat) * (600 / 810)
            + (200 + 3 * self.combat) * (600 / 570)
            + (320 + 3 * self.combat)
        ) / 4
        # TODO: 배틀쉽 봄버 공격주기 확인 필요
        BattleshipBomber = core.BuffSkill(
            "배틀쉽 봄버", delay=0, remain=0, cooltime=30000, red=True
        ).wrap(core.BuffSkillWrapper)
        BattleshipBomber_1 = (
            core.SummonSkill(
                "배틀쉽 봄버(소환,1)",
                summondelay=390,
                delay=600,
                damage=BB_AVERAGE,
                hit=3,
                remain=60000,
                rem=True,
                cooltime=-1,
            )
            .setV(vEhc, 4, 2, True)
            .wrap(core.SummonSkillWrapper)
        )
        BattleshipBomber_2 = (
            core.SummonSkill(
                "배틀쉽 봄버(소환,2)",
                summondelay=390,
                delay=600,
                damage=BB_AVERAGE,
                hit=3,
                remain=60000,
                rem=True,
                cooltime=-1,
            )
            .setV(vEhc, 4, 2, True)
            .wrap(core.SummonSkillWrapper)
        )

        # Damage Skills
        RapidFire = (
            core.DamageSkill(
                "래피드 파이어",
                delay=120,
                damage=325 + 3 * self.combat,
                hit=1,
                modifier=core.CharacterModifier(pdamage=30, boss_pdamage=20)
                + CONTINUAL_AIMING
                + BULLET_ATT,
            )
            .setV(vEhc, 0, 2, True)
            .wrap(core.DamageSkillWrapper)
        )
        Headshot = (
            core.DamageSkill(
                "헤드 샷",
                delay=450,
                damage=525 + 5 * self.combat,
                hit=12 + 1,
                cooltime=5000,
                red=True,
                modifier=core.CharacterModifier(crit=100, armor_ignore=60, pdamage=20)
                + CONTINUAL_AIMING
                + BULLET_ATT,
            )
            .setV(vEhc, 3, 2, True)
            .wrap(core.DamageSkillWrapper)
        )

        Nautilus = (
            core.DamageSkill(
                "노틸러스",
                delay=690,
                damage=440 + 130 + (4 + 3) * self.combat,
                hit=7,
                red=True,
                cooltime=30000,
                modifier=CONTINUAL_AIMING + BULLET_ATT,
            )
            .setV(vEhc, 8, 2, True)
            .wrap(core.DamageSkillWrapper)
        )
        CaptainDignity = (
            core.DamageSkill(
                "캡틴 디그니티",
                delay=0,
                damage=275 + 3 * passive_level,
                hit=1,
                modifier=CONTINUAL_AIMING + BULLET_ATT,
            )
            .setV(vEhc, 1, 2, True)
            .wrap(core.DamageSkillWrapper)
        )

        # Hyper
        StrangeBomb = (
            core.DamageSkill(
                "스트레인지 봄",
                delay=690,
                damage=400,
                hit=12,
                cooltime=30000,
                modifier=CONTINUAL_AIMING + BULLET_ATT,
            )
            .setV(vEhc, 7, 2, True)
            .wrap(core.DamageSkillWrapper)
        )
        EpicAdventure = core.BuffSkill(
            "에픽 어드벤처",
            delay=0,
            remain=60 * 1000,
            cooltime=150 * 1000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)

        # 5th
        PirateFlag = adventurer.PirateFlagWrapper(vEhc, 2, 1, chtr.level)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 4, 4, WEAPON_ATT)

        BulletParty = core.DamageSkill("불릿 파티", 0, 0, 0, cooltime=75000, red=True).wrap(
            core.DamageSkillWrapper
        )
        BulletPartyTick = (
            core.DamageSkill(
                "불릿 파티(틱)",
                delay=BULLET_PARTY_TICK,  # 12초간 지속 -> 50회 시전
                damage=230 + 9 * vEhc.getV(5, 5),
                hit=5,
                modifier=CONTINUAL_AIMING + BULLET_ATT,
            )
            .isV(vEhc, 5, 5)
            .wrap(core.DamageSkillWrapper)
        )
        DeadEye = (
            core.DamageSkill(
                "데드아이",
                delay=450,
                damage=(320 + 13 * vEhc.getV(3, 3)) * DEADEYEACC,
                hit=15,
                cooltime=30000 + DEADEYEAIM,  # TODO: 조준시간은 쿨감 안받아야함
                red=True,
                modifier=core.CharacterModifier(crit=100, pdamage_indep=4 * 11)
                + CONTINUAL_AIMING
                + BULLET_ATT,
            )
            .isV(vEhc, 3, 3)
            .wrap(core.DamageSkillWrapper)
        )
        NautilusAssult = (
            core.SummonSkill(
                "노틸러스 어썰트",
                summondelay=690,
                delay=360,
                damage=600 + 24 * vEhc.getV(0, 0),
                hit=6,
                remain=360 * 7 - 1,
                cooltime=180000,
                red=True,
                modifier=CONTINUAL_AIMING + BULLET_ATT,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.SummonSkillWrapper)
        )  # 7회 2초간
        NautilusAssult_2 = (
            core.SummonSkill(
                "노틸러스 어썰트(일제 사격)",
                summondelay=0,
                delay=160,
                damage=300 + 12 * vEhc.getV(0, 0),
                hit=12,
                remain=160 * 36 - 1,
                cooltime=-1,
                modifier=CONTINUAL_AIMING + BULLET_ATT,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.SummonSkillWrapper)
        )  # 36회 6초간
        DeathTriggerInit = (
            core.DamageSkill("데스 트리거(개시)", 360, 0, 0, cooltime=45000, red=True)
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )
        DeathTrigger = (
            core.DamageSkill(
                "데스 트리거",
                delay=180,
                damage=325 + 13 * vEhc.getV(0, 0),
                hit=7 * 4,
                cooltime=-1,
                modifier=CONTINUAL_AIMING + BULLET_ATT,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )
        DeathTriggerEnd = (
            core.DamageSkill("데스 트리거(후딜)", 300, 0, 0, cooltime=-1)
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )

        ######   Skill Wrapper   ######

        # 크루 사용 후 버프 제공
        SummonCrew.onAfter(SummonCrewBuff)

        # 배틀쉽은 둘 중 꺼져있는걸로 시전
        BattleshipBomber.onAfter(
            core.OptionalElement(
                BattleshipBomber_1.is_active,
                BattleshipBomber_2,
                BattleshipBomber_1,
                name="배틀쉽 1,2",
            )
        )

        # 노틸러스 이후 배틀쉽 쿨감
        Nautilus.onAfter(BattleshipBomber.controller(0.5, "reduce_cooltime_p"))

        # 디그니티는 노틸러스 쿨타임에 강화됨
        CaptainDignity.add_runtime_modifier(
            Nautilus,
            lambda sk: core.CharacterModifier(
                pdamage_indep=30 * (not sk.is_available())
            ),
        )
        for sk in [RapidFire, Headshot, BulletPartyTick, DeadEye, DeathTrigger]:
            sk.onAfter(CaptainDignity)

        # 퀵 드로우
        QuickDrawProc = core.OptionalElement(
            QuickDraw.is_not_active,
            QuickDrawStack.stackController((8 + ceil(self.combat/2)) * 0.01, name="퀵 드로우 확률"),
        )
        QuickDraw.onJustAfter(QuickDrawStack.stackController(-1))
        QuickDrawProc.onJustAfter(
            core.OptionalElement(
                lambda: QuickDrawStack.judge(1, 1) and QuickDraw.is_not_active(),
                QuickDraw,
            )
        )
        for sk in [
            RapidFire,
            Headshot,
            Nautilus,
            StrangeBomb,
            BulletPartyTick,
            DeadEye,
            DeathTrigger,
        ]:
            sk.onJustAfter(QuickDrawProc)
        for sk in [NautilusAssult, NautilusAssult_2]:
            sk.onTick(QuickDrawProc)

        QuickDrawShutdownTrigger = QuickDraw.controller(-1)
        for sk in [Headshot, StrangeBomb, DeadEye, DeathTrigger, Nautilus, MirrorBreak]:
            sk.onJustAfter(QuickDrawShutdownTrigger)
            sk.add_runtime_modifier(QuickDraw, lambda sk: core.CharacterModifier(pdamage_indep=(25 + self.combat) * sk.is_active()))
        for sk in [NautilusAssult, NautilusAssult_2]:
            sk.onTick(QuickDrawShutdownTrigger)
            sk.add_runtime_modifier(QuickDraw, lambda sk: core.CharacterModifier(pdamage_indep=(25 + self.combat) * sk.is_active()))

        # 노틸러스 어썰트
        NautilusAssult.onEventEnd(NautilusAssult_2)
        NautilusAssult.onJustAfter(
            core.OptionalElement(
                partial(Nautilus.is_cooltime_left, 8000, -1),
                Nautilus.controller(8000),
                name="노틸러스 쿨타임 8초",
            )
        )
        Nautilus.onJustAfter(
            core.OptionalElement(
                partial(NautilusAssult.is_cooltime_left, 8000, -1),
                NautilusAssult.controller(8000),
                name="노틸러스 어썰트 쿨타임 8초",
            )
        )

        # 불릿파티
        BulletParty.onAfter(
            core.RepeatElement(BulletPartyTick, 11820 // BULLET_PARTY_TICK)
        )

        # 데스 트리거
        DeathTriggerInit.onAfter(core.RepeatElement(DeathTrigger, 7))
        DeathTriggerInit.onAfter(DeathTriggerEnd)

        return (
            RapidFire,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                SummonCrewBuff,
                PirateStyle,
                LuckyDice,
                EpicAdventure,
                PirateFlag,
                Overdrive,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                QuickDraw,
                globalSkill.soul_contract(),
            ]
            + [
                BattleshipBomber,
                DeathTriggerInit,
                Headshot,
                Nautilus,
                DeadEye,
                StrangeBomb,
                MirrorBreak,
                MirrorSpider,
            ]
            + [
                OctaQuaterdeck,
                BattleshipBomber_1,
                BattleshipBomber_2,
                NautilusAssult,
                NautilusAssult_2,
                SummonCrew,
            ]
            + [BulletParty]
            + [RapidFire],
        )
