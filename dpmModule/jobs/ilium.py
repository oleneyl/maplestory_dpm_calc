from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, MutualRule, InactiveRule, ConcurrentRunRule, ReservationRule, ConditionRule
from . import globalSkill
from .jobbranch import magicians
from . import jobutils

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

class SoulOfCrystalWrapper(core.BuffSkillWrapper):
    def __init__(self, skill, name = None):
        super().__init__(skill, name)

    def turnOff(self):
        self.timeLeft = 0
        self.onoff = False
        return self._disabledResultobjectCache

    def turnOffController(self):
        task = core.Task(self, self.turnOff)
        return core.TaskHolder(task, name = "소오크 흡수")

class RiyoWrapper(core.SummonSkillWrapper):
    """
    1단계:60%의 데미지로 공격, 10회 공격 시 공격력 강화
    2단계:100%의 데미지로 공격, 10회 공격 시 공격력 강화
    3단계:200%의 데미지로 공격, 20회 공격 시 초기화
    크리스탈 스킬: 데우스의 패시브로 각 단계의 데미지 +100%p
    """
    def __init__(self, skill):
        super(RiyoWrapper, self).__init__(skill)
        self.count = 0

    def _use(self, rem = 0, red = 0):
        self.count = 0
        return super(RiyoWrapper, self)._use(rem, red)
    
    def _useTick(self):
        if self.onoff and self.tick <= 0:
            if self.count < 10:
                damage = 160
            if self.count < 20:
                damage = 200
            else:
                damage = 300
            self.count += 1
            if self.count >= 40:
                self.count = 0
            
            self.tick += self.skill.delay
            return core.ResultObject(0, self.get_modifier(), damage, self.skill.hit, sname = self.skill.name, spec = self.skill.spec)
        else:
            return core.ResultObject(0, self.disabledModifier, 0, 0, sname = self.skill.name, spec = self.skill.spec)

class GramHolderWrapper(core.SummonSkillWrapper):
    """
    공격 준비 중 크리스탈 차지가 3 이상 충전되거나 글로리 윙 상태라면 최종 데미지 2배로 증가
    """
    def __init__(self, skill):
        self.chargeBefore = 0
        self.crystalCharge = None
        self.gloryWing = None
        super(GramHolderWrapper, self).__init__(skill)
    
    def registerCrystalCharge(self, skill):
        self.crystalCharge = skill

    def registerGloryWing(self, skill):
        self.gloryWing = skill
    
    def _useTick(self):
        if self.onoff and self.tick <= 0:
            modifier = self.get_modifier()
            if self.gloryWing.is_active() or self.crystalCharge.judge(self.chargeBefore + 3, 1):
                modifier = modifier + core.CharacterModifier(pdamage_indep = 100)
            self.chargeBefore = self.crystalCharge.stack
            self.tick += self.skill.delay
            return core.ResultObject(0, modifier, self.skill.damage, self.skill.hit, sname = self.skill.name, spec = self.skill.spec)
        else:
            return core.ResultObject(0, self.disabledModifier, 0, 0, sname = self.skill.name, spec = self.skill.spec)
    
