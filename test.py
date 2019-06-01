import sys, os

import dpmModule as dpm
import dpmModule.character.characterTemplateHigh as template
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
from dpmModule.kernel import graph
jobname = "나이트로드"
ulevel = 6000
weaponstat = [4,9]
level = 230



my_storage = graph.ConfigurationStorage({})
graph.set_global_storage(my_storage)

parser = IndividualDPMGenerator(jobname, template.getU4000CharacterTemplate)
try:
        dpm = parser.getDpm(ulevel = ulevel,
        weaponstat = weaponstat,
        level = level)
except:
        print(my_storage._origin)
        raise
print(dpm)