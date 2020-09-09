from dpmModule import boss
from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import bowmen
from math import ceil
#TODO : 5차 신스킬 적용

class CardinalStateWrapper(core.BuffSkillWrapper):
    def __init__(self, ancient_force_skills):
        '''
        0 : 디스차지
        1 : 블래스트
        2 : 트랜지션
        '''
        skill = core.BuffSkill("카디널 차지", 0, 99999999)
        super(CardinalStateWrapper, self).__init__(skill)
        
        self.state = 0
        self.ancient_force_skills = ancient_force_skills
        
    def is_state(self, state):
        if self.state == state:
            return True
        return False

    def check_state(self, state):
        if self.state != state:
            self.state = state
            for skill in self.ancient_force_skills:
                skill.reduce_cooltime(1000)
            return True
        else:
            return False
            
    def check_state_discharge(self):
        return self.check_state(0)
    
    def check_state_blast(self):
        return self.check_state(1)
    
    def check_state_transition(self):
        return self.check_state(2)

class RelicChargeStack(core.StackSkillWrapper):
    def __init__(self, ancient_guidance_buff, chtr):
        skill = core.BuffSkill("렐릭 차지", 0, 99999999)
        super(RelicChargeStack, self).__init__(skill, 1000)
        self.ancient_guidance_stack = 0
        self.ancient_guidance_buff = ancient_guidance_buff
        self.ancient_guidance_task = ancient_guidance_buff.build_task(chtr.get_skill_modifier())
        
    def vary(self, d):
        stack_before = self.stack
        res = super(RelicChargeStack, self).vary(d)
        if(self.ancient_guidance_buff.is_not_active()):
            self.ancient_guidance_stack += max(self.stack - stack_before,0)
        if self.ancient_guidance_stack > 1000:
            self.ancient_guidance_stack = 0
            res.cascade = [self.ancient_guidance_task]   #For stability
        return res
    
            
