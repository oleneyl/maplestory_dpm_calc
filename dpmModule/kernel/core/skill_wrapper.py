from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Callable, List, Optional, Tuple

from ..graph import DynamicVariableOperation
from .callback import Callback
from .constant import NOTWANTTOEXECUTE
from .graph_element import (
    ConstraintElement,
    ContextReferringTask,
    GraphElement,
    Task,
    TaskHolder,
)
from .modifier import CharacterModifier
from .result_object import ResultObject

if TYPE_CHECKING:
    from .modifier import SkillModifier
    from .skill import AbstractSkill, BuffSkill, DamageSkill, SummonSkill, DotSkill


class AbstractSkillWrapper(GraphElement):
    """특정 스킬의 사용을 제어하는 ``GraphElement`` 입니다. 이 객체의 _use() 함수 호출은
    인게임 내에서 대응되는 스킬의 시전과 동일하게 작용합니다.

    Parameters
    ----------
    skill : AbstractSkill
        제어 대상이 되는 스킬입니다.
    """

    def __init__(self, skill: AbstractSkill, name: str = None) -> None:
        if name is None:
            super(AbstractSkillWrapper, self).__init__(skill.name)
        else:
            super(AbstractSkillWrapper, self).__init__(name)
        self.set_flag(self.Flag_Skill)
        self.skill: AbstractSkill = skill
        # indicate how much time left to use this wrapper again.
        self.cooltimeLeft: float = 0
        # indicate how much time left for continuing this wrapper.
        self.timeLeft: float = 0
        self.constraint: List[ConstraintElement] = []
        self._result_object_cache = ResultObject(
            0, CharacterModifier(), 0, 0, sname=self.skill.name, spec="graph control"
        )
        if (
            DynamicVariableOperation.reveal_argument(self.skill.cooltime)
            == NOTWANTTOEXECUTE
        ):
            self.set_disabled_and_time_left(-1)

        # Context referring
        self._refer_runtime_context: bool = False

    def enable_referring_runtime_context(self) -> None:
        """If this is true, given skill wrapper may use runtime context.
        with this option, you MUST override _use() method with **kwargs argument is enabled.
        given context may passed by **kwargs option.

        이 함수가 호출될 경우, _use() 함수의 실행 시점에서 `runtime_context`를 참조할 수 있습니다.
        """
        self._refer_runtime_context = True

    def protect_from_running(self) -> None:
        """``Scheduler`` 에 의해 이 객체가 선택되는 것을 방지합니다.
        이는 ``onAfter()`` 과 같은 chaining을 통한 실행은 막지 않습니다.
        """
        constraint = ConstraintElement("사용 금지", self, lambda: False)
        self.onConstraint(constraint)

    def get_explanation(self, lang: str = "ko") -> str:
        return self.skill.get_explanation(lang=lang)

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        li = super(AbstractSkillWrapper, self).get_link()
        for el in self.constraint:
            li.append((self, el, "constraint"))
        return li

    # TODO: Not used method.
    def assert_level_is_positive(
        self, reference_level: int
    ) -> Optional[AbstractSkillWrapper]:
        if reference_level > 0:
            return self
        else:
            return None

    # TODO: Not used method. (onConstraint만 사용됨)
    def createConstraint(
        self, const_name: str, const_ref: GraphElement, const_ftn: Callable[[], bool]
    ) -> None:
        self.onConstraint(ConstraintElement(const_name, const_ref, const_ftn))

    def onConstraint(self, constraint: ConstraintElement) -> None:
        """주어진 제한 조건을 실행 ``constraint`` 목록에 추가합니다.
        해당 제한 조건이 만족되지 않을경우, 이 ``GraphElement``는 ``Scheduler`` 에 의해 실행되지 않습니다.

        이는 ``onAfter()`` 과 같은 chaining을 통한 실행은 막지 않습니다.

        Parameters
        ----------
        constraint : ConstraintElement
        """
        self.constraint.append(constraint)

    def set_disabled(self) -> ResultObject:
        """주어진 요소를 실행 불가 상태로 만듭니다."""
        raise NotImplementedError

    def set_disabled_and_time_left(self, time: float) -> ResultObject:
        """주어진 요소를 실행 불가 상태로 만들고, ``time`` 이후에 실행가능하도록 합니다.

        Parameters
        ----------
        time : float(ms)
        """
        raise NotImplementedError

    def reduce_cooltime(self, time: float) -> ResultObject:
        """주어진 요소의 남은 ``cooltime``을  ``time`` 만큼  감소시킵니다.

        Parameters
        ----------
        time : float(ms)
        """
        self.cooltimeLeft -= time
        return self._result_object_cache

    def reduce_cooltime_p(self, p: float) -> ResultObject:
        """주어진 요소의 남은 ``cooltime``을  ``p`` 만큼 비율로  감소시킵니다.

        Parameters
        ----------
        p : float
            0에서 1 사이의 값이어야 합니다. 1일 경우 모든 쿨타임이 제거됩니다. 0일 경우 아무 일도 일어나지 않습니다.
        """
        self.cooltimeLeft -= self.cooltimeLeft * p
        return self._result_object_cache

    def controller(
        self,
        time: float,
        type_: str = "set_disabled_and_time_left",
        name: Optional[str] = None,
    ) -> TaskHolder:
        # pylint: disable=no-member
        """``AbstractSkillWrapper`` 의 시간을 제어하는 그래프 요소를 생성합니다.
        이 메서드는 ``TaskHolder`` 를 반환하므로, 반환된 요소를 다른 ``GraphElement`` 들의 ``onAfter`` 등을 통해 chaining할 수 있습니다.

        Parameters
        ----------
        time : float
            ``reduce_cooltime_p`` 인 경우 0에서 1 사이의 값, 그렇지 않을 경우 ms단위의 시간
        type_ : str
            set_disabled_and_time_left, reduce_cooltime, reduce_cooltime_p, set_enabled_and_time_left
        name : str(default:None)
            반환될 요소의 이름

        Returns
        -------
        element : TaskHolder
            실행될 경우, 해당 ``GraphElement`` 의 잔여 시간을 제어하는 ``TaskHolder``

        """
        if type_ == "set_disabled":
            _name = "사용 종료"
            task = Task(self, self.set_disabled)
        elif type_ == "set_disabled_and_time_left":
            if time == -1:
                _name = "사용 불가"
            else:
                _name = "%.1f초이후 시전" % (time * 1.0 / 1000)
            task = Task(self, partial(self.set_disabled_and_time_left, time))
        elif type_ == "reduce_cooltime":
            _name = "쿨-%.1f초" % (time * 1.0 / 1000)
            task = Task(self, partial(self.reduce_cooltime, time))
        elif type_ == "reduce_cooltime_p":
            _name = "쿨-" + str(int(time * 100)) + "%"
            task = Task(self, partial(self.reduce_cooltime_p, time))
        elif type_ == "set_enabled_and_time_left":
            _name = "%.1f초간 시전" % (time * 1.0 / 1000)
            task = Task(self, partial(self.set_enabled_and_time_left, time))
        else:
            raise TypeError("You must specify control type correctly.")
        if name is not None:
            return TaskHolder(task, name=name)
        else:
            return TaskHolder(task, name=_name)

    def _use(self, skill_modifier: SkillModifier, **kwargs) -> ResultObject:
        raise NotImplementedError

    def build_task(self, skill_modifier: SkillModifier) -> Task:
        if self._refer_runtime_context:
            task = self._build_task_with_referring_context(skill_modifier)
        else:
            task = Task(self, partial(self._use, skill_modifier))
        self.sync(task, skill_modifier)
        return task

    def _build_task_with_referring_context(
        self, skill_modifier: SkillModifier
    ) -> ContextReferringTask:
        def context_referring_function(**kwargs) -> ResultObject:  # Task가 실행시킬 함수
            return self._use(skill_modifier, **kwargs)

        return ContextReferringTask(self, context_referring_function)

    def is_usable(self) -> bool:
        """이 ``GraphElement`` 가 실행가능한지 여부를 반환합니다.
        이 과정에서 ``constraint`` 들은 검사됩니다.
        """
        if len(self.constraint) > 0:
            for cnst in self.constraint:
                if not cnst.check():
                    return False
        return self.is_available()

    def is_available(self) -> bool:
        """이 ``GraphElement`` 가 실행가능한지 여부를 반환합니다.
        이 과정에서 ``constraint`` 들은 검사되지 않습니다.
        """
        return self.cooltimeLeft <= 0

    def is_not_usable(self) -> bool:
        """이 ``GraphElement`` 가 실행 불가능한지 여부를 반환합니다.
        이 과정에서 ``constraint`` 들은 검사됩니다.
        """
        return not self.is_usable()

    def spend_time(self, time: float) -> None:
        raise NotImplementedError

    def is_active(self) -> bool:
        """이 ``GraphElement`` 가 실행되고 있는지에 대한 여부를 반환합니다.
        지속 시간이 있는 객체에 대해서만 사용합니다.
        """
        return self.timeLeft > 0

    def is_not_active(self) -> bool:
        return not self.is_active()

    def is_cooltime_left(self, time: float, direction: int) -> bool:
        """남은 쿨타임이 ``time`` 과 비교할 때의 대소를 반환합니다.

        Parameters
        ----------
        time : float
            비교 기준이 되는 시간입니다.

        direction : 1 or -1
            direction > 0 이면 ``time`` 보다 남은 ``cooltime`` 이 길 경우 True입니다.
            direction < 0 이면 ``time`` 보다 남은 ``cooltime`` 이 짧을 경우 True입니다.
        """
        if (self.cooltimeLeft - time) * direction > 0:
            return True
        else:
            return False

    def is_time_left(self, time: float, direction: int) -> bool:
        """남은 지속시간이  ``time`` 과 비교할 때의 대소를 반환합니다.

        Parameters
        ----------
        time : float
            비교 기준이 되는 시간입니다.

        direction : 1 or -1
            direction > 0 이면 ``time`` 보다 남은 지속시간이 길 경우 True입니다.
            direction < 0 이면 ``time`` 보다 남은 지속시간이 짧을 경우 True입니다.
        """
        if (self.timeLeft - time) * direction > 0:
            return True
        else:
            return False

    def calculate_cooltime(self, skill_modifier: SkillModifier) -> float:
        """``skill_modifier`` 를 바탕으로, 주어진 ``Skill`` 의 실질적 쿨타임을 계산합니다.

        Parameters
        ----------
        skill_modifier : SkillModifier
            현재 스킬을 사용하는 ``Character`` 가 제공한 ``SkillModifier`` 입니다.
        """
        if self.skill.red is False:
            return self.get_cooltime()

        cooltime = self.get_cooltime()
        pcooltime_reduce = skill_modifier.pcooltime_reduce  # 쿨감%
        cooltime_reduce = skill_modifier.cooltime_reduce  # 쿨감+ (ms)

        if cooltime * (1 - 0.01 * pcooltime_reduce) <= 1000:  # 쿨감%부터 적용, 최소 1초까지
            cd = min(cooltime, 1000)
        else:
            cd = cooltime * (1 - 0.01 * pcooltime_reduce)

        if cd - cooltime_reduce <= 10000:
            cooltime_cap = min(10000, cd)
            cdr_left = (
                cooltime_reduce - (cd - cooltime_cap)
            ) / 1000  # 10초 이하에서 쿨감되는 수치 계산
            cdr_applied = cooltime_cap * (1 - cdr_left * 0.05)  # 1초당 5%씩 감소
        else:
            cdr_applied = cd - cooltime_reduce

        # 5초까지 감소, 단 이미 스킬쿨이 5초 아래였을 경우 그대로 사용
        return max(cdr_applied, min(cd, 5000))

    def get_cooltime(self) -> float:
        return self.skill.cooltime

    def onEventElapsed(self, graph_element: GraphElement, elapsed_time: float) -> None:
        """Invoke graph_element, after elapsed elapsed_time.
        Delay may considered as elapsed_time.
        """
        self._registered_callback_presets.append(
            ("onEventElapsed", (graph_element, elapsed_time))
        )

    def onEventEnd(self, graph_element: GraphElement) -> None:
        """Invoke graph_element, after event ended.
        This only meaningful for duration-involved elements.
        """
        self._registered_callback_presets.append(("onEventEnd", (graph_element, 0)))

    def create_callbacks(self, skill_modifier: SkillModifier, duration: float = 0, **kwargs) -> List[Callback]:
        """해당 object가 _use될 때 발생시키고자 하는 콜백들을 생성합니다."""
        callbacks = []
        for preset_type, context in self._registered_callback_presets:
            if preset_type == "onEventEnd":
                assert (
                    duration > 0
                ), "duration may larger than 0 to use onEventEnd callback."
                element = context[0]
                callbacks.append(Callback.from_graph_element(element, skill_modifier, duration))
            elif preset_type == "onEventElapsed":
                element, elapsed_time = context
                callbacks.append(Callback.from_graph_element(element, skill_modifier, elapsed_time))

        return callbacks


