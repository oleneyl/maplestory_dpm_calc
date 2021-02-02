from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import ComplexConditionRule, ConditionRule, RuleSet
from . import globalSkill
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict


# 4차 스킬은 컴뱃오더스 적용 기준으로 작성해야 함.
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
            if grand_cross.is_usable() and holy_unity.is_time_left(9000, 1):  # 억지로 맞췄는데... 그크 직전에 정확히 쓰도록 해줄 방법이?
                return True
            return False

        def use_mighty_mjolnir(mjolnir, unity):
            if mjolnir.stack >= 2:
                return True
            if unity.is_not_active():
                return False
            return True

        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule('그랜드 크로스', '홀리 유니티', lambda sk: sk.is_time_left(7000, 1)), RuleSet.BASE)
        ruleset.add_rule(ComplexConditionRule('소울 컨트랙트', ['그랜드 크로스', '홀리 유니티'], use_soul_contract), RuleSet.BASE)
        ruleset.add_rule(ComplexConditionRule('마이티 묠니르(시전)', ['홀리 유니티'], use_mighty_mjolnir), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(boss_pdamage=29, armor_ignore=18)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝", stat_main=30, stat_sub=30)
        ShieldMastery = core.InformedCharacterModifier("실드 마스터리", att=10)

        PaladinExpert = core.InformedCharacterModifier(
            "팔라딘 엑스퍼트(두손둔기)",
            crit_damage=5 + (32+passive_level) // 3,
            pdamage_indep=42+passive_level,
            crit=42+passive_level,
            armor_ignore=15+ceil((32+passive_level)/2),
        ) + core.ExtendedCharacterModifier(crit_damage=5, armor_ignore=10)
        PaladinExpert = core.InformedCharacterModifier.from_extended_modifier("팔라딘 엑스퍼트(두손둔기)", PaladinExpert)
        return [PhisicalTraining, ShieldMastery, PaladinExpert]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=34)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep=-4.5 + 0.5*ceil(passive_level/2))  # 오더스 기본적용!

        ElementalCharge = core.InformedCharacterModifier("엘리멘탈 차지", pdamage=25, att=60)  # 조건부 적용 여부는 추후검토.
        ParashockGuard = core.InformedCharacterModifier("파라쇼크 가드", att=20)

        return [WeaponConstant, Mastery, ElementalCharge, ParashockGuard]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        두손둔기

        블래-라차-디차-생츄-파택

        블레싱 아머 미적용.

        블래스트-리인포스, 보너스 어택 / 생츄어리-보너스 어택, 쿨타임 리듀스 / 위협-인핸스
        '''
        buff_rem = chtr.get_base_modifier().buff_rem

        # Buff skills
        Threat = core.BuffSkill("위협", 1440, 80 * 1000, armor_ignore=30 + 20).wrap(core.BuffSkillWrapper)  # 기본 1080, 75% 확률 반영 딜레이
        # BlessingArmor = core.BuffSkill("블레싱 아머", 0, 30 * 1000, cooltime=90 * 1000, att=20, rem=True).wrap(core.BuffSkillWrapper)
        ElementalForce = core.BuffSkill("엘리멘탈 포스", 0, 206 * 1000, pdamage_indep=21, rem=True).wrap(core.BuffSkillWrapper)  # 펫버프

        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime=120 * 1000, pdamage=10).wrap(core.BuffSkillWrapper)

        HolyUnity = (
            core.BuffSkill(
                "홀리 유니티",
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
        LighteningCharge = core.DamageSkill("라이트닝 차지", 630, 462, 3+2, cooltime=60 * 1000 * (1 + buff_rem * 0.01)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)  # 엘리멘탈 차지의 벞지 적용 고려함
        LighteningChargeDOT = core.DotSkill("라이트닝 차지(도트)", 0, 1000, 115, 1, 6000, cooltime=-1).wrap(core.DotSkillWrapper)
        DivineCharge = core.DamageSkill("디바인 차지", 630, 462, 3+2, cooltime=60 * 1000 * (1 + buff_rem * 0.01)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        Sanctuary = core.DamageSkill("생츄어리", 750, 580, 8+2, cooltime=14 * 0.7 * 1000, red=True, modifier=core.CharacterModifier(boss_pdamage=30)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)

        Blast = core.DamageSkill("블래스트", 630, 291, 9+2+1, modifier=core.CharacterModifier(pdamage=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        MightyMjollnirInit = core.StackableDamageSkillWrapper(core.DamageSkill("마이티 묠니르(시전)", 630, 0, 0, cooltime=15000).isV(vEhc, 0, 0), 2)
        MightyMjollnir = core.DamageSkill("마이티 묠니르", 0, 225+9*vEhc.getV(0, 0), 6, cooltime=-1, modifier=core.CharacterModifier(crit=50)).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        MightyMjollnirWave = core.DamageSkill("마이티 묠니르(충격파)", 0, 250+10*vEhc.getV(0, 0), 9, cooltime=-1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        # Summon Skills
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        BlessedHammer = core.SummonSkill("블래스드 해머", 0, 600, 250 + vEhc.getV(1, 1)*10, 2, 999999 * 10000).isV(vEhc, 1, 1).wrap(core.SummonSkillWrapper)
        BlessedHammerActive = core.SummonSkill("블레스드 해머(활성화)", 360, 600, 525+vEhc.getV(1, 1)*21, 3, 30 * 1000, cooltime=60 * 1000, red=True).isV(vEhc, 1, 1).wrap(core.SummonSkillWrapper)
        GrandCross = core.DamageSkill("그랜드 크로스", 900, 0, 0, cooltime=150 * 1000, red=True).wrap(core.DamageSkillWrapper)
        GrandCrossSmallTick = core.DamageSkill("그랜드 크로스(작은)", 200, 175 + vEhc.getV(3, 3)*7, 12, modifier=core.CharacterModifier(crit=100, armor_ignore=100)).isV(vEhc, 3, 3).wrap(core.DamageSkillWrapper)  # 3s, 15*6타
        GrandCrossLargeTick = core.DamageSkill("그랜드 크로스(강화)", 146, 300 + vEhc.getV(3, 3)*12, 12, modifier=core.CharacterModifier(crit=100, armor_ignore=100)).isV(vEhc, 3, 3).wrap(core.DamageSkillWrapper)  # 6s, 41*6타
        GrandCrossEnd = core.DamageSkill("그랜드 크로스(종료)", 450, 0, 0).wrap(core.DamageSkillWrapper)

        FinalAttack = core.DamageSkill("파이널 어택", 0, 80, 2*0.4).setV(vEhc, 4, 5, True).wrap(core.DamageSkillWrapper)

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

        # 오라 웨폰
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
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, combat_level=2),
                globalSkill.soul_contract()
            ] +
            [LighteningCharge, LighteningChargeDOT, DivineCharge, Sanctuary, MightyMjollnirInit, GrandCross, MirrorBreak, MirrorSpider] +
            [BlessedHammer, BlessedHammerActive] +
            [Blast]
        )
