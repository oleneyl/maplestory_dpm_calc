from dpmModule.jobs.jobbranch.pirates import PirateSkills
from dpmModule.jobs.jobclass.flora import FloraSkills, LEF
from .globalSkill import GlobalSkills, BUFF, INIT, LINK, SUBSEQUENT_HIT, SUMMON, ENDING, TICK, STACK
from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule, ConditionRule
from . import globalSkill
from .jobbranch import pirates
from .jobclass import flora
from . import jobutils
from math import ceil
from typing import Any, Dict

from localization.utilities import translator
_ = translator.gettext

# English skill information for Ark here https://maplestory.fandom.com/wiki/Ark/Skills
class ArkSkills:
    # Link Skill
    Solus = _("무아")  # "Solus"
    # Beginner
    ContactCaravan = _("컨택트 카라반")  # "Contact Caravan"
    MagicConversion = _("매직 서킷")  # "Magic Conversion"
    # 1st Job
    SpecterState = _("스펙터 잠식")  # "Specter State"
    OminousNightmare = _("잊혀지지 않는 악몽")  # "Ominous Nightmare"
    OminousDream = _("잊혀지지 않는 흉몽")  # "Ominous Dream"
    BasicChargeDrive = _("플레인 차지드라이브")  # "Basic Charge Drive"
    SpellBullets = _("스펠 불릿")  # "Spell Bullets"
    MysticLeap = _("미스틱 리프")  # "Mystic Leap"
    InstinctualLeap = _("인스팅트 리프")  # "Instinctual Leap"
    MysticArtsMastery = _("미스틱 아츠 마스터리")  # "Mystic Arts Mastery"
    # 2nd Job
    MasterCorruption = _("잠식 제어")  # "Master Corruption"
    ScarletChargeDrive = _("스칼렛 차지드라이브")  # "Scarlet Charge Drive"
    GrievousWound = _("지워지지 않는 상처")  # "Grievous Wound"
    UnstoppableImpulse = _("멈출 수 없는 충동")  # "Unstoppable Impulse"
    TenaciousInstinct = _("멈출 수 없는 본능")  # "Tenacious Instinct"
    ImpendingDeath = _("다가오는 죽음")  # "Impending Death"
    KnuckleBooster = _("너클 부스터")  # "Knuckle Booster"
    KnuckleMastery = _("너클 마스터리")  # "Knuckle Mastery"
    InitateFusion = _("융합 개시")  # "Initate Fusion"
    PhysicalTraining = _("피지컬 트레이닝")  # "Physical Training"
    # 3rd Job
    VividNightmare = _("되살아나는 악몽")  # "Vivid Nightmare"
    VividDream = _("되살아나는 흉몽")  # "Vivid Dream"
    GustChargeDrive = _("거스트 차지드라이브")  # "Gust Charge Drive"
    InsatiableHunger = _("채워지지 않는 굶주림")  # "Insatiable Hunger"
    CreepingTerror = _("기어 다니는 공포")  # "Creeping Terror"
    VengefulHate = _("돌아오는 증오")  # "Vengeful Hate"
    MysticArtsTraining = _("미스틱 아츠 트레이닝")  # "Mystic Arts Training"
    InnateArtsTraining = _("인스팅트 아츠 트레이닝")  # "Innate Arts Training"
    AdvancedFusion = _("융합 진행")  # "Advanced Fusion"
    # 4th Job
    EndlessNightmare = _("끝나지 않는 악몽")  # "Endless Nightmare"
    EndlessDream = _("끝나지 않는 흉몽")  # "Endless Dream"
    AbyssalChargeDrive = _("어비스 차지드라이브")  # "Abyssal Charge Drive"
    UnbridledChaos = _("걷잡을 수 없는 혼돈")  # "Unbridled Chaos"
    BlissfulRestraint = _("황홀한 구속")  # "Blissful Restraint"
    HerooftheFlora = _("레프의 용사")  # "Hero of the Flora"
    KnuckleExpert = _("너클 엑스퍼트")  # "Knuckle Expert"
    AdvancedMysticArts = _("어드밴스드 미스틱 아츠")  # "Advanced Mystic Arts"
    AdvancedInnateArts = _("어드밴스드 인스팅트 아츠")  # "Advanced Innate Arts"
    CompleteFusion = _("융합 완성")  # "Complete Fusion"
    BattleFrenzy = _("전투 광란")  # "Battle Frenzy"
    # Hypers
    ChargeSpellAmplifier = _("차지 스펠 앰플리피케이션")  # "Charge Spell Amplifier"
    EndlessAgony = _("끝없는 고통")  # "Endless Agony"
    DivineWrath = _("레이스 오브 갓")  # "Divine Wrath"
    # 5th Job
    AbyssalRecall = _("근원의 기억")  # "Abyssal Recall"
    InfinitySpell = _("인피니티 스펠")  # "Infinity Spell"
    DeviousNightmare = _("새어 나오는 악몽")  # "Devious Nightmare"
    DeviousDream = _("새어 나오는 흉몽")  # "Devious Dream"
    EndlesslyStarvingBeast = _("영원히 굶주리는 짐승")  # "Endlessly Starving Beast"


# Skill name modifiers only for Ark
TERM_CONNECT = _("종결,연계")
TRIGGER = _("등장")


