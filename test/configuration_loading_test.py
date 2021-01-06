import sys
import json

from dpmModule.character.characterTemplate import TemplateGenerator

sys.path.append('../')

from dpmModule.character.characterKernel import JobGenerator
from dpmModule.kernel.core import CharacterModifier, InformedCharacterModifier


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
    with open('../dpmModule/jobs/configs/archmageFb.json', encoding='utf-8') as f:
        test_conf = json.load(f)
    vEhc = None
    gen = JobGenerator()
    character = TemplateGenerator().get_template(gen, "8000")
    gen.load(test_conf)
    passive_skill_list = gen.get_passive_skill_list(vEhc, character, None)
    not_implied_skill_list = gen.get_not_implied_skill_list(vEhc, character, None)
    print(passive_skill_list)
    print(not_implied_skill_list)
