from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial
from math import ceil

# 마스테마 클로우를 쿨타임마다 시전한다고 가정
def CallMastemaWrapper(vEhc, num1, num2):
    CallMastema = core.BuffSkill("콜 마스테마(버프)", 690, (30 + vEhc.getV(num1, num2))*1000, cooltime = 150*1000, red=True).wrap(core.BuffSkillWrapper)
    MastemaClaw_Attack = core.DamageSkill("마스테마 클로우", 0, 500 + 20 *vEhc.getV(num1, num2), 8, cooltime=4000).wrap(core.DamageSkillWrapper)
    MastemaClaw = core.OptionalElement(CallMastema.is_active(), MastemaClaw_Attack)
    return CallMastema, MastemaClaw

def AnotherWorldWrapper(vEhc, num1, num2):
    # 축복 발동시간 4초, 처음으로 이계의 공허가 발동되며 4개의 축복이 돌아가면서 발동
    void_delay = 4000
    void_chance = 0.25
    AnotherGoddessBuff = core.BuffSkill("이계 여신의 축복", 480, 40000, cooltime = 120000, red=True, final_damage=5+ceil(vEhc.getV(num1, num2)/5)).wrap(core.BuffSkillWrapper)
    AnotherVoid = core.SummonSkill("이계의 공허", 0, void_delay / void_chance, 1200+48*vEhc.getV(num1, num2), 12, 40000, cooltime = -1).wrap(core.SummonSkillWrapper)
    AnotherGoddessBuff.onAfter(AnotherVoid)
    return AnotherGoddessBuff, AnotherVoid

'''
최대 HP의 5% 소비, 40초 동안 최종 데미지 [1레벨에서 6%, 6, 11, 16, 21, 26레벨에서 1%씩 증가] 증가, 일정 시간마다 각종 축복 및 공격을 시전, 축복 시전 시 이전 축복이 남아있다면 소멸
회복의 축복: DF/PP/HP 중 자신이 사용하는 쪽을 최대치의 27%[(15 + 스킬레벨/2)%, 소수점은 버린다.] 회복, 특정한 회복 불가 상황에도 회복 가능
방패의 축복: 1회에 한해 최대 HP의 일정 비율로 피해를 입히는 공격을 포함한 피격 데미지 70%[(45 + 스킬레벨)%] 감소
보호의 축복: 1회에 한해 치명적인 상태이상 방어
이계의 공허: 최대 12명의 적을 2400%[(1200 + 48*스킬레벨)%의 데미지]의 데미지로 12번 공격
재사용 대기시간 120초
'''
