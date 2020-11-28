from dpmModule.character.characterTemplate import get_template_generator
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
from dpmModule.util.configurations import export_configuration
from dpmModule.jobs import jobMap
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from operator import itemgetter

import argparse
try:
    import pandas as pd
    import openpyxl
except ImportError:
    print("pandas, openpyxl, jinja2 모듈을 설치해야 합니다.")
    exit()

def get_args():
    parser = argparse.ArgumentParser('DPM Sheet argument')
    parser.add_argument('--ulevel', type=int, default=8000)
    parser.add_argument('--time', type=int, default=1800)
    parser.add_argument('--thread', type=int, default=4)

    return parser.parse_args()


def test(args):
    jobname, ulevel, runtime = args

    template = get_template_generator('high_standard')().get_template(ulevel)
    parser = IndividualDPMGenerator(jobname, template)
    parser.set_runtime(runtime * 1000)
    dpm = parser.get_dpm(ulevel=ulevel)

    return jobname, dpm


if __name__ == '__main__':
    args = get_args()
    ulevel = args.ulevel
    tasks = product(jobMap.keys(), [ulevel], [args.time])
    pool = ProcessPoolExecutor(max_workers=args.thread)
    results = pool.map(test, tasks)
    results = sorted(list(results), key=itemgetter(1), reverse=True)
    dpms = []
    jobs = []
    for v in results:
        jobs.append(v[0])
        dpms.append(v[1])
    df = pd.DataFrame({'DPM': dpms})
    df.index = jobs
    df.to_excel("./result.xlsx")
