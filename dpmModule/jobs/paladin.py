from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule
from . import globalSkill
from .jobbranch import warriors

#TODO : 5차 신스킬 적용
# 4차 스킬은 컴뱃오더스 적용 기준으로 작성해야 함.
# 생츄어리 필요한지 확인바람

######   Passive Skill   ######

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 10
        self.jobtype = "str"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('그랜드 크로스', '홀리 유니티'), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self):
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        ShieldMastery = core.InformedCharacterModifier("실드 마스터리",att = 10)
        
        PaladinExpert = core.InformedCharacterModifier("팔라딘 엑스퍼트",crit_damage = 15+5, pdamage_indep = 42, crit = 42, armor_ignore = 31)
        PaladinExpertSec = core.InformedCharacterModifier("팔라딘 엑스퍼트(2)",armor_ignore = 10)
        
        return [PhisicalTraining, ShieldMastery, PaladinExpert]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 34)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -4.5)    #오더스 기본적용!
        
        ElementalCharge = core.InformedCharacterModifier("엘리멘탈 차지",pdamage = 25, att = 60)  #조건부 적용 여부는 추후검토.
        ParashockGuard = core.InformedCharacterModifier("파라쇼크 가드",att = 20)
        
        return [WeaponConstant, Mastery, ElementalCharge, ParashockGuard]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        블래-라차-디차-파택
        
        블레싱 아머 미적용.
        '''

        
        #Buff skills
        Threat = core.BuffSkill("위협", 1350, 80 * 1000, armor_ignore = 30 + 20).wrap(core.BuffSkillWrapper)
        BlessingArmor = core.BuffSkill("블레싱 아머", 0, 30 * 1000, cooltime = 90 * 1000, att = 20, rem = True).wrap(core.BuffSkillWrapper)
        ElementalForce = core.BuffSkill("엘리멘탈 포스", 810, 206 * 1000, pdamage_indep = 21, rem = True).wrap(core.BuffSkillWrapper)
        
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        HolyUnity = core.BuffSkill("홀리 유니티", 600, (40 + vEhc.getV(0,0)) * 1000, cooltime = 120 * 1000, pdamage_indep = (35 + 0.5*vEhc.getV(0,0))).isV(vEhc,0,0).wrap(core.BuffSkillWrapper) #딜레이 반영.
    
        #Damage Skills
        LighteningCharge = core.DamageSkill("라이트닝 차지", 810, 462, 3, cooltime = 60 * 1000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LighteningChargeDOT = core.DotSkill("라이트닝 차지(도트)", 115, 6000).wrap(core.SummonSkillWrapper)
        DivineCharge = core.DamageSkill("디바인 차지", 810, 462, 3, cooltime = 60 * 1000).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        Blast = core.DamageSkill("블래스트", 630, 291, 8+2+1, modifier = core.CharacterModifier(crit=20, pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        #Summon Skills
        BlessedHammer = core.SummonSkill("블레스드 해머", 0, 600, (250 + vEhc.getV(1,1)*10), 2, 999999* 10000).isV(vEhc,1,1).wrap(core.SummonSkillWrapper)   #딜레이 반영
        BlessedHammerActive = core.SummonSkill("블레스드 해머(활성화)", 0, 600, (525+vEhc.getV(1,1)*21)*3-(250+vEhc.getV(1,1)*10)*2, 1, 30 * 1000, cooltime = 60 * 1000).isV(vEhc,1,1).wrap(core.SummonSkillWrapper)#딜레이 반영
        #http://www.inven.co.kr/board/maple/2294/21881?category=%ED%8C%94%EB%9D%BC%EB%94%98&name=subject&keyword=%EA%B7%B8%ED%81%AC
        #TODO : 오라웨폰 미발동 적용해야 할 필요 있음.
        GrandCrossSmallTick = core.DamageSkill("그랜드 크로스(작은)", 800, 350 + vEhc.getV(3,3)*14, 13, modifier = core.CharacterModifier(crit = 100, crit_damage = 100)).isV(vEhc,3,3).wrap(core.DamageSkillWrapper) #6s
        GrandCrossLargeTick = core.DamageSkill("그랜드 크로스(강화)", 800, 600 + vEhc.getV(3,3)*24, 43, modifier = core.CharacterModifier(crit = 100, crit_damage = 100)).isV(vEhc,3,3).wrap(core.DamageSkillWrapper) #6s
        GrandCross = core.DamageSkill("그랜드 크로스", 480, 0, 0, cooltime = 150 * 1000).wrap(core.DamageSkillWrapper)#Loop = 480인걸로 봐서 재정의 필요할 수도 있음
                
        FinalAttack = core.DamageSkill("파이널 어택", 0, 80, 2*0.4).setV(vEhc, 3, 5, True).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
    
        #Damage skill
        Blast.onAfter(FinalAttack)
        LighteningCharge.onAfter(FinalAttack)
        DivineCharge.onAfter(FinalAttack)
        
        GrandCrossSmallTick.onAfters([FinalAttack, FinalAttack, FinalAttack])
        GrandCrossLargeTick.onAfters([FinalAttack, FinalAttack, FinalAttack])
        GrandCross.onAfters([core.RepeatElement(GrandCrossLargeTick, 6), 
                            core.RepeatElement(GrandCrossSmallTick, 6)])
        
        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 2)
        for sk in [Blast, GrandCrossSmallTick, GrandCrossLargeTick]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeaponCooltimeDummy = auraweapon_builder.get_buff()
                        
        return(Blast,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster(),
                    Threat, BlessingArmor, ElementalForce, EpicAdventure, HolyUnity, AuraWeaponBuff,
                    globalSkill.soul_contract()] +\
                [LighteningCharge, DivineCharge, GrandCross] +\
                [BlessedHammer, BlessedHammerActive] +\
                [AuraWeaponCooltimeDummy] +\
                [Blast])