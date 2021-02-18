from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConditionRule
from . import globalSkill, jobutils
from .jobclass import heroes
from .jobbranch import magicians
from math import ceil
from typing import Any, Dict

class LuminousStateController(core.BuffSkillWrapper):
    DARK = 0
    LIGHT = 1
    EQUAL = 2
    STACK = 10000
    def __init__(self, skill, buff_rem):
        super(LuminousStateController, self).__init__(skill)
        self.state = self.LIGHT
        self.currentState = self.LIGHT
        self.stack = self.STACK
        
        self.remain = 0
        self.buff_rem = buff_rem
        self.equalCallback = lambda:None
        
    def spend_time(self, time : int) -> None:
        super(LuminousStateController, self).spend_time(time)
        self.remain -= time
        #이퀄이 끝나면, 다음 상태로 진입합니다.
        if self.remain < 0 and self.state == LuminousStateController.EQUAL:
            self.state = self.currentState
            self.stack = LuminousStateController.STACK

    def _modify_stack(self, stack):
        self.stack -= stack * 1.05 # 다크라이트 마스터리 1.05배
        
        if self.stack <= 0:
            self.stack = LuminousStateController.STACK
            self.currentState = 1 - self.currentState
            self.state = LuminousStateController.EQUAL
            self.remain = 17 * (1 + 0.01* self.buff_rem) * 1000
            self.equalCallback()
            
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, '루미너스 스택 변경', spec = 'graph control')     
    
    def memorize(self):
        self.stack = LuminousStateController.STACK
        self.currentState = 1 - self.currentState
        self.state = LuminousStateController.EQUAL
        self.remain = 17*1000
        self.equalCallback()
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname = '메모라이즈', spec = 'graph control')
    
    def modifyStack(self, stack):
        return core.create_task('스택 변경', partial(self._modify_stack, stack), self)

    def getState(self):
        return self.state

    def isLight(self):
        return (self.state == LuminousStateController.LIGHT)

    def isDark(self):
        return (self.state == LuminousStateController.DARK)
    
    def isEqual(self):
        return (self.state == LuminousStateController.EQUAL)
    
    def isNotEqual(self):
        return (self.state != LuminousStateController.EQUAL)

    def isEqualLeft(self, time):
        return self.remain - time > 0

class PunishingResonatorWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2, stateGetter):
        skill = core.SummonSkill("퍼니싱 리소네이터", 990, 6000/28, 0, 0, 6000-1, cooltime = 30 * 1000, red=True, modifier = core.CharacterModifier(crit = 15)).isV(vEhc,num1,num2)
        super(PunishingResonatorWrapper, self).__init__(skill)
        self.skillList = [
            (250 + vEhc.getV(3,2)*10, 5),
            (350 + vEhc.getV(3,2)*14, 4),
            (340 + vEhc.getV(3,2)*13, 6)
        ]
        self.vlevel = vEhc.getV(3,2)
        self.getState = stateGetter

    def get_damage(self) -> float:
        return self.skillList[self.getState()][0]

    def get_hit(self) -> float:
        return self.skillList[self.getState()][1]

class LightAndDarknessWrapper(core.DamageSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        skill = core.DamageSkill("빛과 어둠의 세례", 840, 15 * vEhc.getV(num1,num2)+375, 13 * 7, cooltime = 45*1000, red=True, modifier = core.CharacterModifier(armor_ignore = 100, crit = 100)).isV(vEhc,num1,num2)
        super(LightAndDarknessWrapper, self).__init__(skill)
        self.stack = 12

    def reduceStack(self):
        self.stack -= 1
        if self.stack <= 0:
            self.stack = 12
            self.cooltimeLeft = 0
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname = '빛과 어둠의 세례 스택 증가', spec = 'graph control')

