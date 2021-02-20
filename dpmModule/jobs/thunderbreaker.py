from enum import Enum

from .globalSkill import GlobalSkills
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


# English skill information for Thunder Breaker here https://maplestory.fandom.com/wiki/Thunder_Breaker/Skills
class ThunderBreakerSkills(Enum):
    # Link Skill
    CygnusBlessing = 'Cygnus Blessing | 시그너스 블레스'
    # Beginner
    ElementalHarmony = 'Elemental Harmony | 엘리멘탈 하모니'
    ElementalExpert = 'Elemental Expert | 엘리멘탈 엑스퍼트'
    # 1st Job
    LightningPunch = 'Lightning Punch | 충아'
    Flash = 'Flash | 섬광'
    LightningElemental = 'Lightning Elemental | 엘리멘탈 : 라이트닝'
    Electrified = 'Electrified | 뇌인'
    # 2nd Job
    SharkSweep = 'Shark Sweep | 회축'
    TidalCrash = 'Tidal Crash | 파도'
    KnuckleBooster = 'Knuckle Booster | 너클 부스터'
    KnuckleMastery = 'Knuckle Mastery | 너클 마스터리'
    Gains = 'Gains | 피지컬 트레이닝'
    LightningBoost = 'Lightning Boost | 뇌백'
    # 3rd Job
    Ascension = 'Ascension | 승천'
    Thunder = 'Thunder | 뇌성'
    Gale = 'Gale | 질풍'
    Seawall = 'Seawall | 와류'
    Ironclad = 'Ironclad | 극갑'
    LinkMastery = 'Link Mastery | 연쇄'
    LightningLord = 'Lightning Lord | 뇌제'
    # 4th Job
    CallofCygnus = 'Call of Cygnus | 시그너스 나이츠'
    Annihilate = 'Annihilate | 섬멸'
    Thunderbolt = 'Thunderbolt | 벽력'
    Typhoon = 'Typhoon | 태풍'
    ArcCharger = 'Arc Charger | 축뢰'
    SpeedInfusion = 'Speed Infusion | 윈드 부스터'
    KnuckleExpert = 'Knuckle Expert | 너클 엑스퍼트'
    Electrify = 'Electrify | 자극'
    ThunderGod = 'Thunder God | 뇌신'
    # Hypers
    DeepRising = 'Deep Rising | 해신강림'
    GloryoftheGuardians = 'Glory of the Guardians | 글로리 오브 가디언즈'
    PrimalBolt = 'Primal Bolt | 천지개벽'
    # 5th Job
    LightningCascade = 'Lightning Cascade | 신뇌합일'
    SharkTorpedo = 'Shark Torpedo | 교아탄'
    LightningGodSpearStrike = 'Lightning God Spear Strike | 뇌신창격'
    LightningSpearMultistrike = 'Lightning Spear Multistrike | 창뇌연격'


