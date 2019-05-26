import sys
from os.path import dirname, abspath

sys.path.append(dirname(dirname(abspath(__file__))))

from maplestory_dpm_calculator.jobs import blaster as targetjob
from maplestory_dpm_calculator.kernel import core as jt
import maplestory_dpm_calculator.character.characterTemplateHigh as CT

target = CT.getU6000CharacterTemplate("너클")
gen = targetjob.JobGenerator()
vEhc = jt.vEnhancer()
vEhc.set_state_direct([60,60,60,60,60,60,60,60,60,60,60,60])
vEhc.set_vlevel_direct([30,30,30,30,30,30,30,30,30,30,30,30])

graph = gen.package(target, vlevel = 25, vEhc = vEhc, ulevel = 6000, weaponstat = [4,9])
print(target.get_modifier())

sche = jt.Scheduler(graph) #가져온 그래프를 토대로 스케줄러를 생성합니다.
analytics = jt.Analytics(printFlag = True)  #데이터를 분석할 분석기를 생성합니다.
control = jt.Simulator(sche, target, analytics) #시뮬레이터에 스케줄러, 캐릭터, 애널리틱을 연결하고 생성합니다.

#시뮬레이션 테스트 코드
control.start_simulation(300*1000)
analytics.printFlag = True
analytics.statistics()
'''
#그래프 생성기 테스트 코드
netli = [graph.getNetworkInformation("merged")]

for nd, li in netli:
    print("--------------------")
    for i in nd:
        print(i)
    print("=======")
    for i in li:
        print(i)
'''