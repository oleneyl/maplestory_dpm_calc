import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from .loader import load_data
from .saver import save_data
from .preset import get_preset

plt.style.use(["bmh"])


def get_args():
    parser = argparse.ArgumentParser("graph argument")
    parser.add_argument(
        "--id", type=str, help="Target preset id to calculate statistics"
    )
    parser.add_argument("--ulevel", type=int, default=8000)
    parser.add_argument("--cdr", type=int, default=0)
    parser.add_argument("--task", default="dpm")
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--calc", action="store_true")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--xlim", type=int, default=180)

    return parser.parse_args()


def graph(args, df: pd.DataFrame):
    df = df.drop(["name", "loss", "hit", "mdf", "spec"], axis=1)
    line_y = df["deal"].sum() / (1800/5)
    df.loc[-1] = [0, 0]
    df.index = df.index + 1
    df.sort_index(inplace=True)
    df = df[df["time"] <= args.xlim*1000]
    df["time"] = df["time"].astype("datetime64[ms]")
    deals = df.resample("5000ms", on="time")["deal"].sum()

    preset = get_preset(args.id)

    plt.bar(range(len(deals)), deals.values)
    plt.plot(range(len(deals)), [line_y for _ in range(len(deals))], 'r--')
    plt.xticks(np.arange(0, args.xlim//5, args.xlim//40), [f"{i*5}" for i in np.arange(0, args.xlim//5, args.xlim//40)])
    plt.ylim(0, 5.5e+12)
    plt.yticks(np.arange(0, 5.5e+12, 1e+12), [f"{i/1e+12}T" for i in np.arange(0, 5.5e+12, 1e+12)])
    plt.title(f"{preset.job} {preset.description}, 쿨감{args.cdr}초", fontsize=12)
    if args.show:
        plt.show()

    Path("data/graph/").mkdir(parents=True, exist_ok=True)
    plt.savefig(f"data/graph/{args.task}_{args.id}_{args.ulevel}_{args.cdr}.png")


if __name__ == "__main__":
    args = get_args()
    if args.calc:
        data = save_data(args)
    else:
        data = load_data(args)
    graph(args, data)
