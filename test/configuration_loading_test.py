import sys

sys.path.append('../')
import dpmModule

from dpmModule.kernel.core import CharacterModifier,InformedCharacterModifier
from dpmModule.character.characterKernel import JobGenerator

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
    test_conf = {
        'buffrem': [0, 40],
        'jobtype': 'int',
        'jobname': '아크메이지불/독',
        'vEnhanceNum': 13,
        'preEmptiveSkills': 2,
        'passive_skill_list':[
            {
                'name': '하이 위즈덤',
                'stat_main': 40
            }, {
                'name': '스펠 마스터리',
                'att': 10
            }, {
                'name': '매직 크리티컬',
                'crit': 30,
                'crit_damage': 13
            }

        }
    }
    vEhc = None
    gen = JobGenerator()
    gen.load(test_conf)
    passive_skill_list = gen.get_passive_skill_list(vEhc, None, None)
    print(passive_skill_list)