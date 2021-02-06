from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule, InactiveRule
from . import globalSkill
from .jobclass import adventurer
from .jobbranch import magicians
from math import ceil
from typing import Any, Dict

class FrostEffectWrapper(core.StackSkillWrapper):
    def __init__(self, skill):
        super(FrostEffectWrapper, self).__init__(skill, 5)
        self.stack = 5  # Better point!
        self.modifierInvariantFlag = False
    
    def get_modifier(self):
        return core.CharacterModifier(crit_damage = 3*self.stack, armor_ignore = 0.2*5*self.stack)


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = (0, 40)
        self.jobtype = "INT"
        self.jobname = "아크메이지썬/콜"
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'crit', 'boss_pdamage')
        self.preEmptiveSkills = 2
        
    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 20, pdamage = 60, crit_damage = 15)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule(ArchmageIceLightningSkills.LightningOrb.value, AdventurerSkills.Infinity.value), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(AdventurerSkills.UnreliableMemory.value, AdventurerSkills.Infinity.value), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        ######   Passive Skill   ######
        
        HighWisdom = core.InformedCharacterModifier(ArchmageIceLightningSkills.HighWisdom.value, stat_main = 40)
        SpellMastery = core.InformedCharacterModifier(ArchmageIceLightningSkills.SpellMastery.value, att = 10)
        MagicCritical = core.InformedCharacterModifier(ArchmageIceLightningSkills.ArcaneOverdrive.value, crit = 30, crit_damage = 13)
        ElementAmplication = core.InformedCharacterModifier(ArchmageIceLightningSkills.ElementAmplification.value, pdamage = 50)
        
        ElementalReset = core.InformedCharacterModifier(ArchmageIceLightningSkills.ElementalDecrease.value, pdamage_indep = 50)
        
        MasterMagic = core.InformedCharacterModifier(ArchmageIceLightningSkills.BuffMastery.value, att = 30 + 3*passive_level, buff_rem = 50 + 5*passive_level)
        ArcaneAim = core.InformedCharacterModifier(ArchmageIceLightningSkills.ArcaneAim.value, armor_ignore = 20 + ceil(passive_level / 2))

        UnstableMemorizePassive = adventurer.UnstableMemorizePassiveWrapper(vEhc, 4, 4)
        
        return [HighWisdom, SpellMastery, MagicCritical, ElementalReset, MasterMagic, ElementAmplication, ArcaneAim, UnstableMemorizePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -2.5 + 0.5*ceil(self.combat/2))
        ExtremeMagic = core.InformedCharacterModifier(ArchmageIceLightningSkills.StormMagic.value, pdamage_indep = 20)
        ArcaneAim = core.InformedCharacterModifier(f"{ArchmageIceLightningSkills.ArcaneAim.value}(real time | 실시간)", pdamage = 40)
        ElementalResetActive = core.InformedCharacterModifier(f"{ArchmageIceLightningSkills.ElementalDecrease.value}(active | 사용)", prop_ignore = 10)
        
        return [WeaponConstant, Mastery, ExtremeMagic, ArcaneAim, ElementalResetActive]
        
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
        #Buff skills
        Meditation = core.BuffSkill(ArchmageIceLightningSkills.Meditation.value, 0, 240*1000, att = 30, rem = True, red = True).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill(ArchmageIceLightningSkills.EpicAdventure.value, 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        #Damage Skills
        ChainLightening = core.DamageSkill(ArchmageIceLightningSkills.ChainLightning.value, 600, 185 + 3*self.combat, 10+1, modifier = core.CharacterModifier(crit = 25+ceil(self.combat/2), pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        FrozenOrb = core.SummonSkill(ArchmageIceLightningSkills.FrozenOrb.value, 690, 210, 220+4*self.combat, 1, 4000, cooltime = 5000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)
    
        LighteningSpear = core.DamageSkill(ArchmageIceLightningSkills.LightningOrb.value, 0, 0, 1, cooltime = 75 * 1000).wrap(core.DamageSkillWrapper)
        LighteningSpearSingle = core.DamageSkill(f"{ArchmageIceLightningSkills.LightningOrb.value}(keydown | 키다운)", 267, 105, 15).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper) # 총 8010ms
        LighteningSpearFinalizer = core.DamageSkill(f"{ArchmageIceLightningSkills.LightningOrb.value}(final hit | 막타)", 1080, 350, 15).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        
        IceAgeInit = core.DamageSkill(f"{ArchmageIceLightningSkills.IceAge.value}(cast | 개시)", 660, 500 + vEhc.getV(2,3)*20, 10, cooltime = 60 * 1000, red = True).isV(vEhc,2,3).wrap(core.DamageSkillWrapper)
        IceAgeSummon = core.SummonSkill(f"{ArchmageIceLightningSkills.IceAge.value}(summon | 장판)", 0, 810, 125 + vEhc.getV(2,3)*5, 3*ICE_AGE_SUMMON_HIT, 15 * 1000, cooltime = -1).isV(vEhc,2,3).wrap(core.SummonSkillWrapper)

        # 5% reduction per stack. 중첩당 감소량 5%.
        # TODO: ?? must implement canceling the previous skill delay. 썬브가 이전 스킬 딜레이 캔슬하는것 구현해야 함.
        ThunderBrake = core.DamageSkill(f"{ArchmageIceLightningSkills.BoltBarrage.value}(start skill | 개시스킬)", 120, 0, 1, red = True, cooltime = 40 * 1000).wrap(core.DamageSkillWrapper)  # Awesome! -> Tandem injection treatment is required...Later. Distribute the 690 as soon as possible. Awesome! -> Tandem 사출처리 해야함...Later. 690을 일단 급한대로 분배해서 사용.
        ThunderBrake1 = core.DamageSkill(f"{ArchmageIceLightningSkills.BoltBarrage.value}(1)", 120, (750 + vEhc.getV(0,0)*30), 8).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ThunderBrake2 = core.DamageSkill(f"{ArchmageIceLightningSkills.BoltBarrage.value}(2)", 120, (750 + vEhc.getV(0,0)*30)*0.95, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake3 = core.DamageSkill(f"{ArchmageIceLightningSkills.BoltBarrage.value}(3)", 120, (750 + vEhc.getV(0,0)*30)*0.9, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake4 = core.DamageSkill(f"{ArchmageIceLightningSkills.BoltBarrage.value}(4)", 120, (750 + vEhc.getV(0,0)*30)*0.85, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake5 = core.DamageSkill(f"{ArchmageIceLightningSkills.BoltBarrage.value}(5)", 120, (750 + vEhc.getV(0,0)*30)*0.8, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake6 = core.DamageSkill(f"{ArchmageIceLightningSkills.BoltBarrage.value}(6)", 120, (750 + vEhc.getV(0,0)*30)*0.75, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake7 = core.DamageSkill(f"{ArchmageIceLightningSkills.BoltBarrage.value}(7)", 120, (750 + vEhc.getV(0,0)*30)*0.7, 8).wrap(core.DamageSkillWrapper)
        ThunderBrake8 = core.DamageSkill(f"{ArchmageIceLightningSkills.BoltBarrage.value}(8)", 120, (750 + vEhc.getV(0,0)*30)*0.65, 8).wrap(core.DamageSkillWrapper)
        
        # Single target criteria. 단일 대상 기준.
        SpiritOfSnow = core.SummonSkill(ArchmageIceLightningSkills.SpiritofSnow.value, 720, 3000, 850+34*vEhc.getV(3,1), 9, 30000, red = True, cooltime = 120*1000).isV(vEhc, 3,1).wrap(core.SummonSkillWrapper)
        
        #Summoning skill
        ThunderStorm = core.SummonSkill("썬더 스톰", 900, 1770, 430, 1, 90000, cooltime = 30000).setV(vEhc, 5, 3, False).wrap(core.SummonSkillWrapper)
        Elquiness = core.SummonSkill(ArchmageIceLightningSkills.Elquines.value, 600, 3030, 127+2*self.combat, 3, (260+5*self.combat)*1000).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)
        IceAura = core.SummonSkill(ArchmageIceLightningSkills.AbsoluteZeroAura.value, 0, 1200, 0, 1, 999999999).wrap(core.SummonSkillWrapper)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        JupyterThunder = core.SummonSkill(ArchmageIceLightningSkills.JupiterThunder.value, 630, 330, 300+12*vEhc.getV(0,0), 5, 330*30-1, cooltime=75000, red=True).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        
        #FinalAttack
        Blizzard = core.DamageSkill(ArchmageIceLightningSkills.Blizzard.value, 690, 301+3*self.combat, 12, cooltime = 45 * 1000, red = True).setV(vEhc, 2, 2, True).wrap(core.DamageSkillWrapper)
        BlizzardPassive = core.DamageSkill(f"{ArchmageIceLightningSkills.Blizzard.value}(passive | 패시브)", 0, (220+4*self.combat) * (0.6+0.01*self.combat), 1).setV(vEhc, 2, 2, True).wrap(core.DamageSkillWrapper)
        
        #special skills
        Infinity = adventurer.InfinityWrapper(self.combat)
        FrostEffect = core.BuffSkill(ArchmageIceLightningSkills.FrostClutch.value, 0, 999999 * 1000).wrap(FrostEffectWrapper)

        #Unstable Memorize skills
        EnergyBolt = core.DamageSkill(ArchmageIceLightningSkills.EnergyBolt.value, 630, 309, 1).wrap(core.DamageSkillWrapper)
        ColdBeam = core.DamageSkill(ArchmageIceLightningSkills.ColdBeam.value, 630, 199, 3).wrap(core.DamageSkillWrapper)
        ThunderBolt = core.DamageSkill("썬더 볼트", 630, 210, 3).wrap(core.DamageSkillWrapper)
        IceStrike = core.DamageSkill(ArchmageIceLightningSkills.IceStrike.value, 630, 335, 4).wrap(core.DamageSkillWrapper)
        GlacialChain = core.DamageSkill(ArchmageIceLightningSkills.GlacierChain.value, 630, 383, 3).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
        #Unstable Memorize
        UnstableMemorize = adventurer.UnstableMemorizeWrapper(vEhc, 4, 4, chtr.get_skill_modifier())
        
        for sk, weight in [(EnergyBolt, 1), (ColdBeam, 5), (ThunderBolt, 5), (IceStrike, 10),
                            (GlacialChain, 10), (ThunderStorm, 10), (ChainLightening, 25), (Blizzard, 25), (FrozenOrb, 25),
                            (Infinity, 25), (Elquiness, 25), (LighteningSpear, 10), (EpicAdventure, 10)]:
            UnstableMemorize.add_skill(sk, weight)

        #Frost Effect
        FrostIncrement = FrostEffect.stackController(1)
        FrostDecrement = FrostEffect.stackController(-1)
        def applyFrostEffect(sk: FrostEffect):
            return core.CharacterModifier(pdamage = sk.stack * 12)

        #Energy Bolt
        EnergyBolt.onAfter(BlizzardPassive)

        #Cold Beam
        ColdBeam.onJustAfter(FrostIncrement)
        ColdBeam.onAfter(BlizzardPassive)

        #Thunder Bolt
        ThunderBolt.add_runtime_modifier(FrostEffect, applyFrostEffect)
        ThunderBolt.onJustAfter(FrostDecrement)
        ThunderBolt.onAfter(BlizzardPassive)

        #Ice Strike
        IceStrike.onJustAfter(FrostIncrement)
        IceStrike.onAfter(BlizzardPassive)

        #Glacial Chain
        GlacialChain.onJustAfter(FrostIncrement)
        GlacialChain.onAfter(BlizzardPassive)

        #Thunder Storm
        ThunderStorm.add_runtime_modifier(FrostEffect, applyFrostEffect)
        
        #Elquiness
        Elquiness.onTick(FrostIncrement)
        
        #Frozen Orb
        FrozenOrb.onTick(BlizzardPassive)  # TODO: If the order of onTick execution changes, the order must be adjusted. onTick 실행순서 바뀌면 순서 조정해야 함.
        FrozenOrb.onTick(FrostIncrement)
        
        #Chain Lightening
        ChainLightening.add_runtime_modifier(FrostEffect, applyFrostEffect)
        ChainLightening.onJustAfter(FrostDecrement)
        ChainLightening.onAfter(BlizzardPassive)
        
        #Blizzard
        Blizzard.onJustAfter(FrostIncrement)
        BlizzardPassive.onJustAfter(FrostEffect.stackController(0.6))

        #Lightening Spear
        LighteningSpearSingle.add_runtime_modifier(FrostEffect, applyFrostEffect)
        LighteningSpearSingle.onJustAfter(FrostDecrement)
        LighteningSpearSingle.onAfter(BlizzardPassive)
        LighteningSpearFinalizer.add_runtime_modifier(FrostEffect, applyFrostEffect)
        LighteningSpearFinalizer.onJustAfter(FrostDecrement)
        LighteningSpearFinalizer.onAfter(BlizzardPassive)
        
        LighteningRepeator = core.RepeatElement(LighteningSpearSingle, 30)
        LighteningRepeator.onAfter(LighteningSpearFinalizer)
    
        LighteningSpear.onAfter(LighteningRepeator)
        
        #Ice Aura
        IceAura.onTick(FrostIncrement)
        
        #Ice Age
        IceAgeSummon.onTick(core.RepeatElement(FrostIncrement, ICE_AGE_SUMMON_HIT))
        IceAgeInit.onJustAfter(FrostIncrement)
        IceAgeInit.onAfter(BlizzardPassive)
        IceAgeInit.onAfter(IceAgeSummon)
        
        #Thunder Break
        for node in [ThunderBrake1, ThunderBrake2, ThunderBrake3, ThunderBrake4, ThunderBrake5, ThunderBrake6, ThunderBrake7, ThunderBrake8][:THUNDER_BREAK_HIT]:
            node.add_runtime_modifier(FrostEffect, applyFrostEffect)
            node.onJustAfter(FrostDecrement)
            node.onAfter(BlizzardPassive)
            ThunderBrake.onAfter(node)
        
        #Spirit of Snow
        SpiritOfSnow.onTick(FrostEffect.stackController(3))

        #Jupyter Thunder
        JupyterThunder.add_runtime_modifier(FrostEffect, applyFrostEffect)  # TODO: Make sure that Blizzard does not burst. 블리자드 파택 안터지는게 맞는지 확인할것.
        for i in range(1, 6 + 1):
            JupyterThunder.onEventElapsed(FrostDecrement, 330 * 5 * i) # 5회 타격시마다 빙결 감소, 총 6회 감소

        #Overload Mana
        overload_mana_builder = magicians.OverloadManaBuilder(vEhc, 1, 5)
        for sk in [ChainLightening, FrozenOrb, Blizzard, LighteningSpearSingle, LighteningSpearFinalizer, IceAgeInit,
                    ThunderBrake1, ThunderBrake2, ThunderBrake3, ThunderBrake4, ThunderBrake5, ThunderBrake6, ThunderBrake7, ThunderBrake8,
                    JupyterThunder, EnergyBolt, ColdBeam, ThunderBolt, IceStrike, GlacialChain]:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()

        return(ChainLightening,
                [Infinity, Meditation, EpicAdventure, OverloadMana, FrostEffect,
                globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_wind_booster(),
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()] +\
                [IceAgeInit, Blizzard, JupyterThunder, LighteningSpear, ThunderBrake, MirrorBreak, MirrorSpider] +\
                [ThunderStorm, Elquiness, IceAura, IceAgeSummon, FrozenOrb, SpiritOfSnow] +\
                [UnstableMemorize] +\
                [ChainLightening])