class BuffSkillWrapper(AbstractSkillWrapper):
    def __init__(self, skill: BuffSkill, name: str = None) -> None:
        super(BuffSkillWrapper, self).__init__(skill, name=name)
        self.set_flag(self.Flag_BuffSkill)
        self.disabledModifier = CharacterModifier()
        self.modifierInvariantFlag: bool = True
        self.uniqueFlag: bool = True

    def set_enabled_and_time_left(self, time: float):
        """This function must be used carefully.. You must be sure about this skill's cooltime calculation i.e. -1"""
        self.timeLeft = time
        self.cooltimeLeft = self.skill.cooltime

        mdf = self.get_modifier()
        return ResultObject(
            0,
            mdf,
            0,
            0,
            sname=self.skill.name,
            spec=self.skill.spec,
            kwargs={"remain": time},
        )

    def set_disabled(self) -> ResultObject:
        self.timeLeft = 0
        return self._result_object_cache

    def set_disabled_and_time_left(self, time: float) -> ResultObject:
        self.timeLeft = 0
        self.cooltimeLeft = time
        if time == -1:
            self.cooltimeLeft = NOTWANTTOEXECUTE
        return self._result_object_cache

    # TODO : can make this process more faster.. maybe
    def spend_time(self, time: float) -> None:
        self.timeLeft -= time
        self.cooltimeLeft -= time

    def _use(self, skill_modifier: SkillModifier) -> ResultObject:
        self.timeLeft = self.skill.remain * (
            1 + 0.01 * skill_modifier.buff_rem * self.skill.rem
        )
        self.cooltimeLeft = self.calculate_cooltime(skill_modifier)
        delay = self.get_delay()
        callbacks = self.create_callbacks(skill_modifier=skill_modifier, duration=self.timeLeft)
        return ResultObject(
            delay,
            CharacterModifier(),
            0,
            0,
            sname=self.skill.name,
            spec=self.skill.spec,
            kwargs={
                "remain": self.skill.remain
                * (1 + 0.01 * skill_modifier.buff_rem * self.skill.rem)
            },
            callbacks=callbacks,
        )

    def get_delay(self) -> float:
        return self.skill.delay

    def get_modifier(self) -> CharacterModifier:
        if self.is_active():
            return self.skill.get_modifier()
        else:
            return self.disabledModifier

    def get_modifier_forced(self) -> CharacterModifier:
        return self.skill.get_modifier()

    def prevent_from_caching(self) -> None:
        self.modifierInvariantFlag = False


