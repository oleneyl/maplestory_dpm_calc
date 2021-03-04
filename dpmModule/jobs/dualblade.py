from .globalSkill import GlobalSkills, DOT, BUFF, DEBUFF, TICK, SUMMON, ENDING
from .jobbranch.thieves import ThiefSkills
from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ComplexConditionRule, RuleSet, ConditionRule
from . import globalSkill
from .jobbranch import thieves
from . import jobutils
from math import ceil
from typing import Any, Dict

from localization.utilities import translator
_ = translator.gettext

# TODO: Why is Retouda 5th order value 1,1, but Retouda passive is 2,2? 왜 레투다는 5차값이 1,1인데 레투다 패시브는 2,2일까?


# English skill information for Dual Blade here https://maplestory.fandom.com/wiki/Dual_Blade/Skills
class DualBladeSkills:
    # Link Skill
    ThiefsCunning = _("시프 커닝")  # "Thief's Cunning"
    # Rogue
    DarkSight = _("다크 사이트")  # "Dark Sight"
    FlashJump = _("플래시 점프")  # "Flash Jump"
    SideStep = _("사이드 스텝")  # "Side Step"
    BanditSlash = _("샤프 슬래시")  # "Bandit Slash"
    # Blade Recruit
    KataraMastery = _("이도류 마스터리")  # "Katara Mastery"
    SelfHaste = _("셀프 헤이스트")  # "Self Haste"
    TornadoSpin = _("토네이도 스핀")  # "Tornado Spin"
    # Blade Acolyte
    FatalBlow = _("페이탈 블로우")  # "Fatal Blow"
    SlashStorm = _("슬래시 스톰")  # "Slash Storm"
    ChannelKarma = _("카르마")  # "Channel Karma"
    KataraBooster = _("이도 부스터")  # "Katara Booster"
    PhysicalTraining = _("피지컬 트레이닝")  # "Physical Training"
    # Blade Specialist
    FlyingAssaulter = _("플라잉 어썰터")  # "Flying Assaulter"
    UpperStab = _("어퍼 스탭")  # "Upper Stab"
    Flashbang = _("플래시 뱅")  # "Flashbang"
    Venom = _("베놈")  # "Venom"
    # Blade Lord
    BloodyStorm = _("블러디 스톰")  # "Bloody Storm"
    BladeAscension = _("블레이드 어센션")  # "Blade Ascension"
    ChainsofHell = _("사슬지옥")  # "Chains of Hell"
    MirrorImage = _("미러이미징")  # "Mirror Image"
    AdvancedDarkSight = _("어드밴스드 다크 사이트")  # "Advanced Dark Sight"
    LifeDrain = _("바이탈 스틸")  # "Life Drain"
    EnvelopingDarkness = _("래디컬 다크니스")  # "Enveloping Darkness"
    ShadowMeld = _("섀도우 이베이젼")  # "Shadow Meld"
    # Blade Master
    BladeFury = _("블레이드 퓨리")  # "Blade Fury"
    PhantomBlow = _("팬텀 블로우")  # "Phantom Blow"
    FinalCut = _("파이널 컷")  # "Final Cut"
    SuddenRaid = _("써든레이드")  # "Sudden Raid"
    MirroredTarget = _("더미 이펙트")  # "Mirrored Target"
    Thorns = _("쏜즈 이펙트")  # "Thorns"
    Sharpness = _("샤프니스")  # "Sharpness"
    ToxicVenom = _("페이탈 베놈")  # "Toxic Venom"
    KataraExpert = _("이도류 엑스퍼트")  # "Katara Expert"
    # Hypers
    AsurasAnger = _("아수라")  # "Asura's Anger"
    EpicAdventure = _("에픽 어드벤처")  # "Epic Adventure"
    BladeClone = _("히든 블레이드")  # "Blade Clone"
    # 5th Job
    BladeTempest = _("블레이드 스톰")  # "Blade Tempest"
    BladesofDestiny = _("카르마 퓨리")  # "Blades of Destiny"
    BladeTornado = _("블레이드 토네이도")  # "Blade Tornado"
    HauntedEdge = _("헌티드 엣지")  # "Haunted Edge"


