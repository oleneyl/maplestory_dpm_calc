from functools import partial
'''

store.py :: Store for graph element

사용자들은 그래프를 빌드한 이후에, 그래프 간의 상호작용을 정의하거나, 그래프 내의 원소들에 제약을 부여하는 등 내부 요소에 접근하고 싶을 수 있습니다.
그러나, ScheduleGraph Object는 내부적으로는 모든 그래프 요소를 Tracking 할 수 있으나, 명시적으로 그래프 요소에 접근하는 행위를 허용하고 있지는 않습니다.
이는 그래프 요소에 접근하는 행위가 통제되지 않은 변경을 유발하여 내부 로직을 망가뜨리거나, 잘못된 결과물을 제공할 수도 있기 때문입니다.

이와 같은 불상사를 방지하면서, 필요한 경우에는 내부 요소에 접근할 수 있도록 Store Class를 제공합니다. Store는 다음과 같은 기능을 제공합니다.

(1) 명시된 접근자에 대한 그래프 요소만을 접근 허용함으로서 보안을 보장합니다.
(2) 지원되는 함수를 통한 요소 변경을 권장함으로서 최대한 사용자가 잘못된 설정을 시도하는 행위를 방지합니다.
(3) 다른 Store과의 상호작용을 정의하여 여러개의 Graph를 동시에 연산할 수 있도록 돕습니다.

'''


class Store():
    def __init__(self, allowed_keywords_and_elements):
        self._allowed_keywords = [i for i in allowed_keywords_and_elements]
        self._allowed_keywords_and_elements = allowed_keywords_and_elements
        for kwd in allowed_keywords_and_elements:
            setattr(self, kwd, allowed_keywords_and_elements[kwd])
    
    def check_exist(self, kwd):
        return (kwd in self._allowed_keywords)
        
    def synchronize(self, main_skill, following_skill, mode = 'only_last_use'):
        '''Force following_skill's skill run with main_skill.
        
         -- mode -- 
         only_last_use : only last skill use will be modified by this constraint.
         every_use : every skill usage get duty to retain following_skill's skill timing lag.
         
        '''
        def prevent_skill_use(_main_skill, _following_skill):
            following_cooltime = _following_skill.skill.cooltime
            main_skill_left = _main_skill.cooltimeLeft
            if main_skill_left < following_cooltime * 2:
                return False
            else:
                return True
        
        if main_skill.skill.cooltime < following_skill.skill.cooltime:
            following_skill.onConstraint(jt.ConstraintElement('Store.synchronize',main_skill, main_skill.is_active))
        else:
            if mode == 'only_last_use':
                following_skill.createConstraint('Store.synchronize::only_last_use', main_skill, partial(prevent_skill_use, main_skill, following_skill) ) )
            elif mode == 'every_use':
                raise NotImplementedError('Not maded yet!')
                
    def prevent_collision(self, first_skill, second_skill):
        first_skill.createConstraint('Store.prevent_collision', second_skill, second_skill.isOffOn)
        second_skill.createConstraint('Store.prevent_collision', first_skill, first_skill.isOffOn)
    
    