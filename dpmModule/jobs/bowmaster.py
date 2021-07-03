from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule
from . import globalSkill
from .jobbranch import bowmen
from .jobclass import adventurer
from math import ceil
from typing import Any, Dict
from functools import partial
import os
"""
Advisor : 저격장(레드)
https://github.com/oleneyl/maplestory_dpm_calc/issues/247
"""


class ArmorPiercingWrapper(core.BuffSkillWrapper):
    """
    아머 피어싱 - 적 방어율만큼 최종뎀 추가, 방무+50%. 쿨타임 9초, 공격마다 1초씩 감소, 최소 재발동 대기시간 1초
    """

    def __init__(self, combat, chtr):
        self.piercing_modifier = core.CharacterModifier(
            pdamage_indep=min(core.constant.ARMOR_RATE * (1 + combat * 0.05), 400),
            armor_ignore=50 * (1 + combat * 0.02),
        )
        self.empty_modifier = core.CharacterModifier()
        self.skill_modifier = chtr.get_skill_modifier()
        self.cooltime_skip_task = core.TaskHolder(core.Task(self, self._cooltime_skip))
        skill = core.BuffSkill("아머 피어싱", delay=0, remain=0, cooltime=9000, red=True)
        super(ArmorPiercingWrapper, self).__init__(skill)

    def check_modifier(self) -> core.CharacterModifier:
        if self.cooltimeLeft <= 0:
            self.cooltimeLeft = self.calculate_cooltime(self.skill_modifier)
            return self.piercing_modifier
        else:
            self._cooltime_skip()
            return self.empty_modifier

    def _cooltime_skip(self) -> None:
        if self.cooltimeLeft > 1000:
            self.cooltimeLeft = self.cooltimeLeft - 1000
        return self._result_object_cache

    def cooltime_skip(self):
        return self.cooltime_skip_task


