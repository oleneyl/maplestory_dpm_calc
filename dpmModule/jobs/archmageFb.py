from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, MutualRule, InactiveRule
from . import globalSkill
from .jobclass import adventurer
from .jobbranch import magicians
from math import ceil

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = (0, 40)
        self.jobtype = "int"
        self.jobname = "아크메이지불/독"
        self.vEnhanceNum = 13
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'crit', 'boss_pdamage')
        self.preEmptiveSkills = 2

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(MutualRule('도트 퍼니셔', '포이즌 노바'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('언스테이블 메모라이즈', '인피니티'), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        HighWisdom = core.InformedCharacterModifier("하이 위즈덤", stat_main = 40)
        SpellMastery = core.InformedCharacterModifier("스펠 마스터리", att = 10)
        MagicCritical = core.InformedCharacterModifier("매직 크리티컬", crit = 30, crit_damage = 13)
        ElementAmplication = core.InformedCharacterModifier("엘리멘트 엠플리피케이션", pdamage = 50)
        
        ElementalReset = core.InformedCharacterModifier("엘리멘탈 리셋", pdamage_indep = 40)
        
        MasterMagic = core.InformedCharacterModifier("마스터 매직", att = 30 + 3*passive_level, buff_rem = 50 + 5*passive_level)
        ArcaneAim = core.InformedCharacterModifier("아케인 에임", armor_ignore = 20 + ceil(passive_level / 2))

        UnstableMemorizePassive = adventurer.UnstableMemorizePassiveWrapper(vEhc, 4, 4)
        
        return [HighWisdom, SpellMastery, MagicCritical, ElementalReset, 
                                    MasterMagic, ElementAmplication, ArcaneAim, UnstableMemorizePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -2.5 + 0.5*ceil(self.combat/2))
        ExtremeMagic = core.InformedCharacterModifier("익스트림 매직", pdamage_indep = 20)
        ArcaneAim = core.InformedCharacterModifier("아케인 (실시간)", pdamage = 40)
        PerventDrain = core.InformedCharacterModifier("퍼번트 드레인", pdamage_indep = 25)
        ElementalResetActive = core.InformedCharacterModifier("엘리멘탈 리셋(사용)", prop_ignore = 10)
        
        return [WeaponConstant, Mastery, ExtremeMagic, PerventDrain, ArcaneAim, ElementalResetActive]

    def generate(self, vEhc, chtr : ck.AbstractCharacter):
        '''
        포이즌 노바 4히트
        
        V 코어 강화 순위
        
        쓸윈/쓸샾/(쓸오더)/도퍼/노바/언스/오버마나
        이럽/패럴/헤이즈/이그나이트/오라/메테/이프/메기/텔마
        
        극딜형 스킬은 쿨마다 사용함
        언스테이블 메모라이즈는 인피니티가 꺼져있을때 사용
        
        '''
        DOT_PUNISHER_HIT = 22 # TODO: 현재 도트 개수를 참조해 타수 결정

        # Buff Skills
        Meditation = core.BuffSkill("메디테이션", 0, 240000, att = 30, rem = True, red = True).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        OverloadMana = magicians.OverloadManaWrapper(vEhc, 1, 5)
        Infinity = adventurer.InfinityWrapper(self.combat)
        
        # Damage Skills
        Paralyze = core.DamageSkill("페럴라이즈", 600, 220 + 3*self.combat, 7+1, modifier = core.CharacterModifier(pdamage = 10)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)

        TeleportMastery = core.DamageSkill("텔레포트 마스터리", 0, 272, 1, cooltime=-1).setV(vEhc, 9, 3, True).wrap(core.DamageSkillWrapper)
        
        ERUPTION_RATE = [0, 0, 20, 45, 80, 125]
        FlameHeize = core.DamageSkill("플레임 헤이즈", 1080, 202 + 3*self.combat, 15, cooltime = 10 * 1000, red=True).setV(vEhc, 2, 2, True).wrap(core.DamageSkillWrapper)
        MistEruption = core.DamageSkill("미스트 이럽션", 720, 46 + self.combat, 60, cooltime = 4 * 1000, red=False, modifier = core.CharacterModifier(armor_ignore = 40 + self.combat, pdamage_indep = ERUPTION_RATE[5]) + core.CharacterModifier(pdamage = 10, armor_ignore = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        DotPunisher = core.DamageSkill("도트 퍼니셔", 690, (400+vEhc.getV(0,0)*15), 5 * (1 + (DOT_PUNISHER_HIT - 1) * 0.65), cooltime = 25 * 1000, red = True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)#=775*(1+0.75*19)*5
        PoisonNova = core.DamageSkill("포이즌 노바", 570, 250 + 10*vEhc.getV(2,1), 12, cooltime = 25*1000, red = True).isV(vEhc,2,1).wrap(core.DamageSkillWrapper)
        PoisonNovaErupt = core.DamageSkill("포이즌 노바(폭발)", 0, 225 + 9*vEhc.getV(2,1), 12 * (3 + 0.50)).isV(vEhc,2,1).wrap(core.DamageSkillWrapper)
    
        Meteor = core.DamageSkill("메테오", 690, 225+self.combat*3, 12, cooltime = 45 * 1000, red=True).setV(vEhc, 5, 2, True).wrap(core.DamageSkillWrapper)
        MegidoFlame = core.DamageSkill("메기도 플레임", 690, 420, 15, cooltime = 50 * 1000).setV(vEhc, 8, 2, True).wrap(core.DamageSkillWrapper)
        
        # Summoning Skills
        Ifritt = core.SummonSkill("이프리트", 600, 3030, 90+2*self.combat, 3, (260+5*self.combat)*1000).setV(vEhc, 6, 2, False).wrap(core.SummonSkillWrapper)
        FireAura = core.SummonSkill("파이어 오라", 0, 3000, 400, 2, 999999999).setV(vEhc, 4, 2, True).wrap(core.SummonSkillWrapper)
        FuryOfIfritt = core.SummonSkill("퓨리 오브 이프리트", 480, 6000/25, 200+8*vEhc.getV(3,2), 6, 6*1000-1, cooltime = 75000, red = True).isV(vEhc,2,1).wrap(core.SummonSkillWrapper)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        # Final Attack
        METEOR_PROP = 0.6+0.02*self.combat
        MeteorPassive = core.DamageSkill("메테오(패시브)", 0, 220+4*self.combat, METEOR_PROP).setV(vEhc, 5, 2, True).wrap(core.DamageSkillWrapper)
        Ignite = core.DamageSkill("이그나이트", 0, 40, 3 * 3 * 0.5).setV(vEhc, 3, 4, False).wrap(core.DamageSkillWrapper)
        IgniteMeteor = core.DamageSkill("이그나이트(메테오)", 0, 40, 3 * 3 * 0.5 * METEOR_PROP).setV(vEhc, 3, 4, False).wrap(core.DamageSkillWrapper) # 메테오의 발동 확률 고려
        #Ignite : Need Wrapper
        
        # DoT Skills
        ParalyzeDOT = core.DotSkill("패럴라이즈(도트)", 0, 1000, 240 + self.combat * 4, 1, 10000, cooltime = -1).wrap(core.SummonSkillWrapper)
        MistDOT = core.DotSkill("포이즌 미스트(도트)", 0, 1000, 300 + self.combat * 1, 1, 12000, cooltime = -1).wrap(core.SummonSkillWrapper)
        IfrittDot = core.DotSkill("이프리트(도트)", 0, 1000, 140 + self.combat * 3, 1, 4000, cooltime = -1).wrap(core.SummonSkillWrapper)
        HeizeFlameDOT = core.DotSkill("플레임 헤이즈(도트)", 0, 1000, 200 + self.combat * 3, 1, 20000, cooltime = -1).wrap(core.SummonSkillWrapper)
        TeleportMasteryDOT = core.DotSkill("텔레포트 마스터리(도트)", 0, 1000, 49, 1, 8000, cooltime = -1).wrap(core.SummonSkillWrapper)
        PoisonBreathDOT = core.DotSkill("포이즌 브레스(도트)", 0, 1000, 60, 1, 20000, cooltime = -1).wrap(core.SummonSkillWrapper)
        MegidoFlameDOT = core.DotSkill("메기도 플레임(도트)", 0, 1000, 700, 1, 60000, cooltime = -1).wrap(core.SummonSkillWrapper)
        DotPunisherDOT = core.DotSkill("도트 퍼니셔(도트)", 0, 1000, 200+3*vEhc.getV(0,0), 1, 16000, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        PoisonNovaDOT = core.DotSkill("포이즌 노바(도트)", 0, 1000, 300+12*vEhc.getV(2,1), 1, 20000, cooltime = -1).isV(vEhc,2,1).wrap(core.SummonSkillWrapper)

        # Unstable Memorize Skills
        EnergyBolt = core.DamageSkill("에너지 볼트", 630, 309, 1).wrap(core.DamageSkillWrapper)
        FlameOrb = core.DamageSkill("플레임 오브", 630, 301, 2).wrap(core.DamageSkillWrapper)
        PoisonBreath = core.DamageSkill("포이즌 브레스", 600, 180, 1).wrap(core.DamageSkillWrapper)
        Explosion = core.DamageSkill("익스플로젼", 540, 405, 2).wrap(core.DamageSkillWrapper)
        PoisonMist = core.DamageSkill("포이즌 미스트", 1140, 270, 1).wrap(core.DamageSkillWrapper)
        SlimeVirus = core.DotSkill("슬라임 바이러스", 1680, 1000, 160, 1, 10000, cooltime=-1).wrap(core.SummonSkillWrapper)
        
        # Unstable Memorize
        UnstableMemorize = adventurer.UnstableMemorizeWrapper(vEhc, 4, 4, chtr.get_skill_modifier())
        
        for sk, weight in [(EnergyBolt, 1), (FlameOrb, 5), (PoisonBreath, 5), (Explosion, 10),
                            (PoisonMist, 10), (SlimeVirus, 10), (Paralyze, 25), (MistEruption, 25), (Meteor, 25),
                            (FlameHeize, 25), (Infinity, 25), (Ifritt, 25), (MegidoFlame, 25), (EpicAdventure, 10)]:
            UnstableMemorize.add_skill(sk, weight)
        
        # Ignite
        FlameOrb.onAfter(Ignite)
        Explosion.onAfter(Ignite)
        Paralyze.onAfter(Ignite)
        FlameHeize.onAfter(Ignite)
        Meteor.onAfter(Ignite)
        MeteorPassive.onAfter(IgniteMeteor)
        Ifritt.onTick(Ignite)
        MegidoFlame.onAfter(Ignite)
        FireAura.onTick(Ignite)
        DotPunisher.onAfter(core.RepeatElement(Ignite, DOT_PUNISHER_HIT))
        FuryOfIfritt.onAfter(core.RepeatElement(Ignite, 25))

        # Meteor Passive
        EnergyBolt.onAfter(MeteorPassive)
        FlameOrb.onAfter(MeteorPassive)
        PoisonBreath.onAfter(MeteorPassive)
        Explosion.onAfter(MeteorPassive)
        PoisonMist.onAfter(MeteorPassive)
        Paralyze.onAfter(MeteorPassive)
        MistEruption.onAfter(MeteorPassive)
        FlameHeize.onAfter(MeteorPassive)
        DotPunisher.onAfter(core.RepeatElement(MeteorPassive, DOT_PUNISHER_HIT))
        PoisonNova.onAfter(MeteorPassive)

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
        PoisonNova.onAfter(PoisonNovaErupt)
        MistEruption.onAfter(FlameHeize.controller(1, 'reduce_cooltime_p'))

        return (Paralyze, 
                [Infinity, Meditation, EpicAdventure, OverloadMana.ensure(vEhc,1,5),
                globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_wind_booster(),
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()] +\
                [DotPunisher.ensure(vEhc,0,0), Meteor, MegidoFlame, FlameHeize, MistEruption, PoisonNova.ensure(vEhc,2,1), MirrorBreak, MirrorSpider] +\
                [Ifritt, FireAura, FuryOfIfritt.ensure(vEhc,3,2),
                    SlimeVirus, ParalyzeDOT, MistDOT, PoisonBreathDOT, IfrittDot, HeizeFlameDOT, TeleportMasteryDOT, MegidoFlameDOT, DotPunisherDOT.ensure(vEhc,0,0), PoisonNovaDOT.ensure(vEhc,2,1)] +\
                [UnstableMemorize] +\
                [Paralyze])