from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...character import characterKernel as ck
# 모험가 공용 5차스킬 통합코드

#TODO: 얼닼사, 블리츠실드, 이볼브, 파이렛 플래그
'''
class MapleHero2:
    #vEhc.getV(var1,var2)
    def __init__(self, vEhc):
        return
    def mapleHero2(var1, var2):
        return core.BuffSkill("메이플월드 여신의 축복")
'''
# 모험가 법사
# 3% 증가로 알고있는데... 확인필요
# TODO : 재사용 대기시간 초기화 미적용으로 변경
class InfinityWrapper(core.BuffSkillWrapper):
    def __init__(self, serverlag = 3):
        skill = core.BuffSkill("인피니티", 960, 40000, cooltime = 180 * 1000, rem = True, red = True)
        super(InfinityWrapper, self).__init__(skill)
        self.passedTime = 0
        self.serverlag = serverlag
        
    def spend_time(self, time):
        if self.onoff:
            self.passedTime += time
        super(InfinityWrapper, self).spend_time(time)
            
    def get_modifier(self):
        if self.onoff:
            return core.CharacterModifier(pdamage_indep = (70 + 4 * (self.passedTime // ((4+self.serverlag)*1000))) )
        else:
            return core.CharacterModifier()
        
    def _use(self, rem = 0, red = 0):
        self.passedTime = 0
        return super(InfinityWrapper, self)._use(rem = rem, red = red)

# 이하 모든 코드 테스트 필요
def MapleHeroes2Wrapper(vEhc, num1, num2, level):
    MapleHeroes2 = core.BuffSkill("메이플월드 여신의 축복", 450, 60*1000, stat_main = 0.01 * (100 + 10 * vEhc.getV(num1, num2)) * (25 + level * 5), pdamage = 5 + vEhc.getV(num1, num2) // 2, cooltime = 180*1000).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    return MapleHeroes2

def PirateFlagWrapper(vEhc, num1, num2, level):
    PirateFlag = core.BuffSkill("파이렛 플래그", 990, 30 * 1000, cooltime = (60 - vEhc.getV(num1, num2)) * 1000, armor_ignore = int(10 + 0.5*vEhc.getV(num1, num2)), stat_main_fixed = (level * 5 + 18)*0.01*(10 + 0.5*vEhc.getV(num1, num2))).isV(vEhc,num1, num2).wrap(core.BuffSkillWrapper)
    return PirateFlag

# 작성중, 2초 후 폭발 가정
def BlitzShieldWrappers(vEhc, num1, num2):
    BlitzShieldDummy = core.BuffSkill("블리츠 실드 (더미)", 0, 2000, cooltime = -1).wrap(core.BuffSkillWrapper)
    BlitzShield = core.DamageSkill("블리츠 실드", 0, vEhc.getV(num1, num2)*20+500, 5, cooltime = 15000).isV(vEhc, num1, num2).wrap(core.DamageSkillWrapper)
'''
블리츠 실드
HP 5% 소비, 최대 HP의 20%의[23] 피해를 막아주는 보호막을 5초간 생성
보호막의 지속시간이 끝나거나 스킬을 다시 사용하면 보호막이 폭발하여 최대 12명의 적을 1000%의[(스킬 레벨*20+500)%의 데미지] 데미지로 5번 공격
보호막이 생성된 후 2초가 지나야 스킬을 다시 사용하여 수동 폭발 가능
재사용 대기시간 15초

이볼브
MP 800 소비, 40초 동안 강화되어 최대 10명의 적을 825%[(스킬 레벨*15+450)%의 데미지] 데미지로 7번 공격
재사용 대기시간 108초[(121-스킬 레벨*0.5)초. 소숫점은 버린다.]

얼티밋 다크 사이트
MP 850 소비, 30초 동안 다크 사이트 중 공격 및 스킬 사용 시 은신이 해제되지 않음
다크 사이트 중 공격 시 최종 데미지 15%[기본 10%에서 5레벨마다 1% 증가한다.] 증가, 어드밴스드 다크 사이트의 최종 데미지 증가와 합적용
재사용 대기시간 195초[(220-스킬 레벨)초]
'''