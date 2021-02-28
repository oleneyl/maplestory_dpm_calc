from dpmModule.jobs.jobbranch.pirates import PirateSkills

from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobclass import heroes
from .jobbranch import pirates
from . import jobutils
from ..execution.rules import RuleSet, InactiveRule, ConditionRule
from math import ceil
from typing import Any, Dict

import gettext
_ = gettext.gettext

# English skill information for Shade here https://maplestory.fandom.com/wiki/Shade/Skills
class ShadeSkills:
    # Link Skill
    CloseCall = _("구사 일생")  # "Close Call"
    # Beginner
    FoxTrot = _("축지")  # "Fox Trot"
    SpiritBond1 = _("정령 결속 1식")  # "Spirit Bond 1"
    SpiritAffinity = _("정령친화")  # "Spirit Affinity"
    # 1st Job
    SwiftStrike = _("메가 펀치")  # "Swift Strike"
    # FlashFist = _("")  # "Flash Fist"
    VulpesLeap = _("도약")  # "Vulpes Leap"
    CosmicBalance = _("건곤 일체")  # "Cosmic Balance"
    # 2nd Job
    GroundPound = _("파력권")  # "Ground Pound"
    BladeImpdDownwardSlash = _("파쇄철조-반")  # "Blade Imp - Downward Slash"
    BladeImpForwardSlash = _("파쇄철조-前")  # "Blade Imp - Forward Slash"
    BackStep = _("후방 이동")  # "Back Step"
    KnuckleMastery = _("너클 마스터리")  # "Knuckle Mastery"
    SpiritBond2 = _("정령 결속 2식")  # "Spirit Bond 2"
    StrengthTraining = _("피지컬 트레이닝")  # "Strength Training"
    FoxSpirits = _("여우령")  # "Fox Spirits"
    FoxSpiritMastery = _("여우령 숙련")  # "Fox Spirit Mastery"
    # 3rd Job
    ShockwavePunch = _("통백권 충격파")  # "Shockwave Punch"
    BladeImpSpinSlash = _("파쇄철조-회")  # "Blade Imp - Spin Slash"
    SpiritFrenzy = _("소혼 장막")  # "Spirit Frenzy"
    SpiritTrap = _("속박술")  # "Spirit Trap"
    SpiritBond3 = _("정령 결속 3식")  # "Spirit Bond 3"
    # HarmoniousDefense = _("")  # "Harmonious Defense"
    SummonOtherSpirit = _("환령 강신")  # "Summon Other Spirit"
    Weaken = _("약화")  # "Weaken"
    # 4th Job
    BombPunch = _("폭류권")  # "Bomb Punch"
    SpiritClaw = _("귀참")  # "Spirit Claw"
    DeathMark = _("사혼 각인")  # "Death Mark"
    SoulSplitter = _("분혼 격참")  # "Soul Splitter"
    SpiritWard = _("소혼 결계")  # "Spirit Ward"
    FireFoxSpiritMastery = _("불여우령")  # "Fire Fox Spirit Mastery"
    SpiritBond4 = _("정령 결속 4식")  # "Spirit Bond 4"
    HighQualityKnuckleMastery = _("고급 너클 숙련")  # "High Quality Knuckle Mastery"
    CriticalInsight = _("약점 간파")  # "Critical Insight"
    # Hypers
    SpiritIncarnation = _("정령의 화신")  # "Spirit Incarnation"
    HeroicMemories = _("히어로즈 오쓰")  # "Heroic Memories"
    SpiritBondMax = _("정령 결속 극대화")  # "Spirit Bond Max"
    # 5th Job
    SpiritFlow = _("정령 집속")  # "Spirit Flow"
    Spiritgate = _("귀문진")  # "Spiritgate"
    TrueSpiritClaw = _("진 귀참")  # "True Spirit Claw"
    SmashingMultipunch = _("파쇄 연권")  # "Smashing Multipunch"


