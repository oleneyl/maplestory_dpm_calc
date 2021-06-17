import argparse

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import ticker
import seaborn as sns

plt.style.use(["bmh"])
sns.set_palette(sns.color_palette("Paired", 6))


def get_args():
    parser = argparse.ArgumentParser("graph argument")
    parser.add_argument("--data", type=str, nargs="+")
    parser.add_argument("--xlim", type=int, default=171)

    return parser.parse_args()


def graph(args, data_list):
    ax = plt.axes()
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: f"{x/1e+12:.0f}조")
    )

    for i, df in enumerate(data_list):
        df = df.drop(["name", "loss", "hit", "mdf", "spec"], axis=1)
        df["time"] = df["time"] - df["time"].min()
        df = df[df["time"] <= args.xlim*1000]
        df["time"] = df["time"].astype("timedelta64[ms]")
        df["time"] = df["time"].dt.total_seconds()
        df["deal_total"] = df["deal"].cumsum()
        print(df["deal_total"].max())
        plt.plot(df["time"], df["deal_total"], label=args.data[i])

    plt.legend()
    plt.show()


if __name__ == "__main__":
    args = get_args()
    data_list = [pd.read_pickle(f"./data/{label}.pkl") for label in args.data]
    graph(args, data_list)
