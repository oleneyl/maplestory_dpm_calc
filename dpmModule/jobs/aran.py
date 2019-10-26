from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobclass import heroes
from .jobbranch import warriors

##### TODO: 소스코드 전체 작성 (현재 닼나 복붙) #####

# 최저 콤보 카운트 500 가정

#TODO : 5차 신스킬 적용

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = True
        self.jobtype = "str"
        # 이하 수정 필요
        self.vEnhanceNum = 9
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'buff_rem', 'crit')
        self.preEmptiveSkills = 2
        
    def get_passive_skill_list(self):
        # 기본 뎀퍼 10 + 빙결 뎀퍼 10
        SnowChargePassive = core.InformedCharacterModifier("스노우 차지 (패시브)",pdamage = 20)

        ComboAbility = core.InformedCharacterModifier("콤보 어빌리티 10중첩",att = 20)
        AdvancedComboAbility = core.InformedCharacterModifier("어드밴스드 콤보 어빌리티 10중첩",att = 20)
        AdvancedComboAbilityPassive = core.InformedCharacterModifier("어드밴스드 콤보 어빌리티 패시브",att = 10)

        PhisicalTraining = core.InformedCharacterModifier("피지컬 드레이닝",stat_main = 30, stat_sub = 30)
        
        LordOfDarkness = core.InformedCharacterModifier("로드 오브 다크니스",crit=30, crit_damage = 8)
    
        AdvancedWeaponMastery = core.InformedCharacterModifier("어드밴스드 웨폰 마스터리",att = 30, crit_damage = 15)
    
        return [WeaponMastery, PhisicalTraining, LordOfDarkness, AdvancedWeaponMastery]

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
        
        Frid = heroes.FridWrapper(vEhc, 0, 0)

        # 오라웨폰을 소환수로 변경하는 코드 (발동 딜레이 추가바람)
        AuraWeaponSummon = core.SummonSkill("오라웨폰", 0, 6000, (500 + 20 * vEhc.getV(2,1)), 6, (80 +2*vEhc.getV(2,1)) * 1000, cooltime = 180 * 1000, modifier = core.CharacterModifier(armor_ignore = 15, pdamage_indep = (vEhc.getV(2,1) // 5))).isV(vEhc, 2, 1).wrap(core.SummonSkillWrapper)
        
        ######   Skill Wrapper   ######
    
        #Damage skill
    
        Reincarnation.set_disabled_and_time_left(30000)
        
        
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

        
        return(BasicAttackWrapped, 
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
#                    Booster, CrossoverChain, Sacrifice, Reincarnation,EpicAdventure, DarkThurst, AuraWeaponBuff,
                    Booster, CrossoverChain, Sacrifice, Reincarnation,EpicAdventure, DarkThurst, AuraWeaponSummon,
                    globalSkill.soul_contract()] +\
                [BiholderShock, GoungnilDescent, DarkSpear, PierceCyclone] +\
                [BiholderDominant, BiholderImpact] +\
#                [AuraWeaponCooltimeDummy] +\
                [BasicAttackWrapped])