from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule
from . import globalSkill
from .jobbranch import thieves
#TODO : 5차 신스킬 적용

######   Passive Skill   ######



class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 11
        self.jobtype = "luk"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('얼티밋 다크 사이트', '스프레드 스로우'), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self):
        NimbleBody = core.InformedCharacterModifier("님블 바디",stat_main = 20)
        CriticalThrow = core.InformedCharacterModifier("크리티컬 스로우", crit=50, crit_damage = 5)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        
        Adrenalin = core.InformedCharacterModifier("아드레날린",crit_damage=10)
        JavelinMastery = core.InformedCharacterModifier("자벨린 마스터리",pdamage_indep = 25)    #20%확률로 100%크리. 현재 비활성,
        PurgeAreaPassive = core.InformedCharacterModifier("퍼지 에어리어(패시브)",boss_pdamage = 10)
        DarkSerenity = core.InformedCharacterModifier("다크 세레니티",att = 40, armor_ignore = 30)
        
        JavelineExpert = core.InformedCharacterModifier("자벨린 엑스퍼트",att = 30, crit_damage = 15)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(self.vEhc, 1, 1)
        
        return [NimbleBody, CriticalThrow, PhisicalTraining, 
                Adrenalin, JavelinMastery, PurgeAreaPassive, DarkSerenity, JavelineExpert, ReadyToDiePassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 75)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5)    #오더스 기본적용!        
        
        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        쿼드-마크-쇼다운
        
        스프 3줄 히트
        
        얼닼사는 스프 사용중에만 사용
        
        '''
        #Buff skills
        ShadowPartner = core.BuffSkill("쉐도우 파트너", 600, 200 * 1000, rem = True).wrap(core.BuffSkillWrapper) #어떻게 처리할지 고심중! #딜레이 모름
        SpiritJavelin = core.BuffSkill("스피릿 자벨린", 600, 200 * 1000, rem = True).wrap(core.BuffSkillWrapper) #어떻게 처리할지 고심중! #딜레이 모름
        PurgeArea = core.BuffSkill("퍼지 에어리어", 600, 40 * 1000, armor_ignore=30).wrap(core.BuffSkillWrapper) #딜레이 모름
        BleedingToxin = core.BuffSkill("블리딩 톡신", 600, 90*1000, cooltime = 200 * 1000, att = 60).wrap(core.BuffSkillWrapper) #딜레이 모름
        BleedingToxinDot = core.DotSkill("블리딩 톡신(도트)", 1000, 90*1000).wrap(core.SummonSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)

        
        QuarupleThrow =core.DamageSkill("쿼드러플 스로우", 600, 378, 5 * 1.7, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)    #쉐도우 파트너 적용
        
        MarkOfNightlord = core.DamageSkill("마크 오브 나이트로드", 0, (60 + chtr.level), 0.35*3).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        MarkOfNightlordPungma = core.DamageSkill("마크 오브 나이트로드(풍마)", 0, (60 + chtr.level), 0.193*3).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
    
        FatalVenom = core.DotSkill("페이탈 베놈", 480, 8000).wrap(core.SummonSkillWrapper)
    
        #_VenomBurst = core.DamageSkill("베놈 버스트", ??) ## 패시브 50%확률로 10초간 160+6*vlevel dot. 사용시 도트뎀 모두 피해 + (500+20*vlevel) * 5. 어차피 안쓰는 스킬이므로 작성X
        
        UltimateDarksight = thieves.UltimateDarkSightWrapper(vEhc, 3, 3)
        #UltimateDarksight = core.BuffSkill("얼티밋 다크사이트", 750, 30*1000, cooltime = (220-vEhc.getV(3,3))*1000, pdamage_indep=int(0.5*vEhc.getV(3,3))).isV(vEhc,3,3).wrap(core.BuffSkillWrapper)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 1, 1)
#        ReadyToDie = core.BuffSkill("레디 투 다이", 780, 30*1000, cooltime = (90-int(0.5*vlevel))*1000, pdamage_indep = 30+int(0.2*vlevel)).wrap(core.BuffSkillWrapper)
        
        #조건부 파이널어택으로 설정함.
        SpreadThrowTick = core.DamageSkill("스프레드 스로우(틱)", 0, 378*0.85, 5*3, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        SpreadThrowInit = core.BuffSkill("스프레드 스로우", 600, (30+vEhc.getV(0,0))*1000, cooltime = (240-vEhc.getV(0,0))*1000).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)    #딜레이 모름
        Pungma = core.SummonSkill("풍마수리검", 690, 100, 250+vEhc.getV(4,4)*10, 5*1.7, 1450, cooltime = 25*1000).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)   #10타 가정
        ArcaneOfDarklord = core.SummonSkill("다크로드의 비전서", 360, 780, 350+14*vEhc.getV(2,2), 7 + 5, 11990, cooltime = 60*1000, modifier=core.CharacterModifier(boss_pdamage=30)).isV(vEhc,2,2).wrap(core.SummonSkillWrapper) #56타 + 폭발 1회 ( 7 * 8s)
        ArcaneOfDarklordFinal = core.DamageSkill("다크로드의 비전서(막타)", 0, 900+36*vEhc.getV(2,2), 10, cooltime = -1, modifier=core.CharacterModifier(boss_pdamage=30)).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)

        ######   Skill Wrapper   ######

        #_VenomBurst = core.DamageSkill("베놈 버스트", ??) ## 패시브 50%확률로 10초간 160+6*vlevel dot. 사용시 도트뎀 모두 피해 + (500+20*vlevel) * 5. 어차피 안쓰는 스킬이므로 작성X

        #조건부 파이널어택으로 설정함.
        SpreadThrow = core.OptionalElement(SpreadThrowInit.is_active, SpreadThrowTick)
        SpreadThrowTick.onAfter(core.RepeatElement(MarkOfNightlord, 15))
        Pungma.onTick(MarkOfNightlordPungma)
        
        ArcaneOfDarklord.onAfter(ArcaneOfDarklordFinal.controller(8000))
        
        BleedingToxin.onAfter(BleedingToxinDot)
        
        QuarupleThrow.onAfters([MarkOfNightlord, SpreadThrow])

        for sk in [QuarupleThrow, Pungma, SpreadThrowTick]:
            sk.onAfter(FatalVenom)

        return (QuarupleThrow, 
            [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    ShadowPartner, SpiritJavelin, PurgeArea, BleedingToxin, EpicAdventure, 
                    UltimateDarksight, ReadyToDie, SpreadThrowInit,
                    globalSkill.soul_contract()] + \
                [ArcaneOfDarklordFinal] + \
                [Pungma, ArcaneOfDarklord, BleedingToxinDot, FatalVenom] +\
                [] + [QuarupleThrow])