import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from statistics.preset import get_preset_list

from dpmModule.util.dpmgenerator import IndividualDPMGenerator

try:
    import pandas as pd
    import xlsxwriter
except ImportError:
    print("pandas, xlsxwriter modules are missing, please import them. 모듈을 설치해야 합니다.")
    exit()


def get_args():
    parser = argparse.ArgumentParser("DPM Sheet argument")
    parser.add_argument("--ulevel", type=int, default=8000)
    parser.add_argument("--cdr", nargs="+", type=int, default=[0, 2, 4])
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--thread", type=int, default=4)

    return parser.parse_args()


def test(args):
    preset, ulevel, cdr, runtime = args
    id, jobname, description, options, alt = preset
    parser = IndividualDPMGenerator(jobname)
    parser.set_runtime(runtime * 1000)
    result = parser.get_detailed_dpm(spec_name=str(ulevel), ulevel=ulevel, cdr=cdr, options=options)
    dpm = result["dpm"]
    loss = result["loss"]

    return jobname, cdr, description, dpm, loss, alt


if __name__ == "__main__":
    args = get_args()
    ulevel = args.ulevel
    tasks = product(get_preset_list(), [ulevel], args.cdr, [args.time])
    pool = ProcessPoolExecutor(max_workers=args.thread)
    results = pool.map(test, tasks)

    df = pd.DataFrame.from_records(
        results,
        exclude=["loss"],
        columns=["Job | 직업", "CDR | 쿨감", "Remarks | 비고", "dpm", "loss", "alt"],
    )
    # df.to_pickle("cache.pkl")
    # df: pd.DataFrame = pd.read_pickle("cache.pkl")
    df = df.sort_values(by="dpm", axis=0, ascending=False)
    df = df.drop_duplicates(subset=["Job | 직업", "Remarks | 비고"]).copy()

    df["best"] = df.groupby(["Job | 직업"])["dpm"].transform("max")
    df = df.sort_values(by=["best", "dpm"], axis=0, ascending=False)

    median = df["best"].median()
    df["Percentage to Median | 배율"] = df["dpm"] / median

    df = df[["Job | 직업", "CDR | 쿨감", "Remarks | 비고", "dpm", "Percentage to Median | 배율", "alt"]]

    writer = pd.ExcelWriter(f"./dpm_sheet_{ulevel}.xlsx", engine="xlsxwriter")
    df.to_excel(writer, sheet_name="dpm", index=False)
    workbook: xlsxwriter.Workbook = writer.book
    worksheet: xlsxwriter.workbook.Worksheet = writer.sheets["dpm"]

    center_format = workbook.add_format({"align": "center"})
    num_format = workbook.add_format({"num_format": "#,##0", "align": "center"})
    percent_format = workbook.add_format({"num_format": "0.00%", "align": "center"})
    alt_format = workbook.add_format({"font_color": "#808080"})

    worksheet.set_column("A:I", None, center_format)
    worksheet.set_column("A:A", 15)
    worksheet.set_column("B:B", 5)
    worksheet.set_column("C:C", 45)
    worksheet.set_column("D:D", 18, num_format)
    worksheet.set_column("E:E", 10, percent_format)
    worksheet.set_column("F:F", None, None, {"hidden": True})

    worksheet.conditional_format(
        "E2:E80", {"type": "data_bar", "bar_solid": True, "bar_color": "#63C384"}
    )
    worksheet.conditional_format(
        "A2:D80", {"type": "formula", "criteria": "$F2>0", "format": alt_format}
    )
    writer.close()
