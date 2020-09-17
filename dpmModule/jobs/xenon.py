from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import thieves, pirates
from .jobclass import resistance
from math import ceil

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "luk"
        self.jobname = "제논"
        self.vEnhanceNum = None
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier()
        
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        return []

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 50)
        JobConstant = core.InformedCharacterModifier("직업상수", pdamage_indep = -12.5)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -5 + 0.5 * ceil(passive_level / 2))
        
        return [WeaponConstant, JobConstant, Mastery]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter):
        '''
        TODO: 제논 구현

        '''

        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        # Buff skills

        # Damage skills
        
        
        # Hyper skills
        
    
        # V skills
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        ######   Skill Wrapper   ######

        BasicAttackWrapper = core.DamageSkill("기본 공격", 0, 0, 0).wrap(core.DamageSkillWrapper)
        
        return(BasicAttackWrapper, 
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    globalSkill.useful_wind_booster(), globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()] +\
                [MirrorBreak, MirrorSpider] +\
                [] +\
                [BasicAttackWrapper])