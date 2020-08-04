from ..kernel import core
from ..kernel.graph import DynamicVariableOperation

def debug_damage_skill(skill_wrapper):
    skill_wrapper.onBefore(core.BuffSkill(DynamicVariableOperation.reveal_argument(skill_wrapper.skill.name)+"(디버그)", 0, 1, cooltime = -1).wrap(core.BuffSkillWrapper))