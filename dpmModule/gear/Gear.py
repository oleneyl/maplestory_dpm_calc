import json
import os
from collections import defaultdict
from typing import DefaultDict

from dpmModule.kernel.core import ExtendedCharacterModifier
from .GearPropType import GearPropType
from .GearType import GearType

PropMap = DefaultDict[GearPropType, int]

with open(os.path.join(os.path.dirname(__file__), 'resources', 'geardata.json'), encoding='utf8') as gear_file:
    gear_data = json.load(gear_file)
with open(os.path.join(os.path.dirname(__file__), 'resources', 'titledata.json'), encoding='utf8') as title_file:
    title_data = json.load(title_file)


class Gear:
    __slots__ = (
        "item_id", "name", "type", "req_level", "req_job", "set_item_id", "boss_reward",
        "superior_eqp", "joker_to_set_item", "amazing_scroll", "star", "max_star",
        "tuc", "scroll_up", "scroll_fail", "hammer", "block_hammer",
        "base_stat", "additional_stat", "scroll_stat", "star_stat", "potential", "additional_potential")

    def __init__(self):
        self.item_id: int = 0
        self.name: str = "Default name!"
        self.type: GearType = GearType._dummy

        self.req_level: int = 0
        self.req_job: int = 0
        self.set_item_id: int = 0
        self.boss_reward: bool = False

        self.superior_eqp: bool = False
        self.joker_to_set_item: bool = False

        self.amazing_scroll: bool = False
        self.star: int = 0
        self.max_star: int = 0

        self.tuc: int = 0
        self.scroll_up: int = 0
        self.scroll_fail: int = 0
        self.hammer: int = 0
        self.block_hammer: bool = False

        self.base_stat: PropMap = defaultdict(int)
        self.additional_stat: PropMap = defaultdict(int)
        self.scroll_stat: PropMap = defaultdict(int)
        self.star_stat: PropMap = defaultdict(int)
        self.potential: PropMap = defaultdict(int)
        self.additional_potential: PropMap = defaultdict(int)

    def __str__(self):
        # for debug
        stat_str = ""
        stats = {}
        for propType in self.base_stat:
            stats.setdefault(propType, [0, 0, 0, 0])
            stats[propType][0] = self.base_stat[propType]
        for propType in self.additional_stat:
            stats.setdefault(propType, [0, 0, 0, 0])
            stats[propType][1] = self.additional_stat[propType]
        for propType in self.scroll_stat:
            stats.setdefault(propType, [0, 0, 0, 0])
            stats[propType][2] = self.scroll_stat[propType]
        for propType in self.star_stat:
            stats.setdefault(propType, [0, 0, 0, 0])
            stats[propType][3] = self.star_stat[propType]
        keys = sorted(stats)
        for propType in keys:
            stat_str += "%s: %d (%d +%d +%d +%d)\n" % (propType.name, sum(stats[propType]),
                                                       stats[propType][0], stats[propType][1],
                                                       stats[propType][2], stats[propType][3])
        return ("= ID: " + str(self.item_id) + '\n' +
                "= 이름: " + self.name + '\n' +
                "= 분류: " + self.type.name + '\n' +
                ("놀장" if self.amazing_scroll else "스타포스") + ": " +
                str(self.star) + '/' + str(self.max_star) + '\n' +
                "= 최대 업횟: " + str(self.tuc) +
                " (황금 망치: +" + str(self.hammer) + ')\n' +
                "= 업그레이드 성공 횟수: " + str(self.scroll_up) + '\n' +
                "= 업그레이드 실패 횟수: " + str(self.scroll_fail) + '\n' +
                "= 옵션: 합계 (기본 +추옵 +주문서 +별)\n" + stat_str +
                "= 잠재능력: \n" + str(self.potential) +
                "= 에디셔널 잠재능력: \n" + str(self.additional_potential))

    def get_max_star(self) -> int:
        """
        Returns the number of gear's max star.
        :return: The number of gear's max star.
        """
        if self.tuc <= 0:
            return 0
        if self.is_mechanic_gear(self.type) or self.is_dragon_gear(self.type):
            return 0
        star_data = [
            [0, 5, 3],
            [95, 8, 5],
            [110, 10, 8],
            [120, 15, 10],
            [130, 20, 12],
            [140, 25, 15],
        ]
        data = None
        for item in star_data:
            if self.req_level >= item[0]:
                data = item
            else:
                break
        if data is None:
            return 0
        return data[2 if self.superior_eqp else 1]

    def get_stat_map(self) -> PropMap:
        """
        Returns summed up stats of gear.
        :return: Summed up stats of gear.
        """
        stats = (
            self.base_stat,
            self.additional_stat,
            self.scroll_stat,
            self.star_stat,
            self.potential,
            self.additional_potential
        )
        stat_map = defaultdict(int)
        for _stat_map in stats:
            for key in _stat_map:
                stat_map[key] += _stat_map[key]
        return stat_map

    def get_modifier(self, jobtype: str) -> ExtendedCharacterModifier:
        """
        (temporary)
        :param jobtype: Target jobtype.
        :return: This gear's stat_map converted to ExMDF.
        """
        from dpmModule.character.characterTemplate import _get_stat_type
        stat_main, pstat_main, stat_sub, pstat_sub, stat_sub2, pstat_sub2, att, patt = _get_stat_type(jobtype)
        stat_map = self.get_stat_map()
        mdf = ExtendedCharacterModifier()
        if jobtype == "HP":
            mdf.stat_main += stat_map[stat_main] / 2
            mdf.stat_sub += stat_map[stat_sub]
            mdf.pstat_main += stat_map[pstat_main]
            mdf.pstat_sub += stat_map[pstat_sub]
        elif jobtype == "xenon":
            mdf.stat_main += stat_map[stat_main] + stat_map[stat_sub] + stat_map[stat_sub2]
            mdf.pstat_main += stat_map[pstat_main]
        else:
            mdf.stat_main += stat_map[stat_main]
            mdf.stat_sub += stat_map[stat_sub]
            mdf.pstat_main += stat_map[pstat_main]
            mdf.pstat_sub += stat_map[pstat_sub]
            if stat_sub2 is not None:
                mdf.stat_sub += stat_map[stat_sub2]
        mdf.att += stat_map[att]
        mdf.patt += stat_map[patt]
        mdf.pdamage += stat_map[GearPropType.pdamage]
        mdf.boss_pdamage += stat_map[GearPropType.boss_pdamage]
        mdf.armor_ignore = 100 - 0.01 * (100 - mdf.armor_ignore) * (100 - stat_map[GearPropType.armor_ignore])
        mdf.crit += stat_map[GearPropType.crit]
        mdf.crit_damage += stat_map[GearPropType.crit_damage]
        mdf.cooltime_reduce += stat_map[GearPropType.cooltime_reduce] * 1000
        mdf.pdamage_indep += stat_map[GearPropType.pdamage_indep] * (1 + mdf.pdamage_indep * 0.01)
        return mdf

    @staticmethod
    def is_weapon(gear_type: GearType) -> bool:
        return Gear.is_left_weapon(gear_type) or Gear.is_double_hand_weapon(gear_type)

    @staticmethod
    def is_left_weapon(gear_type: GearType) -> bool:
        return 121 <= gear_type.value <= 139 and gear_type != GearType.katara or gear_type.value // 10 == 121

    @staticmethod
    def is_sub_weapon(gear_type: GearType) -> bool:
        if gear_type == GearType.shield or gear_type == GearType.demon_shield or gear_type == GearType.soul_shield:
            return True
        if gear_type.value // 1000 == 135:
            return True
        return False

    @staticmethod
    def is_double_hand_weapon(gear_type: GearType) -> bool:
        return 140 <= gear_type.value <= 149 or 152 <= gear_type.value <= 159

    @staticmethod
    def is_armor(gear_type: GearType) -> bool:
        return gear_type.value == 100 or 104 <= gear_type.value <= 110

    @staticmethod
    def is_accessory(gear_type: GearType) -> bool:
        return 101 <= gear_type.value <= 103 or 111 <= gear_type.value <= 113 or gear_type == 115

    @staticmethod
    def is_mechanic_gear(gear_type: GearType) -> bool:
        return 161 <= gear_type.value <= 165

    @staticmethod
    def is_dragon_gear(gear_type: GearType) -> bool:
        return 194 <= gear_type.value <= 197

    @staticmethod
    def get_gear_type(gear_id: int) -> GearType:
        value = gear_id // 1000
        if value == 1098:
            return GearType.soul_shield
        if value == 1099:
            return GearType.demon_shield
        if value == 1212:
            return GearType.shining_rod
        if value == 1213:
            return GearType.tuner
        if value == 1214:
            return GearType.breath_shooter
        value = gear_id // 10000
        if value == 135:
            value = gear_id // 100
            if value == 13522 or value == 13528 or value == 13529 or value == 13540:
                return GearType(gear_id // 10)
            return GearType(gear_id // 100 * 10)

        if gear_id // 100 == 11902:
            return GearType(gear_id // 10)
        return GearType(gear_id // 10000)

    @staticmethod
    def _create_from_node(node, gear_id):
        gear = Gear()
        gear.name = node['name']
        gear.item_id = gear_id
        gear.type = Gear.get_gear_type(gear_id)
        for key in node:
            value: int = node[key]
            if key in ("STR", "DEX", "INT", "LUK", "att", "matt", "MHP", "MMP", "MHP_rate", "MMP_rate",
                       "boss_pdamage", "armor_ignore", "crit", "crit_damage", "pdamage"):
                prop_type = GearPropType[key]
                gear.base_stat[prop_type] = value
            else:
                if isinstance(getattr(gear, key), bool):
                    value = bool(value)
                setattr(gear, key, value)
        gear.max_star = gear.get_max_star()
        return gear

    @staticmethod
    def create_from_id(gear_id: int):
        """
        Create Gear from given gear_id.
        :param gear_id: Gear's id stored in MapleStory client data.
        :return: Gear for gear_id.
        :raises ValueError: If gear does not exist for gear_id.
        """
        if str(gear_id) not in gear_data:
            raise ValueError('Gear does not exist for gear_id: ' + str(gear_id))
        data_node = gear_data[str(gear_id)]
        gear = Gear._create_from_node(data_node, gear_id)
        return gear

    @staticmethod
    def get_id_from_name(name: str, exact: bool = True) -> int:
        """
        Search first matching gear's id for name.
        :param name: String to search for in gear names.
        :param exact: (gear.name) equals name if True; (gear.name) contains name if False.
        :return: First matching gear's id.
        :raises ValueError: If gear does not exist for name.
        """
        for gear_id in gear_data:
            if (exact and name == gear_data[gear_id]['name']) or (not exact and name in gear_data[gear_id]['name']):
                return int(gear_id)
        raise ValueError('Gear does not exist for name: ' + name + ', exact: ' + str(exact))

    @staticmethod
    def create_from_name(name: str, exact: bool = True):
        """
        Create Gear from given name.
        :param name: String to search for in gear names.
        :param exact: (gear.name) equals name if True; (gear.name) contains name if False.
        :return: First matching gear for name.
        :raises ValueError: If gear does not exist for name.
        """
        return Gear.create_from_id(Gear.get_id_from_name(name, exact))

    @staticmethod
    def create_title_from_name(name: str):
        """
        Create 'title' Gear from given name.
        :param name: Title Gear's name.
        :return: Title Gear for name.
        :raises ValueError: If gear does not exist for name.
        """
        if name not in title_data:
            raise ValueError('Gear does not exist for name: ' + name)
        gear = Gear._create_from_node(title_data[name], 2000000)
        gear.item_id = 1
        gear.type = GearType.title
        return gear
