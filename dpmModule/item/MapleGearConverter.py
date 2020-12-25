from ..kernel.core import ExtendedCharacterModifier as ExMDF
from . import ItemKernel as it
from .maplegear.Gear import Gear
from .maplegear.GearPropType import GearPropType

stat_dict = {
             "STR" : [GearPropType.STR, GearPropType.STR_rate],
             "DEX" : [GearPropType.DEX, GearPropType.DEX_rate],
             "INT" : [GearPropType.INT, GearPropType.INT_rate],
             "LUK" : [GearPropType.LUK, GearPropType.LUK_rate],
             "HP" : [GearPropType.MHP, GearPropType.MHP_rate]
            }

def convert_option_mdf(propType, chtr_stat):
    # 고정스탯을 포함한 일부 정보는 누락됨

    # 주스탯
    modifier = ExMDF(stat_main=propType[chtr_stat[0][0]],
                      pstat_main=propType[chtr_stat[0][1]] + propType[GearPropType.allstat])

    if chtr_stat[2] is None:
        # 부스탯 1개
        modifier += ExMDF(stat_sub=propType[chtr_stat[1][0]],
                          pstat_sub=propType[chtr_stat[1][1]] + propType[GearPropType.allstat])
    else:
        # 부스탯 2개
        # 부스탯퍼 중복적용 방지를 위해 임시로 최대값 적용중 (ex: 부스탯1 9퍼 + 부스탯2 6퍼)
        # 더 정확한 계산을 위해서는 수정 필요
        modifier += ExMDF(stat_sub=propType[chtr_stat[1][0]]+propType[chtr_stat[2][0]],
                          pstat_sub=max(propType[chtr_stat[1][1]], propType[chtr_stat[2][1]]) + propType[GearPropType.allstat])
    
    modifier += ExMDF(
        crit=propType[GearPropType.crit],
        crit_damage=propType[GearPropType.crit_damage],
        pdamage=propType[GearPropType.pdamage],
        pdamage_indep=0,  # TODO: can't find it in Gear but required (루인포스실드 등)
        boss_pdamage=propType[GearPropType.boss_pdamage],
        armor_ignore=propType[GearPropType.armor_ignore],
        cooltime_reduce=propType[GearPropType.cooltime_reduce]  # TODO: Gear 저장값이 초단위인지 밀리초인지 확인바람
    )

    if chtr_stat[0][0] == GearPropType.INT:  # 마력직업인지 공격력직업인지 확인
        modifier += ExMDF(
            att=propType[GearPropType.matt],
            patt=propType[GearPropType.matt_rate]
        )
    else:
        modifier += ExMDF(
            att=propType[GearPropType.att],
            patt=propType[GearPropType.att_rate]
        )
    return modifier


def gear_to_item(gear: Gear, stat_main: str, stat_sub: str, stat_sub2: str = None) -> it.Item:
    # 주스탯 판별
    if stat_sub2 is None:
        chtr_stat = [stat_dict[stat_main], stat_dict[stat_sub], None]
    else:
        chtr_stat = [stat_dict[stat_main], stat_dict[stat_sub], stat_dict[stat_sub2]]
    
    # 장비 옵션 합치기
    
    modifier = ExMDF()
    each_stat = [gear.base_stat, gear.additional_stat, gear.scroll_stat, gear.star_stat, gear.potential, gear.additional_potential]

    for index in each_stat:
        modifier += convert_option_mdf(index, chtr_stat)

    item = it.Item(name=gear.name, level=gear.props[GearPropType.req_level], main_option=modifier)

    return item

