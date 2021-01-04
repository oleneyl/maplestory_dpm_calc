import sys

sys.path.append('../')
import dpmModule

from dpmModule.kernel.core.status import CharacterStatus


def test_status_building():
    status = CharacterStatus(
        crit=0,
        crit_damage=0,
        pdamage=0,
        pdamage_indep=0,
        stat=[1,2,3,4],
        stat_rate=[1,2,3,4],
        stat_fixed=[1,2,3,4],
        MHP=0,
        boss_pdamage=0,
        armor_ignore=0,
        att=1,
        matt=1,
        att_rate=1,
        matt_rate=1
    )


def test_status_addition():
    answer = [7,9,11,13]

    status = CharacterStatus(stat=[1,2,3,4]) + CharacterStatus(stat=[6,7,8,9])
    for i in range(4):
        assert status.stat[i] == answer[i]
    
    status = CharacterStatus(stat_rate=[1,2,3,4]) + CharacterStatus(stat_rate=[6,7,8,9])
    for i in range(4):
        assert status.stat_rate[i] == answer[i]

    status = CharacterStatus(stat_fixed=[1,2,3,4]) + CharacterStatus(stat_fixed=[6,7,8,9])
    for i in range(4):
        assert status.stat_fixed[i] == answer[i]

    assert (CharacterStatus(crit=3) + CharacterStatus(crit=4)).crit == 7
    assert (CharacterStatus(crit_damage=3) + CharacterStatus(crit_damage=4)).crit_damage == 7
    assert (CharacterStatus(pdamage=3) + CharacterStatus(pdamage=4)).pdamage == 7
    assert (CharacterStatus(MHP=3) + CharacterStatus(MHP=4)).MHP == 7
    assert (CharacterStatus(boss_pdamage=3) + CharacterStatus(boss_pdamage=4)).boss_pdamage == 7
    assert (CharacterStatus(att=3) + CharacterStatus(att=4)).att == 7
    assert (CharacterStatus(matt=3) + CharacterStatus(matt=4)).matt == 7
    assert (CharacterStatus(att_rate=3) + CharacterStatus(att_rate=4)).att_rate == 7
    assert (CharacterStatus(matt_rate=3) + CharacterStatus(matt_rate=4)).matt_rate == 7

    assert (CharacterStatus(pdamage_indep=10) + CharacterStatus(pdamage_indep=20)).pdamage_indep == 32
    assert (CharacterStatus(armor_ignore=20) + CharacterStatus(armor_ignore=40)).armor_ignore == 52


def test_status_keyword_overloading():
    status = CharacterStatus(STR=3, DEX=2, INT=4, LUK=5)
    assert status.stat[0] == 3
    assert status.stat[1] == 2
    assert status.stat[2] == 4
    assert status.stat[3] == 5

    assert status.STR == 3
    assert status.DEX == 2
    assert status.INT == 4
    assert status.LUK == 5


def test_complex_status_keyword_overloading():
    status = CharacterStatus(stat_fixed=[3,4,5,6])
    assert status.STR_fixed == 3
    assert status.DEX_fixed == 4
    assert status.INT_fixed == 5
    assert status.LUK_fixed == 6


def test_status_keyword_setting_overloading():
    status = CharacterStatus()
    status.STR = 3
    status.DEX = 4
    status.INT = 5
    status.LUK = 6

    assert status.STR == 3
    assert status.DEX == 4
    assert status.INT == 5
    assert status.LUK == 6

    assert status.stat[0] == 3
    assert status.stat[1] == 4
    assert status.stat[2] == 5
    assert status.stat[3] == 6
