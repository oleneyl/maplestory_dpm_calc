import sys, os

import dpmModule.character.characterTemplateHigh as template
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
    parser.add_argument('--level', type=int, default=230)
    parser.add_argument('--ulevel', type=int, default=6000)
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
        parser = IndividualDPMGenerator(jobname, template.getU6000CharacterTemplate)
        try:
            dpm = parser.get_dpm(ulevel = args.ulevel,
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
