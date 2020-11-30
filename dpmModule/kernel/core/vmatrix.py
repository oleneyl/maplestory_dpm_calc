from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from ..abstract import AbstractVBuilder, AbstractVEnhancer
from .modifier import CharacterModifier, VSkillModifier

if TYPE_CHECKING:
    from dpmModule.character.characterKernel import AbstractCharacter, JobGenerator
    from .skill import AbstractSkill


class BasicVEnhancer(AbstractVEnhancer):
    def __init__(self) -> None:
        #### value list ####
        self.enhance_list: List[int] = []
        self.v_skill_list: List[int] = []
        self.core_number = None  # TODO: Not used attribute.

        #### analytics list ####
        self.enhancer_priority: List[List[AbstractSkill]] = []  # 5차의 강화스킬 순서
        self.v_skill_priority: List[Dict[str, Any]] = []  # 5차의 사용스킬 순서

    def get_priority(self) -> Dict[str, List[Dict[str, Any]]]:
        v_skill_list_sorted: List[List[Dict[str, Any]]] = [
            [] for i in range(20)]  # 20 is magic number
        for vskill in self.v_skill_priority:
            v_skill_list_sorted[vskill["useIdx"]].append(vskill)

        return {
            "enhance": [{"name": skills[0].name.split('(')[0]} for skills in self.enhancer_priority if len(skills) > 0],
            "vskill": [{"name": skills[0]["target"].name.split('(')[0]} for skills in v_skill_list_sorted if len(skills) > 0]}

    def set_state_direct(self, li: List[int]) -> None:
        self.enhance_list = li
        self.enhancer_priority = [[] for i in li]

    def set_vlevel_direct(self, li: List[int]) -> None:
        self.v_skill_list = li

    def get_reinforcement_with_register(self, index: int, incr, crit: bool, target: AbstractSkill) -> CharacterModifier:
        self.enhancer_priority[index].append(target)

        if index >= len(self.enhance_list):
            return CharacterModifier()
        else:
            return VSkillModifier.get_reinforcement(incr, self.enhance_list[index], crit)

    def getV(self, use_index: int, upgrade_index: int) -> int:
        if use_index <= len(self.v_skill_list):
            return self.v_skill_list[upgrade_index]

    def add_v_skill(self, target: AbstractSkill, use_index: int, upgrade_index: int) -> None:
        self.v_skill_priority.append(
            {"target": target, "useIdx": use_index, "upgIdx": upgrade_index})

    def copy(self) -> BasicVEnhancer:
        retval = BasicVEnhancer()
        retval.set_state_direct(self.enhance_list)
        retval.set_vlevel_direct(self.v_skill_list)
        return retval

    def __repr__(self) -> str:
        return "VEnhancer :: dpmModule.jobs.template\nVEnhance : %s\nVSkill : %s" % (str(self.enhance_list), str(self.v_skill_list))


class DirectVBuilder(AbstractVBuilder):
    def __init__(self, direct_enhance_state: List[int], direct_v_state: List[int]) -> None:
        super().__init__()
        self.direct_enhance_state: List[int] = direct_enhance_state
        self.direct_v_state: List[int] = direct_v_state

    def build_enhancer(self, character, generator) -> BasicVEnhancer:
        enhancer = BasicVEnhancer()
        enhancer.set_state_direct(self.direct_enhance_state)
        enhancer.set_vlevel_direct(self.direct_v_state)
        return enhancer


class AlwaysMaximumVBuilder(AbstractVBuilder):
    def __init__(self) -> None:
        super().__init__()

    # TODO: character, generator are not used.
    def build_enhancer(self, character, generator) -> BasicVEnhancer:
        enhancer = BasicVEnhancer()
        enhancer.set_state_direct([60 for i in range(15)])
        enhancer.set_vlevel_direct([30 for i in range(15)])
        return enhancer


class NjbStyleVBuilder(AbstractVBuilder):
    def __init__(self, skill_core_level: int = 25, each_enhanced_amount: int = 17) -> None:
        super().__init__()
        self.skill_core_level: int = skill_core_level
        self.each_enhanced_amount: int = each_enhanced_amount

    def build_enhancer(self, character: AbstractCharacter, generator: JobGenerator) -> BasicVEnhancer:
        level = character.level
        cores = generator.vSkillNum
        return self.set_state_from_level_and_skill_cores(level, cores, self.skill_core_level, self.each_enhanced_amount)

    # TODO: each_enhanced_amount is not used.
    def set_state_from_level_and_skill_cores(self, level: int, skill_cores: int, skill_core_level: int,
                                             each_enhanced_amount) -> BasicVEnhancer:
        total_core_slots = 6 + (level - 200) // 5
        available_core_slots = max(total_core_slots - skill_cores, 0)
        level_bonus = level - 200

        enhance_state_will_be_setted = [0 for i in range(16)]

        if available_core_slots < 3:
            for i in range(available_core_slots):
                for j in range(3):
                    enhance_state_will_be_setted[j] += 17
        else:
            for i in range(available_core_slots):
                enhance_state_will_be_setted[i] = 50

        while level_bonus > 0:
            chance_for_upgrade = min(level_bonus, 5)
            target_upgrade_skill_index = 0

            enhancement_left = 3  # 하나의 코어는 3개의 스킬을 강화합니다.
            while target_upgrade_skill_index < len(enhance_state_will_be_setted) and enhancement_left > 0:
                if enhance_state_will_be_setted[target_upgrade_skill_index] < 60:
                    maximum_upgrade_level_available = 60 - \
                        enhance_state_will_be_setted[target_upgrade_skill_index]
                    actual_chance_for_upgrade = min(
                        chance_for_upgrade, maximum_upgrade_level_available)
                    enhance_state_will_be_setted[target_upgrade_skill_index] += actual_chance_for_upgrade
                    enhancement_left -= 1

                target_upgrade_skill_index += 1

            level_bonus -= chance_for_upgrade

        enhancer = BasicVEnhancer()
        enhancer.set_state_direct(enhance_state_will_be_setted)
        enhancer.set_vlevel_direct(
            [(i < skill_cores) * skill_core_level for i in range(10)])
        return enhancer
