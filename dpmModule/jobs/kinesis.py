from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import magicians

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = True
        self.vEnhanceNum = 13
        self.jobtype = "int"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2
        
    def apply_complex_options(self, chtr):
        chtr.buff_rem += 20

    def get_passive_skill_list(self):
        SuperSensitive = core.InformedCharacterModifier("초감각",crit = 10)
        PsychicForce1Passive = core.InformedCharacterModifier("사이킥 포스1(패시브)",att = 10)
        Inertia1 = core.InformedCharacterModifier("내재 1",att = 10)
        
        PsychicForce2Passive = core.InformedCharacterModifier("사이킥 포스 2(패시브)",att = 10)
        PureForce = core.InformedCharacterModifier("순수한 힘",pdamage = 20)
        Inertia2 = core.InformedCharacterModifier("내재 2",att = 10)
        ESPMastery = core.InformedCharacterModifier("ESP 마스터리",crit = 10, stat_main = 40)
        
        MindEnhance = core.InformedCharacterModifier("감정 강화",patt = 10)
        Accurate = core.InformedCharacterModifier("정밀",crit = 20, crit_damage = 20)
        PsychicChargingPassive = core.InformedCharacterModifier("사이킥 차징(패시브)",boss_pdamage = 30)
        PsychicForce3Passive = core.InformedCharacterModifier("사이킥 포스 3(패시브)",att = 10)
        
        ESPBattleOrder = core.InformedCharacterModifier("ESP 배틀오더",att = 50, pdamage = 20)
        Transcendence = core.InformedCharacterModifier("각성",pdamage_indep = 25)
        Transport = core.InformedCharacterModifier("전달",armor_ignore = 25)
        Mastery = core.InformedCharacterModifier("마스터리",crit_damage = 10)
        #TODO
        #Elemental Reset --> elemental ignorance +10% --> first we will apply this term as simple pdamage_indep
        
        return [SuperSensitive, PsychicForce1Passive, Inertia1,
                            PsychicForce2Passive, PureForce, Inertia2, ESPMastery,
                            MindEnhance, Accurate, PsychicChargingPassive, PsychicForce3Passive,
                             ESPBattleOrder, Transcendence, Transport, Mastery]

    def get_not_implied_skill_list(self):     
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)
        PsychicForce3Passive = core.InformedCharacterModifier("사이킥 포스 3(패시브)", pdamage_indep = 20)
        return [WeaponConstant, Mastery, PsychicForce3Passive]
        
        

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        하이퍼
        싸이킥 그랩 - 보스포인트/리인포스
        싸이킥그라운드-리듀스 가드/퍼시스트
        싸이코브레이크 - 인핸스
        
        코강 순서:
        BPM 메테리얼 그랩 드레인 트레인
        
        싸이킥 샷 히트율 80%, 타수2배 적용.
        '''
        ######   Skill   ######

            
        '''This function is recommended.
        '''
        Booster = core.BuffSkill("부스터", 0, 180000).wrap(core.BuffSkillWrapper)
        PsychicShield = core.BuffSkill("사이킥 실드", 0, 180000).wrap(core.BuffSkillWrapper)

        Ultimate_Material = core.DamageSkill("얼티메이트-메테리얼", 600, 700, 10, modifier = core.CharacterModifier(crit_damage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)#   7
        PsychicDrain = core.SummonSkill("사이킥 드레인", 690, 660, 150, 1, 10000, rem = False).setV(vEhc, 4, 5, False).wrap(core.SummonSkillWrapper) # 1칸+
        
        PsychicForce3 = core.SummonSkill("싸이킥 포스3", 270, 1000, 75, 1, 20000, rem = False).wrap(core.SummonSkillWrapper)
        PsychicGround = core.BuffSkill("싸이킥 그라운드2", 270, 20000 + 10000, rem = False, armor_ignore = 10 + 6*1, pdamage_indep = 10 + 3*1).wrap(core.BuffSkillWrapper)
        PsychicGroundDamage = core.DamageSkill("싸이킥 그라운드2(공격)", 0, 500, 1).wrap(core.DamageSkillWrapper) # +1
        PsycoBreak = core.BuffSkill("싸이코 브레이크", 720, 30000, pdamage_indep = 5 * 2, rem = False).wrap(core.BuffSkillWrapper) #+1
        PsycoBreakDamage = core.DamageSkill("싸이코 브레이크(공격)", 0, 1000, 4).wrap(core.DamageSkillWrapper)
        
        TeleKinesis = core.DamageSkill("텔레키네시스", 0, 350, 0.7).wrap(core.DamageSkillWrapper)
        UltimateBPM = core.SummonSkill("얼티메이트-BPM", 0, 660, 175, 7, 999999999).setV(vEhc, 0, 2, False).wrap(core.SummonSkillWrapper) #1
        UltimatePsychic = core.DamageSkill("얼티메이트-싸이킥 샷", 660, 300, 3*5*2*0.8,  modifier = core.CharacterModifier(crit_damage = 20, pdamage = 20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper) #5
        UltimatePsychicBuff = core.BuffSkill("얼티메이트-싸이킥 샷(디버프)", 0, 10000, rem = True, armor_ignore = 15, cooltime = -1).wrap(core.BuffSkillWrapper)
        
        PsychicGrab2 = core.DamageSkill("싸이킥 그랩2", 540, 470, 5,  modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper) #+2
        
        PsychicCharging = core.BuffSkill("싸이킥 차징", 0, 500, cooltime = 45000, red = True).wrap(core.BuffSkillWrapper) #남은포인트의 50%충전
        
        #하이퍼
        EverPsychic = core.DamageSkill("에버 싸이킥", 4380, 400, 16, cooltime = 120000).wrap(core.DamageSkillWrapper) # +30
        EverPsychicFinal = core.DamageSkill("에버 싸이킥(최종)", 0, 1500, 1,  modifier = core.CharacterModifier(armor_ignore = 50, crit = 100)).wrap(core.DamageSkillWrapper)
        #Psycometry = core.DamageSkill()
        PsychicOver = core.BuffSkill("싸이킥 오버", 0, 30000, cooltime = 210000).wrap(core.BuffSkillWrapper) # 소모량 절반 / 포인트 지속증가(초당 1)
        PsychicOverSummon = core.SummonSkill("싸이킥 오버(소환)", 0, 1000, 0, 0, 30000, cooltime = -1).wrap(core.SummonSkillWrapper)
        try:
            OverloadMana = OverloadMana = magicians.OverloadManaWrapper(vEhc, 1, 1)
        except:
            print(vEhc)
            raise

        PsychicTornado = core.SummonSkill("싸이킥 토네이도", 720, 1000, 500+20*vEhc.getV(2,2), 4, 20000, red = True, cooltime = 120000).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)# -15
        PsychicTornadoFinal_1 = core.DamageSkill("싸이킥 토네이도(1)", 0, (200+3*vEhc.getV(2,2))*3, 2).wrap(core.DamageSkillWrapper)
        PsychicTornadoFinal_2 = core.DamageSkill("싸이킥 토네이도(2)", 0, (350+10*vEhc.getV(2,2))*3, 6*3).wrap(core.DamageSkillWrapper)

        UltimateMovingMatter = core.SummonSkill("무빙 매터", 630, 25000/64, 500+20*vEhc.getV(0,0), 5, 25000, cooltime = 90000, modifier = core.CharacterModifier(crit_damage=20)).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)# -10
        UltimateMovingMatterFinal = core.DamageSkill("무빙 매터(최종)", 0, 700+28*vEhc.getV(0,0), 12).wrap(core.DamageSkillWrapper)
        
        UltimatePsychicBullet = core.DamageSkill("싸이킥 불릿", 570, 550 + 22*vEhc.getV(3,3), 6, modifier = core.CharacterModifier(crit_damage=20)).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)# -2
        UltimatePsychicBulletBlackhole = core.SummonSkill("싸이킥 불릿(블랙홀)", 0, 500, 500+20*vEhc.getV(3,3), 3, 500*4, cooltime = -1).isV(vEhc,3,3).wrap(core.SummonSkillWrapper)# +1
        
        PsychicPoint = core.StackSkillWrapper(core.BuffSkill("싸이킥 포인트", 0, 999999999), 30)
        PsychicPoint.set_name_style("포인트 변화 : %d")

        
        ### Build Graph ###

        ### Telekinesis
        for sk in [PsychicGrab2, PsychicGroundDamage, PsycoBreakDamage, EverPsychicFinal, PsychicTornadoFinal_1, PsychicTornadoFinal_2]:
            sk.onAfter(TeleKinesis)
        
        
        ### Tandem skill connection
        PsychicGround.onAfter(PsychicGroundDamage)
        PsycoBreak.onAfter(PsycoBreakDamage)
        UltimatePsychic.onAfter(UltimatePsychicBuff)
        EverPsychic.onAfter(EverPsychicFinal)
        PsychicOver.onAfter(PsychicOverSummon)
        PsychicTornado.onAfter(PsychicTornadoFinal_1)
        PsychicTornado.onAfter(PsychicTornadoFinal_2)
        UltimateMovingMatter.onAfter(UltimateMovingMatterFinal)
        UltimatePsychicBullet.onAfter(UltimatePsychicBulletBlackhole)
        
        
        ### Psychic point
        Ultimate_Material.onConstraint(core.ConstraintElement("7포인트", PsychicPoint, partial(PsychicPoint.judge,7,1)))
        Ultimate_Material.onAfter(PsychicPoint.stackController(-7))
        
        PsychicForce3.onAfter(PsychicPoint.stackController(1))
        
        PsychicDrain.onTick(PsychicPoint.stackController(1))
        PsychicGroundDamage.onAfter(PsychicPoint.stackController(1))
        PsycoBreak.onAfter(PsychicPoint.stackController(1))
        
        UltimateBPM.onTick(PsychicPoint.stackController(-1))
        
        UltimatePsychic.onConstraint(core.ConstraintElement("5포인트", PsychicPoint, partial(PsychicPoint.judge,5,1)))
        UltimatePsychic.onAfter(PsychicPoint.stackController(-5))
        UltimatePsychic.onAfter(core.OptionalElement(PsychicOver.is_active, PsychicPoint.stackController(3)))
        
        PsychicGrab2.onAfter(PsychicPoint.stackController(2))
        EverPsychic.onAfter(PsychicPoint.stackController(30))
        PsychicOverSummon.onTick(PsychicPoint.stackController(1))
        
        PsychicTornado.onConstraint(core.ConstraintElement("15포인트", PsychicPoint, partial(PsychicPoint.judge,15,1)))
        PsychicTornado.onAfter(PsychicPoint.stackController(-15))
        PsychicTornado.onAfter(core.OptionalElement(PsychicOver.is_active, PsychicPoint.stackController(8)))

        UltimateMovingMatter.onConstraint(core.ConstraintElement("10포인트", PsychicPoint, partial(PsychicPoint.judge,10,1)))
        UltimateMovingMatter.onAfter(PsychicPoint.stackController(-10))
        UltimateMovingMatter.onAfter(core.OptionalElement(PsychicOver.is_active, PsychicPoint.stackController(5)))
        
        UltimateMovingMatter.onConstraint(core.ConstraintElement("2포인트", PsychicPoint, partial(PsychicPoint.judge,2,1)))
        UltimatePsychicBullet.onAfter(PsychicPoint.stackController(-3))
        UltimatePsychicBullet.onAfter(core.OptionalElement(PsychicOver.is_active, PsychicPoint.stackController(2)))
        
        UltimatePsychicBulletBlackhole.onTick(PsychicPoint.stackController(1))
        
        PsychicCharging.onAfter(PsychicPoint.stackController(10))   #급한대로 +10
        PsychicCharging.onConstraint(core.ConstraintElement("2포인트", PsychicPoint, partial(PsychicPoint.judge,5,-1)))
        
        schedule = core.ScheduleGraph()
        
        return(PsychicGrab2,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster(),
                    Booster, PsychicShield, PsychicGround, 
                    PsycoBreak, UltimatePsychicBuff, PsychicCharging, 
                    PsychicOver, OverloadMana, PsychicPoint,
                    globalSkill.soul_contract()] +\
                [EverPsychic, UltimatePsychic] +\
                [PsychicDrain, PsychicForce3, UltimateBPM, PsychicOverSummon, PsychicTornado, UltimateMovingMatter, UltimatePsychicBulletBlackhole] +\
                [] +\
                [PsychicGrab2])