from enum import Enum

from dpmModule.jobs.globalSkill import GlobalSkills
from dpmModule.jobs.jobbranch.pirates import PirateSkills

from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import DisableRule, InactiveRule, RuleSet, ConditionRule, MutualRule
from . import globalSkill
from .jobbranch import pirates
from .jobclass import adventurer
from . import jobutils
from math import ceil
from typing import Any, Dict


# English skill information for Buccaneer here https://maplestory.fandom.com/wiki/Buccaneer/Skills
class BuccaneerSkills(Enum):
    # link Skill
    PirateBlessing = 'Pirate Blessing | 파이렛 블레스'
    # Beginner
    SuperTransformation = 'Super Transformation | 슈퍼 트랜스폼'
    # 1st Job
    SommersaultKick = 'Sommersault Kick | 써머솔트 킥'
    DoubleShot = 'Double Shot | 더블 파이어'
    Octopush = 'Octopush | 옥토푸시'
    Dash = 'Dash | 대쉬'
    ShadowHeart = 'Shadow Heart | 크리티컬 로어'
    BulletTime = 'Bullet Time | 퀵모션'
    # 2nd Job
    TornadoUppercut = 'Tornado Uppercut | 토네이도 어퍼'
    EnergyVortex = 'Energy Vortex | 에너지 토네이도'
    EnergyCharge = 'Energy Charge | 에너지 차지'
    CorkscrewBlow = 'Corkscrew Blow | 스크류 펀치'
    DarkClarity = 'Dark Clarity | 멘탈 클리어리티'
    KnuckleBooster = 'Knuckle Booster | 너클 부스터'
    AdvancedDash = 'Advanced Dash | 어드밴스드 대쉬'
    KnuckleMastery = 'Knuckle Mastery | 너클 마스터리'
    HPBoost = 'HP Boost | HP 증가'
    PhysicalTraining = 'Physical Training | 피지컬 트레이닝'
    Perseverance = 'Perseverance | 인듀어런스'
    # 3rd Job
    SpiralAssault = 'Spiral Assault | 더블 스파이럴'
    EnergyBurst = 'Energy Burst | 에너지 버스터'
    HedgehogBuster = 'Hedgehog Buster | 헤지호그 버스터'
    Supercharge = 'Supercharge | 슈퍼 차지'
    StaticThumper = 'Static Thumper | 쇼크웨이브'
    RolloftheDice = 'Roll of the Dice | 럭키 다이스'
    AdmiralsWings = 'Admiral\'s Wings | 윌로우 디펜시브'
    PrecisionStrikes = 'Precision Strikes | 크리티컬 레이지'
    StunMastery = 'Stun Mastery | 스턴 마스터리'
    # 4th Job
    Octopunch = 'Octopunch | 피스트 인레이지'
    DragonStrike = 'Dragon Strike | 드래곤 스트라이크'
    NautilusStrike = 'Nautilus Strike | 전함 노틸러스'
    BuccaneerBlast = 'Buccaneer Blast | 에너지 블라스트'
    DoubleBlast = 'Double Blast | 더블 블라스트'
    Crossbones = 'Crossbones | 바이퍼지션'
    TimeLeap = 'Time Leap | 타임 리프'
    SpeedInfusion = 'Speed Infusion | 윈드 부스터'
    DoubleDown = 'Double Down | 더블 럭키 다이스'
    UltraCharge = 'Ultra Charge | 울트라 차지'
    PiratesRevenge = 'Pirate\'s Revenge | 카운터 어택'
    TyphoonCrush = 'Typhoon Crush | 가드 크러시'
    # Hypers
    PowerUnity = 'Power Unity | 유니티 오브 파워'
    EpicAdventure = 'Epic Adventure | 에픽 어드벤처'
    StimulatingConversation = 'Stimulating Conversation | 스티뮬레이트'
    # 5th Job
    Meltdown = 'Meltdown | 트랜스 폼'
    LordoftheDeep = 'Lord of the Deep | 서펜트 스크류'
    SerpentVortex = 'Serpent Vortex | 퓨리어스 차지'
    HowlingFist = 'Howling Fist | 하울링 피스트'


