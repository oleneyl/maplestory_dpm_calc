from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ConditionRule, RuleSet, ReservationRule
from . import globalSkill, jobutils
from .jobbranch import thieves
from math import ceil
from typing import Any, Dict


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = (12, 12)
        self.vEnhanceNum = 14
        self.jobtype = "LUK"
        self.jobname = "팬텀"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=30)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        HighDexterity = core.InformedCharacterModifier("하이 덱스터리티", stat_sub=40)
        LuckMonopoly = core.InformedCharacterModifier("럭 모노폴리", stat_main=60)
        LuckOfPhantomtheif = core.InformedCharacterModifier("럭오브팬텀시프", stat_main=60)
        MoonLight = core.InformedCharacterModifier("문 라이트", att=40)
        AcuteSence = core.InformedCharacterModifier("어큐트 센스", crit=35, pdamage_indep=30)
        CainExpert = core.InformedCharacterModifier("케인 엑스퍼트", att=40+passive_level, crit_damage=15+passive_level//3, pdamage_indep=25 + passive_level//2)

        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 3, 3)

        return [HighDexterity, LuckMonopoly, LuckOfPhantomtheif, MoonLight, AcuteSence, CainExpert, ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=30)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=90+ceil(passive_level / 2))

        return [WeaponConstant, Mastery]

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ReservationRule("소울 컨트랙트", "마크 오브 팬텀"), RuleSet.BASE)

        # TODO: 쿨감 4초기준 최적화, 쿨감 수치를 받아와서 처리해야 함
        ruleset.add_rule(ConditionRule("템페스트 오브 카드(시전)", "블랙잭", lambda sk: sk.is_cooltime_left(8500, 1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule("템페스트 오브 카드(시전)", "마크 오브 팬텀", lambda sk: sk.is_cooltime_left(8500, 1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule("템페스트 오브 카드(시전)", "리프트 브레이크", lambda sk: sk.is_cooltime_left(8500, 1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule("템페스트 오브 카드(시전)", "조커(시전)", lambda sk: sk.is_cooltime_left(8500, 1)), RuleSet.BASE)
        return ruleset

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
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

        # 훔친 스킬은 공격력에 패널티가 있습니다.
        STEALSKILL = core.CharacterModifier(pdamage_indep=100*((1.2 / 1.3)-1))

        # 1차
        CardinalDischarge = core.DamageSkill("카디널 디스차지(탤팬1)", 210, 90, 4, modifier=STEALSKILL).setV(vEhc, 0, 7, True).wrap(core.DamageSkillWrapper)

        # 2차
        # 힐+마오팬보다 분노가 허수아비딜은 잘나옴
        Fury = core.BuffSkill("분노(탤팬2)", 0, 180000, rem=True, att=30).wrap(core.BuffSkillWrapper)
        CardinalBlast = core.DamageSkill("카디널 블래스트(탤팬2)", 240, 200, 4, modifier=STEALSKILL).setV(vEhc, 1, 5, False).wrap(core.DamageSkillWrapper)  # 210~270ms 랜덤 (1.2.338 기준 측정), 최종뎀 단리적용
        Heal = core.BuffSkill("힐(탤팬2)", 450, 2*1000, cooltime=10*1000, pdamage_indep=10).wrap(core.BuffSkillWrapper)

        # 3차
        CrossoverChain = core.BuffSkill("크로스 오버 체인(탤팬3)", 0, 180000, rem=True, pdamage_indep=20).wrap(core.BuffSkillWrapper)
        ArrowFlatter = core.SummonSkill("애로우 플래터(탤팬3)", 600, 210, 85, 1, 30 * 1000, modifier=STEALSKILL).setV(vEhc, 4, 3, False).wrap(core.SummonSkillWrapper)  # 딜레이 모름

        # 4차
        FinalCut = core.DamageSkill("파이널 컷(탤팬4)", 450, 2000 + 20 * self.combat, 1, modifier=STEALSKILL, cooltime=90000, red=True).setV(vEhc, 3, 2, True).wrap(core.DamageSkillWrapper)
        FinalCutBuff = core.BuffSkill("파이널 컷(탤팬4)(버프)", 0, 60000, cooltime=-1, rem=True, pdamage_indep=40 + self.combat).wrap(core.BuffSkillWrapper)

        # 하이퍼
        BoolsEye = core.BuffSkill("불스아이(탤팬H)", 960, 30 * 1000, cooltime=180 * 1000, crit=20, crit_damage=10, armor_ignore=20, pdamage=20).wrap(core.BuffSkillWrapper)
        Preparation = core.BuffSkill("프리퍼레이션(탤팬H)", 900, 30 * 1000, cooltime=120 * 1000, att=50, boss_pdamage=20).wrap(core.BuffSkillWrapper)

        ##### Phantom skills #####

        # Buff skills

        Booster = core.BuffSkill("부스터", 0, 240 * 1000, rem=True).wrap(core.BuffSkillWrapper)    #딜레이 모름

        MileAiguilles = core.DamageSkill("얼티밋 드라이브", 150, 140 + self.combat, 3, modifier=core.CharacterModifier(pdamage=20, armor_ignore=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        CarteNoir = core.DamageSkill("느와르 카르트", 0, 270, min(chtr.get_modifier().crit/100 + 0.1, 1)).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        Judgement = core.DamageSkill("느와르 카르트(저지먼트)", 0, 270, 10).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)

        PrieredAria = core.BuffSkill("프레이 오브 아리아", 0, (240+7*self.combat)*1000, pdamage=30+self.combat, armor_ignore=30+self.combat).wrap(core.BuffSkillWrapper)

        TempestOfCardInit = core.DamageSkill("템페스트 오브 카드(시전)", 0, 0, 0, cooltime=18000*0.8 + 180*56, red=True).wrap(core.DamageSkillWrapper)
        TempestOfCard = core.DamageSkill("템페스트 오브 카드", 180, 200+2*self.combat, 3, modifier=core.CharacterModifier(pdamage=20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        HerosOath = core.BuffSkill("히어로즈 오쓰", 0, 60000, cooltime=120000, pdamage=10).wrap(core.BuffSkillWrapper)

        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 3, 3)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # 트와일라이트 미적용 상태
        # Twilight = core.BuffSkill("트와일라이트", 150, 15000, cooltime=15000, armor_ignore=20 + self.combat//2).wrap(core.BuffSkillWrapper)
        # TwilightHit = core.DamageSkill("트와일라이트(공격)", 540, 450+3*self.combat, 3, cooltime=-1).wrap(core.DamageSkillWrapper)

        JokerInit = core.DamageSkill("조커(시전)", 540, 0, 0, cooltime=150000, red=True).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)
        JokerDamage = core.DamageSkill("조커", 460, 240+9*vEhc.getV(4, 4), 30).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)  # 14회 반복, 총 420타이므로 30타로 적용
        JokerBuff = core.BuffSkill("조커(버프)", 1230, 30000, cooltime=-1, pdamage_indep=(1 + (vEhc.getV(4, 4) - 1) // 5) * 2 / 5).isV(vEhc, 4, 4).wrap(core.BuffSkillWrapper)

        BlackJack = core.SummonSkill("블랙잭", 570, 250, 400+16*vEhc.getV(1, 1), 1, 5000-1, cooltime=15000, red=True).isV(vEhc, 1, 1).wrap(core.SummonSkillWrapper)
        BlackJackFinal = core.DamageSkill("블랙잭(최종)", 0, 600+24*vEhc.getV(1, 1), 12, cooltime=-1).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)

        MarkOfPhantom = core.DamageSkill("마크 오브 팬텀", 690, 300+12*vEhc.getV(2, 2), 6 * 7, cooltime=30000, red=True).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)
        MarkOfPhantomEnd = core.DamageSkill("마크 오브 팬텀(최종)", 0, 485+19*vEhc.getV(2, 2), 15).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)  # 2회 반복

        LiftBreak = core.DamageSkill("리프트 브레이크", 750, 400+16*vEhc.getV(0, 0), 7*7, cooltime=30000, red=True).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        #### 그래프 빌드

        FinalCut.onAfter(CarteNoir)
        FinalCut.onAfter(FinalCutBuff)

        CardStack = core.StackSkillWrapper(core.BuffSkill("카드 스택", 0, 99999999), 40, name="느와르 카르트 스택")

        AddCard = CardStack.stackController(1, name="스택 1 증가")
        Judgement.onAfter(CardStack.stackController(-9999, name="스택 초기화"))

        FullStack = core.OptionalElement(partial(CardStack.judge, 40, 1), Judgement, name="풀스택시")

        CarteNoir.onAfter(AddCard)
        CarteNoir.onAfter(FullStack)
        MileAiguilles.onAfter(CarteNoir)

        TempestOfCardInit.onAfter(core.RepeatElement(TempestOfCard, 45))  # 최대 56, 쿨감 4초 기준 딜사이클 최적화를 위해 45로 변경
        TempestOfCard.onAfter(CarteNoir)

        JokerDamage.onAfter(core.RepeatElement(CarteNoir, 10))  # 조커는 느와르를 발동하나, 조커 3타에 1번씩만 들어가므로 30 / 3 = 10

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
            Inturrupt = core.DamageSkill("얼드 후딜", 120, 0, 0).wrap(core.DamageSkillWrapper)
            for sk in interrupting_skills:
                sk.onBefore(Inturrupt)
        elif DEALCYCLE == "blast_discharge":
            BasicAttack = CardinalBlast
            Talent2 = None
            Inturrupt = core.DamageSkill("연계 취소 딜레이", 360-210, 0, 0).wrap(core.DamageSkillWrapper)
            for sk in interrupting_skills:
                sk.onBefore(Inturrupt)  # 블디 연계 취소 딜레이. TODO: 연계 취소 딜레이를 시뮬레이터에 구현
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
