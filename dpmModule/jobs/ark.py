from ..kernel import core
from ..kernel.policy import TypebaseFetchingPolicy
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, MutualRule, ReservationRule, ConcurrentRunRule, SynchronizeRule
from . import globalSkill
from .jobbranch import pirates
from . import jobutils

class JobGenerator(ck.JobGenerator):
    def __init__(self, vEhc = None):
        super(JobGenerator, self).__init__(vEhc = vEhc)
        self.jobtype = "str"
        self.vEnhanceNum = 12
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'mess')
        
        self.preEmptiveSkills = 2

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('근원의 기억', '차지 스펠 엠플리피케이션'), RuleSet.BASE)
        ruleset.add_rule(MutualRule('인피니티 스펠', '근원의 기억'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('매직 서킷 풀드라이브', '인피니티 스펠'), RuleSet.BASE)

        return ruleset

    def get_passive_skill_list(self):
        vEhc = self.vEhc
        
        # 매직 서킷: 앱솔 기준 15.4
        WEAPON_ATT = jobutils.get_weapon_att("너클")
        
        MagicCircuit = core.InformedCharacterModifier("매직 서킷", att = WEAPON_ATT * 0.1)  #무기 마력의 25%, 최대치 가정.
        MisticArtsMastery = core.InformedCharacterModifier("미스틱 아츠 마스터리", att = 20)
        NuckleMastery = core.InformedCharacterModifier("너클 마스터리", att = 20)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝", stat_main = 60)
        FusionProgress = core.InformedCharacterModifier("융합 진행", pdamage_indep = 10, crit = 20)
        NuckleExpret = core.InformedCharacterModifier("너클 엑스퍼트", att = 30, crit = 20)
        FusionComplete = core.InformedCharacterModifier("융합 완성", att = 40, crit = 10, armor_ignore = 30, boss_pdamage = 30)
        BattleRage = core.InformedCharacterModifier("전투 광란", pdamage_indep = 20)
    
        return [MagicCircuit, MisticArtsMastery, 
                                    NuckleMastery, PhisicalTraining, 
                                    FusionProgress, NuckleExpret, FusionComplete, BattleRage]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -5)        
        
        return [WeaponConstant, Mastery]        
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        연계 시 플레인 차지드라이브 540 → 240ms, 끝나지 않는 흉몽 540 → 180ms
        
        하이퍼 : 배틀아츠-리인포스, 보스킬러, 이그노어 가드 / 엑스트라 힐링, 인핸스
        
        5차 중요도 순서
        
        인피니티스펠 -  근원 - 새어나오는 악몽/흉몽 - 로디드 - 매서풀
        
        5차 강화 
        
        다가오는 죽음/돌아오는 증오 - 끝나지 않는 악몽/흉몽 - 플레인 차지드라이브 - 공포/구속/고통 
        - 스칼렛/상처 - 거스트/굶주림 - 어비스/혼돈 - 충동/본능
        
        '''
        
        # Buff skills
        ContactCaravan = core.BuffSkill("컨택트 카라반", 720, 300 * 1000, cooltime = 500 * 1000, pdamage = 2 + 1).wrap(core.BuffSkillWrapper)
        SpectorState = core.BuffSkill("스펙터 상태", 0, 45000/112*210/2, att = 30, cooltime = 105 * 1000, rem = False, red = False).wrap(core.BuffSkillWrapper)
        # SpectorState = core.BuffSkill("스펙터 상태", 0, 3120, att = 30, cooltime = 13140, rem = False, red = False).wrap(core.BuffSkillWrapper)
        # SpectorState_Infinity = core.BuffSkill("스펙터 상태(인피)", 0, 12690, att = 30, cooltime = 3870, rem = False, red = False).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill("부스터", 0, 200 * 1000).wrap(core.BuffSkillWrapper)
        
        Unforgotable = core.DamageSkill("잊혀지지 않는 악몽", 540, 440, 6, cooltime = 2000).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper) # Dummy

        # 일반 공격들
        
        EndlessNightmare = core.DamageSkill("끝나지 않는 악몽", 540, 440, 6, cooltime = 2000).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        EndlessNightmare_Link = core.DamageSkill("끝나지 않는 악몽(연계)", 540, 440, 6, cooltime = 2000).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        PlainChargeDrive = core.DamageSkill('플레인 차지드라이브', 540, 610, 3).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        PlainChargeDrive_Link = core.DamageSkill('플레인 차지드라이브(연계)', 240, 610, 3, cooltime = 241).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        PlainSpell = core.DamageSkill("플레인 스펠", 0, 370, 2).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        PlainSpell_Infinity = core.DamageSkill("플레인 스펠(인피니티)", 0, 370, 2, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        PlainSpell_InfinityBonus = core.DamageSkill("플레인 스펠(인피니티+)", 0, 370, 2 * 4, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)        
        PlainBuff = core.BuffSkill("플레인 버프", 0, 60 * 1000, cooltime = -1).wrap(core.BuffSkillWrapper)
        
        ScarletChargeDrive = core.DamageSkill("스칼렛 차지드라이브", 540, 350, 3, cooltime = 3000).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletChargeDrive_After = core.DamageSkill("스칼렛 차지드라이브(후속타)", 0, 350, 3).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        
        ScarletSpell = core.DamageSkill("스칼렛 스펠", 0, 220, 5).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletSpell_Infinity = core.DamageSkill("스칼렛 스펠(인피니티)", 0, 220, 5, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        
        ScarletChargeDrive_Link = core.DamageSkill("스칼렛 차지드라이브(연계)", 510, 350, 3, cooltime = 3000).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletBuff = core.BuffSkill("스칼렛 버프", 0, 60 * 1000, cooltime = -1, att = 30, crit = 20).wrap(core.BuffSkillWrapper)
        
        GustChargeDrive = core.DamageSkill("거스트 차지드라이브", 450, 400, 6, cooltime = 5000).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        GustSpell = core.DamageSkill('거스트 스펠', 0, 230, 4).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        GustSpell_Infinity = core.DamageSkill('거스트 스펠(인피니티)', 0, 230, 4, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        GustBuff = core.BuffSkill("거스트 버프", 0, 60*1000, cooltime = -1).wrap(core.BuffSkillWrapper)
        
        GustChargeDrive_Link = core.DamageSkill("거스트 차지드라이브(연계)", 450, 400, 6, cooltime = 5000).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        
        CrawlingFear = core.DamageSkill("기어 다니는 공포", 30 + 630, 1390, 12, cooltime = 60*1000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        CrawlingFear_Link = core.DamageSkill("기어 다니는 공포(연계)", 30 + 360, 1390, 12, cooltime = 60*1000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        
        AbyssChargeDrive = core.DamageSkill("어비스 차지드라이브", 630, 340, 4, cooltime = 9000).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        AbyssChargeDrive_After = core.DamageSkill("어비스 차지드라이브(후속타)", 0, 410, 6).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        
        AbyssSpell = core.SummonSkill("어비스 스펠", 0, 300*0.75, 70, 2, 3000, cooltime = -1).setV(vEhc, 6, 2, False).wrap(core.SummonSkillWrapper)
        AbyssSpell_Infinity = core.SummonSkill("어비스 스펠(인피니티)", 0, 300*0.75, 70, 2, 3000, cooltime = -1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 6, 2, False).wrap(core.SummonSkillWrapper)
        
        AbyssChargeDrive_Link = core.DamageSkill("어비스 차지 드라이브(연계)", 630, 340, 4, cooltime = 9000).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        
        AbyssBuff = core.BuffSkill("어비스 버프", 0, 60*1000, cooltime = -1, pdamage = 20, boss_pdamage = 30, armor_ignore = 20).wrap(core.BuffSkillWrapper)
        
        RaptRestriction = core.DamageSkill("황홀한 구속", 690, 600, 6, cooltime = 180 * 1000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        RaptRestrictionSummon = core.SummonSkill("황홀한 구속(소환)", 0, 450, 400, 3, 9000, cooltime = -1).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)  #임의주기 300ms, DPM 미사용.
        RaptRestrictionEnd = core.DamageSkill("황홀한 구속(종결)", 0, 1000, 8, cooltime = -1).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        
        ##### 스펙터 상태일 때 #####
        UpcomingDeath = core.DamageSkill("다가오는 죽음", 0, 450, 2).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        ReturningHate = core.DamageSkill("돌아오는 증오", 0, 320, 6 * 0.2).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)    #12초당 최대 12회
        ReturningHate_Infinity = core.DamageSkill("돌아오는 증오(인피니티)", 0, 320, 6 * 12, cooltime = 12*1000).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)

        UncurableHurt = core.DamageSkill("지워지지 않는 상처", 480, 510, 6, cooltime = 3000).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)  #스칼렛 차지 드라이브의 변형
        UncurableHurt_Link = core.DamageSkill("지워지지 않는 상처(연계)", 480, 510, 6, cooltime = 3000).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        
        EndlessBadDream = core.DamageSkill("끝나지 않는 흉몽", 540, 445, 6).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper) # 끝나지 않는 악몽 변형
        EndlessBadDream_Link = core.DamageSkill("끝나지 않는 흉몽(연계)", 180, 445, 6, cooltime = 181).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper) # 끝나지 않는 악몽 변형
        
        UnfulfilledHunger = core.DamageSkill("채워지지 않는 굶주림", 750, 510, 7, cooltime = 5000).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)  #거스트 차지 드라이브 변형
        UnfulfilledHunger_Link = core.DamageSkill("채워지지 않는 굶주림(연계)", 660, 320, 7, cooltime = 5000).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        
        UncontrollableChaos = core.DamageSkill("겉잡을 수 없는 혼돈", 810, 440, 12, cooltime = 9000).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper) #어비스 차지 드라이브 변형
        UncontrollableChaos_Link = core.DamageSkill("겉잡을 수 없는 혼돈(연계)", 720, 440, 12, cooltime = 9000).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        
        # 서로 쿨타임을 공유함
        Impulse1 = core.DamageSkill("충동/본능 1회", 0, 0, 0, cooltime = 6000 + 540 + 180).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        Impulse2 = core.DamageSkill("충동/본능 2회", 0, 0, 0, cooltime = 6000).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        UnstoppableImpulse = core.DamageSkill("멈출 수 없는 충동", 540, 435, 5).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        UnstoppableImpulse_Link = core.DamageSkill("멈출 수 없는 충동(연계)", 540, 435, 5).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        TenaciousInstinct = core.DamageSkill("멈출 수 없는 본능", 540, 460, 6).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        TenaciousInstinct_Link = core.DamageSkill("멈출 수 없는 본능(연계)", 540, 460, 6).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        
        
        # 하이퍼
        ChargeSpellAmplification = core.BuffSkill("차지 스펠 엠플리피케이션", 720, 60000, att = 30, crit = 20, pdamage = 20, armor_ignore = 20, boss_pdamage = 30, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)
        

        EndlessPain = core.DamageSkill("끝없는 고통", 30, 0, 0, cooltime = 3030 + 60 * 1000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)   # onTick==> 다가오는 죽음
        EndlessPainTick = core.DamageSkill("끝없는 고통(틱)", 200,  300, 3).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)   #15타
        EndlessPainEnd = core.DamageSkill("끝없는 고통(종결)", 1200, 500*3.5, 12).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper) # 딜레이 : 1200ms 또는 1050ms(이후 연계 시). 일단 1200으로.
        EndlessPainEnd_Link = core.DamageSkill("끝없는 고통(종결,연계)", 1050, 500*3.5, 12).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        
        WraithOfGod = core.BuffSkill("레이스 오브 갓", 0, 60*1000, pdamage = 10, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)
        
        # 5차
        LuckyDice = core.BuffSkill("럭키 다이스", 0, 180*1000, pdamage = 20).isV(vEhc,3,3).wrap(core.BuffSkillWrapper)
        # 로디드 강화순서 확인필요
        #LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 1, 2)
    
        #오버드라이브 (앱솔 가정)
        #TODO: 템셋을 읽어서 무기별로 다른 수치 적용하도록 만들어야 함.
        WEAPON_ATT = jobutils.get_weapon_att("너클")
        Overdrive, OverdrivePenalty = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
    
        MagicCircuitFullDrive = core.BuffSkill("매직 서킷 풀드라이브", 720, (30+vEhc.getV(4,4))*1000, pdamage = (20 + vEhc.getV(3,2)), cooltime = 200*1000).isV(vEhc,4,4).wrap(core.BuffSkillWrapper)
        MagicCircuitFullDriveStorm = core.DamageSkill("매직 서킷 풀드라이브(마력 폭풍)", 0, 500+20*vEhc.getV(4,4), 3, cooltime=4000).wrap(core.DamageSkillWrapper)
        
        
        MemoryOfSource = core.DamageSkill("근원의 기억", 0, 0, 0, cooltime = 200 * 1000).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        MemoryOfSourceTick = core.DamageSkill("근원의 기억(틱)", 250, 400 + 16 * vEhc.getV(1,1), 6).wrap(core.DamageSkillWrapper)    # 43타
        MemoryOfSourceEnd = core.DamageSkill("근원의 기억(종결)", 0, 1200 + 48 * vEhc.getV(1,1), 12 * 6).wrap(core.DamageSkillWrapper)
        MemoryOfSourceBuff = core.BuffSkill("근원의 기억(버프)", 0, 30 * 1000, cooltime = -1).wrap(core.BuffSkillWrapper) #정신력 소모되지 않음
        
        
        InfinitySpell = core.BuffSkill("인피니티 스펠", 720, (40 + 2*vEhc.getV(0,0)) * 1000, cooltime = 240 * 1000).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        #스펠이 남은 수많큼 차지됨
        #심연의 기운은 세개씩 추가 생성됨
        
        EvanescentNightmare = core.DamageSkill("새어 나오는 악몽", 0, 500 + 20*vEhc.getV(2,2), 9, cooltime = 10 * 1000).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        EvanescentBadDream = core.DamageSkill("새어나오는 흉몽", 0, 600 + 24*vEhc.getV(2,2), 9, cooltime = 10 * 1000).wrap(core.DamageSkillWrapper)
        
        # 쿨감스킬인 스칼렛/상처, 거스트/굶주림, 본능의 가동률이 높아서 미리 쿨감시킴
        EvanescentNightmareTimer = core.BuffSkill("새어나오는 악몽(타이머)", 0, 10000 - 1000 - 1000, cooltime = -1).wrap(core.BuffSkillWrapper)
        EvanescentBadDreamTimer = core.BuffSkill("새어나오는 흉몽(타이머)", 0, 10000 - 1000 - 1000 - 1000, cooltime = -1).wrap(core.BuffSkillWrapper)   #악몽만 사용 가정

        # 기본 연결 설정(스펙터)
        for skill in [UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link]:
            skill.onBefore(EndlessBadDream_Link)
        # # 레프 모드의 플레인 차지드라이브에서도 연계 가능한 스킬
        for skill in [CrawlingFear_Link, RaptRestriction, EndlessPain, MemoryOfSource]:
            skill.onBefore(core.OptionalElement(SpectorState.is_active, EndlessBadDream_Link, PlainChargeDrive_Link))
        # 연계 가능한 스킬들이 모두 쿨다운 중이면 540ms짜리 흉몽이 발동
        for skill in [UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link,
            CrawlingFear_Link, RaptRestriction, EndlessPain, MemoryOfSource]:
            EndlessBadDream_Connected = core.OptionalElement(skill.is_not_usable, EndlessBadDream, EndlessBadDream_Link)

        # # onAfter(흉몽(연계))과 onBefore(흉몽(연계)) 사이에 연계 스킬이 들어가지 않아서 제거
        # for skill in [UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link,
        #     CrawlingFear_Link, EndlessPainEnd_Link]:
        #     skill.onAfter(EndlessBadDream_Connected)
  
        # 보스 1:1 시 공격 1회 당 다가오는 죽음 1개 생성, 인피니티 스펠 상태 시 3 ~ 4개
        UpcomingDeath_Connected = core.OptionalElement(InfinitySpell.is_active, core.RepeatElement(UpcomingDeath, 3 + round(vEhc.getV(0,0)/25)), UpcomingDeath)
        # 인피니티 스펠 상태 시 돌아오는 증오 12초에 12개로 제한
        UpcomingDeath.onAfter(core.OptionalElement(InfinitySpell.is_not_active, ReturningHate))
        ReturningHate_Infinity.onConstraint(core.ConstraintElement("증오 최대생성 제한", InfinitySpell, InfinitySpell.is_active))
        
        # 기본 연결 설정(레프)
        # 연계 가능한 스킬들이 모두 쿨다운 중이면 540ms짜리 플레인 차지드라이브가 발동
        for skill in [EndlessNightmare_Link, ScarletChargeDrive_Link, GustChargeDrive_Link, AbyssChargeDrive_Link, UnstoppableImpulse_Link]:
            skill.onBefore(PlainChargeDrive_Link)
            PlainChargeDrive_Connected = core.OptionalElement(skill.is_not_usable, PlainChargeDrive, PlainChargeDrive_Link)
        
        PlainSpell_Connected = core.OptionalElement(InfinitySpell.is_active, PlainSpell_Infinity, PlainSpell)
        #PlainSpell.onAfter(PlainBuff)
        PlainChargeDrive.onAfter(PlainSpell_Connected)
        PlainChargeDrive_Link.onAfter(PlainSpell_Connected)
        
        ScarletSpell_Connected = core.OptionalElement(InfinitySpell.is_active, ScarletSpell_Infinity, ScarletSpell)
        ScarletSpell_Connected.onAfter(ScarletBuff)  
        ScarletChargeDrive.onAfter(ScarletSpell_Connected)
        ScarletChargeDrive_Link.onAfter(ScarletSpell_Connected)      
        ScarletChargeDrive.onAfter(ScarletChargeDrive_After)

        GustSpell_Connected = core.OptionalElement(InfinitySpell.is_active, GustSpell_Infinity, GustSpell)
        # GustSpell.onAfter(GustBuff)
        GustChargeDrive.onAfter(GustSpell_Connected)
        GustChargeDrive_Link.onAfter(GustSpell_Connected)
        
        AbyssSpell_Connected = core.OptionalElement(InfinitySpell.is_active, AbyssSpell_Infinity, AbyssSpell)
        AbyssSpell_Connected.onAfter(AbyssBuff)
        AbyssChargeDrive.onAfter(AbyssSpell_Connected)
        AbyssChargeDrive_Link.onAfter(AbyssSpell_Connected)
        AbyssChargeDrive.onAfter(AbyssChargeDrive_After)
        
        # 인피니티 스펠 상태 시 해당 스펠 + 플레인 스펠 2*4개 생성
        for spell in [PlainSpell_Infinity, ScarletSpell_Infinity, GustSpell_Infinity, AbyssSpell_Infinity]:
            spell.onAfter(PlainSpell_InfinityBonus)

        # 충동/본능 연결 설정
        Impulse1_Connect = core.OptionalElement(SpectorState.is_active, TenaciousInstinct_Link, 
            core.OptionalElement(InfinitySpell.is_not_active,UnstoppableImpulse_Link))
        Impulse1.onAfter(Impulse1_Connect)
        Impulse2.onConstraint(core.ConstraintElement("충동/본능 연속 2회", Impulse1_Connect, Impulse1.is_not_usable))
        Impulse2_Connect = core.OptionalElement(SpectorState.is_active, TenaciousInstinct_Link, 
            core.OptionalElement(InfinitySpell.is_not_active,UnstoppableImpulse_Link))
        Impulse2.onAfter(Impulse2_Connect)
        # UnstoppableImpulse_Link.onConstraint(core.ConstraintElement("인피 상태에서는 충동 미사용", InfinitySpell, InfinitySpell.is_not_active))

        RaptRestriction.onAfter(RaptRestrictionSummon)
        RaptRestriction.onAfter(RaptRestrictionEnd)
        
        EndlessPain.onAfter(core.RepeatElement(EndlessPainTick, 15))
        EndlessPain.onAfter(EndlessPainEnd_Link)
        
        MagicCircuitFullDriveStorm.onConstraint(core.ConstraintElement('매서풀 버프가 지속되는 동안에만 마력 폭풍 발생', MagicCircuitFullDrive, MagicCircuitFullDrive.is_active))  

        # 스펙터 상태 파이널어택류 연계
        for skill in [EndlessBadDream, EndlessBadDream_Link, EvanescentBadDream,
            UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link,
            CrawlingFear_Link, EndlessPainTick, EndlessPainEnd_Link]:
            skill.onAfter(UpcomingDeath_Connected)
        MagicCircuitFullDriveStorm.onAfter(core.OptionalElement(SpectorState.is_active, UpcomingDeath_Connected))
        
        # 5차 - 새어나오는 악몽 / 흉몽 연계
        EndlessNightmare.onAfter(core.OptionalElement(EvanescentNightmareTimer.is_not_active, EvanescentNightmare) )
        for skill in [EndlessBadDream, EndlessBadDream_Link]:
            skill.onAfter(core.OptionalElement(EvanescentBadDreamTimer.is_not_active, EvanescentBadDream))
        EvanescentBadDream.onAfter(EvanescentBadDreamTimer)
        EvanescentNightmare.onAfter(EvanescentNightmareTimer)
        
        EndlessNightmare_Link.onAfter(core.OptionalElement(EvanescentNightmareTimer.is_not_active, EvanescentNightmare) )
        
        for skill in [  # ScarletChargeDrive, ScarletChargeDrive_Link, 
                        # GustChargeDrive, GustChargeDrive_Link,
                        AbyssChargeDrive, AbyssChargeDrive_Link]:
            
            skill.onAfter(EvanescentNightmareTimer.controller(1000, 'reduce_cooltime'))
        
        for skill in [  # UncurableHurt_Link, UncurableHurt,
                        # UnfulfilledHunger_Link, UnfulfilledHunger,
                        UncontrollableChaos_Link, UncontrollableChaos,
                        # TenaciousInstinct_Link, TenaciousInstinct,
                        CrawlingFear_Link, CrawlingFear]:
            
            skill.onAfter(EvanescentBadDreamTimer.controller(1000, 'reduce_cooltime'))
        
        # 기본 공격
        PlainAttack = core.DamageSkill("기본 공격", 0, 0, 0).wrap(core.DamageSkillWrapper)
        PlainAttack.onAfter(core.OptionalElement(SpectorState.is_active, EndlessBadDream_Connected, PlainChargeDrive_Connected))
        
        # Constraint 추가하기 : 레프 모드
        for skill in [PlainChargeDrive, EndlessNightmare, ScarletChargeDrive, GustChargeDrive, AbyssChargeDrive, UnstoppableImpulse,
                PlainChargeDrive_Link, EndlessNightmare_Link, ScarletChargeDrive_Link, GustChargeDrive_Link, AbyssChargeDrive_Link, UnstoppableImpulse_Link]:
            
            skill.onConstraint(core.ConstraintElement("레프 모드", SpectorState, SpectorState.is_not_active) )
        
        # Constraint 추가하기 : 스펙터 모드
        for skill in [EndlessBadDream, UncurableHurt, UnfulfilledHunger, UncontrollableChaos, TenaciousInstinct, ReturningHate_Infinity,
                EndlessBadDream_Link, UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link]:
            skill.onConstraint(core.ConstraintElement("스펙터 모드", SpectorState, SpectorState.is_active) )

        MemoryOfSource.onConstraint(core.ConstraintElement("스펙터 모드", SpectorState, SpectorState.is_active) )
        
        def MemoryOfSourceHandleSpector(spector_state, time):
            spector_state.timeLeft += time
            spector_state.cooltimeLeft += time
            return core.ResultObject(0, core.CharacterModifier(), 0, sname = 'Graph Element', spec = 'graph control')
        
        MemoryOfSource.onAfter(core.TaskHolder(core.Task(SpectorState, partial(MemoryOfSourceHandleSpector, SpectorState, 30*1000)), "30초 더 지속" ))                
        MemoryOfSource.onAfter(core.RepeatElement(MemoryOfSourceTick, 43))
        MemoryOfSource.onAfter(MemoryOfSourceEnd)
        MemoryOfSource.onAfter(MemoryOfSourceBuff)

        # def InfinitySpellHandleSpector(spector_state, remain, cooltime):    # 인피 상태에 따른 변신 스케쥴링용
        #     spector_state.timeLeft += remain
        #     spector_state.cooltimeLeft += cooltime
        #     return core.ResultObject(0, core.CharacterModifier(), 0, sname = 'Graph Element', spec = 'graph control')

        ScarletBuff.set_disabled_and_time_left(0)
        AbyssBuff.set_disabled_and_time_left(0)
        
        # InfinitySpell.onConstraint(core.ConstraintElement('근원의 기억부터 사용하도록', MemoryOfSource, MemoryOfSource.is_not_usable))   
        
        
        return(PlainAttack, 
                [ContactCaravan, ScarletBuff, AbyssBuff, SpectorState, Booster,
                    ChargeSpellAmplification, WraithOfGod,
                    LuckyDice, Overdrive, OverdrivePenalty,
                    MagicCircuitFullDrive, MemoryOfSourceBuff,
                    InfinitySpell,
                    globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes()#, globalSkill.useful_wind_booster()
                    ] +\
                [EndlessNightmare_Link, ScarletChargeDrive_Link, GustChargeDrive_Link, AbyssChargeDrive_Link, 
                    CrawlingFear_Link, MemoryOfSource, EndlessPain, RaptRestriction,ReturningHate_Infinity, Impulse1, Impulse2,
                    UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, 
                    AbyssSpell, AbyssSpell_Infinity, RaptRestrictionSummon
                    ] +\
                [MagicCircuitFullDriveStorm] +\
                [EvanescentBadDreamTimer, EvanescentNightmareTimer] +\
                [PlainAttack])