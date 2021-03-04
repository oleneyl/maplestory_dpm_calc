from ..kernel import core

from localization.utilities import translator
_ = translator.gettext

"""
Oz rings

Excluding rings with low efficiency such as health cut, mana cut, limit, or no deal contribution such as Swift and Overpass

TODO: Ring of ??, Durability, Ultimatum

시드링

헬스컷, 마나컷, 리밋 등 효율이 낮거나 스위프트, 오버패스 등 딜 기여가 없는 링은 제외

TODO: 링오브썸, 듀라빌리티, 얼티메이덤
"""


# English Oz Ring effects and names can be found here https://maplestory.fandom.com/wiki/Miscellaneous_Skills#Equipment_Skills
# and here https://dexless.com/guides/tower-of-oz-comprehensive-guide.145/
class OzRings:
    RingofRestraint = _("리스트레인트 링")  # "Ring of Restraint"
    # UltimatumRing = _("")  # "Ultimatum Ring"
    # LimitRing = _("")  # "Limit Ring"
    # HealthCutRing = _("")  # "Health Cut Ring"
    # ManaCutRing = _("")  # "Mana Cut Ring"
    # CriticalShiftRing = _("")  # "Critical Shift Ring"
    WeaponJumpRing = _("웨폰퍼프 링")  # "Weapon Jump Ring"
    CriticalDamageRing = _("크리데미지 링")  # "Critical Damage Ring"
    CriticalDefenseRing = _("크리디펜스 링")  # "Critical Defense Ring"
    LevelJumpRing = _("레벨퍼프 링")  # "Level Jump Ring"
    RiskTakerRing = _("리스트테이커 링")  # "Risk Taker Ring"
    CrisisHMRing = _("크라이시스 H/M 링")  # "Crisis HM Ring"


def restraint_ring(level: int):
    return core.BuffSkill(
        OzRings.RingofRestraint,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        patt=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crisis_hm_ring(level: int):
    return core.BuffSkill(
        OzRings.CrisisHMRing,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        patt=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def risktaker_ring(level: int):
    return core.BuffSkill(
        OzRings.RiskTakerRing,
        delay=60,
        remain=(6+6*level)*1000,
        cooltime=180000,
        patt=(level+1)*10,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crisis_ring(level: int):
    return core.BuffSkill(
        OzRings.CrisisHMRing,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        patt=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def weaponpuff_ring(level: int, weapon_att: int):
    return core.BuffSkill(
        OzRings.WeaponJumpRing,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        stat_main=level * weapon_att,
        red=True
    ).wrap(core.BuffSkillWrapper)


def demonavenger_weaponpuff_ring(level: int, weapon_att: int):
    return core.BuffSkill(
        f"{OzRings.WeaponJumpRing}({_('데몬어벤져')})",
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        stat_main=level * weapon_att * 17.5,
        red=True
    ).wrap(core.BuffSkillWrapper)


def levelpuff_ring(level: int, chtr_level: int):
    return core.BuffSkill(
        OzRings.WeaponJumpRing,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        stat_main=(2+7*level)*0.1*chtr_level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def demonavenger_levelpuff_ring(level: int, chtr_level: int):
    return core.BuffSkill(
        f"{OzRings.LevelJumpRing}({_('데몬어벤져')})",
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        stat_main=(2+7*level)*0.1*chtr_level*17.5,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crit_damage_ring(level: int):
    return core.BuffSkill(
        OzRings.CriticalDamageRing,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        crit_damage=7*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crit_defense_ring(level: int):
    # 100% assumption. 크확 100% 가정.
    return core.BuffSkill(
        OzRings.CriticalDefenseRing,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        armor_ignore=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)
