from functools import reduce
from typing import List

from ..kernel.core import ExtendedCharacterModifier as ExMDF
from ..kernel.core import InformedCharacterModifier

from localization.utilities import translator
_ = translator.gettext


class LinkSkill:
    DemonSlayer = InformedCharacterModifier(_("링크(데몬슬레이어)"), boss_pdamage=15)
    DemonAvenger = InformedCharacterModifier(_("링크(데몬어벤져)"), pdamage=10)
    Ark = InformedCharacterModifier(_("링크(아크)"), pdamage=11)
    Illium = InformedCharacterModifier(_("링크(일리움)"), pdamage=12)
    Cadena = InformedCharacterModifier(_("링크(카데나)"), pdamage=12)  # optional
    AdventureMage = InformedCharacterModifier(_("링크(모법)"), pdamage=9, armor_ignore=9)
    AdventureRog = InformedCharacterModifier(_("링크(모도)"), pdamage=18 / 2)
    Adele = InformedCharacterModifier(_("링크(아델)"), pdamage=2, boss_pdamage=4)
    Luminous = InformedCharacterModifier(_("링크(루미너스)"), armor_ignore=15)
    Zero = InformedCharacterModifier(_("링크(제로)"), armor_ignore=10)
    Hoyoung = InformedCharacterModifier(_("링크(호영)"), armor_ignore=10)
    Zenon = InformedCharacterModifier(_("링크(제논)"), pstat_main=10, pstat_sub=10)
    AdventurePirate = InformedCharacterModifier(_("링크(모해)"), stat_main=70, stat_sub=70)
    Cygnus = InformedCharacterModifier(_("링크(시그너스)"), att=25)
    Phantom = InformedCharacterModifier(_("링크(팬텀)"), crit=15)
    AdventureArcher = InformedCharacterModifier(_("링크(모궁)"), crit=10)
    Kinesis = InformedCharacterModifier(_("링크(키네시스)"), crit_damage=4)
    Kain = InformedCharacterModifier(_("링크(카인)"), pdamage=17/2)  # pdamage TODO: implement kain link skill
    Angelicbuster = InformedCharacterModifier(_("링크(엔젤릭버스터)"))  # Skill
    Michael = InformedCharacterModifier(_("링크(미하일)"))  # Util skill
    Mercedes = InformedCharacterModifier(_("링크(메르세데스)"))  # Exp
    Aran = InformedCharacterModifier(_("링크(아란)"))  # Exp
    Evan = InformedCharacterModifier(_("링크(에반)"))  # Exp
    Eunwol = InformedCharacterModifier(_("링크(은월)"))  # Util
    Kaiser = InformedCharacterModifier(_("링크(카이저)"), pstat_main=15)  # HP - Demon Avenger only
    Registance = InformedCharacterModifier(_("링크(레지스탕스)"))  # Util
    AdventureWarrior = InformedCharacterModifier(_("링크(모전)"))  # Skill

    jobdict = {
        _("아크메이지불/독"): AdventureMage,
        _("아크메이지썬/콜"): AdventureMage,
        _("비숍"): AdventureMage,
        _("히어로"): AdventureWarrior,
        _("팔라딘"): AdventureWarrior,
        _("다크나이트"): AdventureWarrior,
        _("보우마스터"): AdventureArcher,
        _("패스파인더"): AdventureArcher,
        _("신궁"): AdventureArcher,
        _("나이트로드"): AdventureRog,
        _("섀도어"): AdventureRog,
        _("듀얼블레이드"): AdventureRog,
        _("캡틴"): AdventurePirate,
        _("바이퍼"): AdventurePirate,
        _("캐논슈터"): AdventurePirate,
        _("소울마스터"): Cygnus,
        _("플레임위자드"): Cygnus,
        _("윈드브레이커"): Cygnus,
        _("나이트워커"): Cygnus,
        _("스트라이커"): Cygnus,
        _("미하일"): Michael,
        _("아란"): Aran,
        _("에반"): Evan,
        _("루미너스"): Luminous,
        _("메르세데스"): Mercedes,
        _("팬텀"): Phantom,
        _("은월"): Eunwol,
        _("메카닉"): Registance,
        _("배틀메이지"): Registance,
        _("와일드헌터"): Registance,
        _("블래스터"): Registance,
        _("제논"): Zenon,
        _("데몬어벤져"): DemonAvenger,
        _("데몬슬레이어"): DemonSlayer,
        _("카이저"): Kaiser,
        _("엔젤릭버스터"): Angelicbuster,
        _("카데나"): Cadena,
        _("일리움"): Illium,
        _("아크"): Ark,
        _("아델"): Adele,
        _("제로"): Zero,
        _("키네시스"): Kinesis,
        _("호영"): Hoyoung,
        _("카인"): Kain
    }

    @staticmethod
    def get_link_skill_modifier(
        refMDF: ExMDF, job_name: str
    ) -> InformedCharacterModifier:
        def get_mdf(links: List[InformedCharacterModifier]):
            return reduce(lambda x, y: x + y, links)

        links = {LinkSkill.Registance, LinkSkill.Angelicbuster}
        links.add(LinkSkill.jobdict[job_name])

        # TODO: When using Mihile Link, add jobs to use here. 미하일링크 사용시 이쪽에 사용 직업들 추가

        if job_name in [_("소울마스터"), _("카데나"), _("제로"), _("블래스터"), _("배틀메이지"), _("스트라이커"), _("나이트워커")]:
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
            LinkSkill.Kaiser if job_name == _("데몬어벤져") else LinkSkill.Zenon,
            LinkSkill.Cygnus,
            LinkSkill.Adele,
            LinkSkill.AdventurePirate,
        ]
        for link in link_priority:
            if len(links) < 13:
                links.add(link)

        return get_mdf(links)
