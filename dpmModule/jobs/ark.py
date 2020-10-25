from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, MutualRule, ConcurrentRunRule
from . import globalSkill
from .jobbranch import pirates
from .jobclass import flora
from . import jobutils
from math import ceil, floor

# TODO: core쪽으로 옮길 것, .wrap()과 함께 사용 가능하게 할 것
class MultipleDamageSkillWrapper(core.DamageSkillWrapper):
    def __init__(self, skill, _max, timeLimit):
        self._timeLimit = timeLimit            
        self.timer = self._timeLimit
        self._max = _max
        self.count = 0   
        super(MultipleDamageSkillWrapper, self).__init__(skill)
        
    def _use(self, skill_modifier):
        self.count += 1
        self.timer = self._timeLimit
        if self.count >= self._max:
            self.count = 0
        return super(MultipleDamageSkillWrapper, self)._use(skill_modifier)

    def spend_time(self, time):
        self.timer -= time
        if self.timer <= 0:
            self.count = 0
        super(MultipleDamageSkillWrapper, self).spend_time(time)

    def is_available(self) -> bool:
        if self.count > 0:
            return True
        return super(MultipleDamageSkillWrapper, self).is_available()
        

class DeviousWrapper(core.DamageSkillWrapper):
    def __init__(self, skill):
        self.reduceDict = set()
        super(DeviousWrapper, self).__init__(skill)
    
    def _reduceCooltime(self, time, skillId):
        if skillId not in self.reduceDict:
            self.cooltimeLeft -= time
            self.reduceDict.add(skillId)

        return self._result_object_cache

    def reduceCooltime(self, time, skillId):
        task = core.Task(self, partial(self._reduceCooltime, time, skillId))
        return core.TaskHolder(task)

    def _use(self, skill_modifier):
        self.reduceDict = set()
        return super(DeviousWrapper, self)._use(skill_modifier)

class SpectorWrapper(core.BuffSkillWrapper):
    def __init__(self, memoryBuff, endlessBuff):
        skill = core.BuffSkill("스펙터 상태", 0, 9999999, att = 30, cooltime = -1)
        self.gauge = 500
        self.memoryBuff = memoryBuff
        self.endlessBuff = endlessBuff
        self.schedule = None
        self.cooldown = 0
        self.lockdown = 0
        super(SpectorWrapper, self).__init__(skill)
        self.onoff = False

    def is_active(self):
        return self.onoff

    def spend_time(self, time):
        """
        1020ms마다 게이지가 갱신되며, 레프 상태에서는 +13, 스펙터 상태에서는 -23씩 변동.
        스펙터 잠식-엑스트라 힐링 사용 시 회복량 10% 증가.
        잠식 제어를 통한 상태 전환은 3초의 쿨타임이 있음.
        근원의 기억 시작 후 30초, 끝없는 고통 키다운 3초간은 정신력 소모되지 않음.
        """
        self.cooldown -= time
        self.lockdown -= time
        if self.onoff:
            if self.memoryBuff.is_not_active() and self.endlessBuff.is_not_active():
                self.gauge = max(self.gauge - 23 * time / 1020, 0)
        else:
            if self.lockdown <= 0:
                self.gauge = min(self.gauge + 13 * 1.1 * time / 1020, 1000) # 하이퍼 엑스트라 힐링 적용

        if self.gauge <= 0:
            self.onoff = False
            self.lockdown = 20000
            raise ValueError("The Gauge is exhausted. Fix schedule.") # 게이지 고갈시 에러 발생. 고갈을 허용하고 싶으면 제거.
        else:
            onoff = self.schedule(self.gauge)
            if self.onoff != onoff and self.cooldown <= 0:
                self.onoff = onoff
                self.cooldown = 3000

    def registerSchedule(self, schedule):
        self.schedule = schedule

    def setOnoff(self, onoff):
        self.onoff = onoff
        return self._result_object_cache
    
    def onoffController(self, onoff):
        return core.TaskHolder(core.Task(self, partial(self.setOnoff, onoff)), name = "상태 변경")
        
    def judge(self, gauge, direction):
        if (self.gauge-gauge)*direction>=0:return True
        else: return False
    
