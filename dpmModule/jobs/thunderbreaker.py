from .globalSkill import GlobalSkills
from .jobbranch.pirates import PirateSkills
from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import MutualRule, ReservationRule, RuleSet, ConcurrentRunRule
from . import globalSkill
from . import jobutils
from .jobbranch import pirates
from .jobclass import cygnus
from . import jobutils
from math import ceil
from typing import Any, Dict

import gettext
_ = gettext.gettext

# English skill information for Thunder Breaker here https://maplestory.fandom.com/wiki/Thunder_Breaker/Skills
class ThunderBreakerSkills:
    # Link Skill
    CygnusBlessing = _("시그너스 블레스")  # "Cygnus Blessing"
    # Beginner
    ElementalHarmony = _("엘리멘탈 하모니")  # "Elemental Harmony"
    ElementalExpert = _("엘리멘탈 엑스퍼트")  # "Elemental Expert"
    # 1st Job
    LightningPunch = _("충아")  # "Lightning Punch"
    Flash = _("섬광")  # "Flash"
    LightningElemental = _("엘리멘탈 : 라이트닝")  # "Lightning Elemental"
    Electrified = _("뇌인")  # "Electrified"
    # 2nd Job
    SharkSweep = _("회축")  # "Shark Sweep"
    TidalCrash = _("파도")  # "Tidal Crash"
    KnuckleBooster = _("너클 부스터")  # "Knuckle Booster"
    KnuckleMastery = _("너클 마스터리")  # "Knuckle Mastery"
    Gains = _("피지컬 트레이닝")  # "Gains"
    LightningBoost = _("뇌백")  # "Lightning Boost"
    # 3rd Job
    Ascension = _("승천")  # "Ascension"
    Thunder = _("뇌성")  # "Thunder"
    Gale = _("질풍")  # "Gale"
    Seawall = _("와류")  # "Seawall"
    Ironclad = _("극갑")  # "Ironclad"
    LinkMastery = _("연쇄")  # "Link Mastery"
    LightningLord = _("뇌제")  # "Lightning Lord"
    # 4th Job
    CallofCygnus = _("시그너스 나이츠")  # "Call of Cygnus"
    Annihilate = _("섬멸")  # "Annihilate"
    Thunderbolt = _("벽력")  # "Thunderbolt"
    Typhoon = _("태풍")  # "Typhoon"
    ArcCharger = _("축뢰")  # "Arc Charger"
    SpeedInfusion = _("윈드 부스터")  # "Speed Infusion"
    KnuckleExpert = _("너클 엑스퍼트")  # "Knuckle Expert"
    Electrify = _("자극")  # "Electrify"
    ThunderGod = _("뇌신")  # "Thunder God"
    # Hypers
    DeepRising = _("해신강림")  # "Deep Rising"
    GloryoftheGuardians = _("글로리 오브 가디언즈")  # "Glory of the Guardians"
    PrimalBolt = _("천지개벽")  # "Primal Bolt"
    # 5th Job
    LightningCascade = _("신뇌합일")  # "Lightning Cascade"
    SharkTorpedo = _("교아탄")  # "Shark Torpedo"
    LightningGodSpearStrike = _("뇌신창격")  # "Lightning God Spear Strike"
    LightningSpearMultistrike = _("창뇌연격")  # "Lightning Spear Multistrike"