class JobGenerator(ck.JobGenerator):
    def __init__(self, vEhc = None):
        super(JobGenerator, self).__init__(vEhc = vEhc)
        self.jobtype = "int"
        self.vEnhanceNum = 12
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(MutualRule("패스트 차지", "크리스탈 이그니션(시전)"), RuleSet.BASE)
        ruleset.add_rule(InactiveRule("패스트 차지", "글로리 윙(진입)"), RuleSet.BASE)
        ruleset.add_rule(ReservationRule("그람홀더", "글로리 윙(진입)"), RuleSet.BASE)
        ruleset.add_rule(ConditionRule("글로리 윙(진입)", "그람홀더", lambda x:x.is_active() or x.is_not_usable()), RuleSet.BASE)
        ruleset.add_rule(ReservationRule("크리스탈 스킬:데우스", "글로리 윙(진입)"), RuleSet.BASE)
        ruleset.add_rule(ConditionRule("글로리 윙(진입)", "크리스탈 스킬:데우스", lambda x:x.is_active() or x.is_not_usable()), RuleSet.BASE)

        # 이그니션과 글로리 윙 따로 사용하는 딜사이클
        ruleset.add_rule(InactiveRule("크리스탈 이그니션(시전)", "글로리 윙(진입)"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("크리스탈 이그니션(시전)", "소울 오브 크리스탈"), RuleSet.BASE)

        # 함께 사용하게 하려면 위 2개 주석처리하고 아래 2개 Rule을 사용
        # ruleset.add_rule(ConcurrentRunRule("크리스탈 이그니션(시전)", "글로리 윙(진입)"), RuleSet.BASE)
        # ruleset.add_rule(ConditionRule("글로리 윙(진입)", "크리스탈 이그니션(시전)", lambda x:x.is_cooltime_left(20000, 1) or x.is_cooltime_left(10000, -1)), RuleSet.BASE)
        return ruleset
        
    def get_passive_skill_list(self):
        vEhc = self.vEhc
        # 앱솔 무기 마력 241
        WEAPON_ATT = jobutils.get_weapon_att("건틀렛")
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
        FastCharge = core.BuffSkill("패스트 차지", 30, 10000, cooltime = 120000, rem=True).wrap(core.BuffSkillWrapper)
        WraithOfGod = core.BuffSkill("레이스 오브 갓", 0, 60000, pdamage = 10, cooltime = 120000).wrap(core.BuffSkillWrapper)
        
        Craft_Orb = core.DamageSkill("크래프트:오브", 390, 300, 1).wrap(core.DamageSkillWrapper)
        Reaction_Domination = core.DamageSkill("리액션:도미네이션", 0, 550, 2, cooltime = 4000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        Craft_Javelin_EnhanceBuff = core.BuffSkill("크래프트:오브(자벨린 강화버프)", 0, 2000, cooltime = -1).wrap(core.BuffSkillWrapper)
        
        Craft_Javelin = core.DamageSkill("크래프트:자벨린", 390, 375, 4 * 3, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Craft_Javelin_AfterOrb = core.DamageSkill("크래프트:자벨린(오브 이후)", 390, 375, 4 * 3, modifier = core.CharacterModifier(pdamage = 20 + 15, boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        
        Craft_Javelin_Fragment = core.DamageSkill("크래프트:자벨린(파편)", 0, 130, 2 * 3, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Reaction_Destruction = core.DamageSkill("리액션:디스트럭션", 0, 550, 4*2, modifier = core.CharacterModifier(boss_pdamage = 20), cooltime = 4000).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        Craft_Longinus = core.DamageSkill("크래프트:롱기누스", 600+180, 950, 8, cooltime = 15000).wrap(core.DamageSkillWrapper) # 자체딜레이 600 + 자벨린-오브 연계 취소 180
        
        Riyo = RiyoWrapper(core.SummonSkill("리요", 0, 510, 240, 1, 180000).setV(vEhc, 3, 2, False)) # 최초 사용 이후로는 항상 데우스 종료때 딜레이 없이 리필됨
        Machina = core.SummonSkill("마키나", 0, 1980, 250, 4, 180000).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper)    # 최초 사용 이후로는 항상 데우스 종료때 딜레이 없이 리필됨
        
        CrystalSkill_MortalSwing = core.DamageSkill("크리스탈 스킬:모탈스윙", 0, 600, 10, cooltime = -1).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)    #30
        CrystalSkill_Deus = core.SummonSkill("크리스탈 스킬:데우스", 30, 4800, 500, 5+1, 30*1000, cooltime = -1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)   #90, 7타
        CrystalSkill_Deus_Satelite = RiyoWrapper(core.SummonSkill("크리스탈 스킬:데우스(위성)", 0, 510, 240, 1+1, 30*1000, cooltime = -1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 3, 2, False))
        
        LonginusZone = core.DamageSkill("롱기누스 존", 690, 1500, 12, cooltime = 180*1000)    #안씀
        
        BlessMark = core.BuffSkill("블레스 마크", 0, 99999999, att = 46).wrap(core.BuffSkillWrapper)
        CurseMark = core.BuffSkill("커스 마크", 0, 99999999, armor_ignore = 20).wrap(core.BuffSkillWrapper)
        CurseMarkFinalAttack = core.DamageSkill("커스 마크(추가타)", 0, 200, 1).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        
        #글로리 윙
        GloryWingStackSkill = core.BuffSkill("글로리 윙(스택)", 0, 9999999)
        
        GloryWingUse = core.BuffSkill("글로리 윙(진입)", 30, 20000, pdamage_indep = 25, pdamage = (vEhc.getV(1,0) + 5) * 2, boss_pdamage = 30, cooltime = -1).wrap(core.BuffSkillWrapper) # 소오크 2개에 항상 맞춰 사용
        
        GloryWing_MortalWingbit = core.DamageSkill("글로리 윙:모탈 윙비트", 630, 2000, 8, cooltime = -1).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)  #1회
        
        GloryWing_Craft_Javelin = core.DamageSkill("글로리 윙:자벨린", 420, 465, 7, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, pdamage_indep = 40)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        GloryWing_Craft_Javelin_Fragment = core.DamageSkill("글로리 윙:자벨린(매직 미사일)", 0, 250, 3*3, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)

        #5차 스킬들
        OverloadMana = magicians.OverloadManaWrapper(vEhc, 0, 3)
        GramHolder = GramHolderWrapper(core.SummonSkill("그람홀더", 0, 3000, 1000+25*vEhc.getV(4,3), 6, 40000, cooltime = 180000).isV(vEhc,4,3)) # 클라 딜레이 없음
        
        MagicCircuitFullDrive = core.BuffSkill("매직 서킷 풀드라이브", 720, (30+vEhc.getV(3,2))*1000, pdamage = (20 + vEhc.getV(3,2)), cooltime = 200*1000).isV(vEhc,3,2).wrap(core.BuffSkillWrapper)
        MagicCircuitFullDriveStorm = core.SummonSkill("매직 서킷 풀드라이브(마력 폭풍)", 0, 4000, 500+20*vEhc.getV(3,2), 3, (30+vEhc.getV(3,2))*1000, cooltime = -1).wrap(core.SummonSkillWrapper)
        
        CrystalIgnitionInit = core.DamageSkill("크리스탈 이그니션(시전)", 720, 0, 0, cooltime = 180*1000).wrap(core.DamageSkillWrapper)
        CrystalIgnition = core.DamageSkill("크리스탈 이그니션", 150, 750 + 30*vEhc.getV(2,1), 4, modifier = core.CharacterModifier(boss_pdamage = 20)).isV(vEhc,2,1).wrap(core.DamageSkillWrapper)
        CrystalIgnitionEnd = core.DamageSkill("크리스탈 이그니션(종료)", 630, 0, 0, cooltime = -1).wrap(core.DamageSkillWrapper)
        Reaction_Spectrum = core.DamageSkill("리액션:스펙트럼", 0, 1000+40*vEhc.getV(2,1), 5, cooltime = 1000, modifier = core.CharacterModifier(boss_pdamage = 20)).wrap(core.DamageSkillWrapper) #1초마다 시전됨.
 
        SoulOfCrystal = SoulOfCrystalWrapper(core.BuffSkill("소울 오브 크리스탈", 510*2, 30*1000, cooltime=40*1000).isV(vEhc,1,0))
        SoulOfCrystalPassive = core.BuffSkill("소울 오브 크리스탈(패시브)", 0, 999999999, att = (5+vEhc.getV(1,0)*2)).isV(vEhc,1,0).wrap(core.BuffSkillWrapper)

        SoulOfCrystal_Reaction_Domination = core.DamageSkill("리액션:도미네이션(소오크)", 0, 550 * 0.01 * (50 + vEhc.getV(1,0)), 2*2).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        SoulOfCrystal_Reaction_Destruction = core.DamageSkill("리액션:디스트럭션(소오크)", 0, 550 * 0.01 * (50 + vEhc.getV(1,0)), 4*2*2, modifier = core.CharacterModifier(boss_pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        SoulOfCrystal_Reaction_Spectrum = core.DamageSkill("리액션:스펙트럼(소오크)", 0, 1000+40*vEhc.getV(2,1), 5*2, modifier = core.CharacterModifier(boss_pdamage = 20)).wrap(core.DamageSkillWrapper)
        
        #스킬간 연결

        Reaction_Destruction_Link = core.OptionalElement(SoulOfCrystal.is_active, SoulOfCrystal_Reaction_Destruction, name = "리액션:디스트럭션(소오크여부)")
        Reaction_Domination_Link = core.OptionalElement(SoulOfCrystal.is_active, SoulOfCrystal_Reaction_Domination, name = "리액션:도미네이션(소오크여부)")
        Reaction_Spectrum_Link = core.OptionalElement(SoulOfCrystal.is_active, SoulOfCrystal_Reaction_Spectrum, name = "리액션:스펙트럼(소오크여부)")
        
        Reaction_Destruction.onAfter(Reaction_Destruction_Link)
        Reaction_Domination.onAfter(Reaction_Domination_Link)
        Reaction_Spectrum.onAfter(Reaction_Spectrum_Link)
                
        Reaction_Domination_Trigger = core.OptionalElement(lambda:Reaction_Domination.available, Reaction_Domination, name = "리액션:도미네이션")
        Reaction_Destruction_Trigger = core.OptionalElement(lambda:Reaction_Destruction.available, Reaction_Destruction, name = "리액션:디스트럭션")
        Reaction_Spectrum_Trigger = core.OptionalElement(lambda:Reaction_Spectrum.available, Reaction_Spectrum, name = "리액션:스펙트럼")
        
        Craft_Orb.onAfter(Reaction_Domination_Trigger)
        Craft_Javelin.onAfter(Reaction_Destruction_Trigger)
        Craft_Javelin.onAfter(Craft_Javelin_Fragment)
        
        Craft_Javelin_AfterOrb.onAfter(Reaction_Destruction_Trigger)
        Craft_Javelin_AfterOrb.onAfter(Craft_Javelin_Fragment)        
        
        GloryWing_Craft_Javelin.onAfter(GloryWing_Craft_Javelin_Fragment)
        
        CrystalIgnitionRepeat = core.RepeatElement(CrystalIgnition, 62)
        CrystalIgnitionInit.onAfter(CrystalIgnitionRepeat)
        CrystalIgnitionRepeat.onAfter(CrystalIgnitionEnd)
        CrystalIgnition.onAfter(Reaction_Spectrum_Trigger)

        CrystalSkill_Deus.onAfter(CrystalSkill_Deus_Satelite)
        CrystalSkill_Deus.onAfter(Riyo.controller(30000, type_="set_disabled_and_time_left"))
        CrystalSkill_Deus.onAfter(Machina.controller(30000, type_="set_disabled_and_time_left"))
        
        MagicCircuitFullDrive.onAfter(MagicCircuitFullDriveStorm)
        
        #자벨린 이후 바로 오브를 시전합니다.
        Craft_Javelin.onAfter(Craft_Orb)
        Craft_Javelin_AfterOrb.onAfter(Craft_Orb)

        #스택 연결
        CrystalCharge = IliumStackWrapper(GloryWingStackSkill, 160, FastCharge, GloryWingUse.is_active ,name = "크리스탈 차지")
        CrystalCharge.addTrigger(CrystalSkill_MortalSwing.controller(1), 30)
        CrystalCharge.addTrigger(CrystalSkill_Deus.controller(1), 90)
        CrystalCharge.addTrigger(GloryWingUse.controller(1), 150, isLast = True)

        GloryWingUse.onConstraint(core.ConstraintElement("소오크 가동중", SoulOfCrystal, SoulOfCrystal.is_active))
        GloryWingUse.onAfter(SoulOfCrystal.turnOffController())
        
        SoulOfCrystal.onConstraint(core.ConstraintElement("글로리윙 미사용중", GloryWingUse, GloryWingUse.is_not_active))
        Machina.onConstraint(core.ConstraintElement("글로리윙 미사용중", GloryWingUse, GloryWingUse.is_not_active))

        GramHolder.registerCrystalCharge(CrystalCharge)
        GramHolder.registerGloryWing(GloryWingUse)
        
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
        Reaction_Spectrum.protect_from_running()

        return(BasicAttackWrapper,
                [SoulOfCrystalPassive, globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    Booster, FastCharge, WraithOfGod, MagicCircuitFullDrive, SoulOfCrystal,
                    Craft_Javelin_EnhanceBuff, CrystalCharge, GloryWingUse,
                    OverloadMana, BlessMark, CurseMark,
                    globalSkill.soul_contract()] +\
                [CrystalSkill_MortalSwing, GloryWing_MortalWingbit, CrystalIgnitionInit] +\
                [Riyo, Machina, CrystalSkill_Deus, CrystalSkill_Deus_Satelite,
                    GramHolder, MagicCircuitFullDriveStorm] +\
                [Reaction_Domination, Reaction_Destruction, Reaction_Spectrum] +\
                [BasicAttackWrapper])