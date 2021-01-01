from . import archmageFb
from . import archmageTc
from . import bishop
from . import hero
from . import paladin
from . import sniper
from . import windbreaker
from . import soulmaster
from . import luminous
from . import battlemage
from . import mechanic
from . import mercedes
from . import demonslayer
from . import darknight
from . import wildhunter
from . import flamewizard
from . import shadower
from . import cannonshooter
from . import michael
from . import dualblade
from . import kaiser
from . import captain
from . import angelicbuster
from . import phantom
from . import nightlord
from . import viper
from . import eunwol
from . import nightwalker
from . import striker
from . import evan
from . import bowmaster
from . import zero
from . import kinesis
from . import ilium
from . import pathfinder
from . import cadena
from . import ark
from . import blaster
from . import aran
from . import adele
from . import hoyoung
from . import demonavenger
from . import xenon

__all__ = [
    "hero",
    "paladin",
    "darknight",
    "archmageFb",
    "archmageTc",
    "bishop",
    "bowmaster",
    "sniper",
    "pathfinder",
    "nightlord",
    "shadower",
    "dualblade",
    "viper",
    "captain",
    "cannonshooter",
    "soulmaster",
    "flamewizard",
    "windbreaker",
    "nightwalker",
    "striker",
    "michael",
    "aran",
    "evan",
    "mercedes",
    "phantom",
    "eunwol",
    "luminous",
    "demonslayer",
    "demonavenger",
    "battlemage",
    "wildhunter",
    "mechanic",
    "xenon",
    "blaster",
    "kaiser",
    # "kain",
    "cadena",
    "angelicbuster",
    "zero",
    "kinesis",
    "adele",
    "ilium",
    "ark",
    "hoyoung"]

jobMap = {
    "히어로": hero,
    "팔라딘": paladin,
    "다크나이트": darknight,
    "아크메이지불/독": archmageFb,
    "아크메이지썬/콜": archmageTc,
    "비숍": bishop,
    "보우마스터": bowmaster,
    "신궁": sniper,
    "패스파인더": pathfinder,
    "나이트로드": nightlord,
    "섀도어": shadower,
    "듀얼블레이드": dualblade,
    "바이퍼": viper,
    "캡틴": captain,
    "캐논슈터": cannonshooter,
    "소울마스터": soulmaster,
    "플레임위자드": flamewizard,
    "윈드브레이커": windbreaker,
    "나이트워커": nightwalker,
    "스트라이커": striker,
    "미하일": michael,
    "아란": aran,
    "에반": evan,
    "메르세데스": mercedes,
    "팬텀": phantom,
    "은월": eunwol,
    "루미너스": luminous,
    "데몬슬레이어": demonslayer,
    "데몬어벤져": demonavenger,
    "배틀메이지": battlemage,
    "와일드헌터": wildhunter,
    "메카닉": mechanic,
    "제논": xenon,
    "블래스터": blaster,
    "카이저": kaiser,
    # "카인": kain,
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
    "archmageFb": "아크메이지불/독",
    "archmageTc": "아크메이지썬/콜",
    "hero": "히어로",
    "paladin": "팔라딘",
    "sniper": "신궁",
    "windbreaker": "윈드브레이커",
    "soulmaster": "소울마스터",
    "viper": "바이퍼",
    "flamewizard": "플레임위자드",
    "nightlord": "나이트로드",
    "mercedes": "메르세데스",
    "luminous": "루미너스",
    "bishop": "비숍",
    "battlemage": "배틀메이지",
    "mechanic": "메카닉",
    "demonslayer": "데몬슬레이어",
    "darknight": "다크나이트",
    "wildhunter": "와일드헌터",
    "shadower": "섀도어",
    "cannonshooter": "캐논슈터",
    "michael": "미하일",
    "dualblade": "듀얼블레이드",
    "kaiser": "카이저",
    "captain": "캡틴",
    "angelicbuster": "엔젤릭버스터",
    "phantom": "팬텀",
    "eunwol": "은월",
    "nightwalker": "나이트워커",
    "striker": "스트라이커",
    "evan": "에반",
    "bowmaster": "보우마스터",
    "zero": "제로",
    "kinesis": "키네시스",
    "ilium": "일리움",
    "pathfinder": "패스파인더",
    "cadena": "카데나",
    "ark": "아크",
    "blaster": "블래스터",
    "aran": "아란",
    "adele": "아델",
    "hoyoung": "호영",
    "xenon": "제논",
    "demonavenger": "데몬어벤져"
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
    # "카인": 2,
    "카데나": 3,
    "엔젤릭버스터": 5,
    "제로": 0,
    "키네시스": 1,
    "아델": 0,
    "일리움": 1,
    "아크": 4,
    "호영": 3,
}

jobListOrder = __all__.copy()


def getKoJobName(enJob):
    if enJob in jobList:
        return jobList[enJob]
    else:
        return None


def getGenerator(koJob):
    if koJob in jobMap:
        return jobMap[koJob]
    else:
        return None
