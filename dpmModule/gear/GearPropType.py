from enum import IntEnum


class GearPropType(IntEnum):
    STR = 1,  # STR
    STR_rate = 2,  # STR%
    DEX = 3,  # DEX
    DEX_rate = 4,  # DEX%
    INT = 5,  # INT
    INT_rate = 6,  # INT%
    LUK = 7,  # LUK
    LUK_rate = 8,  # LUK%
    MHP = 11,  # Maximum HP | 최대 HP
    MHP_rate = 12,  # Maximum HP% | 최대 HP%
    MMP = 13,  # Maximum MP | 최대 MP
    MMP_rate = 14,  # Maximum MP | 최대 MP
    att = 17,  # Attack | 공격력
    matt = 18,  # Magic Attack | 마력
    boss_pdamage = 32,  # Boss Damage | 보스 데미지%
    armor_ignore = 34,  # IED | 방어율 무시%
    pdamage = 36,  # Damage | 데미지%
    allstat = 40,  # All stat% # Not used in actual stats, but for applying all stats% | 올스탯% # 실제 스탯에는 사용되지 않고 올스탯% 추옵 적용을 위함
    crit = 90,  # Critical Rate | 크리티컬 확률
    crit_damage = 91,  # Critical Damage | 크리티컬 데미지

    att_rate = 100,  # Attack% | 공격력%
    matt_rate = 101,  # Magic Attack% | 마력%
    cooltime_reduce = 131,  # Cooldown reduction (Used for latent options and additional latent options) | 쿨타임 감소 (잠재옵션, 에디셔널 잠재옵션에 사용)
    pdamage_indep = 132,  # Final Damage% | 최종 데미지%
