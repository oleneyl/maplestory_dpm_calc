from . import template as jt
from .template import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
#TODO : 5차 신스킬 적용

######   Passive Skill   ######



class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = True
        self.vEnhanceNum = 11

    def applyOther(self, chtr):
        chtr.buffRemain += 50
        
    def generate(self, chtr : ck.AbstractCharacter, combat : bool = False , vlevel : int = 0, vEhc = jt.vEnhancer(), applyPassive = True) -> None:
        '''combat : 컴뱃 오더스 적용 여부
        vlevel : V Skill 강화레벨 
        vEnhance : V 강화스킬 레벨. 1순위 / 2순위 / 3순위 순서.
        
        부스터 생략
        
        쿼드-마크-쇼다운
        '''

        ######   Skill   ######
        WeaponConstant = jt.CharacterModifier(pdamage_indep = 75)
        Mastery = jt.CharacterModifier(pdamage_indep = -7.5)    #오더스 기본적용!
        
        NimbleBody = jt.CharacterModifier(stat_main = 20)
        CriticalThrow = jt.CharacterModifier(crit=50, crit_damage = 5)
        PhisicalTraining = jt.CharacterModifier(stat_main = 30, stat_sub = 30)
        
        Adrenalin = jt.CharacterModifier(crit_damage=10)
        JavelinMastery = jt.CharacterModifier(pdamage_indep = 25, crit = 20)    #20%확률로 100%크리.
        PurgeAreaPassive = jt.CharacterModifier(boss_pdamage = 10)
        DarkSerenity = jt.CharacterModifier(att = 40, armor_ignore = 30)
        
        JavelineExpert = jt.CharacterModifier(att = 30, crit_damage = 15)
        
        passiveSkillList = [WeaponConstant, Mastery, NimbleBody, CriticalThrow, PhisicalTraining, 
                Adrenalin, JavelinMastery, PurgeAreaPassive, DarkSerenity, JavelineExpert]
        
        passiveModifier = jt.CharacterModifier()
        for _mdf in passiveSkillList:
            passiveModifier.mergeWith(_mdf)
        #Buff skills
        ShadowPartner = jt.BuffSkill("쉐도우 파트너", 600, 200 * 1000, rem = True).wrap(jt.BuffSkillWrapper) #어떻게 처리할지 고심중! #딜레이 모름
        SpiritJavelin = jt.BuffSkill("스피릿 자벨린", 600, 200 * 1000, rem = True).wrap(jt.BuffSkillWrapper) #어떻게 처리할지 고심중! #딜레이 모름
        PurgeArea = jt.BuffSkill("퍼지 에어리어", 600, 40 * 1000).wrap(jt.BuffSkillWrapper) #딜레이 모름
        BleedingToxin = jt.BuffSkill("블리딩 톡신", 600, 90*1000, cooltime = 200 * 1000, att = 60).wrap(jt.BuffSkillWrapper) #딜레이 모름
        BleedingToxinDot = jt.DotSkill("블리딩 톡신(도트)", 1000, 90*1000).wrap(jt.SummonSkillWrapper)
        EpicAdventure = jt.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(jt.BuffSkillWrapper)
        ReadyToDiePassive = jt.BuffSkill("레디 투 다이(패시브)", 0, 9999 * 100000, att = vEhc.getV(1,1)).isV(vEhc,1,1).wrap(jt.BuffSkillWrapper)
        
        QuarupleThrow =jt.DamageSkill("쿼드러플 스로우", 600, 378, 5 * 1.7, modifier = jt.CharacterModifier(boss_pdamage = 20, pdamage = 20)).setV(vEhc, 0, 2, True).wrap(jt.DamageSkillWrapper)    #쉐도우 파트너 적용
        
        MarkOfNightlord = jt.DamageSkill("마크 오브 나이트로드", 0, (60 + chtr.level), 0.6*3).setV(vEhc, 1, 2, True).wrap(jt.DamageSkillWrapper)
        MarkOfNightlordPungma = jt.DamageSkill("마크 오브 나이트로드", 0, (60 + chtr.level), 0.6*3*0.4).setV(vEhc, 1, 2, True).wrap(jt.DamageSkillWrapper)
    
        FatalVenom = jt.DotSkill("페이탈 베놈", 480, 8000).wrap(jt.SummonSkillWrapper)
    
        #_VenomBurst = jt.DamageSkill("베놈 버스트", ??) ## 패시브 50%확률로 10초간 160+6*vlevel dot. 사용시 도트뎀 모두 피해 + (500+20*vlevel) * 5. 어차피 안쓰는 스킬이므로 작성X
        
        UltimateDarksight = jt.BuffSkill("얼티밋 다크사이트", 750, 30*1000, cooltime = (220-vEhc.getV(3,3))*1000, pdamage_indep=int(0.5*vEhc.getV(3,3))).isV(vEhc,3,3).wrap(jt.BuffSkillWrapper)
        ReadyToDie = jt.BuffSkill("레디 투 다이", 780, 30*1000, cooltime = (90-int(0.5*vEhc.getV(1,1)))*1000, pdamage_indep = 30+int(0.2*vEhc.getV(1,1))).isV(vEhc,1,1).wrap(jt.BuffSkillWrapper)
