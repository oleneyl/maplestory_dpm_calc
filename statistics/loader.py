import pandas as pd


def load_data(args):
    df = pd.read_pickle(f"./data/{args.task}_{args.id}_{args.ulevel}_{args.cdr}.pkl")
    return df
