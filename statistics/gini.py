import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from .loader import load_data
from .saver import save_data

plt.style.use(["bmh"])


def get_args():
    parser = argparse.ArgumentParser("Gini coefficient argument")
    parser.add_argument(
        "--id", type=str, help="Target preset id to calculate statistics"
    )
    parser.add_argument("--ulevel", type=int, default=8000)
    parser.add_argument("--cdr", type=int, default=0)
    parser.add_argument("--task", default="dpm")
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--calc", action="store_true")
    parser.add_argument("--interval", default=10000)
    parser.add_argument("--show", action="store_true")

    return parser.parse_args()


def gini(args, df: pd.DataFrame):
    df = df.drop(["name", "loss", "hit", "mdf", "spec"], axis=1)
    df["time"] = df["time"].astype("datetime64[ms]")
    df["rolled"] = df.rolling(f"{args.interval}ms", on="time")["deal"].sum()
    sorted_frames = df["rolled"].sort_values(axis=0, ascending=True)
    lorenz_curve = sorted_frames.cumsum()
    pred_line = np.linspace(
        start=lorenz_curve.min(), stop=lorenz_curve.max(), num=len(lorenz_curve)
    )

    area_under_lorenz = np.trapz(y=lorenz_curve, dx=1 / len(lorenz_curve))
    area_under_pred = np.trapz(y=pred_line, dx=1 / len(lorenz_curve))

    gini = (area_under_pred - area_under_lorenz) / area_under_pred

    plt.plot(pred_line, lorenz_curve)
    plt.plot(pred_line, pred_line)
    plt.fill_between(pred_line, lorenz_curve)
    plt.title(f"{args.id}: {gini:.6f}", fontsize=20)
    if args.show:
        plt.show()

    Path("data/gini/").mkdir(parents=True, exist_ok=True)
    plt.savefig(f"data/gini/{args.task}_{args.id}_{args.ulevel}_{args.cdr}.png")


if __name__ == "__main__":
    args = get_args()
    if args.calc:
        data = save_data(args)
    else:
        data = load_data(args)
    gini(args, data)
