from ..kernel.core import ExtendedCharacterModifier as ExMDF


class Personality:
    @staticmethod
    def get_personality(avg_level: float) -> ExMDF:
        return ExMDF(
            armor_ignore=(avg_level // 5) * 0.5,
            buff_rem=(avg_level // 10) * 1,
            prop_ignore=0.5 * (avg_level // 10),
        )