# TODO: Move to core, make it available with .wrap(). core쪽으로 옮길 것, .wrap()과 함께 사용 가능하게 할 것.
class MultipleDamageSkillWrapper(core.DamageSkillWrapper):
    def __init__(self, skill, _max, timeLimit):
        self._timeLimit = timeLimit            
        self.timer = self._timeLimit
        self._max = _max
        self.count = 0   
        super(MultipleDamageSkillWrapper, self).__init__(skill)
        
    def _use(self, skill_modifier):
        self.count += 1
        self.timer = self._timeLimit
        if self.count >= self._max:
            self.count = 0
        return super(MultipleDamageSkillWrapper, self)._use(skill_modifier)

    def spend_time(self, time):
        self.timer -= time
        if self.timer <= 0:
            self.count = 0
        super(MultipleDamageSkillWrapper, self).spend_time(time)

    def is_available(self) -> bool:
        if self.count > 0:
            return True
        return super(MultipleDamageSkillWrapper, self).is_available()
        

class DeviousWrapper(core.DamageSkillWrapper):
    def __init__(self, skill):
        self.reduceDict = set()
        super(DeviousWrapper, self).__init__(skill)
    
    def _reduceCooltime(self, time, skillId):
        if skillId not in self.reduceDict:
            self.cooltimeLeft -= time
            self.reduceDict.add(skillId)

        return self._result_object_cache

    def reduceCooltime(self, time, skillId):
        task = core.Task(self, partial(self._reduceCooltime, time, skillId))
        return core.TaskHolder(task)

    def _use(self, skill_modifier):
        self.reduceDict = set()
        return super(DeviousWrapper, self)._use(skill_modifier)

class SpecterWrapper(core.BuffSkillWrapper):
    def __init__(self, memoryBuff, endlessBuff):
        skill = core.BuffSkill(_("스펙터 상태"), 0, 9999999, att = 30, cooltime = -1)
        self.gauge = 800
        self.memoryBuff = memoryBuff
        self.endlessBuff = endlessBuff
        self.schedule = None
        self.cooldown = 0
        self.lockdown = 0
        super(SpecterWrapper, self).__init__(skill)
        self.onoff = False
        self.stopwatch = 0

    def is_active(self):
        return self.onoff

    def spend_time(self, time):
        """
        The gauge is updated every 1020ms, it fluctuates by +13 in the Lev state and -23 in the Specter state.
        Specter Encroachment-Increases recovery by 10% when using Extra Healing.
        State transition through encroachment control has a cooldown of 3 seconds.
        Spirit is not consumed for 30 seconds after the start of the memory of the source, and 3 seconds for the endless pain keydown.

        1020ms마다 게이지가 갱신되며, 레프 상태에서는 +13, 스펙터 상태에서는 -23씩 변동.
        스펙터 잠식-엑스트라 힐링 사용 시 회복량 10% 증가.
        잠식 제어를 통한 상태 전환은 3초의 쿨타임이 있음.
        근원의 기억 시작 후 30초, 끝없는 고통 키다운 3초간은 정신력 소모되지 않음.
        """
        self.cooldown -= time
        self.lockdown -= time
        self.stopwatch += time
        if self.onoff:
            if self.memoryBuff.is_not_active() and self.endlessBuff.is_not_active():
                self.gauge = max(self.gauge - 23 * time / 1020, 0)
        else:
            if self.lockdown <= 0:
                self.gauge = min(self.gauge + 13 * 1.1 * time / 1020, 1000) # 하이퍼 엑스트라 힐링 적용

        if self.gauge <= 0:
            self.setExhausted()
        else:
            onoff = self.schedule(self.gauge, self.stopwatch)
            if self.onoff != onoff and self.cooldown <= 0:
                self.onoff = onoff
                self.stopwatch = 0
                self.cooldown = 3000

    def setExhausted(self):
        self.onoff = False
        self.gauge = 0
        self.cooldown = 20000
        self.lockdown = 20000
        raise ValueError("The Gauge is exhausted. Fix schedule.") # 게이지 고갈시 에러 발생. 고갈을 허용하고 싶으면 제거.

    def advanced(self):
        self.gauge -= 48
        if self.gauge <= 0:
            self.setExhausted()
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, _("잠식-어드밴스드 효과 적용"), spec = 'graph control')

    def advancedController(self):
        task = core.Task(self, self.advanced)
        return core.TaskHolder(task, name = _("정신력 추가 소모"))

    def registerSchedule(self, schedule):
        self.schedule = schedule

    def setOnoff(self, onoff):
        if self.onoff != onoff:
            self.onoff = onoff
            self.stopwatch = 0
        return self._result_object_cache
    
    def onoffController(self, onoff):
        return core.TaskHolder(core.Task(self, partial(self.setOnoff, onoff)), name = _("상태 변경"))
        
    def judge(self, gauge, direction):
        if (self.gauge-gauge)*direction>=0:return True
        else: return False
    
class AmplifiedSpellBuffWrapper(core.BuffSkillWrapper):
    def __init__(self, skill, csa_timeLeft):
        self.csa_timeLeft = csa_timeLeft
        super(AmplifiedSpellBuffWrapper, self).__init__(skill)

    def _use(self, skill_modifier) -> core.ResultObject:
        self.timeLeft = self.csa_timeLeft()
        self.cooltimeLeft = self.calculate_cooltime(skill_modifier)
        delay = self.get_delay()
        callbacks = self.create_callbacks(skill_modifier=skill_modifier, duration=self.timeLeft)
        return core.ResultObject(delay, core.CharacterModifier(), 0, 0, 
                                sname = self.skill.name, 
                                spec = self.skill.spec, 
                                kwargs = {"remain" : self.timeLeft},
                                callbacks=callbacks)                     

