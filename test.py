from dpmModule.util.dpmgenerator import IndividualDPMGenerator
from dpmModule.util.configurations import export_configuration, export_enhancer_configuration

import json

import argparse


def get_args():
    parser = argparse.ArgumentParser("DPM Test argument")
    parser.add_argument("--job", type=str, help="Target class' Korean name to test DPM")
    parser.add_argument("--level", type=int, default=None, help="Character's level, default depends on ulevel")
    parser.add_argument("--ulevel", type=int, default=6000, help="Union level, default is 6000")
    parser.add_argument("--time", type=int, default=1800, help="Test time in seconds, default is 1800(30 min)")
    parser.add_argument("--cdr", type=int, default=0, help="Cooltime reduce (hat potential) in seconds, default is 0")
    parser.add_argument("--log", action="store_true", help="print the log of the test")
    parser.add_argument("--stat", action="store_true", help="print the statistics of the test")
    parser.add_argument("--task", default="dpm")

    return parser.parse_args()


def test():
    args = get_args()
    if args.task == "dpm":
        dpm(args)
    elif args.task == "conf":
        conf(args)


def conf(args):
    job_real = args.job[:].replace("-", "/")

    configuration = export_configuration(job_real)
    vEhc = export_enhancer_configuration(job_real)

    regularized_configuration = {}
    for k_name, v in configuration.items():
        new_v = v
        if new_v['cooltime'] == 99999999:
            new_v['cooltime'] = -1
        if 'static_character_modifier' in new_v:
            for modifier_k, modifier_v in new_v.items():
                if modifier_v != 0:
                    new_v[modifier_k] = modifier_v
            new_v.pop('static_character_modifier')

        if 'static_character_modifier' in new_v:
            new_v['type'] = 'BuffSkill'
        elif 'summondelay' in new_v:
            new_v['type'] = 'SummonSkill'
        else:
            new_v['type'] = 'DamageSkill'

        new_v.pop('explanation')

        if '_static_skill_modifier' in new_v:
            if '0' in new_v['_static_skill_modifier']:
                for k in new_v['_static_skill_modifier']:
                    pops = [k1 for k1, v in new_v['_static_skill_modifier'][k].items() if v == 0]
                    for k2 in pops:
                        new_v['_static_skill_modifier'][k].pop(k2)
            else:
                pops = [k1 for k1, v in new_v['_static_skill_modifier'].items() if v == 0]
                for k2 in pops:
                    new_v['_static_skill_modifier'].pop(k2)
        regularized_configuration[k_name] = v

    for idx, wrps in enumerate(vEhc.enhancer_priority):
        for wrp in wrps:
            skill_name = wrp.name

            static_modifier_pos = sorted(regularized_configuration[skill_name]["_static_skill_modifier"].keys())[-1]
            v_increment = regularized_configuration[skill_name]["_static_skill_modifier"][static_modifier_pos]['pdamage_indep'] // 60
            regularized_configuration[wrp.name]["enhanced_by_v"] = True
            regularized_configuration[wrp.name]["upgrade_priority"] = idx
            regularized_configuration[wrp.name]["v_increment"] = v_increment
            regularized_configuration[wrp.name]["v_crit"] = regularized_configuration[skill_name]["_static_skill_modifier"][static_modifier_pos].get("crit", False)

    for v_priority in vEhc.v_skill_priority:
        skill_name = v_priority['target'].name
        regularized_configuration[skill_name]['tier'] = 5
        regularized_configuration[skill_name]['use_priority'] = v_priority['useIdx']
        regularized_configuration[skill_name]['upgrade_priority'] = v_priority['upgIdx']

    for k_name in regularized_configuration:
        if '_static_skill_modifier' in regularized_configuration[k_name]:
            if "0" in regularized_configuration[k_name]['_static_skill_modifier']:
                regularized_configuration[k_name]['modifier'] = regularized_configuration[k_name]['_static_skill_modifier']["0"]
                regularized_configuration[k_name].pop('_static_skill_modifier')
            else:
                regularized_configuration[k_name]['modifier'] = regularized_configuration[k_name]['_static_skill_modifier']
                regularized_configuration[k_name].pop('_static_skill_modifier')

            if len(regularized_configuration[k_name]['modifier']) == 0:
                regularized_configuration[k_name].pop('modifier')
            
    with open(f"{args.job}.conf.json", "w", encoding="utf8") as f:
        json.dump(regularized_configuration, f, ensure_ascii=False, indent=4)


def dpm(args):
    parser = IndividualDPMGenerator(args.job)
    parser.set_runtime(args.time * 1000)
    try:
        dpm = parser.get_dpm(
            spec_name=str(args.ulevel),
            ulevel=args.ulevel,
            cdr=args.cdr,
            printFlag=args.log,
            statistics=args.stat or args.log,
        )
    finally:
        print(args.job, f"{dpm:,.3f}")


if __name__ == "__main__":
    test()
