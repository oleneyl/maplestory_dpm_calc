from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.jobtype = "int"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1
        
    def apply_complex_options(self, chtr):
        chtr.add_property_ignorance(10)

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 20, pdamage = 50)

    def get_passive_skill_list(self):
        ######   Skill   ######
        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트",stat_main = self.chtr.level // 2)
        ElementalHarmony = core.InformedCharacterModifier("엘리멘탈 하모니",patt = 10)     
        
        SpellControl = core.InformedCharacterModifier("스펠 컨트롤",att = 10)
        #이그니션 : 매초 (220% * 1.8) x2-> 폭발하여 240%
		# 1.2.324 패치 적용
		# 마법의 진리 스킬 없음. 일단 해방된 마력에 마력 10 증가시킴
        LiberatedMagic = core.InformedCharacterModifier("해방된 마력",pdamage_indep = 30, att = 10)
        BurningFocus = core.InformedCharacterModifier("버닝 포커스",crit = 30, crit_damage = 15)
        BriliantEnlightenment = core.InformedCharacterModifier("briliantEnlightenment",stat_main = 60)
        PureMagic = core.InformedCharacterModifier("순수한 마력", att = 10, pdamage_indep = 50)
        #TODO
        #Elemental Reset --> elemental ignorance +10% --> first we will apply this term as simple pdamage_indep
        return [ElementalExpert, ElementalHarmony, SpellControl, LiberatedMagic, BurningFocus, BriliantEnlightenment, PureMagic]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -2.5)       
        
        Flame = core.InformedCharacterModifier("플레임",att = 40)
        return [WeaponConstant, Mastery, Flame]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        오비탈 - 블레이징 - 드래곤 슬레이브 - 이그니션 - 인페르노라이즈
        여우 사용
        블비탈 4히트
        1350타 / 분
        '''
        
        flamewizardDefaultSpeed = 60000 / ((1350) / 6)  #266
        
        #Buff skills
        WordOfFire = core.BuffSkill("북 오브 파이어", 0, 300000, att = 20).wrap(core.BuffSkillWrapper)
        FiresOfCreation = core.BuffSkill("스피릿 오브 플레임", 600, 300 * 1000, armor_ignore = 30).wrap(core.BuffSkillWrapper)
        BurningRegion = core.BuffSkill("버닝 리전", 810, 30 * 1000, cooltime =45 * 1000, rem = True, pdamage = 60).wrap(core.BuffSkillWrapper)
        GloryOfGuardians = core.BuffSkill("글로리 오브 가디언즈", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        OverloadMana = core.BuffSkill("오버로드 마나", 0, 99999 * 10000, pdamage = 8+int(0.1*vEhc.getV(1,2))).isV(vEhc,1,2).wrap(core.BuffSkillWrapper)
        #Damage Skills
        InfernoRize = core.DamageSkill("인페르노 라이즈", 720, 285, 5, cooltime = 30*1000, modifier = core.CharacterModifier(pdamage = 90)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)    #임의딜레이 720
        
        #Full speed, No Combat Orders
        OrbitalFlame = core.DamageSkill("오비탈 플레임", flamewizardDefaultSpeed, 215, 3 * 2, modifier = core.CharacterModifier(armor_ignore = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        CygnusPalanks = core.DamageSkill("시그너스 팔랑크스", 780, 450 + 18*vEhc.getV(2,1), 40 + vEhc.getV(2,1), cooltime = 30 * 1000).isV(vEhc,2,1).wrap(core.DamageSkillWrapper)
        BlazingOrbital = core.DamageSkill("블레이징 오비탈 플레임", 210, 330+13*vEhc.getV(0,0), 6 * 4, cooltime = 5000, modifier = core.CharacterModifier(armor_ignore = 50)).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)    #4타 가정
        
        DragonSlaveTick = core.DamageSkill("드래곤 슬레이브", 280, 500, 6).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)#x7
        DragonSlaveInit = core.DamageSkill("드래곤 슬레이브 개시(더미)", 0, 0, 0, cooltime = 90 * 1000).wrap(core.DamageSkillWrapper)
        DragonSlaveEnd = core.DamageSkill("드래곤 슬레이브 종결", 0, 500, 10).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        
        IgnitionDOT = core.SummonSkill("이그니션", 0, 1000, 220*1.6, 1, 10*1000, modifier = core.CharacterModifier(crit=-9999, armor_ignore=100)).wrap(core.SummonSkillWrapper)
        #여우 사용
        SavageFlameStack = core.StackSkillWrapper(core.BuffSkill("플레임 디스차지(스택)", 0, 99999999), 6)
        
        SavageFlame = core.DamageSkill("플레임 디스차지", 0, 0, 0, cooltime = 20*1000).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
    
        SavageFlame_2 = core.DamageSkill("플레임 디스차지(2)", 840, 250 + 10*vEhc.getV(4,4), 8*(8+2)).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
        SavageFlame_3 = core.DamageSkill("플레임 디스차지(3)", 840, 250 + 10*vEhc.getV(4,4), 8*(8+3)).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
        
        InfinityFlameCircleTick = core.DamageSkill("인피니티 플레임 서클", 180, 500+20*vEhc.getV(3,3),7, modifier = core.CharacterModifier(crit = 50, armor_ignore = 50)).isV(vEhc,3,3).wrap(core.DamageSkillWrapper) #1틱
        InfinityFlameCircleInit = core.DamageSkill("인피니티 플레임 서클(개시)", 360, 0, 0, cooltime = 15*12*1000).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)#계산 필요
        
        ######   Wrappers    ######
    
        DragonSlave = core.RepeatElement(DragonSlaveTick, 7)
        DragonSlave.onAfter(DragonSlaveEnd)
        DragonSlaveInit.onAfter(DragonSlave)
    
        InfinityFlameCircle = core.RepeatElement(InfinityFlameCircleTick, 83)
        
        InfinityFlameCircleInit.onAfter(InfinityFlameCircle)
        
        IgnitionDOT.onAfter(SavageFlameStack.stackController(1))
        InfernoRize.onAfter(IgnitionDOT.controller(1))

        SavageFlame.onAfter( core.OptionalElement(partial(SavageFlameStack.judge, 3, 1), SavageFlame_3, SavageFlame_2, name = "스택 확인") )
        SavageFlame.onAfter(SavageFlameStack.stackController(-15))

        schedule = core.ScheduleGraph()
        
        return (OrbitalFlame,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    WordOfFire, FiresOfCreation, BurningRegion, GloryOfGuardians, OverloadMana,
                    globalSkill.soul_contract()] +\
                [CygnusPalanks, BlazingOrbital, DragonSlaveInit, SavageFlame, InfinityFlameCircleInit, 
                    InfernoRize] +\
                [IgnitionDOT] +\
                [] +\
                [OrbitalFlame])    
    