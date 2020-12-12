from ...kernel import core

# 베놈 버스트는 현재 카데나만 사용하고 있으므로 추가하지 않음


# 직업별 스크립트 완전히 파악되면 통합 필요
def ReadyToDieWrapper(vEhc, num1, num2):
    ReadyToDie = (
        core.BuffSkill(
            "레디 투 다이",
            delay=600 * 2,
            remain=15 * 1000,
            cooltime=(90 - int(0.5 * vEhc.getV(num1, num2))) * 1000,
            red=True,
            pdamage_indep=30 + int(0.2 * vEhc.getV(num1, num2)),
        )
        .isV(vEhc, num1, num2)
        .wrap(core.BuffSkillWrapper)
    )
    return ReadyToDie


def ReadyToDiePassiveWrapper(vEhc, num1, num2):
    ReadyToDiePassive = core.InformedCharacterModifier(
        "레디 투 다이(패시브)", att=vEhc.getV(num1, num2)
    )
    return ReadyToDiePassive


# 3개 직업의 코드가 통일이 안되어 있으므로 아직 쓰면 안됨
# aDS = 어드밴스드 다크사이트 최종뎀값
def UltimateDarkSightWrapper(vEhc, num1, num2, aDS=0):
    UltimateDarkSight = (
        core.BuffSkill(
            "얼티밋 다크 사이트",
            delay=750,
            remain=30000,
            cooltime=(220 - vEhc.getV(num1, num2)) * 1000,
            red=True,
            pdamage_indep=10 + vEhc.getV(num1, num2) // 5 + aDS,
        )
        .isV(vEhc, num1, num2)
        .wrap(core.BuffSkillWrapper)
    )
    return UltimateDarkSight
