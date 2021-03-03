from . import hero
from . import paladin
from . import darknight
from . import archmageFP
from . import archmageIL
from . import bishop
from . import bowmaster
from . import marksman
from . import pathfinder
from . import nightlord
from . import shadower
from . import dualblade
from . import buccaneer
from . import corsair
from . import cannoneer
from . import dawnwarrior
from . import blazewizard
from . import windarcher
from . import nightwalker
from . import thunderbreaker
from . import mihile
from . import aran
from . import evan
from . import mercedes
from . import phantom
from . import shade
from . import luminous
from . import demonslayer
from . import demonavenger
from . import battlemage
from . import wildhunter
from . import mechanic
from . import xenon
from . import blaster
from . import kaiser
from . import kain
from . import cadena
from . import angelicbuster
from . import zero
from . import kinesis
from . import adele
from . import ilium
from . import ark
from . import hoyoung

from localization.utilities import translator
_ = translator.gettext

jobMap = {
    _("히어로"): hero,
    _("팔라딘"): paladin,
    _("다크나이트"): darknight,
    _("아크메이지불/독"): archmageFP,
    _("아크메이지썬/콜"): archmageIL,
    _("비숍"): bishop,
    _("보우마스터"): bowmaster,
    _("신궁"): marksman,
    _("패스파인더"): pathfinder,
    _("나이트로드"): nightlord,
    _("섀도어"): shadower,
    _("듀얼블레이드"): dualblade,
    _("바이퍼"): buccaneer,
    _("캡틴"): corsair,
    _("캐논슈터"): cannoneer,
    _("소울마스터"): dawnwarrior,
    _("플레임위자드"): blazewizard,
    _("윈드브레이커"): windarcher,
    _("나이트워커"): nightwalker,
    _("스트라이커"): thunderbreaker,
    _("미하일"): mihile,
    _("아란"): aran,
    _("에반"): evan,
    _("메르세데스"): mercedes,
    _("팬텀"): phantom,
    _("은월"): shade,
    _("루미너스"): luminous,
    _("데몬슬레이어"): demonslayer,
    _("데몬어벤져"): demonavenger,
    _("배틀메이지"): battlemage,
    _("와일드헌터"): wildhunter,
    _("메카닉"): mechanic,
    _("제논"): xenon,
    _("블래스터"): blaster,
    _("카이저"): kaiser,
    _("카인"): kain,
    _("카데나"): cadena,
    _("엔젤릭버스터"): angelicbuster,
    _("제로"): zero,
    _("키네시스"): kinesis,
    _("아델"): adele,
    _("일리움"): ilium,
    _("아크"): ark,
    _("호영"): hoyoung,
}

# used for gear lookup
# 0: warrior, 1: magician, 2: archer, 3: thief, 4: pirate(STR), 5: pirate(DEX)
job_branch_list = {
    _("히어로"): 0,
    _("팔라딘"): 0,
    _("다크나이트"): 0,
    _("아크메이지불/독"): 1,
    _("아크메이지썬/콜"): 1,
    _("비숍"): 1,
    _("보우마스터"): 2,
    _("신궁"): 2,
    _("패스파인더"): 2,
    _("나이트로드"): 3,
    _("섀도어"): 3,
    _("듀얼블레이드"): 3,
    _("바이퍼"): 4,
    _("캡틴"): 5,
    _("캐논슈터"): 4,
    _("소울마스터"): 0,
    _("플레임위자드"): 1,
    _("윈드브레이커"): 2,
    _("나이트워커"): 3,
    _("스트라이커"): 4,
    _("미하일"): 0,
    _("아란"): 0,
    _("에반"): 1,
    _("메르세데스"): 2,
    _("팬텀"): 3,
    _("은월"): 4,
    _("루미너스"): 1,
    _("데몬슬레이어"): 0,
    _("데몬어벤져"): 0,
    _("배틀메이지"): 1,
    _("와일드헌터"): 2,
    _("메카닉"): 5,
    _("제논"): 3,
    _("블래스터"): 0,
    _("카이저"): 0,
    _("카인"): 2,
    _("카데나"): 3,
    _("엔젤릭버스터"): 5,
    _("제로"): 0,
    _("키네시스"): 1,
    _("아델"): 0,
    _("일리움"): 1,
    _("아크"): 4,
    _("호영"): 3,
}

__all__ = jobMap.keys()
jobListOrder = jobMap.keys()


def getGenerator(job):
    if job in jobMap:
        return jobMap[job]
