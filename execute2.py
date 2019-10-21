import dpmModule
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
import dpmModule.character.characterTemplateHigh as template
job_name = '패스파인더'
gen = IndividualDPMGenerator(job_name, template.getU6000CharacterTemplate)
print(job_name, gen.get_dpm(ulevel = 6000))