from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, List, Union

from .modifier import CharacterModifier

if TYPE_CHECKING:
    from dpmModule.character.characterKernel import AbstractCharacter

    from ..policy import AdvancedGraphScheduler
    from .graph_element import Task
    from .result_object import ResultObject


class Simulator(object):
    __slots__ = 'scheduler', 'character', 'analytics', '_modifier_cache_and_time', '_default_modifier'

    def __init__(self, scheduler: AdvancedGraphScheduler, chtr: AbstractCharacter, analytics: Analytics):
        self.scheduler: AdvancedGraphScheduler = scheduler
        self.character: AbstractCharacter = chtr
        self.analytics: Analytics = analytics

        # TODO: Not used attribute.
        # Buff modifier를 시간별로 캐싱하여 연산량을 줄입니다.
        self._modifier_cache_and_time: List[Union[int,
                                                  CharacterModifier]] = [-1, CharacterModifier()]

        self._default_modifier: CharacterModifier = CharacterModifier()

    def set_default_modifier(self, modifier: CharacterModifier) -> None:
        self._default_modifier = modifier

    def get_default_modifier(self) -> CharacterModifier:
        return self._default_modifier

    def get_skill_info(self) -> Dict[str, Any]:
        return self.analytics.get_skill_info()

    def get_results(self) -> List[Dict[str, Any]]:
        return self.analytics.get_results()

    def get_metadata(self) -> Dict[str, float]:
        mod = self.character.get_buffed_modifier()
        return self.analytics.get_metadata(mod)

    def getDPM(self, restricted: bool = True) -> float:
        if not restricted:
            return self.get_unrestricted_DPM()
        else:
            return self.analytics.total_damage / self.scheduler.total_time_initial * 60000

    def get_unrestricted_DPM(self) -> float:
        return self.analytics.total_damage_without_restriction / self.scheduler.total_time_initial * 60000

    # TODO: Not used method.
    def getTotalDamage(self) -> float:
        return self.analytics.total_damage

    def start_simulation(self, time: float) -> None:
        self._modifier_cache_and_time = [-1, CharacterModifier()]
        self.scheduler.initialize(time)
        self.analytics.set_total_runtime(time)
        self.analytics.chtrmdf = self.character.get_modifier()
        # 캐릭터의 Modifier를 매번 재계산 할 필요가 없으므로 (캐릭터의 상태는 시뮬레이션 도중 변화하지 않음) 캐싱하여 연산 자원을 절약합니다.
        self.character.generate_modifier_cache()
        while not self.scheduler.is_simulation_end():
            task = self.scheduler.dequeue()
            try:
                self.run_task_recursive(task)
            except Exception as e:
                print(task._ref._id)
                print("error raised")
                print("---")
                raise e

    def parse_result(self, result: ResultObject) -> None:
        runtime_context_modifier = self.scheduler.get_buff_modifier() + \
            self.get_default_modifier()
        result.setTime(self.scheduler.get_current_time())

        if result.damage > 0:
            result.mdf += runtime_context_modifier

        self.analytics.analyze(self.character, result)

    def run_task_recursive(self, task: Task) -> None:
        for t in reversed(task._before):
            self.run_task_recursive(t)

        runtime_context_modifier = self.scheduler.get_buff_modifier() + \
            self.get_default_modifier()
        result = task.do(
            runtime_context_modifier=runtime_context_modifier + self.character.get_modifier())
        self.parse_result(result)

        for t in task._justAfter:
            self.run_task_recursive(t)

        if result.delay > 0:
            time_to_spend = result.delay
            while True:
                callback, time_to_spend = self.scheduler.apply_result(
                    result, time_to_spend)
                if self.scheduler.is_simulation_end():
                    return
                if callback:
                    result = callback.resolve()
                    self.parse_result(result)
                else:
                    break

            while True:
                tick = self.scheduler.get_delayed_task()
                if tick is not None:
                    self.run_task_recursive(tick)
                else:
                    break

        for t in reversed(result.cascade + task._after):
            self.run_task_recursive(t)


