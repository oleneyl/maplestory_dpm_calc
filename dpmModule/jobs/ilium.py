from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, MutualRule, InactiveRule, ConcurrentRunRule, ReservationRule, ConditionRule
from . import globalSkill
from .jobbranch import magicians
from .jobclass import flora
from . import jobutils
from typing import Any, Dict

from localization.utilities import translator
_ = translator.gettext

# English skill information for Illium here https://maplestory.fandom.com/wiki/Illium/Skills
class IlliumSkills:
    # Link SKill
    TideofBattle = _("전투의 흐름")  # "Tide of Battle"
    # Beginner
    MagicConversion = _("매직 서킷")  # "Magic Conversion"
    ExclusiveSpell = _("익스클루시브 스펠")  # "Exclusive Spell"
    # 1st Job
    RadiantJavelin = _("크래프트:자벨린")  # "Radiant Javelin"
    RadiantOrb = _("크래프트:오브")  # "Radiant Orb"
    Ex = _("리요")  # "Ex"
    CrystallineWings = _("크리스탈 포탈")  # "Crystalline Wings"
    LucentGauntletMastery = _("매직 건틀렛 마스터리")  # "Lucent Gauntlet Mastery"
    LucentBrand = _("블레스 마크")  # "Lucent Brand"
    # 2nd Job
    CrystalBattery = _("크리스탈 차지")  # "Crystal Battery"
    DeployCrystal = _("크리스탈 컨트롤")  # "Deploy Crystal"
    ReactionDestruction = _("리액션:디스트럭션")  # "Reaction - Destruction"
    ReactionDomination = _("리액션:도미네이션")  # "Reaction - Domination"
    CrystalSkillVortexofLight = _("크리스탈 스킬:모탈스윙")  # "Crystal Skill - Vortex of Light"
    GauntletFrenzy = _("매직 건틀렛 부스터")  # "Gauntlet Frenzy"
    Machina = _("마키나")  # "Machina"
    AegisofLight = _("디바인 실드")  # "Aegis of Light"
    UmbralBrand = _("커스 마크")  # "Umbral Brand"
    # 3rd Job
    CrystalBatteryII = _("크리스탈 차지 숙련")  # "Crystal Battery II"
    ReactionDestructionII = _("리액션:디스트럭션II")  # "Reaction - Destruction II"
    ReactionDominationII = _("리액션:도미네이션II")  # "Reaction - Domination II"
    CrystalSkillWingsofGlory = _("크리스탈 스킬:글로리 윙")  # "Crystal Skill - Wings of Glory"
    CrystalSkillResonance = _("크리스탈 스킬:하모니 링크")  # "Crystal Skill - Resonance"
    LucentBrandII = _("블레스 마크 숙련")  # "Lucent Brand II"
    UmbralBrandII = _("커스 마크 숙련")  # "Umbral Brand II"
    MightoftheFlora = _("레프 마스터리")  # "Might of the Flora"
    Tenacity = _("운명 개척")  # "Tenacity"
    EndlessResearch = _("끊임없는 연구")  # "Endless Research"
    # 4th Job
    CrystalBatteryIII = _("크리스탈 차지 완성")  # "Crystal Battery III"
    RadiantJavelinII = _("크래프트:자벨린II")  # "Radiant Javelin II"
    RadiantOrbII = _("크래프트:오브II")  # "Radiant Orb II"
    LonginusSpear = _("크래프트:롱기누스")  # "Longinus Spear"
    CrystalSkillDeus = _("크리스탈 스킬:데우스")  # "Crystal Skill - Deus"
    VortexWings = _("글로리 윙:모탈 윙비트")  # "Vortex Wings"
    ResonantWings = _("글로리 윙:하모니 윙비트")  # "Resonant Wings"
    HerooftheFlora = _("레프 용사의 의지")  # "Hero of the Flora"
    FlashCrystalBattery = _("패스트 차지")  # "Flash Crystal Battery"
    LucentBrandIII = _("블레스 마크 완성")  # "Lucent Brand III"
    UmbralBrandIII = _("커스 마크 완성")  # "Umbral Brand III"
    WisdomoftheCrystal = _("크리스탈의 비밀")  # "Wisdom of the Crystal"
    # Hypers
    CrystallineBulwark = _("프라이멀 프로텍션")  # "Crystalline Bulwark"
    LonginusZone = _("롱기누스 존")  # "Longinus Zone"
    DivineWrath = _("레이스 오브 갓")  # "Divine Wrath"
    # 5th Job
    CrystalIgnition = _("크리스탈 이그니션")  # "Crystal Ignition"
    ReactionSpectralBlast = _("리액션:스펙트럼")  # "Reaction - Spectral Blast"
    TemplarKnight = _("그람홀더")  # "Templar Knight"
    CrystallineSpirit = _("소울 오브 크리스탈")  # "Crystalline Spirit"
    CrystalGate = _("크리스탈 게이트")  # "Crystal Gate"


