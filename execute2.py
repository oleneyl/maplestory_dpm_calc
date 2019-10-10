import dpmModule
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
import dpmModule.character.characterTemplateHigh as template
job_name = '다크나이트'
gen = IndividualDPMGenerator(job_name, template.getU6000CharacterTemplate)
print(job_name, gen.get_dpm(ulevel = 6000))