from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple, Union

from ..graph import AbstractDynamicVariableInstance
from .modifier import CharacterModifier
from .result_object import ResultObject

if TYPE_CHECKING:
    from ..abstract import AbstractVEnhancer
    from .callback import Callback
    from .modifier import SkillModifier


class Task:
    def __init__(self, ref: GraphElement, ftn: Callable[[Any], ResultObject]) -> None:
        self._ref: GraphElement = ref
        self._ftn: Callable[[Any], ResultObject] = ftn
        self._after: List[Task] = []
        self._before: List[Task] = []
        self._justAfter: List[Task] = []

    def __repr__(self) -> str:
        return f'''Task Object from [{self._ref._id}]'''

    def getRef(self) -> GraphElement:
        return self._ref

    def do(self, **kwargs) -> ResultObject:
        return self._ftn()

    def onAfter(self, afters: List[Task]) -> None:
        self._after += afters

    def onBefore(self, befores: List[Task]) -> None:
        self._before += befores

    def onJustAfter(self, jafters: List[Task]) -> None:
        self._justAfter += jafters

    def copy(self) -> Task:
        retTask = Task(self._ref, self._ftn)
        retTask.onAfter(self._after)
        retTask.onBefore(self._before)
        retTask.onJustAfter(self._justAfter)
        return retTask


class ContextReferringTask(Task):
    def do(self, **kwargs) -> ResultObject:
        return self._ftn(**kwargs)


class GraphElement:
    """Manage time dependent feature of each execution
    """

    Flag_Skill: int = 1
    Flag_BaseSkill: int = 2
    Flag_BuffSkill: int = 4
    Flag_DamageSkill: int = 8
    Flag_SummonSkill: int = 16
    Flag_Optional: int = 32
    Flag_Repeat: int = 64
    Flag_Constraint: int = 128

    def __init__(self, _id: Union[str, AbstractDynamicVariableInstance]) -> None:
        """
        Initialzie Graph Element.

        Parameters
        ----------
        _id : str or AbstractDynamicVariableInstance
            해당 GraphElement가 부여받게 될 identifier입니다. unique할 필요는 없습니다.

        """
        if isinstance(_id, AbstractDynamicVariableInstance):
            _id = _id.evaluate()
        self._id: str = _id
        # Tasks that must be executed before this el.
        self._before: List[GraphElement] = []
        # Tasks that must be executed after this el.
        self._after: List[GraphElement] = []
        self._justAfter: List[GraphElement] = []
        self._registered_callback_presets: List[Tuple[str, Tuple[GraphElement, float]]] = []

        self._result_object_cache: ResultObject = ResultObject(0, CharacterModifier(), 0, 0, sname='Graph Element', spec='graph control')
        self._flag: int = 0

    def set_flag(self, flag: int) -> None:
        self._flag |= flag

    # TODO: Not used method.
    def toggle_flag(self, flag: int) -> None:
        self._flag ^= flag

    # TODO: Not used method.
    def remove_flag(self, flag: int) -> None:
        self._flag &= ~flag

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        """
        주어진 Element가 상호작용하는 다른 Element들을 가져옵니다.

        Returns
        -------
        list of [self, GraphElement, link_type(string)]
        """
        li = []
        for el in self._before:
            li.append((self, el, "before"))
        for el in self._after:
            li.append((self, el, "after"))
        for el in self._justAfter:
            li.append((self, el, "after"))
        for _, context in self._registered_callback_presets:
            li.append((self, context[0], "callback"))
        return li

    def get_explanation(self, lang: str = "ko") -> str:
        """
        해당 그래프 요소에 대한 설명을 받아옵니다.

        이 함수는 상속 과정에서 재정의 되는 것이 좋습니다.

        Parameters
        ----------
        lang
            Language type. Korean : ko, English : en.

        Returns
        -------
        string
        """
        if lang == "ko":
            return "종류:그래프 요소"
        elif lang == "en":
            return "Type:graph Element"

    def _use(self) -> ResultObject:
        """
        해당 그래프 요소를 작동시키고자 할 때 수행해야 하는 작업을 정의합니다.

        이 함수는 상속 과정에서 반드시 재정의되어야 합니다.

        Returns
        -------
        ResultObject
            해당 그래프 요소가 작동하고 난 후의 결과물
        """
        return self._result_object_cache

    def build_task(self, skill_modifier: SkillModifier, **kwargs) -> Task:
        """
        그래프 요소의 실행을 정의하는 Task를 반환합니다.


        Parameters
        ----------
        skill_modifier: SkillModifier

        Returns
        -------
        Task
        """
        task = Task(self, self._use)
        self.sync(task, skill_modifier)
        return task

    def spend_time(self, time: float) -> None:
        """
        시간이 흘렀을 때의 행동을 정의합니다.
        이 함수는 ``Simulator`` 에 의해서 전체 ``GraphElement`` 들이 일괄적으로 처리될 때 호출됩니다.

        Parameters
        ----------
        time : float
            지나간 시간입니다.
        """
        return

    def onAfter(self, el: GraphElement) -> None:
        """
        해당 그래프 요소가 실행된 후에 el 요소를 실행하도록 합니다.
        만약 ``onAfter`` 를 통해 chaining된 GraphElement는 해당 그래프 요소가 실행되었다면, 어떠한 경우에 있어서도 chaining됩니다.

        onAfter메서드가 두 번 호출되었다면, 먼저 호출에 포함된 인자가 우선 수행됩니다.

        Parameters
        ----------
        el : GraphElement
            다음에 실행되어야 할 ``GraphElement``
        """
        self._after = [el] + self._after

    def onAfters(self, ellist: List[GraphElement]) -> None:
        self._after += ellist

    def onBefore(self, el: GraphElement) -> None:
        """
        해당 그래프 요소가 실행된 후에 el 요소를 실행하도록 합니다.
        만약 ``onBefore`` 를 통해 chaining된 GraphElement는 해당 그래프 요소가 실행되었다면, 어떠한 경우에 있어서도 chaining됩니다.

        onAfter메서드가 두 번 호출되었다면, 먼저 호출에 포함된 인자가 나중에 수행됩니다.

        Parameters
        ----------
        el : GraphElement
            이전에 실행되어야 할 ``GraphElement``
        """
        self._before += [el]

    def onBefores(self, ellist: List[GraphElement]) -> None:
        self._before += ellist

    def sync(self, task: Task, skill_modifier: SkillModifier) -> None:
        """
        주어진 ``el`` 가 자신과 연결된 다른 ``GraphElement`` 와 동일한 연결 구조를 가지도록 합니다.

        Parameters
        ----------
        task : Task
        skill_modifier : SkillModifier
        """
        task.onBefore([el.build_task(skill_modifier) for el in self._before])
        task.onAfter([el.build_task(skill_modifier) for el in self._after])
        task.onJustAfter([el.build_task(skill_modifier)
                          for el in self._justAfter])

    def onJustAfter(self, el: GraphElement) -> None:
        self._justAfter = [el] + self._justAfter

    def onJustAfters(self, ellist: List[GraphElement]) -> None:
        self._justAfter += ellist

    def ignore(self) -> None:
        return None

    # TODO: Not used method.
    def ensure_condition(self, cond: Callable[[], bool]) -> Optional[GraphElement]:
        if cond():
            return self
        else:
            return None

    def ensure(self, ehc: AbstractVEnhancer, index_1: int, index_2: int) -> Optional[GraphElement]:
        """주어진 ``ehc`` 의 코어 강화가 존재하지 않는다면, ``None`` 을 반환하여 실행되지 못하도록 막습니다.

        Parameters
        ----------
        ehc: AbstractVEnhancer
        index_1 : int
            ``ehc`` 가 첫번째 인자로 받게 될 index
        index_2 : int
            ``ehc`` 가 두번째 인자로 받게 될 index

        """
        if ehc.getV(index_1, index_2) > 0:
            return self
        else:
            return None

    def create_callbacks(self, **kwargs) -> List[Callback]:
        raise NotImplementedError


