from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, SynchronizeRule
from . import globalSkill
from functools import partial
from .jobclass import adventurer
from .jobbranch import magicians
#비숍 소환수 뎀증보너스 적용
class SacredMarkWrapper(core.BuffSkillWrapper):
    def __init__(self):
        #special skills
        skill = core.BuffSkill("소환수 표식", 0, 999999 * 1000)
        super(SacredMarkWrapper, self).__init__(skill)
        self.stack = 1  #Better point!
        self.bonus = 25 # This value is 25 or 50
        
    def flow(self, diff, bonus = 0):
        self.stack += diff
        self.stack = max(min(1,self.stack),0)
        if diff == 1:
            self.bonus = bonus

    def get_modifier(self):
        return core.CharacterModifier(pdamage_indep = self.stack*self.bonus)

    def getFlow(self, diff, bonus = 0):
        def retftn():
            self.flow(diff, bonus)
            return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname = 'Sacred Mark', spec = 'frost effect control')
        return core.Task(self, retftn)
        
    def getFlowHandler(self, diff, bonus):
        return core.TaskHolder(self.getFlow(diff, bonus), "소환수 표식")
    
    def statusChecker(self, bonus):
        def checker():
            if self.stack == 1 and self.bonus == bonus:
                return True
            else:
                return False
        
        return checker
    
