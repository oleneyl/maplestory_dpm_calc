from ..kernel import core
from ..kernel.graph import DynamicVariableOperation


def create_auxilary_attack(skill_wrapper: core.DamageSkillWrapper, ratio=1, nametag="(복사)"):
    """
    create_auxilary_attack: DamageSkill Duplicator
    Easy Shadow Partner Function
    - parameters
      .skill_wrapper : target DamageSkillWrapper
      .ratio : copy skill's damage ratio
      .nametag : skill copier's name
    """
    original_skill = skill_wrapper.skill
    copial_skill = core.DamageSkill(
        name=DynamicVariableOperation.reveal_argument(original_skill.name) + nametag,
        delay=DynamicVariableOperation.wrap_argument(0),
        damage=original_skill.damage * DynamicVariableOperation.wrap_argument(ratio),
        hit=original_skill.hit,
        modifier=original_skill._static_skill_modifier,
    ).wrap(core.DamageSkillWrapper)

    copial_skill._runtime_modifier_list = skill_wrapper._runtime_modifier_list

    skill_wrapper.onJustAfter(copial_skill)


def get_weapon_att(chtr):
    return chtr.get_weapon_base_att()


def get_weapon_total_att(chtr):
    return chtr.get_weapon_total_att()


def get_starforce_count(chtr):
    return chtr.get_starforce_count()


def debug_skill(skill_wrapper):
    skill_wrapper.onJustAfter(
        core.BuffSkill(skill_wrapper._id + "(디버그)", 0, 1, cooltime=-1).wrap(
            core.BuffSkillWrapper
        )
    )


# 리부트 패시브
def reboot_passive(level=-1):
    if level == -1:
        raise ValueError
    return core.InformedCharacterModifier("리부트", att=5, pdamage=level // 2)