class LiberationOrbActiveWrapper(core.DamageSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        self.light = 0
        self.dark = 0
        skill = core.DamageSkill("리버레이션 오브(액티브)", 0, 400 + 17 * vEhc.getV(num1,num2), 10, cooltime = 1000, modifier = core.CharacterModifier(crit = 100)).isV(vEhc,num1,num2)
        super(LiberationOrbActiveWrapper, self).__init__(skill)

    def _setStack(self, light, dark):
        self.light = light.stack
        self.dark = dark.stack
        return self._result_object_cache

    def setStack(self, light, dark):
        task = core.Task(self, partial(self._setStack, light, dark))
        return core.TaskHolder(task, name="리버레이션 오브 데미지 설정")

    def get_damage(self):
        damage = self.skill.damage
        if self.light == self.dark:
            damage += 25
        damage += max(0, self.light + self.dark - 1) * 50
        return damage

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = (0, 40)
        self.vEnhanceNum = 13
        self.jobtype = "INT"
        self.jobname = "루미너스"
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'crit', 'boss_pdamage')
        self.preEmptiveSkills = 2

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule('소울 컨트랙트', '루미너스 상태', lambda state: state.isEqual() and state.isEqualLeft(20000)), RuleSet.BASE) # TODO: 소울 컨트랙트의 벞지 적용된 지속시간을 가져와야 함
        ruleset.add_rule(ConditionRule('퍼니싱 리소네이터', '루미너스 상태', lambda state: state.isEqual()), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self) -> core.CharacterModifier:
        return core.CharacterModifier(pdamage=32, armor_ignore=32)
                
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        PowerOfLight = core.InformedCharacterModifier("파워 오브 라이트",stat_main = 20)
        SpellMastery = core.InformedCharacterModifier("스펠 마스터리",att = 10, crit=15, pdamage=15)
        HighWisdom = core.InformedCharacterModifier("하이 위즈덤",stat_main = 40)
        MagicMastery = core.InformedCharacterModifier("매직 마스터리",att = 30 + passive_level, crit_damage = 15 + passive_level // 3, crit = 15 + passive_level // 3)
        DarknessSocery = core.InformedCharacterModifier("다크니스 소서리", pdamage_indep = 40 + self.combat, armor_ignore = 40 + self.combat)
        MorningStarfall = core.InformedCharacterModifier("모닝 스타폴(패시브)",pdamage_indep = 30 + self.combat)
        
        return [PowerOfLight, SpellMastery, HighWisdom, MagicMastery, MorningStarfall, DarknessSocery]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]): 
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=95+ceil(passive_level / 2))
        
        BlessOfDarkness =  core.InformedCharacterModifier("블레스 오브 다크니스",att = 30)   #15 -> 24 -> 30
        DarknessSoceryActive = core.InformedCharacterModifier("다크니스 소서리(사용)", prop_ignore = 10)

        return [WeaponConstant, Mastery, BlessOfDarkness, DarknessSoceryActive]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        아포 22회 / 라리플 25회가 이퀄리브리엄 진입까지 요구됨
        
        소울 컨트랙트는 이퀄리브리엄에 맞춰 사용
        퍼니싱 리소네이터는 이퀄리브리엄에 맞춰 사용
        메모라이즈는 이퀄이 아니고 쿨타임이 돌아 있으면 사용
        리버레이션 오브는 쿨마다 사용
        '''
        ######   Skill   ######
        DarkAffinity = core.CharacterModifier(pdamage_indep = 5) # 어둠 마법 강화

        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper) # 펫버프
        PodicMeditaion = core.BuffSkill("포딕 메디테이션", 0, 1800000, att = 40).wrap(core.BuffSkillWrapper) # 펫버프
        DarkCrescendo = core.BuffSkill("다크 크레센도", 0, (180 + 4*self.combat) * 1000, pdamage = 28, rem = True).wrap(core.BuffSkillWrapper) # 펫버프. 스택 제대로 계산 필요함.
        DarknessSocery = core.BuffSkill("다크니스 소서리(버프)", 270, (180 + 5*self.combat) * 1000, rem = True).wrap(core.BuffSkillWrapper)
    
        LuminousState = LuminousStateController(core.BuffSkill("루미너스 상태", 0, 99999999), chtr.get_base_modifier().buff_rem)

        #Damage Skills
        LightReflection = core.DamageSkill("라이트 리플렉션", 690, 400+5*self.combat, 4, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        Apocalypse = core.DamageSkill("아포칼립스", 720, 340+4*self.combat, 7, modifier = core.CharacterModifier(pdamage = 20) + DarkAffinity).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AbsoluteKill = core.DamageSkill("앱솔루트 킬", 630, 385+3*self.combat, 7*2, modifier = core.CharacterModifier(pdamage = 20, crit = 100, armor_ignore=40) + DarkAffinity).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        AbsoluteKillCooltimed = core.DamageSkill('앱솔루트 킬(이퀄X)', 630, 385+3*self.combat, 7, cooltime = 12000, red=True, modifier = core.CharacterModifier(pdamage = 20, crit = 100, armor_ignore=40) + DarkAffinity).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper) # 안쓰는게 dpm이 더 높음

        # Hyper
        Memorize = core.BuffSkill("메모라이즈", 900, 10, cooltime = 150 * 1000).wrap(core.BuffSkillWrapper)
        HerosOath = core.BuffSkill("히어로즈 오쓰", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)

        # 5th
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        DoorOfTruth = core.SummonSkill("진리의 문", 870, 3030, 375 + 15 * vEhc.getV(4,4), 10, (25 + vEhc.getV(4,4) // 2) * 1000, cooltime = -1).isV(vEhc,3,3).wrap(core.SummonSkillWrapper)   #이퀄시 사용 가능해짐.
        PunishingResonator = PunishingResonatorWrapper(vEhc, 2, 1, LuminousState.getState)
        LightAndDarkness = LightAndDarknessWrapper(vEhc, 0, 0)
        LiberationOrbPassive = core.DamageSkill("리버레이션 오브(패시브)", 0, 375+15*vEhc.getV(0,0), 4, cooltime=6000).isV(vEhc,0,0).wrap(core.DamageSkillWrapper) # TODO: 여러번 타격 가능한지 확인할것
        LiberationOrbStackLight = core.StackSkillWrapper(core.BuffSkill("리버레이션 오브(스택)(빛)", 0, 99999999), 4)
        LiberationOrbStackDark = core.StackSkillWrapper(core.BuffSkill("리버레이션 오브(스택)(어둠)", 0, 99999999), 4)
        LiberationOrb = core.BuffSkill("리버레이션 오브", 690, 45000, cooltime=180*1000, red=True).wrap(core.BuffSkillWrapper)
        LiberationOrbActive = LiberationOrbActiveWrapper(vEhc,0,0)
        LiberationOrbActiveStack = core.StackSkillWrapper(core.BuffSkill("리버레이션 오브(액티브)(스택)", 0, 99999999), 20)

        # Skill Wrapper - Basic Attack
        LightReflection.onAfter(LuminousState.modifyStack(390))
        Apocalypse.onAfter(LuminousState.modifyStack(410 + 40)) # 아포칼립스-리차지 +40
        
        Attack = core.DamageSkill('기본 공격', 0, 0, 0).wrap(core.DamageSkillWrapper)
        IsLight = core.OptionalElement(LuminousState.isLight, LightReflection, Apocalypse, name = '빛이면 라리플 사용')
        IsEqual = core.OptionalElement(LuminousState.isEqual, AbsoluteKill, IsLight, name = '이퀄리브리엄이면 앱킬 사용')
        Attack.onAfter(IsEqual)

        for sk in [LightReflection, Apocalypse, AbsoluteKillCooltimed]:
            jobutils.create_auxilary_attack(sk, 0.5, "(선파이어/이클립스)")

        AbsoluteKillCooltimed.onConstraint(core.ConstraintElement("비이퀄때만 앱킬 쿨타임", LuminousState, LuminousState.isNotEqual))
        
        # Skill Wrapper - Memorize
        Memorize.onAfter(core.create_task("메모라이즈", LuminousState.memorize, LuminousState))
        Memorize.onConstraint(core.ConstraintElement('이퀄일때는 사용하지 않음', LuminousState, LuminousState.isNotEqual))

        # Skill Wrapper - Door of Truth
        LuminousState.equalCallback = partial(DoorOfTruth.set_disabled_and_time_left, 1)
        
        # Skill Wrapper - Light and Darkness
        for absolute in [AbsoluteKillCooltimed, AbsoluteKill]:
            absolute.onAfter(core.create_task('빛과 어둠의 세례 쿨다운 스택 1 감소', LightAndDarkness.reduceStack, LightAndDarkness))

        # Skill Wrapper - Liberation Orb
        LiberationOrb.onAfter(LiberationOrbActive.setStack(LiberationOrbStackLight, LiberationOrbStackDark))
        LiberationOrb.onAfter(LiberationOrbActiveStack.stackController(20))
        LiberationOrb.onAfter(LiberationOrbStackLight.stackController(-4))
        LiberationOrb.onAfter(LiberationOrbStackDark.stackController(-4))
        LiberationOrb.onConstraint(core.ConstraintElement("리버레이션 오브 마력 제한",
            LiberationOrbStackDark, lambda: LiberationOrbStackDark.stack + LiberationOrbStackLight.stack >= 1))

        LiberationOrbPassive.onAfter(core.OptionalElement(LuminousState.isLight, LiberationOrbStackLight.stackController(1)))
        LiberationOrbPassive.onAfter(core.OptionalElement(LuminousState.isDark, LiberationOrbStackDark.stackController(1)))
        LiberationOrbActive.onAfter(LiberationOrbActiveStack.stackController(-1))
        
        UseLiberationOrbPassive = core.OptionalElement(
            lambda: LiberationOrbActiveStack.judge(0, -1) and LiberationOrbPassive.is_available(), LiberationOrbPassive, name="리버레이션 오브(패시브) 조건")
        UseLiberationOrbActive = core.OptionalElement(
            lambda: LiberationOrb.is_active() and LiberationOrbActiveStack.judge(1, 1) and LiberationOrbActive.is_available(),
            LiberationOrbActive, name="리버레이션 오브(액티브) 조건")
        for sk in [LightReflection, Apocalypse, AbsoluteKill, AbsoluteKillCooltimed]:
            sk.onAfter(UseLiberationOrbPassive)
            sk.onAfter(UseLiberationOrbActive)
        
        LiberationOrbPassive.protect_from_running()
        LiberationOrbActive.protect_from_running()

        # Overload Mana
        overload_mana_builder = magicians.OverloadManaBuilder(vEhc, 1, 2)
        for sk in [LightReflection, Apocalypse, DoorOfTruth, PunishingResonator, AbsoluteKill, AbsoluteKillCooltimed, LightAndDarkness, LiberationOrbActive]:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()

        return(Attack, 
                [LuminousState, globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_wind_booster(),
                    Booster, PodicMeditaion, DarknessSocery, DarkCrescendo, HerosOath, Memorize, OverloadMana, LiberationOrb,
                    globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()] +\
                [LightAndDarkness, LiberationOrbActive, LiberationOrbPassive, AbsoluteKillCooltimed] +\
                [PunishingResonator, DoorOfTruth, MirrorBreak, MirrorSpider] +\
                [] +\
                [Attack])