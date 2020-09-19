from ..kernel.graph import DynamicVariableOperation
from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ReservationRule, RuleSet, ConcurrentRunRule
from . import globalSkill
from .jobclass import heroes
from .jobbranch import bowmen
from math import ceil

class ElementalGhostWrapper(core.BuffSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        skill = core.BuffSkill("엘리멘탈 고스트", 720, (40+vEhc.getV(num1,num2))*1000, cooltime=150*1000, red=True)
        super(ElementalGhostWrapper, self).__init__(skill)
        self.ratio = (30 + vEhc.getV(num1, num2)) * 0.01
        self.prob_slow = 0.9 * (1 + 0.7 * (1 + 0.5))
        self.prob_fast = 0.45 * (1 + 0.35 * (1 + 0.25))

    def addSkill(self, skill_wrapper, is_fast, is_final_attack):
        p = self.prob_fast if is_fast else self.prob_slow
        ratio = 1 if is_final_attack else self.ratio
        
        original_skill = skill_wrapper.skill
        copial_skill = core.DamageSkill(name = DynamicVariableOperation.reveal_argument(original_skill.name) + f"(엘고)",
            delay = DynamicVariableOperation.wrap_argument(0),
            damage = original_skill.damage * DynamicVariableOperation.wrap_argument(ratio),
            hit = original_skill.hit * p,
            modifier=original_skill._static_skill_modifier).wrap(core.DamageSkillWrapper)
        
        skill_wrapper.onAfter(core.OptionalElement(self.is_active, copial_skill, name="엘고 ON"))

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 11
        self.jobtype = "dex"
        self.jobname = "메르세데스"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('크리티컬 리인포스', '엘리멘탈 고스트'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('이르칼라의 숨결', '엘리멘탈 고스트'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('소울 컨트랙트', '엘리멘탈 고스트'), RuleSet.BASE)
        ruleset.add_rule(ReservationRule('엘비시 블레싱', '엘리멘탈 고스트'), RuleSet.BASE)
        ruleset.add_rule(ReservationRule('히어로즈 오쓰', '엘리멘탈 고스트'), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        PotentialPower = core.InformedCharacterModifier("포텐셜 파워",pdamage = 20)
        SharpAiming = core.InformedCharacterModifier("샤프 에이밍",crit = 40)
        
        SpiritInfusion = core.InformedCharacterModifier("스피릿 인퓨전",pdamage = 30, crit=15)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        
        IgnisRoar = core.InformedCharacterModifier("이그니스 로어",pdamage_indep = 15, att = 40)

        DualbowgunExpert = core.InformedCharacterModifier("듀얼보우건 엑스퍼트",att = 30+passive_level, crit_damage= 10+ceil(passive_level/3))
        DefenceBreak = core.InformedCharacterModifier("디펜스 브레이크",armor_ignore= 25+passive_level, pdamage_indep= 20+passive_level, boss_pdamage = 20+3*(passive_level//4), crit_damage = 20+3*(passive_level//4))
        AdvancedFinalAttack = core.InformedCharacterModifier("어드밴스드 파이널 어택",att = 20 + ceil(passive_level / 2))
        
        return [PotentialPower, SharpAiming, SpiritInfusion, 
                PhisicalTraining, IgnisRoar, DualbowgunExpert, DefenceBreak, AdvancedFinalAttack]
        
    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5+0.5*ceil(passive_level/2))        

        IgnisRoarStack = core.InformedCharacterModifier("이그니스 로어(스택)",pdamage_indep = 2*10)
        
        return [WeaponConstant, Mastery, IgnisRoarStack]
        
    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 60, pdamage = 30)
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter):
        '''
        하이퍼
        이슈타르의 링-리인포스, 이그노어 가드, 보스 킬러
        레전드리 스피어-리듀스 아머, 링크드 리인포스

        코강 순서
        이슈, 스듀/파택, 엘리멘탈, 래쓰오브엔릴, 레전드리, 유니콘, 맆토/다이브
        
        엘리멘탈 고스트, 이르칼라의 숨결, 크리티컬 리인포스, 소울 컨트랙트, 엘비시 블레싱, 히어로즈 오쓰를 함께 사용

        실피디아 사용하지 않음

        엘고 연계
        스듀-엔릴-스듀-유니콘-스듀-스피어-거다
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        # Buff skill
        Booster = core.BuffSkill("부스터", 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        AncientSpirit = core.BuffSkill("엔시언트 스피릿", 0, (200+5*self.combat) * 1000, patt = 30+self.combat, rem=True).wrap(core.BuffSkillWrapper)

        # Summon skill
        ElementalKnights = core.DamageSkill("엘리멘탈 나이트", 0, 0, 0, cooltime=120*1000, red=True).setV(vEhc, 2, 3, False).wrap(core.DamageSkillWrapper) #도트 반영필요
        ElementalKnights_1 = core.SummonSkill("엘리멘탈 나이트(1)", 0, 1470, (385+385+485)/3, 1, 210 * 1000, cooltime=-1, rem=True).setV(vEhc, 2, 3, False).wrap(core.SummonSkillWrapper)
        ElementalKnights_2 = core.SummonSkill("엘리멘탈 나이트(2)", 0, 1470, (385+385+485)/3, 1, 210 * 1000, cooltime=-1, rem=True).setV(vEhc, 2, 3, False).wrap(core.SummonSkillWrapper)
        
        # Damage skill
        IshtarRing = core.DamageSkill("이슈타르의 링", 120, 220 + self.combat, 2, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        # 연계 스킬들 - 연계시 딜레이로 작성
        UnicornSpike = core.DamageSkill("유니콘 스파이크", 450, 315+100 + 2*self.combat, 5, modifier = core.CharacterModifier(crit=100), cooltime = 10 * 1000, red=True).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        UnicornSpikeBuff = core.BuffSkill("유니콘 스파이크(버프)", 0, 30 * 1000, pdamage = 30, cooltime = -1).wrap(core.BuffSkillWrapper)  #직접시전 금지
        RegendrySpear = core.DamageSkill("레전드리 스피어", 690, 700 + 10*self.combat, 3, cooltime = 5 * 1000, red=True, modifier = core.CharacterModifier(crit=100)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        RegendrySpearBuff = core.BuffSkill("레전드리 스피어(버프)", 0, (30+self.combat) * 1000, armor_ignore = 30+20+self.combat, cooltime = -1).wrap(core.BuffSkillWrapper) #직접시전 금지
        LightningEdge = core.DamageSkill("라이트닝 엣지", 630, 420 + 5*self.combat, 3).wrap(core.DamageSkillWrapper)
        LightningEdgeBuff = core.BuffSkill("라이트닝 엣지(버프)", 0, 30000, cooltime=-1).wrap(core.BuffSkillWrapper)
        LeapTornado = core.DamageSkill("리프 토네이도", 390, 390+30+3*self.combat, 4).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        GustDive = core.DamageSkill("거스트 다이브", 480, 430 + 3*self.combat, 4).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        
        AdvanceStrikeDualShot = core.DamageSkill("어드밴스드 스트라이크 듀얼샷", 480, 380, 4).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvanceStrikeDualShot_Link = core.DamageSkill("어드밴스드 스트라이크 듀얼샷(연계)", 360, 380, 4).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)

        AdvancedFinalAttackFast = core.DamageSkill("어드밴스드 파이널 어택(속사)", 0, 120 + passive_level, 2*0.01*(75 + passive_level)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedFinalAttackSlow = core.DamageSkill("어드밴스드 파이널 어택(일반)", 0, 120 + passive_level, 2*0.01*(75 + passive_level)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
    
        # Hyper
        ElvishBlessing = core.BuffSkill("엘비시 블레싱", 900, 60 * 1000, cooltime = 90 * 1000, att = 80).wrap(core.BuffSkillWrapper)
        WrathOfEllil = core.DamageSkill("래쓰 오브 엔릴", 210, 400, 10, cooltime = 8 * 1000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper) #연계시 딜레이
        HerosOath = core.BuffSkill("히어로즈 오쓰", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        # 5th
        Sylphidia = core.BuffSkill("실피디아", 0, (30 + vEhc.getV(5,5)//2) * 1000, cooltime = 150 * 1000, red=True, patt = (5+vEhc.getV(5,5)//2)).isV(vEhc,5,5).wrap(core.BuffSkillWrapper) # 정보 없음
        ElementalGhost = ElementalGhostWrapper(vEhc, 0, 0)
        ElementalGhostSpirit = core.DamageSkill("엘리멘탈 고스트(정령의 기운)", 0, 450+15*vEhc.getV(0,0), 8, cooltime=10*1000).wrap(core.DamageSkillWrapper)
        IrkilaBreathInit = core.DamageSkill("이르칼라의 숨결", 900, 0, 0, cooltime = 150 * 1000, red=True).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        IrkilaBreathTick = core.DamageSkill("이르칼라의 숨결(틱)", 150, 400+16*vEhc.getV(1,1), 8).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        RoyalKnights = core.BuffSkill("로얄 나이츠", 1260, 30000, cooltime=150*1000, red=True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        RoyalKnightsAttack = core.DamageSkill("로얄 나이츠(공격)", 0, 325+13*vEhc.getV(0,0), 4*4, cooltime=1410).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)

        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 4, 4)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
    
        ######   Skill Wrapper   ######
        #Buff
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 2, 2, 10)

        #Summon
        ElementalKnights.onAfter(core.OptionalElement(ElementalKnights_1.is_active, ElementalKnights_2, ElementalKnights_1))
    
        #Damage
        UnicornSpike.onAfter(UnicornSpikeBuff)
        RegendrySpear.onAfter(RegendrySpearBuff)
        LightningEdge.onAfter(LightningEdgeBuff)
        IshtarRing.add_runtime_modifier(LightningEdgeBuff, lambda sk: core.CharacterModifier(pdamage = sk.is_active() * 20))
    
        IrkilaBreath = core.RepeatElement(IrkilaBreathTick, 52)
        IrkilaBreathInit.onAfter(IrkilaBreath)

        #Cooldown
        LinkAttack = core.GraphElement("연계")
        LinkAttack.onAfter(WrathOfEllil.controller(1000, "reduce_cooltime"))
        LinkAttack.onAfter(UnicornSpike.controller(1000, "reduce_cooltime"))
        LinkAttack.onAfter(RegendrySpear.controller(1000, "reduce_cooltime"))
        LinkAttack.onAfter(ElementalGhostSpirit.controller(1000, "reduce_cooltime"))
        
        #Deal Cycle
        DebuffCombo = core.DamageSkill("디버프 콤보", 0, 0, 0).wrap(core.DamageSkillWrapper)
        DebuffComboList = [AdvanceStrikeDualShot_Link, WrathOfEllil, AdvanceStrikeDualShot_Link,
                            UnicornSpike, AdvanceStrikeDualShot_Link, LightningEdge, AdvanceStrikeDualShot_Link,
                            RegendrySpear, WrathOfEllil, AdvanceStrikeDualShot]
        DebuffCombo.onAfter(DebuffComboList[0])
        for sk in DebuffComboList[1:]:
            DebuffCombo.onAfter(sk)
            DebuffCombo.onAfter(LinkAttack)

        ElementalGhostCombo = core.DamageSkill("엘고 콤보", 0, 0, 0).wrap(core.DamageSkillWrapper)
        ElementalGhostComboList = [AdvanceStrikeDualShot_Link, WrathOfEllil, AdvanceStrikeDualShot_Link,
                                    UnicornSpike, AdvanceStrikeDualShot_Link, RegendrySpear, GustDive]
        ElementalGhostCombo.onAfter(ElementalGhostComboList[0])
        for sk in ElementalGhostComboList[1:]:
            ElementalGhostCombo.onAfter(sk)
            ElementalGhostCombo.onAfter(LinkAttack)

        BasicAttack = core.DamageSkill("기본 공격", 0, 0, 0).wrap(core.DamageSkillWrapper)
        BasicAttack.onAfter(
            core.OptionalElement(ElementalGhost.is_active, ElementalGhostCombo,
                core.OptionalElement(UnicornSpikeBuff.is_not_active, DebuffCombo, IshtarRing)
            )
        )

        # TODO: 실피디아 사용시 연계 딜레이와 디버프 콤보 조사하고, 딜 증가하는지 확인할 것
        # Sylphidia.onConstraint(core.ConstraintElement("엘고와 따로 사용", ElementalGhost, lambda: ElementalGhost.is_not_active() and ElementalGhost.is_not_usable()))

        #Final Attack, Elemental Ghost
        UseElementalGhostSpirit = core.OptionalElement(
            lambda: ElementalGhost.is_active() and ElementalGhostSpirit.is_available(), ElementalGhostSpirit, name="정령의 기운 조건")
        UseRoyalNightsAttack = core.OptionalElement(
            lambda: RoyalKnights.is_active() and RoyalKnightsAttack.is_available(), RoyalKnightsAttack, name="로얄 나이츠 조건")

        for wrp in [UnicornSpike, RegendrySpear, LightningEdge, LeapTornado, GustDive,
                    AdvanceStrikeDualShot, AdvanceStrikeDualShot_Link, WrathOfEllil]:
            ElementalGhost.addSkill(wrp, is_fast=False, is_final_attack=False)
            wrp.onAfter(AdvancedFinalAttackSlow)
            wrp.onAfter(UseElementalGhostSpirit)
            wrp.onAfter(UseRoyalNightsAttack)
        ElementalGhost.addSkill(AdvancedFinalAttackSlow, is_fast=False, is_final_attack=True) # 잔상->파택을 파택->잔상으로 처리, 대신 최종뎀 감소는 적용하지 않게 함
            
        for wrp in [IshtarRing, IrkilaBreathTick]:
            ElementalGhost.addSkill(wrp, is_fast=True, is_final_attack=False)
            wrp.onAfter(AdvancedFinalAttackFast)
            wrp.onAfter(UseElementalGhostSpirit)
            wrp.onAfter(UseRoyalNightsAttack)
        ElementalGhost.addSkill(AdvancedFinalAttackFast, is_fast=True, is_final_attack=True)

        GuidedArrow.onTick(UseRoyalNightsAttack)

        for sk in [UnicornSpike, RegendrySpear, WrathOfEllil, ElementalGhostSpirit, RoyalKnightsAttack]:
            sk.protect_from_running()

        for sk in [UnicornSpikeBuff, RegendrySpearBuff, LightningEdgeBuff]:
            sk.set_disabled_and_time_left(1) # 버프 묻은 채로 측정 시작
    
        return(BasicAttack,
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), 
                    Booster, ElvishBlessing, AncientSpirit, HerosOath, Sylphidia.ignore(), RoyalKnights,
                    CriticalReinforce, UnicornSpikeBuff, RegendrySpearBuff, LightningEdgeBuff, ElementalGhost,
                    globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()] +\
                [RoyalKnightsAttack, ElementalGhostSpirit,UnicornSpike, RegendrySpear, WrathOfEllil, IrkilaBreathInit] +\
                [ElementalKnights, ElementalKnights_1, ElementalKnights_2, GuidedArrow, MirrorBreak, MirrorSpider] +\
                [] +\
                [BasicAttack])