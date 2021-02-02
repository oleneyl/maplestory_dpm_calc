from __future__ import annotations

from math import ceil
from typing import Any, Dict, List, Tuple
from typing import Union as UnionType

from ..kernel.core import ExtendedCharacterModifier as ExMDF


class Union:
    peoples = [
        0,
        9,
        10,
        11,
        12,
        13,
        18,
        19,
        20,
        21,
        22,
        27,
        28,
        29,
        30,
        31,
        36,
        37,
        38,
        39,
        40,
    ]

    maxSlot = [6, 13, 21, 30, 40]
    # hierarchy : 공 - 주스텟 - 보공 - 방무 - 크확 - 크뎀 - 벞지
    # links : 연결가능한 경로 제공.
    # 기본적으로 보공과 방무를 연결합니다. 6칸씩 버림.(12칸)

    initial_state = [6, 6, 1, 1, 0, 0, 0]

    def __init__(self, mdf: ExMDF, buff_rem: Tuple[int, int], slots, ulevel: int):
        self.mdf: ExMDF = mdf
        self.buff_rem: Tuple[int, int] = buff_rem
        self.slots = slots
        self.ulevel: int = ulevel

    def as_dict(self) -> Dict[str, Any]:
        return {
            "mdf": self.mdf.as_dict(),
            "buffrem": self.buff_rem,
            "slots": self.slots,
            "ulevel": self.ulevel,
        }

    @staticmethod
    def get_apt_slot(ulevel: int, maplem=True) -> int:
        """get_apt_slot(ulevel, maplem = True) : Return Apt union slot.
        유니온 캐릭터는 기본적으로 200레벨 하나를 가지며, 유니온 레벨을 맞추기 위한 최소한의 200레벨 캐릭터를 가집니다.
        """
        limit = Union.peoples[ulevel // 500]
        numOf200 = min(max(ceil((ulevel - 5600) / 60), 1), limit)
        return numOf200 * 4 + (limit - numOf200) * 3 + (maplem * 3)

    # TODO :: -1을 리턴하지 않도록,
    @staticmethod
    def get_union_object(
        mdf: ExMDF,
        jobname: str,
        ulevel: int,
        buffrem: Tuple[int, int],
        asIndex: bool = False,
        slot=None,
    ) -> Union:
        mdf, buffrem = Union.get_union(
            mdf, jobname, ulevel, buffrem=buffrem, asIndex=asIndex, slot=slot
        )
        return Union(mdf, buffrem, -1, ulevel)

    @staticmethod
    def get_union(
        mdf: ExMDF,
        jobname: str,
        ulevel: int,
        buffrem: Tuple[int, int],
        asIndex: bool = False,
        slot=None,
        critical_reinforce: bool = False,
    ) -> UnionType[ExMDF, List[int]]:
        """get_union(mdf, ulevel, buffrem, asIndex=False, slot=None, critical_reinforce=False) : return optimized ExMDF value.
        return value : (ExMDF, buffremain) tuple.
        """
        if slot is None:
            slots = Union.get_apt_slot(ulevel)
        else:
            slots = slot
        maxvalue = Union.maxSlot[min((ulevel - 2000) // 1000, 4)]

        buffrem_min, buffrem_max = buffrem

        state = [i for i in Union.initial_state]
        slots -= sum(state)

        while state[6] < buffrem_min and slots > 0:
            state[6] += 1
            slots -= 1

        while slots > 0:
            idx = -1
            eff = 0
            for i in range(6):
                _state = [j for j in state]
                _state[i] = min(_state[i] + 1, maxvalue)
                _eff = Union._get_union_increment_from_state(
                    mdf, jobname, _state, critical_reinforce=critical_reinforce
                )
                if _eff > eff:
                    idx = i
                    eff = _eff
            if idx == -1:
                if (Union._get_union_from_state(state, jobname) + mdf).armor_ignore < 66.7:
                    idx = 3
                else:
                    for i in range(6):
                        _state = [j for j in state]
                        _state[i] = min(_state[i] + 1, maxvalue)
                        _eff = Union._get_union_increment_from_state(
                            mdf, jobname, _state, critical_reinforce=critical_reinforce
                        )
                        print(_state, _eff)
                        if _eff > eff:
                            idx = i
                            eff = _eff
                    print("Current state : %s\nslots : %d\n" % (str(state), slots))
                    raise ArithmeticError("Something gonna wrong")
            if idx in [0, 1] and state[6] < min(
                buffrem_max, maxvalue
            ):  # 보공, 방무, 크확, 크뎀 점령이 끝났으면 벞지를 추가 수급
                idx = 6
            state[idx] += 1
            slots -= 1

            if state[6] >= 6 and state[0] >= 6:  # 벞지가 6칸 이상이면 벞지-방무를 이어서 내부 점령 1칸을 절약함
                state[0] -= 1
                slots += 1

        if asIndex:
            return state
        else:
            if state[3] > 100:
                print(state)
                raise ValueError("something gonna wrong")
            return Union._get_union_from_state(state, jobname)

    @staticmethod
    def _get_union_increment_from_state(
        mdf: ExMDF, jobname: str, state: List[int], critical_reinforce: bool = False
    ):
        mdfCopy = mdf + Union._get_union_from_state(state, jobname)
        if critical_reinforce:
            mdfCopy += ExMDF(crit_damage=max(0, mdfCopy.crit) * 0.125)
        return mdfCopy.get_damage_factor()

    @staticmethod
    def _get_union_from_state(state: List[int], jobname: str) -> ExMDF:
        return (
            ExMDF(att=state[0])
            + (ExMDF(stat_main=250 * state[1]) if jobname == "데몬어벤져" else ExMDF(stat_main=5 * state[1]))
            + ExMDF(boss_pdamage=state[2])
            + ExMDF(armor_ignore=state[3])
            + ExMDF(crit=state[4])
            + ExMDF(crit_damage=state[5] * 0.5)
            + ExMDF(buff_rem=state[6])
        )


class Card:
    """
    10/20/40/80/100
    힘캐 : 8
    법캐 : 7
    덱 : 4
    럭 : 5
    5/10/15/20
    공마 : 1

    1/2/3/4/5
    크리율 : 2

    4/6/8/10/12
    소환수 : 1

    250/500/100/2000/2500
    체력 : 2

    아란 : 피회복
    에반 : 마나회복
    메르 : 쿨감 2/3/4/5/6
    팬텀 : 메획 1/2/3/4/5

    1/2/3/5/6
    크뎀 : 1
    방무 : 1
    보공 : 1

    0.8/1.6/2.4/3.2/4 뎀증
    와헌

    벞지 5/10/15/20/25
    메카

    제논 : 힘덱럭 5/10/20/40/50

    제로 : 경치

    닼나 : 체력% 2/3/4/5/6
    소마/미하일 : 체력 250/500/1000/2000/2500
    """

    # 주스텟 / 부스텟 / 크리 / 공마 / 크뎀 / 보공 / 방무 / 총뎀 / 제논 / 쿨감 / 벞지
    CList = [
        [ExMDF(stat_main_fixed=i) for i in [10, 20, 40, 80, 100]],
        [ExMDF(stat_sub_fixed=i) for i in [10, 20, 40, 80, 100]],
        [ExMDF(crit=i) for i in [1, 2, 3, 4, 5]],
        [ExMDF(att=i) for i in [5, 10, 15, 20, None]],
        [ExMDF(crit_damage=i) for i in [1, 2, 3, 5, 6]],
        [ExMDF(armor_ignore=i) for i in [1, 2, 3, 5, 6]],
        [ExMDF(boss_pdamage=i) for i in [1, 2, 3, 5, 6]],
        [ExMDF(pdamage=i) for i in [0.8, 1.6, 2.4, 3.2, 4]],
        [ExMDF(stat_main_fixed=i, stat_sub_fixed=i) for i in [5, 10, 20, 40, 50]],
        [ExMDF(pcooltime_reduce=i) for i in [2, 3, 4, 5, 6]],
        [ExMDF(buff_rem=i) for i in [5, 10, 15, 20, 25]],
        [ExMDF(stat_main_fixed=i * 3) for i in [5, 10, 20, 40, 50]],  # 제논 전용 제논 공격대원
        [ExMDF(stat_main_fixed=i) for i in [250, 500, 1000, 2000, 2500]],  # 데벤 전용 고정HP
        [ExMDF(pstat_main=i) for i in [2, 3, 4, 5, 6]],  # 데벤 전용 HP%
    ]

    priority = {
        "STR": {  # 크확, 크뎀, 방무, 보공, 뎀퍼, 쿨감, 벞지, 주스탯, 제논, 부스탯
            "order": [2, 4, 5, 6, 7, 9, 10, 0, 8, 1],
            "max": [8, 5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        },
        "DEX": {
            "order": [2, 4, 5, 6, 7, 9, 10, 0, 8, 1],
            "max": [5, 8, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        },
        "INT": {
            "order": [2, 4, 5, 6, 7, 9, 10, 0, 8, 1],
            "max": [7, 5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        },
        "LUK": {
            "order": [2, 4, 5, 6, 7, 9, 10, 0, 8, 1],
            "max": [5, 5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        },
        "LUK2": {
            "order": [2, 4, 5, 6, 7, 9, 10, 0, 8, 1],
            "max": [5, 13, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        },
        "HP": {  # 크확, 크뎀, 방무, 보공, 뎀퍼, 쿨감, 벞지, 체력%, 체력, 힘
            "order": [2, 4, 5, 6, 7, 9, 10, 12, 13, 1],
            "max": [0, 8, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 1],
        },
        "xenon": {  # 크확, 크뎀, 방무, 보공, 뎀퍼, 쿨감, 벞지, 제논, 주스탯
            "order": [2, 4, 5, 6, 7, 9, 10, 11, 0],
            "max": [18, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        },
    }

    @staticmethod
    def get_apt_slot(ulevel: int, maplem: bool = True) -> List[int]:
        """get_apt_slot(ulevel, maplem = True) : Return Apt union slot.
        유니온 캐릭터는 2000레벨부터 300레벨당 200짜리가 1개씩 증가합니다. 기본적으로 하나를 가집니다.
        점령 가능한 개수는 아래와 같습니다.

        리턴 값 타입 : 200레벨의 수, 140레벨의 수
        """
        numOf200 = min((ulevel - 2000) // 300 + 1, Union.peoples[ulevel // 500])
        _else = (ulevel - numOf200 * 200) // 140
        return [
            numOf200,
            min(_else, Union.peoples[ulevel // 500] - numOf200) + (maplem * 1),
        ]

    # TODO define Character Cards
    @staticmethod
    def get_card(jobtype: str, ulevel: int, maplem: bool = True) -> ExMDF:
        """get_card : 캐릭터카드 효과를 리턴합니다.
        리턴 형태 : Modifier
        """
        # TODO: 실행을 위해 임시로 변환
        if jobtype not in ["STR", "DEX", "INT", "LUK", "LUK2", "HP", "xenon"]:
            raise TypeError("jobtype must str, dex, int or luk, get:" + str(jobtype))
        retmdf = ExMDF()
        card_4, card_3 = Card.get_apt_slot(ulevel, maplem=maplem)
        order = [i for i in Card.priority[jobtype]["order"]]
        lefts = [i for i in Card.priority[jobtype]["max"]]
        currentorder = 0
        while card_4 + card_3 > 0:
            if currentorder >= len(order):
                break
            idx = order[currentorder]
            if lefts[idx] == 0:
                currentorder += 1
                continue
            if card_4 > 0:
                retmdf += Card.CList[idx][3]
                card_4 -= 1
            else:
                retmdf += Card.CList[idx][2]
                card_3 -= 1
            lefts[idx] -= 1

        if maplem:
            retmdf += Card.CList[3][2]
        return retmdf
