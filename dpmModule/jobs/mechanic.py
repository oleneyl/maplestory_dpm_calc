"""Advisor : 새틀라이트(유니온)
"""
from .globalSkill import GlobalSkills, BUFF, EXPLOSION, HOLDER, CAST, ENDING
from .jobbranch.pirates import PirateSkills
from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule, ReservationRule
from . import globalSkill
from .jobclass import resistance
from .jobbranch import pirates
from . import jobutils
from math import ceil
from typing import Any, Dict

from localization.utilities import translator
_ = translator.gettext

# English skill information for Mechanic here https://maplestory.fandom.com/wiki/Mechanic/Skills
class MechanicSkills:
    # Link Skill
    SpiritofFreedom = _("스피릿 오브 프리덤")  # "Spirit of Freedom"
    # Beginner
    MechanicDash = _("메카닉 대쉬")  # "Mechanic Dash"
    HiddenPeace = _("히든 피스")  # "Hidden Peace"
    SecretAssembly = _("비밀광장 긴급집결")  # "Secret Assembly"
    # 1st Job
    HumanoidMech = _("메탈아머:휴먼")  # "Humanoid Mech"
    GatlingGun = _("개틀링 샷")  # "Gatling Gun"
    ME07Drillhands = _("드릴 러쉬")  # "ME-07 Drillhands"
    RocketBooster = _("로켓 부스터")  # "Rocket Booster"
    # 2nd Job
    HeavyGatlingGun = _("어드밴스드 개틀링 샷")  # "Heavy Gatling Gun"
    HomingBeacon = _("호밍 미사일")  # "Homing Beacon"
    MechanicMastery = _("메카닉 마스터리")  # "Mechanic Mastery"
    MechanicRage = _("메카닉 부스터")  # "Mechanic Rage"
    OpenPortalGX9 = _("오픈 게이트:GX-9")  # "Open Portal: GX-9"
    PerfectArmor = _("퍼펙트 아머")  # "Perfect Armor"
    RoboLauncherRM7 = _("로봇 런처:RM7")  # "Robo Launcher RM7"
    PhysicalTraining = _("피지컬 트레이닝")  # "Physical Training"
    # 3rd Job
    TankMech = _("메탈아머:탱크")  # "Tank Mech"
    HeavySalvo = _("매시브 파이어:SPLASH")  # "Heavy Salvo"
    APSalvo = _("매시브 파이어:IRON")  # "AP Salvo"
    SupportUnitHEX = _("서포트 웨이버:H-EX")  # "Support Unit: H-EX"
    PunchLauncher = _("로켓 펀치")  # "Punch Launcher"
    RocknShock = _("마그네틱 필드")  # "Rock 'n Shock"
    AdvancedHomingBeacon = _("어드밴스드 호밍 미사일")  # "Advanced Homing Beacon"
    MechanizedDefenseSystem = _("메카닉 디펜스 시스템")  # "Mechanized Defense System"
    BattleProgram = _("전투 프로그램 셋업")  # "Battle Program"
    RolloftheDice = _("럭키 다이스")  # "Roll of the Dice"
    Overclock = _("오버 튜닝")  # "Overclock"
    # 4th Job
    HeavySalvoPlus = _("매시브 파이어:SPLASH-F")  # "Heavy Salvo Plus"
    APSalvoPlus = _("매시브 파이어:IRON-B")  # "AP Salvo Plus"
    ExtremeMech = _("메탈아머 익스트림")  # "Extreme Mech"
    GiantRobotSG88 = _("워머신:타이탄")  # "Giant Robot SG-88"
    EnhancedSupportUnit = _("서포트 웨이버 강화")  # "Enhanced Support Unit"
    BotsnTots = _("로봇 팩토리:RM1")  # "Bots 'n Tots"
    RobotMastery = _("로봇 마스터리")  # "Robot Mastery"
    HomingBeaconResearch = _("호밍 미사일 시스템 연구")  # "Homing Beacon Research"
    DoubleDown = _("더블 럭키 다이스")  # "Double Down"
    MechAlloyResearch = _("메탈아머 합금 연구")  # "Mech Alloy Research"
    # Hypers
    DistortionBomb = _("디스토션 필드")  # "Distortion Bomb"
    ForLiberty = _("윌 오브 리버티")  # "For Liberty"
    FullSpread = _("봄버 타임")  # "Full Spread"
    # 5th Job
    DoomsdayDevice = _("멀티플 옵션:M-FL")  # "Doomsday Device"
    MobileMissileBattery = _("마이크로 미사일 컨테이너")  # "Mobile Missile Battery"
    FullMetalBarrage = _("메탈아머 전탄발사")  # "Full Metal Barrage"
    MechaCarrier = _("메카 캐리어")  # "Mecha Carrier"


