from collections import defaultdict
from typing import List

from dpmModule.kernel.core import BuffSkillWrapper, SummonSkillWrapper, GraphElement, AbstractSkillWrapper
from dpmModule.kernel.policy import AbstractRule, NameIndexedGraph


class ConditionRule(AbstractRule):
    def __init__(self, state_element, checking_element, check_function) -> None:
        self._state_element_name = state_element
        self._checking_element_name = checking_element
        self._check_function = check_function

    def get_related_elements(self, reference_graph: NameIndexedGraph) -> List[GraphElement]:
        return [reference_graph.get_element(self._state_element_name)]

    def check(self, caller: AbstractSkillWrapper, reference_graph: NameIndexedGraph, context=None) -> bool:
        return self._check_function(reference_graph.get_element(self._checking_element_name))


class UniquenessRule(AbstractRule):
    def get_related_elements(self, reference_graph: NameIndexedGraph) -> List[GraphElement]:
        return reference_graph.filter_elements(lambda x: isinstance(x, BuffSkillWrapper)) + \
               reference_graph.filter_elements(lambda x: isinstance(x, SummonSkillWrapper))

    def check(self, caller: AbstractSkillWrapper, reference_graph: NameIndexedGraph, context=None) -> bool:
        if caller.unique_flag:
            return not caller.is_active()
        else:
            return True


class ConcurrentRunRule(AbstractRule):
    def __init__(self, state_element: str, checking_element: str):
        self._state_element_name: str = state_element
        self._checking_element_name: str = checking_element

    def get_related_elements(self, reference_graph: NameIndexedGraph) -> List[GraphElement]:
        return [reference_graph.get_element(self._state_element_name)]

    def check(self, caller: AbstractSkillWrapper, reference_graph: NameIndexedGraph, context=None) -> bool:
        return reference_graph.get_element(self._checking_element_name).is_active()


class ReservationRule(AbstractRule):
    def __init__(self, state_element: str, checking_element: str):
        self._state_element_name: str = state_element
        self._checking_element_name: str = checking_element

    def get_related_elements(self, reference_graph: NameIndexedGraph) -> List[GraphElement]:
        return [reference_graph.get_element(self._state_element_name)]

    def check(self, caller: AbstractSkillWrapper, reference_graph: NameIndexedGraph, context=None) -> bool:
        return reference_graph.get_element(self._checking_element_name).is_usable()


class SynchronizeRule(AbstractRule):
    def __init__(self, target_element: str, timer_element: str, time, direction=1):
        self._target_element = target_element
        self._timer_element = timer_element
        self.time: float = time
        self.direction: int = direction

    def get_related_elements(self, reference_graph) -> List[GraphElement]:
        return [reference_graph.get_element(self._target_element)]

    def check(self, caller: AbstractSkillWrapper, reference_graph: NameIndexedGraph, context=None) -> bool:
        timer: AbstractSkillWrapper = reference_graph.get_element(self._timer_element)
        if not timer.is_not_active():
            if not timer.is_time_left(self.time, self.direction):
                if not timer.is_time_left(caller.skill.cooltime, 1):
                    return False
        return True


class MutualRule(AbstractRule):
    def __init__(self, target_element: str, state_element: str):
        self._target_element_name: str = target_element
        self._state_element_name: str = state_element

    def get_related_elements(self, reference_graph: NameIndexedGraph) -> List[GraphElement]:
        return [reference_graph.get_element(self._target_element_name)]

    def check(self, caller: AbstractSkillWrapper, reference_graph: NameIndexedGraph, context=None) -> bool:
        if not reference_graph.get_element(self._state_element_name).is_usable():
            return True
        return False


class InactiveRule(AbstractRule):
    def __init__(self, target_element: str, state_element: str):
        self._target_element_name: str = target_element
        self._state_element_name: str = state_element

    def get_related_elements(self, reference_graph: NameIndexedGraph) -> List[GraphElement]:
        return [reference_graph.get_element(self._target_element_name)]

    def check(self, caller: AbstractSkillWrapper, reference_graph: NameIndexedGraph, context=None) -> bool:
        return reference_graph.get_element(self._state_element_name).is_not_active()


class DisableRule(AbstractRule):
    def __init__(self, target_element: str):
        self.target_element = target_element

    def get_related_elements(self, reference_graph: NameIndexedGraph):
        return [reference_graph.get_element(self.target_element)]

    def check(self, caller: AbstractSkillWrapper, reference_graph: NameIndexedGraph, context=None) -> bool:
        return False


class RuleSet(defaultdict):
    def __init__(self) -> None:
        super(RuleSet, self).__init__(list)

    BASE = 'RuleSet.BASE'
    DENSE = 'RuleSet.DENSE'
    OPTIMISTIC = 'RuleSet.OPTIMISTIC'
    PESSIMISTIC = 'RuleSet.PESSIMISTIC'
    CONFIDENT = 'RuleSet.CONFIDENT'

    def add_rule(self, rule: AbstractRule, tag: str) -> bool:
        self[tag].append(rule)
        return True

    def get_rules(self, tag: str) -> List[AbstractRule]:
        return list(self[tag])
