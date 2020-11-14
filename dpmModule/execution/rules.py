from dpmModule.kernel.policy import AbstractRule
from collections import defaultdict
from dpmModule.kernel.core import BuffSkillWrapper, DamageSkillWrapper, SummonSkillWrapper

class ConditionRule(AbstractRule):
    def __init__(self, state_element, checking_element, check_function):
        self._state_element_name = state_element
        self._checking_element_name = checking_element
        self._check_function = check_function

    def get_related_elements(self, reference_graph):
        return [reference_graph.get_element(self._state_element_name)]

    def check(self, caller, reference_graph, context = None):
        return self._check_function(reference_graph.get_element(self._checking_element_name))

class UniquenessRule(AbstractRule):
    def get_related_elements(self, reference_graph):
        return reference_graph.filter_elements(lambda x:isinstance(x, BuffSkillWrapper)) +\
            reference_graph.filter_elements(lambda x:isinstance(x, SummonSkillWrapper))

    def check(self, caller, reference_graph, context = None):
        if caller.uniqueFlag:
            return not caller.is_active()
        else:
            return True

class ConcurrentRunRule(AbstractRule):
    def __init__(self, state_element, checking_element):
        self._state_element_name = state_element
        self._checking_element_name = checking_element

    def get_related_elements(self, reference_graph):
        return [reference_graph.get_element(self._state_element_name)]

    def check(self, caller, reference_graph, context = None):
        return reference_graph.get_element(self._checking_element_name).is_active()

class ReservationRule(AbstractRule):
    def __init__(self, state_element, checking_element):
        self._state_element_name = state_element
        self._checking_element_name = checking_element

    def get_related_elements(self, reference_graph):
        return [reference_graph.get_element(self._state_element_name)]

    def check(self, caller, reference_graph, context = None):
        return reference_graph.get_element(self._checking_element_name).is_usable()

class SynchronizeRule(AbstractRule):
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
    def __init__(self, target_element, state_element):
        self._target_element_name = target_element
        self._state_element_name = state_element

    def get_related_elements(self, reference_graph):
        return [reference_graph.get_element(self._target_element_name)]

    def check(self, caller, reference_graph, context = None):
        return reference_graph.get_element(self._state_element_name).is_not_active()


class DisableRule(AbstractRule):
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