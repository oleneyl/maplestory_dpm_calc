import sys, os

from  dpmModule.character.characterTemplate import get_template_generator
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
from dpmModule.util.configurations import export_configuration
from dpmModule.kernel import graph
from dpmModule.jobs import jobMap
from dpmModule.kernel import core

import time, json

import argparse

jobname = "나이트로드"
ulevel = 6000
weaponstat = [4,9]
level = 230

def get_args():
    parser = argparse.ArgumentParser('DPM Test argument')
    parser.add_argument('--job', type=str, help='Target job name to test dpm')
    parser.add_argument('--level', type=int, default=None)
    parser.add_argument('--ulevel', type=int, default=6000)
    parser.add_argument('--time', type=int, default=1800)
    parser.add_argument('--log', action='store_true')
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
    if args.job == 'all':
        jobs = jobMap.keys()
    else:
        jobs = [args.job]

    for jobname in jobs:
        template = get_template_generator('high_standard')().get_template(args.ulevel)
        parser = IndividualDPMGenerator(jobname, template)
        parser.set_runtime(args.time*1000)
        try:
            dpm = parser.get_dpm(ulevel = args.ulevel,
            level = args.level,
            weaponstat = weaponstat,
            printFlag=args.log)
        except:
            raise
        finally:
            print(jobname, dpm)

    #with open('conf.json', 'w', encoding='utf8') as f:
    #    graph._unsafe_access_global_storage()._storage.write(f)

if __name__ == '__main__':
    test()
