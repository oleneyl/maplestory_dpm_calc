import sys

sys.path.append('../')
import dpmModule

from dpmModule.kernel import core
from dpmModule.kernel import policy
from dpmModule.execution import rules

from dpmModule.kernel.graph import generate_graph_safely
from dpmModule.character.characterKernel import AbstractCharacter


def test_callback_queue():
    queue = policy.CallbackQueue()
    queue.push_callbacks([
        policy.Callback('x', 7),
        policy.Callback('x', 3),
        policy.Callback('x', 4),
        policy.Callback('x', 5)
    ], 300)
    
    queue.push_callbacks
    assert queue.impending_callback_time(300) == 3

def test_simple_scheduler():
    def create_graph():
        X = core.DamageSkill('X', 200, 50, 5, cooltime=200).wrap(core.DamageSkillWrapper)
        Y = core.DamageSkill('Y', 200, 50, 5).wrap(core.DamageSkillWrapper)
        return Y, [X, Y]

    base_element, all_elements, collection = generate_graph_safely(create_graph)

    X, Y = all_elements

    graph = policy.StorageLinkedGraph(base_element,
        collection.get_storage(), accessible_elements=all_elements)
    graph.build(AbstractCharacter())
    
    scheduler = policy.AdvancedGraphScheduler(
        graph, 
        policy.TypebaseFetchingPolicy([core.DamageSkillWrapper]), 
        rules.RuleSet()
    )
    scheduler.initialize(1000)

    ref_list = []

    for i in range(10):
        obj = scheduler.dequeue()
        print(scheduler.get_current_time())
        result = obj.do()
        scheduler.spend_time(50)
        ref_list.append(obj._ref)

        print(f'current time {i * 50}')
        print(obj)

    answer_list = [X, Y, Y, Y, X, Y, Y, Y, X, Y] 
    # answer_list = [X, Y, Y, Y, Y, X, Y, Y, Y, Y]

    for obj, ans in zip(ref_list, answer_list):
        assert ans == obj


def test_callback_operation():
    class CallbackTestDamageSkillWrapper(core.DamageSkillWrapper):
        def _init__(self, skill):
            super(CallbackTestDamageSkillWrapper, self).__init__(skill)
            self.callback_for_result = []

        def _use(self, skill_modifier):
            result = super(CallbackTestDamageSkillWrapper, self)._use(skill_modifier)
            result.callbacks = self.callback_for_result
            return result
            
    def create_graph():
        X = core.DamageSkill('X', 200, 50, 5, cooltime=500).wrap(CallbackTestDamageSkillWrapper)
        Y = core.DamageSkill('Y', 200, 50, 5).wrap(CallbackTestDamageSkillWrapper)
        A = core.DamageSkill('A', 200, 50, 5).wrap(core.DamageSkillWrapper)
        B = core.DamageSkill('B', 200, 50, 5).wrap(core.DamageSkillWrapper)
        C = core.DamageSkill('C', 200, 50, 5).wrap(core.DamageSkillWrapper)
        X.callback_for_result = [policy.Callback.from_graph_element(A, 320), policy.Callback.from_graph_element(B, 390)]
        Y.callback_for_result = [policy.Callback.from_graph_element(C, 390)]

        return Y, [X, Y]

    base_element, all_elements, collection = generate_graph_safely(create_graph)

    X, Y = all_elements

    graph = policy.StorageLinkedGraph(base_element,
        collection.get_storage(), accessible_elements=all_elements)
    graph.build(AbstractCharacter())
    
    scheduler = policy.AdvancedGraphScheduler(
        graph, 
        policy.TypebaseFetchingPolicy([core.DamageSkillWrapper]), 
        rules.RuleSet()
    )

    analytics = core.Analytics()
    simulator = core.Simulator(scheduler, AbstractCharacter(), analytics)
    simulator.start_simulation(1500)

    answer = [(x['time'], x['sname']) for x in analytics.get_results()]
    reference = [
        (0, 'X'),
        (200, 'Y'),
        (320, 'A'),
        (390, 'B'),
        (400, 'Y'),
        (590, 'C'),
        (600, 'X'),
        (790, 'C'),
        (800, 'Y'),
        (920, 'A'),
        (990, 'B'),
        (1000, 'Y'),
        (1190, 'C'),
        (1200, 'X'),
        (1390, 'C'),
        (1400, 'Y')       
    ]
    
    for ans, ref in zip(answer, reference):
        assert ans[0] == ref[0]
        assert ans[1] == ref[1]