class JobGenerator(ck.JobGenerator):
    def __init__(self, vEhc = None):
        super(JobGenerator, self).__init__(vEhc = vEhc)
        self.jobtype = "str"
        self.jobname = "아크"
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

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        # 매직 서킷: 앱솔 기준 15.4
        WEAPON_ATT = jobutils.get_weapon_att("너클")
        
        MagicCircuit = core.InformedCharacterModifier("매직 서킷", att = WEAPON_ATT * 0.1)  #무기 마력의 25%, 최대치 가정.
        MisticArtsMastery = core.InformedCharacterModifier("미스틱 아츠 마스터리", att = 20)
        NuckleMastery = core.InformedCharacterModifier("너클 마스터리", att = 20)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝", stat_main = 60)
        FusionProgress = core.InformedCharacterModifier("융합 진행", pdamage_indep = 10, crit = 20)
        NuckleExpret = core.InformedCharacterModifier("너클 엑스퍼트", att = 30 + passive_level, crit_damage= 30 + passive_level)
        FusionComplete = core.InformedCharacterModifier("융합 완성", att = 40 + passive_level, crit = 10 + ceil(passive_level/3), armor_ignore = 30 + passive_level, boss_pdamage = 30 + passive_level)
        BattleRage = core.InformedCharacterModifier("전투 광란", pdamage_indep = 20 + passive_level)
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 3, 4)
    
        return [MagicCircuit, MisticArtsMastery, 
                                    NuckleMastery, PhisicalTraining, 
                                    FusionProgress, NuckleExpret, FusionComplete, BattleRage, LoadedDicePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -5 + 0.5*ceil((chtr.get_base_modifier().passive_level + self.combat)/2))
        
        return [WeaponConstant, Mastery]        
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter):
        '''
        연계 시 플레인 차지드라이브 540 → 240ms, 끝나지 않는 흉몽 540 → 180ms
        각각 +30ms 적용해 270ms, 210ms로 적용됨

        스펠 불릿 수동 사용
        
        하이퍼 : 배틀아츠-리인포스, 보스킬러, 이그노어 가드 / 엑스트라 힐링, 인핸스
        
        5차 중요도 순서
        
        인피니티스펠 -  근원 - 새어나오는 악몽/흉몽 - 로디드 - 매서풀
        
        5차 강화 
        
        다가오는 죽음/돌아오는 증오 - 끝나지 않는 악몽/흉몽 - 플레인 차지드라이브 - 공포/구속/고통 
        - 스칼렛/상처 - 거스트/굶주림 - 어비스/혼돈 - 충동/본능
        
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        LINK_DELAY = 30
        BattleArtsHyper = core.CharacterModifier(pdamage=20, boss_pdamage=20, armor_ignore=20)  # 하이퍼 - 배틀아츠 modifier
        SpellBullet = core.CharacterModifier(pdamage=20)


        # Buff skills
        ContactCaravan = core.BuffSkill("컨택트 카라반", 720, 300 * 1000, cooltime = 600 * 1000, pdamage = 2 + 1).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill("부스터", 0, 200 * 1000).wrap(core.BuffSkillWrapper)
        

        # 일반 공격들        
        EndlessNightmare_Link = core.DamageSkill("끝나지 않는 악몽(연계)", 540, 440 + 3*passive_level, 6, cooltime = 2000, red=True, modifier=BattleArtsHyper).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        PlainChargeDrive = core.DamageSkill('플레인 차지드라이브', 540, 610 + 3*passive_level, 3, modifier=BattleArtsHyper).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        PlainChargeDrive_Link = core.DamageSkill('플레인 차지드라이브(연계)', 240+LINK_DELAY, 610 + 3*passive_level, 3, modifier=BattleArtsHyper).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        PlainSpell = core.DamageSkill("플레인 스펠", 0, 370 + 3*passive_level, 2, modifier=SpellBullet).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        PlainBuff = core.BuffSkill("플레인 버프", 0, 60 * 1000, cooltime = -1).wrap(core.BuffSkillWrapper)  # dpm에 영향을 주지 않아 미사용
        
        ScarletChargeDrive = core.DamageSkill("스칼렛 차지드라이브", 540, 350 + 3*passive_level, 3, cooltime = 3000, red=True, modifier=BattleArtsHyper).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletChargeDrive_Link = core.DamageSkill("스칼렛 차지드라이브(연계)", 510, 350 + 3*passive_level, 3, cooltime = 3000, red=True, modifier=BattleArtsHyper).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletChargeDrive_After = core.DamageSkill("스칼렛 차지드라이브(후속타)", 0, 350 + 3*passive_level, 3, modifier=BattleArtsHyper).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletSpell = core.DamageSkill("스칼렛 스펠", 0, 220 + passive_level, 5, modifier=SpellBullet).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ScarletBuff = core.BuffSkill("스칼렛 버프", 0, 60 * 1000, cooltime = -1, rem=True, att = 30, crit = 20).wrap(core.BuffSkillWrapper)
        
        UnstoppableImpulse_Link = core.DamageSkill("멈출 수 없는 충동(연계)", 540, 435 + 3*passive_level, 5, cooltime = -1, modifier=BattleArtsHyper).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)

        GustChargeDrive_Link = core.DamageSkill("거스트 차지드라이브(연계)", 450, 400 + 3*passive_level, 6, cooltime = 5000, red=True, modifier=BattleArtsHyper).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        GustSpell = core.DamageSkill('거스트 스펠', 0, 230 + passive_level, 4, modifier=SpellBullet).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        GustBuff = core.BuffSkill("거스트 버프", 0, 60*1000, cooltime = -1).wrap(core.BuffSkillWrapper) # dpm에 영향을 주지 않아 미사용        
        
        AbyssChargeDrive_Link = core.DamageSkill("어비스 차지드라이브(연계)", 630, 340 + 3*self.combat, 4, cooltime = 9000, red=True, modifier=BattleArtsHyper).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        AbyssChargeDrive_After = core.DamageSkill("어비스 차지드라이브(후속타)", 0, 410 + 3*self.combat, 6, modifier=BattleArtsHyper).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        AbyssSpell = core.SummonSkill("어비스 스펠", 0, 300*0.75, 70 + 2*self.combat, 2, 3000, cooltime = -1, modifier=SpellBullet).setV(vEhc, 6, 2, False).wrap(core.SummonSkillWrapper)
        AbyssBuff = core.BuffSkill("어비스 버프", 0, 60*1000, cooltime = -1, rem=True, pdamage = 20 + floor(self.combat/2), boss_pdamage = 30 + self.combat, armor_ignore = 20 + floor(self.combat/2)).wrap(core.BuffSkillWrapper)

        
        ##### 스펙터 상태일 때 #####
        UpcomingDeath = core.DamageSkill("다가오는 죽음", 0, 450 + 3*passive_level, 2).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        ReturningHateStack = core.StackSkillWrapper(core.BuffSkill("돌아오는 증오(스택)", 0, 99999999), 12)
        ReturningHate = core.StackDamageSkillWrapper(
            core.DamageSkill("돌아오는 증오", 0, 320 + 3*passive_level, 6, cooltime=12000, red=True).setV(vEhc, 0, 2, True),
            ReturningHateStack,
            lambda sk: sk.stack
        )

        EndlessBadDream = core.DamageSkill("끝나지 않는 흉몽", 540, 445 + 3*passive_level, 6, modifier=BattleArtsHyper).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper) # 끝나지 않는 악몽 변형
        EndlessBadDream_Link = core.DamageSkill("끝나지 않는 흉몽(연계)", 180+LINK_DELAY, 445 + 3*passive_level, 6, modifier=BattleArtsHyper).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper) # 끝나지 않는 악몽 변형

        UncurableHurt_Link = core.DamageSkill("지워지지 않는 상처(연계)", 480, 510 + 3*passive_level, 6, cooltime = 3000, red=True, modifier=BattleArtsHyper).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)  #스칼렛 차지 드라이브의 변형
        
        TenaciousInstinct_Link = core.DamageSkill("멈출 수 없는 본능(연계)", 540, 460 + 3*passive_level, 6, cooltime = -1, modifier=BattleArtsHyper).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)

        UnfulfilledHunger = core.DamageSkill("채워지지 않는 굶주림", 750, 510 + 3*passive_level, 7, cooltime = 5000, red=True, modifier=BattleArtsHyper).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)  #거스트 차지 드라이브 변형
        UnfulfilledHunger_Link = core.DamageSkill("채워지지 않는 굶주림(연계)", 660, 510 + 3*passive_level, 7, cooltime = 5000, red=True, modifier=BattleArtsHyper).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        
        CrawlingFear = core.DamageSkill("기어 다니는 공포", 30 + 630, 1290 + 3*passive_level, 15, cooltime = 60*1000, red=True, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        CrawlingFear_Link = core.DamageSkill("기어 다니는 공포(연계)", 30 + 360, 1290 + 3*passive_level, 15, cooltime = 60*1000, red=True, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)

        UncontrollableChaos = core.DamageSkill("걷잡을 수 없는 혼돈", 810, 440 + 3*self.combat, 12, cooltime = 9000, red=True, modifier=BattleArtsHyper).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper) #어비스 차지 드라이브 변형
        UncontrollableChaos_Link = core.DamageSkill("걷잡을 수 없는 혼돈(연계)", 720, 440 + 3*self.combat, 12, cooltime = 9000, red=True, modifier=BattleArtsHyper).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)

        RaptRestriction = core.DamageSkill("황홀한 구속", 690, 600 + 10*self.combat, 6, cooltime = 180 * 1000, red=True, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        RaptRestrictionSummon = core.SummonSkill("황홀한 구속(소환)", 0, 450, 400 + 10*self.combat, 3, 9000, cooltime = -1, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)  #임의주기 300ms, DPM 미사용.
        RaptRestrictionEnd = core.DamageSkill("황홀한 구속(종결)", 0, 1000 + 10*self.combat, 8, cooltime = -1, modifier=BattleArtsHyper).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        
        Impulse_Connected = MultipleDamageSkillWrapper(core.DamageSkill("충동/본능 연결", 0, 0, 0, cooltime = 6000, red=True, modifier=BattleArtsHyper).setV(vEhc, 7, 2, False), 2, 1500)

        # 하이퍼
        ChargeSpellAmplification = core.BuffSkill("차지 스펠 앰플리피케이션", 720, 60000, att = 30, crit = 20, pdamage = 20, armor_ignore = 20, boss_pdamage = 30, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)
        
        EndlessPain = core.DamageSkill("끝없는 고통", 360, 0, 0, cooltime = 3030 + 60 * 1000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)   # onTick==> 다가오는 죽음
        EndlessPainTick = core.DamageSkill("끝없는 고통(틱)", 180, 300, 3).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)   #15타
        EndlessPainEnd = core.DamageSkill("끝없는 고통(종결)", 1200, 100*3.5, 12).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper) # 딜레이 : 1200ms 또는 1050ms(이후 연계 시). 일단 1200으로.
        EndlessPainEnd_Link = core.DamageSkill("끝없는 고통(종결,연계)", 1050, 100*3.5, 12).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        EndlessPainBuff = core.BuffSkill("끝없는 고통(버프)", 0, 3 * 1000, cooltime = -1).wrap(core.BuffSkillWrapper) # 정신력 소모되지 않음
        
        WraithOfGod = core.BuffSkill("레이스 오브 갓", 0, 60*1000, pdamage = 10, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)
        
        # 5차
        LuckyDice = core.BuffSkill("럭키 다이스", 0, 180*1000, pdamage = 20).isV(vEhc,3,4).wrap(core.BuffSkillWrapper)
    
        #오버드라이브 (앱솔 가정)
        #TODO: 템셋을 읽어서 무기별로 다른 수치 적용하도록 만들어야 함.
        WEAPON_ATT = jobutils.get_weapon_att("너클")
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        FloraGoddessBless = flora.FloraGoddessBlessWrapper(vEhc, 0, 0, WEAPON_ATT)
    
        MagicCircuitFullDrive = core.BuffSkill("매직 서킷 풀드라이브", 720, (30+vEhc.getV(4,3))*1000, pdamage = (20 + vEhc.getV(4,3)), cooltime = 200*1000, red=True).isV(vEhc,4,3).wrap(core.BuffSkillWrapper)
        MagicCircuitFullDriveStorm = core.DamageSkill("매직 서킷 풀드라이브(마력 폭풍)", 0, 500+20*vEhc.getV(4,3), 3, cooltime=4000).wrap(core.DamageSkillWrapper)
                
        MemoryOfSource = core.DamageSkill("근원의 기억", 0, 0, 0, cooltime = 200 * 1000, red=True).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        MemoryOfSourceTick = core.DamageSkill("근원의 기억(틱)", 250, 400 + 16 * vEhc.getV(1,1), 6).wrap(core.DamageSkillWrapper)    # 43타
        MemoryOfSourceEnd = core.DamageSkill("근원의 기억(종결)", 0, 1200 + 48 * vEhc.getV(1,1), 12 * 6).wrap(core.DamageSkillWrapper)
        MemoryOfSourceBuff = core.BuffSkill("근원의 기억(버프)", 0, 30 * 1000, cooltime = -1).wrap(core.BuffSkillWrapper) # 정신력 소모되지 않음
                
        InfinitySpell = core.BuffSkill("인피니티 스펠", 720, (40 + 2*vEhc.getV(0,0)) * 1000, cooltime = 240 * 1000, red=True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        
        DeviousNightmare = core.DamageSkill("새어 나오는 악몽", 0, 500 + 20*vEhc.getV(2,2), 9, cooltime = 10 * 1000, red=True).isV(vEhc,2,2).wrap(DeviousWrapper)
        DeviousDream = core.DamageSkill("새어 나오는 흉몽", 0, 600 + 24*vEhc.getV(2,2), 9, cooltime = 10 * 1000, red=True).wrap(DeviousWrapper)

        ForeverHungryBeastInit = core.DamageSkill("영원히 굶주리는 짐승(개시)", 540, 0, 0, cooltime=120*1000, red=True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ForeverHungryBeastTrigger = core.DamageSkill("영원히 굶주리는 짐승(등장)", 0, 0, 0, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ForeverHungryBeast = core.DamageSkill("영원히 굶주리는 짐승", 0, 400+16*vEhc.getV(0,0), 12, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper) # 20회 반복

        ### Skill Wrapper ###

        SpectorState = SpectorWrapper(MemoryOfSourceBuff, EndlessPainBuff)
        
        # 기본 연결 설정(스펙터)
        for skill in [UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link]:
            skill.onBefore(EndlessBadDream_Link)
        # 흉몽(스펙터)과 플레인(레프)에서도 연계 가능한 스킬
        for skill in [CrawlingFear_Link, RaptRestriction, EndlessPain, MemoryOfSource]:
            skill.onBefore(core.OptionalElement(SpectorState.is_active, EndlessBadDream_Link, PlainChargeDrive_Link))
  
        # 보스 1:1 시 공격 1회 당 다가오는 죽음 1개 생성, 인피니티 스펠 상태 시 강화레벨에 따라 총 3 ~ 4개 생성
        UpcomingDeath_Connected = core.OptionalElement(InfinitySpell.is_active, core.RepeatElement(UpcomingDeath, 3 + vEhc.getV(0,0) // 25), UpcomingDeath)
        UpcomingDeath.onAfter(ReturningHateStack.stackController(0.2))
        ReturningHate.onJustAfter(ReturningHateStack.stackController(-15))
        

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

        GustChargeDrive_Link.onAfter(GustSpell)
        
        AbyssSpell.onAfter(AbyssBuff)
        AbyssChargeDrive_Link.onAfter(AbyssSpell)
        AbyssChargeDrive_Link.onAfter(AbyssChargeDrive_After)
        
        Impulse_Connected.onAfter(core.OptionalElement(SpectorState.is_active, TenaciousInstinct_Link, UnstoppableImpulse_Link))

        RaptRestriction.onConstraint(core.ConstraintElement("게이지 150 이상", SpectorState, partial(SpectorState.judge, 150, 1)))
        RaptRestriction.onAfter(SpectorState.onoffController(True))
        RaptRestriction.onAfter(RaptRestrictionSummon)
        RaptRestriction.onAfter(RaptRestrictionEnd.controller(9000))
        
        EndlessPainRepeat = core.RepeatElement(EndlessPainTick, 15) # TODO: 사용 직후 게이지 1틱 감소
        EndlessPainRepeat.onAfter(core.RepeatElement(EndlessPainEnd_Link, 5))
        EndlessPain.onConstraint(core.ConstraintElement("게이지 150 이상", SpectorState, partial(SpectorState.judge, 150, 1)))
        EndlessPain.onAfter(SpectorState.onoffController(True))
        EndlessPain.onAfter(EndlessPainBuff)
        EndlessPain.onAfter(EndlessPainRepeat)
        
        MagicCircuitFullDriveStorm.onConstraint(core.ConstraintElement('매서풀 발동조건', MagicCircuitFullDrive, MagicCircuitFullDrive.is_active)) # TODO: flora.py에 있는 빌더 사용해야 함. 트리거하는 스킬 모두 등록해야함 (매우많음)

        # 스펙터 상태 파이널어택류 연계
        for skill in [EndlessBadDream, EndlessBadDream_Link, DeviousDream,
            UnfulfilledHunger, UncontrollableChaos, 
            UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link,
            CrawlingFear_Link, EndlessPainTick, EndlessPainEnd, EndlessPainEnd_Link, ForeverHungryBeast]:
            skill.onAfter(UpcomingDeath_Connected)
        MagicCircuitFullDriveStorm.onAfter(core.OptionalElement(SpectorState.is_active, UpcomingDeath_Connected))
        
        # 5차 - 새어나오는 악몽 / 흉몽 연계
        EndlessNightmare_Link.onAfter(core.OptionalElement(DeviousNightmare.is_available, DeviousNightmare))
        EndlessBadDream.onAfter(core.OptionalElement(DeviousDream.is_available, DeviousDream))
        EndlessBadDream_Link.onAfter(core.OptionalElement(DeviousDream.is_available, DeviousDream))

        for skills, _id in [([ScarletChargeDrive, ScarletChargeDrive_Link], "스칼렛"), 
                            ([GustChargeDrive_Link], "거스트"),
                            ([AbyssChargeDrive_Link], "어비스")]:
            for skill in skills:
                skill.onAfter(DeviousNightmare.reduceCooltime(1000, _id))
        for skills, _id in [([UncurableHurt_Link], "상처"),
                            ([UnfulfilledHunger_Link, UnfulfilledHunger], "굶주림"),
                            ([UncontrollableChaos_Link, UncontrollableChaos], "혼돈"),
                            ([TenaciousInstinct_Link], "본능"),
                            ([CrawlingFear_Link, CrawlingFear], "공포")]:
            for skill in skills:
                skill.onAfter(DeviousDream.reduceCooltime(1000, _id))

        # 5차 - 영원히 굶주리는 짐승
        ForeverHungryBeastInit.onAfter(ForeverHungryBeastTrigger.controller(9000)) # 9초 후 등장 TODO: 기본 9600+1740ms에 스펙터 스킬 적중시마다 시간 줄어들도록 할것
        ForeverHungryBeastTrigger.onAfter(core.RepeatElement(ForeverHungryBeast, 20))\
        
        # 기본 공격 : 540ms 중립스킬
        PlainAttack = core.DamageSkill("기본 공격", 0, 0, 0).wrap(core.DamageSkillWrapper)
        PlainAttack.onAfter(core.OptionalElement(SpectorState.is_active, EndlessBadDream, PlainChargeDrive))
        
        # Constraint 추가하기 : 레프 모드
        for skill in [PlainChargeDrive, PlainChargeDrive_Link, ScarletChargeDrive, ScarletChargeDrive_Link,
                EndlessNightmare_Link, GustChargeDrive_Link, AbyssChargeDrive_Link, UnstoppableImpulse_Link]:
            skill.onConstraint(core.ConstraintElement("레프 모드", SpectorState, SpectorState.is_not_active))
        
        # Constraint 추가하기 : 스펙터 모드
        for skill in [EndlessBadDream, UnfulfilledHunger, UncontrollableChaos, ReturningHate,
                EndlessBadDream_Link, UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, TenaciousInstinct_Link]:
            skill.onConstraint(core.ConstraintElement("스펙터 모드", SpectorState, SpectorState.is_active))

        CrawlingFear.onConstraint(core.ConstraintElement("게이지 150 이상", SpectorState, partial(SpectorState.judge, 150, 1)))
        CrawlingFear_Link.onConstraint(core.ConstraintElement("게이지 150 이상", SpectorState, partial(SpectorState.judge, 150, 1)))
        CrawlingFear.onAfter(SpectorState.onoffController(True))
        CrawlingFear_Link.onAfter(SpectorState.onoffController(True)) # TODO: 사용 직후 게이지 1틱 감소

        MemoryOfSourceRepeat = core.RepeatElement(MemoryOfSourceTick, 43)
        MemoryOfSourceRepeat.onAfter(MemoryOfSourceEnd)
        MemoryOfSource.onAfter(SpectorState.onoffController(True))
        MemoryOfSource.onAfter(MemoryOfSourceBuff)
        MemoryOfSource.onAfter(MemoryOfSourceRepeat)

        def schedule(gauge):
            """
            스펙터 <-> 레프 상태 스케쥴링을 담당합니다.
            True를 리턴하면 스펙터, False를 리턴하면 레프 상태로 변환합니다.
            """
            if gauge < 150:
                return False

            if AbyssBuff.is_not_active() and AbyssChargeDrive_Link.is_available():
                return False
            if ScarletBuff.is_not_active() and ScarletChargeDrive_Link.is_available():
                return False

            if MemoryOfSourceBuff.is_active():
                return True
            if InfinitySpell.is_active():
                return True

            if gauge > 500:
                return True
            
            return False

        SpectorState.registerSchedule(schedule)

        ScarletBuff.set_disabled_and_time_left(0) # 스칼렛/어비스 버프가 있는 채로 딜 시작하는 것을 가정함.
        AbyssBuff.set_disabled_and_time_left(0)

        DeviousNightmare.protect_from_running()
        DeviousDream.protect_from_running()
        
        return(PlainAttack, 
                [ContactCaravan, ScarletBuff, AbyssBuff, SpectorState, Booster,
                    ChargeSpellAmplification, WraithOfGod,
                    LuckyDice, Overdrive,
                    MagicCircuitFullDrive, MemoryOfSourceBuff, EndlessPainBuff,
                    InfinitySpell, FloraGoddessBless,
                    globalSkill.maple_heros(chtr.level, name = "레프의 용사", combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.soul_contract()
                    ] +\
                [ForeverHungryBeastInit, ForeverHungryBeastTrigger, EndlessNightmare_Link, ScarletChargeDrive_Link, GustChargeDrive_Link, AbyssChargeDrive_Link, 
                    CrawlingFear_Link, MemoryOfSource, EndlessPain, RaptRestriction, ReturningHate, Impulse_Connected,
                    UncurableHurt_Link, UnfulfilledHunger_Link, UncontrollableChaos_Link, 
                    AbyssSpell, RaptRestrictionSummon, RaptRestrictionEnd, DeviousNightmare, DeviousDream, MirrorBreak, MirrorSpider
                    ] +\
                [MagicCircuitFullDriveStorm] +\
                [PlainAttack])