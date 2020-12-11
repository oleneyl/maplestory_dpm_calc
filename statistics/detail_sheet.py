import argparse
from pathlib import Path

from .loader import load_data
from .preset import get_preset
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
    parser.add_argument("--ulevel", type=int, default=8000)
    parser.add_argument("--cdr", type=int, default=0)
    parser.add_argument("--task", default="dpm")
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--calc", action="store_true")

    return parser.parse_args()


def write_sheet(args, df: pd.DataFrame, writer: xlsxwriter):
    id, jobname, description, options, alt = get_preset(args.id)

    df = df.drop(["time", "spec", "mdf"], axis=1)
    df["name"] = df["name"].apply(lambda x: x.split("(")[0])
    df["deal_one"] = df["deal"] / df["hit"]
    df = df.loc[df.deal > 0]
    deal_total = df["deal"].sum()
    loss_total = df["loss"].sum()
    hit_total = df["hit"].sum()

    grouped = df.groupby(["name"])
    df = pd.DataFrame()
    df["누적 데미지"] = grouped["deal"].sum()
    df["맥뎀 누수"] = grouped["loss"].sum()
    df["점유율"] = df["누적 데미지"] / deal_total
    df["평균 데미지(1초당)"] = df["누적 데미지"] / 30
    df["사용 횟수"] = grouped["hit"].count()
    df["평균 데미지(1회당)"] = df["누적 데미지"] / df["사용 횟수"]
    df["공격 횟수"] = grouped["hit"].sum()
    df["최대 데미지(1타당)"] = grouped["deal_one"].max()
    df["최소 데미지(1타당)"] = grouped["deal_one"].min()
    df["맥뎀 누수율"] = df["맥뎀 누수"] / (df["누적 데미지"] + df["맥뎀 누수"])
    df["맥뎀 누수율"].clip(lower=0, inplace=True)

    df = df.sort_values(by="점유율", axis=0, ascending=False)

    sheet_name = jobname.replace("/", "_") + "_" + str(args.cdr) + "_" + str(alt)
    df.to_excel(writer, sheet_name=sheet_name, startrow=3)

    workbook: xlsxwriter.Workbook = writer.book
    worksheet: xlsxwriter.workbook.Worksheet = writer.sheets[sheet_name]

    center_format = workbook.add_format({"align": "center"})
    num_format = workbook.add_format({"num_format": "#,##0", "align": "center"})
    percent_format = workbook.add_format({"num_format": "0.00%", "align": "center"})

    worksheet.set_column("A:K", 20, center_format)
    worksheet.set_column("B:C", 20, num_format)
    worksheet.set_column("D:D", 20, percent_format)
    worksheet.set_column("E:J", 20, num_format)
    worksheet.set_column("K:K", 10, percent_format)

    worksheet.merge_range("B3:G3", "", center_format)

    worksheet.write("A1", "직업")
    worksheet.write("B1", jobname)
    worksheet.write("A2", "쿨감")
    worksheet.write("B2", args.cdr)
    worksheet.write("A3", "비고")
    worksheet.write("B3", description)
    worksheet.write("C1", "dpm")
    worksheet.write("D1", deal_total / 30, num_format)
    worksheet.write("C2", "맥뎀누수")
    worksheet.write("D2", loss_total / 30, num_format)
    worksheet.write("E1", "분당 타수")
    worksheet.write("F1", hit_total / 30, num_format)
    worksheet.write("E2", "맥뎀 누수율")
    worksheet.write("F2", loss_total / deal_total, percent_format)


if __name__ == "__main__":
    args = get_args()
    if args.calc:
        data = save_data(args)
    else:
        data = load_data(args)

    Path("data/detail_sheet/").mkdir(parents=True, exist_ok=True)
    writer = pd.ExcelWriter(f"data/detail_sheet/{args.task}_{args.id}_{args.ulevel}_{args.cdr}.xlsx", engine="xlsxwriter")
    write_sheet(args, data, writer)
    writer.close()
