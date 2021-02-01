import os

from typing import Any, Dict

from . import globalSkill
from ..kernel import core
from .jobclass import adventurer
from .jobbranch import magicians
from ..status.ability import Ability_tool
from ..character import characterKernel as ck
from ..execution.rules import RuleSet, MutualRule, InactiveRule


class PoisonChainToxicWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        skill = core.SummonSkill(
            "포이즌 체인(중독)",  # Poison chain (addiction)
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
        ruleset.add_rule(MutualRule('도트 퍼니셔', '포이즌 노바'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('언스테이블 메모라이즈', '인피니티'), RuleSet.BASE)
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
        Meditation = self.load_skill_wrapper("메디테이션")
        EpicAdventure = self.load_skill_wrapper("에픽 어드벤처")
        Infinity = adventurer.InfinityWrapper(self.combat)

        # Damage Skills
        Paralyze = self.load_skill_wrapper("페럴라이즈", vEhc)
        TeleportMastery = self.load_skill_wrapper("텔레포트 마스터리", vEhc)

        FlameHeize = self.load_skill_wrapper("플레임 헤이즈", vEhc)
        MistEruption = self.load_skill_wrapper("미스트 이럽션", vEhc)

        DotPunisher = self.load_skill_wrapper("도트 퍼니셔", vEhc)
        DotPunisherExceed = self.load_skill_wrapper("도트 퍼니셔(초과)", vEhc)
        PoisonNova = self.load_skill_wrapper("포이즌 노바", vEhc)
        PoisonNovaErupt = self.load_skill_wrapper("포이즌 노바(폭발)", vEhc)
        PoisonNovaEruptExceed = self.load_skill_wrapper("포이즌 노바(폭발)(초과)", vEhc)
        PoisonChain = self.load_skill_wrapper("포이즌 체인", vEhc)
        PoisonChainToxic = PoisonChainToxicWrapper(vEhc, 0, 0)

        Meteor = self.load_skill_wrapper("메테오", vEhc)
        MegidoFlame = self.load_skill_wrapper("메기도 플레임", vEhc)

        # Summoning Skills
        Ifritt = self.load_skill_wrapper("이프리트", vEhc)
        FireAura = self.load_skill_wrapper("파이어 오라", vEhc)
        FuryOfIfritt = self.load_skill_wrapper("퓨리 오브 이프리트", vEhc)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # Final Attack
        MeteorPassive = self.load_skill_wrapper("메테오(패시브)", vEhc)
        Ignite = self.load_skill_wrapper("이그나이트", vEhc)
        IgniteMeteor = self.load_skill_wrapper("이그나이트(메테오)", vEhc)
        # Ignite : Need Wrapper

        # DoT Skills
        ParalyzeDOT = self.load_skill_wrapper("페럴라이즈(도트)")
        MistDOT = self.load_skill_wrapper("포이즌 미스트(도트)")
        IfrittDot = self.load_skill_wrapper("이프리트(도트)")
        HeizeFlameDOT = self.load_skill_wrapper("플레임 헤이즈(도트)")
        TeleportMasteryDOT = self.load_skill_wrapper("텔레포트 마스터리(도트)")
        PoisonBreathDOT = self.load_skill_wrapper("포이즌 브레스(도트)")
        MegidoFlameDOT = self.load_skill_wrapper("메기도 플레임(도트)")
        DotPunisherDOT = self.load_skill_wrapper("도트 퍼니셔(도트)", vEhc)
        PoisonNovaDOT = self.load_skill_wrapper("포이즌 노바(도트)", vEhc)

        # Unstable Memorize Skills
        EnergyBolt = self.load_skill_wrapper("에너지 볼트")
        FlameOrb = self.load_skill_wrapper("플레임 오브")
        PoisonBreath = self.load_skill_wrapper("포이즌 브레스")
        Explosion = self.load_skill_wrapper("익스플로젼")  # magic6(720) -> explosion(180). Both are applied at the speed of 540+150. magic6(720) -> explosion(180). 둘 다 공속 적용되어 540+150.
        PoisonMist = self.load_skill_wrapper("포이즌 미스트")
        SlimeVirus = self.load_skill_wrapper("슬라임 바이러스")

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
