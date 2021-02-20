from enum import Enum

from .globalSkill import GlobalSkills
from .jobbranch.bowmen import ArcherSkills
from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, MutualRule, ConcurrentRunRule, ReservationRule
from . import globalSkill, jobutils
from .jobbranch import bowmen
from .jobclass import adventurer
from math import ceil
from typing import Any, Dict


# English skill information for Marksman here https://maplestory.fandom.com/wiki/Marksman/Skills
class MarksmanSkills(Enum):
    # Link Skill
    AdventurersCuriosity = 'Adventurer\'s Curiosity | '
    # 1st Job
    ArrowBlow = 'Arrow Blow | 애로우 블로우'
    DoubleJump = 'Double Jump | 더블 점프'
    CriticalShot = 'Critical Shot | 크리티컬 샷'
    ArcheryMastery = 'Archery Mastery | 아처 마스터리'
    # 2nd Job
    IronArrow = 'Iron Arrow | 아이언 애로우'
    Rangefinder = 'Rangefinder | 디스턴싱 센스'
    NetToss = 'Net Toss | 네트 쓰로잉'
    CrossbowBooster = 'Crossbow Booster | 크로스보우 부스터'
    SoulArrowCrossbow = 'Soul Arrow: Crossbow | 소울 애로우:석궁'
    CrossbowMastery = 'Crossbow Mastery | 크로스보우 마스터리'
    FinalAttackCrossbow = 'Final Attack: Crossbow | 파이널 어택:석궁'
    PhysicalTraining = 'Physical Training | 피지컬 트레이닝'
    # 3rd Job
    ExplosiveBolt = 'Explosive Bolt | 볼트 럽쳐'
    DragonsBreath = 'Dragon\'s Breath | 드래곤 펄스'
    Freezer = 'Freezer | 프리저'
    Hookshot = 'Hookshot | 슈타이크 아이젠'
    PainKiller = 'Pain Killer | 페인 킬러'
    RecklessHuntCrossbow = 'Reckless Hunt: Crossbow | 익스트림 아처리:석궁'
    MortalBlow = 'Mortal Blow | 모탈 블로우'
    AggressiveResistance = 'Aggressive Resistance | 데미지 리버싱'
    EvasionBoost = 'Evasion Boost | 닷지'
    Marksmanship = 'Marksmanship | 마크맨쉽'
    # 4th Job
    PiercingArrow = 'Piercing Arrow | 피어싱'
    Snipe = 'Snipe | 스나이핑'
    ArrowIllusion = 'Arrow Illusion | 애로우 일루전'
    SharpEyes = 'Sharp Eyes | 샤프 아이즈'
    IllusionStep = 'Illusion Step | 일루젼 스탭'
    CrossbowExpert = 'Crossbow Expert | 크로스보우 엑스퍼트'
    BoltSurplus = 'Bolt Surplus | 어디셔널 볼트'
    LastManStanding = 'Last Man Standing | 라스트맨 스탠딩'
    VitalHunter = 'Vital Hunter | 위크니스 파인딩'
    # Hypers
    HighSpeedShot = 'High Speed Shot | 롱 레인지 트루샷'
    EpicAdventure = 'Epic Adventure | 에픽 어드벤처'
    BullseyeShot = 'Bullseye Shot | 불스아이'
    # 5th Job
    PerfectShot = 'Perfect Shot | 트루 스나이핑'
    SplitShot = 'Split Shot | 스플릿 애로우'
    SurgeBolt = 'Surge Bolt | 차지드 애로우'
    RepeatingCrossbowCartridge = 'Repeating Crossbow Cartridge | 리피팅 크로스보우 카트리지'


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "DEX"
        self.jobname = "신궁"
        self.ability_list = Ability_tool.get_ability_set(
            "boss_pdamage", "crit", "buff_rem"
        )
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore=55, boss_pdamage=48, crit_damage=25)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(MutualRule(MarksmanSkills.SplitShot.value, MarksmanSkills.PerfectShot.value), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(MarksmanSkills.EpicAdventure.value, ArcherSkills.ViciousShot.value), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(MarksmanSkills.BullseyeShot.value, ArcherSkills.ViciousShot.value), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(GlobalSkills.TermsAndConditions.value, ArcherSkills.ViciousShot.value), RuleSet.BASE)
        ruleset.add_rule(ReservationRule(ArcherSkills.ViciousShot.value, MarksmanSkills.SplitShot.value), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(MarksmanSkills.SplitShot.value, GlobalSkills.TermsAndConditions.value), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(MarksmanSkills.RepeatingCrossbowCartridge.value, GlobalSkills.TermsAndConditions.value), RuleSet.BASE)

        return ruleset

    def get_passive_skill_list(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        CriticalShot = core.InformedCharacterModifier(MarksmanSkills.CriticalShot.value, crit=40)
        PhisicalTraining = core.InformedCharacterModifier(MarksmanSkills.PhysicalTraining.value, stat_main=30, stat_sub=30)
        MarkmanShip = core.InformedCharacterModifier(MarksmanSkills.Marksmanship.value, armor_ignore=25, pdamage=15)
        CrossBowExpert = core.InformedCharacterModifier(MarksmanSkills.CrossbowExpert.value, att=30 + passive_level, crit_damage=8)
        ElusionStep = core.InformedCharacterModifier(MarksmanSkills.IllusionStep.value, stat_main=40 + passive_level)

        return [
            CriticalShot,
            PhisicalTraining,
            MarkmanShip,
            CrossBowExpert,
            ElusionStep,
        ]

    def get_not_implied_skill_list(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=35)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=85+ceil(passive_level / 2))

        MortalBlow = core.InformedCharacterModifier(MarksmanSkills.MortalBlow.value, pdamage=2)
        ExtremeArchery = core.InformedCharacterModifier(MarksmanSkills.RecklessHuntCrossbow.value, crit_damage=20)

        return [WeaponConstant, Mastery, MortalBlow, ExtremeArchery]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        Distance 400

        Snare, piercing, long let, freezer

        거리 400

        스나, 피어싱, 롱레트, 프리저
        """
        DISTANCE = options.get("distance", 400)
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        def weakness_finding(distance: float):
            return core.CharacterModifier(
                armor_ignore=min(
                    ceil((20 + passive_level) / 2)
                    + distance // 40 * ceil((20 + passive_level) / 5),
                    20 + 30 + passive_level,
                )
            )

        def distancing_sense(distance: float):
            return core.CharacterModifier(
                armor_ignore=max(
                    min((-200 + distance) // -18 * 3, 20 + (10 + passive_level)), 0
                ),
                pdamage_indep=max(
                    min((distance - 200) // 18 * 4, 30 + (10 + passive_level)), 0
                ),
            )

        LASTMAN_STANDING = core.CharacterModifier(pdamage_indep=20 + 2 * passive_level)
        PASSIVE_MODIFIER = (
            weakness_finding(DISTANCE) + distancing_sense(DISTANCE) + LASTMAN_STANDING
        )
        PASSIVE_MODIFIER_SUMMON = weakness_finding(0) + distancing_sense(0)
        MORTAL_BLOW = core.CharacterModifier(pdamage=2)

        # Buff skills
        SoulArrow = core.BuffSkill(
            name=MarksmanSkills.SoulArrowCrossbow.value,
            delay=0,
            remain=300 * 1000,
            att=30,
            rem=True,
        ).wrap(core.BuffSkillWrapper)
        SharpEyes = core.BuffSkill(
            name=MarksmanSkills.SharpEyes.value,
            delay=660,
            remain=(300 + 10 * self.combat) * 1000,
            crit=20 + ceil(self.combat / 2),
            crit_damage=15 + ceil(self.combat / 2),
            rem=True,
        ).wrap(core.BuffSkillWrapper)

        BoolsEye = core.BuffSkill(
            name=MarksmanSkills.BullseyeShot.value,
            delay=960,
            remain=30 * 1000,
            cooltime=90 * 1000,
            crit=20,
            crit_damage=10,
            armor_ignore=20,
            pdamage=20,
        ).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill(
            name=MarksmanSkills.EpicAdventure.value,
            delay=0,
            remain=60 * 1000,
            cooltime=120 * 1000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)

        # Damage Skills
        # 롱레인지 트루샷: 나무위키피셜 DPM 떨어지므로 보류
        Snipping = (
            core.DamageSkill(
                name=MarksmanSkills.Snipe.value,
                delay=630,
                damage=465 + self.combat * 5,
                hit=9 + 1,
                modifier=core.CharacterModifier(
                    crit=100,
                    armor_ignore=20 + self.combat * 1,
                    pdamage=20,
                    boss_pdamage=10,
                )
                + PASSIVE_MODIFIER
                + MORTAL_BLOW,
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        TrueSnippingTick = (
            core.DamageSkill(
                name=f"{MarksmanSkills.PerfectShot.value}(Tick | 타격)",
                delay=690,
                damage=950 + vEhc.getV(2, 2) * 30,
                hit=14 + 1,
                modifier=core.CharacterModifier(pdamage=100, armor_ignore=100)
                + PASSIVE_MODIFIER
                + MORTAL_BLOW,
            )
            .isV(vEhc, 2, 2)
            .wrap(core.DamageSkillWrapper)
        )
        TrueSnipping = (
            core.DamageSkill(MarksmanSkills.PerfectShot.value, 120, 0, 0, cooltime=180 * 1000, red=True)
            .isV(vEhc, 2, 2)
            .wrap(core.DamageSkillWrapper)
        )

        ChargedArrow = (
            core.DamageSkill(
                name=MarksmanSkills.SurgeBolt.value,
                delay=0,
                damage=750 + vEhc.getV(1, 1) * 30,
                hit=10 + 1,
                cooltime=-1,
                modifier=PASSIVE_MODIFIER + MORTAL_BLOW,
            )
            .isV(vEhc, 1, 1)
            .wrap(core.DamageSkillWrapper)
        )
        ChargedArrowHold = (
            core.SummonSkill(f"{MarksmanSkills.SurgeBolt.value}(Dummy | 더미)", 0, 10000, 0, 0, 9999999, cooltime=-1)
            .isV(vEhc, 1, 1)
            .wrap(core.SummonSkillWrapper)
        )  # TODO: Cool feeling should be applied to the attack cycle. 공격 주기에 쿨감 적용해야 함.

        # Summon Skills
        Freezer = (
            core.SummonSkill(
                name=MarksmanSkills.Freezer.value,
                summondelay=0,
                delay=1710,
                damage=390 if DISTANCE <= 280 else 0,
                hit=1,
                remain=220 * 1000,
                modifier=PASSIVE_MODIFIER_SUMMON,
            )
            .setV(vEhc, 3, 3, False)
            .wrap(core.SummonSkillWrapper)
        )  # It is automatically summoned at the end of Evolve, so if it is more than 0 delay and 280 range, it does not attack. 이볼브 종료시 자동소환되므로 딜레이 0, 사거리 280보다 멀면 공격안함.
        Evolve = adventurer.EvolveWrapper(
            vEhc, 5, 5, Freezer, modifier=PASSIVE_MODIFIER_SUMMON
        )

        GuidedArrow = bowmen.GuidedArrowWrapper(
            vEhc, 4, 4, modifier=PASSIVE_MODIFIER + MORTAL_BLOW
        )
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(
            vEhc,
            0,
            0,
            break_modifier=PASSIVE_MODIFIER + MORTAL_BLOW,
            spider_modifier=PASSIVE_MODIFIER_SUMMON,
        )

        SplitArrow = (
            core.DamageSkill(
                name=f"{MarksmanSkills.SplitShot.value}(Attack | 공격)",
                delay=0,
                damage=600 + vEhc.getV(0, 0) * 24,
                hit=5 + 1,
                modifier=PASSIVE_MODIFIER + MORTAL_BLOW,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )
        SplitArrowBuff = (
            core.BuffSkill(
                name=MarksmanSkills.SplitShot.value,
                delay=810,
                remain=60 * 1000,
                cooltime=120 * 1000,
                red=True,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.BuffSkillWrapper)
        )
        # TODO : Split Arrow calculation. 스플릿애로우 계산.

        RepeatingCartrige = (
            core.BuffSkill(
                name=MarksmanSkills.RepeatingCrossbowCartridge.value,
                delay=510,
                remain=60000,
                cooltime=120 * 1000,
                red=True,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.BuffSkillWrapper)
        )
        CartrigeStack = core.StackSkillWrapper(core.BuffSkill("Cartridge | 카트리지", 0, 99999999), 8)
        FullBurstShot = (
            core.DamageSkill(
                name="Full Burst Shot | 풀버스트 샷",
                delay=810,
                damage=300 + 12 * vEhc.getV(0, 0),
                hit=(9 + 1) * 4,
                cooltime=-1,
                modifier=PASSIVE_MODIFIER + MORTAL_BLOW,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.DamageSkillWrapper)
        )

        FinalAttack = (
            core.DamageSkill(
                name=MarksmanSkills.FinalAttackCrossbow.value,
                delay=0,
                damage=150,
                hit=0.4,
                modifier=PASSIVE_MODIFIER,
            )
            .setV(vEhc, 4, 2, True)
            .wrap(core.DamageSkillWrapper)
        )

        ######   Skill Wrapper   ######

        CriticalReinforce = bowmen.CriticalReinforceWrapper(
            vEhc, chtr, 3, 3, 20 + 20 + ceil(self.combat / 2)
        )  # Sharp Eyes 20 + Bull's Eye 20. Considering the utilization rate as Bull's Eye is always used according to Cree X. 샤프 아이즈 20 + 불스아이 20. 불스아이를 항상 크리인에 맞춰쓰므로 가동률 고려 X.

        SplitArrowOption = core.OptionalElement(
            SplitArrowBuff.is_active, SplitArrow, name=f"Check {MarksmanSkills.SplitShot.value} 여부 확인"
        )
        Snipping.onAfter(SplitArrowOption)
        FullBurstShot.onAfter(core.RepeatElement(SplitArrowOption, 4))

        TrueSnippingDeal = core.RepeatElement(TrueSnippingTick, 7)
        TrueSnipping.onBefore(ChargedArrowHold.controller(10000, name="End of charging | 차징 유예"))
        TrueSnipping.onAfter(TrueSnippingDeal)

        # TODO: Implementing charged cancel / Difficulty stopping mid-delay until it is implemented. 차지드 캔슬 구현할것 / 딜레이 중간에 끊는게 구현되기 전까지 어려움.
        ChargedArrowHold.onTick(
            core.OptionalElement(partial(CartrigeStack.judge, 0, -1), ChargedArrow)
        )  # Charged simultaneous firing is not allowed during full burst shot. 풀버스트샷 도중에는 차지드 동시발사가 안됨.

        for sk in [Snipping, TrueSnippingTick, ChargedArrow]:
            sk.onAfter(FinalAttack)
        FullBurstShot.onAfter(core.RepeatElement(FinalAttack, 4))

        ChargedArrowHold.set_disabled_and_time_left(5000)  # Initial charging time. 최초 차징 시간.

        RepeatingCartrige.onAfter(CartrigeStack.stackController(8))
        FullBurstShot.onAfter(CartrigeStack.stackController(-1))

        BasicAttack = core.DamageSkill("기본 공격", 0, 0, 0).wrap(core.DamageSkillWrapper)
        BasicAttack.onAfter(
            core.OptionalElement(
                partial(CartrigeStack.judge, 1, 1), FullBurstShot, Snipping
            )
        )

        return (
            BasicAttack,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_wind_booster(),
                globalSkill.useful_combat_orders(),
                SoulArrow,
                SharpEyes,
                BoolsEye,
                EpicAdventure,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                CriticalReinforce,
                RepeatingCartrige,
                SplitArrowBuff,
                globalSkill.soul_contract(),
            ]
            + [TrueSnipping, ChargedArrowHold, ChargedArrow]
            + [Freezer, Evolve, GuidedArrow, MirrorBreak, MirrorSpider]
            + []
            + [BasicAttack],
        )