class DelayVaryingSummonSkillWrapper(core.SummonSkillWrapper):
    # TODO: temporal fix... move to kernel/core, make DelayVaryingSummonSkill and use self.skill.delays
    def __init__(self, skill, delays) -> None:
        super(DelayVaryingSummonSkillWrapper, self).__init__(skill)
        self.delays = delays
        self.hit_count = 0

    def _useTick(self) -> core.ResultObject:
        result = super(DelayVaryingSummonSkillWrapper, self)._useTick()
        self.hit_count = (self.hit_count + 1) % len(self.delays)
        return result

    def get_delay(self) -> float:
        return self.delays[self.hit_count]


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.load(os.path.join(os.path.dirname(__file__), 'configs', 'bowmaster.json'))
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=66, patt=8)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule("프리퍼레이션", "퀴버 풀버스트"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("소울 컨트랙트", "퀴버 풀버스트"), RuleSet.BASE)
        return ruleset

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        잔영의 시 : 액티브 13*3타, 패시브 3.5*3타. 패시브는 쿨타임동안 10~11회 사용
        애로우 레인 : 1줄기, 떨어질 때 마다 3.5회 타격

        코강 순서:
        폭시-파택-언카블-퀴버-플래터-피닉스

        하이퍼: 폭풍의 시 3종 / 샤프 아이즈-이그노어 가드, 크리티컬 레이트

        프리퍼레이션, 엔버링크를 120초 주기에 맞춰 사용
        """
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        self.passive_level = chtr.get_base_modifier().passive_level + self.combat
        ######   Skill   ######
        # Buff skills

        SoulArrow = self.load_skill_wrapper("소울 애로우")
        SharpEyes = self.load_skill_wrapper("샤프 아이즈")
        Preparation = self.load_skill_wrapper("프리퍼레이션")

        EpicAdventure = self.load_skill_wrapper("에픽 어드벤처")
        ArmorPiercing = ArmorPiercingWrapper(passive_level, chtr)

        MortalBlow = self.load_skill_wrapper("모탈 블로우")
        MortalBlowStack = core.StackSkillWrapper(
            core.BuffSkill("모탈 블로우(스택)", 0, 99999999), 30
        )

        # Damage Skills
        MagicArrow = self.load_skill_wrapper("어드밴스드 퀴버", vEhc)
        MagicArrow_ArrowRain = self.load_skill_wrapper("어드밴스드 퀴버(애로우 레인)", vEhc)

        AdvancedFinalAttack = self.load_skill_wrapper("어드밴스드 파이널 어택", vEhc)
        ArrowOfStorm = self.load_skill_wrapper("폭풍의 시", vEhc)
        ArrowFlatter = self.load_skill_wrapper("애로우 플래터", vEhc)
        GrittyGust = self.load_skill_wrapper("윈드 오브 프레이", vEhc)
        GrittyGustDOT = self.load_skill_wrapper("윈드 오브 프레이(도트)", vEhc)
        ArrowRainBuff = self.load_skill_wrapper("애로우 레인(버프)", vEhc)

        ArrowRain = DelayVaryingSummonSkillWrapper(
            core.SummonSkill(
                "애로우 레인",
                summondelay=0,
                delay=-1,
                damage=700 + vEhc.getV(0, 0) * 28,
                hit=7,
                remain=(40 + vEhc.getV(0, 0)) * 1000,
                cooltime=-1,
            ).isV(vEhc, 0, 0),
            delays=[1000, 1000, 1000, (5000 - 3000), 1000, 1000, (5000 - 2000)],
        )  # 1초마다 떨어지고, 평균 3.5히트가 나오도록.

        # Summon Skills
        Pheonix = self.load_skill_wrapper("피닉스", vEhc)
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 4, 4)
        Evolve = adventurer.EvolveWrapper(vEhc, 5, 5, Pheonix)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # 잔영의시 미적용
        QuibberFullBurstBuff = self.load_skill_wrapper("퀴버 풀버스트(버프)",vEhc)
        QuibberFullBurst = DelayVaryingSummonSkillWrapper(
            core.SummonSkill(
                "퀴버 풀버스트",
                summondelay=630,
                delay=-1,
                damage=250 + 10 * vEhc.getV(2, 2),
                hit=9,
                remain=30 * 1000,
                cooltime=-1,
            ).isV(vEhc, 2, 2),
            delays=[90, 90, 90, 90, 90, 90 + (2000 - 90 * 6)],
        )  # 2초에 한번씩 90ms 간격으로 6회 발사
        QuibberFullBurstDOT = self.load_skill_wrapper("독화살")
        ImageArrow = self.load_skill_wrapper("잔영의 시", vEhc)
        ImageArrowPassive = self.load_skill_wrapper("잔영의 시(패시브)", vEhc)
        OpticalIllusion = self.load_skill_wrapper("실루엣 미라주", vEhc)

        ######   Skill Wrapper   ######
        GrittyGust.onAfter(GrittyGustDOT)

        CriticalReinforce = bowmen.CriticalReinforceWrapper(
            vEhc, chtr, 3, 3, 25 + ceil(self.combat / 2)
        )

        ArrowOfStorm.onAfter(MagicArrow)
        ArrowOfStorm.onAfter(AdvancedFinalAttack)

        ArrowRainBuff.onAfter(ArrowRain)
        ArrowRain.onTick(MagicArrow_ArrowRain)

        ImageArrow.onJustAfter(
            ImageArrowPassive.controller(99999999, "set_disabled_and_time_left")
        )
        ImageArrow.onEventEnd(ImageArrowPassive)
        ImageArrow.onTick(AdvancedFinalAttack)
        ImageArrow.onTick(MagicArrow)

        GuidedArrow.onTick(MagicArrow)

        QuibberFullBurstBuff.onAfter(QuibberFullBurstDOT)
        QuibberFullBurstBuff.onAfter(QuibberFullBurst)
        QuibberFullBurst.onTick(MagicArrow)

        UseOpticalIllusion = core.OptionalElement(
            OpticalIllusion.is_available,
            OpticalIllusion,
            name="쿨타임 체크",
        )
        for sk in [ArrowOfStorm, GrittyGust]:
            sk.onAfter(UseOpticalIllusion)
        OpticalIllusion.protect_from_running()
        OpticalIllusion.onAfter(MagicArrow)

        # Mortal Blow
        AddMortalStack = core.OptionalElement(
            MortalBlow.is_not_active, MortalBlowStack.stackController(1)
        )
        AddMortalStack.onJustAfter(
            core.OptionalElement(partial(MortalBlowStack.judge, 30, 1), MortalBlow)
        )
        MortalBlow.onJustAfter(MortalBlowStack.stackController(-30))
        ArrowOfStorm.onJustAfter(AddMortalStack)
        ImageArrow.onTick(AddMortalStack)

        # Armor Piercing
        for sk in [
            ArrowRain,
            QuibberFullBurst,
            OpticalIllusion,
            GuidedArrow,
        ]:
            sk.onTick(ArmorPiercing.cooltime_skip())
        for sk in [ArrowOfStorm, ImageArrow]:
            sk.add_runtime_modifier(
                ArmorPiercing,
                lambda armor_piercing: armor_piercing.check_modifier(),
            )
        ArmorPiercing.protect_from_running()

        ### Exports ###
        return (
            ArrowOfStorm,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_combat_orders(),
                SoulArrow,
                SharpEyes,
                EpicAdventure,
                ArmorPiercing,
                Preparation,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                ArrowRainBuff,
                CriticalReinforce,
                QuibberFullBurstBuff,
                QuibberFullBurstDOT,
                ImageArrowPassive,
                globalSkill.soul_contract(),
            ]
            + []
            + [
                Pheonix,
                Evolve,
                ArrowFlatter,
                ArrowRain,
                GuidedArrow,
                QuibberFullBurst,
                ImageArrow,
                MirrorBreak,
                MirrorSpider,
                OpticalIllusion,
            ]
            + [MortalBlow]
            + [ArrowOfStorm],
        )
