import json
import math
import copy
from typing import Any, Dict, List, Optional, Tuple

from ..execution.rules import RuleSet
from ..item.ItemKernel import Item
from ..kernel import policy
from ..kernel.abstract import AbstractVBuilder, AbstractVEnhancer
from ..kernel.core import (
    APPLY_PROP,
    AbstractSkillWrapper,
    CharacterModifier,
    DamageSkillWrapper,
    BuffSkillWrapper,
    SummonSkillWrapper,
    ExtendedCharacterModifier,
    InformedCharacterModifier,
    SkillModifier,
)
from ..kernel.graph import (
    GlobalOperation,
    _unsafe_access_global_storage,
    initialize_global_properties,
)
from ..kernel.core.skill import load_skill, BuffSkill, DamageSkill, SummonSkill
from ..status.ability import Ability_grade, Ability_option, Ability_tool
from .doping import Doping
from .hyperStat import HyperStat
from .linkSkill import LinkSkill
from .personality import Personality
from .union import Card, Union
from .weaponPotential import WeaponPotential


ExMDF = ExtendedCharacterModifier
"""Class AbstractCharacter : Basic template for building specific User. User is such object that contains:
- Items
- Buff Skill Wrappers
- Damage Skill Wrappers
- Some else Modifiers.
"""


def _get_loaded_object_with_mapping(conf, loadable, **kwargs):
    global_variables = globals()
    global_variables.update(kwargs)
    exported_conf = {}
    for k, v in conf.items():
        if isinstance(v, str) and k != 'name':
            assert 'import' not in v
            exported_conf[k] = eval(v, global_variables)
        else:
            exported_conf[k] = v
    return loadable.load(exported_conf)

class AbstractCharacter:
    # TODO : get/set :: use decorator? could be...
    def __init__(self, level: int = 230) -> None:
        # Initialize Items
        self.level: int = level
        self.base_modifier: ExMDF = ExMDF(stat_main=18 + level * 5, stat_sub=4, crit=5)

        self.about: str = ""
        self.add_summary("레벨 %d" % level)

        self._modifier_cache: Optional[CharacterModifier] = None

    def unsafe_change_level(self, level: int) -> None:
        level_delta = level - self.level
        self.add_summary(f"레벨 강제 변경 : {self.level} -> {level}")
        self.level = level
        self.base_modifier += ExMDF(stat_main=level_delta * 5)

    def add_summary(self, txt: str) -> None:
        self.about += "\n" + txt

    def get_property_ignorance_modifier(self) -> ExMDF:
        if not APPLY_PROP:
            return ExMDF()
        return ExMDF(pdamage_indep=self.base_modifier.prop_ignore) + ExMDF(
            pdamage_indep=-50
        )

    def apply_modifiers(self, li: List[CharacterModifier]) -> None:
        """Be careful! This function PERMANENTLY change character's property.
        You must sure that this function call is appropriate.
        """
        for mdf in li:
            self.base_modifier += mdf

    def generate_modifier_cache(self) -> None:
        self._modifier_cache = (
            self.get_static_modifier() + self.get_property_ignorance_modifier()
        )

    def get_base_modifier(self) -> ExMDF:
        return self.base_modifier.copy()

    def get_skill_modifier(self) -> SkillModifier:
        return self.base_modifier.to_skill_modifier()

    def get_modifier(self) -> CharacterModifier:
        if self._modifier_cache is None:
            return self.get_static_modifier() + self.get_property_ignorance_modifier()
        else:
            return self._modifier_cache

    def get_buffed_modifier(self) -> CharacterModifier:
        mod = self.get_static_modifier() + self.get_property_ignorance_modifier()
        return mod

    def get_static_modifier(self) -> CharacterModifier:
        return self.base_modifier.degenerate()


