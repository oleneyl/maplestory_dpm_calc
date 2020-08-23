from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConditionRule
from . import globalSkill
from .jobclass import cygnus
from .jobbranch import magicians

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.jobtype = "int"
        self.jobname = "플레임위자드"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 20, pdamage = 50)

    def get_ruleset(self):
        def check_ifc_time(ifc):
            return (ifc.is_usable() or ifc.is_cooltime_left(90*1000, 1))

        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule('소울 컨트랙트', '인피니티 플레임 서클(개시)', check_ifc_time), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        ######   Skill   ######
        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트", patt = 10)
        ElementalHarmony = core.InformedCharacterModifier("엘리멘탈 하모니", stat_main = chtr.level // 2)
        
        SpellControl = core.InformedCharacterModifier("주문 연마",att = 10)
        LiberatedMagic = core.InformedCharacterModifier("해방된 마력",pdamage_indep = 30)
        BurningFocus = core.InformedCharacterModifier("약점 분석",crit = 30, crit_damage = 15)
        BriliantEnlightenment = core.InformedCharacterModifier("번뜩이는 깨달음",stat_main = 60)
        PureMagic = core.InformedCharacterModifier("마법의 진리", att = 20, pdamage_indep = 50)

        return [ElementalExpert, ElementalHarmony, SpellControl, LiberatedMagic, BurningFocus, BriliantEnlightenment, PureMagic]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -2.5)
        SpiritOfFlameActive = core.InformedCharacterModifier("스피릿 오브 플레임(이그니션)", prop_ignore = 10)
        
        return [WeaponConstant, Mastery, SpiritOfFlameActive]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        오비탈 - 익스팅션 - 드래곤 슬레이브 - 이그니션 - 인페르노라이즈
        디스차지 여우 사용
        블비탈 4히트
        오비탈 1350타 / 분
        '''
        
        flamewizardDefaultSpeed = 60000 / ((1350) / 6)  #266
        blazingOrbitalHit = 4
        
        #Buff skills
        WordOfFire = core.BuffSkill("북 오브 파이어", 0, 300000, att = 20).wrap(core.BuffSkillWrapper)
        FiresOfCreation = core.BuffSkill("스피릿 오브 플레임", 600, 300 * 1000, armor_ignore = 30).wrap(core.BuffSkillWrapper)
        BurningRegion = core.BuffSkill("버닝 리전", 1080, 30 * 1000, cooltime =45 * 1000, rem = True, pdamage = 60).wrap(core.BuffSkillWrapper)
        GloryOfGuardians = core.BuffSkill("글로리 오브 가디언즈", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        Flame = core.BuffSkill("플레임", 0, 8000, att = 40).wrap(core.BuffSkillWrapper) # 벞지 적용 안되는 스킬
        
        OverloadMana = OverloadMana = magicians.OverloadManaWrapper(vEhc, 1, 2)
        #Damage Skills
        InfernoRize = core.DamageSkill("인페르노라이즈", 570, 350, 10, cooltime = 30*1000, modifier = core.CharacterModifier(pdamage_indep = 90), red = True).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        
        #Full speed, No Combat Orders
        OrbitalFlame = core.DamageSkill("오비탈 플레임 IV", 210, 215, 3 * 2 * (210 / flamewizardDefaultSpeed), modifier = core.CharacterModifier(armor_ignore = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        # BlazingExtinction = core.SummonSkill("블레이징 익스팅션", 1020, 2500, 310, 3+1, 10000, cooltime=5000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)
        CygnusPalanks = cygnus.PhalanxChargeWrapper(vEhc, 2, 1)
        BlazingOrbital = core.DamageSkill("블레이징 오비탈 플레임", 210, 330+13*vEhc.getV(0,0), 6 * blazingOrbitalHit, cooltime = 5000, modifier = core.CharacterModifier(armor_ignore = 50), red = True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)    #4타 가정
        
        DragonSlaveTick = core.DamageSkill("드래곤 슬레이브", 280, 500, 6).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)#x7
        DragonSlaveInit = core.DamageSkill("드래곤 슬레이브 개시(더미)", 0, 0, 0, cooltime = 90 * 1000).wrap(core.DamageSkillWrapper)
        DragonSlaveEnd = core.DamageSkill("드래곤 슬레이브 종결", 810, 500, 10).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        
        IgnitionDOT = core.DotSkill("이그니션", 220*1.6, 10*1000).wrap(core.SummonSkillWrapper)

        #여우 사용
        SavageFlameStack = core.StackSkillWrapper(core.BuffSkill("플레임 디스차지(스택)", 0, 99999999), 6)
        
        SavageFlame = core.DamageSkill("플레임 디스차지", 0, 0, 0, cooltime = 20*1000, red = True).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
    
        SavageFlame_2 = core.DamageSkill("플레임 디스차지(2스택)", 840, 250 + 10*vEhc.getV(4,4), 8*8).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
        SavageFlame_3= core.DamageSkill("플레임 디스차지(3스택)", 840, 250 + 10*vEhc.getV(4,4), 8*(8+2)).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
        SavageFlame_4 = core.DamageSkill("플레임 디스차지(4스택)", 840, 250 + 10*vEhc.getV(4,4), 8*(8+2+2)).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
        
        InfinityFlameCircleTick = core.DamageSkill("인피니티 플레임 서클", 180, 500+20*vEhc.getV(3,3), 7, modifier = core.CharacterModifier(crit = 50, armor_ignore = 50)).isV(vEhc,3,3).wrap(core.DamageSkillWrapper) #1틱
        InfinityFlameCircleInit = core.DamageSkill("인피니티 플레임 서클(개시)", 360, 0, 0, cooltime = 15*6*1000).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        
        ######   Wrappers    ######
    
        DragonSlave = core.RepeatElement(DragonSlaveTick, 7)
        DragonSlave.onAfter(DragonSlaveEnd)
        DragonSlaveInit.onAfter(DragonSlave)
    
        InfinityFlameCircle = core.RepeatElement(InfinityFlameCircleTick, 39)
        
        InfinityFlameCircleInit.onAfter(InfinityFlameCircle)
        
        IgnitionDOT.onAfter(SavageFlameStack.stackController(1))
        InfernoRize.onAfter(IgnitionDOT.controller(1))
        DragonSlaveEnd.onAfter(IgnitionDOT.controller(1))

        InfernoRize.onConstraint(core.ConstraintElement("이그니션 시간 체크", IgnitionDOT, partial(IgnitionDOT.is_time_left, 9000, 1)))

        StackCheck3 = core.OptionalElement(partial(SavageFlameStack.judge, 3, 1), SavageFlame_3, SavageFlame_2, name = "스택 확인")
        StackCheck4 = core.OptionalElement(partial(SavageFlameStack.judge, 4, 1), SavageFlame_4, StackCheck3, name = "스택 확인")
        SavageFlame.onAfter(StackCheck4)
        SavageFlame.onAfter(SavageFlameStack.stackController(-15))
        
        return (OrbitalFlame,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    WordOfFire, FiresOfCreation, BurningRegion, GloryOfGuardians, OverloadMana, Flame,
                    globalSkill.soul_contract()] +\
                [CygnusPalanks, BlazingOrbital, DragonSlaveInit, SavageFlame, InfinityFlameCircleInit, 
                    InfernoRize] +\
                [IgnitionDOT] +\
                [] +\
                [OrbitalFlame])    
    