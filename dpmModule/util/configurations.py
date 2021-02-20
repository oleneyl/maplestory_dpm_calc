from ..kernel import core
from ..character.characterTemplate import TemplateGenerator

import dpmModule.jobs as maplejobs


def export_configuration(jobname):
    if maplejobs.getKoJobName(jobname):
        supplier = maplejobs.jobMap[maplejobs.getKoJobName(jobname)]
    else:
        supplier = maplejobs.jobMap[jobname]
    gen = supplier.JobGenerator()
    target = TemplateGenerator().get_template(gen, "6000")

    v_builder = core.AlwaysMaximumVBuilder()
    vEhc = v_builder.build_enhancer(target, gen)
    gen.vEhc = vEhc

    graph = gen.build(vEhc, target, {})

    return graph.storage.export()

def export_enhancer_configuration(jobname):
    supplier = maplejobs.jobMap[jobname]
    gen = supplier.JobGenerator()
    target = TemplateGenerator().get_template(gen, "6000")

    v_builder = core.AlwaysMaximumVBuilder()
    vEhc = v_builder.build_enhancer(target, gen)
    gen.vEhc = vEhc

    graph = gen.build(vEhc, target, {})

    return vEhc
