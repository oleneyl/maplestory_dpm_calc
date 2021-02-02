import json
import os
from collections import defaultdict
from typing import Dict, DefaultDict, Iterable, List

from .Gear import Gear
from .GearPropType import GearPropType

PropMap = DefaultDict[GearPropType, int]

with open(os.path.join(os.path.dirname(__file__), 'resources', 'setitem.json'), encoding='utf8') as file:
    setItemData = json.load(file)


class SetItem:
    set_item_id: int = 0
    set_item_name: str = None
    joker_possible: bool = False
    item_ids: Dict[int, bool] = {}
    effects: Dict[int, PropMap] = {}

    def __init__(self):
        self.item_ids = {}
        self.effects = {}

    def __str__(self):
        return """ID: {}
이름: {}
럭키아이템: {}
장비 ID: {}
효과: {}""".format(self.set_item_id, self.set_item_name, self.joker_possible, self.item_ids, self.effects)

    @property
    def item_count(self) -> int:
        """
        Returns the number of active items in this set item.
        :return: The number of active items.
        """
        return sum(self.item_ids.values())

    @staticmethod
    def create_from_id(set_item_id: int):
        """
        Create SetItem from given set_item_id.
        :param set_item_id: SetItem's id stored in MapleStory client data.
        :return: SetItem for gear_id.
        :raises ValueError: If SetItem does not exist for set_item_id.
        """
        if str(set_item_id) not in setItemData:
            raise ValueError('SetItem does not exist for set_item_id: ' + str(set_item_id))
        set_item_node = setItemData[str(set_item_id)]
        set_item = SetItem()
        set_item.set_item_id = set_item_id
        set_item.set_item_name = set_item_node['set_item_name']
        set_item.joker_possible = set_item_node['joker_possible'] if 'joker_possible' in set_item_node else False
        set_item.item_ids = dict((itemID, False) for itemID in set_item_node['item_id'])
        for count in set_item_node['effect']:
            prop_map = defaultdict(int)
            for prop in set_item_node['effect'][count]:
                prop_map[GearPropType[prop]] = set_item_node['effect'][count][prop]
            set_item.effects[int(count)] = prop_map
        return set_item


def eval_set_item_effect(equipped_gears: Iterable[Gear]) -> PropMap:
    """
    Get summed set item effects of given gears. Faithful to MapleStory set item calculation.
    :param equipped_gears: Equipped gears.
    :return: Defaultdict of summed set item effects.
    """
    set_items: Dict[int, SetItem] = {}
    joker_ids: List[int] = []
    set_item_effect: defaultdict[GearPropType, int] = defaultdict(int)
    # Setup set items and joker items
    for gear in equipped_gears:
        if gear.joker_to_set_item:
            joker_ids.append(gear.item_id)
        set_item_id = gear.set_item_id
        if set_item_id == 0:
            continue
        if set_item_id not in set_items:
            set_items[set_item_id] = SetItem.create_from_id(set_item_id)
        set_items[set_item_id].item_ids[gear.item_id] = True
    # Apply joker item
    # Sort so that gear with lower id is evaluated first.
    joker_ids.sort()
    for joker_id in joker_ids:
        joker_applied = False
        for set_item in set_items.values():
            if not set_item.joker_possible or set_item.item_count < 3:
                continue
            for item_id in set_item.item_ids:
                if set_item.item_ids[item_id]:
                    continue
                if Gear.get_gear_type(item_id) == Gear.get_gear_type(joker_id):
                    set_item.item_ids[item_id] = True
                    joker_applied = True
                    break
        if joker_applied:
            break
    # Sum set item effects
    for set_item in set_items.values():
        count = set_item.item_count
        for index in set_item.effects:
            if index <= count:
                for prop_type in set_item.effects[index]:
                    if prop_type == GearPropType.armor_ignore:
                        set_item_effect[prop_type] = (100 - (1 - set_item_effect[prop_type] / 100) *
                                                      (1 - set_item.effects[index][prop_type] / 100) * 100)
                    else:
                        set_item_effect[prop_type] += set_item.effects[index][prop_type]
            else:
                break
        # remove comment below to check set items
        # print(set_item.set_item_name, count)
    return set_item_effect
