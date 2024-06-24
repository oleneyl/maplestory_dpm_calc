from dpmModule.util.dpmgenerator import IndividualDPMGenerator
from concurrent.futures import ProcessPoolExecutor

import time
import argparse
import numpy as np


def get_args():
    parser = argparse.ArgumentParser("DPM Full Test argument")
    parser.add_argument(
        "--ulevel", type=int, default=8000
    )
    parser.add_argument("--job", type=str)
    parser.add_argument("--iter", type=int, default=100)
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--cdr", type=int, default=0)
    parser.add_argument("--thread", type=int, default=4)

    return parser.parse_args()


def test(args):
    jobname, ulevel, runtime, cdr = args
    start = time.time()
    print(f"{jobname} {ulevel} 계산중")

    parser = IndividualDPMGenerator(jobname)
    parser.set_runtime(runtime * 1000)
    dpm = parser.get_dpm(spec_name=str(ulevel), ulevel=ulevel, cdr=cdr)

    end = time.time()
    print(f"{jobname} {ulevel} 계산완료, {end - start:.3f}초")
    return dpm


if __name__ == "__main__":
    args = get_args()
    start = time.time()
    tasks = [(args.job, args.ulevel, args.time, args.cdr)]*args.iter
    pool = ProcessPoolExecutor(max_workers=args.thread)
    results = list(pool.map(test, tasks))
    mean = np.mean(results)
    std = np.std(results)
    cv = std / mean
    print("mean:", mean)
    print("cv:", cv)
    end = time.time()
    print(f"총 소요시간: {end - start:.3f}초")
