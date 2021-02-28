from dpmModule.util.dpmgenerator import IndividualDPMGenerator
from dpmModule.jobs import jobMap
from concurrent.futures import ProcessPoolExecutor
from itertools import product, groupby
from operator import itemgetter

import time
import argparse

import gettext
_ = gettext.gettext

def get_args():
    parser = argparse.ArgumentParser("DPM Full Test argument")
    parser.add_argument("--ulevel", nargs="+", type=int, default=[4500, 5000, 6000, 7000, 8000, 8500])
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--cdr", type=int, default=0)
    parser.add_argument("--thread", type=int, default=4)

    return parser.parse_args()


def test(args):
    job, ulevel, runtime, cdr = args
    start = time.time()
    print(_("{} {} 계산중".format(job, ulevel)))

    parser = IndividualDPMGenerator(job)
    parser.set_runtime(runtime * 1000)
    dpm = parser.get_dpm(spec_name=str(ulevel), ulevel=ulevel, cdr=cdr)

    end = time.time()
    print(_("{} {} 계산완료, {:.3f}초".format(job, ulevel, end - start)))
    return job, ulevel, dpm


def write_results(results):
    dpm_output = open("dpm_output.txt", "w", encoding="utf-8")
    for job, result in groupby(results, key=itemgetter(0)):
        dpm_output.write(f'{job}')
        for dpm in map(itemgetter(2), result):
            dpm_output.write(" ")
            dpm_output.write(str(dpm))
        dpm_output.write("\n")
    dpm_output.close()


if __name__ == "__main__":
    args = get_args()
    start = time.time()
    ulevels = args.ulevel
    tasks = product(jobMap.keys(), ulevels, [args.time], [args.cdr])
    pool = ProcessPoolExecutor(max_workers=args.thread)
    results = pool.map(test, tasks)
    write_results(results)
    end = time.time()
    print(_("총 소요시간: {:.3f}초".format(end - start)))
