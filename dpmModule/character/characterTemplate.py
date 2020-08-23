from .characterKernel import ItemedCharacter as ichar
from ..item import Arcane, Absolab, Empress, RootAbyss, BossAccesory, Default, Else, Meister, Darkness
from ..item import ItemKernel as it

_STORAGE_FOR_EXISTING_TEMPLATE_DEFINED_BY_ABSTRACT_TEMPLATE_GENERATOR = {}

def register_template_generator(generator_class, generator_name):
    global _STORAGE_FOR_EXISTING_TEMPLATE_DEFINED_BY_ABSTRACT_TEMPLATE_GENERATOR
    _STORAGE_FOR_EXISTING_TEMPLATE_DEFINED_BY_ABSTRACT_TEMPLATE_GENERATOR[generator_name] = generator_class

def get_template_generator(generator_name):
    global _STORAGE_FOR_EXISTING_TEMPLATE_DEFINED_BY_ABSTRACT_TEMPLATE_GENERATOR
    try:
        return _STORAGE_FOR_EXISTING_TEMPLATE_DEFINED_BY_ABSTRACT_TEMPLATE_GENERATOR[generator_name]
    except:
        raise KeyError(f'Given generator {generator_name} not exist or not had been registered.')

class AbstractTemplateGenerator():
    def __init__(self, weaponstat_config):
        self.WEAPONSTAT_CONFIG_RECOMMENDED = weaponstat_config

    def __iter__(self):
        for ulevel in self.get_ulevels():
            yield ulevel, self.get_template(ulevel), self.WEAPONSTAT_CONFIG_RECOMMENDED[ulevel]

    def get_ulevels(self):
        return sorted(self.WEAPONSTAT_CONFIG_RECOMMENDED.keys())

    def get_weaponstat(self, ulevel):
        return self.WEAPONSTAT_CONFIG_RECOMMENDED[ulevel]

    def query(self, ulevel):
        return self.get_template(ulevel), self.get_weaponstat(ulevel)

    def get_template(self, ulevel):
        raise NotImplementedError

