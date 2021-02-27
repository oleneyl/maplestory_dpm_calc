from functools import partial

from .globalSkill import GlobalSkills
from .jobbranch.pirates import PirateSkills
from .jobbranch.thieves import ThiefSkills
from ..kernel import core
from ..character import characterKernel as ck
from ..execution.rules import DisableRule, InactiveRule, RuleSet, ConcurrentRunRule, ConditionRule
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import thieves, pirates
from .jobclass import resistance
from . import jobutils
from math import ceil
from typing import Any, Dict

import gettext
_ = gettext.gettext

# English skill information for Xenon here https://maplestory.fandom.com/wiki/Xenon/Skills
class XenonSkills:
    # Link Skill
    HybridLogic = _("하이브리드 로직")  # "Hybrid Logic"
    # Beginner
    SupplySurplus = _("서플러스 서플라이")  # "Supply Surplus"
    MultilateralI = _("멀티래터럴 I")  # "Multilateral I"
    ModalShift = _("멀티 모드 링커")  # "Modal Shift"
    # 1st Job
    BeamSpline = _("에너지 스플라인")  # "Beam Spline"
    PropulsionBurst = _("서든 프로펠")  # "Propulsion Burst"
    CircuitSurge = _("인클라인 파워")  # "Circuit Surge"
    RadialNerve = _("레디얼너브 리파인")  # "Radial Nerve"
    MultilateralII = _("멀티래터럴 II")  # "Multilateral II"
    PinpointSalvo = _("핀포인트 로켓")  # "Pinpoint Salvo"
    # 2nd Job
    QuicksilverFlash = _("퀵실버 소드 : 섬광")  # "Quicksilver: Flash"
    QuicksilverConcentrate = _("퀵실버 소드 : 집중")  # "Quicksilver: Concentrate"
    QuicksilverTakeoff = _("퀵실버 소드 : 도약")  # "Quicksilver: Takeoff"
    IonThrust = _("이온 쓰러스터")  # "Ion Thrust"
    PerspectiveShift = _("리니어 퍼스펙티브")  # "Perspective Shift"
    EfficiencyStreamline = _("에피션시 파이프라인")  # "Efficiency Streamline"
    XenonBooster = _("제논 부스터")  # "Xenon Booster"
    StructuralIntegrity = _("마이너리티 서포트")  # "Structural Integrity"
    XenonMastery = _("제논 마스터리")  # "Xenon Mastery"
    MultilateralIII = _("멀티래터럴 III")  # "Multilateral III"
    PinpointSalvoRedesignA = _("핀포인트 로켓 1차 강화")  # "Pinpoint Salvo Redesign A"
    # 3rd Job
    CombatSwitchExplosion = _("컴뱃 스위칭 : 폭발")  # "Combat Switch: Explosion"
    CombatSwitchAirWhip = _("컴뱃 스위칭 : 격추")  # "Combat Switch: Air Whip"
    CombatSwitchFission = _("컴뱃 스위칭 : 분열")  # "Combat Switch: Fission"
    DiagonalChase = _("다이아그널 체이스")  # "Diagonal Chase"
    GravityPillar = _("필라 스크램블")  # "Gravity Pillar"
    HybridDefenses = _("듀얼브리드 디펜시브")  # "Hybrid Defenses"
    AegisSystem = _("이지스 시스템")  # "Aegis System"
    Triangulation = _("트라이앵글 포메이션")  # "Triangulation"
    ManifestProjector = _("버추얼 프로젝션")  # "Manifest Projector"
    MultilateralIV = _("멀티래터럴 IV")  # "Multilateral IV"
    EmergencyResupply = _("엑스트라 서플라이")  # "Emergency Resupply"
    PinpointSalvoRedesignB = _("핀포인트 로켓 2차 강화")  # "Pinpoint Salvo Redesign B"
    # 4th Job
    BeamDance = _("블레이드 댄싱")  # "Beam Dance"
    MechaPurgeSnipe = _("퍼지롭 매스커레이드 : 저격")  # "Mecha Purge: Snipe"
    MechaPurgeBombard = _("퍼지롭 매스커레이드 : 포격")  # "Mecha Purge: Bombard"
    MechaPurgeBombardment = _("퍼지롭 매스커레이드 : 폭격")  # "Mecha Purge: Bombardment"
    HypogramFieldPenetrate = _("홀로그램 그래피티 : 관통")  # "Hypogram Field: Penetrate"
    HypogramFieldForceField = _("홀로그램 그래피티 : 역장")  # "Hypogram Field: Force Field"
    HypogramFieldSupport = _("홀로그램 그래피티 : 지원")  # "Hypogram Field: Support"
    OOPArtsCode = _("오파츠 코드")  # "OOPArts Code"
    OffensiveMatrix = _("오펜시브 매트릭스")  # "Offensive Matrix"
    InstantShock = _("인스턴트 셔크")  # "Instant Shock"
    XenonExpert = _("제논 엑스퍼트")  # "Xenon Expert"
    TemporalPod = _("타임 캡슐")  # "Temporal Pod"
    MultilateralV = _("멀티래터럴 V")  # "Multilateral V"
    PinpointSalvoPerfectDesign = _("핀포인트 로켓 최종 강화")  # "Pinpoint Salvo Perfect Design"
    MultilateralVI = _("멀티래터럴 VI")  # "Multilateral VI"
    # Hypers
    OrbitalCataclysm = _("멜트다운 익스플로전")  # "Orbital Cataclysm"
    EntanglingLash = _("컨파인 인탱글")  # "Entangling Lash"
    AmaranthGenerator = _("아마란스 제네레이터")  # "Amaranth Generator"
    # 5th Job
    OmegaBlaster = _("메가 스매셔")  # "Omega Blaster"
    CoreOverload = _("오버로드 모드")  # "Core Overload"
    HypogramFieldFusion = _("홀로그램 그래피티 : 융합")  # "Hypogram Field: Fusion"
    PhotonRay = _("포톤 레이")  # "Photon Ray"


