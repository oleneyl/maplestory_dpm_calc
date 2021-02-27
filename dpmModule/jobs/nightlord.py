from .globalSkill import GlobalSkills
from .jobbranch.thieves import ThiefSkills
from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ComplexConditionRule, ConditionRule, RuleSet, ConcurrentRunRule, InactiveRule
from . import globalSkill
from .jobbranch import thieves
from . import jobutils
from math import ceil
from typing import Any, Dict

import gettext
_ = gettext.gettext

# English skill information for Night Lord here https://maplestory.fandom.com/wiki/Night_Lord/Skills
class NightLordSkills:
    # Link Skill
    ThiefsCunning = _("시프 커닝")  # "Thief's Cunning"
    # 1st Job
    DoubleStab = _("더블 스탭")  # "Double Stab"
    LuckySeven = _("럭키 세븐")  # "Lucky Seven"
    Haste = _("헤이스트")  # "Haste"
    DarkSight = _("다크 사이트")  # "Dark Sight"
    FlashJump = _("플래시 점프")  # "Flash Jump"
    NimbleBody = _("님블 바디")  # "Nimble Body"
    # 2nd Job
    ShurikenBurst = _("슈리켄 버스트")  # "Shuriken Burst"
    AssassinsMark = _("마크 오브 어쌔신")  # "Assassin's Mark"
    GustCharm = _("윈드 탈리스만")  # "Gust Charm"
    ClawBooster = _("자벨린 부스터")  # "Claw Booster"
    ClawMastery = _("자벨린 마스터리")  # "Claw Mastery"
    CriticalThrow = _("크리티컬 스로우")  # "Critical Throw"
    PhysicalTraining = _("피지컬 트레이닝")  # "Physical Training"
    # 3rd Job
    TripleThrow = _("트리플 스로우")  # "Triple Throw"
    ShadeSplitter = _("쉐이드 스플릿")  # "Shade Splitter"
    DarkFlare = _("다크 플레어")  # "Dark Flare"
    ShadowWeb = _("쉐도우 웹")  # "Shadow Web"
    ShadowPartner = _("쉐도우 파트너")  # "Shadow Partner"
    ShadowStars = _("스피릿 자벨린")  # "Shadow Stars"
    EnvelopingDarkness = _("래디컬 다크니스")  # "Enveloping Darkness"
    Venom = _("베놈")  # "Venom"
    ExpertThrowingStarHandling = _("숙련된 표창술")  # "Expert Throwing Star Handling"
    AlchemicAdrenaline = _("아드레날린")  # "Alchemic Adrenaline"
    # 4th Job
    QuadStar = _("쿼드러플 스로우")  # "Quad Star"
    Showdown = _("쇼다운 챌린지")  # "Showdown"
    NightLordsMark = _("마크 오브 나이트로드")  # "Night Lord's Mark"
    SuddenRaid = _("써든레이드")  # "Sudden Raid"
    FrailtyCurse = _("퍼지 에어리어")  # "Frailty Curse"
    DarkHarmony = _("다크 세레니티")  # "Dark Harmony"
    ShadowShifter = _("페이크")  # "Shadow Shifter"
    ToxicVenom = _("페이탈 베놈")  # "Toxic Venom"
    ClawExpert = _("자벨린 엑스퍼트")  # "Claw Expert"
    # Hypers
    DeathStar = _("포 시즌")  # "Death Star"
    EpicAdventure = _("에픽 어드벤처")  # "Epic Adventure"
    BleedDart = _("블리딩 톡신")  # "Bleed Dart"
    # 5th Job
    ThrowingStarBarrage = _("스프레드 스로우")  # "Throwing Star Barrage"
    Shurrikane = _("풍마수리검")  # "Shurrikane"
    DarkLordsOmen = _("다크로드의 비전서")  # "Dark Lord's Omen"
    ThrowBlasting = _("스로우 블래스팅")  # "Throw Blasting"


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 11
        self.jobtype = "LUK"
        self.jobname = _("나이트로드")
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        def use_uds(uds, spread, blasting):
            if spread.is_active():
                return spread.is_time_left(10000, 1)
            elif blasting.is_active() and blasting.is_time_left(50000, 1):
                return spread.is_cooltime_left(50000, 1)
            else:
                return False
        
        ruleset = RuleSet()
        ruleset.add_rule(ComplexConditionRule(ThiefSkills.ShadowWalker, [NightLordSkills.ThrowingStarBarrage, _("{}(액티브)").format(NightLordSkills.ThrowBlasting)], use_uds), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(GlobalSkills.MapleWorldGoddessBlessing, NightLordSkills.ThrowingStarBarrage, lambda sk: sk.is_active() or sk.is_usable()), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(GlobalSkills.TermsAndConditions, _("{}(액티브)").format(NightLordSkills.ThrowBlasting)), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(ThiefSkills.LastResort, GlobalSkills.TermsAndConditions), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(NightLordSkills.SuddenRaid, NightLordSkills.ThrowingStarBarrage), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(NightLordSkills.DarkFlare, NightLordSkills.ThrowingStarBarrage), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=45)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        NimbleBody = core.InformedCharacterModifier(NightLordSkills.NimbleBody,stat_main = 20)
        CriticalThrow = core.InformedCharacterModifier(NightLordSkills.CriticalThrow, crit=50, crit_damage = 5)
        PhisicalTraining = core.InformedCharacterModifier(NightLordSkills.PhysicalTraining,stat_main = 30, stat_sub = 30)
        
        Adrenalin = core.InformedCharacterModifier(NightLordSkills.AlchemicAdrenaline,crit_damage=10)
        JavelinMastery = core.InformedCharacterModifier(NightLordSkills.ClawMastery,pdamage_indep = 25)    #20%확률로 100%크리. 현재 비활성,
        PurgeAreaPassive = core.InformedCharacterModifier(_("{}(패시브)").format(NightLordSkills.FrailtyCurse),boss_pdamage = 10 + ceil(self.combat / 3))
        DarkSerenity = core.InformedCharacterModifier(NightLordSkills.DarkHarmony,att = 40+passive_level, armor_ignore = 30+passive_level)
        
        JavelineExpert = core.InformedCharacterModifier(NightLordSkills.ClawExpert,att = 30 + passive_level, crit_damage = 15 + passive_level//3)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 1, 1)
        
        return [NimbleBody, CriticalThrow, PhisicalTraining, 
                Adrenalin, JavelinMastery, PurgeAreaPassive, DarkSerenity, JavelineExpert, ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep = 75)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=85+ceil(passive_level / 2))
        
        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Quad-mark-showdown

        Hit 3 lines of soup

        Use only while using the soup
        Retouda is used once every 2 times to match the soup

        쿼드-마크-쇼다운
        
        스프 3줄 히트
        
        얼닼사는 스프 사용중에만 사용
        레투다를 2번에 한번씩 스프에 맞춰 사용
        '''
        SPREAD_HIT = 3 - options.get("spread_loss", 0)
        JAVELIN_ATT = core.CharacterModifier(att=29)  # 플레임 표창

        passive_level = chtr.get_base_modifier().passive_level + self.combat
        #Buff skills
        ShadowPartner = core.BuffSkill(NightLordSkills.ShadowPartner, 0, 200 * 1000, rem = True).wrap(core.BuffSkillWrapper) # 펫버프
        SpiritJavelin = core.BuffSkill(NightLordSkills.ShadowStars, 0, 200 * 1000, rem = True).wrap(core.BuffSkillWrapper) # 펫버프
        PurgeArea = core.BuffSkill(NightLordSkills.FrailtyCurse, 600, (40+self.combat) * 1000, armor_ignore=30+self.combat).wrap(core.BuffSkillWrapper)
        BleedingToxin = core.BuffSkill(NightLordSkills.BleedDart, 780, 80*1000, cooltime = 180 * 1000, att = 60).wrap(core.BuffSkillWrapper)
        BleedingToxinDot = core.DotSkill(_("{}(도트)").format(NightLordSkills.BleedDart), 0, 1000, 1000, 1, 90*1000, cooltime = -1).wrap(core.DotSkillWrapper)
        EpicAdventure = core.BuffSkill(NightLordSkills.EpicAdventure, 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        QuarupleThrow = core.DamageSkill(NightLordSkills.QuadStar, 600, 378 + 4 * self.combat, 5, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20) + JAVELIN_ATT).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)    #쉐도우 파트너 적용

        SuddenRaid = core.DamageSkill(NightLordSkills.SuddenRaid, 690, 494+5*self.combat, 7, cooltime = (30-2*(self.combat//2))*1000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        SuddenRaidDOT = core.DotSkill(_("{}(도트)").format(NightLordSkills.SuddenRaid), 0, 1000, 210 + 4 * self.combat, 1, 10000, cooltime = -1).wrap(core.DotSkillWrapper)

        DarkFlare = core.SummonSkill(NightLordSkills.DarkFlare, 600, 60000 / 62, 280, 1, 60000, cooltime=60000, red=True, rem=True).setV(vEhc, 1, 3, False).wrap(core.SummonSkillWrapper)
        
        MARK_PROP = (60+2*passive_level)/(160+2*passive_level)
        MarkOfNightlord = core.DamageSkill(NightLordSkills.NightLordsMark, 0, (60+3*passive_level+chtr.level), MARK_PROP*3, modifier=JAVELIN_ATT).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        MarkOfNightlordPungma = core.DamageSkill(_("{}(풍마)").format(NightLordSkills.NightLordsMark), 0, (60+3*passive_level+chtr.level), MARK_PROP*3, modifier=JAVELIN_ATT).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper) # 툴팁대로면 19.355%가 맞으나, 쿼드러플과 동일한 37.5%로 적용되는 중

        FatalVenom = core.DotSkill(NightLordSkills.ToxicVenom, 0, 1000, 160+5*passive_level, 2+(10+passive_level)//6, 8000, cooltime = -1).wrap(core.DotSkillWrapper)
    
        #_VenomBurst = core.DamageSkill("베놈 버스트", ??) ## 160+6*vlevel dot for 10 seconds with 50% probability of passive. When used, damage to all Dot Dem + (500+20*vlevel) * 5. Since it is a skill I don't use anyway, write X. 패시브 50%확률로 10초간 160+6*vlevel dot. 사용시 도트뎀 모두 피해 + (500+20*vlevel) * 5. 어차피 안쓰는 스킬이므로 작성X
        
        UltimateDarksight = thieves.UltimateDarkSightWrapper(vEhc, 3, 3)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 1, 1)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        # Set as conditional final attack. 조건부 파이널어택으로 설정함.
        SpreadThrowTick = core.DamageSkill(_("{}(스프레드)").format(NightLordSkills.QuadStar), 0, (378 + 4 * self.combat)*0.85, 5*SPREAD_HIT, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20) + JAVELIN_ATT).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        SpreadThrowInit = core.BuffSkill(NightLordSkills.ThrowingStarBarrage, 540, (20+vEhc.getV(0,0))*1000, cooltime = 180*1000, red=True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        
        Pungma = core.SummonSkill(NightLordSkills.Shurrikane, 360, 100, 0, 1, 1450, cooltime = 25*1000, red=True).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)  #10타 가정
        PungmaHit = core.DamageSkill(_("{}(타격)").format(NightLordSkills.Shurrikane), 0, 250+vEhc.getV(4,4)*10, 5, cooltime = -1, modifier=JAVELIN_ATT).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
        
        ArcaneOfDarklord = core.SummonSkill(NightLordSkills.DarkLordsOmen, 360, 1020, 350+14*vEhc.getV(2,2), 7 + 5, 11990, cooltime = 60*1000, red=True, modifier=core.CharacterModifier(boss_pdamage=30) + JAVELIN_ATT).isV(vEhc,2,2).wrap(core.SummonSkillWrapper) # 132타
        ArcaneOfDarklordFinal = core.DamageSkill(_("{}(막타)").format(NightLordSkills.DarkLordsOmen), 0, 900+36*vEhc.getV(2,2), 10, cooltime = -1, modifier=core.CharacterModifier(boss_pdamage=30) + JAVELIN_ATT).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        ThrowBlasting = core.DamageSkill(_("{}(폭발 부적)").format(NightLordSkills.ThrowBlasting), 0, 475+19*vEhc.getV(0,0), 5, cooltime=-1, modifier=JAVELIN_ATT).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ThrowBlastingStack = core.StackSkillWrapper(core.BuffSkill(_("{}(부적 스택)").format(NightLordSkills.ThrowBlasting), 0, 99999999), 45)
        ThrowBlastingActive = core.BuffSkill(_("{}(액티브)").format(NightLordSkills.ThrowBlasting), 720, 60000, cooltime=120*1000, red=True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        ThrowBlastingPassive = core.DamageSkill(_("{}(패시브)").format(NightLordSkills.ThrowBlasting), 0, 0, 0, cooltime=10000).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)

        ######   Skill Wrapper   ######

        # Sudden Raid. 써든레이드.
        SuddenRaid.onAfter(SuddenRaidDOT)

        # ?? Repair Sword. 풍마수리검.
        Pungma.onTick(PungmaHit)

        # Shadow Partner. 쉐도우 파트너.
        for sk in [QuarupleThrow, SuddenRaid, ThrowBlasting, PungmaHit]:
            jobutils.create_auxilary_attack(sk, 0.7, nametag=f"({NightLordSkills.ShadowPartner})")

        # Dark Lord's Scroll. 마크 오브 나이트로드.
        SpreadThrowTick.onAfter(core.RepeatElement(MarkOfNightlord, 5*SPREAD_HIT))
        Pungma.onTick(MarkOfNightlordPungma)
        ThrowBlasting.onAfter(MarkOfNightlord)
        
        # 다크로드의 비전서.
        ArcaneOfDarklord.onEventEnd(ArcaneOfDarklordFinal)
        
        # Bleeding toxin. 블리딩 톡신.
        BleedingToxin.onAfter(BleedingToxinDot)

        # Throw blasting. 스로우 블래스팅.
        ThrowBlastingActive.onAfter(ThrowBlastingStack.stackController(45))
        ThrowBlasting.onAfter(ThrowBlastingStack.stackController(-1))
        ThrowBlastingPassive.onAfter(ThrowBlasting)
        ThrowBlastingPassive.protect_from_running()
        
        # Quadruple related-spread, throw blasting. 쿼드러플 관련 - 스프레드, 스로우 블래스팅.
        QuarupleThrow.onAfter(core.OptionalElement(SpreadThrowInit.is_active, SpreadThrowTick))
        QuarupleThrow.onAfter(core.OptionalElement(lambda: ThrowBlastingStack.judge(0, -1) and ThrowBlastingPassive.is_available(), ThrowBlastingPassive))
        QuarupleThrow.onAfter(core.OptionalElement(
            lambda: ThrowBlastingStack.judge(1, 1),
            core.RepeatElement(ThrowBlasting, 3)
        ))
        QuarupleThrow.onAfter(MarkOfNightlord)

        for sk in [QuarupleThrow, SuddenRaid, Pungma, SpreadThrowTick]:
            sk.onAfter(FatalVenom)
        
        return (QuarupleThrow, 
            [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    ShadowPartner, SpiritJavelin, PurgeArea, DarkFlare, BleedingToxin, EpicAdventure, 
                    globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), UltimateDarksight, ReadyToDie, SpreadThrowInit,
                    ThrowBlasting, ThrowBlastingPassive, ThrowBlastingActive,
                    globalSkill.soul_contract()] + \
                [ArcaneOfDarklordFinal] + \
                [SuddenRaid, SuddenRaidDOT, Pungma, PungmaHit, ArcaneOfDarklord, MirrorBreak, MirrorSpider, BleedingToxinDot, FatalVenom] +\
                [] + \
                [QuarupleThrow])