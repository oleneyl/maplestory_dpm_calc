import sys

sys.path.append('../')
import dpmModule

from dpmModule.kernel import core
from dpmModule.kernel import policy
from dpmModule.execution import rules

from dpmModule.kernel.graph import generate_graph_safely
from dpmModule.character.characterKernel import AbstractCharacter


"""
def test_callback_queue():
    queue = policy.CallbackQueue()
    queue.push_callbacks([
        policy.Callback('x', 7),
        policy.Callback('x', 3),
        policy.Callback('x', 4),
        policy.Callback('x', 5)
    ])
    
    queue.push_callbacks
    assert queue.impending_callback_time() == 3
"""

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
        result = obj.do()
        scheduler.spend_time(50)
        ref_list.append(obj._ref)

        print(f'current time {i * 50}')
        print(obj)

    # answer_list = [X, Y, Y, Y, X, Y, Y, Y, X, Y]
    answer_list = [X, Y, Y, Y, Y, X, Y, Y, Y, Y]

    for obj, ans in zip(ref_list, answer_list):
        assert ans == obj

if __name__ == '__main__':
    test_simple_scheduler()