# Skill name modifiers for Mechanic
INSTALL = _("설치")
PENALTY = _("페널티")
BOMBER = _("봄버")
SHOT = _("전탄")

class MultipleOptionWrapper(core.SummonSkillWrapper):
    """
    3 missiles-5 gatlings repeated. 1530 ms interval.
    At level 30, 33 missiles, 55 Gatling.

    미사일 3회 - 개틀링 5회가 반복됨. 1530ms 간격.
    30레벨 기준 미사일 33회, 개틀링 55회.
    """
    def __init__(self, vEhc, modifier):
        self.cycle = 0
        self.vEhc = vEhc
        skill = core.SummonSkill(MechanicSkills.DoomsdayDevice, 780, 1530, 0, 0, (75+2*vEhc.getV(2, 1))*1000, modifier=modifier, cooltime=200 * 1000, red=True).isV(vEhc, 2, 1)
        super(MultipleOptionWrapper, self).__init__(skill)

    def _useTick(self):
        result = super(MultipleOptionWrapper, self)._useTick()
        self.cycle = (self.cycle + 1) % 8
        return result

    def get_damage(self) -> float:
        if self.cycle < 3:
            return 350+10*self.vEhc.getV(2, 1)
        else:
            return 200+8*self.vEhc.getV(2, 1)

    def get_hit(self) -> float:
        if self.cycle < 3:
            return 8
        else:
            return 6


class MechCarrierWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2, modifier):
        skill = core.SummonSkill(MechanicSkills.MechaCarrier, 720, 2850, 250+10*vEhc.getV(num1, num2), 4, 70000, cooltime=200*1000, red=True, modifier=modifier).isV(vEhc, num1, num2)
        super(MechCarrierWrapper, self).__init__(skill)
        self.interceptor = 9

    def _use(self, skill_modifier):
        self.interceptor = 9
        return super(MechCarrierWrapper, self)._use(skill_modifier)

    def _useTick(self):
        result = super(MechCarrierWrapper, self)._useTick()
        self.interceptor = min(self.interceptor + 1, 16)
        return result

    def get_hit(self):
        return self.skill.hit * self.interceptor

    def get_delay(self):
        return self.skill.delay + self.interceptor * 120


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 14
        self.jobtype = "DEX"
        self.jobname = _("메카닉")
        self.ability_list = Ability_tool.get_ability_set('passive_level', 'boss_pdamage', 'crit')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=51)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        HiddenPiece = core.InformedCharacterModifier(MechanicSkills.HiddenPeace, pdamage=10)
        MechanicMastery = core.InformedCharacterModifier(MechanicSkills.MechanicMastery, att=20, crit=10, crit_damage=5)
        PhisicalTraining = core.InformedCharacterModifier(MechanicSkills.PhysicalTraining, stat_main=30, stat_sub=30)

        OverTunning = core.InformedCharacterModifier(MechanicSkills.Overclock, pdamage_indep=20, crit=20, armor_ignore=30)
        MetalArmorExtreme = core.InformedCharacterModifier(MechanicSkills.ExtremeMech, att=55 + passive_level)
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 1, 2)

        return [HiddenPiece, MechanicMastery, PhisicalTraining, LoadedDicePassive, MetalArmorExtreme, OverTunning]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep=50)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=85+ceil(passive_level / 2))

        MetalArmorTank = core.InformedCharacterModifier(MechanicSkills.TankMech, crit=30)

        return [WeaponConstant, Mastery, MetalArmorTank]

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule(f"{MechanicSkills.FullMetalBarrage}({CAST})", MechanicSkills.FullSpread), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(MechanicSkills.FullSpread, GlobalSkills.TermsAndConditions), RuleSet.BASE)
        ruleset.add_rule(ReservationRule(GlobalSkills.TermsAndConditions, MechanicSkills.FullSpread), RuleSet.BASE)
        return ruleset

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Nose sequence:
        Massive-Homing-Distortion-Magnetic Field-RM7-RM1

        Hyper:
        Massive Fire-Reinforce, Bonus Attack
        Magnetic Field-Persist, Cool Time Reduce
        Support Waver-Party Reinforcement

        코강 순서:
        매시브-호밍-디스토션-마그네틱필드-RM7-RM1

        하이퍼:
        매시브 파이어-리인포스, 보너스 어택
        마그네틱 필드-퍼시스트, 쿨타임 리듀스
        서포트 웨이버-파티 리인포스
        '''
        # Constants
        passive_level = self.combat + chtr.get_base_modifier().passive_level
        ROBOT_SUMMON_REMAIN = 1 + chtr.get_base_modifier().summon_rem / 100 + 0.4 + passive_level * 0.01
        ROBOT_MASTERY = core.CharacterModifier(pdamage_indep=105 + passive_level * 3)
        ROBOT_BUFF = 6 + ceil(passive_level / 5)

        # Buff skills
        Booster = core.BuffSkill(MechanicSkills.MechanicRage, 0, 180 * 1000, rem=True).wrap(core.BuffSkillWrapper)  # 펫버프
        WillOfLiberty = core.BuffSkill(MechanicSkills.ForLiberty, 0, 60*1000, cooltime=120*1000, pdamage=10).wrap(core.BuffSkillWrapper)

        MassiveFire = core.DamageSkill(MechanicSkills.APSalvoPlus, 600, 285+self.combat*6, 6+1, modifier=core.CharacterModifier(pdamage=10)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        MassiveFire2 = core.DamageSkill(f"{MechanicSkills.APSalvoPlus}(2)", 0, 350+self.combat*10, 1, modifier=core.CharacterModifier(pdamage=10)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        # Fixed loaded damage. 로디드 데미지 고정.
        LuckyDice = core.BuffSkill(PirateSkills.LoadedDice, 0, 180*1000, pdamage=20+10/6+10/6*(5/6+1/11)*(10*(5+passive_level)*0.01)).isV(vEhc, 1, 2).wrap(core.BuffSkillWrapper)

        # Robots :: Total Dem 6% per robot, 7% when Ability is applied. 로봇들 :: 로봇당 총뎀6%, 어빌리티 적용 시 7%.
        Robolauncher = core.SummonSkill(MechanicSkills.RoboLauncherRM7, 630, 1000, 250+135+passive_level*4, 1, 60*1000*ROBOT_SUMMON_REMAIN, modifier=ROBOT_MASTERY).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)
        RobolauncherFinal = core.DamageSkill(f"{MechanicSkills.RoboLauncherRM7}({EXPLOSION})", 0, 400+135+passive_level*4, 1, modifier=ROBOT_MASTERY, cooltime=-1).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        RobolauncherBuff = core.BuffSkill(f"{MechanicSkills.RoboLauncherRM7}({BUFF})", 0, 60*1000*ROBOT_SUMMON_REMAIN, cooltime=-1, pdamage=ROBOT_BUFF).wrap(core.BuffSkillWrapper)

        # Magnetic field is not affected by the duration of minions except Robot Mastery and Hyper. Cooldown is dome after installation is complete. 마그네틱 필드는 로봇 마스터리, 하이퍼를 제외한 소환수 지속시간 영향을 받지 않음. 설치 완료 후부터 쿨타임이 돔.
        MagneticFieldInstall = core.DamageSkill(f"{MechanicSkills.RocknShock}({INSTALL})", 630, 0, 0, cooltime=-1).wrap(core.DamageSkillWrapper)
        MagneticField = core.SummonSkill(MechanicSkills.RocknShock, 0, 990, 200, 1, 60*1000*ROBOT_SUMMON_REMAIN+10000, cooltime=160*0.75*1000, red=True, modifier=ROBOT_MASTERY).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)
        MagneticFieldBuff = core.BuffSkill(f"{MechanicSkills.RocknShock}({BUFF})", 0, 60*1000*ROBOT_SUMMON_REMAIN+10000, cooltime=-1, pdamage=ROBOT_BUFF).wrap(core.BuffSkillWrapper)

        SupportWaver = core.SummonSkill(MechanicSkills.EnhancedSupportUnit, 630, 80000*ROBOT_SUMMON_REMAIN, 0, 0, 80*1000*ROBOT_SUMMON_REMAIN).wrap(core.SummonSkillWrapper)
        SupportWaverBuff = core.BuffSkill(f"{MechanicSkills.EnhancedSupportUnit}({BUFF})", 0, 80*1000*ROBOT_SUMMON_REMAIN, pdamage_indep=10+5+ceil(passive_level/3), pdamage=ROBOT_BUFF, armor_ignore=10, cooltime=-1).wrap(core.BuffSkillWrapper)
        SupportWaverFinal = core.DamageSkill(f"{MechanicSkills.EnhancedSupportUnit}({EXPLOSION})", 0, 1100+passive_level*20, 1, modifier=ROBOT_MASTERY, cooltime=-1).wrap(core.DamageSkillWrapper)

        RoboFactory = core.SummonSkill(MechanicSkills.BotsnTots, 630, 3000, 500+self.combat*5, 3, 30*1000*ROBOT_SUMMON_REMAIN, cooltime=60*1000, red=True, modifier=ROBOT_MASTERY).setV(vEhc, 5, 2, False).wrap(core.SummonSkillWrapper)
        RoboFactoryBuff = core.BuffSkill(f"{MechanicSkills.BotsnTots}({BUFF})", 0, 30*1000*ROBOT_SUMMON_REMAIN, cooltime=-1, pdamage=ROBOT_BUFF).wrap(core.BuffSkillWrapper)
        RoboFactoryFinal = core.DamageSkill(f"{MechanicSkills.BotsnTots}({EXPLOSION})", 0, 1000+self.combat*10, 1, modifier=ROBOT_MASTERY).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)

        OpenGateBuff = core.BuffSkill(f"{MechanicSkills.OpenPortalGX9}({BUFF})", 630*2+600, 300*1000*ROBOT_SUMMON_REMAIN, pdamage=ROBOT_BUFF).wrap(core.BuffSkillWrapper)  # Cannot be installed in the same position, and compensates for the loss of one mass by delay. 동위치 설치불가, 매시브 1회 손실을 딜레이로 보정.

        BomberTime = core.BuffSkill(MechanicSkills.FullSpread, 900, 10*1000, cooltime=100*1000).wrap(core.BuffSkillWrapper)
        DistortionField = core.SummonSkill(MechanicSkills.DistortionBomb, 690, 4000/15, 350, 2, 4000-1, cooltime=8000).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper)

        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        RegistanceLineInfantry = resistance.ResistanceLineInfantryWrapper(vEhc, 3, 3)

        MultipleOption = MultipleOptionWrapper(vEhc, ROBOT_MASTERY)
        MultipleOptionBuff = core.BuffSkill(f"{MechanicSkills.DoomsdayDevice}({BUFF})", 0, MultipleOption.skill.remain, cooltime=-1, pdamage=ROBOT_BUFF).wrap(core.BuffSkillWrapper)

        MicroMissle = core.DamageSkill(MechanicSkills.MobileMissileBattery, 540, 375+17*vEhc.getV(0, 0), (30 + vEhc.getV(0, 0) // 3) * 5, cooltime=25000, red=True).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        BusterCall_ = core.DamageSkill(MechanicSkills.FullMetalBarrage, 8670/49, 400+16*vEhc.getV(4, 4), 11).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)
        BusterCallInit = core.DamageSkill(f"{MechanicSkills.FullMetalBarrage}({CAST})", 1330, 0, 0, cooltime=200*1000, red=True).wrap(core.DamageSkillWrapper)  # Sun delay. 선딜레이.
        BusterCallBuff = core.BuffSkill(f"{MechanicSkills.FullMetalBarrage}({BUFF})", 0, 8670, cooltime=-1).isV(vEhc, 4, 4).wrap(core.BuffSkillWrapper)
        BusterCallEnd = core.DamageSkill(f"{MechanicSkills.FullMetalBarrage}({ENDING})", 1800, 0, 0).wrap(core.DamageSkillWrapper)
        BusterCallPenalty = core.BuffSkill(f"{MechanicSkills.FullMetalBarrage}({PENALTY})", 0, 2000, cooltime=-1).wrap(core.BuffSkillWrapper)

        MechCarrier = MechCarrierWrapper(vEhc, 0, 0, ROBOT_MASTERY)
        MechCarrierBuff = core.BuffSkill(f"{MechanicSkills.MechaCarrier}({BUFF})", 0, MechCarrier.skill.remain, cooltime=-1, pdamage=ROBOT_BUFF).wrap(core.BuffSkillWrapper)

        MassiveFire.onAfter(MassiveFire2)
        #### Homing Missile Definition. 호밍 미사일 정의 ####
        HommingMissle_ = core.DamageSkill(MechanicSkills.HomingBeacon, 0, 500*0.6, 9+passive_level).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        HommingMissle_B = core.DamageSkill(f"{MechanicSkills.HomingBeacon}({BOMBER})", 0, 500*0.6, 9+passive_level+6).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        HommingMissle_Bu = core.DamageSkill(f"{MechanicSkills.HomingBeacon}({SHOT})", 0, 500, 9+passive_level+7).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        HommingMissle_B_Bu = core.DamageSkill(f"{MechanicSkills.HomingBeacon}({BOMBER}{SHOT})", 0, 500, 9+passive_level+6+7).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)

        HommingMissleHolder = core.SummonSkill(f"{MechanicSkills.HomingBeacon}({HOLDER})", 0, 660, 0, 0, 99999 * 100000).wrap(core.SummonSkillWrapper)

        MultipleOption.onAfter(MultipleOptionBuff)
        MechCarrier.onAfter(MechCarrierBuff)

        IsBuster_B = core.OptionalElement(BusterCallBuff.is_active, HommingMissle_B_Bu, HommingMissle_B)
        IsBuster = core.OptionalElement(BusterCallBuff.is_active, HommingMissle_Bu, HommingMissle_)
        IsBomber = core.OptionalElement(BomberTime.is_active, IsBuster_B, IsBuster)
        HommingMissle = core.OptionalElement(BusterCallPenalty.is_not_active, IsBomber)

        HommingMissleHolder.onTick(HommingMissle)

        BusterCall = core.RepeatElement(BusterCall_, 49)
        BusterCall.onAfter(BusterCallEnd)
        BusterCall.onAfter(BusterCallPenalty)
        BusterCallInit.onAfter(BusterCallBuff)
        BusterCallInit.onAfter(BusterCall)

        Robolauncher.onEventEnd(RobolauncherFinal)
        Robolauncher.onAfter(RobolauncherBuff)

        MagneticField.onBefore(MagneticFieldInstall)
        MagneticField.onAfter(MagneticFieldBuff)

        SupportWaver.onEventEnd(SupportWaverFinal)
        SupportWaver.onAfter(SupportWaverBuff)

        RoboFactory.onEventEnd(RoboFactoryFinal)
        RoboFactory.onAfter(RoboFactoryBuff)

        return (
            MassiveFire,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                Booster,
                LuckyDice,
                SupportWaverBuff,
                RobolauncherBuff,
                MagneticFieldBuff,
                RoboFactoryBuff,
                OpenGateBuff,
                MultipleOptionBuff,
                MechCarrierBuff,
                WillOfLiberty,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                BomberTime,
                Overdrive,
                globalSkill.soul_contract()
            ] +
            [MicroMissle, MechCarrier, BusterCallInit] +
            [
                HommingMissleHolder,
                RegistanceLineInfantry,
                SupportWaver,
                MagneticField,
                Robolauncher,
                RoboFactory,
                DistortionField,
                MultipleOption,
                MirrorBreak,
                MirrorSpider
            ] +
            [BusterCallBuff, BusterCallPenalty] +
            [MassiveFire]
        )
