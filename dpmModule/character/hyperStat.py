from typing import Any, Dict, List, Union

from ..kernel.core import ExtendedCharacterModifier as ExMDF


class HyperStat:
    requirement = [1, 2, 4, 8, 10, 15, 20, 25, 30, 35, 50, 65, 80, 95, 110, 9999]
    enhancement = [
        [ExMDF(stat_main_fixed=30) for i in range(16)],
        [ExMDF(stat_sub_fixed=30) for i in range(16)],
        [ExMDF(crit=1) for i in range(5)] + [ExMDF(crit=2) for i in range(11)],
        [ExMDF(crit_damage=1) for i in range(16)],
        [
            ExMDF(armor_ignore=3 * (i + 1)) - ExMDF(armor_ignore=3 * i)
            for i in range(16)
        ],
        [ExMDF(pdamage=3) for i in range(16)],
        [ExMDF(boss_pdamage=3) for i in range(5)]
        + [ExMDF(boss_pdamage=4) for i in range(11)],
        [ExMDF(att=3) for i in range(16)],
    ]

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
    def get_hyper_index(
        mdf: ExMDF,
        jobname: str,
        level: int,
        prefixed: int,
        isIndex: bool = True,
        critical_reinforce: bool = False,
    ) -> Union[List[int], ExMDF]:
        """get_hyper_index(mdf, level) : return enhancement index for matching enhancement type."""
        hyper_size = 8
        idxList = [0 for i in range(hyper_size)]
        point_left = HyperStat.get_point(level) - prefixed
        mdfSum = ExMDF()

        if jobname == "데몬어벤져":
            HyperStat.enhancement[0] = [ExMDF(pstat_main=i*2) for i in range(16)]
        while True:
            not_enough = True
            fix_enhance = (mdf + mdfSum).get_damage_factor()
            # print(point_left, idxList, fix_enhance)
            val = -1
            ehc = 0
            for i in range(hyper_size):
                enhanced_mdf = HyperStat.enhancement[i][idxList[i]] + mdf + mdfSum
                if critical_reinforce:
                    enhanced_mdf += ExMDF(crit_damage=max(0, enhanced_mdf.crit) * 0.125)
                _ehc = (
                    enhanced_mdf.get_damage_factor() - fix_enhance
                ) / HyperStat.requirement[idxList[i]]
                if _ehc >= ehc and HyperStat.requirement[idxList[i]] < point_left:
                    ehc = _ehc
                    val = i
                if HyperStat.requirement[idxList[i]] < point_left:
                    not_enough = False
            if not_enough:
                break
            if val == -1:
                if (mdf + mdfSum).armor_ignore < 66.7:
                    val = 4
                else:
                    print(point_left)
                    print(idxList)
                    print((mdf + mdfSum).log())
                    raise TypeError("Something gonna wrong")

            point_left -= HyperStat.requirement[idxList[val]]
            mdfSum = mdfSum + HyperStat.enhancement[val][idxList[val]]
            idxList[val] += 1

        if isIndex:
            return idxList
        else:
            return mdfSum

    @staticmethod
    def get_hyper_object(
        mdf: ExMDF, jobname: str, level: int, prefixed: int, critical_reinforce: bool = False
    ):
        mdf = HyperStat.get_hyper_modifier(mdf, jobname, level, prefixed, critical_reinforce)
        return HyperStat(mdf, level)

    @staticmethod
    def get_hyper_modifier(
        mdf: ExMDF, jobname: str, level: int, prefixed: int, critical_reinforce: bool = False
    ) -> Union[List[int], ExMDF]:
        return HyperStat.get_hyper_index(
            mdf, jobname, level, prefixed, isIndex=False, critical_reinforce=critical_reinforce
        )
