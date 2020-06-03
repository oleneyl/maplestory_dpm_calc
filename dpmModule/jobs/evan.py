from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..kernel.core import CharacterModifier as MDF
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobclass import heroes

# TODO : 조디악 커맨드 수정

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "int"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'reuse', 'buff_rem')
        self.preEmptiveSkills = 1
    
    def apply_complex_options(self, chtr):
        chtr.add_property_ignorance(10)

    def get_passive_skill_list(self):
        InheritWill = core.InformedCharacterModifier("상속된 의지",att = 10, stat_main = 10)
        LinkedMagic = core.InformedCharacterModifier("링크드 매직",att = 20)
        
        HighWisdom =  core.InformedCharacterModifier("하이 위즈덤",stat_main = 40)

        SpellMastery = core.InformedCharacterModifier("스펠 마스터리",crit = 15, att = 10)
        
        ElementalReset = core.InformedCharacterModifier("엘리멘탈 리셋",pdamage_indep = 15)
        CriticalMagic = core.InformedCharacterModifier("크리티컬 매직",crit = 30, crit_damage = 20)
        MagicAmplification = core.InformedCharacterModifier("매직 엠플리피케이션",pdamage_indep = 30)
        DragonPotential = core.InformedCharacterModifier("드래곤 포텐셜",armor_ignore = 20)
        
        MagicMastery = core.InformedCharacterModifier("매직 마스터리",att = 30, crit_damage = 20)
        DragonFury = core.InformedCharacterModifier("드래곤 퓨리",patt = 35)
        HighDragonPotential = core.InformedCharacterModifier("하이 드래곤 포텐셜",boss_pdamage = 20)
        
        return [InheritWill, LinkedMagic,
            HighWisdom, SpellMastery, ElementalReset, CriticalMagic, MagicAmplification, DragonPotential,
            MagicMastery, DragonFury, HighDragonPotential]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 0)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -2.5)  
        Interaction = core.InformedCharacterModifier("연계",pdamage = 20)
        
        return [WeaponConstant, Mastery,Interaction]
    
    def getMergedSkill(self, sname, tick, mirRem, vEhc = None, passive = False, nametag = ''):
        '''You must give vEnhance and vlevel.
        mirRem : 미르 제한조건 버프.
        '''
        #융합스킬
        #SwiftOfWind 
        #DiveOfThunder
        if sname == "스위프트 오브 썬더":
            SwiftOfThunderTick = core.DamageSkill("스위프트 오브 썬더"+nametag, 330, 150+80+300, 6 + 1, cooltime = 8000) # 5회 공격 별그림
            SwiftOfThunder = core.SummonSkill("스위프트 오브 썬더(소환)", 0, 330, 150+80+300, 6+1, tick * 330 - 1, cooltime = (-1 if passive else 8000)).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)
            SwiftOfThunder.onAfter(mirRem.controller(330*tick, "set_enabled_and_time_left"))
            return SwiftOfThunder
        elif sname =="브레스 오브 윈드":
            BreathOfWindTick = core.DamageSkill("브레스 오브 윈드(틱)", 450, 215, 5, cooltime = 7500) # 3.5초 지속, 8회 공격
            BreathOfWind = core.SummonSkill("브레스 오브 윈드"+nametag, 0, 450, 215, 5, tick * 450 - 1, cooltime = (-1 if passive else 7500)).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)
            BreathOfWind.onAfter(mirRem.controller(450*tick, "set_enabled_and_time_left"))
            return BreathOfWind
        elif sname == "브레스 오브 어스":
            BreathOfEarthTick = core.DamageSkill("브레스 오브 어스(틱)", 480, 280, 5, cooltime = 7500) #3.5초 지속, 7회 공격
            BreathOfEarth = core.SummonSkill("브레스 오브 어스"+nametag, 0, 480, 280, 5, tick * 480 - 1, cooltime = (-1 if passive else 7500)).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)
            BreathOfEarth.onAfter(mirRem.controller(480*tick, "set_enabled_and_time_left"))
            return BreathOfEarth
        elif sname == "다이브 오브 어스":
            DiveOfEarthTick = core.DamageSkill("다이브 오브 어스(틱)", 480, 190 + 420, 6, cooltime = 6000, modifier = MDF(pdamage = 20)) # 4타
            DiveOfEarth = core.SummonSkill("다이브 오브 어스"+nametag, 0, 480, 190+420, 6, tick * 480 - 1, cooltime = (-1 if passive else 6000), modifier = MDF(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)
            DiveOfEarth.onAfter(mirRem.controller(480*tick, "set_enabled_and_time_left"))
            return DiveOfEarth
        elif sname == "임페리얼 브레스":
            ImperialBreathTick = core.DamageSkill("임페리얼 브레스(틱)", 250, 500+20*vEhc.getV(3,1), 7)# 4초 지속, 16타
            ImperialBreath = core.SummonSkill("임페리얼 브레스"+nametag, 0, 250, 500+20*vEhc.getV(3,1), 7, tick * 250 - 1, cooltime = (-1 if passive else 60000)).isV(vEhc,3,1).wrap(core.SummonSkillWrapper)
            ImperialBreath.onAfter(mirRem.controller(250 * tick, "set_enabled_and_time_left"))
            return ImperialBreath
        else:
            raise TypeError("적법한 키워드를 넘겨주세요")
        
        
    def getMirSkill(self, sname, tick):
        #DragonBreak = core.DamageSkill("드래곤 브레이크", ?, 450+18*vlevel, 7, cooltime = 20000) 2.5초 지속, 6회
        pass
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        다오어-브레스-브오윈
        
        하이퍼 : 
        드스 / 드다 / 드브 쿨리듀스
        드다 - 엇 인핸스
        썬더 보너스 어택
        
        모든 융합스킬은 5차를 제외하고 전부 캔슬
        
        코강 : 12개
        서오마, 서오어 (+ 다오어, 브오어), 브레스(브레스-돌아와), 서오윈,(+ 브오윈, 스오윈) : 
        서오썬(스오썬, 다오썬), 드래곤 마스터, 잔해
        '''

        
        ######   Skill   ######
        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper)    #딜레이 모름
        OnixBless = core.BuffSkill("오닉스의 축복", 0, 180000, rem = True, att = 80).wrap(core.BuffSkillWrapper)


        CircleOfMana = core.DamageSkill("서클 오브 마나 IV", 600, 315, 8).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)    #클라값 510
        DragonSparking = core.DamageSkill("드래곤 스파킹", 0, 150, 1).setV(vEhc,6,2).wrap(core.DamageSkillWrapper)  
        #MagicParticle = core.DamageSkill("마법 잔해", 110, 1) 0.4초마다 생성, +100 (5개당 증가) -> 6초마다 사용
        MagicParticle = core.DamageSkill("마법 잔해", 0, 410, 15, cooltime = 10000).setV(vEhc, 5, 2, True).wrap(core.DamageSkillWrapper)
        
        ### 에반 스킬
        CircleOfWind = core.DamageSkill("서클 오브 윈드", 780,270 + 150 + 660, 2).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        CircleOfThunder = core.DamageSkill("서클 오브 썬더", 750, 170 + 200, 5).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        CircleOfEarth = core.DamageSkill("서클 오브 어스", 900, 370, 5).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        ### 미르 스킬
        SwiftOfWind = core.DamageSkill("스위프트 오브 윈드", 480, (55+30+160) * 0.65, 2 *3, cooltime = 8000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper) # 3.5초 지속 
        DragonDive = core.DamageSkill("드래곤 다이브", 420, 130 + 195, 3, cooltime = 6000).wrap(core.DamageSkillWrapper) #3.5초 지속, 9회 타격 임의딜레이 420
        DragonBreath = core.DamageSkill("드래곤 브레스", 390, 240, 5, cooltime = 7500).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)  # 3초 지속, 8타
        
        ### 돌아와!
        SwiftBack = core.BuffSkill("스위프트-돌아와!", 0, 60000, cooltime = -1, pdamage_indep = 10).wrap(core.BuffSkillWrapper)
        BreathBack = core.DotSkill("브레스-돌아와!", 150, 30000).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper)
        
        # 하이퍼
        SummonOnixDragon = core.SummonSkill("서먼 오닉스 드래곤", 900, 3030, 550, 2, 4000, cooltime = 80000).wrap(core.SummonSkillWrapper)
        
        # 드래곤 마스터 - 미사용
        HerosOath = core.BuffSkill("히어로즈 오쓰", 0, 60000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        OverloadMana = core.BuffSkill("오버로드 마나", 0, 99999 * 10000, pdamage = 8+int(0.1*vEhc.getV(1,4))).isV(vEhc,1,4).wrap(core.BuffSkillWrapper)
        
        
        # modifierInvariantFlag = False
        Frid = heroes.FridWrapper(vEhc, 0, 0, False)
        
        ElementalBlast = core.DamageSkill("엘리멘탈 블래스트", 1500, (750+30*vEhc.getV(2,3)) * 1.1, 6 * 4, cooltime = 60000, red = True, modifier = MDF(crit = 100)).isV(vEhc,2,3).wrap(core.DamageSkillWrapper) #4연속, 임의 딜레이
        ElementalBlastBuff = core.BuffSkill("엘리멘탈 블래스트(버프)", 0, 10000, pdamage_indep = 20).isV(vEhc,2,3).wrap(core.BuffSkillWrapper)

        DragonBreak = core.DamageSkill("드래곤 브레이크", 0, 450+18*vEhc.getV(5,5), 7 * 6, cooltime = 20000).isV(vEhc,5,5).wrap(core.DamageSkillWrapper)# 420초 6타

        ZodiakRayInit = core.DamageSkill("조디악 레이(개시)", 780, 0, 0, cooltime = 180000, red = True).isV(vEhc,4,2).wrap(core.DamageSkillWrapper)
        ZodiakRay = core.SummonSkill("조디악 레이", 0, 180, 400+16*vEhc.getV(4,2), 6, 180*71, modifier = MDF(armor_ignore = 100), cooltime = -1).isV(vEhc,4,2).wrap(core.SummonSkillWrapper)
        #14+vlevel//10초간 지속, 남은 시간동안 마법진 해방 딜 180ms마다. : 426타 가정( = 71타)
        
        ##### build graph #####
        
        #미르 제한조건.
        MirBuff = core.BuffSkill("미르(사용중)", 0, 100000, cooltime = -1).wrap(core.BuffSkillWrapper)
        MirConstraint = core.ConstraintElement("미르(사용중)(제한)", MirBuff, MirBuff.is_not_active)
        
        #스오썬
        SwiftOfThunder = self.getMergedSkill("스위프트 오브 썬더", 5, MirBuff, vEhc = vEhc)
        SwiftOfThunder.onAfter(CircleOfMana)  #5타 전타 맞춤 가정
        SwiftOfThunder.onAfter(SwiftBack)
        
        SwiftBackConstraint = core.ConstraintElement("스위프트 - 돌아와!(쿨타임) 일때만", SwiftBack, SwiftBack.is_not_active)
        
        SwiftOfThunder.onConstraint(SwiftBackConstraint)
        
        #다오어
        DiveOfEarth = self.getMergedSkill("다이브 오브 어스", 3, MirBuff, vEhc = vEhc)#다오어는 3타만
        DiveOfEarth.onAfter(CircleOfMana)  
        
        #브오어
        BreathOfEarth = self.getMergedSkill("브레스 오브 어스", 7, MirBuff, vEhc = vEhc)
        BreathOfEarth.onAfter(CircleOfMana)
        
        #브오윈
        BreathOfWind = self.getMergedSkill("브레스 오브 윈드", 8, MirBuff, vEhc = vEhc)
        BreathOfWind.onAfter(CircleOfMana)        
        
        DragonBreathForBOW = core.RepeatElement(DragonBreath, 8)
        BreathOfWind.onBefore(DragonBreathForBOW)

        #브오윈 - 조디악
        BreathOfWindZodiak = self.getMergedSkill("브레스 오브 윈드", 1, MirBuff, vEhc = vEhc, nametag = '조디악')
        #임페리얼
        ImperialBreath = self.getMergedSkill("임페리얼 브레스", 16, MirBuff, vEhc = vEhc, passive = True)
        ElementalBlast.onAfter(ElementalBlastBuff)
        ElementalBlast.onAfter(ImperialBreath)
        Imperial = core.OptionalElement(ElementalBlast.is_usable, ElementalBlast)
        
        DragonBreak.onAfter(Imperial)
        
        #조디악 레이
        ZodiakIfNotElemental = core.GraphElement("조디악 레이 - 엘리멘탈X")
        ZodiakIfNotElemental.onAfters([CircleOfMana, CircleOfEarth, DragonBreak, BreathBack, BreathOfWindZodiak])
        
        ZodiakIfElemental = core.GraphElement("조디악 레이 - 엘리멘탈O")
        ZodiakIfElemental.onAfters([ElementalBlast, CircleOfEarth, DragonBreak, BreathBack, BreathOfWindZodiak])
        
        ZodiakRayUse = core.OptionalElement(ElementalBlast.is_usable, ZodiakIfElemental, ZodiakIfNotElemental)
        ZodiakRayUse.onAfter(ZodiakRay)
        ZodiakRayInit.onAfter(ZodiakRayUse)

        #미르 제한조건(Constraint) 적용
        for i in [SwiftOfThunder, DiveOfEarth, BreathOfEarth, ImperialBreath]:
            i.onConstraint(MirConstraint)
            
        for i in [SwiftBack, BreathBack]:
            i.onAfter(MirBuff.controller(-1))
            
        for i in [SwiftOfThunder, DiveOfEarth, BreathOfEarth, ImperialBreath, CircleOfMana, BreathOfWind]:
            i.onAfter(DragonSparking)
            
        return(CircleOfMana,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster(),
                    OverloadMana, Booster, OnixBless, Frid, HerosOath, SwiftBack, ElementalBlastBuff,
                    globalSkill.soul_contract()] +\
                [ZodiakRayInit, DragonBreak, MagicParticle] +\
                [BreathBack, SummonOnixDragon, ZodiakRay, ImperialBreath, SwiftOfThunder, DiveOfEarth, BreathOfWind, BreathOfWindZodiak] +\
                [MirBuff] +\
                [CircleOfMana])