class SoulTrapStackWrapper(core.StackSkillWrapper):
    def __init__(self, skill):
        self.debuffQueue = []
        self.currentTime = 0
        self.DEBUF_PERSISTENCE_TIME = 8000 # 8000ms
        super(SoulTrapStackWrapper, self).__init__(skill, 10)

    def _add_debuff(self):
        # Add debuff, keep up to _max(10). 디버프 추가, 최대 _max(10)개로 유지.
        self.debuffQueue = ([self.currentTime] + self.debuffQueue)[:self._max]
        self.stack = len(self.debuffQueue)
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, _("{} 디버프 변경").format(ShadeSkills.Spiritgate), spec = 'graph control')

    def add_debuff(self):
        return core.TaskHolder(core.Task(self, self._add_debuff), name=_("{} 디버프 추가").format(ShadeSkills.Spiritgate))

    def spend_time(self, time):
        self.currentTime += time
        # Removes debuff over duration. 지속시간이 끝난 디버프 제거.
        self.debuffQueue = [x for x in self.debuffQueue if x + self.DEBUF_PERSISTENCE_TIME > self.currentTime]
        self.stack = len(self.debuffQueue)
        super(SoulTrapStackWrapper, self).spend_time(time)

    def get_modifier(self):
        return core.CharacterModifier(crit = 8 * self.stack, crit_damage = 1*self.stack)


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "STR"
        self.jobname = _("은월")
        self.vEnhanceNum = 15
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'reuse', 'mess')
        self.preEmptiveSkills = 2
        
    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(InactiveRule(ShadeSkills.BladeImpSpinSlash, ShadeSkills.BladeImpdDownwardSlash), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(_("{}(시전)").format(ShadeSkills.SpiritFrenzy), ShadeSkills.TrueSpiritClaw, lambda x: not x.is_available()), RuleSet.BASE)
        # ruleset.add_rule(ReservationRule(GlobalSkills.TermsAndConditions, ShadeSkills.SpiritFlow), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=96, armor_ignore=20, crit_damage=5)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        PhisicalTraining = core.InformedCharacterModifier(ShadeSkills.StrengthTraining,stat_main = 60)
        SpiritLink_3 = core.InformedCharacterModifier(ShadeSkills.SpiritBond3,att = 20, pdamage = 20)

        SpiritLink_4 = core.InformedCharacterModifier(ShadeSkills.SpiritBond4,armor_ignore = 30 + passive_level, boss_pdamage = 30 + passive_level, pdamage_indep = 15 + passive_level // 3)
        AdvancedNuckleMastery = core.InformedCharacterModifier(ShadeSkills.HighQualityKnuckleMastery,crit_damage = 20 + 2 * ceil(passive_level/3), pdamage_indep = 10 + ceil(passive_level/3))
        
        WeaknessFinding = core.InformedCharacterModifier(ShadeSkills.CriticalInsight,crit = 25 + ceil(passive_level/2))

        LoadedDicePassive = core.InformedCharacterModifier(_('{}(패시브)').format(PirateSkills.LoadedDice), att = vEhc.getV(4,4) + 10)

        return [PhisicalTraining, SpiritLink_3, 
                SpiritLink_4, AdvancedNuckleMastery, WeaknessFinding, LoadedDicePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier(_("무기상수"),pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90+2 * (passive_level // 3))
        Weakness = core.InformedCharacterModifier(ShadeSkills.Weaken,pdamage = 20)  # It is debuff, but it is always activated. 디버프지만 상시발동가정.

        # Weakness Detection: Triggers when HP is below (50 + passive_level)%. 약점 간파: 체력 (50 + passive_level)% 이하일 때 발동.

        WEAKNESS_BONUS = options.get("hp_rate", False)

        WeaknessFinding_Bonus = core.InformedCharacterModifier(_("{}(보너스)").format(ShadeSkills.CriticalInsight), crit_damage = (25+passive_level//3) * WEAKNESS_BONUS)
        
        return [WeaponConstant, Mastery, Weakness, WeaknessFinding_Bonus]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        ----Information---
        Hyper: 3 returnees, reinforcement of the Explosive Zone, Fox Spirit summon rate +10%
        Small Wedding Curtain 180ms
        Attack every 1280ms

        V Enhancement: (15)
        Return, Explosive Zone, Fox Spirit
        Separation, small marriage curtain

        100% maintenance of cleanliness

        Elemental Focus: Random skill activation once, keydown lasts 3 seconds,
                   Elemental attack is activated every 2 seconds 1742 Perdem assumes one attack. Two fox spirits ejected
        Small Spirit Veil: Use Ranghorn Veil every 60 seconds. If you can use Jin Gwicham, use it first and use the small wedding curtain
        Guidance: Do not use wall cans
        Separation Fear: Assumed as a mobile boss

        ----정보---
        하이퍼 : 귀참 3개, 폭류권 리인포스, 여우령 소환확률 +10%
        소혼장막 180ms
        귀문진 1280ms마다 공격

        V강화 : (15개)
        귀참, 폭류권, 여우령
        분격, 소혼장막

        정결극 유지 100%

        정령 집속 : 무작위 스킬 1회 발동, 키다운은 3초 지속,
                   정령 공격은 2초마다 발동 1742퍼뎀으로 1회공격 가정. 여우령 2개 사출
        소혼 장막: 60초마다 랑혼장막 사용. 진 귀참을 쓸 수 있으면 먼저 사용하고 소혼장막 사용
        귀참: 벽캔은 사용하지 않음
        분혼 격참: 이동형 보스로 가정
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        SOULENHANCEREM = 100

        ######   Skill   ######

        #Buff skills

        FoxSoul = core.DamageSkill(ShadeSkills.FoxSpirits, 0, 200 + 5 * passive_level, 3 * (25 + 10 + passive_level // 2) * 0.01).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        FoxSoul_100 = core.DamageSkill(f"{ShadeSkills.FoxSpirits}(100%)", 0, 200 + 5 * passive_level, 3).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        SoulAttack = core.DamageSkill(ShadeSkills.SpiritClaw, 630, 265 + 5 * self.combat, 12 + 1, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        DoubleBodyAttack = core.DamageSkill(_("{}(공격)").format(ShadeSkills.SoulSplitter), 0, 2000 + 40*self.combat, 1).wrap(core.DamageSkillWrapper)
        DoubleBody = core.BuffSkill(ShadeSkills.SoulSplitter, 810, 10000, cooltime = (180-6*self.combat) * 1000, red = True, pdamage_indep = 20).wrap(core.BuffSkillWrapper)
        DoubleBodyRegistance = core.BuffSkill(_("{}(저항)").format(ShadeSkills.SoulSplitter), 0, 90000, cooltime = -1).wrap(core.BuffSkillWrapper)

        # Hyperkill. 하이퍼스킬.
        # 100% cleanliness retention rate. 정결극 유지율 100%.
        EnhanceSpiritLink = core.BuffSkill(ShadeSkills.SpiritBondMax, 0, 120000 * (SOULENHANCEREM/100), cooltime = 120*1000, boss_pdamage = 20, pdamage = 35, att = 20, armor_ignore = 20).wrap(core.BuffSkillWrapper)
        EnhanceSpiritLinkSummon_S = core.SummonSkill(_("{}(간간 수월래)").format(ShadeSkills.SpiritBondMax), 0, 3000, 275, 3, 120000 * (SOULENHANCEREM/100), cooltime = -1).wrap(core.SummonSkillWrapper)
        EnhanceSpiritLinkSummon_J_Init = core.SummonSkill(_("{}({})(시전)").format(ShadeSkills.SpiritBondMax, ShadeSkills.SpiritFrenzy), 0, 60 * 1000, 0, 0, 120000 * (SOULENHANCEREM/100), cooltime = -1).wrap(core.SummonSkillWrapper)
        EnhanceSpiritLinkSummon_J = core.SummonSkill(f"{ShadeSkills.SpiritBondMax}({ShadeSkills.SpiritFrenzy})", 0, 150, 150, 1, 4800, cooltime = -1).wrap(core.SummonSkillWrapper)

        # Unconditionally used with Rang (700% of final damage). 랑과 무조건 함께 사용 (최종뎀 700%).
        SpiritFrenzy = core.DamageSkill(_("{}(시전)").format(ShadeSkills.SpiritFrenzy), 0, 0, 0, cooltime=10*1000 + 10080).wrap(core.DamageSkillWrapper)
        SpiritFrenzy_Tick = core.DamageSkill(ShadeSkills.SpiritFrenzy, 180, 45, 5, cooltime = -1, modifier=core.CharacterModifier(pdamage_indep = 700)).setV(vEhc, 3, 3, False).wrap(core.DamageSkillWrapper)

        LuckyDice = core.BuffSkill(PirateSkills.LoadedDice, 0, 180*1000, pdamage = 20).isV(vEhc,4,4).wrap(core.BuffSkillWrapper)
        HerosOath = core.BuffSkill(ShadeSkills.HeroicMemories, 0, 60000, cooltime = 120000, pdamage = 10).wrap(core.BuffSkillWrapper)

        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        SoulConcentrate = core.BuffSkill(ShadeSkills.SpiritFlow, 900, (30+vEhc.getV(2,1))*1000, cooltime = 120*1000, red=True, pdamage_indep = (5+vEhc.getV(2,1)//2)).isV(vEhc,2,1).wrap(core.BuffSkillWrapper)
        SoulConcentrateSummon = core.SummonSkill(_("{}(무작위)").format(ShadeSkills.SpiritFlow), 0, 2000, 1742, 1, (30+vEhc.getV(2,1))*1000, cooltime = -1).isV(vEhc,2,1).wrap(core.SummonSkillWrapper)

        # Gwimunjin: Summons 2 spirits at once. 귀문진: 정령을 한번에 2마리 소환함.
        SoulTrap = core.SummonSkill(ShadeSkills.Spiritgate, 990, 1280, 0, 3 * 2, 40000, cooltime = (120-vEhc.getV(3,2))*1000, red=True).isV(vEhc,3,2).wrap(core.SummonSkillWrapper)
        SoulTrap_D = core.DamageSkill(_("{}(공격)").format(ShadeSkills.Spiritgate), 0, 300+12*vEhc.getV(3,2), 6 * 2, cooltime = -1).isV(vEhc,3,2).wrap(core.DamageSkillWrapper)

        RealSoulAttack = core.DamageSkill(ShadeSkills.TrueSpiritClaw, 540, 540+6*vEhc.getV(1,3), 12 + 1, cooltime=6000, red=True, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20) + core.CharacterModifier(armor_ignore=50)).setV(vEhc, 0, 2, False).isV(vEhc,1,3).wrap(core.DamageSkillWrapper)

        ChainBombPunchInit = core.DamageSkill(_("{}(시전)").format(ShadeSkills.SmashingMultipunch), 390, 0, 0, cooltime=90*1000, red=True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ChainBombPunchTick = core.DamageSkill(_("{}(키다운)").format(ShadeSkills.SmashingMultipunch), 930/8, 400+16*vEhc.getV(0,0), 5, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)  # 8 times of 5 strokes, cast + key down 1320ms. 5타씩 8회, 시전+키다운 1320ms.
        ChainBombPunchFinal = core.DamageSkill(_("{}(막타)").format(ShadeSkills.SmashingMultipunch), 810, 950+38*vEhc.getV(0,0), 15*3, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)  # 3 times of 15 strokes. 15타씩 3회.

        # Shredded iron (for debuff). 파쇄철조 (디버프용).
        BladeImp = core.DamageSkill(ShadeSkills.BladeImpSpinSlash, 360, 160, 4).wrap(core.DamageSkillWrapper)
        BladeImpBuff = core.BuffSkill(ShadeSkills.BladeImpdDownwardSlash, 0, 15 * 1000, cooltime=-1, pdamage_indep=10).wrap(core.BuffSkillWrapper)

        ######   Skill Wrapper   ######

        # Furious marriage. 분혼 격참.
        DoubleBody.onAfter(DoubleBodyAttack)
        DoubleBody.onAfter(DoubleBodyRegistance)
        DoubleBodyConstraint = core.ConstraintElement(_("{}(저항)(제한)").format(ShadeSkills.SoulSplitter), DoubleBodyRegistance, DoubleBodyRegistance.is_not_active)
        DoubleBody.onConstraint(DoubleBodyConstraint)

        def double_body_single_target(doubleBody):
            if doubleBody.is_active():
                # 1 target skill damage reduction during separation, (100/120) * (0.5*1 + 0.5*0.2). 분혼 도중 1타겟 스킬 데미지 감소, (100/120) * (0.5*1 + 0.5*0.2).
                return core.CharacterModifier(pdamage_indep=-40) - core.CharacterModifier(pdamage_indep=20)
            return core.CharacterModifier()

        # The hierarchy of chastity. 정결극 위계.
        EnhanceSpiritLink.onAfters([EnhanceSpiritLinkSummon_S, EnhanceSpiritLinkSummon_J_Init])
        EnhanceSpiritLinkSummon_J_Init.onTick(EnhanceSpiritLinkSummon_J)

        # Elemental cluster. 정령 집속.
        SoulConcentrate.onAfter(DoubleBody.controller(1.0, 'reduce_cooltime_p'))
        SoulConcentrate.onAfter(SoulConcentrateSummon)

        # Gwimunjin. 귀문진.
        SoulTrapStack = SoulTrapStackWrapper(core.BuffSkill(_("{}(버프)").format(ShadeSkills.Spiritgate), 0, 9999999, cooltime = -1))
        SoulTrap.onTick(core.RepeatElement(SoulTrapStack.add_debuff(), 2))  # Generates two debuffs at once. 한 번에 디버프 두 개 생성.
        SoulTrap.onTick(SoulTrap_D)
        SoulTrap_D.add_runtime_modifier(DoubleBody, double_body_single_target)

        # True returning algorithm. 진 귀참 알고리즘.
        BasicAttack = core.OptionalElement(RealSoulAttack.is_available, RealSoulAttack, SoulAttack, name=_("{} 발동 가능?").format(ShadeSkills.TrueSpiritClaw))
        RealSoulAttack.protect_from_running()

        BasicAttackWrapper = core.DamageSkill(_("기본 공격"),0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)

        # Shredding concession. 파쇄 연권.
        ChainBombPunchInit.onAfter(core.RepeatElement(ChainBombPunchTick, 8))
        ChainBombPunchInit.onAfter(ChainBombPunchFinal)

        # Spirit Fox. 여우령.
        FoxSoul.add_runtime_modifier(DoubleBody, double_body_single_target)
        FoxSoul_100.add_runtime_modifier(DoubleBody, double_body_single_target)
        BasicAttack.onAfter(FoxSoul)
        SoulTrap.onTick(core.RepeatElement(FoxSoul, 2))
        SoulConcentrateSummon.onTick(core.RepeatElement(FoxSoul, 2))
        SpiritFrenzy_Tick.onAfter(FoxSoul)
        BladeImp.onAfter(FoxSoul)
        ChainBombPunchTick.onAfter(FoxSoul_100)
        ChainBombPunchFinal.onAfter(core.RepeatElement(FoxSoul_100, 3))

        # Crushed iron. 파쇄철조.
        BladeImp.onAfter(BladeImpBuff)

        # ??. 소혼장막.
        SpiritFrenzy.onAfter(core.RepeatElement(SpiritFrenzy_Tick, 56))
        SpiritFrenzyConstraint = core.ConstraintElement(_("{}(제한)").format(ShadeSkills.SpiritFrenzy), EnhanceSpiritLinkSummon_J, EnhanceSpiritLinkSummon_J.is_active)
        SpiritFrenzy.onConstraint(SpiritFrenzyConstraint)

        return(BasicAttackWrapper, 
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    EnhanceSpiritLink, LuckyDice, HerosOath,
                    globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), Overdrive, SoulConcentrate, DoubleBody, SoulTrapStack,
                    globalSkill.soul_contract()] +\
                [BladeImp, BladeImpBuff, SoulTrap] +\
                [EnhanceSpiritLinkSummon_S, EnhanceSpiritLinkSummon_J_Init, EnhanceSpiritLinkSummon_J, SoulConcentrateSummon] +\
                [RealSoulAttack, DoubleBodyRegistance, SpiritFrenzy, ChainBombPunchInit, MirrorBreak, MirrorSpider] +\
                [BasicAttackWrapper])
