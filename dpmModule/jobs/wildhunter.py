from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobclass import resistance
from .jobbranch import bowmen
# TODO: 재규어 맥시멈 추가

class JaguerStack(core.DamageSkillWrapper, core.TimeStackSkillWrapper):
    def __init__(self, level, vEhc):
        self.level = level
        self.modifier = core.CharacterModifier()
        skill = core.DamageSkill("어나더 바이트", 0, 0, 0, cooltime=-1).setV(vEhc, 1, 2, False)
        super(core.DamageSkillWrapper, self).__init__(skill, 3)
        
    def addStack(self, vary, left):
        if self.getStack() < 0.5:
            vary_ = 1
        else: vary_ = vary
        self.queue.append([vary_, left])
        return core.ResultObject(0, core.CharacterModifier(), 0, sname = self._id, spec = 'graph control')        
        
    def _use(self, rem = 0, red = 0):
        mdf = self.get_modifier()
        dmg = 60*self.getStack() + int(self.level/3)
        return core.ResultObject(0, mdf,  dmg, sname = self._id, spec = 'deal')

    def is_usable(self):
        return False

######   Passive Skill   ######


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 11
        self.jobtype = "dex"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'reuse', 'crit')
        self.preEmptiveSkills = 0
        
    def get_passive_skill_list(self):
        Jaguer = core.InformedCharacterModifier("재규어",crit=5)
        NaturesWrath = core.InformedCharacterModifier("네이처스 래쓰",crit=25)
        AutomaticShootingDevice = core.InformedCharacterModifier("오토매팅 슈팅 디바이스",att=20)
        CrossbowMastery = core.InformedCharacterModifier("크로스보우 마스터리",patt = 10)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        Flurry = core.InformedCharacterModifier("플러리", stat_main = 40)
        JaugerLink = core.InformedCharacterModifier("재규어 링크",crit = 18, crit_damage = 12, att = 10)
        CrossbowExpert = core.InformedCharacterModifier("크로스보우 엑스퍼트",att=30, crit_damage = 20)
        WildInstinct = core.InformedCharacterModifier("와일드 인스팅트",armor_ignore = 30)
        ExtentMagazine = core.InformedCharacterModifier("익스텐드 매거진", pdamage_indep=20, stat_main=60, stat_sub=60)
        AdvancedFinalAttackPassive = core.InformedCharacterModifier("어드밴스드 파이널 어택(패시브)", att = 20)
    
        return [Jaguer, NaturesWrath, AutomaticShootingDevice,
                            CrossbowMastery, PhisicalTraining, Flurry, JaugerLink, CrossbowExpert, 
                            WildInstinct, ExtentMagazine, AdvancedFinalAttackPassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 35)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5)
        
        SummonJaguer = core.InformedCharacterModifier("서먼 재규어", crit_damage = 8)
        
        return [WeaponConstant, Mastery, SummonJaguer]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        재규어 7마리(25레벨시 8마리) 소환, 재규어당 데미지 62+vlevel, 3히트 가정.
        
        코강 순서:
        발칸 - (서먼/어나더) - 파택 - 클로우컷 - 헌팅유닛- 램피지애즈원/플래시레인 - 소닉붐 - 재규어소울 - 크로스 로드
        '''

        
        #재규어 스킬들
        JAGUERNUMBER = 3
        
        Normal = core.DamageSkill("재규어 공격", 0, 140+chtr.level, 1, cooltime = 60000/37, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        ClawCut = core.DamageSkill("클로우 컷", 0, 200+chtr.level, 4, cooltime = 5000*0.9, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        Crossroad = core.DamageSkill("크로스 로드", 0, 450+2*chtr.level, 1, cooltime = 6000*0.9, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 8, 3, False).wrap(core.DamageSkillWrapper)
        SonicBoom = core.DamageSkill("소닉 붐", 0, 220+chtr.level, 6, cooltime = 6000*0.9, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        JaguarSoul = core.DamageSkill("재규어 소울", 0, 1000+20*chtr.level, 1, cooltime = 210000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        RampageAsOne = core.DamageSkill("램피지 애즈 원", 0, 500+1*chtr.level, 9, cooltime=12000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
    
        Normal_JG = core.DamageSkill("재규어 공격(여럿)",          0, (140+chtr.level)*(62+vEhc.getV(0,0))*0.01, 1 * JAGUERNUMBER, cooltime = 60000/37, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        ClawCut_JG = core.DamageSkill("클로우 컷(여럿)",           0, (200+chtr.level)*(62+vEhc.getV(0,0))*0.01, 4 * JAGUERNUMBER, cooltime = 5000*0.9, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        Crossroad_JG = core.DamageSkill("크로스 로드(여럿)",       0, (450+2*chtr.level)*(62+vEhc.getV(0,0))*0.01, 1 * JAGUERNUMBER, cooltime = 6000*0.9, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 8, 3, False).wrap(core.DamageSkillWrapper)
        SonicBoom_JG = core.DamageSkill("소닉 붐(여럿)",           0, (220+chtr.level)*(62+vEhc.getV(0,0))*0.01, 6 * JAGUERNUMBER, cooltime = 6000*0.9, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        JaguarSoul_JG = core.DamageSkill("재규어 소울(여럿)",      0, (1000+20*chtr.level)*(62+vEhc.getV(0,0))*0.01, 1 * JAGUERNUMBER, cooltime = 210000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        RampageAsOne_JG = core.DamageSkill("램피지 애즈 원(여럿)", 0, (500+1*chtr.level)*(62+vEhc.getV(0,0))*0.01, 9 * JAGUERNUMBER, cooltime=12000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
    
    
        ######   Skill   ######
        #Buff skills
        SoulArrow = core.BuffSkill("소울 애로우", 0, 300*1000, rem = True, att = 20).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill("부스터", 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper)    #딜레이 모름
        Hauling = core.BuffSkill("하울링", 0, 300*1000, rem = True, patt = 10).wrap(core.BuffSkillWrapper)
        BeastForm = core.BuffSkill("비스트 폼", 0, 300*1000, rem = True, patt=20+5).wrap(core.BuffSkillWrapper)
        SharpEyes = core.BuffSkill("샤프 아이즈", 1080, 300 * 1000, crit = 20 + combat*1, crit_damage = 15 + combat*1, rem = True).wrap(core.BuffSkillWrapper)
        SilentRampage = core.BuffSkill("사일런트 램피지", 1020, 40*1000, pdamage=40, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)
        
        WillOfLiberty = core.BuffSkill("윌 오브 리버티", 0, 60*1000, cooltime = 120*1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        FinalAttack70 = core.DamageSkill("파이널 어택(70)", 0, 210, 0.7).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        FinalAttack100 = core.DamageSkill("파이널 어택(100)", 0, 210, 1).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        
        HuntingUnit = core.SummonSkill("헌팅 유닛", 660, 31000/90, 150, 1.5, 31000).setV(vEhc, 4, 3, False).wrap(core.SummonSkillWrapper)
    
        WildBalkan = core.DamageSkill("와일드 발칸", 120, 340, 1, modifier = core.CharacterModifier(boss_pdamage=10+20, pdamage=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
    
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 4, 4)
        RegistanceLineInfantry = ResistanceLineInfantryWrapper(vEhc, 3, 3)
    
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 1, 1, 20)
    
        JaguerStorm = core.BuffSkill("재규어 스톰", 840, 40*1000, cooltime = (150-vEhc.getV(0,0))*1000).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        
        AnotherBite = JaguerStack(chtr.level, vEhc)
        #JaguerMaximum = core. 안씀..
        WildGrenade = core.SummonSkill("와일드 그레네이드", 0, 4500, 600+24*vEhc.getV(2,2), 5, 9999*10000).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
    
        FinalAttack = core.OptionalElement(SilentRampage.is_active, FinalAttack100, FinalAttack70)
        
        WildBalkan.onAfter(FinalAttack)
        WildBalkan.onAfter(AnotherBite)
    
        Normal.onAfter(AnotherBite.stackController(0.15, 8000))
        ClawCut.onAfter(AnotherBite.stackController(0.3, 8000))
        Crossroad.onAfter(AnotherBite.stackController(0.8, 8000))
        SonicBoom.onAfter(AnotherBite.stackController(0.4, 8000))
        JaguarSoul.onAfter(AnotherBite.stackController(1, 8000))
        RampageAsOne.onAfter(AnotherBite.stackController(1, 8000))
    
        Normal.onAfter(core.OptionalElement(JaguerStorm.is_active, Normal_JG))
        ClawCut.onAfter(core.OptionalElement(JaguerStorm.is_active, ClawCut_JG))
        Crossroad.onAfter(core.OptionalElement(JaguerStorm.is_active, Crossroad_JG))
        SonicBoom.onAfter(core.OptionalElement(JaguerStorm.is_active, SonicBoom_JG))
        JaguarSoul.onAfter(core.OptionalElement(JaguerStorm.is_active, JaguarSoul_JG))
        RampageAsOne.onAfter(core.OptionalElement(JaguerStorm.is_active, RampageAsOne_JG))
    
        AnotherBite.protect_from_running()

        return(WildBalkan,
                [globalSkill.maple_heros(chtr.level),
                    CriticalReinforce, SoulArrow, Booster, Hauling, BeastForm, SharpEyes, SilentRampage, JaguerStorm,
                    globalSkill.soul_contract()] +\
                [Normal, ClawCut, Crossroad, SonicBoom, JaguarSoul, RampageAsOne] +\
                [HuntingUnit, GuidedArrow, RegistanceLineInfantry, WildGrenade] +\
                [AnotherBite] +\
                [WildBalkan])