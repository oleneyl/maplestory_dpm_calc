from dpmModule.jobs.globalSkill import GlobalSkills, DOT, BUFF, STACK

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
from .globalSkill import PASSIVE

from localization.utilities import translator
_ = translator.gettext

"""
Advisor : Sniper range (red). 저격장(레드).
https://github.com/oleneyl/maplestory_dpm_calc/issues/247
"""
# English skill information for Bowmaster here https://maplestory.fandom.com/wiki/Bowmaster/Skills
class BowmasterSkills:
    # Link Skill
    # AdventurersCuriosity = _("")  # "Adventurer's Curiosity"
    # 1st Job
    ArrowBlow = _("애로우 블로우")  # "Arrow Blow"
    DoubleJump = _("더블 점프")  # "Double Jump"
    CriticalShot = _("크리티컬 샷")  # "Critical Shot"
    ArcheryMastery = _("아처 마스터리")  # "Archery Mastery"
    # 2nd Job
    ArrowBomb = _("애로우 봄")  # "Arrow Bomb"
    CoveringFire = _("리트리트 샷")  # "Covering Fire"
    BowBooster = _("보우 부스터")  # "Bow Booster"
    SoulArrowBow = _("소울 애로우: 활")  # "Soul Arrow: Bow"
    QuiverCartridge = _("퀴버 카트리지")  # "Quiver Cartridge"
    BowMastery = _("보우 마스터리")  # "Bow Mastery"
    FinalAttackBow = _("파이널 어택: 활")  # "Final Attack: Bow"
    PhysicalTraining = _("피지컬 트레이닝")  # "Physical Training"
    # 3rd Job
    FlameSurge = _("플레임 샷")  # "Flame Surge"
    Phoenix = _("피닉스")  # "Phoenix"
    Hookshot = _("슈타이크 아이젠")  # "Hookshot"
    RecklessHuntBow = _("익스트림 아처리")  # "Reckless Hunt: Bow"
    MortalBlow = _("모탈 블로우")  # "Mortal Blow"
    FocusedFury = _("컨센트레이션")  # "Focused Fury"
    EvasionBoost = _("닷지")  # "Evasion Boost"
    Marksmanship = _("마크맨쉽")  # "Marksmanship"
    ArrowBlaster = _("애로우 플래터")  # "Arrow Blaster"
    # 4th Job
    Hurricane = _("폭풍의 시")  # "Hurricane"
    BindingShot = _("운즈 샷")  # "Binding Shot"
    ArrowStream = _("언카운터블 애로우")  # "Arrow Stream"
    SharpEyes = _("샤프 아이즈")  # "Sharp Eyes"
    IllusionStep = _("일루젼 스탭")  # "Illusion Step"
    EnchantedQuiver = _("어드밴스드 퀴버")  # "Enchanted Quiver"
    BowExpert = _("보우 엑스퍼트")  # "Bow Expert"
    AdvancedFinalAttack = _("어드밴스드 파이널 어택")  # "Advanced Final Attack"
    ArmorBreak = _("아머 피어싱")  # "Armor Break"
    # Hypers
    GrittyGust = _("윈드 오브 프레이")  # "Gritty Gust"
    EpicAdventure = _("에픽 어드벤처")  # "Epic Adventure"
    Concentration = _("프리퍼레이션")  # "Concentration"
    # 5th Job
    StormofArrows = _("애로우 레인")  # "Storm of Arrows"
    InhumanSpeed = _("잔영의 시")  # "Inhuman Speed"
    QuiverBarrage = _("퀴버 풀버스트")  # "Quiver Barrage"
    SilhouetteMirage = _("실루엣 미라주")  # "Silhouette Mirage"


