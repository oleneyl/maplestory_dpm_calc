from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from . import globalSkill, jobutils
from .jobclass import anima
from .jobbranch import magicians
from math import ceil
from typing import Any, Dict

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        ### Incomplete ###
        super(JobGenerator, self).__init__()
        self.jobtype = "INT"
        self.jobname = "라라"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'buff_rem', 'mess')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        ### Incomplete ###
        return core.CharacterModifier(armor_ignore=20, pdamage=40)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        ### Incomplete ###
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        SpiritAffinity = core.InformedCharacterModifier("정령친화", summon_rem=10)

        return [SpiritAffinity]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        Mastery = core.InformedCharacterModifier("숙련도", mastery=95 + ceil(passive_level / 2))
        return [Mastery]

    '''
    def get_ruleset(self):
        ruleset = RuleSet()
        return ruleset
        '''

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        """
        ### Incomplete ###
        """

        passive_level = chtr.get_base_modifier().passive_level + self.combat

        BasicAttack = core.DamageSkill("기본 공격", 0, 0, 0).wrap(core.DamageSkillWrapper)

        return (
            BasicAttack,
            [
                globalSkill.maple_heros(chtr.level, name="아니마의 용사", combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                globalSkill.soul_contract()
            ]
            + []
            + []
            + [BasicAttack]
        )
