import argparse
from dpmModule.statistics.preset import get_preset

from dpmModule.jobs import jobMap, weaponList
from dpmModule.character.characterKernel import ItemedCharacter, JobGenerator
from dpmModule.character.characterTemplate import get_template_generator
from dpmModule.execution import rules
from dpmModule.kernel import core, policy
from dpmModule.status.ability import Ability_grade
from importlib import import_module

try:
    import pandas as pd
except ImportError:
    print("pandas 모듈을 설치해야 합니다.")
    exit()


def get_args():
    parser = argparse.ArgumentParser("DPM Test argument")
    parser.add_argument(
        "--id", type=str, help="Target preset id to calculate statistics"
    )
    parser.add_argument("--engine", type=str)
    parser.add_argument(
        "--calc", action="store_true", help="Calculate dpm and save data"
    )
    parser.add_argument("--ulevel", type=int, default=8000)
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--cdr", type=int, default=0)

    return parser.parse_args()


def load_engine(args, df: pd.DataFrame):
    engine = import_module(f"dpmModule.statistics.{args.engine}")
    engine.run(args, df)


def save_data(args):
    preset = get_preset(args.id)
    template = get_template_generator("high_standard")().get_template(args.ulevel)
    target: ItemedCharacter = template(weaponList[preset.job], args.cdr)
    gen: JobGenerator = jobMap[preset.job].JobGenerator()
    v_builder = core.AlwaysMaximumVBuilder()
    graph = gen.package(
        target,
        v_builder,
        options=preset.options,
        ulevel=args.ulevel,
        weaponstat=[4, 9],
        ability_grade=Ability_grade(4, 1),
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
    print(preset.job, dpm)

    log = analytics.get_log()
    df = pd.DataFrame.from_records(log)
    df["name"] = df["name"].astype("category")
    df["spec"] = df["spec"].astype("category")
    df.to_pickle(f"./data/{args.id}.pkl")
    return df


def test(args):
    if args.calc:
        df = save_data(args)
    else:
        df = pd.read_pickle(f"./data/{args.id}.pkl")

    load_engine(args, df)


if __name__ == "__main__":
    test(get_args())
