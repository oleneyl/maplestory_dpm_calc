from dpmModule.jobs.jobbranch.thieves import ThiefSkills

from ..kernel.graph import DynamicVariableOperation
from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill, jobutils
from .jobbranch import thieves
from .jobclass import nova
from math import ceil
from typing import Any, Dict

import gettext
_ = gettext.gettext

# English skill information for Cadena here https://maplestory.fandom.com/wiki/Cadena/Skills
class CadenaSkills:
    # Link Skill
    UnfairAdvantage = _("인텐시브 인썰트")  # "Unfair Advantage"
    # 1st Job
    ChainArtsPursuit = _("체인아츠:체이스")  # "Chain Arts: Pursuit"
    ChainArtsThrash = _("체인아츠:")  # "Chain Arts: Thrash"
    SummonScimitar = _("서먼 커팅 시미터")  # "Summon Scimitar"
    Shadowstep = _("에이전트 시프트")  # "Shadowstep"
    TheWayofShadows = _("에이전트 스텝")  # "The Way of Shadows"
    UncannyLuck = _("콜렉팅 포리프")  # "Uncanny Luck"
    # 2nd Job
    ChainArtsThrashII = _("체인아츠:스트로크 1차 강화")  # "Chain Arts: Thrash II"
    SummonClaw = _("서먼 스크래칭 클로")  # "Summon Claw"
    SummonShuriken = _("서먼 스로잉 윙대거")  # "Summon Shuriken"
    WeaponBooster = _("웨폰 부스터")  # "Weapon Booster"
    MuscleMemory = _("웨폰 버라이어티 I")  # "Muscle Memory"
    WeaponMastery = _("웨폰 마스터리")  # "Weapon Mastery"
    PhysicalTraining = _("피지컬 트레이닝")  # "Physical Training"
    WisdomofShadows = _("퀵서비스 마인드 I")  # "Wisdom of Shadows"
    # 3rd Job
    ChainArtsThrashIII = _("체인아츠:스트로크 2차 강화")  # "Chain Arts: Thrash III"
    SummonShotgun = _("서먼 슈팅 샷건")  # "Summon Shotgun"
    SummonDaggers = _("서먼 슬래싱 나이프")  # "Summon Daggers"
    SummonDecoyBomb = _("서먼 릴리징 봄")  # "Summon Decoy Bomb"
    MuscleMemoryII = _("웨폰 버라이어티 II")  # "Muscle Memory II"
    Determination = _("템퍼")  # "Determination"
    CheapShot = _("위크포인트 어택")  # "Cheap Shot"
    KeenEye = _("베이직 디텍션")  # "Keen Eye"
    # 4th Job
    ChainArtsThrashIV = _("체인아츠:스트로크 최종 강화")  # "Chain Arts: Thrash IV"
    SummonBrick = _("서먼 스트라이킹 브릭")  # "Summon Brick"
    SummonSpikedBat = _("서먼 비팅 니들배트")  # "Summon Spiked Bat"
    ChainArtsReignofChains = _("체인아츠:터프 허슬")  # "Chain Arts: Reign of Chains"
    ChainArtsBeatdown = _("체인아츠:테이크다운")  # "Chain Arts: Beatdown"
    NovaWarrior = _("노바의 용사")  # "Nova Warrior"
    MuscleMemoryIII = _("웨폰 버라이어티 III")  # "Muscle Memory III"
    CheapShotII = _("위크포인트 컨버징 어택")  # "Cheap Shot II"
    WeaponsExpert = _("웨폰 엑스퍼트")  # "Weapons Expert"
    WisdomofShadowsII = _("퀵서비스 마인드 Ⅱ")  # "Wisdom of Shadows II"
    # Hypers
    ChainArtsCrush = _("체인아츠:크러시")  # "Chain Arts: Crush"
    ShadowdealersElixir = _("상인단 특제 비약")  # "Shadowdealer's Elixir"
    VeteranShadowdealer = _("프로페셔널 에이전트")  # "Veteran Shadowdealer"
    # 5th Job
    VenomBurst = _("베놈 버스트")  # "Venom Burst"
    ChainArtsVoidStrike = _("체인아츠:퓨리")  # "Chain Arts: Void Strike"
    ApocalypseCannon = _("A.D 오드넌스")  # "Apocalypse Cannon"
    ChainArtsMaelstrom = _("체인아츠:메일스트롬")  # "Chain Arts: Maelstrom"
    MuscleMemoryFinale = _("웨폰 버라이어티 피날레")  # "Muscle Memory Finale"


