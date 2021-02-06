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
from ..execution.rules import RuleSet, MutualRule, InactiveRule


# English skill information for Fire/Poison Mage here https://maplestory.fandom.com/wiki/Magician_(Fire,_Poison)/Skills
class ArchmageFirePoisonSkills(Enum):
    # Link Skill
    EmpiricalKnowledge = 'Empirical Knowledge | 임피리컬 널리지'
    # 1st Job
    EnergyBolt = 'Energy Bolt | 에너지 볼트'
    MagicGuard = 'Magic Guard | 매직 가드'
    Teleport = 'Teleport | 텔레포트'
    # 2nd Job
    FlameOrb = 'Flame Orb | 플레임 오브'
    ElementalDrain = 'Elemental Drain | 엘리멘탈 드레인'
    PoisonBreath = 'Poison Breath | 포이즌 브레스'
    Meditation = 'Meditation | 메디테이션'
    MagicBooster = 'Magic Booster | 매직 부스터'
    Ignite = 'Ignite | 이그나이트'
    SpellMastery = 'Spell Mastery | 스펠 마스터리'
    HighWisdom = 'High Wisdom | 하이 위즈덤'
    MPEater = 'MP Eater | MP 이터'
    # 3rd Job
    Explosion = 'Explosion | 익스플로젼'
    PoisonMist = 'Poison Mist | 포이즌 미스트'
    ViralSlime = 'Viral Slime | 슬라임 바이러스'
    ElementalAdaptationFirePoison = 'Elemental Adaptation (Fire, Poison) | 엘리멘탈 어뎁팅(불,독)'
    ElementalDecrease = 'Elemental Decrease | 엘리멘탈 리셋'
    TeleportMastery = 'Teleport Mastery | 텔레포트 마스터리'
    ManaBurn = 'Mana Burn | 마나 번'
    ElementAmplification = 'Element Amplification | 엘리먼트 엠플리피케이션'
    ArcaneOverdrive = 'Arcane Overdrive | 매직 크리티컬'
    BurningMagic = 'Burning Magic | 익스트림 매직(불,독)'
    # 4th Job
    Paralyze = 'Paralyze | 페럴라이즈'
    MistEruption = 'Mist Eruption | 미스트 이럽션'
    FerventDrain = 'Fervent Drain | 퍼번트 드레인'
    MeteorShower = 'Meteor Shower | 메테오'
    FlameHaze = 'Flame Haze | 플레임 헤이즈'
    Ifrit = 'Ifrit | 이프리트'
    ArcaneAim = 'Arcane Aim | 아케인 에임'
    BuffMastery = 'Buff Mastery | 마스터 매직'
    # Hypers
    MegiddoFlame = 'Megiddo Flame | 메기도 플레임'
    EpicAdventure = 'Epic Adventure | 에픽 어드벤처'
    InfernoAura = 'Inferno Aura | 파이어 오라'
    # 5th Job
    DoTPunisher = 'DoT Punisher | 도트 퍼니셔'
    PoisonNova = 'Poison Nova | 포이즌 노바'
    ElementalFury = 'Elemental Fury | 퓨리 오브 이프리트'
    PoisonChain = 'Poison Chain | 포이즌 체인'



class PoisonChainToxicWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        skill = core.SummonSkill(
            f"{ArchmageFirePoisonSkills.PoisonChain.value}(addition | 중독)",  # Poison chain (addition)
            0,
            1800,
            150 + 6 * vEhc.getV(3, 2),
            6,
            9 * 1800 - 1,
            cooltime=-1
        ).isV(vEhc, num1, num2)  # 9 explosions, 1800 ms interval. 9회 폭발, 1800ms 간격.
        super(PoisonChainToxicWrapper, self).__init__(skill)
        self.stack = 0
        self.per_stack = 30 + vEhc.getV(num1, num2)

    def _use(self, skill_modifier):
        self.stack = 1
        return super(PoisonChainToxicWrapper, self)._use(skill_modifier)

    def _useTick(self) -> core.ResultObject:
        result = super(PoisonChainToxicWrapper, self)._useTick()
        self.stack = min(self.stack + 1, 5)
        return result

    def get_damage(self):
        damage = self.skill.damage + self.stack * self.per_stack
        return damage


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.load(os.path.join(os.path.dirname(__file__), 'configs', 'archmageFP.yml'))
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'crit', 'boss_pdamage')

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(MutualRule(ArchmageFirePoisonSkills.DoTPunisher.value, ArchmageFirePoisonSkills.PoisonNova.value), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(AdventurerSkills.UnreliableMemory.value, AdventurerSkills.Infinity.value), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        default_list = super(JobGenerator, self).get_passive_skill_list(vEhc, chtr, options)
        UnstableMemorizePassive = adventurer.UnstableMemorizePassiveWrapper(vEhc, 4, 4)
        default_list += [UnstableMemorizePassive]

        return default_list

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Poison Nova 4 Hit

        V core strengthening ranking

        ??/??/(??)/??/Nova/??/??
        ??/??/Haze/Ignite/Aura/Mete/??/??/??

        Extreme deal skills are used every cool time
        Unstable Memory is used when Infinity is off

        포이즌 노바 4히트

        V 코어 강화 순위

        쓸윈/쓸샾/(쓸오더)/도퍼/노바/언스/오버마나
        이럽/패럴/헤이즈/이그나이트/오라/메테/이프/메기/텔마

        극딜형 스킬은 쿨마다 사용함
        언스테이블 메모라이즈는 인피니티가 꺼져있을때 사용
        '''
        DOT_PUNISHER_HIT = self.conf["constant"]["DOT_PUNISHER_HIT"]  # TODO: The number of strokes is determined by referring to the current number of dots. 현재 도트 개수를 참조해 타수 결정.

        # Buff Skills
        Meditation = self.load_skill_wrapper(ArchmageFirePoisonSkills.Meditation.value)
        EpicAdventure = self.load_skill_wrapper(ArchmageFirePoisonSkills.EpicAdventure.value)
        Infinity = adventurer.InfinityWrapper(self.combat)

        # Damage Skills
        Paralyze = self.load_skill_wrapper(ArchmageFirePoisonSkills.Paralyze.value, vEhc)
        TeleportMastery = self.load_skill_wrapper(ArchmageFirePoisonSkills.TeleportMastery.value, vEhc)

        FlameHeize = self.load_skill_wrapper(ArchmageFirePoisonSkills.FlameHaze.value, vEhc)
        MistEruption = self.load_skill_wrapper(ArchmageFirePoisonSkills.MistEruption.value, vEhc)

        DotPunisher = self.load_skill_wrapper(ArchmageFirePoisonSkills.DoTPunisher.value, vEhc)
        DotPunisherExceed = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.DoTPunisher.value}(exceed | 초과)", vEhc)
        PoisonNova = self.load_skill_wrapper(ArchmageFirePoisonSkills.PoisonNova.value, vEhc)
        PoisonNovaErupt = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.PoisonNova.value}(erupt | 폭발)", vEhc)
        PoisonNovaEruptExceed = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.PoisonNova.value}(erupt | 폭발)(exceed | 초과)", vEhc)
        PoisonChain = self.load_skill_wrapper(ArchmageFirePoisonSkills.PoisonChain.value, vEhc)
        PoisonChainToxic = PoisonChainToxicWrapper(vEhc, 0, 0)

        Meteor = self.load_skill_wrapper(ArchmageFirePoisonSkills.MeteorShower.value, vEhc)
        MegidoFlame = self.load_skill_wrapper(ArchmageFirePoisonSkills.MegiddoFlame.value, vEhc)

        # Summoning Skills
        Ifritt = self.load_skill_wrapper(ArchmageFirePoisonSkills.Ifrit.value, vEhc)
        FireAura = self.load_skill_wrapper(ArchmageFirePoisonSkills.InfernoAura.value, vEhc)
        FuryOfIfritt = self.load_skill_wrapper(ArchmageFirePoisonSkills.ElementalFury.value, vEhc)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # Final Attack
        MeteorPassive = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.MeteorShower.value}(passive | 패시브)", vEhc)
        Ignite = self.load_skill_wrapper(ArchmageFirePoisonSkills.Ignite.value, vEhc)
        IgniteMeteor = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.Ignite.value}({ArchmageFirePoisonSkills.MeteorShower.value})", vEhc)
        # Ignite : Need Wrapper

        # DoT Skills
        ParalyzeDOT = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.Paralyze.value}(DoT | 도트)")
        MistDOT = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.PoisonMist.value}(DoT | 도트)")
        IfrittDot = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.Ifrit.value}(DoT | 도트)")
        HeizeFlameDOT = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.FlameHaze.value}(DoT | 도트)")
        TeleportMasteryDOT = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.TeleportMastery.value}(DoT | 도트)")
        PoisonBreathDOT = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.PoisonBreath.value}(DoT | 도트)")
        MegidoFlameDOT = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.MegiddoFlame.value}(DoT | 도트)")
        DotPunisherDOT = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.DoTPunisher.value}(DoT | 도트)", vEhc)
        PoisonNovaDOT = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.PoisonNova.value}(DoT | 도트)", vEhc)

        # Unstable Memorize Skills
        EnergyBolt = self.load_skill_wrapper(ArchmageFirePoisonSkills.EnergyBolt.value)
        FlameOrb = self.load_skill_wrapper(ArchmageFirePoisonSkills.FlameOrb.value)
        PoisonBreath = self.load_skill_wrapper(ArchmageFirePoisonSkills.PoisonBreath.value)
        Explosion = self.load_skill_wrapper(ArchmageFirePoisonSkills.Explosion.value)  # magic6(720) -> explosion(180). Both are applied at the speed of 540+150. magic6(720) -> explosion(180). 둘 다 공속 적용되어 540+150.
        PoisonMist = self.load_skill_wrapper(ArchmageFirePoisonSkills.PoisonMist.value)
        SlimeVirus = self.load_skill_wrapper(ArchmageFirePoisonSkills.ViralSlime.value)

        # Unstable Memorize
        UnstableMemorize = adventurer.UnstableMemorizeWrapper(vEhc, 4, 4, chtr.get_skill_modifier())

        for sk, weight in [(EnergyBolt, 1), (FlameOrb, 5), (PoisonBreath, 5), (Explosion, 10),
                           (PoisonMist, 10), (SlimeVirus, 10), (Paralyze, 25), (MistEruption, 25), (Meteor, 25),
                           (FlameHeize, 25), (Infinity, 25), (Ifritt, 25), (MegidoFlame, 25), (EpicAdventure, 10)]:
            UnstableMemorize.add_skill(sk, weight)

        # Ignite
        for skill in [FlameOrb, Explosion, Paralyze, FlameHeize, Meteor, MegidoFlame]:
            skill.onAfter(Ignite)

        MeteorPassive.onAfter(IgniteMeteor)
        DotPunisher.onAfter(core.RepeatElement(Ignite, DOT_PUNISHER_HIT))
        FuryOfIfritt.onAfter(core.RepeatElement(Ignite, 25))
        Ifritt.onTick(Ignite)
        FireAura.onTick(Ignite)

        # Meteor Passive
        for skill in [EnergyBolt, FlameOrb, PoisonBreath, Explosion, PoisonMist, Paralyze, FlameHeize, PoisonNova, PoisonChain, MistEruption]:
            skill.onAfter(MeteorPassive)

        DotPunisher.onAfter(core.RepeatElement(MeteorPassive, DOT_PUNISHER_HIT))

        # DoT
        Paralyze.onAfter(ParalyzeDOT)
        TeleportMastery.onAfter(TeleportMasteryDOT)
        FlameHeize.onAfter(HeizeFlameDOT)
        FlameHeize.onAfter(MistDOT)
        PoisonMist.onAfter(MistDOT)
        PoisonBreath.onAfter(PoisonBreathDOT)
        Ifritt.onTick(IfrittDot)
        DotPunisher.onAfter(DotPunisherDOT)
        MegidoFlame.onAfter(MegidoFlameDOT)
        PoisonNova.onAfter(PoisonNovaDOT)

        # Skill Link
        DotPunisher.onBefore(TeleportMastery)
        DotPunisher.onJustAfter(DotPunisherExceed)
        PoisonNova.onAfter(PoisonNovaErupt)
        PoisonNovaErupt.onJustAfter(PoisonNovaEruptExceed)
        MistEruption.onAfter(FlameHeize.controller(1, 'reduce_cooltime_p'))
        PoisonChain.onAfter(PoisonChainToxic)

        # Overload Mana
        overload_mana_builder = magicians.OverloadManaBuilder(vEhc, 1, 5)
        for sk in [Paralyze, TeleportMastery, MistEruption, FlameHeize, PoisonMist,
                   Meteor, MegidoFlame, DotPunisher, DotPunisherExceed, PoisonNova,
                   PoisonNovaErupt, PoisonNovaEruptExceed, PoisonChain, PoisonChainToxic,
                   EnergyBolt, FlameOrb, PoisonBreath, Explosion]:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()

        return (Paralyze,
                [Infinity, Meditation, EpicAdventure, OverloadMana,
                 globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_wind_booster(),
                 globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()] +
                [DotPunisher, PoisonChain, Meteor, MegidoFlame, FlameHeize, MistEruption, PoisonNova, MirrorBreak, MirrorSpider] +
                [Ifritt, FireAura, FuryOfIfritt,
                 SlimeVirus, ParalyzeDOT, MistDOT, PoisonBreathDOT, IfrittDot, HeizeFlameDOT, TeleportMasteryDOT, MegidoFlameDOT, DotPunisherDOT, PoisonNovaDOT, PoisonChainToxic] +
                [UnstableMemorize] +
                [Paralyze])
