import json
import os
from copy import copy, deepcopy
from typing import Optional, Tuple, Union

from dpmModule.gear.Gear import Gear
from dpmModule.gear.GearBuilder import GearBuilder
from dpmModule.gear.GearPropType import GearPropType
from dpmModule.gear.Scroll import Scroll
from dpmModule.gear.GearType import GearType
from dpmModule.gear.SetItem import eval_set_item_effect
from dpmModule.kernel.core.modifier import ExtendedCharacterModifier
from dpmModule.character.characterKernel import GearedCharacter, JobGenerator
from dpmModule.jobs import job_branch_list

ExMDF = ExtendedCharacterModifier

# TODO: 보조무기 성장치 반영
# "데몬슬레이어": 1099004,  # 성장으로 STR 9, DEX 9, HP 200, 방어력 20 상승
# "데몬어벤져": 1099009,  # 성장으로 STR 9, HP 200, 방어력 20 상승
# "미하일": 1098003,  # 성장으로 STR 9, DEX 9, HP 200, 방어력 20 상승

# load template.json to 'data'
data = {}


def open_json(*paths) -> dict:
    with open(os.path.join(os.path.dirname(__file__), *paths), encoding='utf8') as _file:
        return json.load(_file)


_template_json = open_json('configs', 'template.json')
for key in _template_json:
    data[key] = open_json('configs', _template_json[key])


parts = ("head", "top", "bottom", "shoes", "glove", "cape", "shoulder", "face", "eye", "ear", "belt",
         "ring1", "ring2", "ring3", "ring4", "pendant1", "pendant2",
         "pocket", "badge", "medal", "weapon", "subweapon", "emblem", "heart")


def get_character_template(gen: JobGenerator, ulevel: int, cdr: int = 0) -> GearedCharacter:
    node = _get_template_dict(ulevel, gen.jobname)
    # Create GearedCharacter with level
    template = GearedCharacter(gen=gen, level=node['level'])
    # Apply arcane, authentic, pet, cash modifiers
    template.apply_modifiers([
        _get_arcane_modifier(node, gen.jobtype),
        _get_authentic_modifier(node, gen.jobtype),
        _get_pet_modifier(node),
        _get_cash_modifier(node),
        _get_job_specific_item_modifier(node),
    ])
    # Equip title
    template.title = _get_title(node)
    template.add_gear_modifier(template.title)
    # Equip gears
    gear_list = {}
    for part in parts:
        gear_list[part] = _get_enchanted_gear(part, node, gen, cdr)
    # Set zero subweapon
    if gen.jobname == "제로":
        gear_list["subweapon"] = _get_zero_subweapon(gear_list["weapon"])
    # Get set item effects
    gear_list["set_effect"] = _get_set_effect(gear_list, node)
    # Apply gear, set item effect to character mdf
    template.set_gears(gear_list)
    return template


def _get_template_dict(ulevel: int, jobname: str) -> dict:
    ulevel = str(ulevel)
    if ulevel not in data:
        raise ValueError('Invalid ulevel: ', ulevel)
    # Get job specific copy of node
    node: dict = deepcopy(data[ulevel]['default'])
    if jobname in data[ulevel]:
        if data[ulevel][jobname]['type'] == "full":
            node = deepcopy(data[ulevel][jobname])
        elif data[ulevel][jobname]['type'] == "override":
            for node_key in data[ulevel][jobname]:
                node[node_key] = deepcopy(data[ulevel][jobname][node_key])
    # Assert node contains all necessary parts
    assert("level" in node and set(parts) <= node.keys())
    # Apply wildcard options (armor, acc)
    if "armor" in node:
        for part in ("head", "top", "bottom", "shoes", "glove", "cape"):
            for option in node["armor"]:
                if option not in node[part]:
                    node[part][option] = node["armor"][option]
        del node["armor"]
    if "acc" in node:
        for part in ("shoulder", "face", "eye", "ear", "belt", "ring1", "ring2", "ring3", "ring4",
                     "pendant1", "pendant2", "pocket", "badge", "medal"):
            for option in node["acc"]:
                if option not in node[part]:
                    node[part][option] = node["acc"][option]
        del node["acc"]
    return node


