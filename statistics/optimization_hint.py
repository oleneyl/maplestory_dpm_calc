import argparse

import pandas as pd
from dpmModule.character.characterKernel import GearedCharacter, JobGenerator
from dpmModule.character.characterTemplate import TemplateGenerator
from dpmModule.jobs import jobMap, weaponList
from dpmModule.kernel import core
from dpmModule.status.ability import Ability_grade

from .loader import load_data
from .preset import get_preset
from .saver import save_data


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
    graph = gen.package(
        target,
        v_builder,
        options=preset.options,
        ulevel=args.ulevel,
        weaponstat=weapon_stat,
        ability_grade=Ability_grade(4, 1),
    )
    return graph.get_default_buff_modifier()


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
    grouped = df.groupby(["name"])

    df = pd.DataFrame()
    df["share"] = grouped["deal"].sum() / deal_total
    df["crit_damage"] = grouped["crit_damage"].mean()
    df["pdamage"] = grouped["pdamage"].mean()
    df["boss_pdamage"] = grouped["boss_pdamage"].mean()
    df["armor_ignore"] = grouped["armor_ignore"].mean()
    df["patt"] = grouped["patt"].mean()

    print(df)

    crit_damage = (df["crit_damage"] * df["share"]).sum()
    pdamage = (df["pdamage"] * df["share"]).sum()
    boss_pdamage = (df["boss_pdamage"] * df["share"]).sum()
    armor_ignore = (df["armor_ignore"] * df["share"]).sum()
    patt = (df["patt"] * df["share"]).sum()

    print(
        {
            "crit_damage": crit_damage - buff_modifier.crit_damage,
            "pdamage": pdamage - buff_modifier.pdamage,
            "boss_pdamage": boss_pdamage - buff_modifier.boss_pdamage,
            "armor_ignore": armor_float_to_percent(
                armor_percent_to_float(armor_ignore)
                / armor_percent_to_float(buff_modifier.armor_ignore)
                / armor_percent_to_float(20)
            ),
            "patt": patt - buff_modifier.patt,
        }
    )


if __name__ == "__main__":
    args = get_args()
    if args.calc:
        data = save_data(args)
    else:
        data = load_data(args)
    optimization_hint(args, data)
