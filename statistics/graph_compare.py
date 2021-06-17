import argparse

import pandas as pd
import numpy as np
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

    m = pd.DataFrame(columns=["time", "deal", "label"])
    for i, df in enumerate(data_list):
        df = df.drop(["name", "loss", "hit", "mdf", "spec"], axis=1)
        df["time"] = df["time"] - df["time"].min()
        df = df[df["time"] <= args.xlim*1000]
        df["time"] = df["time"].astype("timedelta64[ms]")
        deals = df.resample("5000ms", on="time")["deal"].sum().reset_index()
        deals["time"] = deals["time"].dt.total_seconds()
        deals["label"] = args.data[i]
        m = m.append(deals)

    print(m)
    sns.barplot(x="time", y="deal", hue="label", data=m)
    plt.xticks(np.arange(0, args.xlim//5, args.xlim//40), [f"{i*5}" for i in np.arange(0, args.xlim//5, args.xlim//40)])
    plt.legend()
    plt.show()


if __name__ == "__main__":
    args = get_args()
    data_list = [pd.read_pickle(f"./data/{label}.pkl") for label in args.data]
    graph(args, data_list)