class StackSkillWrapper(BuffSkillWrapper):
    def __init__(self, skill: BuffSkill, max_: int, name: str = None) -> None:
        super(StackSkillWrapper, self).__init__(skill, name=name)
        self.stack: int = 0
        self._max: int = max_
        self._style: Optional[str] = None
        self.modifierInvariantFlag: bool = False

    def set_name_style(self, style: str) -> None:
        self._style = style

    def vary(self, d: int) -> ResultObject:
        self.stack = max(min((self.stack + d), self._max), 0)
        return ResultObject(
            0, CharacterModifier(), 0, 0, sname=self.skill.name, spec="graph control"
        )

    def set_stack(self, d: int) -> ResultObject:
        self.stack = d
        return ResultObject(
            0, CharacterModifier(), 0, 0, sname=self.skill.name, spec="graph control"
        )

    def get_modifier(self) -> CharacterModifier:
        return CharacterModifier()

    def stackController(
        self, d: int, name: str = None, dtype: str = "vary"
    ) -> TaskHolder:
        if dtype == "vary":
            task = Task(self, partial(self.vary, d))
        elif dtype == "set":
            task = Task(self, partial(self.set_stack, d))
        if self._style is not None and name is None:
            name = self._style % d
        return TaskHolder(task, name=name)

    def judge(self, stack: int, direction: int) -> bool:
        return (self.stack - stack) * direction >= 0


