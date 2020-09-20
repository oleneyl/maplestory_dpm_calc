from typing import List
from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ConditionRule, RuleSet
from . import globalSkill
from .jobbranch import thieves
from math import ceil
import random
'''
TODO: 다른 직업들과 비슷한 스타일로 순서 재정리
'''

class ChunJiInWrapper(core.GraphElement):
    def __init__(self):
        super(ChunJiInWrapper, self).__init__("천지인")
        
        self.ChunJiIn = {
            "천": False,
            "지": False,
            "인": False
        }
        self.seed = 0

    def _choice(self, arr):
        # return random.choice(arr)
        idx = self.seed % len(arr)
        self.seed += 1
        return arr[idx]
    
    def _add_element(self, el):
        if not self.ChunJiIn[el]:
            self.ChunJiIn[el] = True
        return self._result_object_cache

    def add_element(self, el):
        task = core.Task(self, partial(self._add_element, el))
        return core.TaskHolder(task, name=el)
    
    def count_elements(self):
        return (int(self.ChunJiIn["천"]) + int(self.ChunJiIn["지"]) + int(self.ChunJiIn["인"]))

    def is_stack(self, stack):
        return self.count_elements() == stack
    
    def _reset_elements(self):
        for el in self.ChunJiIn.keys():
            self.ChunJiIn[el] = False
        return self._result_object_cache

    def reset_elements(self):
        task = core.Task(self, self._reset_elements)
        return core.TaskHolder(task, name="천지인 초기화")
    
    def _fill_element(self):
        fillable = [x for x in ["천", "지", "인"] if self.ChunJiIn[x] == False]
        toFill = self._choice(fillable)
        self.ChunJiIn[toFill] = True
        return self._result_object_cache

    def fill_element(self):
        task = core.Task(self, self._fill_element)
        return core.TaskHolder(task, name="속성 연계 완성")
    
    def _choice_reset(self, skills: List[core.DamageSkillWrapper]):
        resetable = [x for x in skills if not x.is_available()]
        if len(resetable) == 0:
            resetable = skills
        toReset = self._choice(resetable)
        toReset.reduce_cooltime_p(1)
        return self._result_object_cache

    def choice_reset(self, skills: List[core.DamageSkillWrapper]):
        task = core.Task(self, partial(self._choice_reset, skills))
        return core.TaskHolder(task, name="속성 도술 쿨타임 초기화")

