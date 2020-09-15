from ..kernel.graph import DynamicVariableOperation
from ..kernel import core
from ..kernel.core import CharacterModifier as MDF
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobclass import heroes
from .jobbranch import magicians

class MagicParticleWrapper(core.DamageSkillWrapper):
    def __init__(self, vEhc, upgrade_index, passive_level):
        skill = core.DamageSkill("마법 잔해", 0, 110, 1, cooltime = 10000).setV(vEhc, upgrade_index, 2, True)
        super(MagicParticleWrapper, self).__init__(skill)
        self.stack = 0
        self.passive_level = passive_level

    def spend_time(self, time):
        self.stack = min(self.stack + time / 400, 15)
        super(MagicParticleWrapper, self).spend_time(time)

    def _use(self, skill_modifier):
        result = super(MagicParticleWrapper, self)._use(skill_modifier)
        self.stack = 0
        return result

    def get_damage(self):
        return self.skill.damage + 2*self.passive_level + (100 + self.passive_level) * (self.stack // 5)

    def get_hit(self):
        return self.skill.hit * self.stack

class SpiralOfManaWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        self.penaltyTime = 0
        skill = core.SummonSkill(
            "스파이럴 오브 마나", 360, 420, 235+vEhc.getV(num1,num2), 6, 7000, cooltime=5000-50*vEhc.getV(num1,num2), red=True
        ).setV(vEhc, 0, 2, False).isV(vEhc, num1, num2)
        super(SpiralOfManaWrapper, self).__init__(skill)

    def spend_time(self, time):
        self.penaltyTime -= time
        super(SpiralOfManaWrapper, self).spend_time(time)

    def _use(self, skill_modifier):
        result = super(SpiralOfManaWrapper, self)._use(skill_modifier)
        self.tick = 780 # TODO: SummonSkill에 공격 시작 시간 입력 가능하게 할 것
        self.penaltyTime = 0
        return result

    def _setPenalty(self):
        if self.is_active():
            self.penaltyTime = 1000
        return self._result_object_cache

    def setPenalty(self):
        task = core.Task(self, self._setPenalty)
        return core.TaskHolder(task, name="스오마 타수 감소")

    def get_hit(self): # 서오마 사용후 1초간 3타, 미사용시 6타
        if self.penaltyTime > 0:
            return self.skill.hit - 3
        else:
            return self.skill.hit

class MirSkillWrapper(core.SummonSkillWrapper):
    def __init__(self, skill):
        super(MirSkillWrapper, self).__init__(skill)
        self.attacking = False

    def _use(self, skill_modifier):
        self.attacking = True
        return super(MirSkillWrapper, self)._use(skill_modifier)

    def endSoon(self, time):
        """
        available, timeLeft만으로 융합/돌아와 시전을 판정하면 종종 available이 먼저 false가 되어 발동에 실패함.
        attacking 변수를 따로 두고, 항상 융합/돌아와 만으로만 스킬이 종료된다는 전제 하에 융합/돌아와 시전 가능 여부를 판정함.
        """
        return self.attacking and self.timeLeft <= time

    def _end(self):
        self.timeLeft = 0
        self.onoff = False
        self.attacking = False
        return self._result_object_cache

    def end(self):
        task = core.Task(self, self._end)
        return core.TaskHolder(task, name="종료")

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "int"
        self.jobname = "에반"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'reuse', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        InheritWill = core.InformedCharacterModifier("계승된 의지",att = 10, stat_main = 10, stat_sub = 10)
        LinkedMagic = core.InformedCharacterModifier("링크드 매직",att = 20)
        
        HighWisdom =  core.InformedCharacterModifier("하이 위즈덤",stat_main = 40)

        SpellMastery = core.InformedCharacterModifier("스펠 마스터리",crit = 15, att = 10)
        
        ElementalReset = core.InformedCharacterModifier("엘리멘탈 리셋",pdamage_indep = 15)
        CriticalMagic = core.InformedCharacterModifier("크리티컬 매직",crit = 30, crit_damage = 20)
        MagicAmplification = core.InformedCharacterModifier("매직 엠플리피케이션",pdamage_indep = 30)
        DragonPotential = core.InformedCharacterModifier("드래곤 포텐셜",armor_ignore = 20)
        
        MagicMastery = core.InformedCharacterModifier("매직 마스터리",att = 30 + passive_level, crit_damage = 20 + passive_level//2)
        DragonFury = core.InformedCharacterModifier("드래곤 퓨리",patt = 35 + passive_level)
        HighDragonPotential = core.InformedCharacterModifier("하이 드래곤 포텐셜",boss_pdamage = 20+passive_level)

        SpiralOfManaPassive = core.InformedCharacterModifier("스파이럴 오브 마나(패시브)", att=5+vEhc.getV(0,0))
        
        return [InheritWill, LinkedMagic,
            HighWisdom, SpellMastery, ElementalReset, CriticalMagic, MagicAmplification, DragonPotential,
            MagicMastery, DragonFury, HighDragonPotential, SpiralOfManaPassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 0)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -2.5 + 0.5*passive_level)  
        Interaction = core.InformedCharacterModifier("교감",pdamage = 20)
        ElementalResetActive = core.InformedCharacterModifier("엘리멘탈 리셋(사용)", prop_ignore = 10)
        
        return [WeaponConstant, Mastery, Interaction, ElementalResetActive]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter):
        '''
        다오어-브레스-브오어

        다오어 3히트
        
        하이퍼 : 
        드스 / 드다 / 드브 쿨리듀스
        드다 - 어스 인핸스
        썬더 보너스 어택
        
        모든 융합스킬은 5차를 제외하고 전부 캔슬
        
        코어 강화
        서오마, 서오어 (+ 다오어, 브오어), 브레스(브레스-돌아와), 서오윈,(+ 브오윈, 스오윈)
        서오썬(스오썬, 다오썬), 드래곤 마스터, 마법 잔해, 드래곤 스파킹, 스위프트
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        SWIFT_OF_THUNDER_HIT = 2
        DIVE_OF_EARTH_HIT = 3
        BREATH_OF_WIND_BONUS = False

        ######   Skill   ######
        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper)
        OnixBless = core.BuffSkill("오닉스의 축복", 0, (180+2*self.combat)*1000, rem = True, att = 80+2*self.combat).wrap(core.BuffSkillWrapper)

        ### 에반 스킬
        CircleOfMana1 = core.DamageSkill("서클 오브 마나 IV(1타)", 180, 290 + self.combat, 4).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        CircleOfMana2 = core.DamageSkill("서클 오브 마나 IV(2타)", 390, 330 + self.combat, 4).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        DragonSparking = core.DamageSkill("드래곤 스파킹", 0, 150, 1).setV(vEhc, 7, 3, True).wrap(core.DamageSkillWrapper)
        MagicParticle = MagicParticleWrapper(vEhc, 6, passive_level)
        
        CircleOfWind = core.DamageSkill("서클 오브 윈드", 660, 320+self.combat, 5).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        CircleOfThunder = core.DamageSkill("서클 오브 썬더", 660, 320+self.combat, 5).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        CircleOfEarth = core.DamageSkill("서클 오브 어스", 660, 320+self.combat, 5).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        DarkFog = core.DamageSkill("다크 포그", 870, 400+2*self.combat, 6, cooltime = 40000, red=True).wrap(core.DamageSkillWrapper)
        
        ### 미르 스킬
        Mir = core.BuffSkill("미르(공격중)", 0, 0, cooltime=-1).wrap(core.BuffSkillWrapper)
        DragonSwift = core.SummonSkill("드래곤 스위프트", 0, 540, 415 + 2*self.combat, 4, 3360, cooltime = 6000, red=True).setV(vEhc, 8, 2, False).wrap(MirSkillWrapper)
        DragonDive = core.SummonSkill("드래곤 다이브", 0, 360, 325 + self.combat, 3, 3480, cooltime = 6000, red=True).wrap(MirSkillWrapper)
        DragonBreath = core.SummonSkill("드래곤 브레스", 0, 360, 240 + self.combat, 5, 2880, cooltime = 7500, red=True).setV(vEhc, 2, 2, False).wrap(MirSkillWrapper)

        ## 융합 스킬
        SwiftOfWind = core.SummonSkill("스위프트 오브 윈드", 0, 360, 215 + self.combat, 2*3, 3360, cooltime=-1, modifier=MDF(pdamage_indep=-35)).setV(vEhc, 3, 2, False).wrap(MirSkillWrapper)
        SwiftOfThunder = core.SummonSkill("스위프트 오브 썬더", 0, 2280/SWIFT_OF_THUNDER_HIT, 450 + self.combat, 6+1, 2280, cooltime=-1).setV(vEhc, 4, 2, False).wrap(MirSkillWrapper)
        # DiveOfThunder - 안씀
        DiveOfEarth = core.SummonSkill("다이브 오브 어스", 0, 2310/DIVE_OF_EARTH_HIT, 190+self.combat+420+2*self.combat, 6, 2310, cooltime=-1, modifier = MDF(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(MirSkillWrapper)
        BreathOfWind = core.SummonSkill("브레스 오브 윈드", 0, 450, 215+self.combat+BREATH_OF_WIND_BONUS*(65+self.combat), 5, 3510, cooltime=-1).setV(vEhc, 3, 2, False).wrap(MirSkillWrapper)
        BreathOfEarth = core.SummonSkill("브레스 오브 어스", 0, 450, 280+self.combat, 5, 3510, cooltime=-1).setV(vEhc, 1, 2, False).wrap(MirSkillWrapper)
        
        ### 돌아와!
        SwiftBack = core.BuffSkill("스위프트-돌아와!", 30, 60000, cooltime=-1, pdamage_indep = 10).wrap(core.BuffSkillWrapper)
        DiveBack = core.BuffSkill("다이브-돌아와!", 30, 60000, cooltime=-1, rem=True).wrap(core.BuffSkillWrapper)
        BreathBack = core.SummonSkill("브레스-돌아와!", 30, 450, 150+self.combat, 1, (30+self.combat // 2)*1000, cooltime=-1).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper)
        
        # 하이퍼
        SummonOnixDragon = core.SummonSkill("서먼 오닉스 드래곤", 900, 3030, 550, 2, 40000, cooltime = 80000).wrap(core.SummonSkillWrapper)
        
        # 드래곤 마스터 - 미사용
        HerosOath = core.BuffSkill("히어로즈 오쓰", 0, 60000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        # 5차
        OverloadMana = magicians.OverloadManaWrapper(vEhc, 1, 4)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        # 각 타마다 최종뎀 스택이 적용됨. 1타(0%)-2타(5%)-3타(10%)-4타(15%) = 평균 7.5%
        ElementalBlast = core.DamageSkill("엘리멘탈 블래스트", 600, 750+30*vEhc.getV(2,3), 6 * 4, cooltime = 60000, red = True, modifier = MDF(crit = 100, pdamage_indep = 7.5)).isV(vEhc,2,3).wrap(core.DamageSkillWrapper)
        ElementalBlastBuff = core.BuffSkill("엘리멘탈 블래스트(버프)", 0, 10000, pdamage_indep = 20, cooltime=-1).isV(vEhc,2,3).wrap(core.BuffSkillWrapper)

        DragonBreak = core.SummonSkill("드래곤 브레이크", 0, 360, 450+18*vEhc.getV(5,5), 7, 2500, cooltime = 20000, red=True).isV(vEhc,5,5).wrap(MirSkillWrapper)
        DragonBreakBack = core.SummonSkill("드래곤 브레이크-돌아와!", 30, 510, 150+6*vEhc.getV(5,5), 3, 5000, cooltime=-1).isV(vEhc,5,5).wrap(core.SummonSkillWrapper)
        ImperialBreath = core.SummonSkill("임페리얼 브레스", 0, 240, 600+24*vEhc.getV(5,5), 7, 4000, cooltime=-1).isV(vEhc,5,5).wrap(MirSkillWrapper)

        ZodiacRayInit = core.DamageSkill("조디악 레이(개시)", 780, 0, 0, cooltime = 180000, red = True).isV(vEhc,4,2).wrap(core.DamageSkillWrapper) # 딜레이 확인 필요
        ZodiacRay = core.SummonSkill("조디악 레이", 0, 180, 400+16*vEhc.getV(4,2), 6, 180*74-1, modifier = MDF(armor_ignore = 100) - MDF(pdamage_indep=10), cooltime = -1).isV(vEhc,4,2).wrap(core.SummonSkillWrapper)
        #14+vlevel//10초간 지속, 남은 시간동안 마법진 해방 딜 180ms마다. : 444타 가정( = 74타)

        SpiralOfMana = SpiralOfManaWrapper(vEhc, 0, 0)
        
        ##### build graph #####
        CircleOfMana1.onAfter(SpiralOfMana.setPenalty())
        CircleOfMana1.onAfter(core.OptionalElement(SpiralOfMana.is_not_active, SpiralOfMana, CircleOfMana2))
        SpiralOfMana.protect_from_running()
        
        #미르 제한조건.
        MirConstraint = core.ConstraintElement("미르(사용중)", Mir, Mir.is_not_active)

        for sk in [DragonSwift, DragonDive, DragonBreath, DragonBreak]:
            sk.onConstraint(MirConstraint)
            sk.onAfter(Mir.controller(DynamicVariableOperation.reveal_argument(sk.skill.remain), "set_enabled_and_time_left"))

        for sk in [BreathOfEarth, BreathOfWind, DiveOfEarth, ImperialBreath]:
            sk.onAfter(Mir.controller(DynamicVariableOperation.reveal_argument(sk.skill.remain), "set_enabled_and_time_left"))

        for back, li in [(SwiftBack, [DragonSwift, SwiftOfThunder, SwiftOfWind]), (DiveBack, [DragonDive, DiveOfEarth]),
                    (BreathBack, [DragonBreath, BreathOfEarth, BreathOfWind]), (DragonBreakBack, [DragonBreak, ImperialBreath])]:
            for sk in li:
                back.onAfter(sk.end())
            back.onAfter(Mir.controller(1))

        # 브레이크/엘블/임브
        ElementalBlast.onConstraint(core.ConstraintElement("엘리멘탈 블래스트 실행조건", Mir, lambda: DragonBreak.endSoon(1000)))
        ElementalBlast.onAfter(ElementalBlastBuff)
        ElementalBlast.onAfter(ImperialBreath)
        
        ImperialBreath.onAfter(DragonBreak.end())

        DragonBreak.onAfter(DragonBreakBack.controller(1))
        ImperialBreath.onAfter(DragonBreakBack.controller(1))
        DragonBreakBack.onConstraint(core.ConstraintElement("드래곤 브레이크-돌아와! 실행조건", Mir,
            lambda: ImperialBreath.endSoon(1000) or (DragonBreak.endSoon(1000) and not ElementalBlast.is_available())
        ))

        # 브레스
        DragonBreath.onAfter(BreathOfEarth.controller(1))
        BreathOfEarth.onConstraint(core.ConstraintElement("브오어 실행조건", Mir, lambda: DragonBreath.endSoon(1000)))
        BreathOfEarth.onAfter(CircleOfMana1) # 마나캔슬
        BreathOfEarth.onAfter(DragonBreath.end())
        
        BreathOfEarth.onAfter(BreathBack.controller(1))
        BreathBack.onConstraint(core.ConstraintElement("브레스-돌아와! 실행조건", Mir, lambda: BreathOfEarth.endSoon(1000)))

        # 다이브
        DragonDive.onAfter(DiveOfEarth.controller(1))
        DiveOfEarth.onConstraint(core.ConstraintElement("다오어 실행조건", Mir, lambda: DragonDive.is_active()))
        DiveOfEarth.onAfter(CircleOfMana1) # 마나캔슬
        DiveOfEarth.onAfter(DragonDive.end())

        DiveOfEarth.onAfter(core.OptionalElement(lambda: DiveBack.is_time_left(8500, -1), DiveBack.controller(1)))
        DiveBack.onConstraint(core.ConstraintElement("다이브-돌아와! 실행조건", Mir, lambda: DiveOfEarth.endSoon(1000)))

        # 스위프트
        DragonSwift.onConstraint(core.ConstraintElement("스위프트 실행조건", Mir, lambda: SwiftBack.is_time_left(5000, -1))) # 버프 없을때만 사용
        SwiftOfWind.onAfter(DragonSwift.end())

        DragonSwift.onAfter(SwiftBack.controller(1))
        SwiftOfWind.onAfter(SwiftBack.controller(1))
        SwiftBack.onConstraint(core.ConstraintElement("스위프트-돌아와! 실행조건", Mir, lambda: SwiftOfWind.is_active() or DragonSwift.is_active())) # 스위프트 즉시 종료

        #조디악 레이
        for sk in [MagicParticle, DragonBreath, CircleOfWind, BreathOfWind, BreathBack, MagicParticle, DragonSwift, CircleOfEarth, SwiftOfWind, DarkFog]:
            ZodiacRayInit.onAfter(sk)
        ZodiacRayInit.onAfter(ZodiacRay)
        
        #파이널 어택
        for i in [CircleOfMana2, CircleOfEarth, CircleOfWind, CircleOfThunder, DarkFog]:
            i.onAfter(DragonSparking)
            
        return(CircleOfMana1,
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_wind_booster(),
                    Mir, OverloadMana, Booster, OnixBless, HerosOath, ElementalBlastBuff,
                    globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()] +\
                [ZodiacRayInit, MagicParticle] +\
                [SummonOnixDragon, SpiralOfMana, ZodiacRay, DragonBreak, DragonBreakBack, ElementalBlast, ImperialBreath,
                    DragonSwift, SwiftBack, DragonDive, DiveOfEarth, DiveBack, DragonBreath, BreathOfEarth, BreathBack, MirrorBreak, MirrorSpider] +\
                [] +\
                [CircleOfMana1])