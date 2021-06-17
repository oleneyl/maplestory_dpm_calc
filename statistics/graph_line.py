import argparse
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import ticker
from .loader import load_data
from .saver import save_data
from .preset import get_preset

plt.style.use(["bmh"])


def get_args():
    parser = argparse.ArgumentParser("Peak argument")
    parser.add_argument(
        "--id", type=str, help="Target preset id to calculate statistics"
    )
    parser.add_argument("--data", type=str)
    parser.add_argument("--ulevel", type=int, default=8000)
    parser.add_argument("--cdr", type=int, default=0)
    parser.add_argument("--task", default="dpm")
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--calc", action="store_true")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--xlim", type=int, default=480)

    return parser.parse_args()


def graph_line(args, df: pd.DataFrame):
    df = df.drop(["name", "loss", "hit", "mdf", "spec"], axis=1)
    df = df[df["time"] <= args.xlim * 1000]
    df["time"] = df["time"].astype("timedelta64[ms]")
    df["time"] = df["time"].dt.total_seconds()
    df["deal_total"] = df["deal"].cumsum()

    preset = get_preset(args.id)

    ax = plt.axes()
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x/1e+12:.0f}조"))
    plt.plot(df["time"], df["deal_total"])
    plt.title(f"{preset.job} {preset.description}, 쿨감{args.cdr}초", fontsize=12)
    if args.show:
        plt.show()
    else:
        Path("data/graph_line/").mkdir(parents=True, exist_ok=True)
        plt.savefig(
            f"data/graph_line/{args.task}_{args.id}_{args.ulevel}_{args.cdr}.png"
        )


if __name__ == "__main__":
    args = get_args()
    if args.calc:
        data = save_data(args)
    elif args.data:
        data = pd.read_pickle(f"./data/{args.data}.pkl")
    else:
        data = load_data(args)
    graph_line(args, data)
