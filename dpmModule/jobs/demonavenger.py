from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from ..execution.rules import RuleSet, ConcurrentRunRule, InactiveRule
from .jobbranch import warriors
from .jobclass import demon
from math import ceil
from typing import Any, Dict

# TODO: 극딜 딜사이클, 패시브 수치

'''
Advisor:
연어먹던곰, 키카이, 능이조아
'''

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "str"
        self.jobname = "데몬어벤져"
        self.vEnhanceNum = 12
        # 쓸샾, 쓸뻥, 쓸오더(아직 미구현)
        self.preEmptiveSkills = 3
        
        self.ability_list = Ability_tool.get_ability_set('reuse', 'crit', 'boss_pdamage')
    
    def get_ruleset(self):
        '''딜 사이클 정리
        '''
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('디멘션 소드 (평딜)', '데모닉 포티튜드'), RuleSet.BASE)
        return ruleset
    
    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 30)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        #TODO: 블러드 컨트랙트, 컨버전 스타포스

        #주스탯 미반영, 추가바람.
        AbyssalRage = core.InformedCharacterModifier("어비셜 레이지", att=40)
        AdvancedDesperadoMastery = core.InformedCharacterModifier("어드밴스드 데스페라도 마스터리",att = 50 + passive_level, crit_damage = 8)
        OverwhelmingPower = core.InformedCharacterModifier("오버휄밍 파워", pdamage=30 + passive_level)
        DefenseExpertise = core.InformedCharacterModifier("디펜스 엑스퍼타이즈", armor_ignore = 30 + passive_level)
        DemonicSharpness = core.InformedCharacterModifier("데모닉 샤프니스", crit=20)

        # 메용: 체력+15%로 수정
        MapleHeroesDemon = core.InformedCharacterModifier("메이플 용사(데몬어벤져)", pstat_main = 15 + self.combat / 2)
        # 최종데미지 (릴리즈 오버로드, 데몬 프렌지)
        InnerStrength = core.InformedCharacterModifier("이너 스트렝스", stat_main = 600)

        HP_RATE = 100
        #최대 HP 대비 소모된 HP 3%(24레벨가지는 4%)당 최종 데미지 1% 증가
        FrenzyPassive = core.InformedCharacterModifier("데몬 프렌지 (최종 데미지)", pdamage_indep = (100 - HP_RATE) // (4 - (vEhc.getV(0, 0) // 25)))

        return [AbyssalRage, AdvancedDesperadoMastery, OverwhelmingPower, DefenseExpertise, DemonicSharpness, MapleHeroesDemon, InnerStrength, FrenzyPassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5 + 0.5*ceil(passive_level/2))
        
        return [WeaponConstant, Mastery]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        하이퍼: 익시드 3종, 실드 체이싱 리인포스, 엑스트라 타겟 적용

        데몬 프렌지 - 중첩당 10.8타/s

        HP 100%
        
        디멘션 소드 - 재시전 X
        '''
        
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        FRENZY_STACK = 2    # 중첩 수

        ######   Skill   ######

        ### Buff skills ###
        Booster = core.BuffSkill("데몬 부스터", 990, 180*1000).wrap(core.BuffSkillWrapper)
        DiabolicRecovery = core.BuffSkill("디아볼릭 리커버리", 990, 180*1000).wrap(core.BuffSkillWrapper)
        WardEvil = core.BuffSkill("리프랙트 이블", 990, 180*1000).wrap(core.BuffSkillWrapper)

        ForbiddenContract = core.BuffSkill("포비든 컨트랙트", 1020, 30*1000, cooltime = 75*1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        DemonicFortitude = core.BuffSkill("데모닉 포티튜드", 0, 60*1000, cooltime=120*1000, pdamage=10).wrap(core.BuffSkillWrapper)

        # 위컴알에서 딜레이 확인 불가
        ReleaseOverload = core.BuffSkill("릴리즈 오버로드", 0, 60*1000, pdamage_indep= 25, rem = True).wrap(core.BuffSkillWrapper)

        ### Damage skills ###

        # 익시드 0~3스택: 클라기준 딜레이 900, 900, 840, 780
        # 릴리즈 사용 직후 익시드 사용시 3번만에 강화모드 진입
        Execution_0 = core.DamageSkill("익시드: 엑스큐션 (0스택)", 660, 540+8*self.combat, 4, modifier = core.CharacterModifier(armor_ignore = 30 + self.combat, pdamage = 20 + 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Execution_1 = core.DamageSkill("익시드: 엑스큐션 (1스택)", 630, 540+8*self.combat, 4, modifier = core.CharacterModifier(armor_ignore = 30 + self.combat, pdamage = 20 + 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Execution_2 = core.DamageSkill("익시드: 엑스큐션 (2스택)", 600, 540+8*self.combat, 4, modifier = core.CharacterModifier(armor_ignore = 30 + self.combat, pdamage = 20 + 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        Execution_3 = core.DamageSkill("익시드: 엑스큐션 (3스택)", 570, 540+8*self.combat, 4, modifier = core.CharacterModifier(armor_ignore = 30 + self.combat, pdamage = 20 + 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        # 익시드 5스택 이상
        ExecutionExceed = core.DamageSkill("익시드: 엑스큐션 (강화)", 540, 540+8*self.combat, 6, modifier = core.CharacterModifier(armor_ignore = 30 + self.combat, pdamage = 20 + 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        # 최대 10회 공격
        ShieldChasing = core.DamageSkill("실드 체이싱", 540, 500 + 10 * self.combat, 2*2*(8+2), cooltime = 6000, modifier = core.CharacterModifier(armor_ignore = 30 + passive_level, pdamage=20+20), red = True).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)

        ArmorBreak = core.DamageSkill("아머 브레이크", 0, 350 + 5 * self.combat, 4, cooltime = (30+self.combat)*1000).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        ArmorBreakBuff = core.BuffSkill("아머 브레이크(디버프)", 720, (30+self.combat)*1000, armor_ignore = 30 + self.combat).wrap(core.BuffSkillWrapper)

        #ThousandSword = core.Damageskill("사우전드 소드", 0, 500, 8, cooltime = 8*1000).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)

        # 보너스 찬스 70% -> 80%
        EnhancedExceed = core.DamageSkill("인핸스드 익시드", 0, 200+4*passive_level, 2*(0.8+0.04*passive_level), cooltime = -1).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)

        # 허수아비 상대 24타
        BatSwarm = core.SummonSkill("배츠 스웜", 840, 330, 200, 1, 24 * 330).setV(vEhc, 3, 5, True).wrap(core.SummonSkillWrapper)

        #BloodImprison = core.DamageSkill("블러디 임프리즌", 0, 800, 3, cooltime = 120*1000)

        ### V skills ###

        # 초당 10.8타 가정
        # http://www.inven.co.kr/board/maple/2304/23974

        FrenzyDOT = core.SummonSkill("프렌지 장판", 0, 1000/10.8, 300 + 8 * vEhc.getV(0, 0), FRENZY_STACK, 99999999).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)

        # 블피 (즉시 시전)
        DemonicBlast = core.DamageSkill("블러드 피스트", 0, 500 + 20*vEhc.getV(0,0), 7, cooltime = 10000, modifier = core.CharacterModifier(crit = 100, armor_ignore = 100)).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        
        # 평딜 기준
        # 참고자료: https://blog.naver.com/oe135/221372243858
        DimensionSword = core.SummonSkill("디멘션 소드 (평딜)", 660, 3000, 1250+14*vEhc.getV(0,0), 8, 40*1000, cooltime = 120*1000, modifier=core.CharacterModifier(armor_ignore=100)).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)
        DimensionSwordReuse = core.SummonSkill("디멘션 소드 (극딜)", 660, 210, 300+vEhc.getV(0,0)*12, 6, 8*1000, cooltime=120*1000, modifier=core.CharacterModifier(armor_ignore=100)).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)
        
        # 기본 4000ms
        # 엑큐 2번당 발동하도록 조정
        REVENANT_COOLTIME = 1080
        Revenant = core.BuffSkill("레버넌트", 1530, (30 + vEhc.getV(0,0)//5)*1000, cooltime = 300000, rem = False).isV(vEhc, 0, 0).wrap(core.BuffSkillWrapper)
        RevenantHit = core.DamageSkill("레버넌트(분노의 가시)", 0, 300 + vEhc.getV(0,0) * 12, 9, cooltime = REVENANT_COOLTIME, modifier = core.CharacterModifier(armor_ignore = 30), red = False).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        
        # 데몬 5차 공용
        CallMastema= demon.CallMastemaWrapper(vEhc, 0, 0)
        AnotherGoddessBuff, AnotherVoid = demon.AnotherWorldWrapper(vEhc, 0, 0)

        ######   Skill Wrapper   ######
        '''딜 사이클 정리
        https://blog.naver.com/oe135/221538210455
        매 3분마다 버프류 스킬 사용하여 극딜
        '''
        
        # TODO: 아머 브레이크 효율 확인필요
        ArmorBreakBuff.onAfter(ArmorBreak)

        BasicAttack = core.DamageSkill("기본 공격", 0, 0, 0).wrap(core.DamageSkillWrapper)
        BasicAttack.onAfter(core.OptionalElement(ReleaseOverload.is_active, ExecutionExceed, ReleaseOverload))
        ReleaseOverload.onAfter(Execution_1)
        ReleaseOverload.onAfter(Execution_2)

        RevenantHitOpt = core.OptionalElement(lambda : Revenant.is_active() and RevenantHit.is_available(), RevenantHit, name = "레버넌트 타격 여부 확인")
        RevenantHit.protect_from_running()

        for sk in [Execution_0, Execution_1, Execution_2, Execution_3, ExecutionExceed]:
            sk.onAfter(EnhancedExceed)
            sk.onAfter(RevenantHitOpt)

        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 3, 2)
        for sk in [Execution_0, Execution_1, Execution_2, Execution_3, ExecutionExceed, ShieldChasing, ArmorBreak, DemonicBlast]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()
        
        return(BasicAttack,
               [globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    FrenzyDOT, Booster, ReleaseOverload, DiabolicRecovery, WardEvil, ForbiddenContract, DemonicFortitude, AuraWeaponBuff, AuraWeapon,
                    globalSkill.soul_contract(), Revenant, RevenantHit, CallMastema, AnotherGoddessBuff, AnotherVoid] +\
                [ShieldChasing, ArmorBreakBuff] +\
                [BatSwarm, MirrorBreak, MirrorSpider, DimensionSword, DemonicBlast] +\
                [BasicAttack])
