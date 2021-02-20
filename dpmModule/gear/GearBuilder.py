import math
from typing import List, Optional, Set

from .Gear import Gear
from .GearPropType import GearPropType
from .GearType import GearType
from .Scroll import Scroll


class GearBuilder:
    def __init__(self, gear: Gear = None):
        self.gear: Optional[Gear] = gear

    def set_gear(self, gear: Gear) -> bool:
        self.gear = gear
        return True

    def get_gear(self) -> Gear:
        return self.gear

    def apply_additional_stat(self, prop_type: GearPropType, grade: int, is_double_add: bool = False) -> bool:
        """
        Apply additional stat (bonus) to gear.
        :param prop_type: Type to apply additional stat to. allstat applies allstat_rate.
        :param grade: 1~7.
        :param is_double_add: Apply as double add stat if True; Apply as single add stat otherwise.
        :return: True if applied; False otherwise.
        :raises AttributeError: If gear is not set.
        """
        if grade <= 0:
            return False
        grade = min(grade, 7)
        req_level = self.gear.req_level
        if req_level <= 0:
            return False
        boss_reward = self.gear.boss_reward
        if prop_type == GearPropType.allstat:
            self.gear.additional_stat[GearPropType.STR_rate] += grade
            self.gear.additional_stat[GearPropType.DEX_rate] += grade
            self.gear.additional_stat[GearPropType.INT_rate] += grade
            self.gear.additional_stat[GearPropType.LUK_rate] += grade
            return True
        elif prop_type in (GearPropType.STR, GearPropType.DEX, GearPropType.INT, GearPropType.LUK):
            value = ((req_level // 40 + 1) * grade) if is_double_add else ((req_level // 20 + 1) * grade)
        # elif prop_type == GearPropType.incPDD:
            # value = (req_level // 20 + 1) * grade
        elif prop_type == GearPropType.att or prop_type == GearPropType.matt:
            gear_type = self.gear.type
            if Gear.is_weapon(gear_type):
                data = ([0, 0, 1, 1.4666, 2.0166, 2.663, 3.4166]
                        if boss_reward else
                        [1, 2.222, 3.63, 5.325, 7.32, 8.777, 10.25])
                att = self.gear.base_stat[GearPropType.att]
                if gear_type == GearType.sword_zb or gear_type == GearType.sword_zl:
                    if gear_type == GearType.sword_zl:
                        if att == 100: att = 102
                        elif att == 103: att = 105
                        elif att == 105: att = 107
                        elif att == 112: att = 114
                        elif att == 117: att = 121
                        elif att == 135: att = 139
                        elif att == 169: att = 173
                        elif att == 203: att = 207
                        elif att == 293: att = 297
                        elif att == 337: att = 342
                        else:
                            print('Not implemented weapon:\n' + str(self.gear))
                            return False
                    value = 6 if req_level > 180 else (5 if req_level > 160 else (4 if req_level > 110 else 3))
                    value = math.ceil(att * data[grade - 1] * value / 100)
                else:
                    mad = self.gear.base_stat[GearPropType.matt]
                    if prop_type == GearPropType.matt and mad >= att:
                        att = mad
                    if boss_reward:
                        if grade < 3:
                            return False
                        value = 18 if req_level > 160 else (15 if req_level > 150 else (12 if req_level > 110 else 9))
                    else:
                        value = 4 if req_level > 110 else 3
                    value = math.ceil(att * data[grade - 1] * value / 100)
            else:
                value = grade
        elif prop_type == GearPropType.MHP or prop_type == GearPropType.MMP:
            value = req_level // 10 * 30 * grade
        # elif prop_type in (GearPropType.incSpeed, GearPropType.incJump):
            # value = grade
        elif prop_type in (GearPropType.armor_ignore, GearPropType.pdamage):
            value = grade
        elif prop_type == GearPropType.boss_pdamage:
            value = 2 * grade
        # elif prop_type == GearPropType.reduceReq:
            # value = min(5 * grade, req_level)
        else:
            return False
        self.gear.additional_stat[prop_type] += value
        return True

    @property
    def scroll_available(self):
        """
        Returns the number of available scroll upgrade.
        :return: The number of available scroll upgrade.
        """
        return self.gear.tuc + self.gear.hammer - self.gear.scroll_fail - self.gear.scroll_up

    def apply_scroll(self, scroll: Scroll, count: int = 1) -> bool:
        """
        Apply given scroll.
        :param scroll: Scroll to apply.
        :param count: Number of upgrades.
        :return: True if applied at least once; False otherwise.
        :raises AttributeError: If gear is not set.
        """
        count = min(count, self.scroll_available)
        if count < 1:
            return False

        for key in scroll.stat:
            self.gear.scroll_stat[key] += scroll.stat[key] * count
        if self.gear.scroll_up < 4 <= self.gear.scroll_up + count:
            if scroll.bonus_pad_on_fourth:
                self.gear.scroll_stat[GearPropType.att] += 1
            if scroll.bonus_mad_on_fourth:
                self.gear.scroll_stat[GearPropType.matt] += 1
        self.gear.scroll_up += count
        return True

    def apply_spell_trace_scroll(self, probability: int, prop_type: GearPropType, count: int = 1) -> bool:
        """
        Apply matching spell trace scroll.
        :param probability: 100 or 70 or 30 or 15
        :param prop_type: Prop type of spell trace scroll.
        :param count: Number of upgrades.
        :return: True if applied at least once; False otherwise.
        :raises AttributeError: If gear is not set.
        :raises TypeError: If matching spell trace scroll does not exist for gear.
        """
        spell_trace = Scroll.get_spell_trace_scroll(self.gear, probability, prop_type)
        return self.apply_scroll(spell_trace, count)

    def apply_hammer(self) -> bool:
        """
        Apply golden hammer.
        :return: True if applied; False otherwise.
        :raises AttributeError: If gear is not set.
        """
        if self.gear.tuc <= 0:
            return False
        if self.gear.block_hammer:
            return False
        if self.gear.hammer == 0:
            self.gear.hammer = 1
            return True
        return False

    def apply_star(self, amazing_scroll: bool = False, bonus: bool = False) -> bool:
        """
        Apply single star and corresponding stats.
        :param amazing_scroll: True to apply blue star; False to apply yellow star.
        :param bonus: True to apply bonus stat to blue star; False otherwise.
        :return: True if applied; False otherwise.
        :raises AttributeError: If gear is not set.
        """
        if self.gear.star >= self.gear.max_star:
            return False
        if amazing_scroll:
            if self.gear.req_level > 150:
                return False
            if self.gear.star >= 15:
                return False

        self.gear.star += 1
        star = self.gear.star
        stat_data = _get_star_data(self.gear, amazing_scroll, False)
        att_data = _get_star_data(self.gear, amazing_scroll, True)
        is_weapon = Gear.is_weapon(self.gear.type) or self.gear.type == GearType.katara
        if self.gear.superior_eqp:
            for prop_type in (GearPropType.STR, GearPropType.DEX, GearPropType.INT, GearPropType.LUK):
                self.gear.star_stat[prop_type] += stat_data[star]
            for att_type in (GearPropType.att, GearPropType.matt):
                self.gear.star_stat[att_type] += att_data[star]
            # pdd = (self.gear.base_stat[GearPropType.incPDD] +
            #        self.gear.scroll_stat[GearPropType.incPDD] +
            #        self.gear.star_stat[GearPropType.incPDD])
            # self.gear.star_stat[GearPropType.incPDD] += pdd // 20 + 1
        elif not amazing_scroll:
            job_stat = [
                [GearPropType.STR, GearPropType.DEX],
                [GearPropType.INT, GearPropType.LUK],
                [GearPropType.DEX, GearPropType.STR],
                [GearPropType.LUK, GearPropType.DEX],
                [GearPropType.STR, GearPropType.DEX],
            ]
            stat_set: Set[GearPropType]
            req_job = self.gear.req_job
            if req_job == 0:
                stat_set = {GearPropType.STR, GearPropType.DEX, GearPropType.INT, GearPropType.LUK}
            else:
                stat_set = set()
                for i in range(0, 5):
                    if req_job & (1 << i) != 0:
                        for prop_type in job_stat[i]:
                            stat_set.add(prop_type)
            for prop_type in (GearPropType.STR, GearPropType.DEX, GearPropType.INT, GearPropType.LUK):
                if prop_type in stat_set:
                    self.gear.star_stat[prop_type] += stat_data[star]
                elif star > 15 and self.gear.base_stat[prop_type] + self.gear.scroll_stat[prop_type] > 0:
                    self.gear.star_stat[prop_type] += stat_data[star]

            if is_weapon:
                use_mad = req_job == 0 or req_job // 2 % 2 == 1 or self.gear.scroll_stat[GearPropType.matt] > 0
                if star > 15:
                    self.gear.star_stat[GearPropType.att] += att_data[star]
                    if use_mad:
                        self.gear.star_stat[GearPropType.matt] += att_data[star]
                else:
                    pad = (self.gear.base_stat[GearPropType.att] +
                           self.gear.scroll_stat[GearPropType.att] +
                           self.gear.star_stat[GearPropType.att])
                    self.gear.star_stat[GearPropType.att] += pad // 50 + 1
                    if use_mad:
                        mad = (self.gear.base_stat[GearPropType.matt] +
                               self.gear.scroll_stat[GearPropType.matt] +
                               self.gear.star_stat[GearPropType.matt])
                        self.gear.star_stat[GearPropType.matt] += mad // 50 + 1
            else:
                self.gear.star_stat[GearPropType.att] += att_data[star]
                self.gear.star_stat[GearPropType.matt] += att_data[star]
                if self.gear.type == GearType.glove:
                    glove_bonus = [0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    if req_job == 0:
                        self.gear.star_stat[GearPropType.att] += glove_bonus[star]
                        self.gear.star_stat[GearPropType.matt] += glove_bonus[star]
                    elif req_job // 2 % 2 == 1:
                        self.gear.star_stat[GearPropType.matt] += glove_bonus[star]
                    else:
                        self.gear.star_stat[GearPropType.att] += glove_bonus[star]

            if not is_weapon and self.gear.type != GearType.machine_heart:
                # pdd = (self.gear.base_stat[GearPropType.incPDD] +
                #        self.gear.scroll_stat[GearPropType.incPDD] +
                #        self.gear.star_stat[GearPropType.incPDD])
                # self.gear.star_stat[GearPropType.incPDD] += pdd // 20 + 1
                pass

            mhp_data = [0, 5, 5, 5, 10, 10, 15, 15, 20, 20, 25, 25, 25, 25, 25, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            mhp_types = [GearType.cap, GearType.coat, GearType.longcoat, GearType.pants, GearType.cape, GearType.ring,
                         GearType.pendant, GearType.belt, GearType.shoulder_pad, GearType.shield]
            if is_weapon:
                self.gear.star_stat[GearPropType.MHP] += mhp_data[star]
                self.gear.star_stat[GearPropType.MMP] += mhp_data[star]
            elif self.gear.type in mhp_types:
                self.gear.star_stat[GearPropType.MHP] += mhp_data[star]

            # if self.gear.type == GearType.shoes:
                # speed_jump_data = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                # self.gear.star_stat[GearPropType.incSpeed] += speed_jump_data[star]
                # self.gear.star_stat[GearPropType.incJump] += speed_jump_data[star]
        else:
            stat_bonus = (2 if star > 5 else 1) if bonus and Gear.is_accessory(self.gear.type) else 0
            for prop_type in (GearPropType.STR, GearPropType.DEX, GearPropType.INT, GearPropType.LUK):
                if (self.gear.base_stat[prop_type] +
                        self.gear.additional_stat[prop_type] +
                        self.gear.scroll_stat[prop_type] +
                        self.gear.star_stat[prop_type] > 0):
                    self.gear.star_stat[prop_type] += stat_data[star] + stat_bonus

            att_bonus = 1 if bonus and (is_weapon or self.gear.type == GearType.shield) else 0
            for att_type in (GearPropType.att, GearPropType.matt):
                att = (self.gear.base_stat[att_type] +
                       self.gear.additional_stat[att_type] +
                       self.gear.scroll_stat[att_type] +
                       self.gear.star_stat[att_type])
                if att > 0:
                    self.gear.star_stat[att_type] += att_data[star] + att_bonus
                    if is_weapon:
                        self.gear.star_stat[att_type] += att // 50 + 1
            # pdd = (self.gear.base_stat[GearPropType.incPDD] +
            #        self.gear.additional_stat[GearPropType.incPDD] +
            #        self.gear.scroll_stat[GearPropType.incPDD] +
            #        self.gear.star_stat[GearPropType.incPDD])
            # self.gear.star_stat[GearPropType.incPDD] += pdd // 20 + 1
            # if bonus and Gear.is_armor(self.gear.type):
            #     self.gear.star_stat[GearPropType.incPDD] += 50
            self.gear.amazing_scroll = True
        return True

    def apply_stars(self, count: int, amazing_scroll: bool = False, bonus: bool = False) -> int:
        """
        Apply multiple stars and corresponding stats.
        :param count: Number for stars to apply.
        :param amazing_scroll: True to apply blue star; False to apply yellow star.
        :param bonus: True to apply bonus stat to blue star; False otherwise.
        :return: Number of increased stars.
        :raises AttributeError: If gear is not set.
        """
        suc = 0
        for i in range(0, count):
            suc += 1 if self.apply_star(amazing_scroll, bonus) else 0
        return suc


def _get_star_data(gear: Gear, amazing_scroll: bool, att: bool) -> List[int]:
    if gear.superior_eqp:
        if att:
            data = __superior_att_data
        else:
            data = __superior_stat_data
    elif not amazing_scroll:
        if att:
            if Gear.is_weapon(gear.type) or gear.type == GearType.katara:
                data = __starforce_weapon_att_data
            else:
                data = __starforce_att_data
        else:
            data = __starforce_stat_data
    else:
        if att:
            data = __amazing_att_data
        else:
            data = __amazing_stat_data
    stat = None
    for item in data:
        if gear.req_level >= item[0]:
            stat = item
        else:
            break
    return stat


__superior_att_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [110, 0, 0, 0, 0, 0, 5, 6, 7, 0, 0, 0, 0, 0, 0, 0],
    [150, 0, 0, 0, 0, 0, 9, 10, 11, 12, 13, 15, 17, 19, 21, 23],
]
__superior_stat_data = [
    [0, 1, 2, 4, 7, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [80, 2, 3, 5, 8, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [110, 9, 10, 12, 15, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [150, 19, 20, 22, 25, 29, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
__starforce_weapon_att_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [108, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 5, 5, 6, 7, 8, 9, 27, 28, 29],
    [118, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 6, 7, 8, 9, 10, 28, 29, 30],
    [128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 7, 7, 8, 9, 10, 11, 29, 30, 31],
    [138, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 8, 8, 9, 10, 11, 12, 30, 31, 32],
    [148, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 9, 10, 11, 12, 13, 31, 32, 33],
    [158, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 10, 11, 12, 13, 14, 32, 33, 34],
    [198, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 13, 14, 14, 15, 16, 17, 34, 35, 36],
]
__starforce_att_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [108, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 7, 8, 9, 10, 12, 13, 15, 17],
    [118, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 7, 8, 9, 10, 11, 13, 14, 16, 18],
    [128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20],
    [138, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 10, 11, 12, 13, 15, 17, 19, 21],
    [148, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22],
    [158, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 11, 12, 13, 14, 15, 17, 19, 21, 23],
    [198, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 13, 14, 15, 16, 17, 19, 21, 23, 25],
]
__starforce_stat_data = [
    [0, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [108, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0],
    [118, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0],
    [128, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0],
    [138, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0],
    [148, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 11, 11, 11, 11, 11, 11, 11, 0, 0, 0],
    [158, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 13, 13, 13, 13, 13, 13, 13, 0, 0, 0],
    [198, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 15, 15, 15, 15, 15, 15, 15, 0, 0, 0],
]
__amazing_att_data = [
    [0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14],
    [80, 0, 0, 0, 0, 0, 2, 3, 4, 5, 6, 7, 9, 11, 13, 15],
    [90, 0, 0, 0, 0, 0, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16],
    [100, 0, 0, 0, 0, 0, 4, 5, 6, 7, 8, 9, 11, 13, 15, 17],
    [110, 0, 0, 0, 0, 0, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18],
    [120, 0, 0, 0, 0, 0, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19],
    [130, 0, 0, 0, 0, 0, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20],
    [140, 0, 0, 0, 0, 0, 8, 9, 10, 11, 12, 13, 15, 17, 19, 21],
    [150, 0, 0, 0, 0, 0, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22],
]
__amazing_stat_data = [
    [0, 1, 2, 4, 7, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [80, 2, 3, 5, 8, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [85, 3, 4, 6, 9, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [90, 4, 5, 7, 10, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [95, 5, 6, 8, 11, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [100, 7, 8, 10, 13, 17, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [105, 8, 9, 11, 14, 18, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [110, 9, 10, 12, 15, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [115, 10, 11, 13, 16, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [120, 12, 13, 15, 18, 22, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [125, 13, 14, 16, 19, 23, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [130, 14, 15, 17, 20, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [135, 15, 16, 18, 21, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [140, 17, 18, 20, 23, 27, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [145, 18, 19, 21, 24, 28, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [150, 19, 20, 22, 25, 29, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
