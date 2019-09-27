from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, SynchronizeRule, ConcurrentRunRule
from . import globalSkill

#TODO : 5차 신스킬 적용

class FrostEffectWrapper(core.BuffSkillWrapper):
    def __init__(self, skill):
        super(FrostEffectWrapper, self).__init__(skill)
        self.stack = 6  #Better point!
        self.skillType = "C" # This value is "T" or "C"
        self.modifierInvariantFlag = False
        
    def flow(self, diff, Type):
        #assert(Type =="T" or Type=="C")
        self.skillType = Type
        self.stack += diff
        self.stack = max(min(6,self.stack),0)

    def getFlow(self, diff, Type):
        self.flow(diff, Type)
        return core.ResultObject(0, core.CharacterModifier(), 0, sname = 'Frost Effect', spec = 'frost effect control')

    def getFlowHandler(self, diff, Type):
        return core.TaskHolder(core.Task(self, partial(self.getFlow, diff, Type)), "FrostEffect("+Type+")")

    def get_modifier(self):
        return core.CharacterModifier(crit_damage = 3*self.stack, pdamage = 12*self.stack*(self.skillType is "T"), armor_ignore = 0.2*5*self.stack)

#Infinity Graph Element
class InfinityWrapper(core.BuffSkillWrapper):
    def __init__(self, serverlag = 3):
        skill = core.BuffSkill("인피니티", 960, 40000, cooltime = 180 * 1000, rem = True, red = True)
        super(InfinityWrapper, self).__init__(skill)
        self.passedTime = 0
        self.serverlag = serverlag
        
    def spend_time(self, time):
        if self.onoff:
            self.passedTime += time
        super(InfinityWrapper, self).spend_time(time)
            
    def get_modifier(self):
        if self.onoff:
            return core.CharacterModifier(pdamage_indep = (70 + 4 * (self.passedTime // ((4+self.serverlag)*1000))) )
        else:
            return core.CharacterModifier()
        
    def _use(self, rem = 0, red = 0):
        self.passedTime = 0
        return super(InfinityWrapper, self)._use(rem = rem, red = red)


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = True
        self.jobtype = "int"
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'crit', 'boss_pdamage')
        self.preEmptiveSkills = 2
        
    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 20, pdamage = 60, crit_damage = 15)

    def apply_complex_options(self, chtr):
        chtr.buff_rem += 50
        chtr.add_property_ignorance(10)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(SynchronizeRule('소울 컨트랙트', '인피니티', 35000, -1), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('라이트닝 스피어', '인피니티'), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self):
        ######   Passive Skill   ######
        
        HighWisdom = core.InformedCharacterModifier("하이 위즈덤", stat_main = 40)
        SpellMastery = core.InformedCharacterModifier("스펠 마스터리", att = 10)
        MagicCritical = core.InformedCharacterModifier("매직 크리티컬", crit = 30, crit_damage = 13)
        ElementAmplication = core.InformedCharacterModifier("엘리멘트 엠플리피케이션", pdamage = 50)
        
        ElementalReset = core.InformedCharacterModifier("엘리멘탈 리셋", pdamage_indep = 50)
        
        MasterMagic = core.InformedCharacterModifier("마스터 매직", att = 30)
        ArcaneAim = core.InformedCharacterModifier("아케인 에임", armor_ignore = 20)
        
        return [HighWisdom, SpellMastery, MagicCritical, ElementalReset, MasterMagic, ElementAmplication, ArcaneAim]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -2.5)
        ExtremeMagic = core.InformedCharacterModifier("익스트림 매직", pdamage_indep = 20)
        ArcaneAim = core.InformedCharacterModifier("아케인 에임(실시간)", pdamage = 40)
        
        return [WeaponConstant, Mastery, ExtremeMagic, ArcaneAim]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        코강 순서
        체라-라스피-블자-오브-엘퀴
        
        썬브 8히트
        
        하이퍼 : 
        텔레포트 - 애드 레인지
        체인 라이트닝 - 리인포스/보너스어택/타겟수 증가
        오브 - 뎀증

        언스테이블 메모라이즈를 사용하지 않음
        라이트닝 스피어는 인피니티가 켜져 있을때만 사용함
        소울 컨트랙트는 인피니티 마지막과 맞춰서 사용
        
        그 외의 극딜기는 쿨마다 사용
        오브는 라스피와 썬브 직전에만 사용함(체라의 경우 풀스택 유지가 가능)
        썬브는 풀히트는 가정

        '''
        ######   Skill   ######
        #Buff skills
        Meditation = core.BuffSkill("메디테이션", 0, 240*1000, att = 30, rem = True, red = True).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10, red = True).wrap(core.BuffSkillWrapper)
        OverloadMana = core.BuffSkill("오버로드 마나", 0, 99999 * 10000, pdamage_indep = 8+int(0.1*vEhc.getV(1,2))).isV(vEhc,1,2).wrap(core.BuffSkillWrapper)
        
        #Damage Skills
        ChainLightening = core.DamageSkill("체인 라이트닝", 600, 230 + 2*combat, 9, modifier = core.CharacterModifier(crit = 25, pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        FrozenOrbEjac = core.SummonSkill("프로즌 오브", 450, 100, 200+4*combat, 1, 1999, cooltime = -1, modifier = core.CharacterModifier(pdamage = 10)).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)
    
        LighteningSpear = core.DamageSkill("라이트닝 스피어", 0, 0, 1, cooltime = 75 * 1000).wrap(core.DamageSkillWrapper)
        LighteningSpearSingle = core.DamageSkill("라이트닝 스피어(단일)", 250, 200, 7).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        LighteningSpearFinalizer = core.DamageSkill("라이트닝 스피어 막타", 0, 1500, 7).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        
        IceAgeHolder = core.DamageSkill("아이스 에이지 개시스킬", 870, 500 + vEhc.getV(2,3)*20, 10, cooltime = 60 * 1000, red = True).isV(vEhc,2,3).wrap(core.DamageSkillWrapper)
        IceAge = core.EjaculateSkill("아이스 에이지 사출기", 870, 375 + vEhc.getV(2,3)*15, 1, 15 * 1000).isV(vEhc,2,3).wrap(core.SummonSkillWrapper) #소환처리 해야함 ;; TODO
        
        Blizzard = core.DamageSkill("블리자드", 870, 900+10*combat, 4, cooltime = 45 * 1000, red = True).setV(vEhc, 2, 2, True).wrap(core.DamageSkillWrapper)
        
        ThunderBrake = core.DamageSkill("썬더브레이크 개시스킬", 0, 0, 1, red = True, cooltime = 45 * 1000).wrap(core.DamageSkillWrapper) #Awesome! -> Tandem 사출처리 해야함...Later. 690을 일단 급한대로 분배해서 사용.
        ThunderBrake1 = core.DamageSkill("썬더브레이크", 100, (750 + vEhc.getV(0,0)*30), 8).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ThunderBrake2 = core.DamageSkill("썬더브레이크(1)", 100, (750 + vEhc.getV(0,0)*30)*0.95, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake3 = core.DamageSkill("썬더브레이크(2)", 100, (750 + vEhc.getV(0,0)*30)*0.9, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake4 = core.DamageSkill("썬더브레이크(3)", 100, (750 + vEhc.getV(0,0)*30)*0.85, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake5 = core.DamageSkill("썬더브레이크(4)", 100, (750 + vEhc.getV(0,0)*30)*0.8, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake6 = core.DamageSkill("썬더브레이크(5)", 100, (750 + vEhc.getV(0,0)*30)*0.75, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake7 = core.DamageSkill("썬더브레이크(6)", 100, (750 + vEhc.getV(0,0)*30)*0.7, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake8 = core.DamageSkill("썬더브레이크(7)", 70, (750 + vEhc.getV(0,0)*30)*0.65, 8).wrap(core.DamageSkillWrapper)
        
        SpiritOfSnow = core.SummonSkill("스피릿 오브 스노우", 720, 3000, 800+36*vEhc.getV(3,1), 9, 30000, red = True, cooltime = 120*1000).isV(vEhc, 3,1).wrap(core.SummonSkillWrapper)
        
        #Summoning skill
        Elquiness = core.SummonSkill("엘퀴네스", 900, 3030, 380+6*combat, 1, 999999999).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)
        IceAura = core.SummonSkill("아이스 오라", 0, 1200, 0, 1, 999999999).wrap(core.SummonSkillWrapper)
        
        #FinalAttack
        BlizzardPassive = core.DamageSkill("블리자드 패시브", 0, (220+4*combat) * (0.6+0.01*combat), 1).setV(vEhc, 2, 2, True).wrap(core.DamageSkillWrapper)
        
        #special skills
        Infinity = InfinityWrapper()
        FrostEffect = core.BuffSkill("프로스트 이펙트", 0, 999999 * 1000).wrap(FrostEffectWrapper)
        
        ######   Skill Wrapper   ######
        #TODO : 블자 패시브가 스택을 유지시켜주나?
        #Frost Effect
        FrostIncrement = FrostEffect.getFlowHandler(1, "C")
        FrostDecrement = FrostEffect.getFlowHandler(-1, "T")
        
        #Ejaculator
        FrozenOrbEjac.onBefore(FrostIncrement)
        FrozenOrbEjac.onTick(FrostIncrement)
        FrozenOrbEjac.onAfter(BlizzardPassive)

        #Lightening Spear
        LighteningSpearSingle.onAfter(BlizzardPassive)
        LighteningSpearSingle.onBefore(FrostDecrement)
        LighteningSpearFinalizer.onAfter(BlizzardPassive)
        LighteningSpearFinalizer.onBefore(FrostDecrement)
        
        LighteningRepeator = core.RepeatElement(LighteningSpearSingle, 32)
        LighteningRepeator.onAfter(LighteningSpearFinalizer)
    
        LighteningSpear.onAfters([LighteningRepeator, FrozenOrbEjac])
        
        #damage skills
        ChainLightening.onAfter(BlizzardPassive)
        ChainLightening.onBefore(FrostDecrement)
        #ChainLightening.onAfter(FrostDecrement)
        
        IceAge.onTicks([BlizzardPassive, FrostIncrement])
        IceAgeHolder.onBefore(FrostIncrement)
        IceAgeHolder.onAfter(IceAge)
        
        Elquiness.onTick(FrostIncrement)
        
        Blizzard.onBefore(FrostIncrement)
        BlizzardPassive.onBefore(FrostEffect.getFlowHandler(0.6, "C"))
        
        node_before = ThunderBrake
        node_before.onBefore(FrostDecrement)
        node_before.onAfter(BlizzardPassive)
        
        SpiritOfSnow.onBefore(core.RepeatElement(FrostIncrement, 3))
        
        for node in [ThunderBrake1, ThunderBrake2, ThunderBrake3, ThunderBrake4, ThunderBrake5, ThunderBrake6, ThunderBrake7, ThunderBrake8]:
            node.onBefore(FrostDecrement)
            node.onAfter(BlizzardPassive)
            node_before.onAfter(node)
        
        ThunderBrake.onBefore(FrozenOrbEjac)
        
        Elquiness.onTick(BlizzardPassive)
        IceAura.onTick(FrostIncrement)
        
        SoulContract = globalSkill.soul_contract()

        return(ChainLightening,
                [Infinity, Meditation, EpicAdventure, OverloadMana, FrostEffect,
                globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster(),
                SoulContract] +\
                [IceAgeHolder, Blizzard, LighteningSpear, ThunderBrake] +\
                [Elquiness, IceAura, IceAge, FrozenOrbEjac, SpiritOfSnow] +\
                [] +\
                [ChainLightening])