class PausableBuffSkillWrapper(core.BuffSkillWrapper):
    def __init__(self, skill):
        super(PausableBuffSkillWrapper, self).__init__(skill)
        self.pausing_element: core.AbstractSkillWrapper = None

    def spend_time(self, time):
        if self.pausing_element.is_active():
            self.cooltimeLeft -= time
        else:
            return super(PausableBuffSkillWrapper, self).spend_time(time)
    
    def is_active(self):
        if self.pausing_element.is_active():
            return False
        else:
            return super(PausableBuffSkillWrapper, self).is_active()

    def is_usable(self):
        if self.pausing_element.is_active():
            return False
        else:
            return super(PausableBuffSkillWrapper, self).is_usable()

    def pauseWhile(self, el):
        self.pausing_element = el

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "luk"
        self.jobname = "호영"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'buff_rem', 'mess')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 40)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        SpiritAffinity = core.InformedCharacterModifier("정령친화", summon_rem = 10)
        FiendSeal = core.InformedCharacterModifier("괴이봉인", patt = 10, pdamage_indep = 10)
        RitualFanMastery = core.InformedCharacterModifier("부채 숙련", att = 25)
        ThirdEye = core.InformedCharacterModifier("심안", crit = 30, crit_damage = 10)
        FortuneFitness = core.InformedCharacterModifier("신체 단련", stat_main = 60)
        Asura = core.InformedCharacterModifier("수라", att = 50, crit = 10, crit_damage = 20, boss_pdamage = 20, armor_ignore = 20)
        AdvancedRitualFanMastery = core.InformedCharacterModifier("고급 부채 숙련", att = 40 + passive_level, pdamage_indep = 35 + passive_level)
        Enlightenment = core.InformedCharacterModifier("득도", pdamage = 10 + ceil(passive_level/2))
        DragonsEye = core.InformedCharacterModifier("점정", att = 10 + passive_level, pdamage_indep = 10 + passive_level, crit = 10 + passive_level, crit_damage = 10 + passive_level, armor_ignore = 10 + passive_level)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 0, 0)

        return [SpiritAffinity, FiendSeal, RitualFanMastery, ThirdEye, FortuneFitness, Asura, AdvancedRitualFanMastery, Enlightenment, DragonsEye, ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -5+0.5*ceil(passive_level/2))
        return [WeaponConstant, Mastery]
    
    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule('권술 : 미생강변', '권술 : 흡성와류', lambda sk: sk.is_time_left(2000, 1)), RuleSet.BASE)
        # ruleset.add_rule(ConcurrentRunRule('소울 컨트랙트', '선기 : 천지인 환영'), RuleSet.BASE)
        # ruleset.add_rule(ConcurrentRunRule('레디 투 다이', '선기 : 천지인 환영'), RuleSet.BASE)
        return ruleset

    def generate(self, vEhc, chtr : ck.AbstractCharacter):
        """
        하이퍼 : 천지인 리인포스 & 보스 킬러, 추적 귀화부 헤이스트, 흡성와류 헤이스트, 호접지몽 보스킬러
        """

        passive_level = chtr.get_base_modifier().passive_level + self.combat
        BASIC_HYPER = core.CharacterModifier(pdamage = 10, boss_pdamage = 15)

        # 소환수 지속시간과 버프 지속시간을 동시에 받는 스킬들 (해당 스킬들에는 rem = True 적용하지 말것)
        SUMMON_AND_BUFF = 1 + 0.01 * (chtr.get_base_modifier().buff_rem + chtr.get_base_modifier().summon_rem)
        
        # 1차
        ChunJiIn = ChunJiInWrapper()
        TalismanEnergy = core.StackSkillWrapper(core.BuffSkill("부적 도력", 0, 99999999), 100)
        #부채 타격 가정
        YeoUiSeon = core.DamageSkill("여의선 : 인", 540 + 30, 560 + 5*passive_level, 5, modifier = BASIC_HYPER + core.CharacterModifier(pdamage_indep = 5)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Mabong = core.DamageSkill("마봉 호로부", 360+210, 1000 + 10 * passive_level, 6, modifier = core.CharacterModifier(boss_pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper) # 흡수 360 공격 210

        # 2차
        Topa = core.DamageSkill("토파류 : 지", 540 + 30, 385 + 5*passive_level, 4, modifier = BASIC_HYPER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Topa_Clone = core.DamageSkill("토파류 : 허/실", 0, 385 + 5*passive_level, 4, cooltime = -1, modifier = BASIC_HYPER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Topa.onAfter(Topa_Clone)
        
        # 벞지 & 소환수 지속시간 둘다 적용
        Talisman_Clone = core.BuffSkill("환영 분신부", 900, 200*1000*SUMMON_AND_BUFF).wrap(PausableBuffSkillWrapper)
        Talisman_Clone_Attack = core.DamageSkill("환영 분신부(공격)", 0, 460 + 5*passive_level, 2 * 3, cooltime = 1500).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Talisman_Clone_Attack_Opt = core.OptionalElement(lambda : Talisman_Clone.is_active() and Talisman_Clone_Attack.is_available(), Talisman_Clone_Attack)
        Talisman_Clone_Attack.protect_from_running()

        Booster = core.BuffSkill("부채 가속", 0, 200*1000, rem=True).wrap(core.BuffSkillWrapper) # 펫버프

        # 3차
        ScrollEnergy = core.StackSkillWrapper(core.BuffSkill("두루마리 도력", 0, 99999999), 900)
        Pacho = core.DamageSkill("파초풍 : 천", 510 + 60, 265 + 2*passive_level, 5, modifier = BASIC_HYPER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Pacho_Clone = core.DamageSkill("파초풍 : 허/실", 0, 265 + 2*passive_level, 5, modifier = BASIC_HYPER, cooltime = -1).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Pacho.onAfter(Pacho_Clone)

        EarthQuake = core.DamageSkill("지진쇄 : 지", 510 + 30, 390 + 5*passive_level, 6, modifier = BASIC_HYPER, cooltime = 6000, red=True).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        EarthQuake_Clone = core.DamageSkill("지진쇄 : 허/실", 0, 390 + 5*passive_level, 6, modifier = BASIC_HYPER, cooltime = -1).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        EarthQuake.onAfter(EarthQuake_Clone)

        Talisman_Seeker = core.SummonSkill("추적 귀화부", 630, 1800 * 0.75, 390 + 5*passive_level, 5, 40*1000, rem = True).setV(vEhc, 0, 2, True).wrap(core.SummonSkillWrapper)

        Misaeng = core.DamageSkill("권술 : 미생강변", 540, 850 + 4*self.combat, 8, modifier = core.CharacterModifier(boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Misaeng_Debuff = core.BuffSkill("권술 : 미생강변(디버프)", 0, 60*1000, armor_ignore = 20, cooltime=-1).wrap(core.BuffSkillWrapper)
        Misaeng.onAfter(Misaeng_Debuff)

        # 4차
        Flames = core.DamageSkill("멸화염 : 천", 420 + 60, 340 + self.combat, 6, modifier = BASIC_HYPER, cooltime = 8000, red=True).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Flames_Clone = core.DamageSkill("멸화염 : 허/실", 0, 340 + self.combat, 6, modifier = BASIC_HYPER, cooltime = -1).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Flames.onAfter(Flames_Clone)

        GeumGoBong = core.DamageSkill("금고봉 : 인(1타)", 330 + 30, 260 + 3*self.combat, 10, cooltime = 11000, red=True, modifier = BASIC_HYPER + core.CharacterModifier(boss_pdamage = 30)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        GeumGoBong_2 = core.DamageSkill("금고봉 : 인(2타)", 300 + 30, 420 + self.combat, 8, cooltime = -1, modifier = BASIC_HYPER + core.CharacterModifier(boss_pdamage = 30)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        GeumGoBong.onAfter(GeumGoBong_2)

        # 추정치 딜레이 (점프부터 이펙트 완전소멸까지 프레임 분석)
        Thousand_Ton_Stone = core.DamageSkill("둔갑 천근석", 1530, 275 + 3*self.combat, 6, cooltime = 500).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Thousand_Ton_Stone_DOT = core.DotSkill("둔갑 천근석(출혈)", 0, 1000, 270 + self.combat, 1, 10000, cooltime = -1).setV(vEhc, 0, 2, False).wrap(core.SummonSkillWrapper)
        Thousand_Ton_Stone.onAfter(Thousand_Ton_Stone_DOT)

        Waryu = core.SummonSkill("권술 : 흡성와류", 990, 1000 * 0.8, 240 + 4*self.combat, 6, 40000, rem=True).setV(vEhc, 0, 2, True).wrap(core.SummonSkillWrapper)
        
        # 벞지 & 소환수 지속시간 둘다 적용
        Butterfly_Dream = core.BuffSkill("권술 : 호접지몽", 600, 100*1000 * SUMMON_AND_BUFF, pdamage_indep = 10).wrap(core.BuffSkillWrapper)
        Butterfly_Dream_Attack = core.DamageSkill("권술 : 호접지몽(공격)", 0, 275 + 3 * self.combat, 5, cooltime = 1000, modifier = core.CharacterModifier(boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Butterfly_Dream_Attack_Opt = core.OptionalElement(Butterfly_Dream_Attack.is_available, Butterfly_Dream_Attack)
        Butterfly_Dream_Attack.protect_from_running()

        # 하이퍼 액티브
        Miracle_Tonic = core.BuffSkill("선기 : 영약 태을선단", 540, 12*1000, cooltime = 100*1000).wrap(core.BuffSkillWrapper)
        Miracle_Tonic_Charge = core.SummonSkill("선기 : 영약 태을선단(회복)", 0, 1000, 0, 0, 12*1000, cooltime = -1).wrap(core.SummonSkillWrapper)
        Miracle_Tonic.onAfter(Miracle_Tonic_Charge)

        CloneBinding = core.DamageSkill("선기 : 분신 둔갑 태을선인", 540, 800, 8, cooltime = 200000).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)

        # 5차 공용 (베놈 버스트 생략)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 0, 0)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # 그란디스 여신의 축복 (아니마)
        # 아니마 신직업 등장시 공용코드화 할것
        AnimaGoddessBless = core.BuffSkill("그란디스 여신의 축복 (아니마)", 0, 40*1000, cooltime = 240*1000, red=True, pdamage = 10 + vEhc.getV(0, 0)).isV(vEhc, 0, 0).wrap(core.BuffSkillWrapper)

        # 환영 분신부를 대체하는 스킬 (알고리즘 구현 필요)
        # 환영 분신부 지속중에만 사용가능, 발동 중에는 환영 분신부의 지속시간이 감소하지 않음
        Clone_Rampage = core.BuffSkill("선기 : 극대 분신난무", 900, 30*1000, cooltime = 200*1000, red=True).wrap(core.BuffSkillWrapper)
        Clone_Rampage_Attack = core.DamageSkill("선기 : 극대 분신난무(공격)", 0, 460 + 5*passive_level + 400 + vEhc.getV(0, 0) * 16, 2 * 12, cooltime = 1500).setV(vEhc, 0, 2, True).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        Clone_Rampage_Attack_Opt = core.OptionalElement(lambda : Clone_Rampage.is_active() and Clone_Rampage_Attack.is_available(), Clone_Rampage_Attack)
        Clone_Rampage_Attack.protect_from_running()

        Summon_Sanryung = core.SummonSkill("권술 : 산령소환", 900, 3000, vEhc.getV(0, 0) * 36 + 900, 8, (vEhc.getV(0, 0)//2 + 45)*1000, cooltime = 200*1000, red=True).wrap(core.SummonSkillWrapper)
        Summon_Sanryung_Bonus = core.DamageSkill("권술 : 산령소환(연계성공)", 0, vEhc.getV(0, 0)*14 + 350, 4, cooltime = 3000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        Summon_Sanryung_Bonus_Opt = core.OptionalElement(lambda : Summon_Sanryung.is_active() and Summon_Sanryung_Bonus.is_available(), Summon_Sanryung_Bonus)
        Summon_Sanryung_Bonus.protect_from_running()

        Nansin = core.BuffSkill("선기 : 강림 괴력난신", 900, 30*1000, cooltime= 200*1000, red=True, pdamage = vEhc.getV(0, 0)*2+20).wrap(core.BuffSkillWrapper)
        Nansin_Stack = core.StackSkillWrapper(core.BuffSkill("선기 : 강림 괴력난신(스택)", 0, 99999999), 12)
        Nansin_Attack = core.DamageSkill("선기 : 강림 괴력난신(신들의 일격)", 0, vEhc.getV(0, 0)*34 + 850, 8, cooltime = 1500).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Nansin_Final = core.DamageSkill("선기 : 강림 괴력난신(신들의 강림)", 0, vEhc.getV(0, 0)*40+1000, 15*6, cooltime = -1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Nansin_Final_Buff = core.BuffSkill("선기 : 강림 괴력난신(신들의 강림)(버프)", 0, 30000, cooltime=-1).wrap(core.BuffSkillWrapper)

        Nansin_Attack_Opt = core.OptionalElement(lambda : Nansin_Attack.is_available() and Nansin_Stack.judge(12, 1), Nansin_Attack)
        Nansin_Attack.protect_from_running()

        Elemental_Clone_Passive = core.DamageSkill("선기 : 천지인 환영(패시브)", 0, 625 + 25*vEhc.getV(0, 0), 6, cooltime = 5000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Elemental_Clone_Passive_Opt = core.OptionalElement(Elemental_Clone_Passive.is_available, Elemental_Clone_Passive)
        Elemental_Clone_Passive.protect_from_running()

        Elemental_Clone = core.BuffSkill("선기 : 천지인 환영", 540, 30*1000, cooltime = 100*1000, red=True).wrap(core.BuffSkillWrapper)
        Elemental_Clone_Active = core.DamageSkill("선기 : 천지인 환영(액티브)", 0, 625 + 25*vEhc.getV(0, 0), 6, cooltime = 2000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Elemental_Clone_Active_Stack = core.StackSkillWrapper(core.BuffSkill("선기 : 천지인 환영(재등장 스택)", 0, 99999999), 2)
        Elemental_Clone.onAfter(Elemental_Clone_Active_Stack.stackController(2))

        Elemental_Clone_Active_Opt = core.OptionalElement(Elemental_Clone_Active.is_available, Elemental_Clone_Active)
        Elemental_Clone_Active.protect_from_running()

        Elemental_Clone_Opt = core.OptionalElement(Elemental_Clone.is_active, Elemental_Clone_Active_Opt, Elemental_Clone_Passive_Opt)

        ### Skill Wrapper ###
        # 그란디스 여신의 축복(아니마)
        def gainEnergy(energy: core.StackSkillWrapper, stack):
            return core.OptionalElement(
                AnimaGoddessBless.is_active,
                energy.stackController(stack*0.01*(45+vEhc.getV(0,0))),
                energy.stackController(stack)
            )

        # 천지인 연계
        AddChun = ChunJiIn.add_element("천")
        AddJi = ChunJiIn.add_element("지")
        AddIn = ChunJiIn.add_element("인")
        FillElement = ChunJiIn.fill_element()
        for el in [AddChun, AddJi, AddIn, FillElement]:
            el.onAfter(gainEnergy(ScrollEnergy, 15))
            el.onAfter(core.OptionalElement(partial(ChunJiIn.is_stack, 1), gainEnergy(TalismanEnergy, 10)))
            el.onAfter(core.OptionalElement(partial(ChunJiIn.is_stack, 2), gainEnergy(TalismanEnergy, 15)))
            el.onAfter(core.OptionalElement(partial(ChunJiIn.is_stack, 3), gainEnergy(TalismanEnergy, 20)))
            el.onAfter(core.OptionalElement(partial(ChunJiIn.is_stack, 3), Summon_Sanryung_Bonus_Opt))
            el.onAfter(core.OptionalElement(partial(ChunJiIn.is_stack, 3),
                core.OptionalElement(Elemental_Clone.is_active, ChunJiIn.choice_reset([EarthQuake, Flames, GeumGoBong]))))
            el.onAfter(core.OptionalElement(partial(ChunJiIn.is_stack, 3), ChunJiIn.reset_elements()))

        for sk in [Pacho, Flames]:
            sk.onAfter(AddChun)
        
        for sk in [Topa, EarthQuake]:
            sk.onAfter(AddJi)
        
        for sk in [YeoUiSeon, GeumGoBong]:
            sk.onAfter(AddIn)

        # 부적 도술
        TalismanConstraint = core.ConstraintElement("부적 도력 100", TalismanEnergy, partial(TalismanEnergy.judge, 100, 1))
        TalismanConsume = TalismanEnergy.stackController(-100)
        TalismanConsume.onAfter(gainEnergy(ScrollEnergy, 200))
        for sk in [Mabong, Talisman_Clone, Talisman_Seeker]:
            sk.onConstraint(TalismanConstraint)
            sk.onAfter(TalismanConsume)

        # 두루마리 도술
        ScrollConstraint = core.ConstraintElement("두루마리 도력 900", ScrollEnergy, partial(ScrollEnergy.judge, 900, 1))
        ScrollConsume = ScrollEnergy.stackController(-900)
        for sk in [Misaeng, Waryu, Butterfly_Dream, Summon_Sanryung]:
            sk.onConstraint(ScrollConstraint)
            sk.onAfter(ScrollConsume)

        # 태을선단
        Miracle_Tonic_Charge.onTick(gainEnergy(TalismanEnergy, 35))
        Miracle_Tonic_Charge.onTick(gainEnergy(ScrollEnergy, 350))

        # 극대 분신난무
        Clone_Rampage.onConstraint(core.ConstraintElement("환영 분신부 지속중", Talisman_Clone, Talisman_Clone.is_active))
        Clone_Rampage.onAfter(Talisman_Clone.controller(1))
        Talisman_Clone.pauseWhile(Clone_Rampage)

        # 괴력난신
        Nansin.onAfter(Nansin_Final.controller(30*1000-1)) # 버프 종료 직전에 막타 발동
        Nansin.onAfter(Nansin_Stack.stackController(-12))
        Nansin_Attack.onAfter(Nansin_Stack.stackController(-12))
        AddNansinStack = Nansin_Stack.stackController(1)
        AddNansinStack.onAfter(Nansin_Attack_Opt)
        Nansin_Final.onAfter(Nansin_Final_Buff)

        # 천지인 환영
        Elemental_Clone_Passive.onAfter(FillElement)
        Elemental_Clone_Active.onAfter(FillElement)

        Elemental_Clone_Active_Reset = Elemental_Clone_Active.controller(1, "reduce_cooltime_p")
        Elemental_Clone_Active.onAfter(core.OptionalElement(partial(Elemental_Clone_Active_Stack.judge, 1, 1), Elemental_Clone_Active_Reset))
        Elemental_Clone_Active_Reset.onAfter(Elemental_Clone_Active_Stack.stackController(-1))
        
        # 신들의 강림 후 30초동안 천/지/인 속성 스킬 및 허/실 스킬의 데미지 20% 증가
        ELEMENT_SKILLS = [YeoUiSeon, Topa, Topa_Clone, Pacho, Pacho_Clone, EarthQuake, EarthQuake_Clone, Flames, Flames_Clone, GeumGoBong, GeumGoBong_2]
        for sk in ELEMENT_SKILLS:
            sk.add_runtime_modifier(Nansin_Final_Buff, lambda sk: core.CharacterModifier(pdamage = 20*sk.is_active()))
        
        # 환영 분신부, 극대 분신난무, 호접지몽, 천지인 환영, 괴력난신
        for base in ELEMENT_SKILLS + [Mabong, CloneBinding]:
            for opt in [Talisman_Clone_Attack_Opt, Clone_Rampage_Attack_Opt, Butterfly_Dream_Attack_Opt, Elemental_Clone_Opt, AddNansinStack]:
                base.onAfter(opt)

        return(Topa,
            [globalSkill.maple_heros(chtr.level, name = "아니마의 용사", combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                Booster, Talisman_Clone, Butterfly_Dream, Clone_Rampage, Nansin, Nansin_Final_Buff, Elemental_Clone, Miracle_Tonic, AnimaGoddessBless, ReadyToDie,
                globalSkill.soul_contract()] +\
            [Talisman_Seeker, Waryu, Summon_Sanryung, Miracle_Tonic_Charge] +\
            [Misaeng_Debuff, Talisman_Clone_Attack, Butterfly_Dream_Attack, Clone_Rampage_Attack, Elemental_Clone_Active,
                Elemental_Clone_Passive, Nansin_Attack, Summon_Sanryung_Bonus, Nansin_Final] +\
            [GeumGoBong, EarthQuake, Flames, Mabong, Misaeng, CloneBinding, MirrorBreak, MirrorSpider] +\
            [Topa])