def _get_arcane_modifier(node, jobtype: str):
    if "arcane_symbol_force" not in node:
        return ExMDF()
    value = node["arcane_symbol_force"] // 10
    if jobtype in ("STR", "DEX", "INT", "LUK", "LUK2"):
        return ExMDF(stat_main_fixed=value * 100)
    elif jobtype == "HP":
        return ExMDF(stat_main_fixed=value * 1750)
    elif jobtype == "xenon":
        # TODO: 제논 아케인심볼 힘덱럭 적용
        # return ExMDF(stat_main_fixed=value * 39, stat_sub_fixed=value * 39)
        return ExMDF(stat_main_fixed=value * 39 * 3)


def _get_authentic_modifier(node, jobtype: str):
    if "authentic_symbol_level" not in node:
        return ExMDF()
    value = sum([(2 * n + 3) for n in node["authentic_symbol_level"]])
    if jobtype in ("STR", "DEX", "INT", "LUK", "LUK2"):
        return ExMDF(stat_main_fixed=value * 100)
    elif jobtype == "HP":
        return ExMDF(stat_main_fixed=value * 1750)
    elif jobtype == "xenon":
        # TODO: 제논 어센틱심볼 힘덱럭 적용
        # return ExMDF(stat_main_fixed=value * 39, stat_sub_fixed=value * 39 * 2)
        return ExMDF(stat_main_fixed=value * 39 * 3)


def _get_pet_modifier(node):
    mdf = ExMDF()
    if "pet_equip" in node:
        mdf.att += node["pet_equip"]
    if "pet_set" in node:
        mdf.att += node["pet_set"]
    return mdf


def _get_cash_modifier(node):
    if "cash" not in node:
        return ExMDF()
    mdf = ExMDF()
    for stat_key in node["cash"]:
        setattr(mdf, stat_key, node["cash"][stat_key])
    return mdf


def _get_job_specific_item_modifier(node):
    if "job_specific_item" not in node:
        return ExMDF()
    mdf = ExMDF()
    for stat_key in node["job_specific_item"]:
        setattr(mdf, stat_key, node["job_specific_item"][stat_key])
    return mdf


def _get_title(node):
    if "title" not in node:
        raise TypeError('template does not contain title.')
    return Gear.create_title_from_name(node["title"]['id'])


def _get_enchanted_gear(part: str, node, gen: JobGenerator, cdr: int):
    return _apply_gear_options(_get_gear_base(node[part]['id'], part, gen.jobname), node[part], gen.jobtype, cdr)


def _get_gear_base(name: Union[int, str], part: str, jobname: str) -> Gear:
    def _get_job_branch(jobname: str) -> int:
        return job_branch_list[jobname]

    def _get_gear_id(name: str, part: str, jobname: str) -> int:
        part = part.rstrip('0123456789')
        preset_node = data['preset']
        if part in ("weapon", "subweapon", "emblem"):
            if name in preset_node[part]:
                if jobname in preset_node[part][name]:
                    return preset_node[part][name][jobname]
        else:
            if name in preset_node['default']:
                if part in preset_node['default'][name]:
                    id_list = preset_node['default'][name][part]
                    if len(id_list) == 6:
                        return id_list[_get_job_branch(jobname)]
                    else:
                        return id_list[0]
        return Gear.get_id_from_name(name)

    debug_name = str(name)
    if type(name) == str:
        name = _get_gear_id(name, part, jobname)
    if name <= 0:
        raise ValueError('Invalid gear name: ' + debug_name + ' (part: ' + part + ', jobname: ' + jobname + ')')
    return Gear.create_from_id(name)