class DamageSkillWrapper(AbstractSkillWrapper):
    def __init__(
        self,
        skill: DamageSkill,
        modifier: CharacterModifier = CharacterModifier(),
        name: str = None,
    ):
        super(DamageSkillWrapper, self).__init__(skill, name=name)
        self.modifier: CharacterModifier = modifier
        self._runtime_modifier_list: List[
            Tuple[
                AbstractSkillWrapper,
                Callable[[AbstractSkillWrapper], CharacterModifier],
            ]
        ] = []

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        li = super(DamageSkillWrapper, self).get_link()
        for sk, _ in self._runtime_modifier_list:
            li.append((self, sk, "modifier"))
        return li

    def set_disabled_and_time_left(self, time: float) -> ResultObject:
        self.cooltimeLeft = time
        if time == -1:
            self.cooltimeLeft = NOTWANTTOEXECUTE
        return ResultObject(
            0, CharacterModifier(), 0, 0, sname=self.skill.name, spec="graph control"
        )

    def spend_time(self, time: float) -> None:
        self.cooltimeLeft -= time

    def _use(self, skill_modifier: SkillModifier) -> ResultObject:
        self.cooltimeLeft = self.calculate_cooltime(skill_modifier)
        callbacks = self.create_callbacks(skill_modifier=skill_modifier)
        return ResultObject(
            self.get_delay(),
            self.get_modifier(),
            self.get_damage(),
            self.get_hit(),
            sname=self.skill.name,
            spec=self.skill.spec,
            callbacks=callbacks,
        )

    def get_delay(self) -> float:
        return self.skill.delay

    def get_damage(self) -> float:
        return self.skill.damage

    def get_hit(self) -> float:
        return self.skill.hit

    def get_modifier(self) -> CharacterModifier:
        modifier = self.skill.get_modifier() + self.modifier
        for skill, fn in self._runtime_modifier_list:
            modifier += fn(skill)
        return modifier

    def add_runtime_modifier(
        self,
        skill: AbstractSkillWrapper,
        fn: Callable[[AbstractSkillWrapper], CharacterModifier],
    ) -> None:
        self._runtime_modifier_list.append((skill, fn))


