from ...kernel import core


class OverdriveWrapper(core.BuffSkillWrapper):
    def __init__(self, vEhc, num1, num2, WEAPON_ATT):
        skill = core.BuffSkill(
            "오버 드라이브",  # Overdrive
            delay=420,
            remain=30 * 1000,
            cooltime=(70 - vEhc.getV(num1, num2) // 5) * 1000,
            red=True,
            att=WEAPON_ATT * 0.01 * (20 + 2 * vEhc.getV(num1, num2)),
        ).isV(vEhc, num1, num2)
        self.penaltyModifier = core.CharacterModifier(att=-0.15 * WEAPON_ATT)
        super(OverdriveWrapper, self).__init__(skill)

    def get_modifier(self) -> core.CharacterModifier:
        if self.is_active():
            return self.skill.get_modifier()
        elif not self.is_available():
            return self.penaltyModifier
        else:
            return self.disabledModifier


def LoadedDicePassiveWrapper(vEhc, num1, num2):
    LoadedDicePassive = core.InformedCharacterModifier(
        "로디드 다이스(패시브)", att=vEhc.getV(num1, num2) + 10  # Loaded Dice (Passive)
    )
    return LoadedDicePassive
