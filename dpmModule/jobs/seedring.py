from ..kernel import core

# TODO: 약칭을 사용 가능하도록 수정필요
# 헬스컷, 마나컷, 리밋 등 효율이 낮거나 스위프트, 오버패스 등 딜 기여가 없는 링은 제외

"""
시드링 (기본 4레벨)

TODO: 링오브썸, 듀라빌리티, 얼티메이덤
"""


def restraint_ring(level: int = 4):
    return core.BuffSkill(
        "리스트레인트 링",
        delay=0,
        remain=(7+2*level)*1000,
        cooltime=180000,
        patt=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def risktaker_ring(level: int = 4):
    return core.BuffSkill(
        "리스트테이커 링",
        delay=0,
        remain=(6+6*level)*1000,
        cooltime=180000,
        patt=(level+1)*10,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crisis_ring(level: int = 4):
    return core.BuffSkill(
        "크라이시스 H/M 링",
        delay=0,
        remain=(7+2*level)*1000,
        cooltime=180000,
        patt=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def weaponpuff_ring(level: int = 4, weapon_att: int = -1):
    if weapon_att == -1:
        raise ValueError
    return core.BuffSkill(
        "웨폰퍼프 링",
        delay=0,
        remain=(7+2*level)*1000,
        cooltime=180000,
        stat_main=level * weapon_att,
        red=True
    ).wrap(core.BuffSkillWrapper)


def levelpuff_ring(level: int = 4, chtr_level: int = -1):
    if chtr_level == -1:
        raise ValueError
    return core.BuffSkill(
        "레벨퍼프 링",
        delay=0,
        remain=(7+2*level)*1000,
        cooltime=180000,
        stat_main=(2+7*level)*0.1*chtr_level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crit_damage_ring(level: int = 4):
    return core.BuffSkill(
        "크리데미지 링",
        delay=0,
        remain=(7+2*level)*1000,
        cooltime=180000,
        crit_damage=7*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crit_defense_ring(level: int = 4):
    # 크확 100% 가정
    return core.BuffSkill(
        "크리디펜스 링",
        delay=0,
        remain=(7+2*level)*1000,
        cooltime=180000,
        armor_ignore=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)