class TaskHolder(GraphElement):
    """This class only holds given task(Does not modify any property of task).
    주어진 Task를 수행하는 ``GraphElement`` 입니다. 단순히 ``Task`` 를 감싸기 위한 용도로 사용합니다.
    """

    def __init__(self, task: Task, name: str = None) -> None:
        if name is None:
            name = "연결"
        super(TaskHolder, self).__init__(name)
        self._taskholder: Task = task

    def get_explanation(self, lang: str = "ko") -> str:
        if lang == "ko":
            return "%s" % self._id
        elif lang == "en":
            return "type:task holder\nname:%s" % self._id

    def build_task(self, skill_modifier: SkillModifier, **kwargs) -> Task:
        task = self._taskholder.copy()
        self.sync(task, skill_modifier)
        return task

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        li = super(TaskHolder, self).get_link()
        li.append((self, self._taskholder.getRef(), "effect"))
        return li


def create_task(task_name: str, task_function: Callable[[Any], ResultObject], task_ref: GraphElement) -> TaskHolder:
    return TaskHolder(Task(task_ref, task_function), task_name)


class OptionalTask(Task):
    def __init__(self, ref, discriminator: Callable[[], bool], task: Task, failtask: Task = None, name: str = 'optionalTask') -> None:
        super(OptionalTask, self).__init__(ref, None)
        self._discriminator: Callable[[], bool] = discriminator
        self._result: Task = task
        self._name: str = name
        self._failtask = failtask  # TODO: Not used attribute.
        self._result_object_cache: ResultObject = ResultObject(0, CharacterModifier(), 0, 0, sname=self._name, spec='graph control', cascade=[self._result])
        self._fail: ResultObject
        if failtask is None:
            self._fail = ResultObject(0, CharacterModifier(), 0, 0, sname=self._name + " fail", spec='graph control')
        else:
            self._fail = ResultObject(0, CharacterModifier(), 0, 0, sname=self._name, spec='graph control', cascade=[failtask])

    def do(self, **kwargs) -> ResultObject:
        if self._discriminator():
            return self._result_object_cache
        else:
            return self._fail


