from .globalSkill import GlobalSkills
from .jobbranch.bowmen import ArcherSkills
from ..kernel.graph import DynamicVariableOperation
from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import ConditionRule, InactiveRule, ReservationRule, RuleSet, ConcurrentRunRule
from . import globalSkill, jobutils
from .jobbranch import bowmen
from math import ceil
from typing import Any, Dict

import gettext
_ = gettext.gettext

# English skill information for Mercedes here https://maplestory.fandom.com/wiki/Mercedes/Skills
class MercedesSkills:
    # Link Skill
    ElvenBlessing = _("엘프의 축복")  # "Elven Blessing"
    # Beginner
    ElvenHealing = _("엘프의 회복")  # "Elven Healing"
    Updraft = _("스타일리쉬 무브")  # "Updraft"
    ElvenGrace = _("왕의 자격")  # "Elven Grace"
    # 1st job
    SwiftDualShot = _("스피드 듀얼샷")  # "Swift Dual Shot"
    PotentialPower = _("포텐셜 파워")  # "Potential Power"
    GlideBlast = _("아크로바틱 점프")  # "Glide Blast"
    SharpAim = _("샤프 에이밍")  # "Sharp Aim"
    # 2nd Job
    PiercingStorm = _("크로스 피어싱")  # "Piercing Storm"
    RisingRush = _("차지 드라이브")  # "Rising Rush"
    PartingShot = _("파이널 샷")  # "Parting Shot"
    DualBowgunsBoost = _("듀얼보우건 부스터")  # "Dual Bowguns Boost"
    SpiritSurge = _("스피릿 인퓨전")  # "Spirit Surge"
    DualBowgunsMastery = _("듀얼보우건 마스터리")  # "Dual Bowguns Mastery"
    FinalAttackDualBowguns = _("파이널 어택: 듀얼보우건")  # "Final Attack: Dual Bowguns"
    PhysicalTraining = _("피지컬 트레이닝")  # "Physical Training"
    # 3rd Job
    StunningStrikes = _("스트라이크 듀얼샷")  # "Stunning Strikes"
    LeapTornado = _("리프 토네이도")  # "Leap Tornado"
    UnicornSpike = _("유니콘 스파이크")  # "Unicorn Spike"
    GustDive = _("거스트 다이브")  # "Gust Dive"
    IgnisRoar = _("이그니스 로어")  # "Ignis Roar"
    WaterShield = _("워터 쉴드")  # "Water Shield"
    AerialBarrage = _("하이킥 데몰리션")  # "Aerial Barrage"
    ElementalKnights = _("엘리멘탈 나이트")  # "Elemental Knights"
    # 4th Job
    IshtarsRing = _("이슈타르의 링")  # "Ishtar's Ring"
    SpikesRoyale = _("레전드리 스피어")  # "Spikes Royale"
    LightningEdge = _("라이트닝 엣지")  # "Lightning Edge"
    RollingMoonsault = _("롤링 문썰트")  # "Rolling Moonsault"
    AncientWarding = _("엔시언트 스피릿")  # "Ancient Warding"
    DualBowgunsExpert = _("듀얼보우건 엑스퍼트")  # "Dual Bowguns Expert"
    DefenseBreak = _("디펜스 브레이크")  # "Defense Break"
    AdvancedFinalAttack = _("어드밴스드 파이널 어택")  # "Advanced Final Attack"
    StaggeringStrikes = _("어드밴스드 스트라이크 듀얼샷")  # "Staggering Strikes"
    SpiritNimbleFlight = _("스피릿 이스케이프")  # "Spirit Nimble Flight"
    # Hypers
    WrathofEnlil = _("래쓰 오브 엔릴")  # "Wrath of Enlil"
    HeroicMemories = _("히어로즈 오쓰")  # "Heroic Memories"
    ElvishBlessing = _("엘비시 블레싱")  # "Elvish Blessing"
    # 5th Job
    SpiritofElluel = _("엘리멘탈 고스트")  # "Spirit of Elluel"
    SylvidiasFlight = _("실피디아")  # "Sylvidia's Flight"
    IrkallasWrath = _("이르칼라의 숨결")  # "Irkalla's Wrath"
    RoyalKnights = _("로얄 나이츠")  # "Royal Knights"


