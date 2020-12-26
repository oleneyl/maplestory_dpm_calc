import dpmModule.character.characterTemplateHigh as template
from dpmModule.util.dpmgenerator import IndividualDPMGenerator

job_name = '나이트로드'
gen = IndividualDPMGenerator(job_name, template.getU6000CharacterTemplate)
print(job_name, gen.get_dpm(ulevel=8000))
