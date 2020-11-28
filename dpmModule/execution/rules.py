from dpmModule.kernel.policy import AbstractRule
from collections import defaultdict
from dpmModule.kernel.core import BuffSkillWrapper, DamageSkillWrapper, SummonSkillWrapper

class ConditionRule(AbstractRule):
    '''
    두 GraphElement A,B와 check_function에 대해, check_function(B)가 True를 리턴하면 A를 사용.      
    '''
    def __init__(self, state_element, checking_element, check_function):
        self._state_element_name = state_element
        self._checking_element_name = checking_element
        self._check_function = check_function

    def get_related_elements(self, reference_graph):
        return [reference_graph.get_element(self._state_element_name)]

    def check(self, caller, reference_graph, context = None):
        return self._check_function(reference_graph.get_element(self._checking_element_name))

class UniquenessRule(AbstractRule):
    '''
    주어진 Element가 on 상태가 아니면 사용을 금지합니다. 이 Rule이 없다면, 버프나 소환수가 이미 켜져 있더라도, 계속 사용합니다.
    '''
    def get_related_elements(self, reference_graph):
        return reference_graph.filter_elements(lambda x:isinstance(x, BuffSkillWrapper)) +\
            reference_graph.filter_elements(lambda x:isinstance(x, SummonSkillWrapper))

    def check(self, caller, reference_graph, context = None):
        if caller.uniqueFlag:
            return not caller.is_active()
        else:
            return True

class ConcurrentRunRule(AbstractRule):
    '''
    두 GraphElement A,B에 대해, A가 B를 사용중일 때만 사용하도록 강제합니다.
    '''
    def __init__(self, state_element, checking_element):
        self._state_element_name = state_element
        self._checking_element_name = checking_element

    def get_related_elements(self, reference_graph):
        return [reference_graph.get_element(self._state_element_name)]

    def check(self, caller, reference_graph, context = None):
        return reference_graph.get_element(self._checking_element_name).is_active()

class ReservationRule(AbstractRule):
    '''
    두 GraphElement A,B에 대해, A가 B가 사용가능할 때만 사용하도록 강제합니다.
    '''
    def __init__(self, state_element, checking_element):
        self._state_element_name = state_element
        self._checking_element_name = checking_element

    def get_related_elements(self, reference_graph):
        return [reference_graph.get_element(self._state_element_name)]

    def check(self, caller, reference_graph, context = None):
        return reference_graph.get_element(self._checking_element_name).is_usable()

class SynchronizeRule(AbstractRule):
    '''
    B가 켜져있다면, B(버프 또는 소환수) 의 남은 시간이 `time(ms)` 이상(`direction`=1) / 이하(`direction`=-1) 일 때 A를 사용할 수 있습니다.

    B가 꺼져있다면, A를 사용할 수 있습니다.
    '''
    def __init__(self, target_element, timer_element, time, direction = 1):
        self._target_element = target_element
        self._timer_element = timer_element
        self.time = time
        self.direction = direction

    def get_related_elements(self, reference_graph):
        return [reference_graph.get_element(self._target_element)]

    def check(self, caller, reference_graph, context = None):
        timer = reference_graph.get_element(self._timer_element)
        if not timer.is_not_active():
            if not timer.is_time_left(self.time, self.direction):
                if not timer.is_time_left(caller.skill.cooltime, 1):
                    return False
        return True

class MutualRule(AbstractRule):
    '''
    A를 B가 사용 가능할 때는 사용하지 않도록 합니다.
    '''
    def __init__(self, target_element, state_element):
        self._target_element_name = target_element
        self._state_element_name = state_element

    def get_related_elements(self, reference_graph):
        return [reference_graph.get_element(self._target_element_name)]

    def check(self, caller, reference_graph, context = None):
        if not reference_graph.get_element(self._state_element_name).is_usable():
            return True
        return False

class InactiveRule(AbstractRule):
    '''
    A를 B가 사용되고 있을 때는 사용하지 않도록 합니다.
    '''
    def __init__(self, target_element, state_element):
        self._target_element_name = target_element
        self._state_element_name = state_element

    def get_related_elements(self, reference_graph):
        return [reference_graph.get_element(self._target_element_name)]

    def check(self, caller, reference_graph, context = None):
        return reference_graph.get_element(self._state_element_name).is_not_active()


class DisableRule(AbstractRule):
    '''
    주어진 GraphElement를 사용하지 못하도록 합니다.
    '''
    def __init__(self, target_element):
        self.target_element = target_element

    def get_related_elements(self, reference_graph):
        return [reference_graph.get_element(self.target_element)]
    
    def check(self, caller, reference_graph, context = None):
        return False

class RuleSet(defaultdict):
    def __init__(self):
        super(RuleSet, self).__init__(list)
    BASE = 'RuleSet.BASE'
    DENSE = 'RuleSet.DENSE'
    OPTIMISTIC = 'RuleSet.OPTIMISTIC'
    PESSIMISTIC = 'RuleSet.PESSIMISTIC'
    CONFIDENT = 'RuleSet.CONFIDENT'
    def add_rule(self, rule, tag):
        self[tag].append(rule)
        return True

    def get_rules(self, tag):
        return list(self[tag])