class ItemedCharacter(AbstractCharacter):
    def __init__(self, level=230) -> None:
        super(ItemedCharacter, self).__init__(level)
        self.itemlist: Dict[str, Optional[Item]] = {}

        # 6 items for armor
        self.itemlist["head"] = None
        self.itemlist["glove"] = None
        self.itemlist["top"] = None
        self.itemlist["bottom"] = None
        self.itemlist["shoes"] = None
        self.itemlist["cloak"] = None

        # 13 items for accessory

        self.itemlist["eye"] = None
        self.itemlist["face"] = None
        self.itemlist["ear"] = None
        self.itemlist["belt"] = None
        self.itemlist["ring1"] = None
        self.itemlist["ring2"] = None
        self.itemlist["ring3"] = None
        self.itemlist["ring4"] = None
        self.itemlist["shoulder"] = None
        self.itemlist["pendant1"] = None
        self.itemlist["pendant2"] = None
        self.itemlist["pocket"] = None
        self.itemlist["badge"] = None

        # 3 items for weapon

        self.itemlist["weapon"] = None
        self.itemlist["subweapon"] = None
        self.itemlist["emblem"] = None

        # 2 items for else

        self.itemlist["medal"] = None
        self.itemlist["heart"] = None
        self.itemlist["title"] = None
        self.itemlist["pet"] = None

    def remove_item_modifier(self, item: Item) -> None:
        mdf = item.get_modifier()
        self.base_modifier = self.base_modifier - mdf

    def add_item_modifier(self, item: Item) -> None:
        mdf = item.get_modifier()
        self.base_modifier = self.base_modifier + mdf

    def set_items(self, item_dict: Dict[str, Item]) -> None:
        keys = [
            "head",
            "glove",
            "top",
            "bottom",
            "shoes",
            "cloak",
            "eye",
            "face",
            "ear",
            "belt",
            "ring1",
            "ring2",
            "ring3",
            "ring4",
            "shoulder",
            "pendant1",
            "pendant2",
            "pocket",
            "badge",
            "weapon",
            "subweapon",
            "emblem",
            "medal",
            "heart",
            "title",
            "pet",
        ]

        for key in keys:
            item = item_dict[key]
            if item is None:
                raise TypeError(key + " item is missing")
            self.itemlist[key] = item_dict[key]
            self.add_item_modifier(item_dict[key])

    def set_weapon_potential(self, weapon_potential: Dict[str, List[ExMDF]]) -> None:
        for item_id in ["weapon", "subweapon", "emblem"]:
            potentials = weapon_potential[item_id]
            ptnl = ExMDF()

            if len(potentials) > 3:
                raise TypeError("무기류 잠재능력은 아이템당 최대 3개입니다.")

            for i in range(len(potentials)):
                ptnl = ptnl + potentials[i]

            item = self.itemlist[item_id]
            self.remove_item_modifier(item)
            item.set_potential(ptnl)
            self.add_item_modifier(item)

    def print_items(self) -> None:
        for item in self.itemlist:
            print("===" + item + "===")
            print(self.itemlist[item].log())


