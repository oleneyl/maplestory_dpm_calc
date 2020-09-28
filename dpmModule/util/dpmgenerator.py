import os, sys
import json
import threading

from ..kernel import core

from ..character.characterTemplate import get_template_generator
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

    def get_dpm(self, ulevel = 6000, level=None, weaponstat = [4,9], printFlag = False, statistics = False, restricted = True, default_modifier=core.CharacterModifier()):
        #TODO target을 동적으로 생성할 수 있도록.
        target = self.template(maplejobs.weaponList[self.job])
        if level is not None:
            target.unsafe_change_level(level)
        gen = (self.supplier).JobGenerator()
        v_builder = core.AlwaysMaximumVBuilder()
        graph = gen.package(target, v_builder, ulevel = ulevel, weaponstat = weaponstat, vEnhanceGenerateFlag = "njb_style")
        sche = policy.AdvancedGraphScheduler(graph,
            policy.TypebaseFetchingPolicy(priority_list = [
                core.BuffSkillWrapper,
                core.SummonSkillWrapper,
                core.DamageSkillWrapper
            ]), 
            [rules.UniquenessRule()] + gen.get_predefined_rules(rules.RuleSet.BASE)) #가져온 그래프를 토대로 스케줄러를 생성합니다.
        analytics = core.Analytics(printFlag=printFlag)  #데이터를 분석할 분석기를 생성합니다.
        if printFlag:
            print(target.get_modifier())
        control = core.Simulator(sche, target, analytics) #시뮬레이터에 스케줄러, 캐릭터, 애널리틱을 연결하고 생성합니다.
        control.set_default_modifier(default_modifier)
        control.start_simulation(self.runtime)
        if statistics:
            control.analytics.statistics()
        return control.getDPM(restricted=restricted)

    def get_detailed_dpm(self, ulevel = 6000, weaponstat = [4,9]):
        #TODO target을 동적으로 생성할 수 있도록.
        
        target = self.template(maplejobs.weaponList[self.job])
        gen = (self.supplier).JobGenerator()
        
        #코어강화량 설정
        v_builder = core.AlwaysMaximumVBuilder()
        graph = gen.package(target, v_builder, ulevel = ulevel, weaponstat = weaponstat, vEnhanceGenerateFlag = "njb_style")
        sche = policy.AdvancedGraphScheduler(graph,
            policy.TypebaseFetchingPolicy(priority_list = [
                core.BuffSkillWrapper,
                core.SummonSkillWrapper,
                core.DamageSkillWrapper
            ]), 
            [rules.UniquenessRule()] + gen.get_predefined_rules(rules.RuleSet.BASE)) #가져온 그래프를 토대로 스케줄러를 생성합니다.
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
    def __init__(self, template, v_builder = core.AlwaysMaximumVBuilder(), ulevel = 0, weaponstat = [3,0]):
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


    def process(self, restricted=True, default_modifier=core.CharacterModifier()):
        print("ulevel : " + str(self.ulevel))
        jobli = maplejobs.jobListOrder
        retli = []
        retDict = []
    
        for _job, idx in zip(jobli, range(len(jobli))):
            job = maplejobs.jobList[_job]
            generator = IndividualDPMGenerator(job, self.template)
            dpm = generator.get_dpm(ulevel = self.ulevel, weaponstat = self.weaponstat, restricted=restricted, default_modifier=default_modifier)
            retli.append(dpm)
            value = {"name" : job, "dpm" : dpm}
            #print(value)
            retDict.append(value)
            print("%s done ... %d / %d ... %d" % (job, idx+1, len(jobli), value["dpm"]))
            
        sorteddata = sorted(retDict, key=lambda d: d["dpm"])
        data =  {"header" : jobli, "dpm" : retli, "dpmdict" : sorteddata, "about" : self.template("스태프").about + "\n"+ "\n".join(self.getSettingInfo())}
        return data

    def processJob(self, koJob, runtime = 180000):
        generator = IndividualDPMGenerator(koJob, self.template)
        generator.set_runtime(runtime)
        return generator.get_detailed_dpm(ulevel = self.ulevel, weaponstat = self.weaponstat)


class DpmInterface():
    def __init__(self, template_generator_name):
        self.generator_name = template_generator_name

    def get_template_generator(self):
        return get_template_generator(self.generator_name)

    def calculate_every(self):
        settings = []
        for ulevel, template, weapon_stat in self.get_template_generator()():
            settings.append(DpmSetting(template, ulevel=ulevel, weaponstat=weapon_stat))
        
        retval = [{"data" : setting.process() , "prefix" : "u" + str(setting.ulevel)} for setting in settings]
        return retval

    def calculate(self, ulevel, restricted=True, default_modifier=core.CharacterModifier()):
        template_generator = self.get_template_generator()()
        template, weaponstat = template_generator.query(ulevel)
        setting = DpmSetting(template, ulevel=ulevel, weaponstat=weaponstat)
        return {"data" : setting.process(restricted=restricted, default_modifier=default_modifier) , "prefix" : "u" + str(setting.ulevel)}

    def calculate_job(self, koJob, ulevel, runtime = 180*1000):
        template_generator = self.get_template_generator()()
        try:
            template, weaponstat = template_generator.query(ulevel)
        except KeyError as e:
            raise e
        except Exception as e:
            print('Unknown error occured')
            raise e
        setting = DpmSetting(template, ulevel=ulevel, weaponstat=weaponstat)
        
        return setting.processJob(koJob, runtime = runtime)