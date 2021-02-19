from enum import Enum

from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobclass import cygnus
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict
# It is necessary to consider whether to apply Mihile Youngme. 미하일 영메 적용여부에 대해 고민해볼 필요 있음.


# English skill information for Mihile here https://maplestory.fandom.com/wiki/Mihile/Skills
class MihileSkills(Enum):
    # Link Skill
    KnightsWatch = 'Knight\'s Watch | 빛의 수호'
    # Beginner
    ElementalExpert = 'Elemental Expert | 엘리멘탈 엑스퍼트'
    # 1st Job
    SoulShield = 'Soul Shield | 소울 실드'
    RoyalGuard = 'Royal Guard | 로얄 가드'
    SoulBlade = 'Soul Blade | 소울 블레이드'
    WeightlessHeart = 'Weightless Heart | 소울 점프'
    SoulDevotion = 'Soul Devotion | 소울 어질리티'
    HPBoost = 'HP Boost | HP 증가'
    # 2nd Job
    SwordMastery = 'Sword Mastery | 소드 마스터리'
    FinalAttack = 'Final Attack | 파이널 어택'
    SwordBooster = 'Sword Booster | 소드 부스터'
    Rally = 'Rally | 격려'
    SoulDriver = 'Soul Driver | 소울 드라이버'
    RadiantDriver = 'Radiant Driver | 샤이닝 체이스'
    VerticalRadiantDriver = 'Vertical Radiant Driver | 버티컬 샤이닝 체이스'
    PhysicalTraining = 'Physical Training | 피지컬 트레이닝'
    # 3rd Job
    SelfRecovery = 'Self Recovery | 셀프 리커버리'
    IntenseFocus = 'Intense Focus | 인텐션'
    RighteousIndignation = 'Righteous Indignation | 소울 어택'
    AdvancedRoyalGuard = 'Advanced Royal Guard | 어드밴스드 로얄 가드'
    RadiantCharge = 'Radiant Charge | 샤이닝 차지'
    EnduringSpirit = 'Enduring Spirit | 소울 인듀어'
    SoulLink = 'Soul Link | 소울 링크'
    MagicCrash = 'Magic Crash | 매직 크래쉬'
    TrinityAttack = 'Trinity Attack | 소울 슬래시'
    # 4th job
    SoulAsylum = 'Soul Asylum | 어드밴스드 소울 실드'
    ExpertSwordMastery = 'Expert Sword Mastery | 어드밴스드 소드 마스터리'
    AdvancedFinalAttack = 'Advanced Final Attack | 어드밴스드 파이널 어택'
    FourPointAssault = 'Four-Point Assault | 소울 어썰트'
    RadiantCross = 'Radiant Cross | 샤이닝 크로스'
    RoilingSoul = 'Roiling Soul | 소울 레이지'
    CombatMastery = 'Combat Mastery | 컴뱃 마스터리'
    PowerStance = 'Power Stance | 스탠스'
    CallofCygnus = 'Call of Cygnus | 시그너스 나이츠'
    # Hypers
    ChargingLight = 'Charging Light | 데들리 차지'
    QueenofTomorrow = 'Queen of Tomorrow | 퀸 오브 투모로우'
    SacredCube = 'Sacred Cube | 세이크리드 큐브'
    # 5th Job
    ShieldofLight = 'Shield of Light | 로 아이아스'
    SwordofLight = 'Sword of Light | 클라우 솔라스'
    RadiantSoul = 'Radiant Soul | 소드 오브 소울 라이트'
    LightofCourage = 'Light of Courage | 라이트 오브 커리지'


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 9
        self.jobtype = "STR"
        self.jobname = "미하일"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'mess')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(crit=20, pdamage=30, armor_ignore=12)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ElementalExpert = core.InformedCharacterModifier(MihileSkills.ElementalExpert.value,patt = 10)
        
        PhisicalTraiging = core.InformedCharacterModifier(MihileSkills.PhysicalTraining.value,stat_main = 30, stat_sub = 30)
        SwordMastery = core.InformedCharacterModifier(MihileSkills.SwordMastery.value,pdamage_indep = 15)
        InvigoratePassive = core.InformedCharacterModifier(f"{MihileSkills.Rally.value}(Passive | 패시브)",att = 20)
        Intension = core.InformedCharacterModifier(MihileSkills.IntenseFocus.value,stat_main = 60, crit = 20, pdamage_indep = 10)
        ShiningCharge = core.InformedCharacterModifier(f"{MihileSkills.RadiantCharge.value}(Passive | 패시브)",pdamage = 60)
        CombatMastery = core.InformedCharacterModifier(MihileSkills.CombatMastery.value,armor_ignore = 40+2*passive_level)
        AdvancedSowrdMastery = core.InformedCharacterModifier(MihileSkills.ExpertSwordMastery.value,att = 30+passive_level, crit = 15+passive_level//3, crit_damage = 10)
        AdvancedFinalAttackPassive = core.InformedCharacterModifier(f"{MihileSkills.AdvancedFinalAttack.value}(Passive | 패시브)",att = 30+passive_level)

        return [ElementalExpert, PhisicalTraiging, SwordMastery,
                            InvigoratePassive, Intension, ShiningCharge, CombatMastery, AdvancedSowrdMastery,
                            AdvancedFinalAttackPassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        PARTYPEOPLE = 1        
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5 + 0.5*ceil(passive_level/2))
        
        SoulLink = core.InformedCharacterModifier(MihileSkills.SoulLink.value,pdamage = 5*PARTYPEOPLE)
        SoulRage = core.InformedCharacterModifier(MihileSkills.RoilingSoul.value, pdamage_indep = 30+self.combat, crit_damage = 8)
        
        return [WeaponConstant, Mastery, SoulLink, SoulRage]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        1 party member

        Hyper
        Shining Cross-Reinforce / Install / Bonus Attack
        Soul Assault-Reinforce / Bonus Attack

        Soul Assault-Shining Cross-Royal Guard-Patek-Deadly Charge

        Shining Cross keeps the cross always there

        Royal Guard is used every 6 seconds and may be used slightly later due to other skills. It is assumed to maintain the Royal Guard 5 stack buff at all times.

        파티원 1명
        
        하이퍼
        샤이닝 크로스 - 리인포스 / 인스톨 / 보너스 어택
        소울 어썰트 - 리인포스 / 보너스 어택
        
        소울어썰트-샤이닝크로스-로얄가드-파택-데들리차지
        
        샤이닝 크로스는 십자가가 항상 남아있도록 유지함
        
        로얄 가드는 6초마다 사용하며 다른 스킬로 인해 약간 나중에 사용할 수도 있음. 로얄 가드 5중첩 버프를 상시 유지하도록 가정.
        '''
        USE_ROYAL_GUARD = options.get("royal_guard", True)

        passive_level = chtr.get_base_modifier().passive_level + self.combat

        # Buff skills
        GuardOfLight = core.BuffSkill(MihileSkills.KnightsWatch.value, 900, 30000, rem = True, red = True, cooltime = 180000, pdamage = 20).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill(MihileSkills.SwordBooster.value, 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        Invigorate = core.BuffSkill(MihileSkills.Rally.value, 0, 180000, rem = True, att = 30).wrap(core.BuffSkillWrapper)
        SoulAttack = core.BuffSkill(MihileSkills.RighteousIndignation.value, 0, 10000, cooltime = -1, pdamage_indep = 25, crit = 20).wrap(core.BuffSkillWrapper)
        
        # Damage skills
        LoyalGuard_1 = core.DamageSkill(f"{MihileSkills.RoyalGuard.value}(1)", 630, 275+chtr.level, 4, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_2 = core.DamageSkill(f"{MihileSkills.RoyalGuard.value}(2)", 630, 340+chtr.level, 5, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_3 = core.DamageSkill(f"{MihileSkills.RoyalGuard.value}(3)", 630, 440+chtr.level, 6, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_4 = core.DamageSkill(f"{MihileSkills.RoyalGuard.value}(4)", 630, 480+chtr.level, 7, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_5 = core.DamageSkill(f"{MihileSkills.RoyalGuard.value}(5)", 630, 565+chtr.level, 9, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuardBuff = core.BuffSkill(MihileSkills.RoyalGuard.value, 0, 12000, att = 45).wrap(core.BuffSkillWrapper)  #10->15->20->30->45
        
        SoulAssult = core.DamageSkill(MihileSkills.FourPointAssault.value, 600, 210+3*self.combat, 11+1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)   # 20% darkness. 암흑 20%.
        
        FinalAttack = core.DamageSkill(MihileSkills.FinalAttack.value, 0, 95+passive_level, 4*0.01*(75+passive_level)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        
        ShiningCross = core.DamageSkill(MihileSkills.RadiantCross.value, 600, 440+3*self.combat, 4+1, cooltime = 12000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)   # Darkness 30% 10 seconds. 암흑 30% 10초.
        ShiningCrossInstall = core.SummonSkill(f"{MihileSkills.RadiantCross.value}(Install | 인스톨)", 0, 1200, 75, 4+1, 12000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)    # 100% dark 5 seconds. 100% 암흑 5초.
        
        # Hyper
        SacredCube = core.BuffSkill(MihileSkills.SacredCube.value, 90, 30000, cooltime = 210000, pdamage = 10).wrap(core.BuffSkillWrapper)
        DeadlyCharge = (
            core.DamageSkill(
                MihileSkills.ChargingLight.value,
                delay=30 if USE_ROYAL_GUARD else 810,
                damage=600,
                hit=10,
                cooltime = 15000,
            )
            .setV(vEhc, 4, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        DeadlyChargeBuff = core.BuffSkill(f"{MihileSkills.ChargingLight.value}(Debuff | 디버프)", 0, 10000, cooltime = -1, pdamage = 10).wrap(core.BuffSkillWrapper)
        QueenOfTomorrow = core.BuffSkill(MihileSkills.QueenofTomorrow.value, 0, 60000, cooltime = 120000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        # 5th
        CygnusPhalanx = cygnus.PhalanxChargeWrapper(vEhc, 3, 3)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        RoIias = core.BuffSkill(MihileSkills.ShieldofLight.value, 840, (75+3*vEhc.getV(0,0))*1000, cooltime = 300*1000, red = True, pdamage_indep = 5 + (35+3*(vEhc.getV(0,0)//4))//2).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        ClauSolis = core.DamageSkill(MihileSkills.SwordofLight.value, 690, 700+28*vEhc.getV(4,4), 7, cooltime = 12000, red = True).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)    # Royal Guard buff duration increased by 6 seconds. 100% dark 5 seconds. 로얄가드 버프지속시간 6초 증가. 100% 암흑 5초.
        ClauSolisSummon = core.SummonSkill(f"{MihileSkills.SwordofLight.value}(Summon | 소환)", 0, 5000, 350+14*vEhc.getV(4,4), 7, 7000, cooltime = -1).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)   # 100% dark 5 seconds. 100% 암흑 5초.
    
        SwordOfSoullight = core.BuffSkill(MihileSkills.RadiantSoul.value, 810, 30000, cooltime = 180*1000, red = True, patt = 15 + vEhc.getV(1,1)//2, crit = 100, armor_ignore = 100).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)
        SoullightSlash = core.DamageSkill(f"{MihileSkills.RadiantSoul.value}(Slash | 슬래시)", 630, 400+16*vEhc.getV(1,1), 12).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)

        LightOfCourage = core.BuffSkill(MihileSkills.LightofCourage.value, 750, 25000, cooltime=90*1000, red=True, pdamage=10+vEhc.getV(0,0)//2).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        LightOfCourageSummon = core.SummonSkill(f"{MihileSkills.LightofCourage.value}(Sword of Light | 빛의 검)", 0, 2400, 325+13*vEhc.getV(0,0), 5, 25000, cooltime=-1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        LightOfCourageAttack = core.DamageSkill(f"{MihileSkills.LightofCourage.value}(Light of Courage | 용기의 빛)", 0, 175+7*vEhc.getV(0,0), 2, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        LightOfCourageFinal = core.DamageSkill(f"{MihileSkills.LightofCourage.value}(Light of Courage | 용기의 빛)(Ending | 종료)", 360, 375+15*vEhc.getV(0,0), 10*6, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ##### Build Graph
        
        # Basic attack. 기본 공격.
        BasicAttack = core.OptionalElement(SwordOfSoullight.is_active, SoullightSlash, SoulAssult)
        BasicAttackWrapper = core.DamageSkill('기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)

        FinalAttack.onAfter(core.OptionalElement(LightOfCourage.is_active, LightOfCourageAttack)) # It is assumed that the light of courage and the list of skills that trigger Final Attack are the same. 용기의 빛과 파이널 어택 발동시키는 스킬 목록이 같다고 가정함.
        
        SoullightSlash.onAfter(FinalAttack)
        SoulAssult.onAfter(FinalAttack)
        LoyalGuard_5.onAfter(FinalAttack)

        # ClauSolis. 클라우 솔라스.
        ClauSolis.onEventElapsed(ClauSolisSummon, 5000)
        ClauSolis.onAfter(SoulAttack.controller(5000,"set_enabled_and_time_left"))
        ClauSolis.onAfter(FinalAttack)
        ClauSolisSummon.onTick(SoulAttack.controller(5000,"set_enabled_and_time_left"))

        # Deadly Charge. 데들리 차지.
        DeadlyCharge.onAfter(DeadlyChargeBuff)
        DeadlyCharge.onAfter(FinalAttack)
        
        # Shining Cross. 샤이닝 크로스.
        ShiningCross.onAfter(ShiningCrossInstall)
        ShiningCross.onAfter(FinalAttack)
        ShiningCrossInstall.onTick(SoulAttack.controller(5000,"set_enabled_and_time_left"))

        # Light of Courage. 라이트 오브 커리지.
        LightOfCourage.onAfter(LightOfCourageSummon)
        LightOfCourage.onAfter(LightOfCourageFinal.controller(25000))

        # Weapon Aura 오라 웨폰.
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 2)
        for sk in [SoullightSlash, SoulAssult, DeadlyCharge, LoyalGuard_5, ShiningCross]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        # Scheduling
        if USE_ROYAL_GUARD is True:
            DeadlyCharge.onAfter(LoyalGuard_5)
            DeadlyCharge.onConstraint(
                core.ConstraintElement(
                    "When its possible to cancel with Royal Guard | 로얄 가드로 캔슬 가능할때",
                    LoyalGuard_5,
                    lambda: LoyalGuard_5.is_available(),
                )
            )
        else:
            LoyalGuard_5 = None
            LoyalGuardBuff = None
        
        return(BasicAttackWrapper, 
                [globalSkill.maple_heros(chtr.level, name=MihileSkills.CallofCygnus.value, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    GuardOfLight, LoyalGuardBuff, SoulAttack, Booster, Invigorate, SacredCube, cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level),
                    DeadlyChargeBuff, QueenOfTomorrow, AuraWeaponBuff, AuraWeapon, RoIias, SwordOfSoullight, LightOfCourage, LightOfCourageSummon, LightOfCourageFinal,
                    globalSkill.soul_contract()] +\
                [CygnusPhalanx, DeadlyCharge, LoyalGuard_5, ShiningCross, ClauSolis, MirrorBreak, MirrorSpider] +\
                [ShiningCrossInstall, ClauSolisSummon] +\
                [BasicAttackWrapper])