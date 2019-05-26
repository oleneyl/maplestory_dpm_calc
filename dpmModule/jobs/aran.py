from . import template as jt
from .template import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill

#TODO : 5차 신스킬 적용

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = True
        self.jobtype = "str"
        self.vEnhanceNum = 9
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'buff_rem', 'crit')
        self.preEmptiveSkills = 2
        
    def buildPassiveSkillList(self):
        WeaponMastery = jt.InformedCharacterModifier("웨폰 마스터리",pdamage = 5)
        PhisicalTraining = jt.InformedCharacterModifier("피지컬 드레이닝",stat_main = 30, stat_sub = 30)
        
        LordOfDarkness = jt.InformedCharacterModifier("로드 오브 다크니스",crit=30, critDamage = 8)
    
        AdvancedWeaponMastery = jt.InformedCharacterModifier("어드밴스드 웨폰 마스터리",att = 30, critDamage = 15)
        ReincarnationBuff = jt.InformedCharacterModifier("리인카네이션(패시브)",pdamage_indep = 30, crit = 10, critDamage = 15)
    
        SacrificePassive = jt.InformedCharacterModifier("새크리파이스(패시브)",armor_ignore = 30)
    
        self.passiveSkillList = [WeaponMastery, PhisicalTraining, LordOfDarkness, AdvancedWeaponMastery, ReincarnationBuff, SacrificePassive]

    def getNotImpliedSkillList(self):
        WeaponConstant = jt.InformedCharacterModifier("무기상수",pdamage_indep = 49)
        Mastery = jt.InformedCharacterModifier("숙련도",pdamage_indep = -5)        
        BiholdersBuff = jt.InformedCharacterModifier("비홀더스 버프",att = 40+30, crit = 10)
        
        return [WeaponConstant, Mastery, BiholdersBuff]
        
    def generate(self, chtr : ck.AbstractCharacter, combat : bool = False , vEhc = jt.vEnhancer()):
        '''
        창 사용
        크오체 풀피 가정
        비홀더 - 리인포스 / 버프 리인포스
        궁그닐 - 리인포스, 이그노어 가드, 보스 킬러
        
        비홀더 임팩트 9타
        피어스 사이클론 22타
        
        임페일-궁그닐-비홀더-파이널어택

        '''

            
        
        #Buff skills
        Booster = jt.BuffSkill("부스터", 0, 180*1000, rem = True).wrap(jt.BuffSkillWrapper)
        CrossoverChain = jt.BuffSkill("크로스 오버 체인", 0, 200*1000, pdamage_indep = 80).wrap(jt.BuffSkillWrapper)
        FinalAttack = jt.DamageSkill("파이널 어택", 0, 150, 0.4).setV(vEhc, 3, 4, True).wrap(jt.DamageSkillWrapper)
        BiholderDominant = jt.SummonSkill("비홀더 도미넌트", 0, 10000, 210, 1, 99999*10000, modifier = jt.CharacterModifier(pdamage = 150)).setV(vEhc, 2, 3, False).wrap(jt.SummonSkillWrapper)
        BiholderShock = jt.DamageSkill("비홀더 쇼크", 0, 640, 2, cooltime = 12000, modifier = jt.CharacterModifier(pdamage = 150)).setV(vEhc, 2, 3, False).wrap(jt.DamageSkillWrapper)
        
        DarkImpail = jt.DamageSkill("다크 임페일", 630, 280, 6).setV(vEhc, 1, 2, False).wrap(jt.DamageSkillWrapper)
        GoungnilDescentNoCooltime = jt.DamageSkill("궁그닐 디센트", 600, 225, 12, modifier = jt.CharacterModifier(armor_ignore = 30+20, pdamage = 20, boss_pdamage = 10)).setV(vEhc, 0, 2, False).wrap(jt.DamageSkillWrapper)    
        GoungnilDescent = jt.DamageSkill("궁그닐 디센트", 600, 225, 12, cooltime = 8000, modifier = jt.CharacterModifier(armor_ignore = 30+20, pdamage = 20, boss_pdamage = 10)).setV(vEhc, 0, 2, False).wrap(jt.DamageSkillWrapper)

        GoungnilDescent_AuraWeapon = jt.DamageSkill("오라 웨폰", 0, 225 * (75 + vEhc.getV(2,1))*0.01, 12, modifier = jt.CharacterModifier(armor_ignore = 30+20, pdamage = 20, boss_pdamage = 10)).wrap(jt.DamageSkillWrapper)
        
        Sacrifice = jt.BuffSkill("새크리파이스", 1080, 30*1000, rem = True, red = True, cooltime = 70000, armor_ignore = 10, boss_pdamage = 10).wrap(jt.BuffSkillWrapper)   #궁그닐 쿨 무시, 비홀더 공격시 쿨0.3감소
        Reincarnation = jt.BuffSkill("리인카네이션", 0, 40*1000, cooltime = 600000, rem = True, red = True).wrap(jt.BuffSkillWrapper) #궁그닐 쿨 무시
        
        #하이퍼
        DarkThurst = jt.BuffSkill("다크 서스트", 900, 30000, cooltime = 120*1000, att = 80).wrap(jt.BuffSkillWrapper)
        EpicAdventure = jt.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(jt.BuffSkillWrapper)
    
        AuraWeaponBuff = jt.BuffSkill("오라웨폰 버프", 0, (80 +2*vEhc.getV(2,1)) * 1000, cooltime = 180 * 1000, armor_ignore = 15, pdamage_indep = (vEhc.getV(2,1) // 5)).isV(vEhc,2,1).wrap(jt.BuffSkillWrapper)  #두 스킬 syncronize 할 것!    
        AuraWeaponCooltimeDummy = jt.BuffSkill("오라웨폰(딜레이 더미)", 0, 4000, cooltime = -1).wrap(jt.BuffSkillWrapper)   # 한 번 발동된 이후에는 4초간 발동되지 않도록 합니다.
    
        DarkSpear = jt.DamageSkill("다크 스피어", 990, 350+10*vEhc.getV(1,0), 7*7, cooltime = 10000, red = True, modifier = jt.CharacterModifier(crit=100, armor_ignore=50)).isV(vEhc,1,0).wrap(jt.DamageSkillWrapper)
        BiholderImpact = jt.SummonSkill("비홀더 임팩트", 0, 100, 300+3*vEhc.getV(0,2), 2, 801, cooltime = 20000, red = True, modifier = jt.CharacterModifier(pdamage = 150)).setV(vEhc, 2, 3, False).isV(vEhc,0,2).wrap(jt.SummonSkillWrapper)#onTick으로 0.3초씩
        PierceCyclone = jt.DamageSkill("피어스 사이클론(더미)", 90, 0, 0, cooltime = 180*1000).wrap(jt.DamageSkillWrapper)
        PierceCycloneTick = jt.DamageSkill("피어스 사이클론", 9000/22, 400+16*vEhc.getV(3,3), 12, modifier = jt.CharacterModifier(crit=100, armor_ignore = 50)).isV(vEhc,3,3).wrap(jt.DamageSkillWrapper) #22타
        PierceCycloneEnd = jt.DamageSkill("피어스 사이클론(종료)", 0, 1500+60*vEhc.getV(3,3), 15, modifier = jt.CharacterModifier(crit=100, armor_ignore = 50)).isV(vEhc,3,3).wrap(jt.DamageSkillWrapper)
        PierceCycloneEnd_AuraWeapon = jt.DamageSkill("오라 웨폰", 0, 1500+60*vEhc.getV(3,3) * (75 + vEhc.getV(2,1))*0.01, 15, modifier = jt.CharacterModifier(crit=100, armor_ignore = 50)).isV(vEhc,3,3).wrap(jt.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
    
        #Damage skill
    
        Reincarnation.setDisabledAndTimeLeft(30000)
        
        def InfGoungnil():
            return (Sacrifice.isOnOff() or Reincarnation.isOnOff())
        
        DarkImpail.onAfter(FinalAttack)
        GoungnilDescentNoCooltime.onAfter(FinalAttack)
        GoungnilDescent.onAfter(FinalAttack)
        BasicAttack = jt.OptionalElement(InfGoungnil, GoungnilDescentNoCooltime, DarkImpail)
        
        BiholderDominant.onTick(Sacrifice.controller(300,'reduceCooltime'))
        BiholderShock.onAfter(Sacrifice.controller(300,'reduceCooltime'))
        BiholderImpact.onTick(Sacrifice.controller(300,'reduceCooltime'))
        
        PierceCyclone_ = jt.RepeatElement(PierceCycloneTick, 22)
        PierceCyclone_.onAfter(PierceCycloneEnd)
        PierceCyclone.onAfter(PierceCyclone_)

        # 오라 웨폰
        def AuraWeapon_connection_builder(origin_skill, target_skill):
            optional = jt.OptionalElement(lambda : (AuraWeaponCooltimeDummy.isOffOn() and AuraWeaponBuff.isOnOff()), target_skill)
            origin_skill.onAfter(optional)
            target_skill.onAfter(AuraWeaponCooltimeDummy)
            
        AuraWeapon_connection_builder(GoungnilDescent, GoungnilDescent_AuraWeapon)
        AuraWeapon_connection_builder(PierceCycloneEnd, PierceCycloneEnd_AuraWeapon)
        
        
        schedule = jt.ScheduleGraph()
        
        schedule.build_graph(
                chtr, 
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    Booster, CrossoverChain, Sacrifice, Reincarnation,EpicAdventure, DarkThurst, AuraWeaponBuff,
                    globalSkill.soul_contract()],
                [BiholderShock, GoungnilDescent, DarkSpear, PierceCyclone],
                [BiholderDominant, BiholderImpact],
                [AuraWeaponCooltimeDummy],
                BasicAttack)
        
        return schedule