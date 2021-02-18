from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import ComplexConditionRule, ReservationRule, RuleSet, ConcurrentRunRule, InactiveRule
from . import globalSkill
from .jobbranch import thieves
from . import jobutils
from math import ceil
from typing import Any, Dict


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 11
        self.jobtype = "LUK"
        self.jobname = "나이트로드"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        def ready_to_die_rule(rtd, uds, soul_contract):
            if uds.is_active():
                return True
            if uds.is_cooltime_left(80000, -1):
                return False
            if soul_contract.is_usable():
                return True
            return False

        ruleset = RuleSet()
        ruleset.add_rule(ReservationRule('에픽 어드벤처', '얼티밋 다크 사이트'), RuleSet.BASE)
        ruleset.add_rule(ReservationRule('메이플월드 여신의 축복', '얼티밋 다크 사이트'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('스로우 블래스팅(액티브)', '얼티밋 다크 사이트'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('스프레드 스로우', '스로우 블래스팅(액티브)'), RuleSet.BASE)
        ruleset.add_rule(ComplexConditionRule('레디 투 다이', ['얼티밋 다크 사이트', '소울 컨트랙트'], ready_to_die_rule), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('소울 컨트랙트', '레디 투 다이'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('써든레이드', '스프레드 스로우'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('다크 플레어', '스프레드 스로우'), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=45)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        NimbleBody = core.InformedCharacterModifier("님블 바디", stat_main=20)
        CriticalThrow = core.InformedCharacterModifier("크리티컬 스로우", crit=50, crit_damage=5)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝", stat_main=30, stat_sub=30)

        Adrenalin = core.InformedCharacterModifier("아드레날린", crit_damage=10)
        JavelinMastery = core.InformedCharacterModifier("자벨린 마스터리", pdamage_indep=25)  # 20%확률로 100%크리. 현재 비활성
        PurgeAreaPassive = core.InformedCharacterModifier("퍼지 에어리어(패시브)", boss_pdamage=10 + ceil(self.combat / 3))
        DarkSerenity = core.InformedCharacterModifier("다크 세레니티", att=40+passive_level, armor_ignore=30+passive_level)

        JavelineExpert = core.InformedCharacterModifier("자벨린 엑스퍼트", att=30 + passive_level, crit_damage=15 + passive_level//3)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 1, 1)

        return [NimbleBody, CriticalThrow, PhisicalTraining,
                Adrenalin, JavelinMastery, PurgeAreaPassive, DarkSerenity, JavelineExpert, ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=75)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=85+ceil(passive_level / 2))

        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        쿼드-마크-쇼다운

        스프 3줄 히트

        얼닼사에 모든 버프를 맞춰 사용
        레디 투 다이, 소울 컨트랙트는 얼닼사 쿨타임 절반마다 함께 사용
        '''
        SPREAD_HIT = 3 - options.get("spread_loss", 0)
        JAVELIN_ATT = core.CharacterModifier(att=29)  # 플레임 표창

        passive_level = chtr.get_base_modifier().passive_level + self.combat
        # Buff skills
        ShadowPartner = core.BuffSkill("쉐도우 파트너", 0, 200 * 1000, rem=True).wrap(core.BuffSkillWrapper)  # 펫버프
        SpiritJavelin = core.BuffSkill("스피릿 자벨린", 0, 200 * 1000, rem=True).wrap(core.BuffSkillWrapper)  # 펫버프
        PurgeArea = core.BuffSkill("퍼지 에어리어", 600, (40+self.combat) * 1000, armor_ignore=30+self.combat).wrap(core.BuffSkillWrapper)
        BleedingToxin = core.BuffSkill("블리딩 톡신", 780, 80*1000, cooltime=180 * 1000, att=60).wrap(core.BuffSkillWrapper)
        BleedingToxinDot = core.DotSkill("블리딩 톡신(도트)", 0, 1000, 1000, 1, 90*1000, cooltime=-1).wrap(core.DotSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime=120 * 1000, pdamage=10).wrap(core.BuffSkillWrapper)

        QuarupleThrow = core.DamageSkill("쿼드러플 스로우", 600, 378 + 4 * self.combat, 5, modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20) + JAVELIN_ATT).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)  # 쉐도우 파트너 적용

        SuddenRaid = core.DamageSkill("써든레이드", 690, 494+5*self.combat, 7, cooltime=(30-2*(self.combat//2))*1000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        SuddenRaidDOT = core.DotSkill("써든레이드(도트)", 0, 1000, 210 + 4 * self.combat, 1, 10000, cooltime=-1).wrap(core.DotSkillWrapper)

        DarkFlare = core.SummonSkill("다크 플레어", 600, 60000 / 62, 280, 1, 60000, cooltime=60000, red=True, rem=True).setV(vEhc, 1, 3, False).wrap(core.SummonSkillWrapper)

        MARK_PROP = (60+2*passive_level)/(160+2*passive_level)
        MarkOfNightlord = core.DamageSkill("마크 오브 나이트로드", 0, (60+3*passive_level+chtr.level), MARK_PROP*3, modifier=JAVELIN_ATT).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        MarkOfNightlordPungma = core.DamageSkill("마크 오브 나이트로드(풍마)", 0, (60+3*passive_level+chtr.level), MARK_PROP*3, modifier=JAVELIN_ATT).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)  # 툴팁대로면 19.355%가 맞으나, 쿼드러플과 동일한 37.5%로 적용되는 중

        FatalVenom = core.DotSkill("페이탈 베놈", 0, 1000, 160+5*passive_level, 2+(10+passive_level)//6, 8000, cooltime=-1).wrap(core.DotSkillWrapper)

        # _VenomBurst = core.DamageSkill("베놈 버스트", ??) ## 패시브 50%확률로 10초간 160+6*vlevel dot. 사용시 도트뎀 모두 피해 + (500+20*vlevel) * 5. 어차피 안쓰는 스킬이므로 작성X

        UltimateDarksight = thieves.UltimateDarkSightWrapper(vEhc, 3, 3)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 1, 1)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # 조건부 파이널어택으로 설정함.
        SpreadThrowTick = core.DamageSkill("쿼드러플 스로우(스프레드)", 0, (378 + 4 * self.combat)*0.85, 5*SPREAD_HIT, modifier=core.CharacterModifier(boss_pdamage=20, pdamage=20) + JAVELIN_ATT).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        SpreadThrowInit = core.BuffSkill("스프레드 스로우", 540, (20+vEhc.getV(0, 0))*1000, cooltime=180*1000, red=True).isV(vEhc, 0, 0).wrap(core.BuffSkillWrapper)

        Pungma = core.SummonSkill("풍마수리검", 360, 100, 0, 1, 1450, cooltime=25*1000, red=True).isV(vEhc, 4, 4).wrap(core.SummonSkillWrapper)  # 10타 가정
        PungmaHit = core.DamageSkill("풍마수리검(타격)", 0, 250+vEhc.getV(4, 4)*10, 5, cooltime=-1, modifier=JAVELIN_ATT).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)

        ArcaneOfDarklord = core.SummonSkill("다크로드의 비전서", 360, 1020, 350+14*vEhc.getV(2, 2), 7 + 5, 11990, cooltime=60*1000, red=True, modifier=core.CharacterModifier(boss_pdamage=30) + JAVELIN_ATT).isV(vEhc, 2, 2).wrap(core.SummonSkillWrapper)  # 132타
        ArcaneOfDarklordFinal = core.DamageSkill("다크로드의 비전서(막타)", 0, 900+36*vEhc.getV(2, 2), 10, cooltime=-1, modifier=core.CharacterModifier(boss_pdamage=30) + JAVELIN_ATT).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)
        ThrowBlasting = core.DamageSkill("스로우 블래스팅(폭발 부적)", 0, 475+19*vEhc.getV(0, 0), 5, cooltime=-1, modifier=JAVELIN_ATT).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        ThrowBlastingStack = core.StackSkillWrapper(core.BuffSkill("스로우 블래스팅(부적 스택)", 0, 99999999), 68)
        ThrowBlastingActive = core.BuffSkill("스로우 블래스팅(액티브)", 720, 60000, cooltime=180*1000, red=True).isV(vEhc, 0, 0).wrap(core.BuffSkillWrapper)
        ThrowBlastingPassive = core.DamageSkill("스로우 블래스팅(패시브)", 0, 0, 0, cooltime=10000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        ######   Skill Wrapper   ######

        # 써든레이드
        SuddenRaid.onAfter(SuddenRaidDOT)

        # 풍마수리검
        Pungma.onTick(PungmaHit)

        # 쉐도우 파트너
        for sk in [QuarupleThrow, SuddenRaid, ThrowBlasting, PungmaHit]:
            jobutils.create_auxilary_attack(sk, 0.7, nametag='(쉐도우파트너)')

        # 마크 오브 나이트로드
        SpreadThrowTick.onAfter(core.RepeatElement(MarkOfNightlord, 5*SPREAD_HIT))
        Pungma.onTick(MarkOfNightlordPungma)
        ThrowBlasting.onAfter(MarkOfNightlord)

        # 다크로드의 비전서
        ArcaneOfDarklord.onEventEnd(ArcaneOfDarklordFinal)

        # 블리딩 톡신
        BleedingToxin.onAfter(BleedingToxinDot)

        # 스로우 블래스팅
        ThrowBlastingActive.onAfter(ThrowBlastingStack.stackController(68))
        ThrowBlasting.onAfter(ThrowBlastingStack.stackController(-1))
        ThrowBlastingPassive.onAfter(ThrowBlasting)
        ThrowBlastingPassive.protect_from_running()

        # 쿼드러플 관련 - 스프레드, 스로우 블래스팅
        QuarupleThrow.onAfter(core.OptionalElement(SpreadThrowInit.is_active, SpreadThrowTick))
        QuarupleThrow.onAfter(core.OptionalElement(lambda: ThrowBlastingStack.judge(0, -1) and ThrowBlastingPassive.is_available(), ThrowBlastingPassive))
        QuarupleThrow.onAfter(core.OptionalElement(
            lambda: ThrowBlastingStack.judge(1, 1),
            core.RepeatElement(ThrowBlasting, 3)
        ))
        QuarupleThrow.onAfter(MarkOfNightlord)

        for sk in [QuarupleThrow, SuddenRaid, Pungma, SpreadThrowTick]:
            sk.onAfter(FatalVenom)

        return (
            QuarupleThrow,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                ShadowPartner, SpiritJavelin, PurgeArea, DarkFlare, BleedingToxin, EpicAdventure,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), UltimateDarksight, ReadyToDie, SpreadThrowInit,
                ThrowBlasting, ThrowBlastingPassive, ThrowBlastingActive,
                globalSkill.soul_contract()
            ]
            + [ArcaneOfDarklordFinal]
            + [SuddenRaid, SuddenRaidDOT, Pungma, PungmaHit, ArcaneOfDarklord, MirrorBreak, MirrorSpider, BleedingToxinDot, FatalVenom]
            + [QuarupleThrow]
        )
