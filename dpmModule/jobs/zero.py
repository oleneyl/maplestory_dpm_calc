from dpmModule.jobs.globalSkill import GlobalSkills, WAVE, BUFF, LINK, SHOCK_WAVE, ENDING, DAMAGE, LAST_HIT

from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, MutualRule
from . import globalSkill, jobutils
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict

from localization.utilities import translator
_ = translator.gettext

# English skill information for Zero here https://maplestory.fandom.com/wiki/Zero/Skills
class ZeroSkills:
    # Link Skill
    RhinnesBlessing = _("륀느의 축복")  # "Rhinne's Blessing"
    # Shared Skills
    DualCombat = _("듀얼 컴뱃")  # "Dual Combat"
    ResolutionTime = _("리졸브 타임")  # "Resolution Time"
    DivineForce = _("디바인 포스")  # "Divine Force"
    DivineSpeed = _("디바인 스위프트")  # "Divine Speed"
    RhinnesProtection = _("륀느의 가호")  # "Rhinne's Protection"
    Doubletime = _("래피드 타임")  # "Doubletime"
    TimeDistortion = _("타임 디스토션")  # "Time Distortion"
    TimeHolding = _("타임 홀딩")  # "Time Holding"
    Rewind = _("타임 리와인드")  # "Rewind"
    ShadowRain = _("쉐도우 레인")  # "Shadow Rain"
    FocusedTime = _("인탠시브 타임")  # "Focused Time"
    # Alpha's Skills
    MoonStrike = _("문 스트라이크")  # "Moon Strike"
    PiercingThrust = _("피어스 쓰러스트")  # "Piercing Thrust"
    ShadowStrike = _("쉐도우 스트라이크")  # "Shadow Strike"
    FlashAssault = _("플래시 어썰터")  # "Flash Assault"
    SpinCutter = _("스핀 커터")  # "Spin Cutter"
    AdvancedSpinCutter = _("어드밴스드 스핀 커터")  # "Advanced Spin Cutter"
    RollingCross = _("롤링 커브")  # "Rolling Cross"
    GrandRollingCross = _("어드밴스드 롤링 커브")  # "Grand Rolling Cross"
    RollingAssault = _("롤링 어썰터")  # "Rolling Assault"
    AdvancedRollingAssault = _("어드밴스드 롤링 어썰터")  # "Advanced Rolling Assault"
    WindCutter = _("윈드 커터")  # "Wind Cutter"
    WindStriker = _("윈드 스트라이크")  # "Wind Striker"
    StormBreak = _("스톰 브레이크")  # "Storm Break"
    AdvancedStormBreak = _("어드밴스드 스톰 브레이크")  # "Advanced Storm Break"
    LongSwordMastery = _("태도 마스터리")  # "Long Sword Mastery"
    TimeGenerator = _("컴뱃 리커버리")  # "Time Generator"
    ReinforceBody = _("리인포스 바디")  # "Reinforce Body"
    DivineLeer = _("디바인 리어")  # "Divine Leer"
    # Beta's Skills
    RisingSlash = _("어퍼 슬래시")  # "Rising Slash"
    AirRaid = _("파워 스텀프")  # "Air Raid"
    AirRiot = _("어드밴스드 파워 스텀프")  # "Air Riot"
    FlashCut = _("프론트 슬래시")  # "Flash Cut"
    ThrowingWeapon = _("스로잉 웨폰")  # "Throwing Weapon"
    AdvancedThrowingWeapon = _("어드밴스드 스로잉 웨폰")  # "Advanced Throwing Weapon"
    SpinDriver = _("터닝 드라이브")  # "Spin Driver"
    WheelWind = _("휠 윈드")  # "Wheel Wind"
    AdvancedWheelWind = _("어드밴스드 휠 윈드")  # "Advanced Wheel Wind"
    GigaCrash = _("기가 크래시")  # "Giga Crash"
    FallingStar = _("점핑 크래시")  # "Falling Star"
    EarthBreak = _("어스 브레이크")  # "Earth Break"
    AdvancedEarthBreak = _("어드밴스드 어스 브레이크")  # "Advanced Earth Break"
    HeavySwordMastery = _("대검 마스터리")  # "Heavy Sword Mastery"
    SolidBody = _("솔리드 바디")  # "Solid Body"
    ArmorSplit = _("아머 스플릿")  # "Armor Split"
    ImmuneBarrier = _("이뮨 배리어")  # "Immune Barrier"
    CriticalBind = _("크리티컬 바인드")  # "Critical Bind"
    # 5th Job
    TranscendentRhinnesPrayer = _("초월자 륀느의 기원")  # "Transcendent Rhinne's Prayer"
    ChronoBreak = _("리미트 브레이크")  # "Chrono Break"
    TwinBladesofTime = _("조인트 어택")  # "Twin Blades of Time"
    ShadowFlash = _("쉐도우 플래시")  # "Shadow Flash"
    EgoWeapon = _("에고 웨폰")  # "Ego Weapon"


