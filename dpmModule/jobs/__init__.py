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

jobMap = {
    "히어로": hero,
    "팔라딘": paladin,
    "다크나이트": darknight,
    "아크메이지불/독": archmageFP,
    "아크메이지썬/콜": archmageIL,
    "비숍": bishop,
    "보우마스터": bowmaster,
    "신궁": marksman,
    "패스파인더": pathfinder,
    "나이트로드": nightlord,
    "섀도어": shadower,
    "듀얼블레이드": dualblade,
    "바이퍼": buccaneer,
    "캡틴": corsair,
    "캐논슈터": cannoneer,
    "소울마스터": dawnwarrior,
    "플레임위자드": blazewizard,
    "윈드브레이커": windarcher,
    "나이트워커": nightwalker,
    "스트라이커": thunderbreaker,
    "미하일": mihile,
    "아란": aran,
    "에반": evan,
    "메르세데스": mercedes,
    "팬텀": phantom,
    "은월": shade,
    "루미너스": luminous,
    "데몬슬레이어": demonslayer,
    "데몬어벤져": demonavenger,
    "배틀메이지": battlemage,
    "와일드헌터": wildhunter,
    "메카닉": mechanic,
    "제논": xenon,
    "블래스터": blaster,
    "카이저": kaiser,
    "카인": kain,
    "카데나": cadena,
    "엔젤릭버스터": angelicbuster,
    "제로": zero,
    "키네시스": kinesis,
    "아델": adele,
    "일리움": ilium,
    "아크": ark,
    "호영": hoyoung,
}

jobList = {
    "hero": "히어로",
    "paladin": "팔라딘",
    "darknight": "다크나이트",
    "archmageFP": "아크메이지불/독",
    "archmageIL": "아크메이지썬/콜",
    "bishop": "비숍",
    "bowmaster": "보우마스터",
    "marksman": "신궁",
    "pathfinder": "패스파인더",
    "nightlord": "나이트로드",
    "shadower": "섀도어",
    "dualblade": "듀얼블레이드",
    "buccaneer": "바이퍼",
    "corsair": "캡틴",
    "cannoneer": "캐논슈터",
    "dawnwarrior": "소울마스터",
    "blazewizard": "플레임위자드",
    "windarcher": "윈드브레이커",
    "nightwalker": "나이트워커",
    "thunderbreaker": "스트라이커",
    "mihile": "미하일",
    "aran": "아란",
    "evan": "에반",
    "mercedes": "메르세데스",
    "phantom": "팬텀",
    "shade": "은월",
    "luminous": "루미너스",
    "demonslayer": "데몬슬레이어",
    "demonavenger": "데몬어벤져",
    "battlemage": "배틀메이지",
    "wildhunter": "와일드헌터",
    "mechanic": "메카닉",
    "xenon": "제논",
    "blaster": "블래스터",
    "kaiser": "카이저",
    "kain": "카인",
    "cadena": "카데나",
    "angelicbuster": "엔젤릭버스터",
    "zero": "제로",
    "kinesis": "키네시스",
    "adele": "아델",
    "ilium": "일리움",
    "ark": "아크",
    "hoyoung": "호영",
}

# used for gear lookup
# 0: warrior, 1: magician, 2: archer, 3: thief, 4: pirate(STR), 5: pirate(DEX)
job_branch_list = {
    "히어로": 0,
    "팔라딘": 0,
    "다크나이트": 0,
    "아크메이지불/독": 1,
    "아크메이지썬/콜": 1,
    "비숍": 1,
    "보우마스터": 2,
    "신궁": 2,
    "패스파인더": 2,
    "나이트로드": 3,
    "섀도어": 3,
    "듀얼블레이드": 3,
    "바이퍼": 4,
    "캡틴": 5,
    "캐논슈터": 4,
    "소울마스터": 0,
    "플레임위자드": 1,
    "윈드브레이커": 2,
    "나이트워커": 3,
    "스트라이커": 4,
    "미하일": 0,
    "아란": 0,
    "에반": 1,
    "메르세데스": 2,
    "팬텀": 3,
    "은월": 4,
    "루미너스": 1,
    "데몬슬레이어": 0,
    "데몬어벤져": 0,
    "배틀메이지": 1,
    "와일드헌터": 2,
    "메카닉": 5,
    "제논": 3,
    "블래스터": 0,
    "카이저": 0,
    "카인": 2,
    "카데나": 3,
    "엔젤릭버스터": 5,
    "제로": 0,
    "키네시스": 1,
    "아델": 0,
    "일리움": 1,
    "아크": 4,
    "호영": 3,
}

__all__ = jobList.keys()
jobListOrder = jobList.keys()


def getKoJobName(enJob):
    if enJob in jobList:
        return jobList[enJob]


def getGenerator(koJob):
    if koJob in jobMap:
        return jobMap[koJob]
