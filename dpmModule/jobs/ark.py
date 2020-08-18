from ..kernel import core
from ..kernel.policy import TypebaseFetchingPolicy
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, MutualRule, ConcurrentRunRule
from . import globalSkill
from .jobbranch import pirates
from . import jobutils

class ReturningHateWrapper(core.DamageSkillWrapper):
    def __init__(self, vEhc):
        self.vEhc = vEhc
        self.stack = 0
        self._max = 12
        skill = core.DamageSkill("돌아오는 증오", 0, 320, 6, cooltime=12000).setV(vEhc, 0, 2, True)
        super(ReturningHateWrapper, self).__init__(skill)
        self.modifierInvariantFlag = False
        
    def _use(self, rem = 0, red = 0):
        self.cooltimeLeft = self.skill.cooltime * (1-0.01*red*self.skill.red)
        if self.cooltimeLeft > 0:
            self.available = False
        
        mdf = self.skill.get_modifier()
        stack = self.stack
        self.stack = 0
        return core.ResultObject(0, mdf.copy(), 320, sname = self._id, spec = 'deal', hit = 6 * stack)
        
    def _addStack(self, d):
        self.stack = min(self.stack + d, self._max)
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname = self.skill.name, spec = 'graph control')
    
    def addStack(self, d):
        return core.TaskHolder(core.Task(self, partial(self._addStack, d)), name = '돌아오는 증오 추가')

