from enum import Enum

from .globalSkill import GlobalSkills
from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import ComplexConditionRule, ConditionRule, RuleSet
from . import globalSkill
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict


# English skill information for Paladin here https://maplestory.fandom.com/wiki/Paladin/Skills
class PaladinSkills(Enum):
    # Link Skill
    InvincibleBelief = 'Invincible Belief | 인빈서블 빌리프'
    # 1st Job
    SlashBlast = 'Slash Blast | 슬래시 블러스트'
    WarLeap = 'War Leap | 워리어 리프'
    LeapAttack = 'Leap Attack | 리프 어택'
    IronBody = 'Iron Body | 아이언 바디'
    WarriorMastery = 'Warrior Mastery | 워리어 마스터리'
    # 2nd Job
    FlameCharge = 'Flame Charge | 플레임 차지'
    BlizzardCharge = 'Blizzard Charge | 블리자드 차지'
    ElementalCharge = 'Elemental Charge | 엘리멘탈 차지'
    CloseCombat = 'Close Combat | 페이지 오더'
    WeaponBooster = 'Weapon Booster | 웨폰 부스터'
    WeaponMastery = 'Weapon Mastery | 웨폰 마스터리'
    FinalAttack = 'Final Attack | 파이널 어택'
    PhysicalTraining = 'Physical Training | 피지컬 트레이닝'
    # 3rd Job
    LightningCharge = 'Lightning Charge | 라이트닝 차지'
    HPRecovery = 'HP Recovery | 리스토네이션'
    Rush = 'Rush | 돌진'
    Threaten = 'Threaten | 위협'
    UpwardCharge = 'Upward Charge | 어퍼 차지'
    ParashockGuard = 'Parashock Guard | 파라쇼크 가드'
    CombatOrders = 'Combat Orders | 컴뱃 오더스'
    ShieldMastery = 'Shield Mastery | 실드 마스터리'
    Achilles = 'Achilles | 아킬레스'
    DivineShield = 'Divine Shield | 블래싱 아머'
    # 4th Job
    Blast = 'Blast | 블래스트'
    DivineCharge = 'Divine Charge | 디바인 차지'
    MagicCrash = 'Magic Crash | 매직 크래쉬'
    HeavensHammer = 'Heaven\'s Hammer | 생츄어리'
    ElementalForce = 'Elemental Force | 엘리멘탈 포스'
    PowerStance = 'Power Stance | 스탠스'
    Guardian = 'Guardian | 가디언 스피릿'
    HighPaladin = 'High Paladin | 팔라딘 엑스퍼트'
    AdvancedCharge = 'Advanced Charge | 어드밴스드 차지'
    # Hypers
    SmiteShield = 'Smite Shield | 스마이트'
    EpicAdventure = 'Epic Adventure | 에픽 어드벤처'
    Sacrosanctity = 'Sacrosanctity | 새크로생티티'
    # 5th Job
    DivineEcho = 'Divine Echo | 홀리 유니티'
    HammersoftheRighteous = 'Hammers of the Righteous | 블래스드 해머'
    GrandGuardian = 'Grand Guardian | 그랜드 크로스'
    MightyMjolnir = 'Mighty Mjolnir | 마이티 묠니르'