'''This function is recommended.
'''
class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = True
        self.jobtype = "int"
        self.vEnhanceNum = 8
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'crit', 'boss_pdamage')
        self.preEmptiveSkills = 1

    def apply_complex_options(self, chtr):
        chtr.buff_rem += 50
        chtr.add_property_ignorance(10)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(SynchronizeRule('소울 컨트랙트', '인피니티', 35000, -1), RuleSet.BASE)
        ruleset.add_rule(SynchronizeRule('프레이', '인피니티', 45000, -1), RuleSet.BASE)        
        return ruleset

    def get_passive_skill_list(self):
        HighWisdom = core.InformedCharacterModifier("하이 위즈덤",stat_main = 40)
        SpellMastery = core.InformedCharacterModifier("스펠 마스터리",att = 10)
        
        MagicCritical = core.InformedCharacterModifier("매직 크리티컬",crit = 30, crit_damage = 13)
        HolyFocus = core.InformedCharacterModifier("홀리 포커스",crit = 40)
        
        MasterMagic = core.InformedCharacterModifier("마스터 매직",att = 30)
        ArcaneAim = core.InformedCharacterModifier("아케인 에임", armor_ignore = 20)
        
        VengenceOfAngelOff = core.InformedCharacterModifier("벤전스 오브 엔젤(off)",pdamage = 40)
        #엔젤레이 반영 필요
        
        return [HighWisdom, SpellMastery, MagicCritical, HolyFocus, MasterMagic, ArcaneAim, VengenceOfAngelOff]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -2.5)       
        BlessingEnsemble = core.InformedCharacterModifier("블레싱 앙상블",pdamage_indep = 3)

        ArcaneAim = core.InformedCharacterModifier("아케인 에임",pdamage = 40)
        VengenceOfAngelOn = core.InformedCharacterModifier("벤전스 오브 엔젤(on)", att = 50, pdamage_indep = 30, armor_ignore = 20, pdamage=-40)#속서애성을 pdamage_indep으로 임시 계싼
        return [WeaponConstant, Mastery, ArcaneAim, VengenceOfAngelOn, BlessingEnsemble]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        ######   Skill   ###### 
        '''리브라 ON
        서버렉 3초
        피스메이커 즉시 폭발
        
        프레이는 인피가 종료될 때 같이 종료되도록 맞추어서 사용
        소울 컨트랙트는 인피 마지막과 맞춰서 사용
        리브라는 쿨마다 사용
        '''
        serverlag = 3
        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 240000, rem = True).wrap(core.BuffSkillWrapper)
        AdvancedBless = core.BuffSkill("어드밴스드 블레스", 0, 240000, att = 30 + combat*1 + 20, boss_pdamage = 10, rem = True).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        OverloadMana = OverloadMana = magicians.OverloadManaWrapper(vEhc, 1, 4)
        
        charMainStat = chtr.get_modifier().stat_main * (1 + 0.01 * chtr.get_modifier().pstat_main)
        Pray = core.BuffSkill("프레이", 810, 1000 * (30 + 0.5 * vEhc.getV(2,2)), cooltime = 180 * 1000, red = True, pdamage_indep = (5 + (charMainStat // 2500))).isV(vEhc, 2,2).wrap(core.BuffSkillWrapper)
        
        #Damage Skills
        AngelRay = core.DamageSkill("엔젤레이", 630, 225 + 5*combat, 14).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper) #벤전스 사용 가정
        AngelRay_25 = core.DamageSkill("엔젤레이(25)", 630, 225 + 5*combat, 14, modifier = core.CharacterModifier(pdamage_indep = 25)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper) #벤전스 사용 가정
        AngelRay_50 = core.DamageSkill("엔젤레이(50)", 630, 225 + 5*combat, 14, modifier = core.CharacterModifier(pdamage_indep = 50)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper) #벤전스 사용 가정
        
        HeavensDoor = core.DamageSkill("헤븐즈도어", 1080, 1000, 8, cooltime = 180 * 1000).wrap(core.DamageSkillWrapper)   #사용하지 않는다--> 일단 Wrapper 제작 안할 것.
        PeaceMaker = core.DamageSkill("피스메이커", 750, 350 + 14*vEhc.getV(0,0), 12, cooltime = 10 * 1000, red = True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper) #풀스택시 미발동..
        PeaceMakerFinal = core.DamageSkill("피스메이커 최종", 0, 500 + 20*vEhc.getV(0,0), 8).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        PeaceMakerFinalBuff = core.BuffSkill("피스메이커 최종 버프", 0, (8 + serverlag)*1000, pdamage = (5 + vEhc.getV(0,0) // 5) + 12, cooltime = -1).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)  #풀스택 가정
    
        #Summoning skill
        Bahamutt = core.SummonSkill("바하뮤트", 600, 3030, 500+6*combat, 1, 90 * 1000, cooltime = 120 * 1000, rem = True).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)    #최종뎀25%스택
        AngelOfLibra = core.SummonSkill("엔젤 오브 리브라", 540, 3333, 500 + 20*vEhc.getV(3,1), 12, 30 * 1000, cooltime = 120 * 1000).isV(vEhc,3,1).wrap(core.SummonSkillWrapper)    #바하뮤트와 겹치지 않도록 재정의 필요, 최종뎀50%스택
        
        ######   Wrappers    ######
        Infinity = adventurer.InfinityWrapper()
        SacredMark = SacredMarkWrapper()
        
        MarkIncrement25 = SacredMark.getFlowHandler(1, 25)
        MarkIncrement50 = SacredMark.getFlowHandler(1, 50)
        MarkDecrement = SacredMark.getFlowHandler(-1, 0)
    
        #damage skills
        AngelRay.onJustAfter(MarkDecrement)
        AngelRay_25.onJustAfter(MarkDecrement)
        AngelRay_50.onJustAfter(MarkDecrement)
        PeaceMakerFinalBuff.set_disabled_and_time_left(-1)
        
        PeaceMakerFinal.onJustAfter(MarkDecrement)
        PeaceMaker.onAfters([PeaceMakerFinal, PeaceMakerFinalBuff, MarkDecrement])
        
        Bahamutt.onTick(MarkIncrement25)
        AngelOfLibra.onTick(MarkIncrement50)
        
        #Scheduling(?)
        
        PeaceMakerFinalBuff.set_disabled_and_time_left(-1)
        
        AngelOfLibra.onAfter(core.TaskHolder(core.Task(Bahamutt, partial(Bahamutt.set_disabled_and_time_left,1))))
        Bahamutt.onConstraint(core.ConstraintElement("리브라와 동시사용 불가", AngelOfLibra, AngelOfLibra.is_not_active))

        AngelRay_is25 = core.OptionalElement(SacredMark.statusChecker(25), AngelRay_25, AngelRay)
        MainAttack = core.OptionalElement(SacredMark.statusChecker(50), AngelRay_50, AngelRay_is25)

        MainAttackWrapped = core.DamageSkill('기본공격',0,0,0).wrap(core.DamageSkillWrapper)
        MainAttackWrapped.onAfter(MainAttack)

        SoulContract = globalSkill.soul_contract()
        
        return(MainAttackWrapped, 
                [Booster, SacredMark, Infinity, PeaceMakerFinalBuff, Pray, EpicAdventure, OverloadMana,
                globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster(),
                SoulContract] +\
                [PeaceMaker] +\
                [AngelOfLibra, Bahamutt] +\
                [] +\
                [MainAttackWrapped])