class StackDamageSkillWrapper(DamageSkillWrapper):
    def __init__(
        self,
        skill: DamageSkill,
        stack_skill: AbstractSkillWrapper,
        fn,
        modifier: CharacterModifier = CharacterModifier(),
        name: str = None,
    ) -> None:
        super(StackDamageSkillWrapper, self).__init__(
            skill, modifier=modifier, name=name
        )
        self.stack_skill: AbstractSkillWrapper = stack_skill
        self.fn = fn

    def get_damage(self) -> float:
        stack = self.fn(self.stack_skill)
        if stack <= 0:
            return 0
        return self.skill.damage

    def get_hit(self) -> float:
        stack = self.fn(self.stack_skill)
        return self.skill.hit * stack


class StackableDamageSkillWrapper(DamageSkillWrapper):
    def __init__(self, skill: AbstractSkill, max_stack: int) -> None:
        super(StackableDamageSkillWrapper, self).__init__(skill)
        self.max_stack = max_stack
        self.stack = self.max_stack

    def spend_time(self, time: float) -> None:
        super(StackableDamageSkillWrapper, self).spend_time(time)
        if self.stack == self.max_stack:
            self.cooltimeLeft = self.skill.cooltime
        if self.cooltimeLeft <= 0:
            self.cooltimeLeft += self.skill.cooltime
            self.stack = min(self.stack + 1, self.max_stack)

    def _use(self, skill_modifier: SkillModifier) -> ResultObject:
        self.stack -= 1
        callbacks = self.create_callbacks(skill_modifier=skill_modifier)
        return ResultObject(
            self.get_delay(),
            self.get_modifier(),
            self.get_damage(),
            self.get_hit(),
            sname=self.skill.name,
            spec=self.skill.spec,
            callbacks=callbacks,
        )

    def is_available(self) -> bool:
        return self.stack > 0

    def judge(self, stack: int, direction: int) -> bool:
        return (self.stack - stack) * direction >= 0


