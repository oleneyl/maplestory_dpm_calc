from .globalSkill import GlobalSkills
from .jobbranch.bowmen import ArcherSkills
from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule, ComplexConditionRule
from . import globalSkill, jobutils
from .jobbranch import bowmen
from .jobclass import cygnus
from math import ceil
from typing import Any, Dict

import gettext
_ = gettext.gettext

# English skill information for Wind Archer here https://maplestory.fandom.com/wiki/Wind_Archer/Skills
class WindArcherSkills:
    # Link Skill
    CygnusBlessing = _("시그너스 블레스")  # "Cygnus Blessing"
    # Beginner
    ElementalHarmony = _("엘리멘탈 하모니")  # "Elemental Harmony"
    ElementalExpert = _("엘리멘탈 엑스퍼트")  # "Elemental Expert"
    # 1st Job
    BreezeArrow = _("브리즈 애로우")  # "Breeze Arrow"
    WindWalk = _("윈드워크")  # "Wind Walk"
    StormElemental = _("엘리멘트 : 스톰")  # "Storm Elemental"
    WhispersoftheWind = _("위스퍼 오브 윈드")  # "Whispers of the Wind"
    # 2nd Job
    FairySpiral = _("페어리 턴")  # "Fairy Spiral"
    GustShot = _("거스트 샷")  # "Gust Shot"
    TriflingWindI = _("트라이플링 윔 I")  # "Trifling Wind I"
    BowBooster = _("보우 부스터")  # "Bow Booster"
    SylvanAid = _("실프스 에이드")  # "Sylvan Aid"
    BowMastery = _("보우 마스터리")  # "Bow Mastery"
    PhysicalTraining = _("피지컬 트레이닝")  # "Physical Training"
    # 3rd Job
    SentientArrow = _("서리바람의 군무")  # "Sentient Arrow"
    PinpointPierce = _("핀포인트 피어스")  # "Pinpoint Pierce"
    TriflingWindII = _("트라이플링 윔II")  # "Trifling Wind II"
    Albatross = _("알바트로스")  # "Albatross"
    EmeraldFlower = _("에메랄드 플라워")  # "Emerald Flower"
    Featherweight = _("페더리니스")  # "Featherweight"
    SecondWind = _("세컨드 윈드")  # "Second Wind"
    # 4th Job
    CallofCygnus = _("시그너스 나이츠")  # "Call of Cygnus"
    SongofHeaven = _("천공의 노래")  # "Song of Heaven"
    SpiralingVortex = _("스파이럴 볼텍스")  # "Spiraling Vortex"
    TriflingWindIII = _("트라이플링 윔III")  # "Trifling Wind III"
    TouchoftheWind = _("윈드 블레싱")  # "Touch of the Wind"
    SharpEyes = _("샤프 아이즈")  # "Sharp Eyes"
    BowExpert = _("보우 엑스퍼트")  # "Bow Expert"
    EmeraldDust = _("에메랄드 더스트")  # "Emerald Dust"
    AlbatrossMax = _("알바트로스 맥시멈")  # "Albatross Max"
    # Hypers
    Monsoon = _("몬순")  # "Monsoon"
    GloryoftheGuardians = _("글로리 오브 가디언즈")  # "Glory of the Guardians"
    StormBringer = _("스톰 브링어")  # "Storm Bringer"
    # 5th Job
    HowlingGale = _("하울링 게일")  # "Howling Gale"
    MercilessWinds = _("아이들 윔")  # "Merciless Winds"
    GaleBarrier = _("윈드 월")  # "Gale Barrier"
    VortexSphere = _("볼텍스 스피어")  # "Vortex Sphere"


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "DEX"
        self.jobname = _("윈드브레이커")
        self.ability_list = Ability_tool.get_ability_set("boss_pdamage", "crit", "buff_rem")

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule(GlobalSkills.TermsAndConditions, ArcherSkills.ViciousShot), RuleSet.BASE)

        def howling_gale_rule(howling_gale, critical_reinforce):
            if critical_reinforce.is_active():
                return True
            if howling_gale.judge(1, -1) and critical_reinforce.is_cooltime_left(
                25000, -1
            ):
                return False
            return True

        ruleset.add_rule(
            ComplexConditionRule(WindArcherSkills.HowlingGale, [ArcherSkills.ViciousShot], howling_gale_rule),
            RuleSet.BASE,
        )
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=45, armor_ignore=15)

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ElementalExpert = core.InformedCharacterModifier(WindArcherSkills.ElementalExpert, patt=10)
        ElementalHarmony = core.InformedCharacterModifier(WindArcherSkills.ElementalHarmony, stat_main=chtr.level // 2)

        WhisperOfWind = core.InformedCharacterModifier(WindArcherSkills.WhispersoftheWind, att=20)
        PhisicalTraining = core.InformedCharacterModifier(WindArcherSkills.PhysicalTraining, stat_main=30, stat_sub=30)

        WindBlessingPassive = core.InformedCharacterModifier(
            _("{}(패시브)").format(WindArcherSkills.TouchoftheWind),
            pstat_main=15 + passive_level // 3,
            patt=10 + ceil(passive_level / 3),
        )
        BowExpert = core.InformedCharacterModifier(
            WindArcherSkills.BowExpert,
            att=30 + passive_level,
            crit_damage=20 + passive_level // 2,
            pdamage_indep=25 + passive_level // 3,
            boss_pdamage=40 + passive_level,
        )
        return [
            ElementalExpert,
            ElementalHarmony,
            WhisperOfWind,
            PhisicalTraining,
            BowExpert,
            WindBlessingPassive,
        ]

    def get_not_implied_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep=30)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=85+ceil(passive_level / 2))

        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        Nose sequence:
        Cheonno-Wim-Bringer

        Hyper:
        Tripling Wim-Reinforce, Enhance, Double Chance
        Celestial Song-Reinforce, Boss Killer

        Howlingale 58 times, vortex sphere 17 times

        Calculated as the average of the tripling wim

        코강 순서:
        천노-윔-브링어

        하이퍼:
        트라이플링 윔-리인포스, 인핸스, 더블찬스
        천공의 노래-리인포스, 보스 킬러

        하울링게일 58회, 볼텍스 스피어 17회 타격

        트라이플링 윔 평균치로 계산
        """
        base_modifier = chtr.get_base_modifier()
        passive_level = base_modifier.passive_level + self.combat
        # Buff skills
        Storm = core.BuffSkill(
            WindArcherSkills.StormElemental, delay=0, remain=200 * 1000, pdamage=10, rem=True
        ).wrap(core.BuffSkillWrapper)
        SylphsAid = core.BuffSkill(
            WindArcherSkills.SylvanAid, delay=0, remain=200 * 1000, att=20, crit=10, rem=True
        ).wrap(core.BuffSkillWrapper)
        Albatross = core.BuffSkill(
            WindArcherSkills.AlbatrossMax,
            delay=0,
            remain=200 * 1000,
            att=50 + passive_level,
            pdamage=25 + 2 * (passive_level // 3),
            armor_ignore=15 + passive_level // 3,
            crit=25 + passive_level // 2,
            rem=True,
        ).wrap(core.BuffSkillWrapper)
        SharpEyes = core.BuffSkill(
            WindArcherSkills.SharpEyes,
            delay=660,
            remain=(300 + 10 * self.combat) * 1000,
            crit=20 + ceil(self.combat / 2),
            crit_damage=15 + ceil(self.combat / 2),
            rem=True,
        ).wrap(core.BuffSkillWrapper)
        GloryOfGuardians = core.BuffSkill(
            name=WindArcherSkills.GloryoftheGuardians,
            delay=0,
            remain=60 * 1000,
            cooltime=120 * 1000,
            pdamage=10,
        ).wrap(core.BuffSkillWrapper)

        StormBringerDummy = core.BuffSkill(
            _("{}(버프)").format(WindArcherSkills.StormBringer),
            delay=0,  # Delay calculation required. 딜레이 계산 필요.
            remain=200 * 1000,
        ).wrap(core.BuffSkillWrapper)

        # Hyper: Increases damage, increases probability by 10%, and increases the number of strokes. 하이퍼: 데미지 증가, 확률 10% 증가, 타수 증가.
        whim_proc = (50 + 10 + passive_level // 2) * 0.01
        advanced_proc = (20 + passive_level // 3) * 0.01
        TriflingWhim = (
            core.DamageSkill(
                WindArcherSkills.TriflingWindIII,
                delay=0,
                damage=(290 + passive_level * 3) * (1 - advanced_proc)
                + (390 + passive_level * 3) * advanced_proc,
                hit=2 * whim_proc,
                modifier=core.CharacterModifier(pdamage=20),
            )
            .setV(vEhc, 1, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        StormBringer = (
            core.DamageSkill(WindArcherSkills.StormBringer, delay=0, damage=500, hit=0.3)
            .setV(vEhc, 2, 2, True)
            .wrap(core.DamageSkillWrapper)
        )

        # Pinpoint Pierce. 핀포인트 피어스.
        PinPointPierce = core.DamageSkill(
            WindArcherSkills.PinpointPierce,
            delay=690,
            damage=340,
            hit=2,
            cooltime=30 * 1000,
        ).wrap(core.DamageSkillWrapper)
        PinPointPierceDebuff = core.BuffSkill(
            _("{}(버프)").format(WindArcherSkills.PinpointPierce),
            delay=0,
            remain=30 * 1000,
            cooltime=-1,
            pdamage=15,
            armor_ignore=15,
        ).wrap(core.BuffSkillWrapper)

        # Damage Skills
        # Hyper: Increased damage, increased boss damage. 하이퍼: 데미지 증가, 보스 데미지 증가.
        target_pdamage = ((120 + self.combat // 2) / 100) ** 3 * 100 - 100
        SongOfHeaven = (
            core.DamageSkill(
                WindArcherSkills.SongofHeaven,
                delay=120,
                damage=345 + self.combat * 3,
                hit=1,
                modifier=core.CharacterModifier(
                    pdamage=target_pdamage + 20, boss_pdamage=30
                ),
            )
            .setV(vEhc, 0, 2, False)
            .wrap(core.DamageSkillWrapper)
        )

        CygnusPhalanx = cygnus.PhalanxChargeWrapper(vEhc, 0, 0)

        IdleWhim = (
            core.DamageSkill(
                WindArcherSkills.MercilessWinds,
                delay=600,
                damage=(500 + 20 * vEhc.getV(4, 4)) * 0.775,
                hit=10 * 3,
                cooltime=10 * 1000,
                red=True,
            )
            .isV(vEhc, 4, 4)
            .wrap(core.DamageSkillWrapper)
        )
        MercilesswindDOT = core.DotSkill(
            _("{}(도트)").format(WindArcherSkills.MercilessWinds),
            summondelay=0,
            delay=1000,
            damage=500 + 20 * vEhc.getV(4, 4),
            hit=1,
            remain=9000,
            cooltime=-1,
        ).wrap(core.DotSkillWrapper)

        # Summon Skills
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 5, 5)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        HowlingGail = core.StackableSummonSkillWrapper(
            core.SummonSkill(
                WindArcherSkills.HowlingGale,
                summondelay=630,
                delay=150,
                damage=250 + 10 * vEhc.getV(1, 1),
                hit=3,
                remain=150 * 58 - 1,  # 58타
                cooltime=20 * 1000,
            ).isV(vEhc, 1, 1),
            max_stack=2,
        )
        WindWall = (
            core.SummonSkill(
                WindArcherSkills.GaleBarrier,
                summondelay=720,
                delay=2000,
                damage=550 + vEhc.getV(2, 2) * 22,
                hit=5 * 3,
                remain=45 * 1000,
                cooltime=90 * 1000,
                red=True,
                modifier=core.CharacterModifier(pdamage_indep=-50),
            )
            .isV(vEhc, 2, 2)
            .wrap(core.SummonSkillWrapper)
        )
        VortexSphere = (
            core.SummonSkill(
                WindArcherSkills.VortexSphere,
                summondelay=720,
                delay=180,
                damage=400 + 16 * vEhc.getV(0, 0),
                hit=6,
                remain=180 * 17 - 1,
                cooltime=35000,
                red=True,
            )
            .isV(vEhc, 0, 0)
            .wrap(core.SummonSkillWrapper)
        )  # 17타

        ######   Skill Wrapper   #####

        CriticalReinforce = bowmen.CriticalReinforceWrapper(
            vEhc, chtr, 3, 3, 10 + 25 + passive_level // 2 + 20 + ceil(self.combat / 2)
        )  # Silps Aid + Albatross Maximum + Sharp Eyes. 실프스 에이드 + 알바트로스 맥시멈 + 샤프 아이즈.

        # Damage
        SongOfHeaven.onAfters([TriflingWhim, StormBringer])
        PinPointPierce.onAfters([PinPointPierceDebuff, TriflingWhim, StormBringer])
        MirrorBreak.onAfters([TriflingWhim, StormBringer])
        # Summon
        CygnusPhalanx.onTicks([TriflingWhim, StormBringer])
        HowlingGail.onTicks([TriflingWhim, StormBringer])
        VortexSphere.onTicks([TriflingWhim, StormBringer])

        IdleWhim.onAfter(MercilesswindDOT)

        return (
            SongOfHeaven,
            [
                globalSkill.maple_heros(
                    chtr.level, name=WindArcherSkills.CallofCygnus, combat_level=self.combat
                ),
                globalSkill.useful_combat_orders(),
                Storm,
                SylphsAid,
                Albatross,
                SharpEyes,
                StormBringerDummy,
                cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level),
                GloryOfGuardians,
                CriticalReinforce,
                globalSkill.soul_contract(),
            ]
            + [
                GuidedArrow,
                CygnusPhalanx,
                HowlingGail,
                VortexSphere,
                WindWall,
            ]
            + [
                MirrorBreak,
                IdleWhim,
                PinPointPierce,
            ]
            + [
                PinPointPierceDebuff,
                MirrorSpider,
                MercilesswindDOT,
            ]  # Not used from scheduler
            + [SongOfHeaven],
        )
