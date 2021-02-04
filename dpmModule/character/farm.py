from ..kernel.core import ExtendedCharacterModifier as ExMDF


class Farm:
    @staticmethod
    def get_farm(jobtype) -> ExMDF:
        Cygnus = ExMDF(pdamage=3)
        Scarecrow = ExMDF(pdamage=4)
        VanLeon = ExMDF(boss_pdamage=5)
        Hilla = ExMDF(crit_damage=2)
        Akairum = ExMDF(buff_rem=5)
        Lazuli = ExMDF(crit=5)
        MainStat = ExMDF(stat_main=10)  # 듀나스 / 프랑켄슈타인 / 릴리노흐 / 타이머
        VikingLegion = ExMDF(pdamage=3)

        if jobtype in ["DEX", "xenon"]:
            BlackViking = ExMDF(pdamage=2, stat_main=6)
            Vikings = ExMDF(stat_main=12)
        elif jobtype in ["STR", "LUK"]:
            BlackViking = ExMDF(pdamage=2, stat_sub=6)
            Vikings = ExMDF(stat_sub=12)
        else:
            BlackViking = ExMDF(pdamage=2)
            Vikings = ExMDF()
        return (
            Cygnus
            + Scarecrow
            + VanLeon
            + Hilla
            + Akairum
            + Lazuli
            + MainStat
            + VikingLegion
            + BlackViking
            + Vikings
        )