# Skill name modifiers only for dual blade
YAKSA = _("나찰")


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "LUK2"
        self.jobname = _("듀얼블레이드")
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=36, armor_ignore=47.7)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        Karma = core.InformedCharacterModifier(DualBladeSkills.ChannelKarma, att = 30)
        PhisicalTraining = core.InformedCharacterModifier(DualBladeSkills.PhysicalTraining, stat_main = 30, stat_sub = 30)
        
        SornsEffect = core.InformedCharacterModifier(DualBladeSkills.Thorns, att = 30 + passive_level)
        DualBladeExpert = core.InformedCharacterModifier(DualBladeSkills.KataraExpert, att = 30 + passive_level, pdamage_indep = 20 + passive_level // 2)
        Sharpness = core.InformedCharacterModifier(DualBladeSkills.Sharpness, crit = 35 + 3 * passive_level, crit_damage = 13 + passive_level)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 2, 2)
        
        return [Karma, PhisicalTraining, SornsEffect, DualBladeExpert, Sharpness, ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90+ceil(passive_level / 2))
        return [WeaponConstant, Mastery]

    def get_ruleset(self):
        def check_final_cut_time(final_cut):
            return (final_cut.is_not_usable() and final_cut.is_cooltime_left(80*1000, 1)) # It is more efficient to use only one harrow immediately after breaking. 파컷 직후 써레 1번만 쓰는게 더 효율적임.

        def sync_burst_buff(burst_buff, blade_storm, ultimate_dark_sight):
            if blade_storm.is_usable():
                if ultimate_dark_sight.is_cooltime_left(80000, 1) or ultimate_dark_sight.is_active():
                    return True
            return False

        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule(DualBladeSkills.SuddenRaid, DualBladeSkills.FinalCut, check_final_cut_time), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(DualBladeSkills.AsurasAnger, DualBladeSkills.BladesofDestiny, lambda sk: sk.is_cooltime_left(6000, 1)), RuleSet.BASE)  # TODO: Optimized for 4 seconds of cooldown reduction, you need to receive and process cooldown reduction values. 쿨감 4초기준 최적화, 쿨감 수치를 받아와서 처리해야 함.
        ruleset.add_rule(ComplexConditionRule(ThiefSkills.LastResort, [DualBladeSkills.BladeTempest, ThiefSkills.ShadowWalker], sync_burst_buff), RuleSet.BASE)
        ruleset.add_rule(ComplexConditionRule(GlobalSkills.TermsAndConditions, [DualBladeSkills.BladeTempest, ThiefSkills.ShadowWalker], sync_burst_buff), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(DualBladeSkills.BladeTempest, ThiefSkills.ShadowWalker, lambda sk: sk.is_active() or sk.is_cooltime_left(80000, 1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(GlobalSkills.MapleWorldGoddessBlessing, ThiefSkills.ShadowWalker, lambda sk: sk.is_active() or sk.is_usable()), RuleSet.BASE)
        return ruleset

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Hyper: Phantom Blow-Reinforce, Ignor Guard, Bonus Attack
        Blade Fury-Reinforce, Extra Target

        Asura 41 strokes
        Blade Tornado 5 Hits

        16 cores valid: Fanble / Asura / Fury - Sudden Raid / Ascension / Hidden Blade

        하이퍼 : 팬텀 블로우 - 리인포스, 이그노어 가드, 보너스 어택
        블레이드 퓨리 - 리인포스, 엑스트라 타겟
        
        아수라 41타
        블레이드 토네이도 5타
        
        코어 16개 유효 : 팬블 / 아수라 / 퓨리 -- 써든레이드 / 어센션 / 히든블레이드
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        #Buff skills
        Booster = core.BuffSkill(DualBladeSkills.KataraBooster, 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        
        DarkSight = core.BuffSkill(DualBladeSkills.DarkSight, 0, 1, cooltime = -1).wrap(core.BuffSkillWrapper)#, pdamage_indep = 20 + 10 + int(0.2*vEhc.getV(3,3))).wrap(core.BuffSkillWrapper)
        
        PhantomBlow = core.DamageSkill(DualBladeSkills.PhantomBlow, 540, 315 + 3 * self.combat, 6+1, modifier = core.CharacterModifier(armor_ignore = 44, pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        SuddenRaid = core.DamageSkill(DualBladeSkills.SuddenRaid, 690, 494+5*self.combat, 7, cooltime = (30-2*(self.combat//2))*1000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)    # Pacutt's remaining cooldown is reduced by 20%. 파컷의 남은 쿨타임 20% 감소.
        SuddenRaidDOT = core.DotSkill(f"{DualBladeSkills.SuddenRaid}({DOT})", 0, 1000, 210 + 4 * self.combat, 1, 10000, cooltime = -1).wrap(core.DotSkillWrapper)

        FinalCut = core.DamageSkill(DualBladeSkills.FinalCut, 450, 2000 + 20 * self.combat, 1, cooltime = 90000, red=True).wrap(core.DamageSkillWrapper)
        FinalCutBuff = core.BuffSkill(f"{DualBladeSkills.FinalCut}({BUFF})", 0, 60000, rem = True, cooltime = -1, pdamage_indep = 40 + self.combat).wrap(core.BuffSkillWrapper)
        
        EpicAdventure = core.BuffSkill(DualBladeSkills.EpicAdventure, 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        FlashBang = core.DamageSkill(DualBladeSkills.Flashbang, 390, 250, 1, cooltime = 60000, red=True).wrap(core.DamageSkillWrapper)  # Random delay. 임의 딜레이.
        FlashBangDebuff = core.BuffSkill(f"{DualBladeSkills.Flashbang}({DEBUFF})", 0, 50000/2, cooltime = -1, pdamage = 10 * 0.9).wrap(core.BuffSkillWrapper)
        Venom = core.DotSkill(DualBladeSkills.ToxicVenom, 0, 1000, 160+5*passive_level, 2+(10+passive_level)//6, 8000, cooltime = -1).wrap(core.DotSkillWrapper)  # Stacks 3 times. 3회 중첩.

        HiddenBladeBuff = core.BuffSkill(f"{DualBladeSkills.BladeClone}({BUFF})", 0, 60000, cooltime = 90000, pdamage = 10).wrap(core.BuffSkillWrapper)
        HiddenBlade = core.DamageSkill(DualBladeSkills.BladeClone, 0, 140, 1).setV(vEhc, 5, 2, True).wrap(core.DamageSkillWrapper)
        
        Asura = core.DamageSkill(DualBladeSkills.AsurasAnger, 810, 0, 0, cooltime = 60000).wrap(core.DamageSkillWrapper)
        AsuraTick = core.DamageSkill(f"{DualBladeSkills.AsurasAnger}({TICK})", 300, 420, 4, modifier =core.CharacterModifier(armor_ignore = 100)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AsuraEnd = core.DamageSkill(f"{DualBladeSkills.AsurasAnger}({ENDING})", 360, 0, 0, cooltime = -1).wrap(core.DamageSkillWrapper)
        
        UltimateDarksight = thieves.UltimateDarkSightWrapper(vEhc, 3, 3, 20)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc,4,4)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        BladeStorm = core.DamageSkill(DualBladeSkills.BladeTempest, 120, 580+23*vEhc.getV(0,0), 7, red = True, cooltime = 90000, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        BladeStormTick = core.DamageSkill(f"{DualBladeSkills.BladeTempest}({TICK})", 210, 350+10*vEhc.getV(0,0), 5, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)  #10000/210 타
        BladeStormEnd = core.DamageSkill(f"{DualBladeSkills.BladeTempest}({ENDING})", 120, 0, 0).wrap(core.DamageSkillWrapper)
        
        KarmaFury = core.DamageSkill(DualBladeSkills.BladesofDestiny, 750, 400+16*vEhc.getV(1,1), 7 * 5, red = True, cooltime = 10000, modifier = core.CharacterModifier(armor_ignore = 30)).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        BladeTornado = core.DamageSkill(DualBladeSkills.BladeTornado, 540, 600+24*vEhc.getV(2,2), 7, red = True, cooltime = 12000, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        BladeTornadoSummon = core.SummonSkill(f"{DualBladeSkills.BladeTornado}({SUMMON})", 0, 3000/5, 400+16*vEhc.getV(2,2), 6, 3000-1, cooltime=-1, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
        BladeTornadoSummonMirrorImaging = core.SummonSkill(f"{DualBladeSkills.BladeTornado}({SUMMON})({DualBladeSkills.MirrorImage})", 0, 3000/5, (400+16*vEhc.getV(2,2)) * 0.7, 6, 3000-1, cooltime=-1, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)

        HauntedEdge = core.DamageSkill(f"{DualBladeSkills.HauntedEdge}({YAKSA})", 0, 200+8*vEhc.getV(0,0), 4*5, cooltime=14000, red=True, modifier=core.CharacterModifier(armor_ignore=30)).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
    
        SuddenRaid.onAfter(SuddenRaidDOT)
        FinalCut.onAfter(FinalCutBuff)
        
        HiddenBladeOpt = core.OptionalElement(HiddenBladeBuff.is_active, HiddenBlade)
        
        FlashBang.onAfter(FlashBangDebuff)
        for sk in [FinalCut, PhantomBlow, SuddenRaid, FlashBang, AsuraTick, BladeStorm, BladeStormTick, BladeTornado, KarmaFury]:
            sk.onAfter(HiddenBladeOpt)
            
        for sk in [PhantomBlow, AsuraTick, BladeStormTick]:
            sk.onAfter(Venom)
        
        AsuraRepeat = core.RepeatElement(AsuraTick, 26)  # Up to 28 times are possible, but 26 times are set for dpm optimization. 최대 28회까지 가능하나, dpm 최적화를 위해 26회로 설정함.
        Asura.onAfter(AsuraRepeat)
        AsuraRepeat.onAfter(AsuraEnd)

        BladeStormRepeat = core.RepeatElement(BladeStormTick, 48)
        BladeStorm.onAfter(BladeStormRepeat)
        BladeStormRepeat.onAfter(BladeStormEnd)

        BladeTornado.onAfter(BladeTornadoSummon)
        BladeTornado.onAfter(BladeTornadoSummonMirrorImaging)

        SuddenRaid.onAfter(FinalCut.controller(0.2, "reduce_cooltime_p"))

        PhantomBlow.onAfter(core.OptionalElement(HauntedEdge.is_available, HauntedEdge, name=_("헌티드 엣지 쿨타임 체크")))
        HauntedEdge.protect_from_running()

        for sk in [PhantomBlow, SuddenRaid, FinalCut, FlashBang, AsuraTick, 
            BladeStorm, BladeStormTick, KarmaFury, BladeTornado, HiddenBlade, HauntedEdge]:
            jobutils.create_auxilary_attack(sk, 0.7, nametag=f"({DualBladeSkills.MirrorImage})")
        
        return(PhantomBlow,
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    Booster, DarkSight, FinalCutBuff, EpicAdventure, FlashBangDebuff, HiddenBladeBuff, globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                    UltimateDarksight, ReadyToDie, globalSkill.soul_contract()] +\
                [FinalCut, FlashBang, BladeTornado, SuddenRaid, KarmaFury, BladeStorm, Asura, MirrorBreak, MirrorSpider] +\
                [SuddenRaidDOT, Venom, BladeTornadoSummon, BladeTornadoSummonMirrorImaging, HauntedEdge] +\
                [] +\
                [PhantomBlow])