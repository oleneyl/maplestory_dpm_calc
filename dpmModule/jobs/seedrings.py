from ..kernel import core


"""
시드링

헬스컷, 마나컷, 리밋 등 효율이 낮거나 스위프트, 오버패스 등 딜 기여가 없는 링은 제외

TODO: 링오브썸, 듀라빌리티, 얼티메이덤
"""


def restraint_ring(level: int):
    return core.BuffSkill(
        "리스트레인트 링",
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        patt=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crisis_hm_ring(level: int):
    return core.BuffSkill(
        "크라이시스-HM링",
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        patt=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def risktaker_ring(level: int):
    return core.BuffSkill(
        "리스크테이커 링",
        delay=60,
        remain=(6+6*level)*1000,
        cooltime=180000,
        patt=(level+1)*10,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crisis_ring(level: int):
    return core.BuffSkill(
        "크라이시스 H/M 링",
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        patt=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def weaponpuff_ring(level: int, weapon_att: int):
    return core.BuffSkill(
        "웨폰퍼프 링",
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        stat_main=level * weapon_att,
        red=True
    ).wrap(core.BuffSkillWrapper)


def levelpuff_ring(level: int, chtr_level: int):
    return core.BuffSkill(
        "레벨퍼프 링",
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        stat_main=(2+7*level)*0.1*chtr_level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crit_damage_ring(level: int):
    return core.BuffSkill(
        "크리데미지 링",
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        crit_damage=7*level,
        red=True
    ).wrap(core.BuffSkillWrapper)


def crit_defense_ring(level: int):
    # 크확 100% 가정
    return core.BuffSkill(
        "크리디펜스 링",
        delay=60,
        remain=(7+2*level)*1000,
        cooltime=180000,
        armor_ignore=25*level,
        red=True
    ).wrap(core.BuffSkillWrapper)
