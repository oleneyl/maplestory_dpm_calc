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
from . import kain

__all__ = ["archmageFb", "archmageTc", "hero", "paladin", "sniper", "windbreaker", "soulmaster", 
            "flamewizard", "mercedes", "luminous", "bishop", "battlemage", "mechanic", "demonslayer", "darknight", "wildhunter",
            "shadower", "cannonshooter", "michael", "dualblade", "kaiser", "captain", "angelicbuster", "phantom", "nightlord",
            "eunwol", "viper", "nightwalker", "striker","evan", "bowmaster", "zero", "kinesis", "ilium", "pathfinder", "cadena",
            "ark", "blaster", "aran", "adele", "hoyoung", "kain"]

jobMap = {"아크메이지불/독" : archmageFb,
        "아크메이지썬/콜" : archmageTc,
        "비숍" : bishop,
        "히어로" : hero,
        "팔라딘" : paladin,
        "신궁" : sniper,
        "윈드브레이커" : windbreaker,
        "소울마스터" : soulmaster,
        "루미너스" : luminous,
        "배틀메이지" : battlemage,
        "메카닉" : mechanic,
        "메르세데스" : mercedes,
        "데몬슬레이어" : demonslayer,
        "다크나이트" : darknight,
        "와일드헌터" : wildhunter,
        "플레임위자드" : flamewizard,
        "섀도어" : shadower,
        "캐논슈터" : cannonshooter,
        "미하일" : michael,
        "듀얼블레이드" : dualblade,
        "카이저" : kaiser,
        "캡틴" : captain,
        "엔젤릭버스터" : angelicbuster,
        "팬텀" : phantom,
        "나이트로드" : nightlord,
        "은월" : eunwol,
        "바이퍼" : viper,
        "나이트워커" : nightwalker,
        "스트라이커" : striker,
        "에반" : evan,
        "보우마스터" : bowmaster,
        "제로" : zero,
        "키네시스" : kinesis,
        "일리움" : ilium,
        "패스파인더" : pathfinder,
        "카데나" : cadena,
        "아크" : ark,
        "블래스터" : blaster,
        "아란" : aran,
        "아델" : adele,
        "호영" : hoyoung,
        "카인" : kain
}

jobList = {"archmageFb" : "아크메이지불/독",
        "archmageTc" : "아크메이지썬/콜",
        "hero" : "히어로",
        "paladin" : "팔라딘",
        "sniper" : "신궁",
        "windbreaker" : "윈드브레이커",
        "soulmaster" : "소울마스터",
        "viper" : "바이퍼",
        "flamewizard" : "플레임위자드",
        "nightlord" : "나이트로드",
        "mercedes" : "메르세데스",
        "luminous" : "루미너스",
        "bishop" : "비숍",
        "battlemage" : "배틀메이지",
        "mechanic" : "메카닉",
        "demonslayer" : "데몬슬레이어",
        "darknight" : "다크나이트",
        "wildhunter" : "와일드헌터",
        "shadower" : "섀도어",
        "cannonshooter" : "캐논슈터",
        "michael" : "미하일",
        "dualblade" : "듀얼블레이드",
        "kaiser" : "카이저",
        "captain" : "캡틴",
        "angelicbuster" : "엔젤릭버스터",
        "phantom" : "팬텀",
        "eunwol" : "은월",
        "nightwalker" : "나이트워커",
        "striker" : "스트라이커",
        "evan" : "에반",
        "bowmaster" : "보우마스터",
        "zero" : "제로",
        "kinesis" : "키네시스",
        "ilium" : "일리움",
        "pathfinder" : "패스파인더",
        "cadena" : "카데나",
        "ark" : "아크",
        "blaster" : "블래스터",
        "aran" : "아란",
        "adele" : "아델",
        "hoyoung" : "호영",
        "kain" : "카인"
}

weaponList = {"아크메이지불/독" : "스태프",
        "아크메이지썬/콜" : "스태프",
        "일리움" : "건틀렛",
        "히어로" : "두손검",
        "팔라딘" : "두손검",
        "신궁" : "석궁",
        "윈드브레이커" : "활",
        "소울마스터" : "두손검",
        "바이퍼" : "너클",
        "플레임위자드" : "스태프",
        "메르세데스" : "듀얼보우건",
        "루미너스" : "샤이닝로드",
        "비숍" : "스태프",
        "배틀메이지" : "스태프",
        "메카닉" : "건",
        "데몬슬레이어" : "두손둔기",
        "다크나이트" : "창",
        "와일드헌터" : "석궁",
        "섀도어" : "단검",
        "캐논슈터" : "핸드캐논",
        "미하일" : "한손검",
        "듀얼블레이드" : "블레이드",
        "카이저" : "두손검",
        "캡틴" : "건",
        "엔젤릭버스터" : "소울슈터",
        "팬텀" : "케인",
        "나이트로드" : "아대",
        "은월" : "너클",
        "나이트워커" : "아대",
        "스트라이커" : "너클",
        "에반" : "스태프",
        "보우마스터" : "활",
        "제로" : "제로무기",
        "키네시스" : "ESP리미터",
        "패스파인더" : "활",
        "카데나" : "체인",
        "아크" : "너클",
        "블래스터" : "리볼버",
        "아란" : "폴암",
        "아델" : "튜너",
        "호영" : "부채",
        "카인" : "브레스슈터"
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


