import sys
import dpmModule
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
import dpmModule.character.characterTemplateHigh as template
import dpmModule.jobs as maplejobs

'''
full_test.py
전체 테스트를 위한 스크립트입니다.

등록된 모든 직업의 표준 DPM 수치를 계산하여 파일로 출력합니다.
'''

sys.stdout = open('output.txt','w')

for value in maplejobs.jobList.values():
    gen = IndividualDPMGenerator(value, template.getU6000CharacterTemplate)
    print(value, gen.get_dpm(ulevel = 6000))