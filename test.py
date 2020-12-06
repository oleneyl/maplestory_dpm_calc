from dpmModule.character.characterTemplate import get_template_generator
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
from dpmModule.util.burstgenerator import BurstGenerator
from dpmModule.util.configurations import export_configuration

import json

import argparse


def get_args():
    parser = argparse.ArgumentParser("DPM Test argument")
    parser.add_argument("--job", type=str, help="Target class' Korean name to test DPM")
    parser.add_argument(
        "--level",
        type=int,
        default=None,
        help="Character's level, default depends on ulevel",
    )
    parser.add_argument(
        "--ulevel", type=int, default=6000, help="Union level, default is 6000"
    )
    parser.add_argument(
        "--time",
        type=int,
        default=1800,
        help="Test time in seconds, default is 1800(30 min)",
    )
    parser.add_argument(
        "--cdr",
        type=int,
        default=0,
        help="Cooltime reduce (hat potential) in seconds, default is 0",
    )
    parser.add_argument("--log", action="store_true", help="print the log of the test")
    parser.add_argument(
        "--stat", action="store_true", help="print the statistics of the test"
    )
    parser.add_argument("--task", default="dpm")

    return parser.parse_args()


def test():
    args = get_args()
    if args.task == "dpm":
        dpm(args)
    elif args.task == "conf":
        conf(args)
    elif args.task == "burst10":
        burst_10sec(args)


def conf(args):
    job_real = args.job[:].replace("-", "/")

    with open(f"{args.job}.conf.json", "w", encoding="utf8") as f:
        json.dump(export_configuration(job_real), f, ensure_ascii=False, indent=4)


def dpm(args):
    template = get_template_generator("high_standard")().get_template(args.ulevel)
    parser = IndividualDPMGenerator(args.job, template)
    parser.set_runtime(args.time * 1000)
    try:
        dpm = parser.get_dpm(
            ulevel=args.ulevel,
            cdr=args.cdr,
            level=args.level,
            weaponstat=[4, 9],
            printFlag=args.log,
            statistics=args.stat or args.log,
        )
    finally:
        print(args.job, "{:,.3f}".format(dpm))


def burst_10sec(args):
    template = get_template_generator("high_standard")().get_template(args.ulevel)
    parser = BurstGenerator(args.job, template)
    parser.set_runtime(args.time * 1000)
    try:
        start, end, dpm, loss = parser.burst_10sec(
            ulevel=args.ulevel,
            cdr=args.cdr,
            weaponstat=[4, 9],
            printFlag=args.log,
            statistics=args.stat or args.log,
        )
    finally:
        print(args.job, "{:,.3f}".format(dpm))
        print("Loss:", "{:,.3f}".format(loss))
        print(start, end)


if __name__ == "__main__":
    test()
