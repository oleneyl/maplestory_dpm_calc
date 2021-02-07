from enum import Enum

from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ConditionRule, RuleSet, InactiveRule
from . import globalSkill
from .jobclass import cygnus
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict


# English skill information for Dawn Warrior here https://maplestory.fandom.com/wiki/Dawn_Warrior/Skills
class DawnWarriorSkills(Enum):
    # Link SKill
    CygnusBlessing = 'Cygnus Blessing | 시그너스 블레스'
    # Beginner
    ElementalHarmony = 'Elemental Harmony | 엘리멘탈 하모니'
    ElementalExpert = 'Elemental Expert | 엘리멘탈 엑스퍼트'
    # 1st Job
    TripleSlash = 'Triple Slash | 트리플 슬래시'
    SoulElement = 'Soul Element | 엘리멘트: 소울'
    HandofLight = 'Hand of Light | 소드 오브 라이트'
    # 2nd Job
    Flicker = 'Flicker | 사일런트 무브'
    Bluster = 'Bluster | 라우드 러쉬'
    TraceCut = 'Trace Cut | 트레이스 컷'
    ShadowTackle = 'Shadow Tackle | 섀도우 번'
    FallingMoon = 'Falling Moon | 폴링 문'
    SoulSpeed = 'Soul Speed | 님블 핑거'
    DivineHand = 'Divine Hand | 이너 트러스트'
    SwordMastery = 'Sword Mastery | 소드 마스터리'
    InnerHarmony = 'Inner Harmony | 바디 앤 소울'
    # 3rd Job
    LightMerger = 'Light Merger | 라이트 플럭스'
    MoonShadow = 'Moon Shadow | 문 섀도우'
    SunCross = 'Sun Cross | 선크로스'
    MoonCross = 'Moon Cross | 문크로스'
    RisingSun = 'Rising Sun | 라이징 선'
    TrueSight = 'True Sight | 트루 사이트'
    SouloftheGuardian = 'Soul of the Guardian | 소울 가디언'
    WillofSteel = 'Will of Steel | 윌 오브 스틸'
    InnerVoice = 'Inner Voice | 이너 샤우트'
    # 4th Job
    CallofCygnus = 'Call of Cygnus | 시그너스 나이츠'
    MoonDancer = 'Moon Dancer | 댄스오브 문'
    SpeedingSunset = 'Speeding Sunset | 스피딩 선셋'
    SolarPierce = 'Solar Pierce | 솔라 피어스'
    CrescentDivide = 'Crescent Divide | 크레센트 디바이드'
    ImpalingRays = 'Impaling Rays | 소울 페네트레이션'
    EquinoxCycle = 'Equinox Cycle | 솔루나 타임'
    EquinoxSlash = 'Equinox Slash | 솔루나 슬래시'
    SoulPledge = 'Soul Pledge | 소울 플레지'
    StudentoftheBlade = 'Student of the Blade | 소드 엑스퍼트'
    Unpredictable = 'Unpredictable | 언포시어블'
    MasteroftheSword = 'Master of the Sword | 마스터 오브 더 소드'
    # Hypers
    StyxCrossing = 'Styx Crossing | 크로스 더 스틱스'
    GloryoftheGuardians = 'Glory of the Guardians | 글로리 오브 가디언즈'
    SoulForge = 'Soul Forge | 소울 포지'
    # 5th Job
    CelestialDance = 'Celestial Dance | 셀레스티얼 댄스'
    RiftofDamnation = 'Rift of Damnation | 엘리시온'
    SoulEclipse = 'Soul Eclipse | 소울 이클립스'
    FlareSlash = 'Flare Slash | 플레어 슬래시'


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "STR"
        self.jobname = "소울마스터"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule(DawnWarriorSkills.RiftofDamnation.value, DawnWarriorSkills.CelestialDance.value, lambda sk: sk.is_not_active() and sk.is_cooltime_left(30000, 1)), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(DawnWarriorSkills.CelestialDance.value, DawnWarriorSkills.RiftofDamnation.value), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage = 20)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ElementalExpert = core.InformedCharacterModifier(DawnWarriorSkills.ElementalExpert.value, patt = 10)
        ElementalHarmony = core.InformedCharacterModifier(DawnWarriorSkills.ElementalHarmony.value, stat_main = chtr.level // 2)
        
        SwordOfLight = core.InformedCharacterModifier(DawnWarriorSkills.HandofLight.value,att = 20)
        Soul = core.InformedCharacterModifier(DawnWarriorSkills.SoulElement.value,armor_ignore = 10)
        InnerTrust = core.InformedCharacterModifier(DawnWarriorSkills.DivineHand.value,att = 20)
        BodyAndSoul = core.InformedCharacterModifier(DawnWarriorSkills.InnerHarmony.value,stat_main = 40, stat_sub = 20)
        InnerShout = core.InformedCharacterModifier(DawnWarriorSkills.InnerVoice.value,att = 30, stat_main = 40)
        
        SoulPledge = core.InformedCharacterModifier(DawnWarriorSkills.SoulPledge.value,stat_main = 30+passive_level, stat_sub = 30+passive_level, crit = 10)
        SwordExpert = core.InformedCharacterModifier(DawnWarriorSkills.StudentoftheBlade.value,att = 50+passive_level, crit_damage = 15+passive_level//3)
        Unforseeable = core.InformedCharacterModifier(DawnWarriorSkills.Unpredictable.value,armor_ignore = 30+2*passive_level, boss_pdamage = 15+passive_level)
        
        return [ElementalHarmony, ElementalExpert, SwordOfLight, Soul, InnerTrust,
                            BodyAndSoul, InnerShout, SoulPledge, SwordExpert, Unforseeable]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 34)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5+0.5*ceil(passive_level/2))
        TrueSightHyper = core.InformedCharacterModifier(f"{DawnWarriorSkills.TrueSight.value}(Hyper | 하이퍼)", prop_ignore = 10)
        
        return [WeaponConstant, Mastery, TrueSightHyper]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Hyper:
        True Sight: Ignoring Resistance / Bangmu
        Boss battle skill: Reinforce / Ignor Guard / Boss Killer

        하이퍼 : 
        트루사이트 : 내성무시 / 방무
        보스전 딜스킬 : 리인포스 / 이그노어 가드 / 보스킬러
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        FallingMoon = core.CharacterModifier(pdamage_indep = -10+passive_level//3)

        #Buff skills
        NimbleFinger = core.BuffSkill(DawnWarriorSkills.SoulSpeed.value, 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper) # 펫버프
        TrueSight = core.BuffSkill(DawnWarriorSkills.TrueSight.value, 990, 30 * 1000, armor_ignore = 10+10, pdamage_indep = 5).wrap(core.BuffSkillWrapper) # 내성무시는 not_implied_skill_list에 있음.
        SolunaTime = core.BuffSkill(DawnWarriorSkills.EquinoxCycle.value, 0, (200+6*self.combat) * 1000, rem = True, crit = 35 + passive_level // 2, pdamage_indep = 25, att = 45+passive_level+passive_level//2).wrap(core.BuffSkillWrapper)  # 딜레이 없음.
        SoulForge = core.BuffSkill(DawnWarriorSkills.SoulForge.value, 0, 180 * 1000, att = 50, rem = True).wrap(core.BuffSkillWrapper) # 펫버프
        GloryOfGuardians = core.BuffSkill(DawnWarriorSkills.GloryoftheGuardians.value, 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        #Damage Skills
        SpeedingDance = core.DamageSkill(f"{DawnWarriorSkills.MoonDancer.value}/{DawnWarriorSkills.SpeedingSunset.value}", (360+270)/2, 400+4*self.combat, 4 * 2, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20) + FallingMoon).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        CygnusPhalanx = cygnus.PhalanxChargeWrapper(vEhc, 4, 4)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        SelestialDanceInit = core.BuffSkill(DawnWarriorSkills.CelestialDance.value, 570, (40+vEhc.getV(0,0))*1000, cooltime = 150 * 1000, red = True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        SelestialDanceSummon = core.SummonSkill(f"{DawnWarriorSkills.CelestialDance.value}(Summon | 추가타)", 0, 5000, (1200 + 40 * vEhc.getV(0,0)), 3, (40 + vEhc.getV(0,0)) * 1000, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        SelestialDanceAttack = core.DamageSkill(f"{DawnWarriorSkills.MoonDancer.value}/{DawnWarriorSkills.SpeedingSunset.value}(Celestial | 셀레스티얼)", 0, (400+4*self.combat)*0.01*(30+vEhc.getV(0,0)), 4 * 2, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20) + FallingMoon).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)    # Direct use X. 직접사용 X.
        
        # Elysion 38 hits / 3 hits. 엘리시온 38타 / 3타.
        Elision = core.BuffSkill(DawnWarriorSkills.RiftofDamnation.value, 750, 30 * 1000, cooltime = 180 * 1000, red=True).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)    # Cast delay 750ms. 시전딜레이 750ms.
        ElisionBreak = core.SummonSkill(f"{DawnWarriorSkills.RiftofDamnation.value}(Crack | 균열)", 0, 10000, 520 + 21*vEhc.getV(1,1), 5 * 12, 30000, cooltime=-1).isV(vEhc,1,1).wrap(core.SummonSkillWrapper)    # Triggers 3 times. 3회 발동.
        ElisionStyx = core.DamageSkill(f"{DawnWarriorSkills.StyxCrossing.value}({DawnWarriorSkills.RiftofDamnation.value})", 30 * 1000 / 40, 580/2, 5 * 5 * 2, modifier = FallingMoon).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)  # 40 reps. 40회 반복.
        
        # Soul Eclipse. 소울 이클립스.
        SoulEclipse = core.SummonSkill(DawnWarriorSkills.SoulEclipse.value, 630, 1000, 450 + 18 * vEhc.getV(3,3), 7, 30 * 1000, cooltime = 180 * 1000, red=True).isV(vEhc,3,3).wrap(core.SummonSkillWrapper)
        SolunaDivide = core.DamageSkill("Equinox Divide | 솔루나 디바이드", 750, 1250 + 50 * vEhc.getV(3,3), 15 * 5, cooltime = -1).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)

        FlareSlash = core.DamageSkill(DawnWarriorSkills.FlareSlash.value, 0, 550+22*vEhc.getV(0,0), 7*2, cooltime=12000, modifier=FallingMoon).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
        
        #Final attack type
        SelestialDanceInit.onAfter(SelestialDanceSummon)
        
        SelecstialDanceOption = core.OptionalElement(SelestialDanceInit.is_active, SelestialDanceAttack)
        
        SpeedingDance.onAfter(SelecstialDanceOption)
        
        Elision.onAfter(ElisionBreak)
    
        SoulEclipse.onAfter(SolunaDivide.controller(30*1000))

        # Elysion branch. 엘리시온 분기.
        BasicAttack = core.OptionalElement(Elision.is_active, ElisionStyx, SpeedingDance, name = "Basic attack (determining whether or not Rift) | 기본공격(엘리시온 여부 판단)")
        BasicAttackWrapper = core.DamageSkill('Basic attack | 기본 공격', 0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)

        # Flare slash. 플레어 슬래시.
        SpeedingDance.onAfter(FlareSlash.controller(300, "reduce_cooltime"))
        SelestialDanceAttack.onAfter(FlareSlash.controller(900, "reduce_cooltime"))
        ElisionStyx.onAfter(FlareSlash.controller(1200, "reduce_cooltime"))

        UseFlareSlash = core.OptionalElement(FlareSlash.is_available, FlareSlash, name="Flare Slash cooldown check | 플레어 슬래시 쿨타임 체크")
        SpeedingDance.onAfter(UseFlareSlash)
        ElisionStyx.onAfter(UseFlareSlash)
        FlareSlash.protect_from_running()

        # Weapon Aura. 오라 웨폰.
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 2, modifier=FallingMoon, hit=6*2)
        for sk in [SpeedingDance, ElisionStyx]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        return(BasicAttackWrapper,
                [globalSkill.maple_heros(chtr.level, name = DawnWarriorSkills.CallofCygnus.value, combat_level=self.combat), globalSkill.useful_sharp_eyes(),
                    NimbleFinger, TrueSight, SolunaTime, SoulForge, cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level),
                    GloryOfGuardians, AuraWeaponBuff, AuraWeapon, globalSkill.soul_contract(), SelestialDanceInit, Elision, ElisionBreak,
                    ] +\
                [FlareSlash, CygnusPhalanx, SolunaDivide] +\
                [SelestialDanceSummon, SoulEclipse, MirrorBreak, MirrorSpider] +\
                [BasicAttackWrapper])