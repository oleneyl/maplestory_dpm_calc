from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import warriors

#TODO : 5차 신스킬 적용

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = True
        self.jobtype = "str"
        self.vEnhanceNum = 9
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'buff_rem', 'crit')
        self.preEmptiveSkills = 2
        
    def get_passive_skill_list(self):
        WeaponMastery = core.InformedCharacterModifier("웨폰 마스터리",pdamage = 5)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 드레이닝",stat_main = 30, stat_sub = 30)
        
        LordOfDarkness = core.InformedCharacterModifier("로드 오브 다크니스",crit=30, crit_damage = 8)
    
        AdvancedWeaponMastery = core.InformedCharacterModifier("어드밴스드 웨폰 마스터리",att = 30, crit_damage = 15)
        ReincarnationBuff = core.InformedCharacterModifier("리인카네이션(패시브)",pdamage_indep = 30, crit = 10, crit_damage = 15)
    
        SacrificePassive = core.InformedCharacterModifier("새크리파이스(패시브)",armor_ignore = 30)
    
        return [WeaponMastery, PhisicalTraining, LordOfDarkness, AdvancedWeaponMastery, ReincarnationBuff, SacrificePassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 49)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)        
        BiholdersBuff = core.InformedCharacterModifier("비홀더스 버프",att = 40+30, crit = 10)
        
        return [WeaponConstant, Mastery, BiholdersBuff]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
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
        Booster = core.BuffSkill("부스터", 0, 180*1000, rem = True).wrap(core.BuffSkillWrapper)
        CrossoverChain = core.BuffSkill("크로스 오버 체인", 0, 200*1000, pdamage_indep = 80).wrap(core.BuffSkillWrapper)
        FinalAttack = core.DamageSkill("파이널 어택", 0, 80, 2*0.4).setV(vEhc, 3, 4, True).wrap(core.DamageSkillWrapper)
        BiholderDominant = core.SummonSkill("비홀더 도미넌트", 0, 10000, 210, 1, 99999*10000, modifier = core.CharacterModifier(pdamage = 150)).setV(vEhc, 2, 3, False).wrap(core.SummonSkillWrapper)
        BiholderShock = core.DamageSkill("비홀더 쇼크", 0, 215, 6, cooltime = 12000, modifier = core.CharacterModifier(pdamage = 150)).setV(vEhc, 2, 3, False).wrap(core.DamageSkillWrapper)
        
        DarkImpail = core.DamageSkill("다크 임페일", 630, 280, 6).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        GoungnilDescentNoCooltime = core.DamageSkill("궁그닐 디센트(무한)", 600, 225, 12, modifier = core.CharacterModifier(armor_ignore = 30+20, pdamage = 20, boss_pdamage = 10)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)    
        GoungnilDescent = core.DamageSkill("궁그닐 디센트", 600, 225, 12, cooltime = 8000, modifier = core.CharacterModifier(armor_ignore = 30+20, pdamage = 20, boss_pdamage = 10)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        Sacrifice = core.BuffSkill("새크리파이스", 1080, 30*1000, rem = True, red = True, cooltime = 70000, armor_ignore = 10, boss_pdamage = 10).wrap(core.BuffSkillWrapper)   #궁그닐 쿨 무시, 비홀더 공격시 쿨0.3감소
        Reincarnation = core.BuffSkill("리인카네이션", 0, 40*1000, cooltime = 600000, rem = True, red = True).wrap(core.BuffSkillWrapper) #궁그닐 쿨 무시
        
        #하이퍼
        DarkThurst = core.BuffSkill("다크 서스트", 900, 30000, cooltime = 120*1000, att = 80).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        DarkSpear = core.DamageSkill("다크 스피어", 990, 350+10*vEhc.getV(1,0), 7 * 8, cooltime = 10000, red = True, modifier = core.CharacterModifier(crit=100, armor_ignore=50)).isV(vEhc,1,0).wrap(core.DamageSkillWrapper)
        BiholderImpact = core.SummonSkill("비홀더 임팩트", 0, 300, 100+vEhc.getV(0,2), 6, 3001, cooltime = 20000, red = True, modifier = core.CharacterModifier(pdamage = 150)).setV(vEhc, 2, 3, False).isV(vEhc,0,2).wrap(core.SummonSkillWrapper)#onTick으로 0.3초씩
        PierceCyclone = core.DamageSkill("피어스 사이클론(더미)", 90, 0, 0, cooltime = 180*1000).wrap(core.DamageSkillWrapper)
        PierceCycloneTick = core.DamageSkill("피어스 사이클론", 9000/22, 400+16*vEhc.getV(3,3), 12, modifier = core.CharacterModifier(crit=100, armor_ignore = 50)).isV(vEhc,3,3).wrap(core.DamageSkillWrapper) #22타
        PierceCycloneEnd = core.DamageSkill("피어스 사이클론(종료)", 0, 1500+60*vEhc.getV(3,3), 15, modifier = core.CharacterModifier(crit=100, armor_ignore = 50)).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
    
        #Damage skill
    
        Reincarnation.set_disabled_and_time_left(30000)
        
        def InfGoungnil():
            return (Sacrifice.is_active() or Reincarnation.is_active())
        
        DarkImpail.onAfter(FinalAttack)
        GoungnilDescentNoCooltime.onAfter(FinalAttack)
        GoungnilDescent.onAfter(FinalAttack)
        BasicAttack = core.OptionalElement(InfGoungnil, GoungnilDescentNoCooltime, DarkImpail)
        BasicAttackWrapped = core.DamageSkill('기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapped.onAfter(BasicAttack)
        BiholderDominant.onTick(Sacrifice.controller(300,'reduce_cooltime'))
        BiholderShock.onAfter(Sacrifice.controller(300,'reduce_cooltime'))
        BiholderImpact.onTick(Sacrifice.controller(300,'reduce_cooltime'))
        
        PierceCyclone_ = core.RepeatElement(PierceCycloneTick, 22)
        PierceCyclone_.onAfter(PierceCycloneEnd)
        PierceCyclone.onAfter(PierceCyclone_)

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 1)
        for sk in [GoungnilDescent, PierceCycloneEnd]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeaponCooltimeDummy = auraweapon_builder.get_buff()
        
        return(BasicAttackWrapped, 
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    Booster, CrossoverChain, Sacrifice, Reincarnation,EpicAdventure, DarkThurst, AuraWeaponBuff,
                    globalSkill.soul_contract()] +\
                [BiholderShock, GoungnilDescent, DarkSpear, PierceCyclone] +\
                [BiholderDominant, BiholderImpact] +\
                [AuraWeaponCooltimeDummy] +\
                [BasicAttackWrapped])