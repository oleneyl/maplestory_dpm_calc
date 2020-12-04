import sys

sys.path.append('../')
import dpmModule

from dpmModule.kernel.core import CharacterModifier,InformedCharacterModifier


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
