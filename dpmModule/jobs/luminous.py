from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobclass import heroes
from .jobbranch import magicians
'''아포 22회
라리플 25회
'''
# TODO: 시전 딜레이 패치 적용

class LuminousStateController(core.BuffSkillWrapper):
    DARK = 0
    LIGHT = 1
    EQUAL = 2
    STACK = 550
    def __init__(self, skill, ch : ck.AbstractCharacter, combat = True):
        super(LuminousStateController, self).__init__(skill)
        self.state = LuminousStateController.LIGHT
        self.currentState = LuminousStateController.LIGHT
        self.stack = LuminousStateController.STACK
        
        self.remain = 0
        self.buff_rem = ch.buff_rem
        self.stackList = [25, 22, 0]
        self.equalCallback = lambda:None
        self.absoluteKillCallback = lambda:None
        
    def spend_time(self, time : int) -> None:
        super(LuminousStateController, self).spend_time(time)
        self.remain -= time
        #이퀄이 끝나면, 다음 상태로 진입합니다.
        if self.remain < 0 and self.state == LuminousStateController.EQUAL:
            self.state = 1 - self.currentState
            self.stack = LuminousStateController.STACK

    def _modify_stack(self, stack):
        self.stack -= self.stackList[self.state]
        
        if self.stack <= 0:
            self.stack = LuminousStateController.STACK
            self.currentState = self.state
            self.state = LuminousStateController.EQUAL
            self.remain = 17 * (1 + 0.01* self.buff_rem) * 1000  #오더스?
            self.equalCallback()
            
        return core.ResultObject(0, core.CharacterModifier(),  0, '루미너스 스택 변경')     
    
    def memorize(self):
        if self.state != LuminousStateController.EQUAL:
            self.currentState = self.state
        self.remain = 17*1000
        self.state = LuminousStateController.EQUAL
        self.equalCallback()
        return core.ResultObject(0, core.CharacterModifier(), 0, sname = '메모라이즈', spec = 'graph control')
        
    def memorizeNode(self):
        task = core.Task(self, self.memorize)
        return core.TaskHolder(task, "메모라이즈")    
    
    def modifyStack(self, stack):
        return core.create_task('스택 변경', partial(self._modify_stack, stack), self)

    def getState(self):
        return self.state
    
    def isState(self, state):
        return (self.state == state)
    
    def isNotEqual(self):
        return (self.state != LuminousStateController.EQUAL)
        



class PunishingResonatorWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, stateGetter):
        super(PunishingResonatorWrapper, self).__init__(skill = core.SummonSkill("퍼니싱 리소네이터", 0, 0, 0, 0, 0))
        self.skillList = [core.SummonSkill("퍼니싱 리소네이터(어둠)", 990, 6000/28, 250 + vEhc.getV(3,2)*10, 5, 6000-1, cooltime = 30 * 1000, modifier = core.CharacterModifier(crit = 15)).isV(vEhc,3,2),
                        core.SummonSkill("퍼니싱 리소네이터(빛)", 990, 6000/28, 350 + vEhc.getV(3,2)*14, 4, 6000-1, cooltime = 30 * 1000, modifier = core.CharacterModifier(crit = 15)).isV(vEhc,3,2),
                        core.SummonSkill("퍼니싱 리소네이터(이퀄)", 990, 6000/28, 340 + vEhc.getV(3,2)*13, 6, 6000-1, cooltime = 30 * 1000, modifier = core.CharacterModifier(crit = 15)).isV(vEhc,3,2)]
        self.vlevel = vEhc.getV(3,2)
        self.getState = stateGetter

    def _use(self, rem = 0, red = 0):
        self.skill = self.skillList[self.getState()]
        return super(PunishingResonatorWrapper, self)._use()

class LightAndDarknessWrapper(core.DamageSkillWrapper):
    def __init__(self, vEhc):
        super(LightAndDarknessWrapper, self).__init__(skill = core.DamageSkill("빛과 어둠의 세례", 840, 15 * vEhc.getV(1,1)+375, 13 * 7, cooltime = 45*1000, modifier = core.CharacterModifier(armor_ignore = 100, crit = 100)).isV(vEhc,1,1))
        self.stack = 12
        self.vlevel = vEhc.getV(1,1)

    def _use(self, rem = 0, red = 0):
        self.stack = 12
        return super(LightAndDarknessWrapper, self)._use()

    def reduceStack(self):
        self.stack -= 1
        if self.stack <= 0:
            self.cooltimeLeft = 0
            self.available = True
        return core.ResultObject(0, core.CharacterModifier(), 0, sname = '빛과 어둠의 세례 스택 증가', spec = 'graph control')            
            
    def reduceStackNode(self):
        return core.TaskHolder(core.Task(self, self.reduceStack))



