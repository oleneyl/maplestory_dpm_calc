from typing import Any, Dict, List, Union

from ..kernel.core import ExtendedCharacterModifier as ExMDF
from ..kernel.core import CharacterModifier as MDF
from itertools import product
from functools import reduce
from operator import itemgetter


class HyperStat:
    def __init__(self, mdf: ExMDF, level: int) -> None:
        self.mdf: ExMDF = mdf
        self.level: int = level

    def as_dict(self) -> Dict[str, Any]:
        return {"mdf": self.mdf.as_dict(), "level": self.level}

    @staticmethod
    def get_point(level: int) -> int:
        """get_point(level) : return hyperstat point of given level."""
        delta = level - 140
        return (delta // 10) * (30 + (delta // 10 + 2) * 10) // 2 + (delta % 10 + 1) * (
            delta // 10 + 3
        )

    @staticmethod
    def optimize(enhancement: List[ExMDF], ref: ExMDF, point: int) -> int:
        req, mdf = max(
            [
                (req, reduce(lambda x, y: x + y, mdf, ExMDF()))
                for req, mdf in [
                    x
                    for x in [
                        (sum(map(itemgetter(0), el)), list(map(itemgetter(1), el)))
                        for el in product(*enhancement)
                    ]
                    if x[0] <= point
                ]
            ]
            + [(0, ExMDF())],
            key=lambda x: (ref + x[1]).get_damage_factor(),
        )
        return req, mdf

    @staticmethod
    def get_hyper_index(
        ref_mdf: ExMDF,
        level: int,
        prefixed: int,
        isIndex: bool = True,
        critical_reinforce: bool = False,
    ) -> Union[List[int], ExMDF]:
        """get_hyper_index(mdf, level) : return enhancement index for matching enhancement type."""
        point = HyperStat.get_point(level) - prefixed
        requirement = [
            0,
            1,
            3,
            7,
            15,
            25,
            40,
            60,
            85,
            115,
            150,
            200,
            265,
            345,
            440,
            550,
            9999,
        ]

        matrix = [
            [(requirement[i], MDF(stat_main_fixed=30 * i)) for i in range(1, 7)],
            [(requirement[i], MDF(stat_sub_fixed=30 * i)) for i in range(1, 5)],
            [(requirement[i], MDF(att=3 * i)) for i in range(1, 7)],
            [(requirement[i], MDF(armor_ignore=3 * i)) for i in range(1, 16)],
            [
                (x[0] + y[0], x[1] + y[1])
                for x, y in product(
                    [(requirement[i], MDF(crit=1 * i)) for i in range(1, 6)]
                    + [
                        (requirement[i], MDF(crit=5 + 2 * (i - 5)))
                        for i in range(6, 10)
                    ],
                    [(requirement[i], MDF(crit_damage=1 * i)) for i in range(8, 16)],
                )
            ],
            [
                (x[0] + y[0], x[1] + y[1])
                for x, y in product(
                    [(requirement[i], MDF(pdamage=3 * i)) for i in range(8, 16)],
                    [
                        (requirement[i], MDF(boss_pdamage=15 + 4 * (i - 5)))
                        for i in range(8, 16)
                    ],
                )
            ],
        ]

        ref_mdf_ = ref_mdf.degenerate()

        def getValue(mdf: MDF):
            if mdf == -1:
                return -1
            return (mdf + ref_mdf_).get_damage_factor()

        n = len(matrix)
        dp = [[-1 for x in range(point + 1)] for x in range(n)]

        dp[0][0] = MDF()

        for i in range(len(matrix[0])):
            take = matrix[0][i][1]
            drop = dp[0][matrix[0][i][0]]
            if getValue(take) > getValue(drop):
                dp[0][matrix[0][i][0]] = take
            else:
                dp[0][matrix[0][i][0]] = drop
        for i in range(1, n):
            for j in range(len(matrix[i])):
                for p in range(matrix[i][j][0], point + 1):
                    if dp[i - 1][p - matrix[i][j][0]] != -1:
                        take = dp[i - 1][p - matrix[i][j][0]] + matrix[i][j][1]
                        drop = dp[i][p]
                        if getValue(take) > getValue(drop):
                            dp[i][p] = take
                        else:
                            dp[i][p] = drop

        res = max(dp[n-1], key=lambda x: getValue(x))
        return res.extend()

    @staticmethod
    def get_hyper_object(
        mdf: ExMDF, level: int, prefixed: int, critical_reinforce: bool = False
    ):
        mdf = HyperStat.get_hyper_modifier(mdf, level, prefixed, critical_reinforce)
        return HyperStat(mdf, level)

    @staticmethod
    def get_hyper_modifier(
        mdf: ExMDF, level: int, prefixed: int, critical_reinforce: bool = False
    ) -> Union[List[int], ExMDF]:
        return HyperStat.get_hyper_index(
            mdf, level, prefixed, isIndex=False, critical_reinforce=critical_reinforce
        )
