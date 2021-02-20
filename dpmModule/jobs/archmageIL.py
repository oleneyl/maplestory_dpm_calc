import os
from enum import Enum

from typing import Any, Dict

from dpmModule.jobs.jobclass.adventurer import AdventurerSkills

from . import globalSkill
from ..kernel import core
from .jobclass import adventurer
from .jobbranch import magicians
from ..status.ability import Ability_tool
from ..character import characterKernel as ck
from ..execution.rules import RuleSet, ConcurrentRunRule, InactiveRule


# English skill information for Ice/Lightning Mage here https://maplestory.fandom.com/wiki/Magician_(Ice,_Lightning)/Skills
class ArchmageIceLightningSkills(Enum):
    # Link Skill
    EmpiricalKnowledge = 'Empirical Knowledge | 임피리컬 널리지'
    # 1st Job
    EnergyBolt = 'Energy Bolt | 에너지 볼트'
    MagicGuard = 'Magic Guard | 매직 가드'
    Teleport = 'Teleport | 텔레포트'
    MagicArmor = 'Magic Armor | 매직 아머'
    MPBoost = 'MP Boost | MP 증가'
    # 2nd Job
    ColdBeam = 'Cold Beam | 콜드 빔'
    FreezingCrush = 'Freezing Crush | 프리징 이펙트'
    ThunderBolt = 'Thunder Bolt | 썬더 볼트'
    ChillingStep = 'Chilling Step | 칠링 스텝'
    Meditation = 'Meditation | 메디테이션'
    MagicBooster = 'Magic Booster | 매직 부스터'
    SpellMastery = 'Spell Mastery | 스펠 마스터리'
    HighWisdom = 'High Wisdom | 하이 위즈덤'
    MPEater = 'MP Eater | MP 이터'
    # 3rd Job
    IceStrike = 'Ice Strike | 아이스 스트라이크'
    GlacierChain = 'Glacier Chain | 글레이셜 체인'
    Thunderstorm = 'Thunderstorm | 썬더 스톰'
    ElementalAdaptationIceLightning = 'Elemental Adaptation (Ice, Lightning) | 엘리멘탈 어뎁팅(썬,콜)'
    ElementalDecrease = 'Elemental Decrease | 엘리멘탈 리셋'
    TeleportMastery = 'Teleport Mastery | 텔레포트 마스터리'
    ArcaneOverdrive = 'Arcane Overdrive | 매직 크리티컬'
    StormMagic = 'Storm Magic | 익스트림 매직(썬,콜)'
    ElementAmplification = 'Element Amplification | 엘리멘트 엠플리피케이션'
    Shatter = 'Shatter | 프로즌 브레이크'
    # 4th Job
    ChainLightning = 'Chain Lightning | 체인 라이트닝'
    FreezingBreath = 'Freezing Breath | 프리징 브레스'
    Blizzard = 'Blizzard | 블리자드'
    FrozenOrb = 'Frozen Orb | 프로즌 오브'
    Elquines = 'Elquines | 엘퀴네스'
    BuffMastery = 'Buff Mastery | 마스터 매직'
    ArcaneAim = 'Arcane Aim | 아케인 에임'
    FrostClutch = 'Frost Clutch | 프로스트 이펙트'
    LightningOrb = 'Lightning Orb | 라이트닝 스피어'
    EpicAdventure = 'Epic Adventure | 에픽 어드벤처'
    AbsoluteZeroAura = 'Absolute Zero Aura | 아이스 오라'
    # 5th Job
    IceAge = 'Ice Age | 아이스 에이지'
    BoltBarrage = 'Bolt Barrage | 썬더 브레이크'
    SpiritofSnow = 'Spirit of Snow | 스피릿 오브 스노우'
    JupiterThunder = 'Jupiter Thunder | 주피터 썬더'


