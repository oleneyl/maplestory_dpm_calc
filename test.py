from dpmModule.character.characterTemplate import get_template_generator
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
from dpmModule.util.configurations import export_configuration

import time, json

import argparse

def get_args():
    parser = argparse.ArgumentParser('DPM Test argument')
    parser.add_argument('--job', type=str, help='Target job name to test dpm')
    parser.add_argument('--level', type=int, default=None)
    parser.add_argument('--ulevel', type=int, default=6000)
    parser.add_argument('--time', type=int, default=1800)
    parser.add_argument('--log', action='store_true')
    parser.add_argument('--stat', action='store_true')
    parser.add_argument('--cdr', type=int, default=0)
    parser.add_argument('--task',default='dpm')

    return parser.parse_args()

def test():
    args = get_args()
    if args.task == 'dpm':
        dpm(args)
    elif args.task == 'conf':
        conf(args)

def conf(args):
    job_real = args.job[:].replace('-','/')
    
    with open(f'{args.job}.conf.json', 'w', encoding='utf8') as f: 
        json.dump( export_configuration(job_real), f, ensure_ascii = False, indent = 4)

def dpm(args):
    template = get_template_generator('high_standard')().get_template(args.ulevel)
    parser = IndividualDPMGenerator(args.job, template)
    parser.set_runtime(args.time*1000)
    try:
        dpm = parser.get_dpm(ulevel = args.ulevel,
        cdr = args.cdr,
        level = args.level,
        weaponstat = [4,9],
        printFlag=args.log,
        statistics=args.stat or args.log)
    except:
        raise
    finally:
        print(args.job, dpm)

if __name__ == '__main__':
    test()
