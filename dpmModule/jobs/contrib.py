from ..kernel import core
from ..kernel.graph import DynamicVariableOperation
def create_auxilary_attack(skill_wrapper, ratio, nametag = '복사'):
    original_skill = skill_wrapper.skill
    copial_skill = core.DamageSkill(name = DynamicVariableOperation.reveal_argument(original_skill.name) + nametag,
        delay = DynamicVariableOperation.wrap_argument(0),
        damage = original_skill.damage * DynamicVariableOperation.wrap_argument(ratio),
        hit = original_skill.hit,
        modifier=original_skill._static_skill_modifier).wrap(core.DamageSkillWrapper)
    
    skill_wrapper.onAfter(copial_skill)