'''
Advisor: Monolith, 몰라#4508
'''

# TODO: damage cycle optimization. 딜사이클 최적화.
# Rogue item Ruxenon family. 도적템 럭제논 가정.
# Aegis system not used. 이지스 시스템 미사용.


class SupplyStackWrapper(core.StackSkillWrapper):
    def __init__(self, skill):
        super(SupplyStackWrapper, self).__init__(skill, 20)
        self.stack = 20
        self.amaranth_generator = False
        self.overload_mode = False
        self.tick_duration = 4000
        self.tick = self.tick_duration

    # No energy consumption when activated by Amaranth or Overlord. 아마란스 혹은 오버로드 활성화시 에너지 소모 없음.
    def consume(self, d):
        if not self.amaranth_generator and not self.overload_mode:
            self.stack = max(self.stack - d, 0)

        return core.ResultObject(
            0, core.CharacterModifier(), 0, 0, sname=self.skill.name, spec="graph control"
        )

    def consumeController(self, d):
        return core.TaskHolder(core.Task(self, partial(self.consume, d)), name=_("에너지 -{}").format(d))

    # Extra and Amaranth cannot be charged in excess of 20. 엑스트라, 아마란스는 20개 초과해서 충전되지 않음.
    def charge(self, d):
        self.stack = min(self.stack + d, max(self.stack, 20))
        return core.ResultObject(
            0, core.CharacterModifier(), 0, 0, sname=self.skill.name, spec="graph control"
        )

    def chargeController(self, d):
        return core.TaskHolder(core.Task(self, partial(self.charge, d)), name=_("에너지 +{}").format(d))

    def judge_energy(self, stack):
        if self.amaranth_generator or self.overload_mode:
            return True
        else:
            return super(SupplyStackWrapper, self).judge(stack, 1)

    def spend_time(self, time: float) -> None:
        """
        If the stack is at its maximum, the tick is fixed at 0, and one space is immediately charged when the stack is consumed or the limit is increased.
        스택이 최대치일 경우 틱이 0으로 고정되어, 스택이 소모되거나 제한이 늘어날 때 즉시 한칸이 충전됨.
        """
        self.tick -= time
        if self.stack == self._max:
            self.tick = 0
        elif self.tick <= 0:
            self.stack = min(self.stack + 1, self._max)
            self.tick = self.tick_duration + self.tick

        return super(SupplyStackWrapper, self).spend_time(time)

    def get_modifier(self):
        """
        Increases all stats by 1% per 1 surplus energy, and increases final damage by 1% per excess energy when exceeding 20.
        서플러스 에너지 1개 당 모든 능력치 1%만큼 증가, 20 초과시 초과 에너지당 최종 데미지 1% 증가.
        """
        return core.CharacterModifier(
            pstat_main=self.stack,
            pstat_sub=self.stack,
            pdamage_indep=max(0, self.stack-20),
        )

    def begin_overload(self):
        self.overload_mode = True
        self._max = 40
        self.tick_duration = 2000
        return self._result_object_cache

    def beginOverloadMode(self):
        return core.TaskHolder(core.Task(self, self.begin_overload), name=_("{} 시작").format(XenonSkills.CoreOverload))

    def end_overload(self):
        self.overload_mode = False
        self.stack = min(20, self.stack)
        self._max = 20
        self.tick_duration = 4000
        return self._result_object_cache

    def endOverloadMode(self):
        return core.TaskHolder(core.Task(self, self.end_overload), name=_("{} 종료").format(XenonSkills.CoreOverload))

    def begin_amaranth(self):
        self.amaranth_generator = True
        return self._result_object_cache

    def beginAmaranthGenerator(self):
        return core.TaskHolder(core.Task(self, self.begin_amaranth), name=_("{} 시작").format(XenonSkills.AmaranthGenerator))

    def end_amaranth(self):
        self.amaranth_generator = False
        return self._result_object_cache

    def endAmaranthGenerator(self):
        return core.TaskHolder(core.Task(self, self.end_amaranth), name=_("{} 종료").format(XenonSkills.AmaranthGenerator))


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "xenon"
        self.jobname = _("제논")
        self.vEnhanceNum = None
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2
        self.hyperStatPrefixed = 25  # 스탠스 5레벨 투자
        self.buffrem = (0, 40)

    # TODO: Photon ray can be used more often with fusion. 포톤 레이가 융합과 함께 사용되는 빈도를 늘릴 수 있음.
    def get_ruleset(self):
        ruleset = RuleSet()

        ruleset.add_rule(ConditionRule(XenonSkills.EmergencyResupply, XenonSkills.SupplySurplus, lambda sk : sk.stack < 20), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(XenonSkills.AmaranthGenerator, XenonSkills.CoreOverload), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(XenonSkills.AmaranthGenerator, XenonSkills.SupplySurplus, lambda sk : sk.stack <= 1), RuleSet.BASE)

        for skill in [_("{}(개시)").format(XenonSkills.OmegaBlaster), GlobalSkills.TermsAndConditions, ThiefSkills.LastResort, PirateSkills.Overdrive]:
            ruleset.add_rule(ConcurrentRunRule(skill, XenonSkills.HypogramFieldFusion), RuleSet.BASE)

        ruleset.add_rule(ConditionRule(XenonSkills.HypogramFieldFusion, XenonSkills.CoreOverload, lambda sk: sk.is_time_left(40000, -1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(XenonSkills.CoreOverload, XenonSkills.HypogramFieldFusion, lambda sk: sk.is_cooltime_left(70000-40000, -1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(GlobalSkills.MapleWorldGoddessBlessing, XenonSkills.CoreOverload, lambda sk: sk.is_active() and sk.is_time_left(60000, -1)), RuleSet.BASE)

        ruleset.add_rule(DisableRule(XenonSkills.OrbitalCataclysm), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pstat_main=20, pstat_sub=20)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        Multilateral1 = core.InformedCharacterModifier(XenonSkills.MultilateralI, pdamage=3)
        Multilateral2 = core.InformedCharacterModifier(XenonSkills.MultilateralII, pdamage=5)
        Multilateral3 = core.InformedCharacterModifier(XenonSkills.MultilateralIII, pdamage=7)
        Multilateral4 = core.InformedCharacterModifier(XenonSkills.MultilateralIV, pdamage=10)
        Multilateral5 = core.InformedCharacterModifier(XenonSkills.MultilateralV, pdamage=10)
        Multilateral6 = core.InformedCharacterModifier(XenonSkills.MultilateralVI, pdamage=5)

        Multilateral = [Multilateral1, Multilateral2, Multilateral3, Multilateral4, Multilateral5, Multilateral6]

        LinearPerspective = core.InformedCharacterModifier(XenonSkills.PerspectiveShift, crit=40)
        MinoritySupport = core.InformedCharacterModifier(XenonSkills.StructuralIntegrity, stat_main=60)  # Strength deck 20 each. 힘덱럭 20씩.
        XenonMastery = core.InformedCharacterModifier(XenonSkills.XenonMastery, att=20)
        HybridDefensesPassive = core.InformedCharacterModifier(_("{}(패시브)").format(XenonSkills.HybridDefenses), stat_main=30)  # Strength deck 30 each. 힘덱럭 30씩.
        XenonExpert = core.InformedCharacterModifier(XenonSkills.XenonExpert, att=30 + passive_level, crit_damage=8)
        OffensiveMatrix = core.InformedCharacterModifier(XenonSkills.OffensiveMatrix, armor_ignore=30 + passive_level)

        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 3, 4)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 2, 2)

        return Multilateral + [LinearPerspective, MinoritySupport, XenonMastery, HybridDefensesPassive, XenonExpert, OffensiveMatrix,
                               LoadedDicePassive, ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep=50)
        JobConstant = core.InformedCharacterModifier(_("직업상수"), pdamage_indep=-12.5)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90+ceil(passive_level/2))

        return [WeaponConstant, JobConstant, Mastery]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Hyper Skill: 3 types of holograms, Fuzzy Lop Demjeung + Bangmu.
        하이퍼 스킬: 홀로그램 3종, 퍼지롭 뎀증 + 방무.
        '''
        HOLOGRAM_FUSION_HIT = 680

        # Buff skills
        # Pet Buff: Epision City, Booster. 펫버프: 에피션시, 부스터.
        InclinePower = core.BuffSkill(XenonSkills.CircuitSurge, 990, 240000, att=30, rem=True).wrap(core.BuffSkillWrapper)
        EfficiencyPipeLine = core.BuffSkill(XenonSkills.EfficiencyStreamline, 0, 240000, rem=True).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill(XenonSkills.XenonBooster, 0, 240000, rem=True).wrap(core.BuffSkillWrapper)
        VirtualProjection = core.BuffSkill(XenonSkills.ManifestProjector, 0, 999999999).wrap(core.BuffSkillWrapper)

        # No delay in Wickham R. 위컴알에 딜레이 없음.
        ExtraSupply = core.BuffSkill(XenonSkills.EmergencyResupply, 0, 1, cooltime=30000, red=True).wrap(core.BuffSkillWrapper)

        OOPArtsCode = core.BuffSkill(XenonSkills.OOPArtsCode, 990, (30+self.combat//2)*1000, pdamage_indep=25+self.combat//2, boss_pdamage=30+self.combat, rem=True).wrap(core.BuffSkillWrapper)

        # Damage skills

        # Rocket enhancement applied. 로켓강화 적용됨.
        PinpointRocket = core.DamageSkill(XenonSkills.PinpointSalvo, 0, 50+40+40+100, 4, cooltime=2000).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)

        # At-bats are transferred to Skill Wrapper. 타수는 Skill Wrapper 쪽으로 이관.
        # AegisSystem = core.DamageSkill("이지스 시스템", 0, 120, 1, modifier=core.CharacterModifier(pdamage=20+passive_level//3), cooltime=1500).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)

        # Stacks with a 30% probability, stacks 3 stacks, and then disappears when attacking. 30%확률로 중첩 쌓임, 3중첩 쌓은 후 공격시 터지면서 사라지도록.
        Triangulation = core.DamageSkill(XenonSkills.Triangulation, 0, 340, 3, cooltime=-1).setV(vEhc, 0, 3, True).wrap(core.DamageSkillWrapper)

        PurgeSnipe = core.DamageSkill(XenonSkills.MechaPurgeSnipe, 690, 345 + 2*self.combat, 7, modifier=core.CharacterModifier(armor_ignore=30 + self.combat) + core.CharacterModifier(pdamage=20, armor_ignore=10)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)

        # Force field criteria. 역장 기준.
        # 3 types of hyper applied. 하이퍼 3종 적용.
        Hologram_Penetrate = core.SummonSkill(XenonSkills.HypogramFieldPenetrate, 720, 30000/116, 213+3*self.combat, 1, 20000+10000, cooltime=30000-1000*ceil(self.combat/3), modifier=core.CharacterModifier(pdamage=10), red=True).setV(vEhc, 0, 2, True).wrap(core.SummonSkillWrapper)
        Hologram_ForceField = core.SummonSkill(XenonSkills.HypogramFieldForceField, 720, 30000/64, 400+5*self.combat, 1, 20000+10000, cooltime=30000-1000*ceil(self.combat/3), modifier=core.CharacterModifier(pdamage=10), red=True).setV(vEhc, 0, 2, True).wrap(core.SummonSkillWrapper)


        # BladeDancingPrepare = core.DamageSkill(_("{}(준비)").format(XenonSkills.BeamDance), 720 + 420, 0, 0).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        # BladeDancing = core.DamageSkill(XenonSkills.BeamDance, 480, 140+4*self.combat, 1).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        # BladeDancingEnd = core.DamageSkill(_("{}(종료)").format(XenonSkills.BeamDance), 300, 0, 0).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)


        # Hyper skills
        AmaranthGenerator = core.BuffSkill(XenonSkills.AmaranthGenerator, 900, 10000, cooltime=90000, rem=False).wrap(core.BuffSkillWrapper)  # 에너지 최대치, 10초간 에너지 소모 없음
        MeltDown = core.DamageSkill(XenonSkills.OrbitalCataclysm, 3150, 900, 6, red=False, cooltime=50000).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        MeltDown_Armor = core.BuffSkill(_("{}(방무)").format(XenonSkills.OrbitalCataclysm), 0, 10000, armor_ignore=30, rem=False, cooltime=-1).wrap(core.BuffSkillWrapper)
        MeltDown_Damage = core.BuffSkill(_("{}(데미지)").format(XenonSkills.OrbitalCataclysm), 0, 25000, pdamage=10, rem=False, cooltime=-1).wrap(core.BuffSkillWrapper)

        # V skills
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        LuckyDice = core.BuffSkill(PirateSkills.LoadedDice, 0, 180*1000, pdamage=20).isV(vEhc, 3, 4).wrap(core.BuffSkillWrapper)
        ResistanceLineInfantry = resistance.ResistanceLineInfantryWrapper(vEhc, 0, 0)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 4, 4)

        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)

        MegaSmasher = core.DamageSkill(_("{}(개시)").format(XenonSkills.OmegaBlaster), 0, 0, 0, cooltime=180000, red=True).wrap(core.DamageSkillWrapper)
        MegaSmasherTick = core.DamageSkill(_("{}(틱)").format(XenonSkills.OmegaBlaster), 210, 300+10*vEhc.getV(4, 4), 6, cooltime=-1).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)

        OVERLOAD_TIME = 70
        OverloadMode = core.BuffSkill(XenonSkills.CoreOverload, 720, OVERLOAD_TIME*1000, cooltime=180000, red=True).wrap(core.BuffSkillWrapper)
        # First attack always starts after 5100ms. 첫 공격은 항상 5100ms 후에 시작.
        # Attack period is random from 3600ms~10800ms. 공격 주기는 3600ms~10800ms 중 랜덤.
        OverloadHit = core.SummonSkill(_("{}(전류)").format(XenonSkills.CoreOverload), 0, (3600+10800)/2, 180+7*vEhc.getV(4, 4), 6*4, OVERLOAD_TIME*1000-5100, cooltime=-1).isV(vEhc, 4, 4).wrap(core.SummonSkillWrapper)
        OverloadHit_copy = core.SummonSkill(_("{}(전류)({})").format(XenonSkills.CoreOverload, XenonSkills.ManifestProjector), 0, (3600+10800)/2, (180+7*vEhc.getV(4, 4))*0.7, 6*4, OVERLOAD_TIME*1000-5100, cooltime=-1).isV(vEhc, 4, 4).wrap(core.SummonSkillWrapper)

        # Hyper applied. 하이퍼 적용됨.
        Hologram_Fusion = core.SummonSkill(XenonSkills.HypogramFieldFusion, 930, (30000+10000)/(HOLOGRAM_FUSION_HIT/5), 250+10*vEhc.getV(4, 4), 5, 30000+10000, cooltime=100000, red=True, modifier=core.CharacterModifier(pdamage=10)).isV(vEhc, 4, 4).wrap(core.SummonSkillWrapper)
        Hologram_Fusion_Buff = core.BuffSkill(_("{}(버프)").format(XenonSkills.HypogramFieldFusion), 0, 30000+10000, pdamage=5+vEhc.getV(4, 4)//2, rem=False, cooltime=-1).wrap(core.BuffSkillWrapper)

        # Activates 30 times, skips firing delay, and charges with fuzzy robs. 30회 발동, 발사 딜레이 생략, 퍼지롭으로 충전.
        PhotonRay = core.BuffSkill(XenonSkills.PhotonRay, 0, 20000, cooltime=35000, red=True).wrap(core.BuffSkillWrapper)
        PhotonRayHit = core.DamageSkill(_("{}(캐논)").format(XenonSkills.PhotonRay), 0, 350+vEhc.getV(4, 4)*14, 4*30, cooltime=-1).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)

        ######   Skill Wrapper   ######
        SupplySurplus = SupplyStackWrapper(core.BuffSkill(XenonSkills.SupplySurplus, 0, 999999999))

        # Hologram skills cannot be used with fusion. 홀로그램 스킬들은 융합과 함께 사용불가.
        for skill in [Hologram_ForceField, Hologram_Penetrate]:
            skill.onConstraint(core.ConstraintElement(skill._id + _("(사용 제한)"), Hologram_Fusion, Hologram_Fusion.is_not_active))
            Hologram_Fusion.onJustAfter(skill.controller(1, 'set_disabled'))

        PinpointRocketOpt = core.OptionalElement(PinpointRocket.is_available, PinpointRocket)

        # 10 or 3 when holographic fusion is activated. 홀로그램 융합 활성화시 10개, 아니면 3개.
        # AegisSystemOpt_ = core.OptionalElement(Hologram_Fusion_Buff.is_active, core.RepeatElement(AegisSystem, 10), core.RepeatElement(AegisSystem, 3))
        # AegisSystemOpt = core.OptionalElement(AegisSystem.is_active, AegisSystemOpt_)

        ExtraSupply.onJustAfter(SupplySurplus.chargeController(10))
        AmaranthGenerator.onJustAfter(SupplySurplus.chargeController(20))

        InclinePower.onConstraint(core.ConstraintElement(_("에너지 3"), SupplySurplus, partial(SupplySurplus.judge_energy, 3)))
        InclinePower.onJustAfter(SupplySurplus.consumeController(3))
        OOPArtsCode.onConstraint(core.ConstraintElement(_("에너지 20"), SupplySurplus, partial(SupplySurplus.judge_energy, 20)))
        OOPArtsCode.onJustAfter(SupplySurplus.consumeController(20))

        AmaranthGenerator.onJustAfter(SupplySurplus.beginAmaranthGenerator())
        AmaranthGenerator.onEventEnd(SupplySurplus.endAmaranthGenerator())

        TriangulationStack = core.StackSkillWrapper(core.BuffSkill(_("{} 스택").format(XenonSkills.Triangulation), 0, 99999999), 3)
        TriangulationTrigger = core.OptionalElement(lambda : TriangulationStack.judge(3, 1), Triangulation, TriangulationStack.stackController(0.3))
        Triangulation.onJustAfter(TriangulationStack.stackController(0, dtype='set'))

        MegaSmasher.onAfter(core.RepeatElement(MegaSmasherTick, 78))

        OverloadMode.onJustAfter(SupplySurplus.beginOverloadMode())
        OverloadMode.onEventEnd(SupplySurplus.endOverloadMode())
        OverloadMode.onEventElapsed(OverloadHit, 5100)
        OverloadMode.onEventElapsed(OverloadHit_copy, 5100)

        # Photon Ray activation after using Fuzzy Lob 15 times, optimization required. 퍼지롭 15회 사용 후 포톤레이 발동, 최적화 필요.
        PhotonRay.onEventElapsed(PhotonRayHit, 690*15)

        for sk in [PurgeSnipe, MeltDown, MegaSmasherTick]:
            sk.onJustAfter(TriangulationTrigger)
            sk.onJustAfter(PinpointRocketOpt)
            jobutils.create_auxilary_attack(sk, 0.7, nametag=f"({XenonSkills.ManifestProjector})")

        MeltDown.onJustAfter(MeltDown_Armor)
        MeltDown.onJustAfter(MeltDown_Damage)

        OverloadHit.onTick(TriangulationTrigger)
        OverloadHit.onTick(PinpointRocketOpt)

        Hologram_Fusion.onJustAfter(Hologram_Fusion_Buff)

        PinpointRocket.protect_from_running()

        # Scheduling
        EnsureOOPArtsCode = core.OptionalElement(lambda: OverloadMode.is_active() and OOPArtsCode.is_time_left(16000, -1), OOPArtsCode)
        MegaSmasher.onBefore(EnsureOOPArtsCode)

        return (
            PurgeSnipe,
            [
                SupplySurplus,
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                globalSkill.useful_hyper_body_xenon(),
                Booster,
                InclinePower,
                EfficiencyPipeLine,
                VirtualProjection,
                LuckyDice,
                ExtraSupply,
                OverloadMode,
                AmaranthGenerator,
                OOPArtsCode,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                Overdrive,
                ReadyToDie,
                globalSkill.soul_contract(),
            ]
            + [
                Hologram_Fusion,
                Hologram_Fusion_Buff,
                ResistanceLineInfantry,
                Hologram_ForceField,
            ]
            + [
                PhotonRay,
                MirrorBreak,
                MirrorSpider,
                MegaSmasher,
                MeltDown,
                MeltDown_Armor,
                MeltDown_Damage,
            ]
            + [  # Not used from scheduler
                OverloadHit,
                OverloadHit_copy,
                PinpointRocket,
                Triangulation,
                MegaSmasherTick,
                PhotonRayHit,
            ]
            + [PurgeSnipe],
        )
