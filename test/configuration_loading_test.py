import sys

sys.path.append('../')

from dpmModule.character.characterKernel import JobGenerator
from dpmModule.character.characterTemplate import get_template_generator
from dpmModule.kernel.core import CharacterModifier, InformedCharacterModifier, AlwaysMaximumVBuilder


def test_modifier_loading():
    test_modifier_conf = {
        'att': 30,
        'pdamage_indep': 20
    }

    test_modifier = CharacterModifier.load(test_modifier_conf)
    assert test_modifier.att == 30
    assert test_modifier.pdamage_indep == 20


def test_informed_modifier_loading():
    test_modifier_conf = {
        'att': 30,
        'pdamage_indep': 20,
        'name': 'test_md'
    }

    test_modifier = InformedCharacterModifier.load(test_modifier_conf)
    assert test_modifier.att == 30
    assert test_modifier.pdamage_indep == 20
    assert test_modifier.name == 'test_md'


def test_job_generator_creation():
    character = get_template_generator("high_standard")().get_template(8000)('스태프')
    gen = JobGenerator(character, v_builder=AlwaysMaximumVBuilder(), options={})
    gen.load('../dpmModule/jobs/configs/archmageFb.json')
    passive_skill_list = gen.loader.load_passive_skill_list()
    not_implied_skill_list = gen.loader.load_not_implied_skill_list()
    print(passive_skill_list)
    print(not_implied_skill_list)