class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = True
        self.vEnhanceNum = 13
        self.jobtype = "int"
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'crit', 'boss_pdamage')
        self.preEmptiveSkills = 2
        
    def apply_complex_options(self, chtr):
        chtr.add_property_ignorance(10)
        
    def get_passive_skill_list(self):

        PowerOfLight = core.InformedCharacterModifier("파워 오브 라이트",stat_main = 20)
        SpellMastery =  core.InformedCharacterModifier("스펠 마스터리",att = 10)
        HighWisdom =  core.InformedCharacterModifier("하이 위즈덤",stat_main = 40)
        LifeTidal = core.InformedCharacterModifier("라이프 타이달",crit = 30) #OR pdamage = 20
        MagicMastery = core.InformedCharacterModifier("매직 마스터리",att = 30, crit_damage = 15, crit = 15)  #오더스 적용필요
        DarknessSocery = core.InformedCharacterModifier("다크니스 소서리", pdamage_indep = 40, armor_ignore = 40)
        MorningStarfall = core.InformedCharacterModifier("모닝 스타폴(패시브)",pdamage_indep = 30)
        
        return [PowerOfLight, SpellMastery, HighWisdom, LifeTidal, MagicMastery, MorningStarfall, DarknessSocery]

    def get_not_implied_skill_list(self): 
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -2.5)
        
        BlessOfDarkness =  core.InformedCharacterModifier("블레스 오브 다크니스",att = 30)   #15 -> 24 -> 30

        return [WeaponConstant, Mastery, BlessOfDarkness]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        아포 22회 / 라리플 25회가 이퀄리브리엄 진입까지 요구됨
        
        소울 컨트랙트는 이퀄리브리엄에 상관없이 사용
        빛, 어둠 상태에서도 쿨마다 앱솔루트 킬을 사용
        메모라이즈는 이퀄이 아니고 쿨타임이 돌아 있으면 사용
        '''
        ######   Skill   ######

        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper)    #딜레이 모름
        PodicMeditaion = core.BuffSkill("포딕 메디테이션", 0, 1800000, att = 40).wrap(core.BuffSkillWrapper)
        DarkCrescendo = core.BuffSkill("다크 크레센도", 780, 180 * 1000, pdamage = 28, rem = True).wrap(core.BuffSkillWrapper)#<- 제대로 계산 필요함. 딜레이 모름
        DarknessSocery = core.BuffSkill("다크니스 소서리(버프)", 780, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper)    #딜레이 모름
        HerosOath = core.BuffSkill("히어로즈 오쓰", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10, rem = True).wrap(core.BuffSkillWrapper)
        Memorize = core.BuffSkill("메모라이즈", 600, 10, cooltime = 150 * 1000, rem = True).wrap(core.BuffSkillWrapper)#Memorize <- 역시 제대로 계산 필요함. 딜레이 모음
    
        OverloadMana = OverloadMana = magicians.OverloadManaWrapper(vEhc, 2, 3)
    
        #Damage Skills

        DoorOfTruth = core.SummonSkill("진리의 문", 870, 3030, 375 + 15 * vEhc.getV(4,4), 10, (25 + 0.5*vEhc.getV(4,4)) * 1000, cooltime = -1).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)   #이퀄시 사용 가능해짐.

        Frid = heroes.FridWrapper(vEhc, 0, 0)
        LightAndDarkness = LightAndDarknessWrapper(vEhc)
    
        LuminousState = LuminousStateController(core.BuffSkill("루미너스 상태", 0, 99999999), chtr)
        
        LuminousState.equalCallback = partial(DoorOfTruth.set_disabled_and_time_left, 1)
        
        Attack = core.DamageSkill('기본 공격', 0, 0, 0).wrap(core.DamageSkillWrapper)
        
        
        LightReflection = core.DamageSkill("라이트 리플렉션", 780, 400, 4 * 1.5, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        Apocalypse = core.DamageSkill("아포칼립스", 1140, 340, 7 * 1.5,modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AbsoluteKill = core.DamageSkill("앱솔루트 킬", 600, 385, 7*2,modifier = core.CharacterModifier(pdamage = 20, crit = 100, armor_ignore=40)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        AbsoluteKillCooltimed = core.DamageSkill('앱솔루트 킬(쿨타임)', 600, 385, 7*2, cooltime = 12000, modifier = core.CharacterModifier(pdamage = 20, crit = 100, armor_ignore=40)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        LightReflection.onAfter(LuminousState.modifyStack(22))
        Apocalypse.onAfter(LuminousState.modifyStack(25))
        
        IsLight = core.OptionalElement(partial(LuminousState.isState, LuminousStateController.LIGHT), LightReflection, Apocalypse, name = '빛이면 라리플 사용')
        IsEqual = core.OptionalElement(partial(LuminousState.isState, LuminousStateController.EQUAL), AbsoluteKill, IsLight, name = '이퀄리브리엄이면 이퀄 사용')
        Attack.onAfter(IsEqual)
        
        for absolute in [AbsoluteKillCooltimed, AbsoluteKill]:
            absolute.onAfter(core.create_task('빛과 어둠의 세례 쿨다운 감소', LightAndDarkness.reduceStack, LightAndDarkness))
        
        Memorize.onAfter(core.create_task("메모라이즈", LuminousState.memorize, LuminousState))
        PunishingResonator = PunishingResonatorWrapper(vEhc, LuminousState.getState)
        
        
        Memorize.onConstraint(core.ConstraintElement('이퀄일때는 사용하지 않음', LuminousState, LuminousState.isNotEqual ) ) 

        SoulContract = globalSkill.soul_contract()

        return(Attack, 
                [LuminousState, globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster(),
                    Booster, PodicMeditaion, DarknessSocery, DarkCrescendo, HerosOath, Memorize, Frid, OverloadMana,
                    SoulContract] +\
                [LightAndDarkness, AbsoluteKillCooltimed] +\
                [PunishingResonator, DoorOfTruth] +\
                [] +\
                [Attack])