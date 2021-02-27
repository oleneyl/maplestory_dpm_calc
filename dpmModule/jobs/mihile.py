from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobclass import cygnus
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict

import gettext
_ = gettext.gettext

# It is necessary to consider whether to apply Mihile Youngme. 미하일 영메 적용여부에 대해 고민해볼 필요 있음.


# English skill information for Mihile here https://maplestory.fandom.com/wiki/Mihile/Skills
class MihileSkills:
    # Link Skill
    KnightsWatch = _("빛의 수호")  # "Knight's Watch"
    # Beginner
    ElementalExpert = _("엘리멘탈 엑스퍼트")  # "Elemental Expert"
    # 1st Job
    SoulShield = _("소울 실드")  # "Soul Shield"
    RoyalGuard = _("로얄 가드")  # "Royal Guard"
    SoulBlade = _("소울 블레이드")  # "Soul Blade"
    WeightlessHeart = _("소울 점프")  # "Weightless Heart"
    SoulDevotion = _("소울 어질리티")  # "Soul Devotion"
    HPBoost = _("HP 증가")  # "HP Boost"
    # 2nd Job
    SwordMastery = _("소드 마스터리")  # "Sword Mastery"
    FinalAttack = _("파이널 어택")  # "Final Attack"
    SwordBooster = _("소드 부스터")  # "Sword Booster"
    Rally = _("격려")  # "Rally"
    SoulDriver = _("소울 드라이버")  # "Soul Driver"
    RadiantDriver = _("샤이닝 체이스")  # "Radiant Driver"
    VerticalRadiantDriver = _("버티컬 샤이닝 체이스")  # "Vertical Radiant Driver"
    PhysicalTraining = _("피지컬 트레이닝")  # "Physical Training"
    # 3rd Job
    SelfRecovery = _("셀프 리커버리")  # "Self Recovery"
    IntenseFocus = _("인텐션")  # "Intense Focus"
    RighteousIndignation = _("소울 어택")  # "Righteous Indignation"
    AdvancedRoyalGuard = _("어드밴스드 로얄 가드")  # "Advanced Royal Guard"
    RadiantCharge = _("샤이닝 차지")  # "Radiant Charge"
    EnduringSpirit = _("소울 인듀어")  # "Enduring Spirit"
    SoulLink = _("소울 링크")  # "Soul Link"
    MagicCrash = _("매직 크래쉬")  # "Magic Crash"
    TrinityAttack = _("소울 슬래시")  # "Trinity Attack"
    # 4th job
    SoulAsylum = _("어드밴스드 소울 실드")  # "Soul Asylum"
    ExpertSwordMastery = _("어드밴스드 소드 마스터리")  # "Expert Sword Mastery"
    AdvancedFinalAttack = _("어드밴스드 파이널 어택")  # "Advanced Final Attack"
    FourPointAssault = _("소울 어썰트")  # "Four-Point Assault"
    RadiantCross = _("샤이닝 크로스")  # "Radiant Cross"
    RoilingSoul = _("소울 레이지")  # "Roiling Soul"
    CombatMastery = _("컴뱃 마스터리")  # "Combat Mastery"
    PowerStance = _("스탠스")  # "Power Stance"
    CallofCygnus = _("시그너스 나이츠")  # "Call of Cygnus"
    # Hypers
    ChargingLight = _("데들리 차지")  # "Charging Light"
    QueenofTomorrow = _("퀸 오브 투모로우")  # "Queen of Tomorrow"
    SacredCube = _("세이크리드 큐브")  # "Sacred Cube"
    # 5th Job
    ShieldofLight = _("로 아이아스")  # "Shield of Light"
    SwordofLight = _("클라우 솔라스")  # "Sword of Light"
    RadiantSoul = _("소드 오브 소울 라이트")  # "Radiant Soul"
    LightofCourage = _("라이트 오브 커리지")  # "Light of Courage"


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 9
        self.jobtype = "STR"
        self.jobname = _("미하일")
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'mess')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(crit=20, pdamage=30, armor_ignore=12)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ElementalExpert = core.InformedCharacterModifier(MihileSkills.ElementalExpert,patt = 10)
        
        PhisicalTraiging = core.InformedCharacterModifier(MihileSkills.PhysicalTraining,stat_main = 30, stat_sub = 30)
        SwordMastery = core.InformedCharacterModifier(MihileSkills.SwordMastery,pdamage_indep = 15)
        InvigoratePassive = core.InformedCharacterModifier(_("{}(패시브)").format(MihileSkills.Rally),att = 20)
        Intension = core.InformedCharacterModifier(MihileSkills.IntenseFocus,stat_main = 60, crit = 20, pdamage_indep = 10)
        ShiningCharge = core.InformedCharacterModifier(_("{}(패시브)").format(MihileSkills.RadiantCharge),pdamage = 60)
        CombatMastery = core.InformedCharacterModifier(MihileSkills.CombatMastery,armor_ignore = 40+2*passive_level)
        AdvancedSowrdMastery = core.InformedCharacterModifier(MihileSkills.ExpertSwordMastery,att = 30+passive_level, crit = 15+passive_level//3, crit_damage = 10)
        AdvancedFinalAttackPassive = core.InformedCharacterModifier(_("{}(패시브)").format(MihileSkills.AdvancedFinalAttack),att = 30+passive_level)

        return [ElementalExpert, PhisicalTraiging, SwordMastery,
                            InvigoratePassive, Intension, ShiningCharge, CombatMastery, AdvancedSowrdMastery,
                            AdvancedFinalAttackPassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        PARTYPEOPLE = 1        
        WeaponConstant = core.InformedCharacterModifier(_("무기상수"),pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90+ceil(passive_level/2))
        
        SoulLink = core.InformedCharacterModifier(MihileSkills.SoulLink,pdamage = 5*PARTYPEOPLE)
        SoulRage = core.InformedCharacterModifier(MihileSkills.RoilingSoul, pdamage_indep = 30+self.combat, crit_damage = 8)
        
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
        GuardOfLight = core.BuffSkill(MihileSkills.KnightsWatch, 900, 30000, rem = True, red = True, cooltime = 180000, pdamage = 20).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill(MihileSkills.SwordBooster, 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        Invigorate = core.BuffSkill(MihileSkills.Rally, 0, 180000, rem = True, att = 30).wrap(core.BuffSkillWrapper)
        SoulAttack = core.BuffSkill(MihileSkills.RighteousIndignation, 0, 10000, cooltime = -1, pdamage_indep = 25, crit = 20).wrap(core.BuffSkillWrapper)
        
        # Damage skills
        LoyalGuard_1 = core.DamageSkill(f"{MihileSkills.RoyalGuard}(1)", 630, 275+chtr.level, 4, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_2 = core.DamageSkill(f"{MihileSkills.RoyalGuard}(2)", 630, 340+chtr.level, 5, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_3 = core.DamageSkill(f"{MihileSkills.RoyalGuard}(3)", 630, 440+chtr.level, 6, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_4 = core.DamageSkill(f"{MihileSkills.RoyalGuard}(4)", 630, 480+chtr.level, 7, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_5 = core.DamageSkill(f"{MihileSkills.RoyalGuard}(5)", 630, 565+chtr.level, 9, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuardBuff = core.BuffSkill(_("{}(버프)").format(MihileSkills.RoyalGuard), 0, 12000, att = 45).wrap(core.BuffSkillWrapper)  #10->15->20->30->45
        
        SoulAssult = core.DamageSkill(MihileSkills.FourPointAssault, 600, 210+3*self.combat, 11+1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)   # 20% darkness. 암흑 20%.
        
        FinalAttack = core.DamageSkill(MihileSkills.FinalAttack, 0, 95+passive_level, 4*0.01*(75+passive_level)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        
        ShiningCross = core.DamageSkill(MihileSkills.RadiantCross, 600, 440+3*self.combat, 4+1, cooltime = 12000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)   # Darkness 30% 10 seconds. 암흑 30% 10초.
        ShiningCrossInstall = core.SummonSkill(_("{}(인스톨)").format(MihileSkills.RadiantCross), 0, 1200, 75, 4+1, 12000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)    # 100% dark 5 seconds. 100% 암흑 5초.
        
        # Hyper
        SacredCube = core.BuffSkill(MihileSkills.SacredCube, 90, 30000, cooltime = 210000, pdamage = 10).wrap(core.BuffSkillWrapper)
        DeadlyCharge = (
            core.DamageSkill(
                MihileSkills.ChargingLight,
                delay=30 if USE_ROYAL_GUARD else 810,
                damage=600,
                hit=10,
                cooltime = 15000,
            )
            .setV(vEhc, 4, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        DeadlyChargeBuff = core.BuffSkill(_("{}(디버프)").format(MihileSkills.ChargingLight), 0, 10000, cooltime = -1, pdamage = 10).wrap(core.BuffSkillWrapper)
        QueenOfTomorrow = core.BuffSkill(MihileSkills.QueenofTomorrow, 0, 60000, cooltime = 120000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        # 5th
        CygnusPhalanx = cygnus.PhalanxChargeWrapper(vEhc, 3, 3)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        RoIias = core.BuffSkill(MihileSkills.ShieldofLight, 840, (75+3*vEhc.getV(0,0))*1000, cooltime = 300*1000, red = True, pdamage_indep = 5 + (35+3*(vEhc.getV(0,0)//4))//2).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        ClauSolis = core.DamageSkill(MihileSkills.SwordofLight, 690, 700+28*vEhc.getV(4,4), 7, cooltime = 12000, red = True).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)    # Royal Guard buff duration increased by 6 seconds. 100% dark 5 seconds. 로얄가드 버프지속시간 6초 증가. 100% 암흑 5초.
        ClauSolisSummon = core.SummonSkill(_("{}(소환)").format(MihileSkills.SwordofLight), 0, 5000, 350+14*vEhc.getV(4,4), 7, 7000, cooltime = -1).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)   # 100% dark 5 seconds. 100% 암흑 5초.
    
        SwordOfSoullight = core.BuffSkill(MihileSkills.RadiantSoul, 810, 30000, cooltime = 180*1000, red = True, patt = 15 + vEhc.getV(1,1)//2, crit = 100, armor_ignore = 100).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)
        SoullightSlash = core.DamageSkill(_("{}(슬래시)").format(MihileSkills.RadiantSoul), 630, 400+16*vEhc.getV(1,1), 12).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)

        LightOfCourage = core.BuffSkill(MihileSkills.LightofCourage, 750, 25000, cooltime=90*1000, red=True, pdamage=10+vEhc.getV(0,0)//2).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        LightOfCourageSummon = core.SummonSkill(_("{}(빛의 검)").format(MihileSkills.LightofCourage), 0, 2400, 325+13*vEhc.getV(0,0), 5, 25000, cooltime=-1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        LightOfCourageAttack = core.DamageSkill(_("{}(용기의 빛)").format(MihileSkills.LightofCourage), 0, 175+7*vEhc.getV(0,0), 2, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        LightOfCourageFinal = core.DamageSkill(_("{}(용기의 빛)(종료)").format(MihileSkills.LightofCourage), 360, 375+15*vEhc.getV(0,0), 10*6, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ##### Build Graph
        
        # Basic attack. 기본 공격.
        BasicAttack = core.OptionalElement(SwordOfSoullight.is_active, SoullightSlash, SoulAssult)
        BasicAttackWrapper = core.DamageSkill(_("기본 공격"),0,0,0).wrap(core.DamageSkillWrapper)
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
                    _("로얄 가드로 캔슬 가능할때"),
                    LoyalGuard_5,
                    lambda: LoyalGuard_5.is_available(),
                )
            )
        else:
            LoyalGuard_5 = None
            LoyalGuardBuff = None
        
        return(BasicAttackWrapper, 
                [globalSkill.maple_heros(chtr.level, name=MihileSkills.CallofCygnus, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    GuardOfLight, LoyalGuardBuff, SoulAttack, Booster, Invigorate, SacredCube, cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level),
                    DeadlyChargeBuff, QueenOfTomorrow, AuraWeaponBuff, AuraWeapon, RoIias, SwordOfSoullight, LightOfCourage, LightOfCourageSummon, LightOfCourageFinal,
                    globalSkill.soul_contract()] +\
                [CygnusPhalanx, DeadlyCharge, LoyalGuard_5, ShiningCross, ClauSolis, MirrorBreak, MirrorSpider] +\
                [ShiningCrossInstall, ClauSolisSummon] +\
                [BasicAttackWrapper])