class JobGenerator:
    """class JobGenerator : Template for job generator.
    JobGenerator is abstract class : you must re-implement this class in usage.AbstractSkill

    - Functions that you must re-implement

    .generate(chtr : ck.AbstractCharacter, vlevel: int = 0, vEnhance: list = [0,0,0]) :
        This function generate given chtr's graph and returns schedule.

    - Values that you must re-  implement

    .buffrem : (min, max), option that this character will use bufrem property in union, card, etc.
    .jobtype : str, int, dex, luk. 사용하는 스탯의 종류를 명시해야 합니다. You must specify which type of stat this job uses.
    .vEnhanceNum : 5차 강화 스킬의 총 개수입니다.
    .vSkillNum : 5차 스킬의 총 개수입니다.
    """

    # TODO: vEhc is not used.
    def __init__(self, vEhc=None) -> None:
        self.buffrem: Tuple[int, int] = (0, 0)
        self.vEnhanceNum: int = 10
        self.vSkillNum: int = 3 + 3
        self.preEmptiveSkills: int = 0
        self.jobname: Optional[str] = None
        self.jobtype: str = "str"  # 재상속 하도록 명시할 필요가 있음.
        self._passive_skill_list = []  # 각 생성기가 자동으로 그래프 생성 시점에서 연산합니다.
        self.combat: int = 1
        self.ability_list: List[Ability_option] = Ability_tool.get_ability_set(
            None, None, None
        )
        self._use_critical_reinforce: bool = False
        self.hyperStatPrefixed: int = 0
        self.conf: dict = None

    def _load_skill(self, skill_name, vEhc, background_information={}):
        skill_conf = copy.deepcopy(self.conf['skills'][skill_name])
        if 'name' not in skill_conf:
            skill_conf['name'] = skill_name

        if skill_conf.get('tier', -1) == 5:
            lv = vEhc.getV(skill_conf['use_priority'], skill_conf['upgrade_priority'])
            background_information['lv'] = lv

        skill = load_skill(skill_conf, background_information)

        if skill_conf.get('enhanced_by_v', False):
            skill = skill.setV(
                vEhc,
                skill_conf['upgrade_priority'],
                skill_conf['v_increment'],
                skill_conf['v_crit']
            )

        return skill

    def load_skill_wrapper(self, skill_name, vEhc=None):
        background_information = self.conf.get('constant', {})
        background_information['combat'] = self.combat
        skill = self._load_skill(skill_name, vEhc, background_information=background_information)
        if isinstance(skill, DamageSkill):
            return skill.wrap(DamageSkillWrapper)
        elif isinstance(skill, BuffSkill):
            return skill.wrap(BuffSkillWrapper)
        elif isinstance(skill, SummonSkill):
            return skill.wrap(SummonSkillWrapper)

    def load(self, conf):
        if isinstance(conf, str):
            with open(conf, encoding='utf-8') as f:
                conf = json.load(f)
        
        self.conf = conf
        self.buffrem = conf.get('buffrem', (0, 0))
        self.vEnhanceNum = conf.get('vEnhanceNum', 10)
        self.vskillNum = conf.get('vSkillNum', 6)
        self.preEmptiveSkills = conf.get('preEmptiveSkills', 0)
        self.jobname = conf['jobname']
        self.jobtype = conf['jobtype']
        self._use_critical_reinforce = conf.get('use_critical_reinforce', False)       

    def get_ruleset(self) -> Optional[RuleSet]:
        return

    def get_predefined_rules(self, rule_type: str) -> List[policy.AbstractRule]:
        ruleset = self.get_ruleset()
        if ruleset is None:
            return []
        else:
            return ruleset.get_rules(rule_type)

    def get_total_modifier_optimization_hint(self) -> ExMDF:
        return self.get_modifier_optimization_hint().extend() + ExMDF(armor_ignore=20)

    def get_modifier_optimization_hint(self) -> CharacterModifier:
        """
        Modifier optimization에서 사용될 Modifier Hint를 기입합니다.

        """
        return CharacterModifier()

    def build(
        self,
        vEhc: AbstractVEnhancer,
        chtr: AbstractCharacter,
        options: Dict[str, Any],
        storage_handler=None,
    ) -> policy.StorageLinkedGraph:
        initialize_global_properties()

        base_element, all_elements = self.generate(vEhc, chtr, options)
        ensured_elements = [el for el in all_elements if el and el.ensure(chtr)]

        GlobalOperation.assign_storage()
        GlobalOperation.attach_namespace()
        GlobalOperation.save_storage()
        if storage_handler is not None:
            storage_handler(_unsafe_access_global_storage())
        GlobalOperation.convert_to_static()

        collection = GlobalOperation.export_collection()

        graph = policy.StorageLinkedGraph(
            base_element, collection.get_storage(), accessible_elements=ensured_elements
        )
        graph.build(chtr)

        return graph

    def generate(
        self, vEhc: AbstractVEnhancer, chtr: AbstractCharacter, options: Dict[str, Any]
    ) -> Tuple[DamageSkillWrapper, List[AbstractSkillWrapper]]:
        raise NotImplementedError

    def build_passive_skill_list(
        self, vEhc, chtr: AbstractCharacter, options: Dict[str, Any]
    ) -> None:
        self._passive_skill_list = self.get_passive_skill_list(vEhc, chtr, options)
        self._passive_skill_list += [InformedCharacterModifier("여제의 축복", att=30)]
        if self.jobname != "제로":
            self._passive_skill_list += [
                InformedCharacterModifier("연합의 의지", att=5, stat_main=5, stat_sub=5)
            ]

    def get_passive_skill_list(
        self, vEhc, chtr: AbstractCharacter, options: Dict[str, Any]
    ) -> List[InformedCharacterModifier]:
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        return [
            _get_loaded_object_with_mapping(opt, InformedCharacterModifier, passive_level=passive_level)
            for opt
            in self.conf['passive_skill_list']
        ]

    def build_not_implied_skill_list(
        self, vEhc, chtr: AbstractCharacter, options: Dict[str, Any]
    ) -> None:
        notImpliedBuffList = self.get_not_implied_skill_list(vEhc, chtr, options)
        self._passive_skill_list += notImpliedBuffList

    def get_not_implied_skill_list(
        self, vEhc, chtr: AbstractCharacter, options: Dict[str, Any]
    ) -> List[InformedCharacterModifier]:
        return [
            _get_loaded_object_with_mapping(opt, InformedCharacterModifier, combat=self.combat)
            for opt
            in self.conf['not_implied_skill_list']
        ]

    def get_passive_skill_modifier(self) -> ExMDF:
        passive_modifier = ExMDF()
        for _mdf in self._passive_skill_list:
            passive_modifier += _mdf
        return passive_modifier

    def package_bare(
        self,
        chtr: AbstractCharacter,
        v_builder: AbstractVBuilder,
        options: Dict[str, Any],
    ) -> policy.StorageLinkedGraph:
        vEhc = v_builder.build_enhancer(chtr, self)

        # Since given character specification already imply both option; ignore these two.

        self.build_not_implied_skill_list(vEhc, chtr, options)
        chtr.apply_modifiers([self.get_passive_skill_modifier()])

        graph = self.build(vEhc, chtr, options)
        graph.set_v_enhancer(vEhc)

        return graph

    def package(
        self,
        chtr: ItemedCharacter,
        v_builder: AbstractVBuilder,
        options: Dict[str, Any],
        ulevel: int,
        weaponstat: List[int],
        ability_grade: Ability_grade,
        log: bool = False,
        storage_handler=None,
    ) -> policy.StorageLinkedGraph:
        """Packaging function"""
        vEhc = v_builder.build_enhancer(chtr, self)
        chtr = chtr

        self.build_passive_skill_list(vEhc, chtr, options)
        self.build_not_implied_skill_list(vEhc, chtr, options)

        # 어빌리티 적용
        adjusted_ability = Ability_tool.adjusted_ability(
            ability_grade,
            self.ability_list[0],
            self.ability_list[1],
            self.ability_list[2],
        )
        chtr.apply_modifiers([self.get_passive_skill_modifier()])
        chtr.apply_modifiers([adjusted_ability])

        # 성향 적용
        personality = Personality.get_personality(100)
        chtr.apply_modifiers([personality])

        graph = self.build(vEhc, chtr, options, storage_handler=storage_handler)

        def log_modifier(modifier, name) -> None:
            if log:
                print("\n---" + name + "---")
                print(modifier.log())

        def log_character(character) -> None:
            if log:
                print("\n---basic CHTR---")
                print(character.get_base_modifier().log())

        def log_buffed_character(character) -> None:
            if log:
                print("\n---final---")
                buffed = (
                    graph.get_default_buff_modifier().extend()
                    + character.get_base_modifier()
                )
                print(buffed.log())

        # refMDF는 상시 - 시전되는 버프에 관련된 정보를 담고 있습니다.
        def get_reference_modifier(character) -> ExMDF:
            return (
                graph.get_default_buff_modifier().extend()
                + character.get_base_modifier()
                + self.get_total_modifier_optimization_hint()
            )

        log_character(chtr)
        log_buffed_character(chtr)

        # 무기 소울
        refMDF = get_reference_modifier(chtr)
        if refMDF.crit <= 65:
            weapon_soul_modifier = ExMDF(crit=12, att=20)
        else:
            weapon_soul_modifier = ExMDF(patt=3, att=20)
        log_modifier(weapon_soul_modifier, "weapon soul")
        chtr.apply_modifiers([weapon_soul_modifier])
        log_buffed_character(chtr)

        # 도핑
        doping = Doping.get_full_doping()
        log_modifier(doping, "doping")
        chtr.apply_modifiers([doping])
        log_buffed_character(chtr)

        # 유니온 공격대원
        unionCard = Card.get_card(self.jobtype, ulevel, True)
        log_modifier(unionCard, "union card")
        chtr.apply_modifiers([unionCard])
        log_buffed_character(chtr)

        # 링크 스킬
        refMDF = get_reference_modifier(chtr)
        link = LinkSkill.get_link_skill_modifier(refMDF, self.jobname)
        log_modifier(link, "link")
        chtr.apply_modifiers([link])
        log_buffed_character(chtr)

        # 하이퍼 스탯
        refMDF = get_reference_modifier(chtr)
        hyperstat = HyperStat.get_hyper_modifier(
            refMDF,
            chtr.level,
            self.hyperStatPrefixed,
            critical_reinforce=self._use_critical_reinforce,
        )
        log_modifier(hyperstat, "hyper stat")
        chtr.apply_modifiers([hyperstat])
        log_buffed_character(chtr)

        # 유니온 점령
        refMDF = get_reference_modifier(chtr)
        union = Union.get_union(
            refMDF,
            ulevel,
            buffrem=self.buffrem,
            critical_reinforce=self._use_critical_reinforce,
        )
        log_modifier(union, "union")
        chtr.apply_modifiers([union])
        log_buffed_character(chtr)

        # 무기류 잠재능력
        refMDF = get_reference_modifier(chtr)
        weapon_potential = WeaponPotential.get_weapon_pontential(
            refMDF, weaponstat[0], weaponstat[1]
        )
        for index, wp in enumerate(weapon_potential["weapon"]):
            log_modifier(wp, "weapon " + str(index + 1))
        for index, wp in enumerate(weapon_potential["subweapon"]):
            log_modifier(wp, "subweapon " + str(index + 1))
        for index, wp in enumerate(weapon_potential["emblem"]):
            log_modifier(wp, "emblem " + str(index + 1))
        chtr.set_weapon_potential(weapon_potential)
        log_buffed_character(chtr)

        # 그래프를 다시 빌드합니다.
        graph = self.build(vEhc, chtr, options, storage_handler=storage_handler)
        graph.set_v_enhancer(vEhc)

        log_character(chtr)
        log_buffed_character(chtr)

        return graph