class SummonSkillWrapper(AbstractSkillWrapper):
    def __init__(
        self,
        skill: SummonSkill,
        modifier: CharacterModifier = CharacterModifier(),
        name: str = None,
    ) -> None:
        super(SummonSkillWrapper, self).__init__(skill, name=name)
        self.tick: int = 0
        self.modifier: CharacterModifier = modifier
        self._runtime_modifier_list: List[
            Tuple[
                AbstractSkillWrapper,
                Callable[[AbstractSkillWrapper], CharacterModifier],
            ]
        ] = []
        self.disabledModifier = CharacterModifier()
        self._onTick: List[GraphElement] = []
        self.uniqueFlag: bool = True
        self.is_periodic: bool = True

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        li = super(SummonSkillWrapper, self).get_link()
        for el in self._onTick:
            li.append((self, el, "tick"))
        for sk, _ in self._runtime_modifier_list:
            li.append((self, sk, "modifier"))
        return li

    def set_disabled(self) -> ResultObject:
        self.timeLeft = 0
        self.tick = 0
        return ResultObject(
            0, CharacterModifier(), 0, 0, sname=self.skill.name, spec="graph control"
        )

    def set_disabled_and_time_left(self, time: float) -> ResultObject:
        self.cooltimeLeft = time
        self.timeLeft = -1
        self.tick = 0
        if time == -1:
            self.cooltimeLeft = NOTWANTTOEXECUTE
        return ResultObject(
            0, CharacterModifier(), 0, 0, sname=self.skill.name, spec="graph control"
        )

    def need_count(self) -> bool:
        if self.is_active() and (self.tick < 0):
            return True
        else:
            return False

    def spend_time(self, time: float) -> None:
        self.timeLeft -= time
        self.cooltimeLeft -= time
        self.tick -= time

    # _use only alloted for start.
    def _use(self, skill_modifier: SkillModifier) -> ResultObject:
        self.tick = 0
        self.timeLeft = self.skill.remain * (
            1 + 0.01 * skill_modifier.summon_rem * self.skill.rem
        )
        self.cooltimeLeft = self.calculate_cooltime(skill_modifier)
        callbacks = self.create_callbacks(skill_modifier=skill_modifier, duration=self.timeLeft)
        return ResultObject(
            self.get_summon_delay(),
            self.disabledModifier,
            0,
            0,
            sname=self.skill.name,
            spec=self.skill.spec,
            callbacks=callbacks,
        )

    def _useTick(self) -> ResultObject:
        self.tick += self.get_delay()
        return ResultObject(
            0,
            self.get_modifier(),
            self.get_damage(),
            self.get_hit(),
            sname=self.skill.name,
            spec=self.skill.spec,
        )

    def build_periodic_task(self, skill_modifier: SkillModifier) -> Task:
        task = Task(self, self._useTick)
        task.onAfter([el.build_task(skill_modifier) for el in self._onTick])
        return task

    def onTick(self, el: GraphElement) -> None:
        self._onTick.append(el)

    def onTicks(self, ellist: List[GraphElement]) -> None:
        self._onTick += ellist

    def get_summon_delay(self) -> float:
        return self.skill.summondelay

    def get_delay(self) -> float:
        return self.skill.delay

    def get_damage(self) -> float:
        return self.skill.damage

    def get_hit(self) -> float:
        return self.skill.hit

    def get_modifier(self) -> CharacterModifier:
        modifier = self.skill.get_modifier() + self.modifier
        for skill, fn in self._runtime_modifier_list:
            modifier += fn(skill)
        return modifier

    def add_runtime_modifier(
        self,
        skill: AbstractSkillWrapper,
        fn: Callable[[AbstractSkillWrapper], CharacterModifier],
    ) -> None:
        self._runtime_modifier_list.append((skill, fn))


