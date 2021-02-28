from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from . import globalSkill
from ..execution.rules import RuleSet
from .jobbranch import warriors
from .jobclass import demon
from . import jobutils
from math import ceil
from typing import Any, Dict


"""
Advisor:
연어먹던곰, 키카이, 능이조아
"""


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "HP"
        self.jobname = "데몬어벤져"
        self.vEnhanceNum = 12
        # 쓸샾, 쓸뻥, 쓸오더(아직 미구현)
        self.preEmptiveSkills = 3

        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'reuse')

    def get_ruleset(self):
        ruleset = RuleSet()
        # ruleset.add_rule(ConcurrentRunRule('디멘션 소드', '데모닉 포티튜드'), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore=30)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        # TODO: 블러드 컨트랙트
        # 컨버전 스타포스
        star = jobutils.get_starforce_count(chtr)
        if star <= 35: value = 60
        elif star <= 60: value = 80
        elif star <= 100: value = 100
        elif star <= 140: value = 120
        elif star <= 200: value = 140
        elif star <= 220: value = 142
        elif star <= 250: value = 144
        elif star <= 270: value = 146
        elif star <= 290: value = 148
        elif star <= 310: value = 150
        else: value = (star - 301) // 10 * 2 + 150
        ConversionStarforce = core.InformedCharacterModifier("컨버전 스타포스", stat_main=star * value)


        # 주스탯 미반영, 추가바람.
        # 주스탯 미반영, 추가바람.
        AbyssalRage = core.InformedCharacterModifier("어비셜 레이지", att=40)
        AdvancedDesperadoMastery = core.InformedCharacterModifier("어드밴스드 데스페라도 마스터리", att=50+passive_level, crit_damage=8)
        OverwhelmingPower = core.InformedCharacterModifier("오버휄밍 파워", pdamage=30+passive_level)
        DefenseExpertise = core.InformedCharacterModifier("디펜스 엑스퍼타이즈", armor_ignore=30+passive_level)
        DemonicSharpness = core.InformedCharacterModifier("데모닉 샤프니스", crit=20)

        # 메용: 체력+15%로 수정
        MapleHeroesDemon = core.InformedCharacterModifier("메이플 용사(데몬어벤져)", pstat_main=15+self.combat/2)

        InnerStrength = core.InformedCharacterModifier("이너 스트렝스", stat_main=600)

        return [ConversionStarforce, AbyssalRage, AdvancedDesperadoMastery, OverwhelmingPower, DefenseExpertise, DemonicSharpness, MapleHeroesDemon, InnerStrength]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=30)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=90+ceil(passive_level/2))

        HP_RATE = options.get('hp_rate', 100)

        # 최대 HP 대비 소모된 HP 3%(24레벨가지는 4%)당 최종 데미지 1% 증가
        FrenzyPassive = core.InformedCharacterModifier(
            "데몬 프렌지 (최종 데미지)",
            pdamage_indep=min((100 - HP_RATE) // (3 - (vEhc.getV(0, 0) // 25)), 35)
        )

        return [WeaponConstant, Mastery, FrenzyPassive]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        """
        하이퍼: 익시드 3종, 실드 체이싱 리인포스, 엑스트라 타겟 적용

        데몬 프렌지 - 중첩당 10.8타/s, 2중첩, HP 100%

        블러드 피스트 쿨타임마다 3중첩 (캔슬 X)

        디멘션 소드 - 재시전 X
        """

        passive_level = chtr.get_base_modifier().passive_level+self.combat

        FRENZY_STACK = options.get('frenzy_hit', 2)  # 프렌지 중첩 수
        BATS_HIT = options.get('bats', 24)  # 배츠 스웜 타수
        DIMENSION_PHASE = options.get('dimension_phase', 1)

        ######   Skill   ######

        ### Buff skills ###

        # 펫버프
        Booster = core.BuffSkill("데몬 부스터", 0, 180*1000).wrap(core.BuffSkillWrapper)
        DiabolicRecovery = core.BuffSkill("디아볼릭 리커버리", 0, 180*1000, pstat_main=25).wrap(core.BuffSkillWrapper)
        WardEvil = core.BuffSkill("리프랙트 이블", 0, 180*1000).wrap(core.BuffSkillWrapper)

        ForbiddenContract = core.BuffSkill("포비든 컨트랙트", 1020, 30*1000, cooltime=75*1000, pdamage=10).wrap(core.BuffSkillWrapper)
        DemonicFortitude = core.BuffSkill("데모닉 포티튜드", 0, 60*1000, cooltime=120*1000, pdamage=10).wrap(core.BuffSkillWrapper)

        # 위컴알에서 딜레이 확인 불가
        ReleaseOverload = core.BuffSkill("릴리즈 오버로드", 0, 60*1000, pdamage_indep=25, rem=True).wrap(core.BuffSkillWrapper)

        ### Damage skills ###

        # 익시드 0~3스택: 클라기준 딜레이 900, 900, 840, 780
        # 릴리즈 사용 직후 익시드 사용시 2스택 부터 시작
        Execution_0 = core.DamageSkill("익시드: 엑스큐션(0스택)", 660, 540+8*self.combat, 4, modifier=core.CharacterModifier(armor_ignore=30+self.combat, pdamage=20+20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Execution_1 = core.DamageSkill("익시드: 엑스큐션(1스택)", 630, 540+8*self.combat, 4, modifier=core.CharacterModifier(armor_ignore=30+self.combat, pdamage=20+20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Execution_2 = core.DamageSkill("익시드: 엑스큐션(2스택)", 600, 540+8*self.combat, 4, modifier=core.CharacterModifier(armor_ignore=30+self.combat, pdamage=20+20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Execution_3 = core.DamageSkill("익시드: 엑스큐션(3스택)", 570, 540+8*self.combat, 4, modifier=core.CharacterModifier(armor_ignore=30+self.combat, pdamage=20+20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        # 익시드 4스택 이상
        ExecutionExceed = core.DamageSkill("익시드: 엑스큐션(강화)", 540, 540+8*self.combat, 6, modifier=core.CharacterModifier(armor_ignore=30+self.combat, pdamage=20+20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        # 최대 10회 공격
        ShieldChasing = core.DamageSkill("실드 체이싱", 720, 500+10*self.combat, 2*2*(8+2), cooltime=6000, modifier=core.CharacterModifier(armor_ignore=30+passive_level, pdamage=20+20), red=True).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)

        ArmorBreak = core.DamageSkill("아머 브레이크", 660, 350+5*self.combat, 4, cooltime=-1).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        ArmorBreakBuff = core.BuffSkill("아머 브레이크(디버프)", 0, (30+self.combat)*1000, armor_ignore=30+self.combat).wrap(core.BuffSkillWrapper)

        # ThousandSword = core.Damageskill("사우전드 소드", 0, 500, 8, cooltime = 8*1000).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)

        # 보너스 찬스 70% -> 80%
        EnhancedExceed = core.DamageSkill("인핸스드 익시드", 0, 200+4*passive_level, 2*(0.8+0.04*passive_level), cooltime=-1).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)

        if BATS_HIT > 0:  # avoid dividing by zero
            BatSwarm = core.SummonSkill("배츠 스웜", 840, 330/(BATS_HIT/24), 200, 1, 24*330).setV(vEhc, 3, 5, True).wrap(core.SummonSkillWrapper)
        else:
            BatSwarm = None

        # BloodImprison = core.DamageSkill("블러디 임프리즌", 0, 800, 3, cooltime = 120*1000)

        ### V skills ###

        # 초당 10.8타 가정
        # http://www.inven.co.kr/board/maple/2304/23974
        DemonFrenzy = core.SummonSkill("데몬 프렌지", 0, 1000/10.8, 300+8*vEhc.getV(0, 0), FRENZY_STACK, 99999999).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)

        # 블피 (3중첩)
        # TODO: 블피캔슬 구현 (다른스킬 시전중에 블피사용시 그 전에 사용한 스킬 딜레이가 캔슬되고 즉시 블피가 발동)
        DemonicBlast = core.DamageSkill("블러드 피스트", 330, 800+32*vEhc.getV(0, 0), 7, cooltime=17000, red=True, modifier=core.CharacterModifier(crit=100, armor_ignore=100)).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        # 평딜 기준
        # 참고자료: https://blog.naver.com/oe135/221372243858
        if DIMENSION_PHASE == 1:
            DimensionSword = core.SummonSkill("디멘션 소드", 510, 3000, 850+34*vEhc.getV(0, 0), 8, 40*1000, cooltime=120*1000, red=True, modifier=core.CharacterModifier(armor_ignore=100)).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)
        else:
            DimensionSword = core.SummonSkill("디멘션 소드", 510, 210, 300+12*vEhc.getV(0, 0), 6, (40*1000-510)*0.2, cooltime=120*1000, modifier=core.CharacterModifier(armor_ignore=100), red=True).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)

        # 기본 4000ms
        # 엑큐 2번당 발동하도록 조정
        REVENANT_COOLTIME = 1080
        Revenant = core.BuffSkill("레버넌트", 1530, 30*1000, cooltime=240*1000, red=True).isV(vEhc, 0, 0).wrap(core.BuffSkillWrapper)
        RevenantHit = core.DamageSkill("레버넌트(분노의 가시)", 0, 300+vEhc.getV(0, 0)*12, 9, cooltime=REVENANT_COOLTIME, modifier=core.CharacterModifier(armor_ignore=30), red=False).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        # 데몬 5차 공용
        CallMastema = demon.CallMastemaWrapper(vEhc, 0, 0)
        AnotherGoddessBuff, AnotherVoid = demon.AnotherWorldWrapper(vEhc, 0, 0)

        ######   Skill Wrapper   ######
        ArmorBreakBuff.onBefore(ArmorBreak)

        BasicAttack = core.DamageSkill("기본 공격", 0, 0, 0).wrap(core.DamageSkillWrapper)
        BasicAttack.onAfter(core.OptionalElement(ReleaseOverload.is_active, ExecutionExceed, ReleaseOverload))
        ReleaseOverload.onAfter(Execution_2)
        ReleaseOverload.onAfter(Execution_3)
        ReleaseOverload.protect_from_running()

        RevenantHitOpt = core.OptionalElement(lambda : Revenant.is_active() and RevenantHit.is_available(), RevenantHit, name="레버넌트 타격 여부 확인")
        RevenantHit.protect_from_running()

        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 3, 2)

        # 익시드 스킬 후속타
        for sk in [Execution_0, Execution_1, Execution_2, Execution_3, ExecutionExceed]:
            sk.onAfter(EnhancedExceed)
            sk.onAfter(RevenantHitOpt)
            auraweapon_builder.add_aura_weapon(sk)

        # non 익시드 스킬 후속타
        for sk in [ArmorBreak, DemonicBlast]:
            auraweapon_builder.add_aura_weapon(sk)

        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        """
        프렌지 발동 타이밍을 앞당기기 위한 initializer입니다.
        일반적으로 SummonSkill이 BuffSkill보다 실행 순위가 밀리기 때문에 이 코드가 없으면 프렌지가 7~8초 후에서야 실행됩니다.
        """

        FrenzyInit = core.BuffSkill("데몬 프렌지(개시)", 0, 999999999).wrap(core.BuffSkillWrapper)
        FrenzyInit.onAfter(DemonFrenzy)
        DemonFrenzy.protect_from_running()

        return(BasicAttack,
               [FrenzyInit, globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_hyper_body_demonavenger(),
                Booster, ReleaseOverload, DiabolicRecovery, WardEvil, ForbiddenContract, DemonicFortitude, AuraWeaponBuff, AuraWeapon,
                globalSkill.soul_contract(), Revenant, RevenantHit, CallMastema, AnotherGoddessBuff, AnotherVoid] +
               [DemonFrenzy, ShieldChasing, ArmorBreakBuff] +
               [BatSwarm, MirrorBreak, MirrorSpider, DimensionSword, DemonicBlast] +
               [BasicAttack])