class IliumStackWrapper(core.StackSkillWrapper):
    def __init__(self, skill, _max, fastChargeJudge, stopJudge, name = None):
        super().__init__(skill, _max, name = name)
        self.triggers = []
        self.fastChargeJudge = fastChargeJudge
        self.stopJudge = stopJudge

    def addTrigger(self, skill, stack, isLast = False):
        self.triggers.append({"skill" : skill, "stack" : stack, "state" : False, "isLast" : isLast})
    
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
            if (trigger["stack"] <= self.stack) and (not trigger["state"]):
                trigger["skill"].set_disabled_and_time_left(1)
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
        return self._result_object_cache

    def turnOffController(self):
        task = core.Task(self, self.turnOff)
        return core.TaskHolder(task, name = _("소오크 흡수"))

class RiyoWrapper(core.SummonSkillWrapper):
    """
    Stage 1: Attack with 60% damage, increase attack power when attacking 10 times
    Step 2: Attack with 100% damage, increase attack power when attacking 10 times
    Step 3: Attack with 200% damage, reset after attacking 20 times
    Crystal Skill: Deus' Passive Damage +100%p

    1단계:60%의 데미지로 공격, 10회 공격 시 공격력 강화
    2단계:100%의 데미지로 공격, 10회 공격 시 공격력 강화
    3단계:200%의 데미지로 공격, 20회 공격 시 초기화
    크리스탈 스킬: 데우스의 패시브로 각 단계의 데미지 +100%p
    """
    def __init__(self, skill):
        super(RiyoWrapper, self).__init__(skill)
        self.count = 0

    def _use(self, skill_modifier):
        self.count = 0
        return super(RiyoWrapper, self)._use(skill_modifier)
    
    def _useTick(self):
        result = super(RiyoWrapper, self)._useTick()
        self.count += 1
        if self.count >= 40:
            self.count = 0
        return result

    def get_damage(self) -> float:
        if self.count < 10:
            return 160
        elif self.count < 20:
            return 200
        else:
            return 300

class GramHolderWrapper(core.SummonSkillWrapper):
    """
    When preparing to attack, if the Crystal Charge is 3 or more charged or in Glory Wing, the final damage is doubled

    공격 준비 중 크리스탈 차지가 3 이상 충전되거나 글로리 윙 상태라면 최종 데미지 2배로 증가
    """
    def __init__(self, skill):
        self.chargeBefore = 0
        self.crystalCharge: IliumStackWrapper = None
        self.gloryWing = None
        super(GramHolderWrapper, self).__init__(skill)
    
    def registerCrystalCharge(self, skill: IliumStackWrapper):
        self.crystalCharge = skill

    def registerGloryWing(self, skill):
        self.gloryWing = skill
    
    def _useTick(self):
        result = super(GramHolderWrapper, self)._useTick()
        self.chargeBefore = self.crystalCharge.stack
        return result
    
    def get_modifier(self) -> core.CharacterModifier:
        modifier = super(GramHolderWrapper, self).get_modifier()
        if self.gloryWing.is_active() or self.crystalCharge.judge(self.chargeBefore + 3, 1):
            modifier = modifier + core.CharacterModifier(pdamage_indep=100)
        return modifier
    
