from functools import partial
from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet
from . import globalSkill
from .jobbranch import bowmen
from .jobclass import nova
from math import ceil
from typing import Any, Dict


BREATH_SHOOTER_REINFORCE = core.CharacterModifier(pdamage=10)
BREATH_SHOOTER_BOSSKILLER = core.CharacterModifier(boss_pdamage=15)
EXECUTION_BOSSKILLER = core.CharacterModifier(boss_pdamage=20)
REMAIN_INCENSE_REINFORCE = core.CharacterModifier()  # pdamage=50


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
            damage=70 + 89 + 79 + 85 + passive_level,
            hit=5,
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    StrikeArrowII = (
        core.DamageSkill(
            name="스트라이크 애로우 II",
            delay=450,  # base delay 570
            damage=160 + 79 + 85 + passive_level,
            hit=5,
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
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
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    StrikeArrowIII = (
        core.DamageSkill(
            name="스트라이크 애로우 III",
            delay=450,  # base delay 570
            damage=240 + 85 + passive_level,
            hit=5,
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
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
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
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
            modifier=core.CharacterModifier(pdamage_indep=-50)
            + BREATH_SHOOTER_REINFORCE
            + BREATH_SHOOTER_BOSSKILLER,
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
            cooltime=7000,
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
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
            modifier=core.CharacterModifier(pdamage_indep=-50)
            + BREATH_SHOOTER_REINFORCE
            + BREATH_SHOOTER_BOSSKILLER,
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
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
        ).setV(vEhc, 0, 2),
        max_stack=3,
    )
    ShaftBreakExplode = (
        core.DamageSkill(
            name="샤프트 브레이크(폭발)",
            delay=0,
            damage=140 + 60 + passive_level,
            hit=10,
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
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
            cooltime=12000,
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
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
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
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
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
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
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
        ).setV(vEhc, 0, 2),
        max_stack=2,
    )
    FallingDustRelease = (
        core.DamageSkill(
            name="[발현] 폴링 더스트",
            delay=510,  # base delay 660
            damage=420 + 5 * combat,
            hit=8,
            cooltime=16000,
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
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
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
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
            delay=240,  # base delay 300
            damage=180 + 2 * combat,
            hit=6,
            cooltime=7000,
            red=True,
            modifier=EXECUTION_BOSSKILLER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    ChainSickleFinish = (
        core.DamageSkill(
            name="[처형] 체인 시클(마무리 일격)",
            delay=360,  # base delay 480
            damage=230 + 2 * combat,
            hit=12,
            cooltime=-1,
            modifier=EXECUTION_BOSSKILLER,
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
            delay=360,  # base delay 360
            damage=260 + 3 * combat,
            hit=8,
            cooltime=15000,
            red=True,
            modifier=EXECUTION_BOSSKILLER,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    PoisonNeedleSpin = (
        core.DamageSkill(  # 연속공격을 스킬 하나에 합쳐둠
            name="[처형] 포이즌 니들(연속 공격)",
            delay=900 - 360,
            damage=115 + combat,
            hit=12 * 5,  # 12타, 5회 반복
            modifier=EXECUTION_BOSSKILLER,
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
    class RemainIncenseWrapper(core.DamageSkillWrapper):
        def __init__(self):
            skill = core.DamageSkill(
                name="리메인 인센스",
                delay=0,
                damage=150 + 100 + passive_level,
                hit=4,
                cooltime=6000,  # TODO: 재생성 대기시간에 쿨감이 적용되는지?
                modifier=REMAIN_INCENSE_REINFORCE,
            ).setV(vEhc, 0, 2)
            super(RemainIncenseWrapper, self).__init__(skill)
            self.thanatos_descent: core.BuffSkillWrapper = None

        def get_cooltime(self) -> float:
            if self.thanatos_descent.is_active():
                return 1500
            else:
                return super(RemainIncenseWrapper, self).get_cooltime()

        def register_thanatos(self, skill: core.BuffSkillWrapper):
            self.thanatos_descent = skill

    RemainIncense = RemainIncenseWrapper()
    RemainIncenseExceed = (
        core.DamageSkill(
            name="리메인 인센스(초과)",
            delay=0,
            damage=150 + 100 + passive_level,
            hit=4 * 4,  # 4타, 4회 반복
            cooltime=-1,
            modifier=core.CharacterModifier(pdamage_indep=-50)
            + REMAIN_INCENSE_REINFORCE,
        )
        .setV(vEhc, 0, 2)
        .wrap(core.DamageSkillWrapper)
    )
    RemainIncense.onJustAfter(RemainIncenseExceed)

    UseRemainIncense = core.OptionalElement(RemainIncense.is_available, RemainIncense)
    RemainIncense.protect_from_running()

    return RemainIncense, UseRemainIncense


def death_blessing(vEhc, passive_level: int):
    Incarnation = core.BuffSkill(
        name="인카네이션",
        delay=780,
        remain=30000,
        cooltime=180 * 1000,
        pdamage=15,
        patt=15,
    ).wrap(core.BuffSkillWrapper)

    DeathBlessingStack = core.StackSkillWrapper(
        core.BuffSkill(name="데스 블레싱 스택", delay=0, remain=9999999), 10
    )
    DeathBlessing = (
        core.DamageSkill(
            name="데스 블레싱",
            delay=0,
            damage=150 + 155 + passive_level * 5,
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
            damage=150 + 155 + passive_level * 5,
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

    for sk in [DeathBlessing, DeathBlessingIncarnation]:
        sk.onJustAfter(DeathBlessingStack.stackController(-1))
        sk.onJustAfter(DeathBlessingBonus)
        sk.add_runtime_modifier(
            DeathBlessingBonus,
            lambda sk: core.CharacterModifier(pdamage_indep=10 * sk.is_active()),
        )
    UseDeathBlessing = core.OptionalElement(
        partial(DeathBlessingStack.judge, 1, 1),
        core.OptionalElement(
            Incarnation.is_active,
            DeathBlessingIncarnation,
            DeathBlessing,
        ),
    )

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
        cooltime=60000,
        red=True,
    ).wrap(core.DamageSkillWrapper)
    DragonBurstReleaseTick = (
        core.DamageSkill(
            name="[발현] 드래곤 버스트(키다운)",
            delay=210,
            damage=475 + vEhc.getV(0, 0) * 19,
            hit=10,
            cooltime=-1,
            modifier=BREATH_SHOOTER_REINFORCE + BREATH_SHOOTER_BOSSKILLER,
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

    DragonBurstReleaseRepeat = core.RepeatElement(DragonBurstReleaseTick, 10)
    DragonBurstReleaseInit.onAfter(DragonBurstReleaseRepeat)
    DragonBurstReleaseRepeat.onAfter(DragonBurstReleaseEnd)

    return DragonBurstReleaseInit, DragonBurstReleaseTick, DragonBurstReleaseEnd


def fatal_blitz(vEhc):
    FatalBlitzInit = core.DamageSkill(
        name="[처형] 페이탈 블리츠",
        delay=360,
        damage=0,
        hit=0,
        cooltime=60000,
        red=True,
    ).wrap(core.DamageSkillWrapper)
    FatalBlitzTick = (
        core.DamageSkill(
            name="[처형] 페이탈 블리츠(키다운)",
            delay=240,
            damage=325 + vEhc.getV(0, 0) * 13,
            hit=12,
            cooltime=-1,
            modifier=EXECUTION_BOSSKILLER,
        )
        .isV(vEhc, 0, 0)
        .wrap(core.DamageSkillWrapper)
    )
    FatalBlitzEnd = core.DamageSkill(
        name="[처형] 페이탈 블리츠(후딜)",
        delay=360,
        damage=0,
        hit=0,
        cooltime=-1,
    ).wrap(core.DamageSkillWrapper)

    FatalBlitzRepeat = core.RepeatElement(FatalBlitzTick, 10)
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
    ThanatosDescentHand = (
        core.DamageSkill(
            name="타나토스 디센트(죽음의 손길)",
            delay=0,
            damage=500 + 20 * vEhc.getV(0, 0),
            hit=12,
            cooltime=3000,
        )
        .isV(vEhc, 0, 0)
        .wrap(core.DamageSkillWrapper)
    )
    ThanatosDescentFinish = (
        core.DamageSkill(
            name="타나토스 디센트(죽음의 영역)",
            delay=4890,  # TODO: check actual delay
            damage=650 + 26 * vEhc.getV(0, 0),
            hit=15 * 9,  # 15타, 9회 반복 TODO: is *9 correct?
            cooltime=-1,
        )
        .isV(vEhc, 0, 0)
        .wrap(core.DamageSkillWrapper)
    )

    ThanatosDescentStack = core.StackSkillWrapper(
        core.BuffSkill("타나토스 디센트(죽음의 손길)(스택)", 0, 9999999), 6
    )
    UseThanatosDescentHand = core.OptionalElement(
        lambda: ThanatosDescentHand.is_available() and ThanatosDescentStack.judge(6, 1),
        ThanatosDescentHand,
    )
    UseThanatosDescentHand.onBefore(ThanatosDescentStack.stackController(1))
    ThanatosDescentHand.onJustAfter(ThanatosDescentStack.stackController(-6))

    ThanatosDescent.onJustAfter(ThanatosDescentFinish.controller(35000))

    ThanatosDescentHand.protect_from_running()

    return (
        ThanatosDescent,
        ThanatosDescentHand,
        ThanatosDescentFinish,
        UseThanatosDescentHand,
        ThanatosDescentStack,
    )


class GrapOfAgonyWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        skill = core.SummonSkill(
            name="그립 오브 애거니",
            summondelay=510,  # base delay 660, TODO: check AS applying
            delay=340,  # TODO: check delay in game
            damage=225 + 9 * vEhc.getV(num1, num2),
            hit=4,
            remain=6000,
            cooltime=180 * 1000,
            red=True,
        ).isV(vEhc, num1, num2)
        super(GrapOfAgonyWrapper, self).__init__(skill)
        self.stack = 0
        self.max_stack = 15 * 12
        self.remain_time = self.skill.remain

    def _use(self, skill_modifier):
        result = super(GrapOfAgonyWrapper, self)._use(skill_modifier)
        self.timeLeft += (self.stack // 12 - 1) * 1000
        self.stack = self.stack % 12
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
        self.jobtype = "dex"
        self.jobname = "카인"
        self.ability_list = Ability_tool.get_ability_set(
            "boss_pdamage", "crit", "buff_rem"
        )
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(crit_damage=15, pdamage=40, armor_ignore=-10)

    def get_ruleset(self):
        ruleset = RuleSet()
        return ruleset

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        Hitman = core.InformedCharacterModifier("히트맨", att=40, crit=35)
        BreathShooterMastery = core.InformedCharacterModifier("브레스 슈터 마스터리", att=30)
        PhysicalTraining = core.InformedCharacterModifier("피지컬 트레이닝", stat_main=60)
        NaturalBornInstinct = core.InformedCharacterModifier(
            "네츄럴 본 인스팅트", pdamage_indep=25, att=40, crit=20, armor_ignore=10
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
        Mastery = core.InformedCharacterModifier(
            "숙련도", pdamage_indep=-5 + 0.5 * ceil(passive_level / 2)
        )

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
                damage=190 + 100 + passive_level,
                hit=6,
                modifier=EXECUTION_BOSSKILLER,
            )
            .setV(vEhc, 0, 2)
            .wrap(core.DamageSkillWrapper)
        )

        TearingKnife = (
            core.DamageSkill(
                name="[처형] 테어링 나이프",
                delay=510,  # base delay 660
                damage=250 + 80 + passive_level,
                hit=7,
                cooltime=4500,
                red=True,
                modifier=EXECUTION_BOSSKILLER,
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
        DragonPang = (
            core.SummonSkill(
                name="드래곤 팡",
                summondelay=0,
                delay=(1650 * 7 + 3000) / 7,  # 평균으로 계산, 필요해지면 공격 간격 정확히 반영
                damage=85 + 50 + 40 + passive_level,
                hit=4 * 3,  # 구체 3개 유지 가정
                remain=9999999,
            )
            .setV(vEhc, 0, 2)
            .wrap(core.SummonSkillWrapper)
        )

        RemainIncense, UseRemainIncense = remain_incense(vEhc, passive_level)
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
            delay=5010,
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
                delay=960,  # base delay 960, AS not applied
                damage=320,
                hit=6 * 3,
                cooltime=30000,
                modifier=BREATH_SHOOTER_BOSSKILLER + BREATH_SHOOTER_REINFORCE,
            )
            .setV(vEhc, 0, 2)
            .wrap(core.DamageSkillWrapper)
        )
        SneakySniping = (
            core.DamageSkill(
                name="스니키 스나이핑",
                delay=420 + 270,  # prepare.action + keydownend.action, need more check
                damage=150,
                hit=10 * 5,  # 10타, 5회 반복
                cooltime=45000,
            )
            .setV(vEhc, 0, 2)
            .wrap(core.DamageSkillWrapper)
        )
        SneakySnipingRelease = (
            core.DamageSkill(
                name="[발현/처형] 스니키 스나이핑",
                delay=420 + 270,  # prepare.time + keydownend.action
                damage=190,
                hit=12 * 5,  # 12타, 5회 반복
                cooltime=60000,
            )
            .setV(vEhc, 0, 2)
            .wrap(core.DamageSkillWrapper)
        )

        # V skills
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
            ThanatosDescentHand,
            ThanatosDescentFinish,
            UseThanatosDescentHand,
            ThanatosDescentStack,
        ) = thanatos_descent(vEhc)
        GrapOfAgony = GrapOfAgonyWrapper(vEhc, 0, 0)

        ######   Skill Wrapper   ######
        # Malice
        MaliceTick.onAfter(
            core.OptionalElement(
                ThanatosDescent.is_active,
                Malice.stackController(20),
                Malice.stackController(10),
            )
        )
        AddMalice = core.OptionalElement(
            ThanatosDescent.is_active,
            Malice.stackController(25),
            Malice.stackController(17),
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
        for sk in [
            StrikeArrowRelease,
            ScatteringShotRelease,
            ShaftBreakReleaseExplode,
            FallingDustRelease,
            SneakySnipingRelease,
            DragonBurstReleaseTick,
            ThanatosDescentHand,
            ThanatosDescentFinish,
        ]:
            sk.onJustAfter(UseRemainIncense)
        GrapOfAgony.onTick(UseRemainIncense)

        # Death Blessing
        AddDeathBlessingStack = DeathBlessingStack.stackController(1)
        for sk in [
            StrikeArrowRelease,
            ScatteringShotRelease,
            ShaftBreakReleaseExplode,
            FallingDustRelease,
            SneakySnipingRelease,
            DragonBurstReleaseTick,
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

        # Thanatos Descent
        RemainIncense.register_thanatos(ThanatosDescent)

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
            sk.onJustAfter(UseThanatosDescentHand)

        # Grap of Agony
        AddAgony = GrapOfAgony.stackController(1)
        for sk in counted_skills:
            sk.onJustAfter(AddAgony)

        # Scheduling
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

        GrapOfAgony.vary(15 * 12)  # start with full stack
        StrikeArrowRelease.protect_from_running()

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
            + [ThanatosDescentFinish]  # reserved task, use as early as possible
            + [Pantheon]
            + [
                DragonBurstReleaseInit,
                SneakySnipingRelease,
                FallingDustRelease,
                ShaftBreakRelease,
                ScatteringShotRelease,
                StrikeArrowRelease,
            ]
            + [FatalBlitzInit, ChainSickle, PoisonNeedle, TearingKnife, PhantomBlade]
            + [ChasingShot, SneakySniping, FallingDust, ShaftBreak, ScatteringShot]
            + [
                RemainIncense,
                DeathBlessingBonus,
                PoisonNeedleDOT,
                ThanatosDescentHand,
            ]  # Not used from scheduler
            + [BasicAttack],
        )
