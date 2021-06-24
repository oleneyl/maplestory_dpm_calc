from ...kernel import core


def AnimaGoddessBlessWrapper(vEhc, num1, num2):
    AnimaGoddessBless = core.BuffSkill("그란디스 여신의 축복 (아니마)", 0, 40*1000, cooltime=240*1000, red=True, pdamage=10 + vEhc.getV(num1, num2)).isV(vEhc, num1, num2).wrap(core.BuffSkillWrapper)
    return AnimaGoddessBless
