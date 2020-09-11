from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import pirates
from .jobclass import adventurer
from . import jobutils
from math import ceil

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "dex"
        self.jobname = "캡틴"
        self.vEnhanceNum = 14
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'buff_rem', 'crit')
        self.preEmptiveSkills = 1
    
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        CriticalRoar = core.InformedCharacterModifier("크리티컬 로어",crit = 20, crit_damage = 5)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        HalopointBullet = core.InformedCharacterModifier("할로포인트 불릿",att = 60)
        FullMetaJacket = core.InformedCharacterModifier("풀 메탈 재킷",pdamage_indep = 20, crit = 30, armor_ignore = 20)
        ContinualAimingPassive = core.InformedCharacterModifier("컨티뉴얼 에이밍(패시브)",crit_damage = 20 + self.combat)
        CaptainDignityPassive = core.InformedCharacterModifier("캡틴 디그니티(패시브)",att = 30 + passive_level)
        CrueCommandership = core.InformedCharacterModifier("크루 커맨더쉽",crit_damage = 25 + passive_level)
    
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 1, 2)
    
        return [CriticalRoar, PhisicalTraining, HalopointBullet, ContinualAimingPassive,
            FullMetaJacket, CaptainDignityPassive, CrueCommandership, LoadedDicePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 50)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5 + 0.5*ceil(passive_level/2))
        
        return [WeaponConstant, Mastery]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter):
        '''
        ----정보---
        크루 커멘더쉽 : 최종뎀 15%
        무라트 : 500 크뎀5
        발레리 : 560 크리15
        잭 : 320
        스토너 : 480
        두명 소환
    
        하이퍼
        래피드파이어 - 보스킬러, 리인포스, 애드레인지
        헤드샷 - 보너스 어택, 리인포스
        
        데드아이 조준률 3배

        퀵 드로우 : 사용 가능하면 헤드샷, 스트레인지 봄, 데드아이 전에 사용
        
        서먼 크루 분당 17타, 평균 퍼뎀 465
        봄버 평균 데미지 600ms당 297%x3
        
        카운터 어택 미발동
        
        5차 강화
        래피드 / 퍼실 / 디그니티
        헤드샷 / 배틀쉽 / 옥타
        서먼크루 / 스트봄 / 노틸러스
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        DEADEYEACC = 3
        BULLET_PARTY_TICK = 150
        CONTINUAL_AIMING = core.CharacterModifier(pdamage_indep = 25 + 2*self.combat)
        
        ######   Skill   ######
        # Buff skills
        PirateStyle = core.BuffSkill("파이렛 스타일", 0, (180+6*self.combat)*1000, rem = True, patt = 20 + self.combat).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill("부스터", 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        InfiniteBullet = core.BuffSkill("인피닛 불릿", 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        LuckyDice = core.BuffSkill("로디드 다이스", 990, 180*1000, pdamage = 20+10/6+10/6*(5/6+1/11)*(10*(5+passive_level)*0.01)).isV(vEhc,1,2).wrap(core.BuffSkillWrapper)
        QuickDraw = core.BuffSkill("퀵 드로우", 60, core.infinite_time(), cooltime = -1, pdamage_indep = 25 + self.combat).wrap(core.BuffSkillWrapper) # 임의 딜레이
        QuickDrawStack = core.StackSkillWrapper(core.BuffSkill("퀵 드로우(준비)", 0, 99999999), 1)

        # Summon Skills
        OctaQuaterdeck = core.SummonSkill("옥타 쿼터덱", 630, 60000/110, 300, 1, 30000, rem = True, cooltime = 10000).setV(vEhc, 5, 2, True).wrap(core.SummonSkillWrapper)
        SummonCrew = core.SummonSkill("서먼 크루", 900, 60000/17, 465, 2, 120000, modifier=core.CharacterModifier(pdamage_indep = 15 + passive_level), rem = True).setV(vEhc, 6, 2, True).wrap(core.SummonSkillWrapper)   #분당 17타, 평균 퍼뎀 465
        SummonCrewBuff = core.BuffSkill("서먼 크루(버프)", 0, 120000, cooltime = -1, crit = (15+passive_level)/2, crit_damage = 5/2, att = 45 + 3*passive_level).wrap(core.BuffSkillWrapper)
        
        '''
        돈틀레스 : 330 보통 13/22 타수3 600
        블랙바크 : 445 느림 15/18 타수3 810
        슈린츠 : 200 빠름   15/27 타수3 570
        조나단 : 320 보통   12/20 타수3 600
        평균 데미지 600ms당 297
        '''
        BB_AVERAGE = ((330+3*self.combat) + (445+3*self.combat)*(600/810) + (200+3*self.combat)*(600/570) + (320+3*self.combat))/4
        # TODO: 배틀쉽 봄버 공격주기 확인 필요
        BattleshipBomber = core.DamageSkill("배틀쉽 봄버", 0,0,0, cooltime = 30000, red = True).wrap(core.DamageSkillWrapper)
        BattleshipBomber_1 = core.SummonSkill("배틀쉽 봄버(소환,1)", 390, 600, BB_AVERAGE, 3, 60000, rem = True, cooltime = -1).setV(vEhc, 4, 2, True).wrap(core.SummonSkillWrapper)
        BattleshipBomber_2 = core.SummonSkill("배틀쉽 봄버(소환,2)", 390, 600, BB_AVERAGE, 3, 60000, rem = True, cooltime = -1).setV(vEhc, 4, 2, True).wrap(core.SummonSkillWrapper)
        
        # Damage Skills
        RapidFire = core.DamageSkill("래피드 파이어", 150, 325 + 3*self.combat, 1, modifier = core.CharacterModifier(pdamage = 30, boss_pdamage = 20) + CONTINUAL_AIMING).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Headshot = core.DamageSkill("헤드 샷", 450, 525+5*self.combat, 12+1, cooltime = 5000, red=True, modifier = core.CharacterModifier(crit = 100, armor_ignore = 60, pdamage = 20) + CONTINUAL_AIMING).setV(vEhc, 3, 2, True).wrap(core.DamageSkillWrapper)
        
        Nautilus = core.DamageSkill("노틸러스", 690, 440+130+(4+3)*self.combat, 7, red = True, cooltime = 30000, modifier = CONTINUAL_AIMING).setV(vEhc, 8, 2, True).wrap(core.DamageSkillWrapper)
        CaptainDignityNormal = core.DamageSkill("캡틴 디그니티", 0, 275 + 3*passive_level, 1, modifier = CONTINUAL_AIMING).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        CaptainDignityEnhance = core.DamageSkill("캡틴 디그니티(강화)", 0, (275 + 3*passive_level)*1.3, 1, modifier = CONTINUAL_AIMING).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        
        # Hyper
        UnwierdingNectar = core.BuffSkill("언위어링 넥타", 0, 180000, crit=10).wrap(core.BuffSkillWrapper)
        StrangeBomb = core.DamageSkill("스트레인지 봄", 810, 400, 12, cooltime = 30000, modifier = CONTINUAL_AIMING).setV(vEhc, 7, 2, True).wrap(core.DamageSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 150 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        # 5th
        PirateFlag = adventurer.PirateFlagWrapper(vEhc, 2, 1, chtr.level)
        #오버드라이브 (앱솔 가정)
        #TODO: 템셋을 읽어서 무기별로 다른 수치 적용하도록 만들어야 함.
        WEAPON_ATT = jobutils.get_weapon_att("건")
        Overdrive = pirates.OverdriveWrapper(vEhc, 4, 4, WEAPON_ATT)
        
        BulletParty = core.DamageSkill("불릿 파티", 0, 0, 0, cooltime = 75000, red = True).wrap(core.DamageSkillWrapper)
        BulletPartyTick = core.DamageSkill("불릿 파티(틱)", BULLET_PARTY_TICK, 230+9*vEhc.getV(5,5), 5, modifier = CONTINUAL_AIMING).isV(vEhc,5,5).wrap(core.DamageSkillWrapper) #12초간 지속 -> 50회 시전
        DeadEye = core.DamageSkill("데드아이", 450, (800+32*vEhc.getV(3,3))*DEADEYEACC, 6, cooltime = 30000, red = True, modifier = core.CharacterModifier(crit = 100, pdamage_indep = 4*11) + CONTINUAL_AIMING).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        NautilusAssult = core.SummonSkill("노틸러스 어썰트", 690, 360, 600+24*vEhc.getV(0,0), 6, 360*7-1, cooltime = 180000, red = True, modifier = CONTINUAL_AIMING).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)#7회 2초간
        NautilusAssult_2 = core.SummonSkill("노틸러스 어썰트(일제 사격)", 0, 160, 300+12*vEhc.getV(0,0), 12, 160*36-1, cooltime = -1, modifier = CONTINUAL_AIMING).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)#36회 6초간

        ######   Skill Wrapper   ######
    
        #크루 사용 후 버프 제공
        SummonCrew.onAfter(SummonCrewBuff)

        #배틀쉽은 둘 중 꺼져있는걸로 시전
        BattleshipBomber.onAfter(core.OptionalElement(BattleshipBomber_1.is_active, BattleshipBomber_2, BattleshipBomber_1, name = "배틀쉽 1,2"))

        #노틸러스 이후 배틀쉽 쿨감
        Nautilus.onAfter(BattleshipBomber.controller(0.5, "reduce_cooltime_p"))
        
        #디그니티는 노틸러스 쿨타임에 강화됨
        CaptainDignity = core.OptionalElement(Nautilus.is_usable, CaptainDignityNormal, CaptainDignityEnhance, name = "캡틴 디그니티 강화")
        for sk in [RapidFire, Headshot, BulletPartyTick, DeadEye]:
            sk.onAfter(CaptainDignity)

        # 퀵 드로우
        QuickDraw.onAfter(QuickDrawStack.stackController(-1, name = "퀵 드로우 준비 해제"))
        QuickDrawProc = QuickDrawStack.stackController((8 + self.combat) * 0.01, name = "퀵 드로우 확률")
        for sk in [RapidFire, Headshot, Nautilus, StrangeBomb, BulletPartyTick, DeadEye, NautilusAssult]:
            sk.onAfter(QuickDrawProc)
        
        QuickDrawActivateTrigger = core.OptionalElement(partial(QuickDrawStack.judge, 1, 1), QuickDraw, name = "퀵 드로우 사용")
        QuickDrawShutdownTrigger = core.OptionalElement(QuickDraw.is_active, QuickDraw.controller(-1), name = "퀵 드로우 종료")
        for sk in [Headshot, StrangeBomb, DeadEye]:
            sk.onBefore(QuickDrawActivateTrigger)
            sk.onJustAfter(QuickDrawShutdownTrigger)

        #노틸러스 어썰트
        NautilusAssult.onAfter(NautilusAssult_2)
        NautilusAssult.onAfter(core.OptionalElement(partial(Nautilus.is_cooltime_left, 8000, -1), Nautilus.controller(8000), name = "노틸러스 쿨타임 8초"))
        Nautilus.onAfter(core.OptionalElement(partial(NautilusAssult.is_cooltime_left, 8000, -1), NautilusAssult.controller(8000), name = "노틸러스 어썰트 쿨타임 8초"))

        #불릿파티
        BulletParty.onAfter(core.RepeatElement(BulletPartyTick, 11820 // BULLET_PARTY_TICK))

        return (RapidFire,
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    SummonCrewBuff, PirateStyle, Booster, InfiniteBullet, LuckyDice, UnwierdingNectar, EpicAdventure, PirateFlag, Overdrive,
                    QuickDraw, globalSkill.soul_contract()] +\
                [BattleshipBomber, Headshot, Nautilus, DeadEye, StrangeBomb] +\
                [OctaQuaterdeck, BattleshipBomber_1, BattleshipBomber_2, NautilusAssult, NautilusAssult_2, SummonCrew] +\
                [BulletParty] +\
                [RapidFire])