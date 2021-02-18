from ..kernel import core
from ..character import characterKernel as ck
from functools import partial, reduce
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule
from . import globalSkill, jobutils
from .jobclass import resistance
from .jobbranch import bowmen
from math import ceil
from typing import Any, Dict

class JaguerStack(core.DamageSkillWrapper):
    def __init__(self, level, vEhc):
        self.debuffQueue = []  # (확률, 시간)
        self.currentTime = 0
        self.stack = 0
        self.DEBUF_PERSISTENCE_TIME = 15000  # 15000ms
        skill = core.DamageSkill("어나더 바이트", 0, 60 + level // 3, 0, cooltime=-1).setV(vEhc, 1, 2, False)
        super(JaguerStack, self).__init__(skill)

    def _add_debuff(self, value):
        self.debuffQueue = [(self.currentTime, value)] + self.debuffQueue
        return self._result_object_cache

    def add_debuff(self, value):
        return core.TaskHolder(core.Task(self, partial(self._add_debuff, value)), name = f"{value*100}%")

    def calculate_stack(self):
        """
        현재 시점부터 15초 이전까지의 재규어 공격이 전부 실패했을 확률을 바탕으로 스택 기댓값을 연산합니다.
        """
        fail_prob = reduce(lambda x, y: x * y, [max(1 - x[1], 0) for x in self.debuffQueue], 1)
        return 3 * (1 - fail_prob)

    def spend_time(self, time):
        self.currentTime += time
        # 8초 이상 지난 기록 제거
        self.debuffQueue = [x for x in self.debuffQueue if x[0] + self.DEBUF_PERSISTENCE_TIME > self.currentTime]
        self.stack = self.calculate_stack()
        super(JaguerStack, self).spend_time(time)
    
    def get_hit(self):
        return self.stack

class JaguarWrapper(core.SummonSkillWrapper):
    def __init__(self):
        skill = core.SummonSkill("재규어", 0, 0, 0, 0, 99999999)
        super(JaguarWrapper, self).__init__(skill)

    def _set_delay(self, value):
        self.tick = value
        return self._result_object_cache

    def set_delay(self, value):
        return core.TaskHolder(core.Task(self, partial(self._set_delay, value)), name = f"재규어 딜레이 {value}")

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 11
        self.jobtype = "DEX"
        self.jobname = "와일드헌터"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'reuse', 'crit')
        self.preEmptiveSkills = 0

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('소울 컨트랙트', '재규어 스톰'), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=45, crit_damage=17.3)
        
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        Jaguer = core.InformedCharacterModifier("재규어",crit=5, buff_rem=10)
        NaturesWrath = core.InformedCharacterModifier("네이처스 래쓰",crit=25)
        AutomaticShootingDevice = core.InformedCharacterModifier("오토매팅 슈팅 디바이스",att=20)
        CrossbowMastery = core.InformedCharacterModifier("크로스보우 마스터리",pdamage = 10)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        Flurry = core.InformedCharacterModifier("플러리", stat_main = 40)
        JaugerLink = core.InformedCharacterModifier("재규어 링크",crit = 18, crit_damage = 12, att = 10)
        CrossbowExpert = core.InformedCharacterModifier("크로스보우 엑스퍼트",att=30 + passive_level, crit_damage = 20 + passive_level//2)
        WildInstinct = core.InformedCharacterModifier("와일드 인스팅트",armor_ignore = 30 + 3*passive_level)
        ExtentMagazine = core.InformedCharacterModifier("익스텐드 매거진", pdamage_indep=20 + passive_level // 3, stat_main=60 + 2*passive_level, stat_sub=60 + 2*passive_level)
        AdvancedFinalAttackPassive = core.InformedCharacterModifier("어드밴스드 파이널 어택(패시브)", att = 20 + ceil(passive_level/2))
        JaugerStormPassive = core.InformedCharacterModifier("재규어 스톰(패시브)", att = 5+2*vEhc.getV(0,0))
    
        return [Jaguer, NaturesWrath, AutomaticShootingDevice,
                            CrossbowMastery, PhisicalTraining, Flurry, JaugerLink, CrossbowExpert, 
                            WildInstinct, ExtentMagazine, AdvancedFinalAttackPassive, JaugerStormPassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 35)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=85+ceil(passive_level/2))
        
        SummonJaguer = core.InformedCharacterModifier("서먼 재규어", crit_damage = 8)
        
        return [WeaponConstant, Mastery, SummonJaguer]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        재규어 스톰 3히트

        하이퍼:
        비스트 폼-리인포스
        서먼 재규어-리인포스, 쿨타임 리듀스
        와일드 발칸-리인포스, 보스 킬러

        소울 컨트랙트를 크리티컬 리인포스+재규어 스톰+와일드 발칸 Type X에 맞춰 사용
        
        코강 순서:
        발칸 - (서먼/어나더) - 파택 - 클로우컷 - 헌팅유닛- 램피지애즈원/플래시레인 - 소닉붐 - 재규어소울 - 크로스 로드 - 드릴 컨테이너
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        # Jaguar Skills
        JAGUAR_STORM_HIT = 3
        
        Jaguar = JaguarWrapper()
        Normal = core.DamageSkill("재규어 평타", 0, 140+chtr.level, 1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        ClawCut = core.DamageSkill("클로우 컷", 0, 200+chtr.level, 4, cooltime = 5000*0.8, red=True, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        Crossroad = core.DamageSkill("크로스 로드", 0, 225+chtr.level, 2, cooltime = 6000*0.8, red=True, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 8, 3, False).wrap(core.DamageSkillWrapper)
        SonicBoom = core.DamageSkill("소닉 붐", 0, 220+chtr.level, 6, cooltime = 6000*0.8, red=True, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        JaguarSoul = core.DamageSkill("재규어 소울", 0, 270+chtr.level, 12, cooltime = 210000, red=True, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        RampageAsOne = core.DamageSkill("램피지 애즈 원", 0, 500+1*chtr.level, 9, cooltime = 12000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
    
        Normal_JG = core.DamageSkill("재규어 평타(재규어 스톰)", 0, (140+chtr.level)*(62+vEhc.getV(0,0))*0.01, 1 * JAGUAR_STORM_HIT, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        ClawCut_JG = core.DamageSkill("클로우 컷(재규어 스톰)", 0, (200+chtr.level)*(62+vEhc.getV(0,0))*0.01, 4 * JAGUAR_STORM_HIT, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        Crossroad_JG = core.DamageSkill("크로스 로드(재규어 스톰)", 0, (225+chtr.level)*(62+vEhc.getV(0,0))*0.01, 2 * JAGUAR_STORM_HIT, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 8, 3, False).wrap(core.DamageSkillWrapper)
        SonicBoom_JG = core.DamageSkill("소닉 붐(재규어 스톰)", 0, (220+chtr.level)*(62+vEhc.getV(0,0))*0.01, 6 * JAGUAR_STORM_HIT, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        JaguarSoul_JG = core.DamageSkill("재규어 소울(재규어 스톰)", 0, (270+chtr.level)*(62+vEhc.getV(0,0))*0.01, 12 * JAGUAR_STORM_HIT, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        RampageAsOne_JG = core.DamageSkill("램피지 애즈 원(재규어 스톰)", 0, (500+1*chtr.level)*(62+vEhc.getV(0,0))*0.01, 9 * JAGUAR_STORM_HIT, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
    

        ######   Skill   ######
        #Buff skills
        SoulArrow = core.BuffSkill("소울 애로우", 0, 300*1000, rem = True, att = 20).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill("부스터", 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper)
        Hauling = core.BuffSkill("하울링", 0, 300*1000, rem = True, patt = 10).wrap(core.BuffSkillWrapper)
        BeastForm = core.BuffSkill("비스트 폼", 0, 300*1000, rem = True, patt=20+5).wrap(core.BuffSkillWrapper)
        SharpEyes = core.BuffSkill("샤프 아이즈", 1080, (300+3*self.combat) * 1000, crit = 20 + ceil(self.combat/2), crit_damage = 15 + ceil(self.combat/2), rem = True).wrap(core.BuffSkillWrapper)

        #Summon skills
        HuntingUnit = core.SummonSkill("어시스턴트 헌팅 유닛", 660, 31000/90, 150, 1.5, 31000, rem=True).setV(vEhc, 4, 3, False).wrap(core.SummonSkillWrapper)
        DrillContainer = core.SummonSkill("드릴 컨테이너", 660, 270, 430+4*self.combat, 1, 15000, cooltime = 30000, red=True, rem=True).setV(vEhc, 9, 2, False).wrap(core.SummonSkillWrapper)
        
        #Damage skills
        WildBalkan = core.DamageSkill("와일드 발칸", 120, 370 + 2*self.combat, 1, modifier = core.CharacterModifier(boss_pdamage=10+20, pdamage=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        FinalAttack70 = core.DamageSkill("파이널 어택(70)", 0, 210 + 2*passive_level, 0.01*(70+passive_level)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        FinalAttack100 = core.DamageSkill("파이널 어택(100)", 0, 210 + 2*passive_level, 1).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        AnotherBite = JaguerStack(chtr.level, vEhc)

        #Hyper
        WillOfLiberty = core.BuffSkill("윌 오브 리버티", 0, 60*1000, cooltime = 120*1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        SilentRampage = core.BuffSkill("사일런트 램피지", 840, 40*1000, pdamage=40, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)
        
        #5th
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 4, 4)
        RegistanceLineInfantry = resistance.ResistanceLineInfantryWrapper(vEhc, 3, 3)
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 1, 1, 20 + ceil(self.combat/2))
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
    
        JaguerStorm = core.BuffSkill("재규어 스톰", 840, 40*1000, cooltime = (150-vEhc.getV(0,0))*1000, red=True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        
        JaguarMaximum = core.DamageSkill("재규어 맥시멈", 2160, 350+13*vEhc.getV(5,5), 12*9, cooltime = 120*1000, red=True, modifier=core.CharacterModifier(crit=100, armor_ignore=100)).isV(vEhc,5,5).wrap(core.DamageSkillWrapper)
        JaguarMaximumFinal = core.DamageSkill("재규어 맥시멈(마무리)", 630, 450+18*vEhc.getV(5,5), 15*4, cooltime=-1, modifier=core.CharacterModifier(crit=100, armor_ignore=100)).isV(vEhc,5,5).wrap(core.DamageSkillWrapper)
        RidingOff = core.DamageSkill("하차 딜레이", 1800, 0, 0, cooltime=-1).wrap(core.DamageSkillWrapper) # 재규어 맥시멈 강제 탑승 해제 딜레이

        WildGrenade = core.SummonSkill("와일드 그레네이드", 0, 4500, 600+24*vEhc.getV(2,2), 5, 9999*10000).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)

        WildBalkanTypeXInit = core.DamageSkill("와일드 발칸 Type X(개시)", 540, 0, 0, cooltime=120*1000, red=True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        WildBalkanTypeXTick = core.DamageSkill("와일드 발칸 Type X", 120, 450+18*vEhc.getV(0,0), 5, cooltime=-1, modifier=core.CharacterModifier(armor_ignore=20)).isV(vEhc,0,0).wrap(core.DamageSkillWrapper) # 67회 반복
        WildBalkanTypeXEnd = core.DamageSkill("와일드 발칸 Type X(후딜)", 540, 0, 0, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)

        #Build Graph
        FinalAttack = core.OptionalElement(SilentRampage.is_active, FinalAttack100, FinalAttack70)
        
        for sk in [WildBalkan, WildBalkanTypeXTick]:
            sk.onAfter(FinalAttack)
            sk.onAfter(AnotherBite)
        
        JaguarMaximum.onAfter(JaguarMaximumFinal)
        JaguarMaximumFinal.onAfter(AnotherBite.add_debuff(3))
        JaguarMaximumFinal.onAfter(RidingOff)

        WildBalkanTypeXKeydown = core.RepeatElement(WildBalkanTypeXTick, 56)
        WildBalkanTypeXInit.onAfter(WildBalkanTypeXKeydown)
        WildBalkanTypeXInit.onAfter(WildBalkanTypeXEnd)

        #Jaguar
        JaguarSelector = None
        for skill, stormskill, bite, delay in [(Normal, Normal_JG, 0.15, 960), (ClawCut, ClawCut_JG, 0.3, 1530),
            (Crossroad, Crossroad_JG, 0.8, 990), (SonicBoom, SonicBoom_JG, 0.4, 960),
            (JaguarSoul, JaguarSoul_JG, 1, 1320), (RampageAsOne, RampageAsOne_JG, 1, 1440)]:
                if JaguarSelector == None:
                    JaguarSelector = skill
                else:
                    JaguarSelector = core.OptionalElement(skill.is_available, skill, JaguarSelector)
                skill.onAfter(AnotherBite.add_debuff(bite))
                stormskill.onAfter(core.RepeatElement(AnotherBite.add_debuff(bite), JAGUAR_STORM_HIT))
                skill.onAfter(core.OptionalElement(JaguerStorm.is_active, stormskill))
                skill.onAfter(Jaguar.set_delay(delay))
                skill.protect_from_running()

        Jaguar.onTick(JaguarSelector)

        return(WildBalkan,
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_combat_orders(),
                    globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), CriticalReinforce, SoulArrow,
                    Booster, Hauling, BeastForm, SharpEyes, SilentRampage, JaguerStorm, WillOfLiberty, Jaguar,
                    globalSkill.soul_contract()] +\
                [RampageAsOne, JaguarSoul, SonicBoom, Crossroad, ClawCut, Normal] +\
                [HuntingUnit, DrillContainer, GuidedArrow, RegistanceLineInfantry, WildGrenade, JaguarMaximum, WildBalkanTypeXInit, MirrorBreak, MirrorSpider] +\
                [AnotherBite] +\
                [WildBalkan])