#        ReadyToDie = jt.BuffSkill("레디 투 다이", 780, 30*1000, cooltime = (90-int(0.5*vlevel))*1000, pdamage_indep = 30+int(0.2*vlevel)).wrap(jt.BuffSkillWrapper)
        
        #조건부 파이널어택으로 설정함.
        SpreadThrowTick = jt.DamageSkill("스프레드 스로우", 0, 378*0.6, 5*3, modifier = jt.CharacterModifier(boss_pdamage = 20, pdamage = 20)).setV(vEhc, 0, 2, True).wrap(jt.DamageSkillWrapper)
        SpreadThrowInit = jt.BuffSkill("스프레드 스로우(시전)", 600, (30+vEhc.getV(0,0))*1000, cooltime = (240-vEhc.getV(0,0))*1000).isV(vEhc,0,0).wrap(jt.BuffSkillWrapper)    #딜레이 모름
        Pungma = jt.SummonSkill("풍마수리검", 480, 100, 250+vEhc.getV(4,4)*10, 5*1.7, 950, cooltime = 25*1000).isV(vEhc,4,4).wrap(jt.SummonSkillWrapper)   #10타 가정
        ArcaneOfDarklord = jt.SummonSkill("다크로드의 비전서", 360, 1000, 350+14*vEhc.getV(2,2), 7 + 5, 7990, cooltime = 60*1000).isV(vEhc,2,2).wrap(jt.SummonSkillWrapper) #56타 + 폭발 1회 ( 7 * 8s)
        ArcaneOfDarklordFinal = jt.DamageSkill("다크로드의 비전서(막타)", 0, 900+18*vEhc.getV(2,2), 10, cooltime = -1).isV(vEhc,2,2).wrap(jt.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######

        #_VenomBurst = jt.DamageSkill("베놈 버스트", ??) ## 패시브 50%확률로 10초간 160+6*vlevel dot. 사용시 도트뎀 모두 피해 + (500+20*vlevel) * 5. 어차피 안쓰는 스킬이므로 작성X

        #조건부 파이널어택으로 설정함.
        SpreadThrow = jt.OptionalElement(SpreadThrowInit.isOnOff, SpreadThrowTick)
        SpreadThrowTick.onAfter(jt.RepeatElement(MarkOfNightlord, 6))
        Pungma.onTick(MarkOfNightlordPungma)
        
        ArcaneOfDarklord.onTick(jt.RepeatElement(MarkOfNightlord, 7))
        ArcaneOfDarklord.onAfter(ArcaneOfDarklordFinal.controller(8000))
        
        BleedingToxin.onAfter(BleedingToxinDot)
        
        QuarupleThrow.onAfters([MarkOfNightlord, SpreadThrow])

        schedule = jt.ScheduleGraph()
        
        schedule.build_graph(
                chtr, 
                [ShadowPartner, SpiritJavelin, PurgeArea, BleedingToxin, EpicAdventure, 
                    ReadyToDiePassive, UltimateDarksight, ReadyToDie, SpreadThrowInit],
                [ArcaneOfDarklordFinal],
                [Pungma, ArcaneOfDarklord, BleedingToxinDot],
                [],
                QuarupleThrow)
        
        if applyPassive:        
            chtr.applyModifiers([passiveModifier])        
                
        return schedule