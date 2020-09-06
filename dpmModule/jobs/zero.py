from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import warriors
from math import ceil

# TODO: 4카 5앱 적용, 리미트 막타 추가
# 제로는 패시브 레벨 +1 어빌 미적용

# 현재로는 계산 알고리즘 작성 구문에서 연산과정에 접근을 할 수 없도록 캡슐화되어 있으므로 사용 불가능
'''
class LimitBreakNew():
    def __init__(self, enhancer, skill_importance, enhance_importance):
        self.damage_start = 0
        self.damage_end = 0
        self.analytics = core.Analytics()
        self.vLevel = enhancer.getV(skill_importance, enhance_importance)

        self.LimitBreakAttack = core.DamageSkill("리미트 브레이크", 0, 400+15*self.vLevel, 5).isV(enhancer, skill_importance, enhance_importance).wrap(core.DamageSkillWrapper)
        self.LimitBreak = core.BuffSkill("리미트 브레이크(버프)", 450, (30+self.vLevel//2)*1000, pdamage_indep = (30+self.vLevel//5) * 1.2 + 20, cooltime = 240*1000).isV(enhancer, skill_importance, enhance_importance).wrap(core.BuffSkillWrapper)
        self.LimitBreak.onAfter(self.LimitBreakAttack)
        
    def LimitBreakStart(self):
        self.damage_start = self.analytics.total_damage
        return LimitBreak

    def LimitBreakEnd(self):
        self.damage_end = self.analytics.total_damage - self.damage_start
        # 지속시간 동안 가한 데미지의 20% / 15
        # 퍼뎀이 아니라 고정값으로 뜨게 수정해야 함
        return core.DamageSkill("리미트 브레이크(막타)", 0, damage_end / 75, 15).wrap(core.DamageSkillWrapper)
    def get_buff(self):
        return self.LimitBreak

# LimitBreakSet = LimitBreakNew(vEhc, 0, 0)
# LimitBreak = LimitBreakSet.get_buff()
'''

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vSkillNum = 5
        self.vEnhanceNum = 13
        self.jobtype = "str"
        self.jobname = "제로"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2
        self._combat = 0

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)

        ResolutionTime = core.InformedCharacterModifier("리졸브 타임",pdamage_indep = 25, stat_main = 50)
        
        # 무기상수 1.34
        AlphaState = core.InformedCharacterModifier("상태-알파", pdamage_indep = 34, crit = 40, att = 40, armor_ignore = 30, crit_damage = 50)
        #4카5앱 옵션을 직접 작성할 경우를 가정하여...
        #VellumHelm = core.InformedCharacterModifier("카오스 벨룸의 헬름(4카 5앱)",boss_pdamage = 30, armor_ignore = -10)

        return [Mastery, ResolutionTime, AlphaState]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        ArmorSplit = core.InformedCharacterModifier("아머 스플릿", armor_ignore = 50)
        return [ArmorSplit]

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(crit = 15, pdamage = 30, armor_ignore = 20)
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        마스터리 별개로 적용 : 알파 : 1.34, 베타 : 1.49
        
        디바인 스위프트 사용

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
        AlphaMastery = core.CharacterModifier(pdamage_indep = 34) + \
            core.CharacterModifier(att = 40, armor_ignore = 30) + \
            core.CharacterModifier(crit = 40) + \
            core.CharacterModifier(crit_damage = 50)
        BetaMastery = core.CharacterModifier(pdamage_indep = 49) + \
                    core.CharacterModifier(crit = 15, boss_pdamage = 30, att = 80)

        AlphaBetaDiff = BetaMastery - AlphaMastery
        
        # 알파: 크리티컬 바인드 크뎀 평균값 적용
        AlphaState = core.BuffSkill("상태-알파", 0, 9999*10000, cooltime = -1, crit_damage = (20*4/35)).wrap(core.BuffSkillWrapper)
        BetaState = core.BuffSkill("상태-베타", 0, 9999*10000, cooltime = -1,
            pdamage_indep = AlphaBetaDiff.pdamage_indep,
            crit = AlphaBetaDiff.crit,
            boss_pdamage = AlphaBetaDiff.boss_pdamage,
            att = AlphaBetaDiff.att,
            armor_ignore = AlphaBetaDiff.armor_ignore,
            crit_damage = AlphaBetaDiff.crit_damage
        ).wrap(core.BuffSkillWrapper)

        #### 알파 ####
        MoonStrike = core.DamageSkill("문 스트라이크", 390, 120, 6).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        MoonStrikeTAG = core.DamageSkill("문 스트라이크(태그)", 0, 120, 6).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        
        PierceStrike = core.DamageSkill("피어스 쓰러스트", 510, 170, 6 ).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        PierceStrikeTAG = core.DamageSkill("피어스 쓰러스트(태그)", 0, 170, 6 ).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        
        '''
        미사용 스킬

        ShadowStrike = core.DamageSkill("쉐도우 스트라이크", ?, 195, 8)
        ShadowStrikeAura = core.DamageSkill("쉐도우 스트라이크", 0, 310, 1)
        '''
        FlashAssault = core.DamageSkill("플래시 어썰터", 480, 165, 8 ).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        FlashAssaultTAG = core.DamageSkill("플래시 어썰터(태그)", 0, 165, 8 ).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        
        ### Dummy Skills
        _SpinCutter = core.DamageSkill("스핀 커터", 630, 260, 10 ).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper) 
        _RollingCurve = core.DamageSkill("롤링 커브", 960, 365, 12 ).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        _RollingAssulter = core.DamageSkill("롤링 어썰터", 960, 375, 12 ).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        _StormBreak = core.DamageSkill("스톰 브레이크", 690, 335, 10 ).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        ### Dummy SKill End 

        AdvancedSpinCutter = core.DamageSkill("어드밴스드 스핀 커터", 630, 260+3*self._combat, 10 ).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedSpinCutterTAG = core.DamageSkill("어드밴스드 스핀 커터(태그)", 0, 260+3*self._combat, 10 ).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedSpinCutterAura = core.DamageSkill("어드밴스드 스핀 커터(오라)", 0, 130+3*self._combat, 4 ).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        AdvancedRollingCurve = core.DamageSkill("어드밴스드 롤링 커브", 960, 365+3*self._combat, 12 ).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingCurveTAG = core.DamageSkill("어드밴스드 롤링 커브(태그)", 0, 365+3*self._combat, 12 ).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingCurveAura = core.DamageSkill("어드밴스드 롤링 커브(오라)", 0, 350+self._combat, 2 ).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        
        AdvancedRollingAssulter = core.DamageSkill("어드밴스드 롤링 어썰터", 960, 375+2*self._combat, 12 ).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingAssulterTAG = core.DamageSkill("어드밴스드 롤링 어썰터(태그)", 0, 375+2*self._combat, 12 ).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingAssulterAura = core.DamageSkill("어드밴스드 롤링 어썰터(오라)", 0, 250+self._combat, 3 ).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        
        WindCutter = core.DamageSkill("윈드 커터", 540, 165, 8 ).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        WindCutterSummon = core.SummonSkill("윈드 커터(소환)", 0, 500, 110, 3, 3000, cooltime=-1).setV(vEhc, 7, 2, False).wrap(core.SummonSkillWrapper)
        #WindCutterSummon = core.DamageSkill("윈드 커터(소환)", 0, 110, 3*3 ).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper) #3타 타격

        WindStrike = core.DamageSkill("윈드 스트라이크",600, 250, 8).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)

        StormBreak = core.DamageSkill("어드밴스드 스톰 브레이크", 690, 335+2*self._combat, 10 ).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        StormBreakSummon = core.SummonSkill("어드밴스드 스톰 브레이크(소환)", 0, 500, 335+2*self._combat, 4, 3000, cooltime=-1).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)
        #StormBreakSummon = core.DamageSkill("어드밴스드 스톰 브레이크(소환)", 0, 335+2*self._combat, 4).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper) #2타 타격
        #StormBreakElectric = core.DotSkill("어드밴스드 스톰 브레이크(전기)", 230+2*self._combat, (3+ ceil(self._combat /10))*1000).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)
        StormBreakElectric = core.DamageSkill("어드밴스드 스톰 브레이크(전기)", 0, 230+2*self._combat, 3+ceil(self._combat /10)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)

        DivineLeer = core.DotSkill("디바인 리어", 0, 1000, 200, 1, 99999999).wrap(core.SummonSkillWrapper)

        #### 베타 ####

        #대검 마스터리: 스킬 사용 시 공격 받은 적이 스킬의 최대 공격 가능한 몬스터 수보다 적을 때 1명 당 8%의 데미지 증가
        #각각 베타 스킬에 꼭 적용해주세요. 툴팁에 나와있는 몬스터 수를 그대로 작성해주시면 됩니다.
        #일반 스킬은 True, 5차 스킬은 False
        beta_enrage = lambda x, y: core.CharacterModifier(pdamage = 8 * (x + int(y) - 1))

        UpperStrike = core.DamageSkill("어퍼 슬래시", 690, 210, 6, modifier = beta_enrage(6, True)).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        UpperStrikeTAG = core.DamageSkill("어퍼 슬래시(태그)", 0, 210, 6, modifier = beta_enrage(6, True)).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        
        AirRiot = core.DamageSkill("어드밴스드 파워 스텀프", 570, 330 + 5*self._combat, 9, modifier = beta_enrage(6, True)).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        AirRiotTAG = core.DamageSkill("어드밴스드 파워 스텀프(태그)", 0, 330 + 5*self._combat, 9, modifier = beta_enrage(6, True)).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        AirRiotWave = core.DamageSkill("어드밴스드 파워 스텀프(파동)", 0, 330 + 5*self._combat, 9, modifier = beta_enrage(6, True)).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        
        THROWINGHIT = 5
        FlashCut = core.DamageSkill("프론트 슬래시", 630, 205, 6, modifier = beta_enrage(6, True)).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        ThrowingWeapon = core.SummonSkill("어드밴스드 스로잉 웨폰", 360, 300, 550 + 5*self._combat, 2, THROWINGHIT*300, cooltime=-1, modifier = beta_enrage(6, True)).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)
        #ThrowingWeapon = core.DamageSkill("어드밴스드 스로잉 웨폰", 360, 550 + 5*self._combat, 2 * 5, modifier = beta_enrage(6, True)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)    #5타 = 1.5s
        
        SpinDriver = core.DamageSkill("터닝 드라이브", 540, 260, 6, modifier = beta_enrage(6, True)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedWheelWind = core.DamageSkill("어드밴스드 휠 윈드", 540, 200+2*self._combat, 2*7, modifier = beta_enrage(6, True)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)     #   0.1초당 1타, 최대 7초, 7타로 적용
        
        GigaCrash = core.DamageSkill("기가 크래시", 630, 250, 6, modifier = beta_enrage(6, True)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        GigaCrashTAG = core.DamageSkill("기가 크래시(태그)", 0, 250, 6, modifier = beta_enrage(6, True)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        
        FallingStar = core.DamageSkill("점핑 크래시", 660, 225, 6, modifier = beta_enrage(6, True)).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)
        # 충격파 값 포함
        FallingStarTAG = core.DamageSkill("점핑 크래시(태그)", 0, 225, 6, modifier = beta_enrage(6, True)).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)
        FallingStarWave = core.DamageSkill("점핑 크래시(충격파)", 0, 225, 3, modifier = beta_enrage(6, True)).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)
        
        AdvancedEarthBreak = core.DamageSkill("어드밴스드 어스 브레이크", 1170, 380+3*self._combat, 10, modifier = beta_enrage(6, True)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedEarthBreakTAG = core.DamageSkill("어드밴스드 어스 브레이크(태그)", 0, 380+3*self._combat, 10, modifier = beta_enrage(6, True)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper) 
        
        AdvancedEarthBreakWave = core.DamageSkill("어드밴스드 어스 브레이크(파동)", 0, 285+3*self._combat, 10, modifier = beta_enrage(6, True)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        
        #AdvancedEarthBreakElectric = core.DotSkill("어드밴스드 어스 브레이크(전기)", 340+3*self._combat, 5).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)
        AdvancedEarthBreakElectric = core.DamageSkill("어드밴스드 어스 브레이크(전기)", 0, 340+3*self._combat, 5, modifier = beta_enrage(6, True)).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)

        DoubleTime = core.BuffSkill("래피드 타임", 0, 9999*10000, crit = 20, pdamage = 10).wrap(core.BuffSkillWrapper)
        TimeDistortion = core.BuffSkill("타임 디스토션", 540, 30000, cooltime = 240 * 1000, pdamage = 25).wrap(core.BuffSkillWrapper)
        TimeHolding = core.BuffSkill("타임 홀딩", 1080, 90000, 180*1000, pdamage = 10).wrap(core.BuffSkillWrapper) #  쿨타임 초기화.(타임 리와 / 리미트 브레이크 제외)
        IntensiveTime = core.BuffSkill("인탠시브 타임", 0, 40*60*1000, patt = 4).wrap(core.BuffSkillWrapper)
        
        # 딜레이 확인필요, 딜사이클에 포함되는 스킬인지 확인필요
        ShadowRain = core.DamageSkill("쉐도우 레인", 0, 1400, 14, cooltime = 300*1000).wrap(core.DamageSkillWrapper)
        
        SoulContract = globalSkill.soul_contract()

        #### 5차 스킬 ####
        #5차스킬들 마스터리 알파/베타 구분해서 적용할것.
        
        LimitBreakAttack = core.DamageSkill("리미트 브레이크", 0, 400+15*vEhc.getV(0,0), 5, modifier = beta_enrage(15, False)).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        # 리미트 브레이크 중에는 디바인 포스 사용 (공격력 20 증가)
        LimitBreak = core.BuffSkill("리미트 브레이크(버프)", 450, (30+vEhc.getV(0,0)//2)*1000, pdamage_indep = (30+vEhc.getV(0,0)//5) *1.2 + 20, att = 20, cooltime = 240*1000).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        
        #LimitBreakFinal = core.DamageSkill("리미트 브레이크 (막타)", 0, '''지속시간 동안 가한 데미지의 20% / 15''', 15)
        # 베타로 사용함.
        TwinBladeOfTime = core.DamageSkill("조인트 어택", 0, 0, 0, cooltime = 120*1000, modifier = beta_enrage(12, False)).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_1 = core.DamageSkill("조인트 어택(1)", 3480, 875+35*vEhc.getV(1,1), 8, modifier = beta_enrage(12, False)).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_2 = core.DamageSkill("조인트 어택(2)", 0, 835+33*vEhc.getV(1,1), 8, modifier = beta_enrage(12, False)).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_3 = core.DamageSkill("조인트 어택(3)", 0, 1000+40*vEhc.getV(1,1), 13, modifier = beta_enrage(12, False)).wrap(core.DamageSkillWrapper)
        # 45타수가 시스템상으로 잘 반영되는지 확인필요.
        TwinBladeOfTime_end = core.DamageSkill("조인트 어택(4)", 0, 900+36*vEhc.getV(1,1), 45, modifier = (beta_enrage(12, False) + core.CharacterModifier(armor_ignore = 100))).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        
        #알파
        ShadowFlashAlpha = core.DamageSkill("쉐도우 플래시(알파)", 670, 500+20*vEhc.getV(2,2), 6, cooltime = 40*1000, red = True).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        ShadowFlashAlphaEnd = core.DamageSkill("쉐도우 플래시(알파)(종료)", 0, 400+16*vEhc.getV(2,2), 15*3).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        
        #베타
        ShadowFlashBeta = core.DamageSkill("쉐도우 플래시(베타)", 670, 600+24*vEhc.getV(2,2), 5, cooltime = 40*1000, modifier = beta_enrage(8, False), red = True).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        ShadowFlashBetaEnd = core.DamageSkill("쉐도우 플래시(베타)(종료)", 0, 750+30*vEhc.getV(2,2), 12 * 2, modifier = beta_enrage(8, False)).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        
        ComboHolder = core.DamageSkill("어파스", 0,0,0).wrap(core.DamageSkillWrapper)

        #초월자 륀느의 기원
        '''
        RhinneBless = core.BuffSkill("초월자 륀느의 기원", 630, 30+vEhc.getV(0, 0)//2, cooltime = 240000, att = 10+3*vEhc.getV(0, 0)).wrap(core.BuffSkillWrapper)
        RhinneBlessAttack_hit = core.DamageSkill("초월자 륀느의 기원 (타격)", 0, 125+5*vEhc.getV(0, 0), 5, cooltime = -1).wrap(core.DamageSkillWrapper)
        RhinneBlessAttack = core.OptionalElement(RhinneBless.is_active(), RhinneBlessAttack_hit)
        '''


        ######   Skill Wrapper   ######
        
        '''제로의 콤보 사용방식 정리!
        터닝드라이브-휠윈드 /  프론트슬래시-쓰로잉웨폰 / 어퍼슬래시-파워스텀프 / 
        롤커 - 어드밴스드롤어 / 플래시어썰터-스핀커터 / 문스트라이크 - 피어스쓰러스트
        
        윈드커터-윈드스트라이크-스톰브레이크 / 문스트라이크-피어스쓰러스트 / 문스트라이크-피어스 쓰러스트 /
        기가크래시-점핑크래시-어드어스브레이크 / 어퍼슬래시-파워스텀프 / 어퍼슬래시-파워스텀프/
        '''

        ### 스킬 연결 ###
        ### 알파 ###
        MoonStrike.onAfter(PierceStrike)
        MoonStrikeTAG.onAfter(PierceStrikeTAG)
        
        FlashAssault.onAfter(AdvancedSpinCutter)
        AdvancedSpinCutter.onAfter(AdvancedSpinCutterAura)
        
        FlashAssaultTAG.onAfter(AdvancedSpinCutterTAG)
        AdvancedSpinCutterTAG.onAfter(AdvancedSpinCutterAura)
        
        AdvancedRollingCurve.onAfter(AdvancedRollingCurveAura)
        AdvancedRollingCurveTAG.onAfter(AdvancedRollingCurveAura)
        
        AdvancedRollingCurve.onAfter(AdvancedRollingAssulter)
        AdvancedRollingCurveTAG.onAfter(AdvancedRollingAssulterTAG)
        
        AdvancedRollingAssulter.onAfter(AdvancedRollingAssulterAura)
        AdvancedRollingAssulterTAG.onAfter(AdvancedRollingAssulterAura)
        
        WindCutter.onAfter(WindCutterSummon)
        WindCutter.onAfter(WindStrike)
        WindStrike.onAfter(StormBreak)
        StormBreak.onAfters([StormBreakElectric, StormBreakSummon])
        
        ### 베타 ###
        UpperStrike.onAfter(AirRiot)
        UpperStrikeTAG.onAfter(AirRiotTAG)
        
        AirRiot.onAfter(AirRiotWave)
        AirRiotTAG.onAfter(AirRiotWave)
        
        FlashCut.onAfter(ThrowingWeapon)
        SpinDriver.onAfter(AdvancedWheelWind)
        
        GigaCrash.onAfter(FallingStar)
        FallingStar.onAfters([AdvancedEarthBreak, FallingStarWave])
        AdvancedEarthBreak.onAfter(AdvancedEarthBreakWave)
        AdvancedEarthBreak.onAfter(AdvancedEarthBreakElectric)
        
        GigaCrashTAG.onAfter(FallingStarTAG)
        FallingStarTAG.onAfters([AdvancedEarthBreakTAG, FallingStarWave])
        AdvancedEarthBreakTAG.onAfter(AdvancedEarthBreakWave)
        AdvancedEarthBreakTAG.onAfter(AdvancedEarthBreakElectric)
        
        ### 어시스트 연결 ###
        SpinDriver.onAfter(AdvancedRollingCurveTAG)
        FlashCut.onAfter(FlashAssaultTAG)
        UpperStrike.onAfter(MoonStrikeTAG)
        
        WindCutter.onAfter(GigaCrashTAG)
        MoonStrike.onAfter(UpperStrikeTAG)
        
        ### 상태 태그! ###
        SetAlpha = core.GraphElement("알파로 태그")
        SetAlpha.onAfter(AlphaState)
        SetAlpha.onAfter(BetaState.controller(-1))
        SetBeta = core.GraphElement("베타로 태그")
        SetBeta.onAfter(BetaState)
        SetBeta.onAfter(AlphaState.controller(-1))
        
        ### 5차 스킬들 ###
        TwinBladeOfTime.onAfters([TwinBladeOfTime_end, TwinBladeOfTime_3, TwinBladeOfTime_2, TwinBladeOfTime_1])
        ShadowFlashAlpha.onAfter(ShadowFlashAlphaEnd)
        ShadowFlashBeta.onAfter(ShadowFlashBetaEnd)
        LimitBreak.onAfter(LimitBreakAttack)

        LimitBreakCDR = core.BuffSkill("리미트 브레이크(재사용 대기시간 감소)", 0, 0, cooltime = -1).wrap(core.BuffSkillWrapper)
        LimitBreak.onAfter(LimitBreakCDR)
        for sk in [ShadowRain, TimeDistortion, SoulContract]:
            # 재사용 대기시간 초기화의 효과를 받지 않는 스킬을 제외한 스킬의 재사용 대기시간이 (기본 200%에 5레벨마다 10%씩) 더 빠르게 감소
            LimitBreakCDR.onAfter(sk.controller(2000 + 20 * vEhc.getV(0, 0), 'reduce_cooltime'))
        
        # 리미트 브레이크 지속시간동안 쿨감효과 반복
        LimitBreakCDR.onAfter(core.OptionalElement(LimitBreak.is_active, LimitBreakCDR.controller(1000)))

        StateTAG = core.OptionalElement(AlphaState.is_active, SetBeta, SetAlpha)
        
        ### 국콤 생성
        li = [SetAlpha, WindCutter, MoonStrike, MoonStrike, SetBeta, SpinDriver, FlashCut, UpperStrike]
        li.reverse()
        ComboHolder.onAfters(li)

        TimeHolding.onAfters([TimeDistortion.controller(1), ShadowRain.controller(1)])
        TimeHolding.onConstraint(core.ConstraintElement("쉐레사용 이후사용", ShadowRain, ShadowRain.is_not_usable))

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 3, 3)
        for sk in [MoonStrike, PierceStrike, FlashAssault, AdvancedSpinCutter,
                    AdvancedRollingCurve, AdvancedRollingAssulter, StormBreak, UpperStrike, AirRiot, GigaCrash,
                    FallingStar, AdvancedEarthBreak, TwinBladeOfTime_end]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        '''
        스킬 사용 후 초월자 륀느의 기원 발동
        for sk in [MoonStrike, PierceStrike, FlashAssault, AdvancedSpinCutter,
                    AdvancedRollingCurve, AdvancedRollingAssulter, StormBreak, UpperStrike, AirRiot, GigaCrash,
                    FallingStar, AdvancedEarthBreak]:
            sk.onAfter(RhinneBlessAttack)

        스킬 쿨타임 초기화
        RhinneBless.onAfters(TimeDistortion.controller(1, 'reduce_cooltime_p'), ShadowRain.controller(1, 'reduce_cooltime_p'), SoulContract.controller(1, 'reduce_cooltime_p'))
        '''

        return(ComboHolder,
                [globalSkill.maple_heros(chtr.level, name = "륀느의 가호", combat_level = 0), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster(),
                    AlphaState, BetaState, DivineLeer, AuraWeaponBuff, AuraWeapon, DoubleTime, TimeDistortion, TimeHolding, IntensiveTime, LimitBreak,
                    SoulContract]+\
                [ShadowRain, TwinBladeOfTime, ShadowFlashAlpha, ShadowFlashBeta]+\
                [StormBreakSummon, WindCutterSummon, ThrowingWeapon]+\
                []+\
                [ComboHolder])