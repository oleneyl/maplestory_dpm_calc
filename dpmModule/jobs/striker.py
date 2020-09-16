from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from . import jobutils
from .jobbranch import pirates
from .jobclass import cygnus
from . import jobutils
from math import ceil

#TODO : 5차 신스킬 적용
#TODO : 천지개벽 발동 중에는 태풍을 노쿨로 사용하도록

######   Passive Skill   ######

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
        self.jobtype = "str"
        self.jobname = "스트라이커"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 40) # 뇌전 스택으로 평균 35~40%의 방무 적용

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트",stat_main = chtr.level // 2)
        ElementalHarmony = core.InformedCharacterModifier("엘리멘탈 하모니",patt = 10)

        NoieBack = core.InformedCharacterModifier("뇌백",att = 20)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 60)
        
        Gekgap = core.InformedCharacterModifier("극갑",pdamage = 5)
        NoiGe = core.InformedCharacterModifier("뇌제",att = 30)
        NuckleExpert = core.InformedCharacterModifier("너클 엑스퍼트",att = 30 + passive_level, crit_damage = 20 + passive_level // 2)
        NoiShin = core.InformedCharacterModifier("뇌신",crit = 30, crit_damage = 25)
        
        SkyOpenPassive = core.InformedCharacterModifier("천지개벽(패시브)",pdamage_indep = 20)
        
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 1, 3)

        
        return [ElementalHarmony, ElementalExpert,
            NoieBack, PhisicalTraining, Gekgap, NoiGe, NuckleExpert, NoiShin,
            SkyOpenPassive, LoadedDicePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5 + 0.5*ceil(passive_level/2))
        
        return [WeaponConstant, Mastery]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter):
        '''
        하이퍼 : 질풍-보너스어택 + 섬멸-리인포스/이그노어 가드/보스킬러  + 벽력-보너스어택
        
        코강 : 10개
        섬멸, 벽력, 승천, (뇌성)
        
        뇌전버프 상시 풀스택 가정
        연계 100% 가정

        천지개벽 ON: 태풍 - 섬멸
        천지개벽 OFF: 벽력 - 섬멸
        
        벽섬 : 1020ms
        태섬 : 900ms
        
        모든 스킬은 쿨타임마다 사용
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        CHOOKROI = 0.7 + 0.01*passive_level
        #Buff skills

        Booster = core.BuffSkill("부스터", 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        ChookRoi = core.BuffSkill("축뢰", 690, (180+5*self.combat)*1000, rem = True).wrap(core.BuffSkillWrapper)
        WindBooster = core.BuffSkill("윈드 부스터", 0, (300+5*passive_level)*1000, rem = True).wrap(core.BuffSkillWrapper)
        HuricaneBuff = core.BuffSkill("태풍(버프)", 0, (90+passive_level)*1000, rem = True, pdamage = 35).wrap(core.BuffSkillWrapper)
    
        LightningStack = LightningWrapper(core.BuffSkill("엘리멘탈 : 라이트닝", 0, 99999999))

        HuricaneConcat = core.DamageSkill("태풍(연계)", 420, 390+3*passive_level, 5+1, modifier = core.CharacterModifier(pdamage_indep = 20)).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        
        Destroy = core.DamageSkill("섬멸", 480, 350 + 4*self.combat, 7, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Thunder = core.DamageSkill("벽력", 540, 320 + 4*self.combat, 5 + 1).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        DestroyConcat = core.DamageSkill("섬멸(연계)", 480, 350 + 4*self.combat, 7, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20, pdamage_indep = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        ThunderConcat = core.DamageSkill("벽력(연계)", 540, 320 + 4*self.combat, 5 + 1, modifier = core.CharacterModifier(pdamage_indep = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)   #연계최종뎀 20%

        # 하이퍼
        # 딜레이 추가 필요
        SkyOpen = core.BuffSkill("천지개벽", 0, 30*1000, cooltime = 120*1000).wrap(core.BuffSkillWrapper)
        
        GloryOfGuardians = core.BuffSkill("글로리 오브 가디언즈", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        CygnusPalanks = cygnus.PhalanxChargeWrapper(vEhc, 4, 4)
        LuckyDice = core.BuffSkill("로디드 다이스", 0, 180*1000, pdamage = 20).isV(vEhc,1,3).wrap(core.BuffSkillWrapper)

        #오버드라이브 (앱솔 가정)
        #TODO: 템셋을 읽어서 무기별로 다른 수치 적용하도록 만들어야 함.
        WEAPON_ATT = jobutils.get_weapon_att("너클")
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        ShinNoiHapL = core.BuffSkill("신뇌합일", 540, (30+vEhc.getV(3,2)//2) * 1000, red = True, cooltime = (121-vEhc.getV(3,2)//2)*1000, pdamage_indep=4+vEhc.getV(3,2)//5).isV(vEhc,3,2).wrap(core.BuffSkillWrapper)
        ShinNoiHapLAttack = core.SummonSkill("신뇌합일(공격)", 0, 3000, 16*vEhc.getV(3,2) + 400, 7, (30+vEhc.getV(3,2)//2) * 1000, cooltime = -1).isV(vEhc,3,2).wrap(core.SummonSkillWrapper)
        ShinNoiHapLAttack_ChookRoi = core.DamageSkill('신뇌합일(축뢰)', 0, (16*vEhc.getV(3,2) + 400) * CHOOKROI, 7 ).wrap(core.DamageSkillWrapper)
        GioaTan = core.DamageSkill("교아탄", 480, 1000+40*vEhc.getV(2,1), 7, cooltime = 8000, red = True, modifier = core.CharacterModifier(pdamage_indep = 20)).isV(vEhc,2,1).wrap(core.DamageSkillWrapper) #  교아탄-벽력 콤보 사용함

        NoiShinChanGeuk = core.DamageSkill("뇌신창격", 0, 150+6*vEhc.getV(0,0), 6, cooltime = 7000, red = True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        NoiShinChanGeukAttack = core.SummonSkill("뇌신창격(후속타)", 0, 1000, 200 + 8*vEhc.getV(0,0), 7, 3999, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)    #4번 발동
        NoiShinChanGeukAttack_ChookRoi = core.DamageSkill("뇌신창격(후속타)(축뢰)", 0, (200 + 8*vEhc.getV(0,0)) * CHOOKROI, 7).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        #섬멸 연계

        BasicAttack = core.OptionalElement(SkyOpen.is_active, HuricaneConcat, ThunderConcat)
        BasicAttackWrapper = core.DamageSkill('기본 공격', 0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)

        HuricaneConcat.onAfter(DestroyConcat)
        ThunderConcat.onAfter(DestroyConcat)
        
        for skill in [Destroy, Thunder, DestroyConcat, ThunderConcat, HuricaneConcat, GioaTan, NoiShinChanGeuk]:
            jobutils.create_auxilary_attack(skill, CHOOKROI, "(축뢰)")

        for skill in [Destroy, Thunder, DestroyConcat, ThunderConcat, NoiShinChanGeuk]:
            skill.onAfter(LightningStack.stackController(1))

        for skill in [ShinNoiHapLAttack, CygnusPalanks, NoiShinChanGeukAttack]:
            skill.onTick(LightningStack.stackController(1))

        GioaTan.onAfter(LightningStack.stackController(-2))
        
        ShinNoiHapLAttack.onTick(ShinNoiHapLAttack_ChookRoi)
        NoiShinChanGeukAttack.onTick(NoiShinChanGeukAttack_ChookRoi)
        
        ShinNoiHapL.onAfter(ShinNoiHapLAttack)
        #GioaTan.onAfter(DestroyConcat)
        NoiShinChanGeuk.onAfter(NoiShinChanGeukAttack)

        return(BasicAttackWrapper,
                [globalSkill.maple_heros(chtr.level, name = "시그너스 나이츠", combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    LightningStack, Booster, ChookRoi, WindBooster, LuckyDice,
                    HuricaneBuff, GloryOfGuardians, SkyOpen, Overdrive, ShinNoiHapL, cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level),
                    globalSkill.soul_contract()] +\
                [GioaTan, CygnusPalanks, NoiShinChanGeuk, MirrorBreak, MirrorSpider] +\
                [ShinNoiHapLAttack, NoiShinChanGeukAttack] +\
                [] +\
                [BasicAttackWrapper])