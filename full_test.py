import dpmModule
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
import dpmModule.character.characterTemplateHigh as template
import dpmModule.jobs as maplejobs

dpm_list = []
for value in maplejobs.jobList.values():
    gen = IndividualDPMGenerator(value, template.getU6000CharacterTemplate)
    print(value, gen.get_dpm(ulevel = 6000))