class ArmorPiercingWrapper(core.BuffSkillWrapper):
    """
    Armor Piercing-Adds final damage as much as enemy DEF, Bangmu +50%. Cooldown 9 seconds, decreases by 1 second per attack, minimum reactivation wait time 1 second
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
        skill = core.BuffSkill(_("아머 피어싱"), delay=0, remain=0, cooltime=9000, red=True)
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
        self.jobtype = "DEX"
        self.jobname = _("보우마스터")
        self.vEnhanceNum = 11
        self.ability_list = Ability_tool.get_ability_set(
            "boss_pdamage", "crit", "buff_rem"
        )
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=66, patt=8)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule(BowmasterSkills.Concentration, BowmasterSkills.QuiverBarrage), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(GlobalSkills.TermsAndConditions, BowmasterSkills.QuiverBarrage), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        CriticalShot = core.InformedCharacterModifier(BowmasterSkills.CriticalShot, crit=40)
        PhisicalTraining = core.InformedCharacterModifier(BowmasterSkills.PhysicalTraining, stat_main=30, stat_sub=30)

        MarkmanShip = core.InformedCharacterModifier(BowmasterSkills.Marksmanship, armor_ignore=25, patt=25)

        BowExpert = core.InformedCharacterModifier(
            BowmasterSkills.BowExpert, att=60 + passive_level, crit_damage=8
        )
        AdvancedFinalAttackPassive = core.InformedCharacterModifier(
            f"{BowmasterSkills.AdvancedFinalAttack}({PASSIVE})", att=20 + ceil(passive_level / 2)
        )  # Need to apply order. 오더스 적용필요.

        ElusionStep = core.InformedCharacterModifier(
            BowmasterSkills.IllusionStep, stat_main=80 + 2 * passive_level
        )

        return [
            CriticalShot,
            PhisicalTraining,
            MarkmanShip,
            BowExpert,
            AdvancedFinalAttackPassive,
            ElusionStep,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep=30)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=85 + ceil(passive_level / 2))
        ExtremeArchery = core.InformedCharacterModifier(BowmasterSkills.RecklessHuntBow, att=40, pdamage_indep=30)

        return [WeaponConstant, Mastery, ExtremeArchery]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        Remnant Poetry: Active 13*3 hits, passive 3.5*3 hits. Passive use 10 to 11 times during cooldown
        Arrow Lane: 1 stalk, hitting 3.5 times each fall

        Nose sequence:
        Foxy-Patag-Uncarble-Quieber-Platter-Phoenix

        Hyper: Storm City 3 types / Sharp Eyes-Ignor Guard, Critical Rate

        Preparation and ?? are used in a 120-second cycle

        잔영의 시 : 액티브 13*3타, 패시브 3.5*3타. 패시브는 쿨타임동안 10~11회 사용
        애로우 레인 : 1줄기, 떨어질 때 마다 3.5회 타격

        코강 순서:
        폭시-파택-언카블-퀴버-플래터-피닉스

        하이퍼: 폭풍의 시 3종 / 샤프 아이즈-이그노어 가드, 크리티컬 레이트

        프리퍼레이션, 엔버링크를 120초 주기에 맞춰 사용
        """
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ######   Skill   ######
        # Buff skills
        SoulArrow = core.BuffSkill(
            BowmasterSkills.SoulArrowBow, delay=0, remain=300 * 1000, att=30  # Pet buff. 펫버프.
        ).wrap(core.BuffSkillWrapper)
        SharpEyes = core.BuffSkill(
            BowmasterSkills.SharpEyes,
            delay=690,
            remain=300 * 1000,
            crit=20 + 5 + ceil(self.combat / 2),
            crit_damage=15 + ceil(self.combat / 2),
            armor_ignore=5,
        ).wrap(core.BuffSkillWrapper)
        Preparation = core.BuffSkill(
            BowmasterSkills.Concentration,
            delay=540,
            remain=30 * 1000,
            cooltime=90 * 1000,
            att=50,
            boss_pdamage=20,
        ).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill(
            BowmasterSkills.EpicAdventure, delay=0, remain=60 * 1000, cooltime=120 * 1000, pdamage=10
        ).wrap(core.BuffSkillWrapper)

        ArmorPiercing = ArmorPiercingWrapper(passive_level, chtr)
        MortalBlow = core.BuffSkill(
            BowmasterSkills.MortalBlow,
            delay=0,
            remain=5000,
            cooltime=-1,
            pdamage=35,
        ).wrap(core.BuffSkillWrapper)
        MortalBlowStack = core.StackSkillWrapper(
            core.BuffSkill(f"{BowmasterSkills.MortalBlow}({STACK})", 0, 99999999), 30
        )

        # Damage Skills
        MagicArrow = (
            core.DamageSkill(BowmasterSkills.EnchantedQuiver, delay=0, damage=260, hit=0.6)
            .setV(vEhc, 3, 2, True)
            .wrap(core.DamageSkillWrapper)
        )
        MagicArrow_ArrowRain = (
            core.DamageSkill(f"{BowmasterSkills.EnchantedQuiver}({BowmasterSkills.StormofArrows})", delay=0, damage=260, hit=1)
            .setV(vEhc, 3, 2, True)
            .wrap(core.DamageSkillWrapper)
        )
        AdvancedFinalAttack = (
            core.DamageSkill(
                BowmasterSkills.AdvancedFinalAttack,
                delay=0,
                damage=210 + 2 * passive_level,
                hit=0.7 + 0.01 * passive_level,
            )
            .setV(vEhc, 1, 2, True)
            .wrap(core.DamageSkillWrapper)
        )

        ArrowOfStorm = (
            core.DamageSkill(
                BowmasterSkills.Hurricane,
                delay=120,
                damage=(350 + self.combat * 3) * 0.75,
                hit=1 + 1,
                modifier=core.CharacterModifier(pdamage=30, boss_pdamage=10),
            )
            .setV(vEhc, 0, 2, True)
            .wrap(core.DamageSkillWrapper)
        )
        ArrowFlatter = (
            core.SummonSkill(
                BowmasterSkills.ArrowBlaster,
                summondelay=600,  # I don't know the delay. 딜레이 모름.
                delay=210,
                damage=85 + 90 + self.combat * 3,
                hit=1,
                remain=30 * 1000,
                modifier=core.CharacterModifier(pdamage=30),
            )
            .setV(vEhc, 4, 2, False)
            .wrap(core.SummonSkillWrapper)
        )

        GrittyGust = (
            core.DamageSkill(
                BowmasterSkills.GrittyGust,
                delay=720,
                damage=335,
                hit=12,
                cooltime=15 * 1000,
            )
            .setV(vEhc, 6, 2, True)
            .wrap(core.DamageSkillWrapper)
        )
        GrittyGustDOT = core.DotSkill(
            f"{BowmasterSkills.GrittyGust}({DOT})",
            summondelay=0,
            delay=1000,
            damage=200,
            hit=1,
            remain=10 * 1000,
            cooltime=-1,
        ).wrap(core.DotSkillWrapper)

        ArrowRainBuff = (
            core.BuffSkill(
                f"{BowmasterSkills.StormofArrows}({BUFF})",
                delay=510,
                remain=(40 + vEhc.getV(0, 0)) * 1000,
                cooltime=120 * 1000,
                red=True,
                pdamage=15 + (vEhc.getV(0, 0) // 2),
            )
            .isV(vEhc, 0, 0)
            .wrap(core.BuffSkillWrapper)
        )
        ArrowRain = DelayVaryingSummonSkillWrapper(
            core.SummonSkill(
                BowmasterSkills.StormofArrows,
                summondelay=0,
                delay=-1,
                damage=700 + vEhc.getV(0, 0) * 28,
                hit=7,
                remain=(40 + vEhc.getV(0, 0)) * 1000,
                cooltime=-1,
            ).isV(vEhc, 0, 0),
            delays=[1000, 1000, 1000, (5000 - 3000), 1000, 1000, (5000 - 2000)],
        )  # It drops every second and averages 3.5 hits. 1초마다 떨어지고, 평균 3.5히트가 나오도록.

        # Summon Skills
        Pheonix = (
            core.SummonSkill(
                BowmasterSkills.Phoenix,
                summondelay=0,  # When Evolve is over, it is automatically summoned, so the delay is 0. 이볼브가 끝나면 자동으로 소환되므로 딜레이 0.
                delay=1710,
                damage=390,
                hit=1,
                remain=220 * 1000,
            )
            .setV(vEhc, 5, 3, True)
            .wrap(core.SummonSkillWrapper)
        )
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 4, 4)
        Evolve = adventurer.EvolveWrapper(vEhc, 5, 5, Pheonix)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # No application of remnant poems. 잔영의시 미적용.
        QuibberFullBurstBuff = core.BuffSkill(
            f"{BowmasterSkills.QuiverBarrage}({BUFF})",
            delay=0,
            remain=30 * 1000,
            cooltime=120 * 1000,
            red=True,
            patt=(5 + int(vEhc.getV(2, 2) * 0.5)),
            crit_damage=8,  # Combine poison arrow Cdem here. 독화살 크뎀을 이쪽에 합침.
        ).wrap(core.BuffSkillWrapper)
        QuibberFullBurst = DelayVaryingSummonSkillWrapper(
            core.SummonSkill(
                BowmasterSkills.QuiverBarrage,
                summondelay=630,
                delay=-1,
                damage=250 + 10 * vEhc.getV(2, 2),
                hit=9,
                remain=30 * 1000,
                cooltime=-1,
            ).isV(vEhc, 2, 2),
            delays=[90, 90, 90, 90, 90, 90 + (2000 - 90 * 6)],
        )  # Fires 6 times every 2 seconds at 90ms intervals. 2초에 한번씩 90ms 간격으로 6회 발사.
        QuibberFullBurstDOT = core.DotSkill(
            _("독화살"),
            summondelay=0,
            delay=1000,
            damage=220,
            hit=3,  # Stacks 3 times. 3회 중첩.
            remain=30 * 1000,
            cooltime=-1,
        ).wrap(core.DotSkillWrapper)

        ImageArrow = (
            core.SummonSkill(
                BowmasterSkills.InhumanSpeed,
                summondelay=720,
                delay=240,
                damage=400 + 16 * vEhc.getV(1, 1),
                hit=3,  # 13 * 3 hits. 13 * 3타.
                remain=3000,
                cooltime=30000,
                red=True,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.SummonSkillWrapper)
        )
        ImageArrowPassive = (
            core.SummonSkill(
                f"{BowmasterSkills.InhumanSpeed}({PASSIVE})",
                summondelay=0,
                delay=2580,
                damage=400 + 16 * vEhc.getV(1, 1),
                hit=3.5 * 3,  # 3~4 * 3 hits, 11 times during cooldown. 3~4 * 3타, 잔시 쿨동안 11회 사용.
                remain=9999999,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.SummonSkillWrapper)
        )

        OpticalIllusion = (
            core.SummonSkill(
                BowmasterSkills.SilhouetteMirage,
                summondelay=0,
                delay=210,
                damage=400 + 16 * vEhc.getV(0, 0),
                hit=3,
                remain=210 * 5,
                cooltime=7500,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.SummonSkillWrapper)
        )

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

        GuidedArrow.onTick(MagicArrow)

        QuibberFullBurstBuff.onAfter(QuibberFullBurstDOT)
        QuibberFullBurstBuff.onAfter(QuibberFullBurst)
        QuibberFullBurst.onTick(MagicArrow)

        UseOpticalIllusion = core.OptionalElement(
            OpticalIllusion.is_available,
            OpticalIllusion,
            name=_("쿨타임 체크"),
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
