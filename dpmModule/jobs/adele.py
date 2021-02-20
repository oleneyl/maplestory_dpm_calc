from enum import Enum

from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ReservationRule, RuleSet
from . import globalSkill
from .jobbranch import warriors
from .jobclass import flora
from . import jobutils
from math import ceil
from typing import Any, Dict


# English skill information for Adele here https://maplestory.fandom.com/wiki/Adele/Skills
class AdeleSkills(Enum):
    # Link SKill
    NobleFire = 'Noble Fire | 노블레스'
    # Beginner Skills
    MagicConversion = 'Magic Conversion | 매직 서킷'
    RecallingGreatness = 'Recalling Greatness | 패이스'
    # 1st Job
    BladeofWill = 'Blade of Will | 플레인'
    MagicDispatch = 'Magic Dispatch | 샤드'
    MartialDiscipline = 'Martial Discipline | 루디먼트'
    # 2nd Job
    AetherWeaving = 'Aether Weaving | 에테르'
    AetherCrystal = 'Aether Crystal | 에테르 결정'
    Skewering = 'Skewering | 펀토'
    AetherForge = 'Aether Forge | 크리에이션'
    Impale = 'Impale | ??'
    ResonanceRush = 'Resonance Rush | 레조넌스'
    AetherialArms = 'Aetherial Arms | 원더'
    WeaveInfusion = 'Weave Infusion | 부채 가속'
    BladecasterControl = 'Bladecaster Control | 마스터리'
    EliteTraining = 'Elite Training | 트레인'
    # 3rd Job
    Eviscerate = 'Eviscerate | 크로스'
    HuntingDecree = 'Hunting Decree | 오더'
    NobleSummons = 'Noble Summons | 게더링'
    ReignofDestruction = 'Reign of Destruction | 테리토리'
    TrueNobility = 'True Nobility | 노빌리티'
    Ascent = 'Ascent | 어센트'
    # 4th Job
    AetherMastery = 'Aether Mastery | 하이 에테르'
    Cleave = 'Cleave | 디바이드'
    AetherBloom = 'Aether Bloom | 블로섬'
    GraveProclamation = 'Grave Proclamation | 그레이브'
    HerooftheFlora = 'Hero of the Flora | 레프의 용사'
    BladecasterExpertise = 'Bladecaster Expertise | 엑스퍼트'
    Perfection = 'Perfection | 퍼펙션'
    Ruination = 'Ruination | 데몰리션'
    Strive = 'Strive | 어테인'
    # Hypers
    Shardbreaker = 'Shardbreaker | 마커'
    BladeTorrent = 'Blade Torrent | 스콜'
    DivineWrath = ' Divine Wrath | 레이스 오브 갓'
    # 5th Job
    Ruin = 'Ruin | 루인'
    InfinityBlade = 'Infinity Blade | 인피니트'
    LegacyRestoration = 'Legacy Restoration | 리스토어'
    Storm = 'Storm | 스톰'


class OrderWrapper(core.SummonSkillWrapper):
    def __init__(self, skill, ether: core.StackSkillWrapper):
        super(OrderWrapper, self).__init__(skill)
        self.ether = ether
        self.condition = None
        self.queue = []  # (Attack start time, end time) | (공격 시작 시간, 종료 시간)
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

    def _delayQueue(self, time):  # Order duration does not flow during gathering/blossom. 게더링/블로섬 도중에는 오더의 지속시간이 흐르지 않음.
        self.set_disabled_and_time_left(time)
        self.queue = [(self.currentTime + time + self.skill.delay, end + time) for start, end in self.queue]
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname=self.skill.name, spec='graph control')

    def delayQueue(self, time):
        task = core.Task(self, partial(self._delayQueue, time))
        return core.TaskHolder(task, name="오더 지속시간 지연")  # Delayed order duration

    def get_stack(self):
        return len(self.queue) * 2

    def judge(self, stack, direction):
        return (self.get_stack() - stack) * direction >= 0

    def get_hit(self):
        attackable = sum(1 for start, end in self.queue if self.currentTime >= start) * 2
        return attackable * self.skill.hit


class StormWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2, order: OrderWrapper, serverlag=0):  # TODO: Measure the average number of seconds of server rack. 서버렉 평균 몇초인지 측정할것
        skill = core.SummonSkill(AdeleSkills.Storm.value, 780, 330, 250 + 10 * vEhc.getV(num1, num2), 2, 14000 + serverlag, cooltime=90 * 1000, red=True).isV(vEhc, num1, num2)
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
        self.vEnhanceNum = 10
        self.jobtype = "STR"
        self.jobname = "아델"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ReservationRule("그란디스 여신의 축복(레프)", "인피니트"), RuleSet.BASE)
        # ruleset.add_rule(ReservationRule("매직 서킷 풀드라이브(버프)", "인피니트"), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self) -> core.CharacterModifier:
        return core.CharacterModifier(pdamage=66, armor_ignore=25)

    def get_passive_skill_list(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        # Magic Circuit: Absolute Standard 15.4. 매직 서킷: 앱솔 기준 15.4.
        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        MagicCircuit = core.InformedCharacterModifier(AdeleSkills.MagicConversion.value, att=WEAPON_ATT * 0.15)  # 15% of weapon attack power, assumed maximum. 무기 공격력의 15%, 최대치 가정.
        Pace = core.InformedCharacterModifier(AdeleSkills.RecallingGreatness.value, crit_damage=10, patt=10)
        Rudiment = core.InformedCharacterModifier(AdeleSkills.MartialDiscipline.value, att=30)
        Mastery = core.InformedCharacterModifier(AdeleSkills.BladecasterControl.value, att=30)
        Train = core.InformedCharacterModifier(AdeleSkills.EliteTraining.value, stat_main=60)
        Accent = core.InformedCharacterModifier(AdeleSkills.Ascent.value, att=30, pdamage_indep=15, crit=20)
        Expert = core.InformedCharacterModifier(AdeleSkills.BladecasterExpertise.value, att=30)
        Demolition = core.InformedCharacterModifier(AdeleSkills.Ruination.value, pdamage_indep=30 + passive_level, armor_ignore=20 + passive_level)
        Attain = core.InformedCharacterModifier(AdeleSkills.Strive.value, att=30 + passive_level, boss_pdamage=10 + ceil(passive_level / 2), crit=20 + passive_level)

        return [MagicCircuit, Pace, Rudiment, Mastery, Train, Accent, Expert, Demolition, Attain]

    def get_not_implied_skill_list(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 34)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=90+ceil(passive_level / 2))

        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Hyper Skill
        Trigger-Reinforce
        Nobility-Shield Reinforcement
        Resonance-Extra Healing
        Territory-Persist
        Blossom-Cool Time Reduce

        Starch reference: https://youtu.be/PiTnzyy0F1M

        Gathering-Blossom 1020ms

        80% hits gathered

        Resonance used every 10 seconds

        Order of strengthening the core
        Divide-Order (Grave)-Territory (Tread)-Blossom (Scall)-Impale (Resonance/Marker)-Creation (Gathering)-Shard (Wonder)
        Infinite-Restore-Ruin-Maserful-Ora Weapon-(Baos)

        하이퍼스킬
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

        Shard = core.DamageSkill(AdeleSkills.MagicDispatch.value, 630, 80 + 30 + 115 + 225 + passive_level * 3, 3 * 5, cooltime=6000, red=True).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)  # 5 450*3 projectiles. 450*3의 투사체 5개.
        Wonder = core.DamageSkill(f"{AdeleSkills.MagicDispatch.value}(Aetherial Arms | 원더)", 0, 80 + 30 + 115 + 225 + passive_level * 3, 3 * 5, cooltime=8000).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)  # Trigger skill hit every 8 seconds. 8초마다 트리거 스킬 적중시 시전.

        Ether = core.StackSkillWrapper(core.BuffSkill(AdeleSkills.AetherWeaving.value, 0, 9999999), 400)
        EtherTick = core.SummonSkill(f'{AdeleSkills.AetherWeaving.value}(Natural Recovery | 자연 회복)', 0, 10020, 0, 0, 9999999).wrap(core.SummonSkillWrapper)

        Resonance = core.DamageSkill(AdeleSkills.ResonanceRush.value, 690, (120+125+265+passive_level*3), 6, cooltime=10*1000, modifier=core.CharacterModifier(pdamage_indep=15*5)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper) # 클라공속 900ms, 스택 유지를 위해 10초마다 사용함

        ResonanceStack = core.BuffSkill(f'{AdeleSkills.ResonanceRush.value}(Stack | 스택)', 0, 30 * 1000, cooltime=-1, pdamage_indep=10, armor_ignore=10).wrap(core.BuffSkillWrapper)  # Final damage 5, ?? 5, Max 2 times. Assume always overlapping. 최종뎀 5, 방무 5, 최대2회. 상시 중첩으로 가정.

        Creation = core.StackDamageSkillWrapper(core.DamageSkill(AdeleSkills.AetherForge.value, 0, 200 + 240 + 270 + passive_level * 3, 1, cooltime=1500, red=True).setV(vEhc, 5, 2, False),
            Ether,
            lambda ether: min(ether.stack // 100, 3) * 2)  # 270ms basic attack speed for direct casting. 직접시전시 270ms 기본공속

        Territory = core.SummonSkill(AdeleSkills.ReignofDestruction.value, 420, 405, 100 + 300 + passive_level * 5, 4, 7000 + 4000, rem=False, cooltime=30 * 1000, red=True).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper)  # 27 hits, clack 540 ms. 27회 타격, 클라공속540ms.
        TerritoryEnd = core.DamageSkill(f'{AdeleSkills.ReignofDestruction.value}(Ending | 종료)', 0, 550 + 300 + passive_level * 5, 12, cooltime=-1).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        Order = OrderWrapper(core.SummonSkill(AdeleSkills.HuntingDecree.value, 0, 1020, 240 + 120 + passive_level * 3, 2, 99999999).setV(vEhc, 1, 2, False), Ether)  # 15% ether crystal, assuming no casting delay, attack period 1020ms. 15% 에테르 결정, 시전딜레이 없음으로 가정, 공격주기 1020ms.

        Gathering = core.StackDamageSkillWrapper(core.DamageSkill(AdeleSkills.NobleSummons.value, 630, 260 + 300 + passive_level * 3, 4, cooltime=12 * 1000, red=True).setV(vEhc, 5, 2, False),
            Order,
            lambda order: order.get_stack() * 0.8
        )  # Bring up the knife. Linked to Blossom, assuming about 600ms to gather. 칼 불러오기. 블라섬과 연계됨, 모이는데 약 600ms 가정

        Divide = core.DamageSkill(AdeleSkills.Cleave.value, 600, 375 + self.combat * 3, 6, modifier=core.CharacterModifier(pdamage=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)  # Trigger skill, claw speed 780ms. 트리거 스킬, 클라공속 780ms.

        Grave = core.DamageSkill(AdeleSkills.GraveProclamation.value, 630, 800 + self.combat * 20, 10, cooltime=90000, red=True).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)  # 840ms. 클라공속 840ms.
        GraveDebuff = core.BuffSkill(f'{AdeleSkills.GraveProclamation.value}(Debuff | 디버프)', 0, 999999999, pdamage=20, armor_ignore=10, cooltime=-1).wrap(core.BuffSkillWrapper)

        Blossom = core.DamageSkill(AdeleSkills.AetherBloom.value, 420, 650 + self.combat * 6, 8, cooltime=20 * 1000 * 0.75, red=True).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)  # 50% decision. 420 ms, no attack speed. 50%결정. 클라공속 420ms, 공속 안받음
        BlossomExceed = core.StackDamageSkillWrapper(core.DamageSkill(f'{AdeleSkills.AetherBloom.value}(Exceed | 초과)', 0, 650 + self.combat * 6, 8, cooltime=-1, modifier=core.CharacterModifier(pdamage_indep=-25)).setV(vEhc, 3, 2, False),
            Order,
            lambda order: max(order.get_stack() - 1, 0)
        )

        # Hypers
        Marker = core.DamageSkill(AdeleSkills.Shardbreaker.value, 690, 500, 6 * 2, cooltime=60 * 1000, modifier=core.CharacterModifier(pdamage_indep=300)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)  # 300% increase in final damage, 5 random location pieces, 1 hit, 5 crystals, each attack with spawn/shredding, clack speed 900ms. 최종뎀 300% 증가, 임의위치 조각 5개, 1히트, 결정 5개, 생성/파쇄 각각 공격, 클라공속 900ms
        Scool = core.DamageSkill(AdeleSkills.BladeTorrent.value, 690, 1000, 12, cooltime=180 * 1000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)  # Bind. Clutch speed 900ms. 바인드. 클라공속 900ms.
        WraithOfGod = core.BuffSkill(AdeleSkills.DivineWrath.value, 0, 60 * 1000, pdamage=10, cooltime=120 * 1000).wrap(core.BuffSkillWrapper)

        # 5차
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        FloraGoddessBless = flora.FloraGoddessBlessWrapper(vEhc, 0, 0, jobutils.get_weapon_att(chtr))

        Ruin = core.DamageSkill(f'{AdeleSkills.Ruin.value}(Cast | 시전)', 600, 0, 0, cooltime=60 * 1000, red=True).isV(vEhc, 2, 2).wrap(core.DamageSkillWrapper)  # Assumed to be cast in 4 seconds. 4초에 나누어서 시전되는 것으로 가정
        RuinFirstTick = core.SummonSkill(f'{AdeleSkills.Ruin.value}(Summons | 소환)', 0, 160, 250 + vEhc.getV(2, 2) * 10, 6, 2000, cooltime=-1).isV(vEhc, 2, 2).wrap(core.SummonSkillWrapper)  # 12 times, assumed to be used in 2 seconds. 12번, 2초에 나누어 사용으로 가정.
        RuinSecondTick = core.SummonSkill(f'{AdeleSkills.Ruin.value}(Attack | 공격)', 0, 250, 450 + vEhc.getV(2, 2) * 18, 9, 2000, cooltime=-1).isV(vEhc, 2, 2).wrap(core.SummonSkillWrapper)  # Assume that the use is divided into 8 times and 2 seconds. 8번, 2초에 나누어 사용으로 가정.

        Infinite = core.SummonSkill(AdeleSkills.InfinityBlade.value, 540, 342, 350 + vEhc.getV(0, 0) * 14, 2 * 6, 30000, cooltime=180 * 1000, red=True).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)  # 5% crystal generated for each attack. 517 hits based on starch -> 18 hits are assumed to be hit by 6 each. (30000-540)//342*6 = 516. 매 공격마다 5% 결정생성. 전분 기준 517회 타격 -> 18개를 6개씩 묶어서 타격 가정. (30000-540)//342*6 = 516.
        Restore = core.BuffSkill(AdeleSkills.LegacyRestoration.value, 720, 30 * 1000, pdamage=15 + vEhc.getV(1, 1), cooltime=180 * 1000, red=True).isV(vEhc, 1, 1).wrap(core.BuffSkillWrapper)  # 2 swords increase, ether acquisition 40+d(x/2)% increase. 소드 2개 증가, 에테르획득량 40+d(x/2)%증가.
        RestoreTick = core.SummonSkill(f'{AdeleSkills.LegacyRestoration.value}(Periodic attack | 주기공격)', 0, 2970, 900 + 36 * vEhc.getV(1, 1), 3, 30 * 1000, cooltime=-1).isV(vEhc, 1, 1).wrap(core.SummonSkillWrapper)  # Cast 11 times. 11회 시전

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
            Ether.stackController(5 * RESTORE_MULTIPLIER),
            Ether.stackController(5)
        ))
        Divide.onAfter(core.OptionalElement(
            Restore.is_active,
            Ether.stackController(12 * RESTORE_MULTIPLIER),
            Ether.stackController(12)
        ))
        Resonance.onAfter(core.OptionalElement(  # Resonance-Extra Healing. 레조넌스-엑스트라 힐링.
            Restore.is_active,
            Ether.stackController(20 * RESTORE_MULTIPLIER),
            Ether.stackController(20)
        ))

        # Hunting Decree. 오더.
        def use_order():
            if Ether.judge(100, -1):
                return False
            if Order.judge(4, -1):  # Use if less than 2 pairs. 2쌍 이하면 사용.
                return True
            if Restore.is_active() and Order.judge(6, -1):  # Use if 3 pairs or less during restore. 리스토어중 3쌍 이하면 사용.
                return True
            return False

        Order.setCondition(use_order)

        # Noble Summons - Aether Bloom. 게더링-블로섬.
        Blossom.onConstraint(core.ConstraintElement('When there is a summon | 오더가 있을 때', Order, partial(Order.judge, 1, 1)))  # When there is a bloom?
        Blossom.onBefores([Gathering, Order.delayQueue(690 + 2010)])  # Gathering->Blossom order, _befores is executed from the end of the list. The order is stopped during Gathering (690ms) + Blossom (2010ms). 게더링->블로섬 순서, _befores는 리스트의 끝부터 실행됨. 게더링(690ms)+블로섬(2010ms)동안 오더가 멈춤.
        Blossom.onAfter(BlossomExceed)

        Grave.onAfter(GraveDebuff)

        # Ruin. 루인.
        Ruin.onAfter(RuinFirstTick)
        RuinFirstTick.onEventEnd(RuinSecondTick)

        # legacy restoration. 리스토어.
        Restore.onAfter(RestoreTick)

        # Reign of destruction. 테리토리.
        Territory.onEventEnd(TerritoryEnd)

        # Resonance. 레조넌스.
        Resonance.onAfter(ResonanceStack)

        # AetherForge. 크리에이션.
        Divide.onAfter(core.OptionalElement(Creation.is_available, Creation))

        # Aetherial Arms. 원더.
        Divide.onAfter(core.OptionalElement(Wonder.is_available, Wonder))

        Creation.protect_from_running()
        Wonder.protect_from_running()

        return(Divide,
                [globalSkill.maple_heros(chtr.level, name = "레프의 용사", combat_level=self.combat), ResonanceStack, GraveDebuff, WraithOfGod, Restore,
                    AuraWeaponBuff, AuraWeapon, MagicCircuitFullDrive, FloraGoddessBless,
                    globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.soul_contract()] +\
                [EtherTick, Resonance, Grave, Blossom, Marker, Ruin, Storm, MirrorBreak, MirrorSpider, Shard] +\
                [Order, Wonder, Territory, TerritoryEnd, Infinite, RuinFirstTick, RuinSecondTick, RestoreTick, Creation, Scool, ManaStorm] +\
                [] +\
                [Divide])
