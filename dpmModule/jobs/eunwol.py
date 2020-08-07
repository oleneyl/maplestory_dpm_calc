from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobclass import heroes
from .jobbranch import pirates
from . import jobutils
from ..execution.rules import RuleSet, InactiveRule, ReservationRule, ConcurrentRunRule

class SoulTrapBuffWrapper(core.StackSkillWrapper):
    def __init__(self, skill):
        self.debuffQueue = []
        self.currentTime = 0
        self.DEBUF_PERSISTENCE_TIME = 8000 # 8000ms
        super(SoulTrapBuffWrapper, self).__init__(skill, 10)
        
    def _use(self, rem = 0, red = 0):
        return super(SoulTrapBuffWrapper, self)._use()
    
    def _add_debuff(self):
        # 한 번에 디버프 2개 생성
        self.stack += 2
        self.debuffQueue += [self.currentTime]
        if self.stack > self._max:
            self.stack -= 2
            del(self.debuffQueue[0])
        return core.ResultObject(0, 0, 0)

    def add_debuff(self):
        return core.TaskHolder(core.Task(self, self._add_debuff), name="귀문진 디버프 추가")
    
    def spend_time(self, time):
        self.currentTime += time
        # debuff removal
        
        if self.debuffQueue:
            for idx, t in enumerate(self.debuffQueue):
                if t + self.DEBUF_PERSISTENCE_TIME > self.currentTime:
                    break
            if self.debuffQueue[0] + self.DEBUF_PERSISTENCE_TIME < self.currentTime:
                idx = 1
            if idx > 0:
                self.debuffQueue = self.debuffQueue[idx:]
                self.stack = 2 * len(self.debuffQueue)

        super(SoulTrapBuffWrapper, self).spend_time(time)
    
    def get_modifier(self):
        if self.onoff:
            return core.CharacterModifier(crit = 8 * self.stack, crit_damage = 1*self.stack)
        else:
            return self.disabledModifier
        

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.jobtype = "str"
        self.vEnhanceNum = 15
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'reuse', 'mess')
        self.preEmptiveSkills = 2

    def get_passive_skill_list(self):
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 60)
        SpiritLink_3 = core.InformedCharacterModifier("정령 결속 3",att = 20, pdamage = 20)

        SpiritLink_4 = core.InformedCharacterModifier("정령 결속 4",armor_ignore = 30, boss_pdamage = 30, pdamage_indep = 15)
        AdvancedNuckleMastery = core.InformedCharacterModifier("고급 너클 숙련",crit_damage = 20, pdamage_indep = 10)
        WeaknessFinding = core.InformedCharacterModifier("약점 간파",crit = 25)
        #체력 50%이하인 적에게 크리율 65%, 크뎀 20% 증가??

        LoadedDicePassive = core.InformedCharacterModifier("로디드 다이스(패시브)", att = self.vEhc.getV(4,4) + 10)
    
        return [PhisicalTraining, SpiritLink_3, 
                SpiritLink_4, AdvancedNuckleMastery, WeaknessFinding, LoadedDicePassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -5)   
        Weakness = core.InformedCharacterModifier("약화",pdamage = 20) #디버프지만 상시발동가정    
        return [WeaponConstant, Mastery, Weakness]

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(InactiveRule("파쇄철조-회", "파쇄철조-반"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("소혼 장막(시전)", "수호 정령(소혼 장막)"), RuleSet.BASE)
        #ruleset.add_rule(ReservationRule("소울 컨트랙트", "정령 집속"), RuleSet.BASE)
        return ruleset

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        ----정보---
        하이퍼 : 귀참 3개, 폭류권 리인포스, 여우령 소환확률 +10%
        
        소혼장막 150ms / 60초마다 랑혼장막 사용
        귀문진 930ms마다 공격
        
        V강화 : (15개)
        귀참, 폭류권, 여우령
        분격, 소혼장막
        
        정결극 유지 100%
        
        정령 집속 : 무작위 스킬 1회 발동, 키다운은 3초 지속, 정령 공격은 2초마다 발동 1742퍼뎀으로 1회공격 가정.
        '''
        SOULENHANCEREM = 100
        
        ######   Skill   ######
        #Buff skills

        FoxSoul = core.DamageSkill("여우령", 0, 200, 3 * (0.25+0.1)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        SoulAttack = core.DamageSkill("귀참", 600, 265, 12 + 1, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        DoubleBodyAttack = core.DamageSkill("분혼 격참(공격)", 0, 2000, 1).wrap(core.DamageSkillWrapper)
        DoubleBody = core.BuffSkill("분혼 격참", 1000, 10000, cooltime = 180 * 1000, red = True, pdamage_indep = 20).wrap(core.BuffSkillWrapper)
    
        #하이퍼스킬
        #정결극 유지율 100%
        EnhanceSpiritLink = core.BuffSkill("정령 결속 극대화", 0, 120000 * (SOULENHANCEREM/100), cooltime = 120*1000, boss_pdamage = 20, pdamage = 35, att = 20, armor_ignore = 20).wrap(core.BuffSkillWrapper)
        EnhanceSpiritLinkSummon_S = core.SummonSkill("수호 정령(간간 수월래)", 0, 3000, 275, 3, 120000 * (SOULENHANCEREM/100), cooltime = -1).wrap(core.SummonSkillWrapper)
        EnhanceSpiritLinkSummon_J_Init = core.SummonSkill("수호 정령(소혼 장막)(시전)", 0, 60 * 1000, 0, 0, 120000 * (SOULENHANCEREM/100), cooltime = -1).wrap(core.SummonSkillWrapper)
        EnhanceSpiritLinkSummon_J = core.SummonSkill("수호 정령(소혼 장막)", 0, 150, 150, 1, 4800, cooltime = -1).wrap(core.SummonSkillWrapper)
        
        #소혼 장막을 은월이 시전해야함
        #소혼 장막: 최대 10명의 적을 150% 데미지로 4.8초 동안 지속 공격, 수호 정령이 소혼 장막을 시전 하는 동안 은월이 시전하는 소혼장막의 최종 데미지 700% 증가. 재사용 대기시간 60초
        #최종 데미지 450 -> 700으로 수정
        SpiritFrenzy = core.DamageSkill("소혼 장막(시전)", 0, 0, 0, cooltime=10*1000 + 10080).wrap(core.DamageSkillWrapper)
        SpiritFrenzy_Tick = core.DamageSkill("소혼 장막", 180, 45, 5, cooltime = -1, modifier=core.CharacterModifier(pdamage_indep = 700)).setV(vEhc, 3, 3, False).wrap(core.DamageSkillWrapper)
        SpiritFrenzy.onAfter(core.RepeatElement(SpiritFrenzy_Tick, 56))

        LuckyDice = core.BuffSkill("로디드 다이스", 0, 180*1000, pdamage = 20).isV(vEhc,4,4).wrap(core.BuffSkillWrapper)
        #1중첩 럭다 재사용 50초 감소 / 방어력30% / 체엠 20% / 크리율15% / 뎀증20 / 경치30
        #2중첩 럭다 재사용 50초 감소 / 방어력40% / 체엠 30% / 크리율25% / 뎀증30 / 경치40
        #7 발동시 방무 20 -> 30
        HerosOath = core.BuffSkill("히어로즈 오쓰", 0, 60000, cooltime = 120000, pdamage = 10).wrap(core.BuffSkillWrapper)
        Frid = heroes.FridWrapper(vEhc, 0, 0)
    
        #오버드라이브 (앱솔 가정)
        #TODO: 템셋을 읽어서 무기별로 다른 수치 적용하도록 만들어야 함.

        WEAPON_ATT = jobutils.get_weapon_att("너클")
        Overdrive, OverdrivePenalty = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
        
        SoulConcentrate = core.BuffSkill("정령 집속", 960, (30+vEhc.getV(2,1))*1000, cooltime = 120*1000, pdamage_indep = (5+vEhc.getV(2,1)//2)).isV(vEhc,2,1).wrap(core.BuffSkillWrapper)
        SoulConcentrateSummon = core.SummonSkill("정령 집속(무작위)", 0, 2000, 1742, 1, (30+vEhc.getV(2,1))*1000, cooltime = -1).isV(vEhc,2,1).wrap(core.SummonSkillWrapper)

        # 귀문진: 정령을 한번에 2마리 소환함
        SoulTrap = core.SummonSkill("귀문진", 1000, 930, 600+24*vEhc.getV(3,2), 3 * 2, 40000, cooltime = (120-vEhc.getV(3,2))*1000).isV(vEhc,3,2).wrap(core.SummonSkillWrapper)
        SoulTrapBuff = core.BuffSkill("귀문진(버프)", 0, 50000, cooltime = -1).wrap(SoulTrapBuffWrapper)
        # 귀문진(버프)는 마지막 귀문진 디버프가 사라질 때까지 유지하기 위해 여유시간을 추가하였음

        RealSoulAttack = core.DamageSkill("진 귀참", 600, 540+6*vEhc.getV(1,3), 12 + 1, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20) + core.CharacterModifier(armor_ignore=50)).setV(vEhc, 0, 2, False).isV(vEhc,1,3).wrap(core.DamageSkillWrapper)
        RealSoulAttackCounter = core.BuffSkill("진 귀참(딜레이)", 0, 6000, cooltime = -1).wrap(core.BuffSkillWrapper)
        
        DoubleBodyRegistance = core.BuffSkill("분혼 격참(저항)", 0, 90000, cooltime = -1).wrap(core.BuffSkillWrapper)

        # 파쇄철조 (디버프용)
        BladeImp = core.DamageSkill("파쇄철조-회", 90, 160, 4).wrap(core.DamageSkillWrapper)
        BladeImpBuff = core.BuffSkill("파쇄철조-반", 0, 15 * 1000, cooltime=-1, pdamage_indep=10).wrap(core.BuffSkillWrapper)
        ######   Skill Wrapper   ######
        
        #분혼 격참
        DoubleBody.onAfter(DoubleBodyAttack)
        DoubleBody.onAfter(DoubleBodyRegistance)
        DoubleBodyConstraint = core.ConstraintElement("분혼 격참(저항)(제한)", DoubleBodyRegistance, DoubleBodyRegistance.is_not_active)
        DoubleBody.onConstraint(DoubleBodyConstraint)
        
        #정결극 위계
        EnhanceSpiritLink.onAfters([EnhanceSpiritLinkSummon_S, EnhanceSpiritLinkSummon_J_Init])
        EnhanceSpiritLinkSummon_J_Init.onTick(EnhanceSpiritLinkSummon_J)
        
        #정령 집속
        SoulConcentrate.onAfter(DoubleBody.controller(1.0, 'reduce_cooltime_p'))
        SoulConcentrate.onAfter(SoulConcentrateSummon)

        #귀문진
        SoulTrap.onTick(SoulTrapBuff.add_debuff())
        SoulTrap.onAfter(SoulTrapBuff)
        
        #진 귀참 알고리즘
        RealSoulAttack.onAfter(RealSoulAttackCounter)
        BasicAttack = core.OptionalElement(RealSoulAttackCounter.is_active, SoulAttack, RealSoulAttack, name = "진 귀참 발동 불가능?")

        BasicAttackWrapper = core.DamageSkill('기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)

        #여우령
        BasicAttack.onAfter(FoxSoul)
        SoulTrap.onTick(FoxSoul)
        SoulConcentrateSummon.onTick(FoxSoul)
        SpiritFrenzy_Tick.onAfter(FoxSoul)
        
        #파쇄철조
        BladeImp.onAfter(BladeImpBuff)

        schedule = core.ScheduleGraph()
        
        return(BasicAttackWrapper, 
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster(),
                    EnhanceSpiritLink, LuckyDice, HerosOath, Frid, 
                    Overdrive, OverdrivePenalty, SoulConcentrate, DoubleBody, SoulTrapBuff,
                    globalSkill.soul_contract()] +\
                [BladeImp, BladeImpBuff, SoulTrap] +\
                [EnhanceSpiritLinkSummon_S, EnhanceSpiritLinkSummon_J_Init, EnhanceSpiritLinkSummon_J, SoulConcentrateSummon] +\
                [RealSoulAttackCounter, DoubleBodyRegistance, SpiritFrenzy] +\
                [BasicAttackWrapper])
        
        return schedule
