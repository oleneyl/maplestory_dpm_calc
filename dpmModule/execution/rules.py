from dpmModule.kernel.policy import AbstractRule
from collections import defaultdict
from dpmModule.kernel.core import BuffSkillWrapper, DamageSkillWrapper, SummonSkillWrapper

class UniquenessRule(AbstractRule):
    def get_related_elements(self, reference_graph):
        return reference_graph.filter_elements(lambda x:isinstance(x, BuffSkillWrapper)) +\
            reference_graph.filter_elements(lambda x:isinstance(x, SummonSkillWrapper))

    def check(self, caller, reference_graph, context = None):
        return not caller.onoff

class ConcurrentRunRule(AbstractRule):
    def __init__(self, state_element, checking_element):
        self._state_element_name = state_element
        self._checking_element_name = checking_element

    def get_related_elements(self, reference_graph):
        return reference_graph.get_element(self._state_element_name)

    def check(self, caller, reference_graph, context = None):
        return reference_graph.get_element(self._checking_element_name).is_onoff()


class RuleSet(defaultdict):
    BASE = 'RuleSet.BASE'
    DENSE = 'RuleSet.DENSE'
    OPTIMISTIC = 'RuleSet.OPTIMISTIC'
    PESSIMISTIC = 'RuleSet.PESSIMISTIC'
    CONFIDENT = 'RuleSet.CONFIDENT'
    def add_rule(self, rule, tag):
        self[tag].append(rule)
        return True

    def get_rules(self, tags):
        rules = []
        for tag in tags:
            rules.append(self[tag])
        return list(set(rules))