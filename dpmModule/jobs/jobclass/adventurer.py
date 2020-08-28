from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...character import characterKernel as ck
# 모험가 및 모험가 직업 공용 5차스킬 통합코드

#TODO: 얼닼사

# 모험가 법사
# 3% 증가로 알고있는데... 확인필요

class InfinityWrapper(core.BuffSkillWrapper):
    def __init__(self, combat, serverlag = 3):
        skill = core.BuffSkill("인피니티", 600, (40+combat)*1000, cooltime = 180 * 1000, rem = True, red = True)
        super(InfinityWrapper, self).__init__(skill)
        self.passedTime = 0
        self.serverlag = serverlag
        self.combat = combat
        
    def spend_time(self, time):
        if self.onoff:
            self.passedTime += time
        super(InfinityWrapper, self).spend_time(time)
            
    def get_modifier(self):
        if self.onoff:
            return core.CharacterModifier(pdamage_indep = (70 + self.combat + 3 * (self.passedTime // ((4+self.serverlag)*1000))) )
        else:
            return core.CharacterModifier()
        
    def _use(self, skill_modifier):
        self.passedTime = 0
        return super(InfinityWrapper, self)._use(skill_modifier)

# 이하 모든 코드 테스트 필요

def PirateFlagWrapper(vEhc, num1, num2, level):
    PirateFlag = core.BuffSkill("파이렛 플래그", 990, 30 * 1000, cooltime = (60 - vEhc.getV(num1, num2)) * 1000, armor_ignore = int(10 + 0.5*vEhc.getV(num1, num2)), stat_main = (level * 5 + 18)*0.01*int(10 + 0.5*vEhc.getV(num1, num2))).isV(vEhc,num1, num2).wrap(core.BuffSkillWrapper)
    return PirateFlag

# 작성중, 2초 후 폭발 가정
def BlitzShieldWrappers(vEhc, num1, num2):
    # 딜레이 추가 필요
    BlitzShieldDummy = core.BuffSkill("블리츠 실드 (더미)", 600, 2000, cooltime = 15000).wrap(core.BuffSkillWrapper)
    BlitzShield = core.DamageSkill("블리츠 실드", 2000, vEhc.getV(num1, num2)*20+500, 5).wrap(core.DamageSkillWrapper)
    BlitzShieldDummy.onAfter(BlitzShield)
    return BlitzShieldDummy, BlitzShield

# 아직 사용하지 말것! 연계 설정 추가 필요
def EvolveWrapper(vEhc, num1, num2):
    Evolve = core.SummonSkill("이볼브", 600, 3330, 450+vEhc.getV(num1, num2)*15, 7, 40*1000, cooltime = (121-int(0.5*vEhc.getV(num1, num2)))*1000).isV(vEhc,num1, num2).wrap(core.SummonSkillWrapper)
    return Evolve
