from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import (
    ConditionRule,
    DisableRule,
    MutualRule,
    RuleSet,
    ConcurrentRunRule,
)
from . import globalSkill
from .jobbranch import pirates
from .jobclass import adventurer
from . import jobutils
from math import ceil
from typing import Any, Dict


class CaptainSummonSkillWrapper(core.SummonSkillWrapper):
    def __init__(self, skill, nectar_delay, nectar_damage):
        super(CaptainSummonSkillWrapper, self).__init__(skill)
        self.nectar_skill = None
        self.nectar_delay = nectar_delay
        self.nectar_damage = nectar_damage

    def get_delay(self) -> float:
        if self.nectar_skill.is_active():
            return self.nectar_delay
        else:
            return super(CaptainSummonSkillWrapper, self).get_delay()

    def get_damage(self) -> float:
        if self.nectar_skill.is_active():
            return self.nectar_damage
        else:
            return super(CaptainSummonSkillWrapper, self).get_damage()

    def register_nectar(self, skill: core.BuffSkillWrapper):
        self.nectar_skill = skill


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
        ruleset.add_rule(
            ConditionRule("스트레인지 봄", "헤드 샷", lambda sk: sk.is_cooltime_left(4200, 1)),
            RuleSet.BASE,
        )
        ruleset.add_rule(DisableRule("불릿 파티"), RuleSet.BASE)

        return ruleset

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        CriticalRoar = core.InformedCharacterModifier("크리티컬 로어", crit=20, crit_damage=5)
        GunAccelation = core.InformedCharacterModifier("건 액셀레이션", stat_main=20)
        GunMastery = core.InformedCharacterModifier("건 마스터리", crit=10)
        PhisicalTraining = core.InformedCharacterModifier(
            "피지컬 트레이닝", stat_main=30, stat_sub=30
        )
        InfiniteBullet = core.InformedCharacterModifier("인피닛 불릿", att=10)
        HalopointBullet = core.InformedCharacterModifier("할로포인트 불릿", att=60)
        FullMetalJacket = core.InformedCharacterModifier(
            "풀 메탈 재킷", pdamage_indep=20, crit=30, armor_ignore=20
        )
        ContinualAimingPassive = core.InformedCharacterModifier(
            "컨티뉴얼 에이밍(패시브)", crit_damage=20 + self.combat
        )
        CaptainDignityPassive = core.InformedCharacterModifier(
            "캡틴 디그니티(패시브)", att=30 + passive_level, pdamage_indep=8
        )
        CrewCommandership = core.InformedCharacterModifier(
            "크루 커맨더쉽", crit_damage=25 + passive_level
        )

        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 1, 2)

        return [
            CriticalRoar,
            GunAccelation,
            GunMastery,
            PhisicalTraining,
            InfiniteBullet,
            HalopointBullet,
            ContinualAimingPassive,
            FullMetalJacket,
            CaptainDignityPassive,
            CrewCommandership,
            LoadedDicePassive,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=50)
        Mastery = core.InformedCharacterModifier(
            "숙련도", mastery=85 + ceil(passive_level / 2)
        )
        ContinualAiming = core.InformedCharacterModifier(
            "컨티뉴얼 에이밍", pdamage_indep=25 + 2 * self.combat
        )
        OffenseForm = core.InformedCharacterModifier("오펜스 폼", pdamage=15)  # 상시유지 가정

        return [WeaponConstant, Mastery, ContinualAiming, OffenseForm]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        하이퍼
        래피드파이어 - 리인포스, 애드레인지
        헤드샷 - 보너스 어택, 리인포스, 보스킬러

        데드아이 조준률 3배
        """
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        DEADEYEACC = 3
        DEADEYEAIM = 3480
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
        QuickDrawStack = core.StackSkillWrapper(
            core.BuffSkill("퀵 드로우(스택)", 0, core.infinite_time()), 99999999
        )

        # Summon Skills
        SiegeBomber = CaptainSummonSkillWrapper(
            core.SummonSkill(
                "시즈 봄버",
                summondelay=630,
                delay=540,
                damage=300,
                hit=1,
                remain=60000,
                rem=True,
                cooltime=10000,
            ).setV(vEhc, 5, 3, True),
            nectar_delay=540,
            nectar_damage=450,
        )
        SummonCrewPistol = CaptainSummonSkillWrapper(
            core.SummonSkill(
                "서먼 크루(쌍권총)",
                summondelay=900,
                delay=3030,
                damage=150 + 200,
                hit=3 * 2,
                remain=120000,
                cooltime=45000,
                modifier=core.CharacterModifier(pdamage_indep=15 + passive_level),
                rem=True,
            ).setV(vEhc, 6, 2, True),
            nectar_delay=1200,
            nectar_damage=285 + 200,
        )
        SummonCrewMarksman = CaptainSummonSkillWrapper(
            core.SummonSkill(
                "서먼 크루(명사수)",
                summondelay=0,
                delay=3030,
                damage=170,
                hit=4,
                remain=120000,
                cooltime=-1,
                modifier=core.CharacterModifier(pdamage_indep=15 + passive_level),
                rem=True,
            ).setV(vEhc, 6, 2, True),
            nectar_delay=1440,
            nectar_damage=220,
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

        BattleshipBomber = CaptainSummonSkillWrapper(
            core.SummonSkill(
                "배틀쉽 봄버",
                summondelay=390 * 2,  # 2대 연속 소환
                delay=1110,
                damage=400 + 3 * self.combat,
                hit=3 * 2,  # 2대 소환
                remain=60000,
                rem=True,
            ).setV(vEhc, 4, 2, True),
            nectar_delay=1080,
            nectar_damage=500,
        )

        # Damage Skills
        RapidFire = (
            core.DamageSkill(
                "래피드 파이어",
                delay=120,
                damage=375 + 3 * self.combat,
                hit=1,
                modifier=core.CharacterModifier(pdamage=30) + BULLET_ATT,
            )
            .setV(vEhc, 0, 2, True)
            .wrap(core.DamageSkillWrapper)
        )
        Headshot = (
            core.DamageSkill(
                "헤드 샷",
                delay=450,
                damage=1185 + 13 * self.combat,
                hit=13 + 1,
                cooltime=5000,
                red=True,
                modifier=core.CharacterModifier(
                    crit=100, armor_ignore=60, pdamage=20, boss_pdamage=20
                )
                + BULLET_ATT,
            )
            .setV(vEhc, 3, 2, True)
            .wrap(core.DamageSkillWrapper)
        )

        CaptainDignity = (
            core.DamageSkill(
                "캡틴 디그니티",
                delay=0,
                damage=275 + 3 * passive_level,
                hit=1,
                modifier=core.CharacterModifier(pdamage_indep=30) + BULLET_ATT,
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
                modifier=BULLET_ATT,
            )
            .setV(vEhc, 7, 2, True)
            .wrap(core.DamageSkillWrapper)
        )
        UnwearyingNectar = core.BuffSkill(
            "언위어링 넥타",
            delay=390,
            remain=30 * 1000,
            cooltime=120 * 1000,
        ).wrap(core.BuffSkillWrapper)
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

        BulletParty = core.DamageSkill(
            "불릿 파티", 180, 0, 0, cooltime=75000, red=True
        ).wrap(core.DamageSkillWrapper)
        BulletPartyTick = (
            core.DamageSkill(
                "불릿 파티(틱)",
                delay=150,
                damage=230 + 9 * vEhc.getV(5, 5),
                hit=5,
                modifier=BULLET_ATT,
            )
            .isV(vEhc, 5, 5)
            .wrap(core.DamageSkillWrapper)
        )
        BulletPartyEnd = core.DamageSkill("불릿 파티(종료)", 180, 0, 0).wrap(
            core.DamageSkillWrapper
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
                modifier=BULLET_ATT,
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
                modifier=BULLET_ATT,
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
                modifier=BULLET_ATT,
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
        SummonCrewPistol.onJustAfter(SummonCrewMarksman)
        SummonCrewPistol.onAfter(SummonCrewBuff)

        for sk in [RapidFire, Headshot, BulletPartyTick, DeadEye, DeathTrigger]:
            sk.onAfter(CaptainDignity)

        # 퀵 드로우
        QuickDrawProc = QuickDrawStack.stackController(1)
        for sk in [
            RapidFire,
            Headshot,
            StrangeBomb,
            BulletPartyTick,
            DeadEye,
            DeathTrigger,
            CaptainDignity,
        ]:
            sk.onAfter(QuickDrawProc)
        for sk in [NautilusAssult, NautilusAssult_2]:
            sk.onTick(QuickDrawProc)

        QuickDrawShutdownTrigger = QuickDrawStack.stackController(-99999999)
        QUICK_DRAW_PROB = 8 + ceil(passive_level / 2)

        def get_quick_draw_multiplier(stack):
            return 1 - pow((100 - QUICK_DRAW_PROB) / 100, stack)

        for sk in [Headshot, StrangeBomb, DeadEye]:
            sk.onJustAfter(QuickDrawShutdownTrigger)
            sk.add_runtime_modifier(
                QuickDrawStack,
                lambda sk: core.CharacterModifier(
                    pdamage_indep=(25 + passive_level)
                    * get_quick_draw_multiplier(sk.stack)
                ),
            )

        # 언위어링 넥타
        for sk in [SiegeBomber, SummonCrewPistol, SummonCrewMarksman, BattleshipBomber]:
            sk.register_nectar(UnwearyingNectar)

        # 노틸러스 어썰트
        NautilusAssult.onEventEnd(NautilusAssult_2)

        # 불릿파티
        BulletParty.onAfter(core.RepeatElement(BulletPartyTick, 11820 // 150))
        BulletParty.onAfter(BulletPartyEnd)

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
                UnwearyingNectar,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                globalSkill.soul_contract(),
            ]
            + [
                Headshot,
                DeathTriggerInit,
                DeadEye,
                StrangeBomb,
                MirrorBreak,
                MirrorSpider,
            ]
            + [
                SiegeBomber,
                SummonCrewPistol,
                SummonCrewMarksman,
                BattleshipBomber,
                NautilusAssult,
                NautilusAssult_2,
            ]
            + [BulletParty]
            + [RapidFire],
        )