def _apply_gear_options(gear: Gear, gear_node, jobtype: str, cdr):
    def _apply_bonus(bonus_node):
        for bonus_type in bonus_node:
            if bonus_type == "att_grade":
                gb.apply_additional_stat(att, bonus_node[bonus_type])
            elif bonus_type == "all_stat_rate":
                gb.apply_additional_stat(GearPropType.allstat, bonus_node[bonus_type])
            else:
                gear.additional_stat[stat_type[bonus_type]] = bonus_node[bonus_type]

    def _apply_upgrade(upgrade_node):
        gb.apply_hammer()
        for scroll in upgrade_node:
            type = scroll['type']
            count = scroll['count']
            if count < 0:
                count = gb.scroll_available
            if type == "주문의 흔적" or type == "주흔":
                prob = scroll['prob']
                stat = stat_type[scroll['stat']]
                gb.apply_spell_trace_scroll(prob, stat, count)
            elif type == "방공" or type == "악공":
                gb.apply_scroll(Scroll.create_from_dict({att: scroll['value']}), count)
            elif type == "매지컬":
                value = scroll['value']
                gb.apply_scroll(Scroll.create_from_dict({
                    GearPropType.STR: 3, GearPropType.DEX: 3, GearPropType.INT: 3, GearPropType.LUK: 3, att: value
                }), count)
            elif type == "파편":
                gb.apply_scroll(Scroll.create_from_dict({
                    GearPropType.STR: 3, GearPropType.DEX: 3, GearPropType.INT: 3, GearPropType.LUK: 3,
                    GearPropType.MHP: 40, GearPropType.att: 3, GearPropType.matt: 3
                }), count)
            elif type == "혼돈의 주문서" or "혼줌":
                stat = {}
                for stat_key in scroll['option']:
                    stat[stat_type[stat_key]] = scroll['option'][stat_key]
                gb.apply_scroll(Scroll.create_from_dict(stat), count)
            else:
                raise TypeError('Invalid upgrade type: ', type)

    def _apply_star(gear_node):
        star = gear_node['star']
        if star > 0:
            gb.apply_stars(star)
        elif star < 0:
            bonus = 0
            if 'surprise_bonus' in gear_node:
                bonus = gear_node['surprise_bonus']
            bonus_count = star * bonus // 100
            gb.apply_stars(star - bonus_count, True, False)
            gb.apply_stars(bonus_count, True, True)

    def _apply_potential(potential_node, gear_potential_dict):
        gear_potential_dict.clear()
        for stat_key in potential_node:
            if stat_key == "all_stat_rate":
                gear_potential_dict[pstat_main] += potential_node[stat_key]
                gear_potential_dict[pstat_sub] += potential_node[stat_key]
                gear_potential_dict[pstat_sub2] += potential_node[stat_key]
            gear_potential_dict[stat_type[stat_key]] += potential_node[stat_key]

    stat_main, pstat_main, stat_sub, pstat_sub, stat_sub2, pstat_sub2, att, patt = _get_stat_type(jobtype)
    stat_type = {
        "stat_main": stat_main, "pstat_main": pstat_main,
        "stat_sub": stat_sub, "pstat_sub": pstat_sub,
        "stat_sub2": stat_sub2, "pstat_sub2": pstat_sub2,
        "att": att, "patt": patt,
        "pdamage": GearPropType.pdamage,
        "boss_pdamage": GearPropType.boss_pdamage,
        "armor_ignore": GearPropType.armor_ignore,
        "crit": GearPropType.crit,
        "crit_damage": GearPropType.crit_damage,
        "cooltime_reduce": GearPropType.cooltime_reduce,
        "pdamage_indep": GearPropType.pdamage_indep,
    }
    gb = GearBuilder(gear)
    # 추가옵션
    if 'bonus' in gear_node:
        _apply_bonus(gear_node['bonus'])
    # 주문서 강화
    if 'upgrade' in gear_node and gear.tuc > 0:
        _apply_upgrade(gear_node['upgrade'])
    # 스타포스 강화
    if 'star' in gear_node:
        _apply_star(gear_node)
    # 잠재능력
    if 'potential' in gear_node:
        _apply_potential(gear_node['potential'], gear.potential)
    # 에디셔널 잠재능력
    if 'add_potential' in gear_node:
        _apply_potential(gear_node['add_potential'], gear.additional_potential)
    # 모자 쿨타임 감소 옵션
    if gear.type == GearType.cap and cdr > 0:
        if "cdr" not in gear_node or str(cdr) not in gear_node["cdr"]:
            raise ValueError('template does not contain cdr information for cdr input: ' + str(cdr))
        cdr_node = gear_node["cdr"][str(cdr)]
        if 'potential' in cdr_node:
            _apply_potential(cdr_node['potential'], gear.potential)
        if 'add_potential' in cdr_node:
            _apply_potential(cdr_node['add_potential'], gear.additional_potential)
    return gear