class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "dex"
        self.jobname = "패스파인더"
        self.vEnhanceNum = 11
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1
        self._combat = 0

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self._combat

        CriticalShot = core.InformedCharacterModifier("크리티컬 샷",crit = 40)
        AncientBowMastery = core.InformedCharacterModifier("에인션트 보우 마스터리", att = 30)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        
        EssenceOfArcher = core.InformedCharacterModifier("에센스 오브 아처", crit = 10, pdamage = 10, armor_ignore = 30)
        
        AdditionalTransitionPassive = core.InformedCharacterModifier("에디셔널 트랜지션(패시브)", patt = 20 + passive_level)
        
        AncientBowExpert = core.InformedCharacterModifier("에인션트 보우 엑스퍼트", att=60 + 2*passive_level, crit_damage = 10+ceil(passive_level/3))
        IllusionStep = core.InformedCharacterModifier("일루젼 스텝", stat_main = 80 + 2*passive_level)
        return [CriticalShot, AncientBowMastery, PhisicalTraining,
                                    EssenceOfArcher, AdditionalTransitionPassive, 
                                        AncientBowExpert, IllusionStep]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self._combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5 + 0.5*ceil(passive_level /2))

        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        카디널 : 20, 
        카디널 디스차지 : 10,(화살당)
        레이븐 : 10,
        다른 카디널 포스 사용시 : 에인션트포스/인챈트포스 1초 쿨감소
        
        하이퍼
        
        에인션트 포스 - 보스 킬러, 이그노어 가드
        카디널 포스- 리인포스, 에디셔널 인핸스, 보너스 어택
        
        코강 순서
        카디 - 카블 - 에인션트아스트라 - 카트 - 임팩트 - 미스텔 - 어썰트 - 레조넌스 - 레이븐
        
        5차 순서
        레이븐템페 - 크리인 - 얼티밋 - 가이디드 - 옵시 - 이볼브
        
        미스텔 미사용(데미지 감소함)
        '''
        passive_level = chtr.get_base_modifier().passive_level + self._combat
        ANCIENT_FORCE = core.CharacterModifier(pdamage_indep=10, boss_pdamage=50+20, armor_ignore=20)
        ENCHANT_FORCE = core.CharacterModifier(pdamage_indep=10, boss_pdamage=50)
        ######   Skill   ######
        # Buff skills
        AncientBowBooster = core.BuffSkill("에인션트 보우 부스터", 0, 300*1000, rem=True).wrap(core.BuffSkillWrapper)
        CurseTolerance = core.BuffSkill("커스 톨러런스", 0, 300*1000, rem=True).wrap(core.BuffSkillWrapper)
        SharpEyes = core.BuffSkill("샤프 아이즈", 0, (300+10*self._combat)*1000, crit = 20+ceil(self._combat/2), crit_damage = 15+ceil(self._combat/2), rem=True).wrap(core.BuffSkillWrapper)
        AncientGuidance = core.BuffSkill("에인션트 가이던스(버프)", 0, 30000, pdamage_indep = 15, cooltime = -1, rem = False).wrap(core.BuffSkillWrapper)
        CurseTransition = core.BuffSkill("커스 트랜지션", 0, 15*1000, crit_damage = 20, cooltime=-1).wrap(core.BuffSkillWrapper) # 5스택 유지 가정

        # Summon skills
        Raven = core.SummonSkill("레이븐", 450, 2670, 390, 4, 220*1000).setV(vEhc, 8, 3, False).wrap(core.SummonSkillWrapper)
        
        # Damage skills
        # 카디널 포스
        CardinalDischarge = core.DamageSkill("카디널 디스차지", 360+5*passive_level, (4 + 1)*2, 300, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        AdditionalDischarge = core.DamageSkill("에디셔널 디스차지", 0, 100 + 50 + passive_level, 3*(3+1)*(0.4+0.02*passive_level+0.1)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)

        CardinalBlast = core.DamageSkill("카디널 블래스트", 140, 4 + 1, (400+5*passive_level) * 1.1 * 1.1 * 1.1 * 1.1 * 1.1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdditionalBlast = core.DamageSkill("에디셔널 블래스트", 0, 150 + 50 + passive_level, (2+1)*3*(0.4+0.02*passive_level+0.1)).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        
        CardinalTransition = core.DamageSkill("카디널 트랜지션", 330, 540+7*passive_level, 5).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        AdditionalTransition = core.BuffSkill("에디셔널 트랜지션", 0, 7000, cooltime = -1).wrap(core.BuffSkillWrapper) #전환시 카디널 디스/블래 사용시 40%확률로 고대 1중첩

        # 에인션트 포스
        SplitMistel = core.DamageSkill("스플릿 미스텔", 540, 200+350+7*passive_level, 4, cooltime = 10*1000,
                    modifier = ANCIENT_FORCE).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        SplitMistelBonus = core.DamageSkill("스플릿 미스텔(보너스)", 0, 100+200+4*passive_level, 4 * 2,
                    modifier = ANCIENT_FORCE).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)

        TripleImpact = core.DamageSkill("트리플 임팩트", 420, 400 + 200+5*passive_level, 5*3, cooltime = 10*1000,
                    modifier = ANCIENT_FORCE).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
                
        #스택당 최종뎀 50이나 5스택 가정, 엣오레 임의딜레이 720
        EdgeOfResonance = core.DamageSkill("엣지 오브 레조넌스", 720, 800+15*self._combat, 6, cooltime = 15*1000,
                        modifier = ANCIENT_FORCE + core.CharacterModifier(pdamage_indep = 61.051)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        
        # 인챈트 포스
        ComboAssultHolder = core.DamageSkill("콤보 어썰트", 720, 0, 0, cooltime = 20 * 1000).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        
        ComboAssultDischarge = core.DamageSkill("콤보 어썰트(디스차지)", 0, 600+10*self._combat, 7,
                modifier = ENCHANT_FORCE).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)# 디버프 +1
        ComboAssultDischargeArrow = core.DamageSkill("콤보 어썰트(디스차지)(화살)", 0, 650+10*self._combat, 4,
                modifier = ENCHANT_FORCE).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        
        ComboAssultBlast = core.DamageSkill("콤보 어썰트(블래스트)", 0, 600+10*self._combat, 8,
                modifier = ENCHANT_FORCE).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)# 디버프 +1
        ComboAssultBlastArrow = core.DamageSkill("콤보 어썰트(블래스트)(화살)", 0, 600+10*self._combat, 5,
                modifier = ENCHANT_FORCE).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        
        ComboAssultTransition = core.DamageSkill("콤보 어썰트(트랜지션)", 0, 600+10*self._combat, 6,
                modifier = ENCHANT_FORCE).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)# 디버프 +5
        ComboAssultTransitionArrow = core.DamageSkill("콤보 어썰트(트랜지션)(화살)", 0, 650+10*self._combat, 5,
                modifier = ENCHANT_FORCE).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        
        ## 하이퍼
        RelicEvolution = core.BuffSkill("렐릭 에볼루션", 0, 0, cooltime = 120*1000).wrap(core.BuffSkillWrapper)
        #렐릭 게이지 최대로 충전, 딜레이 0-으로 가정
        
        AncientAstraHolder = core.DamageSkill("에인션트 아스트라", 630, 0, 0, cooltime = 80*1000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        
        # 21회 / 4회 사용
        AncientAstraDischarge = core.DamageSkill("에인션트 아스트라(디스차지)", 710, 450, 5, modifier = ENCHANT_FORCE).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AncientAstraDischargeArrow = core.DamageSkill("에인션트 아스트라(디스차지)(화살)", 0, 300, 0.3*2*2,
                modifier = ENCHANT_FORCE).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        
        AncientAstraBlast = core.DamageSkill("에인션트 아스트라(블래스트)", 3750, 1800, 10, modifier = ENCHANT_FORCE).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        
        AncientAstraTransition = core.DamageSkill("에인션트 아스트라(트랜지션)", 710, 450, 6*3, modifier = ENCHANT_FORCE).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120*1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        # 5차
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 3, 3)
        
        Evolve = core.SummonSkill("이볼브", 600, 3330, 450+vEhc.getV(5,5)*15, 7, 40*1000, cooltime = (121-int(0.5*vEhc.getV(5,5)))*1000).isV(vEhc,5,5).wrap(core.SummonSkillWrapper)
        UltimateBlast = core.DamageSkill("얼티밋 블래스트", 1800, 2500+100*vEhc.getV(2,2), 15, cooltime = 120*1000, 
                modifier = core.CharacterModifier(armor_ignore = 100, pdamage_indep = 100) + ANCIENT_FORCE).isV(vEhc, 2,2).wrap(core.DamageSkillWrapper)
            
        RavenTempest = core.SummonSkill("레이븐 템페스트", 720, 250, 500+20*vEhc.getV(0,0), 5, 25*1000, cooltime = 120*1000, modifier = ANCIENT_FORCE).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)

        ObsidionBarrierBlast = core.SummonSkill("옵시디언 배리어", 60, 480, 500+18*vEhc.getV(4,4), 4, 15000,cooltime = 200*1000, modifier = ENCHANT_FORCE).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)
        ######   Skill Wrapper   ######

        #이볼브 연계 설정
        Evolve.onAfter(Raven.controller(1))
        Raven.onConstraint(core.ConstraintElement("이볼브 사용시 사용 금지", Evolve, Evolve.is_not_active))
        
    
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 1, 1, 20)
    
        RelicCharge = RelicChargeStack(AncientGuidance, chtr)
        CardinalState = CardinalStateWrapper([SplitMistel, EdgeOfResonance, ComboAssultHolder, AncientAstraHolder])
        
        # 기본적인 스킬연계 연결
        SplitMistel.onAfter(SplitMistelBonus)
        ComboAssultBlast.onAfter(ComboAssultBlastArrow)
        ComboAssultDischarge.onAfter(ComboAssultDischargeArrow)
        ComboAssultTransition.onAfter(ComboAssultTransitionArrow)
        
        AncientAstraDischarge.onAfter(AncientAstraDischargeArrow)
        
        AncientAstraBlastRepeat = core.RepeatElement(AncientAstraBlast, 21)
        AncientAstraDischargeRepeat = core.RepeatElement(AncientAstraDischarge, 4)
        AncientAstraTransitionRepeat = core.RepeatElement(AncientAstraTransition, 21) 
        
        # 렐릭 차지 연결
        CardinalDischarge.onAfter(RelicCharge.stackController(20))
        CardinalBlast.onAfter(RelicCharge.stackController(20))
        CardinalTransition.onAfter(RelicCharge.stackController(20))
        
        Raven.onTick(RelicCharge.stackController(10))
        
        SplitMistel.onAfter(RelicCharge.stackController(-50))
        SplitMistel.onConstraint(core.ConstraintElement('50', RelicCharge, partial(RelicCharge.judge, 50, 1)))
        
        TripleImpact.onAfter(RelicCharge.stackController(-50))
        TripleImpact.onConstraint(core.ConstraintElement('50', RelicCharge, partial(RelicCharge.judge, 50, 1)))  

        EdgeOfResonance.onAfter(RelicCharge.stackController(-100))
        EdgeOfResonance.onConstraint(core.ConstraintElement('100', RelicCharge, partial(RelicCharge.judge, 100, 1)))
    
        ComboAssultHolder.onAfter(RelicCharge.stackController(-150))
        ComboAssultHolder.onConstraint(core.ConstraintElement('150', RelicCharge, partial(RelicCharge.judge, 150, 1)))
        
        AncientAstraHolder.onConstraint(core.ConstraintElement('300', RelicCharge, partial(RelicCharge.judge, 300, 1)))
        AncientAstraDischarge.onAfter(RelicCharge.stackController(-300))
        AncientAstraTransition.onAfter(RelicCharge.stackController(-57))
        
        RavenTempest.onConstraint(core.ConstraintElement('300', RelicCharge, partial(RelicCharge.judge, 300, 1)))
        RavenTempest.onAfter(RelicCharge.stackController(-300))
        RavenTempest.onTick(RelicCharge.stackController(20))
        
        ObsidionBarrierBlast.onConstraint(core.ConstraintElement('500', RelicCharge, partial(RelicCharge.judge, 500, 1)))
        ObsidionBarrierBlast.onAfter(RelicCharge.stackController(-500))
        
        RelicEvolution.onAfter(RelicCharge.stackController(1000))
        
        #카디널 차지 연결
        DischargeUsed = core.OptionalElement(CardinalState.check_state_discharge, AdditionalDischarge)
        BlastUsed = core.OptionalElement(CardinalState.check_state_blast, AdditionalBlast)
        TransitionUsed = core.OptionalElement(CardinalState.check_state_transition, AdditionalTransition)
        
        CardinalBlast.onAfter(BlastUsed)
        CardinalDischarge.onAfter(DischargeUsed)
        CardinalTransition.onAfter(TransitionUsed)
        
        #인챈트 포스 설정
        ComboAssultOptional = core.OptionalElement(partial(CardinalState.is_state,0), ComboAssultDischarge, 
                                core.OptionalElement(partial(CardinalState.is_state,1), ComboAssultBlast, ComboAssultTransition))
        
        AncientAstraOptional = core.OptionalElement(partial(CardinalState.is_state,0), AncientAstraDischargeRepeat, 
                                core.OptionalElement(partial(CardinalState.is_state,1), AncientAstraBlastRepeat, AncientAstraTransitionRepeat))
        
        ComboAssultHolder.onAfter(ComboAssultOptional)
        AncientAstraHolder.onAfter(AncientAstraOptional)
        
        # 커스 트랜지션
        ComboAssultDischarge.onAfter(CurseTransition)
        ComboAssultBlast.onAfter(CurseTransition)
        ComboAssultTransition.onAfter(CurseTransition)
        
        # 기본공격 = 블래스트-디스차지
        CardinalBlast.onAfter(CardinalDischarge)
        
        #레이븐 설정
        RavenTempest.onAfter(Raven.controller(25000))
        
        # 12초마다 트랜지션 사용
        CardinalTransition_ForceUse = core.DamageSkill("카디널 트랜지션(강제)", 0, 0, 0, cooltime = 12000).wrap(core.DamageSkillWrapper)
        CardinalTransition_ForceUse.onAfter(CardinalTransition)
        
        #에인션트 아스트라는 레이븐과 맞추고, 레이븐 이후 트랜지션 전환 후에 사용하도록 스케줄
        
        AncientAstraHolder.onBefore(CardinalTransition)
        #ObsidionBarrierBlast.set_disabled_and_time_left(10000)
        
        # 딜비중 높은 극딜기는 가이던스와 싱크로. -> 미사용함.
        #RavenTempest.onConstraint(core.ConstraintElement("가이던스와 같이", AncientGuidance, AncientGuidance.is_active))
        #UltimateBlast.onConstraint(core.ConstraintElement("가이던스와 같이", AncientGuidance, AncientGuidance.is_active))
        
        ### Exports ###
        return(CardinalBlast,
                [globalSkill.maple_heros(chtr.level, combat_level=self._combat), globalSkill.useful_wind_booster(),
                    AncientBowBooster, CurseTolerance, CurseTransition, SharpEyes,
                    RelicEvolution, EpicAdventure,
                    AncientGuidance, AdditionalTransition, CriticalReinforce,
                    globalSkill.soul_contract()] +\
                [CardinalTransition_ForceUse, 
                    AncientAstraHolder, TripleImpact, EdgeOfResonance, 
                        ComboAssultHolder, UltimateBlast] +\
                [Evolve, Raven, GuidedArrow, RavenTempest, ObsidionBarrierBlast] +\
                [] +\
                [CardinalBlast])