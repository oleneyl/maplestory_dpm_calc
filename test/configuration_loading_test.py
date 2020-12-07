import sys

sys.path.append('../')
import dpmModule

from dpmModule.kernel.core import CharacterModifier,InformedCharacterModifier
from dpmModule.character.characterKernel import JobGenerator
from dpmModule.character.characterTemplate import get_template_generator

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
            }, {
                'name': '엘리멘트 엠플리피케이션',
                'pdamage': 50
            }, {
                'name': '엘리멘탈 리셋',
                'pdamage_indep': 40
            }, {
                'name': '마스터 매직',
                'att': '30 + 3 * passive_level',
                'buff_rem': '50 + 5 * passive_level'
            }, {
                'name': '아케인 에임',
                'armor_ignore': '20 + math.ceil(passive_level // 2)'
            }
        ],
        'not_implied_skill_list':[

        ]
    }
    vEhc = None
    gen = JobGenerator()
    character = get_template_generator("high_standard")().get_template(8000)('스태프')
    gen.load(test_conf)
    passive_skill_list = gen.get_passive_skill_list(vEhc, character, None)
    print(passive_skill_list)