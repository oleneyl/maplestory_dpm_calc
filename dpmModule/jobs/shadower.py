from .jobbranch.thieves import ThiefSkills
from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import thieves
from . import jobutils
from math import ceil
from typing import Any, Dict
from .globalSkill import PASSIVE, TICK, ONE_HIT, TWO_HIT

from localization.utilities import translator
_ = translator.gettext

# English skill information for Shadower here https://maplestory.fandom.com/wiki/Shadower/Skills
class ShadowerSkills:
    # Link Skill
    ThiefsCunning = _("시프 커닝")  # "Thief's Cunning"
    # 1st Job
    DoubleStab = _("더블 스탭")  # "Double Stab"
    LuckySeven = _("럭키 세븐")  # "Lucky Seven"
    Haste = _("헤이스트")  # "Haste"
    DarkSight = _("다크사이트")  # "Dark Sight"
    FlashJump = _("플래시 점프")  # "Flash Jump"
    NimbleBody = _("님블 바디")  # "Nimble Body"
    # 2nd Job
    SavageBlow = _("새비지 블로우")  # "Savage Blow"
    CriticalGrowth = _("크리티컬 그로잉")  # "Critical Growth"
    Steal = _("스틸")  # "Steal"
    DaggerBooster = _("대거 부스터")  # "Dagger Booster"
    Mesoguard = _("메소 가드")  # "Mesoguard"
    ChannelKarma = _("카르마")  # "Channel Karma"
    DaggerMastery = _("대거 마스터리")  # "Dagger Mastery"
    PhysicalTraining = _("피지컬 트레이닝")  # "Physical Training"
    ShieldMastery = _("실드 마스터리")  # "Shield Mastery"
    # 3rd Job
    MidnightCarnival = _("엣지 카니발")  # "Midnight Carnival"
    PhaseDash = _("무스펠 하임")  # "Phase Dash"
    MesoExplosion = _("메소 익스플로전")  # "Meso Explosion"
    DarkFlare = _("다크 플레어")  # "Dark Flare"
    PickPocket = _("픽파킷")  # "Pick Pocket"
    ShadowPartner = _("섀도우 파트너")  # "Shadow Partner"
    Venom = _("베놈")  # "Venom"
    MesoMastery = _("그리드")  # "Meso Mastery"
    EnvelopingDarkness = _("래디컬 다크니스")  # "Enveloping Darkness"
    AdvancedDarkSight = _("어드밴스드 다크 사이트")  # "Advanced Dark Sight"
    IntoDarkness = _("인투 다크니스")  # "Into Darkness"
    # 4th Job
    Assassinate = _("암살")  # "Assassinate"
    BoomerangStab = _("부메랑 스텝")  # "Boomerang Stab"
    PrimeCritical = _("프리마 크리티컬")  # "Prime Critical"
    SuddenRaid = _("써든레이드")  # "Sudden Raid"
    Smokescreen = _("연막탄")  # "Smokescreen"
    ShadowerInstinct = _("섀도어 인스팅트")  # "Shadower Instinct"
    ShadowShifter = _("페이크")  # "Shadow Shifter"
    ToxicVenom = _("페이탈 베놈")  # "Toxic Venom"
    DaggerExpert = _("대거 엑스퍼트")  # "Dagger Expert"
    # Hypers
    ShadowVeil = _("베일 오브 섀도우")  # "Shadow Veil"
    EpicAdventure = _("에픽 어드벤처")  # "Epic Adventure"
    FlipoftheCoin = _("플립 더 코인")  # "Flip of the Coin"
    # 5th Job
    ShadowAssault = _("쉐도우 어썰트")  # "Shadow Assault"
    Trickblade = _("절개")  # "Trickblade"
    SonicBlow = _("소닉 블로우")  # "Sonic Blow"
    SlashShadowFormation = _("멸귀참영진")  # "Slash Shadow Formation"