# TODO : Added to the Haesin Advent damage cycle. 해신강림 딜사이클에 추가.
class LightningWrapper(core.StackSkillWrapper):
    def __init__(self, skill):
        super(LightningWrapper, self).__init__(skill, 5)
        self.stack = 5
        self.set_name_style("%d 만큼 뇌전 변화")

    def get_modifier(self):
        return core.CharacterModifier(armor_ignore = self.stack * 9)

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "STR"
        self.jobname = "스트라이커"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore=43, pdamage=43)  # 뇌전 스택으로 평균 35~40%의 방무 적용 + 하이퍼

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ReservationRule(GlobalSkills.TermsAndConditions.value, f'{ThunderBreakerSkills.LightningSpearMultistrike.value}(Cast | 시전)'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(f'{ThunderBreakerSkills.LightningSpearMultistrike.value}(Cast | 시전)', GlobalSkills.TermsAndConditions.value), RuleSet.BASE)
        ruleset.add_rule(MutualRule(ThunderBreakerSkills.PrimalBolt.value, f'{ThunderBreakerSkills.LightningSpearMultistrike.value}(Cast | 시전)'), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ElementalExpert = core.InformedCharacterModifier(ThunderBreakerSkills.ElementalExpert.value,stat_main = chtr.level // 2)
        ElementalHarmony = core.InformedCharacterModifier(ThunderBreakerSkills.ElementalHarmony.value,patt = 10)

        NoieBack = core.InformedCharacterModifier(ThunderBreakerSkills.LightningBoost.value,att = 20)
        PhisicalTraining = core.InformedCharacterModifier(ThunderBreakerSkills.Gains.value,stat_main = 60)
        
        Gekgap = core.InformedCharacterModifier(ThunderBreakerSkills.Ironclad.value,pdamage = 5)
        NoiGe = core.InformedCharacterModifier(ThunderBreakerSkills.LightningLord.value,att = 30)
        NuckleExpert = core.InformedCharacterModifier(ThunderBreakerSkills.KnuckleExpert.value,att = 30 + passive_level, crit_damage = 20 + passive_level // 2)
        NoiShin = core.InformedCharacterModifier(ThunderBreakerSkills.ThunderGod.value,crit = 30, crit_damage = 25)
        
        SkyOpenPassive = core.InformedCharacterModifier(f"{ThunderBreakerSkills.PrimalBolt.value}(Passive | 패시브)",pdamage_indep = 20)
        
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 1, 3)

        
        return [ElementalHarmony, ElementalExpert,
            NoieBack, PhisicalTraining, Gekgap, NoiGe, NuckleExpert, NoiShin,
            SkyOpenPassive, LoadedDicePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=90+ceil(passive_level/2))
        
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

        Booster = core.BuffSkill(ThunderBreakerSkills.KnuckleBooster.value, 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        ChookRoi = core.BuffSkill(ThunderBreakerSkills.ArcCharger.value, 690, (180+5*self.combat)*1000, rem = True).wrap(core.BuffSkillWrapper)
        WindBooster = core.BuffSkill(ThunderBreakerSkills.SpeedInfusion.value, 0, (300+5*passive_level)*1000, rem = True).wrap(core.BuffSkillWrapper)
        HurricaneBuff = core.BuffSkill(f"{ThunderBreakerSkills.Typhoon.value}(Buff | 버프)", 0, (90+passive_level)*1000, rem = True, pdamage = 35).wrap(core.BuffSkillWrapper) # TODO: 뇌전 스택에 연동해야함
    
        LightningStack = LightningWrapper(core.BuffSkill(ThunderBreakerSkills.LightningElemental.value, 0, 99999999))

        Hurricane = core.DamageSkill(ThunderBreakerSkills.Typhoon.value, 420, 390+3*passive_level, 5+1).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        HurricaneConcat = core.DamageSkill(f"{ThunderBreakerSkills.Typhoon.value}(Link | 연계)", 420, 390+3*passive_level, 5+1, modifier = LINK_MASTERY).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        
        Destroy = core.DamageSkill(ThunderBreakerSkills.Annihilate.value, 480, 350 + 4*self.combat, 7, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Thunder = core.DamageSkill(ThunderBreakerSkills.Thunderbolt.value, 540, 320 + 4*self.combat, 5 + 1).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        WaterWave = core.DamageSkill(ThunderBreakerSkills.TidalCrash.value, 270, 255, 2).setV(vEhc, 1, 5, False).wrap(core.DamageSkillWrapper)
        DestroyConcat = core.DamageSkill(f"{ThunderBreakerSkills.Annihilate.value}(Link | 연계)", 480, 350 + 4*self.combat, 7, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20) + LINK_MASTERY).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        ThunderConcat = core.DamageSkill(f"{ThunderBreakerSkills.Thunderbolt.value}(연계)", 540, 320 + 4*self.combat, 5 + 1, modifier = LINK_MASTERY).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)   # Linked Final Damage 20%. 연계최종뎀 20%.
        WaterWaveConcat = core.DamageSkill(f"{ThunderBreakerSkills.TidalCrash.value}(Link | 연계)", 270, 255, 2, modifier = LINK_MASTERY).setV(vEhc, 1, 5, False).wrap(core.DamageSkillWrapper)
        WaterWaveConcatCancel = core.DamageSkill(f"{ThunderBreakerSkills.TidalCrash.value}(Link | 연계)(Cancel | 캔슬)", 60+60, 255, 2, modifier = LINK_MASTERY).setV(vEhc, 1, 5, False).wrap(core.DamageSkillWrapper)

        # Hyper. 하이퍼.
        # Need to add delay. 딜레이 추가 필요.
        SkyOpen = core.BuffSkill(ThunderBreakerSkills.PrimalBolt.value, 0, 30*1000, cooltime = 120*1000).wrap(core.BuffSkillWrapper)
        
        GloryOfGuardians = core.BuffSkill(ThunderBreakerSkills.GloryoftheGuardians.value, 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        CygnusPhalanx = cygnus.PhalanxChargeWrapper(vEhc, 4, 4)
        LuckyDice = core.BuffSkill("로디드 다이스", 0, 180*1000, pdamage = 20).isV(vEhc,1,3).wrap(core.BuffSkillWrapper)

        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        ShinNoiHapL = core.BuffSkill(ThunderBreakerSkills.LightningCascade.value, 540, (30+vEhc.getV(3,2)//2) * 1000, red = True, cooltime = (120-vEhc.getV(3,2)//2)*1000, pdamage_indep=5+vEhc.getV(3,2)//6).isV(vEhc,3,2).wrap(core.BuffSkillWrapper)
        ShinNoiHapLAttack = core.SummonSkill(f"{ThunderBreakerSkills.LightningCascade.value}(Attack | 공격)", 0, 3000, 16*vEhc.getV(3,2) + 400, 7, (30+vEhc.getV(3,2)//2) * 1000, cooltime = -1).isV(vEhc,3,2).wrap(core.SummonSkillWrapper)
        ShinNoiHapLAttack_ChookRoi = core.DamageSkill(f'{ThunderBreakerSkills.LightningCascade.value}({ThunderBreakerSkills.ArcCharger.value})', 0, (16*vEhc.getV(3,2) + 400) * CHOOKROI, 7 ).wrap(core.DamageSkillWrapper)
        GioaTan = core.DamageSkill(ThunderBreakerSkills.SharkTorpedo.value, 360, 1000+40*vEhc.getV(2,1), 7, cooltime = 8000, red = True, modifier = LINK_MASTERY).isV(vEhc,2,1).wrap(core.DamageSkillWrapper)  # Uses the Kyo-Atan-Break Power combo. 교아탄-벽력 콤보 사용함.

        NoiShinChanGeuk = core.DamageSkill(ThunderBreakerSkills.LightningGodSpearStrike.value, 0, 150+6*vEhc.getV(0,0), 6, cooltime = 7000, red = True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        NoiShinChanGeukAttack = core.SummonSkill(f"{ThunderBreakerSkills.LightningGodSpearStrike.value}(Follow-up | 후속타)", 0, 1000, 200 + 8*vEhc.getV(0,0), 7, 3999, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)    # Act 4 times. 4번 발동.
        NoiShinChanGeukAttack_ChookRoi = core.DamageSkill(f"{ThunderBreakerSkills.LightningGodSpearStrike.value}(Follow-up | 후속타)({ThunderBreakerSkills.ArcCharger.value})", 0, (200 + 8*vEhc.getV(0,0)) * CHOOKROI, 7).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)

        SpearLightningAttackInit = core.DamageSkill(f"{ThunderBreakerSkills.LightningSpearMultistrike.value}(Cast | 시전)", 0, 0, 0, cooltime=120*1000, red=True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)  # It's a stack-saving skill like throw blasting, but it's just handled with a 12 repetition extreme deal. 스로우 블래스팅같은 스택 저장형 스킬이지만... 그냥 12회 반복되는 극딜기로 처리.
        SpearLightningAttack = core.DamageSkill(ThunderBreakerSkills.LightningSpearMultistrike.value, 240, 375+15*vEhc.getV(0,0), 5, cooltime=-1, modifier = LINK_MASTERY).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        SpearLightningAttack_Lightning = core.DamageSkill(f"{ThunderBreakerSkills.LightningSpearMultistrike.value}(Lightning | 번개)", 0, 500+20*vEhc.getV(0,0), 4, cooltime=-1, modifier = LINK_MASTERY).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        SpearLightningAttack_Final = core.DamageSkill(f"{ThunderBreakerSkills.LightningSpearMultistrike.value}(Final attack | 막타)", 450, 600+24*vEhc.getV(0,0), 7, cooltime=-1, modifier = LINK_MASTERY).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        SpearLightningAttack_Final_Lightning = core.DamageSkill(f"{ThunderBreakerSkills.LightningSpearMultistrike.value}(Final attack | 막타)(Lightning | 번개)", 0, 725+29*vEhc.getV(0,0), 6, cooltime=-1, modifier = LINK_MASTERY).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)

        # Annihilation linkage (default). 섬멸 연계 (default).
        WaterWaveDestroy = core.GraphElement("파섬")
        WaterWaveDestroy.onAfter(WaterWaveConcat)
        WaterWaveDestroy.onAfter(DestroyConcat)
        HurricaneDestroy = core.GraphElement("태섬")
        HurricaneDestroy.onAfter(HurricaneConcat)
        HurricaneDestroy.onAfter(DestroyConcat)

        # Destruction connection (optional). 섬멸 연계 (optional).
        ThunderDestroy = core.GraphElement("벽섬")
        ThunderDestroy.onAfter(ThunderConcat)
        ThunderDestroy.onAfter(DestroyConcat)
        WaterWaveCancelDestroy = core.GraphElement("파파섬")
        WaterWaveCancelDestroy.onAfter(WaterWaveConcatCancel)
        WaterWaveCancelDestroy.onAfter(Destroy)
        WaterWaveCancelHurricane = core.GraphElement("파파태")
        WaterWaveCancelHurricane.onAfter(WaterWaveConcatCancel)
        WaterWaveCancelHurricane.onAfter(Hurricane)

        if DEALCYCLE == "waterwave":
            BasicAttack = core.OptionalElement(SkyOpen.is_active, HurricaneDestroy, WaterWaveDestroy)
        elif DEALCYCLE == "thunder":
            BasicAttack = core.OptionalElement(SkyOpen.is_active, HurricaneDestroy, ThunderDestroy)
        else:
            raise ValueError(DEALCYCLE)

        BasicAttackWrapper = core.DamageSkill('기본 공격', 0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)
        
        for skill in [Destroy, Thunder, WaterWave, DestroyConcat, ThunderConcat, WaterWaveConcat, WaterWaveConcatCancel, Hurricane, HurricaneConcat, GioaTan, NoiShinChanGeuk,
                        SpearLightningAttack, SpearLightningAttack_Lightning, SpearLightningAttack_Final, SpearLightningAttack_Final_Lightning]:
            jobutils.create_auxilary_attack(skill, CHOOKROI, nametag=f'({ThunderBreakerSkills.ArcCharger.value})')

        for skill in [Thunder, ThunderConcat, WaterWave, WaterWaveConcat, NoiShinChanGeuk,
                        SpearLightningAttack, SpearLightningAttack_Final]:
            skill.onAfter(LightningStack.stackController(1))

        for skill in [ShinNoiHapLAttack, CygnusPhalanx, NoiShinChanGeukAttack]:
            skill.onTick(LightningStack.stackController(1))

        GioaTan.onAfter(core.OptionalElement(SkyOpen.is_not_active, LightningStack.stackController(-2), name=f"Check {ThunderBreakerSkills.PrimalBolt.value} 체크"))
        
        ShinNoiHapLAttack.onTick(ShinNoiHapLAttack_ChookRoi)
        NoiShinChanGeukAttack.onTick(NoiShinChanGeukAttack_ChookRoi)
        
        ShinNoiHapL.onAfter(ShinNoiHapLAttack)
        #GioaTan.onAfter(DestroyConcat) # TODO: Including Gyoatan in BasicAttack and running. 교아탄을 BasicAttack에 포함해서 돌릴것.
        NoiShinChanGeuk.onAfter(NoiShinChanGeukAttack)

        SpearLightningAttack.onAfter(SpearLightningAttack_Lightning)
        SpearLightningAttack_Final.onAfter(SpearLightningAttack_Final_Lightning)
        SpearLightningAttackInit.onAfter(core.RepeatElement(SpearLightningAttack, 11))
        SpearLightningAttackInit.onAfter(SpearLightningAttack_Final)

        return(BasicAttackWrapper,
                [globalSkill.maple_heros(chtr.level, name=ThunderBreakerSkills.CallofCygnus.value, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    LightningStack, Booster, ChookRoi, WindBooster, LuckyDice,
                    HurricaneBuff, GloryOfGuardians, SkyOpen, Overdrive, ShinNoiHapL, cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level),
                    globalSkill.soul_contract()] +\
                [GioaTan, CygnusPhalanx, NoiShinChanGeuk, SpearLightningAttackInit, MirrorBreak, MirrorSpider] +\
                [ShinNoiHapLAttack, NoiShinChanGeukAttack] +\
                [] +\
                [BasicAttackWrapper])