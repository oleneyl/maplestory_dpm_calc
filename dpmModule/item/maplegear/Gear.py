import json
from typing import DefaultDict, List

from collections import defaultdict

from GearPropType import GearPropType
from GearType import GearType

PropMap = DefaultDict[GearPropType, int]

with open('./resources/geardata.json', encoding='utf8') as gear_file:
    gear_data = json.load(gear_file)


class Gear:
    item_id: int = 0
    name: str = None
    type: GearType = 0

    req_level: int = 0,
    req_job: int = 0,
    set_item_id: int = 0
    boss_reward: bool = False

    superior_eqp: bool = False
    joker_to_set_item: bool = False

    amazing_scroll: bool = False
    star: int = 0
    max_star: int = 0

    tuc: int = 0
    scroll_up: int = 0
    scroll_fail: int = 0
    hammer: int = 0

    base_stat: PropMap = defaultdict(int)  # 기본 옵션
    additional_stat: PropMap = defaultdict(int)  # 추가 옵션
    scroll_stat: PropMap = defaultdict(int)  # 주문서 옵션
    star_stat: PropMap = defaultdict(int)  # 스타포스 옵션

    potential: PropMap  # 잠재옵션
    additional_potential: PropMap  # 에디셔널 잠재옵션

    def __init__(self):
        self.props = defaultdict(int)
        self.base_stat: PropMap = defaultdict(int)
        self.additional_stat: PropMap = defaultdict(int)
        self.scroll_stat: PropMap = defaultdict(int)
        self.star_stat: PropMap = defaultdict(int)
        self.potential = defaultdict(int)
        self.additional_potential = defaultdict(int)

    def __str__(self):
        # for debug
        statStr = ""
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
            statStr += "%s: %d (%d +%d +%d +%d)\n" % (propType.name, sum(stats[propType]),
                                                      stats[propType][0], stats[propType][1],
                                                      stats[propType][2], stats[propType][3])
        propStr = ""
        keys = sorted(self.props)
        for propType in keys:
            propStr += propType.name + ": " + str(self.props[propType]) + '\n'

        return "ID: " + str(self.item_id) + '\n' + \
               "이름: " + self.name + '\n' + \
               "분류: " + self.type.name + '\n' + \
               ("놀장" if self.amazing_scroll else "스타포스") + ": " + \
               str(self.star) + '/' + str(self.max_star) + '\n' + \
               "최대 업횟: " + str(self.tuc) + \
               " +(황금 망치: " + str(self.hammer) + ')\n' + \
               "업그레이드 성공 횟수: " + str(self.scroll_up) + '\n' + \
               "업그레이드 실패 횟수: " + str(self.scroll_fail) + '\n' + \
               "옵션: 합계 (기본 +추옵 +주문서 +별)\n" + statStr + \
               "기타 속성:\n" + propStr

    def get_max_star(self) -> int:
        if self.is_mechanic_gear(self.type) or self.is_dragon_gear(self.type):
            return 0
        starData = [
            [0, 5, 3],
            [95, 8, 5],
            [110, 10, 8],
            [120, 15, 10],
            [130, 20, 12],
            [140, 25, 15],
        ]
        data = None
        for item in starData:
            if self.req_level >= item[0]:
                data = item
            else:
                break
        if data is None:
            return 0
        return data[2 if self.superior_eqp else 1]

    @staticmethod
    def is_weapon(gear_type: GearType) -> bool:
        return Gear.is_left_weapon(gear_type) or Gear.is_double_hand_weapon(gear_type)

    @staticmethod
    def is_left_weapon(gear_type: GearType) -> bool:
        _type: int = gear_type.value
        if gear_type == GearType.shining_rod or gear_type == GearType.tuner:
            _type = gear_type.value // 10
        return 121 <= _type <= 139 and gear_type != GearType.katara

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
        value = gear_id // 10000
        if value == 135:
            value = gear_id // 100
            if value == 13522 or value == 13528 or value == 13529:
                return GearType(gear_id // 10)
            return GearType(gear_id // 100 * 10)

        if gear_id // 100 == 11902:
            return GearType(gear_id // 10)
        return GearType(gear_id // 10000)

    @staticmethod
    def create_from_id(gear_id: int):
        if str(gear_id) not in gear_data:
            return Gear()
        data_node = gear_data[str(gear_id)]
        gear = Gear()
        gear.item_id = gear_id
        gear.type = Gear.get_gear_type(gear_id)
        gear.name = data_node['name']
        for key in data_node:
            value: int = data_node[key]
            if key in GearPropType:
                prop_type = GearPropType[key]
                gear.base_stat[prop_type] = value
            else:
                setattr(gear, key, value)
        gear.max_star = gear.get_max_star()
        return gear


def _search_ids_by_name(name: str, exact: bool = True) -> List[int]:
    # utility function
    ids = []
    for gear_id in gear_data:
        if (exact and name == gear_data[gear_id]['name']) or (not exact and name in gear_data[gear_id]['name']):
            ids.append(int(gear_id))
    return ids