######   Passive Skill   ######
class WeaponVarietyStackWrapper(core.StackSkillWrapper):
    def __init__(self, _max, prof_agent, final_attack, use_prof_agent_attack):
        super(WeaponVarietyStackWrapper, self).__init__(core.BuffSkill(_("{}(스택)").format(CadenaSkills.MuscleMemoryIII), 0, 99999999), _max)
        self.currentWeapon = None
        self.use_final_attack = core.OptionalElement(final_attack.is_available, final_attack, name=_("{}(쿨타임)").format(CadenaSkills.MuscleMemoryIII))
        self.use_prof_agent_attack = use_prof_agent_attack
        self.prof_agent = prof_agent
        self.modifierInvariantFlag = False

    def vary(self, weapon):
        self.currentWeapon = weapon
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname=self.skill.name, spec='graph control')

    def get_modifier(self):
        multiplier = 11
        if self.prof_agent.is_active():
            multiplier *= 2
        return core.CharacterModifier(pdamage_indep=8*multiplier)

    def _changed(self, weapon):
        return self.currentWeapon != weapon

    def stackController(self, weapon):
        task = core.Task(self, partial(self.vary, weapon))
        taskHolder = core.TaskHolder(task, name=_("웨버 스택"))
        taskHolder.onAfter(self.use_final_attack)
        taskHolder.onAfter(self.use_prof_agent_attack)
        conditionalTask = core.OptionalElement(partial(self._changed, weapon), taskHolder, name=_("무기 교체"))
        return conditionalTask


class MaelstromWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, tick):
        self.tick_list = [840, 120, 180, 270, 390, 540, 720, 930, 1170, 1440, 1740, 99999999]
        self.currentTick = len(self.tick_list)
        self.reuseTick = tick
        skill = core.SummonSkill(CadenaSkills.ChainArtsMaelstrom, 540, 0, 300+12*vEhc.getV(3, 2), 4, 8540).isV(vEhc, 3, 2)
        super(MaelstromWrapper, self).__init__(skill)

    def check_use(self):
        return self.currentTick >= self.reuseTick

    def _use(self, skill_modifier):
        result = super(MaelstromWrapper, self)._use(skill_modifier)
        self.tick = self.tick_list[0]
        self.currentTick = 1
        return result

    def _useTick(self):
        result = super(MaelstromWrapper, self)._useTick()
        self.currentTick += 1
        return result

    def get_delay(self) -> float:
        return self.tick_list[self.currentTick]


