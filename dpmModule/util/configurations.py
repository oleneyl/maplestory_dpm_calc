from dpmModule.character.characterTemplate import get_template_generator
from ..kernel import core

import dpmModule.jobs as maplejobs



def export_configuration(jobname):
    template, _ = get_template_generator('high_standard')().query(6000)
    target = template(maplejobs.weaponList[jobname])
    supplier = maplejobs.jobMap[jobname]

    v_builder = core.AlwaysMaximumVBuilder()
    gen = supplier.JobGenerator()
    gen.vEhc = v_builder.build_enhancer(target, gen)

    graph = gen.build(target)

    return graph.storage.export()