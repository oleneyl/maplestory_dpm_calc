from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobclass import cygnus
from .jobbranch import thieves
#TODO : 5차 신스킬 적용

######   Passive Skill   ######



class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 9
        self.jobtype = "luk"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1
        
    def get_passive_skill_list(self):
        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트",stat_main = self.chtr.level // 2)
        ElementalHarmony = core.InformedCharacterModifier("엘리멘탈 하모니",patt = 10)

        ThrowingMastery = core.InformedCharacterModifier("스로잉 마스터리",pdamage = 30)
        CriticalThrowing = core.InformedCharacterModifier("크리티컬 스로잉",crit = 35, crit_damage = 10)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 60)
        Adrenalin = core.InformedCharacterModifier("아드레날린",crit_damage = 10)

        ThrowingExpert = core.InformedCharacterModifier("스로잉 엑스퍼트",att = 30, crit_damage = 10)
        DarknessBlessing = core.InformedCharacterModifier("다크니스 블레싱",att = 30, armor_ignore = 15)

        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(self.vEhc, 3, 3)

        return [ElementalExpert, ElementalHarmony, ThrowingMastery, CriticalThrowing, PhisicalTraining, 
            Adrenalin, ThrowingExpert, DarknessBlessing,
            ReadyToDiePassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 75)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5)    #오더스 기본적용!
        
        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        하이퍼 스킬 : 
        퀸터플 3종 + 다크니스 오멘 2개
        
        V코어 : 9개
        퀸터플, 배트, 도미니언, 다크니스 오멘 : 1티어
        
        스피어 배트에도 발동
        매 퀸터플마다 스피어 1개
        
        점샷 가동률 100%
        배트 사출률 0.22 (0.333이 아님)
        
        퀸터-배트
        '''
        ######   Skill   ######

        JUMPRATE = 1
        BATRATE = 0.3333

        ElementalDarkness = core.BuffSkill("엘리멘탈 : 다크니스", 900, 180000, armor_ignore = (4+1+1+1) * (2+1+1+1)).wrap(core.BuffSkillWrapper)
        ElementalDarknessDOT = core.DotSkill("엘리멘탈 : 다크니스(도트)", (80 + 40 + 50 + 50) * (2+1+1+1), 100000000).wrap(core.SummonSkillWrapper)
        Heist = core.BuffSkill("헤이스트", 0, 180000, rem  = True).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill("부스터", 0, 180000, rem  = True).wrap(core.BuffSkillWrapper) # 펫버프
        ShadowServent = core.BuffSkill("쉐도우 서번트", 0, 180000).wrap(core.BuffSkillWrapper) # 펫버프
        SpiritThrowing = core.BuffSkill("스피릿 스로잉", 0, 180000, rem  = True).wrap(core.BuffSkillWrapper) # 펫버프
        
        ShadowBat = core.DamageSkill("쉐도우 배트", 0, 150 + 120 + 150 + 200, BATRATE).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)  #3회 공격당 1번 소환
        
        #점샷기준(400ms)
        QuintupleThrow = core.DamageSkill("퀸터플 스로우", (400 * JUMPRATE + 630 * (1-JUMPRATE)), 340, 4, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, crit = 10, pdamage_indep = (JUMPRATE*15))).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        QuintupleThrowFinal = core.DamageSkill("퀸터플 스로우(막타)", 0, 475, 1, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, crit = 10, pdamage_indep = (JUMPRATE*15))).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        QuintupleThrow_Sv = core.DamageSkill("퀸터플 스로우(서번트)", 0, 340*0.7, 4, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, crit = 10, pdamage_indep = (JUMPRATE*15))).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        QuintupleThrowFinal_Sv = core.DamageSkill("퀸터플 스로우(서번트)(막타)", 0, 475*0.7, 1, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, crit = 10, pdamage_indep = (JUMPRATE*15))).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        QuintupleThrow_I = core.DamageSkill("퀸터플 스로우(일루젼)", 0, 340*1.5, 4, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, crit = 10, pdamage_indep = (JUMPRATE*15))).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        QuintupleThrowFinal_I = core.DamageSkill("퀸터플 스로우(일루젼)(막타)", 0, 475*1.5, 1, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, crit = 10, pdamage_indep = (JUMPRATE*15))).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        QuintupleThrow_V = core.DamageSkill("퀸터플 스로우(5차)", 0, 340 * 0.01 * (20+vEhc.getV(0,0)), 4, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, crit = 10, pdamage_indep = (JUMPRATE*15))).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        QuintupleThrowFinal_V = core.DamageSkill("퀸터플 스로우(5차)(막타)", 0, 475 * 0.01 * (20+vEhc.getV(0,0)), 1, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, crit = 10, pdamage_indep = (JUMPRATE*15))).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
    
        #하이퍼스킬
        ShadowElusion = core.BuffSkill("쉐도우 일루전", 690, 30000, cooltime = 180000).wrap(core.BuffSkillWrapper)
        Dominion = core.BuffSkill("도미니언", 1890, 30000, crit = 100, pdamage_indep = 20, cooltime = 180000).wrap(core.BuffSkillWrapper)
        DominionAttack = core.DamageSkill("도미니언(공격)", 0, 1000, 10).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        GloryOfGuardians = core.BuffSkill("글로리 오브 가디언즈", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        CygnusPalanks = cygnus.PhalanxChargeWrapper(vEhc, 4, 4)

        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 3, 3)

        ShadowSpear = core.BuffSkill("쉐도우 스피어", 600, (50+vEhc.getV(0,0))*1000, red = True, cooltime = int(181 - vEhc.getV(0,0) / 2)*1000).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        ShadowSpearSmall = core.DamageSkill("쉐도우 스피어(창)", 0, 100+4*vEhc.getV(0,0), 4).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ShadowSpearSmallBat = core.DamageSkill("쉐도우 스피어(창)(배트)", 0, 100+4*vEhc.getV(0,0), 4.0*BATRATE).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ShadowSpearLarge = core.SummonSkill("쉐도우 스피어(거대 창)", 0, 3000, 400 + 16*vEhc.getV(0,0), 6, (50+vEhc.getV(0,0))*1000 - 1, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)

        ShadowServentExtend = core.BuffSkill("쉐도우 서번트 익스텐드", 570, (30+vEhc.getV(1,1)//2)*1000, red = True, cooltime = 60000).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)

        ShadowBite = core.DamageSkill("쉐도우 바이트", 630, 600+24*vEhc.getV(2,2), 14, red = True, cooltime = 20000).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        ShadowBiteBuff = core.BuffSkill("쉐도우 바이트(버프)", 0, (15+vEhc.getV(2,2)//10)*1000, pdamage_indep = (8+vEhc.getV(2,2)//4), cooltime = -1).isV(vEhc,2,2).wrap(core.BuffSkillWrapper)
        ######   Skill Wrapper   ######

        #_VenomBurst = core.DamageSkill("베놈 버스트", ??) ## 패시브 50%확률로 10초간 160+6*vlevel dot. 사용시 도트뎀 모두 피해 + (500+20*vlevel) * 5. 어차피 안쓰는 스킬이므로 작성X

        ShadowSpearTickBat = core.OptionalElement(ShadowSpear.is_active, ShadowSpearSmallBat, name = "스피어ON")
        ShadowSpearTick = core.OptionalElement(ShadowSpear.is_active, ShadowSpearSmall, name = "스피어ON")
        ShadowSpear.onAfter(ShadowSpearLarge)

        for start, end in [[QuintupleThrow, QuintupleThrowFinal],
                            [QuintupleThrow_Sv, QuintupleThrowFinal_Sv],
                            [QuintupleThrow_I, QuintupleThrowFinal_I],
                            [QuintupleThrow_V, QuintupleThrowFinal_V]]:
            
            start.onAfter(end)
            for i in [start, end]:
                i.onAfter(ShadowBat)
                i.onAfter(ShadowSpearTick)
        
        #ShadowBat.onAfter(ShadowSpearTickBat)
        
        QuintupleThrow_Shadow = core.OptionalElement(ShadowElusion.is_active, QuintupleThrow_I, QuintupleThrow_Sv, name = "일루전 여부")
        QuintupleThrow_V_Use = core.OptionalElement(ShadowServentExtend.is_active, QuintupleThrow_V, name = "익스텐드 여부")
        QuintupleThrow.onAfters([QuintupleThrow_Shadow, QuintupleThrow_V_Use])

        #도미니언
        Dominion.onAfter(DominionAttack)
        #쉐도우 바이트
        ShadowBite.onAfter(ShadowBiteBuff.controller(2000))
                
        return( QuintupleThrow,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    ElementalDarkness, Heist, Booster, ShadowServent, SpiritThrowing, 
                    ShadowElusion, ReadyToDie, Dominion, GloryOfGuardians, ShadowSpear, ShadowServentExtend, ShadowBite, ShadowBiteBuff,
                    globalSkill.soul_contract()] +\
                [CygnusPalanks] +\
                [ElementalDarknessDOT, ShadowSpearLarge] +\
                [] +\
                [QuintupleThrow])