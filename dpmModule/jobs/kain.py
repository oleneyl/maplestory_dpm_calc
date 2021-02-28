from functools import partial
from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import ConcurrentRunRule, RuleSet
from . import globalSkill, jobutils
from .jobbranch import bowmen
from .jobclass import nova
from math import ceil
from typing import Any, Dict


BREATH_SHOOTER_HYPER = core.CharacterModifier(
    pdamage=10, boss_pdamage=15, armor_ignore=15
)  # 리인포스, 보스킬러, 이그노어 가드
EXECUTION_HYPER = core.CharacterModifier(armor_ignore=25)  # 이그노어 가드
REMAIN_INCENSE_REINFORCE = core.CharacterModifier(pdamage=50)


def strike_arrow(vEhc, passive_level: int):  # 1980ms 대기하면 초기화
    class StrikeArrowStatusWrapper(core.StackSkillWrapper):
        def __init__(self) -> None:
            super(StrikeArrowStatusWrapper, self).__init__(
                core.BuffSkill("스트라이크 애로우 선택", 0, 9999999), 3
            )
            self.time_elapsed = 0

        def spend_time(self, time: float) -> None:
            self.time_elapsed += time
            if self.time_elapsed >= 1980:
                self.time_elapsed = 0
                self.stack = 0
            return super(StrikeArrowStatusWrapper, self).spend_time(time)

        def vary(self, d: int) -> core.ResultObject:
            self.stack = (self.stack + d) % self._max
            self.time_elapsed = 0
            return core.ResultObject(
                delay=0,
                mdf=core.CharacterModifier(),
                damage=0,
                hit=0,
                sname=self.skill.name,
                spec="graph control",
            )

    StrikeArrowStatus = StrikeArrowStatusWrapper()
    NextStatus = StrikeArrowStatus.stackController(1)

    StrikeArrowI = (
        core.DamageSkill(
            name="스트라이크 애로우",
            delay=450,  # base delay 570
            damage=70 + 89 + 79 + 100 + passive_level,
            hit=5,
            modifier=BREATH_SHOOTER_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    StrikeArrowII = (
        core.DamageSkill(
            name="스트라이크 애로우 II",
            delay=450,  # base delay 570
            damage=160 + 79 + 100 + passive_level,
            hit=5,
            modifier=BREATH_SHOOTER_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    StrikeArrowRelease = (
        core.DamageSkill(
            name="[발현] 스트라이크 애로우",
            delay=450,  # base delay 570
            damage=200 + 80 + 85 + passive_level,
            hit=8,
            cooltime=1000,
            modifier=BREATH_SHOOTER_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    StrikeArrowIII = (
        core.DamageSkill(
            name="스트라이크 애로우 III",
            delay=450,  # base delay 570
            damage=240 + 100 + passive_level,
            hit=5,
            modifier=BREATH_SHOOTER_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )

    StrikeArrowI.onJustAfter(NextStatus)
    StrikeArrowII.onJustAfter(NextStatus)
    StrikeArrowRelease.onJustAfter(NextStatus)
    StrikeArrowIII.onJustAfter(NextStatus)

    BasicAttack = core.DamageSkill(name="기본 공격", delay=0, damage=0, hit=0).wrap(
        core.DamageSkillWrapper
    )
    BasicAttack.onJustAfter(
        core.OptionalElement(
            partial(StrikeArrowStatus.judge, 0, -1),
            StrikeArrowI,
            core.OptionalElement(
                partial(StrikeArrowStatus.judge, 1, -1),
                StrikeArrowII,
                StrikeArrowIII,
            ),
        )
    )

    return (
        StrikeArrowI,
        StrikeArrowII,
        StrikeArrowRelease,
        StrikeArrowIII,
        StrikeArrowStatus,
        BasicAttack,
    )


def scattering_shot(vEhc, passive_level: int):
    ScatteringShot = core.StackableDamageSkillWrapper(
        core.DamageSkill(
            name="스캐터링 샷",
            delay=480,  # base delay 630
            damage=120 + 75 + 75 + passive_level,
            hit=4,
            cooltime=6000,
            modifier=BREATH_SHOOTER_HYPER,
        ).setV(vEhc, 0, 2),
        max_stack=3,
    )
    ScatteringShotExceed = (
        core.DamageSkill(
            name="스캐터링 샷(초과)",
            delay=0,
            damage=120 + 75 + 75 + passive_level,
            hit=4 * 4,  # 4타, 4회 반복
            cooltime=-1,
            modifier=core.CharacterModifier(pdamage_indep=-50) + BREATH_SHOOTER_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    ScatteringShotRelease = (
        core.DamageSkill(
            name="[발현] 스캐터링 샷",
            delay=480,  # base delay 630
            damage=135 + 80 + 80 + passive_level,
            hit=4,
            cooltime=6000,
            modifier=BREATH_SHOOTER_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    ScatteringShotReleaseExceed = (
        core.DamageSkill(
            name="[발현] 스캐터링 샷(초과)",
            delay=0,
            damage=135 + 80 + 80 + passive_level,
            hit=4 * 5,  # 4타, 5회 반복
            modifier=core.CharacterModifier(pdamage_indep=-50) + BREATH_SHOOTER_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )

    ScatteringShot.onJustAfter(ScatteringShotExceed)
    ScatteringShotRelease.onJustAfter(ScatteringShotReleaseExceed)

    return (
        ScatteringShot,
        ScatteringShotExceed,
        ScatteringShotRelease,
        ScatteringShotReleaseExceed,
    )


def shaft_break(vEhc, passive_level: int):
    ShaftBreak = core.StackableDamageSkillWrapper(
        core.DamageSkill(
            name="샤프트 브레이크",
            delay=510,  # base delay 660
            damage=180 + 60 + passive_level,
            hit=3,
            cooltime=8000,
            modifier=BREATH_SHOOTER_HYPER,
        ).setV(vEhc, 0, 2),
        max_stack=3,
    )
    ShaftBreakExplode = (
        core.DamageSkill(
            name="샤프트 브레이크(폭발)",
            delay=0,
            damage=140 + 60 + passive_level,
            hit=10,
            modifier=BREATH_SHOOTER_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    ShaftBreakRelease = (
        core.DamageSkill(
            name="[발현] 샤프트 브레이크",
            delay=510,  # base delay 660
            damage=180 + 75 + passive_level,
            hit=3,
            cooltime=11000,
            modifier=BREATH_SHOOTER_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    ShaftBreakReleaseExplode = (
        core.DamageSkill(
            name="[발현] 샤프트 브레이크(폭발)",
            delay=0,
            damage=240 + 75 + passive_level,
            hit=10,
            modifier=BREATH_SHOOTER_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    ShaftBreakReleaseTornado = (
        core.DamageSkill(
            name="[발현] 샤프트 브레이크(회오리)",
            delay=0,
            damage=40 + 20 + passive_level // 3,
            hit=3 * 12,  # 3타, 12회 타격
            modifier=BREATH_SHOOTER_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )

    ShaftBreak.onJustAfter(ShaftBreakExplode)
    ShaftBreakRelease.onJustAfter(ShaftBreakReleaseExplode)
    ShaftBreakReleaseExplode.onJustAfter(ShaftBreakReleaseTornado)

    return (
        ShaftBreak,
        ShaftBreakExplode,
        ShaftBreakRelease,
        ShaftBreakReleaseExplode,
        ShaftBreakReleaseTornado,
    )


def falling_dust(vEhc, combat: int):
    FallingDust = core.StackableDamageSkillWrapper(
        core.DamageSkill(
            name="폴링 더스트",
            delay=510,  # base delay 660
            damage=410 + 5 * combat,
            hit=8,
            cooltime=10000,
            modifier=BREATH_SHOOTER_HYPER,
        ).setV(vEhc, 0, 2),
        max_stack=2,
    )
    FallingDustRelease = (
        core.DamageSkill(
            name="[발현] 폴링 더스트",
            delay=510,  # base delay 660
            damage=420 + 5 * combat,
            hit=8,
            cooltime=14000,
            modifier=BREATH_SHOOTER_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    FallingDustReleaseBlow = (
        core.DamageSkill(
            name="[발현] 폴링 더스트(악의)",
            delay=0,
            damage=240 + 5 * combat,
            hit=15,
            cooltime=-1,
            modifier=BREATH_SHOOTER_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )

    FallingDustRelease.onJustAfter(FallingDustReleaseBlow)

    return FallingDust, FallingDustRelease, FallingDustReleaseBlow


def chain_sickle(vEhc, combat: int):
    ChainSickle = (
        core.DamageSkill(
            name="[처형] 체인 시클",
            delay=240,  # base delay 330 -> 300 by skipActionFrame=4
            damage=200 + 2 * combat,
            hit=6,
            cooltime=7000,
            red=True,
            modifier=EXECUTION_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    ChainSickleFinish = (
        core.DamageSkill(
            name="[처형] 체인 시클(마무리 일격)",
            delay=390,  # base delay 510
            damage=220 + 2 * combat,
            hit=12,
            cooltime=-1,
            modifier=EXECUTION_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    ChainSickle.onAfter(ChainSickleFinish)

    return ChainSickle, ChainSickleFinish


def poison_needle(vEhc, combat: int):
    PoisonNeedle = (
        core.DamageSkill(
            name="[처형] 포이즌 니들",
            delay=330,  # prepare.time 330
            damage=250 + 3 * combat,
            hit=8,
            cooltime=15000,
            red=True,
            modifier=EXECUTION_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    PoisonNeedleSpin = (
        core.DamageSkill(  # 연속공격을 스킬 하나에 합쳐둠
            name="[처형] 포이즌 니들(연속 공격)",
            delay=720 - 330,  # common.updatableTime - prepare.time
            damage=190 + combat,
            hit=8 * 4,  # 8타, 4회 반복
            modifier=EXECUTION_HYPER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    PoisonNeedleEnd = (
        core.DamageSkill(
            name="[처형] 포이즌 니들(후딜)",
            delay=180,
            damage=0,
            hit=0,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    PoisonNeedleDOT = core.DotSkill(
        name="[처형] 포이즌 니들(도트)",
        summondelay=0,
        delay=1000,
        damage=290 + 3 * combat,
        hit=1,
        remain=12000,
        cooltime=-1,
    ).wrap(core.DotSkillWrapper)
    PoisonNeedle.onAfter(PoisonNeedleSpin)
    PoisonNeedleSpin.onAfter(PoisonNeedleEnd)
    PoisonNeedleSpin.onJustAfter(PoisonNeedleDOT)

    return PoisonNeedle, PoisonNeedleSpin, PoisonNeedleEnd, PoisonNeedleDOT


def remain_incense(vEhc, passive_level: int):
    RemainIncense = (
        core.DamageSkill(
            name="리메인 인센스",
            delay=0,
            damage=90 + 60 + passive_level,
            hit=4,
            cooltime=300,
            modifier=REMAIN_INCENSE_REINFORCE,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )

    def use_remain_incense(count):
        return core.OptionalElement(
            RemainIncense.is_available, core.RepeatElement(RemainIncense, count)
        )

    RemainIncense.protect_from_running()

    return RemainIncense, use_remain_incense


def death_blessing(vEhc, passive_level: int):
    Incarnation = core.BuffSkill(
        name="인카네이션",
        delay=780,
        remain=40000,
        cooltime=180 * 1000,
        pdamage=15,
        patt=15,
    ).wrap(core.BuffSkillWrapper)

    DeathBlessingStack = core.StackSkillWrapper(
        core.BuffSkill(name="데스 블레싱 스택", delay=0, remain=9999999), 15
    )
    DeathBlessing = (
        core.DamageSkill(
            name="데스 블레싱",
            delay=0,
            damage=140 + 135 + passive_level * 3,
            hit=10,
            cooltime=-1,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    DeathBlessingIncarnation = (
        core.DamageSkill(
            name="데스 블레싱(인카네이션)",
            delay=0,
            damage=140 + 135 + passive_level * 3,
            hit=13,
            cooltime=-1,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    DeathBlessingBonus = core.BuffSkill(
        name="데스 블레싱(버프)",
        delay=0,
        remain=5000,
        cooltime=-1,
    ).wrap(core.BuffSkillWrapper)

    UseDeathBlessing = core.OptionalElement(
        partial(DeathBlessingStack.judge, 1, 1),
        core.OptionalElement(
            Incarnation.is_active,
            DeathBlessingIncarnation,
            DeathBlessing,
        ),
    )

    for sk in [DeathBlessing, DeathBlessingIncarnation]:
        sk.onJustAfter(DeathBlessingStack.stackController(-1))
        sk.onJustAfter(DeathBlessingBonus)

    return (
        Incarnation,
        DeathBlessingStack,
        DeathBlessing,
        DeathBlessingIncarnation,
        DeathBlessingBonus,
        UseDeathBlessing,
    )


def dragon_burst(vEhc):
    DragonBurstReleaseInit = core.DamageSkill(
        name="[발현] 드래곤 버스트",
        delay=300,
        damage=0,
        hit=0,
        cooltime=90000,
        red=True,
    ).wrap(core.DamageSkillWrapper)
    DragonBurstReleaseTick = (
        core.DamageSkill(
            name="[발현] 드래곤 버스트(키다운)",
            delay=180,
            damage=400 + vEhc.getV(0, 0) * 16,
            hit=12,
            cooltime=-1,
        )
        .isV(vEhc, 0, 0)
        .wrap(core.DamageSkillWrapper)
    )
    DragonBurstReleaseEnd = core.DamageSkill(
        name="[발현] 드래곤 버스트(후딜)",
        delay=180,
        damage=0,
        hit=0,
        cooltime=-1,
    ).wrap(core.DamageSkillWrapper)

    DragonBurstReleaseRepeat = core.RepeatElement(DragonBurstReleaseTick, 15)
    DragonBurstReleaseInit.onAfter(DragonBurstReleaseRepeat)
    DragonBurstReleaseRepeat.onAfter(DragonBurstReleaseEnd)

    return DragonBurstReleaseInit, DragonBurstReleaseTick, DragonBurstReleaseEnd


def fatal_blitz(vEhc):
    FatalBlitzInit = core.DamageSkill(
        name="[처형] 페이탈 블리츠",
        delay=360,
        damage=0,
        hit=0,
        cooltime=90000,
        red=True,
    ).wrap(core.DamageSkillWrapper)
    FatalBlitzTick = (
        core.DamageSkill(
            name="[처형] 페이탈 블리츠(키다운)",
            delay=90,
            damage=300 + vEhc.getV(0, 0) * 12,
            hit=12,
            cooltime=-1,
        )
        .isV(vEhc, 0, 0)
        .wrap(core.DamageSkillWrapper)
    )
    FatalBlitzEnd = core.DamageSkill(
        name="[처형] 페이탈 블리츠(후딜)",
        delay=180,
        damage=0,
        hit=0,
        cooltime=-1,
    ).wrap(core.DamageSkillWrapper)

    FatalBlitzRepeat = core.RepeatElement(FatalBlitzTick, 14)
    FatalBlitzInit.onAfter(FatalBlitzRepeat)
    FatalBlitzRepeat.onAfter(FatalBlitzEnd)

    return FatalBlitzInit, FatalBlitzTick, FatalBlitzEnd


def thanatos_descent(vEhc):
    ThanatosDescent = (
        core.BuffSkill(
            name="타나토스 디센트",
            delay=420,  # base delay 540 TODO: check AS applying
            remain=35000,
            cooltime=180 * 1000,
            red=True,
            pdamage=15 + vEhc.getV(0, 0),
        )
        .isV(vEhc, 0, 0)
        .wrap(core.BuffSkillWrapper)
    )
    ThanatosDescentArrow = (
        core.DamageSkill(
            name="타나토스 디센트(죽음의 화살)",
            delay=0,
            damage=325 + 13 * vEhc.getV(0, 0),
            hit=3 * 6,  # 3타, 6개 발사
            cooltime=3000,
        )
        .isV(vEhc, 0, 0)
        .wrap(core.DamageSkillWrapper)
    )
    ThanatosDescentFinalInit = (
        core.DamageSkill(
            name="타나토스 디센트(죽음의 영역)(시전)",
            delay=2490,
            damage=0,
            hit=0,
            cooltime=-1,
        )
        .isV(vEhc, 0, 0)
        .wrap(core.DamageSkillWrapper)
    )
    ThanatosDescentFinal = (
        core.DamageSkill(
            name="타나토스 디센트(죽음의 영역)",
            delay=180,
            damage=650 + 26 * vEhc.getV(0, 0),
            hit=15,
            cooltime=-1,
        )
        .isV(vEhc, 0, 0)
        .wrap(core.DamageSkillWrapper)
    )
    ThanatosDescentFinalFinish = (
        core.DamageSkill(
            name="타나토스 디센트(죽음의 영역)(후딜)",
            delay=780,
            damage=0,
            hit=0,
            cooltime=-1,
        )
        .isV(vEhc, 0, 0)
        .wrap(core.DamageSkillWrapper)
    )

    UseThanatosDescentArrow = core.OptionalElement(
        lambda: ThanatosDescentArrow.is_available() and ThanatosDescent.is_active(),
        ThanatosDescentArrow,
    )

    ThanatosDescent.onJustAfter(ThanatosDescentFinalInit.controller(35000))
    ThanatosDescentFinalRepeat = core.RepeatElement(ThanatosDescentFinal, 9)
    ThanatosDescentFinalInit.onAfter(ThanatosDescentFinalRepeat)
    ThanatosDescentFinalRepeat.onAfter(ThanatosDescentFinalFinish)

    ThanatosDescentArrow.protect_from_running()

    return (
        ThanatosDescent,
        ThanatosDescentArrow,
        ThanatosDescentFinalInit,
        ThanatosDescentFinal,
        UseThanatosDescentArrow,
    )


class GrapOfAgonyWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        skill = core.SummonSkill(
            name="그립 오브 애거니",
            summondelay=510,  # base delay 660, TODO: check AS applying
            delay=340,  # TODO: check delay in game
            damage=475 + 19 * vEhc.getV(num1, num2),
            hit=6,
            remain=6000,
            cooltime=180 * 1000,
            red=True,
        ).isV(vEhc, num1, num2)
        super(GrapOfAgonyWrapper, self).__init__(skill)
        self.stack = 0
        self.hit_per_stack = 25
        self.max_stack = 15 * self.hit_per_stack
        self.remain_time = self.skill.remain

    def _use(self, skill_modifier):
        result = super(GrapOfAgonyWrapper, self)._use(skill_modifier)
        self.timeLeft += (self.stack // self.hit_per_stack - 1) * 1000
        self.stack = self.stack % self.hit_per_stack
        return result

    def vary(self, d: int) -> core.ResultObject:
        self.stack = max(min((self.stack + d), self.max_stack), 0)
        return core.ResultObject(
            0,
            core.CharacterModifier(),
            0,
            0,
            sname=self.skill.name,
            spec="graph control",
        )

    def stackController(self, d: int) -> core.TaskHolder:
        task = core.Task(self, partial(self.vary, d))
        return core.TaskHolder(task, name=f"+{d}")

    def judge(self, stack: int, direction: int) -> bool:
        return (self.stack - stack) * direction >= 0


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "DEX"
        self.jobname = "카인"
        self.ability_list = Ability_tool.get_ability_set(
            "boss_pdamage", "crit", "buff_rem"
        )
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(crit_damage=15, pdamage=50)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule("크리티컬 리인포스", "타나토스 디센트"), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        Hitman = core.InformedCharacterModifier("히트맨", att=40, crit=35)
        BreathShooterMastery = core.InformedCharacterModifier("브레스 슈터 마스터리", att=40)
        PhysicalTraining = core.InformedCharacterModifier("피지컬 트레이닝", stat_main=60)
        NaturalBornInstinct = core.InformedCharacterModifier(
            "내츄럴 본 인스팅트", pdamage_indep=20, att=40, crit=20, armor_ignore=10
        )
        GrindingII = core.InformedCharacterModifier("그라인딩 II", att=30 + passive_level)
        Dogma = core.InformedCharacterModifier(
            "도그마",
            pdamage_indep=20 + passive_level // 2,
            crit_damage=20 + passive_level,
            armor_ignore=30 + passive_level,
        )
        BreathShooterExpert = core.InformedCharacterModifier(
            "브레스 슈터 엑스퍼트",
            pdamage_indep=30 + passive_level // 2,
            att=30 + passive_level,
            crit_damage=20 + passive_level // 2,
        )
        AdaptToDeath = core.InformedCharacterModifier(
            "어댑트 투 데스",
            pdamage=10 + ceil(passive_level / 2),
            boss_pdamage=10 + passive_level // 4,
        )

        return [
            Hitman,
            BreathShooterMastery,
            PhysicalTraining,
            NaturalBornInstinct,
            GrindingII,
            Dogma,
            BreathShooterExpert,
            AdaptToDeath,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=30)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=90+ceil(passive_level / 2))

        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """"""
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        # Release Skills
        (
            StrikeArrowI,
            StrikeArrowII,
            StrikeArrowRelease,
            StrikeArrowIII,
            StrikeArrowStatus,
            BasicAttack,
        ) = strike_arrow(vEhc, passive_level)
        (
            ScatteringShot,
            ScatteringShotExceed,
            ScatteringShotRelease,
            ScatteringShotReleaseExceed,
        ) = scattering_shot(vEhc, passive_level)
        (
            ShaftBreak,
            ShaftBreakExplode,
            ShaftBreakRelease,
            ShaftBreakReleaseExplode,
            ShaftBreakReleaseTornado,
        ) = shaft_break(vEhc, passive_level)
        (
            FallingDust,
            FallingDustRelease,
            FallingDustReleaseBlow,
        ) = falling_dust(vEhc, self.combat)

        # Execution skills
        PhantomBlade = (
            core.DamageSkill(
                name="[처형] 팬텀 블레이드",
                delay=510,  # base delay 660
                damage=155 + 35 + passive_level,
                hit=6,
                modifier=EXECUTION_HYPER,
            )
            .setV(vEhc, 0, 2)
            .wrap(core.DamageSkillWrapper)
        )

        TearingKnife = (
            core.DamageSkill(
                name="[처형] 테어링 나이프",
                delay=510,  # base delay 660
                damage=210 + 95 + passive_level,
                hit=7,
                cooltime=4500,
                red=True,
                modifier=EXECUTION_HYPER,
            )
            .setV(vEhc, 0, 2)
            .wrap(core.DamageSkillWrapper)
        )

        (
            ChainSickle,
            ChainSickleFinal,
        ) = chain_sickle(vEhc, self.combat)
        (
            PoisonNeedle,
            PoisonNeedleSpin,
            PoisonNeedleEnd,
            PoisonNeedleDOT,
        ) = poison_needle(vEhc, self.combat)

        # Additional Hit
        DragonPang = (  # TODO: 공격주기 정확히 측정
            core.SummonSkill(
                name="드래곤 팡",
                summondelay=0,
                delay=(1650 * 7 + 3000) / 7,  # 평균으로 계산, 필요해지면 공격 간격 정확히 반영
                damage=100 + 60 + 70 + passive_level * 2,
                hit=4 * 3,  # 구체 3개 유지 가정
                remain=9999999,
            )
            .setV(vEhc, 0, 2)
            .wrap(core.SummonSkillWrapper)
        )

        RemainIncense, use_remain_incense = remain_incense(vEhc, passive_level)
        (
            Incarnation,
            DeathBlessingStack,
            DeathBlessing,
            DeathBlessingIncarnation,
            DeathBlessingBonus,
            UseDeathBlessing,
        ) = death_blessing(vEhc, passive_level)

        # Gauge
        Malice = core.StackSkillWrapper(
            core.BuffSkill(name="멜리스", delay=0, remain=9999999), 500
        )
        MaliceTick = core.SummonSkill(
            name="멜리스(자연회복)",
            summondelay=0,
            delay=4020,
            damage=0,
            hit=0,
            remain=99999999,
        ).wrap(core.SummonSkillWrapper)

        Possession = core.BuffSkill(
            name="포제션",
            delay=0,  # base delay 270, 다른 스킬 딜레이 중 사용 가능 -> 0
            remain=15000,
            cooltime=30,
        ).wrap(core.BuffSkillWrapper)

        # Hyper skills
        ChasingShot = (
            core.DamageSkill(
                name="체이싱 샷",
                delay=840,  # base delay 960, AS from buff not applied
                damage=320,
                hit=6 * 3,
                cooltime=30000,
                modifier=BREATH_SHOOTER_HYPER,
            )
            .setV(vEhc, 0, 2)
            .wrap(core.DamageSkillWrapper)
        )
        SneakySniping = (
            core.DamageSkill(
                name="스니키 스나이핑",
                delay=60 + 270,  # 60 + keydownend.action
                damage=175,
                hit=10 * 5,  # 10타, 5회 반복
                cooltime=40000,
                modifier=BREATH_SHOOTER_HYPER,
            )
            .setV(vEhc, 0, 2)
            .wrap(core.DamageSkillWrapper)
        )
        SneakySnipingRelease = (
            core.DamageSkill(
                name="[발현/처형] 스니키 스나이핑",
                delay=60 + 270,  # 60 + keydownend.action
                damage=200,
                hit=12 * 5,  # 12타, 5회 반복
                cooltime=60000,
                modifier=BREATH_SHOOTER_HYPER + EXECUTION_HYPER,
            )
            .setV(vEhc, 0, 2)
            .wrap(core.DamageSkillWrapper)
        )

        # V skills
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 0, 0, 10)
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 0, 0)
        Pantheon = nova.PantheonWrapper(vEhc, 0, 0)
        NovaGoddessBless = nova.NovaGoddessBlessWrapper(vEhc, 0, 0)

        (
            DragonBurstReleaseInit,
            DragonBurstReleaseTick,
            DragonBurstReleaseEnd,
        ) = dragon_burst(vEhc)
        (
            FatalBlitzInit,
            FatalBlitzTick,
            FatalBlitzEnd,
        ) = fatal_blitz(vEhc)
        (
            ThanatosDescent,
            ThanatosDescentArrow,
            ThanatosDescentFinalInit,
            ThanatosDescentFinal,
            UseThanatosDescentArrow,
        ) = thanatos_descent(vEhc)
        GrapOfAgony = GrapOfAgonyWrapper(vEhc, 0, 0)

        ######   Skill Wrapper   ######
        # Malice
        MaliceTick.onTick(
            core.OptionalElement(
                ThanatosDescent.is_active,
                Malice.stackController(40),
                Malice.stackController(20),
            )
        )
        AddMalice = core.OptionalElement(
            ThanatosDescent.is_active,
            Malice.stackController(35),
            Malice.stackController(18),
        )
        for sk in [
            StrikeArrowI,
            StrikeArrowII,
            StrikeArrowIII,
            ScatteringShot,
            ShaftBreakExplode,
            FallingDust,
            ChasingShot,
            SneakySniping,
        ]:
            sk.onJustAfter(AddMalice)

        # Possession
        Possession.onConstraint(
            core.ConstraintElement("멜리스 스톤 > 1", Malice, partial(Malice.judge, 100, 1))
        )
        Possession.onJustAfter(Malice.stackController(-100))

        # Release
        IsPosession = core.ConstraintElement("포제션 ON", Possession, Possession.is_active)
        for normal, release in [
            (StrikeArrowI, StrikeArrowRelease),
            (ScatteringShot, ScatteringShotRelease),
            (ShaftBreak, ShaftBreakRelease),
            (FallingDust, FallingDustRelease),
            (SneakySniping, SneakySnipingRelease),
        ]:
            release.onConstraint(IsPosession)
            release.onJustAfter(Possession.controller(1))
            normal.onConstraint(
                core.ConstraintElement("제한", release, release.is_not_usable)
            )

        # Remain Incense
        # 발현 스킬의 쿨타임 있는 파이널 어택처럼 취급
        for sk, count in [
            (StrikeArrowRelease, 1),
            (ScatteringShotRelease, 2),
            (ShaftBreakReleaseExplode, 6),
            (FallingDustRelease, 8),
            (SneakySnipingRelease, 8),
            (DragonBurstReleaseTick, 1),
            (ThanatosDescentFinal, 2),
        ]:
            sk.onJustAfter(use_remain_incense(count))

        # Death Blessing
        AddDeathBlessingStack = DeathBlessingStack.stackController(1)
        for sk in [
            StrikeArrowRelease,
            ScatteringShotRelease,
            ShaftBreakReleaseExplode,
            FallingDustRelease,
            SneakySnipingRelease,
            DragonBurstReleaseTick,
            ThanatosDescentFinal,
        ]:
            sk.onJustAfter(AddDeathBlessingStack)
        for sk in [
            PhantomBlade,
            TearingKnife,
            ChainSickle,
            PoisonNeedle,
            SneakySnipingRelease,
            FatalBlitzTick,
        ]:
            sk.onJustAfter(UseDeathBlessing)

        DeathBlessingBonusMalice = core.OptionalElement(
            lambda: DeathBlessingBonus.is_active() and DeathBlessingStack.judge(1, 1),
            Malice.stackController(12),
        )
        for sk in [
            PhantomBlade,
            TearingKnife,
            ChainSickle,
            PoisonNeedle,
            FatalBlitzTick,
        ]:
            sk.add_runtime_modifier(
                DeathBlessingBonus,
                lambda sk: core.CharacterModifier(pdamage_indep=15 * sk.is_active()),
            )
            sk.onJustAfter(DeathBlessingBonusMalice)

        for sk in [
            ChainSickleFinal,
            PoisonNeedleSpin,
            DeathBlessing,
            DeathBlessingIncarnation,
        ]:
            sk.add_runtime_modifier(
                DeathBlessingBonus,
                lambda sk: core.CharacterModifier(pdamage_indep=15 * sk.is_active()),
            )

        # Thanatos Descent
        counted_skills = [
            StrikeArrowI,
            StrikeArrowII,
            StrikeArrowIII,
            ScatteringShot,
            ShaftBreakExplode,
            FallingDust,
            ChasingShot,
            SneakySniping,
            StrikeArrowRelease,
            ScatteringShotRelease,
            ShaftBreakReleaseExplode,
            FallingDustRelease,
            SneakySnipingRelease,
            DragonBurstReleaseTick,
            PhantomBlade,
            TearingKnife,
            ChainSickle,
            PoisonNeedle,
            FatalBlitzTick,
        ]
        for sk in counted_skills:
            sk.onJustAfter(UseThanatosDescentArrow)

        # Grap of Agony
        AddAgony = GrapOfAgony.stackController(1)
        for sk in counted_skills:
            sk.onJustAfter(AddAgony)

        # Scheduling
        GrapOfAgony.vary(15 * 25)  # start with full stack

        IsDeathBlessed = core.ConstraintElement(
            "데스 블레싱 스택 >= 1",
            DeathBlessingStack,
            partial(DeathBlessingStack.judge, 1, 1),
        )
        for sk in [
            PhantomBlade,
            TearingKnife,
            ChainSickle,
            PoisonNeedle,
            SneakySnipingRelease,
            FatalBlitzTick,
        ]:
            sk.onConstraint(IsDeathBlessed)
        StrikeArrowRelease.onConstraint(
            core.ConstraintElement("맬리스 조건", Malice, partial(Malice.judge, 500, 1))
        )
        PhantomBlade.onConstraint(
            core.ConstraintElement(
                "데스 블레싱 조건",
                DeathBlessingStack,
                partial(DeathBlessingStack.judge, 9, 1),
            )
        )

        return (
            BasicAttack,
            [
                Malice,
                StrikeArrowStatus,
                globalSkill.maple_heros(
                    chtr.level, name="노바의 용사", combat_level=self.combat
                ),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                NovaGoddessBless,
                CriticalReinforce,
                Incarnation,
                ThanatosDescent,
                globalSkill.soul_contract(),
                Possession,
            ]
            + [MaliceTick, DragonPang, GuidedArrow, GrapOfAgony]
            + [ThanatosDescentFinalInit]  # reserved task, use as early as possible
            + [Pantheon, DragonBurstReleaseInit, FatalBlitzInit, MirrorBreak, MirrorSpider]
            + [
                SneakySnipingRelease,
                FallingDustRelease,
                ShaftBreakRelease,
                ScatteringShotRelease,
                StrikeArrowRelease,
            ]
            + [PoisonNeedle, ChainSickle, TearingKnife, PhantomBlade]
            + [ChasingShot, SneakySniping, FallingDust, ScatteringShot, ShaftBreak]
            + [
                RemainIncense,
                DeathBlessingBonus,
                PoisonNeedleDOT,
                ThanatosDescentArrow,
            ]  # Not used from scheduler
            + [BasicAttack],
        )
