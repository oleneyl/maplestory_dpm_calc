from typing import Any, Dict, NamedTuple


class Preset(NamedTuple):
    id: str
    job: str
    description: str
    options: Dict[str, Any]
    alt: int


presets = [
    Preset(
        id="hero",
        job="히어로",
        description="두손도끼, 소오버 고정",
        options={},
        alt=0,
    ),
    Preset(
        id="paladin",
        job="팔라딘",
        description="두손둔기, 블레싱 아머 미발동",
        options={},
        alt=0,
    ),
    Preset(
        id="darknight",
        job="다크나이트",
        description="다크 스피어 8히트, 체력 100%, 리인카 사용",
        options={},
        alt=0,
    ),
    Preset(
        id="archmage_fp",
        job="아크메이지불/독",
        description="포이즌 노바 4히트, 언스 사용",
        options={},
        alt=0,
    ),
    Preset(
        id="archmage_tc",
        job="아크메이지썬/콜",
        description="썬브 2히트, 언스 사용",
        options={"thunder_break_hit": 2},
        alt=0,
    ),
    Preset(
        id="archmage_tc_thunder_8",
        job="아크메이지썬/콜",
        description="썬브 8히트, 언스 사용",
        options={"thunder_break_hit": 8},
        alt=1,
    ),
    Preset(
        id="bishop",
        job="비숍",
        description="피스메이커 3히트, 솔플, 언스 사용",
        options={},
        alt=0,
    ),
    Preset(
        id="bowmaster",
        job="보우마스터",
        description="애로우 레인 1줄기",
        options={},
        alt=0,
    ),
    Preset(
        id="sniper",
        job="신궁",
        description="거리 400",
        options={"distance": 400},
        alt=0,
    ),
    Preset(
        id="sniper_distance_100",
        job="신궁",
        description="거리 100",
        options={"distance": 100},
        alt=1,
    ),
    Preset(
        id="pathfinder",
        job="패스파인더",
        description="블래 210ms 디차 240ms",
        options={},
        alt=0,
    ),
    Preset(
        id="nightlord",
        job="나이트로드",
        description="스프 풀히트",
        options={},
        alt=0,
    ),
    Preset(
        id="shadower",
        job="섀도어",
        description="KP3 1타 94.6% / 2타 100%",
        options={},
        alt=0,
    ),
    Preset(
        id="dualblade",
        job="듀얼블레이드",
        description="블토 태풍 5히트",
        options={},
        alt=0,
    ),
    Preset(id="viper", job="바이퍼", description="카운터 어택 미발동", options={}, alt=0),
    Preset(
        id="captain",
        job="캡틴",
        description="데드아이 풀조준, 카운터 어택 미발동",
        options={},
        alt=0,
    ),
    Preset(
        id="cannonshooter",
        job="캐논슈터",
        description="코코볼 27히트",
        options={},
        alt=0,
    ),
    Preset(id="soulmaster", job="소울마스터", description="", options={}, alt=0),
    Preset(
        id="michile",
        job="미하일",
        description="솔플, 로얄가드 쿨마다",
        options={},
        alt=0,
    ),
    Preset(
        id="flamewizard",
        job="플레임위자드",
        description="블비탈 4히트, 오비탈 분당 1350타",
        options={"orbital_per_min": 1350},
        alt=0,
    ),
    Preset(
        id="flamewizard_orbital_1150",
        job="플레임위자드",
        description="블비탈 4히트, 오비탈 분당 1150타",
        options={"orbital_per_min": 1150},
        alt=1,
    ),
    Preset(
        id="windbreaker",
        job="윈드브레이커",
        description="하울링게일 58히트, 볼텍스 스피어 17히트",
        options={},
        alt=0,
    ),
    Preset(
        id="nightwalker",
        job="나이트워커",
        description="점샷 400ms",
        options={},
        alt=0,
    ),
    Preset(
        id="striker",
        job="스트라이커",
        description="파섬",
        options={"dealcycle": "waterwave"},
        alt=0,
    ),
    Preset(
        id="striker_thunder",
        job="스트라이커",
        description="벽섬",
        options={"dealcycle": "thunder"},
        alt=1,
    ),
    Preset(
        id="blaster",
        job="블래스터",
        description="매그팡 510ms",
        options={},
        alt=0,
    ),
    Preset(
        id="demonslayer",
        job="데몬슬레이어",
        description="블블 100%",
        options={},
        alt=0,
    ),
    Preset(
        id="battlemage",
        job="배틀메이지",
        description="좌우텔 분당 83회, 디버프 오라만, 명계문 미사용",
        options={},
        alt=0,
    ),
    Preset(
        id="wildhunter",
        job="와일드헌터",
        description="재규어 스톰 3히트",
        options={},
        alt=0,
    ),
    Preset(id="mechanic", job="메카닉", description="", options={}, alt=0),
    Preset(id="aran", job="아란", description="", options={}, alt=0),
    Preset(
        id="evan",
        job="에반",
        description="다오어 3히트, 다오어-브레스-브오어",
        options={},
        alt=0,
    ),
    Preset(id="luminous", job="루미너스", description="", options={}, alt=0),
    Preset(
        id="mercedes",
        job="메르세데스",
        description="엘고때 연계사이클",
        options={"dealcycle": "combo"},
        alt=0,
    ),
    Preset(
        id="mercedes_ishtar",
        job="메르세데스",
        description="엘고때 이슈타르",
        options={"dealcycle": "ishtar"},
        alt=1,
    ),
    Preset(
        id="phantom_pathfinder",
        job="팬텀",
        description="블디, 블디/크오체/파컷/불스아이, 체력 100%",
        options={"dealcycle": "blast_discharge"},
        alt=0,
    ),
    Preset(
        id="phantom",
        job="팬텀",
        description="얼드, 분노/크오체/파컷/불스아이, 체력 100%",
        options={"dealcycle": "ultimate_drive"},
        alt=1,
    ),
    Preset(
        id="eunwol",
        job="은월",
        description="분혼 격참 이동형 보스 판정, 약점 간파 적용",
        options={"hp_rate": True},
        alt=0,
    ),
    Preset(
        id="eunwol_weakness_off",
        job="은월",
        description="분혼 격참 이동형 보스 판정, 약점 간파 미적용",
        options={"hp_rate": False},
        alt=1,
    ),
    Preset(id="kaiser", job="카이저", description="", options={}, alt=0),
    Preset(
        id="cadena",
        job="카데나",
        description="1타캔슬 150ms, 캔슬 180ms, 윙대거 3틱",
        options={},
        alt=0,
    ),
    Preset(
        id="angelicbuster",
        job="엔젤릭버스터",
        description="스포트라이트 3중첩, 어피니티IV 가동률 94.18%",
        options={"spotlight": 3},
        alt=0,
    ),
    Preset(
        id="angelicbuster_spotlight_2",
        job="엔젤릭버스터",
        description="스포트라이트 2중첩, 어피니티IV 가동률 94.18%",
        options={"spotlight": 2},
        alt=1,
    ),
    Preset(
        id="adele",
        job="아델",
        description="게더링 80% 히트, 레조넌스 10초마다",
        options={},
        alt=0,
    ),
    Preset(id="illium", job="일리움", description="", options={}, alt=0),
    Preset(
        id="ark",
        job="아크",
        description="플레인 캔슬 270ms, 흉몽 캔슬 210ms",
        options={},
        alt=0,
    ),
    Preset(
        id="hoyoung",
        job="호영",
        description="금고봉/지진쇄/토파류",
        options={},
        alt=0,
    ),
    Preset(
        id="zero",
        job="제로",
        description="문피쉐, 카벨뚝",
        options={"dealcycle": "alpha_new"},
        alt=0,
    ),
    Preset(
        id="zero_alpha_legacy",
        job="제로",
        description="어파스, 카벨뚝",
        options={"dealcycle": "alpha_legacy"},
        alt=1,
    ),
    Preset(id="kinesis", job="키네시스", description="메테리얼", options={}, alt=0),
]

preset_dict = {el.id: el for el in presets}


def get_preset(id: str):
    return preset_dict[id]


def get_preset_list():
    return presets
