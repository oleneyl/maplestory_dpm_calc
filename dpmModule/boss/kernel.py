from ..kernel.core import *

'''Boss Pattern
(1) Boss Pattern DO NOT HAVE delay, because each skill represents boss's state only.
(2) Each pattern has state flag which represents boss's state during given action is progressing.

(1) 보스 패턴은 딜레이를 가지지 않습니다. 이는 보스 패턴이 보스의 상태를 기술하기 위함이기 때문이며,
    데미지를 가하는 주체가 보스가 아닌 유저이기 때문입니다.
(2) 보스 패턴은 state flag를 가집니다. 

예를 들어, 패턴이 종료되기 1초 전이고 현재 상황이 X라면 Y를 한다 라는 걸 구현하고 싶다면?
Policy를 사용합니다.

Policy는 스킬 단위로 사용될 수도 있고 (Local policy) 전역 단위로 사용될 수도 있습니다 ( Global Policy )
하지만 Local Policy는 연산량을 극도로 늘릴 위험이 있으며 기본 template function의 변화를 야기하므로 
Global Policy만을 우선적으로 허용합니다.
'''


class BossPattern(AbstractSkill):
    def __init__(self, name, remain, boss_state_flag, cooltime = 0):
        super(BossPattern, self).__init__(name, 0, cooltime = cooltime, rem = False, red = False)
        self.remain = remain
        self.accessible_boss_state = boss_state_flag

    def get_explanation(self, lang = "ko", expl_level = 2):
        '''level 0 / 1 / 2
        '''
        pass

class BossPatternWrapper(AbstractSkillWrapper):
    def __init__(self, skill, name = None):
        super(BossPatternWrapper, self).__init__(skill, name = name)
        self.onoff = False
        
    def _use(self, **kwargs):
        self.cooltimeLeft = self.skill.cooltime
        self.timeLeft = self.skill.remain
        
    def spend_time(self, time):
        self.timeLeft -= time
        self.cooltimeLeft -= time
        if self.timeLeft < 0:
            self.onoff = False
        if self.cooltimeLeft < 0:
            self.available = True

class BossScenario(ScheduleGraph):
    def __init__(self):
        self.patterns = []
        self._no_action_exist_pattern = BossPattern("정지 상태", 99999999, AccessibleBossState.ALWAYS).wrap(BossPatternWrapper)
        
    def build_graph(self, patterns):
        for pat in patterns:
            self.patterns.append([pat, pat.build_task()])
        
        self.patterns.append([self._no_action_exist_pattern, self._no_action_exist_pattern.build_task()])


class BossScenarioPolicy():
    '''BossScenarioPolicy는 유저가 특정 Flag에서 특정 상황에 대해 어떻게 반응할 지를 정의합니다.
    다양한 Policy를 적용함으로서 유저는 패턴에 대해 원하는 대로 대응할 수 있습니다.
    '''
    def __init__(self, avail_type, avail_flag):
        self.avail_type = avail_type
        self.avail_flag = avail_flag
    
    def judge(self, scenario_scheduler, wrapper):
        raise NotImplementedError(" You must Implement BossScenarioPolicy.judge ")



class BossScenarioScheduler(Scheduler):
    '''BossScenarioScheduler Handle Boss graph directly. This if difference btw user and boss.
    User is not controlled directly.
    
    BossScenarioScheduler는 자체적으로 보스 액션을 시뮬레이션합니다. 따라서 Scheduler의 기존
    Simulator과의 호환성을 보장합니다. 모든 보스 관련 행동은 BossScenarioScheduler 내부에서 
    처리되며 외부로 노출되지 않습니다.
    '''
    def __init__(self, boss_scenario, user_scenario):
        super(BossScenarioScheduler, self).__init__(user_scenario)
        self.boss_scenario = boss_scenario
        self.boss_action_remain_time = 0
        self.current_action = BossPattern("정지 상태", 0, AccessibleBossState.NO_FLAG)
        
    def initialize(self, time):
        super(BossScenarioScheduler, self).initialize(time)
        
    def dequeueBossAction(self):
        for wrp, sk in self.boss_scenario.patterns:
            if wrp.is_usable():
                return sk

    def dequeue(self):
        '''Boss Flag를 체크하도록 해야 합니다. Boss Flag는 해당 상황에서 사용할 지 안할지를
        정의하는 값입니다. 
        
        기본값 : 
        Buff : 31 (무시하고 사용)
        Damage : 1 (공격 가능 시에만 사용)
        Summon : 31 (무시하고 사용)
        '''
        current_action_state = self.current_action.accessible_boss_state
        if not self.pendingTime:
            for wrp, buff in self.graph.buff:
                if wrp.is_usable() and (not wrp.onoff) and (wrp.accessible_boss_state & current_action_state):
                    return buff
        
            for wrp, summon in self.graph.summon:
                if wrp.is_usable() and (not wrp.onoff) and (wrp.accessible_boss_state & current_action_state):
                    return summon
                    
            for wrp, damage in self.graph.damage:
                if wrp.is_usable() and (wrp.accessible_boss_state & current_action_state):
                    return damage
            
            return self.graph.defaultTask[1]

    
    def spendBossTime(self, time):
        self.boss_action_remain_time -= time
        for wrp, _ in self.boss_scenario.patterns:
            wrp.spend_time(time)
    
    def activateBossAction(self, action):
        self.boss_action_remain_time = action.remain
        self.current_action = action
    
    def spend_time(self, time):
        time_left_to_spend = time
        while time_left_to_spend > self.boss_action_remain_time:
            super(BossScenarioScheduler, self).spend_time(self.boss_action_remain_time)
            self.spendBossTime(self.boss_action_remain_time)
            time_left_to_spend -= self.boss_action_remain_time
            action = self.dequeueBossAction()
            self.activateBossAction(action)
            
    
            
            
            
            
            
            