class OptionalElement(GraphElement):
    """조건에 따라서, 다른 Task를 수행하는 ``GraphElement`` 입니다.

    Parameters
    ----------
    disc : function
        조건 판별시에 수행될 함수입니다.
    after : GraphElement
        ``disc()`` 함수 호출의 반환값이 ``True`` 일 때 실행될 ``GraphElement`` 입니다.
    fail : GraphElement(default:None)
        ``disc()`` 함수 호출의 반환값이 ``False`` 일 때 실행될 ``GraphElement`` 입니다. 값이 주어지지 않을 경우 실행되지 않습니다.
    name : string
        ``GraphElement`` 의 이름입니다. Unique할 필요는 없습니다.
    """

    def __init__(self, disc: Callable[[], bool], after: GraphElement, fail: GraphElement = None, name: str = "Optional Element") -> None:
        super(OptionalElement, self).__init__(name)
        self.disc: Callable[[], bool] = disc
        self.after: GraphElement = after
        self.fail: GraphElement = fail
        self.set_flag(self.Flag_Optional)

    def get_explanation(self, lang: str = "ko") -> str:
        if lang == "ko":
            return "종류:조건적 실행\n%s" % self._id
        elif lang == "en":
            return "type:Optional Element\nname:%s" % self._id

    def build_task(self, skill_modifier: SkillModifier, **kwargs) -> Task:
        if self.fail is None:
            fail = None
        else:
            fail = self.fail.build_task(skill_modifier)
        task = OptionalTask(self, self.disc, self.after.build_task(skill_modifier), failtask=fail, name=self._id)
        self.sync(task, skill_modifier)
        return task

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        li = super(OptionalElement, self).get_link()
        li.append((self, self.after, "if-true"))
        if self.fail is not None:
            li.append((self, self.fail, "if-false"))
        return li


class RepeatElement(GraphElement):
    """주어진 ``GraphElement`` 를 반복 시행하고 싶을 때 사용합니다.

    Parameters
    -----------
    target : GraphElement
        반복 수행할 대상
    itr : int
        반복 수행할 횟수
    """

    def __init__(self, target: GraphElement, itr: int, name: str = None) -> None:
        if name is None:
            name = "%d회 반복" % itr
        super(RepeatElement, self).__init__(name)
        self._repeat_target: GraphElement = target
        self.itr: int = itr
        for i in range(itr):
            self.onAfter(target)
        self.set_flag(self.Flag_Repeat)
        self._result_object_cache: ResultObject = ResultObject(0, CharacterModifier(), 0, 0, sname='Repeat Element', spec='graph control')

    def get_explanation(self, lang: str = "ko") -> str:
        if lang == "ko":
            return "종류:반복\n이름:%s\n반복대상:%s\n반복 횟수:%d" % (self._id, self._repeat_target._id, self.itr)
        elif lang == "en":
            return "type:Repeat Element\nname:%s\ntarget:%s\niterations:%d" % (self._id, self._repeat_target._id, self.itr)

    def _use(self) -> ResultObject:
        return self._result_object_cache

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        li = []
        li.append((self, self._repeat_target, "repeat " + str(self.itr)))
        for el in self._after:
            if el != self._repeat_target:
                li.append((self, el, "after"))
        for el in self._before:
            li.append((self, el, "before"))
        return li


class ConstraintElement(GraphElement):
    """특정 요소의 검사를 Graph로 추적하기 위해 사용되는 더미 요소 입니다.

    Parameters
    ----------
    name : str
        ``constraint`` 에 대한 설명입니다.
    ref : GraphElement
        제한조건을 파악하기 위해 참조하는 ``GraphElement`` 입니다.
    cnst : function
        조건을 검사하고자 할 때 실행되는 함수입니다. ``False``가 반환될 경우 제한합니다.
    """

    def __init__(self, name: str, ref: GraphElement, cnst: Callable[[], bool]) -> None:
        super(ConstraintElement, self).__init__(name)
        self._ref = ref
        self._ftn: Callable[[], bool] = cnst
        self.set_flag(self.Flag_Constraint)

    def get_explanation(self, lang: str = "ko") -> str:
        if lang == "ko":
            return "종류:제한\n이름:%s" % self._id
        elif lang == "en":
            return "type:Constraint Element\nname:%s" % self._id

    def check(self) -> bool:
        return self._ftn()

    def build_task(self) -> None:
        raise NotImplementedError("ConstraintElement must not builded.")

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        return [(self, self._ref, "check")]
