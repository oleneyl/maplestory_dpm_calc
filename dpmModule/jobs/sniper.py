from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
#TODO : 5차 신스킬 적용

class CriticalReinforceWrapper(core.BuffSkillWrapper):
    def __init__(self, vEhc, character : ck.AbstractCharacter):
        skill = core.BuffSkill("크리티컬 리인포스", 780, 30 * 1000, cooltime = 120 * 1000).isV(vEhc,3,3)
        super(CriticalReinforceWrapper, self).__init__(skill)
        self.char = character
        self.inhancer = (20 + vEhc.getV(3,3))*0.01
        
    def get_modifier(self):
        if self.onoff:
            return core.CharacterModifier(crit_damage = self.inhancer * max(0,self.char.get_modifier().crit + 20 + 6.6))
        else:
            return self.disabledModifier        


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 10
        self.jobtype = "dex"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1
        
    def get_passive_skill_list(self):
        CriticalShot = core.InformedCharacterModifier("크리티컬 샷",crit = 40)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        
        MarkmanShip = core.InformedCharacterModifier("마크맨쉽",armor_ignore = 25, pdamage = 15)

        CrossBowExpert = core.InformedCharacterModifier("크로스보우 엑스퍼트",att= 30+self.combat*1, crit_damage = 8)
        
        return [CriticalShot, PhisicalTraining, MarkmanShip, 
                CrossBowExpert]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 35)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5)
        
        DistancingSence = core.InformedCharacterModifier("디스턴싱 센스",pdamage_indep = 42) #최대 사정거리
        MortalBlow = core.InformedCharacterModifier("모탈 블로우",pdamage = 2)        
        ExtremeArchery = core.InformedCharacterModifier("익스트림 아처리:석궁",crit_damage = 20)
        
        LastmanStanding = core.InformedCharacterModifier("라스트맨 스탠딩",pdamage_indep = 20+self.combat*2)
        WeaknessFinding = core.InformedCharacterModifier("위크니스 파인딩",armor_ignore = 50+self.combat*1)
        
        return [WeaponConstant, Mastery, DistancingSence, MortalBlow, 
               ExtremeArchery, LastmanStanding, WeaknessFinding]
        

    def generate(self, chtr : ck.AbstractCharacter, combat : bool = False , vEhc = core.vEnhancer()):
        '''
        거리 400
        
        스나, 피어싱, 롱레트, 프리저
        '''
        distance = 400
        
        #Buff skills
        SoulArrow = core.BuffSkill("소울 애로우", 0, 300 * 1000, att = 30, rem = True).wrap(core.BuffSkillWrapper)
        ElusionStep = core.BuffSkill("일루젼 스탭", 0, (300+combat*16) * 1000, stat_main = 40 + combat*1, rem = True).wrap(core.BuffSkillWrapper)
        SharpEyes = core.BuffSkill("샤프 아이즈", 660, 300 * 1000, crit = 20 + combat*1, crit_damage = 15 + combat*1, rem = True).wrap(core.BuffSkillWrapper)
        #크리티컬 리인포스 - >재정의 필요함..
        
        BoolsEye = core.BuffSkill("불스아이", 960, 30 * 1000, cooltime = 90 * 1000, crit = 20, crit_damage = 10, armor_ignore = 20, pdamage = 20).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        #Damage Skills
        Snipping = core.DamageSkill("스나이핑", 660, 730+combat*10, 5 + 1, modifier = core.CharacterModifier(crit = 100, armor_ignore = 20 + combat*1, pdamage = 20, boss_pdamage = 10)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        TrueSnippingTick = core.DamageSkill("트루 스나이핑", 700, 1200+vEhc.getV(2,2)*48, 9+1, modifier = core.CharacterModifier(pdamage_indep = 100, armor_ignore = 100)).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        TrueSnipping = core.DamageSkill("트루 스나이핑 홀더", 0, 0, 0, cooltime = 180 * 1000).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        
        #TODO : 차지드 애로우용 홀더 생성이 필요함.
        ChargedArrow = core.DamageSkill("차지드 애로우", 0, 750 + vEhc.getV(1,1)*30, 10+1, cooltime = -1).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        ChargedArrowUse = core.DamageSkill("차지드 애로우(차징)", 0, 0, 0, cooltime = 10000).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        #Summon Skills
        Freezer = core.SummonSkill("프리저", 900, 3030, 390, 1, 220 * 1000).setV(vEhc, 3, 3, False).wrap(core.SummonSkillWrapper)
        GuidedArrow = core.SummonSkill("가이디드 애로우", 720, 330, 400+16*vEhc.getV(4,4), 1, 30 * 1000, cooltime = 60 * 1000).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)
        
        Evolve = core.SummonSkill("이볼브", 600, 3330, 450+vEhc.getV(5,5)*15, 7, 40*1000, cooltime = (121-int(0.5*vEhc.getV(5,5)))*1000).isV(vEhc,5,5).wrap(core.SummonSkillWrapper)
        
        SplitArrow = core.DamageSkill("스플릿 애로우", 0, 600 + vEhc.getV(0,0) * 24, 5+1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        SplitArrowBuff = core.BuffSkill("스플릿 애로우 시전", 810, 60 * 1000, 120 * 1000).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        #TODO : 스플릿애로우 계산
        
        ######   Skill Wrapper   ######
        
        #이볼브 연계 설정
        Evolve.onAfter(Freezer.controller(1))
        Freezer.onConstraint(core.ConstraintElement("이볼브 사용시 사용 금지", Evolve, Evolve.is_not_active))
        
        CriticalReinforce = CriticalReinforceWrapper(vEhc, chtr) #Maybe need to sync
    
        SplitArrowOption = core.OptionalElement(SplitArrowBuff.is_active, SplitArrow, name = "스플릿 애로우 여부 확인")
        Snipping.onAfter(SplitArrowOption)
    
        TrueSnippingDeal = core.RepeatElement(TrueSnippingTick, 7)
        TrueSnipping.onAfter(TrueSnippingDeal)
        TrueSnipping.onAfter(ChargedArrow.controller(9999999, name = "차징 해제"))
        
        ChargedArrowUse.onAfter(ChargedArrow.controller(5000))
        
        ### 제한
        SplitArrowBuff.onConstraint(core.ConstraintElement("트스나 사용불가시에만", TrueSnipping, TrueSnipping.is_not_usable))
        schedule = core.ScheduleGraph()
        
        return(Snipping,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_wind_booster(),
                    SoulArrow, ElusionStep, SharpEyes, BoolsEye, EpicAdventure, CriticalReinforce, SplitArrowBuff,
                        globalSkill.soul_contract()] +\
                [TrueSnipping, ChargedArrowUse, ChargedArrow] +\
                [Evolve,Freezer, GuidedArrow] +\
                [] +\
                [Snipping])