# TODO : Added to the Haesin Advent damage cycle. 해신강림 딜사이클에 추가.
class LightningWrapper(core.StackSkillWrapper):
    def __init__(self, skill):
        super(LightningWrapper, self).__init__(skill, 5)
        self.stack = 5
        self.set_name_style(_("%d 만큼 뇌전 변화"))

    def get_modifier(self):
        return core.CharacterModifier(armor_ignore = self.stack * 9)

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "STR"
        self.jobname = _("스트라이커")
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore=43, pdamage=43)  # 뇌전 스택으로 평균 35~40%의 방무 적용 + 하이퍼

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ReservationRule(GlobalSkills.TermsAndConditions, _("{}(시전)").format(ThunderBreakerSkills.LightningSpearMultistrike)), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(_("{}(시전)").format(ThunderBreakerSkills.LightningSpearMultistrike), GlobalSkills.TermsAndConditions), RuleSet.BASE)
        ruleset.add_rule(MutualRule(ThunderBreakerSkills.PrimalBolt, _("{}(시전)").format(ThunderBreakerSkills.LightningSpearMultistrike)), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ElementalExpert = core.InformedCharacterModifier(ThunderBreakerSkills.ElementalExpert,stat_main = chtr.level // 2)
        ElementalHarmony = core.InformedCharacterModifier(ThunderBreakerSkills.ElementalHarmony,patt = 10)

        NoieBack = core.InformedCharacterModifier(ThunderBreakerSkills.LightningBoost,att = 20)
        PhisicalTraining = core.InformedCharacterModifier(ThunderBreakerSkills.Gains,stat_main = 60)
        
        Gekgap = core.InformedCharacterModifier(ThunderBreakerSkills.Ironclad,pdamage = 5)
        NoiGe = core.InformedCharacterModifier(ThunderBreakerSkills.LightningLord,att = 30)
        NuckleExpert = core.InformedCharacterModifier(ThunderBreakerSkills.KnuckleExpert,att = 30 + passive_level, crit_damage = 20 + passive_level // 2)
        NoiShin = core.InformedCharacterModifier(ThunderBreakerSkills.ThunderGod,crit = 30, crit_damage = 25)
        
        SkyOpenPassive = core.InformedCharacterModifier(_("{}(패시브)").format(ThunderBreakerSkills.PrimalBolt),pdamage_indep = 20)
        
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 1, 3)

        
        return [ElementalHarmony, ElementalExpert,
            NoieBack, PhisicalTraining, Gekgap, NoiGe, NuckleExpert, NoiShin,
            SkyOpenPassive, LoadedDicePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier(_("무기상수"),pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90+ceil(passive_level/2))
        
        return [WeaponConstant, Mastery]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Hyper: Flurry-Bonus Attack + Annihilation-Reinforce / Ignor Guard / Boss Killer + Wall Power-Bonus Attack

        Assume 100% linkage

        Heaven and Earth Gaebyeok ON: Typhoon-Annihilation
        Cheonjigaewall OFF: Wave-Annihilation

        Byeokseom: 1020ms
        Taesum: 900ms
        Parsum: 750ms

        Soul contract is used in conjunction with the window-brain attack
        It is used so that the wall of heaven and earth does not overlap

        하이퍼 : 질풍-보너스어택 + 섬멸-리인포스/이그노어 가드/보스킬러  + 벽력-보너스어택
        
        연계 100% 가정

        천지개벽 ON: 태풍 - 섬멸
        천지개벽 OFF: 파도 - 섬멸
        
        벽섬 : 1020ms
        태섬 : 900ms
        파섬 : 750ms
        
        소울 컨트랙트를 창뇌연격에 맞춰 사용
        천지개벽과 창뇌연격이 겹쳐지지 않게 사용
        '''
        DEALCYCLE = options.get('dealcycle', 'waterwave')

        passive_level = chtr.get_base_modifier().passive_level + self.combat
        CHOOKROI = 0.7 + 0.01*passive_level
        LINK_MASTERY = core.CharacterModifier(pdamage_indep = 20)
        #Buff skills

        Booster = core.BuffSkill(ThunderBreakerSkills.KnuckleBooster, 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        ChookRoi = core.BuffSkill(ThunderBreakerSkills.ArcCharger, 690, (180+5*self.combat)*1000, rem = True).wrap(core.BuffSkillWrapper)
        WindBooster = core.BuffSkill(ThunderBreakerSkills.SpeedInfusion, 0, (300+5*passive_level)*1000, rem = True).wrap(core.BuffSkillWrapper)
        HurricaneBuff = core.BuffSkill(_("{}(버프)").format(ThunderBreakerSkills.Typhoon), 0, (90+passive_level)*1000, rem = True, pdamage = 35).wrap(core.BuffSkillWrapper) # TODO: 뇌전 스택에 연동해야함
    
        LightningStack = LightningWrapper(core.BuffSkill(ThunderBreakerSkills.LightningElemental, 0, 99999999))

        Hurricane = core.DamageSkill(ThunderBreakerSkills.Typhoon, 420, 390+3*passive_level, 5+1).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        HurricaneConcat = core.DamageSkill(_("{}(연계)").format(ThunderBreakerSkills.Typhoon), 420, 390+3*passive_level, 5+1, modifier = LINK_MASTERY).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        
        Destroy = core.DamageSkill(ThunderBreakerSkills.Annihilate, 480, 350 + 4*self.combat, 7, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Thunder = core.DamageSkill(ThunderBreakerSkills.Thunderbolt, 540, 320 + 4*self.combat, 5 + 1).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        WaterWave = core.DamageSkill(ThunderBreakerSkills.TidalCrash, 270, 255, 2).setV(vEhc, 1, 5, False).wrap(core.DamageSkillWrapper)
        DestroyConcat = core.DamageSkill(_("{}(연계)").format(ThunderBreakerSkills.Annihilate), 480, 350 + 4*self.combat, 7, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20) + LINK_MASTERY).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        ThunderConcat = core.DamageSkill(_("{}(연계)").format(ThunderBreakerSkills.Thunderbolt), 540, 320 + 4*self.combat, 5 + 1, modifier = LINK_MASTERY).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)   # Linked Final Damage 20%. 연계최종뎀 20%.
        WaterWaveConcat = core.DamageSkill(_("{}(연계)").format(ThunderBreakerSkills.TidalCrash), 270, 255, 2, modifier = LINK_MASTERY).setV(vEhc, 1, 5, False).wrap(core.DamageSkillWrapper)
        WaterWaveConcatCancel = core.DamageSkill(_("{}(연계)(캔슬)").format(ThunderBreakerSkills.TidalCrash), 60+60, 255, 2, modifier = LINK_MASTERY).setV(vEhc, 1, 5, False).wrap(core.DamageSkillWrapper)

        # Hyper. 하이퍼.
        # Need to add delay. 딜레이 추가 필요.
        SkyOpen = core.BuffSkill(ThunderBreakerSkills.PrimalBolt, 0, 30*1000, cooltime = 120*1000).wrap(core.BuffSkillWrapper)
        
        GloryOfGuardians = core.BuffSkill(ThunderBreakerSkills.GloryoftheGuardians, 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        CygnusPhalanx = cygnus.PhalanxChargeWrapper(vEhc, 4, 4)
        LuckyDice = core.BuffSkill(PirateSkills.LoadedDice, 0, 180*1000, pdamage = 20).isV(vEhc,1,3).wrap(core.BuffSkillWrapper)

        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        ShinNoiHapL = core.BuffSkill(ThunderBreakerSkills.LightningCascade, 540, (30+vEhc.getV(3,2)//2) * 1000, red = True, cooltime = (120-vEhc.getV(3,2)//2)*1000, pdamage_indep=5+vEhc.getV(3,2)//6).isV(vEhc,3,2).wrap(core.BuffSkillWrapper)
        ShinNoiHapLAttack = core.SummonSkill(_("{}(공격)").format(ThunderBreakerSkills.LightningCascade), 0, 3000, 16*vEhc.getV(3,2) + 400, 7, (30+vEhc.getV(3,2)//2) * 1000, cooltime = -1).isV(vEhc,3,2).wrap(core.SummonSkillWrapper)
        ShinNoiHapLAttack_ChookRoi = core.DamageSkill(f"{ThunderBreakerSkills.LightningCascade}({ThunderBreakerSkills.ArcCharger})", 0, (16*vEhc.getV(3,2) + 400) * CHOOKROI, 7 ).wrap(core.DamageSkillWrapper)
        ShinNoiHapLPassive = core.DamageSkill(_("{}(패시브)").format(ThunderBreakerSkills.LightningCascade), 0, 16 * vEhc.getV(3, 2) + 400, 7, cooltime=6000).wrap(core.DamageSkillWrapper)
        GioaTan = core.DamageSkill(ThunderBreakerSkills.SharkTorpedo, 360, 1000+40*vEhc.getV(2,1), 7, cooltime = 8000, red = True, modifier = LINK_MASTERY).isV(vEhc,2,1).wrap(core.DamageSkillWrapper)  # Uses the Kyo-Atan-Break Power combo. 교아탄-벽력 콤보 사용함.

        NoiShinChanGeuk = core.DamageSkill(ThunderBreakerSkills.LightningGodSpearStrike, 0, 150+6*vEhc.getV(0,0), 6, cooltime = 7000, red = True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        NoiShinChanGeukAttack = core.SummonSkill(_("{}(후속타)").format(ThunderBreakerSkills.LightningGodSpearStrike), 0, 1000, 200 + 8*vEhc.getV(0,0), 7, 3999, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)    # Act 4 times. 4번 발동.
        NoiShinChanGeukAttack_ChookRoi = core.DamageSkill(_("{}(후속타)({})").format(ThunderBreakerSkills.LightningGodSpearStrike, ThunderBreakerSkills.ArcCharger), 0, (200 + 8*vEhc.getV(0,0)) * CHOOKROI, 7).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)

        SpearLightningAttackInit = core.DamageSkill(_("{}(시전)").format(ThunderBreakerSkills.LightningSpearMultistrike), 0, 0, 0, cooltime=120*1000, red=True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)  # It's a stack-saving skill like throw blasting, but it's just handled with a 12 repetition extreme deal. 스로우 블래스팅같은 스택 저장형 스킬이지만... 그냥 12회 반복되는 극딜기로 처리.
        SpearLightningAttack = core.DamageSkill(ThunderBreakerSkills.LightningSpearMultistrike, 240, 375+15*vEhc.getV(0,0), 5, cooltime=-1, modifier = LINK_MASTERY).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        SpearLightningAttack_Lightning = core.DamageSkill(_("{}(번개)").format(ThunderBreakerSkills.LightningSpearMultistrike), 0, 500+20*vEhc.getV(0,0), 4, cooltime=-1, modifier = LINK_MASTERY).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        SpearLightningAttack_Final = core.DamageSkill(_("{}(막타)").format(ThunderBreakerSkills.LightningSpearMultistrike), 450, 600+24*vEhc.getV(0,0), 7, cooltime=-1, modifier = LINK_MASTERY).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        SpearLightningAttack_Final_Lightning = core.DamageSkill(_("{}(막타)(번개)").format(ThunderBreakerSkills.LightningSpearMultistrike), 0, 725+29*vEhc.getV(0,0), 6, cooltime=-1, modifier = LINK_MASTERY).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)

        # Annihilation linkage (default). 섬멸 연계 (default).
        WaterWaveDestroy = core.GraphElement(_("파섬"))
        WaterWaveDestroy.onAfter(WaterWaveConcat)
        WaterWaveDestroy.onAfter(DestroyConcat)
        HurricaneDestroy = core.GraphElement(_("태섬"))
        HurricaneDestroy.onAfter(HurricaneConcat)
        HurricaneDestroy.onAfter(DestroyConcat)

        # Destruction connection (optional). 섬멸 연계 (optional).
        ThunderDestroy = core.GraphElement(_("벽섬"))
        ThunderDestroy.onAfter(ThunderConcat)
        ThunderDestroy.onAfter(DestroyConcat)
        WaterWaveCancelDestroy = core.GraphElement(_("파파섬"))
        WaterWaveCancelDestroy.onAfter(WaterWaveConcatCancel)
        WaterWaveCancelDestroy.onAfter(Destroy)
        WaterWaveCancelHurricane = core.GraphElement(_("파파태"))
        WaterWaveCancelHurricane.onAfter(WaterWaveConcatCancel)
        WaterWaveCancelHurricane.onAfter(Hurricane)

        if DEALCYCLE == "waterwave":
            BasicAttack = core.OptionalElement(SkyOpen.is_active, HurricaneDestroy, WaterWaveDestroy)
        elif DEALCYCLE == "thunder":
            BasicAttack = core.OptionalElement(SkyOpen.is_active, HurricaneDestroy, ThunderDestroy)
        else:
            raise ValueError(DEALCYCLE)

        BasicAttackWrapper = core.DamageSkill(_("기본 공격"), 0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)
        
        for skill in [Destroy, Thunder, WaterWave, DestroyConcat, ThunderConcat, WaterWaveConcat, WaterWaveConcatCancel, Hurricane, HurricaneConcat, GioaTan, NoiShinChanGeuk,
                        SpearLightningAttack, SpearLightningAttack_Lightning, SpearLightningAttack_Final, SpearLightningAttack_Final_Lightning]:
            jobutils.create_auxilary_attack(skill, CHOOKROI, nametag=f"({ThunderBreakerSkills.ArcCharger})")

        for skill in [Thunder, ThunderConcat, WaterWave, WaterWaveConcat, NoiShinChanGeuk,
                        ShinNoiHapLPassive, SpearLightningAttack, SpearLightningAttack_Final]:
            skill.onAfter(LightningStack.stackController(1))

        for skill in [ShinNoiHapLAttack, CygnusPhalanx, NoiShinChanGeukAttack]:
            skill.onTick(LightningStack.stackController(1))

        GioaTan.onAfter(core.OptionalElement(SkyOpen.is_not_active, LightningStack.stackController(-2), name=_("{} 체크").format(ThunderBreakerSkills.PrimalBolt)))
        
        ShinNoiHapLAttack.onTick(ShinNoiHapLAttack_ChookRoi)
        NoiShinChanGeukAttack.onTick(NoiShinChanGeukAttack_ChookRoi)
        
        ShinNoiHapL.onAfter(ShinNoiHapLAttack)
        #GioaTan.onAfter(DestroyConcat) # TODO: Including Gyoatan in BasicAttack and running. 교아탄을 BasicAttack에 포함해서 돌릴것.
        NoiShinChanGeuk.onAfter(NoiShinChanGeukAttack)

        SpearLightningAttack.onAfter(SpearLightningAttack_Lightning)
        SpearLightningAttack_Final.onAfter(core.RepeatElement(SpearLightningAttack_Final_Lightning, 3))
        SpearLightningAttackInit.onAfter(core.RepeatElement(SpearLightningAttack, 11))
        SpearLightningAttackInit.onAfter(SpearLightningAttack_Final)

        ShinNoiHapLPassive.onConstraint(core.ConstraintElement(f"{ThunderBreakerSkills.LightningCascade} OFF", ShinNoiHapL, ShinNoiHapL.is_not_active))

        return(BasicAttackWrapper,
                [globalSkill.maple_heros(chtr.level, name=ThunderBreakerSkills.CallofCygnus, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    LightningStack, Booster, ChookRoi, WindBooster, LuckyDice,
                    HurricaneBuff, GloryOfGuardians, SkyOpen, Overdrive, ShinNoiHapL, cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level),
                    globalSkill.soul_contract()] +\
                [GioaTan, CygnusPhalanx, NoiShinChanGeuk, SpearLightningAttackInit, MirrorBreak, MirrorSpider] +\
                [ShinNoiHapLAttack, NoiShinChanGeukAttack] +\
                [] +\
                [BasicAttackWrapper])