class EnergyChargeWrapper(core.StackSkillWrapper):
    def __init__(self, combat):
        skill = core.BuffSkill(BuccaneerSkills.EnergyCharge.value, 0, 999999*1000)
        super(EnergyChargeWrapper, self).__init__(skill, 10000)
        self.stack = 0
        self.charged = False
        self.combat = combat
        self.drainCallback = None
    
    def charge(self, val, force):
        if (force or not self.charged) and val > 0:
            self.stack = min(self.stack + val, 10000)
        elif val < 0:
            self.stack = max(self.stack + val, 0)
        if self.charged and self.stack <= 0:
            self.charged = False
        elif (not self.charged) and self.stack >= 10000:
            self.charged = True
        if self.stack <= 0:
            self.drainCallback() # 게이지 고갈시 서펜트 종료. 카데나와 같이 Taskholder에 체이닝해서 구현하는게 좋지만, 성능 문제로 이와 같이 해둠.
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname = self.skill.name, spec = 'graph control')

    def chargeController(self, val, force = False):
        task = core.Task(self, partial(self.charge, val, force))
        return core.TaskHolder(task, name = f"Gauge | 게이지: {val}")

    def get_modifier(self):
        if self.charged == 1:
            return core.CharacterModifier(att = 50 + 2 * self.combat)
        else:
            return core.CharacterModifier(att = 25 + 1 * self.combat)

    def isStateOn(self):
        return self.charged

    def isStateOff(self):
        return not self.charged

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "STR"
        self.jobname = "바이퍼"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule('Energy Orb | 에너지 오브(Dummy | 더미)', BuccaneerSkills.EnergyCharge.value, lambda sk: sk.isStateOff()), RuleSet.BASE)
        ruleset.add_rule(MutualRule(BuccaneerSkills.StimulatingConversation.value, BuccaneerSkills.Meltdown.value), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(BuccaneerSkills.StimulatingConversation.value, BuccaneerSkills.EnergyCharge.value, lambda sk: sk.judge(2000, -1) or sk.isStateOff()), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(BuccaneerSkills.PowerUnity.value, f'{BuccaneerSkills.PowerUnity.value}(debuff | 디버프)', lambda sk: sk.is_time_left(1000, -1)), RuleSet.BASE)
        # ruleset.add_rule(MutualRule(BuccaneerSkills.TimeLeap.value, GlobalSkills.TermsAndConditions.value), RuleSet.BASE)
        # ruleset.add_rule(InactiveRule(BuccaneerSkills.TimeLeap.value, GlobalSkills.TermsAndConditions.value), RuleSet.BASE)
        ruleset.add_rule(DisableRule(BuccaneerSkills.TimeLeap.value), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=49, armor_ignore=15.3, crit_damage=39, patt=2.4)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        CriticalRoar = core.InformedCharacterModifier(BuccaneerSkills.ShadowHeart.value,crit = 20, crit_damage = 5)
        MentalClearity = core.InformedCharacterModifier(BuccaneerSkills.DarkClarity.value,att = 30)
        PhisicalTraining = core.InformedCharacterModifier(BuccaneerSkills.PhysicalTraining.value,stat_main = 30, stat_sub = 30)
        CriticalRage = core.InformedCharacterModifier(BuccaneerSkills.PrecisionStrikes.value,crit = 15, crit_damage = 10)    # Boss opponent +20% Crit rate. 보스상대 추가+20% 크리율.
        StimulatePassive = core.InformedCharacterModifier(f"{BuccaneerSkills.StimulatingConversation.value}(Passive | 패시브)",boss_pdamage = 20)

        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 2, 3)
        
        return [CriticalRoar, MentalClearity, PhisicalTraining, CriticalRage, StimulatePassive, LoadedDicePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5 + 0.5*ceil(self.combat/2))

        CriticalRage = core.InformedCharacterModifier(f"{BuccaneerSkills.PrecisionStrikes.value}(Boss | 보스)",crit = 20)    # Boss opponent +20% Crit rate. 보스상대 추가+20% 크리율.
        GuardCrush = core.InformedCharacterModifier(BuccaneerSkills.TyphoonCrush.value,armor_ignore = 40 + 2*passive_level)  # 40% chance of ignoring 100% of defence. 40% 확률로 방무 100% 무시.
        # CounterAttack = core.InformedCharacterModifier(BuccaneerSkills.PiratesRevenge.value,pdamage = 25 + 2*passive_level) # TODO: Should decide whether to apply. 적용 여부 결정해야함.
        
        return [WeaponConstant, Mastery, CriticalRage, GuardCrush]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Ultra Charge: 350 charge when attacking, double charge when attacking boss. Stack 10000.

        Stimulate is used when it is not in a fully buffered state or is below 2000 gauge
        Energy Orb is used for gauge recovery

        Double Lucky Dice-Enhance
        Fist Enrage-Reinforce, Boss Killer, Bonus Attack
        Energy Blast-Bonus Attack

        Inlay-Nautil-Des-Unity

        울트라 차지 : 공격시 350충전, 보스공격시 2배 충전. 최대스택 10000.

        스티뮬레이트는 완충 상태가 아니거나 게이지 2000 이하일때 사용
        에너지 오브는 게이지 회복용으로 사용

        더블 럭키 다이스-인핸스
        피스트 인레이지-리인포스, 보스킬러, 보너스 어택
        에너지 블라스트-보너스 어택

        인레이지-노틸-드스-유니티
        '''
        ######   Skill   ######
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        serverlag = 3
        TRANSFORM_HIT = 12

        # Buff Skill
        DICE_WEIGHT = 22
        DICE_POOL = 115
        DICE_PROC = DICE_WEIGHT / DICE_POOL # 더블 럭키 다이스 - 인핸스
        LuckyDice = core.BuffSkill(PirateSkills.LoadedDice.value, 990, 180 * 1000, pdamage = 20+10*DICE_PROC+10*DICE_PROC*((1-DICE_PROC)+DICE_WEIGHT/(DICE_POOL*2-DICE_WEIGHT))*(10*(5+passive_level)*0.01)).isV(vEhc, 2, 2).wrap(core.BuffSkillWrapper)
        Viposition = core.BuffSkill(BuccaneerSkills.Crossbones.value, 0, (180+4*self.combat) * 1000, patt = 30+self.combat).wrap(core.BuffSkillWrapper)

        # Damage Skill    
        FistInrage = core.DamageSkill(BuccaneerSkills.Octopunch.value, 690, 320 + 4*self.combat, 8 + 1, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        FistInrage_T = core.DamageSkill(f"{BuccaneerSkills.Octopunch.value}(Transform | 변신)", 690, 320+4*self.combat, 8 + 1 + 2, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        DragonStrike = core.DamageSkill(BuccaneerSkills.DragonStrike.value, 690, 300 + 4*self.combat, 12, cooltime = 15 * 1000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        DragonStrikeBuff = core.BuffSkill(f"{BuccaneerSkills.DragonStrike.value}(Debuff | 디버프)", 0, 15 * 1000, cooltime = -1, pdamage_indep = 20 + self.combat//2).wrap(core.BuffSkillWrapper)
        
        Nautilus = core.DamageSkill(BuccaneerSkills.NautilusStrike.value, 690, 440+4*self.combat, 7, cooltime = 60 * 1000, red=True).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        NautilusFinalAttack = core.DamageSkill(f"{BuccaneerSkills.NautilusStrike.value}(Final attack | 파이널 어택)", 0, 165+2*self.combat, 2).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)

        # 타임 리프: 안 쓰는 게 더 셈
        TimeLeap = core.DamageSkill(BuccaneerSkills.TimeLeap.value, 1080, 0, 0, cooltime = 180000).wrap(core.DamageSkillWrapper)

        # Hyper
        Stimulate = core.BuffSkill(BuccaneerSkills.StimulatingConversation.value, 930, 120 * 1000, cooltime = 240 * 1000, pdamage = 20).wrap(core.BuffSkillWrapper)# 에너지 주기적으로 800씩 증가, 미완충시 풀완충.
        StimulateSummon = core.SummonSkill(f"{BuccaneerSkills.StimulatingConversation.value}(Guage increasing | 게이지 증가 더미)", 0, (5 + serverlag) * 1000, 0, 0, 120 * 1000, cooltime = -1).wrap(core.SummonSkillWrapper)
        UnityOfPower = core.DamageSkill(BuccaneerSkills.PowerUnity.value, 690, 650, 5, cooltime = 10000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)   #완충시에만 사용 가능, 에너지 1500 소모.
        UnityOfPowerBuff = core.BuffSkill(f"{BuccaneerSkills.PowerUnity.value}(Debuff | 디버프)", 0, 90 * 1000, cooltime = -1, crit_damage = 40).wrap(core.BuffSkillWrapper)   #4스택 가정.
        EpicAdventure = core.BuffSkill(BuccaneerSkills.EpicAdventure.value, 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)

        # 5th
        PirateFlag = adventurer.PirateFlagWrapper(vEhc, 3, 2, chtr.level)

        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        Transform = core.BuffSkill(BuccaneerSkills.Meltdown.value, 450, (50+vEhc.getV(1,1))*1000, cooltime = 180 * 1000, red=True, pdamage_indep = 20 + vEhc.getV(1,1) // 5).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)
        TransformEnergyOrbDummy = core.DamageSkill("Energy Orb | 에너지 오브(Dummy | 더미)", 0, 0, 0, cooltime = -1).wrap(core.DamageSkillWrapper)
        TransformEnergyOrb = core.DamageSkill("Energy Orb | 에너지 오브", 780, 450 +vEhc.getV(1,1)*18, 3 * TRANSFORM_HIT, modifier = core.CharacterModifier(crit = 50, armor_ignore = 50)).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)

        SerpentScrew = core.SummonSkill(BuccaneerSkills.LordoftheDeep.value, 600, 260, 360 + vEhc.getV(0,0)*14, 3, 99999 * 10000).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        SerpentScrewDummy = core.SummonSkill(f"{BuccaneerSkills.LordoftheDeep.value}(Continuing | 지속)", 0, 1000, 0, 0, 99999 * 10000, cooltime = -1).wrap(core.SummonSkillWrapper)
    
        FuriousCharge = core.DamageSkill(BuccaneerSkills.SerpentVortex.value, 420, 600+vEhc.getV(4,4)*24, 10, cooltime = 10 * 1000, modifier = core.CharacterModifier(boss_pdamage = 30)).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)

        HowlingFistInit = core.DamageSkill(f"{BuccaneerSkills.HowlingFist.value}(Cast | 개시)", 240, 0, 0, cooltime=90000, red=True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        HowlingFistCharge = core.DamageSkill(f"{BuccaneerSkills.HowlingFist.value}(Charge | 충전)", 240, 425+17*vEhc.getV(0,0), 6, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        HowlingFistFinal = core.DamageSkill(f"{BuccaneerSkills.HowlingFist.value}(Final attack | 막타)", 1950, 525+21*vEhc.getV(0,0), 10*14, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)

        ######   Skill Wrapper   ######
        # Energy Charge
        EnergyCharge = EnergyChargeWrapper(passive_level)
        EnergyConstraint = core.ConstraintElement("Can only be used in enerhy charged state | 에너지 차지 상태에서만 사용 가능", EnergyCharge, EnergyCharge.isStateOn)

        Stimulate.onAfter(EnergyCharge.chargeController(10000, force=True))
        Transform.onAfter(EnergyCharge.chargeController(10000, force=True))
        TransformEnergyOrb.onAfter(EnergyCharge.chargeController(700 * TRANSFORM_HIT))
        StimulateSummon.onTick(EnergyCharge.chargeController(800, force=True))
        FistInrage.onAfter(EnergyCharge.chargeController(700))
        Nautilus.onAfter(EnergyCharge.chargeController(700))
        MirrorBreak.onAfter(EnergyCharge.chargeController(700))
        SerpentScrewDummy.onTick(EnergyCharge.chargeController(-60))
        SerpentScrew.onTick(EnergyCharge.chargeController(-85*0.3))
        FistInrage_T.onAfter(EnergyCharge.chargeController(-150))
        DragonStrike.onAfter(EnergyCharge.chargeController(-180))
        UnityOfPower.onAfter(EnergyCharge.chargeController(-1500))
        HowlingFistInit.onAfter(EnergyCharge.chargeController(-1750))
        
        # Basic Attack
        BasicAttack = core.OptionalElement(EnergyCharge.isStateOn, FistInrage_T, FistInrage, "Energy buffer | 에너지 완충")
        BasicAttackWrapper = core.DamageSkill('Basic attack | 기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)

        # Dragon Strike
        DragonStrike.onConstraint(EnergyConstraint)
        DragonStrike.onAfter(DragonStrikeBuff)
    
        # Final Attack
        FinalAttack = core.OptionalElement(lambda: not Nautilus.is_available(), NautilusFinalAttack, name=f"{BuccaneerSkills.NautilusStrike.value}(cooldown | 쿨타임)")
        FistInrage.onAfter(FinalAttack)
        FistInrage_T.onAfter(FinalAttack)
        FuriousCharge.onAfter(FinalAttack)

        # Stimulate
        Stimulate.onAfter(StimulateSummon)
    
        # Unity Of Power
        UnityOfPower.onConstraint(EnergyConstraint)
        UnityOfPower.onAfter(UnityOfPowerBuff)
        
        # Transform
        Transform.onAfter(TransformEnergyOrbDummy.controller(1))
        TransformEnergyOrbDummy.onConstraint(core.ConstraintElement("Available only in transform state | 트랜스폼 상태에서만 사용가능", Transform, Transform.is_active))
        TransformEnergyOrbDummy.onAfter(core.RepeatElement(TransformEnergyOrb, 2 + vEhc.getV(1, 1) // 30))
        
        # Serpent Screw
        SerpentScrew.onConstraint(core.ConstraintElement("More than 100 energy | 에너지 100 이상", EnergyCharge, partial(EnergyCharge.judge, 100, 1)))
        SerpentScrew.onAfter(SerpentScrewDummy)
        EnergyCharge.drainCallback = lambda: [SerpentScrew.set_disabled_and_time_left(1), SerpentScrewDummy.set_disabled_and_time_left(-1)]

        # Howling Fist
        HowlingFistInit.onConstraint(core.ConstraintElement("More than 1750 energy | 에너지 1750 이상", EnergyCharge, partial(EnergyCharge.judge, 1750, 1)))
        HowlingFistInit.onAfter(core.RepeatElement(HowlingFistCharge, 8))
        HowlingFistInit.onAfter(HowlingFistFinal)

        SoulContract = globalSkill.soul_contract()

        TimeLeap.onAfter(SoulContract.controller(1.0, "reduce_cooltime_p"))
        TimeLeap.onAfter(Nautilus.controller(1.0, "reduce_cooltime_p"))
        TimeLeap.onAfter(DragonStrike.controller(1.0, "reduce_cooltime_p"))
            
        return (BasicAttackWrapper,
            [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                LuckyDice, Viposition, Stimulate, EpicAdventure, PirateFlag, Overdrive, Transform,
                UnityOfPowerBuff, DragonStrikeBuff, EnergyCharge,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), SoulContract] +\
            [UnityOfPower, HowlingFistInit, Nautilus, DragonStrike, FuriousCharge, TransformEnergyOrbDummy, MirrorBreak, MirrorSpider, TimeLeap] +\
            [SerpentScrew, SerpentScrewDummy, StimulateSummon] +\
            [] +\
            [BasicAttackWrapper])
