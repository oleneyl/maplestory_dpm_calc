from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConditionRule
from . import globalSkill, jobutils
from .jobbranch import pirates
from .jobclass import adventurer
from math import ceil
from typing import Any, Dict
import os


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.load(os.path.join(os.path.dirname(__file__), 'configs', 'canonshooter.json'))

    def get_ruleset(self):
        def cannonball_rule(soul_contract):
            if soul_contract.is_active():
                return True
            if soul_contract.is_cooltime_left(50000, -1):
                return False
            return True

        ruleset = RuleSet()
        ruleset.add_rule(
            ConditionRule("빅 휴즈 기간틱 캐논볼", "소울 컨트랙트", cannonball_rule),
            RuleSet.BASE,
        )
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=66, crit_damage=6, armor_ignore=30)

    def get_passive_skill_list(
        self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]
    ):
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 3, 4)
        return super(JobGenerator, self).get_passive_skill_list(vEhc, chtr, options) + [LoadedDicePassive]

    def generate(self, vEhc, chtr: ck.AbstractCharacter, options: Dict[str, Any]):
        """
        하이퍼 : 몽키트윈스-스플릿, 인핸스, 캐논버스터 - 리인포스, 보너스 어택.
        롤링캐논레인보우 26타

        코코볼 6초
        이씨밤 5타

        코강 순서:
        버스터-서포트-다수기-롤캐
        """
        COCOBALLHIT = options.get("cocoball_hit", 27)
        ICBMHIT = 6
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        self.passive_level = passive_level
        # Buff skills
        Booster = self.load_skill_wrapper("부스터")
        Buckshot = self.load_skill_wrapper("벅 샷")

        LuckyDice = self.load_skill_wrapper("로디드 다이스", vEhc)

        MonkeyWave = self.load_skill_wrapper("몽키 웨이브", vEhc)
        MonkeyWaveBuff = self.load_skill_wrapper("몽키 웨이브(버프)", vEhc)

        MonkeyFurious = self.load_skill_wrapper("몽키 퓨리어스", vEhc)
        MonkeyFuriousBuff = self.load_skill_wrapper("몽키 퓨리어스(버프)", vEhc)
        MonkeyFuriousDot = self.load_skill_wrapper("몽키 퓨리어스(도트)")

        OakRoulette = self.load_skill_wrapper("오크통 룰렛")
        OakRuletDOT = self.load_skill_wrapper("오크통 룰렛(도트)")
        MonkeyMagic = self.load_skill_wrapper("하이퍼 몽키 스펠")

        # Damage Skills
        CannonBuster = self.load_skill_wrapper("캐논 버스터", vEhc)

        # Summon Skills
        SupportMonkeyTwins = self.load_skill_wrapper("서포트 몽키 트윈스", vEhc)

        # Hyper
        RollingCannonRainbow = self.load_skill_wrapper("롤링 캐논 레인보우", vEhc)
        EpicAdventure = self.load_skill_wrapper("에픽 어드벤처")

        # V skills
        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)

        PirateFlag = adventurer.PirateFlagWrapper(vEhc, 4, 3, chtr.level)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # 쿨타임마다 사용
        # 허수아비 대상 27회 충돌
        BFGCannonball = self.load_skill_wrapper("빅 휴즈 기간틱 캐논볼", vEhc)

        ICBM = self.load_skill_wrapper("ICBM", vEhc)
        ICBMDOT = self.load_skill_wrapper("ICBM(장판)", vEhc)

        SpecialMonkeyEscort_Cannon = self.load_skill_wrapper("스페셜 몽키 에스코트", vEhc)
        SpecialMonkeyEscort_Bomb = self.load_skill_wrapper("스페셜 몽키 에스코트(폭탄)", vEhc)

        FullMaker = self.load_skill_wrapper("풀 메이커", vEhc)

        ### build graph relationships
        MonkeyWave.onAfter(MonkeyWaveBuff)
        MonkeyFurious.onAfters([MonkeyFuriousBuff, MonkeyFuriousDot])

        CannonBuster.onAfter(OakRuletDOT)
        BFGCannonball.onAfter(OakRuletDOT)
        ICBM.onAfter(OakRuletDOT)

        ICBM.onAfter(ICBMDOT)

        SpecialMonkeyEscort_Cannon.onJustAfter(SpecialMonkeyEscort_Bomb)

        return (
            CannonBuster,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                Booster,
                OakRoulette,
                Buckshot,
                MonkeyMagic,
                LuckyDice,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                EpicAdventure,
                Overdrive,
                PirateFlag,
                globalSkill.soul_contract(),
            ]
            + [
                SpecialMonkeyEscort_Cannon,
                BFGCannonball,
                FullMaker,
                RollingCannonRainbow,
                SupportMonkeyTwins,
            ]
            + [MonkeyWave, MonkeyFurious, ICBM, MirrorBreak]
            + [
                SpecialMonkeyEscort_Bomb,
                MirrorSpider,
                OakRuletDOT,
                MonkeyFuriousDot,
                MonkeyWaveBuff,
                MonkeyFuriousBuff,
                ICBMDOT,
            ]  # Not used from scheduler
            + [CannonBuster],
        )
