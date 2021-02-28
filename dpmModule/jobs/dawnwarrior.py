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

import gettext
_ = gettext.gettext

# English skill information for Dawn Warrior here https://maplestory.fandom.com/wiki/Dawn_Warrior/Skills
class DawnWarriorSkills:
    # Link SKill
    CygnusBlessing = _("시그너스 블레스")  # "Cygnus Blessing"
    # Beginner
    ElementalHarmony = _("엘리멘탈 하모니")  # "Elemental Harmony"
    ElementalExpert = _("엘리멘탈 엑스퍼트")  # "Elemental Expert"
    # 1st Job
    TripleSlash = _("트리플 슬래시")  # "Triple Slash"
    SoulElement = _("엘리멘트: 소울")  # "Soul Element"
    HandofLight = _("소드 오브 라이트")  # "Hand of Light"
    # 2nd Job
    Flicker = _("사일런트 무브")  # "Flicker"
    Bluster = _("라우드 러쉬")  # "Bluster"
    TraceCut = _("트레이스 컷")  # "Trace Cut"
    ShadowTackle = _("섀도우 번")  # "Shadow Tackle"
    FallingMoon = _("폴링 문")  # "Falling Moon"
    SoulSpeed = _("님블 핑거")  # "Soul Speed"
    DivineHand = _("이너 트러스트")  # "Divine Hand"
    SwordMastery = _("소드 마스터리")  # "Sword Mastery"
    InnerHarmony = _("바디 앤 소울")  # "Inner Harmony"
    # 3rd Job
    LightMerger = _("라이트 플럭스")  # "Light Merger"
    MoonShadow = _("문 섀도우")  # "Moon Shadow"
    SunCross = _("선크로스")  # "Sun Cross"
    MoonCross = _("문크로스")  # "Moon Cross"
    RisingSun = _("라이징 선")  # "Rising Sun"
    TrueSight = _("트루 사이트")  # "True Sight"
    SouloftheGuardian = _("소울 가디언")  # "Soul of the Guardian"
    WillofSteel = _("윌 오브 스틸")  # "Will of Steel"
    InnerVoice = _("이너 샤우트")  # "Inner Voice"
    # 4th Job
    CallofCygnus = _("시그너스 나이츠")  # "Call of Cygnus"
    MoonDancer = _("댄스오브 문")  # "Moon Dancer"
    SpeedingSunset = _("스피딩 선셋")  # "Speeding Sunset"
    SolarPierce = _("솔라 피어스")  # "Solar Pierce"
    CrescentDivide = _("크레센트 디바이드")  # "Crescent Divide"
    ImpalingRays = _("소울 페네트레이션")  # "Impaling Rays"
    EquinoxCycle = _("솔루나 타임")  # "Equinox Cycle"
    EquinoxSlash = _("솔루나 슬래시")  # "Equinox Slash"
    SoulPledge = _("소울 플레지")  # "Soul Pledge"
    StudentoftheBlade = _("소드 엑스퍼트")  # "Student of the Blade"
    Unpredictable = _("언포시어블")  # "Unpredictable"
    MasteroftheSword = _("마스터 오브 더 소드")  # "Master of the Sword"
    # Hypers
    StyxCrossing = _("크로스 더 스틱스")  # "Styx Crossing"
    GloryoftheGuardians = _("글로리 오브 가디언즈")  # "Glory of the Guardians"
    SoulForge = _("소울 포지")  # "Soul Forge"
    # 5th Job
    CelestialDance = _("셀레스티얼 댄스")  # "Celestial Dance"
    RiftofDamnation = _("엘리시온")  # "Rift of Damnation"
    SoulEclipse = _("소울 이클립스")  # "Soul Eclipse"
    FlareSlash = _("플레어 슬래시")  # "Flare Slash"


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "STR"
        self.jobname = _("소울마스터")
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule(DawnWarriorSkills.RiftofDamnation, DawnWarriorSkills.CelestialDance, lambda sk: sk.is_not_active() and sk.is_cooltime_left(30000, 1)), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(DawnWarriorSkills.CelestialDance, DawnWarriorSkills.RiftofDamnation), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage = 20)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ElementalExpert = core.InformedCharacterModifier(DawnWarriorSkills.ElementalExpert, patt = 10)
        ElementalHarmony = core.InformedCharacterModifier(DawnWarriorSkills.ElementalHarmony, stat_main = chtr.level // 2)
        
        SwordOfLight = core.InformedCharacterModifier(DawnWarriorSkills.HandofLight,att = 20)
        Soul = core.InformedCharacterModifier(DawnWarriorSkills.SoulElement,armor_ignore = 10)
        InnerTrust = core.InformedCharacterModifier(DawnWarriorSkills.DivineHand,att = 20)
        BodyAndSoul = core.InformedCharacterModifier(DawnWarriorSkills.InnerHarmony,stat_main = 40, stat_sub = 20)
        InnerShout = core.InformedCharacterModifier(DawnWarriorSkills.InnerVoice,att = 30, stat_main = 40)
        
        SoulPledge = core.InformedCharacterModifier(DawnWarriorSkills.SoulPledge,stat_main = 30+passive_level, stat_sub = 30+passive_level, crit = 10)
        SwordExpert = core.InformedCharacterModifier(DawnWarriorSkills.StudentoftheBlade,att = 50+passive_level, crit_damage = 15+passive_level//3)
        Unforseeable = core.InformedCharacterModifier(DawnWarriorSkills.Unpredictable,armor_ignore = 30+2*passive_level, boss_pdamage = 15+passive_level)
        
        return [ElementalHarmony, ElementalExpert, SwordOfLight, Soul, InnerTrust,
                            BodyAndSoul, InnerShout, SoulPledge, SwordExpert, Unforseeable]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier(_("무기상수"),pdamage_indep = 34)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90+ceil(passive_level/2))
        TrueSightHyper = core.InformedCharacterModifier(_("{}(하이퍼)").format(DawnWarriorSkills.TrueSight), prop_ignore = 10)
        
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
        NimbleFinger = core.BuffSkill(DawnWarriorSkills.SoulSpeed, 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper) # 펫버프
        TrueSight = core.BuffSkill(DawnWarriorSkills.TrueSight, 600, 30 * 1000, armor_ignore = 10+10, pdamage_indep = 5).wrap(core.BuffSkillWrapper) # 내성무시는 not_implied_skill_list에 있음.
        SolunaTime = core.BuffSkill(DawnWarriorSkills.EquinoxCycle, 0, (200+6*self.combat) * 1000, rem = True, crit = 35 + passive_level // 2, pdamage_indep = 25, att = 45+passive_level+passive_level//2).wrap(core.BuffSkillWrapper)  # 딜레이 없음.
        SoulForge = core.BuffSkill(DawnWarriorSkills.SoulForge, 0, 180 * 1000, att = 50, rem = True).wrap(core.BuffSkillWrapper) # 펫버프
        GloryOfGuardians = core.BuffSkill(DawnWarriorSkills.GloryoftheGuardians, 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        #Damage Skills
        SpeedingDance = core.DamageSkill(f"{DawnWarriorSkills.MoonDancer}/{DawnWarriorSkills.SpeedingSunset}", (360+330+270+270)/4, 400+4*self.combat, 4 * 2, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20) + FallingMoon).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        CygnusPhalanx = cygnus.PhalanxChargeWrapper(vEhc, 4, 4)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        SelestialDanceInit = core.BuffSkill(DawnWarriorSkills.CelestialDance, 570, (40+vEhc.getV(0,0))*1000, cooltime = 150 * 1000, red = True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        SelestialDanceSummon = core.SummonSkill(_("{}(추가타)").format(DawnWarriorSkills.CelestialDance), 0, 5000, (1200 + 40 * vEhc.getV(0,0)), 3, (40 + vEhc.getV(0,0)) * 1000, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        SelestialDanceAttack = core.DamageSkill(_("{}/{}(셀레스티얼)").format(DawnWarriorSkills.MoonDancer, DawnWarriorSkills.SpeedingSunset), 0, (400+4*self.combat)*0.01*(30+vEhc.getV(0,0)), 4 * 2, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20) + FallingMoon).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)    # Direct use X. 직접사용 X.
        
        # Elysion 38 hits / 3 hits. 엘리시온 38타 / 3타.
        Elision = core.BuffSkill(DawnWarriorSkills.RiftofDamnation, 750, 30 * 1000, cooltime = 180 * 1000, red=True).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)    # Cast delay 750ms. 시전딜레이 750ms.
        ElisionBreak = core.SummonSkill(_("{}(균열)").format(DawnWarriorSkills.RiftofDamnation), 0, (750 * 6 + 5000), 520 + 21*vEhc.getV(1,1), 5 * 6 * 2, (750 * 6 + 5000) * 4 - 1, cooltime=-1, modifier = FallingMoon).isV(vEhc,1,1).wrap(core.SummonSkillWrapper)    # Triggers 3 times. 3회 발동.
        ElisionStyx = core.DamageSkill(f"{DawnWarriorSkills.StyxCrossing}({DawnWarriorSkills.RiftofDamnation})", 750, 580/2, 5 * 5 * 2, modifier = FallingMoon).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)  # 40 reps. 40회 반복.
        
        # Soul Eclipse. 소울 이클립스.
        SoulEclipse = core.SummonSkill(DawnWarriorSkills.SoulEclipse, 270, 1000, 450 + 18 * vEhc.getV(3,3), 7, 30 * 1000, cooltime = 180 * 1000, red=True).isV(vEhc,3,3).wrap(core.SummonSkillWrapper)
        SolunaDivide = core.DamageSkill(_("솔루나 디바이드"), 750 - 300, 1250 + 50 * vEhc.getV(3,3), 15 * 5, cooltime = -1).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)

        FlareSlash = core.DamageSkill(DawnWarriorSkills.FlareSlash, 0, 550+22*vEhc.getV(0,0), 7*2, cooltime=12000, modifier=FallingMoon).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
        
        #Final attack type
        SelestialDanceInit.onAfter(SelestialDanceSummon)
        
        SelecstialDanceOption = core.OptionalElement(SelestialDanceInit.is_active, SelestialDanceAttack)
        
        SpeedingDance.onAfter(SelecstialDanceOption)
        
        Elision.onAfter(ElisionBreak)
    
        SoulEclipse.onAfter(SolunaDivide.controller(30*1000))

        # Elysion branch. 엘리시온 분기.
        BasicAttack = core.OptionalElement(Elision.is_active, ElisionStyx, SpeedingDance, name = _("기본공격(엘리시온 여부 판단)"))
        BasicAttackWrapper = core.DamageSkill(_("기본 공격"), 0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)

        # Flare slash. 플레어 슬래시.
        SpeedingDance.onAfter(FlareSlash.controller(300, "reduce_cooltime"))
        SelestialDanceAttack.onAfter(FlareSlash.controller(900, "reduce_cooltime"))
        ElisionStyx.onAfter(FlareSlash.controller(1200, "reduce_cooltime"))

        UseFlareSlash = core.OptionalElement(FlareSlash.is_available, FlareSlash, name=_("플레어 슬래시 쿨타임 체크"))
        SpeedingDance.onAfter(UseFlareSlash)
        ElisionStyx.onAfter(UseFlareSlash)
        FlareSlash.protect_from_running()

        # Weapon Aura. 오라 웨폰.
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 2, modifier=FallingMoon, hit=6*2)
        for sk in [SpeedingDance, ElisionStyx]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        return(BasicAttackWrapper,
                [globalSkill.maple_heros(chtr.level, name = DawnWarriorSkills.CallofCygnus, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    NimbleFinger, TrueSight, SolunaTime, SoulForge, cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level),
                    GloryOfGuardians, AuraWeaponBuff, AuraWeapon, globalSkill.soul_contract(), SelestialDanceInit, Elision, ElisionBreak,
                    ] +\
                [FlareSlash, CygnusPhalanx, SolunaDivide] +\
                [SelestialDanceSummon, SoulEclipse, MirrorBreak, MirrorSpider] +\
                [BasicAttackWrapper])