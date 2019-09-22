from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill

class MesoStack(core.DamageSkillWrapper, core.StackSkillWrapper):
    def __init__(self, vEhc):
        self.vEhc = vEhc
        skill = core.DamageSkill("메소익스플로전", 0, 220, 1).setV(vEhc, 2, 3, False)
        super(core.DamageSkillWrapper, self).__init__(skill, 20)
        self.modifierInvariantFlag = False
        
    def _use(self, rem = 0, red = 0):
        mdf = self.skill.get_modifier()
        dmg = 220
        stack = self.stack
        self.stack = 0
        return core.ResultObject(0, mdf.copy(),  dmg * stack, sname = self._id, spec = 'deal')

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 10
        self.jobtype = "luk"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage = 70, armor_ignore = 20)
        
    def get_passive_skill_list(self):

        
        NimbleBody = core.InformedCharacterModifier("님블 바디",stat_main = 20)
        Karma = core.InformedCharacterModifier("카르마",att = 30)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        SheildMastery = core.InformedCharacterModifier("실드 마스터리",att = 15)
        Grid = core.InformedCharacterModifier("그리드",att = 5)
        
        PrimaCriticalPassive = core.InformedCharacterModifier("프리마 크리티컬(패시브)",stat_main = 10, crit_damage = 20)
        PrimaCritical = core.InformedCharacterModifier("프리마 크리티컬",crit = 53.8 / 4, crit_damage = 8.8) #스택식으로도 계산 가능.
        
        BoomerangStepPassive = core.InformedCharacterModifier("부메랑 스텝(패시브)",pdamage_indep = 25)
        
        ShadowerInstinctPassive = core.InformedCharacterModifier("섀도어 인스팅트(패시브)",armor_ignore = 20)
        ReadyToDiePassive = core.InformedCharacterModifier("레디 투 다이(패시브)",att = self.vEhc.getV(2,2))
    
        DaggerExpert = core.InformedCharacterModifier("대거 엑스퍼트",att = 40, crit_damage = 15)
        
        return [NimbleBody, Karma,
                        PhisicalTraining, SheildMastery, Grid, PrimaCriticalPassive,
                        PrimaCritical, BoomerangStepPassive, ShadowerInstinctPassive, ReadyToDiePassive, DaggerExpert]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)    #오더스 기본적용!
        
        return [WeaponConstant, Mastery]
    
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        일반 다크사이트는 깡으로 사용하지 않음.
        
        프리마 크리티컬 : 6/12/18/24/30/36/42/48/... / 96/100 -> 53.8
        크뎀 : 8.8
        쉐도우 파트너는 절개와 암살에만 적용.
        
        하이퍼 : 메익 인핸스, 암살 리인포스 / 보킬 / 이그노어 가드.
        
        암살 1타 3스택 34% / 2타 91%
        암살-부스-익플-배오섀
        '''

        
        ######   Skill   ######
        STACK1RATE = 34
        STACK2RATE = 91

        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 200*1000).wrap(core.BuffSkillWrapper)
        FlipTheCoin = core.BuffSkill("플립 더 코인", 0, 24000, pdamage = 5*5, crit = 10*5).wrap(core.BuffSkillWrapper)
        ShadowerInstinct = core.BuffSkill("섀도어 인스팅트", 0, 200*1000, rem = True, att = 40+30).wrap(core.BuffSkillWrapper)
        ShadowPartner = core.BuffSkill("섀도우 파트너", 1000, 2000*1000, rem = True).wrap(core.BuffSkillWrapper)
        
        Assasinate1 = core.DamageSkill("암살(1타)", 630, 550, 3 * 1.7, modifier = core.CharacterModifier(pdamage=20, boss_pdamage = 20, armor_ignore = 10, pdamage_indep = STACK1RATE)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper, name = "암살 1타")   #쉐파
        Assasinate2 = core.DamageSkill("암살(2타)", 630+30, 700, 3 * 1.7, modifier = core.CharacterModifier(pdamage=20, boss_pdamage = 20, armor_ignore = 10, pdamage_indep = STACK2RATE)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper, name = "암살 2타")   #쉐파
        
        Assasinate1_D = core.DamageSkill("암살(1타)(다크사이트)", 630, 550, 3 * 1.7, modifier = core.CharacterModifier(pdamage=20+150, boss_pdamage = 20, armor_ignore = 10, pdamage_indep = STACK1RATE)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper, name = "암살 1타(닼사)")   #쉐파
        Assasinate2_D = core.DamageSkill("암살(2타)(다크사이트)", 630+30, 700, 3 * 1.7, modifier = core.CharacterModifier(pdamage=20+150, boss_pdamage = 20, armor_ignore = 10, pdamage_indep = STACK2RATE)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper, name = "암살 2타(닼사)")   #쉐파
        
        BailOfShadow = core.DamageSkill("베일 오브 섀도우", 810, 800, 15, cooltime = 60000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        #킬포3개 사용시 최종뎀 100% 증가.
    
        Smoke = core.BuffSkill("연막탄", 1080, 30000, cooltime = 150000, crit_damage = 20).wrap(core.BuffSkillWrapper)
        Venom = core.DotSkill("페이탈 베놈", 480, 89999 * 1000).wrap(core.SummonSkillWrapper)
        
        AdvancedDarkSight = core.BuffSkill("다크 사이트", 0, 10000, cooltime = -1, pdamage_indep = 5).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        #_VenomBurst = core.DamageSkill("베놈 버스트", ??) ## 패시브 50%확률로 10초간 160+6*vlevel dot. 사용시 도트뎀 모두 피해 + (500+20*vlevel) * 5. 어차피 안쓰는 스킬이므로 작성X
        
        UltimateDarksight = core.BuffSkill("얼티밋 다크사이트", 750, 30000, cooltime = (220-vEhc.getV(3,3))*1000, pdamage_indep = (10 + int(0.2*vEhc.getV(3,3))/1.05 )).isV(vEhc,3,3).wrap(core.BuffSkillWrapper)
        ReadyToDie = core.BuffSkill("레디 투 다이", 780, 15*1000, cooltime = (90-int(0.5*vEhc.getV(2,2)))*1000, pdamage_indep = 30+int(0.2*vEhc.getV(2,2))).isV(vEhc,2,2).wrap(core.BuffSkillWrapper)
        
        Eviscerate = core.DamageSkill("절개", 570, 1900+76*vEhc.getV(0,0), 7*1.7, modifier = core.CharacterModifier(crit=100, armor_ignore=100), cooltime = 14000).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        SonicBlow = core.DamageSkill("소닉 블로우", 900, 0, 0, cooltime = 80 * 1000).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        SonicBlowTick = core.DamageSkill("소닉 블로우(틱)", 125, 440+17*vEhc.getV(1,1), 7*1.7, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,1,1).wrap(core.DamageSkillWrapper, name = "소닉 블로우(사용)")#20타
        
        ### build graph relationships
        def isNotDarkSight():
            return (not AdvancedDarkSight.is_active())
        
        AdvancedDarkSight.set_disabled_and_time_left(-1)    
        DarkSightTurnedOn = core.ConstraintElement("다크사이트 여부 확인", AdvancedDarkSight, isNotDarkSight)
        
        MesoExplosion = MesoStack(vEhc)
        
        Assasinate2.onAfters([SonicBlow.controller(1500, "reduce_cooltime"), MesoExplosion.stackController(6*0.4, name = "메소 생성")])
        Assasinate1.onAfter(MesoExplosion.stackController(6*0.4, name = "메소 생성"))
        Assasinate1.onAfter(MesoExplosion)
        Assasinate1.onAfter(Assasinate2)
        
        Assasinate2_D.onAfters([SonicBlow.controller(1500, "reduce_cooltime"), MesoExplosion.stackController(6*0.4, name = "메소 생성")])
        Assasinate1_D.onAfter(MesoExplosion.stackController(6*0.4, name = "메소 생성"))
        Assasinate1_D.onAfter(MesoExplosion)
        Assasinate1_D.onAfter(Assasinate2_D)
        
        BailOfShadow.onConstraint(DarkSightTurnedOn)
        BailOfShadow.onAfter(MesoExplosion.stackController(15*0.4, name = "메소 생성"))
        BailOfShadow.onAfter(AdvancedDarkSight.controller(12000, "set_enabled_and_time_left"))
        
        Smoke.onConstraint(DarkSightTurnedOn)
        Smoke.onAfter(AdvancedDarkSight.controller(30000, "set_enabled_and_time_left"))
        
        UltimateDarksight.onConstraint(DarkSightTurnedOn)
        UltimateDarksight.onAfter(AdvancedDarkSight.controller(30000,"set_enabled_and_time_left" ))
        
        SonicBlowTick.onAfter(MesoExplosion.stackController(14*0.4, name = "메소 생성"))
        SonicBlow.onAfter(core.RepeatElement(SonicBlowTick, 20))
        
        Eviscerate.onAfter(MesoExplosion.stackController(14*0.4, name = "메소 생성"))
        
        Assasinate = core.OptionalElement(AdvancedDarkSight.is_active, Assasinate1_D, Assasinate1, name = "닼사 여부")
        BasicAttackWrapper = core.DamageSkill('기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(Assasinate)
        
        return(BasicAttackWrapper, 
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    Booster, FlipTheCoin, ShadowerInstinct, ShadowPartner, Smoke, AdvancedDarkSight, EpicAdventure, UltimateDarksight, 
                        ReadyToDie, globalSkill.soul_contract()] +\
                [Eviscerate, SonicBlow, BailOfShadow]+\
                [Venom]+\
                []+\
                [BasicAttackWrapper])