# Skill name modifiers for shadower only
CAPTAIN = _("우두머리")


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "LUK2"
        self.jobname = _("섀도어")
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=102, armor_ignore=26.8, crit_damage=5)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        NimbleBody = core.InformedCharacterModifier(ShadowerSkills.NimbleBody, stat_main=20)
        Karma = core.InformedCharacterModifier(ShadowerSkills.ChannelKarma, att=30)
        PhisicalTraining = core.InformedCharacterModifier(ShadowerSkills.PhysicalTraining, stat_main=30, stat_sub=30)
        SheildMastery = core.InformedCharacterModifier(ShadowerSkills.ShieldMastery, att=15)
        Grid = core.InformedCharacterModifier(ShadowerSkills.MesoMastery, att=5)
        
        PrimaCriticalPassive = core.InformedCharacterModifier(f"{ShadowerSkills.PrimeCritical}({PASSIVE})", stat_main=10, crit_damage=20)
        PrimaCritical = core.InformedCharacterModifier(ShadowerSkills.PrimeCritical, crit_damage=8.33)  # Can also be calculated stacked. 150/18 = 8.33... 스택식으로도 계산 가능. 150 / 18 = 8.33...
        
        BoomerangStepPassive = core.InformedCharacterModifier(f"{ShadowerSkills.BoomerangStab}({PASSIVE})", pdamage_indep=25+2*(self.combat//3))
        
        ShadowerInstinctPassive = core.InformedCharacterModifier(f"{ShadowerSkills.ShadowerInstinct}({PASSIVE})", armor_ignore=20 + self.combat)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 2, 2)
    
        DaggerExpert = core.InformedCharacterModifier(ShadowerSkills.DaggerExpert, att=40 + passive_level, crit_damage=15 + passive_level//3)

        return [NimbleBody, Karma,
                PhisicalTraining, SheildMastery, Grid, PrimaCriticalPassive,
                PrimaCritical, BoomerangStepPassive, ShadowerInstinctPassive, ReadyToDiePassive, DaggerExpert]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep=30)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90+ceil(passive_level/2))    # Basic application of orders! 오더스 기본적용!

        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Normal dark sites are not used as gangs.

        Prima Critical Cdem: 8.33%
        Shadow partner only applies to incision, assassination, and sonic blow.

        Hyper: Meic Enhance, Assassination Reinforce / Vokill / Ignor Guard.

        Killing Points 3 Stack Chance 1 hit 94.6% / 2 hits 100%
        Assassination-Single-Make-Beosha

        일반 다크사이트는 깡으로 사용하지 않음.

        프리마 크리티컬 크뎀 : 8.33%
        쉐도우 파트너는 절개, 암살, 소닉 블로우에만 적용.

        하이퍼 : 메익 인핸스, 암살 리인포스 / 보킬 / 이그노어 가드.

        킬링 포인트 3스택 확률 1타 94.6% / 2타 100%
        암살-닼플-메익-배오섀
        '''

        ######   Skill   ######
        # http://m.inven.co.kr/board/powerbbs.php?come_idx=2297&stype=subject&svalue=%EC%8A%A4%ED%83%9D&l=52201

        # 1 hit 94.6%, 2 hits 100%. 1타 94.6%, 2타 100%.
        # Croa Server Skinhead. 크로아 서버 스킨헤드님.
        # https://drive.google.com/file/d/1ORJc-F77ELssCSVWgHiuQP49pifgCjpo/view

        passive_level = chtr.get_base_modifier().passive_level + self.combat

        STACK1RATE = 94.6
        STACK2RATE = 100

        #Buff skills
        Booster = core.BuffSkill(ShadowerSkills.DaggerBooster, 0, 200*1000, rem=True).wrap(core.BuffSkillWrapper)
        FlipTheCoin = core.BuffSkill(ShadowerSkills.FlipoftheCoin, 0, 120*1000, pdamage=5*5, crit=10*5).wrap(core.BuffSkillWrapper)
        ShadowerInstinct = core.BuffSkill(ShadowerSkills.ShadowerInstinct, 900, (200+6*self.combat)*1000, rem=True, att=40+30+2*self.combat).wrap(core.BuffSkillWrapper)
        # StealPotion = core.BuffSkill(f"{ShadowerSkills.Steal}({_('포션')})", 0, 180000, cooltime=-1, att=30).wrap(core.BuffSkillWrapper)
        
        ShadowPartner = core.BuffSkill(ShadowerSkills.ShadowPartner, 0, 2000*1000, rem=True).wrap(core.BuffSkillWrapper)
        
        # When using 3 kills, the final damage is increased by 100%. 킬포3개 사용시 최종뎀 100% 증가.
        Assasinate1 = core.DamageSkill(f"{ShadowerSkills.Assassinate}({ONE_HIT})", 630, 275+4*self.combat, 6, modifier=core.CharacterModifier(pdamage=20, boss_pdamage=20, armor_ignore=10, pdamage_indep=STACK1RATE)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)   # ??. 쉐파.
        Assasinate2 = core.DamageSkill(f"{ShadowerSkills.Assassinate}({TWO_HIT})", 420, 350+5*self.combat, 6, modifier=core.CharacterModifier(pdamage=20, boss_pdamage=20, armor_ignore=10, pdamage_indep=STACK2RATE)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)   # ??. 쉐파.
        
        Assasinate1_D = core.DamageSkill(f"{ShadowerSkills.Assassinate}({ONE_HIT})({ShadowerSkills.DarkSight})", 630, 275+4*self.combat, 6, modifier=core.CharacterModifier(pdamage=20+150+4*self.combat, boss_pdamage=20, armor_ignore=10, pdamage_indep=STACK1RATE)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)   # ??. 쉐파.
        Assasinate2_D = core.DamageSkill(f"{ShadowerSkills.Assassinate}({TWO_HIT})({ShadowerSkills.DarkSight})", 420, 350+5*self.combat, 6, modifier=core.CharacterModifier(pdamage=20+150+4*self.combat, boss_pdamage=20, armor_ignore=10, pdamage_indep=STACK2RATE)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)   # ??. 쉐파.

        MesoStack = core.StackSkillWrapper(core.BuffSkill(ShadowerSkills.PickPocket, 0, 9999999), 20)
        MesoExplosion = core.StackDamageSkillWrapper(core.DamageSkill(ShadowerSkills.MesoExplosion, 0, 120, 2).setV(vEhc, 2, 3, False), MesoStack, lambda skill: skill.stack)
        
        BailOfShadow = core.SummonSkill(ShadowerSkills.ShadowVeil, 900 + 120, 12000 / 14, 800, 1, 12*1000, cooltime=60000).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)  # Dark sight delay summation. 다크 사이트 딜레이 합산.

        DarkFlare = core.SummonSkill(ShadowerSkills.DarkFlare, 600, 60000 / 62, 360, 1, 60*1000, cooltime=60000, red=True, rem=True).setV(vEhc, 1, 3, False).wrap(core.SummonSkillWrapper)
    
        Smoke = core.BuffSkill(ShadowerSkills.Smokescreen, 900 + 120, 30000, cooltime=(150-2*self.combat)*1000, crit_damage=20+ceil(self.combat/3), red=True).wrap(core.BuffSkillWrapper)  # Dark sight delay summation. 다크 사이트 딜레이 합산.
        Venom = core.DotSkill(ShadowerSkills.ToxicVenom, 0, 1000, 160+5*passive_level, 2+(10+passive_level)//6, 89999 * 1000).wrap(core.DotSkillWrapper)
        
        AdvancedDarkSight = core.BuffSkill(ShadowerSkills.AdvancedDarkSight, 0, 10000, cooltime=-1, pdamage_indep=5).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill(ShadowerSkills.EpicAdventure, 0, 60*1000, cooltime=120 * 1000, pdamage=10).wrap(core.BuffSkillWrapper)

        '''
        Steal = core.DamageSkill("스틸", 600, 330, 1, cooltime=180000).isV(?, ?).wrap(core.DamageSkillWrapper)
        Steal.onAfter(StealPotion)
        '''
        UltimateDarksight = core.BuffSkill(
            ThiefSkills.ShadowWalker,
            delay=750,
            remain=30000,
            cooltime=(220-vEhc.getV(3, 3))*1000,
            pdamage_indep=(100 + 10 + 5 + vEhc.getV(3, 3)//5) / (100 + 5) * 100 - 100,
            red=True
        ).isV(vEhc, 3, 3).wrap(core.BuffSkillWrapper)

        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 2, 2)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        Eviscerate = core.DamageSkill(ShadowerSkills.Trickblade, 570, 475+19*vEhc.getV(0, 0), 7*4, modifier=core.CharacterModifier(crit=100, armor_ignore=100), cooltime=14000, red=True).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper) # 720ms - 150ms(암살 2타연계)

        # Patch 1.2.324 applied. 1.2.324 패치 적용.
        SonicBlow = core.DamageSkill(ShadowerSkills.SonicBlow, 900, 0, 0, cooltime=80 * 1000, red=True).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)
        SonicBlowTick = core.DamageSkill(f"{ShadowerSkills.SonicBlow}({TICK})", 107, 500+20*vEhc.getV(1, 1), 7, modifier=core.CharacterModifier(armor_ignore=100)).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper, name="소닉 블로우(사용)") # 7 * 15

        ShadowFormation = core.SummonSkill(ShadowerSkills.SlashShadowFormation, 0, 8000/12, 425+17*vEhc.getV(0, 0), 8, 8000-1, cooltime=90000, red=True, modifier=core.CharacterModifier(armor_ignore=20)).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)
        ShadowFormationFinal = core.DamageSkill(f"{ShadowerSkills.SlashShadowFormation}({CAPTAIN})", 0, 625+25*vEhc.getV(0, 0), 15*4, cooltime=-1, modifier=core.CharacterModifier(armor_ignore=20)).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        
        ### build graph relationships
        def isNotDarkSight():
            return (not AdvancedDarkSight.is_active())
        
        AdvancedDarkSight.set_disabled_and_time_left(-1)
        DarkSightTurnedOn = core.ConstraintElement(_("{} 여부 확인").format(ShadowerSkills.DarkSight), AdvancedDarkSight, isNotDarkSight)

        MesoExplosion.onJustAfter(MesoStack.stackController(-20, name = _("메소 제거")))
        
        Assasinate2.onAfters([SonicBlow.controller(1500 * STACK2RATE * 0.01, "reduce_cooltime"), MesoStack.stackController(6*2*0.4, name = _("메소 생성"))])
        Assasinate1.onAfter(MesoStack.stackController(6*2*0.4, name = _("메소 생성")))
        Assasinate1.onAfter(MesoExplosion)
        Assasinate1.onAfter(Assasinate2)
        
        Assasinate2_D.onAfters([SonicBlow.controller(1500 * STACK2RATE * 0.01, "reduce_cooltime"), MesoStack.stackController(6*2*0.4, name = _("메소 생성"))])
        Assasinate1_D.onAfter(MesoStack.stackController(6*2*0.4, name = _("메소 생성")))
        Assasinate1_D.onAfter(MesoExplosion)
        Assasinate1_D.onAfter(Assasinate2_D)

        BailOfShadow.onConstraint(DarkSightTurnedOn)
        BailOfShadow.onTick(MesoStack.stackController(0.4, name = _("메소 생성")))
        BailOfShadow.onAfter(AdvancedDarkSight.controller(12000, "set_enabled_and_time_left"))

        Smoke.onConstraint(DarkSightTurnedOn)
        Smoke.onAfter(AdvancedDarkSight.controller(30000, "set_enabled_and_time_left"))

        UltimateDarksight.onConstraint(DarkSightTurnedOn)
        UltimateDarksight.onAfter(AdvancedDarkSight.controller(30000, "set_enabled_and_time_left" ))
        
        SonicBlowTick.onAfter(MesoStack.stackController(7*2*0.4, name = _("메소 생성")))
        SonicBlow.onAfter(core.RepeatElement(SonicBlowTick, 15))
        
        UseEviscerate = core.OptionalElement(Eviscerate.is_available, Eviscerate, name=_("{} 연계 여부").format(ShadowerSkills.Trickblade))
        Assasinate2.onAfter(UseEviscerate)
        Assasinate2_D.onAfter(UseEviscerate)
        Eviscerate.onAfter(MesoStack.stackController(7*2*0.4, name = _("메소 생성")))
        Eviscerate.protect_from_running()

        ShadowFormation.onEventEnd(ShadowFormationFinal)
        
        Assasinate = core.OptionalElement(AdvancedDarkSight.is_active, Assasinate1_D, Assasinate1, name = _("닼사 여부"))
        BasicAttackWrapper = core.DamageSkill(_("기본 공격"), 0, 0, 0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(Assasinate)

        for sk in [Assasinate1, Assasinate2, Assasinate1_D, Assasinate2_D, Eviscerate, SonicBlowTick]:
            jobutils.create_auxilary_attack(sk, 0.7, nametag=f"({ShadowerSkills.ShadowPartner})")
        
        return(
            BasicAttackWrapper,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                Booster, FlipTheCoin, ShadowerInstinct, ShadowPartner, Smoke, AdvancedDarkSight, EpicAdventure, UltimateDarksight, MesoStack,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), ReadyToDie, globalSkill.soul_contract()
            ]
            + [ShadowFormation, ShadowFormationFinal, Eviscerate, SonicBlow, BailOfShadow, DarkFlare, MirrorBreak, MirrorSpider]
            + [Venom]
            + [BasicAttackWrapper]
        )