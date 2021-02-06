from enum import Enum

from dpmModule.jobs.globalSkill import GlobalSkills
from dpmModule.jobs.jobclass.adventurer import AdventurerSkills

from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import ConcurrentRunRule, RuleSet, SynchronizeRule, InactiveRule, DisableRule
from . import globalSkill
from functools import partial
from .jobclass import adventurer
from .jobbranch import magicians
from math import ceil
from typing import Any, Dict


# English skill information for Bishop here https://maplestory.fandom.com/wiki/Bishop/Skills
class BishopSkills(Enum):
    # Link SKill
    EmpiricalKnowledge = 'Empirical Knowledge | 임피리컬 널리지'
    # 1st Job
    EnergyBolt = 'Energy Bolt | 에너지 볼트'
    MagicGuard = 'Magic Guard | 매직 가드'
    Teleport = 'Teleport | 텔레포트'
    MagicArmor = 'Magic Armor | 매직 아머'
    MPBoost = 'MP Boost | MP 증가'
    # 2nd Job
    HolyArrow = 'Holy Arrow | 홀리 애로우'
    BlessedEnsemble = 'Blessed Ensemble | 블레싱 앙상블'
    Heal = 'Heal | 힐'
    Bless = 'Bless | 블레스'
    MagicBooster = 'Magic Booster | 매직 부스터'
    Invincible = 'Invincible | 인빈서블'
    SpellMastery = 'Spell Mastery | 스펠 마스터리'
    HighWisdom = 'High Wisdom | 하이 위즈덤'
    MPEater = 'MP Eater | MP 이터'
    # 3rd Job
    ShiningRay = 'Shining Ray | 샤이닝 레이'
    HolyFountain = 'Holy Fountain | 홀리 파운틴'
    DivineProtection = 'Divine Protection | 디바인 프로텍션'
    MysticDoor = 'Mystic Door | 미스틱 도어'
    Dispel = 'Dispel | 디스펠'
    HolySymbol = 'Holy Symbol | 홀리 심볼'
    TeleportMastery = 'Teleport Mastery | 텔레포트 마스터리'
    HolyMagicShell = 'Holy Magic Shell | 홀리 매직쉘'
    ArcaneOverdrive = 'Arcane Overdrive | 매직 크리티컬'
    HolyFocus = 'Holy Focus | 홀리 포커스'
    # 4th Job
    AngelRay = 'Angel Ray | 엔젤레이'
    Genesis = 'Genesis | 제네시스'
    BigBang = 'Big Bang | 빅뱅'
    BlessedHarmony = 'Blessed Harmony | 블레싱 하모니'
    Resurrection = 'Resurrection | 리저렉션'
    Bahamut = 'Bahamut | 바하뮤트'
    AdvancedBlessing = 'Advanced Blessing | 어드밴스드 블레스'
    BuffMastery = 'Buff Mastery | 마스터 매직'
    ArcaneAim = 'Arcane Aim | 아케인 에임'
    # Hypers
    HeavensDoor = 'Heaven\'s Door | 헤븐즈도어'
    EpicAdventure = 'Epic Adventure | 에픽 어드벤쳐'
    RighteouslyIndignant = 'Righteously Indignant | 벤전스 오브 엔젤'
    # 5th Job
    Benediction = 'Benediction | 프레이'
    AngelofBalance = 'Angel of Balance | 엔젤 오브 리브라'
    Peacemaker = 'Peacemaker | 피스메이커'
    DivinePunishment = 'Divine Punishment | 디바인 퍼니시먼트'


