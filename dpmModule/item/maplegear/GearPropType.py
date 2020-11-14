from enum import IntEnum


class GearPropType(IntEnum):
    STR = 1,
    STR_rate = 2,
    DEX = 3,
    DEX_rate = 4,
    INT = 5,
    INT_rate = 6,
    LUK = 7,
    LUK_rate = 8,
    MHP = 11,
    MHP_rate = 12,
    MMP = 13,
    MMP_rate = 14,
    att = 17,
    matt = 18,
    boss_pdamage = 32,
    armor_ignore = 34,
    pdamage = 36,
    allstat = 40,

    att_rate = 100,
    matt_rate = 101,
    crit = 106,
    cooltime_reduce = 131,
    crit_pdamage = 141,

    tuc = 201,
    set_item_id = 202,
    boss_reward = 204,

    req_level = 1000,
    req_job = 1005,

    superior_eqp = 1116,
    joker_to_set_item = 1121,

    amazing_scroll = 10000,
