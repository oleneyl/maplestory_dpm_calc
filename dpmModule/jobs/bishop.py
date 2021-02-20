import os

from typing import Any, Dict
from enum import Enum

from dpmModule.jobs.globalSkill import GlobalSkills
from dpmModule.jobs.jobclass.adventurer import AdventurerSkills

from . import globalSkill
from ..kernel import core
from .jobclass import adventurer
from .jobbranch import magicians
from ..character import characterKernel
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, SynchronizeRule, InactiveRule, DisableRule


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
        super(PrayWrapper, self).__init__(core.BuffSkill(BishopSkills.Benediction.value, 360, 1000 * (30 + vEhc.getV(num1, num2) // 2), cooltime=180 * 1000, red=True).isV(vEhc, num1, num2))
        self.enable_referring_runtime_context()
        self.stat = None
        self.modifierInvariantFlag = False

    def _use(self, skill_modifier, runtime_context_modifier):
        self.stat = runtime_context_modifier.stat_main * (1 + 0.01 * runtime_context_modifier.pstat_main) + runtime_context_modifier.stat_main_fixed
        return super(PrayWrapper, self)._use(skill_modifier)

    def get_modifier(self):
        if self.is_active():
            return core.CharacterModifier(pdamage_indep=5 + min(self.stat // 2500, 45))
        else:
            return self.disabledModifier


class JobGenerator(characterKernel.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.load(os.path.join(os.path.dirname(__file__), 'configs', 'bishop.yml'))
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'crit', 'boss_pdamage')

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(SynchronizeRule(GlobalSkills.TermsAndConditions.value, AdventurerSkills.Infinity.value, 35000, -1), RuleSet.BASE)
        ruleset.add_rule(SynchronizeRule(BishopSkills.Benediction.value, AdventurerSkills.Infinity.value, 45000, -1), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(AdventurerSkills.UnreliableMemory.value, AdventurerSkills.Infinity.value), RuleSet.BASE)
        ruleset.add_rule(DisableRule(BishopSkills.Heal.value), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=43)

    def get_passive_skill_list(self, vEhc, chtr : characterKernel.AbstractCharacter, options: Dict[str, Any]):
        default_list = super(JobGenerator, self).get_passive_skill_list(vEhc, chtr, options)
        UnstableMemorizePassive = adventurer.UnstableMemorizePassiveWrapper(vEhc, 4, 4)
        default_list += [UnstableMemorizePassive]

    def generate(self, vEhc, chtr : characterKernel.AbstractCharacter, options: Dict[str, Any]):
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
        # Buff skills
        Booster = self.load_skill_wrapper(BishopSkills.MagicBooster.value)
        AdvancedBless = self.load_skill_wrapper(BishopSkills.AdvancedBlessing.value)
        Heal = self.load_skill_wrapper(BishopSkills.Heal.value)
        Infinity = adventurer.InfinityWrapper(self.combat)
        EpicAdventure = self.load_skill_wrapper(BishopSkills.EpicAdventure.value)

        Pray = PrayWrapper(vEhc, 2, 2)

        # Damage Skills
        AngelRay = self.load_skill_wrapper(BishopSkills.AngelRay.value, vEhc)

        HeavensDoor = self.load_skill_wrapper(BishopSkills.HeavensDoor.value)

        PeaceMakerInit = self.load_skill_wrapper(f"{BishopSkills.Peacemaker.value}(Cast | 시전)", vEhc)
        PeaceMaker = self.load_skill_wrapper(BishopSkills.Peacemaker.value, vEhc)
        PeaceMakerFinal = self.load_skill_wrapper(f"{BishopSkills.Peacemaker.value}(Explosion | 폭발)", vEhc)
        PeaceMakerFinalBuff = self.load_skill_wrapper(f"{BishopSkills.Peacemaker.value}(Buff | 버프)", vEhc)

        DivinePunishmentInit = self.load_skill_wrapper(f"{BishopSkills.DivinePunishment.value}(Cast | 개시)", vEhc)
        DivinePunishmentTick = self.load_skill_wrapper(f"{BishopSkills.DivinePunishment.value}(Tick | 키다운)", vEhc)

        # Summoning skill
        Bahamutt = self.load_skill_wrapper(BishopSkills.Bahamut.value, vEhc)  # 최종뎀25%스택, 리브라 종료시 자동소환 되므로 딜레이 0
        AngelOfLibra = self.load_skill_wrapper(BishopSkills.AngelofBalance.value, vEhc)  # 최종뎀50%스택
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # Unstable Memorize skills
        EnergyBolt = self.load_skill_wrapper(BishopSkills.EnergyBolt.value)
        HolyArrow = self.load_skill_wrapper(BishopSkills.HolyArrow.value)
        ShiningRay = self.load_skill_wrapper(BishopSkills.ShiningRay.value)
        HolyFountain = self.load_skill_wrapper(BishopSkills.HolyFountain.value)
        Dispell = self.load_skill_wrapper(BishopSkills.Dispel.value)
        DivineProtection = self.load_skill_wrapper(BishopSkills.DivineProtection.value)
        Genesis = self.load_skill_wrapper(BishopSkills.Genesis.value)
        BigBang = self.load_skill_wrapper(BishopSkills.BigBang.value)
        Resurrection = self.load_skill_wrapper(BishopSkills.Resurrection.value)

        VengenceOfAngel_Delay = self.load_skill_wrapper(f"{BishopSkills.RighteouslyIndignant.value}(Delay | 딜레이)")

        ######   Wrappers    ######
        # Unstable Memorize
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
            sk.add_runtime_modifier(SacredMark, lambda skill: core.CharacterModifier(pdamage_indep=skill.stack))

        # Peace Maker
        PeaceMakerRepeat = core.RepeatElement(PeaceMaker, self.conf["constant"]["PEACEMAKER_HIT"])
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
        for sk in [AngelRay, Genesis, BigBang, HeavensDoor,
                   AngelOfLibra, PeaceMaker, PeaceMakerFinal, DivinePunishmentTick,
                   EnergyBolt, HolyArrow, ShiningRay]:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()

        return (AngelRay,
                [Booster, SacredMark, Infinity, PeaceMakerFinalBuff, Pray, EpicAdventure, OverloadMana,
                 globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_wind_booster(), AdvancedBless, Heal,
                 globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract(),
                 PeaceMakerInit,
                 AngelOfLibra, Bahamutt, HeavensDoor, DivinePunishmentInit, MirrorBreak, MirrorSpider,
                 UnstableMemorize,
                 AngelRay])
