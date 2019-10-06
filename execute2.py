import dpmModule
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
import dpmModule.character.characterTemplateHigh as template
gen = IndividualDPMGenerator('히어로', template.getU6000CharacterTemplate)
print(gen.get_dpm(ulevel = 6000))