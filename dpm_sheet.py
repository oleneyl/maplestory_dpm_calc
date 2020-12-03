from dpmModule.character.characterTemplate import get_template_generator
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
from concurrent.futures import ProcessPoolExecutor
from itertools import product

import argparse

try:
    import pandas as pd
    import xlsxwriter
except ImportError:
    print("pandas, xlsxwriter 모듈을 설치해야 합니다.")
    exit()


def get_args():
    parser = argparse.ArgumentParser("DPM Sheet argument")
    parser.add_argument("--ulevel", type=int, default=8000)
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--thread", type=int, default=4)

    return parser.parse_args()


def get_presets():
    return [
        ("히어로", "두손도끼, 소오버 고정", {}, 0),
        ("팔라딘", "두손둔기, 블레싱 아머 미발동", {}, 0),
        ("다크나이트", "다크 스피어 8히트, 체력 100%, 리인카 사용", {}, 0),
        ("아크메이지불/독", "포이즌 노바 4히트, 언스 사용", {}, 0),
        ("아크메이지썬/콜", "썬브 2히트, 언스 사용", {"thunder_break_hit": 2}, 0),
        ("아크메이지썬/콜", "썬브 8히트, 언스 사용", {"thunder_break_hit": 8}, 1),
        ("비숍", "피스메이커 3히트, 솔플, 언스 사용", {}, 0),
        ("보우마스터", "애로우 레인 1줄기", {}, 0),
        ("신궁", "거리 400", {"distance": 400}, 0),
        ("신궁", "거리 0", {"distance": 0}, 1),
        ("패스파인더", "블래 210ms 디차 240ms", {}, 0),
        ("나이트로드", "스프 풀히트", {}, 0),
        ("섀도어", "KP3 1타 94.6% / 2타 100%", {}, 0),
        ("듀얼블레이드", "블토 태풍 5히트", {}, 0),
        ("바이퍼", "카운터 어택 미발동", {}, 0),
        ("캡틴", "데드아이 풀조준, 카운터 어택 미발동", {}, 0),
        ("캐논슈터", "코코볼 27히트", {}, 0),
        ("소울마스터", "", {}, 0),
        ("미하일", "솔플, 로얄가드 쿨마다", {}, 0),
        ("플레임위자드", "블비탈 4히트, 오비탈 분당 1350타", {"orbital_per_min": 1350}, 0),
        ("플레임위자드", "블비탈 4히트, 오비탈 분당 1150타", {"orbital_per_min": 1150}, 1),
        ("윈드브레이커", "하울링게일 58히트, 볼텍스 스피어 17히트", {}, 0),
        ("나이트워커", "점샷 400ms", {}, 0),
        ("스트라이커", "파섬", {"dealcycle": "waterwave"}, 0),
        ("스트라이커", "벽섬", {"dealcycle": "thunder"}, 1),
        ("블래스터", "매그팡 510ms", {}, 0),
        ("데몬슬레이어", "블블 100%", {}, 0),
        ("배틀메이지", "좌우텔 분당 83회, 디버프 오라만, 명계문 미사용", {}, 0),
        ("와일드헌터", "재규어 스톰 3히트", {}, 0),
        ("메카닉", "", {}, 0),
        ("아란", "", {}, 0),
        ("에반", "다오어 3히트, 다오어-브레스-브오어", {}, 0),
        ("루미너스", "", {}, 0),
        ("메르세데스", "엘고때 연계사이클", {"dealcycle": "combo"}, 0),
        ("메르세데스", "엘고때 이슈타르", {"dealcycle": "ishtar"}, 1),
        ("팬텀", "블디, 블디/크오체/파컷/불스아이, 체력 100%", {"dealcycle": "blast_discharge"}, 0),
        ("팬텀", "얼드, 분노/크오체/파컷/불스아이, 체력 100%", {"dealcycle": "ultimate_drive"}, 1),
        ("은월", "분혼 격참 이동형 보스 판정, 약점 간파 적용", {"hp_rate": True}, 0),
        ("은월", "분혼 격참 이동형 보스 판정, 약점 간파 미적용", {"hp_rate": False}, 1),
        ("카이저", "", {}, 0),
        ("카데나", "1타캔슬 150ms, 캔슬 180ms, 윙대거 3틱", {}, 0),
        ("엔젤릭버스터", "스포트라이트 3중첩, 어피니티IV 가동률 94.18%", {"spotlight": 3}, 0),
        ("엔젤릭버스터", "스포트라이트 2중첩, 어피니티IV 가동률 94.18%", {"spotlight": 2}, 1),
        ("아델", "게더링, 블로섬 80% 히트, 레조넌스 10초마다", {}, 0),
        ("일리움", "", {}, 0),
        ("아크", "플레인 캔슬 270ms, 흉몽 캔슬 210ms", {}, 0),
        ("호영", "금고봉/지진쇄/토파류", {}, 0),
        ("제로", "문피쉐, 카벨뚝", {"dealcycle": "alpha_new"}, 0),
        ("제로", "어파스, 카벨뚝", {"dealcycle": "alpha_legacy"}, 1),
        ("키네시스", "메테리얼", {}, 0),
    ]


def test(args):
    preset, ulevel, cdr, runtime = args
    jobname, description, options, alt = preset

    template = get_template_generator("high_standard")().get_template(ulevel)
    parser = IndividualDPMGenerator(jobname, template)
    parser.set_runtime(runtime * 1000)
    result = parser.get_detailed_dpm(ulevel=ulevel, cdr=cdr, options=options)
    dpm = result["dpm"]
    loss = result["loss"]

    return jobname, cdr, description, dpm, loss, alt


if __name__ == "__main__":
    args = get_args()
    ulevel = args.ulevel
    tasks = product(get_presets(), [ulevel], [0, 2, 4], [args.time])
    pool = ProcessPoolExecutor(max_workers=args.thread)
    results = pool.map(test, tasks)

    df = pd.DataFrame.from_records(
        results,
        columns=["직업", "쿨감", "비고", "dpm", "loss", "alt"],
    )
    # df.to_pickle("cache.pkl")
    # df: pd.DataFrame = pd.read_pickle("cache.pkl")
    df = df.sort_values(by="dpm", axis=0, ascending=False)
    df = df.drop_duplicates(subset=["직업", "비고"]).copy()

    median = df["dpm"].median()
    df["배율"] = df["dpm"] / median
    df["맥뎀누수율"] = df["loss"] / df["dpm"]

    non_alts = df[df["alt"] == 0].copy()
    non_alts["격차"] = non_alts["배율"] - non_alts["배율"].shift(-1)
    alts = df[df["alt"] > 0].copy()

    df = non_alts.append(alts)
    df = df.sort_values(by="dpm", axis=0, ascending=False)
    df = df[["직업", "쿨감", "비고", "dpm", "배율", "맥뎀누수율", "alt"]]

    writer = pd.ExcelWriter("./result.xlsx", engine="xlsxwriter")
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
    worksheet.set_column("F:F", 10, percent_format)
    worksheet.set_column("G:G", None, None, {"hidden": True})

    worksheet.conditional_format(
        "E2:E55", {"type": "data_bar", "bar_solid": True, "bar_color": "#63C384"}
    )
    worksheet.conditional_format(
        "F2:F55", {"type": "data_bar", "bar_solid": True, "bar_color": "#FF555A"}
    )
    worksheet.conditional_format(
        "A2:D55", {"type": "formula", "criteria": "$G2>0", "format": alt_format}
    )

    writer.close()
