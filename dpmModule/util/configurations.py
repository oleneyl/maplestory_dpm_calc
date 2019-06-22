import sys, os

import dpmModule as dpm
import dpmModule.character.characterTemplateHigh as template
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
from dpmModule.kernel import graph
from dpmModule.jobs import jobMap
from ..kernel import core

import dpmModule.jobs as maplejobs

import time
import argparse



def export_configuration(jobname):
    target = template.getU6000CharacterTemplate(maplejobs.weaponList[jobname])
    supplier = maplejobs.jobMap[jobname]

    v_builder = core.NjbStyleVBuilder(skill_core_level=25, each_enhanced_amount=17)
    gen = supplier.JobGenerator()
    gen.vEhc = v_builder.build_enhancer(target, gen)

    graph = gen.build(target)

    return graph.storage.export()