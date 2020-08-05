import sys
import dpmModule
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
import dpmModule.character.characterTemplateHigh as template
import dpmModule.jobs as maplejobs
import time

'''
full_test.py
전체 테스트를 위한 스크립트입니다.

등록된 모든 직업의 모든 스펙 기준 DPM 수치를 계산하여 파일로 출력합니다.
'''

charTemplate = {4000: template.getU4000CharacterTemplate, 5000: template.getU5000CharacterTemplate, 6000: template.getU6000CharacterTemplate, 7000: template.getU7000CharacterTemplate, 8000: template.getU8000CharacterTemplate, 8500: template.getU8500CharacterTemplate}

dpm_output = open('dpm_output.txt','w', encoding= 'utf-8')

index = 1

start = time.time()

print("maplestory_dpm_calc Full Test")
print("등록된 모든 직업의 모든 스펙 기준 DPM 수치를 계산하여 파일로 출력합니다. \n")
for value in maplejobs.jobList.values():
    union_level_list = [4000, 5000, 6000, 7000, 8000, 8500]
    #union_level_list = [6000]
    dpm_output.write(value + '\t')
    print(value + " 계산 중 (" + str(index) + '/' + str(len(maplejobs.jobList)) + ')')
    index += 1
    for union_level in union_level_list:
        sstart = time.time()
        gen = IndividualDPMGenerator(value, charTemplate[union_level])
        dpm_output.write(str(gen.get_dpm(ulevel = union_level)) + '\t')
        print(str(union_level) + "레벨급 스펙 계산완료 (소요시간: " + str(round(time.time() - sstart, 3)) + "초)")
    print()
    dpm_output.write('\n')

print(str(len(maplejobs.jobList)) + "개의 직업 계산 완료\n" + "출력: dpm_output.txt")
print("총 소요시간: " + str(round(time.time() - start, 3)) + "초")