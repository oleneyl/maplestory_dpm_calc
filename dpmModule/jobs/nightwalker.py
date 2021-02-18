from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill, jobutils
from .jobclass import cygnus
from .jobbranch import thieves
from math import ceil
from typing import Any, Dict

class ShadowBatStackWrapper(core.StackSkillWrapper):
    def __init__(self, skill):
        self.BAT_SUMMON_DELAY = 960
        self.MAX_BAT = 5
        self.throwCount = 0
        self.stack = 0
        self.batQueue = []
        self.currentTime = 0
        super(ShadowBatStackWrapper, self).__init__(skill, self.MAX_BAT)
        
    def _add_throw(self):
        '''
        표창 사용 3회마다 배트를 1개씩 소환합니다.
        단, 소환중인 배트 + 소환된 배트의 수는 최대 5개 까지만 가능합니다.
        따라서 소환 큐에는 최대 (5 - 현재 스택) 개수까지만 들어갈 수 있습니다.
        '''
        self.throwCount = self.throwCount + 1
        if self.throwCount >= 3:
            self.throwCount -= 3
            if len(self.batQueue) < self._max - self.stack:
                self.batQueue = self.batQueue + [self.currentTime]
        return self._result_object_cache

    def add_throw(self):
        return core.TaskHolder(core.Task(self, self._add_throw), name="표창 사용 추가")

    def spend_time(self, time):
        '''
        매 시간마다 큐에서 960ms 이상 지난 원소들을 제거하고, 그만큼 스택에 추가합니다.
        '''
        self.currentTime += time
        batQueue = [x for x in self.batQueue if x + self.BAT_SUMMON_DELAY > self.currentTime]
        summonedBat = len(self.batQueue) - len(batQueue)
        self.stack = min(self.stack + summonedBat, self.MAX_BAT)
        self.batQueue = batQueue
        super(ShadowBatStackWrapper, self).spend_time(time)


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 9
        self.jobtype = "LUK"
        self.jobname = "나이트워커"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(boss_pdamage=51)
        
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트",stat_main = chtr.level // 2)
        ElementalHarmony = core.InformedCharacterModifier("엘리멘탈 하모니",patt = 10)

        ElementalDarkness = core.InformedCharacterModifier("엘리멘탈 : 다크니스", pdamage_indep=15)

        ThrowingMastery = core.InformedCharacterModifier("스로잉 마스터리",pdamage = 30)
        CriticalThrowing = core.InformedCharacterModifier("크리티컬 스로잉",crit = 35, crit_damage = 10)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 60)
        Adrenalin = core.InformedCharacterModifier("아드레날린",crit_damage = 10)

        ThrowingExpert = core.InformedCharacterModifier("스로잉 엑스퍼트",att = 30 + passive_level, crit_damage = 10 + ceil(passive_level/3))
        DarknessBlessing = core.InformedCharacterModifier("다크니스 블레싱",att = 30 + passive_level, armor_ignore = 15 + ceil(passive_level/2))

        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 3, 3)

        return [ElementalExpert, ElementalHarmony, ElementalDarkness, ThrowingMastery, CriticalThrowing, PhisicalTraining, 
            Adrenalin, ThrowingExpert, DarknessBlessing,
            ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 75)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=85+ceil(passive_level/2))

        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        하이퍼 스킬 : 
        퀸터플 스로우-리인포스, 보스킬러 / 사이펀 바이탈리티-리인포스 / 다크니스 오멘 2개
        
        V코어 : 9개
        퀸터플, 배트, 도미니언, 다크니스 오멘 : 1티어
        
        스피어 배트에도 발동
        매 퀸터플마다 스피어 1개
        
        점샷 가동률 100%
        
        퀸터-배트
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        JAVELIN_ATT = core.CharacterModifier(att=29)  # 플레임 표창
        JUMPRATE = options.get("jump_rate", 1)

        QUINTAPLE_MDF = core.CharacterModifier(pdamage=20, boss_pdamage=20) + JAVELIN_ATT
        RAPID_MDF = JAVELIN_ATT
        ######   Skill   ######

        ElementalDarkness = core.BuffSkill("엘리멘탈 : 다크니스", 0, 180000, armor_ignore = (4+1+1+1) * (2+1+1+1), att = 60).wrap(core.BuffSkillWrapper) # 펫버프, 사이펀 바이탈리티-리인포스 합산
        ElementalDarknessDOT = core.DotSkill("엘리멘탈 : 다크니스(도트)", 0, 1000, 80 + 40 + 50 + 50, 2+1+1+1, 100000000, cooltime = -1).wrap(core.DotSkillWrapper)
        Booster = core.BuffSkill("부스터", 0, 180000, rem  = True).wrap(core.BuffSkillWrapper) # 펫버프
        ShadowServent = core.BuffSkill("쉐도우 서번트", 990, 180000).wrap(core.BuffSkillWrapper) # 펫버프 등록불가
        SpiritThrowing = core.BuffSkill("스피릿 스로잉", 0, 180000, rem  = True).wrap(core.BuffSkillWrapper) # 펫버프

        ShadowBatStack = ShadowBatStackWrapper(core.BuffSkill("쉐도우 배트(스택)", 0, 0, cooltime=-1))
        ShadowBat = core.DamageSkill("쉐도우 배트", 0, 150 + 120 + 150 + 200 + 4*passive_level, 1).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        
        #점샷기준(400ms)
        QuintupleThrow = core.DamageSkill("퀸터플 스로우", (400 * JUMPRATE + 630 * (1-JUMPRATE)), 340+self.combat, 4, modifier=QUINTAPLE_MDF).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        QuintupleThrowFinal = core.DamageSkill("퀸터플 스로우(막타)", 0, 475+self.combat, 1, modifier=QUINTAPLE_MDF).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        QuintupleThrow_Sv = core.DamageSkill("퀸터플 스로우(서번트)", 0, (340+self.combat)*0.7, 4, modifier=QUINTAPLE_MDF).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        QuintupleThrowFinal_Sv = core.DamageSkill("퀸터플 스로우(서번트)(막타)", 0, (475+self.combat)*0.7, 1, modifier=QUINTAPLE_MDF).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        QuintupleThrow_I50 = core.DamageSkill("퀸터플 스로우(일루젼 50%)", 0, (340+self.combat)*0.5, 4, modifier=QUINTAPLE_MDF).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        QuintupleThrowFinal_I50 = core.DamageSkill("퀸터플 스로우(일루젼 50%)(막타)", 0, (475+self.combat)*0.5, 1, modifier=QUINTAPLE_MDF).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        QuintupleThrow_I30 = core.DamageSkill("퀸터플 스로우(일루젼 30%)", 0, (340+self.combat)*0.3, 4, modifier=QUINTAPLE_MDF).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        QuintupleThrowFinal_I30 = core.DamageSkill("퀸터플 스로우(일루젼 30%)(막타)", 0, (475+self.combat)*0.3, 1, modifier=QUINTAPLE_MDF).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        QuintupleThrow_V = core.DamageSkill("퀸터플 스로우(5차)", 0, (340+self.combat) * 0.01 * (25+vEhc.getV(0,0)), 4, modifier=QUINTAPLE_MDF).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        QuintupleThrowFinal_V = core.DamageSkill("퀸터플 스로우(5차)(막타)", 0, (475+self.combat) * 0.01 * (25+vEhc.getV(0,0)), 1, modifier=QUINTAPLE_MDF).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
    
        #하이퍼스킬
        ShadowElusion = core.BuffSkill("쉐도우 일루전", 690, 30000, cooltime = 180000).wrap(core.BuffSkillWrapper)
        Dominion = core.BuffSkill("도미니언", 1890, 30000, crit = 100, pdamage_indep = 20, cooltime = 180000).wrap(core.BuffSkillWrapper)
        DominionAttack = core.DamageSkill("도미니언(공격)", 0, 1000, 10, modifier=JAVELIN_ATT).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        GloryOfGuardians = core.BuffSkill("글로리 오브 가디언즈", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        CygnusPhalanx = cygnus.PhalanxChargeWrapper(vEhc, 4, 4)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 3, 3)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        ShadowSpear = core.BuffSkill("쉐도우 스피어", 600, (50+vEhc.getV(0,0))*1000, red = True, cooltime = int(181 - vEhc.getV(0,0) / 2)*1000).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        ShadowSpearSmall = core.DamageSkill("쉐도우 스피어(창)", 0, 100+4*vEhc.getV(0,0), 4).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ShadowSpearLarge = core.SummonSkill("쉐도우 스피어(거대 창)", 0, 3000, 400 + 16*vEhc.getV(0,0), 6, (50+vEhc.getV(0,0))*1000 - 1, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)

        ShadowServentExtend = core.BuffSkill("쉐도우 서번트 익스텐드", 570, (30+vEhc.getV(1,1)//2)*1000, red = True, cooltime = 60000).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)

        ShadowBite = core.DamageSkill("쉐도우 바이트", 630, 600+24*vEhc.getV(2,2), 14, red = True, cooltime = 15000).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        ShadowBiteBuff = core.BuffSkill("쉐도우 바이트(버프)", 0, (10+vEhc.getV(2,2)//3)*1000, pdamage_indep = (8+vEhc.getV(2,2)//3), cooltime = -1).isV(vEhc,2,2).wrap(core.BuffSkillWrapper)

        RapidThrowInit = core.DamageSkill("래피드 스로우(개시)", 120, 0, 0, cooltime=90000, red=True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)

        # 22회 반복
        RapidThrow = core.DamageSkill("래피드 스로우", 180, 475+19*vEhc.getV(0,0), 5, cooltime=-1, modifier=RAPID_MDF).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        RapidThrow_Sv = core.DamageSkill("래피드 스로우(서번트)", 0, (475+19*vEhc.getV(0,0))*0.7, 5, cooltime=-1, modifier=RAPID_MDF).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        RapidThrow_I50 = core.DamageSkill("래피드 스로우(일루젼 50%)", 0, (475+19*vEhc.getV(0,0))*0.5, 5, cooltime=-1, modifier=RAPID_MDF).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        RapidThrow_I30 = core.DamageSkill("래피드 스로우(일루젼 30%)", 0, (475+19*vEhc.getV(0,0))*0.3, 5, cooltime=-1, modifier=RAPID_MDF).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        RapidThrow_V = core.DamageSkill("래피드 스로우(5차)", 0, (475+19*vEhc.getV(0,0)) * 0.01 * (25+vEhc.getV(0,0)), 5, cooltime=-1, modifier=RAPID_MDF).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)

        RapidThrowFinal = core.DamageSkill("래피드 스로우(막타)", 480, 850+34*vEhc.getV(0,0), 13, cooltime=-1, modifier=RAPID_MDF).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        RapidThrowFinal_Sv = core.DamageSkill("래피드 스로우(막타)(서번트)", 0, (850+34*vEhc.getV(0,0))*0.7, 13, cooltime=-1, modifier=RAPID_MDF).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        RapidThrowFinal_I50 = core.DamageSkill("래피드 스로우(막타)(일루젼 50%)", 0, (850+34*vEhc.getV(0,0))*0.5, 13, cooltime=-1, modifier=RAPID_MDF).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        RapidThrowFinal_I30 = core.DamageSkill("래피드 스로우(막타)(일루젼 30%)", 0, (850+34*vEhc.getV(0,0))*0.3, 13, cooltime=-1, modifier=RAPID_MDF).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        RapidThrowFinal_V = core.DamageSkill("래피드 스로우(막타)(5차)", 0, (850+34*vEhc.getV(0,0)) * 0.01 * (25+vEhc.getV(0,0)), 13, cooltime=-1, modifier=RAPID_MDF).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ######   Skill Wrapper   ######

        ElementalDarkness.onAfter(ElementalDarknessDOT)
        ShadowBat.onAfter(ShadowBatStack.stackController(-1))
        AddBat = ShadowBatStack.add_throw()
        UseBat = core.RepeatElement(core.OptionalElement(partial(ShadowBatStack.judge, 1, 1), ShadowBat, name = "배트 사출가능 여부"), 5)

        ShadowSpearTick = core.OptionalElement(ShadowSpear.is_active, ShadowSpearSmall, name = "스피어ON")
        ShadowSpear.onAfter(ShadowSpearLarge)
        ShadowBat.onAfter(ShadowSpearTick)

        for start, end in [[QuintupleThrow, QuintupleThrowFinal],
                            [QuintupleThrow_Sv, QuintupleThrowFinal_Sv],
                            [QuintupleThrow_I50, QuintupleThrowFinal_I50],
                            [QuintupleThrow_I30, QuintupleThrowFinal_I30],
                            [QuintupleThrow_V, QuintupleThrowFinal_V]]:
            
            start.onAfter(end)
            start.onAfter(AddBat)
            end.onAfter(AddBat)
        
        for sk in [QuintupleThrowFinal, QuintupleThrow_Sv, QuintupleThrowFinal_Sv,
                    QuintupleThrow_I50, QuintupleThrowFinal_I50, QuintupleThrow_I30, QuintupleThrowFinal_I30,
                    QuintupleThrow_V, QuintupleThrowFinal_V, RapidThrow, RapidThrow_Sv, RapidThrow_I50, RapidThrow_I30, RapidThrow_V,
                    RapidThrowFinal, RapidThrowFinal_Sv, RapidThrowFinal_I50, RapidThrowFinal_I30, RapidThrowFinal_V, ShadowBite, DominionAttack]:
            
            sk.onAfter(ShadowSpearTick)
        
        QuintupleThrow.onAfter(UseBat)
        QuintupleThrow_I50_Use = core.OptionalElement(ShadowElusion.is_active, QuintupleThrow_I50, name = "일루전 여부")
        QuintupleThrow_I30_Use = core.OptionalElement(ShadowElusion.is_active, QuintupleThrow_I30, name = "일루전 여부")
        QuintupleThrow_V_Use = core.OptionalElement(ShadowServentExtend.is_active, QuintupleThrow_V, name = "익스텐드 여부")
        QuintupleThrow.onAfters([QuintupleThrow_Sv, QuintupleThrow_I50_Use, QuintupleThrow_I30_Use, QuintupleThrow_V_Use])

        # 래피드 스로우
        for sk in [RapidThrow, RapidThrow_Sv, RapidThrow_I50, RapidThrow_I30, RapidThrow_V,
                    RapidThrowFinal, RapidThrowFinal_Sv, RapidThrowFinal_I50, RapidThrowFinal_I30, RapidThrowFinal_V]:
            sk.onAfter(AddBat)
        RapidThrow.onAfter(RapidThrow_Sv)
        RapidThrow.onAfter(core.OptionalElement(ShadowElusion.is_active, RapidThrow_I50, name = "일루전 여부"))
        RapidThrow.onAfter(core.OptionalElement(ShadowElusion.is_active, RapidThrow_I30, name = "일루전 여부"))
        RapidThrow.onAfter(core.OptionalElement(ShadowServentExtend.is_active, RapidThrow_V, name = "익스텐드 여부"))
        RapidThrow.onAfter(UseBat)
        RapidThrowFinal.onAfter(RapidThrowFinal_Sv)
        RapidThrowFinal.onAfter(core.OptionalElement(ShadowElusion.is_active, RapidThrowFinal_I50, name = "일루전 여부"))
        RapidThrowFinal.onAfter(core.OptionalElement(ShadowElusion.is_active, RapidThrowFinal_I30, name = "일루전 여부"))
        RapidThrowFinal.onAfter(core.OptionalElement(ShadowServentExtend.is_active, RapidThrowFinal_V, name = "익스텐드 여부"))
        RapidThrowFinal.onAfter(UseBat)
        RapidThrowInit.onAfter(core.RepeatElement(RapidThrow, 18))
        RapidThrowInit.onAfter(RapidThrowFinal)

        #도미니언
        Dominion.onAfter(DominionAttack)
        #쉐도우 바이트
        ShadowBite.onEventElapsed(ShadowBiteBuff, 2000)
                
        return( QuintupleThrow,
                [globalSkill.maple_heros(chtr.level, name = "시그너스 나이츠", combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    ElementalDarkness, Booster, ShadowServent, SpiritThrowing, ShadowBatStack,
                    ShadowElusion, ReadyToDie, Dominion, cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level),
                    GloryOfGuardians, ShadowSpear, ShadowServentExtend, ShadowBite, ShadowBiteBuff,
                    globalSkill.soul_contract()] +\
                [RapidThrowInit, CygnusPhalanx, MirrorBreak, MirrorSpider] +\
                [ElementalDarknessDOT, ShadowSpearLarge] +\
                [] +\
                [QuintupleThrow])