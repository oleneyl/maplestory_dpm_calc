from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ConcurrentRunRule, RuleSet, InactiveRule, SynchronizeRule
from . import globalSkill, jobutils
from .jobbranch import warriors
from .jobclass import resistance
from math import ceil
from typing import Any, Dict


class RevolvingCannonMasteryWrapper(core.DamageSkillWrapper):
    """
    실린더 게이지 1개일때 기본 데미지, 2개 이상부터 개당 1.1배 복리 계산.
    실린더 과열 도중에는 게이지 최대치로 취급함.
    """
    def __init__(self, cylinder, overheat, passive_level):
        self.cylinder = cylinder
        self.overheat = overheat
        skill = core.DamageSkill("리볼빙 캐논 마스터리", 0, 215 + passive_level, 1)
        super(RevolvingCannonMasteryWrapper, self).__init__(skill)
        
    def _use(self, skill_modifier):
        if self._get_stack() <= 0:
            return self._result_object_cache
        
        return super(RevolvingCannonMasteryWrapper, self)._use(skill_modifier)

    def _get_stack(self) -> float:
        if self.overheat.is_active():
            return 6
        else:
            return self.cylinder.stack

    def get_damage(self) -> float:
        damage = super(RevolvingCannonMasteryWrapper, self).get_damage()
        multiplier = 1.1 ** (self._get_stack() - 1)
        return damage * multiplier

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "STR"
        self.jobname = "블래스터"
        self.vEnhanceNum = 12
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'mess')

    def get_ruleset(self):
        ruleset = RuleSet()

        ruleset.add_rule(InactiveRule('버닝 브레이커(준비)','벙커 버스터'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('버닝 브레이커(준비)','맥시마이즈 캐논'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('맥시마이즈 캐논','벙커 버스터'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('벙커 버스터', '맥시마이즈 캐논'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('발칸 펀치', '벙커 버스터'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('발칸 펀치', '맥시마이즈 캐논'), RuleSet.BASE)

        ruleset.add_rule(SynchronizeRule('버닝 브레이커(준비)', '해머 스매시(디버프)', 3420, 1), RuleSet.BASE)
        ruleset.add_rule(SynchronizeRule('발칸 펀치', '해머 스매시(디버프)', 8000, 1), RuleSet.BASE)
        
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        GuntletMastery = core.InformedCharacterModifier("건틀렛 마스터리", crit= 30, att = 20)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        ChargeMastery= core.InformedCharacterModifier("차지 마스터리", pdamage = 20)
        CombinationTraining = core.InformedCharacterModifier("콤비네이션 트레이닝", patt=15)
        GuntletExpert = core.InformedCharacterModifier("건틀렛 엑스퍼트",
            crit_damage = 20 + ceil(passive_level / 2),
            boss_pdamage = 20 + ceil(passive_level / 2)
        )
        AdvancedChargeMastery= core.InformedCharacterModifier("어드밴스드 차지 마스터리", armor_ignore = 35 + 3 * passive_level)
        CombinationTraining2 = core.InformedCharacterModifier("콤비네이션 트레이닝II", att = 40 + 2 * passive_level)
        return [GuntletMastery, PhisicalTraining, ChargeMastery, 
                        GuntletExpert, AdvancedChargeMastery, CombinationTraining]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=90+ceil(passive_level / 2))
        CombinationTraining = core.InformedCharacterModifier("콤비네이션 트레이닝II",
            pdamage_indep = 10 * (4 + ceil((20 + passive_level) / 10)),
            crit = 10 * ceil((20 + passive_level) / 7)
        )

        return [WeaponConstant, Mastery, CombinationTraining]

    def get_modifier_optimization_hint(self) -> core.CharacterModifier:
        return core.CharacterModifier(boss_pdamage=10, armor_ignore=20)

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        하이퍼 : 쇼크웨이브 보너스어택 / 펀치-리인포스, 펀치-이그노어 가드, 릴파벙-리인포스, 릴파벙-숔웨리인포스
        
        코강 순서
        릴리즈 파일 벙커  > 매그넘 펀치=더블 팡 > 해머 스매시 > 리볼빙 캐논 > 쇼크웨이브 펀치
        
        5차스킬 강화 순서
        벙커버스터 - 버닝 브레이커 - 오라웨폰 - 레지스탕스 라인 인팬트리 - 발칸 펀치
        
        매그팡 510ms
        벙커버스터는 버닝 브레이커, 맥시마이즈 캐논과 같이 사용하지 않음
        발칸 펀치는 벙커 버스터, 맥시마이즈 캐논과 같이 사용하지 않음
        
        발칸 펀치의 피격시 최종 데미지는 적용하지 않음
        '''          
        CANCEL_DELAY = 180 # 최소 150
        DUCKING_DELAY = 150 # 최소 110 (30 + 80)
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        CHARGE_TIME = ceil(480 * (1 - 2 * (20 + passive_level) * 0.01) // 30) * 30 # 어드밴스드 차지 마스터리 적용된 차지 속도 계산
        
        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 180*1000, rem = True).wrap(core.BuffSkillWrapper)

        DuckingDelay = core.DamageSkill("더킹 딜레이", DUCKING_DELAY, 0, 0, cooltime=-1).wrap(core.DamageSkillWrapper)
        
        MagnumPunch = core.DamageSkill("매그넘 펀치", 180, 430 + 2*self.combat, 3, modifier = core.CharacterModifier(pdamage = 10, armor_ignore = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        MagnumPunch_Revolve = core.DamageSkill("리볼빙 캐논(매그넘 펀치)", 0, 180 + passive_level, 3).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        
        Cylinder = core.StackSkillWrapper(core.BuffSkill("실린더 게이지", 0, 9999999), 6)
        Overheat = core.BuffSkill("실린더 과열", 0, 0, cooltime = -1).wrap(core.BuffSkillWrapper)

        ReleaseFileBunker = core.DamageSkill("릴리즈 파일 벙커", CANCEL_DELAY, 370 + passive_level, 8, modifier = core.CharacterModifier(pdamage = 20, armor_ignore = 80)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        ReleaseFileBunker_A = core.DamageSkill("릴리즈 파일 벙커(A)", 0, 220 + passive_level, 6, modifier = core.CharacterModifier(pdamage = 15)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        ReleaseFileBunker_B = core.DamageSkill("릴리즈 파일 벙커(B)", 0, 230 + passive_level, 6, modifier = core.CharacterModifier(pdamage = 15)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        ReleaseFileBunker_C = core.DamageSkill("릴리즈 파일 벙커(C)", 0, 270 + passive_level, 6, modifier = core.CharacterModifier(pdamage = 15)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        ReleaseFileBunker_D = core.DamageSkill("릴리즈 파일 벙커(D)", 0, 320 + passive_level, 6, modifier = core.CharacterModifier(pdamage = 15)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        DoublePang = core.DamageSkill("더블 팡", CANCEL_DELAY, 360 + 2*self.combat, 4, modifier = core.CharacterModifier(pdamage = 10, armor_ignore = 20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        DoublePang_Revolve = core.DamageSkill("리볼빙 캐논(더블 팡)", 0, 180 + passive_level, 3).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        
        HammerSmash = core.DamageSkill("해머 스매시", CANCEL_DELAY, 395 + 2*self.combat, 6, modifier = core.CharacterModifier(pdamage = 10, armor_ignore = 20)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        HammerSmashWave = core.SummonSkill("해머 스매시(충격파)", 0, 1500, 150, 2+2, 5000, cooltime = -1).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)
        HammerSmashDebuff = core.BuffSkill("해머 스매시(디버프)", 0, 10*1000+5000, pdamage_indep = 10, rem = False, cooltime = -1).wrap(core.BuffSkillWrapper) # 기본 10초, 충격파의 지속시간 합산
        
        RevolvingCannonMastery = RevolvingCannonMasteryWrapper(Cylinder, Overheat, passive_level)
        
        #하이퍼
        # 불릿을 사용하는 스킬 데미지 50% 증가, 불릿자동리로드 70%감소, 릴파벙이후 과열시간 1초로 감소
        MaximizeCannon = core.BuffSkill("맥시마이즈 캐논", 870, 35*1000, cooltime = 240 * 1000).wrap(core.BuffSkillWrapper)
        WillOfLiberty = core.BuffSkill("윌 오브 리버티", 0, 60*1000, cooltime = 120*1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        #5차
        RegistanceLineInfantry = resistance.ResistanceLineInfantryWrapper(vEhc, 3, 3)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        BunkerBuster = core.BuffSkill("벙커 버스터", 720, 45000, cooltime = 120000, red = True).isV(vEhc, 0, 0).wrap(core.BuffSkillWrapper)
        BunkerBusterAttack = core.DamageSkill("벙커 버스터(공격)", 0, 180 + 7 * vEhc.getV(0,0), 8, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        
        BalkanPunch = core.DamageSkill("발칸 펀치", 1140, 500 + 20 * vEhc.getV(4,4), 12, cooltime = 60 * 1000, red = True).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)
        BalkanPunchTick = core.DamageSkill("발칸 펀치(틱)", 120, 425 + 17 * vEhc.getV(4,4), 8).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper) # 24회 반복
        BalkanPunchEnd = core.DamageSkill("발칸 펀치(후딜)", 360, 0, 0).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)
        
        BurningBreaker = core.DamageSkill("버닝 브레이커(준비)", 120+210*5, 0, 0, cooltime = 100*1000, red = True).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper) # 리볼빙*3 매크로 사용, 1->2 120ms, 2~ 210ms 총 1170ms
        BurningBreakerRush = core.DamageSkill("버닝 브레이커(돌진)", 2220, 1500 + 60*vEhc.getV(1,1), 15, modifier = core.CharacterModifier(armor_ignore = 100, crit = 100)).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper) # 공속 적용됨, 2940ms -> 2220ms
        BurningBreakerExplode = core.DamageSkill("버닝 브레이커(폭발)", 0, 1200+48*vEhc.getV(1,1), 15 * 6, modifier = core.CharacterModifier(armor_ignore = 100, crit = 100)).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)

        AfterImageShockInit = core.BuffSkill("애프터이미지 쇼크", 780, 180*1000, cooltime=240*1000, red=True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        AfterImageShockStack = core.StackSkillWrapper(core.BuffSkill("애프터이미지 쇼크(스택)", 0, 99999999), 99)
        AfterImageShockActive = core.DamageSkill("애프터이미지 쇼크(액티브)", 0, 450+18*vEhc.getV(0,0), 5, cooltime=100).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        AfterImageShockPassive = core.DamageSkill("애프터이미지 쇼크(패시브)", 0, 500+20*vEhc.getV(0,0), 3, cooltime=6000).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        
        #스킬 기본 연계 연결
        ReleaseFileBunker.onAfter(Cylinder.stackController(-6))
        ReleaseFileBunker.onAfter(core.OptionalElement(
            MaximizeCannon.is_active,
            Overheat.controller(1000, "set_enabled_and_time_left"),
            Overheat.controller(7000, "set_enabled_and_time_left")
            ))
        ReleaseFileBunker.onAfters([ReleaseFileBunker_A, ReleaseFileBunker_B, ReleaseFileBunker_C, ReleaseFileBunker_D])
        HammerSmash.onAfters([HammerSmashWave, HammerSmashDebuff])

        #발칸 펀치
        BalkanPunchRepeat = core.RepeatElement(BalkanPunchTick, 24)
        BalkanPunch.onAfter(BalkanPunchRepeat)
        BalkanPunchRepeat.onAfter(BalkanPunchEnd)
        
        #맥시마이즈 캐논
        for sk in [BurningBreakerExplode, BunkerBusterAttack, MagnumPunch_Revolve, DoublePang_Revolve]:
            sk.add_runtime_modifier(MaximizeCannon, lambda sk: core.CharacterModifier(pdamage=50*sk.is_active()))
        
        #버닝 브레이커
        BurningBreaker.onAfter(BurningBreakerRush)
        BurningBreakerRush.onAfter(BurningBreakerExplode)

        #애프터이미지 쇼크 - 패시브
        UseAfterImageShockPassive = core.OptionalElement(lambda: AfterImageShockStack.judge(0, -1) and AfterImageShockPassive.is_available(), AfterImageShockPassive)
        for sk in [MagnumPunch, DoublePang, HammerSmash, BalkanPunch, BalkanPunchTick, BurningBreakerExplode]:
            sk.onAfter(UseAfterImageShockPassive)
        AfterImageShockPassive.protect_from_running()

        #애프터이미지 쇼크 - 액티브
        AfterImageShockInit.onAfter(AfterImageShockStack.stackController(99))
        UseAfterImageShockActive = core.OptionalElement(lambda: AfterImageShockStack.judge(1, 1) and AfterImageShockActive.is_available(), AfterImageShockActive)
        AfterImageShockActive.onAfter(AfterImageShockStack.stackController(-1))
        for sk in [MagnumPunch, DoublePang, HammerSmash, BalkanPunch, BalkanPunchTick, BurningBreakerExplode, ReleaseFileBunker]:
            sk.onAfter(UseAfterImageShockActive)
        AfterImageShockActive.protect_from_running()
        
        # 리볼빙 캐논 발동
        AddCylinder = core.OptionalElement(Overheat.is_not_active, Cylinder.stackController(1))
        
        MagnumPunch_Revolve_Final = core.OptionalElement(BunkerBuster.is_active, BunkerBusterAttack, MagnumPunch_Revolve)
        DoublePang_Revolve_Final = core.OptionalElement(BunkerBuster.is_active, BunkerBusterAttack, DoublePang_Revolve)
        MagnumPunch.onAfter(MagnumPunch_Revolve_Final)
        MagnumPunch.onAfter(AddCylinder)
        DoublePang.onAfter(DoublePang_Revolve_Final)
        DoublePang.onAfter(AddCylinder)

        HammerSmash.onAfter(core.OptionalElement(BunkerBuster.is_active, BunkerBusterAttack))
        
        # 기본 콤보
        Mag_Pang = core.DamageSkill("매그-팡", 0, 0, 0).wrap(core.DamageSkillWrapper)
        Mag_Pang.onAfter(MagnumPunch)
        Mag_Pang.onAfter(DoublePang)
        Mag_Pang.onAfter(DuckingDelay)
        
        # TODO: 맥시마이즈 캐논일땐 매번 릴파벙해머를 쓸 필요가 없음
        ReleaseHammer = core.DamageSkill("릴파벙해머", 0, 0, 0).wrap(core.DamageSkillWrapper)
        ReleaseHammer.onConstraint(core.ConstraintElement("실린더 게이지 최대", Cylinder, partial(Cylinder.judge, 6, 1)))
        ReleaseHammer.onAfter(ReleaseFileBunker)
        ReleaseHammer.onAfter(HammerSmash)
        ReleaseHammer.onAfter(DuckingDelay)
        
        for wrp in [MagnumPunch, DoublePang, HammerSmash, BalkanPunch, BalkanPunchTick, BurningBreakerRush]:
            wrp.onAfter(RevolvingCannonMastery)

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 2)
        for sk in [ReleaseFileBunker, BurningBreaker, HammerSmash, MagnumPunch, DoublePang, BalkanPunch, BalkanPunchTick, BurningBreakerRush]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        SoulContract = globalSkill.soul_contract()
        BurningBreaker.onBefore(SoulContract)

        SoulContract.protect_from_running()
        
        return(Mag_Pang,
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    Booster, globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), MaximizeCannon, WillOfLiberty, AuraWeaponBuff, AuraWeapon, BunkerBuster, Cylinder, Overheat, HammerSmashDebuff,
                    SoulContract] +\
                [ReleaseHammer, BurningBreaker, BalkanPunch, AfterImageShockInit, AfterImageShockActive, AfterImageShockPassive, MirrorBreak, MirrorSpider] +\
                [RegistanceLineInfantry, HammerSmashWave] +\
                [Mag_Pang])