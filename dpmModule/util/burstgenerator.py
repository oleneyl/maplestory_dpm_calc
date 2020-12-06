import dpmModule.jobs as maplejobs
from dpmModule.character.characterKernel import ItemedCharacter, JobGenerator
from dpmModule.execution import rules
from dpmModule.kernel import policy
from dpmModule.status.ability import Ability_grade

from ..kernel import core


class BurstGenerator:
    def __init__(self, job, template):
        self.job = job
        self.template = template
        self.supplier = maplejobs.jobMap[job]
        self.runtime = 1800 * 1000

    def set_runtime(self, time):
        self.runtime = time

    def burst_10sec(
        self,
        ulevel=8000,
        weaponstat=[4, 9],
        cdr=0,
        options={},
        printFlag=False,
        statistics=False,
    ):
        target: ItemedCharacter = self.template(maplejobs.weaponList[self.job], cdr)
        gen: JobGenerator = self.supplier.JobGenerator()
        v_builder = core.AlwaysMaximumVBuilder()
        graph = gen.package(
            target,
            v_builder,
            options=options,
            ulevel=ulevel,
            weaponstat=weaponstat,
            ability_grade=Ability_grade(4, 1),
        )
        sche = policy.AdvancedGraphScheduler(
            graph,
            policy.ListedFetchingPolicy(skill_ids=gen.get_skill_rotation_10sec(graph)),
            [rules.UniquenessRule()],
        )
        analytics = core.StatAnalytics(printFlag=printFlag)
        if printFlag:
            print(target.get_modifier())
        control = core.Simulator(sche, target, analytics)
        control.start_simulation(self.runtime)
        if statistics:
            control.analytics.statistics()
        return analytics.get_peak(10000)