class ElementalGhostWrapper(core.BuffSkillWrapper):
    def __init__(self, vEhc, num1, num2, sylphidia: core.BuffSkillWrapper):
        skill = core.BuffSkill(MercedesSkills.SpiritofElluel, 720, (40+vEhc.getV(num1, num2))*1000, cooltime=150*1000, red=True)
        super(ElementalGhostWrapper, self).__init__(skill)
        self.ratio = (30 + vEhc.getV(num1, num2)) * 0.01
        self.prob_slow = 0.9 * (1 + 0.7 * (1 + 0.5))
        self.prob_fast = 0.45 * (1 + 0.35 * (1 + 0.25))
        self.sylphidia = sylphidia

    def addSkill(self, skill_wrapper: core.DamageSkillWrapper, is_fast: bool, is_final_attack: bool):
        p = self.prob_fast if is_fast else self.prob_slow
        ratio = 1 if is_final_attack else self.ratio

        original_skill = skill_wrapper.skill
        copial_skill = core.DamageSkill(
            name=DynamicVariableOperation.reveal_argument(original_skill.name) + _("(엘고)"),
            delay=0,
            damage=original_skill.damage * ratio,
            hit=original_skill.hit * p,
            modifier=original_skill._static_skill_modifier
        ).wrap(core.DamageSkillWrapper)

        if not is_final_attack:
            skill_wrapper.add_runtime_modifier(
                self.sylphidia,
                lambda sk: core.CharacterModifier(pdamage_indep=p * ratio * 100)
                if sk.is_active()
                and self.is_active()  # TODO: Refers to a skill not passed to runtime_modifier Extend runtime_modifier. runtime_modifier에 전달하지 않은 스킬을 참조하고 있음. runtime_modifier 확장할 것.
                else core.CharacterModifier()
            )

        skill_wrapper.onAfter(
            core.OptionalElement(
                lambda: self.is_active() and self.sylphidia.is_not_active(),
                copial_skill,
                name=_("엘고 ON, 실피디아 OFF")
            )
        )


