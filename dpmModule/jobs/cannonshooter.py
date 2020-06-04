from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import pirates
from .jobclass import adventurer
from . import jobutils

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.jobtype = "str"
        self.vEnhanceNum = 16
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'reuse')
        self.preEmptiveSkills = 2

    def get_passive_skill_list(self):
        BuildupCanon = core.InformedCharacterModifier("빌드업 캐논",att = 20)
        CriticalFire = core.InformedCharacterModifier("크리티컬 파이어",crit=20, crit_damage=5)
        PirateTraining = core.InformedCharacterModifier("파이렛 트레이닝",stat_main=30, stat_sub=30)
        
        MonkeyWavePassive = core.InformedCharacterModifier("몽키 웨이브(패시브)",crit=20)
        OakRuletPassive = core.InformedCharacterModifier("오크통 룰렛(패시브)",pdamage_indep = 10) 
        ReinforceCanon = core.InformedCharacterModifier("리인포스 캐논",att = 40)
        PirateSpirit = core.InformedCharacterModifier("파이렛 스피릿",boss_pdamage=40)
        OverburningCanon = core.InformedCharacterModifier("오버버닝 캐논",pdamage_indep=30, armor_ignore=20)
    
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(self.vEhc, 3, 4)
    
        return [BuildupCanon, CriticalFire, 
                            PirateTraining, MonkeyWavePassive, OakRuletPassive, ReinforceCanon,
                            PirateSpirit, OverburningCanon, LoadedDicePassive]
        
    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 50)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5)        
        return [WeaponConstant, Mastery]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        하이퍼 : 몽키트윈스-스플릿, 인핸스, 캐논버스터 - 리인포스, 보너스 어택.
        롤링캐논레인보우 25타
        
        코코볼 6초
        이씨밤 5타
        
        코강 순서:
        버스터-서포트-다수기-롤캐
        '''
        COCOBALLHIT = 6000
        ICBMHIT = 5
        
        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 200*1000).wrap(core.BuffSkillWrapper)
        
        MonkeyWave = core.DamageSkill("몽키 웨이브", 810, 860, 1, cooltime = 30*1000).wrap(core.DamageSkillWrapper)
        MonkeyWaveBuff = core.BuffSkill("몽키 웨이브(버프)", 0, 30000, cooltime = -1, crit_damage = 5).wrap(core.BuffSkillWrapper)
        MonkeyFurious = core.DamageSkill("몽키 퓨리어스", 690, 180, 3, cooltime = 30*1000).wrap(core.DamageSkillWrapper)
        MonkeyFuriousBuff = core.BuffSkill("몽키 퓨리어스(버프)", 0, 30000, cooltime = -1, pdamage = 40).wrap(core.BuffSkillWrapper)
        OakRulet = core.BuffSkill("오크통 룰렛", 810, 180000, rem = True, cooltime = 180000, crit_damage = 1.25).wrap(core.BuffSkillWrapper)
        OakRuletDOT = core.DotSkill("오크통 도트", 50, 5000).wrap(core.SummonSkillWrapper)
        MonkeyMagic = core.BuffSkill("하이퍼 몽키 스펠", 0, 180000, rem = True, stat_main=60, stat_sub=60).wrap(core.BuffSkillWrapper)
    
        CanonBuster = core.DamageSkill("캐논 버스터", 690, 750*0.45, 3*(4+1), modifier = core.CharacterModifier(crit=15, armor_ignore=20, pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
    
        #서포트 몽키 트윈스 공격주기 확ㄷ인
        SupportMonkeyTwins = core.SummonSkill("서포트 몽키 트윈스", 720, 60000/195*3, 3*295*0.6, 2, 60000, rem = True).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)
        
        RollingCanonRainbow = core.SummonSkill("롤링 캐논 레인보우", 810, 12000/25, 600, 3, 12000, cooltime = 90000).setV(vEhc, 3, 2, True).wrap(core.SummonSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60000, cooltime = 120000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        #로디드 데미지 고정.
        LuckyDice = core.BuffSkill("럭키 다이스", 0, 180*1000, pdamage = 20 * 4 / 3).isV(vEhc,3,4).wrap(core.BuffSkillWrapper)
    
        #오버드라이브 (앱솔 가정)
        #TODO: 템셋을 읽어서 무기별로 다른 수치 적용하도록 만들어야 함.
        WEAPON_ATT = jobutils.getWeaponATT("핸드캐논")
        Overdrive, OverdrivePenalty = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
    
        PirateFlag = PirateFlag = adventurer.PirateFlagWrapper(vEhc, 4, 3, chtr.level)

        # 쿨타임마다 사용
        # 1.2.332 패치 반영 (50회 제한)
        BFGCannonball = core.SummonSkill("빅 휴즈 기간틱 캐논볼", 600, 210, (450+15*vEhc.getV(0,0)) * 0.45, 4 * 3, 210*50, cooltime = 25000).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)


        ICBM = core.DamageSkill("ICBM", 1190, (1200+48*vEhc.getV(1,1)) * 0.45, 5*ICBMHIT * 3, cooltime = 30000).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        ICBMDOT = core.SummonSkill("ICBM(장판)", 0, 15000/27, (500+20*vEhc.getV(1,1)) * 0.45, 1 * 3, 15000, cooltime = -1).isV(vEhc,1,1).wrap(core.SummonSkillWrapper) #27타
    
        SpecialMonkeyEscort_Canon = core.SummonSkill("스페셜 몽키 에스코트", 780, int(45000 / 97), 300+12*vEhc.getV(2,2), 4, (30+int(0.5*vEhc.getV(2,2)))*1000 - 1500, cooltime = 120000).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
        SpecialMonkeyEscort_Boom = core.SummonSkill("스페셜 몽키 에스코트(폭탄)", 0, int(45000 / 17), 450+18*vEhc.getV(2,2), 7, (30+int(0.5*vEhc.getV(2,2)))*5000 - 1500, cooltime = 120000, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
        ### build graph relationships
    
        MonkeyWave.onAfter(MonkeyWaveBuff)
        MonkeyFurious.onAfter(MonkeyFuriousBuff)
    
        CanonBuster.onAfter(OakRuletDOT)
        BFGCannonball.onAfter(OakRuletDOT)
        ICBM.onAfter(OakRuletDOT)
        SupportMonkeyTwins.onAfter(OakRuletDOT)
        
        ICBM.onAfter(ICBMDOT)
    
        SpecialMonkeyEscort_Canon.onAfter(SpecialMonkeyEscort_Boom)
    
        return(CanonBuster,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster(),
                    Booster, MonkeyWaveBuff, MonkeyFuriousBuff, OakRulet, MonkeyMagic,
                    EpicAdventure, LuckyDice, Overdrive, OverdrivePenalty, PirateFlag,
                    globalSkill.soul_contract()] +\
                [MonkeyWave, MonkeyFurious, ICBM] +\
                [OakRuletDOT, SupportMonkeyTwins, RollingCanonRainbow, BFGCannonball, ICBMDOT, SpecialMonkeyEscort_Boom, SpecialMonkeyEscort_Canon] +\
                [] +\
                [CanonBuster])