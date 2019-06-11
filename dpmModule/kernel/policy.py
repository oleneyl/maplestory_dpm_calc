import random
from collections import defaultdict
from .abstract import AbstractScenarioGraph, AbstractScheduler
from .core import CharacterModifier
from .core import BuffSkillWrapper, DamageSkillWrapper, SummonSkillWrapper

class StorageLinkedGraph(AbstractScenarioGraph):
    def __init__(self, base_element, all_elements, storage, accessible_elements = [] ) :
        self.base_element = base_element
        self.storage = storage
        self._all_elements = all_elements
        self.accessible_elements = accessible_elements
        self._element_map = {}
        self._task_map = {}
        self._tick_task_map = {}
        for el in accessible_elements:
            name = el._id
            if name in self._element_map:
                raise KeyError(f'''Given Graph element {name} was duplicated, cannot create unique mapping.
                Check yor graph configuration have graph element that has assigned as same name. This error
                maight be solved becuase you may contaminate storage system with overriding.
                ''')
            else:
                self._element_map[name] = el
    
    def build(self, chtr):
        rem = chtr.buff_rem
        red = chtr.cooltimeReduce
        
        self._rem = rem
        self._red = red

        for name, wrp in self._element_map.items():
            self._task_map[name] = wrp.build_task(rem = rem, red = red)
            if hasattr(wrp, 'build_periodic_task'):
                self._tick_task_map[name] = wrp.build_periodic_task()

    def spend_time(self, t):
        for _, wrp in self._element_map.items():
            wrp.spend_time(t)

    def get_element(self, name):
        if name in self._element_map:
            return self._element_map[name]
        else:
            raise KeyError(f'''No element name {name} exist. Check your graph configuration, or
            check with graph.get_storage()''')

    def get_tick_task(self):
        return {n:[self._element_map[n], self._tick_task_map[n]] for n in self._tick_task_map}

    def get_all(self):
        return self.accessible_elements

    def get_element_and_task(self):
        ret_dict = {}
        for name in self._element_map:
            ret_dict[name] = [self._element_map[name], self._task_map[name]]
        return ret_dict

    def get_storage(self):
        return self.storage

    def export_task(self, common_args = {}, tick_args = {}):
        self._task_map = {k:self._all_elements[k].build_task(**common_args) for k in self._element_map}
        self._tick_task_map = {k:self._all_elements[k].build_periodic_task(**tick_args)
                 for k in self._element_map if hasattr(self._element_map[k], 'is_periodic') and getattr(self._element_map[k], 'is_periodic')}

    def set_v_enhancer(self, vEhc):
        self._vEhc = vEhc

    def filter_elements(self, ftr):
        return list(filter(ftr, self.get_all()))

    def get_default_buff_modifier(self):
        mdf = CharacterModifier()
        for wrp in self.filter_elements(lambda x:isinstance(x, BuffSkillWrapper)):
            if wrp.skill.cooltime == 0:
                mdf = mdf + wrp.skill.get_modifier()
        return mdf

    def get_task_from_element(self, element):
        return self._task_map[element._id]

class AdvancedGraphScheduler(AbstractScheduler):
    def __init__(self, graph, fetching_policy, rules):
        super(AdvancedGraphScheduler, self).__init__(graph)
        self.fetching_policy = fetching_policy(graph)
        self.rules = rules
        self._rule_map = defaultdict(list)
    
    def dequeue(self):
        for avail in self.fetching_policy.fetch_targets():
            failed = False
            for rule in self._rule_map[avail._id]:
                if not rule.check(avail, self.graph):
                    failed = True
                    break
            if not failed:
                #print(self.totalTimeLeft, avail._id)
                return self.graph.get_task_from_element(avail)

    def get_delayed_task(self):  
        for _, (wrp, tick) in self.graph.get_tick_task().items():
            if hasattr(wrp, 'need_count'):
                if wrp.need_count():
                    return tick
        return None

    def initialize(self, time):
        self.total_time_left = time
        self.total_time_initial = time
        
        self._buffMdfPreCalc = CharacterModifier()
        self._buffMdfCalcZip = []
        
        ## For faster calculation, we will pre- calculate invariant buff skills.
        for __, (buffwrp, _) in self.graph.get_element_and_task().items():
            if isinstance(buffwrp, BuffSkillWrapper):
                if buffwrp.skill.cooltime == 0 and buffwrp.modifierInvariantFlag:
                    #print(buffwrp.skill.name)  #캐싱되는 버프를 확인하기 위해 이 주석부분을 활성화 합니다.
                    self._buffMdfPreCalc = self._buffMdfPreCalc + buffwrp.get_modifier_forced()
                    st = False
                else:
                    st = True
                self._buffMdfCalcZip.append([buffwrp, st])

        for rule in self.rules:
            for wrp in rule.get_related_elements(self.graph):
                self._rule_map[wrp._id].append(rule)

    def get_buff_modifier(self):
        '''
        mdf = CharacterModifier()
        for buffwrp, _ in self.graph.buff:
            if buffwrp.onoff:
                mdf += buffwrp.get_modifier()
        return mdf
        '''
        mdf = self._buffMdfPreCalc.copy()   #BuffModifier는 쿨타임이 없는 버프에 한해 캐싱하여 연산량을 감소시킵니다. 캐싱된 
        for buffwrp, st in self._buffMdfCalcZip:
            if st: 
                mdf += buffwrp.get_modifier()
                #print(buffwrp.skill.name, buffwrp.is_active(), buffwrp.get_modifier().pdamage_indep)
        return mdf

class FetchingPolicy():
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, graph):
        self.target = graph.get_all()
        return self

    def fetch_targets(self):
        return filter(lambda x:x.is_usable(), self.get_sorted())

    def get_sorted(self):
        raise NotImplementedError('''
        Describle how to rearrange element's priority.
        You can also purpose some FILTERING in this actions, but
        it must be careful becuase following rules cannot notice filtered 
        elements had been existed in graph.''')


class TypebaseFetchingPolicy(FetchingPolicy):
    def __init__(self, priority_list = [0,1,2,3]):
        super(TypebaseFetchingPolicy, self).__init__()
        self.priority_list = priority_list

    def __call__(self, graph):
        super(TypebaseFetchingPolicy, self).__call__(graph)
        self.sorted = []
        for clstype in self.priority_list:
            self.sorted += (list(filter(lambda x:isinstance(x,clstype), self.target)))
        self.sorted.pop(self.sorted.index(graph.base_element))
        self.sorted.append(graph.base_element)
        return self
    
    def get_sorted(self):
        return [i for i in self.sorted]
    


class AbstractRule():
    '''Rule defines given element will be aceepted or not. This concept is somewhat simmillar with Constraint,
    but rule can constraint element 'Dynamically', which means can refer every context in judging point.
    '''
    def get_related_elements(self, reference_graph):
        raise NotImplementedError('''get_related_elements(reference_graph) will return which elements are 
        using this rule. Return : elements(list), will be hashed by unique namespace from storage.
        ''')

    def check(self, caller, reference_graph, context = None):
        raise NotImplementedError('''check(referce_graph) will return current context / graph satisfy
        given rule or not. context not offered yet, but for future work it is given.
        ''')

    def compile(self, reference_graph):
        '''compile() is cache hint for fast running. You can get reference elements earlier, and store 
        them as object instance, and refer those elements in runtime's check() calling. Overiding this
        method is not mandatory; you can skip this method(will not raise any error)
        '''
        return