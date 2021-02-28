"""Advisor : 새틀라이트(유니온)
"""

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


class MultipleOptionWrapper(core.SummonSkillWrapper):
    """
    미사일 3회 - 개틀링 5회가 반복됨. 1530ms 간격.
    30레벨 기준 미사일 33회, 개틀링 55회.
    """
    def __init__(self, vEhc, modifier):
        self.cycle = 0
        self.vEhc = vEhc
        skill = core.SummonSkill("멀티플 옵션", 780, 1530, 0, 0, (75+2*vEhc.getV(2, 1))*1000, modifier=modifier, cooltime=200 * 1000, red=True).isV(vEhc, 2, 1)
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
        skill = core.SummonSkill("메카 캐리어", 720, 2850, 250+10*vEhc.getV(num1, num2), 4, 70000, cooltime=200*1000, red=True, modifier=modifier).isV(vEhc, num1, num2)
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
        self.jobname = "메카닉"
        self.ability_list = Ability_tool.get_ability_set('passive_level', 'boss_pdamage', 'crit')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=51)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        HiddenPiece = core.InformedCharacterModifier("히든 피스", pdamage=10)
        MechanicMastery = core.InformedCharacterModifier("메카닉 마스터리", att=20, crit=10, crit_damage=5)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝", stat_main=30, stat_sub=30)

        OverTunning = core.InformedCharacterModifier("오버 튜닝", pdamage_indep=20, crit=20, armor_ignore=30)
        MetalArmorExtreme = core.InformedCharacterModifier("메탈아머 익스트림", att=55 + passive_level)
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 1, 2)

        return [HiddenPiece, MechanicMastery, PhisicalTraining, LoadedDicePassive, MetalArmorExtreme, OverTunning]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=50)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=85+ceil(passive_level / 2))

        MetalArmorTank = core.InformedCharacterModifier("메탈아머:탱크", crit=30)

        return [WeaponConstant, Mastery, MetalArmorTank]

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('메탈아머 전탄발사(시전)', '봄버 타임'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('봄버 타임', '소울 컨트랙트'), RuleSet.BASE)
        ruleset.add_rule(ReservationRule('소울 컨트랙트', '봄버 타임'), RuleSet.BASE)
        return ruleset

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
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
        Booster = core.BuffSkill("부스터", 0, 180 * 1000, rem=True).wrap(core.BuffSkillWrapper)  # 펫버프
        WillOfLiberty = core.BuffSkill("윌 오브 리버티", 0, 60*1000, cooltime=120*1000, pdamage=10).wrap(core.BuffSkillWrapper)

        MassiveFire = core.DamageSkill("매시브 파이어", 600, 285+self.combat*6, 6+1, modifier=core.CharacterModifier(pdamage=10)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        MassiveFire2 = core.DamageSkill("매시브 파이어(2)", 0, 350+self.combat*10, 1, modifier=core.CharacterModifier(pdamage=10)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        # 로디드 데미지 고정.
        LuckyDice = core.BuffSkill("로디드 다이스", 0, 180*1000, pdamage=20+10/6+10/6*(5/6+1/11)*(10*(5+passive_level)*0.01)).isV(vEhc, 1, 2).wrap(core.BuffSkillWrapper)

        # 로봇들 :: 로봇당 총뎀6%, 어빌리티 적용 시 7%
        Robolauncher = core.SummonSkill("로봇 런처:RM7", 630, 1000, 250+135+passive_level*4, 1, 60*1000*ROBOT_SUMMON_REMAIN, modifier=ROBOT_MASTERY).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)
        RobolauncherFinal = core.DamageSkill("로봇 런처:RM7(폭발)", 0, 400+135+passive_level*4, 1, modifier=ROBOT_MASTERY, cooltime=-1).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        RobolauncherBuff = core.BuffSkill("로봇 런처:RM7(버프)", 0, 60*1000*ROBOT_SUMMON_REMAIN, cooltime=-1, pdamage=ROBOT_BUFF).wrap(core.BuffSkillWrapper)

        # 마그네틱 필드는 로봇 마스터리, 하이퍼를 제외한 소환수 지속시간 영향을 받지 않음. 설치 완료 후부터 쿨타임이 돔.
        MagneticFieldInstall = core.DamageSkill("마그네틱 필드(설치)", 630, 0, 0, cooltime=-1).wrap(core.DamageSkillWrapper)
        MagneticField = core.SummonSkill("마그네틱 필드", 0, 990, 200, 1, 60*1000*ROBOT_SUMMON_REMAIN+10000, cooltime=160*0.75*1000, red=True, modifier=ROBOT_MASTERY).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)
        MagneticFieldBuff = core.BuffSkill("마그네틱 필드(버프)", 0, 60*1000*ROBOT_SUMMON_REMAIN+10000, cooltime=-1, pdamage=ROBOT_BUFF).wrap(core.BuffSkillWrapper)

        SupportWaver = core.SummonSkill("서포트 웨이버", 630, 80000*ROBOT_SUMMON_REMAIN, 0, 0, 80*1000*ROBOT_SUMMON_REMAIN).wrap(core.SummonSkillWrapper)
        SupportWaverBuff = core.BuffSkill("서포트 웨이버(버프)", 0, 80*1000*ROBOT_SUMMON_REMAIN, pdamage_indep=10+5+ceil(passive_level/3), pdamage=ROBOT_BUFF, armor_ignore=10, cooltime=-1).wrap(core.BuffSkillWrapper)
        SupportWaverFinal = core.DamageSkill("서포트 웨이버(폭발)", 0, 1100+passive_level*20, 1, modifier=ROBOT_MASTERY, cooltime=-1).wrap(core.DamageSkillWrapper)

        RoboFactory = core.SummonSkill("로봇 팩토리", 630, 3000, 500+self.combat*5, 3, 30*1000*ROBOT_SUMMON_REMAIN, cooltime=60*1000, red=True, modifier=ROBOT_MASTERY).setV(vEhc, 5, 2, False).wrap(core.SummonSkillWrapper)
        RoboFactoryBuff = core.BuffSkill("로봇 팩토리(버프)", 0, 30*1000*ROBOT_SUMMON_REMAIN, cooltime=-1, pdamage=ROBOT_BUFF).wrap(core.BuffSkillWrapper)
        RoboFactoryFinal = core.DamageSkill("로봇 팩토리(폭발)", 0, 1000+self.combat*10, 1, modifier=ROBOT_MASTERY).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)

        OpenGateBuff = core.BuffSkill("오픈 게이트(버프)", 630*2+600, 300*1000*ROBOT_SUMMON_REMAIN, pdamage=ROBOT_BUFF).wrap(core.BuffSkillWrapper)  # 동위치 설치불가, 매시브 1회 손실을 딜레이로 보정

        BomberTime = core.BuffSkill("봄버 타임", 900, 10*1000, cooltime=100*1000).wrap(core.BuffSkillWrapper)
        DistortionField = core.SummonSkill("디스토션 필드", 690, 4000/15, 350, 2, 4000-1, cooltime=8000).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper)

        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        RegistanceLineInfantry = resistance.ResistanceLineInfantryWrapper(vEhc, 3, 3)

        MultipleOption = MultipleOptionWrapper(vEhc, ROBOT_MASTERY)
        MultipleOptionBuff = core.BuffSkill("멀티플 옵션(버프)", 0, MultipleOption.skill.remain, cooltime=-1, pdamage=ROBOT_BUFF).wrap(core.BuffSkillWrapper)

        MicroMissle = core.DamageSkill("마이크로 미사일 컨테이너", 540, 375+17*vEhc.getV(0, 0), (30 + vEhc.getV(0, 0) // 3) * 5, cooltime=25000, red=True).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        BusterCall_ = core.DamageSkill("메탈아머 전탄발사", 8670/49, 400+16*vEhc.getV(4, 4), 11).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)
        BusterCallInit = core.DamageSkill("메탈아머 전탄발사(시전)", 1330, 0, 0, cooltime=200*1000, red=True).wrap(core.DamageSkillWrapper)  # 선딜레이
        BusterCallBuff = core.BuffSkill("메탈아머 전탄발사(버프)", 0, 8670, cooltime=-1).isV(vEhc, 4, 4).wrap(core.BuffSkillWrapper)
        BusterCallEnd = core.DamageSkill("메탈아머 전탄발사(하차)", 1800, 0, 0).wrap(core.DamageSkillWrapper)
        BusterCallPenalty = core.BuffSkill("메탈아머 전탄발사(페널티)", 0, 2000, cooltime=-1).wrap(core.BuffSkillWrapper)

        MechCarrier = MechCarrierWrapper(vEhc, 0, 0, ROBOT_MASTERY)
        MechCarrierBuff = core.BuffSkill("메카 캐리어(버프)", 0, MechCarrier.skill.remain, cooltime=-1, pdamage=ROBOT_BUFF).wrap(core.BuffSkillWrapper)

        MassiveFire.onAfter(MassiveFire2)
        #### 호밍 미사일 정의 ####
        HommingMissle_ = core.DamageSkill("호밍 미사일", 0, 500*0.6, 9+passive_level).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        HommingMissle_B = core.DamageSkill("호밍 미사일(봄버)", 0, 500*0.6, 9+passive_level+6).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        HommingMissle_Bu = core.DamageSkill("호밍 미사일(전탄)", 0, 500, 9+passive_level+7).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        HommingMissle_B_Bu = core.DamageSkill("호밍 미사일(봄버)(전탄)", 0, 500, 9+passive_level+6+7).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)

        HommingMissleHolder = core.SummonSkill("호밍 미사일(더미)", 0, 660, 0, 0, 99999 * 100000).wrap(core.SummonSkillWrapper)

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
