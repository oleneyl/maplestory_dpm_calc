from ..kernel.core import ExtendedCharacterModifier as ExMDF


class Doping:
    dopingListAtt = {
        "길드의 더 큰 축복": ExMDF(att=30),
        "우뿌": ExMDF(att=30),
        "붕뿌": ExMDF(att=30),
        "유니온의 힘": ExMDF(att=30),
        "익스레드/블루": ExMDF(att=30),
        "MVP 버프": ExMDF(att=30),
        "영웅의 메아리": ExMDF(patt=4),
        # "이벤트 버프": ExMDF(att=20, armor_ignore=30, boss_pdamage=30, stat_main=40, stat_sub=40)
    }

    dopingListStat = {"향상된 10단계 물약": ExMDF(stat_main=30)}
    dopingListXenon = {"향상된 10단계 물약": ExMDF(stat_main=30*3)}
    dopingListHP = {"익스트림 레드": ExMDF(stat_main=2000)}

    dopingListDamage = {
        "노블레스(뎀퍼)": ExMDF(pdamage=30),
        "노블레스(보공)": ExMDF(boss_pdamage=28),
        "반빨별": ExMDF(boss_pdamage=20),
    }

    dopingListArmor = {"고관비": ExMDF(armor_ignore=20)}

    dopingListCritDamage = {"노블레스(크뎀)": ExMDF(crit_damage=30)}

    @staticmethod
    def get_full_doping(jobtype: str) -> ExMDF:
        retMdf = ExMDF()

        for name in Doping.dopingListAtt:
            retMdf = retMdf + Doping.dopingListAtt[name]
        if jobtype == "xenon":
            for name in Doping.dopingListXenon:
                retMdf = retMdf + Doping.dopingListXenon[name]
        elif jobtype == "HP":
            for name in Doping.dopingListHP:
                retMdf = retMdf + Doping.dopingListHP[name]
        else:
            for name in Doping.dopingListStat:
                retMdf = retMdf + Doping.dopingListStat[name]
        for name in Doping.dopingListDamage:
            retMdf = retMdf + Doping.dopingListDamage[name]
        for name in Doping.dopingListArmor:
            retMdf = retMdf + Doping.dopingListArmor[name]
        for name in Doping.dopingListCritDamage:
            retMdf = retMdf + Doping.dopingListCritDamage[name]

        return retMdf
