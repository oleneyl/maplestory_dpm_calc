from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..kernel.graph import DynamicVariableOperation
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobclass import heroes
from .jobbranch import warriors
from ..execution.rules import RuleSet, InactiveRule, ConditionRule
from math import ceil

# Advisor : 아지르캐리(크로아)

# 최저 콤보 카운트 500 가정

#TODO : 5차 신스킬 적용
#TODO : 펜릴 크래시 이후에 파이널 블로우가 아닌 다른 스킬이 오면 30ms 딜레이가 추가되어야 함
#TODO : 게더링 캐쳐로 프리드, 오라웨폰 딜레이도 캔슬해야 함

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "str"
        self.jobname = "아란"
        self.vEnhanceNum = 13
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2
        self._combat = 0
    
    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 20)
        
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self._combat
        RetrievedMemory = core.InformedCharacterModifier("되찾은 기억", patt=5)
        SnowChargePassive = core.InformedCharacterModifier("스노우 차지(패시브)", pdamage=10)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        AdvancedComboAbilityPassive = core.InformedCharacterModifier("어드밴스드 콤보 어빌리티", att=10, crit=20, crit_damage=10)
        CleavingAttack = core.InformedCharacterModifier("클리빙 어택", armor_ignore=40, pdamage=10)
        Might = core.InformedCharacterModifier("마이트", att=40)
        HighMastery = core.InformedCharacterModifier("하이 마스터리", att=30, crit_damage=8) 
        AdvancedFinalAttackPassive = core.InformedCharacterModifier("어드밴스드 파이널 어택(패시브)", att=30 + passive_level)

        return [RetrievedMemory, SnowChargePassive, PhisicalTraining, 
            AdvancedComboAbilityPassive, CleavingAttack, Might, HighMastery, AdvancedFinalAttackPassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self._combat
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 49)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5 + 0.5*ceil(passive_level / 2))        
        return [WeaponConstant, Mastery]

    def get_ruleset(self):
        def check_soul_contract_time(adrenaline_el):
            return (adrenaline_el.is_not_active() or (adrenaline_el.is_time_left(10*1000, 1)))

        ruleset = RuleSet()
        ruleset.add_rule(InactiveRule('브랜디쉬 마하(홀더)', '아드레날린 부스트'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('히어로즈 오쓰', '아드레날린 부스트'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('쓸만한 샤프 아이즈', '아드레날린 부스트'), RuleSet.BASE)
        ruleset.add_rule(ConditionRule('소울 컨트랙트', '아드레날린 부스트', check_soul_contract_time), RuleSet.BASE)
        ruleset.add_rule(ConditionRule('부스트 엔드-헌터즈 타겟팅', '아드레날린 부스트', lambda x:x.is_time_left(10*1000, -1)), RuleSet.BASE)
        
        # ruleset.add_rule(InactiveRule('쓸만한 컴뱃 오더스', '아드레날린 부스트'), RuleSet.BASE)
        return ruleset


    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        하이퍼 : 비욘더(3종)
        스윙 - 리메인타임 리인포스
        아드레날린 부스트 - 퍼시스트

        코어강화 순서 어파-파블-비욘더-헌터즈타겟팅-스매시스윙

        브랜디쉬 마하 / 인스톨 마하 / 마하의 영역 : 게더링 캐쳐로 캔슬(600ms)
        아드레날린 부스트 도중에 다음을 사용하지 않음 : 브랜디쉬 마하, 히어로즈 오쓰, 쓸만한 샤프 아이즈
        소울 컨트랙트는 아드레날린 부스트가 10초 이상 남았다면 사용함

        '''
        JUDGEMENT_DELAY=600
        BOOST_END_HUNTERS_TARGETING_DELAY=1100
        ADRENALINE_GENERATOR_DELAY=600
        ADRENALINE_BOOST_REMAIN = (20+3)*1000
        passive_level = chtr.get_base_modifier().passive_level + self._combat

        def get_beyonder_pdamage(excess_target, reinforce = True):
            return int(1.06 ** excess_target * 100 - 100 + reinforce * 20)

        BEYONDER_PDAMAGE = get_beyonder_pdamage(6)
        BEYONDER_ADRENALINE_PDAMAGE = get_beyonder_pdamage(11)
        PENRIL_PDAMAGE = get_beyonder_pdamage(10)
        PENRIL_ADRENALINE_PDAMAGE = get_beyonder_pdamage(15)
        
        SmashSwing = core.DamageSkill("스매시 스윙", 360, 800 + 50 * passive_level, 2).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        SmashSwingIncr = core.BuffSkill("스매시 스윙(최종데미지)", 0, 5000+3000, pdamage_indep=15 + passive_level, pdamage=20, cooltime=-1).wrap(core.BuffSkillWrapper)
        SmashSwingIllusion = core.DamageSkill("스매시 스윙(잔상)", 0, 280, 5).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)

        FinalBlow = core.DamageSkill("파이널 블로우", 420, 285 + 100 + (60 + 2 * passive_level) + (20 + passive_level), 5, modifier=core.CharacterModifier(armor_ignore=15)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)

        Booster = core.BuffSkill("부스터", 0, 180*1000, rem = True).wrap(core.BuffSkillWrapper)
        SnowCharge = core.BuffSkill("스노우 차지", 0, 200*1000, pdamage=10).wrap(core.BuffSkillWrapper) # 펫버프

        FinalAttack = core.DamageSkill("파이널 어택", 0, 85+passive_level+100, 3*0.01*(60+passive_level)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper) # 아드레날린 부스트의 퍼뎀, 타수 효과 적용됨
        FinalAttackAdrenaline = core.DamageSkill("파이널 어택(아드레날린)", 0, 85+passive_level+100+150, (3+2)*0.01*(60+passive_level)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        FinalAttackHolder = core.DamageSkill("파이널어택(홀더)", 0, 0, 0).wrap(core.DamageSkillWrapper)

        AdvancedComboAbility = core.BuffSkill("어드밴스드 콤보 어빌리티", 0, 9999*9999, att=2*10, crit=3*10).wrap(core.BuffSkillWrapper)
        ComboAbility = core.BuffSkill("콤보 어빌리티", 0, 9999*9999, att=2*10).wrap(core.BuffSkillWrapper) 
        Judgement = core.DamageSkill("저지먼트", JUDGEMENT_DELAY, 380 + (60 + 2 * passive_level) + (20 + passive_level), 4).wrap(core.DamageSkillWrapper)
        JudgementDot = core.DotSkill("저지먼트(도트)", 200, 6000).wrap(core.SummonSkillWrapper)

        BlessingMaha = core.BuffSkill("블레싱 마하", 0, 200*1000, att=30).wrap(core.BuffSkillWrapper)   #펫버프

        BeyonderFirst = core.DamageSkill("비욘더(1타)", 420, 385 + 10 * ceil(self._combat / 3), 6, modifier=core.CharacterModifier(pdamage=BEYONDER_PDAMAGE, armor_ignore=44, crit=100)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        BeyonderSecond = core.DamageSkill("비욘더(2타)", 360, 400 + 10 * ceil(self._combat / 3), 6, modifier=core.CharacterModifier(pdamage=BEYONDER_PDAMAGE, armor_ignore=44, crit=100)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        BeyonderThird = core.DamageSkill("비욘더(3타)", 420, 415 + 10 * ceil(self._combat / 3), 6, modifier=core.CharacterModifier(pdamage=BEYONDER_PDAMAGE, armor_ignore=44, crit=100)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        AdrenalineBoost = core.BuffSkill("아드레날린 부스트", 0, ADRENALINE_BOOST_REMAIN).wrap(core.BuffSkillWrapper)
        AdrenalineBoostEndDummy = core.BuffSkill("아드레날린 부스트(종료 더미)", 0, 0, cooltime=-1).wrap(core.BuffSkillWrapper)

        AdrenalineSmashSwing = core.DamageSkill("스매시 스윙(아드레날린)", 360, 950, 4).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        AdrenalineFinalBlow = core.DamageSkill("파이널 블로우(아드레날린)", 420, 285 + 100 + (60 + 2 * passive_level) + (20 + passive_level) + 150, 7, modifier=core.CharacterModifier(armor_ignore=15)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        FinalBlowWaveAdrenaline = core.DamageSkill("파이널 블로우(파동)", 0, 350, 4).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)

        AdrenalineBeyonderFirst = core.DamageSkill("비욘더(1타)(아드레날린)", 420, 535 + 10 * ceil(self._combat / 3), 8, modifier=core.CharacterModifier(pdamage=BEYONDER_ADRENALINE_PDAMAGE, armor_ignore=44, crit=100)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdrenalineBeyonderSecond = core.DamageSkill("비욘더(2타)(아드레날린)", 360, 550 + 10 * ceil(self._combat / 3), 8, modifier=core.CharacterModifier(pdamage=BEYONDER_ADRENALINE_PDAMAGE, armor_ignore=44, crit=100)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdrenalineBeyonderThird = core.DamageSkill("비욘더(3타)(아드레날린)", 420, 565 + 10 * ceil(self._combat / 3), 8, modifier=core.CharacterModifier(pdamage=BEYONDER_ADRENALINE_PDAMAGE, armor_ignore=44, crit=100)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdrenalineBeyonderWave = core.DamageSkill("비욘더(파동)", 0, 400, 5).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        BoostEndHuntersTargeting = core.DamageSkill("부스트 엔드-헌터즈 타겟팅", BOOST_END_HUNTERS_TARGETING_DELAY, 1500 + 15 * self._combat + (20 + passive_level), 15*5, cooltime=-1).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)

        AdrenalineGenerator = core.BuffSkill("아드레날린 제네레이터", ADRENALINE_GENERATOR_DELAY, 0, cooltime=240*1000).wrap(core.BuffSkillWrapper)
        MahaRegion = core.SummonSkill("마하의 영역", 600, 1000, 500, 3, 10*1000, cooltime=150*1000).wrap(core.SummonSkillWrapper) # 게더링캐쳐 캔슬 : 1680 -> 600
        MahaRegionInit = core.DamageSkill("마하의 영역(시전)", 0, 800, 5).wrap(core.DamageSkillWrapper)
        HerosOath = core.BuffSkill("히어로즈 오쓰", 0, 60*1000, cooltime=120*1000, pdamage=10).wrap(core.BuffSkillWrapper)

        InstallMaha = core.BuffSkill("인스톨 마하", 600, (30+vEhc.getV(1,1))*1000, patt=5+vEhc.getV(1,1), cooltime=150*1000, red=True).isV(vEhc, 1, 1).wrap(core.BuffSkillWrapper) # 게더링캐쳐 캔슬 : 960 -> 600
        InstallMahaBlizzard = core.SummonSkill("인스톨 마하(눈보라)", 0, 3000, 450+18*vEhc.getV(1,1), 5, 60*1000, cooltime=-1).isV(vEhc, 1, 1).wrap(core.SummonSkillWrapper)

        BrandishMahaNormal = core.DamageSkill('브랜디쉬 마하', 600, 600+vEhc.getV(2,2)*24 + (20 + passive_level) +100, 15*2, cooltime=-1, red=True, modifier=core.CharacterModifier(boss_pdamage=20)).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)  # 게더링캐쳐 캔슬 : 960 -> 600
        BrandishMaha = core.DamageSkill('브랜디쉬 마하(홀더)', 0, 0, 0, cooltime=20*1000, red=True, modifier=core.CharacterModifier(boss_pdamage=20)).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)
        BrandishMahaAdrenaline = core.DamageSkill('브랜디쉬 마하(아드레날린)', 600, 600+vEhc.getV(2,2)*24+(20 + passive_level)+100+150, 15*2, cooltime=-1, modifier=core.CharacterModifier(boss_pdamage=20)).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)

        GatheringCatcher = core.DamageSkill('게더링 캐쳐(캔슬)', 0, 170+(20 + passive_level), 2).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        
        PenrilCrashHit = 6 + vEhc.getV(3,3) // 30 + 1
        PenrilCrash = core.DamageSkill('펜릴 크래시', 420, 100+500+vEhc.getV(3,3)*5, PenrilCrashHit, modifier=core.CharacterModifier(crit=100, armor_ignore=60,pdamage=PENRIL_PDAMAGE)).setV(vEhc, 2, 2, False).isV(vEhc, 3, 3).wrap(core.DamageSkillWrapper)
        AdrenalinePenrilCrash = core.DamageSkill('펜릴 크래시(아드레날린)', 420, 150+100+500+vEhc.getV(3,3)*5, PenrilCrashHit + 2, modifier=core.CharacterModifier(crit=100, armor_ignore=60,pdamage=PENRIL_ADRENALINE_PDAMAGE)).setV(vEhc, 2, 2, False).isV(vEhc, 3, 3).wrap(core.DamageSkillWrapper)       
        PenrilCrashIceburg = core.DamageSkill('펜릴 크래시(빙산)', 0, 500+vEhc.getV(3,3)*5, 6).setV(vEhc, 2, 2, False).isV(vEhc, 3, 3).wrap(core.DamageSkillWrapper)
        
        Combo = core.BuffSkill("아란(콤보)", 0, 99999999)
        Combo = core.StackSkillWrapper(Combo, 1000)
        Combo.set_name_style("콤보 %d만큼 증가")

        # 인스톨 마하
        InstallMaha.onAfter(InstallMahaBlizzard)
        InstallMaha.onAfter(Combo.stackController(100))
        
        # 브랜디쉬 마하
        BrandishMaha.onAfter(core.OptionalElement(AdrenalineBoost.is_active, BrandishMahaAdrenaline, BrandishMahaNormal))
        BrandishMaha.onAfter(core.OptionalElement(InstallMaha.is_active, BrandishMaha.controller(0.5, 'reduce_cooltime_p')))
        
        # 파이널어택
        FinalAttackHolder.onAfter(core.OptionalElement(AdrenalineBoost.is_active, FinalAttackAdrenaline, FinalAttack))

        # 콤보 계산, 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 1)
        for sk in [SmashSwing, AdrenalineSmashSwing, FinalBlow, AdrenalineFinalBlow,
                Judgement, MahaRegionInit, GatheringCatcher,
                BeyonderFirst, BeyonderSecond, BeyonderThird,
                AdrenalineBeyonderFirst, AdrenalineBeyonderSecond, AdrenalineBeyonderThird,
                PenrilCrash, AdrenalinePenrilCrash, BrandishMahaNormal, BrandishMahaAdrenaline]:
            sk.onAfter(FinalAttackHolder)
            sk.onAfter(Combo.stackController(DynamicVariableOperation.reveal_argument(sk.skill.hit)))
            auraweapon_builder.add_aura_weapon(sk)
        
        BoostEndHuntersTargeting.onAfter(core.RepeatElement(FinalAttackHolder, 5))
        auraweapon_builder.add_aura_weapon(BoostEndHuntersTargeting)
            
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        # 기본 공격
        BasicAttack = core.DamageSkill("기본 공격", 0,0,0).wrap(core.DamageSkillWrapper)

        FinalBlow.onAfter(BeyonderFirst)
        BeyonderFirst.onAfter(BeyonderSecond)
        BeyonderSecond.onAfter(BeyonderThird)
        BeyonderThird.onAfter(PenrilCrash)

        AdrenalineFinalBlow.onAfter(AdrenalineBeyonderFirst)
        AdrenalineFinalBlow.onAfter(FinalBlowWaveAdrenaline)
        AdrenalineBeyonderFirst.onAfter(AdrenalineBeyonderSecond)
        AdrenalineBeyonderSecond.onAfter(AdrenalineBeyonderThird)
        AdrenalineBeyonderThird.onAfter(AdrenalinePenrilCrash)
        
        AdrenalineBeyonderFirst.onAfter(AdrenalineBeyonderWave)
        AdrenalineBeyonderSecond.onAfter(AdrenalineBeyonderWave)
        AdrenalineBeyonderThird.onAfter(AdrenalineBeyonderWave)
        
        AdrenalinePenrilCrash.onAfter(PenrilCrashIceburg)

        BasicAttack.onAfter(core.OptionalElement(AdrenalineBoost.is_active, AdrenalineFinalBlow, FinalBlow))
        
        # 스매시 스윙
        SmashSwing.onAfter(SmashSwingIncr)
        SmashSwing.onAfter(SmashSwingIllusion)

        AdrenalineSmashSwing.onAfter(SmashSwingIncr)
        AdrenalineSmashSwing.onAfter(SmashSwingIllusion)

        SmashSwingHolder = core.DamageSkill("스매시 스윙", 0,0,0).wrap(core.DamageSkillWrapper)
        SmashSwingHolder.onAfter(core.OptionalElement(AdrenalineBoost.is_active, AdrenalineSmashSwing, SmashSwing))
        SmashSwingHolder.onConstraint(core.ConstraintElement('스매시 스윙이 없을때', SmashSwingIncr, SmashSwingIncr.is_not_active))      
        
        # 게캐 캔슬
        BrandishMaha.onAfter(GatheringCatcher)
        MahaRegion.onAfter(GatheringCatcher)
        InstallMaha.onAfter(GatheringCatcher)

        Combo.set_stack(0)

        # 아드레날린
        AdrenalineBoost.onConstraint(core.ConstraintElement('콤보가 1000이상', Combo, partial(Combo.judge,1000,1) ))
        AdrenalineBoost.onAfter(AdrenalineBoostEndDummy.controller(ADRENALINE_BOOST_REMAIN))
        AdrenalineBoost.onAfter(Combo.stackController(-999999999, dtype='set'))
        AdrenalineBoost.onAfter(BoostEndHuntersTargeting.controller(1))
        AdrenalineBoostEndDummy.onAfter(Combo.stackController(500, dtype='set'))
        AdrenalineGenerator.onConstraint(core.ConstraintElement('아드레날린부스트가 불가능할때', AdrenalineBoost, AdrenalineBoost.is_not_active))
        AdrenalineGenerator.onAfter(AdrenalineBoost)
        return(BasicAttack, 
                [globalSkill.maple_heros(chtr.level, combat_level=self._combat), globalSkill.useful_sharp_eyes(), HerosOath,
                    Booster, SmashSwingIncr, SnowCharge, AdvancedComboAbility, ComboAbility,
                    BlessingMaha, AdrenalineBoost, AdrenalineBoostEndDummy,
                    AdrenalineGenerator, 
                    InstallMaha, InstallMahaBlizzard, Combo, AuraWeaponBuff, AuraWeapon, 
                    globalSkill.soul_contract()] +\
                [SmashSwingHolder, BrandishMaha, BoostEndHuntersTargeting] +\
                [MahaRegion] +\
                [BasicAttack])
