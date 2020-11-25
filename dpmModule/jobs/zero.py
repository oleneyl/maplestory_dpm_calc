from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, MutualRule
from . import globalSkill
from .jobbranch import warriors
from math import ceil

# TODO: 4카 5앱 적용
# 제로는 패시브 레벨 +1 어빌 미적용
'''
어시스트 매커니즘 정리

항상 알파 스탯 적용: 스핀 커터 오라, 롤링 커브 오라, 롤링 어썰터 오라
항상 베타 스탯 적용: 파워 스텀프 충격파

https://github.com/Monolith11/memo/wiki/Zero-Skill-Mechanics
'''

class CriticalBindWrapper(core.BuffSkillWrapper):
    def __init__(self, alphaState: core.BuffSkillWrapper, betaState: core.BuffSkillWrapper):
        skill = core.BuffSkill("크리티컬 바인드", 0, 4000, cooltime=35000, crit=30, crit_damage=20)
        super(CriticalBindWrapper, self).__init__(skill)
        self.alphaState = alphaState
        self.betaState = betaState

    def get_modifier(self):
        if self.alphaState.is_not_active():
            return self.disabledModifier
        return super(CriticalBindWrapper, self).get_modifier()

    def is_usable(self):
        if self.betaState.is_not_active():
            return False
        return super(CriticalBindWrapper, self).is_usable()

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vSkillNum = 5
        self.vEnhanceNum = 13
        self.jobtype = "str"
        self.jobname = "제로"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2
        self.combat = 0

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(MutualRule('타임 홀딩', '소울 컨트랙트'), RuleSet.BASE)
        ruleset.add_rule(MutualRule('타임 홀딩', '타임 디스토션'), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)
        ResolutionTime = core.InformedCharacterModifier("리졸브 타임",pdamage_indep = 25, stat_main = 50)
        # 유니온 6000 기준
        # 4카5앱 임시 구현 (보공 +30%, 방무 -10%)
        LuckyHat_Temp = core.InformedCharacterModifier("카오스 벨룸의 헬름 (임시)", boss_pdamage = 30) - core.ExtendedCharacterModifier(armor_ignore = 10, stat_main = 21, stat_sub = 21, pstat_main = 5, pstat_sub = 5, att = 3)
        LuckyHat_Temp = core.InformedCharacterModifier.from_extended_modifier("카오스 벨룸의 헬름 (임시)", LuckyHat_Temp)

        return [Mastery, ResolutionTime, LuckyHat_Temp]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        ArmorSplit = core.InformedCharacterModifier("아머 스플릿", armor_ignore = 50)
        return [ArmorSplit]

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(crit = 15, pdamage = 80, armor_ignore = 20, crit_damage = 25)
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter):
        '''
        마스터리 별개로 적용 : 알파 : 1.34, 베타 : 1.49
        
        디바인 스위프트 사용
        리미트 브레이크 도중에만 디바인 포스 사용

        코강 순서
        
        피어스 쓰러스트 (+ 파워 스텀프)
        스핀커터 + 스로잉웨폰
        롤커 + 터닝 드라이브
        롤링 어썰터 + 휠윈드
        스톰브레이크 + 어스브레이크
        
        문스 + 어퍼슬래시
        플래시어썰터 + 프론트 슬래시
        윈드커터 + 기가크래시
        윈드슬래시 + 점핑크래시
        
        어파스 기준
        '''
        #### 마스터리 ####
        AlphaMDF = core.CharacterModifier(pdamage_indep = 34, crit = 40, att = 40, armor_ignore = 30, crit_damage = 50)
        BetaMDF = core.CharacterModifier(pdamage_indep = 49, crit = 15, boss_pdamage = 30, att = 80 + 4)
        
        AlphaState = core.BuffSkill("상태-알파", 0, 9999*10000, cooltime = -1,
            pdamage_indep = AlphaMDF.pdamage_indep,
            crit = AlphaMDF.crit,
            boss_pdamage = AlphaMDF.boss_pdamage,
            att = AlphaMDF.att,
            armor_ignore = AlphaMDF.armor_ignore,
            crit_damage = AlphaMDF.crit_damage).wrap(core.BuffSkillWrapper)
        BetaState = core.BuffSkill("상태-베타", 0, 9999*10000, cooltime = -1,
            pdamage_indep = BetaMDF.pdamage_indep,
            crit = BetaMDF.crit,
            boss_pdamage = BetaMDF.boss_pdamage,
            att = BetaMDF.att,
            armor_ignore = BetaMDF.armor_ignore,
            crit_damage = BetaMDF.crit_damage
        ).wrap(core.BuffSkillWrapper)

        # extra_dmg(x, y): x = 타겟 수, y = 코강으로 인한 타겟수 증가여부
        extra_dmg = lambda x, y : (core.CharacterModifier(pdamage = (x - 1 + int(y))*8))

        #### 알파 ####
        MoonStrike = core.DamageSkill("문 스트라이크", 330, 120, 6).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        MoonStrikeTAG = core.DamageSkill("문 스트라이크(태그)", 0, 120, 6).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        
        PierceStrike = core.DamageSkill("피어스 쓰러스트", 360, 170, 6).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        PierceStrikeTAG = core.DamageSkill("피어스 쓰러스트(태그)", 0, 170, 6).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        
        '''
        미사용 스킬

        TODO: 쉐스 검기 항상 알파스펙인지 확인할 것
        ShadowStrike = core.DamageSkill("쉐도우 스트라이크", 510, 195, 8).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        ShadowStrikeAura = core.DamageSkill("쉐도우 스트라이크(오라)", 0, 310, 1).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        '''
        FlashAssault = core.DamageSkill("플래시 어썰터", 270, 165, 8).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        FlashAssaultTAG = core.DamageSkill("플래시 어썰터(태그)", 0, 165, 8).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)

        AdvancedSpinCutter = core.DamageSkill("어드밴스드 스핀 커터", 270, 260+3*self.combat, 10).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedSpinCutterTAG = core.DamageSkill("어드밴스드 스핀 커터(태그)", 0, 260+3*self.combat, 10).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedSpinCutterAura = core.DamageSkill("어드밴스드 스핀 커터(오라)", 0, 130+3*self.combat, 4).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedSpinCutterAuraTAG = core.DamageSkill("어드밴스드 스핀 커터(오라)(태그)", 0, 130+3*self.combat, 4, modifier=AlphaMDF-BetaMDF).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper) # 항상 알파 스탯이 적용됨
        
        AdvancedRollingCurve = core.DamageSkill("어드밴스드 롤링 커브", 960, 365+3*self.combat, 12).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingCurveTAG = core.DamageSkill("어드밴스드 롤링 커브(태그)", 0, 365+3*self.combat, 12).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingCurveAura = core.DamageSkill("어드밴스드 롤링 커브(오라)", 0, 350+self.combat, 2).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingCurveAuraTAG = core.DamageSkill("어드밴스드 롤링 커브(오라)(태그)", 0, 350+self.combat, 2*2, modifier=AlphaMDF-BetaMDF).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper) # 항상 알파 스탯이 적용됨, 각 투사체가 2회 타격함
        
        AdvancedRollingAssulter = core.DamageSkill("어드밴스드 롤링 어썰터", 960, 375+2*self.combat, 12).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingAssulterTAG = core.DamageSkill("어드밴스드 롤링 어썰터(태그)", 0, 375+2*self.combat, 12).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingAssulterAura = core.DamageSkill("어드밴스드 롤링 어썰터(오라)", 0, 250+self.combat, 3).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingAssulterAuraTAG = core.DamageSkill("어드밴스드 롤링 어썰터(오라)(태그)", 0, 250+self.combat, 3*2*2, modifier=AlphaMDF-BetaMDF).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper) # 항상 알파 스탯이 적용됨, 2회 사출, 각 투사체가 2회 타격함
        
        WindCutter = core.DamageSkill("윈드 커터", 420, 165, 8).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        WindCutterSummon = core.DamageSkill("윈드 커터(소용돌이)", 0, 110, 3*2, cooltime=-1).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper) # 최대 3초지속, 2회 타격

        WindStrike = core.DamageSkill("윈드 스트라이크", 480, 250, 8).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)

        AdvancedStormBreak = core.DamageSkill("어드밴스드 스톰 브레이크", 690, 335+2*self.combat, 10).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedStormBreakSummon = core.DamageSkill("어드밴스드 스톰 브레이크(소용돌이)", 0, 335+2*self.combat, 4, cooltime=-1).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper) # 최대 3초지속, 1회 타격
        AdvancedStormBreakElectric = core.SummonSkill("어드밴스드 스톰 브레이크(전기)", 0, 1000, 230+2*self.combat, 1, (3+ ceil(self.combat /10))*1000, cooltime = -1).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)

        # 도트스킬은 크뎀 미적용이므로 AlphaSkill 추가할 필요없음.
        DivineLeer = core.DotSkill("디바인 리어", 0, 1000, 200, 1, 99999999).wrap(core.SummonSkillWrapper)

        #### 베타 ####

        UpperSlash = core.DamageSkill("어퍼 슬래시", 390, 210, 6, modifier = extra_dmg(6, True)).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        UpperSlashTAG = core.DamageSkill("어퍼 슬래시(태그)", 0, 210, 6, modifier = extra_dmg(6, True)).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        
        AdvancedPowerStomp = core.DamageSkill("어드밴스드 파워 스텀프", 570, 330 + 5*self.combat, 9, modifier = extra_dmg(6, True)).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        AdvancedPowerStompTAG = core.DamageSkill("어드밴스드 파워 스텀프(태그)", 0, 330 + 5*self.combat, 9, modifier = extra_dmg(6, True)).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        AdvancedPowerStompWave = core.DamageSkill("어드밴스드 파워 스텀프(파동)", 0, 330 + 5*self.combat, 9, modifier = extra_dmg(6, True)).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        AdvancedPowerStompWaveTAG = core.DamageSkill("어드밴스드 파워 스텀프(파동)(태그)", 0, 330 + 5*self.combat, 9, modifier = extra_dmg(6, True) + BetaMDF-AlphaMDF).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper) # 항상 베타 스탯이 적용됨
        
        THROWINGHIT = 5
        FrontSlash = core.DamageSkill("프론트 슬래시", 450, 205, 6, modifier = extra_dmg(6, True)).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        ThrowingWeapon = core.SummonSkill("어드밴스드 스로잉 웨폰", 360, 300, 550 + 5*self.combat, 2, THROWINGHIT*300, cooltime=-1, modifier = extra_dmg(6, True)).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)
        
        TurningDrive = core.DamageSkill("터닝 드라이브", 360, 260, 6, modifier = extra_dmg(6, True)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedWheelWind = core.DamageSkill("어드밴스드 휠 윈드", 900, 200+2*self.combat, 2*7, modifier = extra_dmg(6, True)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)     #   0.1초당 1타, 최대 7초, 7타로 적용
        
        GigaCrash = core.DamageSkill("기가 크래시", 540, 250, 6, modifier = extra_dmg(6, True)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        GigaCrashTAG = core.DamageSkill("기가 크래시(태그)", 0, 250, 6, modifier = extra_dmg(6, True)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        
        JumpingCrash = core.DamageSkill("점핑 크래시", 300, 225, 6, modifier = extra_dmg(6, True)).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)
        JumpingCrashTAG = core.DamageSkill("점핑 크래시(태그)", 0, 225, 6, modifier = extra_dmg(6, True)).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)
        JumpingCrashWave = core.DamageSkill("점핑 크래시(충격파)", 0, 225, 3, modifier = extra_dmg(6, True)).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)
        
        AdvancedEarthBreak = core.DamageSkill("어드밴스드 어스 브레이크", 630+390, 380+3*self.combat, 10, modifier = extra_dmg(6, True)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedEarthBreakTAG = core.DamageSkill("어드밴스드 어스 브레이크(태그)", 0, 380+3*self.combat, 10, modifier = extra_dmg(6, True)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper) 
        
        AdvancedEarthBreakWave = core.DamageSkill("어드밴스드 어스 브레이크(파동)", 0, 285+3*self.combat, 10, modifier = extra_dmg(6, True)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedEarthBreakElectric = core.SummonSkill("어드밴스드 어스 브레이크(전기)", 0, 1000, 340+3*self.combat, 1, 5000, cooltime = -1, modifier = extra_dmg(6, True)).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)

        CriticalBind = CriticalBindWrapper(AlphaState, BetaState)

        #### 초월자 스킬 ####

        DoubleTime = core.BuffSkill("래피드 타임", 0, 9999*10000, crit = 20, pdamage = 10).wrap(core.BuffSkillWrapper)
        TimeDistortion = core.BuffSkill("타임 디스토션", 540, 30000, cooltime = 240 * 1000, pdamage = 25).wrap(core.BuffSkillWrapper)
        TimeHolding = core.BuffSkill("타임 홀딩", 0, 90000, cooltime = 180*1000, pdamage = 10, red = False).wrap(core.BuffSkillWrapper) #  쿨타임 초기화.(타임 리와 / 리미트 브레이크 제외)
        # 인탠시브 타임 - 기본 도핑에 영메 포함되어 있음

        # 알파 4410ms 베타 4980ms
        #ShadowRain = core.DamageSkill("쉐도우 레인", 0, 1400, 14, cooltime = 300*1000).wrap(core.DamageSkillWrapper)
        
        SoulContract = globalSkill.soul_contract()

        #### 5차 스킬 ####
        # 5차스킬들 마스터리 알파/베타 구분해서 적용할것.
        # 리미트 브레이크, 조인트 어택은 베타 상태에서 사용
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0) # TODO: 베타 타겟당 데미지 증가 적용여부 확인할것
        
        LimitBreakAttack = core.DamageSkill("리미트 브레이크", 0, 400+15*vEhc.getV(0,0), 5, modifier = extra_dmg(15, False)).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        # 리미트 브레이크 중에는 디바인 포스 사용 (공격력 20 증가)
        LimitBreak = core.BuffSkill("리미트 브레이크(버프)", 450, (30+vEhc.getV(0,0)//2)*1000, pdamage_indep = 30+vEhc.getV(0,0)//5, att = 20, cooltime = 240*1000, red=True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        LimitBreakCDR = core.SummonSkill("리미트 브레이크(재사용 대기시간 감소)", 0, 1000, 0, 0, (30+vEhc.getV(0,0)//2)*1000, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        
        LimitBreakFinal = core.DamageSkill("리미트 브레이크 (막타)", 0, 650 + 26*vEhc.getV(0,0), 12*6, cooltime = -1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        # 베타로 사용함.
        TwinBladeOfTime = core.DamageSkill("조인트 어택", 0, 0, 0, cooltime = 120*1000, red=True).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_Alpha_1 = core.DamageSkill("조인트 어택(알파)(1)", 450, 875+35*vEhc.getV(1,1), 8).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_Alpha_2 = core.DamageSkill("조인트 어택(알파)(2)", 720, 835+33*vEhc.getV(1,1), 12).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_Alpha_3 = core.DamageSkill("조인트 어택(알파)(3)", 1020, 1000+40*vEhc.getV(1,1), 13).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_Beta_1 = core.DamageSkill("조인트 어택(베타)(1)", 540, 875+35*vEhc.getV(1,1), 8, modifier = extra_dmg(12, False)).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_Beta_2 = core.DamageSkill("조인트 어택(베타)(2)", 450, 835+33*vEhc.getV(1,1), 12, modifier = extra_dmg(12, False)).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_Beta_3 = core.DamageSkill("조인트 어택(베타)(3)", 360, 1000+40*vEhc.getV(1,1), 13, modifier = extra_dmg(12, False)).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_end = core.DamageSkill("조인트 어택(4)", 1050, 900+36*vEhc.getV(1,1), 15*3, modifier = (extra_dmg(12, False) + core.CharacterModifier(armor_ignore = 100))).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        
        #알파
        ShadowFlashAlpha = core.DamageSkill("쉐도우 플래시(알파)", 510, 500+20*vEhc.getV(2,2), 6, cooltime = 40*1000, red = True).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        ShadowFlashAlphaEnd = core.DamageSkill("쉐도우 플래시(알파)(종료)", 660, 400+16*vEhc.getV(2,2), 15*3).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        
        #베타
        ShadowFlashBeta = core.DamageSkill("쉐도우 플래시(베타)", 510, 600+24*vEhc.getV(2,2), 5, cooltime = 40*1000, modifier = extra_dmg(8, False), red = True).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        ShadowFlashBetaEnd = core.DamageSkill("쉐도우 플래시(베타)(종료)", 660, 750+30*vEhc.getV(2,2), 12 * 2, modifier = extra_dmg(15, False)).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        
        #초월자 륀느의 기원
        RhinneBless = core.BuffSkill("초월자 륀느의 기원", 480, (30+vEhc.getV(0,0)//2)*1000, cooltime = 240000, att = 10+3*vEhc.getV(0,0)).wrap(core.BuffSkillWrapper)
        RhinneBlessAttack_hit = core.DamageSkill("초월자 륀느의 기원 (타격)", 0, 125+5*vEhc.getV(0, 0), 5, cooltime = -1).wrap(core.DamageSkillWrapper)
        RhinneBlessAttack = core.OptionalElement(RhinneBless.is_active, RhinneBlessAttack_hit)

        #에고 웨폰
        EgoWeaponAlpha = core.DamageSkill("에고 웨폰(알파)", 0, 175+7*vEhc.getV(0,0), 6*9, cooltime=15000, red=True).wrap(core.DamageSkillWrapper)
        EgoWeaponBeta = core.DamageSkill("에고 웨폰(베타)", 0, 175+7*vEhc.getV(0,0), 9*2*3, cooltime=15000, red=True, modifier = extra_dmg(4, False)).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
        ### 스킬 연결 ###
        ### 알파 ###
        AdvancedSpinCutter.onAfter(AdvancedSpinCutterAura)
        AdvancedSpinCutterTAG.onAfter(AdvancedSpinCutterAuraTAG)
        
        AdvancedRollingCurve.onAfter(AdvancedRollingCurveAura)
        AdvancedRollingCurveTAG.onAfter(AdvancedRollingCurveAuraTAG)
        
        AdvancedRollingAssulter.onAfter(AdvancedRollingAssulterAura)
        AdvancedRollingAssulterTAG.onAfter(AdvancedRollingAssulterAuraTAG)
        
        WindCutter.onAfter(WindCutterSummon)
        AdvancedStormBreak.onAfter(AdvancedStormBreakElectric)
        AdvancedStormBreak.onAfter(AdvancedStormBreakSummon)
        
        ### 베타 ###
        AdvancedPowerStomp.onAfter(AdvancedPowerStompWave)
        AdvancedPowerStompTAG.onAfter(AdvancedPowerStompWaveTAG)
                
        JumpingCrash.onAfter(JumpingCrashWave)
        AdvancedEarthBreak.onAfter(AdvancedEarthBreakWave)
        AdvancedEarthBreak.onAfter(AdvancedEarthBreakElectric)
        
        JumpingCrashTAG.onAfter(JumpingCrashWave)
        AdvancedEarthBreakTAG.onAfter(AdvancedEarthBreakWave)
        AdvancedEarthBreakTAG.onAfter(AdvancedEarthBreakElectric)
        
        ### 상태 태그! ###
        SetAlpha = core.GraphElement("알파로 태그")
        SetAlpha.onAfter(AlphaState)
        SetAlpha.onAfter(BetaState.controller(-1))
        SetBeta = core.GraphElement("베타로 태그")
        SetBeta.onAfter(BetaState)
        SetBeta.onAfter(AlphaState.controller(-1))

        BetaState.controller(1) # 베타로 시작
        
        ### 어파스 생성
        # 윈커(0ms) - 윈스(420ms) - 스톰(900ms) - 문스(1590ms) - 피어싱(1920ms) - 문스(2280ms) - 피어싱(2610ms) - 2970ms -> 태그 쿨타임 대기 +130ms
        # 기가(0ms) -       점핑(630ms) -     어스(1290ms) -    어스 후딜 도중 문스 사용, 어퍼 씹힘 -   어파스(2850ms)
        TagCooltimeWait = core.DamageSkill("태그 쿨타임 대기(알파)", 130, 0, 0, cooltime=-1).wrap(core.DamageSkillWrapper)
        AlphaCombo = [SetAlpha, WindCutter, GigaCrashTAG, WindStrike, JumpingCrashTAG, AdvancedStormBreak, AdvancedEarthBreakTAG,
                        MoonStrike, PierceStrike, MoonStrike, PierceStrike, AdvancedPowerStompTAG, TagCooltimeWait]
        # 터닝(0ms) - 휠윈(360ms) - 프런트(1260ms) - 스로잉(1710ms) - 어퍼(2190ms) - 어파스(2580ms) - 3150ms -> 태그 쿨타임 대기 0ms
        # 롤커(0ms) -         롤어(960ms) -  플래시 씹힘 -    스핀(1920ms) -  문스 씹힘 -  피어싱(2640ms)
        BetaCombo = [SetBeta, TurningDrive, AdvancedRollingCurveTAG, AdvancedWheelWind, AdvancedRollingAssulterTAG,
                        FrontSlash, ThrowingWeapon, AdvancedSpinCutterTAG, UpperSlash, AdvancedPowerStomp, PierceStrikeTAG]
        ComboHolder = core.DamageSkill("어파스", 0,0,0).wrap(core.DamageSkillWrapper)
        for sk in AlphaCombo + BetaCombo:
            ComboHolder.onAfter(sk)

        ### 타임 홀딩 초기화 ###
        TimeHolding.onAfter(TimeDistortion.controller(1.0, "reduce_cooltime_p"))
        TimeHolding.onAfter(SoulContract.controller(1.0, "reduce_cooltime_p"))
        
        ### 5차 스킬들 ###
        TwinBladeOfTime.onBefore(SetBeta)
        for sk in [TwinBladeOfTime_Beta_1, TwinBladeOfTime_Alpha_1, TwinBladeOfTime_Beta_2, TwinBladeOfTime_Alpha_2,
                    TwinBladeOfTime_Beta_3, TwinBladeOfTime_Alpha_3, TwinBladeOfTime_end]:
            TwinBladeOfTime.onAfter(sk)
        ShadowFlashAlpha.onAfter(ShadowFlashAlphaEnd)
        ShadowFlashBeta.onAfter(ShadowFlashBetaEnd)
        LimitBreak.onBefore(SetBeta)
        LimitBreak.onAfter(LimitBreakAttack)
        LimitBreak.onAfter(LimitBreakCDR)
        # 버프 종료 직전에 캔슬 TODO: 리밋브 최종뎀 종료 전에 발동되는 것이 반드시 보장되어야 함 (콜백)
        LimitBreak.onAfter(LimitBreakFinal.controller((30+vEhc.getV(0,0)//2)*1000-1))
        LimitBreakFinal.add_runtime_modifier(BetaState, lambda beta: extra_dmg(15, False) if beta.is_active() else core.CharacterModifier())

        for sk in [TimeDistortion, SoulContract]:
            # 재사용 대기시간 초기화의 효과를 받지 않는 스킬을 제외한 스킬의 재사용 대기시간이 (기본 200%에 5레벨마다 10%씩) 더 빠르게 감소
            LimitBreakCDR.onTick(sk.controller(2000 + 20 * vEhc.getV(0, 0), 'reduce_cooltime'))
        
        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 3, 3)
        for sk in [MoonStrike, PierceStrike, FlashAssault, AdvancedSpinCutter,
                    AdvancedRollingCurve, AdvancedRollingAssulter, WindCutter, WindStrike, AdvancedStormBreak,
                    UpperSlash, AdvancedPowerStomp, FrontSlash, TurningDrive, AdvancedWheelWind, GigaCrash,
                    JumpingCrash, AdvancedEarthBreak, TwinBladeOfTime_Beta_1, TwinBladeOfTime_Alpha_1, 
                    TwinBladeOfTime_Beta_2, TwinBladeOfTime_Alpha_2, TwinBladeOfTime_Beta_3, TwinBladeOfTime_Alpha_3, TwinBladeOfTime_end]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()
        AuraWeapon.add_runtime_modifier(BetaState, lambda beta: extra_dmg(10, False) if beta.is_active() else core.CharacterModifier()) # 베타시 오라 웨폰에 대검 마스터리 적용

        
        # 초월자 륀느의 기원
        for sk in [MoonStrike, PierceStrike, FlashAssault, AdvancedSpinCutter,
                    AdvancedRollingCurve, AdvancedRollingAssulter, WindCutter, WindStrike, AdvancedStormBreak,
                    UpperSlash, AdvancedPowerStomp, FrontSlash, TurningDrive, AdvancedWheelWind, GigaCrash,
                    JumpingCrash, AdvancedEarthBreak]:
            sk.onAfter(RhinneBlessAttack)

        RhinneBless.onAfter(TimeDistortion.controller(1.0, 'reduce_cooltime_p'))
        RhinneBless.onAfter(SoulContract.controller(1.0, 'reduce_cooltime_p'))

        # 에고 웨폰
        UseEgoWeaponAlpha = core.OptionalElement(EgoWeaponAlpha.is_available, EgoWeaponAlpha)
        EgoWeaponAlpha.protect_from_running()
        for sk in [MoonStrike, PierceStrike, FlashAssault, AdvancedSpinCutter, AdvancedRollingCurve, AdvancedRollingAssulter,
            WindCutter, WindStrike, AdvancedStormBreak, ShadowFlashAlpha, ShadowFlashAlphaEnd]:
            sk.onAfter(UseEgoWeaponAlpha)
            
        UseEgoWeaponBeta = core.OptionalElement(EgoWeaponBeta.is_available, EgoWeaponBeta)
        EgoWeaponBeta.protect_from_running()
        for sk in [UpperSlash, AdvancedPowerStomp, FrontSlash, TurningDrive, AdvancedWheelWind, GigaCrash,
                    JumpingCrash, AdvancedEarthBreak, ShadowFlashBeta, ShadowFlashBetaEnd]:
            sk.onAfter(UseEgoWeaponBeta)
        
        return(ComboHolder,
                [globalSkill.maple_heros(chtr.level, name = "륀느의 가호", combat_level = 0), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster(),
                    AlphaState, BetaState, DivineLeer, AuraWeaponBuff, AuraWeapon, RhinneBless,
                    DoubleTime, TimeDistortion, TimeHolding, LimitBreak, LimitBreakCDR, LimitBreakFinal, CriticalBind,
                    SoulContract]+\
                [TwinBladeOfTime, ShadowFlashAlpha, ShadowFlashBeta, MirrorBreak, MirrorSpider]+\
                [AdvancedStormBreakSummon, AdvancedStormBreakElectric, AdvancedEarthBreakElectric, WindCutterSummon, ThrowingWeapon]+\
                [EgoWeaponAlpha, EgoWeaponBeta]+\
                [ComboHolder])