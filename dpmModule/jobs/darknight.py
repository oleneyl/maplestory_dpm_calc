from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import warriors
from math import ceil

#TODO : 5차 신스킬 적용

#TODO: 비홀더스 리벤지 메인 효과 추가

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = (7, 7)
        self.jobtype = "str"
        self.jobname = "다크나이트"
        self.vEnhanceNum = 9
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'reuse', 'boss_pdamage')
        self.preEmptiveSkills = 2
        self._combat = 0

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(boss_pdamage=10, armor_ignore=44)
        
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self._combat
        
        WeaponMastery = core.InformedCharacterModifier("웨폰 마스터리",pdamage = 5)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 드레이닝",stat_main = 30, stat_sub = 30)
        
        LordOfDarkness = core.InformedCharacterModifier("로드 오브 다크니스",crit=30, crit_damage = 8)
    
        AdvancedWeaponMastery = core.InformedCharacterModifier("어드밴스드 웨폰 마스터리",att = 30 + passive_level, crit_damage = 15 + passive_level // 3)
        ReincarnationBuff = core.InformedCharacterModifier("리인카네이션(패시브)",pdamage_indep = 30 + passive_level, crit = 10 + ceil(passive_level / 3), crit_damage = 15 + passive_level // 3)
        ReincarnationHyper = core.InformedCharacterModifier("리인카네이션-크리티컬 레이트", crit = 20)
    
        SacrificePassive = core.InformedCharacterModifier("새크리파이스(패시브)",armor_ignore = 30)
        CrossoverChainPassive = core.InformedCharacterModifier("크로스 오버 체인(패시브)", pdamage_indep=50)
        return [WeaponMastery, PhisicalTraining, LordOfDarkness, AdvancedWeaponMastery, ReincarnationBuff, ReincarnationHyper, SacrificePassive, CrossoverChainPassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self._combat
        
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 49)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5 + 0.5 * ceil(passive_level / 2))        
        BiholdersBuff = core.InformedCharacterModifier("비홀더스 버프",att = 40, crit = 10)
        
        return [WeaponConstant, Mastery, BiholdersBuff]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        창 사용
        크오체 풀피 가정
        비홀더 - 리인포스
        리인카네이션 - 데미지, 크리티컬 레이트
        궁그닐 - 리인포스, 이그노어 가드
        
        비홀더 임팩트 9타
        피어스 사이클론 25타
        다크 스피어 7*8타
        
        임페일-궁그닐-비홀더-파이널어택

        '''

        passive_level = chtr.get_base_modifier().passive_level + self._combat
        
        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 180*1000, rem = True).wrap(core.BuffSkillWrapper) # 펫버프
        CrossoverChain = core.BuffSkill("크로스 오버 체인", 0, 200*1000, pdamage_indep = 20).wrap(core.BuffSkillWrapper) # 펫버프
        FinalAttack = core.DamageSkill("파이널 어택", 0, 80, 2*0.4).setV(vEhc, 3, 4, True).wrap(core.DamageSkillWrapper)
        BiholderDominant = core.SummonSkill("비홀더 도미넌트", 0, 10000, 210, 1, 99999*10000, modifier = core.CharacterModifier(pdamage = 150)).setV(vEhc, 2, 3, False).wrap(core.SummonSkillWrapper)
        BiholderShock = core.DamageSkill("비홀더 쇼크", 0, 215+300 + 5 * passive_level, 6, cooltime = 12000, red=True, modifier = core.CharacterModifier(pdamage = 150)).setV(vEhc, 2, 3, False).wrap(core.DamageSkillWrapper)
        
        DarkImpail = core.DamageSkill("다크 임페일", 630, 280 + 4 * self._combat, 5 + (30 + self._combat) // 16).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)

        GOUNGNIL_MODIFIER = core.CharacterModifier(armor_ignore = 30 + self._combat) + core.CharacterModifier(armor_ignore = 20, pdamage = 20)
        GoungnilDescentNoCooltime = core.DamageSkill("궁그닐 디센트(무한)", 600, 225 + self._combat, 12, modifier = GOUNGNIL_MODIFIER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)    
        GoungnilDescent = core.DamageSkill("궁그닐 디센트", 600, 225 + self._combat, 12, cooltime = 8000, red=True, modifier = GOUNGNIL_MODIFIER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        Sacrifice = core.BuffSkill("새크리파이스", 1080, (30 + self._combat // 2)*1000, rem = True, red = True, cooltime = 70000, armor_ignore = 10 + self._combat // 3, boss_pdamage = 10 + self._combat // 3).wrap(core.BuffSkillWrapper)   #궁그닐 쿨 무시, 비홀더 공격시 쿨0.3감소
        Reincarnation = core.BuffSkill("리인카네이션", 0, (40+passive_level)*1000, cooltime = (900 - 7 * passive_level) * 1000, rem = True, red = True, pdamage_indep=30).wrap(core.BuffSkillWrapper) #궁그닐 쿨 무시
        
        #하이퍼
        DarkThurst = core.BuffSkill("다크 서스트", 900, 30000, cooltime = 120*1000, att = 80).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        #5차
        DarkSpear = core.DamageSkill("다크 스피어", 750, 350+10*vEhc.getV(1,0), 7 * 8, cooltime = 10000, red = True, modifier = core.CharacterModifier(crit=100, armor_ignore=50)).isV(vEhc,1,0).wrap(core.DamageSkillWrapper)
        BiholderImpact = core.SummonSkill("비홀더 임팩트", 0, 270, 100+vEhc.getV(0,2), 6, 2880, cooltime = 20000, red = True, modifier = core.CharacterModifier(pdamage = 150)).setV(vEhc, 2, 3, False).isV(vEhc,0,2).wrap(core.SummonSkillWrapper)#onTick으로 0.3초씩
        PierceCyclone = core.DamageSkill("피어스 사이클론(더미)", 90, 0, 0, cooltime = 180*1000, red = True).wrap(core.DamageSkillWrapper)
        PierceCycloneTick = core.DamageSkill("피어스 사이클론", 360, 400+16*vEhc.getV(3,3), 12, modifier = core.CharacterModifier(crit=100, armor_ignore = 50)).isV(vEhc,3,3).wrap(core.DamageSkillWrapper) #25타
        PierceCycloneEnd = core.DamageSkill("피어스 사이클론(종료)", 900, 1500+60*vEhc.getV(3,3), 15, modifier = core.CharacterModifier(crit=100, armor_ignore = 50)).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
    
        #Damage skill
    
        Reincarnation.set_disabled_and_time_left(30000)
        Reincarnation.onAfter(Reincarnation.controller(300*1000, 'reduce_cooltime'))
        
        def InfGoungnil():
            return (Sacrifice.is_active() or Reincarnation.is_active())
        
        DarkImpail.onAfter(FinalAttack)
        GoungnilDescentNoCooltime.onAfter(FinalAttack)
        GoungnilDescent.onAfter(FinalAttack)
        GoungnilDescent.onConstraint(core.ConstraintElement("새크리 OFF", Sacrifice, Sacrifice.is_not_active))
        GoungnilDescent.onConstraint(core.ConstraintElement("리인카 OFF", Reincarnation, Reincarnation.is_not_active))
        BasicAttack = core.OptionalElement(InfGoungnil, GoungnilDescentNoCooltime, DarkImpail)
        BasicAttackWrapped = core.DamageSkill('기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapped.onAfter(BasicAttack)
        BiholderDominant.onTick(Sacrifice.controller(300,'reduce_cooltime'))
        BiholderShock.onAfter(Sacrifice.controller(300,'reduce_cooltime'))
        BiholderImpact.onTick(Sacrifice.controller(300,'reduce_cooltime'))
        
        PierceCyclone_ = core.RepeatElement(PierceCycloneTick, 25)
        PierceCyclone_.onAfter(PierceCycloneEnd)
        PierceCyclone.onAfter(PierceCyclone_)

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 1)
        for sk in [GoungnilDescent, GoungnilDescentNoCooltime, DarkImpail, PierceCycloneEnd]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()
        
        return(BasicAttackWrapped, 
                [globalSkill.maple_heros(chtr.level, combat_level=self._combat), globalSkill.useful_sharp_eyes(),
                    Booster, CrossoverChain, Sacrifice, Reincarnation,EpicAdventure, DarkThurst, AuraWeaponBuff, AuraWeapon,
                    globalSkill.soul_contract()] +\
                [BiholderShock, GoungnilDescent, DarkSpear, PierceCyclone] +\
                [BiholderDominant, BiholderImpact] +\
                [BasicAttackWrapped])