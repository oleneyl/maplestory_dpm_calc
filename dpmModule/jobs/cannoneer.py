from enum import Enum

from .globalSkill import GlobalSkills
from .jobbranch.pirates import PirateSkills
from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConditionRule
from . import globalSkill
from .jobbranch import pirates
from .jobclass import adventurer
from . import jobutils
from math import ceil
from typing import Any, Dict


# English skill information for Cannoneer here https://maplestory.fandom.com/wiki/Cannoneer/Skills
class CannoneerSkills(Enum):
    # Link SKill
    PirateBlessing = 'Pirate Blessing | 파이렛 블레스'
    # 1st Job
    CannonBlaster = 'Cannon Blaster | 캐논 스플래셔'
    CannonStrike = 'Cannon Strike | 펀칭 캐논'
    BlastBack = 'Blast Back | 기간틱 백스탭'
    MonkeyPush = 'Monkey Push | 몽키푸시'
    CannonBoost = 'Cannon Boost | 빌드업 캐논'
    # 2nd Job
    ScatterShot = 'Scatter Shot | 슬러그 샷'
    BarrelBomb = 'Barrel Bomb | 몽키 러쉬붐'
    CannonBooster = 'Cannon Booster | 캐논 부스터'
    MonkeyMagic = 'Monkey Magic | 몽키 매직'
    CriticalFire = 'Critical Fire | 크리티컬 파이어'
    CannonMastery = 'Cannon Mastery | 캐논 마스터리'
    PirateTraining = 'Pirate Training | 파이렛 트레이닝'
    # 3rd job
    CannonSpike = 'Cannon Spike | 캐논 스파이크'
    MonkeyFury = 'Monkey Fury | 몽키 퓨리어스'
    MonkeyWave = 'Monkey Wave | 몽키 웨이브'
    CannonJump = 'Cannon Jump | 캐논 점프'
    BarrelRoulette = 'Barrel Roulette | 오크통 룰렛'
    RolloftheDice = 'Roll of the Dice | 럭키 다이스'
    ReinforcedCannon = 'Reinforced Cannon | 리인포스 캐논'
    PirateRush = 'Pirate Rush | 바이탈 익스트림'
    CounterCrush = 'Counter Crush | 반격의 슈터'
    # 4th Job
    CannonBazooka = 'Cannon Bazooka | 캐논 바주카'
    CannonBarrage = 'Cannon Barrage | 캐논 버스터'
    AnchorsAweigh = 'Anchors Aweigh | 마그네틱 앵커'
    MonkeyMilitia = 'Monkey Militia | 서포트 몽키 트윈스'
    NautilusStrike = 'Nautilus Strike | 전함 노틸러스'
    PiratesSpirit = 'Pirate\'s Spirit | 파이렛 스피릿'
    CannonOverload = 'Cannon Overload | 오버버닝 캐논'
    MegaMonkeyMagic = 'Mega Monkey Magic | 하이퍼 몽키 스펠'
    DoubleDown = 'Double Down | 더블 럭키 다이스'
    # Hypers
    RollingRainbow = 'Rolling Rainbow | 롤링 캐논 레인보우'
    EpicAdventure = 'Epic Adventure | 에픽 어드벤처'
    Buckshot = 'Buckshot | 벅 샷'
    # 5th Job
    CannonofMassDestruction = 'Cannon of Mass Destruction | 빅 휴즈 기간틱 캐논볼'
    TheNuclearOption = 'The Nuclear Option | ICBM'
    MonkeyBusiness = 'Monkey Business | 스페셜 몽키 에스코트'
    Poolmaker = 'Poolmaker | 풀 메이커'


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "STR"
        self.jobname = "캐논슈터"
        self.vEnhanceNum = 16
        self.ability_list = Ability_tool.get_ability_set(
            "boss_pdamage", "crit", "reuse"
        )
        self.preEmptiveSkills = 2

    def get_ruleset(self):
        def cannonball_rule(soul_contract):
            if soul_contract.is_active():
                return True
            if soul_contract.is_cooltime_left(50000, -1):
                return False
            return True

        ruleset = RuleSet()
        ruleset.add_rule(
            ConditionRule(CannoneerSkills.CannonofMassDestruction.value, GlobalSkills.TermsAndConditions.value, cannonball_rule),
            RuleSet.BASE,
        )
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=66, crit_damage=6, armor_ignore=30)

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        BuildupCannon = core.InformedCharacterModifier(CannoneerSkills.CannonBoost.value, att=20)
        CriticalFire = core.InformedCharacterModifier(CannoneerSkills.CriticalFire.value, crit=20, crit_damage=5)
        PirateTraining = core.InformedCharacterModifier(CannoneerSkills.PirateTraining.value, stat_main=30, stat_sub=30)

        MonkeyWavePassive = core.InformedCharacterModifier(f"{CannoneerSkills.MonkeyWave.value}(Passive | 패시브)", crit=20)
        OakRuletPassive = core.InformedCharacterModifier(f"{CannoneerSkills.BarrelRoulette.value}(Passive | 패시브)", pdamage_indep=10)
        ReinforceCannon = core.InformedCharacterModifier(CannoneerSkills.ReinforcedCannon.value, att=40)
        PirateSpirit = core.InformedCharacterModifier(CannoneerSkills.PiratesSpirit.value, boss_pdamage=40 + self.combat)
        OverburningCannon = core.InformedCharacterModifier(CannoneerSkills.CannonOverload.value,pdamage_indep=30 + passive_level,armor_ignore=20 + passive_level // 2,)

        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 3, 4)

        return [
            BuildupCannon,
            CriticalFire,
            PirateTraining,
            MonkeyWavePassive,
            OakRuletPassive,
            ReinforceCannon,
            PirateSpirit,
            OverburningCannon,
            LoadedDicePassive,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=50)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep=-7.5 + 0.5 * ceil(passive_level / 2))
        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        Hyper: Monkey Twins-Split, Enhance, Cannon Buster-Reinforce, Bonus Attack.
        Rolling Cannon Rainbow 26

        Coco ball 6 seconds
        Lee's Bomb 5

        Nose sequence:
        Buster-Support-Many-roll-car

        하이퍼 : 몽키트윈스-스플릿, 인핸스, 캐논버스터 - 리인포스, 보너스 어택.
        롤링캐논레인보우 26타

        코코볼 6초
        이씨밤 5타

        코강 순서:
        버스터-서포트-다수기-롤캐
        """
        COCOBALLHIT = options.get("cocoball_hit", 27)
        ICBMHIT = 6
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        # Buff skills
        Booster = core.BuffSkill(CannoneerSkills.CannonBooster.value, 0, 200 * 1000).wrap(core.BuffSkillWrapper)
        Buckshot = core.BuffSkill(CannoneerSkills.Buckshot.value, 0, 180000).wrap(core.BuffSkillWrapper)

        LuckyDice = (
            core.BuffSkill(
                PirateSkills.LoadedDice.value,
                delay=0,
                remain=180 * 1000,
                pdamage=20  # 로디드 데미지 고정.
                + 10 / 6
                + 10 / 6 * (5 / 6 + 1 / 11) * (10 * (5 + passive_level) * 0.01),
            )
            .isV(vEhc, 3, 4)
            .wrap(core.BuffSkillWrapper)
        )

        MonkeyWave = core.DamageSkill(
            CannoneerSkills.MonkeyWave.value,
            delay=810,
            damage=860,
            hit=1,
            cooltime=30 * 1000,
        ).wrap(core.DamageSkillWrapper)
        MonkeyWaveBuff = core.BuffSkill(
            f"{CannoneerSkills.MonkeyWave.value}(Buff | 버프)",
            delay=0,
            remain=30000,
            cooltime=-1,
            crit_damage=5,
        ).wrap(core.BuffSkillWrapper)

        MonkeyFurious = core.DamageSkill(
            CannoneerSkills.MonkeyFury.value,
            delay=720,
            damage=180,
            hit=3,
            cooltime=30 * 1000,
        ).wrap(core.DamageSkillWrapper)
        MonkeyFuriousBuff = core.BuffSkill(
            f"{CannoneerSkills.MonkeyFury.value}(Buff | 버프)",
            delay=0,
            remain=30000,
            cooltime=-1,
            pdamage=40,
        ).wrap(core.BuffSkillWrapper)
        MonkeyFuriousDot = core.DotSkill(
            f"{CannoneerSkills.MonkeyFury.value}(DoT | 도트)",
            summondelay=0,
            delay=1000,
            damage=200,
            hit=1,
            remain=30000,
            cooltime=-1,
        ).wrap(core.DotSkillWrapper)

        OakRoulette = core.BuffSkill(
            CannoneerSkills.BarrelRoulette.value,
            delay=840,
            remain=180000,
            rem=True,
            cooltime=180000,
            crit_damage=1.25,
        ).wrap(core.BuffSkillWrapper)
        OakRuletDOT = core.DotSkill(
            f"{CannoneerSkills.BarrelRoulette.value}(DoT | 도트)",
            summondelay=0,
            delay=1000,
            damage=50,
            hit=1,
            remain=5000,
            cooltime=-1,
        ).wrap(core.DotSkillWrapper)

        MonkeyMagic = core.BuffSkill(
            CannoneerSkills.MegaMonkeyMagic.value,
            delay=0,
            remain=180000,
            rem=True,
            stat_main=60 + passive_level,
            stat_sub=60 + passive_level,
        ).wrap(core.BuffSkillWrapper)

        # Damage Skills
        CannonBuster = (
            core.DamageSkill(
                CannoneerSkills.CannonBarrage.value,
                delay=690,
                damage=(750 + 5 * self.combat) * 0.45,  # BuckShot
                hit=3 * (4 + 1),
                modifier=core.CharacterModifier(
                    crit=15 + ceil(self.combat / 2),
                    armor_ignore=20 + self.combat // 2,
                    pdamage=20,
                ),
            )
            .setV(vEhc, 0, 2, True)
            .wrap(core.DamageSkillWrapper)
        )

        # Summon Skills
        SupportMonkeyTwins = (
            core.SummonSkill(
                CannoneerSkills.MonkeyMilitia.value,
                summondelay=720,
                delay=930,
                damage=(295 + 8 * self.combat) * 0.6,  # Split Damage
                hit=(1 + 1) * (2 + 1),  # Split Damage, Enhance
                remain=60000 + 2000 * self.combat,
                rem=True,
            )
            .setV(vEhc, 1, 2, False)
            .wrap(core.SummonSkillWrapper)
        )

        # Hyper
        RollingCannonRainbow = (
            core.SummonSkill(
                CannoneerSkills.RollingRainbow.value,
                summondelay=480,
                delay=12000 / 26,
                damage=600,
                hit=3,
                remain=12000,
                cooltime=90000,
            )
            .setV(vEhc, 3, 2, True)
            .wrap(core.SummonSkillWrapper)
        )
        EpicAdventure = core.BuffSkill(
            CannoneerSkills.EpicAdventure.value,
            delay=0,
            remain=60000,
            cooltime=120000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)

        # V skills
        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)

        PirateFlag = adventurer.PirateFlagWrapper(vEhc, 4, 3, chtr.level)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # Used every cooldown. 쿨타임마다 사용.
        # Conflict 27 times against the scarecrow. 허수아비 대상 27회 충돌.
        BFGCannonball = core.StackableSummonSkillWrapper(
            core.SummonSkill(
                CannoneerSkills.CannonofMassDestruction.value,
                summondelay=600,
                delay=210,
                damage=(450 + 15 * vEhc.getV(0, 0)) * 0.45,  # BuckShot
                hit=4 * 3,
                remain=210 * COCOBALLHIT,
                cooltime=25000,
            ).isV(vEhc, 0, 0),
            max_stack=3,
        )

        ICBM = (
            core.DamageSkill(
                CannoneerSkills.TheNuclearOption.value,
                delay=1140,
                damage=(800 + 32 * vEhc.getV(1, 1)) * 0.45,  # BuckShot
                hit=5 * ICBMHIT * 3,
                cooltime=30000,
                red=True,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.DamageSkillWrapper)
        )
        ICBMDOT = (
            core.SummonSkill(
                f"{CannoneerSkills.TheNuclearOption.value}(DoT | 장판)",
                summondelay=0,
                delay=15000 / 27,  # 27 hits. 27타.
                damage=(500 + 20 * vEhc.getV(1, 1)) * 0.45,  # BuckShot
                hit=1 * 3,
                remain=15000,
                cooltime=-1,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.SummonSkillWrapper)
        )

        SpecialMonkeyEscort_Cannon = (
            core.SummonSkill(
                CannoneerSkills.MonkeyBusiness.value,
                summondelay=780,
                delay=1500,
                damage=300 + 12 * vEhc.getV(2, 2),
                hit=4 * 3,
                remain=(30 + vEhc.getV(2, 2) // 2) * 1000,
                cooltime=120000,
                red=True,
            )
            .isV(vEhc, 2, 2)
            .wrap(core.SummonSkillWrapper)
        )
        SpecialMonkeyEscort_Bomb = (
            core.SummonSkill(
                f"{CannoneerSkills.MonkeyBusiness.value}(Bomb | 폭탄)",
                summondelay=0,
                delay=5000,
                damage=450 + 18 * vEhc.getV(2, 2),
                hit=7 * 3,
                remain=(30 + vEhc.getV(2, 2) // 2) * 1000,
                cooltime=-1,
                modifier=core.CharacterModifier(armor_ignore=100),
            )
            .isV(vEhc, 2, 2)
            .wrap(core.SummonSkillWrapper)
        )

        FullMaker = (
            core.SummonSkill(
                CannoneerSkills.Poolmaker.value,
                summondelay=720,
                delay=360,
                damage=(700 + 28 * vEhc.getV(0, 0)) * 0.45,  # BuckShot
                hit=3 * 3,
                remain=360 * 20 - 1,
                cooltime=60000,
                red=True,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.SummonSkillWrapper)
        )

        ### build graph relationships
        MonkeyWave.onAfter(MonkeyWaveBuff)
        MonkeyFurious.onAfters([MonkeyFuriousBuff, MonkeyFuriousDot])

        CannonBuster.onAfter(OakRuletDOT)
        BFGCannonball.onAfter(OakRuletDOT)
        ICBM.onAfter(OakRuletDOT)

        ICBM.onAfter(ICBMDOT)

        SpecialMonkeyEscort_Cannon.onJustAfter(SpecialMonkeyEscort_Bomb)

        return (
            CannonBuster,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                globalSkill.useful_wind_booster(),
                Booster,
                OakRoulette,
                Buckshot,
                MonkeyMagic,
                LuckyDice,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                EpicAdventure,
                Overdrive,
                PirateFlag,
                globalSkill.soul_contract(),
            ]
            + [
                SpecialMonkeyEscort_Cannon,
                BFGCannonball,
                FullMaker,
                RollingCannonRainbow,
                SupportMonkeyTwins,
            ]
            + [MonkeyWave, MonkeyFurious, ICBM, MirrorBreak]
            + [
                SpecialMonkeyEscort_Bomb,
                MirrorSpider,
                OakRuletDOT,
                MonkeyFuriousDot,
                MonkeyWaveBuff,
                MonkeyFuriousBuff,
                ICBMDOT,
            ]  # Not used from scheduler
            + [CannonBuster],
        )
