from enum import Enum

from ..kernel import core


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
class OzRings(Enum):
    RingofRestraint = 'Ring of Restraint | 리스트레인트 링'
    UltimatumRing = 'Ultimatum Ring | '
    LimitRing = 'Limit Ring | '
    HealthCutRing = 'Health Cut Ring | '
    ManaCutRing = 'Mana Cut Ring | '
    CriticalShiftRing = 'Critical Shift Ring | '
    WeaponJumpRing = 'Weapon Jump Ring | 웨폰퍼프 링'
    CriticalDamageRing = 'Critical Damage Ring | 크리데미지 링'
    CriticalDefenseRing = 'Critical Defense Ring | 크리디펜스 링'
    LevelJumpRing = 'Level Jump Ring | 레벨퍼프 링'
    RiskTakerRing = 'Risk Taker Ring | 리스트테이커 링'
    CrisisHMRing = 'Crisis HM Ring | 크라이시스 H/M 링'

def restraint_ring(level: int):
    return core.BuffSkill(
        OzRings.RingofRestraint.value,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        patt=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crisis_hm_ring(level: int):
    return core.BuffSkill(
        OzRings.CrisisHMRing.value,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        patt=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def risktaker_ring(level: int):
    return core.BuffSkill(
        OzRings.RiskTakerRing.value,
        delay=60,
        remain=(6+6*level)*1000,
        cooltime=180000,
        patt=(level+1)*10,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crisis_ring(level: int):
    return core.BuffSkill(
        OzRings.CrisisHMRing.value,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        patt=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def weaponpuff_ring(level: int, weapon_att: int):
    return core.BuffSkill(
        OzRings.WeaponJumpRing.value,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        stat_main=level * weapon_att,
        red=True
    ).wrap(core.BuffSkillWrapper)


def demonavenger_weaponpuff_ring(level: int, weapon_att: int):
    return core.BuffSkill(
        f"{OzRings.WeaponJumpRing.value}(Demon Avenger | 데몬어벤져)",
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        stat_main=level * weapon_att * 17.5,
        red=True
    ).wrap(core.BuffSkillWrapper)


def levelpuff_ring(level: int, chtr_level: int):
    return core.BuffSkill(
        OzRings.WeaponJumpRing.value,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        stat_main=(2+7*level)*0.1*chtr_level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def demonavenger_levelpuff_ring(level: int, chtr_level: int):
    return core.BuffSkill(
        f"{OzRings.LevelJumpRing.value}(Demon Avenger | 데몬어벤져)",
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        stat_main=(2+7*level)*0.1*chtr_level*17.5,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crit_damage_ring(level: int):
    return core.BuffSkill(
        OzRings.CriticalDamageRing.value,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        crit_damage=7*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crit_defense_ring(level: int):
    # 100% assumption. 크확 100% 가정.
    return core.BuffSkill(
        OzRings.CriticalDefenseRing.value,
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        armor_ignore=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)
