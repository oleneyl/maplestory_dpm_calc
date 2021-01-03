import sys

sys.path.append('../')
import dpmModule

from dpmModule.kernel.core.status import CharacterStatus

def status_test():
    status_a = CharacterStatus(
        crit=0,
        crit_damage=0,
        pdamage=0,
        pdamage_indep=0,
        stat=0,
        pstat=0,
        stat_fixed=0,
        hp=0,
        boss_pdamage=0,
        armor_ignore=0,
        att=0,
        patt=0
    )
    status_b = 