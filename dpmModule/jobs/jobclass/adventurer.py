from ...kernel import core
from functools import partial
import random

# 모험가 및 모험가 직업 공용 5차스킬 통합코드


class InfinityWrapper(core.BuffSkillWrapper):
    def __init__(self, combat, interval=7):
        skill = core.BuffSkill(
            name="인피니티",
            delay=600,
            remain=(40 + combat) * 1000,
            cooltime=180 * 1000,
            rem=True,
            red=True,
        )
        super(InfinityWrapper, self).__init__(skill)
        self.passedTime = 0
        self.interval = interval
        self.combat = combat

    def spend_time(self, time):
        if self.is_active():
            self.passedTime += time
        super(InfinityWrapper, self).spend_time(time)

    def get_modifier(self):
        if self.is_active():
            return core.CharacterModifier(
                pdamage_indep=(
                    70 + self.combat + 3 * (self.passedTime // (self.interval * 1000))
                )
            )
        else:
            return core.CharacterModifier()

    def _use(self, skill_modifier):
        self.passedTime = 0
        return super(InfinityWrapper, self)._use(skill_modifier)


class UnstableMemorizeWrapper(core.DamageSkillWrapper):
    def __init__(
        self,
        vEhc: core.BasicVEnhancer,
        num1: int,
        num2: int,
        skill_modifier: core.SkillModifier,
    ):
        skill = core.DamageSkill(
            name="언스테이블 메모라이즈",
            delay=870,
            damage=0,
            hit=0,
            cooltime=(15 - vEhc.getV(num1, num2) // 5) * 1000,
            red=True,
        ).isV(vEhc, num1, num2)
        super(UnstableMemorizeWrapper, self).__init__(skill)
        self.skill_modifier = skill_modifier
        self.weight_total = 0
        self.weights = {}
        self.stacks = {}
        self.skills = {}

    def _indirect_use(
        self, skill: core.AbstractSkillWrapper, skill_modifier: core.SkillModifier
    ):
        """
        스킬의 쿨타임, 사용가능 여부가 변하지 않도록 바꿔치기 합니다.
        TODO: 위험한 방식이기 때문에, side-effect에 위험하지 않은 방식으로 변경해야 합니다.
        """
        cooltimeLeft = skill.cooltimeLeft
        result = skill._use(skill_modifier)
        skill.cooltimeLeft = cooltimeLeft
        return result

    def add_skill(self, skill: core.AbstractSkillWrapper, weight: int):
        self.weight_total += weight
        self.weights[skill._id] = weight
        self.stacks[skill._id] = 0
        self.skills[skill._id] = skill

    def _use(self, skill_modifier):
        result = super(UnstableMemorizeWrapper, self)._use(skill_modifier)

        for k in self.stacks:
            self.stacks[k] += self.weights[k]

        nextId = random.choices(list(self.weights.keys()), weights=list(self.weights.values()), k=1)[0]
        # nextId = sorted(self.stacks.items(), key=lambda x: x[1], reverse=True)[0][0]
        # self.stacks[nextId] -= self.weight_total

        skill = self.skills[nextId]
        task = core.Task(skill, partial(self._indirect_use, skill, self.skill_modifier))
        skill.sync(task, self.skill_modifier)

        result.cascade = [task]

        return result


def UnstableMemorizePassiveWrapper(vEhc, num1, num2):
    UnstableMemorizePassive = core.InformedCharacterModifier(
        "언스테이블 메모라이즈(패시브)", stat_main=vEhc.getV(num1, num2)
    )
    return UnstableMemorizePassive


# 이하 모든 코드 테스트 필요


def PirateFlagWrapper(vEhc, num1, num2, level):
    PirateFlag = (
        core.BuffSkill(
            name="파이렛 플래그",
            delay=990,
            remain=30 * 1000,
            cooltime=(60 - vEhc.getV(num1, num2)) * 1000,
            armor_ignore=int(10 + 0.5 * vEhc.getV(num1, num2)),
            stat_main=(level * 5 + 18) * 0.01 * int(10 + 0.5 * vEhc.getV(num1, num2)),
        )
        .isV(vEhc, num1, num2)
        .wrap(core.BuffSkillWrapper)
    )
    return PirateFlag


# 작성중, 2초 후 폭발 가정
def BlitzShieldWrappers(vEhc, num1, num2):
    # 딜레이 추가 필요
    BlitzShieldDummy = core.BuffSkill(
        name="블리츠 실드 (더미)",
        delay=600,
        remain=2000,
        cooltime=15000,
    ).wrap(core.BuffSkillWrapper)
    BlitzShield = core.DamageSkill(
        name="블리츠 실드",
        delay=2000,
        damage=vEhc.getV(num1, num2) * 20 + 500,
        hit=5,
    ).wrap(core.DamageSkillWrapper)
    BlitzShieldDummy.onAfter(BlitzShield)
    return BlitzShieldDummy, BlitzShield


def EvolveWrapper(
    vEhc,
    num1: int,
    num2: int,
    bird: core.SummonSkillWrapper,
    modifier: core.CharacterModifier = core.CharacterModifier(),
):
    Evolve = (
        core.SummonSkill(
            name="이볼브",
            summondelay=600,
            delay=3330,
            damage=450 + vEhc.getV(num1, num2) * 15,
            hit=7,
            remain=40 * 1000,
            cooltime=(120 - vEhc.getV(num1, num2) // 2) * 1000,
            red=True,
            modifier=modifier,
        )
        .isV(vEhc, num1, num2)
        .wrap(core.SummonSkillWrapper)
    )
    Evolve.onAfter(bird.controller(1))
    Evolve.onConstraint(
        core.ConstraintElement(bird._id + " 있을때 사용 가능", bird, bird.is_active)
    )
    bird.onConstraint(
        core.ConstraintElement("이볼브 지속중 사용 금지", Evolve, Evolve.is_not_active)
    )
    return Evolve
