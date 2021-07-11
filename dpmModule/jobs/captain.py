from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ConditionRule, RuleSet, ConcurrentRunRule
from . import globalSkill
from .jobbranch import pirates
from .jobclass import adventurer
from . import jobutils
from math import ceil
from typing import Any, Dict
import os


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.load(os.path.join(os.path.dirname(__file__), 'configs', 'captain.json'))

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=28, armor_ignore=22)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule('노틸러스', '노틸러스 어썰트', lambda sk: sk.is_cooltime_left(8000, 1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule('소울 컨트랙트', '노틸러스 어썰트', lambda sk: sk.is_usable() or sk.is_cooltime_left(70000, 1)), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('노틸러스 어썰트', '소울 컨트랙트'), RuleSet.BASE)

        return ruleset

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_skill_list = super(JobGenerator, self).get_passive_skill_list(vEhc, chtr, options)
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 1, 2)
        return passive_skill_list + [LoadedDicePassive]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        ----정보---
        크루 커멘더쉽 : 최종뎀 15%
        무라트 : 500 크뎀5
        발레리 : 560 크리15
        잭 : 320
        스토너 : 480
        두명 소환

        하이퍼
        래피드파이어 - 보스킬러, 리인포스, 애드레인지
        헤드샷 - 보너스 어택, 리인포스

        데드아이 조준률 3배

        퀵 드로우 : 사용 가능하면 헤드샷, 스트레인지 봄, 데드아이 전에 사용

        서먼 크루 분당 17타, 평균 퍼뎀 465
        봄버 평균 데미지 600ms당 297%x3

        카운터 어택 미발동

        5차 강화
        래피드 / 퍼실 / 디그니티
        헤드샷 / 배틀쉽 / 옥타
        서먼크루 / 스트봄 / 노틸러스
        """
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        self.passive_level = chtr.get_base_modifier().passive_level + self.combat

        DEADEYEACC = 3
        DEADEYEAIM = 3480
        BULLET_PARTY_TICK = 150
        CONTINUAL_AIMING = core.CharacterModifier(pdamage_indep=25 + 2 * self.combat)
        BULLET_ATT = core.CharacterModifier(att=22)  # 자이언트 불릿

        ######   Skill   ######
        # Buff skills
        PirateStyle = self.load_skill_wrapper("파이렛 스타일")
        LuckyDice = self.load_skill_wrapper("로디드 다이스", vEhc)
        QuickDraw = self.load_skill_wrapper("퀵 드로우", vEhc)

        QuickDrawStack = core.StackSkillWrapper(
            core.BuffSkill("퀵 드로우(준비)", 0, core.infinite_time()), 1
        )
        # Summon Skills
        OctaQuaterdeck = self.load_skill_wrapper("옥타 쿼터덱", vEhc)
        SummonCrew = self.load_skill_wrapper("서먼 크루", vEhc)
        SummonCrewBuff = self.load_skill_wrapper("서먼 크루(버프)")
        """
        돈틀레스 : 330 보통 13/22 타수3 600
        블랙바크 : 445 느림 15/18 타수3 810
        슈린츠 : 200 빠름   15/27 타수3 570
        조나단 : 320 보통   12/20 타수3 600
        평균 데미지 600ms당 297
        """
        BB_AVERAGE = (
            (330 + 3 * self.combat)
            + (445 + 3 * self.combat) * (600 / 810)
            + (200 + 3 * self.combat) * (600 / 570)
            + (320 + 3 * self.combat)
        ) / 4
        # TODO: 배틀쉽 봄버 공격주기 확인 필요
        BattleshipBomber = self.load_skill_wrapper("배틀쉽 봄버")

        BattleshipBomber_1 = self.load_skill_wrapper("배틀쉽 봄버(소환, 1)", vEhc)
        BattleshipBomber_2 = self.load_skill_wrapper("배틀쉽 봄버(소환, 2)", vEhc)

        # Damage Skills
        RapidFire = self.load_skill_wrapper("래피드 파이어", vEhc)
        Headshot = self.load_skill_wrapper("헤드 샷", vEhc)
        Nautilus = self.load_skill_wrapper("노틸러스", vEhc)
        CaptainDignity = self.load_skill_wrapper("캡틴 디그니티", vEhc)

        # Hyper
        StrangeBomb = self.load_skill_wrapper("스트레인지 봄", vEhc)
        EpicAdventure = self.load_skill_wrapper("에픽 어드벤처")

        # 5th
        PirateFlag = adventurer.PirateFlagWrapper(vEhc, 2, 1, chtr.level)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 4, 4, WEAPON_ATT)
        BulletParty = self.load_skill_wrapper("불릿 파티", vEhc)
        BulletPartyTick = self.load_skill_wrapper("불릿 파티(틱)", vEhc)
        
        DeadEye = self.load_skill_wrapper("데드아이", vEhc)
        NautilusAssult = self.load_skill_wrapper("노틸러스 어썰트", vEhc)
        NautilusAssult_2 = self.load_skill_wrapper("노틸러스 어썰트(일제 사격)", vEhc)

        DeathTriggerInit = self.load_skill_wrapper("데스 트리거(개시)", vEhc)
        DeathTrigger = self.load_skill_wrapper("데스 트리거", vEhc)
        DeathTriggerEnd = self.load_skill_wrapper("데스 트리거(후딜)", vEhc)


        ######   Skill Wrapper   ######

        # 크루 사용 후 버프 제공
        SummonCrew.onAfter(SummonCrewBuff)

        # 배틀쉽은 둘 중 꺼져있는걸로 시전
        BattleshipBomber.onAfter(
            core.OptionalElement(
                BattleshipBomber_1.is_active,
                BattleshipBomber_2,
                BattleshipBomber_1,
                name="배틀쉽 1,2",
            )
        )

        # 노틸러스 이후 배틀쉽 쿨감
        Nautilus.onAfter(BattleshipBomber.controller(0.5, "reduce_cooltime_p"))

        # 디그니티는 노틸러스 쿨타임에 강화됨
        CaptainDignity.add_runtime_modifier(
            Nautilus,
            lambda sk: core.CharacterModifier(
                pdamage_indep=30 * (not sk.is_available())
            ),
        )
        for sk in [RapidFire, Headshot, BulletPartyTick, DeadEye, DeathTrigger]:
            sk.onAfter(CaptainDignity)

        # 퀵 드로우
        QuickDrawProc = core.OptionalElement(
            QuickDraw.is_not_active,
            QuickDrawStack.stackController((8 + ceil(self.combat/2)) * 0.01, name="퀵 드로우 확률"),
        )
        QuickDraw.onJustAfter(QuickDrawStack.stackController(-1))
        QuickDrawProc.onJustAfter(
            core.OptionalElement(
                lambda: QuickDrawStack.judge(1, 1) and QuickDraw.is_not_active(),
                QuickDraw,
            )
        )
        for sk in [
            RapidFire,
            Headshot,
            Nautilus,
            StrangeBomb,
            BulletPartyTick,
            DeadEye,
            DeathTrigger,
        ]:
            sk.onJustAfter(QuickDrawProc)
        for sk in [NautilusAssult, NautilusAssult_2]:
            sk.onTick(QuickDrawProc)

        QuickDrawShutdownTrigger = QuickDraw.controller(-1)
        for sk in [Headshot, StrangeBomb, DeadEye, DeathTrigger, Nautilus, MirrorBreak]:
            sk.onJustAfter(QuickDrawShutdownTrigger)
            sk.add_runtime_modifier(QuickDraw, lambda sk: core.CharacterModifier(pdamage_indep=(25 + self.combat) * sk.is_active()))
        for sk in [NautilusAssult, NautilusAssult_2]:
            sk.onTick(QuickDrawShutdownTrigger)
            sk.add_runtime_modifier(QuickDraw, lambda sk: core.CharacterModifier(pdamage_indep=(25 + self.combat) * sk.is_active()))

        # 노틸러스 어썰트
        NautilusAssult.onEventEnd(NautilusAssult_2)
        NautilusAssult.onJustAfter(
            core.OptionalElement(
                partial(Nautilus.is_cooltime_left, 8000, -1),
                Nautilus.controller(8000),
                name="노틸러스 쿨타임 8초",
            )
        )
        Nautilus.onJustAfter(
            core.OptionalElement(
                partial(NautilusAssult.is_cooltime_left, 8000, -1),
                NautilusAssult.controller(8000),
                name="노틸러스 어썰트 쿨타임 8초",
            )
        )

        # 불릿파티
        BulletParty.onAfter(
            core.RepeatElement(BulletPartyTick, 11820 // BULLET_PARTY_TICK)
        )

        # 데스 트리거
        DeathTriggerInit.onAfter(core.RepeatElement(DeathTrigger, 7))
        DeathTriggerInit.onAfter(DeathTriggerEnd)

        return (
            RapidFire,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                SummonCrewBuff,
                PirateStyle,
                LuckyDice,
                EpicAdventure,
                PirateFlag,
                Overdrive,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                QuickDraw,
                globalSkill.soul_contract(),
            ]
            + [
                BattleshipBomber,
                DeathTriggerInit,
                Headshot,
                Nautilus,
                DeadEye,
                StrangeBomb,
                MirrorBreak,
                MirrorSpider,
            ]
            + [
                OctaQuaterdeck,
                BattleshipBomber_1,
                BattleshipBomber_2,
                NautilusAssult,
                NautilusAssult_2,
                SummonCrew,
            ]
            + [BulletParty]
            + [RapidFire],
        )