class JobGenerator(ck.JobGenerator):
    def __init__(self, vEhc = None):
        super(JobGenerator, self).__init__(vEhc = vEhc)
        self.jobtype = "STR"
        self.jobname = _("아크")
        self.vEnhanceNum = 12
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'mess')
        self.preEmptiveSkills = 2

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(crit=20, pdamage=71, boss_pdamage=53, armor_ignore=29.6)

    def get_ruleset(self):
        ruleset = RuleSet()

        ruleset.add_rule(ConditionRule(ArkSkills.InfinitySpell, ArkSkills.AbyssalRecall, lambda x:x.is_cooltime_left(0, 1)), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(f"{FloraSkills.ConversionOverdrive}({BUFF})", ArkSkills.InfinitySpell), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(f"{FloraSkills.GrandisGoddessBlessing}({LEF})", f"{FloraSkills.ConversionOverdrive}({BUFF})"), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(f"{ArkSkills.EndlesslyStarvingBeast}({INIT})", ArkSkills.InfinitySpell, lambda x:x.is_cooltime_left(80000, 1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(ArkSkills.EndlessAgony, ArkSkills.InfinitySpell, lambda x:x.is_cooltime_left(40000, 1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(GlobalSkills.TermsAndConditions, f"{ArkSkills.EndlesslyStarvingBeast}({INIT})", lambda x:x.is_cooltime_left(60000, 1)), RuleSet.BASE)

        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        # 매직 서킷: 앱솔 기준 15.4
        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        
        MagicCircuit = core.InformedCharacterModifier(ArkSkills.MagicConversion, att = WEAPON_ATT * 0.1)  #무기 마력의 25%, 최대치 가정.
        MisticArtsMastery = core.InformedCharacterModifier(ArkSkills.MysticArtsMastery, att = 20)
        NuckleMastery = core.InformedCharacterModifier(ArkSkills.KnuckleMastery, att = 20)
        PhisicalTraining = core.InformedCharacterModifier(ArkSkills.PhysicalTraining, stat_main = 60)
        FusionProgress = core.InformedCharacterModifier(ArkSkills.AdvancedFusion, pdamage_indep = 10, crit = 20)
        NuckleExpret = core.InformedCharacterModifier(ArkSkills.KnuckleExpert, att = 30 + passive_level, crit_damage= 30 + passive_level)
        FusionComplete = core.InformedCharacterModifier(ArkSkills.CompleteFusion, att = 40 + passive_level, crit = 10 + ceil(passive_level/3), armor_ignore = 30 + passive_level, boss_pdamage = 30 + passive_level)
        BattleRage = core.InformedCharacterModifier(ArkSkills.BattleFrenzy, pdamage_indep = 20 + passive_level)
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 3, 4)
    
        return [MagicCircuit, MisticArtsMastery, 
                                    NuckleMastery, PhisicalTraining, 
                                    FusionProgress, NuckleExpret, FusionComplete, BattleRage, LoadedDicePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90+ceil((chtr.get_base_modifier().passive_level + self.combat)/2))
        
        return [WeaponConstant, Mastery]        
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        When linked, Plane Charge Drive 540 → 240ms, Unending Nightmare 540 → 180ms
        Each +30ms is applied to 270ms and 210ms.

        Automatic use of spell bullets

        Hyper: Battle Arts-Reinforce, Boss Killer, Ignor Guard / Extra Healing, Enhance

        5th order of importance

        Infinity Fell-Spirit Hunger-Dexterity-Source-Loaded-Maserful

        5th reinforcement

        Death Coming/Hate Coming Back-Unending Nightmare/Smoky Dream-Plane Charge Drive-Fear/Redemption/Pain
        -Scarlet/Wound-Gust/Hunger-Abyss/Confusion-Impulse/Instinct

        연계 시 플레인 차지드라이브 540 → 240ms, 끝나지 않는 흉몽 540 → 180ms
        각각 +30ms 적용해 270ms, 210ms로 적용됨

        스펠 불릿 자동 사용
        
        하이퍼 : 배틀아츠-리인포스, 보스킬러, 이그노어 가드 / 엑스트라 힐링, 인핸스
        
        5차 중요도 순서
        
        인피니티스펠 -  영굶짐 - 새악흉 - 근원 - 로디드 - 매서풀
        
        5차 강화 
        
        다가오는 죽음/돌아오는 증오 - 끝나지 않는 악몽/흉몽 - 플레인 차지드라이브 - 공포/구속/고통 
        - 스칼렛/상처 - 거스트/굶주림 - 어비스/혼돈 - 충동/본능
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        LINK_DELAY = 30
        BattleArtsHyper = core.CharacterModifier(pdamage=20, boss_pdamage=20, armor_ignore=20)  # 하이퍼 - 배틀아츠 modifier


        # Buff skills
        ContactCaravan = core.BuffSkill(ArkSkills.ContactCaravan, 720, 300 * 1000, cooltime = 600 * 1000, pdamage = 2 + 1).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill(ArkSkills.KnuckleBooster, 0, 200 * 1000).wrap(core.BuffSkillWrapper)
        

        # 일반 공격들        
        EndlessNightmare_Link = core.DamageSkill(f"{ArkSkills.EndlessNightmare}({LINK})".format(), 540, 440 + 3*passive_level, 6, cooltime = 2000, red=True, modifier=BattleArtsHyper).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        PlainChargeDrive = core.DamageSkill(ArkSkills.BasicChargeDrive, 540, 610 + 3*passive_level, 3, modifier=BattleArtsHyper).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        PlainChargeDrive_Link = core.DamageSkill(f"{ArkSkills.BasicChargeDrive}({LINK})", 240+LINK_DELAY, 610 + 3*passive_level, 3, modifier=BattleArtsHyper).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        PlainSpell = core.DamageSkill(_("플레인 스펠"), 0, 370 + 3*passive_level, 2).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        PlainBuff = core.BuffSkill(_("플레인 버프"), 0, 60 * 1000, cooltime = -1).wrap(core.BuffSkillWrapper)  # Not used because it does not affect dpm. dpm에 영향을 주지 않아 미사용.
        
        ScarletChargeDrive = core.DamageSkill(ArkSkills.ScarletChargeDrive, 540, 350 + 3*passive_level, 3, cooltime = 3000, red=True, modifier=BattleArtsHyper).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletChargeDrive_Link = core.DamageSkill(f"{ArkSkills.ScarletChargeDrive}({LINK})", 510, 350 + 3*passive_level, 3, cooltime = 3000, red=True, modifier=BattleArtsHyper).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletChargeDrive_After = core.DamageSkill(f"{ArkSkills.ScarletChargeDrive}({SUBSEQUENT_HIT})", 0, 350 + 3*passive_level, 3, modifier=BattleArtsHyper).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletSpell = core.DamageSkill(_("스칼렛 스펠"), 0, 220 + passive_level, 5).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletBuff = core.BuffSkill(_("스칼렛 버프"), 0, 60 * 1000, cooltime = -1, rem=True, att = 30, crit = 20).wrap(core.BuffSkillWrapper)
        
        UnstoppableImpulse_Link = core.DamageSkill(f"{ArkSkills.UnstoppableImpulse}({LINK})", 540, 435 + 3*passive_level, 5, cooltime = -1, modifier=BattleArtsHyper).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)

        GustChargeDrive_Link = core.DamageSkill(f"{ArkSkills.GustChargeDrive}({LINK})", 450, 400 + 3*passive_level, 6, cooltime = 5000, red=True, modifier=BattleArtsHyper).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        GustSpell = core.DamageSkill(_("거스트 스펠(접촉)"), 0, 1 + 30 + passive_level, 1).wrap(core.DamageSkillWrapper)
        GustSpellAttack = core.DamageSkill(_("거스트 스펠"), 0, 230 + passive_level, 4, cooltime = -1).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        GustBuff = core.BuffSkill(_("거스트 버프"), 0, 60*1000, cooltime = -1).wrap(core.BuffSkillWrapper) # dpm에 영향을 주지 않아 미사용
        
        AbyssChargeDrive_Link = core.DamageSkill(f"{ArkSkills.AbyssalChargeDrive}({LINK})", 630, 340 + 3*self.combat, 4, cooltime = 9000, red=True, modifier=BattleArtsHyper).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        AbyssChargeDrive_After = core.DamageSkill(f"{ArkSkills.AbyssalChargeDrive}({SUBSEQUENT_HIT})", 0, 410 + 3*self.combat, 6, modifier=BattleArtsHyper).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        AbyssSpell = core.DamageSkill(_("어비스 스펠(접촉)"), 0, 1, 1).wrap(core.DamageSkillWrapper)
        AbyssSpellSummon = core.SummonSkill(_("어비스 스펠"), 0, 300, 70 + 2*self.combat, 2, 3900, cooltime = -1).setV(vEhc, 6, 2, False).wrap(core.SummonSkillWrapper)  # 13 hit
        AbyssBuff = core.BuffSkill(_("어비스 버프"), 0, 60*1000, cooltime = -1, rem=True, pdamage = 20 + self.combat//2, boss_pdamage = 30 + self.combat, armor_ignore = 20 + self.combat//2).wrap(core.BuffSkillWrapper)

        HUMAN_SKILLS_MCF = [EndlessNightmare_Link, PlainChargeDrive, PlainChargeDrive_Link, ScarletChargeDrive, ScarletChargeDrive_Link, UnstoppableImpulse_Link,
            GustChargeDrive_Link, AbyssChargeDrive_Link, PlainSpell, ScarletSpell, GustSpell, AbyssSpell]
        
        ##### When in Specter state | 스펙터 상태일 때 #####
        UpcomingDeath = core.DamageSkill(ArkSkills.ImpendingDeath, 0, 450 + 3*passive_level, 2, cooltime = -1).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        ReturningHateStack = core.StackSkillWrapper(core.BuffSkill(f"{ArkSkills.VengefulHate}({STACK})", 0, 99999999), 12)
        ReturningHate = core.StackDamageSkillWrapper(
            core.DamageSkill(ArkSkills.VengefulHate, 0, 320 + 3*passive_level, 6, cooltime=12000, red=True).setV(vEhc, 0, 2, True),
            ReturningHateStack,
            lambda sk: sk.stack
        )

        EndlessBadDream = core.DamageSkill(ArkSkills.EndlessDream, 540, 445 + 3*passive_level, 6, modifier=BattleArtsHyper).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)  # An unending nightmare transformation. 끝나지 않는 악몽 변형.
        EndlessBadDream_Link = core.DamageSkill(f"{ArkSkills.EndlessDream}({LINK})", 180+LINK_DELAY, 445 + 3*passive_level, 6, modifier=BattleArtsHyper).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)  # An unending nightmare transformation. 끝나지 않는 악몽 변형.

        UncurableHurt_Link = core.DamageSkill(f"{ArkSkills.GrievousWound}({LINK})", 480, 510 + 3*passive_level, 6, cooltime = 3000, red=True, modifier=BattleArtsHyper).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)  # A variant of the Scarlet Charge Drive. 스칼렛 차지 드라이브의 변형.
        
        TenaciousInstinct_Link = core.DamageSkill(f"{ArkSkills.TenaciousInstinct}({LINK})", 540, 460 + 3*passive_level, 6, cooltime = -1, modifier=BattleArtsHyper).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)

        UnfulfilledHunger = core.DamageSkill(ArkSkills.InsatiableHunger, 750, 510 + 3*passive_level, 7, cooltime = 5000, red=True, modifier=BattleArtsHyper).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)  # Gust charge drive variant. 거스트 차지 드라이브 변형.
        UnfulfilledHunger_Link = core.DamageSkill(f"{ArkSkills.InsatiableHunger}({LINK})", 660, 510 + 3*passive_level, 7, cooltime = 5000, red=True, modifier=BattleArtsHyper).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        
        CrawlingFear = core.DamageSkill(ArkSkills.CreepingTerror, 30 + 630, 1290 + 3*passive_level, 15, cooltime = 60*1000, red=True, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        CrawlingFear_Link = core.DamageSkill(f"{ArkSkills.CreepingTerror}({LINK})", 30 + 360, 1290 + 3*passive_level, 15, cooltime = 60*1000, red=True, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)

        UncontrollableChaos = core.DamageSkill(ArkSkills.UnbridledChaos, 810, 440 + 3*self.combat, 12, cooltime = 9000, red=True, modifier=BattleArtsHyper).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)  # Abyss Charge Drive variant. 어비스 차지 드라이브 변형.
        UncontrollableChaos_Link = core.DamageSkill(f"{ArkSkills.UnbridledChaos}({LINK})", 720, 440 + 3*self.combat, 12, cooltime = 9000, red=True, modifier=BattleArtsHyper).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)

        RaptRestriction = core.DamageSkill(ArkSkills.BlissfulRestraint, 690, 600 + 10*self.combat, 6, cooltime = 180 * 1000, red=True, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        RaptRestrictionSummon = core.SummonSkill(f"{ArkSkills.BlissfulRestraint}({SUMMON})", 0, 450, 400 + 10*self.combat, 3, 9000, cooltime = -1, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)
        RaptRestrictionEnd = core.DamageSkill(f"{ArkSkills.BlissfulRestraint}({ENDING})", 0, 1000 + 10*self.combat, 8, cooltime = -1, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        
        Impulse_Connected = MultipleDamageSkillWrapper(core.DamageSkill(_("충동/본능 연결"), 0, 0, 0, cooltime = 6000, red=True, modifier=BattleArtsHyper).setV(vEhc, 7, 2, False), 2, 1500)

        SPECTER_SKILLS_MCF = [ReturningHate, EndlessBadDream, EndlessBadDream_Link, UncurableHurt_Link, TenaciousInstinct_Link, UnfulfilledHunger, UnfulfilledHunger_Link,
            CrawlingFear, CrawlingFear_Link, UncontrollableChaos, UncontrollableChaos_Link, RaptRestriction, RaptRestrictionSummon, RaptRestrictionEnd]
            
        # Hyper. 하이퍼.
        ChargeSpellAmplification = core.BuffSkill(ArkSkills.ChargeSpellAmplifier, 720, 60000, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)
        ScarletBuff2 = AmplifiedSpellBuffWrapper(core.BuffSkill(_("증폭된 스칼렛(버프)"), 0, 60000, cooltime = -1, att = 30, crit = 20), lambda: ChargeSpellAmplification.timeLeft)
        AbyssBuff2 = AmplifiedSpellBuffWrapper(core.BuffSkill(_("증폭된 어비스(버프)"), 0, 60000, cooltime = -1, pdamage = 20 + self.combat//2, boss_pdamage = 30 + self.combat, armor_ignore = 20 + self.combat//2), lambda: ChargeSpellAmplification.timeLeft)

        EndlessPain = core.DamageSkill(ArkSkills.EndlessAgony, 360, 0, 0, cooltime = 3030 + 60 * 1000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)   # onTick==> Coming death. onTick==> 다가오는 죽음.
        EndlessPainTick = core.DamageSkill(f"{ArkSkills.EndlessAgony}({TICK})", 180, 300, 3).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)   # 15 hits. 15타.
        EndlessPainEnd = core.DamageSkill(f"{ArkSkills.EndlessAgony}({ENDING})", 1200/5, 100*3.5, 12).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)  # Delay: 1200ms or 1050ms (when connected later). First to 1200. It repeats 5 times -> delay /5. 딜레이 : 1200ms 또는 1050ms(이후 연계 시). 일단 1200으로. 5회 반복되므로 -> 딜레이 /5.
        EndlessPainEnd_Link = core.DamageSkill(f"{ArkSkills.EndlessAgony}({TERM_CONNECT})", 1050/5, 100*3.5, 12).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        EndlessPainBuff = core.BuffSkill(f"{ArkSkills.EndlessAgony}({BUFF})", 0, 3 * 1000, cooltime = -1).wrap(core.BuffSkillWrapper)  # No mental power is consumed. 정신력 소모되지 않음.
        
        WraithOfGod = core.BuffSkill(ArkSkills.DivineWrath, 0, 60*1000, pdamage = 10, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)
        
        # 5차
        LuckyDice = core.BuffSkill(PirateSkills.LoadedDice, 0, 180*1000, pdamage = 20).isV(vEhc, 3, 4).wrap(core.BuffSkillWrapper)

        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        FloraGoddessBless = flora.FloraGoddessBlessWrapper(vEhc, 0, 0, WEAPON_ATT)
    
        MemoryOfSource = core.DamageSkill(ArkSkills.AbyssalRecall, 990, 0, 0, cooltime = 200 * 1000, red=True).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)
        MemoryOfSourceTick = core.DamageSkill(f"{ArkSkills.AbyssalRecall}({TICK})", 210, 400 + 16 * vEhc.getV(1,1), 6).wrap(core.DamageSkillWrapper)    # 43타
        MemoryOfSourceEnd = core.DamageSkill(f"{ArkSkills.AbyssalRecall}({ENDING})", 60, 1200 + 48 * vEhc.getV(1,1), 12 * 6).wrap(core.DamageSkillWrapper)
        MemoryOfSourceBuff = core.BuffSkill(f"{ArkSkills.AbyssalRecall}({BUFF})", 0, 30 * 1000, cooltime = -1).wrap(core.BuffSkillWrapper) # 정신력 소모되지 않음
                
        InfinitySpell = core.BuffSkill(ArkSkills.InfinitySpell, 720, (40 + 2*vEhc.getV(0,0)) * 1000, cooltime = 240 * 1000, red=True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        
        DeviousNightmare = core.DamageSkill(ArkSkills.DeviousNightmare, 0, 500 + 20*vEhc.getV(2,2), 9, cooltime = 10 * 1000, red=True).isV(vEhc,2,2).wrap(DeviousWrapper)
        DeviousDream = core.DamageSkill(ArkSkills.DeviousDream, 0, 600 + 24*vEhc.getV(2,2), 9, cooltime = 10 * 1000, red=True).wrap(DeviousWrapper)

        ForeverHungryBeastInit = core.DamageSkill(f"{ArkSkills.EndlesslyStarvingBeast}({INIT})", 540, 0, 0, cooltime=120*1000, red=True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ForeverHungryBeastTrigger = core.DamageSkill(f"{ArkSkills.EndlesslyStarvingBeast}({TRIGGER})", 0, 0, 0, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ForeverHungryBeast = core.DamageSkill(ArkSkills.EndlesslyStarvingBeast, 0, 400+16*vEhc.getV(0,0), 12, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper) # 20회 반복

        ### Skill Wrapper ###

        SpecterState = SpecterWrapper(MemoryOfSourceBuff, EndlessPainBuff)
        
        # Basic connection settings (spector). 기본 연결 설정(스펙터).
        for skill in [UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link]:
            skill.onBefore(EndlessBadDream_Link)
        # A skill that can also be linked in the Nightmare (Specter) and Plane (Lev). 흉몽(스펙터)과 플레인(레프)에서도 연계 가능한 스킬.
        for skill in [CrawlingFear_Link, RaptRestriction, EndlessPain, MemoryOfSource]:
            skill.onBefore(core.OptionalElement(SpecterState.is_active, EndlessBadDream_Link, PlainChargeDrive_Link))
  
        # When the boss is 1:1, 1 oncoming death is generated per attack, and when infinity spell is activated, a total of 3 to 4 are generated depending on the reinforcement level. 보스 1:1 시 공격 1회 당 다가오는 죽음 1개 생성, 인피니티 스펠 상태 시 강화레벨에 따라 총 3 ~ 4개 생성.
        UpcomingDeath_Connected = core.OptionalElement(InfinitySpell.is_active, core.RepeatElement(UpcomingDeath, 3 + vEhc.getV(0,0) // 25), UpcomingDeath)
        UpcomingDeath.onAfter(ReturningHateStack.stackController(0.2))
        ReturningHate.onJustAfter(ReturningHateStack.stackController(-15))
        

        # Basic connection settings (lev). 기본 연결 설정(레프).
        for skill in [EndlessNightmare_Link, ScarletChargeDrive_Link, GustChargeDrive_Link, AbyssChargeDrive_Link, UnstoppableImpulse_Link]:
            skill.onBefore(PlainChargeDrive_Link)
        
        # When infinity spell is in effect, the spell bullet stack is filled with 1 corresponding spell + 4 plane spells. 인피니티 스펠 상태 시 스펠 불릿 스택에는 해당 스펠 1칸 + 플레인 스펠 4칸이 채워짐.
        PlainSpell_Connected = core.OptionalElement(InfinitySpell.is_active, core.RepeatElement(PlainSpell, 5), PlainSpell)
        for skill in [ScarletSpell, GustSpell, AbyssSpell]:
            skill.onAfter(core.OptionalElement(InfinitySpell.is_active, core.RepeatElement(PlainSpell, 4)))

        for spell in [PlainSpell, ScarletSpell, GustSpellAttack, AbyssSpellSummon]:
            spell.add_runtime_modifier(InfinitySpell, lambda sk: core.CharacterModifier(pdamage = 20*sk.is_active()))

        PlainChargeDrive.onAfter(PlainSpell_Connected)
        PlainChargeDrive_Link.onAfter(PlainSpell_Connected)
        
        ScarletSpell.onAfter(ScarletBuff)
        ScarletSpell.onAfter(core.OptionalElement(ChargeSpellAmplification.is_active, ScarletBuff2))
        ScarletChargeDrive.onAfter(ScarletSpell)
        ScarletChargeDrive_Link.onAfter(ScarletSpell)
        ScarletChargeDrive.onAfter(ScarletChargeDrive_After)
        ScarletChargeDrive_Link.onAfter(ScarletChargeDrive_After)

        GustChargeDrive_Link.onAfter(GustSpell)
        GustSpell.onAfter(GustSpellAttack)
        
        AbyssSpell.onAfter(AbyssBuff)
        AbyssSpell.onAfter(AbyssSpellSummon)
        AbyssSpell.onAfter(core.OptionalElement(ChargeSpellAmplification.is_active, AbyssBuff2))
        AbyssChargeDrive_Link.onAfter(AbyssSpell)
        AbyssChargeDrive_Link.onAfter(AbyssChargeDrive_After)
        
        Impulse_Connected.onAfter(core.OptionalElement(SpecterState.is_active, TenaciousInstinct_Link, UnstoppableImpulse_Link))

        # Limits the use of nightmares and impulses while infinity spells are active. 인피니티 스펠 지속 중일 때 악몽과 충동의 사용을 제한함.
        EndlessNightmare_Link.onConstraint(core.ConstraintElement(_("악몽 사용제한"), InfinitySpell,
            lambda: InfinitySpell.is_not_active() or DeviousNightmare.is_available()))
        Impulse_Connected.onConstraint(core.ConstraintElement(_("충동 사용제한"), InfinitySpell,
            lambda: InfinitySpell.is_not_active() or SpecterState.is_active()))

        # Prevent twisting of transformation schedule due to charge spell amplification. 차지 스펠 앰플리피케이션으로 인한 변신 스케쥴 꼬임 방지.
        def SpellBuffsArePrepared(): 
            return ChargeSpellAmplification.is_not_active() or (ScarletBuff2.is_active() and AbyssBuff2.is_active())

        RaptRestriction.onConstraint(core.ConstraintElement(_("차지앰플 확인"), ChargeSpellAmplification, SpellBuffsArePrepared))
        RaptRestriction.onConstraint(core.ConstraintElement(_("게이지 150 이상"), SpecterState, partial(SpecterState.judge, 150, 1)))
        RaptRestriction.onAfter(SpecterState.onoffController(True))
        RaptRestriction.onAfter(RaptRestrictionSummon)
        RaptRestriction.onAfter(RaptRestrictionEnd.controller(9000))

        EndlessPainRepeat = core.RepeatElement(EndlessPainTick, 15)
        EndlessPainEndRepeat = core.RepeatElement(EndlessPainEnd_Link, 5)
        EndlessPainRepeat.onAfter(EndlessPainEndRepeat)
        EndlessPain.onConstraint(core.ConstraintElement(_("차지앰플 확인"), ChargeSpellAmplification, SpellBuffsArePrepared))
        EndlessPain.onConstraint(core.ConstraintElement(_("게이지 150 이상"), SpecterState, partial(SpecterState.judge, 150, 1)))
        EndlessPain.onAfter(SpecterState.onoffController(True))
        EndlessPain.onAfter(EndlessPainBuff)
        EndlessPain.onAfter(EndlessPainRepeat)
        AdditionalConsumption = core.OptionalElement(MemoryOfSourceBuff.is_not_active, SpecterState.advancedController())
        EndlessPainEndRepeat.onJustAfter(AdditionalConsumption)

        magic_curcuit_full_drive_builder = flora.MagicCircuitFullDriveBuilder(vEhc, 4, 3)
        for sk in (HUMAN_SKILLS_MCF + SPECTER_SKILLS_MCF +
            [EndlessPainTick, EndlessPainEnd, EndlessPainEnd_Link, MemoryOfSourceTick, MemoryOfSourceEnd, 
            DeviousNightmare, DeviousDream, ForeverHungryBeast, MirrorBreak]):
            magic_curcuit_full_drive_builder.add_trigger(sk)
        MagicCircuitFullDrive, MagicCircuitFullDriveStorm = magic_curcuit_full_drive_builder.get_skill()

        # Specter state final attack type connection. 스펙터 상태 파이널어택류 연계.
        for skill in [EndlessBadDream, EndlessBadDream_Link, DeviousDream,
            UnfulfilledHunger, UncontrollableChaos, 
            UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link,
            CrawlingFear_Link, EndlessPainTick, EndlessPainEnd, EndlessPainEnd_Link, ForeverHungryBeast]:
            skill.onAfter(UpcomingDeath_Connected)
        MagicCircuitFullDriveStorm.onAfter(core.OptionalElement(SpecterState.is_active, UpcomingDeath_Connected))
        MirrorBreak.onAfter(core.OptionalElement(SpecterState.is_active, UpcomingDeath_Connected))
        
        # 5th-Leaking Nightmare / Nightmare Connection. 5차 - 새어나오는 악몽 / 흉몽 연계.
        EndlessNightmare_Link.onAfter(core.OptionalElement(DeviousNightmare.is_available, DeviousNightmare))
        EndlessBadDream.onAfter(core.OptionalElement(DeviousDream.is_available, DeviousDream))
        EndlessBadDream_Link.onAfter(core.OptionalElement(DeviousDream.is_available, DeviousDream))

        for skills, _id in [([ScarletChargeDrive, ScarletChargeDrive_Link], _("스칼렛")),
                            ([GustChargeDrive_Link], _("거스트")),
                            ([AbyssChargeDrive_Link], _("어비스"))]:
            for skill in skills:
                skill.onAfter(DeviousNightmare.reduceCooltime(1000, _id))
        for skills, _id in [([UncurableHurt_Link], _("상처")),
                            ([UnfulfilledHunger_Link, UnfulfilledHunger], _("굶주림")),
                            ([UncontrollableChaos_Link, UncontrollableChaos], _("혼돈")),
                            ([TenaciousInstinct_Link], _("본능")),
                            ([CrawlingFear_Link, CrawlingFear], _("공포"))]:
            for skill in skills:
                skill.onAfter(DeviousDream.reduceCooltime(1000, _id))

        # 5th-The beast that hungers forever. 5차 - 영원히 굶주리는 짐승.
        ForeverHungryBeastInit.onConstraint(core.ConstraintElement(_("차지앰플 확인"), ChargeSpellAmplification, SpellBuffsArePrepared))
        ForeverHungryBeastInit.onConstraint(core.ConstraintElement(_("게이지 250 이상"), SpecterState, partial(SpecterState.judge, 250, 1)))
        ForeverHungryBeastInit.onAfter(SpecterState.onoffController(True))
        ForeverHungryBeastInit.onAfter(ForeverHungryBeastTrigger.controller(6000)) # Appears after 6 seconds. 6초 후 등장. TODO: The default 9600+1740ms will decrease the time for each Specter skill hit. 기본 9600+1740ms에 스펙터 스킬 적중시마다 시간 줄어들도록 할것.
        ForeverHungryBeastTrigger.onAfter(core.RepeatElement(ForeverHungryBeast, 20))
        
        # Basic Attack: 540ms neutral skill. 기본 공격 : 540ms 중립스킬.
        PlainAttack = core.DamageSkill(_("기본 공격"), 0, 0, 0).wrap(core.DamageSkillWrapper)
        PlainAttack.onAfter(core.OptionalElement(SpecterState.is_active, EndlessBadDream, PlainChargeDrive))
        
        # Adding Constraint: Lev Mode. Constraint 추가하기 : 레프 모드.
        for skill in [PlainChargeDrive, PlainChargeDrive_Link, ScarletChargeDrive, ScarletChargeDrive_Link,
                EndlessNightmare_Link, GustChargeDrive_Link, AbyssChargeDrive_Link, UnstoppableImpulse_Link]:
            skill.onConstraint(core.ConstraintElement(_("레프 모드"), SpecterState, SpecterState.is_not_active))
        
        # Adding Constraint: Specter Mode. Constraint 추가하기 : 스펙터 모드.
        for skill in [EndlessBadDream, UnfulfilledHunger, UncontrollableChaos, ReturningHate,
                EndlessBadDream_Link, UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link]:
            skill.onConstraint(core.ConstraintElement(_("스펙터 모드"), SpecterState, SpecterState.is_active))

        CrawlingFear.onConstraint(core.ConstraintElement(_("차지앰플 확인"), ChargeSpellAmplification, SpellBuffsArePrepared))
        CrawlingFear_Link.onConstraint(core.ConstraintElement(_("차지앰플 확인"), ChargeSpellAmplification, SpellBuffsArePrepared))
        CrawlingFear.onConstraint(core.ConstraintElement(_("게이지 150 이상"), SpecterState, partial(SpecterState.judge, 150, 1)))
        CrawlingFear_Link.onConstraint(core.ConstraintElement(_("게이지 150 이상"), SpecterState, partial(SpecterState.judge, 150, 1)))
        CrawlingFear.onAfter(SpecterState.onoffController(True))
        CrawlingFear_Link.onAfter(SpecterState.onoffController(True))
        CrawlingFear.onJustAfter(AdditionalConsumption)
        CrawlingFear_Link.onJustAfter(AdditionalConsumption)
        
        MemoryOfSource.onConstraint(core.ConstraintElement(_("차지앰플 확인"), ChargeSpellAmplification, SpellBuffsArePrepared))
        MemoryOfSourceRepeat = core.RepeatElement(MemoryOfSourceTick, 43)
        MemoryOfSourceRepeat.onAfter(MemoryOfSourceEnd)
        MemoryOfSource.onAfter(SpecterState.onoffController(True))
        MemoryOfSource.onAfter(MemoryOfSourceBuff)
        MemoryOfSource.onAfter(MemoryOfSourceRepeat)

        def schedule(gauge, stopwatch):
            """
            Specter <-> Responsible for scheduling the LEV status.
            Returning True converts it to Specter, returning False converts it to LEV.
            스펙터 <-> 레프 상태 스케쥴링을 담당합니다.
            True를 리턴하면 스펙터, False를 리턴하면 레프 상태로 변환합니다.
            """
            if (ChargeSpellAmplification.is_active() and (ScarletBuff2.is_not_active() or AbyssBuff2.is_not_active()))\
                or (AbyssBuff.is_not_active() and AbyssChargeDrive_Link.is_available())\
                or (ScarletBuff.is_not_active() and ScarletChargeDrive_Link.is_available()):
                return False
            if ForeverHungryBeastInit.is_available() and gauge < 300:
                return False
            if ForeverHungryBeastTrigger.is_cooltime_left(6001, -1):
                return True
            if MemoryOfSourceBuff.is_active():
                return True

            # Gauge consumption is given priority while infinity spell is ongoing. 인피니티 스펠 지속 중일 때 게이지 소모를 우선.
            if InfinitySpell.is_active():
                if gauge <= 200:
                    return False
                elif gauge <= 500:
                    if SpecterState.is_active() and stopwatch >= 4680:
                        return False
                else:
                    if SpecterState.is_active() and stopwatch >= 10590:
                        return False
                return True
            # Prioritizes gauge recovery when infinity spell is not ongoing. 인피니티 스펠 지속 중이 아닐 때 게이지 회복을 우선.
            else:   
                if gauge > 800:
                    return True
                elif gauge > 700:
                    if SpecterState.is_not_active() and stopwatch >= 10350:
                        return True
                else:
                    if SpecterState.is_not_active() and stopwatch >= 17850:
                        return True
                return False

        SpecterState.registerSchedule(schedule)

        ScarletBuff.set_disabled_and_time_left(0)  # Assumes starting a deal with a Scarlet/Abyss buff. 스칼렛/어비스 버프가 있는 채로 딜 시작하는 것을 가정함.
        AbyssBuff.set_disabled_and_time_left(0)

        DeviousNightmare.protect_from_running()
        DeviousDream.protect_from_running()

        return(
            PlainAttack, 
            [
                globalSkill.maple_heros(chtr.level, name = ArkSkills.HerooftheFlora, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                ContactCaravan, Booster, LuckyDice, ScarletBuff, AbyssBuff, SpecterState, ScarletBuff2, AbyssBuff2,
                ChargeSpellAmplification, WraithOfGod, InfinitySpell, MagicCircuitFullDrive, FloraGoddessBless, Overdrive, 
                MemoryOfSourceBuff, EndlessPainBuff,
                globalSkill.soul_contract()
            ]
            + [RaptRestrictionEnd, ForeverHungryBeastTrigger]  # reserved task, use as early as possible
            + [
                MemoryOfSource, RaptRestriction, ReturningHate, ForeverHungryBeastInit, CrawlingFear_Link, 
                EndlessNightmare_Link, ScarletChargeDrive_Link, GustChargeDrive_Link, AbyssChargeDrive_Link, 
                UncurableHurt_Link, UnfulfilledHunger_Link, Impulse_Connected, UncontrollableChaos_Link, EndlessPain, 
                GustSpellAttack, AbyssSpellSummon, RaptRestrictionSummon, DeviousNightmare, DeviousDream, MirrorBreak, MirrorSpider
            ]
            + [MagicCircuitFullDriveStorm]
            + [PlainAttack]
        )