from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from . import contrib
#TODO : 5차 신스킬 적용
#[섬멸] : 공격 횟수가 뇌전 버프와 무관하게 7회로적용되게 됩니다.
#[뇌신] : 컴뱃 오더스가 적용되지 않는 현재 로직과 같은 스킬 설명이 추가됩니다.
#[천지개벽] : 지속시간이 90초에서 30초로, 재사용 대기시간이 180초에서 120초로 감소되고 지속시간 동안 뇌전 버프를 소모하지 않는 기능이 추가됩니다. 천지개벽 지속시간 동안 질풍을 사용하면 데미지 증가 버프의 지속시간이 30초미만일 때만 지속시간이 갱신되게 됩니다.

######   Passive Skill   ######



class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = True
        self.vEnhanceNum = 10
        self.jobtype = "str"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_passive_skill_list(self):
        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트",stat_main = self.chtr.level // 2)
        ElementalHarmony = core.InformedCharacterModifier("엘리멘탈 하모니",patt = 10)

        NoieBack = core.InformedCharacterModifier("뇌백",att = 20)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 60)
        
        Gekgap = core.InformedCharacterModifier("극갑",pdamage = 5)
        NoiGe = core.InformedCharacterModifier("뇌제",att = 30)
        NuckleExpert = core.InformedCharacterModifier("너클 숙련",att = 30, crit_damage = 20)
        NoiShin = core.InformedCharacterModifier("뇌신",crit = 30, crit_damage = 25)
        
        SkyOpenPassive = core.InformedCharacterModifier("천지개벽(패시브)",pdamage_indep = 20)
        
        LoadedDicePassive = core.InformedCharacterModifier("로디드 다이스(패시브)",att = self.vEhc.getV(1,3) + 10)

        
        return [ElementalHarmony, ElementalExpert,
            NoieBack, PhisicalTraining, Gekgap, NoiGe, NuckleExpert, NoiShin,
            SkyOpenPassive, LoadedDicePassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)
        
        return [WeaponConstant, Mastery]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        하이퍼 : 섬멸 3종 + 벽력-리인포스/보너스어택
        
        코강 : 10개
        섬멸, 벽력, 승천, (뇌성)
        
        뇌전버프 상시 풀스택 가정
        태풍은 버프 쿨타임마다만 사용
        
        벽섬 : 1080ms (420 / 660)
        
        팔랑크스의 타수를 2/3만 적용되도록 함
        모든 스킬은 쿨타임마다 사용
        '''

        PALANKSRATE = 2 / 3
        CHOOKROI = 0.7
        #Buff skills

        Lightening = core.BuffSkill("엘리멘탈 : 라이트닝", 0, 180000, rem = True, armor_ignore = (5+4) * (1+1+1+1+1)).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill("부스터", 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        ChookRoi = core.BuffSkill("축뢰", 1620, 180000, rem = True).wrap(core.BuffSkillWrapper) # 타수증가 적용으로 계싼할지는 염두에 두어야 함
        WindBooster = core.BuffSkill("윈드 부스터", 0, 300000, rem = True).wrap(core.BuffSkillWrapper)
    
        Huricane = core.DamageSkill("태풍", 0, 390, 5).wrap(core.DamageSkillWrapper)
        HuricaneBuff = core.BuffSkill("태풍(버프)", 900, 90000, rem = True, pdamage = 35).wrap(core.BuffSkillWrapper)
        
        Destroy = core.DamageSkill("섬멸", 420, 350, 2 + 5, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Thunder = core.DamageSkill("벽력", 660, 320, 5 + 1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        DestroyConcat = core.DamageSkill("섬멸(연계)", 420, 350, 2 + 5, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20, pdamage_indep = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        ThunderConcat = core.DamageSkill("벽력(연계)", 660, 320, 5 + 1, modifier = core.CharacterModifier(pdamage = 20, pdamage_indep = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)   #연계최종뎀 20%
        
        
        
        #BasicAttack = core.DamageSkill("섬멸", 420, 350, 2 + 5, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        BasicAttack = core.DamageSkill("벽력(기본공격)", 660, 320, 5 + 1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)        

        # 하이퍼
        SkyOpen = core.BuffSkill("천지개벽", 0, 180000).wrap(core.BuffSkillWrapper) #   안씀
        
        GloryOfGuardians = core.BuffSkill("글로리 오브 가디언즈", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        CygnusPalanks = core.DamageSkill("시그너스 팔랑크스", 780, 450 + 18*vEhc.getV(4,4), int(40 + vEhc.getV(4,4) * PALANKSRATE), cooltime = 30 * 1000).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
        LuckyDice = core.BuffSkill("럭키 다이스", 0, 180*1000, pdamage = 20).isV(vEhc,1,3).wrap(core.BuffSkillWrapper)

        Overdrive = core.BuffSkill("오버드라이브", 540, 30*1000, cooltime = (70 - 0.2*vEhc.getV(5,5))*1000, att = 1.54*(20+2*vEhc.getV(5,5))).isV(vEhc,5,5).wrap(core.BuffSkillWrapper) #무기공의 (30+vlevel)만큼 공 증가 이후 15%만큼 감소. 30초유지, 70 - (0.2*vlevel), 앱솔가정,
        OverdrivePenalty = core.BuffSkill("오버드라이브(페널티)", 0, (40 - 0.2*vEhc.getV(5,5))*1000, cooltime = -1, att = -15*1.54).isV(vEhc,5,5).wrap(core.BuffSkillWrapper) #페널티

        ShinNoiHapL = core.BuffSkill("신뇌합일", 0, (30+vEhc.getV(3,2)//2) * 1000, red = True, cooltime = (121-vEhc.getV(3,2)//2)*1000, pdamage_indep=4+vEhc.getV(3,2)//5).isV(vEhc,3,2).wrap(core.BuffSkillWrapper)
        ShinNoiHapLAttack = core.SummonSkill("신뇌합일(공격)", 0, 3000, 16*vEhc.getV(3,2) + 400, 7, (30+vEhc.getV(3,2)//2) * 1000, cooltime = -1).isV(vEhc,3,2).wrap(core.SummonSkillWrapper)
        ShinNoiHapLAttack_ChookRoi = core.DamageSkill('신뇌합일(축뢰)', 0, (16*vEhc.getV(3,2) + 400) * CHOOKROI, 7 ).wrap(core.DamageSkillWrapper)
        GioaTan = core.DamageSkill("교아탄", 480, 1000+40*vEhc.getV(2,1), 7, cooltime = 8000).isV(vEhc,2,1).wrap(core.DamageSkillWrapper) #  교아탄-벽력 콤보 사용함

        NoiShinChanGeuk = core.DamageSkill("뇌신창격", 0, 150+6*vEhc.getV(0,0), 6, cooltime = 7000).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        NoiShinChanGeukAttack = core.SummonSkill("뇌신창격(공격)", 0, 1000, 200 + 8*vEhc.getV(0,0), 7, 3999, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)    #4번 발동
        NoiShinChanGeukAttack_ChookRoi = core.DamageSkill("뇌신창격(축뢰)", 0, (200 + 8*vEhc.getV(0,0)) * CHOOKROI, 7).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        #섬멸 연계
        
        for skill in [Destroy, Thunder, DestroyConcat, BasicAttack, ThunderConcat, GioaTan, NoiShinChanGeuk]:
            contrib.create_auxilary_attack(skill, CHOOKROI)
        ShinNoiHapLAttack.onTick(ShinNoiHapLAttack_ChookRoi)
        NoiShinChanGeukAttack.onTick(NoiShinChanGeukAttack_ChookRoi)
        
        #조건부 파이널어택으로 설정함.

        Overdrive.onAfter(OverdrivePenalty.controller(30*1000))

        HuricaneBuff.onAfter(Huricane)
        #BasicAttack.onAfter(ThunderConcat)
        BasicAttack.onAfter(DestroyConcat)
        
        ShinNoiHapL.onAfter(ShinNoiHapLAttack)
        GioaTan.onAfter(ThunderConcat)
        NoiShinChanGeuk.onAfter(NoiShinChanGeukAttack)

        return(BasicAttack,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    Lightening, Booster, ChookRoi, WindBooster, LuckyDice,
                    HuricaneBuff, GloryOfGuardians, Overdrive, OverdrivePenalty, ShinNoiHapL,
                    globalSkill.soul_contract()] +\
                [GioaTan, CygnusPalanks, NoiShinChanGeuk] +\
                [ShinNoiHapLAttack, NoiShinChanGeukAttack] +\
                [] +\
                [BasicAttack])