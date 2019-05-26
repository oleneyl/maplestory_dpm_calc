from ..kernel import core

def create_auxilary_attack(skill_wrapper, ratio):
    original_skill = skill_wrapper.skill
    copial_skill = original_skill.copy()
    copial_skill.damage = copial_skill.damage * ratio
    #copial_skill.name = copial_skill.name + "_추가타"
    copial_skill.delay = 0
    skill_wrapper.onAfter(core.DamageSkillWrapper(copial_skill))
