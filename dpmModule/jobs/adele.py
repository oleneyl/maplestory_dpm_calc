import os
from functools import partial

from typing import Any, Dict

from . import jobutils
from . import globalSkill
from ..kernel import core
from .jobclass import flora
from .jobbranch import warriors
from ..execution.rules import RuleSet
from ..status.ability import Ability_tool
from ..character import characterKernel as ck


class OrderWrapper(core.SummonSkillWrapper):
    def __init__(self, skill, ether: core.StackSkillWrapper):
        super(OrderWrapper, self).__init__(skill)
        self.ether = ether
        self.condition = None
        self.queue = []  # (공격 시작 시간, 종료 시간)
        self.summonCooltime = 0
        self.currentTime = 0
        self.REMAIN_TIME = 40000

    def setCondition(self, condition):
        self.condition = condition

    def add(self):
        self.ether.vary(-100)
        self.queue += [(self.currentTime + self.skill.delay, self.currentTime + self.REMAIN_TIME)]
        self.summonCooltime = 500

    def calculateRefund(self, timeLeft):
        if timeLeft < 16000:
            return 0
        if timeLeft < 24000:
            return 20
        if timeLeft < 32000:
            return 40
        return 60

    def consume(self):
        count = len(self.queue)
        refund = sum([self.calculateRefund(end - self.currentTime) for start, end in self.queue])
        self.ether.vary(refund)
        self.queue = []
        return count

    def spend_time(self, time):
        self.currentTime += time
        self.queue = [(start, end) for start, end in self.queue if end > self.currentTime]
        self.summonCooltime -= time

        if self.summonCooltime <= 0 and self.condition():
            self.add()

        super(OrderWrapper, self).spend_time(time)

    def _delayQueue(self, time):  # 게더링/블로섬 도중에는 오더의 지속시간이 흐르지 않음
        self.set_disabled_and_time_left(time)
        self.queue = [(self.currentTime + time + self.skill.delay, end + time) for start, end in self.queue]
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname=self.skill.name, spec='graph control')

    def delayQueue(self, time):
        task = core.Task(self, partial(self._delayQueue, time))
        return core.TaskHolder(task, name="오더 지속시간 지연")

    def get_stack(self):
        return len(self.queue) * 2

    def judge(self, stack, direction):
        return (self.get_stack() - stack) * direction >= 0

    def get_hit(self):
        attackable = sum(1 for start, end in self.queue if self.currentTime >= start) * 2
        return attackable * self.skill.hit


class StormWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2, order: OrderWrapper, serverlag=0):  # TODO: 서버렉 평균 몇초인지 측정할것
        skill = core.SummonSkill("스톰", 780, 330, 250 + 10 * vEhc.getV(num1, num2), 2, 14000 + serverlag, cooltime=90 * 1000, red=True).isV(vEhc, num1, num2)
        super(StormWrapper, self).__init__(skill)
        self.order = order
        self.consumed_order = 0

    def _use(self, skill_modifier):
        self.consumed_order = self.order.consume()
        return super(StormWrapper, self)._use(skill_modifier)

    def get_hit(self):
        return self.skill.hit + max(self.consumed_order - 1, 0) * 2


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.load(os.path.join(os.path.dirname(__file__), 'configs', 'adele.yml'))
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')

    def get_ruleset(self):
        ruleset = RuleSet()
        return ruleset

    def get_modifier_optimization_hint(self) -> core.CharacterModifier:
        return core.CharacterModifier(pdamage=66, armor_ignore=25)

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''하이퍼스킬
        트리거-리인포스
        노빌리티-실드 리인포스
        레조넌스-엑스트라 힐링
        테리토리-퍼시스트
        블로섬-쿨타임 리듀스

        전분 참조 : https://youtu.be/PiTnzyy0F1M

        게더링-블로섬 1020ms

        게더링 80% 히트

        레조넌스 10초마다 사용

        코어 강화 순서
        디바이드 - 오더(그레이브) - 테리토리(트레드) - 블로섬(스콜) - 임페일(레조넌스/마커) - 크리에이션(게더링) - 샤드(원더)
        인피니트 - 리스토어 - 루인 - 매서풀 - 오라웨폰 - (바오스)

        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        Shard = self.load_skill_wrapper("샤드", vEhc, passive_level=passive_level)
        Wonder = self.load_skill_wrapper("샤드(원더)", vEhc, passive_level=passive_level)

        Ether = core.StackSkillWrapper(core.BuffSkill('에테르', 0, 9999999), 400)
        EtherTick = self.load_skill_wrapper("에테르(자연 회복)")

        Resonance = self.load_skill_wrapper("레조넌스", vEhc, passive_level=passive_level)

        ResonanceStack = self.load_skill_wrapper("레조넌스(스택)", vEhc)

        Creation = core.StackDamageSkillWrapper(
            core.DamageSkill('크리에이션', 0, 200+240+270+passive_level*3, 1, cooltime=1500, red=True).setV(vEhc, 5, 2, False),
            Ether,
            lambda ether: min(ether.stack // 100, 3) * 2
        )  # 직접시전시 270ms 기본공속

        Territory = self.load_skill_wrapper("테리토리", vEhc, passive_level=passive_level)
        TerritoryEnd = self.load_skill_wrapper("테리토리(종료)", vEhc, passive_level=passive_level)

        Order = OrderWrapper(core.SummonSkill('오더', 0, 1020, 240+120+passive_level*3, 2, 99999999).setV(vEhc, 1, 2, False), Ether)  # 15% 에테르 결정, 시전딜레이 없음으로 가정, 공격주기 1020ms

        Gathering = core.StackDamageSkillWrapper(
            core.DamageSkill('게더링', 630, 260+300+passive_level*3, 4, cooltime=12*1000, red=True).setV(vEhc, 5, 2, False),
            Order,
            lambda order: order.get_stack() * 0.8
        )  # 칼 불러오기. 블라섬과 연계됨, 모이는데 약 600ms 가정

        Divide = self.load_skill_wrapper("디바이드", vEhc)

        Grave = self.load_skill_wrapper("그레이브", vEhc)
        GraveDebuff = self.load_skill_wrapper("그레이브(디버프)")

        Blossom = self.load_skill_wrapper("블로섬", vEhc)
        BlossomExceed = core.StackDamageSkillWrapper(
            core.DamageSkill('블로섬(초과)', 0, 650+self.combat*6, 8, cooltime=-1, modifier=core.CharacterModifier(pdamage_indep=-25)).setV(vEhc, 3, 2, False),
            Order,
            lambda order: max(order.get_stack() - 1, 0)
        )

        Marker = self.load_skill_wrapper("마커", vEhc)
        Scool = self.load_skill_wrapper("스콜", vEhc)
        WraithOfGod = self.load_skill_wrapper("레이스 오브 갓")

        # 5차
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        FloraGoddessBless = flora.FloraGoddessBlessWrapper(vEhc, 0, 0, jobutils.get_weapon_att(chtr))

        Ruin = self.load_skill_wrapper("루인(시전)", vEhc)
        RuinFirstTick = self.load_skill_wrapper("루인(소환)", vEhc)
        RuinSecondTick = self.load_skill_wrapper("루인(공격)", vEhc)

        Infinite = self.load_skill_wrapper("인피니트", vEhc)
        Restore = self.load_skill_wrapper("리스토어", vEhc)
        RestoreTick = self.load_skill_wrapper("리스토어(주기공격)", vEhc)

        Storm = StormWrapper(vEhc, 0, 0, Order)

        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 4, 4)
        magic_curcuit_full_drive_builder = flora.MagicCircuitFullDriveBuilder(vEhc, 3, 3)
        for sk in [Divide, Resonance, Ruin, Marker, Grave, Scool, Order, RestoreTick, Storm]:
            auraweapon_builder.add_aura_weapon(sk)
            magic_curcuit_full_drive_builder.add_trigger(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()
        MagicCircuitFullDrive, ManaStorm = magic_curcuit_full_drive_builder.get_skill()

        # 딜 사이클 정의

        # 에테르
        Ether.set_stack(400)
        RESTORE_MULTIPLIER = 1 + (50 + vEhc.getV(1, 1)) / 100
        EtherTick.onTick(core.OptionalElement(
            Restore.is_active,
            Ether.stackController(5*RESTORE_MULTIPLIER),
            Ether.stackController(5)
        ))
        Divide.onAfter(core.OptionalElement(
            Restore.is_active,
            Ether.stackController(12*RESTORE_MULTIPLIER),
            Ether.stackController(12)
        ))
        Resonance.onAfter(core.OptionalElement(  # 레조넌스-엑스트라 힐링
            Restore.is_active,
            Ether.stackController(20*RESTORE_MULTIPLIER),
            Ether.stackController(20)
        ))

        # 오더
        def use_order():
            if Ether.judge(100, -1):
                return False
            if Order.judge(4, -1):  # 2쌍 이하면 사용
                return True
            if Restore.is_active() and Order.judge(6, -1):  # 리스토어중 3쌍 이하면 사용
                return True
            return False
        Order.setCondition(use_order)

        # 게더링-블로섬
        Blossom.onConstraint(core.ConstraintElement('오더가 있을 때', Order, partial(Order.judge, 1, 1)))
        Blossom.onBefores([Gathering, Order.delayQueue(690+2010)])  # 게더링->블로섬 순서, _befores는 리스트의 끝부터 실행됨. 게더링(690ms)+블로섬(2010ms)동안 오더가 멈춤.
        Blossom.onAfter(BlossomExceed)

        Grave.onAfter(GraveDebuff)

        # 루인
        Ruin.onAfter(RuinFirstTick)
        RuinFirstTick.onEventEnd(RuinSecondTick)

        # 리스토어
        Restore.onAfter(RestoreTick)

        # 테리토리
        Territory.onEventEnd(TerritoryEnd)

        # 레조넌스
        Resonance.onAfter(ResonanceStack)

        # 크리에이션
        Divide.onAfter(core.OptionalElement(Creation.is_available, Creation))

        # 원더
        Divide.onAfter(core.OptionalElement(Wonder.is_available, Wonder))

        Creation.protect_from_running()
        Wonder.protect_from_running()

        return(Divide,
               [globalSkill.maple_heros(chtr.level, name="레프의 용사", combat_level=self.combat), ResonanceStack, GraveDebuff, WraithOfGod, Restore,
                AuraWeaponBuff, AuraWeapon, MagicCircuitFullDrive, FloraGoddessBless,
                globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.soul_contract()] +
               [EtherTick, Resonance, Grave, Blossom, Marker, Ruin, Storm, MirrorBreak, MirrorSpider, Shard] +
               [Order, Wonder, Territory, TerritoryEnd, Infinite, RuinFirstTick, RuinSecondTick, RestoreTick, Creation, Scool, ManaStorm] +
               [] +
               [Divide])
