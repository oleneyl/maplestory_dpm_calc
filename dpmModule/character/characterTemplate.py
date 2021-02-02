import yaml
import os
from copy import copy, deepcopy
from typing import List, Optional, Tuple, Union

from ..character.characterKernel import GearedCharacter, JobGenerator
from ..gear import Gear, GearBuilder, GearType, GearPropType, Scroll, eval_set_item_effect
from ..jobs import job_branch_list
from ..kernel.core.modifier import ExtendedCharacterModifier as ExMDF


def open_yaml(*paths) -> dict:
    with open(os.path.join(os.path.dirname(__file__), *paths), encoding='utf8') as _file:
        return yaml.safe_load(_file)


'''How template override works:
1. "default" <- "job" (type: override):
    Override by keys in "job"
    ex) default.armor = job.armor, default.head = job.head
2. "armor" <- "head":
    Override by keys in "head"
'''

'''Order of template gear attributes:
1. id*
2. bonus
3. upgrade
4. star
5. potential
6. add_potential
7. cdr
'''


class TemplateGenerator:
    def __init__(self):
        # TODO: 보조무기 성장치 반영
        # "데몬슬레이어": 1099004,  # 성장으로 STR 9, DEX 9, HP 200, 방어력 20 상승
        # "데몬어벤져": 1099009,  # 성장으로 STR 9, HP 200, 방어력 20 상승
        # "미하일": 1098003,  # 성장으로 STR 9, DEX 9, HP 200, 방어력 20 상승
        # TODO: Maybe use 'inherit: true' keyword to inherit from 'armor', 'acc', etc... ?
        # ex 1) eye: { "inherit": "true", "bonus": { ... }, ... } # inherit everything
        # ex 2) eye: { "bonus": "inherit" or { ... }, ... } # inherit single attribute
        # Or create gear factory json and load by key (maybe simpler to implement)

        self.parts = ("head", "top", "bottom", "shoes", "glove", "cape", "shoulder", "face", "eye", "ear", "belt",
                      "ring1", "ring2", "ring3", "ring4", "pendant1", "pendant2",
                      "pocket", "badge", "medal", "weapon", "subweapon", "emblem", "heart")

        # load template.yaml to 'data'
        self.data = {}
        _template_yaml = open_yaml('configs', 'template.yaml')
        for key in _template_yaml:
            self.data[key] = open_yaml('configs', _template_yaml[key])

    def get_spec_names(self) -> Tuple[str]:
        names: List[str] = []
        for name in self.data.keys():
            if not name.startswith("_"):
                names.append(name)
        return tuple(names)

    def get_template_and_weapon_stat(self, gen: JobGenerator, spec_name: str, cdr: int = 0):
        return self.get_template(gen, spec_name, cdr), self.get_weapon_stat(gen, spec_name)

    def get_weapon_stat(self, gen: JobGenerator, spec_name: str) -> Tuple[int, int]:
        return self._get_weapon_stat(self._get_template_dict(spec_name, gen.jobname))

    def get_template(self, gen: JobGenerator, spec_name: str, cdr: int = 0) -> GearedCharacter:
        """
        :param gen: JobGenerator
        :param spec_name: 스펙 이름; 유니온 레벨이 사용됩니다.
        :param cdr: 쿨타임 감소 (초)
        :return: GearedCharacter
        """
        node = self._get_template_dict(spec_name, gen.jobname)
        # Create GearedCharacter with level
        template = GearedCharacter(gen=gen, level=node['level'])
        # Apply arcane, authentic, pet, cash modifiers

        template.apply_modifiers([
            self._get_arcane_modifier(node, gen.jobtype),
            self._get_authentic_modifier(node, gen.jobtype),
            self._get_pet_modifier(node),
            self._get_cash_modifier(node, gen.jobtype),
            self._get_job_specific_item_modifier(node)
        ])
        # Equip title
        template.title = self._get_title(node)
        template.add_gear_modifier(template.title)
        # Equip gears
        gear_list = {}
        for part in self.parts:
            # Set zero subweapon
            if part == "subweapon" and gen.jobname == "제로":
                gear_list["subweapon"] = self._get_zero_subweapon(gear_list["weapon"])
            else:
                gear_list[part] = self._get_enchanted_gear(part, node, gen, cdr)
        # Get set item effects
        gear_list["set_effect"] = self._get_set_effect(gear_list, node)
        # Apply gear, set item effect to character mdf
        template.set_gears(gear_list)
        return template

    def _get_template_dict(self, spec_name: str, jobname: str) -> dict:
        if spec_name not in self.data:
            raise ValueError('Invalid spec_name: ' + spec_name)
        # Get job specific copy of node
        node: dict = deepcopy(self.data[spec_name]['default'])
        if jobname in self.data[spec_name]:
            if self.data[spec_name][jobname]['type'] == "full":
                node = deepcopy(self.data[spec_name][jobname])
            elif self.data[spec_name][jobname]['type'] == "override":
                for node_key in self.data[spec_name][jobname]:
                    node[node_key] = deepcopy(self.data[spec_name][jobname][node_key])
        # Assert node contains all necessary parts
        assert("level" in node and set(self.parts) <= node.keys())
        return node

    def _get_weapon_stat(self, node) -> Tuple[int, int]:
        if 'weapon_stat' not in node or len(node['weapon_stat']) != 2:
            raise TypeError('template does not contain valid weapon_stat field')
        return tuple(node['weapon_stat'])

    def _get_arcane_modifier(self, node, jobtype: str) -> ExMDF:
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

    def _get_authentic_modifier(self, node, jobtype: str) -> ExMDF:
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

    def _get_pet_modifier(self, node) -> ExMDF:
        mdf = ExMDF()
        if "pet_equip" in node:
            mdf.att += node["pet_equip"]
        if "pet_set" in node:
            mdf.att += node["pet_set"]
        return mdf

    def _get_cash_modifier(self, node, jobtype: str) -> ExMDF:
        if "cash" not in node:
            return ExMDF()
        mdf = ExMDF()
        for stat_key in ("att", "stat_main"):
            if stat_key in node["cash"]:
                setattr(mdf, stat_key, node["cash"][stat_key])
        if "stat_sub" in node["cash"]:  # TODO: 캐시장비도 Gear로 처리하도록 변경할것
            if jobtype == "xenon":
                setattr(mdf, "stat_main", getattr(mdf, "stat_main", 0) + node["cash"]["stat_sub"])
            else:
                setattr(mdf, "stat_sub", node["cash"]["stat_sub"])
        if "stat_sub2" in node["cash"]:
            if jobtype == "xenon":
                setattr(mdf, "stat_main", getattr(mdf, "stat_main", 0) + node["cash"]["stat_sub2"])
            if jobtype == "LUK2":
                setattr(mdf, "stat_sub", getattr(mdf, "stat_sub", 0) + node["cash"]["stat_sub2"])
        return mdf

    def _get_job_specific_item_modifier(self, node) -> ExMDF:
        if "job_specific_item" not in node:
            return ExMDF()
        mdf = ExMDF()
        for stat_key in node["job_specific_item"]:
            setattr(mdf, stat_key, node["job_specific_item"][stat_key])
        return mdf

    def _get_title(self, node) -> Gear:
        if "title" not in node:
            raise TypeError('template does not contain title.')
        return Gear.create_title_from_name(node["title"]['id'])

    def _get_enchanted_gear(self, part: str, node, gen: JobGenerator, cdr: int) -> Gear:
        return self._apply_gear_options(
            self._get_gear_base(node[part]['id'], part, gen.jobname), node[part], part, gen.jobtype, cdr
        )

    def _get_gear_base(self, name: Union[int, str], part: str, jobname: str) -> Gear:
        def _get_job_branch(jobname: str) -> int:
            return job_branch_list[jobname]

        def _get_gear_id(name: str, part: str, jobname: str) -> int:
            part = part.rstrip('0123456789')
            preset_node = self.data['_preset']
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

    def _apply_gear_options(self, gear: Gear, gear_node, part: str, jobtype: str, cdr) -> Gear:
        def _apply_bonus(bonus_node):
            def _is_bonus_gear(part: str):
                part = part.rstrip("0123456789")
                return part in ("head", "top", "bottom", "shoes", "glove", "cape", "shoulder",
                                "face", "eye", "ear", "belt", "pendant", "pocket", "weapon")
            if len(bonus_node) > 0 and not _is_bonus_gear(part):
                raise TypeError('Cannot apply bonus to gear type: ' + gear.type.name)
            for bonus_type in bonus_node:
                if bonus_type == "att_grade":
                    gb.apply_additional_stat(att, bonus_node[bonus_type])
                elif bonus_type == "allstat_rate":
                    gb.apply_additional_stat(GearPropType.allstat, bonus_node[bonus_type])
                else:
                    gear.additional_stat[stat_type[bonus_type]] = bonus_node[bonus_type]

        def _apply_upgrade(upgrade_node):
            # Ignore special case: subweapon / shield
            if len(upgrade_node) > 0 and gear.tuc < 1 and part != "subweapon":
                raise TypeError('Cannot apply scroll upgrade to gear: ' + str(gear))
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
                    raise TypeError('Invalid upgrade type: ' + type)

        def _apply_star(gear_node):
            star = gear_node['star']
            # Ignore special case: subweapon / shield
            if abs(star) > gear.max_star and part != "subweapon":
                raise TypeError('Tried to apply star ' + str(star) + ' but max_star was ' + str(gear.max_star))
            if star > 0:
                gb.apply_stars(star)
            elif star < 0:
                bonus = 0
                if 'surprise_bonus' in gear_node:
                    bonus = gear_node['surprise_bonus']
                bonus_count = abs(star) * bonus // 100
                gb.apply_stars(abs(star) - bonus_count, True, False)
                gb.apply_stars(bonus_count, True, True)

        def _apply_potential(potential_node, gear_potential_dict):
            def _is_potential_gear(part: str):
                part = part.rstrip("0123456789")
                return part in ("head", "top", "bottom", "shoes", "glove", "cape", "shoulder", "face", "eye",
                                "ear", "belt", "ring", "pendant", "weapon", "subweapon", "emblem", "heart")
            if len(potential_node) > 0 and not _is_potential_gear(part):
                raise TypeError('Cannot apply potential to gear type: ' + gear.type.name)
            gear_potential_dict.clear()
            for stat_key in potential_node:
                if stat_key == "allstat_rate":
                    gear_potential_dict[pstat_main] += potential_node[stat_key]
                    gear_potential_dict[pstat_sub] += potential_node[stat_key]
                    gear_potential_dict[pstat_sub2] += potential_node[stat_key]
                else:
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
        if 'upgrade' in gear_node:
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

    def _get_zero_subweapon(self, zero_weapon: Gear) -> Gear:
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

    def _get_set_effect(self, gears, node) -> Gear:
        def _get_zero_weapon_set_id(name: str):
            try:
                return self.data['_preset']["zero_weapon_set_id"][name]
            except KeyError:
                return 0

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