# The 4th skill should be written based on Combat Orders. 4차 스킬은 컴뱃오더스 적용 기준으로 작성해야 함.
class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "STR"
        self.jobname = "팔라딘"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2

    def get_ruleset(self):
        def use_soul_contract(soul_contract, grand_cross, holy_unity):
            if holy_unity.is_not_active():
                return False
            if grand_cross.is_usable() and holy_unity.is_time_left(9000, 1):  # I guessed it by force... Is there a way to make sure I use it right before it? 억지로 맞췄는데... 그크 직전에 정확히 쓰도록 해줄 방법이?
                return True
            return False

        def use_mighty_mjolnir(mjolnir, unity):
            if mjolnir.stack >= 2:
                return True
            if unity.is_not_active():
                return False
            return True

        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule(PaladinSkills.GrandGuardian.value, PaladinSkills.DivineEcho.value, lambda sk: sk.is_time_left(7000, 1)), RuleSet.BASE)
        ruleset.add_rule(ComplexConditionRule(GlobalSkills.TermsAndConditions.value, [PaladinSkills.GrandGuardian.value, PaladinSkills.DivineEcho.value], use_soul_contract), RuleSet.BASE)
        ruleset.add_rule(ComplexConditionRule(f'{PaladinSkills.MightyMjolnir.value}(Cast | 시전)', [PaladinSkills.DivineEcho.value], use_mighty_mjolnir), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(boss_pdamage=29, armor_ignore=18)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level
        PhisicalTraining = core.InformedCharacterModifier(PaladinSkills.PhysicalTraining.value, stat_main=30, stat_sub=30)
        ShieldMastery = core.InformedCharacterModifier(PaladinSkills.ShieldMastery.value, att=10)

        PaladinExpert = core.InformedCharacterModifier(
            f"{PaladinSkills.HighPaladin.value}(Two-handed blunt | 두손둔기)",
            crit_damage=5 + (32+passive_level) // 3,
            pdamage_indep=42+passive_level,
            crit=42+passive_level,
            armor_ignore=15+ceil((32+passive_level)/2),
        ) + core.ExtendedCharacterModifier(crit_damage=5, armor_ignore=10)
        PaladinExpert = core.InformedCharacterModifier.from_extended_modifier(f"{PaladinSkills.HighPaladin.value}(Two-handed blunt | 두손둔기)", PaladinExpert)
        return [PhisicalTraining, ShieldMastery, PaladinExpert]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=34)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep=-4.5 + 0.5*ceil(passive_level/2))  # Basic application of orders! 오더스 기본적용!

        ElementalCharge = core.InformedCharacterModifier(PaladinSkills.ElementalCharge.value, pdamage=25, att=60)  # The conditional application is reviewed later. 조건부 적용 여부는 추후검토.
        ParashockGuard = core.InformedCharacterModifier(PaladinSkills.ParashockGuard.value, att=20)

        return [WeaponConstant, Mastery, ElementalCharge, ParashockGuard]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Two-handed blunt

        Blae-Racha-Dicha-Saengchu-Pataek

        Blessing armor not applied.

        Blast-Reinforce, Bonus Attack / Sanctuary-Bonus Attack, Cooldown Reduce / Threat-Enhance

        두손둔기

        블래-라차-디차-생츄-파택

        블레싱 아머 미적용.

        블래스트-리인포스, 보너스 어택 / 생츄어리-보너스 어택, 쿨타임 리듀스 / 위협-인핸스
        '''
        buff_rem = chtr.get_base_modifier().buff_rem

        # Buff skills
        Threat = core.BuffSkill(PaladinSkills.Threaten.value, 1440, 80 * 1000, armor_ignore=30 + 20).wrap(core.BuffSkillWrapper)  # Default 1080, 75% probability reflected delay. 기본 1080, 75% 확률 반영 딜레이.
        # BlessingArmor = core.BuffSkill("블레싱 아머", 0, 30 * 1000, cooltime=90 * 1000, att=20, rem=True).wrap(core.BuffSkillWrapper)
        ElementalForce = core.BuffSkill(PaladinSkills.ElementalForce.value, 0, 206 * 1000, pdamage_indep=21, rem=True).wrap(core.BuffSkillWrapper)  # Pet buff. 펫버프.

        EpicAdventure = core.BuffSkill(PaladinSkills.EpicAdventure.value, 0, 60*1000, cooltime=120 * 1000, pdamage=10).wrap(core.BuffSkillWrapper)

        HolyUnity = (
            core.BuffSkill(
                PaladinSkills.DivineEcho.value,
                delay=600,
                remain=(40 + vEhc.getV(0, 0)) * 1000,
                cooltime=120 * 1000,
                red=True,
                pdamage_indep=int(35 + 0.5*vEhc.getV(0, 0)),
            )
            .isV(vEhc, 0, 0)
            .wrap(core.BuffSkillWrapper)
        )

        # Damage Skills
        LighteningCharge = core.DamageSkill(PaladinSkills.LightningCharge.value, 630, 462, 3+2, cooltime=60 * 1000 * (1 + buff_rem * 0.01)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)  # Consider the potential application of elemental charge. 엘리멘탈 차지의 벞지 적용 고려함.
        LighteningChargeDOT = core.DotSkill(f"{PaladinSkills.LightningCharge.value}(DoT | 도트)", 0, 1000, 115, 1, 6000, cooltime=-1).wrap(core.DotSkillWrapper)
        DivineCharge = core.DamageSkill(PaladinSkills.DivineCharge.value, 630, 462, 3+2, cooltime=60 * 1000 * (1 + buff_rem * 0.01)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        Sanctuary = core.DamageSkill(PaladinSkills.HeavensHammer.value, 750, 580, 8+2, cooltime=14 * 0.7 * 1000, red=True, modifier=core.CharacterModifier(boss_pdamage=30)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)

        Blast = core.DamageSkill(PaladinSkills.Blast.value, 630, 291, 9+2+1, modifier=core.CharacterModifier(pdamage=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        MightyMjollnirInit = core.StackableDamageSkillWrapper(core.DamageSkill(f"{PaladinSkills.MightyMjolnir.value}(Cast | 시전)", 630, 0, 0, cooltime=15000).isV(vEhc, 0, 0), 2)
        MightyMjollnir = core.DamageSkill(PaladinSkills.MightyMjolnir.value, 0, 225+9*vEhc.getV(0, 0), 6, cooltime=-1, modifier=core.CharacterModifier(crit=50)).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        MightyMjollnirWave = core.DamageSkill(f"{PaladinSkills.MightyMjolnir.value}(Shock wave | 충격파)", 0, 250+10*vEhc.getV(0, 0), 9, cooltime=-1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        # Summon Skills
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        BlessedHammer = core.SummonSkill(PaladinSkills.HammersoftheRighteous.value, 0, 600, 250 + vEhc.getV(1, 1)*10, 2, 999999 * 10000).isV(vEhc, 1, 1).wrap(core.SummonSkillWrapper)
        BlessedHammerActive = core.SummonSkill("Blessed Hammer | 블레스드 해머(Activation | 활성화)", 360, 600, 525+vEhc.getV(1, 1)*21, 3, 30 * 1000, cooltime=60 * 1000, red=True).isV(vEhc, 1, 1).wrap(core.SummonSkillWrapper)
        GrandCross = core.DamageSkill(PaladinSkills.GrandGuardian.value, 900, 0, 0, cooltime=150 * 1000, red=True).wrap(core.DamageSkillWrapper)
        GrandCrossSmallTick = core.DamageSkill(f"{PaladinSkills.GrandGuardian.value}(Small tick | 작은)", 200, 175 + vEhc.getV(3, 3)*7, 12, modifier=core.CharacterModifier(crit=100, armor_ignore=100)).isV(vEhc, 3, 3).wrap(core.DamageSkillWrapper)  # 3s, 15*6 strokes. 3s, 15*6타.
        GrandCrossLargeTick = core.DamageSkill(f"{PaladinSkills.GrandGuardian.value}(Large tick | 강화)", 146, 300 + vEhc.getV(3, 3)*12, 12, modifier=core.CharacterModifier(crit=100, armor_ignore=100)).isV(vEhc, 3, 3).wrap(core.DamageSkillWrapper)  # 6s, 41*6 strokes. 6s, 41*6타.
        GrandCrossEnd = core.DamageSkill(f"{PaladinSkills.GrandGuardian.value}(Ending | 종료)", 450, 0, 0).wrap(core.DamageSkillWrapper)

        FinalAttack = core.DamageSkill(PaladinSkills.FinalAttack.value, 0, 80, 2*0.4).setV(vEhc, 4, 5, True).wrap(core.DamageSkillWrapper)

        ######   Skill Wrapper   ######

        # Damage skill
        Blast.onAfter(FinalAttack)
        Sanctuary.onAfter(FinalAttack)
        LighteningCharge.onAfter(FinalAttack)
        LighteningCharge.onAfter(LighteningChargeDOT)
        DivineCharge.onAfter(FinalAttack)

        GrandCrossSmallTick.onAfter(FinalAttack)
        GrandCrossLargeTick.onAfter(FinalAttack)
        GrandCross.onAfters([GrandCrossEnd,
                            core.RepeatElement(GrandCrossLargeTick, 41),
                            core.RepeatElement(GrandCrossSmallTick, 15)])

        BlessedHammer.onTick(FinalAttack)
        BlessedHammerActive.onAfter(BlessedHammer.controller(99999999))
        BlessedHammerActive.onEventEnd(BlessedHammer)

        MightyMjollnirInit.onAfter(core.RepeatElement(MightyMjollnir, 4))
        MightyMjollnir.onAfter(MightyMjollnirWave)

        # Weapon Aura. 오라 웨폰.
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 2)
        for sk in [Blast, Sanctuary, GrandCrossSmallTick, GrandCrossLargeTick, MightyMjollnirInit]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        return(
            Blast,
            [
                globalSkill.maple_heros(chtr.level, combat_level=2),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_wind_booster(),
                Threat,
                ElementalForce,
                EpicAdventure,
                HolyUnity,
                AuraWeaponBuff,
                AuraWeapon,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                globalSkill.soul_contract()
            ] +
            [LighteningCharge, LighteningChargeDOT, DivineCharge, Sanctuary, MightyMjollnirInit, GrandCross, MirrorBreak, MirrorSpider] +
            [BlessedHammer, BlessedHammerActive] +
            [Blast]
        )