class Analytics:
    def __init__(self, printFlag: bool = False) -> None:
        self.totalTime: float = 0
        self.total_damage: float = 0
        self.total_damage_without_restriction: float = 0
        self.logList: List[Dict[str, Any]] = []
        self.meta_save = {}  # TODO: Not used attribute.
        self.print_calculation_progress: bool = printFlag
        self.skillList: Dict[str, Dict] = {}
        self.chtrmdf: CharacterModifier = CharacterModifier()

    def set_total_runtime(self, time: float) -> None:
        self.totalTime = time

    def analyze(self, chtr: AbstractCharacter, result: ResultObject) -> None:
        self.add_damage_from_result_with_log(chtr.get_modifier(), result)

    def get_skill_info(self) -> Dict[str, Any]:
        return {"dict": self.skillList, "li": list(self.skillList.keys())}

    def get_metadata(self, mod: CharacterModifier) -> Dict[str, float]:
        meta = {"stat_main": mod.stat_main,
                "stat_sub": mod.stat_sub,
                "stat_main_fixed": mod.stat_main_fixed,
                "pstat_main": mod.pstat_main,
                "att": mod.att,
                "patt": mod.patt,
                "pdamage": mod.pdamage + mod.boss_pdamage,
                "boss_pdamage": mod.boss_pdamage,
                "armor_ignore": mod.armor_ignore,
                "pdamage_indep": mod.pdamage_indep,
                "effective_status": mod.get_status_factor(),
                "crit_damage": mod.crit_damage,
                "crit": mod.crit
                }

        return meta

    def statistics(self) -> None:
        print("Total damage %.1f in %d second" %
              (self.total_damage, self.totalTime / 1000))
        print(
            f"Loss {self.total_damage_without_restriction - self.total_damage:.1f}")

        def getSkillNames(logList) -> List[str]:
            return sorted(set(map(lambda log: log["result"].sname, logList)))

        print("\n===Buff Skills===")
        buffList = list(
            filter(lambda log: log["result"].spec == "buff", self.logList))
        names = getSkillNames(buffList)
        for name in names:
            skillLog = list(
                filter(lambda log: log["result"].sname == name, buffList))
            use = len(skillLog)
            delay = sum(map(lambda log: log["result"].delay, skillLog))
            print(f"{name} Used {use} Delay {delay}")

        shareDict = defaultdict(int)

        print("\n===Damage Skills===")
        damageList = list(
            filter(lambda log: log["result"].spec == "damage", self.logList))
        names = getSkillNames(damageList)
        for name in names:
            skillLog = list(
                filter(lambda log: log["result"].sname == name, damageList))
            use = len(skillLog)
            hit = sum(map(lambda log: log["result"].hit, skillLog))
            damage = sum(map(lambda log: log["deal"], skillLog))
            loss = sum(map(lambda log: log["loss"], skillLog))
            delay = sum(map(lambda log: log["result"].delay, skillLog))
            share = damage / self.total_damage * 100
            shareDict[name.split('(')[0]] += share
            print(f"{name} Used {use} Delay {delay}")
            print(f"Hit {hit} Damage {damage:.1f} Loss {loss:.1f}")
            print(f"Share {share:.4f}%")

        print("\n===Summon/DoT Skills===")
        summonList = list(filter(lambda log: log["result"].spec in [
                          "summon", "dot"], self.logList))
        names = getSkillNames(summonList)
        for name in names:
            skillLog = list(
                filter(lambda log: log["result"].sname == name, summonList))
            summon = len(list(filter(lambda log: log["deal"] == 0, skillLog)))
            use = len(skillLog) - summon
            hit = sum(map(lambda log: log["result"].hit, skillLog))
            damage = sum(map(lambda log: log["deal"], skillLog))
            loss = sum(map(lambda log: log["loss"], skillLog))
            delay = sum(map(lambda log: log["result"].delay, skillLog))
            share = damage / self.total_damage * 100
            shareDict[name.split('(')[0]] += share
            print(f"{name} Summoned {summon} Delay {delay}")
            print(f"Used {use} Hit {hit}")
            print(f"Damage {damage:.1f} Loss {loss:.1f}")
            print(f"Share {share:.4f}%")

        print("\n===Skill Share===")
        for name, share in sorted(shareDict.items(), key=lambda x: x[1], reverse=True):
            if share > 0:
                print(f"{name}, {share:.4f}%")

        # self.log("Percent damage per second is %.2f" % (100*self.total_damage / self.character.get_modifier().get_damage_factor() / self.totalTimeInitial * 1000))

    def skill_share(self) -> Dict[str, int]:
        damageDict = {}
        for log in self.logList:
            if log["deal"] > 0:
                if log["result"].sname not in damageDict:
                    damageDict[log["result"].sname] = 0
                damageDict[log["result"].sname] += log["deal"]

        return damageDict

    def get_results(self) -> List[Dict[str, Any]]:
        retli = []
        for log in self.logList:
            retli.append({"time": log["time"],
                          "sname": log["result"].sname,
                          "deal": log["deal"],
                          "spec": log["result"].spec,
                          "else": log["result"].kwargs})
        return retli

    def add_damage_from_result_with_log(self, charmdf: CharacterModifier, result: ResultObject) -> None:
        if result.damage > 0:
            mdf = charmdf + result.mdf

            deal, loss = mdf.calculate_damage(
                result.damage, result.hit, result.spec)
            free_deal = deal + loss

            # free_deal = mdf.get_damage_factor() * result.damage * 0.01
            # deal = min(result.hit * MAX_DAMAGE_RESTRICTION, free_deal)
        else:
            deal = 0
            free_deal = 0

        if deal > 0:
            self.total_damage += deal
            self.total_damage_without_restriction += free_deal

        # For speed acceleration
        if self.print_calculation_progress:
            print('At Time %.1f, Skill [%s] ... Damage [%.1f] ... Loss [%.1f] ... Delay [%.1f] ... Spec [%s]' % (
                result.time, result.sname, deal, free_deal - deal, result.delay, result.spec))
            print(f'{result.mdf}')
        if deal > 0:
            self.logList.append(
                {"result": result, "time": result.time, "deal": deal, "loss": free_deal - deal})
        else:
            self.logList.append(
                {"result": result, "time": result.time, "deal": 0, "loss": 0})
        if result.sname not in self.skillList:
            self.skillList[result.sname] = {}

    def deduce_increment_of_temporal_modifier(self, continue_time_length: int, temporal_modifier: CharacterModifier,
                                              search_time_scan_rate: int = 1000) -> Dict[str, float]:
        def search_time_index(time: float, hoping_rate_init: int = 100) -> int:
            hoping_rate = hoping_rate_init
            time_index = 0
            while True:
                if time_index >= len(self.logList):
                    time_index = len(self.logList) - 1
                    break
                if self.logList[time_index]["time"] < time:
                    time_index += hoping_rate
                else:
                    if self.logList[time_index - 1]["time"] <= time:
                        break
                    else:
                        hoping_rate = max(1, hoping_rate // 2)
                        time_index -= hoping_rate
                        time_index = max(0, time_index)
                        if time_index == 0:
                            return 0

            return time_index

        def get_damage_sum_in_time_interval(time_start: float, time_length: float) -> float:
            damage_sum = 0
            time_log_index = max(0, search_time_index(time_start))
            # print("start_time_index", time_log_index, time_start)

            while time_start <= self.logList[time_log_index]["time"] <= time_start + time_length:
                damage_sum += self.logList[time_log_index]["deal"]
                time_log_index += 1
                if time_log_index >= len(self.logList):
                    break

            for t in range(time_log_index, time_log_index + 20):
                if t < len(self.logList):
                    if time_start + time_length >= self.logList[t]["time"] >= time_start:
                        damage_sum += self.logList[time_log_index]["deal"]

            # print("end_time_index", time_log_index)

            # print("log",time_start, time_length, damage_sum)
            return damage_sum

        # search_time_scan_rate : 기록되어 있는 로그를 스캔할 시간주기입니다. 기본값 : 1000(ms)

        # scanning algorithm
        maximal_time_loc = 0
        damage_log_queue = [get_damage_sum_in_time_interval(
            i * search_time_scan_rate, search_time_scan_rate) for i in range(continue_time_length // search_time_scan_rate)]
        maximal_damage = sum(damage_log_queue)

        scanning_end_time = (continue_time_length //
                             search_time_scan_rate) * search_time_scan_rate

        while scanning_end_time < self.totalTime:
            damage_log_queue.pop(0)
            damage_log_queue.append(get_damage_sum_in_time_interval(
                scanning_end_time, search_time_scan_rate))
            if sum(damage_log_queue) > maximal_damage:
                maximal_time_loc = scanning_end_time - continue_time_length
                maximal_damage = sum(damage_log_queue)
            scanning_end_time += search_time_scan_rate

        # Now we know when damage is maximized. We now apply our modifier into this.

        total_damage = 0
        for log in self.logList:
            result = log["result"]
            if result.damage > 0:
                mdf = self.chtrmdf + result.mdf
                if maximal_time_loc <= log["time"] < maximal_time_loc + continue_time_length:
                    mdf += temporal_modifier
                deal, loss = mdf.calculate_damage(
                    result.damage, result.hit, result.spec)
                total_damage += deal

        simple_increment = ((self.chtrmdf + temporal_modifier).get_damage_factor() / (
            self.chtrmdf.get_damage_factor()) - 1) * (continue_time_length / self.totalTime)

        return {"damage": (total_damage - self.total_damage) * (60000 / self.totalTime),
                "increment": (total_damage / self.total_damage) - 1, "simple_increment": simple_increment}
