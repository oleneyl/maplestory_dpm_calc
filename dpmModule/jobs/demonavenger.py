from enum import Enum

from dpmModule.jobs.globalSkill import GlobalSkills

from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from . import globalSkill
from ..execution.rules import RuleSet, ConcurrentRunRule
from .jobbranch import warriors
from .jobclass import demon
from . import jobutils
from math import ceil
from typing import Any, Dict

# TODO: 극딜 딜사이클, 패시브 수치

'''
Advisor:
연어먹던곰, 키카이, 능이조아
'''


# English skill information for Demon Avenger here https://maplestory.fandom.com/wiki/Demon_Avenger/Skills
class DemonAvengerSkills(Enum):
    # Link Skill
    WildRage = 'Wild Rage | 와일드 레이지'
    # Beginner
    DarkWinds = 'Dark Winds | 데몬 점프'
    DemonicBlood = 'Demonic Blood | 데모닉 블러드'
    DemonWings = 'Demon Wings | 데빌 윙즈'
    Exceed = 'Exceed | 익시드'
    HyperPotionMastery = 'Hyper Potion Mastery | 하이 이피션시'
    StarForceConversion = 'Star Force Conversion | 컨버전 스타포스'
    BloodPact = 'Blood Pact | 블러드 컨트랙트'
    # 1st Job
    ExceedDoubleSlash = 'Exceed: Double Slash | 익시드: 더블 슬래시'
    OverloadRelease = 'Overload Release | 릴리즈 오버로드'
    LifeSap = 'Life Sap | 앱졸브 라이프'
    DemonicVeracity = 'Demonic Veracity | 데모닉 샤프니스'
    # 2nd Job
    ExceedDemonStrike = 'Exceed: Demon Strike | 익시드: 데몬 스트라이크'
    BatSwarm = 'Bat Swarm | 배츠 스웜'
    BattlePact = 'Battle Pact | 데몬 부스터'
    AbyssalConnection = 'Abyssal Connection | 어비셜 레이지'
    UnbreakableSteel = 'Unbreakable Steel | 솔리드 윌'
    DesperadoMastery = 'Desperado Mastery | 데스페라도 마스터리'
    RageWithin = 'Rage Within | 이너 스트렝스'
    # 3rd Job
    ExceedLunarSlash = 'Exceed: Lunar Slash | 익시드: 문라이트 슬래시'
    VitalityVeil = 'Vitality Veil | 인헤일 바이탈러티'
    ShieldCharge = 'Shield Charge | 쉴드 차지'
    WardEvil = 'Ward Evil | 리프랙트 이블'
    DiabolicRecovery = 'Diabolic Recovery | 디아볼릭 리커버리'
    PainDampener = 'Pain Dampener | 이즈 익시드 페인'
    AdvancedLifeSap = 'Advanced Life Sap | 어드밴스드 앱졸브 라이프'
    # 4th Job
    ExceedExecution = 'Exceed: Execution | 익시드: 엑스큐션'
    NetherShield = 'Nether Shield | 실드 체이싱'
    NetherSlice = 'Nether Slice | 아머 브레이크'
    BloodPrison = 'Blood Prison | 블러디 임프리즌'
    OverwhelmingPower = 'Overwhelming Power | 오버휄밍 파워'
    DefenseExpertise = 'Defense Expertise | 디펜스 엑스퍼타이즈'
    AdvancedDesperadoMastery = 'Advanced Desperado Mastery | 어드밴스드 데스페라도 마스터리'
    InfernalExceed = 'Infernal Exceed | 인핸스드 익시드'
    # Hypers
    ThousandSwords = 'Thousand Swords | 사우전드 소드'
    DemonicFortitude = 'Demonic Fortitude | 데모닉 포티튜드'
    ForbiddenContract = 'Forbidden Contract | 포비든 컨트랙트'
    # 5th Job
    DemonicFrenzy = 'Demonic Frenzy | 데몬 프렌지'
    DemonicBlast = 'Demonic Blast | 블러드 피스트'
    DimensionalSword = 'Dimensional Sword | 디멘션 소드'
    Revenant = 'Revenant | 레버넌트'


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "HP"
        self.jobname = "데몬어벤져"
        self.vEnhanceNum = 12
        # Write, write, write order (not yet implemented). 쓸샾, 쓸뻥, 쓸오더(아직 미구현).
        self.preEmptiveSkills = 3

        self.ability_list = Ability_tool.get_ability_set('reuse', 'crit', 'boss_pdamage')

    def get_ruleset(self):
        '''
        Damage Cycle Cleanup

        딜 사이클 정리
        '''
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('디멘션 소드', '데모닉 포티튜드'), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore=30)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        # TODO: Blood Contract. 블러드 컨트랙트.
        # Conversion Star Force. 컨버전 스타포스.
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


        # Juice stat not reflected, please add. 주스탯 미반영, 추가바람.
        AbyssalRage = core.InformedCharacterModifier("어비셜 레이지", att=40)
        AdvancedDesperadoMastery = core.InformedCharacterModifier("어드밴스드 데스페라도 마스터리", att=50+passive_level, crit_damage=8)
        OverwhelmingPower = core.InformedCharacterModifier("오버휄밍 파워", pdamage=30+passive_level)
        DefenseExpertise = core.InformedCharacterModifier("디펜스 엑스퍼타이즈", armor_ignore=30+passive_level)
        DemonicSharpness = core.InformedCharacterModifier("데모닉 샤프니스", crit=20)

        # Meyong: Fixed to +15% health. 메용: 체력+15%로 수정.
        MapleHeroesDemon = core.InformedCharacterModifier("메이플 용사(데몬어벤져)", pstat_main=15+self.combat/2)

        InnerStrength = core.InformedCharacterModifier("이너 스트렝스", stat_main=600)

        return [ConversionStarforce, AbyssalRage, AdvancedDesperadoMastery, OverwhelmingPower, DefenseExpertise, DemonicSharpness, MapleHeroesDemon, InnerStrength]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=30)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep=-5+0.5*ceil(passive_level/2))

        HP_RATE = options.get('hp_rate', 100)

        # Increases final damage by 1% per 3% HP consumed (4% at 24 levels) compared to the maximum HP. 최대 HP 대비 소모된 HP 3%(24레벨가지는 4%)당 최종 데미지 1% 증가.
        FrenzyPassive = core.InformedCharacterModifier("데몬 프렌지 (최종 데미지)", pdamage_indep=(100-HP_RATE)//(4-(vEhc.getV(0, 0)//25)))

        return [WeaponConstant, Mastery, FrenzyPassive]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Hyper: 3 types of Ex-seed, Shield Chasing Reinforce, and Extra Target applied

        Demon Frenzy-10.8 hits/s per stack, 2 stacks, HP 100%

        Blood Fist 3 stacks per cooldown (Cancel X)

        Dimension Sword-Recast X

        하이퍼: 익시드 3종, 실드 체이싱 리인포스, 엑스트라 타겟 적용

        데몬 프렌지 - 중첩당 10.8타/s, 2중첩, HP 100%

        블러드 피스트 쿨타임마다 3중첩 (캔슬 X)

        디멘션 소드 - 재시전 X
        '''

        passive_level = chtr.get_base_modifier().passive_level+self.combat

        FRENZY_STACK = options.get('frenzy_hit', 2)    # Number of nests. 중첩 수.

        ######   Skill   ######

        ### Buff skills ###

        # Pet buff. 펫버프.
        Booster = core.BuffSkill("데몬 부스터", 0, 180*1000).wrap(core.BuffSkillWrapper)
        DiabolicRecovery = core.BuffSkill("디아볼릭 리커버리", 0, 180*1000).wrap(core.BuffSkillWrapper)
        WardEvil = core.BuffSkill("리프랙트 이블", 0, 180*1000).wrap(core.BuffSkillWrapper)

        ForbiddenContract = core.BuffSkill("포비든 컨트랙트", 1020, 30*1000, cooltime=75*1000, pdamage=10).wrap(core.BuffSkillWrapper)
        DemonicFortitude = core.BuffSkill("데모닉 포티튜드", 0, 60*1000, cooltime=120*1000, pdamage=10).wrap(core.BuffSkillWrapper)

        # Delay cannot be checked in WiccomR. 위컴알에서 딜레이 확인 불가.
        ReleaseOverload = core.BuffSkill("릴리즈 오버로드", 0, 60*1000, pdamage_indep=25, rem=True).wrap(core.BuffSkillWrapper)

        ### Damage skills ###

        # Exceed 0~3 stack: Clar standard delay 900, 900, 840, 780. 익시드 0~3스택: 클라기준 딜레이 900, 900, 840, 780.
        # Entering reinforcement mode in 3 times when using Exceed immediately after release. 릴리즈 사용 직후 익시드 사용시 3번만에 강화모드 진입.
        Execution_0 = core.DamageSkill("익시드: 엑스큐션(0스택)", 660, 540+8*self.combat, 4, modifier=core.CharacterModifier(armor_ignore=30+self.combat, pdamage=20+20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Execution_1 = core.DamageSkill("익시드: 엑스큐션(1스택)", 630, 540+8*self.combat, 4, modifier=core.CharacterModifier(armor_ignore=30+self.combat, pdamage=20+20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Execution_2 = core.DamageSkill("익시드: 엑스큐션(2스택)", 600, 540+8*self.combat, 4, modifier=core.CharacterModifier(armor_ignore=30+self.combat, pdamage=20+20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Execution_3 = core.DamageSkill("익시드: 엑스큐션(3스택)", 570, 540+8*self.combat, 4, modifier=core.CharacterModifier(armor_ignore=30+self.combat, pdamage=20+20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        # Five or more extended seeded stacks. 익시드 5스택 이상.
        ExecutionExceed = core.DamageSkill("익시드: 엑스큐션(강화)", 540, 540+8*self.combat, 6, modifier=core.CharacterModifier(armor_ignore=30+self.combat, pdamage=20+20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        # Up to 10 attacks. 최대 10회 공격.
        ShieldChasing = core.DamageSkill("실드 체이싱", 720, 500+10*self.combat, 2*2*(8+2), cooltime=6000, modifier=core.CharacterModifier(armor_ignore=30+passive_level, pdamage=20+20), red=True).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)

        ArmorBreak = core.DamageSkill("아머 브레이크", 0, 350+5*self.combat, 4, cooltime=(30+self.combat)*1000).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        ArmorBreakBuff = core.BuffSkill("아머 브레이크(디버프)", 720, (30+self.combat)*1000, armor_ignore=30+self.combat).wrap(core.BuffSkillWrapper)

        # ThousandSword = core.Damageskill("사우전드 소드", 0, 500, 8, cooltime = 8*1000).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)

        # Bonus chance 70% -> 80%. 보너스 찬스 70% -> 80%.
        EnhancedExceed = core.DamageSkill("인핸스드 익시드", 0, 200+4*passive_level, 2*(0.8+0.04*passive_level), cooltime=-1).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)

        # 24 shots against the scarecrow. 허수아비 상대 24타.
        BatSwarm = core.SummonSkill("배츠 스웜", 840, 330, 200, 1, 24*330).setV(vEhc, 3, 5, True).wrap(core.SummonSkillWrapper)

        # BloodImprison = core.DamageSkill("블러디 임프리즌", 0, 800, 3, cooltime = 120*1000)

        ### V skills ###

        # Assume 10.8 hits per second. 초당 10.8타 가정.
        # http://www.inven.co.kr/board/maple/2304/23974

        DemonFrenzy = core.SummonSkill("데몬 프렌지", 0, 1000/10.8, 300+8*vEhc.getV(0, 0), FRENZY_STACK, 99999999).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)

        # Bluffy (3 stacks). 블피 (3중첩).
        # TODO: Implemented blpe cancellation (when using blpe while casting another skill, the previously used skill delay is canceled and blppy is activated immediately). 블피캔슬 구현 (다른스킬 시전중에 블피사용시 그 전에 사용한 스킬 딜레이가 캔슬되고 즉시 블피가 발동).
        DemonicBlast = core.DamageSkill("블러드 피스트", 330, 800+32*vEhc.getV(0, 0), 7, cooltime=17000, modifier=core.CharacterModifier(crit=100, armor_ignore=100)).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        # Standard deal. 평딜 기준.
        # Reference: https://blog.naver.com/oe135/221372243858. 참고자료: https://blog.naver.com/oe135/221372243858
        DimensionSword = core.SummonSkill("디멘션 소드", 660, 3000, 1250+14*vEhc.getV(0, 0), 8, 40*1000, cooltime=120*1000, modifier=core.CharacterModifier(armor_ignore=100)).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)
        # DimensionSwordReuse = core.SummonSkill("디멘션 소드", 660, 210, 300+vEhc.getV(0, 0)*12, 6, 8*1000, cooltime=120*1000, modifier=core.CharacterModifier(armor_ignore=100)).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)

        # Default 4000ms. 기본 4000ms.
        # Adjusted to trigger every 2 Accu. 엑큐 2번당 발동하도록 조정.
        REVENANT_COOLTIME = 1080
        Revenant = core.BuffSkill("레버넌트", 1530, (30+vEhc.getV(0, 0)//5)*1000, cooltime=300000, rem=False).isV(vEhc, 0, 0).wrap(core.BuffSkillWrapper)
        RevenantHit = core.DamageSkill("레버넌트(분노의 가시)", 0, 300+vEhc.getV(0, 0)*12, 9, cooltime=REVENANT_COOLTIME, modifier=core.CharacterModifier(armor_ignore=30), red=False).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        # Demon 5th common. 데몬 5차 공용.
        CallMastema = demon.CallMastemaWrapper(vEhc, 0, 0)
        AnotherGoddessBuff, AnotherVoid = demon.AnotherWorldWrapper(vEhc, 0, 0)

        ######   Skill Wrapper   ######

        # TODO: Need to check armor brake efficiency. 아머 브레이크 효율 확인필요.
        ArmorBreakBuff.onAfter(ArmorBreak)

        BasicAttack = core.DamageSkill("기본 공격", 0, 0, 0).wrap(core.DamageSkillWrapper)
        BasicAttack.onAfter(core.OptionalElement(ReleaseOverload.is_active, ExecutionExceed, ReleaseOverload))
        ReleaseOverload.onAfter(Execution_1)
        ReleaseOverload.onAfter(Execution_2)
        ReleaseOverload.protect_from_running()

        RevenantHitOpt = core.OptionalElement(lambda : Revenant.is_active() and RevenantHit.is_available(), RevenantHit, name="레버넌트 타격 여부 확인")
        RevenantHit.protect_from_running()

        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 3, 2)

        # Exceed skill follow-up. 익시드 스킬 후속타.
        for sk in [Execution_0, Execution_1, Execution_2, Execution_3, ExecutionExceed]:
            sk.onAfter(EnhancedExceed)
            sk.onAfter(RevenantHitOpt)
            auraweapon_builder.add_aura_weapon(sk)

        # non-extended skill follow-up hit. non 익시드 스킬 후속타.
        for sk in [ArmorBreak, DemonicBlast]:
            auraweapon_builder.add_aura_weapon(sk)

        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        '''
        This is an initializer to advance the timing of the Frenzy activation.
        In general, SummonSkill has a lower execution priority than BuffSkill, so without this code, Frenzy will only run after 7-8 seconds.
        
        프렌지 발동 타이밍을 앞당기기 위한 initializer입니다.
        일반적으로 SummonSkill이 BuffSkill보다 실행 순위가 밀리기 때문에 이 코드가 없으면 프렌지가 7~8초 후에서야 실행됩니다.
        '''
        FrenzyInit = core.BuffSkill("데몬 프렌지(개시)", 0, 999999999).wrap(core.BuffSkillWrapper)
        FrenzyInit.onAfter(DemonFrenzy)
        DemonFrenzy.protect_from_running()

        return(BasicAttack,
               [FrenzyInit, globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_hyper_body_demonavenger(),
                DemonFrenzy, Booster, ReleaseOverload, DiabolicRecovery, WardEvil, ForbiddenContract, DemonicFortitude, AuraWeaponBuff, AuraWeapon,
                globalSkill.soul_contract(), Revenant, RevenantHit, CallMastema, AnotherGoddessBuff, AnotherVoid] +
               [ShieldChasing, ArmorBreakBuff] +
               [BatSwarm, MirrorBreak, MirrorSpider, DimensionSword, DemonicBlast] +
               [BasicAttack])