def comboBuilder(name, skill_list):
    combo = core.DamageSkill(name, 0, 0, 0).wrap(core.DamageSkillWrapper)
    for sk in skill_list:
        combo.onAfter(sk)

    delaySum = 0
    cnst_list = []
    for sk in skill_list:
        if DynamicVariableOperation.reveal_argument(sk.skill.cooltime) > 0:
            cnst_list += [core.ConstraintElement(sk._id + _("(쿨타임)"), sk, partial(sk.is_cooltime_left, delaySum, -1))]
        delaySum += DynamicVariableOperation.reveal_argument(sk.skill.delay)

    for cnst in cnst_list:
        combo.onConstraint(cnst)

    return combo


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 11
        self.jobtype = "LUK2"
        self.jobname = _("카데나")
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'reuse', 'mess')  # Temporarily use the first line of boring, change it when implementing reuse. 임시로 보공 첫줄 사용, 재사용 구현시 변경.
        self.preEmptiveSkills = 1

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        CollectingForLeap = core.InformedCharacterModifier(CadenaSkills.UncannyLuck, stat_main=50)

        PhisicalTraining = core.InformedCharacterModifier(CadenaSkills.PhysicalTraining, stat_main=30, stat_sub=30)
        QuickserviceMind = core.InformedCharacterModifier(CadenaSkills.WisdomofShadows, att=10, crit_damage=5, crit=10)

        BasicDetection = core.InformedCharacterModifier(CadenaSkills.KeenEye, armor_ignore=20)

        WeaponMastery = core.InformedCharacterModifier(CadenaSkills.WeaponsExpert, att=30+passive_level, crit=30+passive_level, crit_damage=15+ceil(passive_level/2))
        QuickserviceMind_II = core.InformedCharacterModifier(CadenaSkills.WisdomofShadowsII, att=30, crit_damage=5, crit=10)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 2, 3)

        return [CollectingForLeap, PhisicalTraining,
                QuickserviceMind, BasicDetection, WeaponMastery, QuickserviceMind_II, ReadyToDiePassive]

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore=30, crit_damage=44, pdamage=20, crit=6)

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep=30)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90+ceil(passive_level/2))

        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        """
        Non-Chain Arts-Reinforce, Boss Killer
        Chain Arts Stroke-Next Attack Reinforce, Reinforce

        Chain Arts: Takedown-Cool Time Reduce

        Nose order:
        Stroke, Variety, Hustle-Needle Bat-Brick-Shotgun/Spring-Crush/Agent-Scimitar/Claw-Knife/Wing Dagger-Takedown

        Skill enhancement order:
        Fury-Aude-Burst-Mel-Retouda

        1 stroke cancellation 150ms
        Cancel 180ms

        Summon Throwing Wing Dagger explode after 3 strokes

        Scimitar, shotgun, knife, brick, needle bat 1 stroke and wing dagger 1 tick receive 15% final damage.

        Bomb-Brick / Shotgun-Claw / Knife / Wing Dagger / Bat / Scimitar-Chase / Mailstrom once every 4 seconds

        논체인아츠-리인포스, 보스킬러
        체인아츠스트로크-넥스트어택 리인포스, 리인포스

        체인아츠:테이크다운-쿨타임 리듀스

        코강순서:
        스트로크,버라이어티,허슬 - 니들배트 - 브릭 - 샷건/봄 - 크러시/에이전트 - 시미터/클로 - 나이프/윙대거 - 테이크다운

        스킬강화순서:
        퓨리-오드-버스트-멜-레투다

        1타캔슬 150ms
        캔슬 180ms

        서먼 스로잉 윙대거 3타 후 폭발

        시미터, 샷건, 나이프, 브릭, 니들배트 1타, 윙대거 1틱은 최종뎀 15%를 받고 있음.

        봄-브릭 / 샷건-클로 / 나이프 / 윙대거 / 배트 / 시미터-체이스 / 메일스트롬 4초당 1회
        """

        STROKE1_HIT_RATE = 1
        STROKE1_CANCEL_TIME = 150
        CANCEL_TIME = 180
        WINGDAGGER_HIT = 3

        passive_level = chtr.get_base_modifier().passive_level + self.combat
        CheapShotII = core.CharacterModifier(crit=2, crit_damage=10+ceil(passive_level/4))  # Weekpoint Converging Attack. 위크포인트 컨버징 어택.
        CheapShotIIBleed = core.DotSkill(_("{}(출혈)").format(CadenaSkills.CheapShotII), 0, 1000, 110+2*passive_level, 1, 99999999).wrap(core.DotSkillWrapper)
        CheapShotIIBleedBuff = core.BuffSkill(_("{}(출혈)(디버프)").format(CadenaSkills.CheapShotII), 0, 99999999, crit=CheapShotII.crit, crit_damage=CheapShotII.crit_damage).wrap(core.BuffSkillWrapper)
        CheapShotIIAdventureMageBuff = core.BuffSkill(_("{}(모법링크)").format(CadenaSkills.CheapShotII), 0, 99999999, crit=CheapShotII.crit, crit_damage=CheapShotII.crit_damage).wrap(core.BuffSkillWrapper)

        # buff. 버프.
        Booster = core.BuffSkill(CadenaSkills.WeaponBooster, 0, 200000).wrap(core.BuffSkillWrapper)
        SpecialPotion = core.BuffSkill(CadenaSkills.ShadowdealersElixir, 570, 60*1000, pdamage=10, crit=10, cooltime=120*1000).wrap(core.BuffSkillWrapper)  # Only Cadena has a delay. 카데나만 딜레이있음.

        ProfessionalAgent = core.BuffSkill(CadenaSkills.VeteranShadowdealer, 570, 30000, cooltime=180000).wrap(core.BuffSkillWrapper)
        ProfessionalAgentAdditionalDamage = core.DamageSkill(_("{}(공격)").format(CadenaSkills.VeteranShadowdealer), 0, 255, 3).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ProfessionalAgent_Attack = core.OptionalElement(ProfessionalAgent.is_active, ProfessionalAgentAdditionalDamage, name=_("{} 추가타").format(CadenaSkills.VeteranShadowdealer))

        # Add weapon variety. 웨폰버라이어티 추가타.
        WeaponVarietyAttack = core.DamageSkill(CadenaSkills.MuscleMemoryIII, 0, 350+15*passive_level, 4, cooltime=250).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        WeaponVariety = WeaponVarietyStackWrapper(11, ProfessionalAgent, WeaponVarietyAttack, ProfessionalAgent_Attack)

        # Chain Arts. 체인아츠.
        ChainArts_Stroke_1 = core.DamageSkill(_("{}(1타)").format(CadenaSkills.ChainArtsThrashIV), 210, 150, 2 * STROKE1_HIT_RATE, modifier=core.CharacterModifier(pdamage=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        ChainArts_Stroke_1_Cancel = core.DamageSkill(_("{}(1타)(캔슬)").format(CadenaSkills.ChainArtsThrashIV), STROKE1_CANCEL_TIME, 150, 2 * STROKE1_HIT_RATE, modifier=core.CharacterModifier(pdamage=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        ChainArts_Stroke_2 = core.DamageSkill(_("{}(2타)").format(CadenaSkills.ChainArtsThrashIV), 390, 400, 5, modifier=core.CharacterModifier(pdamage=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        ChainArts_Stroke_2_Cancel = core.DamageSkill(_("{}(2타)(캔슬)").format(CadenaSkills.ChainArtsThrashIV), CANCEL_TIME, 400, 5, modifier=core.CharacterModifier(pdamage=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        ChainArts_Chais = core.DamageSkill(CadenaSkills.ChainArtsPursuit, 150, 100, 1).wrap(core.DamageSkillWrapper)
        ChainArts_Crush = core.DamageSkill(CadenaSkills.ChainArtsCrush, 750, 510, 15, cooltime=30000).setV(vEhc, 4, 2, True).wrap(core.DamageSkillWrapper)  # unused. 미사용.

        # ChainArts_ToughHustleInit = core.DamageSkill("체인아츠:터프허슬", 0, 0, 0, cooltime=50000).setV(vEhc, 0, 2, False)  # Persistent. 지속형.
        # ChainArts_ToughHustle = core.DamageSkill("체인아츠:터프허슬", 5000000, 600 + 7 * self.combat, 2).setV(vEhc, 0, 2, False)  # Lasting, 6 seconds, unused. 지속형, 6초, 미사용.

        ChainArts_Takedown_Init = core.DamageSkill(CadenaSkills.ChainArtsBeatdown, 4080, 300+3*self.combat, 2, cooltime=(150-30)*1000, red=True).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        ChainArts_Takedown_Attack = core.DamageSkill(_("{}(연속 공격)").format(CadenaSkills.ChainArtsBeatdown), 2970, 990+15*self.combat, 15, modifier=core.CharacterModifier(armor_ignore=80)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        ChainArts_Takedown_Wave = core.DamageSkill(_("{}(파동)").format(CadenaSkills.ChainArtsBeatdown), 0, 600+5*self.combat, 4).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)  # 8 repetitions. 8회 반복.
        ChainArts_Takedown_Final = core.DamageSkill(_("{}(최종)").format(CadenaSkills.ChainArtsBeatdown), 0, 500, 10, modifier=core.CharacterModifier(armor_ignore=80)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        ChainArts_Takedown_Bind = core.BuffSkill(_("{}(바인드)").format(CadenaSkills.ChainArtsBeatdown), 0, 10000, crit=CheapShotII.crit, crit_damage=CheapShotII.crit_damage, cooltime=-1).wrap(core.BuffSkillWrapper)

        # Non-chain arts skills. 논체인아츠 스킬.

        SummonCuttingSimiter = core.DamageSkill(CadenaSkills.SummonScimitar, CANCEL_TIME, 425 + 5 * passive_level, 5, cooltime=4000, red=True, modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20, pdamage_indep=15)).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        SummonScratchingClaw = core.DamageSkill(CadenaSkills.SummonClaw, CANCEL_TIME, 455 + 5 * passive_level, 4, cooltime=3000, red=True, modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20)).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)

        SummonThrowingWingdagger = core.DamageSkill(CadenaSkills.SummonShuriken, 780, 0, 0, cooltime=10000, red=True, modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20)).wrap(core.DamageSkillWrapper)
        SummonThrowingWingdaggerSummon = core.SummonSkill(_("{}(소환)").format(CadenaSkills.SummonShuriken), 0, 330, 425 + 5 * passive_level, 1, 330*WINGDAGGER_HIT, cooltime=-1, modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20, pdamage_indep=15 / WINGDAGGER_HIT)).setV(vEhc, 6, 2, False).wrap(core.SummonSkillWrapper)
        SummonThrowingWingdaggerEnd = core.DamageSkill(_("{}(폭발)").format(CadenaSkills.SummonShuriken), 0, 670 + 5 * passive_level, 3, cooltime=-1, modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20)).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)

        SummonShootingShotgun = core.DamageSkill(CadenaSkills.SummonShotgun, CANCEL_TIME, 510 + 5 * passive_level, 7, cooltime=5000, red=True, modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20, pdamage_indep=15)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        SummonSlachingKnife = core.DamageSkill(CadenaSkills.SummonDaggers, CANCEL_TIME, 435 + 5 * passive_level, 8, cooltime=10000, red=True, modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20, pdamage_indep=15)).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        SummonSlachingKnife_Horror = core.BuffSkill(_("{}(공포)").format(CadenaSkills.SummonDaggers), 0, 10000, armor_ignore=30, crit=CheapShotII.crit, crit_damage=CheapShotII.crit_damage, cooltime=-1).wrap(core.BuffSkillWrapper)

        SummonReleasingBoom = core.DamageSkill(CadenaSkills.SummonDecoyBomb, CANCEL_TIME, 0, 0, cooltime=8000, red=True).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        SummonReleasingBoom_Explode = core.DamageSkill(_("{}(폭발)").format(CadenaSkills.SummonDecoyBomb), 0, 535 + 5 * passive_level, 6, cooltime=-1, modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        SummonStrikingBrick = core.DamageSkill(CadenaSkills.SummonBrick, 390+CANCEL_TIME-STROKE1_CANCEL_TIME, 485 + 8*self.combat, 7, cooltime=8000, red=True, modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20, pdamage_indep=15)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        # Forced movement 390ms, explosion 360ms (cancellable), 1 stroke can be used during forced movement, so 1 stroke delay is subtracted. 강제이동 390ms, 폭발 360ms(캔슬가능), 강제이동 도중 1타 사용 가능하므로 1타 딜레이만큼 뺌.

        SummonBeatingNeedlebat_1 = core.DamageSkill(_("{}(1타)").format(CadenaSkills.SummonSpikedBat), 360, 450 + 10 * self.combat, 6, modifier=core.CharacterModifier(pdamage=35+20, boss_pdamage=20, pdamage_indep=15), cooltime=12000, red=True).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        SummonBeatingNeedlebat_2 = core.DamageSkill(_("{}(2타)").format(CadenaSkills.SummonSpikedBat), 420, 555 + 10 * self.combat, 7, modifier=core.CharacterModifier(pdamage=35+20, boss_pdamage=20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        SummonBeatingNeedlebat_3 = core.DamageSkill(_("{}(3타)").format(CadenaSkills.SummonSpikedBat), CANCEL_TIME, 715 + 10 * self.combat, 8, modifier=core.CharacterModifier(pdamage=45+20, boss_pdamage=20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        SummonBeatingNeedlebat_Honmy = core.BuffSkill(_("{}(혼미)").format(CadenaSkills.SummonSpikedBat), 0, 15000, crit=CheapShotII.crit, crit_damage=CheapShotII.crit_damage, cooltime=-1).wrap(core.BuffSkillWrapper)

        # 5th. 5차.
        VenomBurst = core.DotSkill(ThiefSkills.VenomBurst, 0, 1000, 160+6*vEhc.getV(4, 4), 1, 99999999).isV(vEhc, 4, 4).wrap(core.DotSkillWrapper)
        VenomBurst_Poison = core.BuffSkill(_("{}(중독)").format(ThiefSkills.VenomBurst), 0, 99999999, crit=CheapShotII.crit, crit_damage=CheapShotII.crit_damage, cooltime=-1).isV(vEhc, 4, 4).wrap(core.BuffSkillWrapper)

        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 2, 3)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        NovaGoddessBless = nova.NovaGoddessBlessWrapper(vEhc, 0, 0)

        ChainArts_Fury = core.BuffSkill(CadenaSkills.ChainArtsVoidStrike, 420, (35+vEhc.getV(0, 0))*1000, cooltime=(180-vEhc.getV(0, 0))*1000, red=True).isV(vEhc, 0, 0).wrap(core.BuffSkillWrapper)
        ChainArts_Fury_Damage = core.DamageSkill(_("{}(공격)").format(CadenaSkills.ChainArtsVoidStrike), 0, 250+10*vEhc.getV(0, 0), 6, cooltime=600).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        AD_Odnunce = core.SummonSkill(CadenaSkills.ApocalypseCannon, 360, 270, 225+9*vEhc.getV(1, 1), 5, 10000, cooltime=25000, red=True).isV(vEhc, 1, 1).wrap(core.SummonSkillWrapper)  # 37*5타
        AD_Odnunce_Final = core.DamageSkill(_("{}(막타)").format(CadenaSkills.ApocalypseCannon), 0, 750+30*vEhc.getV(1, 1), 8, cooltime=-1).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)

        ChainArts_Maelstorm = MaelstromWrapper(vEhc, 8)
        ChainArts_Maelstorm_Slow = core.BuffSkill(_("{}(중독)").format(CadenaSkills.ChainArtsMaelstrom), 0, 4000+6000, crit=CheapShotII.crit, crit_damage=CheapShotII.crit_damage, cooltime=-1).isV(vEhc, 3, 2).wrap(core.BuffSkillWrapper)

        WeaponVarietyFinale = core.StackableDamageSkillWrapper(core.DamageSkill(CadenaSkills.MuscleMemoryFinale, 0, 250+10*vEhc.getV(0, 0), 7*4, cooltime=11000).isV(vEhc, 0, 0), 3)
        WeaponVarietyFinaleTrigger = core.StackSkillWrapper(core.BuffSkill(_("{}(웨버횟수)").format(CadenaSkills.MuscleMemoryFinale), 0, 99999999), 4)

        ######   Skill Wrapper   ######

        # Basic linkage connection. 기본 연계 연결.
        # ChainArts_ToughHustleInit.onAfter(ChainArts_ToughHustle) No tough hustle. 터프허슬 미사용.
        ChainArts_Takedown_Init.onBefore(ChainArts_Takedown_Bind)
        ChainArts_Takedown_Init.onAfter(ChainArts_Takedown_Attack)
        ChainArts_Takedown_Init.onAfter(core.RepeatElement(ChainArts_Takedown_Wave, 8))
        ChainArts_Takedown_Init.onAfter(ChainArts_Takedown_Final)

        SummonThrowingWingdagger.onAfter(SummonThrowingWingdaggerSummon)
        SummonThrowingWingdaggerSummon.onAfter(SummonThrowingWingdaggerEnd.controller(330*WINGDAGGER_HIT))

        SummonSlachingKnife.onAfter(SummonSlachingKnife_Horror)
        SummonReleasingBoom.onAfter(SummonReleasingBoom_Explode.controller(1000))  # Explosion after 1 second. 1초 후 폭발.

        VenomBurst.onAfter(VenomBurst_Poison)

        ChainArts_Fury_Use = core.OptionalElement(lambda : ChainArts_Fury_Damage.is_available() and ChainArts_Fury.is_active(), ChainArts_Fury_Damage, name=_("{} 발동조건").format(CadenaSkills.ChainArtsVoidStrike))

        AD_Odnunce.onEventEnd(AD_Odnunce_Final)
        ChainArts_Maelstorm.onAfter(ChainArts_Maelstorm_Slow)

        # Calling weapon variety. 웨폰 버라이어티 호출.
        SummonCuttingSimiter.onAfter(WeaponVariety.stackController(_("시미터")))
        SummonScratchingClaw.onAfter(WeaponVariety.stackController(_("클로")))
        SummonThrowingWingdaggerSummon.onTick(WeaponVariety.stackController(_("윙대거")))
        SummonThrowingWingdaggerEnd.onAfter(WeaponVariety.stackController(_("윙대거")))

        SummonShootingShotgun.onAfter(WeaponVariety.stackController(_("샷건")))
        SummonSlachingKnife.onAfter(WeaponVariety.stackController(_("나이프")))
        SummonReleasingBoom_Explode.onAfter(WeaponVariety.stackController(_("봄")))
        SummonStrikingBrick.onAfter(WeaponVariety.stackController(_("브릭")))

        SummonBeatingNeedlebat_1.onAfter(WeaponVariety.stackController(_("배트")))
        SummonBeatingNeedlebat_1.onAfter(SummonBeatingNeedlebat_2)
        SummonBeatingNeedlebat_2.onAfter(WeaponVariety.stackController(_("배트")))
        SummonBeatingNeedlebat_2.onAfter(SummonBeatingNeedlebat_3)
        SummonBeatingNeedlebat_3.onAfter(WeaponVariety.stackController(_("배트")))
        SummonBeatingNeedlebat_3.onAfter(SummonBeatingNeedlebat_Honmy)

        # Weapon Variety Finale. 웨폰 버라이어티 피날레.
        WeaponVarietyFinale.onAfter(WeaponVarietyFinaleTrigger.stackController(-4))
        WeaponVarietyAttack.onAfter(WeaponVarietyFinaleTrigger.stackController(1))
        WeaponVarietyAttack.onAfter(core.OptionalElement(lambda: WeaponVarietyFinaleTrigger.judge(4, 1) and WeaponVarietyFinale.is_available(), WeaponVarietyFinale, name="웨버피 발동조건"))

        Reduce2sec = WeaponVarietyFinale.controller(2000, 'reduce_cooltime')
        Reduce1sec = WeaponVarietyFinale.controller(1000, 'reduce_cooltime')
        ChainArts_Fury_Damage.onAfter(Reduce1sec)
        ChainArts_Crush.onAfter(Reduce2sec)
        ChainArts_Takedown_Init.onAfter(Reduce2sec)
        ChainArts_Takedown_Attack.onAfter(Reduce2sec)
        ChainArts_Takedown_Wave.onAfter(Reduce2sec)
        ChainArts_Takedown_Final.onAfter(Reduce2sec)

        # Cadena damage cycle combo. 카데나 딜 사이클 콤보.

        # Pyeongtaek. 평타.
        NormalAttack = core.DamageSkill(_("평타"), 0, 0, 0).wrap(core.DamageSkillWrapper)
        for i in [ChainArts_Stroke_1, ChainArts_Stroke_2]:
            NormalAttack.onAfter(i)

        # Shotgun-Claw. 샷건-클로.
        ShootgunClawCombo = comboBuilder(_("샷건-클로"), [ChainArts_Stroke_1_Cancel, SummonShootingShotgun, ChainArts_Stroke_1, ChainArts_Stroke_2_Cancel, SummonScratchingClaw])

        # Scimitar-Chase. 시미터 - 체이스.
        SimiterChaseCombo = comboBuilder(_("시미터-체이스"), [ChainArts_Stroke_1_Cancel, SummonCuttingSimiter, ChainArts_Chais])

        # knife. 나이프.
        KnifeCombo = comboBuilder(_("나이프"), [ChainArts_Stroke_1_Cancel, SummonSlachingKnife])

        # Spring-Brick. 봄-브릭.
        BommBrickCombo = comboBuilder(_("봄브릭"), [ChainArts_Stroke_1_Cancel, SummonReleasingBoom, ChainArts_Stroke_1_Cancel, SummonStrikingBrick])

        # Wing Dagger. 윙대거.
        WingDaggerCombo = comboBuilder(_("윙대거"), [ChainArts_Stroke_1_Cancel, SummonThrowingWingdagger])

        # Bat. 배트.
        BatCombo = comboBuilder(_("배트"), [ChainArts_Stroke_1_Cancel, SummonBeatingNeedlebat_1])

        # Mailstrom. 메일스트롬.
        MaleStromCombo = core.DamageSkill(_("메일스트롬"), 0, 0, 0).wrap(core.DamageSkillWrapper)
        for i in [ChainArts_Stroke_1, ChainArts_Stroke_2_Cancel, ChainArts_Maelstorm]:
            MaleStromCombo.onAfter(i)

        for c in [core.ConstraintElement(_("메일스트롬"), ChainArts_Maelstorm, ChainArts_Maelstorm.check_use)]:
            MaleStromCombo.onConstraint(c)

        # Chain Arts-Fury interlocking. 체인아츠 - 퓨리 연동.
        # TODO: Fury, Tough Hustle added to the activation of additional professional strokes. 퓨리, 프로페셔널 추가타 발동에 터프허슬 추가.
        for s in [ChainArts_Stroke_1, ChainArts_Stroke_2, ChainArts_Stroke_1_Cancel, ChainArts_Stroke_2_Cancel,
                  SummonCuttingSimiter, SummonScratchingClaw, SummonShootingShotgun, SummonSlachingKnife, ChainArts_Chais, SummonThrowingWingdaggerEnd,
                  ChainArts_Takedown_Init, ChainArts_Takedown_Attack, ChainArts_Takedown_Wave, ChainArts_Takedown_Final, ChainArts_Crush,
                  SummonReleasingBoom, SummonStrikingBrick, SummonBeatingNeedlebat_1, SummonBeatingNeedlebat_2, SummonBeatingNeedlebat_3, MirrorBreak]:
            s.onAfter(ChainArts_Fury_Use)

        for s in [SummonThrowingWingdaggerSummon, ChainArts_Maelstorm]:
            s.onTick(ChainArts_Fury_Use)

        # Add a professional agent. 프로페셔널 에이전트 추가타.
        for s in [ChainArts_Stroke_1, ChainArts_Stroke_2, ChainArts_Stroke_1_Cancel, ChainArts_Stroke_2_Cancel,
                  SummonCuttingSimiter, SummonScratchingClaw, SummonShootingShotgun, SummonSlachingKnife, ChainArts_Chais, SummonThrowingWingdaggerEnd,
                  SummonReleasingBoom, SummonStrikingBrick, SummonBeatingNeedlebat_1, SummonBeatingNeedlebat_2, SummonBeatingNeedlebat_3, ChainArts_Crush,
                  ChainArts_Takedown_Init, ChainArts_Takedown_Attack, ChainArts_Takedown_Wave, ChainArts_Takedown_Final,
                  ChainArts_Maelstorm, ChainArts_Fury_Damage]:
            s.onAfter(ProfessionalAgent_Attack)

        for s in [SummonThrowingWingdaggerSummon]:
            s.onTick(ProfessionalAgent_Attack)

        for s in [ChainArts_Fury_Damage, SummonShootingShotgun, SummonScratchingClaw,
                  SummonCuttingSimiter, SummonSlachingKnife,
                  SummonReleasingBoom, SummonStrikingBrick,
                  SummonBeatingNeedlebat_1, SummonThrowingWingdagger, ChainArts_Maelstorm, WeaponVarietyAttack, WeaponVarietyFinale]:
            s.protect_from_running()

        return(NormalAttack,
               [globalSkill.maple_heros(chtr.level, name=CadenaSkills.NovaWarrior, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                WeaponVariety, Booster, SpecialPotion, ProfessionalAgent,
                ReadyToDie, ChainArts_Fury, NovaGoddessBless,
                SummonSlachingKnife_Horror, SummonBeatingNeedlebat_Honmy, VenomBurst_Poison, ChainArts_Maelstorm_Slow,
                globalSkill.soul_contract(), CheapShotIIBleed, CheapShotIIBleedBuff, CheapShotIIAdventureMageBuff] +
               [SummonReleasingBoom_Explode, SummonThrowingWingdaggerEnd, AD_Odnunce_Final] +
               [WingDaggerCombo, BatCombo, BommBrickCombo, ShootgunClawCombo, SimiterChaseCombo, KnifeCombo, MaleStromCombo, ChainArts_Crush, MirrorBreak, MirrorSpider] +
               [WeaponVarietyAttack, SummonThrowingWingdaggerSummon, VenomBurst, AD_Odnunce, ChainArts_Maelstorm] +
               [ChainArts_Fury_Damage, WeaponVarietyFinale, SummonShootingShotgun, SummonScratchingClaw,
                SummonCuttingSimiter, SummonSlachingKnife,
                SummonReleasingBoom, SummonStrikingBrick,
                SummonBeatingNeedlebat_1, SummonThrowingWingdagger] +
               [NormalAttack])