class FrostEffectWrapper(core.StackSkillWrapper):
    def __init__(self, skill):
        super(FrostEffectWrapper, self).__init__(skill, 5)
        self.stack = 5  # Better point!
        self.modifierInvariantFlag = False

    def get_modifier(self):
        return core.CharacterModifier(crit_damage=3 * self.stack, armor_ignore=0.2 * 5 * self.stack)


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.load(os.path.join(os.path.dirname(__file__), 'configs', 'archmageIL.yml'))
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'crit', 'boss_pdamage')

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore=5, pdamage=60, crit_damage=15)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule(ArchmageIceLightningSkills.LightningOrb.value, AdventurerSkills.Infinity.value), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(AdventurerSkills.UnreliableMemory.value, AdventurerSkills.Infinity.value), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        default_list = super(JobGenerator, self).get_passive_skill_list(vEhc, chtr, options)
        UnstableMemorizePassive = adventurer.UnstableMemorizePassiveWrapper(vEhc, 4, 4)
        default_list += [UnstableMemorizePassive]

        return default_list

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Node order
        ??-??-??-??

        ?? 2 hit
        Ice Age Floor 2 hits

        Hyper:
        Teleport-Ad Range
        Chain Lightning-Reinforcement/Bonus Attack/Increase the number of targets
        Orb-Dempsey

        Unstable Memory is used when Infinity is off
        Lightning Sphere is used only when Infinity is on

        Other extreme deals are used for each cooldown.
        Used per Frozen of Cool, 19 hits

        코강 순서
        체라-라스피-블자-오브-엘퀴-썬더스톰

        썬브 2히트
        아이스 에이지 장판 2히트

        하이퍼 :
        텔레포트 - 애드 레인지
        체인 라이트닝 - 리인포스/보너스어택/타겟수 증가
        오브 - 뎀증

        언스테이블 메모라이즈는 인피니티가 꺼져있을때 사용
        라이트닝 스피어는 인피니티가 켜져 있을때만 사용함

        그 외의 극딜기는 쿨마다 사용
        프로즌 오브 쿨마다 사용, 19타
        '''
        THUNDER_BREAK_HIT = options.get("thunder_break_hit", 2)
        ICE_AGE_SUMMON_HIT = 2

        ######   Skill   ######
        # Buff skills
        Meditation = self.load_skill_wrapper(ArchmageIceLightningSkills.Meditation.value)
        EpicAdventure = self.load_skill_wrapper(ArchmageIceLightningSkills.EpicAdventure.value)

        # Damage Skills
        ChainLightening = self.load_skill_wrapper(ArchmageIceLightningSkills.ChainLightning.value, vEhc)

        FrozenOrb = self.load_skill_wrapper(ArchmageIceLightningSkills.FrozenOrb.value, vEhc)
        LighteningSpear = self.load_skill_wrapper(ArchmageIceLightningSkills.LightningOrb.value, vEhc)
        LighteningSpearSingle = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.LightningOrb.value}(Key down | 키다운)", vEhc)
        LighteningSpearFinalizer = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.LightningOrb.value}(Final attack | 막타)", vEhc)

        IceAgeInit = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.IceAge.value}(Cast | 개시)", vEhc)
        IceAgeSummon = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.IceAge.value}(Floor | 장판)", vEhc)

        # 5% reduction per stack. 중첩당 감소량 5%.
        # TODO: ?? must implement canceling the previous skill delay. 썬브가 이전 스킬 딜레이 캔슬하는것 구현해야 함.
        ThunderBrake = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.BoltBarrage.value}(Start skill | 개시스킬)", vEhc)  # Awesome! -> Tandem 사출처리 해야함...Later. 690을 일단 급한대로 분배해서 사용.
        ThunderBrake1 = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.BoltBarrage.value}(1)", vEhc)
        ThunderBrake2 = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.BoltBarrage.value}(2)", vEhc)
        ThunderBrake3 = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.BoltBarrage.value}(3)", vEhc)
        ThunderBrake4 = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.BoltBarrage.value}(4)", vEhc)
        ThunderBrake5 = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.BoltBarrage.value}(5)", vEhc)
        ThunderBrake6 = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.BoltBarrage.value}(6)", vEhc)
        ThunderBrake7 = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.BoltBarrage.value}(7)", vEhc)
        ThunderBrake8 = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.BoltBarrage.value}(8)", vEhc)

        # Single target criteria. 단일 대상 기준.
        SpiritOfSnow = self.load_skill_wrapper(ArchmageIceLightningSkills.SpiritofSnow.value, vEhc)

        # Summoning skill
        ThunderStorm = self.load_skill_wrapper(ArchmageIceLightningSkills.Thunderstorm.value, vEhc)
        Elquiness = self.load_skill_wrapper(ArchmageIceLightningSkills.Elquines.value, vEhc)
        IceAura = self.load_skill_wrapper(ArchmageIceLightningSkills.AbsoluteZeroAura.value, vEhc)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        JupyterThunder = self.load_skill_wrapper(ArchmageIceLightningSkills.JupiterThunder.value, vEhc)

        # FinalAttack
        Blizzard = self.load_skill_wrapper(ArchmageIceLightningSkills.Blizzard.value, vEhc)
        BlizzardPassive = self.load_skill_wrapper(f"{ArchmageIceLightningSkills.Blizzard.value}(Passive | 패시브)", vEhc)

        # special skills
        Infinity = adventurer.InfinityWrapper(self.combat)
        FrostEffect = core.BuffSkill(ArchmageIceLightningSkills.FrostClutch.value, 0, 999999 * 1000).wrap(FrostEffectWrapper)

        # Unstable Memorize skills
        EnergyBolt = self.load_skill_wrapper(ArchmageIceLightningSkills.EnergyBolt.value)
        ColdBeam = self.load_skill_wrapper(ArchmageIceLightningSkills.ColdBeam.value)
        ThunderBolt = self.load_skill_wrapper(ArchmageIceLightningSkills.ThunderBolt.value)
        IceStrike = self.load_skill_wrapper(ArchmageIceLightningSkills.IceStrike.value)
        GlacialChain = self.load_skill_wrapper(ArchmageIceLightningSkills.GlacierChain.value)

        ######   Skill Wrapper   ######
        # Unstable Memorize
        UnstableMemorize = adventurer.UnstableMemorizeWrapper(vEhc, 4, 4, chtr.get_skill_modifier())

        for sk, weight in [(EnergyBolt, 1), (ColdBeam, 5), (ThunderBolt, 5), (IceStrike, 10),
                           (GlacialChain, 10), (ThunderStorm, 10), (ChainLightening, 25), (Blizzard, 25), (FrozenOrb, 25),
                           (Infinity, 25), (Elquiness, 25), (LighteningSpear, 10), (EpicAdventure, 10)]:

            UnstableMemorize.add_skill(sk, weight)

        # Frost Effect
        FrostIncrement = FrostEffect.stackController(1)
        FrostDecrement = FrostEffect.stackController(-1)

        def applyFrostEffect(sk: FrostEffect):
            return core.CharacterModifier(pdamage=sk.stack * 12)

        # Energy Bolt
        EnergyBolt.onAfter(BlizzardPassive)

        # Cold Beam
        ColdBeam.onJustAfter(FrostIncrement)
        ColdBeam.onAfter(BlizzardPassive)

        # Thunder Bolt
        ThunderBolt.add_runtime_modifier(FrostEffect, applyFrostEffect)
        ThunderBolt.onJustAfter(FrostDecrement)
        ThunderBolt.onAfter(BlizzardPassive)

        # Ice Strike
        IceStrike.onJustAfter(FrostIncrement)
        IceStrike.onAfter(BlizzardPassive)

        # Glacial Chain
        GlacialChain.onJustAfter(FrostIncrement)
        GlacialChain.onAfter(BlizzardPassive)

        # Thunder Storm
        ThunderStorm.add_runtime_modifier(FrostEffect, applyFrostEffect)

        # Elquiness
        Elquiness.onTick(FrostIncrement)

        # Frozen Orb
        FrozenOrb.onTick(BlizzardPassive)  # TODO: If the order of onTick execution changes, the order must be adjusted. onTick 실행순서 바뀌면 순서 조정해야 함
        FrozenOrb.onTick(FrostIncrement)

        # Chain Lightening
        ChainLightening.add_runtime_modifier(FrostEffect, applyFrostEffect)
        ChainLightening.onJustAfter(FrostDecrement)
        ChainLightening.onAfter(BlizzardPassive)

        # Blizzard
        Blizzard.onJustAfter(FrostIncrement)
        BlizzardPassive.onJustAfter(FrostEffect.stackController(0.6))

        # Lightening Spear
        LighteningSpearSingle.add_runtime_modifier(FrostEffect, applyFrostEffect)
        LighteningSpearSingle.onJustAfter(FrostDecrement)
        LighteningSpearSingle.onAfter(BlizzardPassive)
        LighteningSpearFinalizer.add_runtime_modifier(FrostEffect, applyFrostEffect)
        LighteningSpearFinalizer.onJustAfter(FrostDecrement)
        LighteningSpearFinalizer.onAfter(BlizzardPassive)

        LighteningRepeator = core.RepeatElement(LighteningSpearSingle, 30)
        LighteningRepeator.onAfter(LighteningSpearFinalizer)

        LighteningSpear.onAfter(LighteningRepeator)

        # Ice Aura
        IceAura.onTick(FrostIncrement)

        # Ice Age
        IceAgeSummon.onTick(core.RepeatElement(FrostIncrement, ICE_AGE_SUMMON_HIT))
        IceAgeInit.onJustAfter(FrostIncrement)
        IceAgeInit.onAfter(BlizzardPassive)
        IceAgeInit.onAfter(IceAgeSummon)

        # Thunder Break
        for node in [ThunderBrake1, ThunderBrake2, ThunderBrake3, ThunderBrake4, ThunderBrake5, ThunderBrake6, ThunderBrake7, ThunderBrake8][:THUNDER_BREAK_HIT]:
            node.add_runtime_modifier(FrostEffect, applyFrostEffect)
            node.onJustAfter(FrostDecrement)
            node.onAfter(BlizzardPassive)
            ThunderBrake.onAfter(node)

        # Spirit of Snow
        SpiritOfSnow.onTick(FrostEffect.stackController(3))

        # Jupyter Thunder
        JupyterThunder.add_runtime_modifier(FrostEffect, applyFrostEffect)  # TODO: Make sure that Blizzard does not burst. 블리자드 파택 안터지는게 맞는지 확인할것.
        for i in range(1, 6 + 1):
            JupyterThunder.onEventElapsed(FrostDecrement, 330 * 5 * i)  # Freeze reduction for every 5 hits, a total of 6 reductions. 5회 타격시마다 빙결 감소, 총 6회 감소

        # Overload Mana
        overload_mana_builder = magicians.OverloadManaBuilder(vEhc, 1, 5)
        for sk in [ChainLightening, FrozenOrb, Blizzard, LighteningSpearSingle, LighteningSpearFinalizer, IceAgeInit,
                   ThunderBrake1, ThunderBrake2, ThunderBrake3, ThunderBrake4, ThunderBrake5, ThunderBrake6, ThunderBrake7, ThunderBrake8,
                   JupyterThunder, EnergyBolt, ColdBeam, ThunderBolt, IceStrike, GlacialChain]:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()

        return (ChainLightening,
                [Infinity, Meditation, EpicAdventure, OverloadMana, FrostEffect,
                 globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_wind_booster(),
                 globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract(),
                 IceAgeInit, Blizzard, JupyterThunder, LighteningSpear, ThunderBrake, MirrorBreak, MirrorSpider,
                 ThunderStorm, Elquiness, IceAura, IceAgeSummon, FrozenOrb, SpiritOfSnow,
                 UnstableMemorize,
                 ChainLightening])
