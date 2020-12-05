from dpmModule.character.characterTemplate import get_template_generator
from dpmModule.util.dpmgenerator import IndividualDPMGenerator

import math
import argparse

import numpy


def get_args():
    parser = argparse.ArgumentParser("DPM Statistics Test argument")
    parser.add_argument("--job", type=str, help="Target class' Korean name to test DPM")
    parser.add_argument("--level", type=int, default=None, help="Character's level, default depends on ulevel")
    parser.add_argument("--ulevel", type=int, default=6000, help="Union level, default is 6000")
    parser.add_argument("--time", type=int, default=1800, help="Test time in seconds, default is 1800(30 min)")
    parser.add_argument("--cdr", type=int, default=0, help="Cooltime reduce (hat potential) in seconds, default is 0")
    parser.add_argument("--interval", type=int, default=1000, help="Interval of the unit of the test in miliseconds (default: 1000)")
    parser.add_argument("--task", type=str, default="stddev", help="Task of the test (Standard Deviation(default): stddev, Gini coefficient: gini)")

    return parser.parse_args()


def distribution_table(table, runtime, interval):
    SIZE = math.ceil(1000/interval*runtime)
    pdf = [0]*SIZE  # 확률 분포 함수
    for elem in table:
        pdf[min(int(elem['time']/interval), SIZE-1)] += elem['deal']
    return pdf


def get_stddev(data, runtime, interval):
    pdf = distribution_table(data['data'], runtime, interval)
    return numpy.std(pdf)


def get_gini(data, runtime, interval):
    pdf = distribution_table(data['data'], runtime, interval)
    SIZE = len(pdf)
    pdf.sort()  # 적분을 위해 정렬

    lorenz = [0]  # (0, 0)부터 (SIZE, SUM)까지
    for i in range(0, SIZE):
        lorenz.append(0)
        for j in range(0, i+1):
            lorenz[-1] += pdf[j]  # 적분

    gini = 0  # 지니 계수
    for i in range(0, SIZE+1):
        gini += (i/SIZE)-lorenz[i]/lorenz[-1]  # (SIZE, SUM)을 (SIZE, 1)로 변환하여 합산
    return 2*gini/SIZE  # 결과값: (SIZE, 1)을 (1, 1)로 변환하고 2를 곱함


def dpm(args):
    template = get_template_generator("high_standard")().get_template(args.ulevel)
    parser = IndividualDPMGenerator(args.job, template)
    parser.set_runtime(args.time*1000)
    # TODO: get_detailed_dpm()에 level 매개변수가 추가되면 아래 주석을 풀어주시기 바랍니다.
    data = parser.get_detailed_dpm(
                ulevel=args.ulevel,
                cdr=args.cdr,
                # level=args.level,
                weaponstat=[4, 9]
            )
    res = None
    try:
        if args.task == "stddev":
            res = get_stddev(data, args.time, args.interval)
        elif args.task == "gini":
            res = get_gini(data, args.time, args.interval)
    finally:
        if res:
            print(args.job, res)
        else:
            print("Wrong argument!")


if __name__ == "__main__":
    dpm(get_args())
