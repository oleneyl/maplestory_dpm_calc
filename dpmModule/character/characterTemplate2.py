import json
import os
from copy import deepcopy
from typing import Union

from dpmModule.gear.Gear import Gear
from dpmModule.gear.GearBuilder import GearBuilder
from dpmModule.gear.GearPropType import GearPropType
from dpmModule.gear.Scroll import Scroll
from dpmModule.gear.GearType import GearType
from dpmModule.gear.SetItem import eval_set_item_effect
from dpmModule.kernel.core.modifier import ExtendedCharacterModifier
from dpmModule.character.characterKernel import GearedCharacter, JobGenerator
from dpmModule.jobs import job_branch_list

with open(os.path.join(os.path.dirname(__file__), 'configs', 'template.json'), encoding='utf8') as template_file:
    data = json.load(template_file)


def get_character_template(gen: JobGenerator, unionlevel: int, cdr: int = 0) -> GearedCharacter:
    """
    job: 한글 직업명
    unionlevel: 8000 | (8500)
    """
    # functions
    def _get_job_branch(jobname: str):
        return job_branch_list[jobname]

    def _get_id_from_name(name: Union[str, int], part: str):
        try:
            # name is int or int as str
            return int(name)
        except ValueError:
            # name is str
            if part == "weapon" or part == "subweapon" or part == "emblem":
                if name in _weapon_lookup:
                    if job in _weapon_lookup[name]:
                        return _weapon_lookup[name][job]
            else:
                if name in _armor_lookup:
                    if part in _armor_lookup[name]:
                        ids = _armor_lookup[name][part]
                        if len(ids) == 6:
                            return ids[_get_job_branch(job)]
                        else:
                            return ids[0]
            return Gear.get_id_from_name(name)

    def _get_set_effect(gears, node):
        # replace to mdf later.
        set_effect = Gear()
        set_effect.name = "세트효과 합계"
        set_effect.type = GearType._dummy
        weapon_id = gears["weapon"].item_id
        weapon_set_item_id = gears["weapon"].set_item_id
        if "weapon_lucky_item" in node:
            gears["weapon"].item_id = 1570000
            gears["weapon"].set_item_id = _weapon_lucky_item_lookup[node["weapon_lucky_item"]]
        set_effect.base_stat = eval_set_item_effect(list(gears.values()))
        gears["weapon"].item_id = weapon_id
        gears["weapon"].set_item_id = weapon_set_item_id
        return set_effect

    def _get_title(name: str):
        return Gear.create_title_from_name(name)

    def _get_pet_equip(att: int):
        pet: Gear = Gear()
        pet.name = "펫장비 (공격력=" + str(att) + ")"
        pet.type = GearType.pet_equip
        pet.base_stat[GearPropType.att] = att
        pet.base_stat[GearPropType.matt] = att
        return pet

    def _get_zero_subweapon(zero_weapon: Gear):
        _zero_data = Gear.create_from_id(_zero_weapon_lookup[zero_weapon.item_id])
        zero_sub = Gear()
        zero_sub.name = _zero_data.name
        zero_sub.type = _zero_data.type
        zero_sub.base_stat[GearPropType.STR] = 1
        zero_sub.base_stat[GearPropType.att] = 1
        zero_sub.base_stat[GearPropType.boss_pdamage] = zero_weapon.base_stat[GearPropType.boss_pdamage]
        zero_sub.base_stat[GearPropType.armor_ignore] = zero_weapon.base_stat[GearPropType.armor_ignore]
        zero_sub.base_stat[GearPropType.pdamage] = zero_weapon.base_stat[GearPropType.pdamage]
        zero_sub.additional_stat[GearPropType.boss_pdamage] = zero_weapon.additional_stat[GearPropType.boss_pdamage]
        zero_sub.additional_stat[GearPropType.armor_ignore] = zero_weapon.additional_stat[GearPropType.armor_ignore]
        zero_sub.additional_stat[GearPropType.pdamage] = zero_weapon.additional_stat[GearPropType.pdamage]
        zero_sub.additional_stat[GearPropType.STR_rate] = zero_weapon.additional_stat[GearPropType.STR_rate]
        zero_sub.additional_stat[GearPropType.DEX_rate] = zero_weapon.additional_stat[GearPropType.DEX_rate]
        zero_sub.additional_stat[GearPropType.INT_rate] = zero_weapon.additional_stat[GearPropType.INT_rate]
        zero_sub.additional_stat[GearPropType.LUK_rate] = zero_weapon.additional_stat[GearPropType.LUK_rate]
        zero_sub.additional_potential[GearPropType.STR_rate] = zero_weapon.additional_potential[GearPropType.STR_rate]
        zero_sub.additional_potential[GearPropType.DEX_rate] = zero_weapon.additional_potential[GearPropType.DEX_rate]
        zero_sub.additional_potential[GearPropType.att] = zero_weapon.additional_potential[GearPropType.att]
        zero_sub.additional_potential[GearPropType.crit_damage] = zero_weapon.additional_potential[GearPropType.crit_damage]
        zero_sub.additional_potential[GearPropType.att_rate] = zero_weapon.additional_potential[GearPropType.att_rate]
        return zero_sub

    def _get_enchanted_gear(part: str) -> Gear:
        def _get_fallback_part(part: str) -> str:
            _part = part.rstrip("0123456789")
            if _part in ("head", "top", "bottom", "shoes", "glove", "cape"):
                return "armor"
            if _part in ("shoulder", "face", "eye", "ear", "belt", "ring", "pendant", "heart", "pocket"):
                return "accessory"
            if _part in ("weapon", "subweapon", "blade", "emblem"):
                return "weapon"
            return ""  # badge, medal, title

        def _get_part_data(_node, part: str, fallback_part: str):
            if part in _node:
                return _node[part]
            elif fallback_part in _node:
                return _node[fallback_part]
            else:
                return None

        def _is_addition_gear(part: str) -> bool:
            _part = part.rstrip("0123456789")
            return _part in ("head", "top", "bottom", "shoes", "glove", "cape",
                             "face", "eye", "ear", "belt", "ring", "pendant", "pocket", "weapon")

        def _is_potential_gear(part: str) -> bool:
            _part = part.rstrip("0123456789")
            return _part in ("head", "top", "bottom", "shoes", "glove", "cape",
                             "shoulder", "face", "eye", "ear", "belt", "ring", "pendant", "heart")

        def _is_add_potential_gear(part: str) -> bool:
            _part = part.rstrip("0123456789")
            return _is_potential_gear(part) or _part in ("weapon", "subweapon", "emblem", "blade")

        def _apply_scroll(gear: Gear, scroll_data):
            scroll_type, scroll_value = scroll_data
            gb = GearBuilder(gear)
            if scroll_type == 0:
                gb.apply_spell_trace_scroll(scroll_value, main_type, gb.scroll_available)
            elif scroll_type == 1:
                gb.apply_scroll(Scroll.create_from_dict({att_type: scroll_value}))
                gb.apply_spell_trace_scroll(30, main_type, gb.scroll_available)
            elif scroll_type == 2:
                gb.apply_scroll(Scroll.create_from_dict({att_type: 2}), 3)
                gb.apply_spell_trace_scroll(30, main_type)
                gb.apply_scroll(Scroll.create_from_dict({att_type: 2}), gb.scroll_available)
            elif scroll_type == 10:
                scroll = Scroll.create_from_dict({att_type: scroll_value // 10, main_type: scroll_value % 10})
                gb.apply_scroll(scroll, gb.scroll_available)
            elif scroll_type == 20:
                scroll = Scroll.create_from_dict({
                    GearPropType.STR: 3, GearPropType.DEX: 3, GearPropType.INT: 3, GearPropType.LUK: 3,
                    att_type: scroll_value
                })
                gb.apply_scroll(scroll, gb.scroll_available)
            elif scroll_type == 100:
                scroll = Scroll.create_from_dict({
                    GearPropType.STR: 3, GearPropType.DEX: 3, GearPropType.INT: 3, GearPropType.LUK: 3,
                    GearPropType.MHP: 40, GearPropType.MMP: 40, GearPropType.PAD: 3, GearPropType.MAD: 3,
                })
                gb.apply_scroll(scroll, gb.scroll_available)
            elif scroll_type == 101:
                scroll = Scroll.create_from_dict({
                    GearPropType.STR: 10, GearPropType.DEX: 10, GearPropType.INT: 10, GearPropType.LUK: 10,
                    GearPropType.MHP: 1000, GearPropType.MMP: 1000, GearPropType.PAD: 5, GearPropType.MAD: 5,
                })
                gb.apply_scroll(scroll, gb.scroll_available)
            else:
                raise TypeError('Not implemented scroll type: ', scroll_type)

        if part == "subweapon" and gen.jobname == "제로":
            return Gear()
        if part == "subweapon" and gen.jobname == "듀얼블레이드":
            part = "blade"

        main_type, sub_type, sub_type2, att_type, att_rate_type = {
            "STR": (GearPropType.STR, GearPropType.DEX, None, GearPropType.att, GearPropType.att_rate),
            "DEX": (GearPropType.DEX, GearPropType.STR,  None, GearPropType.att, GearPropType.att_rate),
            "INT": (GearPropType.INT, GearPropType.LUK, None, GearPropType.matt, GearPropType.matt_rate),
            "LUK": (GearPropType.LUK, GearPropType.DEX, None, GearPropType.att, GearPropType.att_rate),
            "LUK2": (GearPropType.LUK, GearPropType.DEX, GearPropType.STR, GearPropType.att, GearPropType.att_rate),
            "HP": (GearPropType.MHP, GearPropType.STR, None, GearPropType.att, GearPropType.att_rate),
            "xenon": (GearPropType.LUK, GearPropType.DEX, GearPropType.STR, GearPropType.att, GearPropType.att_rate),
        }[gen.jobtype]
        ######
        gear_id = node["gear_id"][part][0]
        if gear_id == 0:
            gear_id = _get_id_from_name(node["gear_id"][part][1], part)
        if gear_id == 0:
            raise TypeError('Invalid gear_id:', node["gear_id"][part][0], node["gear_id"][part][1], part, job)
        ######
        gear: Gear = Gear.create_from_id(gear_id)
        gb: GearBuilder = GearBuilder(gear)
        fallback_part = _get_fallback_part(part)
        # 추가옵션
        if _is_addition_gear(part):
            addition_data = _get_part_data(node["addition"], part, fallback_part)
            if addition_data is not None:
                if part == "weapon":
                    gb.apply_additional_stat(att_type, addition_data[0])
                    gear.additional_stat[GearPropType.boss_pdamage] = addition_data[1]
                    gear.additional_stat[GearPropType.pdamage] = addition_data[2]
                    gb.apply_additional_stat(GearPropType.allstat, addition_data[3])
                else:
                    gear.additional_stat[main_type] = addition_data[0]
                    gear.additional_stat[sub_type] = addition_data[1]
                    if sub_type2 is not None:
                        gear.additional_stat[sub_type2] = addition_data[2]
                    gear.additional_stat[att_type] = addition_data[3]
                    gb.apply_additional_stat(GearPropType.allstat, addition_data[4])
        # 주문서
        scroll_data = _get_part_data(node["upgrade"], part, fallback_part)
        if gear.tuc > 0:
            if scroll_data is not None:
                # 황금 망치
                gb.apply_hammer()
                _apply_scroll(gear, scroll_data)
        # 스타포스
        star_data = _get_part_data(node["star"], part, fallback_part)
        if star_data is not None:
            if star_data > 0:
                gb.apply_stars(star_data)
            elif star_data < 0:
                gb.apply_stars(star_data // 2, True, False)
                gb.apply_stars(star_data - (star_data // 2), True, True)
        # 잠재능력
        if _is_potential_gear(part):
            potential_data = _get_part_data(node["potential"], part, fallback_part)
            if potential_data is not None:
                gear.potential[main_type] = potential_data[0]
                gear.potential[sub_type] = potential_data[1]
                gear.potential[GearPropType.crit_damage] = potential_data[2]
        # 에디셔널 잠재능력
        if _is_add_potential_gear(part):
            add_potential_data = _get_part_data(node["add_potential"], part, fallback_part)
            if add_potential_data is not None:
                gear.additional_potential[main_type] = add_potential_data[0]
                gear.additional_potential[sub_type] = add_potential_data[1]
                gear.additional_potential[att_type] = add_potential_data[2]
                gear.additional_potential[GearPropType.crit_damage] = add_potential_data[3]
                gear.additional_potential[att_rate_type] = add_potential_data[4]
        return gear
    # end functions

    if str(unionlevel) not in data:
        raise TypeError('Invalid unionlevel')
    union_node = data[str(unionlevel)]

    job = gen.jobname
    node = union_node["default"]
    if job in union_node:
        if union_node[job]["type"] == "full":
            node = union_node[job]
        elif union_node[job]["type"] == "override":
            node = deepcopy(union_node["default"])
            jobnode = union_node[job]
            for nodekey in jobnode:
                subnode = jobnode[nodekey]
                if type(subnode) is dict:
                    for subnodekey in subnode:
                        if type(subnode[subnodekey]) is dict:
                            raise TypeError('Something went wrong with template.json')
                        node[nodekey][subnodekey] = subnode[subnodekey]
                else:
                    node[nodekey] = subnode

    keys = [
        "head", "top", "bottom", "shoes", "glove", "cape", "shoulder",
        "face", "eye", "ear", "belt", "ring1", "ring2", "ring3", "ring4",
        "pendant1", "pendant2", "heart", "pocket", "weapon", "subweapon", "emblem",
        "badge", "medal",
    ]
    template = GearedCharacter(gen=gen, level=node["level"])
    # 아케인심볼 스탯
    # replace to _get_arcane_stat(arcane_force: int, gen: JobGenerator) -> ExMDF later.
    template.apply_modifiers([ExtendedCharacterModifier(stat_main_fixed=node["arcane_stat"] * 3 if job == "제논" else 1)])
    # 장비
    gear_list = {}
    for key in keys:
        gear_list[key] = _get_enchanted_gear(key)
    if job == "제로":
        gear_list["subweapon"] = _get_zero_subweapon(gear_list["weapon"])
    # 세트효과
    gear_list["set_effect"] = _get_set_effect(gear_list, node)
    # 칭호
    gear_list["title"] = _get_title(node["title"])
    # 펫 장비
    gear_list["pet"] = _get_pet_equip(node["pet"])
    template.set_gears(gear_list)

    return template


_armor_lookup = {
    # "여제": {},
    "마이스터": {
        "ear": [1032200],
        "ring": [1113055],
        "shoulder": [1152154]
    },
    "타일런트": {
        "shoes": [1072743, 1072744, 1072745, 1072746, 1072747, 1072747],
        "glove": [1082543, 1082544, 1082545, 1082546, 1082547, 1082547],
        "cape": [1102481, 1102482, 1102483, 1102484, 1102485, 1102485],
        "belt": [1132174, 1132175, 1132176, 1132177, 1132178, 1132178]
    },
    "카루타": {
        "head": [1003797, 1003798, 1003799, 1003800, 1003801, 1003801],
        "top": [1042254, 1042255, 1042256, 1042257, 1042258, 1042258],
        "bottom": [1062165, 1062166, 1062167, 1062168, 1062169, 1062169],
        "blade": [1342082],
    },
    "앱솔랩스": {
        "head": [1004422, 1004423, 1004424, 1004425, 1004426, 1004426],
        "shoes": [1073030, 1073032, 1073033, 1073034, 1073035, 1073035],
        "glove": [1082636, 1082637, 1082638, 1082639, 1082640, 1082640],
        "cape": [1102775, 1102794, 1102795, 1102796, 1102797, 1102797],
        "shoulder": [1152174, 1152176, 1152177, 1152178, 1152179, 1152179],
        "blade": [1342101]
    },
    "아케인셰이드": {
        "head": [1004808, 1004809, 1004810, 1004811, 1004812, 1004812],
        "shoes": [1073158, 1073159, 1073160, 1073161, 1073162, 1073162],
        "glove": [1082695, 1082696, 1082697, 1082698, 1082699, 1082699],
        "cape": [1102940, 1102941, 1102942, 1102943, 1102944, 1102944],
        "shoulder": [1152196, 1152197, 1152198, 1152199, 1152200, 1152200],
        "blade": [1342104]
    },
    "칠흑": {
        "face": [1012632],
        "eye": [1022278],
        "ear": [1032316],
        "belt": [1132308],
        "ring": [1113306],
        "pendant": [1122430],
        "pocket": [1162080, 1162081, 1162082, 1162083, 1162080, 1162082],
        "badge": [1182285],
        "heart": [1672076],
    },
    "130얼장": {
        "face": [1012406, 1012407, 1012408, 1012409, 1012410, 1012410],
    },
}

_weapon_lookup = {
    "카루타": {
        "아크메이지불/독": 1382208,
        "아크메이지썬/콜": 1382208,
        "비숍": 1382208,
        "히어로": 1412135,
        "팔라딘": 1422140,
        "신궁": 1462193,
        "윈드브레이커": 1452205,
        "소울마스터": 1402196,
        "루미너스": 1212063,
        "배틀메이지": 1382208,
        "메카닉": 1492179,
        "메르세데스": 1522094,
        "데몬어벤져": 1232057,
        "데몬슬레이어": 1312153,
        "다크나이트": 1432167,
        "와일드헌터": 1462193,
        "플레임위자드": 1382208,
        "섀도어": 1332225,
        "캐논슈터": 1532098,
        "미하일": 1302275,
        "듀얼블레이드": 1332225,
        "카이저": 1402196,
        "캡틴": 1492179,
        "엔젤릭버스터": 1222058,
        "팬텀": 1362090,
        "나이트로드": 1472214,
        "은월": 1482168,
        "바이퍼": 1482168,
        "나이트워커": 1472214,
        "스트라이커": 1482168,
        "에반": 1382208,
        "보우마스터": 1452205,
        "제로": 1572007,
        "키네시스": 1262016,
        "일리움": 1282015,
        "패스파인더": 1592018,
        "카데나": 1272015,
        "아크": 1482168,
        "블래스터": 1582016,
        "아란": 1442223,
        "아델": 1213016,
        "호영": 1292016,
        "제논": 1242060,
    },
    "앱솔랩스": {
        "아크메이지불/독": 1382259,
        "아크메이지썬/콜": 1382259,
        "비숍": 1382259,
        "히어로": 1412177,
        "팔라딘": 1422184,
        "신궁": 1462239,
        "윈드브레이커": 1452252,
        "소울마스터": 1402251,
        "루미너스": 1212115,
        "배틀메이지": 1382259,
        "메카닉": 1492231,
        "메르세데스": 1522138,
        "데몬어벤져": 1232109,
        "데몬슬레이어": 1312199,
        "다크나이트": 1432214,
        "와일드헌터": 1462239,
        "플레임위자드": 1382259,
        "섀도어": 1332274,
        "캐논슈터": 1532144,
        "미하일": 1302333,
        "듀얼블레이드": 1332274,
        "카이저": 1402251,
        "캡틴": 1492231,
        "엔젤릭버스터": 1222109,
        "팬텀": 1362135,
        "나이트로드": 1472261,
        "은월": 1482216,
        "바이퍼": 1482216,
        "나이트워커": 1472261,
        "스트라이커": 1482216,
        "에반": 1382259,
        "보우마스터": 1452252,
        "제로": 1572008,
        "키네시스": 1262017,
        "일리움": 1282016,
        "패스파인더": 1592019,
        "카데나": 1272016,
        "아크": 1482216,
        "블래스터": 1582017,
        "아란": 1442268,
        "아델": 1213017,
        "호영": 1292017,
        "제논": 1242120,
    },
    "아케인셰이드": {
        "아크메이지불/독": 1382265,
        "아크메이지썬/콜": 1382265,
        "비숍": 1382265,
        "히어로": 1412181,
        "팔라딘": 1422189,
        "신궁": 1462243,
        "윈드브레이커": 1452257,
        "소울마스터": 1402259,
        "루미너스": 1212120,
        "배틀메이지": 1382265,
        "메카닉": 1492235,
        "메르세데스": 1522143,
        "데몬어벤져": 1232113,
        "데몬슬레이어": 1312203,
        "다크나이트": 1432218,
        "와일드헌터": 1462243,
        "플레임위자드": 1382265,
        "섀도어": 1332279,
        "캐논슈터": 1532150,
        "미하일": 1302343,
        "듀얼블레이드": 1332279,
        "카이저": 1402259,
        "캡틴": 1492235,
        "엔젤릭버스터": 1222113,
        "팬텀": 1362140,
        "나이트로드": 1472265,
        "은월": 1482221,
        "바이퍼": 1482221,
        "나이트워커": 1472265,
        "스트라이커": 1482221,
        "에반": 1382265,
        "보우마스터": 1452257,
        "제로": 1572009,
        "키네시스": 1262039,
        "일리움": 1282017,
        "패스파인더": 1592020,
        "카데나": 1272017,
        "아크": 1482221,
        "블래스터": 1582023,
        "아란": 1442274,
        "아델": 1213018,
        "호영": 1292018,
        "제논": 1242122,
    },
    "제네시스": {
        "아크메이지불/독": 1382274,
        "아크메이지썬/콜": 1382274,
        "비숍": 1382274,
        "히어로": 1412189,
        "팔라딘": 1422197,
        "신궁": 1462252,
        "윈드브레이커": 1452266,
        "소울마스터": 1402268,
        "루미너스": 1212129,
        "배틀메이지": 1382274,
        "메카닉": 1492245,
        "메르세데스": 1522152,
        "데몬어벤져": 1232122,
        "데몬슬레이어": 1312213,
        "다크나이트": 1432227,
        "와일드헌터": 1462252,
        "플레임위자드": 1382274,
        "섀도어": 1332289,
        "캐논슈터": 1532157,
        "미하일": 1302355,
        "듀얼블레이드": 1332289,
        "카이저": 1402268,
        "캡틴": 1492245,
        "엔젤릭버스터": 1222122,
        "팬텀": 1362149,
        "나이트로드": 1472275,
        "은월": 1482232,
        "바이퍼": 1482232,
        "나이트워커": 1472275,
        "스트라이커": 1482232,
        "에반": 1382274,
        "보우마스터": 1452266,
        "제로": 1572010,
        "키네시스": 1262051,
        "일리움": 1282040,
        "패스파인더": 1592022,
        "카데나": 1272040,
        "아크": 1482232,
        "블래스터": 1582044,
        "아란": 1442285,
        "아델": 1213022,
        "호영": 1292022,
        "제논": 1242141,
    },
    "보조무기": {
        "아크메이지불/독": 1352232,
        "아크메이지썬/콜": 1352242,
        "비숍": 1352252,
        "히어로": 1352202,
        "팔라딘": 1352212,
        "신궁": 1352272,
        "윈드브레이커": 1352972,
        "소울마스터": 1352972,
        "루미너스": 1352403,
        "배틀메이지": 1352952,
        "메카닉": 1352703,
        "메르세데스": 1352003,
        "데몬어벤져": 1099009,  # 성장으로 STR 9, HP 200, 방어력 20 상승
        "데몬슬레이어": 1099004,  # 성장으로 STR 9, DEX 9, HP 200, 방어력 20 상승
        "다크나이트": 1352222,
        "와일드헌터": 1352962,
        "플레임위자드": 1352972,
        "섀도어": 1352282,
        "캐논슈터": 1352922,
        "미하일": 1098003,  # 성장으로 STR 9, DEX 9, HP 200, 방어력 20 상승
        "듀얼블레이드": 0,
        "카이저": 1352503,
        "캡틴": 1352912,
        "엔젤릭버스터": 1352604,
        "팬텀": 1352103,
        "나이트로드": 1352292,
        "은월": 1353103,
        "바이퍼": 1352902,
        "나이트워커": 1352972,
        "스트라이커": 1352972,
        "에반": 1352942,
        "보우마스터": 1352262,
        "제로": 0,
        "키네시스": 1353203,
        "일리움": 1353503,
        "패스파인더": 1353703,
        "카데나": 1353303,
        "아크": 1353603,
        "블래스터": 1353403,
        "아란": 1352932,
        "아델": 1354003,
        "호영": 1353803,
        "제논": 1353004,
    },
    "엠블렘": {
        "아크메이지불/독": 1190301,
        "아크메이지썬/콜": 1190301,
        "비숍": 1190301,
        "히어로": 1190301,
        "팔라딘": 1190301,
        "신궁": 1190301,
        "윈드브레이커": 1190801,
        "소울마스터": 1190801,
        "루미너스": 1190517,
        "배틀메이지": 1190601,
        "메카닉": 1190601,
        "메르세데스": 1190511,
        "데몬어벤져": 1190701,
        "데몬슬레이어": 1190701,
        "다크나이트": 1190301,
        "와일드헌터": 1190601,
        "플레임위자드": 1190801,
        "섀도어": 1190301,
        "캐논슈터": 1190301,
        "미하일": 1190801,
        "듀얼블레이드": 1190301,
        "카이저": 1190001,
        "캡틴": 1190301,
        "엔젤릭버스터": 1190100,
        "팬텀": 1190515,
        "나이트로드": 1190301,
        "은월": 1190521,
        "바이퍼": 1190301,
        "나이트워커": 1190801,
        "스트라이커": 1190801,
        "에반": 1190519,
        "보우마스터": 1190301,
        "제로": 1190900,
        "키네시스": 1191001,
        "일리움": 1190532,
        "패스파인더": 1190301,
        "카데나": 1190530,
        "아크": 1190540,
        "블래스터": 1190601,
        "아란": 1190513,
        "아델": 1190552,
        "호영": 1190550,
        "제논": 1190201,
    }
}

_zero_weapon_lookup = {
    1572001: 1562001,
    1572002: 1562002,
    1572003: 1562003,
    1572004: 1562004,
    1572005: 1562005,
    1572006: 1562006,
    1572007: 1562007,
    1572008: 1562008,
    1572009: 1562009,
    1572010: 1562010,
}

_weapon_lucky_item_lookup = {
    "카루타": 247,
    "앱솔랩스": 504,
    "아케인셰이드": 617,
}