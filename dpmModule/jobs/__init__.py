from . import hero
from . import paladin
from . import darknight
from . import archmageFb
from . import archmageTc
from . import bishop
from . import bowmaster
from . import sniper
from . import pathfinder
from . import nightlord
from . import shadower
from . import dualblade
from . import viper
from . import captain
from . import cannonshooter
from . import soulmaster
from . import flamewizard
from . import windbreaker
from . import nightwalker
from . import striker
from . import michael
from . import aran
from . import evan
from . import mercedes
from . import phantom
from . import eunwol
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

job_generator_map = {
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

job_ko_en = {
    "히어로" : "hero",
    "팔라딘" : "paladin",
    "다크나이트" : "darknight",
    "아크메이지불/독" : "archmageFb",
    "아크메이지썬/콜" : "archmageTc",
    "비숍" : "bishop",
    "보우마스터" : "bowmaster",
    "신궁" : "sniper",
    "패스파인더" : "pathfinder",
    "나이트로드" : "nightlord",
    "섀도어" : "shadower",
    "듀얼블레이드" : "dualblade",
    "바이퍼" : "viper",
    "캡틴" : "captain",
    "캐논슈터" : "cannonshooter",
    "소울마스터" : "soulmaster",
    "플레임위자드" : "flamewizard",
    "윈드브레이커" : "windbreaker",
    "나이트워커" : "nightwalker",
    "스트라이커" : "striker",
    "미하일" : "michael",
    "아란" : "aran",
    "에반" : "evan",
    "메르세데스" : "mercedes",
    "팬텀" : "phantom",
    "은월" : "eunwol",
    "루미너스" : "luminous",
    "데몬슬레이어" : "demonslayer",
    "데몬어벤져" : "demonavenger",
    "배틀메이지" : "battlemage",
    "와일드헌터" : "wildhunter",
    "메카닉" : "mechanic",
    "제논" : "xenon",
    "블래스터" : "blaster",
    "카이저" : "kaiser",
    "카인" : "kain",
    "카데나" : "cadena",
    "엔젤릭버스터" : "angelicbuster",
    "제로" : "zero",
    "키네시스" : "kinesis",
    "아델" : "adele",
    "일리움" : "ilium",
    "아크" : "ark",
    "호영" : "hoyoung",
}

job_en_ko = {v: k for k, v in job_ko_en.items()}

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

job_list_order = job_generator_map.keys()


def get_ko_jobname(jobname):
    if jobname in job_en_ko:
        return job_en_ko[jobname]
    elif jobname in job_generator_map:
        return jobname
    else:
        return None


def get_generator(jobname_ko):
    if jobname_ko in job_generator_map:
        return job_generator_map[jobname_ko]
    else:
        return None
