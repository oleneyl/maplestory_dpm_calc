import argparse
import yaml
import os.path
from collections import defaultdict

import pandas as pd
from .loader import load_data
from .saver import save_data
from .preset import get_preset, get_preset_list

TEST_TIME = 30  # 30 min = 1800 sec


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


def get_counts(conf):
    count_dict = defaultdict(int)
    for group in conf:
        if group == "else":
            continue
        for item in conf[group]:
            if type(item) == str:
                count_dict[item] = 1
            else:
                count_dict[item[0]] = item[1]
    return count_dict


def skill_names(li):
    return [x if type(x) == str else x[0] for x in li]


def cpm(args, df: pd.DataFrame):
    # for x in df.sort_values(by="spec")["name"].unique():
    #     print("- " + x)
    df_all = df[["name", "spec"]]
    df_without_tick = df[~df["spec"].str.endswith(":tick")]

    fname = f"./statistics/cpm/{args.id}.yaml"
    if not os.path.isfile(fname):
        return

    with open(fname, encoding="utf-8") as f:
        conf = yaml.safe_load(f)
        counts = get_counts(conf)
        every = skill_names(conf.get("every", []))
        summon = skill_names(conf.get("summon", []))
        independant = skill_names(conf.get("independant", []))
        pressing = skill_names(conf.get("pressing", []))

    click_dict = defaultdict(int)
    for sk in every:
        click_dict[sk] = len(df_all[df_all["name"] == sk]) * counts[sk]

    for sk in summon:
        click_dict[sk] = len(df_without_tick[df_without_tick["name"] == sk]) * counts[sk]

    for sk in independant:
        click_dict[sk] = len(df_all[df_all["name"] == sk]) * counts[sk]

    df_keydown = df_without_tick[
        df_without_tick["name"].isin(pressing + every + summon)
    ]["name"]
    df_keydown = df_keydown.loc[df_keydown.shift() != df_keydown]

    for sk in pressing:
        click_dict[sk] = len(df_keydown[df_keydown == sk]) * counts[sk]

    # print(click_dict)
    click = sum(click_dict.values()) / TEST_TIME + conf.get("else", 0)

    preset = get_preset(args.id)
    print(args.id, preset.job, click)


if __name__ == "__main__":
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
            cpm(task, data)
    else:
        if args.calc:
            data = save_data(args)
            cpm(args, data)
        else:
            data = load_data(args)
            cpm(args, data)
