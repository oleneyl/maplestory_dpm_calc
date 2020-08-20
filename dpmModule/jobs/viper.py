from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import pirates
from .jobclass import adventurer
from . import jobutils
#TODO : 5차 신스킬 적용

class EnergyChargeWrapper(core.StackSkillWrapper):
    def __init__(self):
        skill = core.BuffSkill("에너지차지 발동", 0, 999999*1000)
        super(EnergyChargeWrapper, self).__init__(skill, 10000)
        self.stack = 0
        self._st = 0

    def vary(self, val, force = False):
#        print(" State : %d, %d \n vary %d" % (self.stack, self._st, val))
        if (force or not self._st) and val > 0:
            self.stack += val
        elif val < 0:
            self.stack += val
            
        if self._st and self.stack <= 0:
            self.turnOff()
        elif (not self._st) and self.stack >= 10000:
            self.turnOn()
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname = self.skill.name, spec = 'graph control')
            
    def turnOn(self):
        self.stack = 10000
        self.skill.att = 50
        self._st = 1

    def turnOff(self):
        self.stack = 0
        self.skill.att = 25
        self._st = 0       

    def isStateOn(self):
        return self._st


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 10
        self.jobtype = "str"
        self.jobname = "바이퍼"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_passive_skill_list(self):
        CriticalRoar = core.InformedCharacterModifier("크리티컬 로어",crit = 20, crit_damage = 5)
        
        MentalClearity = core.InformedCharacterModifier("멘탈 클리어리티",att = 30)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        
        CriticalRage = core.InformedCharacterModifier("크리티컬 레이지",crit = 15, crit_damage = 10)    #보스상대 추가+20% 크리율
        
        StimulatePassive = core.InformedCharacterModifier("스티뮬레이트(패시브)",boss_pdamage = 20)
        
        EchoOfHero = core.InformedCharacterModifier("영웅의 메아리", patt = 4) #타임리프

        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(self.vEhc, 2, 3)
        
        return [CriticalRoar, MentalClearity, PhisicalTraining, CriticalRage, StimulatePassive, EchoOfHero, LoadedDicePassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)

        CriticalRage = core.InformedCharacterModifier("크리티컬 레이지(준액티브)",crit = 20)    #보스상대 추가+20% 크리율
        GuardCrush = core.InformedCharacterModifier("가드 크러시",armor_ignore = 40) #40% 확률로 방무 100% 무시.
        CounterAttack = core.InformedCharacterModifier("카운터 어택",pdamage = 25)  #피격시 25%로발동.
        
        
        return [WeaponConstant, Mastery, CriticalRage, GuardCrush, CounterAttack]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        울트라 차지 : 공격시 350충전, 최대 차지시 공50, 보스공격시 2배 충전. 최대스택 10000.

        인레이지-노틸-드스-유니티
        '''
        ######   Skill   ######
        serverlag = 3

        LuckyDice = core.BuffSkill("로디드 다이스", 600, 180 * 1000, pdamage = 20 *4/3).isV(vEhc, 2, 2).wrap(core.BuffSkillWrapper)#딜레이 모름
        #1중첩 럭다 재사용 50초 감소 / 방어력30% / 체엠 20% / 크리율15% / 뎀증20 / 경치30
        #2중첩 럭다 재사용 50초 감소 / 방어력40% / 체엠 30% / 크리율25% / 뎀증30 / 경치40
        #7 발동시 방무 20 -> 30
        Viposition = core.BuffSkill("바이퍼지션", 0, 180 * 1000, patt = 30).wrap(core.BuffSkillWrapper)
        Stimulate = core.BuffSkill("스티뮬레이트", 930, 120 * 1000, cooltime = 240 * 1000, pdamage = 20).wrap(core.BuffSkillWrapper)# 에너지 주기적으로 800씩 증가, 미완충시 풀완충.
        StimulateSummon = core.SummonSkill("스티뮬레이트(게이지 증가 더미)", 0, (5 + serverlag) * 1000, 0, 0, 120 * 1000).wrap(core.SummonSkillWrapper)
        
        UnityOfPower = core.DamageSkill("유니티 오브 파워", 1080, 650, 5, cooltime = 90000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)   #완충시에만 사용 가능, 에너지 1500 소모.
        UnityOfPowerBuff = core.BuffSkill("유니티 오브 파워(디버프)", 0, 90 * 1000, cooltime = -1, crit_damage = 40).wrap(core.BuffSkillWrapper)   #4스택 가정.
        #크리티컬 리인포스 - >재정의 필요함..
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)

        PirateFlag = PirateFlag = adventurer.PirateFlagWrapper(vEhc, 3, 2, chtr.level)
        
        #오버드라이브 (앱솔 가정)
        #TODO: 템셋을 읽어서 무기별로 다른 수치 적용하도록 만들어야 함.
        WEAPON_ATT = jobutils.get_weapon_att("너클")
        Overdrive, OverdrivePenalty = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
        
        Transform = core.BuffSkill("트랜스 폼", 450, (50+vEhc.getV(1,1))*1000, cooltime = 180 * 1000, pdamage_indep = (20 + 0.2*vEhc.getV(1,1))).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)#에너지 완충
        TransformEnergyOrb = core.DamageSkill("에너지 오브", 1140, 450 +vEhc.getV(1,1)*18, (2+(vEhc.getV(1,1) == 25)*1) * 8, modifier = core.CharacterModifier(crit = 50, armor_ignore = 50)).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
    
        FistInrage = core.DamageSkill("피스트 인레이지", 690, 320, 8 + 1, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        FistInrage_T = core.DamageSkill("피스트 인레이지(변신)", 690, 320, 8 + 1 + 2, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)#완충시 10번 공격
        
        DragonStrike = core.DamageSkill("드래곤 스트라이크", 690, 300, 12, cooltime = 15 * 1000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        DragonStrikeBuff = core.BuffSkill("드래곤 스트라이크(디버프)", 0, 15 * 1000, cooltime = -1, pdamage_indep = 20).wrap(core.BuffSkillWrapper)
        
        Nautilus = core.DamageSkill("노틸러스", 690, 440, 7, cooltime = 60 * 1000).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        NautilusBuff = core.BuffSkill("노틸러스(버프)", 0, 60 * 1000, cooltime = -1).wrap(core.BuffSkillWrapper)
        NautilusFinalAttack = core.DamageSkill("노틸러스(파이널 어택)", 0, 165, 2).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        
        SerpentScrew = core.SummonSkill("서펜트 스크류", 600, 285, 360 + vEhc.getV(0,0)*14, 3, 99999 * 10000).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)    #보스 공격시 에너지 소모량 70% 감소, 틱당 에너지 85 소모.
        SerpentScrewDummy = core.SummonSkill("서펜트 스크류(지속)", 0, 1000, 0, 0, 99999 * 10000, cooltime = -1).wrap(core.SummonSkillWrapper)   #초당 에너지 60 소모 #보스 공격시 에너지 소모량 70% 감소, 틱당 에너지 85 소모.
        SerpentScrewTrackingBuff = core.BuffSkill("서펜트 스크류(On)", 0, 999999999, cooltime = -1).wrap(core.BuffSkillWrapper)
    
        FuriousCharge = core.DamageSkill("퓨리어스 차지", 540, 600+vEhc.getV(4,4)*24, 10, cooltime = 10 * 1000, modifier = core.CharacterModifier(boss_pdamage = 30)).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
        ######   Skill Wrapper   ######
        EnergyCharge = EnergyChargeWrapper()
        EnergyCharge.set_name_style("게이지 %d만큼 변화")
        #1중첩 럭다 재사용 50초 감소 / 방어력30% / 체엠 20% / 크리율15% / 뎀증20 / 경치30
        #2중첩 럭다 재사용 50초 감소 / 방어력40% / 체엠 30% / 크리율25% / 뎀증30 / 경치40
        #7 발동시 방무 20 -> 30
        
        Stimulate.onAfter(EnergyCharge.stackController(10000, name = "스티뮬레이트"))
        Stimulate.onAfter(StimulateSummon)
    
        UnityOfPower.onAfter(EnergyCharge.stackController(-1500))
        UnityOfPower.onAfter(UnityOfPowerBuff)
        
        Transform.onAfter(EnergyCharge.stackController(10000, name = "트랜스 폼"))
        Transform.onAfter(core.RepeatElement(TransformEnergyOrb, 3))
    
        Nautilus.onAfter(NautilusBuff)
    
        FinalAttack = core.OptionalElement(NautilusBuff.is_active, NautilusFinalAttack)
    
        FistInrage.onAfter(NautilusFinalAttack)
        FistInrage.onAfter(EnergyCharge.stackController(700))
        FistInrage_T.onAfter(NautilusFinalAttack)
        FistInrage_T.onAfter(EnergyCharge.stackController(-150))
        
        BasicAttack = core.OptionalElement(EnergyCharge.isStateOn, FistInrage_T, FistInrage)
        BasicAttackWrapper = core.DamageSkill('기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)
        DragonStrike.onAfter(EnergyCharge.stackController(-180))
        DragonStrike.onAfter(DragonStrikeBuff)
        
        SerpentScrewDummy.onTick(EnergyCharge.stackController(-60*0.3))
        SerpentScrew.onTick(EnergyCharge.stackController(-85*0.3))
        SerpentScrew.onAfter(SerpentScrewDummy)
        SerpentScrew.onAfter(SerpentScrewTrackingBuff)  #디버깅용
        
        SerpentScrewOff = SerpentScrew.controller(150, name = "서펜트 스크류 사용 종료")
        SerpentScrewOff.onAfter(SerpentScrewDummy.controller(-1))
        SerpentScrewOff.onAfter(SerpentScrewTrackingBuff.controller(-1))    #디버깅용
        
        SerpentScrewDummy.onTick(core.OptionalElement(partial(EnergyCharge.judge, 100, -1), SerpentScrewOff, name = "서펜트 스크류 사용 종료(100 미만 게이지일 경우)"))
        
        ### 에너지 차지 옵션 적용 ###
        EnergyConstraint = core.ConstraintElement("에너지 차지 상태에서만 사용 가능", EnergyCharge, EnergyCharge.isStateOn)
        
        UnityOfPower.onConstraint(EnergyConstraint)
        DragonStrike.onConstraint(EnergyConstraint)
        SerpentScrew.onConstraint(EnergyConstraint)
    
        return (BasicAttackWrapper,
            [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
            LuckyDice, Viposition, Stimulate, EpicAdventure, PirateFlag, Overdrive, Transform, NautilusBuff,
            UnityOfPowerBuff, OverdrivePenalty, DragonStrikeBuff, EnergyCharge,
            SerpentScrewTrackingBuff, globalSkill.soul_contract()] +\
            [UnityOfPower, Nautilus, DragonStrike, FuriousCharge] +\
            [SerpentScrew, SerpentScrewDummy, StimulateSummon] +\
            [] +\
            [BasicAttackWrapper])