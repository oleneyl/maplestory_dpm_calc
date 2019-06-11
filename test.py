import sys, os

import dpmModule as dpm
import dpmModule.character.characterTemplateHigh as template
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
from dpmModule.kernel import graph
from dpmModule.jobs import jobMap
jobname = "나이트로드"
ulevel = 6000
weaponstat = [4,9]
level = 230



#my_storage = graph.ConfigurationStorage({})
#graph.set_global_storage(my_storage)
for jobname in ['나이트로드']:
#for jobname in jobMap:
        parser = IndividualDPMGenerator(jobname, template.getU4000CharacterTemplate)
        try:
                dpm = parser.unstable_getDpm(ulevel = ulevel,
                weaponstat = weaponstat,
                level = level,
                printFlag=False)
        except:
                raise
        finally:
                print(jobname, dpm)
        with open('conf.json', 'w', encoding='utf8') as f:
                graph._unsafe_access_global_storage()._storage.write(f)

