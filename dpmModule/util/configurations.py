from ..kernel import core

import dpmModule.jobs as maplejobs


def export_configuration(jobname):
    target = template(maplejobs.weaponList[jobname])
    supplier = maplejobs.jobMap[jobname]

    v_builder = core.AlwaysMaximumVBuilder()
    gen = supplier.JobGenerator()
    vEhc = v_builder.build_enhancer(target, gen)
    gen.vEhc = vEhc

    graph = gen.build(vEhc, target, {})

    return graph.storage.export()
