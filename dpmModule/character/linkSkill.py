from functools import reduce
from typing import List

from ..kernel.core import ExtendedCharacterModifier as ExMDF
from ..kernel.core import InformedCharacterModifier


class LinkSkill:
    DemonSlayer = InformedCharacterModifier("링크(데몬슬레이어)", boss_pdamage=15)
    DemonAvenger = InformedCharacterModifier("링크(데몬어벤져)", pdamage=10)
    Ark = InformedCharacterModifier("링크(아크)", pdamage=11)
    Illium = InformedCharacterModifier("링크(일리움)", pdamage=12)
    Cadena = InformedCharacterModifier("링크(카데나)", pdamage=12)  # optional
    AdventureMage = InformedCharacterModifier("링크(모법)", pdamage=9, armor_ignore=9)
    AdventureRog = InformedCharacterModifier("링크(모도)", pdamage=18 / 2)
    Adele = InformedCharacterModifier("링크(아델)", pdamage=2, boss_pdamage=4)
    Luminous = InformedCharacterModifier("링크(루미너스)", armor_ignore=15)
    Zero = InformedCharacterModifier("링크(제로)", armor_ignore=10)
    Hoyoung = InformedCharacterModifier("링크(호영)", armor_ignore=10)
    Zenon = InformedCharacterModifier("링크(제논)", pstat_main=10, pstat_sub=10)
    AdventurePirate = InformedCharacterModifier("링크(모해)", stat_main=70, stat_sub=70)
    Cygnus = InformedCharacterModifier("링크(시그너스)", att=25)
    Phantom = InformedCharacterModifier("링크(팬텀)", crit=15)
    AdventureArcher = InformedCharacterModifier("링크(모궁)", crit=10)
    Kinesis = InformedCharacterModifier("링크(키네시스)", crit_damage=4)
    Kain = InformedCharacterModifier("링크(카인)", pdamage=17/2)  # pdamage TODO: implement kain link skill
    Angelicbuster = InformedCharacterModifier("링크(엔젤릭버스터)")  # Skill
    Michael = InformedCharacterModifier("링크(미하일)")  # Util skill
    Mercedes = InformedCharacterModifier("링크(메르세데스)")  # Exp
    Aran = InformedCharacterModifier("링크(아란)")  # Exp
    Evan = InformedCharacterModifier("링크(에반)")  # Exp
    Eunwol = InformedCharacterModifier("링크(은월)")  # Util
    Kaiser = InformedCharacterModifier("링크(카이저)", pstat_main=15)  # HP - Demon Avenger only
    Registance = InformedCharacterModifier("링크(레지스탕스)")  # Util
    AdventureWarrior = InformedCharacterModifier("링크(모전)")  # Skill

    jobdict = {
        "아크메이지불/독": AdventureMage,
        "아크메이지썬/콜": AdventureMage,
        "비숍": AdventureMage,
        "히어로": AdventureWarrior,
        "팔라딘": AdventureWarrior,
        "다크나이트": AdventureWarrior,
        "보우마스터": AdventureArcher,
        "패스파인더": AdventureArcher,
        "신궁": AdventureArcher,
        "나이트로드": AdventureRog,
        "섀도어": AdventureRog,
        "듀얼블레이드": AdventureRog,
        "캡틴": AdventurePirate,
        "바이퍼": AdventurePirate,
        "캐논슈터": AdventurePirate,
        "소울마스터": Cygnus,
        "플레임위자드": Cygnus,
        "윈드브레이커": Cygnus,
        "나이트워커": Cygnus,
        "스트라이커": Cygnus,
        "미하일": Michael,
        "아란": Aran,
        "에반": Evan,
        "루미너스": Luminous,
        "메르세데스": Mercedes,
        "팬텀": Phantom,
        "은월": Eunwol,
        "메카닉": Registance,
        "배틀메이지": Registance,
        "와일드헌터": Registance,
        "블래스터": Registance,
        "제논": Zenon,
        "데몬어벤져": DemonAvenger,
        "데몬슬레이어": DemonSlayer,
        "카이저": Kaiser,
        "엔젤릭버스터": Angelicbuster,
        "카데나": Cadena,
        "일리움": Illium,
        "아크": Ark,
        "아델": Adele,
        "제로": Zero,
        "키네시스": Kinesis,
        "호영": Hoyoung,
        "카인": Kain
    }

    @staticmethod
    def get_link_skill_modifier(
        refMDF: ExMDF, job_name: str
    ) -> InformedCharacterModifier:
        def get_mdf(links: List[InformedCharacterModifier]):
            return reduce(lambda x, y: x + y, links)

        links = {LinkSkill.Registance, LinkSkill.Angelicbuster}
        links.add(LinkSkill.jobdict[job_name])

        # TODO: 미하일링크 사용시 이쪽에 사용 직업들 추가

        if job_name in ["소울마스터", "카데나", "제로", "블래스터", "배틀메이지", "스트라이커", "나이트워커"]:
            links.add(LinkSkill.Illium)

        if (refMDF + get_mdf(links)).armor_ignore < 90:
            links.add(LinkSkill.Luminous)
        if (refMDF + get_mdf(links)).armor_ignore < 85:
            links.add(LinkSkill.Zero)
        if (refMDF + get_mdf(links)).armor_ignore < 85:
            links.add(LinkSkill.Hoyoung)

        if (refMDF + get_mdf(links)).crit < 90:
            links.add(LinkSkill.Phantom)
        if (refMDF + get_mdf(links)).crit < 90:
            links.add(LinkSkill.AdventureArcher)

        link_priority = [
            LinkSkill.DemonSlayer,
            LinkSkill.AdventureMage,
            LinkSkill.Cadena,
            LinkSkill.Kinesis,
            LinkSkill.Ark,
            LinkSkill.DemonAvenger,
            LinkSkill.AdventureRog,
            LinkSkill.Kaiser if job_name == "데몬어벤져" else LinkSkill.Zenon,
            LinkSkill.Cygnus,
            LinkSkill.Adele,
            LinkSkill.AdventurePirate,
        ]
        for link in link_priority:
            if len(links) < 13:
                links.add(link)

        return get_mdf(links)
