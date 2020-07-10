import sys
import dpmModule
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
import dpmModule.character.characterTemplateHigh as template
import dpmModule.jobs as maplejobs

'''
full_test.py
전체 테스트를 위한 스크립트입니다.

등록된 모든 직업의 모든 스펙 기준 DPM 수치를 계산하여 파일로 출력합니다.
'''

charTemplate = {4000: template.getU4000CharacterTemplate, 5000: template.getU5000CharacterTemplate, 6000: template.getU6000CharacterTemplate, 7000: template.getU7000CharacterTemplate, 8000: template.getU8000CharacterTemplate, 8500: template.getU8500CharacterTemplate}

sys.stdout = open('output.txt','w', encoding= 'utf-8')

for value in maplejobs.jobList.values():
    union_level_list = [4000, 5000, 6000, 7000, 8000, 8500]
    print(value, end = '\t')
    for union_level in union_level_list:
        gen = IndividualDPMGenerator(value, charTemplate[union_level])
        print(gen.get_dpm(ulevel = union_level), end = '\t')
    print("")