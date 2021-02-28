from .hero import HeroSkills
from .pathfinder import PathfinderSkills
from .bishop import BishopSkills
from .dualblade import DualBladeSkills
from .darknight import DarkKnightSkills
from .bowmaster import BowmasterSkills
from .marksman import MarksmanSkills

from .globalSkill import GlobalSkills
from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ConditionRule, RuleSet, ReservationRule
from . import globalSkill, jobutils
from .jobbranch import thieves
from math import ceil
from typing import Any, Dict

import gettext
_ = gettext.gettext

# English skill information for Phantom here https://maplestory.fandom.com/wiki/Phantom/Skills
class PhantomSkills:
    # Link Skill
    PhantomInstinct = _("데들리 인스팅트")  # "Phantom Instinct"
    # Beginner
    ShroudWalk = _("팬텀 슈라우드")  # "Shroud Walk"
    DexterousTraining = _("하이 덱스터리티")  # "Dexterous Training"
    SkillSwipe = _("스틸 스킬")  # "Skill Swipe"
    Loadout = _("스킬 매니지먼트")  # "Loadout"
    JudgmentDraw = _("저지먼트")  # "Judgment Draw"
    Ghostwalk = _("스니킹 무브먼트")  # "Ghostwalk"
    # 1st Job
    DoubleEntendre = _("더블 피어싱")  # "Double Entendre"
    ImpeccableMemoryI = _("탤런트 오브 팬텀시프 Ⅰ")  # "Impeccable Memory I"
    PhantomSwiftness = _("스위프트 팬텀")  # "Phantom Swiftness"
    FeatherFoot = _("퀵 이베이젼")  # "Feather Foot"
    # 2nd Job
    CallingCard = _("콜 오브 페이트")  # "Calling Card"
    ImpeccableMemoryII = _("탤런트 오브 팬텀시프 II")  # "Impeccable Memory II"
    MilleCartes = _("브리즈 카르트")  # "Mille Cartes"
    CarteBlanche = _("블랑 카르트")  # "Carte Blanche"
    CaneMastery = _("케인 마스터리")  # "Cane Mastery"
    CaneBooster = _("케인 부스터")  # "Cane Booster"
    DevilsLuck = _("럭 모노폴리")  # "Devil's Luck"
    # 3rd Job
    Blason = _("코트 오브 암즈")  # "Blason"
    ImpeccableMemoryIII = _("탤런트 오브 팬텀시프 Ⅲ")  # "Impeccable Memory III"
    FinalFeint = _("럭오브팬텀시프")  # "Final Feint"
    BadLuckWard = _("미스포츈 프로텍션")  # "Bad Luck Ward"
    MistMask = _("플래시 앤 플리")  # "Mist Mask"
    Lune = _("문 라이트")  # "Lune"
    RapierWit = _("팬텀 차지")  # "Rapier Wit"
    PiercingVision = _("어큐트 센스")  # "Piercing Vision"
    # 4th Job
    MilleAiguilles = _("얼티밋 드라이브")  # "Mille Aiguilles"
    ImpeccableMemoryIV = _("탤런트 오브 팬텀시프 Ⅳ")  # "Impeccable Memory IV"
    CarteNoir = _("느와르 카르트")  # "Carte Noir"
    Penombre = _("트와일라이트")  # "Penombre"
    PriereDAria = _("프레이 오브 아리아")  # "Priere D'Aria"
    Tempest = _("템페스트 오브 카드")  # "Tempest"
    CaneExpert = _("케인 엑스퍼트")  # "Cane Expert"
    VolDAme = _("소울 스틸")  # "Vol D'Ame"
    # Hypers
    CarteRoseFinale = _("로즈 카르트 피날레")  # "Carte Rose Finale"
    HeroicMemories = _("히어로즈 오쓰")  # "Heroic Memories"
    ImpeccableMemoryH = _("탤런트 오브 팬텀시프 H")  # "Impeccable Memory H"
    # 5th Job
    LuckoftheDraw = _("조커")  # "Luck of the Draw"
    AceintheHole = _("블랙잭")  # "Ace in the Hole"
    PhantomsMark = _("마크 오브 팬텀")  # "Phantom's Mark"
    RiftBreak = _("리프트 브레이크")  # "Rift Break"


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = (12, 12)
        self.vEnhanceNum = 14
        self.jobtype = "LUK"
        self.jobname = _("팬텀")
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=30)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        HighDexterity = core.InformedCharacterModifier(PhantomSkills.DexterousTraining, stat_sub=40)
        LuckMonopoly = core.InformedCharacterModifier(PhantomSkills.DevilsLuck, stat_main=60)
        LuckOfPhantomtheif = core.InformedCharacterModifier(PhantomSkills.FinalFeint, stat_main=60)
        MoonLight = core.InformedCharacterModifier(PhantomSkills.Lune, att=40)
        AcuteSence = core.InformedCharacterModifier(PhantomSkills.PiercingVision, crit=35, pdamage_indep=30)
        CainExpert = core.InformedCharacterModifier(PhantomSkills.CaneExpert, att=40+passive_level, crit_damage=15+passive_level//3, pdamage_indep=25 + passive_level//2)

        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 3, 3)

        return [HighDexterity, LuckMonopoly, LuckOfPhantomtheif, MoonLight, AcuteSence, CainExpert, ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep=30)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90+ceil(passive_level / 2))

        return [WeaponConstant, Mastery]

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ReservationRule(GlobalSkills.TermsAndConditions, PhantomSkills.PhantomsMark), RuleSet.BASE)

        # TODO: 쿨감 4초기준 최적화, 쿨감 수치를 받아와서 처리해야 함
        ruleset.add_rule(ConditionRule(_("{}(시전)").format(PhantomSkills.Tempest), PhantomSkills.AceintheHole, lambda sk: sk.is_cooltime_left(8500, 1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(_("{}(시전)").format(PhantomSkills.Tempest), PhantomSkills.PhantomsMark, lambda sk: sk.is_cooltime_left(8500, 1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(_("{}(시전)").format(PhantomSkills.Tempest), PhantomSkills.RiftBreak, lambda sk: sk.is_cooltime_left(8500, 1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(_("{}(시전)").format(PhantomSkills.Tempest), _("{}(시전)").format(PhantomSkills.LuckoftheDraw), lambda sk: sk.is_cooltime_left(8500, 1)), RuleSet.BASE)
        return ruleset

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Hyper:
        Tempoka-Reinforce / Cool Reduce
        Earld-Reinforce, Ignorguard

        100% Joker

        v Core: 14
        Tier 1: Ultimate, Noir, Temwa
        Tier 2: Talpan 4

        Pet Buff: Play of Aria, Meyong, Croce
        Tempest of Card not used

        하이퍼 :
        템오카 - 리인포스 / 쿨리듀스
        얼드 - 리인포스, 이그노어가드

        조커 100%

        v코어 : 14개
        1티어 :  얼티밋, 느와르, 템와
        2티어 : 탤팬4

        펫버프 : 프레이 오브 아리아, 메용, 크오체
        템페스트 오브 카드 사용하지 않음
        '''
        DEALCYCLE = options.get('dealcycle', 'ultimate_drive')

        ##### Steal skills #####

        # Stolen skills have a penalty in attack power. 훔친 스킬은 공격력에 패널티가 있습니다.
        STEALSKILL = core.CharacterModifier(pdamage_indep=100*((1.2 / 1.3)-1))

        # Primary. 1차.
        CardinalDischarge = core.DamageSkill(f"{PathfinderSkills.CardinalDeluge}({PhantomSkills.ImpeccableMemoryI})", 210, 90, 4, modifier=STEALSKILL).setV(vEhc, 0, 7, True).wrap(core.DamageSkillWrapper)

        # Secondary. 2차.
        # Rage is better than Hill + Mao Fan, and scarecrow deals are better. 힐+마오팬보다 분노가 허수아비딜은 잘나옴.
        Fury = core.BuffSkill(f"{HeroSkills.Rage}({PhantomSkills.ImpeccableMemoryII})", 0, 180000, rem=True, att=30).wrap(core.BuffSkillWrapper)
        CardinalBlast = core.DamageSkill(f"{PathfinderSkills.CardinalBurst}({PhantomSkills.ImpeccableMemoryII})", 240, 200, 4, modifier=STEALSKILL).setV(vEhc, 1, 5, False).wrap(core.DamageSkillWrapper)  # 210~270ms random (measured based on 1.2.338), final dem isolated applied. 210~270ms 랜덤 (1.2.338 기준 측정), 최종뎀 단리적용.
        Heal = core.BuffSkill(f"{BishopSkills.Heal}({PhantomSkills.ImpeccableMemoryII})", 450, 2*1000, cooltime=10*1000, pdamage_indep=10).wrap(core.BuffSkillWrapper)

        # 3rd. 3차.
        CrossoverChain = core.BuffSkill(f"{DarkKnightSkills.CrossSurge}({PhantomSkills.ImpeccableMemoryIII})", 0, 180000, rem=True, pdamage_indep=20).wrap(core.BuffSkillWrapper)
        ArrowFlatter = core.SummonSkill(f"{BowmasterSkills.ArrowBlaster}({PhantomSkills.ImpeccableMemoryIII})", 600, 210, 85, 1, 30 * 1000, modifier=STEALSKILL).setV(vEhc, 4, 3, False).wrap(core.SummonSkillWrapper)  # I don't know the delay. 딜레이 모름.

        # 4th. 4차.
        FinalCut = core.DamageSkill(f"{DualBladeSkills.FinalCut}({PhantomSkills.ImpeccableMemoryIV})", 450, 2000 + 20 * self.combat, 1, modifier=STEALSKILL, cooltime=90000, red=True).setV(vEhc, 3, 2, True).wrap(core.DamageSkillWrapper)
        FinalCutBuff = core.BuffSkill(_("{}({})(버프)").format(DualBladeSkills.FinalCut, PhantomSkills.ImpeccableMemoryIV), 0, 60000, cooltime=-1, rem=True, pdamage_indep=40 + self.combat).wrap(core.BuffSkillWrapper)

        # Hyper. 하이퍼.
        BoolsEye = core.BuffSkill(f"{MarksmanSkills.BullseyeShot}({PhantomSkills.ImpeccableMemoryH})", 960, 30 * 1000, cooltime=180 * 1000, crit=20, crit_damage=10, armor_ignore=20, pdamage=20).wrap(core.BuffSkillWrapper)
        Preparation = core.BuffSkill(f"{BowmasterSkills.Concentration}({PhantomSkills.ImpeccableMemoryH})", 540, 30 * 1000, cooltime=120 * 1000, att=50, boss_pdamage=20).wrap(core.BuffSkillWrapper)

        ##### Phantom skills #####

        # Buff skills

        Booster = core.BuffSkill(PhantomSkills.CaneBooster, 0, 240 * 1000, rem=True).wrap(core.BuffSkillWrapper)    # I don't know the delay. 딜레이 모름.

        MileAiguilles = core.DamageSkill(PhantomSkills.MilleAiguilles, 150, 140 + self.combat, 3, modifier=core.CharacterModifier(pdamage=20, armor_ignore=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        CarteNoir = core.DamageSkill(PhantomSkills.CarteNoir, 0, 270, min(chtr.get_modifier().crit/100 + 0.1, 1)).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        Judgement = core.DamageSkill(f"{PhantomSkills.CarteNoir}({PhantomSkills.JudgmentDraw})", 0, 270, 10).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)

        PrieredAria = core.BuffSkill(PhantomSkills.PriereDAria, 0, (240+7*self.combat)*1000, pdamage=30+self.combat, armor_ignore=30+self.combat).wrap(core.BuffSkillWrapper)

        TempestOfCardInit = core.DamageSkill(_("{}(시전)").format(PhantomSkills.Tempest), 0, 0, 0, cooltime=18000*0.8 + 180*56, red=True).wrap(core.DamageSkillWrapper)
        TempestOfCard = core.DamageSkill(PhantomSkills.Tempest, 180, 200+2*self.combat, 3, modifier=core.CharacterModifier(pdamage=20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        HerosOath = core.BuffSkill(PhantomSkills.HeroicMemories, 0, 60000, cooltime=120000, pdamage=10).wrap(core.BuffSkillWrapper)

        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 3, 3)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # Twilight not applied. 트와일라이트 미적용 상태.
        # Twilight = core.BuffSkill(PhantomSkills.Penombre, 150, 15000, cooltime=15000, armor_ignore=20 + self.combat//2).wrap(core.BuffSkillWrapper)
        # TwilightHit = core.DamageSkill(_("{}(공격)").format(PhantomSkills.Penombre), 540, 450+3*self.combat, 3, cooltime=-1).wrap(core.DamageSkillWrapper)

        JokerInit = core.DamageSkill(_("{}(시전)").format(PhantomSkills.LuckoftheDraw), 540, 0, 0, cooltime=150000, red=True).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)
        JokerDamage = core.DamageSkill(PhantomSkills.LuckoftheDraw, 460, 240+9*vEhc.getV(4, 4), 30).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)  # 14 repetitions, a total of 420 strokes, so 30 strokes applied. 14회 반복, 총 420타이므로 30타로 적용.
        JokerBuff = core.BuffSkill(_("{}(버프)").format(PhantomSkills.LuckoftheDraw), 1230, 30000, cooltime=-1, pdamage_indep=(1 + (vEhc.getV(4, 4) - 1) // 5) * 2 / 5).isV(vEhc, 4, 4).wrap(core.BuffSkillWrapper)

        BlackJack = core.SummonSkill(PhantomSkills.AceintheHole, 570, 250, 400+16*vEhc.getV(1, 1), 1, 5000-1, cooltime=15000, red=True).isV(vEhc, 1, 1).wrap(core.SummonSkillWrapper)
        BlackJackFinal = core.DamageSkill(_("{}(최종)").format(PhantomSkills.AceintheHole), 0, 600+24*vEhc.getV(1, 1), 12, cooltime=-1).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)

        MarkOfPhantom = core.DamageSkill(PhantomSkills.PhantomsMark, 690, 300+12*vEhc.getV(2, 2), 6 * 7, cooltime=30000, red=True).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)
        MarkOfPhantomEnd = core.DamageSkill(_("{}(최종)").format(PhantomSkills.PhantomsMark), 0, 485+19*vEhc.getV(2, 2), 15).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)  # Repeat 2 times. 2회 반복.

        LiftBreak = core.DamageSkill(PhantomSkills.RiftBreak, 750, 400+16*vEhc.getV(0, 0), 7*7, cooltime=30000, red=True).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        #### Build the graph. 그래프 빌드.

        FinalCut.onAfter(CarteNoir)
        FinalCut.onAfter(FinalCutBuff)

        CardStack = core.StackSkillWrapper(core.BuffSkill(_("카드 스택"), 0, 99999999), 40, name=_("{}(스택)").format(PhantomSkills.CarteNoir))

        AddCard = CardStack.stackController(1, name=_("스택 1 증가"))
        Judgement.onAfter(CardStack.stackController(-9999, name=_("스택 초기화")))

        FullStack = core.OptionalElement(partial(CardStack.judge, 40, 1), Judgement, name=_("풀스택시"))

        CarteNoir.onAfter(AddCard)
        CarteNoir.onAfter(FullStack)
        MileAiguilles.onAfter(CarteNoir)

        TempestOfCardInit.onAfter(core.RepeatElement(TempestOfCard, 45))  # Changed to 45 to optimize the damage cycle based on a maximum of 56 and a cool feeling of 4 seconds. 최대 56, 쿨감 4초 기준 딜사이클 최적화를 위해 45로 변경.
        TempestOfCard.onAfter(CarteNoir)

        JokerDamage.onAfter(core.RepeatElement(CarteNoir, 10))  # The Joker activates noir, but it only goes once per 3 Joker strokes, so 30/3 = 10. 조커는 느와르를 발동하나, 조커 3타에 1번씩만 들어가므로 30 / 3 = 10.

        JokerDamages = core.RepeatElement(JokerDamage, 14)
        JokerInit.onAfter(JokerDamages)
        JokerDamages.onAfter(JokerBuff)

        BlackJack.onTick(CarteNoir)
        BlackJack.onAfter(BlackJackFinal.controller(5000))
        BlackJackFinal.onAfter(CarteNoir)

        MarkOfPhantom.onAfter(core.RepeatElement(CarteNoir, 7))
        MarkOfPhantom.onAfter(core.RepeatElement(MarkOfPhantomEnd, 2))
        MarkOfPhantomEnd.onAfter(CarteNoir)

        LiftBreak.onAfter(core.RepeatElement(CarteNoir, 7))

        CardinalBlast.onAfter(CarteNoir)
        CardinalDischarge.onAfter(CarteNoir)

        CardinalBlast.onAfter(CardinalDischarge)

        '''
        얼드: MileAiguilles
        블디: CardinalBlast
        '''

        interrupting_skills = [FinalCut, JokerInit, BlackJack]

        if DEALCYCLE == "ultimate_drive":
            BasicAttack = MileAiguilles
            Talent2 = Fury
            Inturrupt = core.DamageSkill(_("얼드 후딜"), 120, 0, 0).wrap(core.DamageSkillWrapper)
            for sk in interrupting_skills:
                sk.onBefore(Inturrupt)
        elif DEALCYCLE == "blast_discharge":
            BasicAttack = CardinalBlast
            Talent2 = None
            Inturrupt = core.DamageSkill(_("연계 취소 딜레이"), 360-210, 0, 0).wrap(core.DamageSkillWrapper)
            for sk in interrupting_skills:
                sk.onBefore(Inturrupt)  # Bloody linkage cancellation delay. 블디 연계 취소 딜레이. TODO: Implement linkage cancellation delay in simulator. 연계 취소 딜레이를 시뮬레이터에 구현.
        else:
            raise ValueError(DEALCYCLE)

        return (
            BasicAttack,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                Talent2,
                CrossoverChain,
                Booster,
                PrieredAria,
                FinalCutBuff,
                JokerBuff,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                BoolsEye,
                HerosOath,
                ReadyToDie,
                globalSkill.soul_contract()
            ] +
            [BlackJackFinal] +  # reserved task, use as early as possible
            [FinalCut, BlackJack, MarkOfPhantom, LiftBreak, JokerInit] +
            [MirrorBreak, MirrorSpider, TempestOfCardInit] +
            [BasicAttack]
        )
