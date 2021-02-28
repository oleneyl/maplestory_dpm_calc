from typing import Any, Dict, List

from dpmModule.status.ability import Ability_grade
from dpmModule.character.characterKernel import GearedCharacter, JobGenerator

from ..kernel import core

from dpmModule.character.characterTemplate import TemplateGenerator

import dpmModule.jobs as maplejobs

from dpmModule.kernel import policy
from dpmModule.execution import rules


class IndividualDPMGenerator:
    """IndividualDPMGenerator는 단일 직업의 dpm을 연산합니다. 연산을 위해 인자로 job을 받습니다."""

    def __init__(self, job):
        self.job = job
        self.supplier = maplejobs.jobMap[job]
        self.runtime = 1800 * 1000

    def set_runtime(self, time):
        self.runtime = time

    def get_dpm(
        self,
        spec_name: str,
        ulevel: int,
        cdr: int = 0,
        options={},
        printFlag=False,
        statistics=False,
        restricted=True,
        default_modifier=core.CharacterModifier(),
    ) -> float:
        gen: JobGenerator = self.supplier.JobGenerator()
        target, weapon_stat = TemplateGenerator().get_template_and_weapon_stat(gen=gen, spec_name=spec_name, cdr=cdr)

        v_builder = core.AlwaysMaximumVBuilder()
        graph = gen.package(
            target,
            v_builder,
            options=options,
            ulevel=ulevel,
            weaponstat=weapon_stat,
            ability_grade=Ability_grade(4, 1),
            farm=False,
        )
        sche = policy.AdvancedGraphScheduler(
            graph,
            policy.TypebaseFetchingPolicy(
                priority_list=[
                    core.BuffSkillWrapper,
                    core.SummonSkillWrapper,
                    core.DamageSkillWrapper,
                ]
            ),
            [rules.UniquenessRule()] + gen.get_predefined_rules(rules.RuleSet.BASE),
        )  # 가져온 그래프를 토대로 스케줄러를 생성합니다.
        analytics = core.Analytics(printFlag=printFlag)  # 데이터를 분석할 분석기를 생성합니다.
        if printFlag:
            print(target.get_modifier())
        control = core.Simulator(
            sche, target, analytics
        )  # 시뮬레이터에 스케줄러, 캐릭터, 애널리틱을 연결하고 생성합니다.
        control.set_default_modifier(default_modifier)
        control.start_simulation(self.runtime)
        if statistics:
            control.analytics.statistics()
        return analytics.getDPM(restricted=restricted)

    def get_detailed_dpm(
            self,
            spec_name: str,
            ulevel: int,
            cdr: int = 0,
            options={}
    ) -> Dict[str, Any]:
        gen: JobGenerator = self.supplier.JobGenerator()
        target, weapon_stat = TemplateGenerator().get_template_and_weapon_stat(gen=gen, spec_name=spec_name, cdr=cdr)

        # 코어강화량 설정
        v_builder = core.AlwaysMaximumVBuilder()
        graph = gen.package(
            target,
            v_builder,
            options=options,
            ulevel=ulevel,
            weaponstat=weapon_stat,
            ability_grade=Ability_grade(4, 1),
            farm=False,
        )
        # 가져온 그래프를 토대로 스케줄러를 생성합니다.
        sche = policy.AdvancedGraphScheduler(
            graph,
            policy.TypebaseFetchingPolicy(
                priority_list=[
                    core.BuffSkillWrapper,
                    core.SummonSkillWrapper,
                    core.DamageSkillWrapper,
                ]
            ),
            [rules.UniquenessRule()] + gen.get_predefined_rules(rules.RuleSet.BASE),
        )
        # 데이터를 분석할 분석기를 생성합니다.
        analytics = core.Analytics()
        # 시뮬레이터에 스케줄러, 캐릭터, 애널리틱을 연결하고 생성합니다.
        control = core.Simulator(
            sche, target, analytics
        )
        control.start_simulation(self.runtime)

        return {
            "data": analytics.get_results(),
            "meta": analytics.get_metadata(target.get_buffed_modifier()),
            "skill": analytics.get_skill_info(),
            "graph": graph.get_network_information("merged"),
            "dpm": analytics.getDPM(),
            "detail": gen.generate.__doc__,
            "loss": analytics.get_unrestricted_DPM() - analytics.getDPM(),
        }


class DpmSetting:
    """DpmSetting은 모든 직업의 dpm 설정값을 연산합니다. IndividualDPMGenerator에 필요한 메타데이터를 저장합니다."""

    itemGrade = ["노말", "레어", "에픽", "유니크", "레전"]

    def __init__(
        self,
        # v_builder=core.AlwaysMaximumVBuilder(),
        ulevel: int =0,
    ):
        self.ulevel = ulevel
        self.detail = ""

    def getSettingInfo(self) -> List[str]:
        retli = []
        retli.append("유니온 %d" % self.ulevel)
        # retli.append("무기상태 %s %d줄" % (self.itemGrade[self.weaponstat[0]], (self.weaponstat[1] // 3)))
        retli.append(self.detail)
        return retli

    def process(
            self,
            restricted=True,
            default_modifier=core.CharacterModifier()
    ) -> Dict[str, Any]:
        print("ulevel : " + str(self.ulevel))
        jobli = maplejobs.jobListOrder
        retli = []
        retDict = []

        for _job, idx in zip(jobli, range(len(jobli))):
            job = maplejobs.jobList[_job]
            generator = IndividualDPMGenerator(job)
            dpm = generator.get_dpm(
                spec_name=str(self.ulevel),
                ulevel=self.ulevel,
                restricted=restricted,
                default_modifier=default_modifier,
            )
            retli.append(dpm)
            value = {"name": job, "dpm": dpm}
            # print(value)
            retDict.append(value)
            print(
                "%s done ... %d / %d ... %d" % (job, idx + 1, len(jobli), value["dpm"])
            )

        sorteddata = sorted(retDict, key=lambda d: d["dpm"])
        data = {
            "header": jobli,
            "dpm": retli,
            "dpmdict": sorteddata,
            # "about": self.template("스태프").about
            # + "\n"
            # + "\n".join(self.getSettingInfo()),
        }
        return data

    def processJob(
            self,
            koJob: str,
            runtime: int = 180 * 1000
    ) -> Dict[str, Any]:
        generator = IndividualDPMGenerator(koJob)
        generator.set_runtime(runtime)
        return generator.get_detailed_dpm(
            spec_name=str(self.ulevel),
            ulevel=self.ulevel
        )


class DpmInterface:
    def __init__(self):
        self.template_generator = TemplateGenerator()

    def calculate_every(self) -> List[Dict[str, Any]]:
        settings = []
        for spec_name in self.template_generator.get_spec_names():
            settings.append(DpmSetting(ulevel=int(spec_name)))

        retval = [
            {"data": setting.process(), "prefix": "u" + str(setting.ulevel)}
            for setting in settings
        ]
        return retval

    def calculate(
            self,
            ulevel: int,
            restricted=True,
            default_modifier=core.CharacterModifier()
    ) -> Dict[str, Any]:
        setting = DpmSetting(ulevel=ulevel)
        return {
            "data": setting.process(
                restricted=restricted, default_modifier=default_modifier
            ),
            "prefix": "u" + str(setting.ulevel),
        }

    def calculate_job(
            self,
            koJob: str,
            ulevel: int,
            runtime: int = 180 * 1000
    ) -> Dict[str, Any]:
        setting = DpmSetting(ulevel=ulevel)

        return setting.processJob(koJob, runtime=runtime)
