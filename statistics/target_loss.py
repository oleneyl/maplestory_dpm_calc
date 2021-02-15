import argparse
import yaml

import pandas as pd
from .loader import load_data
from .saver import save_data
from .preset import get_preset, get_preset_list


def get_args():
    parser = argparse.ArgumentParser("cpm argument")
    parser.add_argument(
        "--id", type=str, help="Target preset id to calculate statistics"
    )
    parser.add_argument("--ulevel", type=int, default=8000)
    parser.add_argument("--cdr", type=int, default=0)
    parser.add_argument("--task", default="dpm")
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--calc", action="store_true")
    parser.add_argument("--all", action="store_true")

    return parser.parse_args()


def target_loss(args, df: pd.DataFrame):
    df = df.loc[df["deal"] > 0]
    df = df.groupby("name")["deal"].sum().reset_index()
    df = df.loc[df["deal"] > 0]
    # for x in df["name"]:
    #     print(x)

    with open("./statistics/target_loss/common.yaml", encoding="utf-8") as f:
        conf: dict = yaml.safe_load(f)
    with open(f"./statistics/target_loss/{args.id}.yaml", encoding="utf-8") as f:
        conf.update(yaml.safe_load(f))

    def chtr_mob_boss(name):
        if conf[name]["type"] == "random":
            return min(conf[name]["target"] / 2, 1)
        if conf[name]["type"] == "nearest":
            return min(conf[name]["target"] - 1, 1)
        if conf[name]["type"] == "homing":
            return 1

    def chtr_boss_mob(name):
        if conf[name]["type"] == "random":
            return min(conf[name]["target"] / 2, 1)
        if conf[name]["type"] == "nearest":
            return 1
        if conf[name]["type"] == "homing":
            return 1

    df["chtr_mob_boss"] = df.apply(lambda x: chtr_mob_boss(x["name"]) * x["deal"], axis=1)
    df["chtr_boss_mob"] = df.apply(lambda x: chtr_boss_mob(x["name"]) * x["deal"], axis=1)
    # print(df)

    preset = get_preset(args.id)
    dpm = df["deal"].sum() / 30
    chtr_mob_boss_dpm = df["chtr_mob_boss"].sum() / 30
    chtr_boss_mob_dpm = df["chtr_boss_mob"].sum() / 30
    print(f"{preset.job} {dpm:,.0f} {chtr_mob_boss_dpm:,.0f} {chtr_boss_mob_dpm:,.0f}")


if __name__ == "__main__":
    print("job | dpm | chtr_mob_boss | chtr_boss_mob")
    args = get_args()
    if args.all:
        presets = get_preset_list()
        tasks = [
            argparse.Namespace(
                id=id, ulevel=args.ulevel, cdr=args.cdr, time=args.time, task=args.task
            )
            for id, *_ in presets
        ]
        for task in tasks:
            data = load_data(task)
            target_loss(task, data)
    else:
        if args.calc:
            data = save_data(args)
            target_loss(args, data)
        else:
            data = load_data(args)
            target_loss(args, data)