def _get_zero_subweapon(zero_weapon: Gear):
    assert (zero_weapon.type == GearType.sword_zl)
    subweapon_id = zero_weapon.item_id - 10000
    subweapon = Gear.create_from_id(subweapon_id)
    shared_types = (GearPropType.boss_pdamage, GearPropType.armor_ignore, GearPropType.pdamage,
                    GearPropType.STR_rate, GearPropType.DEX_rate, GearPropType.INT_rate, GearPropType.LUK_rate)
    for stat_type in shared_types:
        subweapon.additional_stat[stat_type] = zero_weapon.additional_stat[stat_type]
    subweapon.potential = copy(zero_weapon.potential)
    subweapon.additional_potential = copy(zero_weapon.additional_potential)
    return subweapon


def _get_set_effect(gears, node):
    def _get_zero_weapon_set_id(name: str):
        try:
            return data['preset']["zero_weapon_set_id"][name]
        except KeyError:
            return 0

    # TODO: Replace gear => ExMDF
    set_effect = Gear()
    set_effect.name = "세트효과 합계"
    set_effect.type = GearType._dummy
    # Zero set item id effect
    weapon_id = gears["weapon"].item_id
    weapon_set_item_id = gears["weapon"].set_item_id
    if gears["weapon"].type == GearType.sword_zl and "zero_weapon_set_name" in node:
        gears["weapon"].item_id = 1570000
        gears["weapon"].set_item_id = _get_zero_weapon_set_id(node["zero_weapon_set_name"])
    set_effect.base_stat = eval_set_item_effect(gears.values())
    # Revert zero set item id
    gears["weapon"].item_id = weapon_id
    gears["weapon"].set_item_id = weapon_set_item_id
    return set_effect


def _get_stat_type(jobtype: str) -> Tuple[
        GearPropType, GearPropType,
        GearPropType, GearPropType,
        Optional[GearPropType], Optional[GearPropType],
        GearPropType, GearPropType]:
    # stat_main, pstat_main, stat_sub, pstat_sub, stat_sub2, pstat_sub2, att, patt
    return {
        "STR": (
            GearPropType.STR, GearPropType.STR_rate,
            GearPropType.DEX, GearPropType.DEX_rate,
            None, None,
            GearPropType.att, GearPropType.att_rate
        ),
        "DEX": (
            GearPropType.DEX, GearPropType.DEX_rate,
            GearPropType.STR, GearPropType.STR_rate,
            None, None,
            GearPropType.att, GearPropType.att_rate
        ),
        "INT": (
            GearPropType.INT, GearPropType.INT_rate,
            GearPropType.LUK, GearPropType.LUK_rate,
            None, None,
            GearPropType.matt, GearPropType.matt_rate
        ),
        "LUK": (
            GearPropType.LUK, GearPropType.LUK_rate,
            GearPropType.DEX, GearPropType.DEX_rate,
            None, None,
            GearPropType.att, GearPropType.att_rate
        ),
        "LUK2": (
            GearPropType.LUK, GearPropType.LUK_rate,
            GearPropType.DEX, GearPropType.DEX_rate,
            GearPropType.STR, GearPropType.STR_rate,
            GearPropType.att, GearPropType.att_rate
        ),
        "HP": (
            GearPropType.MHP, GearPropType.MHP_rate,
            GearPropType.STR, GearPropType.STR_rate,
            None, None,
            GearPropType.att, GearPropType.att_rate
        ),
        "xenon": (
            GearPropType.LUK, GearPropType.LUK_rate,
            GearPropType.DEX, GearPropType.DEX_rate,
            GearPropType.STR, GearPropType.STR_rate,
            GearPropType.att, GearPropType.att_rate
        ),
    }[jobtype]