# Skill name modifiers for zero only
TAG = _("태그")
AURA = _("오라")
SWIRL = _("소용돌이")
ELECTRIC = _("전기")
CDR = _("재사용 대기시간 감소")
ALPHA = _("알파")
BETA = _("베타")
'''
Assist mechanism summary

Always Alpha Stats: Spin Cutter Aura, Rolling Curve Aura, Rolling Assault Aura
Always Apply Beta Stat: Power Stump Shockwave

어시스트 매커니즘 정리

항상 알파 스탯 적용: 스핀 커터 오라, 롤링 커브 오라, 롤링 어썰터 오라
항상 베타 스탯 적용: 파워 스텀프 충격파

https://github.com/Monolith11/memo/wiki/Zero-Skill-Mechanics
'''


class CriticalBindWrapper(core.BuffSkillWrapper):
    def __init__(self, alphaState: core.BuffSkillWrapper, betaState: core.BuffSkillWrapper):
        skill = core.BuffSkill(ZeroSkills.CriticalBind, 0, 4000, cooltime=35000, crit=30, crit_damage=20)
        super(CriticalBindWrapper, self).__init__(skill)
        self.alphaState = alphaState
        self.betaState = betaState

    def get_modifier(self):
        if self.alphaState.is_not_active():
            return self.disabledModifier
        return super(CriticalBindWrapper, self).get_modifier()

    def is_usable(self):
        if self.betaState.is_not_active():
            return False
        return super(CriticalBindWrapper, self).is_usable()