class SylphidiaDamageSkill(core.DamageSkillWrapper):
    """
    Some skills are delayed when riding Silphidia.

    일부 스킬들은 실피디아 탑승시 딜레이가 변경됨.
    """
    def __init__(self, skill: core.DamageSkill, sylphidia: core.BuffSkillWrapper, delay: int):
        super(SylphidiaDamageSkill, self).__init__(skill)
        self.sylphidia = sylphidia
        self.delay = delay

    def get_delay(self) -> float:
        if self.sylphidia.is_active():
            return self.delay
        else:
            return super().get_delay()

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 11
        self.jobtype = "DEX"
        self.jobname = _("메르세데스")
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule(ArcherSkills.ViciousShot, MercedesSkills.SpiritofElluel), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(MercedesSkills.IrkallasWrath, MercedesSkills.SpiritofElluel), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(GlobalSkills.TermsAndConditions, MercedesSkills.SpiritofElluel), RuleSet.BASE)
        ruleset.add_rule(ReservationRule(MercedesSkills.ElvishBlessing, MercedesSkills.SpiritofElluel), RuleSet.BASE)
        ruleset.add_rule(ReservationRule(MercedesSkills.HeroicMemories, MercedesSkills.SpiritofElluel), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(MercedesSkills.SylvidiasFlight, MercedesSkills.SpiritofElluel), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(MercedesSkills.SylvidiasFlight, MercedesSkills.SpiritofElluel, lambda sk: sk.is_cooltime_left(30000, -1)), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        PotentialPower = core.InformedCharacterModifier(MercedesSkills.PotentialPower,pdamage = 20)
        SharpAiming = core.InformedCharacterModifier(MercedesSkills.SharpAim,crit = 40)
        
        SpiritInfusion = core.InformedCharacterModifier(MercedesSkills.SpiritSurge,pdamage = 30, crit=15)
        PhisicalTraining = core.InformedCharacterModifier(MercedesSkills.PhysicalTraining,stat_main = 30, stat_sub = 30)
        
        IgnisRoar = core.InformedCharacterModifier(MercedesSkills.IgnisRoar,pdamage_indep = 15, att = 40)

        DualbowgunExpert = core.InformedCharacterModifier(MercedesSkills.DualBowgunsExpert,att = 30+passive_level, crit_damage= 10+ceil(passive_level/3))
        DefenceBreak = core.InformedCharacterModifier(MercedesSkills.DefenseBreak,armor_ignore= 25+passive_level, pdamage_indep= 20+passive_level, boss_pdamage = 20+3*(passive_level//4), crit_damage = 20+3*(passive_level//4))
        AdvancedFinalAttack = core.InformedCharacterModifier(MercedesSkills.AdvancedFinalAttack,att = 20 + ceil(passive_level / 2))
        
        return [PotentialPower, SharpAiming, SpiritInfusion, 
                PhisicalTraining, IgnisRoar, DualbowgunExpert, DefenceBreak, AdvancedFinalAttack]
        
    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier(_("무기상수"),pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=85+ceil(passive_level/2))

        IgnisRoarStack = core.InformedCharacterModifier(_("{}(스택)").format(MercedesSkills.IgnisRoar),pdamage_indep = 2*10)
        
        return [WeaponConstant, Mastery, IgnisRoarStack]
        
    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=60, armor_ignore=47.7, patt=7, crit_damage=20)
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Hyper
        Ishtar's Ring-Reinforce, Ignor Guard, Boss Killer
        Legendary Spear-Reduce Armor, Linked Reinforcement

        Nasal order
        Issue, Sudu/Pataek, Elemental, Rath of Enlil, Legendary, Unicorn, Letto/Dive

        Elemental Ghost, Irkala's Breath, Critical Reinforce, Soul Contract, Elvisy Blessing, and Heroes Oth are used together

        Not using Silphidia

        Elgo Link
        Sudew-Enlil-Sudew-Unicorn-Sudew-Sphere-It's

        하이퍼
        이슈타르의 링-리인포스, 이그노어 가드, 보스 킬러
        레전드리 스피어-리듀스 아머, 링크드 리인포스

        코강 순서
        이슈, 스듀/파택, 엘리멘탈, 래쓰오브엔릴, 레전드리, 유니콘, 맆토/다이브
        
        엘리멘탈 고스트, 이르칼라의 숨결, 크리티컬 리인포스, 소울 컨트랙트, 엘비시 블레싱, 히어로즈 오쓰를 함께 사용

        실피디아 사용하지 않음

        엘고 연계
        스듀-엔릴-스듀-유니콘-스듀-스피어-거다
        '''
        DEALCYCLE = options.get('dealcycle', 'combo')
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        # Buff skill
        Booster = core.BuffSkill(MercedesSkills.DualBowgunsBoost, 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        AncientSpirit = core.BuffSkill(MercedesSkills.AncientWarding, 0, (200+5*self.combat) * 1000, patt = 30+self.combat, rem=True).wrap(core.BuffSkillWrapper)

        # Summon skill
        ElementalKnights = core.DamageSkill(MercedesSkills.ElementalKnights, 0, 0, 0, cooltime=120*1000, red=True).setV(vEhc, 2, 3, False).wrap(core.DamageSkillWrapper) # Dot reflection required. 도트 반영필요.
        ElementalKnights_1 = core.SummonSkill(f"{MercedesSkills.ElementalKnights}(1)", 0, 1470, (385+385+485)/3, 1, 210 * 1000, cooltime=-1, rem=True).setV(vEhc, 2, 3, False).wrap(core.SummonSkillWrapper)
        ElementalKnights_2 = core.SummonSkill(f"{MercedesSkills.ElementalKnights}(2)", 0, 1470, (385+385+485)/3, 1, 210 * 1000, cooltime=-1, rem=True).setV(vEhc, 2, 3, False).wrap(core.SummonSkillWrapper)
        
        # Damage skill
        IshtarRing = core.DamageSkill(MercedesSkills.IshtarsRing, 120, 220 + self.combat, 2, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        AdvanceStrikeDualShot = core.DamageSkill(MercedesSkills.StaggeringStrikes, 480, 380, 4).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvanceStrikeDualShot_Link = core.DamageSkill(_("{}(연계)").format(MercedesSkills.StaggeringStrikes), 360, 380, 4).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)

        AdvancedFinalAttackFast = core.DamageSkill(_("{}(속사)").format(MercedesSkills.AdvancedFinalAttack), 0, 120 + passive_level, 2*0.01*(75 + passive_level)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedFinalAttackSlow = core.DamageSkill(_("{}(일반)").format(MercedesSkills.AdvancedFinalAttack), 0, 120 + passive_level, 2*0.01*(75 + passive_level)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
    
        # Hyper
        ElvishBlessing = core.BuffSkill(MercedesSkills.ElvishBlessing, 900, 60 * 1000, cooltime = 90 * 1000, att = 80).wrap(core.BuffSkillWrapper)
        HerosOath = core.BuffSkill(MercedesSkills.HeroicMemories, 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        # 5th
        Sylphidia = core.BuffSkill(MercedesSkills.SylvidiasFlight, 0, (30 + vEhc.getV(5,5)//2) * 1000, cooltime = 150 * 1000, red=True, patt = (5+vEhc.getV(5,5)//2)).isV(vEhc,5,5).wrap(core.BuffSkillWrapper) # No information. 정보 없음.
        ElementalGhost = ElementalGhostWrapper(vEhc, 0, 0, sylphidia=Sylphidia)
        ElementalGhostSpirit = core.DamageSkill(_("{}(정령의 기운)").format(MercedesSkills.SpiritofElluel), 0, 450+15*vEhc.getV(0,0), 8, cooltime=10*1000).wrap(core.DamageSkillWrapper)
        IrkilaBreathInit = core.DamageSkill(MercedesSkills.IrkallasWrath, 900, 0, 0, cooltime = 150 * 1000, red=True).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        IrkilaBreathTick = core.DamageSkill(_("{}(틱)").format(MercedesSkills.IrkallasWrath), 150, 400+16*vEhc.getV(1,1), 8).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        RoyalKnights = core.BuffSkill(MercedesSkills.RoyalKnights, 1260, 30000, cooltime=150*1000, red=True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        RoyalKnightsAttack = core.DamageSkill(_("{}(공격)").format(MercedesSkills.RoyalKnights), 0, 325+13*vEhc.getV(0,0), 4*4, cooltime=1410).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)

        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 4, 4)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # Linked skills-Write as a delay when linking. 연계 스킬들 - 연계시 딜레이로 작성.
        UnicornSpike = SylphidiaDamageSkill(
            core.DamageSkill(MercedesSkills.UnicornSpike, 450, 345+100 + 2*self.combat, 5, modifier = core.CharacterModifier(crit=100), cooltime = 10 * 1000, red=True).setV(vEhc, 5, 3, False),
            Sylphidia,
            540
        )
        UnicornSpikeBuff = core.BuffSkill(_("{}(버프)").format(MercedesSkills.UnicornSpike), 0, 30 * 1000, pdamage = 30, cooltime = -1).wrap(core.BuffSkillWrapper)  # No direct casting. 직접시전 금지.
        RegendrySpear = SylphidiaDamageSkill(
            core.DamageSkill(MercedesSkills.SpikesRoyale, 690, 700 + 10*self.combat, 3, cooltime = 5 * 1000, red=True, modifier = core.CharacterModifier(crit=100)).setV(vEhc, 4, 2, False),
            Sylphidia,
            540
        )
        RegendrySpearBuff = core.BuffSkill(_("{}(버프)").format(MercedesSkills.SpikesRoyale), 0, (30+self.combat) * 1000, armor_ignore = 30+20+self.combat, cooltime = -1).wrap(core.BuffSkillWrapper) # No direct casting. 직접시전 금지.
        LightningEdge = core.DamageSkill(MercedesSkills.LightningEdge, 630, 420 + 5*self.combat, 3).wrap(core.DamageSkillWrapper)
        LightningEdgeBuff = core.BuffSkill(_("{}(버프)").format(MercedesSkills.LightningEdge), 0, 30000, cooltime=-1).wrap(core.BuffSkillWrapper)
        LeapTornado = core.DamageSkill(MercedesSkills.LeapTornado, 390, 390+30+3*self.combat, 4).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        GustDive = core.DamageSkill(MercedesSkills.GustDive, 480, 430 + 3*self.combat, 4).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        WrathOfEllil = SylphidiaDamageSkill(
            core.DamageSkill(MercedesSkills.WrathofEnlil, 210, 460, 10, cooltime = 8 * 1000).setV(vEhc, 3, 2, False),
            Sylphidia,
            540
        )
    
        ######   Skill Wrapper   ######
        #Buff
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 2, 2, 10)

        #Summon
        ElementalKnights.onAfter(core.OptionalElement(ElementalKnights_1.is_active, ElementalKnights_2, ElementalKnights_1))
    
        #Damage
        UnicornSpike.onAfter(UnicornSpikeBuff)
        RegendrySpear.onAfter(RegendrySpearBuff)
        LightningEdge.onAfter(LightningEdgeBuff)
        IshtarRing.add_runtime_modifier(LightningEdgeBuff, lambda sk: core.CharacterModifier(pdamage = sk.is_active() * 20))
    
        IrkilaBreath = core.RepeatElement(IrkilaBreathTick, 52)
        IrkilaBreathInit.onAfter(IrkilaBreath)

        #Cooldown
        LinkAttack = core.GraphElement(_("연계"))
        LinkAttack.onAfter(WrathOfEllil.controller(1000, "reduce_cooltime"))
        LinkAttack.onAfter(UnicornSpike.controller(1000, "reduce_cooltime"))
        LinkAttack.onAfter(RegendrySpear.controller(1000, "reduce_cooltime"))
        LinkAttack.onAfter(ElementalGhostSpirit.controller(1000, "reduce_cooltime"))
        
        # Damage Cycle
        DebuffCombo = core.DamageSkill(_("디버프 콤보"), 0, 0, 0).wrap(core.DamageSkillWrapper)
        DebuffComboList = [AdvanceStrikeDualShot_Link, WrathOfEllil, AdvanceStrikeDualShot_Link,
                            UnicornSpike, AdvanceStrikeDualShot_Link, LightningEdge, AdvanceStrikeDualShot_Link,
                            RegendrySpear, WrathOfEllil, AdvanceStrikeDualShot]
        DebuffCombo.onAfter(DebuffComboList[0])
        for sk in DebuffComboList[1:]:
            DebuffCombo.onAfter(sk)
            DebuffCombo.onAfter(LinkAttack)
        DebuffCombo.onConstraint(core.ConstraintElement(_("디버프 없을시"), UnicornSpikeBuff, UnicornSpikeBuff.is_not_active))
        DebuffCombo.onConstraint(core.ConstraintElement(_("{} 아닐시").format(MercedesSkills.SylvidiasFlight), Sylphidia, Sylphidia.is_not_active))

        ElementalGhostCombo = core.DamageSkill(_("엘고 콤보"), 0, 0, 0).wrap(core.DamageSkillWrapper)
        ElementalGhostComboList = [AdvanceStrikeDualShot_Link, WrathOfEllil, AdvanceStrikeDualShot_Link,
                                    UnicornSpike, AdvanceStrikeDualShot_Link, RegendrySpear, GustDive]
        ElementalGhostCombo.onAfter(ElementalGhostComboList[0])
        for sk in ElementalGhostComboList[1:]:
            ElementalGhostCombo.onAfter(sk)
            ElementalGhostCombo.onAfter(LinkAttack)

        BasicAttack = core.DamageSkill(_("기본 공격"), 0, 0, 0).wrap(core.DamageSkillWrapper)
        if DEALCYCLE == "combo":
            BasicAttack.onAfter(
                core.OptionalElement(lambda: ElementalGhost.is_active() and Sylphidia.is_not_active(), ElementalGhostCombo, IshtarRing)
            )
        elif DEALCYCLE == "ishtar":
            BasicAttack.onAfter(IshtarRing)
        else:
            raise ValueError(DEALCYCLE)

        #Final Attack, Elemental Ghost
        UseElementalGhostSpirit = core.OptionalElement(
            lambda: ElementalGhost.is_active() and ElementalGhostSpirit.is_available(), ElementalGhostSpirit, name=_("정령의 기운 조건"))
        UseRoyalNightsAttack = core.OptionalElement(
            lambda: RoyalKnights.is_active() and RoyalKnightsAttack.is_available(), RoyalKnightsAttack, name=_("{}(조건)").format(MercedesSkills.RoyalKnights))

        for wrp in [UnicornSpike, RegendrySpear, LightningEdge, LeapTornado,
                    AdvanceStrikeDualShot, AdvanceStrikeDualShot_Link, WrathOfEllil]:
            ElementalGhost.addSkill(wrp, is_fast=False, is_final_attack=False)
            wrp.onAfter(AdvancedFinalAttackSlow)
            wrp.onAfter(UseElementalGhostSpirit)
            wrp.onAfter(UseRoyalNightsAttack)
        
        GustDive.onAfter(AdvancedFinalAttackSlow)  # Gust Dive does not have an afterimage of Elgo. 거스트 다이브는 엘고 잔상이 안터짐.
        GustDive.onAfter(UseRoyalNightsAttack)

        # Issue #446 An error in which almost all of the afterimages are chewed. Issue #446 잔상 파택이 거의 전부 씹히는 오류.
        # ElementalGhost.addSkill(AdvancedFinalAttackSlow, is_fast=False, is_final_attack=True) # Afterimage->Pataek is treated as afterimage->Afterimage, the final damage reduction is not applied instead. 잔상->파택을 파택->잔상으로 처리, 대신 최종뎀 감소는 적용하지 않게 함.
            
        for wrp in [IshtarRing, IrkilaBreathTick]:
            ElementalGhost.addSkill(wrp, is_fast=True, is_final_attack=False)
            wrp.onAfter(AdvancedFinalAttackFast)
            wrp.onAfter(UseElementalGhostSpirit)
            wrp.onAfter(UseRoyalNightsAttack)
        ElementalGhost.addSkill(AdvancedFinalAttackFast, is_fast=True, is_final_attack=True)

        GuidedArrow.onTick(UseRoyalNightsAttack)

        IsSylphidia = core.ConstraintElement(_("{} 탑승중").format(MercedesSkills.SylvidiasFlight), Sylphidia, Sylphidia.is_active)
        for sk in [UnicornSpike, RegendrySpear, WrathOfEllil]:  # When boarding Silphidia, use it separately without going through DebuffCombo. 실피디아 탑승시에는 DebuffCombo를 통하지 않고 따로 사용.
            sk.onConstraint(IsSylphidia)

        for sk in [ElementalGhostSpirit, RoyalKnightsAttack]:
            sk.protect_from_running()

        for sk in [UnicornSpikeBuff, RegendrySpearBuff, LightningEdgeBuff]:
            sk.set_disabled_and_time_left(1)  # Start measuring with the buff on. 버프 묻은 채로 측정 시작.
    
        return(BasicAttack,
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), 
                    Booster, ElvishBlessing, AncientSpirit, HerosOath, RoyalKnights,
                    CriticalReinforce, UnicornSpikeBuff, RegendrySpearBuff, LightningEdgeBuff, ElementalGhost, Sylphidia,
                    globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()] +\
                [RoyalKnightsAttack, ElementalGhostSpirit, DebuffCombo, UnicornSpike, RegendrySpear, WrathOfEllil, IrkilaBreathInit] +\
                [ElementalKnights, ElementalKnights_1, ElementalKnights_2, GuidedArrow, MirrorBreak, MirrorSpider] +\
                [] +\
                [BasicAttack])