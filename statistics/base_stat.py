import argparse

import pandas as pd
from dpmModule.character.characterKernel import JobGenerator
from dpmModule.character.characterTemplate import TemplateGenerator
from dpmModule.jobs import jobMap
from dpmModule.kernel import core
from dpmModule.status.ability import Ability_grade

from .loader import load_data
from .saver import save_data
from .preset import get_preset, get_preset_list


def get_args():
    parser = argparse.ArgumentParser("Optimization hint argument")
    parser.add_argument(
        "--id", type=str, help="Target preset id to calculate statistics"
    )
    parser.add_argument("--ulevel", type=int, default=8000)
    parser.add_argument("--cdr", type=int, default=0)
    parser.add_argument("--time", type=int, default=1800)
    parser.add_argument("--task", default="dpm")
    parser.add_argument("--calc", action="store_true")
    parser.add_argument("--all", action="store_true")

    return parser.parse_args()


def armor_percent_to_float(num: float):
    return (100 - num) / 100


def armor_float_to_percent(num: float):
    return 100 - num * 100


def get_modifier(args) -> core.CharacterModifier:
    preset = get_preset(args.id)
    gen: JobGenerator = jobMap[preset.job].JobGenerator()
    target, weapon_stat = TemplateGenerator().get_template_and_weapon_stat(gen, str(args.ulevel), args.cdr)
    v_builder = core.AlwaysMaximumVBuilder()
    gen.package(
        target,
        v_builder,
        options=preset.options,
        ulevel=args.ulevel,
        weaponstat=weapon_stat,
        ability_grade=Ability_grade(4, 1),
        farm=False,
    )
    return gen.get_passive_skill_modifier()


def optimization_hint(args, df: pd.DataFrame):
    buff_modifier = get_modifier(args)

    df = df[["name", "deal", "mdf"]]
    df = df.loc[df["deal"] > 0]
    deal_total = df["deal"].sum()

    df["crit_damage"] = df["mdf"].apply(lambda x: x["crit_damage"])
    df["pdamage"] = df["mdf"].apply(lambda x: x["pdamage"])
    df["boss_pdamage"] = df["mdf"].apply(lambda x: x["boss_pdamage"])
    df["armor_ignore"] = df["mdf"].apply(lambda x: x["armor_ignore"])
    df["patt"] = df["mdf"].apply(lambda x: x["patt"])
    df["att"] = df["mdf"].apply(lambda x: x["att"])
    df["stat_main"] = df["mdf"].apply(lambda x: x["stat_main"])
    grouped = df.groupby(["name"])

    df = pd.DataFrame()
    df["share"] = grouped["deal"].sum() / deal_total
    df["crit_damage"] = grouped["crit_damage"].mean()
    df["pdamage"] = grouped["pdamage"].mean()
    df["boss_pdamage"] = grouped["boss_pdamage"].mean()
    df["armor_ignore"] = grouped["armor_ignore"].mean()
    df["patt"] = grouped["patt"].mean()
    df["att"] = grouped["att"].mean()
    df["stat_main"] = grouped["stat_main"].mean()

    # print(df)

    crit_damage = (df["crit_damage"] * df["share"]).sum()
    pdamage = (df["pdamage"] * df["share"]).sum()
    boss_pdamage = (df["boss_pdamage"] * df["share"]).sum()
    armor_ignore = (df["armor_ignore"] * df["share"]).sum()
    patt = (df["patt"] * df["share"]).sum()
    att = (df["att"] * df["share"]).sum()
    stat_main = (df["stat_main"] * df["share"]).sum()

    print(
        args.id,
        get_preset(args.id).job,
        crit_damage + buff_modifier.crit_damage,
        pdamage + boss_pdamage + buff_modifier.pdamage + buff_modifier.boss_pdamage,
        armor_float_to_percent(armor_percent_to_float(armor_ignore) * armor_percent_to_float(buff_modifier.armor_ignore)),
        patt + buff_modifier.patt,
        att + buff_modifier.att,
        stat_main + buff_modifier.stat_main,
    )


if __name__ == "__main__":
    args = get_args()
    if args.all:
        presets = get_preset_list()
        tasks = [
            argparse.Namespace(
                id=id, ulevel=args.ulevel, cdr=args.cdr, time=args.time, task=args.task
            )
            for id, *_ in presets
        ]
        for task in tasks:
            data = load_data(task)
            optimization_hint(task, data)
    else:
        if args.calc:
            data = save_data(args)
            optimization_hint(args, data)
        else:
            data = load_data(args)
            optimization_hint(args, data)
