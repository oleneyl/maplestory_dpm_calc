import os, sys
import json
import threading

from dpmModule.kernel import core

import dpmModule.character.characterTemplate as CT
import dpmModule.character.characterTemplateHigh as CT_high
import dpmModule.character.characterKernel

import dpmModule.jobs as maplejobs

from dpmModule.kernel import policy
from dpmModule.execution import rules

class IndividualDPMGenerator():
    '''IndividualDPMGenerator는 단일 직업의 dpm을 연산합니다. 연산을 위해 인자로 job 과 template 를 받습니다.
    '''
    inputViewList = [[6,9,15,21],[6,9,15,21],[10,15,17,22]]
    
    def __init__(self, job, template):
        self.job = job
        self.template = template
        self.supplier = maplejobs.jobMap[job]
        self.runtime = 1800 * 1000
        
    def set_runtime(self, time):
        self.runtime = time

    def get_dpm(self, ulevel = 6000, weaponstat = [4,9], level = 230, printFlag = False):
        #TODO target을 동적으로 생성할 수 있도록.
        target = self.template(maplejobs.weaponList[self.job])
        target.level = level
        gen = (self.supplier).JobGenerator()

        v_builder = core.NjbStyleVBuilder(skill_core_level=25, each_enhanced_amount=17)
        graph = gen.package(target, v_builder, ulevel = ulevel, weaponstat = weaponstat, vEnhanceGenerateFlag = "njb_style")
        sche = policy.AdvancedGraphScheduler(graph,
            policy.TypebaseFetchingPolicy(priority_list = [
                core.BuffSkillWrapper,
                core.SummonSkillWrapper,
                core.DamageSkillWrapper
            ]), 
            [rules.UniquenessRule()]) #가져온 그래프를 토대로 스케줄러를 생성합니다.
        analytics = core.Analytics(printFlag=printFlag)  #데이터를 분석할 분석기를 생성합니다.
        control = core.Simulator(sche, target, analytics) #시뮬레이터에 스케줄러, 캐릭터, 애널리틱을 연결하고 생성합니다.
        control.start_simulation(self.runtime)

        return control.getDPM()

    def get_detailed_dpm(self, ulevel = 6000, weaponstat = [4,9], level = 230):
        #TODO target을 동적으로 생성할 수 있도록.
        
        target = self.template(maplejobs.weaponList[self.job])
        target.level = level
        gen = (self.supplier).JobGenerator()
        
        #코어강화량 설정
        v_builder = core.NjbStyleVBuilder(skill_core_level=25, each_enhanced_amount=17)
        graph = gen.package(target, v_builder, ulevel = ulevel, weaponstat = weaponstat, vEnhanceGenerateFlag = "njb_style")
        sche = policy.AdvancedGraphScheduler(graph,
            policy.TypebaseFetchingPolicy(priority_list = [
                core.BuffSkillWrapper,
                core.SummonSkillWrapper,
                core.DamageSkillWrapper
            ]), 
            [rules.UniquenessRule()]) #가져온 그래프를 토대로 스케줄러를 생성합니다.
        analytics = core.Analytics()  #데이터를 분석할 분석기를 생성합니다.
        control = core.Simulator(sche, target, analytics) #시뮬레이터에 스케줄러, 캐릭터, 애널리틱을 연결하고 생성합니다.
        control.start_simulation(self.runtime)

        return {"data" : control.get_results(), 
                "meta" : control.get_metadata(),
                "skill" : control.get_skill_info(), 
                "graph" : graph.get_network_information("merged"),
                "dpm" : control.getDPM(),
                "detail" : gen.generate.__doc__,
                "loss" : control.get_unrestricted_DPM() - control.getDPM()
        }



