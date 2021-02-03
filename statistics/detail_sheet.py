import argparse
from pathlib import Path

from .loader import load_data
from .preset import get_preset, get_preset_list
from .saver import save_data

try:
    import pandas as pd
    import xlsxwriter
except ImportError:
    print("pandas, xlsxwriter 모듈을 설치해야 합니다.")
    exit()


def get_args():
    parser = argparse.ArgumentParser("Detail sheet argument")
    parser.add_argument(
        "--id", type=str, help="Target preset id to calculate statistics"
    )
    parser.add_argument("--graph", action="store_true")
    parser.add_argument("--ulevel", type=int, default=8000)
    parser.add_argument("--cdr", type=int, default=0)
    parser.add_argument("--task", default="dpm")
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--calc", action="store_true")
    parser.add_argument("--all", action="store_true")

    return parser.parse_args()


def write_sheet(args, df: pd.DataFrame, writer: xlsxwriter):
    id, jobname, description, options, alt = get_preset(args.id)
    time = 1800

    df = df.drop(["time", "spec", "mdf"], axis=1)
    df["name"] = df["name"].apply(lambda x: x.split("(")[0])
    df["deal_one"] = df["deal"] / df["hit"]
    df = df.loc[df.deal > 0]
    deal_total = df["deal"].sum()
    hit_total = df["hit"].sum()

    grouped = df.groupby(["name"])
    df = pd.DataFrame()
    df["누적 데미지"] = grouped["deal"].sum()
    df["점유율"] = df["누적 데미지"] / deal_total
    df["평균 데미지(1초당)"] = df["누적 데미지"] / time
    df["공격 횟수"] = grouped["hit"].sum()
    df["최대 데미지(1타당)"] = grouped["deal_one"].max()
    df["평균 데미지(1타당)"] = grouped["deal_one"].mean()
    df["최소 데미지(1타당)"] = grouped["deal_one"].min()

    df = df.sort_values(by="점유율", axis=0, ascending=False)

    sheet_name = jobname.replace("/", "_") + "_" + str(args.cdr) + "_" + str(alt)
    df.to_excel(writer, sheet_name=sheet_name, startrow=3)

    workbook: xlsxwriter.Workbook = writer.book
    worksheet: xlsxwriter.workbook.Worksheet = writer.sheets[sheet_name]

    center_format = workbook.add_format({"align": "center"})
    num_format = workbook.add_format({"num_format": "#,##0", "align": "center"})
    percent_format = workbook.add_format({"num_format": "0.00%", "align": "center"})

    worksheet.set_column("A:G", 20, center_format)
    worksheet.set_column("B:B", 20, num_format)
    worksheet.set_column("C:C", 20, percent_format)
    worksheet.set_column("D:H", 20, num_format)

    worksheet.merge_range("B3:G3", "", center_format)

    worksheet.write("A1", "직업")
    worksheet.write("B1", jobname)
    worksheet.write("A2", "쿨감")
    worksheet.write("B2", args.cdr)
    worksheet.write("A3", "비고")
    worksheet.write("B3", description)
    worksheet.write("C1", "dpm")
    worksheet.write("D1", deal_total / (time / 60), num_format)
    worksheet.write("C2", "분당 타수")
    worksheet.write("D2", hit_total / (time / 60), num_format)

    if args.graph:
        worksheet.insert_image(f"B{len(grouped)+6}", f"data/graph/{args.task}_{args.id}_{args.ulevel}_{args.cdr}.png")


def save_all(args):
    presets = get_preset_list()
    tasks = [
        argparse.Namespace(
            id=id, graph=args.graph, ulevel=args.ulevel, cdr=cdr, time=args.time, task=args.task
        )
        for id, *_ in presets for cdr in [0, 2, 4]
    ]
    Path("data/detail_sheet/").mkdir(parents=True, exist_ok=True)
    writer = pd.ExcelWriter("data/detail_sheet/detail_sheet.xlsx", engine="xlsxwriter")
    for task in tasks:
        data = load_data(task)
        write_sheet(task, data, writer)
    writer.close()


if __name__ == "__main__":
    args = get_args()
    if args.all:
        save_all(args)
        exit()

    if args.calc:
        data = save_data(args)
    else:
        data = load_data(args)

    Path("data/detail_sheet/").mkdir(parents=True, exist_ok=True)
    writer = pd.ExcelWriter(f"data/detail_sheet/{args.task}_{args.id}_{args.ulevel}_{args.cdr}.xlsx", engine="xlsxwriter")
    write_sheet(args, data, writer)
    writer.close()
