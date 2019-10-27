from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import magicians

class IliumStackWrapper(core.StackSkillWrapper):
    def __init__(self, skill, _max, fastChargeJudge, stopJudge, name = None):
        super().__init__(skill, _max, name = name)
        self.triggers = []
        self.fastChargeJudge = fastChargeJudge
        self.stopJudge = stopJudge

    def addTrigger(self, controller, stack, isLast = False):
        self.triggers.append({"controller":controller.build_task(), "stack" : stack, "state" : False, "isLast" : isLast})
    
    def vary(self, d):
        delta = d
        if self.fastChargeJudge.is_active():
            #print("====FAST====")
            delta += d
        
        if not self.stopJudge():
            result = super().vary(delta)
        else:
            result = super().vary(0)

        for trigger in self.triggers:
            if (trigger["stack"] < self.stack) and (not trigger["state"]):
                #result.cascade.append(trigger["controller"])
                #Insafe mode running! But this prevents event loop.
                trigger["controller"].do()
                trigger["state"] = True
                
                if trigger["isLast"]:
                    self.stack = 0
                    for eachTrigger in self.triggers:
                        eachTrigger["state"] = False
                    
        return result



class JobGenerator(ck.JobGenerator):
    def __init__(self, vEhc = None):
        super(JobGenerator, self).__init__(vEhc = vEhc)
        self.jobtype = "int"
        self.vEnhanceNum = 12
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1
        
    def get_passive_skill_list(self):
        vEhc = self.vEhc
        # 앱솔 무기 마력 241
        WEAPON_ATT = 241
        MagicCircuit = core.InformedCharacterModifier("매직 서킷", att = WEAPON_ATT*0.2)
        
        MagicGuntletMastery = core.InformedCharacterModifier("매직 건틀렛 마스터리", crit = 20)
        BlessMarkPassive = core.InformedCharacterModifier("블레스 마크(패시브)", pdamage = 10)
        LefMastery = core.InformedCharacterModifier("레프 마스터리", pdamage = 10)
        
        DestinyPioneer = core.InformedCharacterModifier("운명 개척", stat_main = 40, patt = 10)
        ContinualResearch = core.InformedCharacterModifier("끊임없는 연구", att = 50, crit = 20, crit_damage = 30)
        CrystalSecret = core.InformedCharacterModifier("크리스탈의 비밀", boss_pdamage = 30, pdamage_indep = 35, armor_ignore = 25)
        
        return [MagicCircuit, MagicGuntletMastery, BlessMarkPassive,
            LefMastery, DestinyPioneer, ContinualResearch, CrystalSecret ]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -5)
        
        return [WeaponConstant, Mastery]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        하이퍼 : 자벨린- 보스킬러, 리인포스, 보너스 어택
        
        소환수 강화 아직 미적용
        
        '''
        
        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 200*1000).wrap(core.BuffSkillWrapper)
        FastCharge = core.BuffSkill("패스트 차지", 600, 10000, cooltime = 120000).wrap(core.BuffSkillWrapper) #임의딜레이 600
        WraithOfGod = core.BuffSkill("레이스 오브 갓", 0, 60000, pdamage = 10, cooltime = 120000).wrap(core.BuffSkillWrapper)
        
        Craft_Orb = core.DamageSkill("크래프트:오브", 510, 300, 1).wrap(core.DamageSkillWrapper)
        Reaction_Domination = core.DamageSkill("리액션 : 도미네이션", 0, 550, 2, cooltime = 4000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        Craft_Javelin_EnhanceBuff = core.BuffSkill("크래프트:오브(자벨린 강화버프)", 0, 2000, cooltime = -1).wrap(core.BuffSkillWrapper)
        
        Craft_Javelin = core.DamageSkill("크래프트:자벨린", 510, 375, 4 * 3, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Craft_Javelin_AfterOrb = core.DamageSkill("크래프트:자벨린(오브 이후)", 510, 405, 4 * 3, modifier = core.CharacterModifier(pdamage = 20 + 15, boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        
        Craft_Javelin_Fragment = core.DamageSkill("크래프트:자벨린(파편)", 0, 130, 2 * 3, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Reaction_Destruction = core.DamageSkill("리액션 : 디스트럭션", 0, 550, 4*2, modifier = core.CharacterModifier(boss_pdamage = 20), cooltime = 4000).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        Craft_Longinus = core.DamageSkill("크래프트:롱기누스", 1170, 900, 7, cooltime = 15000).wrap(core.DamageSkillWrapper)
        
        Riyo = core.SummonSkill("리요", 900, 500, 140, 1, 180000).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper) #임의딜레이 900
        Machina = core.SummonSkill("마키나", 900, 1980, 350, 4, 180000).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper)    #임의딜레이 900
        
        CrystalSkill_MortalSwing = core.DamageSkill("크리스탈 스킬:모탈 스윙", 0, 600, 10, cooltime = -1).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)    #30
        CrystalSkill_Deus = core.SummonSkill("데우스", 0, 4800, 315, 5, 30*1000, cooltime = -1).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)   #90, 7타
        
        LonginusZone = core.DamageSkill("롱기누스 존", 690, 1500, 12, cooltime = 180*1000)    #안씀
        
        BlessMark = core.BuffSkill("블레스 마크", 0, 99999999, att = 46).wrap(core.BuffSkillWrapper)
        CurseMark = core.BuffSkill("커스 마크", 0, 99999999, armor_ignore = 20).wrap(core.BuffSkillWrapper)
        CurseMarkFinalAttack = core.DamageSkill("커스 마크(추가타)", 0, 200, 1).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        '''
        
        데우스 리인포스 / 보택 찍기.
        
        ( 500 * 5 * 7 + 39 * 140 ) / 30 => 1초당 765
        
        280+170=450
        데우스 공격력 : 315
        '''
        
        #글로리 윙
        GloryWingStackSkill = core.BuffSkill("글로링 윙(스택)", 0, 9999999)
        
        GloryWingUse = core.BuffSkill("글로리 윙(진입)", 30, 20000, pdamage_indep = 25, boss_pdamage = 30, cooltime = -1).wrap(core.BuffSkillWrapper) #150
        
        GloryWing_MortalWingbit = core.DamageSkill("글로리 윙(모탈 윙비트)", 0, 2000, 8, cooltime = -1).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)  #1회
        
        GloryWing_Craft_Javelin = core.DamageSkill("크래프트:자벨린(글로리 윙)", 390, 465, 7, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, pdamage_indep=80)).setV(vEhc, 0, 0, True).wrap(core.DamageSkillWrapper)
        GloryWing_Craft_Javelin_Fragment = core.DamageSkill("크래프트:자벨린(글로리 윙)(파편)", 0, 200+100, 3*3, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20)).setV(vEhc, 0, 0, True).wrap(core.DamageSkillWrapper)
        #5차 스킬들
        OverloadMana = OverloadMana = magicians.OverloadManaWrapper(vEhc, 0, 3)
        GramHolder = core.SummonSkill("그람홀더", 900, 3000, 1000+25*vEhc.getV(4,3), 6, 40000, cooltime = 180000).isV(vEhc,4,3).wrap(core.SummonSkillWrapper)   #임의딜레이 900
        
        MagicCircuitFullDrive = core.BuffSkill("매직서킷 풀드라이브", 720, (30+vEhc.getV(3,2))*1000, pdamage = (20 + vEhc.getV(3,2)), cooltime = 200*1000).isV(vEhc,3,2).wrap(core.BuffSkillWrapper)
        MagicCircuitFullDriveStorm = core.SummonSkill("매직서킷 풀드라이브(마력 폭풍)", 0, 4000, 500+20*vEhc.getV(3,2), 3, (30+vEhc.getV(3,2))*1000, cooltime = -1).wrap(core.SummonSkillWrapper)
        
        CrystalIgnitionInit = core.DamageSkill("크리스탈 이그니션(시전)", 960, 0, 0, cooltime = 180*1000).wrap(core.DamageSkillWrapper)
        CrystalIgnition = core.DamageSkill("크리스탈 이그니션", 270, 750 + 25*vEhc.getV(2,1), 4, modifier = core.CharacterModifier(boss_pdamage = 20)).isV(vEhc,2,1).wrap(core.DamageSkillWrapper) #75회
        
        Reaction_Spectrum = core.SummonSkill("리액션:스펙트럼", 0, 1000, 1000+40*vEhc.getV(2,1), 5, 10000, cooltime = -1).wrap(core.SummonSkillWrapper) #1초마다 시전됨.
 
        # TODO:소오크 소모시 강화 반영필요
        SoulOfCrystal = core.BuffSkill("소울 오브 크리스탈", 660, 30*1000, cooltime = 40*1000).isV(vEhc,1,0).wrap(core.BuffSkillWrapper)
        SoulOfCrystalPassive = core.BuffSkill("소울 오브 크리스탈(패시브)", 0, 999999999, att = (5+vEhc.getV(1,0)*2)).isV(vEhc,1,0).wrap(core.BuffSkillWrapper)
        SoulOfCrystal_Reaction_Domination = core.DamageSkill("리액션 : 도미네이션(소오크)", 0, 550 * 0.01 * (50 + vEhc.getV(1,0)) * 2, 2).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        SoulOfCrystal_Reaction_Destruction = core.DamageSkill("리액션 : 디스트럭션(소오크)", 0, 550* 0.01 * (50 + vEhc.getV(1,0)) * 2, 4*2, modifier = core.CharacterModifier(boss_pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        SoulOfCrystal_Reaction_Spectrum = core.SummonSkill("리액션:스펙트럼(소오크)", 0, 1000, 1000+40*vEhc.getV(2,1) * 2, 5, 10000, cooltime = -1).wrap(core.SummonSkillWrapper)
        
        #스킬간 연결

        Reaction_Destruction_Link = core.OptionalElement(SoulOfCrystal.is_active, SoulOfCrystal_Reaction_Destruction, name = "리액션:디스트럭션(소오크여부)")
        Reaction_Domination_Link = core.OptionalElement(SoulOfCrystal.is_active, SoulOfCrystal_Reaction_Domination, name = "리액션:도미네이션(소오크여부)")
        Reaction_Spectrum_Link = core.OptionalElement(SoulOfCrystal.is_active, SoulOfCrystal_Reaction_Spectrum, name = "리액션:스펙트럼(소오크여부)")
        
        Reaction_Destruction.onAfter(Reaction_Destruction_Link)
        Reaction_Domination.onAfter(Reaction_Domination_Link)
        Reaction_Spectrum.onAfter(Reaction_Spectrum_Link)
                
        Reaction_Domination_Trigger = core.OptionalElement(lambda:Reaction_Domination.available, Reaction_Domination, name = "리액션:도미네이션")
        Reaction_Destruction_Trigger = core.OptionalElement(lambda:Reaction_Destruction.available, Reaction_Destruction, name = "리액션:디스트럭션")
        Reaction_Spectrum_Trigger = core.OptionalElement(Reaction_Spectrum.is_usable, Reaction_Spectrum, name = "리액션:스펙트럼")
        
        Craft_Orb.onAfter(Reaction_Domination_Trigger)
        Craft_Javelin.onAfter(Reaction_Destruction_Trigger)
        Craft_Javelin.onAfter(Craft_Javelin_Fragment)
        
        Craft_Javelin_AfterOrb.onAfter(Reaction_Destruction_Trigger)
        Craft_Javelin_AfterOrb.onAfter(Craft_Javelin_Fragment)        
        
        GloryWing_Craft_Javelin.onAfter(GloryWing_Craft_Javelin_Fragment)
        
        CrystalIgnitionInit.onAfter(core.RepeatElement(CrystalIgnition, 75))
        CrystalIgnitionInit.onAfter(Reaction_Spectrum_Trigger)
        
        MagicCircuitFullDrive.onAfter(MagicCircuitFullDriveStorm)
        
        #자벨린 이후 바로 오브를 시전합니다.
        Craft_Javelin.onAfter(Craft_Orb)
        Craft_Javelin_AfterOrb.onAfter(Craft_Orb)

        #스택 연결
        CrystalCharge = IliumStackWrapper(GloryWingStackSkill, 160, FastCharge, GloryWingUse.is_active ,name = "크리스탈 차지")
        CrystalCharge.addTrigger(CrystalSkill_MortalSwing.controller(1), 30)
        CrystalCharge.addTrigger(CrystalSkill_Deus.controller(1), 90)
        CrystalCharge.addTrigger(GloryWingUse.controller(1), 150, isLast = True)
        
        FastCharge.onConstraint( core.ConstraintElement("글로리윙 미사용중", GloryWingUse, GloryWingUse.is_not_active ) )
        
        #기본공격 설정
        BasicAttack = core.OptionalElement(GloryWingUse.is_active, GloryWing_Craft_Javelin, Craft_Javelin_AfterOrb, name = "기본공격(글로리 윙 여부 판단)")
        BasicAttackWrapper = core.DamageSkill('기본 공격', 0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)
        #커스마크 파이널어택
        BasicAttack.onAfter(CurseMarkFinalAttack)
        CrystalIgnition.onAfter(CurseMarkFinalAttack)
        
        GloryWingUse.onAfter(GloryWing_MortalWingbit.controller(1))
        
        Craft_Javelin_AfterOrb.onAfter(CrystalCharge.stackController(2))
        Craft_Javelin.onAfter(CrystalCharge.stackController(2))
        Craft_Orb.onAfter(CrystalCharge.stackController(1))
        Craft_Longinus.onAfter(CrystalCharge.stackController(3))

        Reaction_Domination.protect_from_running()
        Reaction_Destruction.protect_from_running()

        return(BasicAttackWrapper,
                [SoulOfCrystalPassive, globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    Booster, FastCharge, WraithOfGod, MagicCircuitFullDrive, SoulOfCrystal,
                    Craft_Javelin_EnhanceBuff, CrystalCharge, GloryWingUse,
                    OverloadMana, BlessMark, CurseMark,
                    globalSkill.soul_contract()] +\
                [CrystalSkill_MortalSwing, GloryWing_MortalWingbit, CrystalIgnitionInit] +\
                [Riyo, Machina, CrystalSkill_Deus, 
                    GramHolder, MagicCircuitFullDriveStorm, Reaction_Spectrum, SoulOfCrystal_Reaction_Spectrum] +\
                [Reaction_Domination, Reaction_Destruction] +\
                [BasicAttackWrapper])