from ...kernel import core
from ...kernel.core import VSkillModifier as V
from ...kernel.core import CharacterModifier as MDF
from ...character import characterKernel as ck
from functools import partial

#레프
def FloraGoddessBlessWrapper(vEhc, num1, num2, WEAPON_ATT):
    # 장비 비례 증가 수치는 최대치로 가정
    FloraGoddessBless = core.BuffSkill("그란디스 여신의 축복(레프)", 450, 40*1000, att = 10 + 3 * vEhc.getV(num1, num2) + 1.5 * WEAPON_ATT, cooltime = 240*1000).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    return FloraGoddessBless

class MagicCircuitFullDriveBuilder():
    def __init__(self, vEhc, num1, num2, mana=100):
        # 마나 최대치 유지 가정, 비율에 따라 수치가 어떻게 변동되는지 확인 필요
        # 마력 폭풍 발생 시 데미지 증가량 갱신하지 않음
        self.MANA = mana
        self.MagicCircuitFullDriveBuff = core.BuffSkill("매직 서킷 풀드라이브 (버프)", 0, 30+vEhc.getV(num1, num2), cooltime = 200*1000, pdamage= (20+vEhc.getV(num1, num2)) * (self.MANA/100)).wrap(core.BuffSkillWrapper)
        self.ManaStorm = core.SummonSkill("매직 서킷 풀드라이브 (마나 폭풍)", 0, 4000, 500+20*vEhc.getV(num1, num2), 3, 30+vEhc.getV(num1, num2), cooltime = -1).wrap(core.SummonSkillWrapper)

    def get_skill(self):
        return self.MagicCircuitFullDriveBuff, self.ManaStorm

'''
매직 서킷 풀드라이브
최대 MP의 15% 소비, 55초[(스킬 레벨+30)초] 동안 현재 MP의 비율에 따라 데미지 최대 45%[(스킬 레벨+20)%]까지 증가, 마력 폭풍 발생 시 데미지 증가량 갱신
공격 스킬 사용 시 4초마다 MP를 150 추가 소모하고 최대 6명의 적을 1000%의[(스킬 레벨*20+500)%의 데미지] 데미지로 3번 공격하는 마력 폭풍 발생
재사용 대기시간 200초
'''