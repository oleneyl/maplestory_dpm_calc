from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule, InactiveRule
from . import globalSkill
from .jobbranch import warriors
from .jobclass import flora
from . import jobutils
import math

class OrderWrapper(core.SummonSkillWrapper):
    def __init__(self, skill, ether: core.StackSkillWrapper):
        super(OrderWrapper, self).__init__(skill)
        self.ether = ether
        self.condition = None
        self.queue = []
        self.stack = 0
        self.currentTime = 0
        self.REMAIN_TIME = 40000

    def setCondition(self, condition):
        self.condition = condition

    def add(self):
        self.ether.vary(-100)
        self.queue = self.queue + [self.currentTime + self.REMAIN_TIME]

    def spend_time(self, time):
        self.currentTime += time
        self.queue = [x for x in self.queue if x > self.currentTime]

        if self.condition():
            self.add()
        
        self.stack = len(self.queue) * 2
        super(OrderWrapper, self).spend_time(time)

    def _delayQueue(self, time): # 게더링/블로섬 도중에는 오더의 지속시간이 흐르지 않음
        self.set_disabled_and_time_left(time)
        self.queue = [x + time for x in self.queue]
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname = self.skill.name, spec = 'graph control')

    def delayQueue(self, time):
        task = core.Task(self, partial(self._delayQueue, time))
        return core.TaskHolder(task, name = "오더 지속시간 지연")
        
    def judge(self, stack, direction):
        return (self.stack-stack)*direction>=0

    def _useTick(self):
        if self.onoff and self.tick <= 0:
            self.tick += self.skill.delay
            return core.ResultObject(0, self.get_modifier(), self.skill.damage, self.skill.hit * self.stack, sname = self.skill.name, spec = self.skill.spec)
        else:
            return core.ResultObject(0, self.disabledModifier, 0, 0, sname = self.skill.name, spec = self.skill.spec)

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 10
        self.jobtype = "str"
        self.jobname = "아델"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1
        self._combat = 0 # 임시 사용, vEhc에서 받아와야 함

    def get_ruleset(self):
        ruleset = RuleSet()
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        # 매직 서킷: 앱솔 기준 15.4
        WEAPON_ATT = jobutils.get_weapon_att("튜너")
        passive_level = chtr.get_base_modifier().passive_level + self._combat
        
        MagicCircuit = core.InformedCharacterModifier("매직 서킷", att=WEAPON_ATT * 0.15)  #무기 공격력의 15%, 최대치 가정.
        Pace = core.InformedCharacterModifier("패이스", crit_damage=10, patt=10)
        Rudiment = core.InformedCharacterModifier("루디먼트", att=30)
        Mastery = core.InformedCharacterModifier("마스터리", att=30)
        Train = core.InformedCharacterModifier("트레인", stat_main=60)
        Accent = core.InformedCharacterModifier("어센트", att=30, pdamage_indep=15, crit=20)
        Expert = core.InformedCharacterModifier("엑스퍼트", att=30)
        Demolition = core.InformedCharacterModifier("데몰리션", pdamage_indep=30+passive_level, armor_ignore=20+passive_level)
        Attain = core.InformedCharacterModifier("어테인", att=30+passive_level, boss_pdamage=10+math.ceil(passive_level/2), crit=20+passive_level)

        return [MagicCircuit, Pace, Rudiment, Mastery, Train, Accent, Expert, Demolition, Attain]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self._combat
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 34)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5 + 0.5 * math.ceil(passive_level / 2))

        return [WeaponConstant, Mastery]


    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''하이퍼스킬
        트리거-리인포스
        노빌리티-실드 리인포스
        레조넌스-엑스트라 힐링
        테리토리-퍼시스트
        블로섬-쿨타임 리듀스

        전분 참조 : https://youtu.be/m2LX8otP-9w

        게더링-디바이드-블로섬

        게더링, 블로섬 80% 히트

        레조넌스 10초마다 사용

        코어 강화 순서
        디바이드 - 오더(그레이브) - 테리토리(트레드) - 블로섬(스콜) - 임페일(레조넌스/마커) - 크리에이션(게더링) - 샤드(원더)
        인피니트 - 리스토어 - 루인 - 매서풀 - 오라웨폰 - (바오스)

        '''
        passive_level = chtr.get_base_modifier().passive_level + self._combat

        ShardActive = core.DamageSkill("샤드(액티브)", 0, 80+30+115+225+passive_level*3, 3 * 5).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper) # 자동사용만, 최종 450*3
        Shard = core.DamageSkill("샤드", 0, 80+30+115+225+passive_level*3, 3 * 5, cooltime=8000, red=True).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper) # 8초마다 트리거 스킬 적중시 시전

        Ether = core.StackSkillWrapper(core.BuffSkill('에테르', 0, 9999999), 400)
        EtherTick = core.SummonSkill('에테르(자연 회복)', 0, 10020, 0, 0, 9999999).wrap(core.SummonSkillWrapper)

        Resonance = core.DamageSkill("레조넌스", 690, (120+125+265+passive_level*3) * (1.15**6), 6, cooltime=10*1000, red=True).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper) # 클라공속 900ms, 스택 유지를 위해 10초마다 사용함

        ResonanceStack = core.BuffSkill('레조넌스(스택)', 0, 30*1000, cooltime=-1, pdamage_indep=15, armor_ignore=15).wrap(core.BuffSkillWrapper) # 최종뎀 5, 방무 5, 최대3회. 상시 중첩으로 가정

        Creation = core.StackDamageSkillWrapper(
            core.DamageSkill('크리에이션', 0, 200+240+270+passive_level*3, 1, cooltime = 1500, red=True).setV(vEhc, 5, 2, False),
            Ether,
            lambda ether: min(ether.stack // 100, 3) * 2
        ) # 직접시전시 270ms 기본공속

        Territory = core.SummonSkill('테리토리', 420, 405, 100+300+passive_level*5, 4, 7000+4000, rem=False, cooltime=30*1000, red=True).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper) # 27회 타격, 클라공속540ms
        TerritoryEnd = core.DamageSkill('테리토리(종료)', 0, 550+300+passive_level*5, 12, cooltime=-1).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        Order = OrderWrapper(core.SummonSkill('오더', 0, 1140, 240+120+passive_level*3, 2, 99999999).setV(vEhc, 1, 2, False), Ether) # 15% 에테르 결정, 시전딜레이 없음으로 가정, 공격주기 1140ms(인피니트로부터 추정됨)

        Gathering = core.StackDamageSkillWrapper(
            core.DamageSkill('게더링', 0, 260+300+passive_level*3, 4, cooltime=12*1000, red=True).setV(vEhc, 5, 2, False),
            Order,
            lambda order: order.stack * 0.8
        ) # 칼 불러오기. 블라섬과 연계됨, 딜레이 0 가정

        Divide = core.DamageSkill('디바이드', 600, 375+self._combat*3, 6, modifier=core.CharacterModifier(pdamage=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper) #트리거 스킬, 클라공속 780ms

        # TODO: 쿨마다 사용하는게 나을 수 있음
        Grave = core.DamageSkill('그레이브', 630, 800+self._combat*20, 10, cooltime=90000, red=True).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper) #한 번만 사용, 클라공속 840ms
        GraveDebuff = core.BuffSkill('그레이브(디버프)', 0, 999999999, pdamage=20, armor_ignore=10, cooltime=-1).wrap(core.BuffSkillWrapper)

        Blossom = core.DamageSkill('블로섬', 420, 650+self._combat*6, 8, cooltime=20*1000*0.75, red=True).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper) # 50%결정. 클라공속 420ms, 공속 안받음
        BlossomExceed = core.StackDamageSkillWrapper(
            core.DamageSkill('블로섬(초과)', 0, 650+self._combat*6, 8, cooltime=-1, modifier=core.CharacterModifier(pdamage_indep=-25)).setV(vEhc, 3, 2, False),
            Order,
            lambda order: max(order.stack * 0.8 - 1, 0)
        )

        Marker = core.DamageSkill('마커', 690, 1000, 3*2, cooltime=60*1000, modifier=core.CharacterModifier(pdamage_indep=300)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper) # 최종뎀 300% 증가, 임의위치 조각 5개, 1히트, 결정 5개, 생성/파쇄 각각 공격, 클라공속 900ms
        Scool = core.DamageSkill('스콜', 690, 1000, 12, cooltime=180*1000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper) #바인드. 클라공속 900ms
        WraithOfGod = core.BuffSkill("레이스 오브 갓", 0, 60*1000, pdamage = 10, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)

        # 5차

        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 4, 4)
        magic_curcuit_full_drive_builder = flora.MagicCircuitFullDriveBuilder(vEhc, 3, 3)
        for sk in [Divide, Resonance]:
            auraweapon_builder.add_aura_weapon(sk)
            magic_curcuit_full_drive_builder.add_trigger(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()
        MagicCircuitFullDrive, ManaStorm = magic_curcuit_full_drive_builder.get_skill()

        # TODO: 5차 스킬 딜레이 공속 적용여부 테스트
        Ruin = core.DamageSkill('루인(시전)', 780, 0, 0, cooltime=60*1000, red=True).isV(vEhc,2,2).wrap(core.DamageSkillWrapper) # 4초에 나누어서 시전되는 것으로 가정
        RuinFirstTick = core.SummonSkill('루인(소환)', 0, 160, 250 + vEhc.getV(2,2)*10, 6, 2000, cooltime=-1).isV(vEhc,2,2).wrap(core.SummonSkillWrapper) # 12번, 2초에 나누어 사용으로 가정
        RuinSecondTick = core.SummonSkill('루인(공격)', 0, 250, 450 + vEhc.getV(2,2)*18, 9, 2000, cooltime=-1).isV(vEhc,2,2).wrap(core.SummonSkillWrapper) # 8번, 2초에 나누어 사용으로 가정

        Infinite = core.SummonSkill('인피니트', 540, 342, 350 + vEhc.getV(0,0) * 14, 2 * 6, 30000, cooltime=180*1000, red=True).isV(vEhc,0,0).wrap(core.SummonSkillWrapper) #매 공격마다 5% 결정생성. 전분 기준 517회 타격 -> 18개를 6개씩 묶어서 타격 가정. (30000-540)//342*6 = 516.
        Restore = core.BuffSkill('리스토어', 720, 30*1000, pdamage=15+vEhc.getV(1,1), cooltime=180*1000, red=True).isV(vEhc,1,1).wrap(core.BuffSkillWrapper) #소드 2개 증가, 에테르획득량 40+d(x/2)%증가
        RestoreTick = core.SummonSkill('리스토어(주기공격)', 0, 2970, 900+36*vEhc.getV(1,1), 3, 30*1000, cooltime=-1).isV(vEhc,1,1).wrap(core.SummonSkillWrapper) # 11회 시전

        # 딜 사이클 정의

        # 에테르
        Ether.set_stack(400)
        RESTORE_MULTIPLIER = 1 + (40 + vEhc.getV(1,1) // 2) / 100
        EtherTick.onTick(core.OptionalElement(
            Restore.is_active,
            Ether.stackController(5*RESTORE_MULTIPLIER),
            Ether.stackController(5)
        ))
        Divide.onAfter(core.OptionalElement(
            Restore.is_active,
            Ether.stackController(10*RESTORE_MULTIPLIER),
            Ether.stackController(10)
        ))
        Resonance.onAfter(core.OptionalElement( # 레조넌스-엑스트라 힐링
            Restore.is_active,
            Ether.stackController(20*RESTORE_MULTIPLIER),
            Ether.stackController(20)
        ))

        # 오더
        def use_order():
            if Ether.judge(100, -1):
                return False
            if Order.judge(4, -1): # 2쌍 이하면 사용
                return True
            if Restore.is_active() and Order.judge(6, -1): # 리스토어중 3쌍 이하면 사용
                return True
            return False
        Order.setCondition(use_order)

        # 게더링-블로섬
        Blossom.onConstraint(core.ConstraintElement('오더가 있을 때', Order, partial(Order.judge, 1, 1)))
        Blossom.onBefores([Divide, Gathering, Order.delayQueue(600+1410)]) # 게더링->디바이드->블로섬 순서, _befores는 리스트의 끝부터 실행됨. 2010ms동안 오더가 멈춤.
        Blossom.onAfter(BlossomExceed)

        Grave.onAfter(GraveDebuff)

        # 루인
        Ruin.onAfter(RuinFirstTick)
        Ruin.onAfter(RuinSecondTick.controller(2000))

        # 리스토어
        Restore.onAfter(RestoreTick)

        # 테리토리
        Territory.onAfter(TerritoryEnd.controller(7000+4000))

        # 레조넌스
        Resonance.onAfter(ResonanceStack)

        # 크리에이션
        Divide.onAfter(core.OptionalElement(Creation.is_available, Creation))

        # 원더
        Divide.onAfter(core.OptionalElement(Shard.is_available, Shard))

        Creation.protect_from_running()
        Shard.protect_from_running()

        return(Divide,
                [globalSkill.maple_heros(chtr.level), ResonanceStack, GraveDebuff, WraithOfGod, Restore,
                    AuraWeaponBuff, AuraWeapon, MagicCircuitFullDrive, 
                    globalSkill.useful_sharp_eyes(), globalSkill.soul_contract()] +\
                [Resonance, Grave, Blossom, Marker, Ruin] +\
                [Order, Shard, Territory, TerritoryEnd, Infinite, RuinFirstTick, RuinSecondTick, RestoreTick, Creation, Scool, ManaStorm] +\
                [] +\
                [Divide])        


        