class StackableSummonSkillWrapper(SummonSkillWrapper):
    def __init__(self, skill: AbstractSkill, max_stack: int) -> None:
        super(StackableSummonSkillWrapper, self).__init__(skill)
        self.max_stack = max_stack
        self.stack = self.max_stack

    def spend_time(self, time: float) -> None:
        super(StackableSummonSkillWrapper, self).spend_time(time)
        if self.stack == self.max_stack:
            self.cooltimeLeft = self.skill.cooltime
        if self.cooltimeLeft <= 0:
            self.cooltimeLeft += self.skill.cooltime
            self.stack = min(self.stack + 1, self.max_stack)

    def _use(self, skill_modifier: SkillModifier) -> ResultObject:
        self.tick = 0
        self.timeLeft = self.skill.remain * (
            1 + 0.01 * skill_modifier.summon_rem * self.skill.rem
        )
        self.stack -= 1
        callbacks = self.create_callbacks(skill_modifier=skill_modifier, duration=self.timeLeft)
        return ResultObject(
            self.get_summon_delay(),
            self.disabledModifier,
            0,
            0,
            sname=self.skill.name,
            spec=self.skill.spec,
            callbacks=callbacks,
        )

    def is_available(self) -> bool:
        return self.stack > 0 and self.is_not_active()

    def judge(self, stack: int, direction: int) -> bool:
        return (self.stack - stack) * direction >= 0


class DotSkillWrapper(SummonSkillWrapper):
    def __init__(
        self,
        skill: DotSkill,
        modifier: CharacterModifier = CharacterModifier(),
        name: str = None,
    ) -> None:
        super(DotSkillWrapper, self).__init__(skill, modifier, name=name)

    # _use only alloted for start.
    def _use(self, skill_modifier: SkillModifier) -> ResultObject:
        self.tick = max(self.tick, 0)
        self.timeLeft = self.skill.remain * (
            1 + 0.01 * skill_modifier.summon_rem * self.skill.rem
        )
        self.cooltimeLeft = self.calculate_cooltime(skill_modifier)
        callbacks = self.create_callbacks(skill_modifier=skill_modifier, duration=self.timeLeft)
        return ResultObject(
            self.get_summon_delay(),
            self.disabledModifier,
            0,
            0,
            sname=self.skill.name,
            spec=self.skill.spec,
            callbacks=callbacks,
        )
