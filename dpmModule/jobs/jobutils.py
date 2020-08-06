from ..kernel import core
from ..kernel.graph import DynamicVariableOperation
from ..item import *

def create_auxilary_attack(skill_wrapper, ratio, nametag = '복사'):
    original_skill = skill_wrapper.skill
    copial_skill = core.DamageSkill(name = DynamicVariableOperation.reveal_argument(original_skill.name) + nametag,
        delay = DynamicVariableOperation.wrap_argument(0),
        damage = original_skill.damage * DynamicVariableOperation.wrap_argument(ratio),
        hit = original_skill.hit,
        modifier=original_skill._static_skill_modifier).wrap(core.DamageSkillWrapper)
    
    skill_wrapper.onAfter(copial_skill)

# 스펙 측정시마다 수동으로 변경 필요

def get_weapon_att(WEAPON_NAME, spec = 6000):
    if spec < 5000:
        #파프
        return RootAbyss.WeaponFactory.getWeapon(WEAPON_NAME, star = 0, elist = [0,0,0,0] ).att
    elif spec < 7000:
        #앱솔
        return Absolab.WeaponFactory.getWeapon(WEAPON_NAME, star = 0, elist = [0,0,0,0] ).att
    else:
        #아케인
        return Arcane.WeaponFactory.getWeapon(WEAPON_NAME, star = 0, elist = [0,0,0,0] ).att