class JobGenerator(ck.JobGenerator):
    # 제로는 쓸컴뱃 효율이 낮으나 일단 딜이 증가하므로 사용
    # 패시브 레벨 +1 어빌 사용 불가능
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vSkillNum = 5
        self.vEnhanceNum = 13
        self.jobtype = "STR"
        self.jobname = _("제로")
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(MutualRule(ZeroSkills.TimeHolding, GlobalSkills.TermsAndConditions), RuleSet.BASE)
        ruleset.add_rule(MutualRule(ZeroSkills.TimeHolding, ZeroSkills.TimeDistortion), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90)
        ResolutionTime = core.InformedCharacterModifier(_("리졸브 타임"), pdamage_indep=25, stat_main=50)

        return [Mastery, ResolutionTime]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        ArmorSplit = core.InformedCharacterModifier(ZeroSkills.ArmorSplit, armor_ignore=50)
        return [ArmorSplit]

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(crit=15, pdamage=75, armor_ignore=20, crit_damage=22)

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Applied separately from Mastery: Alpha: 1.34, Beta: 1.49

        Using Divine Swift
        Divine Force is used only during limit brake

        Nasal order

        Pierce Thrust (+ Power Stump)
        Spin Cutter + Throwing Weapon
        Roller + Turning Drive
        Rolling Assaulter + Wheelwind
        Storm Break + Earth Break

        Moons + Upper Slash
        Flash Assaulter + Front Slash
        Wind Cutter + Giga Crash
        Wind slash + dot pink lash

        Appas standard

        마스터리 별개로 적용 : 알파 : 1.34, 베타 : 1.49

        디바인 스위프트 사용
        리미트 브레이크 도중에만 디바인 포스 사용

        코강 순서

        피어스 쓰러스트 (+ 파워 스텀프)
        스핀커터 + 스로잉웨폰
        롤커 + 터닝 드라이브
        롤링 어썰터 + 휠윈드
        스톰브레이크 + 어스브레이크

        문스 + 어퍼슬래시
        플래시어썰터 + 프론트 슬래시
        윈드커터 + 기가크래시
        윈드슬래시 + 점핑크래시

        어파스 기준
        '''
        DEALCYCLE = options.get('dealcycle', 'alpha_legacy')

        #### Mastery. 마스터리 ####
        # Beta Mastery's attack power +4 is the difference in weapon base attack power. 베타 마스터리의 공격력 +4는 무기 기본 공격력 차이.
        # Genesis weapon needs to be changed to +5 제네시스 무기의 경우 +5로 변경 필요.

        AlphaMDF = core.CharacterModifier(pdamage_indep=5, crit=40, att=40, armor_ignore=30, crit_damage=50) + core.CharacterModifier(pdamage_indep=34)
        BetaMDF = core.CharacterModifier(pdamage_indep=5, crit=15, boss_pdamage=30, att=80+4) + core.CharacterModifier(pdamage_indep=49)

        AlphaState = core.BuffSkill(_("상태-알파"), 0, 9999*10000, cooltime=-1,
                                    pdamage_indep=AlphaMDF.pdamage_indep,
                                    crit=AlphaMDF.crit,
                                    boss_pdamage=AlphaMDF.boss_pdamage,
                                    att=AlphaMDF.att,
                                    armor_ignore=AlphaMDF.armor_ignore,
                                    crit_damage=AlphaMDF.crit_damage
                                    ).wrap(core.BuffSkillWrapper)
        BetaState = core.BuffSkill(_("상태-베타"), 0, 9999*10000, cooltime=-1,
                                   pdamage_indep=BetaMDF.pdamage_indep,
                                   crit=BetaMDF.crit,
                                   boss_pdamage=BetaMDF.boss_pdamage,
                                   att=BetaMDF.att,
                                   armor_ignore=BetaMDF.armor_ignore,
                                   crit_damage=BetaMDF.crit_damage
                                   ).wrap(core.BuffSkillWrapper)

        # extra_damage(x): A bonus damper for decreasing the number of targets in Greatsword Mastery (x = number of targets). extra_damage(x): 대검 마스터리의 타겟수 감소에 따른 보너스 뎀퍼 (x = 타겟 수).
        # The increase in the number of targets due to the nasal cavity does not affect the increase in the damper. 코강으로 인한 타겟수 증가는 뎀퍼 증가에 영향을 주지 않음.
        def extra_damage(x):
            return core.CharacterModifier(pdamage=8*(x-1))

        #### Alpha. 알파 ####
        MoonStrike = core.DamageSkill(ZeroSkills.MoonStrike, 390, 120, 6).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        MoonStrikeLink = core.DamageSkill(f"{ZeroSkills.MoonStrike}({LINK})", 330, 120, 6).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        MoonStrikeTAG = core.DamageSkill(f"{ZeroSkills.MoonStrike}({TAG})", 0, 120, 6).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)

        PierceStrike = core.DamageSkill(ZeroSkills.PiercingThrust, 510, 170, 6).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        PierceStrikeLink = core.DamageSkill(f"{ZeroSkills.PiercingThrust}({LINK})", 360, 170, 6).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        PierceStrikeTAG = core.DamageSkill(f"{ZeroSkills.PiercingThrust}({TAG})", 0, 170, 6).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)

        ShadowStrike = core.DamageSkill(ZeroSkills.ShadowStrike, 240+90, 195, 8).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        ShadowStrikeAura = core.DamageSkill(f"{ZeroSkills.ShadowStrike}({AURA})", 0, 310, 1).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)

        FlashAssault = core.DamageSkill(ZeroSkills.FlashAssault, 270, 165, 8).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        FlashAssaultTAG = core.DamageSkill(f"{ZeroSkills.FlashAssault}({TAG})", 0, 165, 8).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)

        AdvancedSpinCutter = core.DamageSkill(ZeroSkills.AdvancedSpinCutter, 270, 260+3*self.combat, 10).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedSpinCutterTAG = core.DamageSkill(f"{ZeroSkills.AdvancedSpinCutter}({TAG})", 0, 260+3*self.combat, 10).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedSpinCutterAura = core.DamageSkill(f"{ZeroSkills.AdvancedSpinCutter}({AURA})", 0, 130+3*self.combat, 4).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedSpinCutterAuraTAG = core.DamageSkill(f"{ZeroSkills.AdvancedSpinCutter}({AURA})({TAG})", 0, 130+3*self.combat, 4, modifier=AlphaMDF-BetaMDF).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)  # 항상 알파 스탯이 적용됨

        AdvancedRollingCurve = core.DamageSkill(ZeroSkills.GrandRollingCross, 960, 365+3*self.combat, 12).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingCurveTAG = core.DamageSkill(f"{ZeroSkills.GrandRollingCross}({TAG})", 0, 365+3*self.combat, 12).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingCurveAura = core.DamageSkill(f"{ZeroSkills.GrandRollingCross}({AURA})", 0, 350+self.combat, 2).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingCurveAuraTAG = core.DamageSkill(f"{ZeroSkills.GrandRollingCross}({AURA})({TAG})", 0, 350+self.combat, 2*2, modifier=AlphaMDF-BetaMDF).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)  # 항상 알파 스탯이 적용됨, 각 투사체가 2회 타격함

        AdvancedRollingAssulter = core.DamageSkill(ZeroSkills.AdvancedRollingAssault, 960, 375+2*self.combat, 12).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingAssulterTAG = core.DamageSkill(f"{ZeroSkills.AdvancedRollingAssault}({TAG})", 0, 375+2*self.combat, 12).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingAssulterAura = core.DamageSkill(f"{ZeroSkills.AdvancedRollingAssault}({AURA})", 0, 250+self.combat, 3).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingAssulterAuraTAG = core.DamageSkill(f"{ZeroSkills.AdvancedRollingAssault}({AURA})({TAG})", 0, 250+self.combat, 3*2*2, modifier=AlphaMDF-BetaMDF).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)  # 항상 알파 스탯이 적용됨, 2회 사출, 각 투사체가 2회 타격함

        WindCutter = core.DamageSkill(ZeroSkills.WindCutter, 420, 165, 8).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        WindCutterSummon = core.DamageSkill(f"{ZeroSkills.WindCutter}({SWIRL})", 0, 110, 3*2, cooltime=-1).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)  # Lasts up to 3 seconds, hits twice. 최대 3초지속, 2회 타격.
        WindCutterTAG = core.DamageSkill(f"{ZeroSkills.WindCutter}({TAG})", 0, 165, 8).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)

        WindStrike = core.DamageSkill(ZeroSkills.WindStriker, 480, 250, 8).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)
        WindStrikeTAG = core.DamageSkill(f"{ZeroSkills.WindStriker}({TAG})", 0, 250, 8).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)

        AdvancedStormBreak = core.DamageSkill(ZeroSkills.AdvancedStormBreak, 690, 335+2*self.combat, 10).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedStormBreakSummon = core.DamageSkill(f"{ZeroSkills.AdvancedStormBreak}({SWIRL})", 0, 335+2*self.combat, 4, cooltime=-1).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)  # Lasts up to 3 seconds, hits once. 최대 3초지속, 1회 타격.
        AdvancedStormBreakElectric = core.SummonSkill(f"{ZeroSkills.AdvancedStormBreak}({ELECTRIC})", 0, 1000, 230+2*self.combat, 1, (3+ceil(self.combat/10))*1000, cooltime=-1).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)
        AdvancedStormBreakTAG = core.DamageSkill(f"{ZeroSkills.AdvancedStormBreak}({TAG})", 0, 335+2*self.combat, 10).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)

        # Dot skill does not apply Cdem, so there is no need to add AlphaSkill. 도트스킬은 크뎀 미적용이므로 AlphaSkill 추가할 필요없음.
        DivineLeer = core.DotSkill(ZeroSkills.DivineLeer, 0, 1000, 200, 1, 99999999).wrap(core.DotSkillWrapper)

        #### Beta. 베타 ####

        UpperSlash = core.DamageSkill(ZeroSkills.RisingSlash, 390, 210, 6, modifier=extra_damage(6)).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        UpperSlashTAG = core.DamageSkill(f"{ZeroSkills.RisingSlash}({TAG})", 0, 210, 6, modifier=extra_damage(6)).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)

        AdvancedPowerStomp = core.DamageSkill(ZeroSkills.AirRiot, 570, 330+5*self.combat, 9, modifier=extra_damage(6)).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        AdvancedPowerStompTAG = core.DamageSkill(f"{ZeroSkills.AirRiot}({TAG})", 0, 330+5*self.combat, 9, modifier=extra_damage(6)).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        AdvancedPowerStompWave = core.DamageSkill(f"{ZeroSkills.AirRiot}({WAVE})", 0, 330+5*self.combat, 9, modifier=extra_damage(6)).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        AdvancedPowerStompWaveTAG = core.DamageSkill(f"{ZeroSkills.AirRiot}({WAVE})({TAG})", 0, 330+5*self.combat, 9, modifier=extra_damage(6)+BetaMDF-AlphaMDF).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)  # Beta stats are always applied. 항상 베타 스탯이 적용됨.

        FrontSlash = core.DamageSkill(ZeroSkills.FlashCut, 450, 205, 6, modifier=extra_damage(6)).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        FrontSlashTAG = core.DamageSkill(f"{ZeroSkills.FlashCut}({TAG})", 0, 205, 6, modifier=extra_damage(6)).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)

        THROWINGHIT = 5
        ThrowingWeapon = core.SummonSkill(ZeroSkills.AdvancedThrowingWeapon, 480, 300, 550+5*self.combat, 2, THROWINGHIT*300, cooltime=-1, modifier=extra_damage(6)).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)

        TurningDrive = core.DamageSkill(ZeroSkills.SpinDriver, 360, 260, 6, modifier=extra_damage(6)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        TurningDriveTAG = core.DamageSkill(f"{ZeroSkills.SpinDriver}({TAG})", 0, 260, 6, modifier=extra_damage(6)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedWheelWind = core.DamageSkill(ZeroSkills.AdvancedWheelWind, 900, 200+2*self.combat, 2*7, modifier=extra_damage(6)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)  # 1 stroke per 0.1 seconds, maximum 7 seconds, 7 strokes applied. 0.1초당 1타, 최대 7초, 7타로 적용.
        AdvancedWheelWindTAG = core.DamageSkill(f"{ZeroSkills.AdvancedWheelWind}({TAG})", 0, 200+2*self.combat, 2*7, modifier=extra_damage(6)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)  # 1 stroke per 0.1 seconds, maximum 7 seconds, 7 strokes applied. 0.1초당 1타, 최대 7초, 7타로 적용.

        GigaCrash = core.DamageSkill(ZeroSkills.GigaCrash, 540, 250, 6, modifier=extra_damage(6)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        GigaCrashTAG = core.DamageSkill(f"{ZeroSkills.GigaCrash}({TAG})", 0, 250, 6, modifier=extra_damage(6)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)

        JumpingCrash = core.DamageSkill(ZeroSkills.FallingStar, 300+210, 225, 6, modifier=extra_damage(6)).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)
        JumpingCrashTAG = core.DamageSkill(f"{ZeroSkills.FallingStar}({TAG})", 0, 225, 6, modifier=extra_damage(6)).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)
        JumpingCrashWave = core.DamageSkill(f"{ZeroSkills.FallingStar}({SHOCK_WAVE})", 0, 225, 3, modifier=extra_damage(6)).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)

        AdvancedEarthBreak = core.DamageSkill(ZeroSkills.AdvancedEarthBreak, 630+390, 380+3*self.combat, 10, modifier=extra_damage(6)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedEarthBreakTAG = core.DamageSkill(f"{ZeroSkills.AdvancedEarthBreak}({TAG})", 0, 380+3*self.combat, 10, modifier=extra_damage(6)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedEarthBreakWave = core.DamageSkill(f"{ZeroSkills.AdvancedEarthBreak}({WAVE})", 0, 285+3*self.combat, 10, modifier=extra_damage(6)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedEarthBreakElectric = core.SummonSkill(f"{ZeroSkills.AdvancedEarthBreak}({ELECTRIC})", 0, 1000, 340+3*self.combat, 1, 5000, cooltime=-1, modifier=extra_damage(6)).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)

        CriticalBind = CriticalBindWrapper(AlphaState, BetaState)

        #### Transcendental Skill. 초월자 스킬 ####

        DoubleTime = core.BuffSkill(ZeroSkills.Doubletime, 0, 9999*10000, crit=20, pdamage=10).wrap(core.BuffSkillWrapper)
        TimeDistortion = core.BuffSkill(ZeroSkills.TimeDistortion, 540, 30000, cooltime=240*1000, red=True, pdamage=25).wrap(core.BuffSkillWrapper)
        TimeHolding = core.BuffSkill(ZeroSkills.TimeHolding, 0, 90000, cooltime=180*1000, pdamage=10, red=True).wrap(core.BuffSkillWrapper)  # Reset cooldown. (Excluding Time Rewa / Limit Break). 쿨타임 초기화. (타임 리와 / 리미트 브레이크 제외).
        # Intensive Time-Basic doping includes spirits. 인탠시브 타임 - 기본 도핑에 영메 포함되어 있음.

        # Alpha 4410ms Beta 4980ms. 알파 4410ms 베타 4980ms.
        # ShadowRain = core.DamageSkill(ZeroSkills.ShadowRain, 0, 1400, 14, cooltime=300*1000).wrap(core.DamageSkillWrapper)

        SoulContract = globalSkill.soul_contract()

        #### 5th skill. 5차 스킬 ####
        # 5th skill Mastery Alpha/Beta should be applied separately.
        # Limit brake and joint attack are used in beta condition.
        # 5차스킬들 마스터리 알파/베타 구분해서 적용할것.
        # 리미트 브레이크, 조인트 어택은 베타 상태에서 사용.
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)  # TODO: Check whether the damage increase per beta target is applied. 베타 타겟당 데미지 증가 적용여부 확인할것.

        LimitBreakAttack = core.DamageSkill(ZeroSkills.ChronoBreak, 0, 400+15*vEhc.getV(0, 0), 5, modifier=extra_damage(15)).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        LimitBreak = core.BuffSkill(f"{ZeroSkills.ChronoBreak}({BUFF})", 450, (30+vEhc.getV(0, 0)//2)*1000, pdamage_indep=30+vEhc.getV(0, 0)//5, cooltime=240*1000, red=True).isV(vEhc, 0, 0).wrap(core.BuffSkillWrapper)
        LimitBreakCDR = core.SummonSkill(f"{ZeroSkills.ChronoBreak}({CDR})", 0, 1000, 0, 0, (30+vEhc.getV(0, 0)//2)*1000, cooltime=-1).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)

        LimitBreakFinal = core.DamageSkill(f"{ZeroSkills.ChronoBreak}({LAST_HIT})", 0, 650 + 26*vEhc.getV(0, 0), 12*6, cooltime=-1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        # 베타로 사용함.
        TwinBladeOfTime = core.DamageSkill(ZeroSkills.TwinBladesofTime, 0, 0, 0, cooltime=120*1000, red=True).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_Alpha_1 = core.DamageSkill(f"{ZeroSkills.TwinBladesofTime}({ALPHA}(1))", 450, 875+35*vEhc.getV(1, 1), 8).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_Alpha_2 = core.DamageSkill(f"{ZeroSkills.TwinBladesofTime}({ALPHA}(2))", 720, 835+33*vEhc.getV(1, 1), 12).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_Alpha_3 = core.DamageSkill(f"{ZeroSkills.TwinBladesofTime}({ALPHA}(3))", 1020, 1000+40*vEhc.getV(1, 1), 13).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_Beta_1 = core.DamageSkill(f"{ZeroSkills.TwinBladesofTime}({BETA}(1))", 540, 875+35*vEhc.getV(1, 1), 8, modifier=extra_damage(12)).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_Beta_2 = core.DamageSkill(f"{ZeroSkills.TwinBladesofTime}({BETA}(2))", 450, 835+33*vEhc.getV(1, 1), 12, modifier=extra_damage(12)).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_Beta_3 = core.DamageSkill(f"{ZeroSkills.TwinBladesofTime}({BETA}(3))", 360, 1000+40*vEhc.getV(1, 1), 13, modifier=extra_damage(12)).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_end = core.DamageSkill(f"{ZeroSkills.TwinBladesofTime}(4)", 1050, 900+36*vEhc.getV(1, 1), 15*3, modifier=extra_damage(12)+core.CharacterModifier(armor_ignore=100)).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)

        # Alpha. 알파.
        ShadowFlashAlpha = core.DamageSkill(f"{ZeroSkills.ShadowFlash}({ALPHA})", 510, 500+20*vEhc.getV(2, 2), 6, cooltime=40*1000, red=True).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)
        ShadowFlashAlphaEnd = core.DamageSkill(f"{ZeroSkills.ShadowFlash}({ALPHA})({ENDING})", 660, 400+16*vEhc.getV(2, 2), 15*3).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)

        # Beta. 베타.
        ShadowFlashBeta = core.DamageSkill(f"{ZeroSkills.ShadowFlash}({BETA})", 510, 600+24*vEhc.getV(2, 2), 5, cooltime=40*1000, modifier=extra_damage(8), red=True).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)
        ShadowFlashBetaEnd = core.DamageSkill(f"{ZeroSkills.ShadowFlash}({BETA})({ENDING})", 660, 750+30*vEhc.getV(2, 2), 12*2, modifier=extra_damage(15)).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)

        # The origin of the Transcendent Lune 초월자 륀느의 기원.
        RhinneBless = core.BuffSkill(ZeroSkills.TranscendentRhinnesPrayer, 480, (30+vEhc.getV(0, 0)//2)*1000, cooltime=240000, att=10+3*vEhc.getV(0, 0)).wrap(core.BuffSkillWrapper)
        RhinneBlessAttack_hit = core.DamageSkill(f"{ZeroSkills.TranscendentRhinnesPrayer}({DAMAGE})", 0, 125+5*vEhc.getV(0, 0), 5).wrap(core.DamageSkillWrapper)
        RhinneBlessAttack = core.OptionalElement(RhinneBless.is_active, RhinneBlessAttack_hit)

        # Ego weapon. 에고 웨폰.
        EgoWeaponAlpha = core.DamageSkill(f"{ZeroSkills.EgoWeapon}({ALPHA})", 0, 175+7*vEhc.getV(0, 0), 6*9, cooltime=15000, red=True).wrap(core.DamageSkillWrapper)
        EgoWeaponBeta = core.DamageSkill(f"{ZeroSkills.EgoWeapon}({BETA})", 0, 175+7*vEhc.getV(0, 0), 9*2*3, cooltime=15000, red=True, modifier=extra_damage(4)).wrap(core.DamageSkillWrapper)

        ######   Skill Wrapper   ######

        # Come Divine. 디바인 오라.
        DivineForce = core.BuffSkill(ZeroSkills.DivineForce, 0, core.infinite_time(), att=20).wrap(core.BuffSkillWrapper)

        ### Skill connection. 스킬 연결 ###
        ### Alpha. 알파 ###
        ShadowStrike.onAfter(ShadowStrikeAura)

        AdvancedSpinCutter.onAfter(AdvancedSpinCutterAura)
        AdvancedSpinCutterTAG.onAfter(AdvancedSpinCutterAuraTAG)

        AdvancedRollingCurve.onAfter(AdvancedRollingCurveAura)
        AdvancedRollingCurveTAG.onAfter(AdvancedRollingCurveAuraTAG)

        AdvancedRollingAssulter.onAfter(AdvancedRollingAssulterAura)
        AdvancedRollingAssulterTAG.onAfter(AdvancedRollingAssulterAuraTAG)

        WindCutter.onAfter(WindCutterSummon)
        AdvancedStormBreak.onAfter(AdvancedStormBreakElectric)
        AdvancedStormBreak.onAfter(AdvancedStormBreakSummon)

        ### Beta. 베타 ###
        AdvancedPowerStomp.onAfter(AdvancedPowerStompWave)
        AdvancedPowerStompTAG.onAfter(AdvancedPowerStompWaveTAG)

        JumpingCrash.onAfter(JumpingCrashWave)
        AdvancedEarthBreak.onAfter(AdvancedEarthBreakWave)
        AdvancedEarthBreak.onAfter(AdvancedEarthBreakElectric)

        JumpingCrashTAG.onAfter(JumpingCrashWave)
        AdvancedEarthBreakTAG.onAfter(AdvancedEarthBreakWave)
        AdvancedEarthBreakTAG.onAfter(AdvancedEarthBreakElectric)

        ### Status tag! 상태 태그! ###
        SetAlpha = core.GraphElement(_("알파로 태그"))
        SetAlpha.onAfter(AlphaState)
        SetAlpha.onAfter(BetaState.controller(-1))
        SetBeta = core.GraphElement(_("베타로 태그"))
        SetBeta.onAfter(BetaState)
        SetBeta.onAfter(AlphaState.controller(-1))

        BetaState.controller(1)  # Start with beta. 베타로 시작.

        ### Create damage cycle. 딜사이클 생성.
        if DEALCYCLE == "alpha_new":
            # Moons(0ms)-Pierce(330ms)-Chess(690ms)-Moons(1020ms)-Pierces(1350ms)-Chess(1710ms)-Moons(2040ms)-Pierces(2370ms)-Chess(2730ms)-Moons(3060ms) -3450 ms.
            # Upper(60ms)-Upper(330ms)-Upper(900ms)-Upper(1350ms)-Upper(1920ms)-Upper(2370ms)-2940ms-3330ms.
            # 2940ms: Appas delay ends.
            # 3330ms: Even after the Apas Delay is over, a shockwave must occur before tagging (2370 + 960).

            # 문스(0ms) - 피어스(330ms) - 쉐스(690ms) - 문스(1020ms) - 피어스(1350ms) - 쉐스(1710ms) - 문스(2040ms) - 피어스(2370ms) - 쉐스(2730ms) - 문스(3060ms) - 3450ms.
            # 어퍼(60ms) - 어파스(330ms) -      어퍼(900ms) -          어파스(1350ms) -            어퍼(1920ms)    - 어파스(2370ms)               - 2940ms -   3330ms.
            # 2940ms: 어파스 딜레이 종료.
            # 3330ms: 어파스 딜레이가 끝났어도 충격파 발생해야 태그 가능 (2370 + 960).
            AlphaCombo = [SetAlpha, MoonStrikeLink, UpperSlashTAG, PierceStrikeLink, AdvancedPowerStompTAG, ShadowStrike,
                          MoonStrikeLink, UpperSlashTAG, PierceStrikeLink, AdvancedPowerStompTAG, ShadowStrike,
                          MoonStrikeLink, UpperSlashTAG, PierceStrikeLink, AdvancedPowerStompTAG, ShadowStrike,
                          MoonStrike]
        elif DEALCYCLE == "alpha_legacy":
            # Winker(0ms)-Wins(420ms)-Storm(900ms)-Moons(1590ms)-Piercing(1920ms)-Moons(2430ms)-Piercing(2760ms)-3270ms.
            # Giga (60ms)-Jumping (690ms)-Earth (1260ms)-Upper Chewing-Upper Chewing (2340ms) Upper, Upper Chewing-2970ms.

            # 윈커(0ms) - 윈스(420ms) - 스톰(900ms) - 문스(1590ms) - 피어싱(1920ms) - 문스(2430ms) - 피어싱(2760ms) - 3270ms.
            # 기가(60ms) -       점핑(690ms) -   어스(1260ms) - 어퍼 씹힘 -   어파스(2340ms)   어퍼, 어파스 씹힘  - 2970ms.
            AlphaCombo = [SetAlpha, WindCutter, GigaCrashTAG, WindStrike, JumpingCrashTAG, AdvancedStormBreak, AdvancedEarthBreakTAG,
                          MoonStrikeLink, PierceStrike, AdvancedPowerStompTAG, MoonStrikeLink, PierceStrike]
        elif DEALCYCLE == "alpha_legacy2":
            # Winker-Wins-Moons-Piercing-Ches-Moons-Piercing-Chess.
            # Assy list is the same.
            # 윈커-윈스-문스-피어싱-쉐스-문스-피어싱-쉐스.
            # 어시 목록은 동일.
            AlphaCombo = [SetAlpha, WindCutter, GigaCrashTAG, WindStrike, JumpingCrashTAG, AdvancedStormBreak, AdvancedEarthBreakTAG,
                          MoonStrikeLink, PierceStrikeLink, AdvancedPowerStompTAG, ShadowStrike, MoonStrikeLink, PierceStrikeLink, ShadowStrike]
        else:
            raise ValueError(DEALCYCLE)

        # Turning (0ms)-Wheelwin (360ms)-Front (1260ms)-Throwing (1710ms)-Upper (2190ms)-Upper (2580ms)-3150ms.
        # Roller (60ms)-Roller (1020ms)-Flash Chew-Spin (1710ms)-Moons (2190ms)-2640ms.

        # 터닝(0ms) - 휠윈(360ms) - 프런트(1260ms) - 스로잉(1710ms) - 어퍼(2190ms) - 어파스(2580ms) - 3150ms.
        # 롤커(60ms) -        롤어(1020ms) - 플래시 씹힘 - 스핀(1710ms) - 문스(2190ms)  -  2640ms.
        BetaCombo = [SetBeta, TurningDrive, AdvancedRollingCurveTAG, AdvancedWheelWind, AdvancedRollingAssulterTAG,
                     FrontSlash, ThrowingWeapon, AdvancedSpinCutterTAG, UpperSlash, MoonStrikeTAG, AdvancedPowerStomp]
        ComboHolder = core.DamageSkill(_("기본 공격"), 0, 0, 0).wrap(core.DamageSkillWrapper)
        for sk in AlphaCombo + BetaCombo:
            ComboHolder.onAfter(sk)

        ### Time holding initialization. 타임 홀딩 초기화 ###
        TimeHolding.onAfter(TimeDistortion.controller(1.0, "reduce_cooltime_p"))
        TimeHolding.onAfter(SoulContract.controller(1.0, "reduce_cooltime_p"))

        ### 5th skills. 5차 스킬들 ###
        TwinBladeOfTime.onBefore(SetBeta)
        for sk in [TwinBladeOfTime_Beta_1, TwinBladeOfTime_Alpha_1, TwinBladeOfTime_Beta_2, TwinBladeOfTime_Alpha_2,
                   TwinBladeOfTime_Beta_3, TwinBladeOfTime_Alpha_3, TwinBladeOfTime_end]:
            TwinBladeOfTime.onAfter(sk)
        ShadowFlashAlpha.onAfter(ShadowFlashAlphaEnd)
        ShadowFlashBeta.onAfter(ShadowFlashBetaEnd)
        LimitBreak.onBefore(SetBeta)
        LimitBreak.onAfter(LimitBreakAttack)
        LimitBreak.onAfter(LimitBreakCDR)
        LimitBreak.onEventElapsed(LimitBreakFinal, (30+vEhc.getV(0,0)//2)*1000-1)  # Last hit just before the end of the buff. 버프 종료 직전에 막타.
        LimitBreakFinal.add_runtime_modifier(BetaState, lambda beta: extra_damage(15) if beta.is_active() else core.CharacterModifier())

        for sk in [TimeDistortion, SoulContract]:
            # The cooldown of skills, excluding those that are not affected by the cooldown reset, decreases faster (base 200%, 10% every 5 levels).
            # 재사용 대기시간 초기화의 효과를 받지 않는 스킬을 제외한 스킬의 재사용 대기시간이 (기본 200%에 5레벨마다 10%씩) 더 빠르게 감소.
            LimitBreakCDR.onTick(sk.controller(2000+20*vEhc.getV(0, 0), 'reduce_cooltime'))

        # Aura Weapon. 오라 웨폰.
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 3, 3)
        for sk in [MoonStrike, MoonStrikeLink, PierceStrike, PierceStrikeLink, ShadowStrike, FlashAssault, AdvancedSpinCutter,
                   AdvancedRollingCurve, AdvancedRollingAssulter, WindCutter, WindStrike, AdvancedStormBreak,
                   UpperSlash, AdvancedPowerStomp, FrontSlash, TurningDrive, AdvancedWheelWind, GigaCrash,
                   JumpingCrash, AdvancedEarthBreak, TwinBladeOfTime_Beta_1, TwinBladeOfTime_Alpha_1,
                   TwinBladeOfTime_Beta_2, TwinBladeOfTime_Alpha_2, TwinBladeOfTime_Beta_3, TwinBladeOfTime_Alpha_3, TwinBladeOfTime_end]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()
        AuraWeapon.add_runtime_modifier(BetaState, lambda beta: extra_damage(10) if beta.is_active() else core.CharacterModifier())  # Greatsword Mastery applied to Aura weapon during Beta. 베타시 오라 웨폰에 대검 마스터리 적용.

        # The origin of the Transcendent Lune. 초월자 륀느의 기원.
        for sk in [MoonStrike, MoonStrikeLink, PierceStrike, PierceStrikeLink, ShadowStrike, FlashAssault, AdvancedSpinCutter,
                   AdvancedRollingCurve, AdvancedRollingAssulter, WindCutter, WindStrike, AdvancedStormBreak,
                   UpperSlash, AdvancedPowerStomp, FrontSlash, TurningDrive, AdvancedWheelWind, GigaCrash,
                   JumpingCrash, AdvancedEarthBreak]:
            sk.onAfter(RhinneBlessAttack)
        RhinneBlessAttack_hit.protect_from_running()

        RhinneBless.onAfter(TimeDistortion.controller(1.0, 'reduce_cooltime_p'))
        RhinneBless.onAfter(SoulContract.controller(1.0, 'reduce_cooltime_p'))

        # Ego weapon. 에고 웨폰.
        UseEgoWeaponAlpha = core.OptionalElement(EgoWeaponAlpha.is_available, EgoWeaponAlpha)
        for sk in [MoonStrike, MoonStrikeLink, PierceStrike, PierceStrikeLink, ShadowStrike, FlashAssault, AdvancedSpinCutter, AdvancedRollingCurve, AdvancedRollingAssulter,
                   WindCutter, WindStrike, AdvancedStormBreak, ShadowFlashAlpha, ShadowFlashAlphaEnd]:
            sk.onAfter(UseEgoWeaponAlpha)
        EgoWeaponAlpha.protect_from_running()

        UseEgoWeaponBeta = core.OptionalElement(EgoWeaponBeta.is_available, EgoWeaponBeta)
        for sk in [UpperSlash, AdvancedPowerStomp, FrontSlash, TurningDrive, AdvancedWheelWind, GigaCrash,
                   JumpingCrash, AdvancedEarthBreak, ShadowFlashBeta, ShadowFlashBetaEnd]:
            sk.onAfter(UseEgoWeaponBeta)
        EgoWeaponBeta.protect_from_running()

        return(ComboHolder,

               [globalSkill.maple_heros(chtr.level, name=ZeroSkills.RhinnesProtection, combat_level=0), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                DivineForce, AlphaState, BetaState, DivineLeer, AuraWeaponBuff, AuraWeapon, RhinneBless,
                DoubleTime, TimeDistortion, TimeHolding, LimitBreak, LimitBreakCDR, LimitBreakFinal, CriticalBind,
                SoulContract] +
               [TwinBladeOfTime, ShadowFlashAlpha, ShadowFlashBeta, MirrorBreak, MirrorSpider] +
               [AdvancedStormBreakSummon, AdvancedStormBreakElectric, AdvancedEarthBreakElectric, WindCutterSummon, ThrowingWeapon] +
               [EgoWeaponAlpha, EgoWeaponBeta] +
               [ComboHolder])
