from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

def PhalanxChargeWrapper(vEhc, num1, num2):
    PhalanxCharge = core.DamageSkill("시그너스 팔랑크스", 780, 450 + 18*vEhc.getV(num1, num2), 40 + vEhc.getV(num1, num2), cooltime = 30 * 1000).isV(vEhc, num1, num2).wrap(core.DamageSkillWrapper)
    return PhalanxCharge

class CygnusBlessWrapper(core.BuffSkillWrapper):
    def __init__(self, enhancer, skill_importance, enhance_importance, serverlag = 3, level = 230):
        self.isUpgraded = (level >= 245) 
        self.enhancer = enhancer
        self.skill_importance = skill_importance
        self.enhance_importance = enhance_importance
        
        # 스킬 딜레이, 쿨타임 확인 필요
        skill = core.BuffSkill("초월자 시그너스의 축복" if isUpgraded else "여제 시그너스의 축복" , 450, 45000, cooltime = 240*1000).wrap(core.BuffSkillWrapper)
        super(CygnusBlessWrapper, self).__init__(skill)

        self.passedTime = 0
        self.serverlag = serverlag

    def spend_time(self, time):
        if self.onoff:
            self.passedTime += time
        super(CygnusBlessWrapper, self).spend_time(time)
    
    #세부값 확인해서 변경필요
    #MP 500 소비, 45초 동안 데미지 25% 증가, 일정 시간마다 HP 4%씩 회복 및 데미지 3% 추가 증가, 시그너스의 축복으로 증가하는 데미지는 합 적용이며 최대 90%까지 증가
    #MP 500 소비, 45초 동안 데미지 25% 증가 및 최대 HP의 일정 비율로 피해를 입히는 공격을 포함한 피격 데미지 5% 감소, 일정 시간마다 HP 7%씩 회복 및 데미지 5% 추가 증가, 시그너스의 축복으로 증가하는 데미지는 합 적용이며 최대 120%까지 증가

    def calc_damage(self):
        interval = 4
        if self.isUpgraded:
            pd_value = min(25 + 5 * (self.passedTime // ((interval + self.serverlag) * 1000)), 120)
        else:
            pd_value = min(25 + 3 * (self.passedTime // ((interval + self.serverlag) * 1000)), 90)
        return pd_value

    def get_modifier(self):
        if self.onoff:
            return core.CharacterModifier(pdamage = self.calc_damage())
        else:
            return core.CharacterModifier()
        
    def _use(self, rem = 0, red = 0):
        self.passedTime = 0
        return super(CygnusBlessWrapper, self)._use(rem = rem, red = red)