import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from dpmModule.character.characterKernel import JobGenerator
from dpmModule.character.characterTemplate import TemplateGenerator
from dpmModule.execution import rules
from dpmModule.jobs import jobMap
from dpmModule.kernel import core, policy
from dpmModule.status.ability import Ability_grade

from .preset import get_preset, get_preset_list

try:
    import pandas as pd
except ImportError:
    print("pandas 모듈을 설치해야 합니다.")
    exit()


def get_args():
    parser = argparse.ArgumentParser("Statistics saver argument")
    parser.add_argument(
        "--id", type=str, help="Target preset id to calculate statistics"
    )
    parser.add_argument("--ulevel", type=int, default=8000)
    parser.add_argument("--cdr", type=int, default=0)
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--task", default="dpm")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--thread", type=int, default=4)

    return parser.parse_args()


def dpm(args):
    preset = get_preset(args.id)
    gen: JobGenerator = jobMap[preset.job].JobGenerator()
    target, weapon_stat = TemplateGenerator().get_template_and_weapon_stat(gen, str(args.ulevel), args.cdr)
    v_builder = core.AlwaysMaximumVBuilder()
    graph = gen.package(
        target,
        v_builder,
        options=preset.options,
        ulevel=args.ulevel,
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
    )
    analytics = core.StatAnalytics()
    control = core.Simulator(sche, target, analytics)
    control.start_simulation(args.time * 1000)
    dpm = analytics.get_dpm()
    print(preset.job, f"{dpm:,.3f}")

    return analytics.get_log()


def burst10(args):
    preset = get_preset(args.id)
    gen: JobGenerator = jobMap[preset.job].JobGenerator()
    target, weapon_stat = TemplateGenerator().get_template_and_weapon_stat(gen, str(args.ulevel), args.cdr)
    v_builder = core.AlwaysMaximumVBuilder()
    graph = gen.package(
        target,
        v_builder,
        options=preset.options,
        ulevel=args.ulevel,
        weaponstat=weapon_stat,
        ability_grade=Ability_grade(4, 1),
        farm=False,
    )
    sche = policy.AdvancedGraphScheduler(
        graph,
        policy.ListedFetchingPolicy(skill_ids=gen.get_skill_rotation_10sec(graph)),
        [rules.UniquenessRule()],
    )
    analytics = core.StatAnalytics()
    control = core.Simulator(sche, target, analytics)
    control.start_simulation(args.time * 1000)
    start, end, dpm, loss = analytics.get_peak(10000)
    print(preset.job, f"{dpm:,.3f}")

    return analytics.get_log()


def save_data(args):
    if args.task == "dpm":
        log = dpm(args)
    elif args.task == "burst10":
        log = burst10(args)
    else:
        raise ValueError(args.task)

    df = pd.DataFrame.from_records(log)
    df["name"] = df["name"].astype("category")
    df["spec"] = df["spec"].astype("category")

    Path("./data").mkdir(parents=True, exist_ok=True)
    df.to_pickle(f"data/{args.task}_{args.id}_{args.ulevel}_{args.cdr}.pkl")

    return df


def save_all(args):
    presets = get_preset_list()
    tasks = [
        argparse.Namespace(
            id=id, ulevel=args.ulevel, cdr=args.cdr, time=args.time, task=args.task
        )
        for id, *_ in presets
    ]
    pool = ProcessPoolExecutor(max_workers=args.thread)
    res = pool.map(save_data, tasks)
    return list(res)


if __name__ == "__main__":
    args = get_args()
    if args.all is True:
        save_all(args)
    else:
        save_data(args)
