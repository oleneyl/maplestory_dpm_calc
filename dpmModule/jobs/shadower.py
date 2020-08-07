from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import thieves
from . import contrib

class MesoStack(core.DamageSkillWrapper, core.StackSkillWrapper):
    # 메익 리인포스 미적용 기준
    def __init__(self, vEhc):
        self.vEhc = vEhc
        skill = core.DamageSkill("메소 익스플로전", 0, 100, 2).setV(vEhc, 2, 3, False)
        super(core.DamageSkillWrapper, self).__init__(skill, 20)
        self.modifierInvariantFlag = False
        
    def _use(self, rem = 0, red = 0):
        mdf = self.skill.get_modifier()
        dmg = 100
        stack = self.stack
        self.stack = 0
        # 확인 필요
        return core.ResultObject(0, mdf.copy(),  dmg * (2 * stack), sname = self._id, spec = 'deal', hit = 2 * stack)

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
        PrimaCritical = core.InformedCharacterModifier("프리마 크리티컬", crit_damage = 8.8) #스택식으로도 계산 가능.
        
        BoomerangStepPassive = core.InformedCharacterModifier("부메랑 스텝(패시브)",pdamage_indep = 25)
        
        ShadowerInstinctPassive = core.InformedCharacterModifier("섀도어 인스팅트(패시브)",armor_ignore = 20)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(self.vEhc, 2, 2)
    
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
        
        프리마 크리티컬 크뎀 : 8.8%
        쉐도우 파트너는 절개, 암살, 소닉 블로우에만 적용.
        
        하이퍼 : 메익 인핸스, 암살 리인포스 / 보킬 / 이그노어 가드.
        
        킬링 포인트 3스택 확률 1타 94.6% / 2타 100%
        암살-부스-익플-배오섀
        '''
        
        ######   Skill   ######
        # http://m.inven.co.kr/board/powerbbs.php?come_idx=2297&stype=subject&svalue=%EC%8A%A4%ED%83%9D&l=52201

        # 1타 94.6%, 2타 100%
        # 크로아 서버 스킨헤드님 (https://maple.gg/u/%EC%8A%A4%ED%82%A8%ED%97%A4%EB%93%9C)
        # https://drive.google.com/file/d/1ORJc-F77ELssCSVWgHiuQP49pifgCjpo/view

        STACK1RATE = 94.6
        STACK2RATE = 100

        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 200*1000).wrap(core.BuffSkillWrapper)
        FlipTheCoin = core.BuffSkill("플립 더 코인", 0, 24000, pdamage = 5*5, crit = 10*5).wrap(core.BuffSkillWrapper)
        ShadowerInstinct = core.BuffSkill("섀도어 인스팅트", 0, 200*1000, rem = True, att = 40+30).wrap(core.BuffSkillWrapper)
        #StealPotion = core.BuffSkill("스틸 (포션)", 0, 180000, cooltime = -1, att = 30).wrap(core.BuffSkillWrapper)
        
        # 더미 데이터
        ShadowPartner = core.BuffSkill("섀도우 파트너", 1000, 2000*1000, rem = True).wrap(core.BuffSkillWrapper)
        
        #킬포3개 사용시 최종뎀 100% 증가.
        Assasinate1 = core.DamageSkill("암살(1타)", 630, 275, 6, modifier = core.CharacterModifier(pdamage=20, boss_pdamage = 20, armor_ignore = 10, pdamage_indep = STACK1RATE)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper, name = "암살 1타")   #쉐파
        Assasinate2 = core.DamageSkill("암살(2타)", 420, 350, 6, modifier = core.CharacterModifier(pdamage=20, boss_pdamage = 20, armor_ignore = 10, pdamage_indep = STACK2RATE)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper, name = "암살 2타")   #쉐파
        
        Assasinate1_D = core.DamageSkill("암살(1타)(다크사이트)", 630, 275, 6, modifier = core.CharacterModifier(pdamage=20+150, boss_pdamage = 20, armor_ignore = 10, pdamage_indep = STACK1RATE)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper, name = "암살 1타(닼사)")   #쉐파
        Assasinate2_D = core.DamageSkill("암살(2타)(다크사이트)", 420, 350, 6, modifier = core.CharacterModifier(pdamage=20+150, boss_pdamage = 20, armor_ignore = 10, pdamage_indep = STACK2RATE)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper, name = "암살 2타(닼사)")   #쉐파
        
        BailOfShadow = core.SummonSkill("베일 오브 섀도우", 810, 12000 / 14, 800, 1, 12*1000, cooltime = 60000).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)
        
    
        Smoke = core.BuffSkill("연막탄", 1080, 30000, cooltime = 150000, crit_damage = 20).wrap(core.BuffSkillWrapper)
        Venom = core.DotSkill("페이탈 베놈", 480, 89999 * 1000).wrap(core.SummonSkillWrapper)
        
        AdvancedDarkSight = core.BuffSkill("어드밴스드 다크 사이트", 0, 10000, cooltime = -1, pdamage_indep = 5).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        '''
        Steal = core.DamageSkill("스틸", 600, 330, 1, cooltime = 180000).isV(?, ?).wrap(core.DamageSkillWrapper)
        Steal.onAfter(StealPotion)
        '''
        #_VenomBurst = core.DamageSkill("베놈 버스트", ??) ## 패시브 50%확률로 10초간 160+6*vlevel dot. 사용시 도트뎀 모두 피해 + (500+20*vlevel) * 5. 어차피 안쓰는 스킬이므로 작성X
        
        UltimateDarksight = core.BuffSkill("얼티밋 다크 사이트", 750, 30000,
            cooltime = (220-vEhc.getV(3, 3))*1000,
            pdamage_indep= (100 + 10 + 5 + vEhc.getV(3, 3)//5) / (100 + 5) * 100 - 100 # (얼닼사 + 어닼사) - (어닼사) 최종뎀 연산
        ).isV(vEhc, 3, 3).wrap(core.BuffSkillWrapper)

        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 2, 2)
        
        Eviscerate = core.DamageSkill("절개", 570, 1900+76*vEhc.getV(0,0), 7, modifier = core.CharacterModifier(crit=100, armor_ignore=100), cooltime = 14000).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
		
		# 1.2.324 패치 적용
        SonicBlow = core.DamageSkill("소닉 블로우", 900, 0, 0, cooltime = 80 * 1000).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        SonicBlowTick = core.DamageSkill("소닉 블로우(틱)", 107, 500+20*vEhc.getV(1,1), 7, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,1,1).wrap(core.DamageSkillWrapper, name = "소닉 블로우(사용)") # 7 * 15
        
        ### build graph relationships
        def isNotDarkSight():
            return (not AdvancedDarkSight.is_active())
        
        AdvancedDarkSight.set_disabled_and_time_left(-1)    
        DarkSightTurnedOn = core.ConstraintElement("다크사이트 여부 확인", AdvancedDarkSight, isNotDarkSight)
        
        MesoExplosion = MesoStack(vEhc)
        
        Assasinate2.onAfters([SonicBlow.controller(1500 * STACK2RATE * 0.01, "reduce_cooltime"), MesoExplosion.stackController(6*2*0.4, name = "메소 생성")])
        Assasinate1.onAfter(MesoExplosion.stackController(6*2*0.4, name = "메소 생성"))
        Assasinate1.onAfter(MesoExplosion)
        Assasinate1.onAfter(Assasinate2)
        
        Assasinate2_D.onAfters([SonicBlow.controller(1500 * STACK2RATE * 0.01, "reduce_cooltime"), MesoExplosion.stackController(6*2*0.4, name = "메소 생성")])
        Assasinate1_D.onAfter(MesoExplosion.stackController(6*2*0.4, name = "메소 생성"))
        Assasinate1_D.onAfter(MesoExplosion)
        Assasinate1_D.onAfter(Assasinate2_D)
        
        BailOfShadow.onConstraint(DarkSightTurnedOn)
        BailOfShadow.onTick(MesoExplosion.stackController(0.4, name = "메소 생성"))
        BailOfShadow.onAfter(AdvancedDarkSight.controller(12000, "set_enabled_and_time_left"))
        
        Smoke.onConstraint(DarkSightTurnedOn)
        Smoke.onAfter(AdvancedDarkSight.controller(30000, "set_enabled_and_time_left"))
        
        UltimateDarksight.onConstraint(DarkSightTurnedOn)
        UltimateDarksight.onAfter(AdvancedDarkSight.controller(30000,"set_enabled_and_time_left" ))
        
        SonicBlowTick.onAfter(MesoExplosion.stackController(7*2*0.4, name = "메소 생성"))
        SonicBlow.onAfter(core.RepeatElement(SonicBlowTick, 15))
        
        Eviscerate.onAfter(MesoExplosion.stackController(7*2*0.4, name = "메소 생성"))
        
        Assasinate = core.OptionalElement(AdvancedDarkSight.is_active, Assasinate1_D, Assasinate1, name = "닼사 여부")
        BasicAttackWrapper = core.DamageSkill('기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(Assasinate)

        for sk in [Assasinate1, Assasinate2, Assasinate1_D, Assasinate2_D, Eviscerate, SonicBlowTick]:
            contrib.create_auxilary_attack(sk, 0.7, nametag = '(쉐도우파트너)')
        
        return(BasicAttackWrapper, 
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    Booster, FlipTheCoin, ShadowerInstinct, ShadowPartner, Smoke, AdvancedDarkSight, EpicAdventure, UltimateDarksight, 
                        ReadyToDie, globalSkill.soul_contract()] +\
                [Eviscerate, SonicBlow, BailOfShadow]+\
                [Venom]+\
                []+\
                [BasicAttackWrapper])