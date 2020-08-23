from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, SynchronizeRule, ConcurrentRunRule
from . import globalSkill
from .jobclass import adventurer
from .jobbranch import magicians

#TODO : 5차 신스킬 적용

class FrostEffectWrapper(core.StackSkillWrapper):
    def __init__(self, skill):
        super(FrostEffectWrapper, self).__init__(skill, 5)
        self.stack = 5  # Better point!
        self.modifierInvariantFlag = False
    
    def get_modifier(self):
        return core.CharacterModifier(crit_damage = 3*self.stack, pdamage = 12*self.stack, armor_ignore = 0.2*5*self.stack)


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = True
        self.jobtype = "int"
        self.jobname = "아크메이지썬/콜"
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'crit', 'boss_pdamage')
        self.preEmptiveSkills = 2
        
    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 20, pdamage = 60, crit_damage = 15)

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
        
        MasterMagic = core.InformedCharacterModifier("마스터 매직", att = 30, buff_rem = 50)
        ArcaneAim = core.InformedCharacterModifier("아케인 에임", armor_ignore = 20)
        
        return [HighWisdom, SpellMastery, MagicCritical, ElementalReset, MasterMagic, ElementAmplication, ArcaneAim]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -2.5)
        ExtremeMagic = core.InformedCharacterModifier("익스트림 매직", pdamage_indep = 20)
        ArcaneAim = core.InformedCharacterModifier("아케인 에임(실시간)", pdamage = 40)
        ElementalResetActive = core.InformedCharacterModifier("엘리멘탈 리셋(사용)", prop_ignore = 10)
        
        return [WeaponConstant, Mastery, ExtremeMagic, ArcaneAim, ElementalResetActive]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        코강 순서
        체라-라스피-블자-오브-엘퀴-썬더스톰
        
        썬브 8히트
        
        하이퍼 : 
        텔레포트 - 애드 레인지
        체인 라이트닝 - 리인포스/보너스어택/타겟수 증가
        오브 - 뎀증

        언스테이블 메모라이즈를 사용하지 않음
        라이트닝 스피어는 인피니티가 켜져 있을때만 사용함
        소울 컨트랙트는 인피니티 마지막과 맞춰서 사용
        
        그 외의 극딜기는 쿨마다 사용
        오브는 쿨마다 사용, 19타
        썬브는 풀히트는 가정

        '''
        ######   Skill   ######
        #Buff skills
        Meditation = core.BuffSkill("메디테이션", 0, 240*1000, att = 30, rem = True, red = True).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10, red = True).wrap(core.BuffSkillWrapper)
        OverloadMana = magicians.OverloadManaWrapper(vEhc, 1, 2)
        
        #Damage Skills
        ChainLightening = core.DamageSkill("체인 라이트닝", 600, 185 + 3*combat, 10+1, modifier = core.CharacterModifier(crit = 25, pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        FrozenOrbEjac = core.SummonSkill("프로즌 오브", 690, 210, 220+4*combat, 1, 4000, cooltime = 5000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)
    
        LighteningSpear = core.DamageSkill("라이트닝 스피어", 0, 0, 1, cooltime = 75 * 1000).wrap(core.DamageSkillWrapper)
        LighteningSpearSingle = core.DamageSkill("라이트닝 스피어(단일)", 270, 200, 7).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        LighteningSpearFinalizer = core.DamageSkill("라이트닝 스피어 막타", 1080, 1500, 7).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        
        IceAgeInit = core.DamageSkill("아이스 에이지(개시)", 660, 500 + vEhc.getV(2,3)*20, 10, cooltime = 60 * 1000, red = True).isV(vEhc,2,3).wrap(core.DamageSkillWrapper)
        IceAgeSummon = core.SummonSkill("아이스 에이지(장판)", 0, 810, 125 + vEhc.getV(2,3)*5, 3, 15 * 1000, cooltime = -1).isV(vEhc,2,3).wrap(core.SummonSkillWrapper)
                
        # 중첩당 감소량 5%
        # TODO: 썬브가 이전 스킬 딜레이 캔슬하는것 구현해야 함
        ThunderBrake = core.DamageSkill("썬더 브레이크 개시스킬", 120, 0, 1, red = True, cooltime = 40 * 1000).wrap(core.DamageSkillWrapper) #Awesome! -> Tandem 사출처리 해야함...Later. 690을 일단 급한대로 분배해서 사용.
        ThunderBrake1 = core.DamageSkill("썬더 브레이크(1)", 120, (750 + vEhc.getV(0,0)*30), 8).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ThunderBrake2 = core.DamageSkill("썬더 브레이크(2)", 120, (750 + vEhc.getV(0,0)*30)*0.95, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake3 = core.DamageSkill("썬더 브레이크(3)", 120, (750 + vEhc.getV(0,0)*30)*0.9, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake4 = core.DamageSkill("썬더 브레이크(4)", 120, (750 + vEhc.getV(0,0)*30)*0.85, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake5 = core.DamageSkill("썬더 브레이크(5)", 120, (750 + vEhc.getV(0,0)*30)*0.8, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake6 = core.DamageSkill("썬더 브레이크(6)", 120, (750 + vEhc.getV(0,0)*30)*0.75, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake7 = core.DamageSkill("썬더 브레이크(7)", 120, (750 + vEhc.getV(0,0)*30)*0.7, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake8 = core.DamageSkill("썬더 브레이크(8)", 120, (750 + vEhc.getV(0,0)*30)*0.65, 8).wrap(core.DamageSkillWrapper)
        
        # 단일 대상 기준
        SpiritOfSnow = core.SummonSkill("스피릿 오브 스노우", 720, 3000, 850+34*vEhc.getV(3,1), 9, 30000, red = True, cooltime = 120*1000).isV(vEhc, 3,1).wrap(core.SummonSkillWrapper)
                
        #Summoning skill
        ThunderStorm = core.SummonSkill("썬더 스톰", 900, 1770, 430, 1, 90000, cooltime = 30000).setV(vEhc, 5, 3, False).wrap(core.SummonSkillWrapper)
        Elquiness = core.SummonSkill("엘퀴네스", 600, 3030, 380+6*combat, 1, 260*1000).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)
        IceAura = core.SummonSkill("아이스 오라", 0, 1200, 0, 1, 999999999).wrap(core.SummonSkillWrapper)
        
        #FinalAttack
        Blizzard = core.DamageSkill("블리자드", 720, 450+5*combat, 8, cooltime = 45 * 1000, red = True).setV(vEhc, 2, 2, True).wrap(core.DamageSkillWrapper)
        BlizzardPassive = core.DamageSkill("블리자드 패시브", 0, (220+4*combat) * (0.6+0.01*combat), 1).setV(vEhc, 2, 2, True).wrap(core.DamageSkillWrapper)
        
        #special skills
        Infinity = adventurer.InfinityWrapper()
        FrostEffect = core.BuffSkill("프로스트 이펙트", 0, 999999 * 1000).wrap(FrostEffectWrapper)
        
        ######   Skill Wrapper   ######
        #Frost Effect
        FrostIncrement = FrostEffect.stackController(1)
        FrostDecrement = FrostEffect.stackController(-1)
        
        #Ejaculator
        FrozenOrbEjac.onTick(FrostIncrement)
        FrozenOrbEjac.onTick(BlizzardPassive)

        #Lightening Spear
        LighteningSpearSingle.onAfter(BlizzardPassive)
        LighteningSpearSingle.onAfter(FrostDecrement)
        LighteningSpearFinalizer.onAfter(BlizzardPassive)
        LighteningSpearFinalizer.onAfter(FrostDecrement)
        
        LighteningRepeator = core.RepeatElement(LighteningSpearSingle, 30)
        LighteningRepeator.onAfter(LighteningSpearFinalizer)
    
        LighteningSpear.onAfter(LighteningRepeator)
        
        #damage skills
        ChainLightening.onAfter(BlizzardPassive)
        ChainLightening.onAfter(FrostDecrement)
        
        IceAgeSummon.onTicks([BlizzardPassive, FrostIncrement])
        IceAgeInit.onBefore(FrostIncrement)
        IceAgeInit.onAfter(BlizzardPassive)
        IceAgeInit.onAfter(IceAgeSummon)
        
        Elquiness.onTick(FrostIncrement)
        
        Blizzard.onBefore(FrostIncrement)
        BlizzardPassive.onBefore(FrostEffect.stackController(0.6))
        
        SpiritOfSnow.onTick(FrostEffect.stackController(3))
        
        node_before = ThunderBrake
        
        for node in [ThunderBrake1, ThunderBrake2, ThunderBrake3, ThunderBrake4, ThunderBrake5, ThunderBrake6, ThunderBrake7, ThunderBrake8]:
            node.onAfter(FrostDecrement)
            node.onAfter(BlizzardPassive)
            node_before.onAfter(node)
        
        Elquiness.onTick(BlizzardPassive)
        IceAura.onTick(FrostIncrement)
        
        SoulContract = globalSkill.soul_contract()

        return(ChainLightening,
                [Infinity, Meditation, EpicAdventure, OverloadMana, FrostEffect,
                globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster(),
                SoulContract] +\
                [IceAgeInit, Blizzard, LighteningSpear, ThunderBrake] +\
                [ThunderStorm, Elquiness, IceAura, IceAgeSummon, FrozenOrbEjac, SpiritOfSnow] +\
                [] +\
                [ChainLightening])