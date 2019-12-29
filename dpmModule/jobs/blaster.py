from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, InactiveRule
from . import globalSkill
from .jobbranch import warriors
from .jobclass import resistance
#TODO : 5차 신스킬 적용

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "str"
        self.vEnhanceNum = 12
        self.ability_list = Ability_tool.get_ability_set('passive_level', 'boss_pdamage', 'crit')

    def get_ruleset(self):
        ruleset = RuleSet()

        ruleset.add_rule(InactiveRule('버닝 브레이커','벙커 버스터'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('맥시마이즈 캐논','벙커 버스터'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('벙커 버스터', '맥시마이즈 캐논'), RuleSet.BASE)
        
        return ruleset

    def get_passive_skill_list(self):
        GuntletMastery = core.InformedCharacterModifier("건틀렛 마스터리 마스터리", crit= 30, att = 20)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 드레이닝",stat_main = 30, stat_sub = 30)
        ChargeMastery= core.InformedCharacterModifier("차지 마스터리", pdamage = 20)
        GuntletExpert = core.InformedCharacterModifier("건틀렛 엑스퍼트", crit_damage = 15, boss_pdamage = 15)
        AdvancedChargeMastery= core.InformedCharacterModifier("어드밴스드 차지 마스터리", armor_ignore = 35)
        CombinationTraining = core.InformedCharacterModifier("콤비네이션 트레이닝II", att = 40)	#패시브스킬+1, 오더스+1
        return [GuntletMastery, PhisicalTraining, ChargeMastery, 
                        GuntletExpert, AdvancedChargeMastery, CombinationTraining]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)
        CombinationTraining = core.InformedCharacterModifier("콤비네이션 트레이닝II", pdamage_indep = 60, crit = 40)	#패시브스킬+1, 오더스+1
        

        return [WeaponConstant, Mastery, CombinationTraining]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        하이퍼 : 쇼크웨이브 보너스어택 / 펀치-리인포스, 펀치-이그노어 가드, 릴파벙-리인포스, 릴파벙-숔웨리인포스
        
        코강 순서
        릴리즈 파일 벙커  > 매그넘 펀치=더블 팡 > 해머 스매시 > 리볼빙 캐논 > 쇼크웨이브 펀치
        
        5차스킬 강화 순서
        벙커버스터 - 버닝 브레이커 - 오라웨폰 - 레지스탕스 라인 인팬트리
        
        9.5초당 매그팡 17회 + 릴파벙해머
        벙커버스터는 버닝 브레이커, 맥시마이즈 캐논과 같이 사용하지 않음
        
        '''          
        MAGPANGDELAY = (9500-600) / 17
        RELFILEBUNKCOOLTIME = 9500
        
        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 180*1000, rem = True).wrap(core.BuffSkillWrapper)
        
        MagnumPunch = core.DamageSkill("매그넘 펀치", 0, 430, 3, modifier = core.CharacterModifier(pdamage = 10, armor_ignore = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        MagnumPunch_Revolve = core.DamageSkill("매그넘 펀치(리볼빙 캐논)", 0, 180, 3).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        MagnumPunch_Revolve_Maximize = core.DamageSkill("매그넘 펀치(리볼빙 캐논)", 0, 180*1.5, 3).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        
        ReleaseFileBunker = core.DamageSkill("릴리즈 파일 벙커", 600, 370, 8, modifier = core.CharacterModifier(pdamage = 20, armor_ignore = 80)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper) #임의 딜레이 600
        ReleaseFileBunker_A = core.DamageSkill("릴리즈 파일 벙커(A)", 0, 220, 6, modifier = core.CharacterModifier(pdamage = 15, armor_ignore = 80)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        ReleaseFileBunker_B = core.DamageSkill("릴리즈 파일 벙커(B)", 0, 230, 6, modifier = core.CharacterModifier(pdamage = 15, armor_ignore = 80)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        ReleaseFileBunker_C = core.DamageSkill("릴리즈 파일 벙커(C)", 0, 270, 6, modifier = core.CharacterModifier(pdamage = 15, armor_ignore = 80)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        ReleaseFileBunker_D = core.DamageSkill("릴리즈 파일 벙커(D)", 0, 320, 6, modifier = core.CharacterModifier(pdamage = 15, armor_ignore = 80)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        DoublePang = core.DamageSkill("더블 팡", 0, 360, 4, modifier = core.CharacterModifier(pdamage = 10, armor_ignore = 20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        DoublePang_Revolve = core.DamageSkill("더블 팡(리볼빙 캐논)", 0, 180, 3).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        DoublePang_Revolve_Maximize = core.DamageSkill("더블 팡(리볼빙 캐논,맥시마이즈)", 0, 180*1.5, 3).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        
        HammerSmash = core.DamageSkill("해머 스매시", 0, 200+195, 6, modifier = core.CharacterModifier(pdamage = 10, armor_ignore = 20)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        HammerSmashWave = core.SummonSkill("해머 스매시(충격파)", 0, 1500, 150, 2+2, 5000, cooltime = -1, modifier = core.CharacterModifier(pdamage = 10, armor_ignore = 20)).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)
        HammerSmashDebuff = core.BuffSkill("해머 스매시(디버프)", 0, 10*1000, pdamage_indep = 10, rem = False, cooltime = -1).wrap(core.BuffSkillWrapper)
        
        RevolvingCannonMastery = core.DamageSkill("리볼빙 캐논 마스터리", 0, 215 * 1.1*1.1*1.1*1.1*1.1*1.1, 1).wrap(core.DamageSkillWrapper)
        
        #하이퍼
        MaximizeCannon = core.BuffSkill("맥시마이즈 캐논", 720, 30*1000, cooltime = 210 * 1000).wrap(core.BuffSkillWrapper)   #임의딜레이 720
        # 불릿을 사용하는 스킬 데미지 50% 증가, 불릿자동리로드 70$%감소, 릴파벙이후 과열시간 1초로 감소
        WillOfLiberty = core.BuffSkill("윌 오브 리버티", 0, 60*1000, cooltime = 120*1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        RegistanceLineInfantry = core.SummonSkill("레지스탕스 라인 인팬트리", 360, 1000, 215+8*vEhc.getV(3,3), 9, 10*1000, cooltime = 25000).isV(vEhc,3,3).wrap(core.SummonSkillWrapper)
        
        BunkerBuster = core.BuffSkill("벙커 버스터", 720, 45000, cooltime = 120000, rem = False).wrap(core.BuffSkillWrapper)    #임의딜레이 720
        BunkerBusterAttack = core.DamageSkill("벙커 버스터(공격)", 0, 120 + 9* vEhc.getV(0,0), 8, modifier = core.CharacterModifier(armor_ignore = 100)).wrap(core.DamageSkillWrapper)
        BunkerBusterAttack_Maximize = core.DamageSkill("벙커 버스터(맥시마이즈)", 0, (120 + 9* vEhc.getV(0,0))*1.5, 8, modifier = core.CharacterModifier(armor_ignore = 100)).wrap(core.DamageSkillWrapper)
        
        #발칸 펀치는 최대딜사이클에서는 사용하지 않음.
        BalkanPunch = core.DamageSkill("발칸 펀치", 720, 1000 + 40* vEhc.getV(4,4), 6, cooltime = 60 * 1000).wrap(core.DamageSkillWrapper) #임의 딜레이 720
        BalkanPunchTick = core.DamageSkill("발칸 펀치(틱)", 180, 450 + 8*vEhc.getV(4,4), 5).wrap(core.DamageSkillWrapper)	#8초간 43번
        
        
        BurningBreaker = core.DamageSkill("버닝 브레이커", 5000, 1500 + 60*vEhc.getV(1,1), 15, cooltime = 100*1000, modifier = core.CharacterModifier(armor_ignore = 100, crit = 100)).wrap(core.DamageSkillWrapper)
        BurningBreakerSplash = core.DamageSkill("버닝 브레이커(스플래시)", 0, 1200+48*vEhc.getV(1,1), 15 * 6, modifier = core.CharacterModifier(armor_ignore = 100, crit = 100)).wrap(core.DamageSkillWrapper)
        BurningBreakerSplash_Maximize = core.DamageSkill("버닝 브레이커(스플래시,맥시마이즈)", 0, (1200+48*vEhc.getV(1,1))*1.5, 15 * 6, modifier = core.CharacterModifier(armor_ignore = 100, crit = 100)).wrap(core.DamageSkillWrapper)
        
        #스킬 기본 연계 연결
        ReleaseFileBunker.onAfters([ReleaseFileBunker_A, ReleaseFileBunker_B, ReleaseFileBunker_C, ReleaseFileBunker_D])
        HammerSmash.onAfters([HammerSmashWave, HammerSmashDebuff])
        
        #맥시마이즈 캐논
        BurningBreakerSplash_WithMaximize = core.OptionalElement(MaximizeCannon.is_active, BurningBreakerSplash_Maximize, BurningBreakerSplash, name = "맥시마이즈 캐논 여부")
        
        BunkerBusterAttack_WithMaximize = core.OptionalElement(MaximizeCannon.is_active, BunkerBusterAttack_Maximize, BunkerBusterAttack, name = "맥시마이즈 캐논 여부")
        MagnumPunch_Revolve_WithMaximize = core.OptionalElement(MaximizeCannon.is_active, MagnumPunch_Revolve_Maximize, MagnumPunch_Revolve, name = "맥시마이즈 캐논 여부")
        DoublePang_Revolve_WithMaximize = core.OptionalElement(MaximizeCannon.is_active, DoublePang_Revolve_Maximize, DoublePang_Revolve, name = "맥시마이즈 캐논 여부")
        
        BurningBreaker.onAfter(BurningBreakerSplash_WithMaximize)
        
        
        # 리볼빙 캐논 발동
        
        MagnumPunch_Revolve_Final = core.OptionalElement(BunkerBuster.is_active, BunkerBusterAttack_WithMaximize, MagnumPunch_Revolve_WithMaximize)
        DoublePang_Revolve_Final = core.OptionalElement(BunkerBuster.is_active, BunkerBusterAttack_WithMaximize, DoublePang_Revolve_WithMaximize)
        MagnumPunch.onAfter(MagnumPunch_Revolve_Final)
        DoublePang.onAfter(DoublePang_Revolve_Final)
        
        # 기본 콤보
        Mag_Pang = core.DamageSkill("매그-팡", MAGPANGDELAY, 0, 0).wrap(core.DamageSkillWrapper)
        Mag_Pang.onAfter(MagnumPunch)
        Mag_Pang.onAfter(DoublePang)
        
        ReleaseHammer = core.DamageSkill("릴파벙", 0, 0, 0, cooltime = RELFILEBUNKCOOLTIME).wrap(core.DamageSkillWrapper)
        ReleaseHammer.onAfter(ReleaseFileBunker)
        ReleaseHammer.onAfter(HammerSmash)
        
        for wrp in [MagnumPunch, DoublePang, HammerSmash]:
            wrp.onAfter(RevolvingCannonMastery)

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 2)
        # 리스트 내용 검증 필요
        for sk in [ReleaseHammer, BurningBreaker, HammerSmashWave, Mag_Pang]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeaponCooltimeDummy = auraweapon_builder.get_buff()

        
        return(Mag_Pang,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    Booster, MaximizeCannon, WillOfLiberty, AuraWeaponBuff, BunkerBuster,
                    globalSkill.soul_contract()] +\
                [ReleaseHammer, BurningBreaker] +\
                [RegistanceLineInfantry, HammerSmashWave] +\
                [AuraWeaponCooltimeDummy] +\
                [Mag_Pang])