from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ReservationRule, ConcurrentRunRule
from . import globalSkill
from .jobclass import heroes
from .jobbranch import bowmen

#TODO : 5차 신스킬 적용

class ElementalGhostWrapper(core.BuffSkillWrapper):
    def __init__(self, vEhc, target1, target2):
        skill = core.BuffSkill("엘리멘탈 고스트", 780, (40 + vEhc.getV(0,0))*1000, cooltime = 150 * 1000).isV(vEhc,0,0)#딜레이 모름
        super(ElementalGhostWrapper, self).__init__(skill)
        self.target = [target1, target2]
        self.vlevel = vEhc.getV(0,0)
        
    def spend_time(self, time : int) -> None :  #TODO : can make this process more faster.. maybe
        self.timeLeft -= time
        self.cooltimeLeft -= time
        if self.timeLeft < 0:
            self.onoff = False
            self.target[0].pdamage_indep = 0
            self.target[1].pdamage_indep = 0
        if self.cooltimeLeft < 0:
            self.available = True
    
    def _use(self, rem = 0, red = 0):
        self.target[0].pdamage_indep = 64.687 * 0.01 * (30 + self.vlevel)
        self.target[1].pdamage_indep = 184.5 * 0.01 * (30 + self.vlevel)
        return super(ElementalGhostWrapper, self)._use()


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 11
        self.jobtype = "dex"
        self.jobname = "메르세데스"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ReservationRule('엘리멘탈 고스트', '소울 컨트랙트'), RuleSet.BASE)
        # ruleset.add_rule(ReservationRule('히어로즈 오쓰', '이르칼라의 숨결'), RuleSet.BASE)
        # ruleset.add_rule(ReservationRule('크리티컬 리인포스', '이르칼라의 숨결'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('크리티컬 리인포스', '엘리멘탈 고스트'), RuleSet.BASE)
        # ruleset.add_rule(ReservationRule('엘리멘탈 고스트', '이르칼라의 숨결'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('이르칼라의 숨결','엘리멘탈 고스트'), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self):
        PotentialPower = core.InformedCharacterModifier("포텐셜 파워",pdamage = 20)
        SharpAiming = core.InformedCharacterModifier("샤프 에이밍",crit = 40)
        
        SpiritInfusion = core.InformedCharacterModifier("스피릿 인퓨전",pdamage = 30, crit=15)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        
        IgnisRoar = core.InformedCharacterModifier("이그니스 로어",pdamage_indep = 15, att = 40)

        DualbowgunExpert = core.InformedCharacterModifier("듀얼보우건 엑스퍼트",att = 30, crit_damage =10)
        DefenceBreak = core.InformedCharacterModifier("디펜스 브레이크",armor_ignore=25, pdamage_indep=20, boss_pdamage = 20, crit_damage = 20)
        AdvancedFinalAttack = core.InformedCharacterModifier("어드밴스드 파이널 어택",att = 20)
        
        return [PotentialPower, SharpAiming, SpiritInfusion, 
                PhisicalTraining, IgnisRoar, DualbowgunExpert, DefenceBreak, AdvancedFinalAttack]
        
    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5)        

        IgnisRoarStack = core.InformedCharacterModifier("이그니스 로어(스택)",pdamage_indep = 2*10)#유지되나?       
        
        return [WeaponConstant, Mastery, IgnisRoarStack]
        
    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 60, pdamage = 30)
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        코강 순서
        
        이슈, 스듀/파택, 엘리멘탈, 래쓰오브엔릴, 레전드리, 유니콘
        
        엘리멘탈 고스트는 최종뎀으로 계산되며 각각 64.687, 184.5%의 최종뎀을 받음
        최종뎀으로 계산함으로서 맥뎀 부분에서 약간의 오류가 발생할 수 있으나 미미함
        소울 컨트랙트, 히어로즈 오쓰, 크리티컬 리인포스는 모두 이르칼라와 함께 사용되도록 함
        '''

        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        HerosOath = core.BuffSkill("히어로즈 오쓰", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        UnicornSpike = core.DamageSkill("유니콘 스파이크", 780, 315+100, 5, modifier = core.CharacterModifier(crit=100), cooltime = 30 * 1000).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)#딜레이 모름
        UnicornSpikeBuff = core.BuffSkill("유니콘 스파이크(버프)", 0, 30 * 1000, pdamage = 30, cooltime = -1).wrap(core.BuffSkillWrapper)  #직접시전 금지
        
        IshtarRing = core.DamageSkill("이슈타르의 링", 120, 220, 2, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        RegendrySpear = core.DamageSkill("레전드리 스피어", 660, 700, 3, modifier = core.CharacterModifier(crit=100, pdamage = 20), cooltime = 30 * 1000).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)  #870 -> 660
        RegendrySpearBuff = core.BuffSkill("레전드리 스피어(버프)", 0, 30 * 1000, armor_ignore = 30+20, cooltime = 99999 * 1000).wrap(core.BuffSkillWrapper) #직접시전 금지
        
        AncientSpirit = core.BuffSkill("엔시언트 스피릿", 780, 200 * 1000, patt = 30).wrap(core.BuffSkillWrapper)#딜레이 모름    
    
        AdvanceStrikeDualShot = core.DamageSkill("어드밴스드 스트라이크 듀얼샷", 480, 380, 4).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)    #630 -> 480
    
        ElementalKnights = core.SummonSkill("엘리멘탈 나이트", 680, 1500, (385+385+485)/3, 210/120, 120 *1000).setV(vEhc, 2, 3, False).wrap(core.SummonSkillWrapper) #가동률을 타수로 반영, 210/360 가동률 100% 도트 반영필요, 딜레이 모름.
        
        ElvishBlessing = core.BuffSkill("엘비시 블레싱", 780, 60 * 1000, cooltime = 90 * 1000, att = 80).wrap(core.BuffSkillWrapper) #딜레이 모름!
        
        AdvancedFinalAttackFast = core.DamageSkill("어드밴스드 파이널 어택(속사)", 0, 120, 2*0.75).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedFinalAttackSlow = core.DamageSkill("어드밴스드 파이널 어택(일반)", 0, 120, 2*0.75).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
    
        WrathOfEllil = core.DamageSkill("래쓰 오브 엔릴", 600, 400, 10, cooltime = 7 * 1000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)#연꼐시 1초 감소, 딜레이 모름!=>7초로 감소 반영.
        
        Sylphidia = core.BuffSkill("실피디아", 0, (30 + 0.5*vEhc.getV(5,5)) * 1000, cooltime = 150 * 1000, patt = (5+0.5*vEhc.getV(5,5))).isV(vEhc,5,5).wrap(core.BuffSkillWrapper)  #정보 없음..
        
        IrkilaBreathInit = core.DamageSkill("이르칼라의 숨결", 720, 0, 0, cooltime = 150 * 1000).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        IrkilaBreathTick = core.DamageSkill("이르칼라의 숨결(틱)", 150, 425+15*vEhc.getV(1,1), 8).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)

        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 4, 4)

        ElementalGhostFast = core.CharacterModifier()
        ElementalGhostSlow = core.CharacterModifier()
    
        ######   Skill Wrapper   ######
        #Buff
        ElementalGhost = ElementalGhostWrapper(vEhc, ElementalGhostFast, ElementalGhostSlow)
        Frid = heroes.FridWrapper(vEhc, 3, 3)
        
        AdvancedFinalAttackFast.modifier = ElementalGhostFast
        AdvancedFinalAttackSlow.modifier = ElementalGhostSlow
        
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 2, 2, 10)
    
        #Damage
        UnicornSpike.onAfter(UnicornSpikeBuff.controller(1))
        RegendrySpear.onAfter(RegendrySpearBuff.controller(1))
        WrathOfEllil.onAfter(AdvanceStrikeDualShot)
    
        IrkilaBreath = core.RepeatElement(IrkilaBreathTick, 52)
        IrkilaBreathInit.onAfter(IrkilaBreath)
        
        # 극딜기 몰아서 사용하기
        SoulContract = globalSkill.soul_contract()
            
        for wrp in [UnicornSpike, AdvanceStrikeDualShot, RegendrySpear, WrathOfEllil]:
            wrp.onAfter(AdvancedFinalAttackSlow)
            wrp.modifier = ElementalGhostSlow
            
        for wrp in [IshtarRing, IrkilaBreathTick]:
            wrp.onAfter(AdvancedFinalAttackFast)
            wrp.modifier = ElementalGhostFast
    
        return(IshtarRing,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), 
                    Booster, ElvishBlessing, AncientSpirit, HerosOath, Frid, Sylphidia.ignore(), CriticalReinforce, UnicornSpikeBuff, RegendrySpearBuff, ElementalGhost,
                    SoulContract] +\
                [UnicornSpike, RegendrySpear, WrathOfEllil, IrkilaBreathInit] +\
                [ElementalKnights, GuidedArrow] +\
                [] +\
                [IshtarRing])