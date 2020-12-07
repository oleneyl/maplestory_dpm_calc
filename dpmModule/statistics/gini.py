import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

plt.style.use(["bmh"])


def run(args, df: pd.DataFrame):
    df = df.drop(["name", "loss", "hit", "mdf", "spec"], axis=1)
    df["time"] = df["time"].astype("datetime64[ms]")
    df["rolled"] = df.rolling(str(args.interval)+"ms", on="time")["deal"].sum()
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
    plt.savefig(f"data/{args.id}.png")
    # plt.show()
