from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ConcurrentRunRule, ConditionRule, DisableRule, MutualRule, RuleSet
from . import globalSkill, jobutils
from .jobbranch import bowmen
from .jobclass import adventurer
from math import ceil
from typing import Any, Dict


class CardinalStateWrapper(core.BuffSkillWrapper):
    def __init__(self, ancient_force_skills):
        '''
        DISCHARGE / BLAST / TRANSITION / NONE
        '''
        skill = core.BuffSkill("카디널 차지", 0, 99999999)
        super(CardinalStateWrapper, self).__init__(skill)

        self.state = "DISCHARGE"
        self.ancient_force_skills = ancient_force_skills

    def is_state(self, state):
        if self.state == state:
            return True
        return False

    def _change_state(self, state):
        assert(state in ["DISCHARGE", "BLAST", "TRANSITION", "NONE"])
        if self.state != state and state != "NONE" and self.state != "NONE":
            for skill in self.ancient_force_skills:
                skill.reduce_cooltime(1000)
        self.state = state
        return self._result_object_cache

    def change_state(self, state):
        task = core.Task(self, partial(self._change_state, state))
        return core.TaskHolder(task, name="문양 변경")


class RelicChargeStack(core.StackSkillWrapper):
    def __init__(self, ancient_guidance_buff, chtr):
        skill = core.BuffSkill("렐릭 차지", 0, 99999999)
        super(RelicChargeStack, self).__init__(skill, 1000)
        self.set_name_style("%d")
        self.ancient_guidance_stack = 0
        self.ancient_guidance_buff = ancient_guidance_buff
        self.ancient_guidance_task = ancient_guidance_buff.build_task(chtr.get_skill_modifier())

    def vary(self, d):
        stack_before = self.stack
        res = super(RelicChargeStack, self).vary(d)
        self.ancient_guidance_stack += max(self.stack - stack_before, 0)
        if self.ancient_guidance_stack >= 1000:
            self.ancient_guidance_stack = 0
            res.cascade = [self.ancient_guidance_task]  # For stability
        return res


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "DEX"
        self.jobname = "패스파인더"
        self.vEnhanceNum = 11
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(DisableRule('에인션트 아스트라'), RuleSet.BASE)
        ruleset.add_rule(DisableRule('스플릿 미스텔'), RuleSet.BASE)
        ruleset.add_rule(DisableRule('콤보 어썰트'), RuleSet.BASE)
        ruleset.add_rule(MutualRule('이볼브', '레이븐 템페스트'), RuleSet.BASE)
        ruleset.add_rule(ConditionRule('카디널 트랜지션', '커스 트랜지션', lambda sk: sk.is_time_left(2000, -1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule('얼티밋 블래스트', '렐릭 차지', lambda sk: sk.judge(1000, 1)), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('소울 컨트랙트', '크리티컬 리인포스'), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=50, armor_ignore=15, crit_damage=20)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        CriticalShot = core.InformedCharacterModifier("크리티컬 샷", crit=40)
        AncientBowMastery = core.InformedCharacterModifier("에인션트 보우 마스터리", att=30)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝", stat_main=30, stat_sub=30)

        EssenceOfArcher = core.InformedCharacterModifier("에센스 오브 아처", crit=10, pdamage=10, armor_ignore=30)

        AdditionalTransitionPassive = core.InformedCharacterModifier("에디셔널 트랜지션(패시브)", patt=20 + passive_level)

        AncientBowExpert = core.InformedCharacterModifier("에인션트 보우 엑스퍼트", att=60+2*passive_level, crit_damage=10+ceil(passive_level/3))
        IllusionStep = core.InformedCharacterModifier("일루젼 스텝", stat_main=80+2*passive_level)
        return [CriticalShot, AncientBowMastery, PhisicalTraining, EssenceOfArcher,
                AdditionalTransitionPassive, AncientBowExpert, IllusionStep]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=30)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=85+ceil(passive_level/2))

        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        에인션트 아스트라 사용하지 않음
        카디널 트랜지션은 커스 트랜지션의 지속시간이 2초 이하 남았을때 사용
        블래 210ms 디차 240ms
        렐릭 언바운드 디스차지로 사용

        하이퍼

        에인션트 포스 - 보스 킬러, 이그노어 가드
        카디널 포스- 리인포스, 에디셔널 인핸스, 보너스 어택

        코강 순서
        카디 - 카블 - 에인션트아스트라 - 카트 - 임팩트 - 미스텔 - 어썰트 - 레조넌스 - 레이븐

        5차 순서
        레이븐템페 - 크리인 - 얼티밋 - 가이디드 - 옵시 - 이볼브

        미스텔 미사용(데미지 감소함)
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        ANCIENT_ARCHERY = core.CharacterModifier(pdamage_indep=10, boss_pdamage=50+20+passive_level, armor_ignore=20)
        LINK_DELAY = 30

        ######   Skill   ######
        # Buff skills
        AncientBowBooster = core.BuffSkill("에인션트 보우 부스터", 0, 300*1000, rem=True).wrap(core.BuffSkillWrapper)
        CurseTolerance = core.BuffSkill("커스 톨러런스", 0, 300*1000, rem=True).wrap(core.BuffSkillWrapper)
        SharpEyes = core.BuffSkill("샤프 아이즈", 0, (300+10*self.combat)*1000, crit=20+ceil(self.combat/2), crit_damage=15+ceil(self.combat/2), rem=True).wrap(core.BuffSkillWrapper)
        AncientGuidance = core.BuffSkill("에인션트 가이던스(버프)", 0, 30000, pdamage_indep=15, cooltime=-1, rem=False).wrap(core.BuffSkillWrapper)
        CurseTransition = core.BuffSkill("커스 트랜지션", 0, 15*1000, crit_damage=20, cooltime=-1).wrap(core.BuffSkillWrapper)  # 5스택 유지 가정

        # Summon skills
        Raven = core.SummonSkill("레이븐", 0, 1800, 390, 1, 220*1000).setV(vEhc, 8, 3, False).wrap(core.SummonSkillWrapper)  # 이볼브 종료시 자동 소환되므로 딜레이 0

        # Damage skills
        # 카디널 포스
        CardinalDischarge = core.DamageSkill("카디널 디스차지", 210, 300+5*passive_level, (4 + 1)*2, modifier=core.CharacterModifier(pdamage=20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        AdditionalDischarge = core.DamageSkill("에디셔널 디스차지", 0, 100 + 50 + passive_level, 3*3*(0.4+0.1)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        AdditionalDischargeEvolution = core.DamageSkill("에디셔널 디스차지(렐릭 에볼루션)", 0, 100 + 50 + passive_level, 3*(0.4+0.1)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)

        CardinalBlast = core.DamageSkill("카디널 블래스트", 240, 400+5*passive_level, 4 + 1, modifier=core.CharacterModifier(pdamage=20, pdamage_indep=50)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)  # 210~270ms 랜덤 (1.2.338 기준 측정), 최종뎀 단리적용
        AdditionalBlast = core.DamageSkill("에디셔널 블래스트", 0, 150 + 50 + passive_level, 2*3*(0.4+0.1)).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        AdditionalBlastEvolution = core.DamageSkill("에디셔널 블래스트(렐릭 에볼루션)", 0, 150 + 50 + passive_level, 3*(0.4+0.1)).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)

        CardinalTransition = core.DamageSkill("카디널 트랜지션", 210, 540+7*passive_level, 5).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        AdditionalTransition = core.BuffSkill("에디셔널 트랜지션", 0, 7000, cooltime=-1).wrap(core.BuffSkillWrapper)  # 전환시 카디널 디스/블래 사용시 40%확률로 고대 1중첩

        # 에인션트 포스
        SplitMistel = core.DamageSkill("스플릿 미스텔", LINK_DELAY + 540, 200+350+7*passive_level, 4, cooltime=10*1000, red=True, modifier=ANCIENT_ARCHERY).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        SplitMistelBonus = core.DamageSkill("스플릿 미스텔(보너스)", 0, 100+200+4*passive_level, 4 * 2, modifier=ANCIENT_ARCHERY).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)

        TripleImpactJump = core.DamageSkill("트리플 임팩트(점프)", LINK_DELAY + 420, 0, 0, cooltime=-1).wrap(core.DamageSkillWrapper)
        TripleImpact = core.DamageSkill("트리플 임팩트", 0, 400 + 200+5*passive_level, 5*3, cooltime=10*1000, red=True, modifier=ANCIENT_ARCHERY).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)

        # 5스택 가정, 다른 스킬 사용 중에 시전가능
        EdgeOfResonance = core.DamageSkill("엣지 오브 레조넌스", 0, 800+15*self.combat, 6, cooltime=15*1000, red=True, modifier=ANCIENT_ARCHERY + core.CharacterModifier(pdamage_indep=50)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)

        # 인챈트 포스
        ComboAssultHolder = core.DamageSkill("콤보 어썰트", 0, 0, 0, cooltime=20 * 1000, red=True).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)

        ComboAssultDischarge = core.DamageSkill("콤보 어썰트(디스차지)", LINK_DELAY + 600, 600+10*self.combat, 7, modifier=ANCIENT_ARCHERY).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)  # 디버프 +1
        ComboAssultDischargeArrow = core.DamageSkill("콤보 어썰트(디스차지)(화살)", 150, 650+10*self.combat, 5, modifier=ANCIENT_ARCHERY).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)

        ComboAssultBlast = core.DamageSkill("콤보 어썰트(블래스트)", LINK_DELAY + 600, 600+10*self.combat, 8, modifier=ANCIENT_ARCHERY).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)  # 디버프 +1
        ComboAssultBlastArrow = core.DamageSkill("콤보 어썰트(블래스트)(화살)", 150, 600+10*self.combat, 5, modifier=ANCIENT_ARCHERY).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)

        ComboAssultTransition = core.DamageSkill("콤보 어썰트(트랜지션)", LINK_DELAY + 600, 600+10*self.combat, 7, modifier=ANCIENT_ARCHERY).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)  # 디버프 +5
        ComboAssultTransitionArrow = core.DamageSkill("콤보 어썰트(트랜지션)(화살)", 150, 650+10*self.combat, 5, modifier=ANCIENT_ARCHERY).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)

        ## 하이퍼
        RelicEvolution = core.BuffSkill("렐릭 에볼루션", 0, 30*1000, cooltime=120*1000).wrap(core.BuffSkillWrapper)  # 딜레이 0으로 가정

        AncientAstraHolder = core.DamageSkill("에인션트 아스트라", LINK_DELAY + 420, 0, 0, cooltime=80*1000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        AncientAstraDischarge = core.DamageSkill("에인션트 아스트라(디스차지)", 270, 500, 6, modifier=ANCIENT_ARCHERY).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)  # 16.11초 60*6타
        AncientAstraDischargeArrow = core.DamageSkill("에인션트 아스트라(디스차지)(화살)", 0, 300, 0.3*2*2, modifier=ANCIENT_ARCHERY).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        AncientAstraBlast = core.DamageSkill("에인션트 아스트라(블래스트)", 1570, 1800, 10, modifier=ANCIENT_ARCHERY).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)  # 15.72초 10*10타

        AncientAstraTransition = core.DamageSkill("에인션트 아스트라(트랜지션)", 270, 450, 6, modifier=ANCIENT_ARCHERY).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)  # 16.11초 60*6타

        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime=120*1000, pdamage=10).wrap(core.BuffSkillWrapper)

        # 5차
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 3, 3)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 1, 1, 20+ceil(self.combat/2))

        Evolve = adventurer.EvolveWrapper(vEhc, 5, 5, Raven)
        UltimateBlast = core.DamageSkill("얼티밋 블래스트", LINK_DELAY + 1350, 400+20*vEhc.getV(2, 2), 15*5, cooltime=120*1000, red=True, modifier=core.CharacterModifier(armor_ignore=100) + ANCIENT_ARCHERY).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)

        RavenTempest = core.SummonSkill("레이븐 템페스트", LINK_DELAY + 540, 250, 400+20*vEhc.getV(0, 0), 5, 25*1000, cooltime=120*1000, red=True, modifier=ANCIENT_ARCHERY).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)

        ObsidionBarrierBlast = core.SummonSkill("옵시디언 배리어", LINK_DELAY + 60, 510, 400+12*vEhc.getV(4, 4), 4, (10+vEhc.getV(4, 4)//5)*1000, cooltime=200*1000, red=True, modifier=ANCIENT_ARCHERY).isV(vEhc, 4, 4).wrap(core.SummonSkillWrapper)

        RelicUnboundDischarge = core.SummonSkill("렐릭 언바운드(디스차지)", LINK_DELAY + 540, 360, 500+20*vEhc.getV(0, 0), 3, 22000, cooltime=120*1000, red=True, modifier=ANCIENT_ARCHERY).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)
        # RelicUnboundBlast = core.SummonSkill("렐릭 언바운드(블래스트)", LINK_DELAY + 540, 2000, 625+25*vEhc.getV(0, 0), 8*4, 2000*4-1, cooltime=120*1000, red=True, modifier=ANCIENT_ARCHERY).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)
        ######   Skill Wrapper   ######

        # 이볼브 / 레이븐 설정
        RavenTempest.onAfter(Raven.controller(0, "set_disabled"))
        RavenTempest.onAfter(Evolve.controller(0, "set_disabled"))
        Raven.onConstraint(core.ConstraintElement("레이븐 템페스트시 사용 금지", RavenTempest, RavenTempest.is_not_active))

        RelicCharge = RelicChargeStack(AncientGuidance, chtr)
        CardinalState = CardinalStateWrapper([SplitMistel, TripleImpact, EdgeOfResonance, ComboAssultHolder, AncientAstraHolder])

        # 기본적인 스킬연계 연결
        SplitMistel.onAfter(SplitMistelBonus)
        ComboAssultBlast.onAfter(ComboAssultBlastArrow)
        ComboAssultDischarge.onAfter(ComboAssultDischargeArrow)
        ComboAssultTransition.onAfter(ComboAssultTransitionArrow)

        TripleImpact.onBefore(TripleImpactJump)
        TripleImpact.onConstraint(core.ConstraintElement("레조넌스 동기화", EdgeOfResonance, EdgeOfResonance.is_usable))

        AncientAstraDischarge.onAfter(AncientAstraDischargeArrow)

        AncientAstraBlastRepeat = core.RepeatElement(AncientAstraBlast, 10)
        AncientAstraDischargeRepeat = core.RepeatElement(AncientAstraDischarge, 60)
        AncientAstraTransitionRepeat = core.RepeatElement(AncientAstraTransition, 60)

        # 렐릭 차지 연결
        CardinalDischarge.onAfter(RelicCharge.stackController(10*2))
        CardinalBlast.onAfter(RelicCharge.stackController(20))
        CardinalTransition.onAfter(RelicCharge.stackController(20))

        Raven.onTick(RelicCharge.stackController(10))
        Evolve.onTick(RelicCharge.stackController(10))

        SplitMistel.onAfter(RelicCharge.stackController(-50))
        SplitMistel.onConstraint(core.ConstraintElement('50 이상', RelicCharge, partial(RelicCharge.judge, 50, 1)))

        TripleImpact.onAfter(RelicCharge.stackController(-50))
        TripleImpact.onConstraint(core.ConstraintElement('50 이상', RelicCharge, partial(RelicCharge.judge, 50, 1)))

        EdgeOfResonance.onAfter(RelicCharge.stackController(-100))
        EdgeOfResonance.onConstraint(core.ConstraintElement('100 이상', RelicCharge, partial(RelicCharge.judge, 100, 1)))

        ComboAssultHolder.onAfter(RelicCharge.stackController(-150))
        ComboAssultHolder.onConstraint(core.ConstraintElement('150 이상', RelicCharge, partial(RelicCharge.judge, 150, 1)))

        AncientAstraHolder.onConstraint(core.ConstraintElement('300 이상', RelicCharge, partial(RelicCharge.judge, 300, 1)))
        AncientAstraBlast.onAfter(RelicCharge.stackController(-65*1.57))
        AncientAstraDischarge.onAfter(RelicCharge.stackController(-65*0.27))
        AncientAstraTransition.onAfter(RelicCharge.stackController(-65*0.27))

        RavenTempest.onConstraint(core.ConstraintElement('300 이상', RelicCharge, partial(RelicCharge.judge, 300, 1)))
        RavenTempest.onAfter(RelicCharge.stackController(-300))
        RavenTempest.onTick(RelicCharge.stackController(20))

        ObsidionBarrierBlast.onConstraint(core.ConstraintElement('500 이상', RelicCharge, partial(RelicCharge.judge, 500, 1)))
        ObsidionBarrierBlast.onAfter(RelicCharge.stackController(-500))

        RelicEvolution.onAfter(RelicCharge.stackController(1000))

        UltimateBlast.onConstraint(core.ConstraintElement('200 이상', RelicCharge, partial(RelicCharge.judge, 200, 1)))
        UltimateBlast.onAfter(RelicCharge.stackController(-1000))
        UltimateBlast.add_runtime_modifier(RelicCharge, lambda charge: core.CharacterModifier(pdamage_indep=(charge.stack // 250) * 25))

        RelicUnboundDischarge.onConstraint(core.ConstraintElement('350 이상', RelicCharge, partial(RelicCharge.judge, 350, 1)))
        RelicUnboundDischarge.onAfter(RelicCharge.stackController(-350))

        # 카디널 차지 연결
        CardinalBlast.onAfter(core.OptionalElement(partial(CardinalState.is_state, "DISCHARGE"), AdditionalDischarge))
        CardinalBlast.onAfter(core.OptionalElement(partial(CardinalState.is_state, "TRANSITION"), AdditionalTransition))
        CardinalDischarge.onAfter(core.OptionalElement(partial(CardinalState.is_state, "BLAST"), AdditionalBlast))
        CardinalDischarge.onAfter(core.OptionalElement(partial(CardinalState.is_state, "TRANSITION"), AdditionalTransition))

        CardinalBlast.onAfter(CardinalState.change_state("BLAST"))
        CardinalDischarge.onAfter(CardinalState.change_state("DISCHARGE"))
        CardinalTransition.onAfter(CardinalState.change_state("TRANSITION"))

        AdditionalBlast.onAfter(core.OptionalElement(RelicEvolution.is_active, AdditionalBlastEvolution))
        AdditionalDischarge.onAfter(core.OptionalElement(RelicEvolution.is_active, AdditionalDischargeEvolution))

        # 인챈트 포스 설정
        ComboAssultOptional = core.OptionalElement(partial(CardinalState.is_state, "DISCHARGE"), ComboAssultDischarge,
                                                   core.OptionalElement(partial(CardinalState.is_state, "BLAST"),
                                                   ComboAssultBlast, ComboAssultTransition))

        AncientAstraOptional = core.OptionalElement(partial(CardinalState.is_state, "DISCHARGE"), AncientAstraDischargeRepeat,
                                                    core.OptionalElement(partial(CardinalState.is_state, "BLAST"),
                                                    AncientAstraBlastRepeat, AncientAstraTransitionRepeat))

        ComboAssultHolder.onAfter(ComboAssultOptional)
        AncientAstraHolder.onAfter(AncientAstraOptional)

        ComboAssultHolder.onAfter(CardinalState.change_state("NONE"))
        AncientAstraHolder.onAfter(CardinalState.change_state("NONE"))
        ObsidionBarrierBlast.onAfter(CardinalState.change_state("NONE"))
        RelicUnboundDischarge.onAfter(CardinalState.change_state("NONE"))

        # 커스 트랜지션
        ComboAssultDischarge.onAfter(CurseTransition)
        ComboAssultBlast.onAfter(CurseTransition)
        ComboAssultTransition.onAfter(CurseTransition)
        CardinalTransition.onAfter(CurseTransition)

        # 기본공격 = 블래스트-디스차지
        CardinalBlast.onAfter(CardinalDischarge)

        ### Exports ###
        return(CardinalBlast,
               [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_wind_booster(), globalSkill.useful_combat_orders(),
                RelicCharge, AncientBowBooster, CurseTolerance, CurseTransition, SharpEyes,
                RelicEvolution, EpicAdventure,
                AncientGuidance, AdditionalTransition, globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), CriticalReinforce,
                globalSkill.soul_contract()] +
               [RelicUnboundDischarge, AncientAstraHolder, TripleImpact, EdgeOfResonance,
                ComboAssultHolder, UltimateBlast, SplitMistel, CardinalTransition] +
               [Evolve, Raven, GuidedArrow, RavenTempest, ObsidionBarrierBlast, MirrorBreak, MirrorSpider] +
               [] +
               [CardinalBlast])
