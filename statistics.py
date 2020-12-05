from dpmModule.character.characterTemplate import get_template_generator
from dpmModule.util.dpmgenerator import IndividualDPMGenerator

import argparse

import numpy


def get_args():
    parser = argparse.ArgumentParser("DPM Statistics Test argument")
    parser.add_argument("--job", type=str, help="Target class' Korean name to test DPM")
    parser.add_argument("--level", type=int, default=None, help="Character's level, default depends on ulevel")
    parser.add_argument("--ulevel", type=int, default=6000, help="Union level, default is 6000")
    parser.add_argument("--time", type=int, default=1800, help="Test time in seconds, default is 1800(30 min)")
    parser.add_argument("--cdr", type=int, default=0, help="Cooltime reduce (hat potential) in seconds, default is 0")
    parser.add_argument("--task", type=str, default="stddev", help="Task of the test (Standard Deviation(default): stddev, Gini coefficient: gini)")

    return parser.parse_args()


def get_stddev(data, runtime):
    # interval: 1초
    table = data['data']
    pdf = [0]*(runtime+1)  # 확률 분포 함수
    for elem in table:
        pdf[int(min(elem['time']/1000, runtime))] += elem['deal']
    return numpy.std(pdf)


def get_gini(data, runtime):
    # interval: 1초
    table = data['data']
    cdf = [0]*(runtime+1)  # 누적 분포 함수
    lorenz = [0]*(runtime+1)  # 로렌츠 곡선
    gini = 0  # 지니 계수
    for elem in table:
        cdf[int(min(elem['time']/1000, runtime))] += elem['deal']
    cdf.sort()
    for i in range(0, runtime+1):
        for j in range(i, runtime+1):
            lorenz[j] += cdf[i]
    for i in range(0, runtime+1):
        gini += lorenz[-1] * (i/runtime) - lorenz[i]
    return gini/(1/2*lorenz[-1]*(runtime+1))


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
            res = get_stddev(data, args.time)
        elif args.task == "gini":
            res = get_gini(data, args.time)
    finally:
        if res:
            print(args.job, res)
        else:
            print("Wrong argument!")


if __name__ == "__main__":
    dpm(get_args())
