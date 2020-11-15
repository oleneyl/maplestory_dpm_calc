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
    MHP = 11,  # 최대 HP
    MHP_rate = 12,  # 최대 HP%
    MMP = 13,  # 최대 MP
    MMP_rate = 14,  # 최대 MP
    att = 17,  # 공격력
    matt = 18,  # 마력
    boss_pdamage = 32,  # 보스 데미지%
    armor_ignore = 34,  # 방어율 무시%
    pdamage = 36,  # 데미지%
    allstat = 40,  # 올스탯% # 실제 스탯에는 사용되지 않고 올스탯% 추옵 적용을 위함

    att_rate = 100,  # 공격력%
    matt_rate = 101,  # 마력%
    crit = 106,  # 크리티컬 확률
    cooltime_reduce = 131,  # 쿨타임 감소 (잠재옵션, 에디셔널 잠재옵션에 사용)
    crit_damage = 141,  # 크리티컬 데미지

    tuc = 201,  # 최대 업그레이드 가능 횟수 (황금 망치 제외)
    set_item_id = 202,  # 세트아이템 ID
    boss_reward = 204,  # 보스 보상 (무기의 공격력/마력 추옵 계산에만 사용)

    req_level = 1000,  # 착용 제한 레벨
    req_job = 1005,  # 착용 제한 직업 (초보자=0/전사=1/마법사=2/궁수=4/도적=8/해적=16)

    superior_eqp = 1116,  # 슈페리얼
    joker_to_set_item = 1121,  # 럭키아이템

    amazing_scroll = 10000,  # 놀장 적용 여부
