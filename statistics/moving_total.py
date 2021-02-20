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
    parser = argparse.ArgumentParser("Peak argument")
    parser.add_argument(
        "--id", type=str, help="Target preset id to calculate statistics"
    )
    parser.add_argument("--ulevel", type=int, default=8000)
    parser.add_argument("--cdr", type=int, default=0)
    parser.add_argument("--task", default="dpm")
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--calc", action="store_true")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--interval", type=int, default=10000)
    parser.add_argument("--xlim", type=int, default=480)

    return parser.parse_args()


def moving_total(args, df: pd.DataFrame):
    df = df.drop(["name", "loss", "hit", "mdf", "spec"], axis=1)
    df = df[df["time"] <= args.xlim*1000]
    df["time"] = df["time"].astype("timedelta64[ms]")
    df = df.set_index("time")
    rolled = df.rolling(f"{args.interval}ms")["deal"].sum().reset_index()
    rolled["time"] = rolled["time"].dt.total_seconds()
    peak = rolled["deal"].max()
    print(f"{peak:,.0f}")

    preset = get_preset(args.id)

    plt.plot(rolled["time"], rolled["deal"])
    plt.yticks(np.arange(0, 10e+12, 1e+12), [f"{i/1e+12}T" for i in np.arange(0, 10e+12, 1e+12)])
    plt.title(f"{preset.job} {preset.description}, 쿨감{args.cdr}초, {args.interval//1000}초 이동합계", fontsize=12)
    if args.show:
        plt.show()
    else:
        Path("data/graph/").mkdir(parents=True, exist_ok=True)
        plt.savefig(f"data/graph/{args.task}_{args.id}_{args.ulevel}_{args.cdr}.png")


if __name__ == "__main__":
    args = get_args()
    if args.calc:
        data = save_data(args)
    else:
        data = load_data(args)
    moving_total(args, data)