class DpmSetting():
    '''DpmSetting은 모든 직업의 dpm 설정값을 연산합니다. IndividualDPMGenerator에 필요한 메타데이터를 저장합니다.
    '''
    itemGrade = ["노말", "레어", "에픽", "유니크", "레전"]
    def __init__(self, template, v_builder = core.NjbStyleVBuilder(), ulevel = 0, weaponstat = [3,0], level = 200):
        self.level = level
        self.vEhc = vEhc
        self.ulevel = ulevel
        self.weaponstat = weaponstat
        self.template = template
        self.detail = ''
        
    def getSettingInfo(self):
        retli = []
        retli.append("유니온 %d" % self.ulevel)
        retli.append("무기상태 %s %d줄" % (self.itemGrade[self.weaponstat[0]], (self.weaponstat[1] // 3)))
        retli.append(self.detail)
        return retli


    def process(self):
        print("ulevel : " + str(self.ulevel))
        jobli = maplejobs.jobListOrder
        retli = []
        retDict = []
    
        for _job, idx in zip(jobli, range(len(jobli))):
            job = maplejobs.jobList[_job]
            parser = IndividualDPMGenerator(job, self.template)
            dpm = parser.getDpm(vEhc = self.vEhc.copy(), ulevel = self.ulevel, weaponstat = self.weaponstat, level = self.level)
            retli.append(dpm)
            value = {"name" : job, "dpm" : dpm}
            #print(value)
            retDict.append(value)
            print("%s done ... %d / %d ... %d" % (job, idx+1, len(jobli), value["dpm"]))
            
        sorteddata = sorted(retDict, key=lambda d: d["dpm"])
        data =  {"header" : jobli, "dpm" : retli, "dpmdict" : sorteddata, "about" : self.template("스태프").about + "\n"+ "\n".join(self.getSettingInfo())}
        return data

    def processJob(self, koJob, runtime = 180000):
        parser = IndividualDPMGenerator(koJob, self.template)
        parser.setRuntime(runtime)
        return parser.getDetailedDpm(vEhc = self.vEhc.copy(), ulevel = self.ulevel, weaponstat = self.weaponstat, level = self.level)


        

def CalculateEvery():
    U4000DpmSetting = DpmSetting(CT.getU4000CharacterTemplate, ulevel = 4000, weaponstat = [3,3], level = 210)
    U5000DpmSetting = DpmSetting(CT.getU5000CharacterTemplate, ulevel = 5000, weaponstat = [3,6], level = 220)
    U6000DpmSetting = DpmSetting(CT.getU6000CharacterTemplate, ulevel = 6000, weaponstat = [4,3], level = 225)
    U6500DpmSetting = DpmSetting(CT.getU6500CharacterTemplate, ulevel = 6500, weaponstat = [4,5], level = 230)
    U7000DpmSetting = DpmSetting(CT.getU7000CharacterTemplate, ulevel = 7000, weaponstat = [4,6], level = 235)
    U7500DpmSetting = DpmSetting(CT.getU7500CharacterTemplate, ulevel = 7500, weaponstat = [4,7], level = 240)
    U8000DpmSetting = DpmSetting(CT.getU8000CharacterTemplate, ulevel = 8000, weaponstat = [4,8], level = 245)
    U8200DpmSetting = DpmSetting(CT.getU8200CharacterTemplate, ulevel = 8200, weaponstat = [4,9], level = 250)
    U8500DpmSetting = DpmSetting(CT.getU8500CharacterTemplate, ulevel = 8500, weaponstat = [4,9], level = 255)
    
    settings = [U4000DpmSetting, 
                U5000DpmSetting, 
                U6000DpmSetting, 
                U6500DpmSetting, 
                U7000DpmSetting, 
                U7500DpmSetting, 
                U8000DpmSetting, 
                U8200DpmSetting, 
                U8500DpmSetting]
    
    retval = [{"data" : setting.process() , "prefix" : "u" + str(setting.ulevel)} for setting in settings]
    return retval

def CalculateEveryHigh():
    U4000DpmSetting = DpmSetting(CT_high.getU4000CharacterTemplate, ulevel = 4000, weaponstat = [2,6], level = 215)
    U5000DpmSetting = DpmSetting(CT_high.getU5000CharacterTemplate, ulevel = 5000, weaponstat = [3,6], level = 230)
    U6000DpmSetting = DpmSetting(CT_high.getU6000CharacterTemplate, ulevel = 6000, weaponstat = [4,9], level = 240)
    U7000DpmSetting = DpmSetting(CT_high.getU7000CharacterTemplate, ulevel = 7000, weaponstat = [4,9], level = 250)
    U8000DpmSetting = DpmSetting(CT_high.getU8000CharacterTemplate, ulevel = 8000, weaponstat = [4,9], level = 255)
    U8500DpmSetting = DpmSetting(CT_high.getU8500CharacterTemplate, ulevel = 8500, weaponstat = [4,9], level = 260)
    
    settings = [U4000DpmSetting, 
                U5000DpmSetting, 
                U6000DpmSetting, 
                U7000DpmSetting, 
                U8000DpmSetting, 
                U8500DpmSetting]
    
    retval = [{"data" : setting.process() , "prefix" : "u" + str(setting.ulevel)} for setting in settings]
    return retval

def CalculateAt(ulevel):
    settings = {
    4000 : DpmSetting(CT.getU4000CharacterTemplate, ulevel = 4000, weaponstat = [3,3], level = 210),
    5000 :  DpmSetting(CT.getU5000CharacterTemplate, ulevel = 5000, weaponstat = [3,6], level = 220),
    6000 :  DpmSetting(CT.getU6000CharacterTemplate, ulevel = 6000, weaponstat = [4,3], level = 225),
    6500 :  DpmSetting(CT.getU6500CharacterTemplate, ulevel = 6500, weaponstat = [4,5], level = 230),
    7000 :  DpmSetting(CT.getU7000CharacterTemplate, ulevel = 7000, weaponstat = [4,6], level = 235),
    7500 :  DpmSetting(CT.getU7500CharacterTemplate, ulevel = 7500, weaponstat = [4,7], level = 240),
    8000 :  DpmSetting(CT.getU8000CharacterTemplate, ulevel = 8000, weaponstat = [4,8], level = 245),
    8200 :  DpmSetting(CT.getU8200CharacterTemplate, ulevel = 8200, weaponstat = [4,9], level = 250),
    8500 :  DpmSetting(CT.getU8500CharacterTemplate, ulevel = 8500, weaponstat = [4,9], level = 255)}
    
    setting = settings[ulevel]
    return {"data" : setting.process() , "prefix" : "u" + str(setting.ulevel)}

def CalculateHighAt(ulevel):
    settings = {
    4000 : DpmSetting(CT_high.getU4000CharacterTemplate, ulevel = 4000, weaponstat = [2,6], level = 215),
    5000 :  DpmSetting(CT_high.getU5000CharacterTemplate, ulevel = 5000, weaponstat = [3,6], level = 230),
    6000 :  DpmSetting(CT_high.getU6000CharacterTemplate, ulevel = 6000, weaponstat = [4,9], level = 240),
    7000 :  DpmSetting(CT_high.getU7000CharacterTemplate, ulevel = 7000, weaponstat = [4,9], level = 250),
    8000 :  DpmSetting(CT_high.getU8000CharacterTemplate, ulevel = 8000, weaponstat = [4,9], level = 255),
    8500 :  DpmSetting(CT_high.getU8500CharacterTemplate, ulevel = 8500, weaponstat = [4,9], level = 260)}
    
    setting = settings[ulevel]
    return {"data" : setting.process() , "prefix" : "u" + str(setting.ulevel)}

def CalculateJobHigh(koJob, ulevel, runtime = 180*1000):
    if ulevel not in [4000, 5000, 6000, 7000, 8000, 8500]:
        raise TypeError("ULEVEL must be in available ulevel list")
    
    if ulevel == 4000:
        dpmSetting = DpmSetting(CT_high.getU4000CharacterTemplate, ulevel = 4000, weaponstat = [2,6], level = 215)
    elif ulevel == 5000:
        dpmSetting = DpmSetting(CT_high.getU5000CharacterTemplate, ulevel = 5000, weaponstat = [3,6], level = 230)
    elif ulevel == 6000:        
        dpmSetting = DpmSetting(CT_high.getU6000CharacterTemplate, ulevel = 6000, weaponstat = [4,9], level = 240)
    elif ulevel == 7000:                
        dpmSetting = DpmSetting(CT_high.getU7000CharacterTemplate, ulevel = 7000, weaponstat = [4,9], level = 250)
    elif ulevel == 8000:                
        dpmSetting = DpmSetting(CT_high.getU8000CharacterTemplate, ulevel = 8000, weaponstat = [4,9], level = 255)
    elif ulevel == 8500:        
        dpmSetting = DpmSetting(CT_high.getU8500CharacterTemplate, ulevel = 8500, weaponstat = [4,9], level = 260)
    else:
        raise TypeError("Undefined Action")
    
    return dpmSetting.processJob(koJob, runtime = runtime)    
    
def CalculateJob(koJob, ulevel, runtime = 180000):

    if ulevel not in [2000, 4000, 5000, 6000, 6500, 7000, 7500, 8000, 8200, 8500]:
        raise TypeError("ULEVEL must be in available ulevel list")
    
    if ulevel == 4000:
        dpmSetting = DpmSetting(CT.getU4000CharacterTemplate, ulevel = 4000, weaponstat = [3,3], level = 210)
    elif ulevel == 5000:
        dpmSetting = DpmSetting(CT.getU5000CharacterTemplate, ulevel = 5000, weaponstat = [3,6], level = 220)
    elif ulevel == 6000:        
        dpmSetting = DpmSetting(CT.getU6000CharacterTemplate, ulevel = 6000, weaponstat = [4,6], level = 225)
    elif ulevel == 6500:                
        dpmSetting = DpmSetting(CT.getU6500CharacterTemplate, ulevel = 6500, weaponstat = [4,6], level = 230)
    elif ulevel == 7000:                
        dpmSetting = DpmSetting(CT.getU7000CharacterTemplate, ulevel = 7000, weaponstat = [4,7], level = 235)
    elif ulevel == 7500:                
        dpmSetting = DpmSetting(CT.getU7500CharacterTemplate, ulevel = 7500, weaponstat = [4,7], level = 240)
    elif ulevel == 8000:                
        dpmSetting = DpmSetting(CT.getU8000CharacterTemplate, ulevel = 8000, weaponstat = [4,8], level = 245)
    elif ulevel == 8200:        
        dpmSetting = DpmSetting(CT.getU8200CharacterTemplate, ulevel = 8200, weaponstat = [4,9], level = 250)
    elif ulevel == 8500:        
        dpmSetting = DpmSetting(CT.getU8500CharacterTemplate, ulevel = 8500, weaponstat = [4,9], level = 255)
    else:
        raise TypeError("Undefined Action")
    
    return dpmSetting.processJob(koJob, runtime = runtime)