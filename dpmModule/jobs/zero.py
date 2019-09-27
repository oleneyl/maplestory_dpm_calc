from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = True
        self.vSkillNum = 5
        self.vEnhanceNum = 13
        self.jobtype = "str"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2

    def get_passive_skill_list(self):
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)

        ResolutionTime = core.InformedCharacterModifier("레졸루션 타임",pdamage_indep = 25, stat_main = 50)
        
        AlphaState = core.InformedCharacterModifier("상태-알파", pdamage_indep = 34, crit = 40, att = 40, armor_ignore = 30, crit_damage = 50)

        return [Mastery, ResolutionTime, AlphaState]

    def get_not_implied_skill_list(self):
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
        #### 알파 ####
        AlphaMastery = core.CharacterModifier(pdamage_indep = 34) + \
            core.CharacterModifier(att = 40, armor_ignore = 30) + \
            core.CharacterModifier(crit = 40) + \
            core.CharacterModifier(crit_damage = 50) + \
            core.CharacterModifier(crit_damage = 20*4/35)  #크리티컬 바인드
            
        AlphaState = core.BuffSkill("상태-알파", 0, 9999*10000, cooltime = -1, crit_damage = (20*4/35)).wrap(core.BuffSkillWrapper)
        BetaState = core.BuffSkill("상태-베타", 0, 9999*10000, cooltime = -1, pdamage_indep = 9.70, crit = 15-40, boss_pdamage = 30 + 30, att = 80-40, pdamage = 40, armor_ignore = -42.85, crit_damage = -50).wrap(core.BuffSkillWrapper)
            
        BetaMastery = core.CharacterModifier(pdamage_indep = 49) + \
                    core.CharacterModifier(crit = 15, boss_pdamage = 30 + 30, att = 80, pdamage = 40) + \
                    core.CharacterModifier(armor_ignore = 50)
        
        MoonStrike = core.DamageSkill("문 스트라이크", 390, 180, 4).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        MoonStrikeTAG = core.DamageSkill("문 스트라이크(태그)", 0, 180, 4).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        
        PierceStrike = core.DamageSkill("피어스 쓰러스트", 510, 250, 4 ).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        PierceStrikeTAG = core.DamageSkill("피어스 쓰러스트(태그)", 0, 250, 4 ).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        
        '''
        ShadowStrike = core.DamageSkill("쉐도우 스트라이크", ?, 310, 5)
        ShadowStrikeAura = core.DamageSkill("쉐도우 스트라이크", 0, 310, 1)
        '''
        FlashAssault = core.DamageSkill("플래시 어썰터", 480, 330, 4 ).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        FlashAssaultTAG = core.DamageSkill("플래시 어썰터(태그)", 0, 330, 4 ).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        
        AdvancedSpinCutter = core.DamageSkill("어드밴스드 스핀 커터", 630, 520, 5 ).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedSpinCutterTAG = core.DamageSkill("어드밴스드 스핀 커터(태그)", 0, 520, 5 ).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedSpinCutterAura = core.DamageSkill("어드밴스드 스핀 커터(오라)", 0, 475, 1 ).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        AdvancedRollingCurve = core.DamageSkill("어드밴스드 롤링 커브", 960, 530, 8 ).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingCurveTAG = core.DamageSkill("어드밴스드 롤링 커브(태그)", 0, 530, 8 ).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingCurveAura = core.DamageSkill("어드밴스드 롤링 커브(오라)", 0, 700, 1 ).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        
        AdvancedRollingAssulter = core.DamageSkill("어드밴스드 롤링 어썰터", 960, 745, 6 ).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingAssulterTAG = core.DamageSkill("어드밴스드 롤링 어썰터(태그)", 0, 745, 6 ).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedRollingAssulterAura = core.DamageSkill("어드밴스드 롤링 어썰터(오라)", 0, 745, 1 ).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        
        WindCutter = core.DamageSkill("윈드 커터", 540, 325, 4 ).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        WindCutterSummon = core.DamageSkill("윈드 커터(소환)", 0, 325, 3 ).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper) #3타 타격
        WindStrike = core.DamageSkill("윈드 스트라이크",600, 500, 4 ).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)
        StormBreak = core.DamageSkill("어드밴스드 스톰 브레이크", 690, 670, 5 ).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        StormBreakSummon = core.DamageSkill("어드밴스드 스톰 브레이크(소환)", 0, 670, 2).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper) #2타 타격
        StormBreakElectric = core.DamageSkill("어드밴스드 스톰 브레이크(전기)", 0, 230, 3 ).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)

        
        CriticalBind = core.BuffSkill("크리티컬 바인드", 0, 4000, crit = 30, crit_damage = 20, cooltime = 35 * 1000).wrap(core.BuffSkillWrapper) #알파만 적용됨.

        #### 베타 ####
        

        UpperStrike = core.DamageSkill("어퍼 슬래시", 690, 630, 2).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        UpperStrikeTAG = core.DamageSkill("어퍼 슬래시(태그)", 0, 630, 2).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        
        AirRiot = core.DamageSkill("어드밴스드 파워 스텀프", 570, 980, 3).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        AirRiotTAG = core.DamageSkill("어드밴스드 파워 스텀프(태그)", 0, 980, 3).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        AirRiotWave = core.DamageSkill("어드밴스드 파워 스텀프(파동)", 0, 980, 3).setV(vEhc, 0, 3, False).wrap(core.DamageSkillWrapper)
        
        FlashCut = core.DamageSkill("프론트 슬래시", 630, 610, 2).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        ThrowingWeapon = core.DamageSkill("어드밴스드 스로잉 웨폰", 360, 550, 2 * 5).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)    #5타 = 1.5s
        
        SpinDriver = core.DamageSkill("터닝 드라이브", 540, 780, 2).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedWheelWind = core.DamageSkill("어드밴스드 휠 윈드", 540, 400, 7).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)     #   0.1초당 1타, 최대 7초, 7타로 적용
        
        GigaCrash = core.DamageSkill("기가 크래시", 630, 750, 2).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        GigaCrashTAG = core.DamageSkill("기가 크래시(태그)", 0, 750, 2).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        
        FallingStar = core.DamageSkill("점핑 크래시", 660, 670, 3).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)
        FallingStarTAG = core.DamageSkill("점핑 크래시(태그)", 0, 670, 3).setV(vEhc, 8, 2, False).wrap(core.DamageSkillWrapper)
        
        AdvancedEarthBreak = core.DamageSkill("어드밴스드 어스 브레이크", 1170, 760, 5).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedEarthBreakTAG = core.DamageSkill("어드밴스드 어스 브레이크(태그)", 0, 760, 5).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper) 
        
        AdvancedEarthBreakWave = core.DamageSkill("어드밴스드 어스 브레이크(전기)(파동)", 0, 570, 5).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedEarthBreakElectric = core.DamageSkill("어드밴스드 어스 브레이크(전기)", 0, 340, 5).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)

        DoubleTime = core.BuffSkill("래피드 타임", 0, 9999*10000, crit = 20, pdamage = 10).wrap(core.BuffSkillWrapper)
        TimeDistortion = core.BuffSkill("타임 디스토션", 540, 30000, cooltime = 240 * 1000, pdamage = 25).wrap(core.BuffSkillWrapper)
        TimeHolding = core.BuffSkill("타임 홀딩", 1080, 90000, 180*1000, pdamage = 10).wrap(core.BuffSkillWrapper) #  쿨타임 초기화.(타임 리와 / 리미트 브레이크 제외)
        IntensiveTime = core.BuffSkill("인탠시브 타임", 0, 40*60*1000, patt = 4).wrap(core.BuffSkillWrapper)
        
        ShadowRain = core.DamageSkill("쉐도우 레인", 0, 1400, 14, cooltime = 300*1000).wrap(core.DamageSkillWrapper)
        
        #### 5차 스킬 ####
        #5차스킬들 마스터리 알파/베타 구분해서 적용할것.
        
        LimitBreakAttack = core.DamageSkill("리미트 브레이크", 0, 400+15*vEhc.getV(0,0), 5).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        LimitBreak = core.BuffSkill("리미트 브레이크(버프)", 450, (30+vEhc.getV(0,0)//2)*1000, pdamage_indep = (30+vEhc.getV(0,0)//5) *1.2 + 20, cooltime = 240*1000).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        
        # 베타로 사용함.
        TwinBladeOfTime = core.DamageSkill("조인트 어택", 0, 0, 0, cooltime = 120*1000, red = True).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_1 = core.DamageSkill("조인트 어택(1)", 3480, 875+35*vEhc.getV(1,1), 8).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_2 = core.DamageSkill("조인트 어택(2)", 0, 835+33*vEhc.getV(1,1), 8).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_3 = core.DamageSkill("조인트 어택(3)", 0, 1000+40*vEhc.getV(1,1), 13).wrap(core.DamageSkillWrapper)
        TwinBladeOfTime_end = core.DamageSkill("조인트 어택(4)", 0, 900+36*vEhc.getV(1,1), 15*3, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        
        #알파
        ShadowFlashAlpha = core.DamageSkill("쉐도우 플래시(알파)", 670, 500+20*vEhc.getV(2,2), 6, cooltime = 40*1000, red=True).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        ShadowFlashAlphaEnd = core.DamageSkill("쉐도우 플래시(알파)(종료)", 0, 400+16*vEhc.getV(2,2), 15*3).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        
        #베타
        ShadowFlashBeta = core.DamageSkill("쉐도우 플래시(베타)", 670, 600+24*vEhc.getV(2,2), 5, cooltime = 40*1000, red=True).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        ShadowFlashBetaEnd = core.DamageSkill("쉐도우 플래시(베타)(종료)", 0, 750+30*vEhc.getV(2,2), 12 * 2).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        
        ComboHolder = core.DamageSkill("어파스", 0,0,0).wrap(core.DamageSkillWrapper)
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
        FallingStar.onAfter(AdvancedEarthBreak)
        AdvancedEarthBreak.onAfter(AdvancedEarthBreakWave)
        AdvancedEarthBreak.onAfter(AdvancedEarthBreakElectric)
        
        GigaCrashTAG.onAfter(FallingStarTAG)
        FallingStarTAG.onAfter(AdvancedEarthBreakTAG)
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
        
        StateTAG = core.OptionalElement(AlphaState.is_active, SetBeta, SetAlpha)
        
        ### 국콤 생성
        li = [SetAlpha, WindCutter, MoonStrike, MoonStrike, SetBeta, SpinDriver, FlashCut, UpperStrike]
        li.reverse()
        ComboHolder.onAfters(li)

        TimeHolding.onAfters([TimeDistortion.controller(1), ShadowRain.controller(1)])
        TimeHolding.onConstraint(core.ConstraintElement("쉐레사용 이후사용", ShadowRain, ShadowRain.is_not_usable))

        # 오라 웨폰
        auraweapon_builder = globalSkill.AuraWeaponBuilder(vEhc, 2, 2)
        for sk in [MoonStrike, PierceStrike, FlashAssault, AdvancedSpinCutter,
                    AdvancedRollingCurve, AdvancedRollingAssulter, StormBreak, UpperStrike, AirRiot, GigaCrash,
                    FallingStar, AdvancedEarthBreak, TwinBladeOfTime_end]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeaponCooltimeDummy = auraweapon_builder.get_buff()


        return(ComboHolder,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster(),
                    AlphaState, BetaState, AuraWeaponBuff, DoubleTime, TimeDistortion, TimeHolding, IntensiveTime, LimitBreak,
                    globalSkill.soul_contract()]+\
                [ShadowRain, TwinBladeOfTime, ShadowFlashAlpha, ShadowFlashBeta]+\
                []+\
                [AuraWeaponCooltimeDummy]+\
                [ComboHolder])