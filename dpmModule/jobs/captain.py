from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import pirates

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.jobtype = "dex"
        self.vEnhanceNum = 14
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'buff_rem', 'crit')
        self.preEmptiveSkills = 1
    
    def get_passive_skill_list(self):

        
        CriticalRoar = core.InformedCharacterModifier("크리티컬 로어",crit = 20, crit_damage = 5)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        HalopointBullet = core.InformedCharacterModifier("할로포인트 불릿",att = 60)
        FullMetaJacket = core.InformedCharacterModifier("풀 메탈 재킷",pdamage_indep = 20, crit = 30, armor_ignore = 20)
        ContinualAimingPassive = core.InformedCharacterModifier("컨티뉴얼 에이밍(패시브)",crit_damage = 20)
        CaptainDignitiyPassive = core.InformedCharacterModifier("캡틴 디그니티(패시브)",att = 30)
        CrueCommandership = core.InformedCharacterModifier("크루 커맨더쉽",crit_damage = 25)
    
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(self.vEhc, 1, 2)
    
        return [CriticalRoar, PhisicalTraining, HalopointBullet, ContinualAimingPassive,
            FullMetaJacket, CaptainDignitiyPassive, CrueCommandership]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 50)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5)
        ContinualAimingPassive = core.InformedCharacterModifier("컨티뉴얼 에이밍(액티브)",pdamage_indep = 25)
        
        return [WeaponConstant, Mastery, ContinualAimingPassive]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        ----정보---
        크루 커멘더쉽 : 최종뎀 15%
        무라트 : 500 크뎀5
        발레리 : 560 크리15
        잭 : 320
        스토너 : 480
        두명 소환
    
        하이퍼 : 레피드파이어 : 보스킬러, 리인포스, 애드레인지
        헤드샷 - 보너스 어택, 리인포스
        
        데드아이 조준률 3배
        
        서먼 크루 분당 17타, 평균 퍼뎀 465
        봄버 평균 데미지 600ms당 249%x3
        
        퀵드로우 미사용
        
        5차 강화
        래피드/퍼실/디그니티
        헤드샷 / 배틀쉽/ 옥타
        서먼크루 / 스트봄 / 노틸러스
        '''
        DEADEYEACC = 3
        
        ######   Skill   ######
        #Buff skills
    
        SummonCrew = core.SummonSkill("어셈블 크루", 900, 60000/17, 465 * 1.15, 2, 120000, rem = True).setV(vEhc, 6, 2, True).wrap(core.SummonSkillWrapper)   #분당 17타, 평균 퍼뎀 465
        SummonCrewBuff = core.BuffSkill("어셈블 크루(버프)", 0, 120000, rem = True, crit = 15/2, crit_damage = 5/2, cooltime = -1, att = 45).wrap(core.BuffSkillWrapper)
    
        OctaQuaterdeck = core.SummonSkill("옥타 쿼터덱", 630, 60000/110, 300, 1, 30000, rem = True, cooltime = 10000).setV(vEhc, 5, 2, True).wrap(core.SummonSkillWrapper)
        RapidFire = core.DamageSkill("래피드 파이어", 120, 325, 1, modifier = core.CharacterModifier(pdamage = 30, boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        
        BattleshipBomber = core.DamageSkill("배틀쉽 봄버", 0,0,0, red = True, cooltime = 30000).wrap(core.DamageSkillWrapper)
        BattleshipBomber_1_ON = core.BuffSkill("배틀쉽봄버-1", 0, 30000, rem = True, cooltime = -1).wrap(core.BuffSkillWrapper)
        BattleshipBomber_2_ON = core.BuffSkill("배틀쉽봄버-2", 0, 30000, rem = True, cooltime = -1).wrap(core.BuffSkillWrapper)
        BattleshipBomber_1 = core.SummonSkill("배틀쉽 봄버(소환,1)", 300, 600, 249, 3, 30000, rem = True, cooltime = -1).setV(vEhc, 4, 2, True).wrap(core.SummonSkillWrapper)
        BattleshipBomber_2 = core.SummonSkill("배틀쉽 봄버(소환, 2)", 300, 600, 249, 3, 30000, rem = True, cooltime = -1).setV(vEhc, 4, 2, True).wrap(core.SummonSkillWrapper)
        '''
        돈틀레스 : 275 보통 13/22 타수3 600
        블랙바크 : 445 느림 15/18 타수3 810
        슈린츠 : 150 빠름   15/27 타수3 570
        조나단 : 235 보통   12/20 타수3 600
        평균 데미지 600ms당 249
        '''

        Headshot = core.DamageSkill("헤드 샷", 660, 525, 12+1, cooltime = 5000, modifier = core.CharacterModifier(crit=100, armor_ignore=60, pdamage = 20)).setV(vEhc, 3, 2, True).wrap(core.DamageSkillWrapper)
        
        Nautilus = core.DamageSkill("노틸러스", 690, 440+130, 7, red = True, cooltime = 30000).setV(vEhc, 8, 2, True).wrap(core.DamageSkillWrapper)
        PirateStyle = core.BuffSkill("파이렛 스타일", 0, 180000, rem = True, patt = 20).wrap(core.BuffSkillWrapper)
        CaptainDignitiyNormal = core.DamageSkill("캡틴 디그니티", 0, 275, 1).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        CaptainDignitiyEnhance = core.DamageSkill("캡틴 디그니티(강화)", 0, 275*1.3, 1).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper, name = "디그니티(강화)")
        
        QuickDraw = core.BuffSkill("퀵 드로우", 0, 10, cooltime = -1, pdamage_indep = 25).wrap(core.BuffSkillWrapper)
        
        Booster = core.BuffSkill("부스터", 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        InfiniteBullet = core.BuffSkill("인피닛 불릿", 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        LuckyDice = core.BuffSkill("럭키 다이스", 0, 180*1000, pdamage = 20 * 4 / 3, crit = 15 * 2/3 - 5 /36).isV(vEhc,1,2).wrap(core.BuffSkillWrapper)
        #1중첩 럭다 재사용 50초 감소 / 방어력30% / 체엠 20% / 크리율15% / 뎀증20 / 경치30
        #2중첩 럭다 재사용 50초 감소 / 방어력40% / 체엠 30% / 크리율25% / 뎀증30 / 경치40
        #7 발동시 방무 20 -> 30
        
        UnwierdingNectar = core.BuffSkill("언위어링 넥타", 1170, 180000, crit=10).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        PirateFlag = core.BuffSkill("파이렛 플래그", 990, 30 * 1000, cooltime = (60 - vEhc.getV(2,1)) * 1000, armor_ignore = (10 + 0.5*vEhc.getV(2,1)), stat_main_fixed = (chtr.level * 5 + 18)*0.01*(10 + 0.5*vEhc.getV(2,1))).isV(vEhc,2,1).wrap(core.BuffSkillWrapper)
        #오버드라이브 (앱솔 가정)
        #TODO: 템셋을 읽어서 무기별로 다른 수치 적용하도록 만들어야 함.
        WEAPON_ATT = 150
        OverdriveBuff = pirates.OverdriveWrapper(vEhc, WEAPON_ATT, 4, 4)
        Overdrive = OverdriveBuff.Overdrive
        OverdrivePenalty = OverdriveBuff.OverdrivePenalty
        
        BulletParty = core.DamageSkill("불릿 파티", 0, 0, 0, cooltime = 75000).wrap(core.DamageSkillWrapper)
        BulletPartyTick = core.DamageSkill("불릿 파티(틱)", 240, 230+9*vEhc.getV(5,5), 5).isV(vEhc,5,5).wrap(core.DamageSkillWrapper) #임의 딜레이, 사용안함.
        
        DeadEye = core.DamageSkill("데드아이", 600, (800+32*vEhc.getV(3,3))*3, 6, cooltime = 30000, red = True, modifier = core.CharacterModifier(crit = 100, pdamage_indep = 4*11)).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        NautillusAssult = core.SummonSkill("노틸러스 어썰트", 900, 360, 600+24*vEhc.getV(0,0), 6, 360*7-1, red = True, cooltime = 180000).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)#7회 2초간
        NautillusAssult_2 = core.SummonSkill("노틸러스 어썰트(2)", 0, 160, 300+12*vEhc.getV(0,0), 12, 160*36-1, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)#36회 6초간
        ######   Skill Wrapper   ######
    
        #크루 사용 후 버프 제공
        SummonCrew.onAfter(SummonCrewBuff)
        #배틀쉽은 둘 중 꺼져있는걸로 시전
        BattleshipBomber.onAfter(core.OptionalElement(BattleshipBomber_1.is_active, BattleshipBomber_2, BattleshipBomber_1))
        BattleshipBomber_1.onAfter(BattleshipBomber_1_ON)
        BattleshipBomber_2.onAfter(BattleshipBomber_2_ON)
        #노틸러스 이후 배틀쉽 쿨감

        NautilusConstraint = core.ConstraintElement("배틀쉽 쿨이 20초 이상", BattleshipBomber, partial(BattleshipBomber.is_cooltime_left, 20000, 1))

        Nautilus.onAfter(BattleshipBomber.controller(0.5, "reduce_cooltime_p"))
        Nautilus.onConstraint(NautilusConstraint)
        #디그니티는 노틸러스 쿨을 반영    
        CaptainDignitiy = core.OptionalElement(Nautilus.is_usable, CaptainDignitiyNormal, CaptainDignitiyEnhance)
        #오버드라이브 연계
        Overdrive.onAfter(OverdrivePenalty.controller(30*1000))
        #노틸러스 어썰트는 2개로 분리되어 잇음
        NautillusAssult.onAfter(NautillusAssult_2)
        #디그니티
        RapidFire.onAfter(CaptainDignitiy)
    
        return (RapidFire,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    SummonCrewBuff, PirateStyle, Booster, InfiniteBullet, LuckyDice, UnwierdingNectar, EpicAdventure, PirateFlag, Overdrive, OverdrivePenalty,
                    BattleshipBomber_1_ON, BattleshipBomber_2_ON,
                    globalSkill.soul_contract()] +\
                [BattleshipBomber, Headshot, Nautilus, DeadEye] +\
                [OctaQuaterdeck, BattleshipBomber_1, BattleshipBomber_2, NautillusAssult, NautillusAssult_2, SummonCrew] +\
                [] +\
                [RapidFire])
        
        return schedule