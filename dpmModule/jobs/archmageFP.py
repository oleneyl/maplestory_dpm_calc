import os

from typing import Any, Dict

from dpmModule.jobs.jobclass.adventurer import AdventurerSkills

from . import globalSkill, jobutils
from ..kernel import core
from .jobclass import adventurer
from .jobbranch import magicians
from ..status.ability import Ability_tool
from ..character import characterKernel as ck
from ..execution.rules import RuleSet, MutualRule, InactiveRule
from math import ceil

import gettext
_ = gettext.gettext

# English skill information for Fire/Poison Mage here https://maplestory.fandom.com/wiki/Magician_(Fire,_Poison)/Skills
class ArchmageFirePoisonSkills:
    # Link Skill
    EmpiricalKnowledge = _("임피리컬 널리지")  # "Empirical Knowledge"
    # 1st Job
    EnergyBolt = _("에너지 볼트")  # "Energy Bolt"
    MagicGuard = _("매직 가드")  # "Magic Guard"
    Teleport = _("텔레포트")  # "Teleport"
    # 2nd Job
    FlameOrb = _("플레임 오브")  # "Flame Orb"
    ElementalDrain = _("엘리멘탈 드레인")  # "Elemental Drain"
    PoisonBreath = _("포이즌 브레스")  # "Poison Breath"
    Meditation = _("메디테이션")  # "Meditation"
    MagicBooster = _("매직 부스터")  # "Magic Booster"
    Ignite = _("이그나이트")  # "Ignite"
    SpellMastery = _("스펠 마스터리")  # "Spell Mastery"
    HighWisdom = _("하이 위즈덤")  # "High Wisdom"
    MPEater = _("MP 이터")  # "MP Eater"
    # 3rd Job
    Explosion = _("익스플로젼")  # "Explosion"
    PoisonMist = _("포이즌 미스트")  # "Poison Mist"
    ViralSlime = _("슬라임 바이러스")  # "Viral Slime"
    ElementalAdaptationFirePoison = _("엘리멘탈 어뎁팅")  # "Elemental Adaptation"
    ElementalDecrease = _("엘리멘탈 리셋")  # "Elemental Decrease"
    TeleportMastery = _("텔레포트 마스터리")  # "Teleport Mastery"
    ManaBurn = _("마나 번")  # "Mana Burn"
    ElementAmplification = _("엘리멘트 엠플리피케이션")  # "Element Amplification"
    ArcaneOverdrive = _("매직 크리티컬")  # "Arcane Overdrive"
    BurningMagic = _("익스트림 매직")  # "Burning Magic"
    # 4th Job
    Paralyze = _("페럴라이즈")  # "Paralyze"
    MistEruption = _("미스트 이럽션")  # "Mist Eruption"
    FerventDrain = _("퍼번트 드레인")  # "Fervent Drain"
    MeteorShower = _("메테오")  # "Meteor Shower"
    FlameHaze = _("플레임 헤이즈")  # "Flame Haze"
    Ifrit = _("이프리트")  # "Ifrit"
    ArcaneAim = _("아케인 에임")  # "Arcane Aim"
    BuffMastery = _("마스터 매직")  # "Buff Mastery"
    # Hypers
    MegiddoFlame = _("메기도 플레임")  # "Megiddo Flame"
    EpicAdventure = _("에픽 어드벤처")  # "Epic Adventure"
    InfernoAura = _("파이어 오라")  # "Inferno Aura"
    # 5th Job
    DoTPunisher = _("도트 퍼니셔")  # "DoT Punisher"
    PoisonNova = _("포이즌 노바")  # "Poison Nova"
    ElementalFury = _("퓨리 오브 이프리트")  # "Elemental Fury"
    PoisonChain = _("포이즌 체인")  # "Poison Chain"


class PoisonChainToxicWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        skill = core.SummonSkill(
            _("{}(중독)").format(ArchmageFirePoisonSkills.PoisonChain),  # Poison chain (addition)
            summondelay=0,
            delay=1800,
            damage=150 + 6 * vEhc.getV(3, 2),
            hit=5,
            remain=9 * 1800 - 1,
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
        ruleset.add_rule(MutualRule(ArchmageFirePoisonSkills.DoTPunisher, ArchmageFirePoisonSkills.PoisonNova), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(AdventurerSkills.UnreliableMemory, AdventurerSkills.Infinity), RuleSet.BASE)
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
        Meditation = self.load_skill_wrapper(ArchmageFirePoisonSkills.Meditation)
        EpicAdventure = self.load_skill_wrapper(ArchmageFirePoisonSkills.EpicAdventure)
        Infinity = adventurer.InfinityWrapper(self.combat)

        # Damage Skills
        Paralyze = self.load_skill_wrapper(ArchmageFirePoisonSkills.Paralyze, vEhc)
        TeleportMastery = self.load_skill_wrapper(ArchmageFirePoisonSkills.TeleportMastery, vEhc)

        FlameHeize = self.load_skill_wrapper(ArchmageFirePoisonSkills.FlameHaze, vEhc)
        MistEruption = self.load_skill_wrapper(ArchmageFirePoisonSkills.MistEruption, vEhc)

        DotPunisher = self.load_skill_wrapper(ArchmageFirePoisonSkills.DoTPunisher, vEhc)
        DotPunisherExceed = self.load_skill_wrapper(_("{}(초과)").format(ArchmageFirePoisonSkills.DoTPunisher), vEhc)
        PoisonNova = self.load_skill_wrapper(ArchmageFirePoisonSkills.PoisonNova, vEhc)
        PoisonNovaErupt = self.load_skill_wrapper(_("{}(폭발)").format(ArchmageFirePoisonSkills.PoisonNova), vEhc)
        PoisonNovaEruptExceed = self.load_skill_wrapper(_("{}(폭발)(초과)").format(ArchmageFirePoisonSkills.PoisonNova), vEhc)
        PoisonChain = self.load_skill_wrapper(ArchmageFirePoisonSkills.PoisonChain, vEhc)
        PoisonChainToxic = PoisonChainToxicWrapper(vEhc, 0, 0)

        Meteor = self.load_skill_wrapper(ArchmageFirePoisonSkills.MeteorShower, vEhc)
        MegidoFlame = self.load_skill_wrapper(ArchmageFirePoisonSkills.MegiddoFlame, vEhc)

        # Summoning Skills
        Ifritt = self.load_skill_wrapper(ArchmageFirePoisonSkills.Ifrit, vEhc)
        FireAura = self.load_skill_wrapper(ArchmageFirePoisonSkills.InfernoAura, vEhc)
        FuryOfIfritt = self.load_skill_wrapper(ArchmageFirePoisonSkills.ElementalFury, vEhc)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # Final Attack
        MeteorPassive = self.load_skill_wrapper(_("{}(패시브)").format(ArchmageFirePoisonSkills.MeteorShower), vEhc)
        Ignite = self.load_skill_wrapper(ArchmageFirePoisonSkills.Ignite, vEhc)
        IgniteMeteor = self.load_skill_wrapper(f"{ArchmageFirePoisonSkills.Ignite}({ArchmageFirePoisonSkills.MeteorShower})", vEhc)
        # Ignite : Need Wrapper

        # DoT Skills
        ParalyzeDOT = self.load_skill_wrapper(_("{}(도트)").format(ArchmageFirePoisonSkills.Paralyze))
        MistDOT = self.load_skill_wrapper(_("{}(도트)").format(ArchmageFirePoisonSkills.PoisonMist))
        IfrittDot = self.load_skill_wrapper(_("{}(도트)").format(ArchmageFirePoisonSkills.Ifrit))
        HeizeFlameDOT = self.load_skill_wrapper(_("{}(도트)").format(ArchmageFirePoisonSkills.FlameHaze))
        TeleportMasteryDOT = self.load_skill_wrapper(_("{}(도트)").format(ArchmageFirePoisonSkills.TeleportMastery))
        PoisonBreathDOT = self.load_skill_wrapper(_("{}(도트)").format(ArchmageFirePoisonSkills.PoisonBreath))
        MegidoFlameDOT = self.load_skill_wrapper(_("{}(도트)").format(ArchmageFirePoisonSkills.MegiddoFlame))
        DotPunisherDOT = self.load_skill_wrapper(_("{}(도트)").format(ArchmageFirePoisonSkills.DoTPunisher), vEhc)
        PoisonNovaDOT = self.load_skill_wrapper(_("{}(도트)").format(ArchmageFirePoisonSkills.PoisonNova), vEhc)

        # Unstable Memorize Skills
        EnergyBolt = self.load_skill_wrapper(ArchmageFirePoisonSkills.EnergyBolt)
        FlameOrb = self.load_skill_wrapper(ArchmageFirePoisonSkills.FlameOrb)
        PoisonBreath = self.load_skill_wrapper(ArchmageFirePoisonSkills.PoisonBreath)
        Explosion = self.load_skill_wrapper(ArchmageFirePoisonSkills.Explosion)  # magic6(720) -> explosion(180). Both are applied at the speed of 540+150. magic6(720) -> explosion(180). 둘 다 공속 적용되어 540+150.
        PoisonMist = self.load_skill_wrapper(ArchmageFirePoisonSkills.PoisonMist)
        SlimeVirus = self.load_skill_wrapper(ArchmageFirePoisonSkills.ViralSlime)

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