class PrayWrapper(core.BuffSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        super(PrayWrapper, self).__init__(core.BuffSkill(BishopSkills.Benediction.value, 360, 1000 * (30 + vEhc.getV(num1,num2) // 2), cooltime = 180 * 1000, red = True).isV(vEhc, num1, num2))
        self.enable_referring_runtime_context()
        self.stat = None
        self.modifierInvariantFlag = False

    def _use(self, skill_modifier, runtime_context_modifier):
        self.stat = runtime_context_modifier.stat_main * (1 + 0.01 * runtime_context_modifier.pstat_main) + runtime_context_modifier.stat_main_fixed
        return super(PrayWrapper, self)._use(skill_modifier)

    def get_modifier(self):
        if self.is_active():
            return core.CharacterModifier(pdamage_indep = 5 + min(self.stat // 2500, 45))
        else:
            return self.disabledModifier

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = (0, 40)
        self.jobtype = "INT"
        self.jobname = "비숍"
        self.vEnhanceNum = 8
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'crit', 'boss_pdamage')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(SynchronizeRule(GlobalSkills.TermsAndConditions.value, AdventurerSkills.Infinity.value, 35000, -1), RuleSet.BASE)
        ruleset.add_rule(SynchronizeRule(BishopSkills.Benediction.value, AdventurerSkills.Infinity.value, 45000, -1), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(AdventurerSkills.UnreliableMemory.value, AdventurerSkills.Infinity.value), RuleSet.BASE)
        ruleset.add_rule(DisableRule(BishopSkills.Heal.value), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=43)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        HighWisdom = core.InformedCharacterModifier(BishopSkills.HighWisdom.value,stat_main = 40)
        SpellMastery = core.InformedCharacterModifier(BishopSkills.SpellMastery.value,att = 10)
        
        MagicCritical = core.InformedCharacterModifier(BishopSkills.ArcaneOverdrive.value,crit = 30, crit_damage = 13)
        HolyFocus = core.InformedCharacterModifier(BishopSkills.HolyFocus.value,crit = 40)
        
        MasterMagic = core.InformedCharacterModifier(BishopSkills.BuffMastery.value,att = 30 + passive_level * 3, buff_rem = 50 + passive_level * 5)
        ArcaneAim = core.InformedCharacterModifier(BishopSkills.ArcaneAim.value, armor_ignore = 20)
        
        VengenceOfAngelOff = core.InformedCharacterModifier(f"{BishopSkills.RighteouslyIndignant.value}(off)",pdamage = 40)

        UnstableMemorizePassive = adventurer.UnstableMemorizePassiveWrapper(vEhc, 4, 4)
        
        return [HighWisdom, SpellMastery, MagicCritical, HolyFocus, MasterMagic, ArcaneAim, VengenceOfAngelOff, UnstableMemorizePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -2.5)       
        BlessingEnsemble = core.InformedCharacterModifier(BishopSkills.BlessedEnsemble.value,pdamage_indep = 3)

        ArcaneAim = core.InformedCharacterModifier(BishopSkills.ArcaneAim.value,pdamage = 40 + ceil(passive_level / 2))
        VengenceOfAngelOn = core.InformedCharacterModifier(f"{BishopSkills.RighteouslyIndignant.value}(on)", att = 50, pdamage_indep = 30, armor_ignore = 20, pdamage=-40, prop_ignore=10)
        AngelRayArmorIgnore = core.InformedCharacterModifier(f"{BishopSkills.AngelRay.value}(IED | 방깎)", armor_ignore = (10 + ceil(self.combat / 3)) * 4)
        return [WeaponConstant, Mastery, ArcaneAim, VengenceOfAngelOn, BlessingEnsemble, AngelRayArmorIgnore]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        ######   Skill   ###### 
        '''
        Libra ON
        Server rack 3 seconds
        Peacemaker 3 hits

        Unstable Memorise is used when Infinity is off
        The fray is used in a way that ends when the infi ends.
        Soul contract is used in line with the end of Infi
        Libra is used every cool time

        리브라 ON
        서버렉 3초
        피스메이커 3히트
        
        언스테이블 메모라이즈는 인피니티가 꺼져있을때 사용
        프레이는 인피가 종료될 때 같이 종료되도록 맞추어서 사용
        소울 컨트랙트는 인피 마지막과 맞춰서 사용
        리브라는 쿨마다 사용
        '''
        SERVERLAG = 3
        PEACEMAKER_HIT = 3

        #Buff skills
        Booster = core.BuffSkill(BishopSkills.MagicBooster.value, 0, 240000, rem = True).wrap(core.BuffSkillWrapper)
        AdvancedBless = core.BuffSkill(BishopSkills.AdvancedBlessing.value, 0, 240000, att = 30 + self.combat*1 + 20, boss_pdamage = 10, rem = True).wrap(core.BuffSkillWrapper)
        Heal = core.BuffSkill(BishopSkills.Heal.value, 600, 2000, cooltime=4000, pdamage_indep=10, red=True).wrap(core.BuffSkillWrapper)
        Infinity = adventurer.InfinityWrapper(self.combat)
        EpicAdventure = core.BuffSkill(BishopSkills.EpicAdventure.value, 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        Pray = PrayWrapper(vEhc, 2, 2)
        
        #Damage Skills
        AngelRay = core.DamageSkill(BishopSkills.AngelRay.value, 630, 225 + 5*self.combat, 14).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)  # Vengeance use assumptions. 벤전스 사용 가정.
        
        HeavensDoor = core.DamageSkill(BishopSkills.HeavensDoor.value, 270, 1000, 8, cooltime = 180 * 1000).wrap(core.DamageSkillWrapper)

        PeaceMakerInit = core.DamageSkill(f"{BishopSkills.Peacemaker.value}(cast | 시전)", 750, 0, 0, cooltime = 10 * 1000, red = True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        PeaceMaker = core.DamageSkill(BishopSkills.Peacemaker.value, 0, 350 + 14*vEhc.getV(0,0), 4, cooltime = -1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        PeaceMakerFinal = core.DamageSkill(f"{BishopSkills.Peacemaker.value}(Explosion | 폭발)", 0, 350 + 14*vEhc.getV(0,0), 12, cooltime = -1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        PeaceMakerFinalBuff = core.BuffSkill(f"{BishopSkills.Peacemaker.value}(buff | 버프)", 0, (8 + SERVERLAG)*1000, pdamage = (5 + vEhc.getV(0,0) // 5) + (12 - PEACEMAKER_HIT), cooltime = -1).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)

        DivinePunishmentInit = core.DamageSkill(f"{BishopSkills.DivinePunishment.value}(cast | 개시)", 240, 0, 0, cooltime=85000).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        DivinePunishmentTick = core.DamageSkill(f"{BishopSkills.DivinePunishment.value}(tick | 키다운)", 240, 175+7*vEhc.getV(0,0), 5+5, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
    
        #Summoning skill
        Bahamutt = core.SummonSkill(BishopSkills.Bahamut.value, 0, 3030, 170+2*self.combat, 3, 90 * 1000, cooltime = 120 * 1000, rem = True).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)    # Delay 0 as it is automatically summoned at the end of the final Dem 25% stack and Libra ends. 최종뎀25%스택, 리브라 종료시 자동소환 되므로 딜레이 0.
        AngelOfLibra = core.SummonSkill(BishopSkills.AngelofBalance.value, 540, 4020, 500 + 20*vEhc.getV(3,1), 12, 30 * 1000, cooltime = 120 * 1000, red=True).isV(vEhc,3,1).wrap(core.SummonSkillWrapper)    # 50% final damage stack. 최종뎀50%스택.
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        #Unstable Memorize skills
        EnergyBolt = core.DamageSkill(BishopSkills.EnergyBolt.value, 660, 309, 1).wrap(core.DamageSkillWrapper)
        HolyArrow = core.DamageSkill(BishopSkills.HolyArrow.value, 660, 518, 1).wrap(core.DamageSkillWrapper)
        ShiningRay = core.DamageSkill(BishopSkills.ShiningRay.value, 690, 254, 4).wrap(core.DamageSkillWrapper)
        HolyFountain = core.DamageSkill(BishopSkills.HolyFountain.value, 960, 0, 0).wrap(core.DamageSkillWrapper)
        Dispell = core.DamageSkill(BishopSkills.Dispel.value, 900, 0, 0).wrap(core.DamageSkillWrapper)
        DivineProtection = core.DamageSkill(BishopSkills.DivineProtection.value, 870, 0, 0).wrap(core.DamageSkillWrapper)
        Genesis = core.DamageSkill(BishopSkills.Genesis.value, 630, 820, 6, cooltime=45000, red=True).wrap(core.DamageSkillWrapper)
        BigBang = core.DamageSkill(BishopSkills.BigBang.value, 630, 480+6*self.combat, 4).wrap(core.DamageSkillWrapper)
        Resurrection = core.DamageSkill(BishopSkills.Resurrection.value, 900, 0, 0).wrap(core.DamageSkillWrapper)

        VengenceOfAngel_Delay = core.DamageSkill(f"{BishopSkills.RighteouslyIndignant.value}(delay | 딜레이)", 480, 0, 0).wrap(core.DamageSkillWrapper)
        
        ######   Wrappers    ######
        #Unstable Memorize
        UnstableMemorize = adventurer.UnstableMemorizeWrapper(vEhc, 4, 4, chtr.get_skill_modifier())
        UnstableMemorize.onAfter(VengenceOfAngel_Delay)  # Vengeance OFF (Delay 0)-Unstable-Vengeance ON (Delay 480). 벤전스 OFF(딜레이 0) - 언스테이블 - 벤전스 ON(딜레이 480).
        
        for sk, weight in [(EnergyBolt, 1), (HolyArrow, 10), (Heal, 10), (ShiningRay, 10),
                            (HolyFountain, 10), (Dispell, 25), (DivineProtection, 10), (AngelRay, 25), (Genesis, 25),
                            (BigBang, 25), (Resurrection, 25), (Infinity, 25), (Bahamutt, 25), (HeavensDoor, 10), (EpicAdventure, 10)]:
            UnstableMemorize.add_skill(sk, weight)
            
        # Sacred Mark Control
        SacredMark = core.StackSkillWrapper(core.BuffSkill("Sacred Mark | 소환수 표식", 0, 999999 * 1000), 50)
        Bahamutt.onTick(SacredMark.stackController(25, name="Mark | 표식(25%)", dtype="set"))
        AngelOfLibra.onTick(SacredMark.stackController(50, name="Mark | 표식(50%)", dtype="set"))

        for sk in [HolyArrow, ShiningRay, Genesis, BigBang, AngelRay, PeaceMaker, PeaceMakerFinal, DivinePunishmentTick]:
            sk.onJustAfter(SacredMark.stackController(0, name="Mark | 표식(Consumption | 소모)", dtype="set"))
            sk.add_runtime_modifier(SacredMark, lambda skill: core.CharacterModifier(pdamage_indep = skill.stack))
        
        # Peace Maker
        PeaceMakerRepeat = core.RepeatElement(PeaceMaker, PEACEMAKER_HIT)
        PeaceMakerInit.onAfter(PeaceMakerRepeat)
        PeaceMakerRepeat.onAfter(PeaceMakerFinal)
        PeaceMakerFinal.onAfter(PeaceMakerFinalBuff)
        
        # Libra - Bahamutt exclusive
        AngelOfLibra.onAfter(Bahamutt.controller(1))
        Bahamutt.onConstraint(core.ConstraintElement("Cannot be used with Libra | 리브라와 동시사용 불가", AngelOfLibra, AngelOfLibra.is_not_active))

        # Divine Punishment
        DivinePunishmentInit.onAfter(core.RepeatElement(DivinePunishmentTick, 33))

        # Overload Mana
        overload_mana_builder = magicians.OverloadManaBuilder(vEhc, 1, 4)
        for sk in [AngelRay, Genesis, BigBang, HeavensDoor, AngelOfLibra, PeaceMaker, PeaceMakerFinal, DivinePunishmentTick,
                    EnergyBolt, HolyArrow, ShiningRay]:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()
        
        return(AngelRay, 
                [Booster, SacredMark, Infinity, PeaceMakerFinalBuff, Pray, EpicAdventure, OverloadMana,
                globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_wind_booster(), AdvancedBless, Heal,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()] +\
                [PeaceMakerInit] +\
                [AngelOfLibra, Bahamutt, HeavensDoor, DivinePunishmentInit, MirrorBreak, MirrorSpider] +\
                [UnstableMemorize] +\
                [AngelRay])