class JobGenerator(ck.JobGenerator):
    def __init__(self, vEhc = None):
        super(JobGenerator, self).__init__(vEhc = vEhc)
        self.jobtype = "INT"
        self.jobname = _("일리움")
        self.vEnhanceNum = 12
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1
        self.combat = 0

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(MutualRule(IlliumSkills.FlashCrystalBattery, _("{}(시전)").format(IlliumSkills.CrystalIgnition)), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(IlliumSkills.FlashCrystalBattery, _("{}(진입)").format(IlliumSkills.CrystalSkillWingsofGlory)), RuleSet.BASE)
        ruleset.add_rule(ReservationRule(IlliumSkills.TemplarKnight, _("{}(진입)").format(IlliumSkills.CrystalSkillWingsofGlory)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(_("{}(진입)").format(IlliumSkills.CrystalSkillWingsofGlory), IlliumSkills.TemplarKnight, lambda x:x.is_active() or x.is_not_usable()), RuleSet.BASE)
        ruleset.add_rule(ReservationRule(IlliumSkills.CrystalSkillDeus, _("{}(진입)").format(IlliumSkills.CrystalSkillWingsofGlory)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(_("{}(진입)").format(IlliumSkills.CrystalSkillWingsofGlory), IlliumSkills.CrystalSkillDeus, lambda x:x.is_active() or x.is_not_usable()), RuleSet.BASE)

        # A damage cycle that uses Ignition and Glory Wings separately. 이그니션과 글로리 윙 따로 사용하는 딜사이클.
        ruleset.add_rule(InactiveRule(_("{}(시전)").format(IlliumSkills.CrystalIgnition), _("{}(진입)").format(IlliumSkills.CrystalSkillWingsofGlory)), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(_("{}(시전)").format(IlliumSkills.CrystalIgnition), IlliumSkills.CrystallineSpirit), RuleSet.BASE)

        # To use together, comment out the above 2 and use the below 2 rules. 함께 사용하게 하려면 위 2개 주석처리하고 아래 2개 Rule을 사용
        # ruleset.add_rule(ConcurrentRunRule(_("{IlliumSkills.CrystalIgnition}(시전)", _("{IlliumSkills.CrystalSkillWingsofGlory}(진입)"), RuleSet.BASE)
        # ruleset.add_rule(ConditionRule(_("{IlliumSkills.CrystalSkillWingsofGlory}(진입)", _("{IlliumSkills.CrystalIgnition}(시전)", lambda x:x.is_cooltime_left(20000, 1) or x.is_cooltime_left(10000, -1)), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self) -> core.CharacterModifier:
        return core.CharacterModifier(boss_pdamage=106, armor_ignore=-5.4)
        
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        # Absolab weapon magic attack 241. 앱솔 무기 마력 241.
        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        MagicCircuit = core.InformedCharacterModifier(IlliumSkills.MagicConversion, att = WEAPON_ATT*0.2)
        
        MagicGuntletMastery = core.InformedCharacterModifier(IlliumSkills.LucentGauntletMastery, crit = 20)
        BlessMarkPassive = core.InformedCharacterModifier(_("{}(패시브)").format(IlliumSkills.LucentBrand), pdamage = 10)
        LefMastery = core.InformedCharacterModifier(IlliumSkills.MightoftheFlora, pdamage = 10)
        
        DestinyPioneer = core.InformedCharacterModifier(IlliumSkills.Tenacity, stat_main = 40, patt = 10)
        ContinualResearch = core.InformedCharacterModifier(IlliumSkills.EndlessResearch, att = 50, crit = 20, crit_damage = 30)
        CrystalSecret = core.InformedCharacterModifier(IlliumSkills.WisdomoftheCrystal, boss_pdamage = 30, pdamage_indep = 35, armor_ignore = 25)
        
        return [MagicCircuit, MagicGuntletMastery, BlessMarkPassive,
            LefMastery, DestinyPioneer, ContinualResearch, CrystalSecret ]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90)
        
        return [WeaponConstant, Mastery]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Hyper: Javelin- Boss Killer, Reinforcement, Bonus Attack

        Minion enhancement not yet applied

        하이퍼 : 자벨린- 보스킬러, 리인포스, 보너스 어택
        
        소환수 강화 아직 미적용
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        #Buff skills
        Booster = core.BuffSkill(IlliumSkills.GauntletFrenzy, 0, 200*1000).wrap(core.BuffSkillWrapper)
        FastCharge = core.BuffSkill(IlliumSkills.FlashCrystalBattery, 30, 10000, cooltime = (120-5*self.combat)*1000, rem=True).wrap(core.BuffSkillWrapper)
        WraithOfGod = core.BuffSkill(IlliumSkills.DivineWrath, 0, 60000, pdamage = 10, cooltime = 120000).wrap(core.BuffSkillWrapper)

        Craft_Orb = core.DamageSkill(IlliumSkills.RadiantOrb, 390, 300+4*self.combat, 1).wrap(core.DamageSkillWrapper)
        Reaction_Domination = core.DamageSkill(IlliumSkills.ReactionDomination, 0, 550 + 100 + self.combat*2, 2, cooltime = 4000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        Craft_Javelin_EnhanceBuff = core.BuffSkill(_("{}(자벨린 강화버프)").format(IlliumSkills.RadiantOrb), 0, 2000, cooltime = -1).wrap(core.BuffSkillWrapper)
        
        Craft_Javelin = core.DamageSkill(IlliumSkills.RadiantJavelin, 390, 375 + 2*self.combat, 4 * 3, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Craft_Javelin_AfterOrb = core.DamageSkill(_("{}(오브 이후)").format(IlliumSkills.RadiantJavelin), 390, 375 + 2*self.combat, 4 * 3, modifier = core.CharacterModifier(pdamage = 20 + 15, boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        
        Craft_Javelin_Fragment = core.DamageSkill(_("{}(파편)").format(IlliumSkills.RadiantJavelin), 0, 130 + 2*self.combat, 2 * 3, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Reaction_Destruction = core.DamageSkill(IlliumSkills.ReactionDestruction, 0, 550 + 100 + self.combat*2, 4*2, modifier = core.CharacterModifier(boss_pdamage = 20), cooltime = 4000).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        Craft_Longinus = core.DamageSkill(IlliumSkills.LonginusSpear, 600+180 +10*self.combat, 950, 8, cooltime = (15-self.combat//2)*1000).wrap(core.DamageSkillWrapper)  # Self-delay 600 + Javelin-of link cancellation 180. 자체딜레이 600 + 자벨린-오브 연계 취소 180.
        
        Riyo = RiyoWrapper(core.SummonSkill(IlliumSkills.Ex, 0, 510, 240, 1, 180000).setV(vEhc, 3, 2, False))  # After initial use, it is always refilled without delay at the end of deus. 최초 사용 이후로는 항상 데우스 종료때 딜레이 없이 리필됨.
        Machina = core.SummonSkill(IlliumSkills.Machina, 0, 1980, 250, 4, 180000).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper)    # After initial use, it is always refilled without delay at the end of deus. 최초 사용 이후로는 항상 데우스 종료때 딜레이 없이 리필됨.
        
        CrystalSkill_MortalSwing = core.DamageSkill(IlliumSkills.CrystalSkillVortexofLight, 0, 600 + 2* passive_level, 10, cooltime = -1).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)    #30
        # Deus Passive Riyo Demjeung does not apply to combat. 데우스 패시브 리요 뎀증은 컴뱃 미적용.
        CrystalSkill_Deus = core.SummonSkill(IlliumSkills.CrystalSkillDeus, 30, 4800, 500+4*self.combat, 5+1, (30+self.combat//3)*1000, cooltime = -1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 3, 2, False).wrap(core.SummonSkillWrapper)   #90, 7타
        CrystalSkill_Deus_Satelite = RiyoWrapper(core.SummonSkill(_("{}(위성)").format(IlliumSkills.CrystalSkillDeus), 0, 510, 240, 1+1, 30*1000, cooltime = -1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 3, 2, False))
                
        BlessMark = core.BuffSkill(IlliumSkills.LucentBrand, 0, 99999999, att = 46).wrap(core.BuffSkillWrapper)
        CurseMark = core.BuffSkill(IlliumSkills.UmbralBrand, 0, 99999999, armor_ignore = 20).wrap(core.BuffSkillWrapper)
        CurseMarkFinalAttack = core.DamageSkill(_("{}(추가타)").format(IlliumSkills.UmbralBrand), 0, 200, 1).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        
        # Glory Wing. 글로리 윙.
        GloryWingStackSkill = core.BuffSkill(_("{}(스택)").format(IlliumSkills.CrystalSkillWingsofGlory), 0, 9999999)
        
        GloryWingUse = core.BuffSkill(_("{}(진입)").format(IlliumSkills.CrystalSkillWingsofGlory), 30, 20000, pdamage_indep = 25, pdamage = (vEhc.getV(1,0) + 5) * 2, boss_pdamage = 30, cooltime = -1).wrap(core.BuffSkillWrapper)  # Always matched with 2 soaks. 소오크 2개에 항상 맞춰 사용.
        
        GloryWing_MortalWingbit = core.DamageSkill(IlliumSkills.VortexWings, 630, 1070 + 20*self.combat, 15, cooltime = -1).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)  # 1 time. 1회.
        
        GloryWing_Craft_Javelin = core.DamageSkill(f"{IlliumSkills.CrystalSkillWingsofGlory}:{IlliumSkills.RadiantJavelin}", 420, 465 + 3*self.combat, 7, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, pdamage_indep = 40)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        GloryWing_Craft_Javelin_Fragment = core.DamageSkill(_("{}:{}(매직 미사일)").format(IlliumSkills.CrystalSkillWingsofGlory, IlliumSkills.RadiantJavelin), 0, 250 + 5*self.combat, 3*3, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)

        # 5th skills. 5차 스킬들.
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        FloraGoddessBless = flora.FloraGoddessBlessWrapper(vEhc, 0, 0, jobutils.get_weapon_att(chtr))
        GramHolder = GramHolderWrapper(core.SummonSkill(IlliumSkills.TemplarKnight, 210, 3000, 500+20*vEhc.getV(4,3), 12, 40000, cooltime = 180000).isV(vEhc,4,3))

        CrystalIgnitionInit = core.DamageSkill(_("{}(시전)").format(IlliumSkills.CrystalIgnition), 720, 0, 0, cooltime = 180*1000).wrap(core.DamageSkillWrapper)
        CrystalIgnition = core.DamageSkill(IlliumSkills.CrystalIgnition, 150, 750 + 30*vEhc.getV(2,1), 4, modifier = core.CharacterModifier(boss_pdamage = 20)).isV(vEhc,2,1).wrap(core.DamageSkillWrapper)
        CrystalIgnitionEnd = core.DamageSkill(_("{}(종료)").format(IlliumSkills.CrystalIgnition), 630, 0, 0, cooltime = -1).wrap(core.DamageSkillWrapper)
        Reaction_Spectrum = core.DamageSkill(IlliumSkills.ReactionSpectralBlast, 0, 1000+40*vEhc.getV(2,1), 5, cooltime = 1000, modifier = core.CharacterModifier(boss_pdamage = 20)).wrap(core.DamageSkillWrapper)  # Cast every 1 second. 1초마다 시전됨.
 
        SoulOfCrystal = SoulOfCrystalWrapper(core.BuffSkill(IlliumSkills.CrystallineSpirit, 510*2, 30*1000, cooltime=40*1000).isV(vEhc,1,0))
        SoulOfCrystalPassive = core.BuffSkill(_("{}(패시브)").format(IlliumSkills.CrystallineSpirit), 0, 999999999, att = (5+vEhc.getV(1,0)*2)).isV(vEhc,1,0).wrap(core.BuffSkillWrapper)

        SoulOfCrystal_Reaction_Domination = core.DamageSkill(_("{}(소오크)").format(IlliumSkills.ReactionDomination), 0, (550 + 100 + self.combat*2) * 0.01 * (50 + vEhc.getV(1,0)), 2*2).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        SoulOfCrystal_Reaction_Destruction = core.DamageSkill(_("{}(소오크)").format(IlliumSkills.ReactionDestruction), 0, (550 + 100 + self.combat*2) * 0.01 * (50 + vEhc.getV(1,0)), 4*2*2, modifier = core.CharacterModifier(boss_pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        SoulOfCrystal_Reaction_Spectrum = core.DamageSkill(_("{}(소오크)").format(IlliumSkills.ReactionSpectralBlast), 0, 1000+40*vEhc.getV(2,1), 5*2, modifier = core.CharacterModifier(boss_pdamage = 20)).wrap(core.DamageSkillWrapper)

        CrystalGate = core.BuffSkill(IlliumSkills.CrystalGate, 420*2, (130+vEhc.getV(0,0))*1000, cooltime=180*1000, red=True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        CrystalGateBuff = core.BuffSkill(_("{}(버프)").format(IlliumSkills.CrystalGate), 0, 25000, att=5+2*vEhc.getV(0,0)).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        CrystalGateAttack = core.DamageSkill(_("{}(폭격)").format(IlliumSkills.CrystalGate), 0, 450+18*vEhc.getV(0,0), 5, cooltime=1500).wrap(core.DamageSkillWrapper)
        
        # Links between skills. 스킬간 연결.

        Reaction_Destruction_Link = core.OptionalElement(SoulOfCrystal.is_active, SoulOfCrystal_Reaction_Destruction, name=_("{}(소오크여부)").format(IlliumSkills.ReactionDestruction))
        Reaction_Domination_Link = core.OptionalElement(SoulOfCrystal.is_active, SoulOfCrystal_Reaction_Domination, name=_("{}(소오크여부)").format(IlliumSkills.ReactionDomination))
        Reaction_Spectrum_Link = core.OptionalElement(SoulOfCrystal.is_active, SoulOfCrystal_Reaction_Spectrum, name=_("{}(소오크여부)").format(IlliumSkills.ReactionSpectralBlast))
        
        Reaction_Destruction.onAfter(Reaction_Destruction_Link)
        Reaction_Domination.onAfter(Reaction_Domination_Link)
        Reaction_Spectrum.onAfter(Reaction_Spectrum_Link)
                
        Reaction_Domination_Trigger = core.OptionalElement(lambda:Reaction_Domination.is_available(), Reaction_Domination, name=IlliumSkills.ReactionDomination)
        Reaction_Destruction_Trigger = core.OptionalElement(lambda:Reaction_Destruction.is_available(), Reaction_Destruction, name=IlliumSkills.ReactionDestruction)
        Reaction_Spectrum_Trigger = core.OptionalElement(lambda:Reaction_Spectrum.is_available(), Reaction_Spectrum, name=IlliumSkills.ReactionSpectralBlast)
        
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
        
        magic_curcuit_full_drive_builder = flora.MagicCircuitFullDriveBuilder(vEhc, 3, 2)
        for sk in [Craft_Orb, Craft_Javelin, Craft_Javelin_AfterOrb, Craft_Longinus, CrystalSkill_MortalSwing, GloryWing_MortalWingbit, GloryWing_Craft_Javelin, CrystalIgnition, MirrorSpider]:
            magic_curcuit_full_drive_builder.add_trigger(sk)
        MagicCircuitFullDrive, MagicCircuitFullDriveStorm = magic_curcuit_full_drive_builder.get_skill()

        CrystalGate.onAfter(CrystalGateBuff)
        CrystalGateBuff.onConstraint(core.ConstraintElement(f"{IlliumSkills.CrystalGate} ON", CrystalGate, CrystalGate.is_active))
        CrystalGateBuff.prevent_from_caching()

        UseCrystalGateAttack = core.OptionalElement(lambda: CrystalGate.is_active() and CrystalGateAttack.is_available(), CrystalGateAttack, name=_("폭격 조건 체크"))
        for sk in [Craft_Javelin, Craft_Javelin_AfterOrb, Craft_Orb, Craft_Longinus,
                    GloryWing_Craft_Javelin, GloryWing_MortalWingbit, CrystalSkill_MortalSwing, CrystalIgnition]:
            sk.onAfter(UseCrystalGateAttack)
        CrystalGateAttack.protect_from_running()
        
        # Orb is cast right after Javelin. 자벨린 이후 바로 오브를 시전합니다.
        Craft_Javelin.onAfter(Craft_Orb)
        Craft_Javelin_AfterOrb.onAfter(Craft_Orb)

        # Stack connection. 스택 연결.
        CrystalCharge = IliumStackWrapper(GloryWingStackSkill, 160, FastCharge, GloryWingUse.is_active, name=IlliumSkills.CrystalBattery)
        CrystalCharge.addTrigger(CrystalSkill_MortalSwing, 30)
        CrystalCharge.addTrigger(CrystalSkill_Deus, 90)
        CrystalCharge.addTrigger(GloryWingUse, 150, isLast = True)

        GloryWingUse.onConstraint(core.ConstraintElement(_("소오크 가동중"), SoulOfCrystal, SoulOfCrystal.is_active))
        GloryWingUse.onAfter(SoulOfCrystal.turnOffController())
        
        SoulOfCrystal.onConstraint(core.ConstraintElement(_("글로리윙 미사용중"), GloryWingUse, GloryWingUse.is_not_active))
        Machina.onConstraint(core.ConstraintElement(_("글로리윙 미사용중"), GloryWingUse, GloryWingUse.is_not_active))

        GramHolder.registerCrystalCharge(CrystalCharge)
        GramHolder.registerGloryWing(GloryWingUse)
        
        # Basic attack settings. 기본공격 설정.
        BasicAttack = core.OptionalElement(GloryWingUse.is_active, GloryWing_Craft_Javelin, Craft_Javelin_AfterOrb, name = _("기본공격(글로리 윙 여부 판단)"))
        BasicAttackWrapper = core.DamageSkill(_("기본 공격"), 0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)
        # Customs Mark Final Attack. 커스마크 파이널어택.
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

        # Mana Overload
        overload_mana_builder = magicians.OverloadManaBuilder(vEhc, 0, 3)
        for sk in [Riyo, Machina, CrystalSkill_MortalSwing, GloryWing_MortalWingbit, CrystalSkill_Deus, CrystalSkill_Deus_Satelite,
                    Craft_Javelin, Craft_Javelin_AfterOrb, Craft_Javelin_Fragment, Craft_Orb, Craft_Longinus, Reaction_Destruction,
                    SoulOfCrystal_Reaction_Destruction, Reaction_Domination, SoulOfCrystal_Reaction_Domination,
                    CrystalIgnition, Reaction_Spectrum, SoulOfCrystal_Reaction_Spectrum, GramHolder, GloryWing_Craft_Javelin]:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()

        return(BasicAttackWrapper,
                [SoulOfCrystalPassive, globalSkill.maple_heros(chtr.level, name = IlliumSkills.HerooftheFlora, combat_level=0), globalSkill.useful_sharp_eyes(),
                    Booster, FastCharge, WraithOfGod, MagicCircuitFullDrive, FloraGoddessBless, SoulOfCrystal,
                    Craft_Javelin_EnhanceBuff, CrystalCharge, GloryWingUse,
                    OverloadMana, BlessMark, CurseMark, CrystalGate, CrystalGateBuff,
                    globalSkill.soul_contract()] +\
                [CrystalSkill_MortalSwing, GloryWing_MortalWingbit, CrystalIgnitionInit, MirrorBreak, MirrorSpider] +\
                [Riyo, Machina, CrystalSkill_Deus, CrystalSkill_Deus_Satelite,
                    GramHolder, MagicCircuitFullDriveStorm, CrystalGateAttack] +\
                [Reaction_Domination, Reaction_Destruction, Reaction_Spectrum] +\
                [BasicAttackWrapper])