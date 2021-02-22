from enum import Enum

from ...kernel import core
from ...kernel.core.utilities import Language


class WarriorSkills(Enum):
    WeaponAura = Language('Weapon Aura', '오라 웨폰')  # Taken from https://maplestory.fandom.com/wiki/Weapon_Aura


class AuraWeaponBuilder:
    def __init__(
        self,
        enhancer,
        skill_importance: int,
        enhance_importance: int,
        modifier=core.CharacterModifier(),
        hit=6,
        lang='ko'
    ):
        self.AuraWeaponBuff = (
            core.BuffSkill(
                f"{WarriorSkills.WeaponAura.value[lang]}(Buff | 버프)",  # Weapon Aura (Buff)
                delay=720,
                remain=(80 + 2 * enhancer.getV(skill_importance, enhance_importance)) * 1000,
                cooltime=180 * 1000,
                red=True,
                armor_ignore=15,
                pdamage_indep=(
                    enhancer.getV(skill_importance, enhance_importance) // 5
                ),
            )
            .isV(enhancer, skill_importance, enhance_importance)
            .wrap(core.BuffSkillWrapper)
        )
        self.AuraWeapon = core.DamageSkill(
            f"{WarriorSkills.WeaponAura.value[lang]}(Wave | 파동)",  # Weapon Aura (Wave)
            delay=0,
            damage=500 + 20 * enhancer.getV(skill_importance, enhance_importance),
            hit=hit,
            modifier=modifier,
            cooltime=5000,
        ).wrap(core.DamageSkillWrapper)

        self.AuraWeapon.protect_from_running()
        self.AuraWeaponOptional = core.OptionalElement(
            lambda: (
                self.AuraWeapon.is_available() and self.AuraWeaponBuff.is_active()
            ),
            self.AuraWeapon,
        )

    def add_aura_weapon(self, origin_skill):
        if getattr(origin_skill, "is_periodic", False):
            origin_skill.onTick(self.AuraWeaponOptional)
        else:
            origin_skill.onAfter(self.AuraWeaponOptional)

    def get_buff(self):
        return self.AuraWeaponBuff, self.AuraWeapon