class JobGenerator(ck.JobGenerator):
    def __init__(self, vEhc = None):
        super(JobGenerator, self).__init__(vEhc = vEhc)
        self.jobtype = "str"
        self.vEnhanceNum = 12
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'mess')
        
        self.preEmptiveSkills = 2

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(crit=20)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('근원의 기억', '차지 스펠 앰플리피케이션'), RuleSet.BASE)
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
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 3, 4)
    
        return [MagicCircuit, MisticArtsMastery, 
                                    NuckleMastery, PhisicalTraining, 
                                    FusionProgress, NuckleExpret, FusionComplete, BattleRage, LoadedDicePassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -5)        
        
        return [WeaponConstant, Mastery]        
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        연계 시 플레인 차지드라이브 540 → 240ms, 끝나지 않는 흉몽 540 → 180ms

        스펠 불릿 수동 사용
        
        하이퍼 : 배틀아츠-리인포스, 보스킬러, 이그노어 가드 / 엑스트라 힐링, 인핸스
        
        5차 중요도 순서
        
        인피니티스펠 -  근원 - 새어나오는 악몽/흉몽 - 로디드 - 매서풀
        
        5차 강화 
        
        다가오는 죽음/돌아오는 증오 - 끝나지 않는 악몽/흉몽 - 플레인 차지드라이브 - 공포/구속/고통 
        - 스칼렛/상처 - 거스트/굶주림 - 어비스/혼돈 - 충동/본능
        
        '''
        
        BattleArtsHyper = core.CharacterModifier(pdamage=20, boss_pdamage=20, armor_ignore=20)  # 하이퍼 - 배틀아츠 modifier
        SpellBullet = core.CharacterModifier(pdamage=20)


        # Buff skills
        ContactCaravan = core.BuffSkill("컨택트 카라반", 720, 300 * 1000, cooltime = 500 * 1000, pdamage = 2 + 1).wrap(core.BuffSkillWrapper)
        SpectorState = core.BuffSkill("스펙터 상태", 0, 45000/112*210/2, att = 30, cooltime = 210/2 * 1000, rem = False, red = False).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill("부스터", 0, 200 * 1000).wrap(core.BuffSkillWrapper)
        

        # 일반 공격들        
        EndlessNightmare = core.DamageSkill("끝나지 않는 악몽", 540, 440, 6, cooltime = 2000, modifier=BattleArtsHyper).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        EndlessNightmare_Link = core.DamageSkill("끝나지 않는 악몽(연계)", 540, 440, 6, cooltime = 2000, modifier=BattleArtsHyper).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        PlainChargeDrive = core.DamageSkill('플레인 차지드라이브', 540, 610, 3, modifier=BattleArtsHyper).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        PlainChargeDrive_Link = core.DamageSkill('플레인 차지드라이브(연계)', 240, 610, 3, modifier=BattleArtsHyper).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        PlainSpell = core.DamageSkill("플레인 스펠", 0, 370, 2, modifier=SpellBullet).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        PlainBuff = core.BuffSkill("플레인 버프", 0, 60 * 1000, cooltime = -1).wrap(core.BuffSkillWrapper)  # dpm에 영향을 주지 않아 미사용
        
        ScarletChargeDrive = core.DamageSkill("스칼렛 차지드라이브", 540, 350, 3, cooltime = 3000, modifier=BattleArtsHyper).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletChargeDrive_Link = core.DamageSkill("스칼렛 차지드라이브(연계)", 510, 350, 3, cooltime = 3000, modifier=BattleArtsHyper).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletChargeDrive_After = core.DamageSkill("스칼렛 차지드라이브(후속타)", 0, 350, 3, modifier=BattleArtsHyper).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletSpell = core.DamageSkill("스칼렛 스펠", 0, 220, 5, modifier=SpellBullet).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletBuff = core.BuffSkill("스칼렛 버프", 0, 60 * 1000, cooltime = -1, att = 30, crit = 20).wrap(core.BuffSkillWrapper)
        
        UnstoppableImpulse = core.DamageSkill("멈출 수 없는 충동", 540, 435, 5).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        UnstoppableImpulse_Link = core.DamageSkill("멈출 수 없는 충동(연계)", 540, 435, 5).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)

        GustChargeDrive = core.DamageSkill("거스트 차지드라이브", 450, 400, 6, cooltime = 5000, modifier=BattleArtsHyper).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        GustChargeDrive_Link = core.DamageSkill("거스트 차지드라이브(연계)", 450, 400, 6, cooltime = 5000, modifier=BattleArtsHyper).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        GustSpell = core.DamageSkill('거스트 스펠', 0, 230, 4, modifier=SpellBullet).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        GustBuff = core.BuffSkill("거스트 버프", 0, 60*1000, cooltime = -1).wrap(core.BuffSkillWrapper) # dpm에 영향을 주지 않아 미사용        
        
        AbyssChargeDrive = core.DamageSkill("어비스 차지드라이브", 630, 340, 4, cooltime = 9000, modifier=BattleArtsHyper).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        AbyssChargeDrive_Link = core.DamageSkill("어비스 차지 드라이브(연계)", 630, 340, 4, cooltime = 9000, modifier=BattleArtsHyper).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        AbyssChargeDrive_After = core.DamageSkill("어비스 차지드라이브(후속타)", 0, 410, 6, modifier=BattleArtsHyper).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        AbyssSpell = core.SummonSkill("어비스 스펠", 0, 300*0.75, 70, 2, 3000, cooltime = -1, modifier=SpellBullet).setV(vEhc, 6, 2, False).wrap(core.SummonSkillWrapper)
        AbyssBuff = core.BuffSkill("어비스 버프", 0, 60*1000, cooltime = -1, pdamage = 20, boss_pdamage = 30, armor_ignore = 20).wrap(core.BuffSkillWrapper)

        
        ##### 스펙터 상태일 때 #####
        UpcomingDeath = core.DamageSkill("다가오는 죽음", 0, 450, 2).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        ReturningHate = ReturningHateWrapper(vEhc)

        EndlessBadDream = core.DamageSkill("끝나지 않는 흉몽", 540, 445, 6, modifier=BattleArtsHyper).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper) # 끝나지 않는 악몽 변형
        EndlessBadDream_Link = core.DamageSkill("끝나지 않는 흉몽(연계)", 180, 445, 6, modifier=BattleArtsHyper).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper) # 끝나지 않는 악몽 변형

        UncurableHurt = core.DamageSkill("지워지지 않는 상처", 480, 510, 6, cooltime = 3000, modifier=BattleArtsHyper).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)  #스칼렛 차지 드라이브의 변형
        UncurableHurt_Link = core.DamageSkill("지워지지 않는 상처(연계)", 480, 510, 6, cooltime = 3000, modifier=BattleArtsHyper).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        
        TenaciousInstinct = core.DamageSkill("멈출 수 없는 본능", 540, 460, 6, modifier=BattleArtsHyper).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        TenaciousInstinct_Link = core.DamageSkill("멈출 수 없는 본능(연계)", 540, 460, 6, modifier=BattleArtsHyper).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        
        UnfulfilledHunger = core.DamageSkill("채워지지 않는 굶주림", 750, 510, 7, cooltime = 5000, modifier=BattleArtsHyper).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)  #거스트 차지 드라이브 변형
        UnfulfilledHunger_Link = core.DamageSkill("채워지지 않는 굶주림(연계)", 660, 320, 7, cooltime = 5000, modifier=BattleArtsHyper).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        
        CrawlingFear = core.DamageSkill("기어 다니는 공포", 30 + 630, 1390, 12, cooltime = 60*1000, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        CrawlingFear_Link = core.DamageSkill("기어 다니는 공포(연계)", 30 + 360, 1390, 12, cooltime = 60*1000, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)

        UncontrollableChaos = core.DamageSkill("걷잡을 수 없는 혼돈", 810, 440, 12, cooltime = 9000, modifier=BattleArtsHyper).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper) #어비스 차지 드라이브 변형
        UncontrollableChaos_Link = core.DamageSkill("걷잡을 수 없는 혼돈(연계)", 720, 440, 12, cooltime = 9000, modifier=BattleArtsHyper).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)

        RaptRestriction = core.DamageSkill("황홀한 구속", 690, 600, 6, cooltime = 180 * 1000, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        RaptRestrictionSummon = core.SummonSkill("황홀한 구속(소환)", 0, 450, 400, 3, 9000, cooltime = -1, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)  #임의주기 300ms, DPM 미사용.
        RaptRestrictionEnd = core.DamageSkill("황홀한 구속(종결)", 0, 1000, 8, cooltime = -1, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)

        # 충동/본능의 쿨타임 공유와 연속 2회 사용 구현을 위한 연결용 스킬
        Impulse1 = core.DamageSkill("충동/본능 1회", 0, 0, 0, cooltime = 6000 + 540 + 180).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        Impulse2 = core.DamageSkill("충동/본능 2회", 0, 0, 0, cooltime = 6000).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        
        # 하이퍼
        ChargeSpellAmplification = core.BuffSkill("차지 스펠 앰플리피케이션", 720, 60000, att = 30, crit = 20, pdamage = 20, armor_ignore = 20, boss_pdamage = 30, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)
        
        EndlessPain = core.DamageSkill("끝없는 고통", 30, 0, 0, cooltime = 3030 + 60 * 1000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)   # onTick==> 다가오는 죽음
        EndlessPainTick = core.DamageSkill("끝없는 고통(틱)", 200,  300, 3).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)   #15타
        EndlessPainEnd = core.DamageSkill("끝없는 고통(종결)", 1200, 500*3.5, 12).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper) # 딜레이 : 1200ms 또는 1050ms(이후 연계 시). 일단 1200으로.
        EndlessPainEnd_Link = core.DamageSkill("끝없는 고통(종결,연계)", 1050, 500*3.5, 12).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        
        WraithOfGod = core.BuffSkill("레이스 오브 갓", 0, 60*1000, pdamage = 10, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)
        
        # 5차
        LuckyDice = core.BuffSkill("럭키 다이스", 0, 180*1000, pdamage = 20).isV(vEhc,3,4).wrap(core.BuffSkillWrapper)
    
        #오버드라이브 (앱솔 가정)
        #TODO: 템셋을 읽어서 무기별로 다른 수치 적용하도록 만들어야 함.
        WEAPON_ATT = jobutils.get_weapon_att("너클")
        Overdrive, OverdrivePenalty = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
    
        MagicCircuitFullDrive = core.BuffSkill("매직 서킷 풀드라이브", 720, (30+vEhc.getV(4,3))*1000, pdamage = (20 + vEhc.getV(4,3)), cooltime = 200*1000).isV(vEhc,4,3).wrap(core.BuffSkillWrapper)
        MagicCircuitFullDriveStorm = core.DamageSkill("매직 서킷 풀드라이브(마력 폭풍)", 0, 500+20*vEhc.getV(4,3), 3, cooltime=4000).wrap(core.DamageSkillWrapper)
                
        MemoryOfSource = core.DamageSkill("근원의 기억", 0, 0, 0, cooltime = 200 * 1000).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        MemoryOfSourceTick = core.DamageSkill("근원의 기억(틱)", 250, 400 + 16 * vEhc.getV(1,1), 6).wrap(core.DamageSkillWrapper)    # 43타
        MemoryOfSourceEnd = core.DamageSkill("근원의 기억(종결)", 0, 1200 + 48 * vEhc.getV(1,1), 12 * 6).wrap(core.DamageSkillWrapper)
        MemoryOfSourceBuff = core.BuffSkill("근원의 기억(버프)", 0, 30 * 1000, cooltime = -1).wrap(core.BuffSkillWrapper) #정신력 소모되지 않음
                
        InfinitySpell = core.BuffSkill("인피니티 스펠", 720, (40 + 2*vEhc.getV(0,0)) * 1000, cooltime = 240 * 1000).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        
        EvanescentNightmare = core.DamageSkill("새어 나오는 악몽", 0, 500 + 20*vEhc.getV(2,2), 9, cooltime = 10 * 1000).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        EvanescentBadDream = core.DamageSkill("새어 나오는 흉몽", 0, 600 + 24*vEhc.getV(2,2), 9, cooltime = 10 * 1000).wrap(core.DamageSkillWrapper)
        
        # 쿨감스킬인 스칼렛/상처, 거스트/굶주림, 본능이 새악흉 1회 동안 자주 사용될 수 있어 미리 쿨감시킴
        EvanescentNightmareTimer = core.BuffSkill("새어 나오는 악몽(타이머)", 0, 10000 - 1000 - 1000, cooltime = -1).wrap(core.BuffSkillWrapper)
        EvanescentBadDreamTimer = core.BuffSkill("새어 나오는 흉몽(타이머)", 0, 10000 - 1000 - 1000 - 1000, cooltime = -1).wrap(core.BuffSkillWrapper)   #악몽만 사용 가정

        # 기본 연결 설정(스펙터)
        for skill in [UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link]:
            skill.onBefore(EndlessBadDream_Link)
        # 흉몽(스펙터)과 플레인(레프)에서도 연계 가능한 스킬
        for skill in [CrawlingFear_Link, RaptRestriction, EndlessPain, MemoryOfSource]:
            skill.onBefore(core.OptionalElement(SpectorState.is_active, EndlessBadDream_Link, PlainChargeDrive_Link))
  
        # 보스 1:1 시 공격 1회 당 다가오는 죽음 1개 생성, 인피니티 스펠 상태 시 강화레벨에 따라 총 3 ~ 4개 생성
        UpcomingDeath_Connected = core.OptionalElement(InfinitySpell.is_active, core.RepeatElement(UpcomingDeath, 3 + vEhc.getV(0,0) // 25), UpcomingDeath)
        UpcomingDeath.onAfter(ReturningHate.addStack(0.2))
        

        # 기본 연결 설정(레프)
        for skill in [EndlessNightmare_Link, ScarletChargeDrive_Link, GustChargeDrive_Link, AbyssChargeDrive_Link, UnstoppableImpulse_Link]:
            skill.onBefore(PlainChargeDrive_Link)
        
        # 인피니티 스펠 상태 시 스펠 불릿 스택에는 해당 스펠 1칸 + 플레인 스펠 4칸이 채워짐
        PlainSpell_Connected = core.OptionalElement(InfinitySpell.is_active, core.RepeatElement(PlainSpell, 5), PlainSpell)
        for skill in [ScarletSpell, GustSpell, AbyssSpell]:
            skill.onAfter(core.OptionalElement(InfinitySpell.is_active, core.RepeatElement(PlainSpell, 4)))

        PlainChargeDrive.onAfter(PlainSpell_Connected)
        PlainChargeDrive_Link.onAfter(PlainSpell_Connected)
        
        ScarletSpell.onAfter(ScarletBuff)  
        ScarletChargeDrive.onAfter(ScarletSpell)
        ScarletChargeDrive_Link.onAfter(ScarletSpell)      
        ScarletChargeDrive.onAfter(ScarletChargeDrive_After)

        GustChargeDrive.onAfter(GustSpell)
        GustChargeDrive_Link.onAfter(GustSpell)
        
        AbyssSpell.onAfter(AbyssBuff)
        AbyssChargeDrive.onAfter(AbyssSpell)
        AbyssChargeDrive_Link.onAfter(AbyssSpell)
        AbyssChargeDrive.onAfter(AbyssChargeDrive_After)
        
        # 충동/본능 연결 설정
        Impulse1_Connect = core.OptionalElement(SpectorState.is_active, TenaciousInstinct_Link, 
            core.OptionalElement(InfinitySpell.is_not_active,UnstoppableImpulse_Link))  # 인피 상태에서는 충동을 사용하지 않음
        Impulse1.onAfter(Impulse1_Connect)
        Impulse2.onConstraint(core.ConstraintElement("충동/본능 연속 2회", Impulse1_Connect, Impulse1.is_not_usable))
        Impulse2_Connect = core.OptionalElement(SpectorState.is_active, TenaciousInstinct_Link, 
            core.OptionalElement(InfinitySpell.is_not_active,UnstoppableImpulse_Link))  # 인피 상태에서는 충동을 사용하지 않음
        Impulse2.onAfter(Impulse2_Connect)

        RaptRestriction.onAfter(RaptRestrictionSummon)
        RaptRestriction.onAfter(RaptRestrictionEnd)
        
        EndlessPain.onAfter(core.RepeatElement(EndlessPainTick, 15))
        EndlessPain.onAfter(EndlessPainEnd_Link)
        
        MagicCircuitFullDriveStorm.onConstraint(core.ConstraintElement('매서풀 버프가 지속되는 동안에만 마력 폭풍 발생', MagicCircuitFullDrive, MagicCircuitFullDrive.is_active))  

        # 스펙터 상태 파이널어택류 연계
        for skill in [EndlessBadDream, EndlessBadDream_Link, EvanescentBadDream,
            UncurableHurt, UnfulfilledHunger, UncontrollableChaos, TenaciousInstinct, 
            UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link,
            CrawlingFear_Link, EndlessPainTick, EndlessPainEnd, EndlessPainEnd_Link]:
            skill.onAfter(UpcomingDeath_Connected)
        MagicCircuitFullDriveStorm.onAfter(core.OptionalElement(SpectorState.is_active, UpcomingDeath_Connected))
        
        # 5차 - 새어나오는 악몽 / 흉몽 연계
        for skill in [EndlessNightmare, EndlessNightmare_Link]:
            skill.onAfter(core.OptionalElement(EvanescentNightmareTimer.is_not_active, EvanescentNightmare))
        for skill in [EndlessBadDream, EndlessBadDream_Link]:
            skill.onAfter(core.OptionalElement(EvanescentBadDreamTimer.is_not_active, EvanescentBadDream))
        EvanescentBadDream.onAfter(EvanescentBadDreamTimer)
        EvanescentNightmare.onAfter(EvanescentNightmareTimer)

        # 쿨감스킬인 스칼렛/상처, 거스트/굶주림, 본능이 새악흉 1회 동안 더 자주 사용될 수 있어 미리 쿨감시킴
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
        
        # 기본 공격 : 540ms 중립스킬
        PlainAttack = core.DamageSkill("기본 공격", 0, 0, 0).wrap(core.DamageSkillWrapper)
        PlainAttack.onAfter(core.OptionalElement(SpectorState.is_active, EndlessBadDream, PlainChargeDrive))
        
        # Constraint 추가하기 : 레프 모드
        for skill in [PlainChargeDrive, EndlessNightmare, ScarletChargeDrive, GustChargeDrive, AbyssChargeDrive, UnstoppableImpulse,
                PlainChargeDrive_Link, EndlessNightmare_Link, ScarletChargeDrive_Link, GustChargeDrive_Link, AbyssChargeDrive_Link, UnstoppableImpulse_Link]:
            
            skill.onConstraint(core.ConstraintElement("레프 모드", SpectorState, SpectorState.is_not_active) )
        
        # Constraint 추가하기 : 스펙터 모드
        for skill in [EndlessBadDream, UncurableHurt, UnfulfilledHunger, UncontrollableChaos, TenaciousInstinct, ReturningHate,
                EndlessBadDream_Link, UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link]:
            skill.onConstraint(core.ConstraintElement("스펙터 모드", SpectorState, SpectorState.is_active) )

        MemoryOfSource.onConstraint(core.ConstraintElement("스펙터 모드", SpectorState, SpectorState.is_active) )
        
        def MemoryOfSourceHandleSpector(spector_state, time):
            spector_state.timeLeft += time
            spector_state.cooltimeLeft += time
            return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname = 'Graph Element', spec = 'graph control')
        
        MemoryOfSource.onAfter(core.TaskHolder(core.Task(SpectorState, partial(MemoryOfSourceHandleSpector, SpectorState, 30*1000)), "30초 더 지속" ))                
        MemoryOfSource.onAfter(core.RepeatElement(MemoryOfSourceTick, 43))
        MemoryOfSource.onAfter(MemoryOfSourceEnd)
        MemoryOfSource.onAfter(MemoryOfSourceBuff)

        ScarletBuff.set_disabled_and_time_left(0)
        AbyssBuff.set_disabled_and_time_left(0)
        
        return(PlainAttack, 
                [ContactCaravan, ScarletBuff, AbyssBuff, SpectorState, Booster,
                    ChargeSpellAmplification, WraithOfGod,
                    LuckyDice, Overdrive, OverdrivePenalty,
                    MagicCircuitFullDrive, MemoryOfSourceBuff,
                    InfinitySpell,
                    globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes()
                    ] +\
                [EndlessNightmare_Link, ScarletChargeDrive_Link, GustChargeDrive_Link, AbyssChargeDrive_Link, 
                    CrawlingFear_Link, MemoryOfSource, EndlessPain, RaptRestriction, ReturningHate, Impulse1, Impulse2,
                    UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, 
                    AbyssSpell, RaptRestrictionSummon
                    ] +\
                [MagicCircuitFullDriveStorm] +\
                [EvanescentBadDreamTimer, EvanescentNightmareTimer] +\
                [PlainAttack])