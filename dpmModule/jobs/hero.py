import gettext
_ = gettext.gettext

from .globalSkill import GlobalSkills
from ..kernel import core
from ..character import characterKernel as ck
from functools import partial

from ..status.ability import Ability_tool
from ..execution.rules import ConcurrentRunRule, ReservationRule, RuleSet, InactiveRule
from . import globalSkill, jobutils
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict

'''
Hero skill summary
-Combo Attack: 2 Attack Power per Stack, 10% Final Damage -> 11% Order +2% (Hyper) Bogong +2%
-Anger (ball 30)
-Weapon Mastery (Final Dem 10 + Ax Dem 5%)
-Physical training (major/minor stats 30)
-Chance Attack (Creat 20, Dempeng 25 in case of abnormal condition)
-Inlay (25 final dem, 20 dem last)
-Combat Mastery (Bangmu 50)
-Fish (30 blank), 75% (applied hyper +15)
-Level +20%, At-bats +1

히어로 스킬 정리
- 콤보 어택 :: 스택당 공격력 2, 최종뎀10% -> 오더 11% +2%(하이퍼) 보공+2%
- 분노(공30)
- 웨폰 마스터리 (최종뎀 10 + 도끼 뎀5%)
- 피지컬 트레이닝 (주/부 스텟 30)
- 찬스 어택 (크리율 20, 상태이상시 뎀뻥25)
- 인레이지 (최종뎀25, 크뎀 20)
- 컴뱃 마스터리 (방무 50)
- 어파 (공30), 75%(하이퍼적용+15)
- 레블 +20%, 타수+1
'''


# English skill information for Hero here https://maplestory.fandom.com/wiki/Hero/Skills
class HeroSkills:
    # 1st Job
    SlashBlast = _("슬래시 블러스트")  # "Slash Blast"
    WarLeap = _("워리어 리프")  # "War Leap"
    LeapAttack = _("리프 어택")  # "Leap Attack"
    # 2nd Job
    Brandish = _("브랜디쉬")  # "Brandish"
    ComboFury = _("콤보 포스")  # "Combo Fury"
    ComboAttack = _("콤보 어택")  # "Combo Attack"
    WeaponBooster = _("웨폰 부스터")  # "Weapon Booster"
    Rage = "분노"  # "Rage"
    WeaponMastery = _("웨폰 마스터리")  # "Weapon Mastery"
    FinalAttack = _("파이널 어택")  # "Final Attack"
    PhysicalTraining = _("피지컬 트레이닝")  # "Physical Training"
    # 3rd Job
    Panic = _("패닉 ")  # "Panic"
    Rush = _("돌진")  # "Rush"
    IntrepidSlash = _("브레이브 슬래시")  # "Intrepid Slash"
    Shout = "샤우트"  # "Shout"
    UpwardCharge = _("어퍼 차지")  # "Upward Charge"
    ComboSynergy = _("콤보 시너지")  # "Combo Synergy"
    ChanceAttack = _("찬스 어택")  # "Chance Attack"
    # 4th Job
    RagingBlow = _("레이징 블로우")  # "Raging Blow"
    Puncture = _("인사이징")  # "Puncture"
    MagicCrash = _("매직 크래쉬")  # "Magic Crash"
    PowerStance = _("스탠스")  # "Power Stance"
    Enrage = _("인레이지")  # "Enrage"
    AdvancedCombo = _("어드밴스드 콤보")  # "Advanced Combo"
    CombatMastery = _("컴뱃 마스터리")  # "Combat Mastery"
    AdvancedFinalAttack = _("어드밴스드 파이널 어택")  # "Advanced Final Attack"
    # Hypers
    RisingRage = _("레이지 업라이징")  # "Rising Rage"
    EpicAdventure = _("에픽 어드벤처")  # "Epic Adventure"
    CryValhalla = _("발할라")  # "Cry Valhalla"
    # 5th Job
    SwordIllusion = _("소드 일루전")  # "Sword Illusion"
    InstinctualCombo = _("콤보 인스팅트")  # "Instinctual Combo"
    Worldreaver = _("콤보 데스폴트")  # "Worldreaver"
    BurningSoulBlade = _("소드 오브 버닝 소울")  # "Burning Soul Blade"


#ComboAttack
class ComboAttackWrapper(core.StackSkillWrapper):
    def __init__(self, skill, deathfault_buff, vEhc, combat):
        super(ComboAttackWrapper, self).__init__(skill, 10)
        self.deathfault_buff = deathfault_buff
        self.vEhc = vEhc
        self.combat = combat
        self.stack = 10  #Better point!
        self.tick = 12 + ceil(self.combat / 6)
        self.instinct = False
        self.set_name_style(_("%d 만큼 콤보 변화"))
    
    def toggle(self, state):
        self.instinct = state
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname = self.skill.name, spec = 'graph control')
        
    def toggleController(self, state):
        task = core.Task(self, partial(self.toggle, state))
        return core.TaskHolder(task, name = _("인스팅트 토글"))
        
    def vary(self, diff):
        if diff > 0:
            chance = 0.8 - self.instinct * 0.5
            chanceDouble = chance * (0.8+0.02*self.combat)
            diff = diff * (2 * chanceDouble + chance)
        self.stack += diff
        self.stack = max(min(10,self.stack),0)
        return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname = self.skill.name, spec = 'graph control')

    def get_modifier(self):
        multiplier = (1 + self.instinct * 0.01 * (5 + 0.5*self.vEhc.getV(1,1)))
        return core.CharacterModifier(pdamage = 2 * self.stack * multiplier, 
                                            pdamage_indep = self.tick * (self.stack + self.deathfault_buff.is_active() * 6) * multiplier,
                                            att = 2 * self.stack * multiplier)

######   Passive Skill   ######
class JobGenerator(ck.JobGenerator):
    def __init__(self, **kwargs):
        super(JobGenerator, self).__init__(**kwargs)
        self.jobtype = "STR"
        self.jobname = _("히어로")
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'mess')
        self.preEmptiveSkills = 2

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(InactiveRule(HeroSkills.Worldreaver, HeroSkills.InstinctualCombo), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(HeroSkills.RisingRage, HeroSkills.InstinctualCombo), RuleSet.BASE)
        ruleset.add_rule(ReservationRule(GlobalSkills.MapleWorldGoddessBlessing, HeroSkills.InstinctualCombo), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule(GlobalSkills.TermsAndConditions, HeroSkills.BurningSoulBlade), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponMastery = core.InformedCharacterModifier(_("{}(두손도끼)").format(HeroSkills.WeaponMastery), pdamage_indep = 10, pdamage = 5)  # Two-handed ax. 두손도끼.
        PhisicalTraining = core.InformedCharacterModifier(HeroSkills.PhysicalTraining,stat_main = 30, stat_sub = 30)
        
        ChanceAttack = core.InformedCharacterModifier(_("{}(패시브)").format(HeroSkills.ChanceAttack),crit = 20)

        CombatMastery = core.InformedCharacterModifier(HeroSkills.CombatMastery,armor_ignore = 50 + passive_level)
        AdvancedFinalAttack = core.InformedCharacterModifier(_("{}(패시브)").format(HeroSkills.AdvancedFinalAttack),att = 30 + passive_level)
        
        return [WeaponMastery, PhisicalTraining, ChanceAttack, CombatMastery, AdvancedFinalAttack]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        # Final Damage??
        WeaponConstant = core.InformedCharacterModifier(_("무기상수"), pdamage_indep = 44)
        Mastery = core.InformedCharacterModifier(_("숙련도"), mastery=90+(passive_level // 2))
        Enrage = core.InformedCharacterModifier(HeroSkills.Enrage,pdamage_indep = 25 + self.combat // 2, crit_damage = 20 + self.combat // 3)
        
        return [WeaponConstant, Mastery, Enrage]

    def get_modifier_optimization_hint(self) -> core.CharacterModifier:
        return core.CharacterModifier(boss_pdamage=65)
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Two-handed ax

        Nose sequence:
        Level-Patek-Uprising-Shout-Puncture-Panic

        Advanced Combo-Reinforcement, Boss Killer / Advanced Final Attack-Bonus Chance / Raging Blow-Reinforcement, Bonus Attack

        Use the main shaft according to the instinct

        Combo counter increase probability
        64%-2
        16%-1
        20%-0

        Instinct City
        24%-2
        6%-1 piece
        70%-0

        두손도끼

        코강 순서:
        레블 - 파택 - 업라이징 - 샤우트 - 인사이징 - 패닉

        어드밴스드 콤보-리인포스, 보스 킬러 / 어드밴스드 파이널 어택-보너스 찬스 / 레이징 블로우-리인포스, 보너스 어택

        메여축을 인스팅트에 맞춰 사용
        
        콤보 카운터 증가 확률
        64% - 2개
        16% - 1개
        20% - 0개

        인스팅트 시
        24% - 2개
        6%  - 1개
        70% - 0개
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        ######   Skill   ######
        #Buff skills
        Fury = core.BuffSkill(HeroSkills.Rage, 0, 200*1000, att = 30, rem = True).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill(HeroSkills.EpicAdventure, 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        #Damage Skills
        Panic = core.DamageSkill(HeroSkills.Panic, 630, 1150, 1, cooltime = 40000).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        PanicBuff = core.BuffSkill(_("{}(디버프)").format(HeroSkills.Panic), 0, 40000, cooltime = -1, pdamage_indep = 25, rem = False).wrap(core.BuffSkillWrapper)
        
        RagingBlow = core.DamageSkill(HeroSkills.RagingBlow, 600, 200 + 3*self.combat, 8, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        RagingBlowEnrage = core.DamageSkill(_("{}(인레이지)").format(HeroSkills.RagingBlow), 600, 215+3*self.combat, 6, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)  # I use this. 이걸 사용함.
        RagingBlowEnrageFinalizer = core.DamageSkill(_("{}(인레이지)(최종타)").format(HeroSkills.RagingBlow), 0, 215+3*self.combat, 2, modifier = core.CharacterModifier(pdamage = 20, crit = 100)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)  # I use this. You need to connect the two. 이걸 사용함. 둘을 연결해야 함.
        
        Puncture = core.DamageSkill(HeroSkills.Puncture, 660, 576 + 7 * self.combat, 4, cooltime = 30 * 1000).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        PunctureBuff = core.BuffSkill(_("{}(버프)").format(HeroSkills.Puncture), 0, (30 + self.combat // 2) * 1000, cooltime = -1, pdamage = 25 + ceil(self.combat / 2)).wrap(core.BuffSkillWrapper)
        PunctureDot = core.DotSkill(_("{}(도트)").format(HeroSkills.Puncture), 0, 2000, 165 + 3*self.combat, 1, (30 + self.combat // 2) * 1000, cooltime = -1).wrap(core.DotSkillWrapper)
    
        AdvancedFinalAttack = core.DamageSkill(HeroSkills.AdvancedFinalAttack, 0, 170 + 2*passive_level, 3 * 0.01 * (60 + ceil(passive_level/2) + 15)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)

        RisingRage = core.DamageSkill(HeroSkills.RisingRage, 750, 500, 8, cooltime = 10*1000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        Valhalla = core.BuffSkill(HeroSkills.CryValhalla, 900, 30 * 1000, cooltime = 150 * 1000, crit = 30, att = 50).wrap(core.BuffSkillWrapper)

        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        SwordOfBurningSoul = core.SummonSkill(HeroSkills.BurningSoulBlade, 810, 1000, (315+12*vEhc.getV(0,0)), 6, (60+vEhc.getV(0,0)//2) * 1000, cooltime = 120 * 1000, red=True, modifier = core.CharacterModifier(crit = 50)).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)
        
        ComboDeathFault = core.DamageSkill(HeroSkills.Worldreaver, 1260, 400 + 16*vEhc.getV(2,3), 14, cooltime = 20 * 1000, red=True).isV(vEhc, 2, 3).wrap(core.DamageSkillWrapper)
        ComboDeathFaultBuff = core.BuffSkill(_("{}(버프)").format(HeroSkills.Worldreaver), 0, 5 * 1000, rem = False, cooltime = -1).isV(vEhc, 2, 3).wrap(core.BuffSkillWrapper)
        
        ComboInstinct = core.BuffSkill(HeroSkills.InstinctualCombo, 360, 30 * 1000, cooltime = 240 * 1000, rem = False, red = True).isV(vEhc, 1, 1).wrap(core.BuffSkillWrapper)
        ComboInstinctFringe = core.DamageSkill(_("{}(균열)").format(HeroSkills.InstinctualCombo), 0, 200 + 8*vEhc.getV(1,1), 18).isV(vEhc, 1, 1).wrap(core.DamageSkillWrapper)
        ComboInstinctOff = core.BuffSkill(_("{}(종료)").format(HeroSkills.InstinctualCombo), 0, 1, cooltime = -1).wrap(core.BuffSkillWrapper)

        SwordIllusionInit = core.DamageSkill(_("{}(시전)").format(HeroSkills.SwordIllusion), 660, 0, 0, cooltime=30000, red=True).wrap(core.DamageSkillWrapper)
        SwordIllusion = core.DamageSkill(HeroSkills.SwordIllusion, 0, 125+5*vEhc.getV(0,0), 4, cooltime=-1).wrap(core.DamageSkillWrapper)
        SwordIllusionFinal = core.DamageSkill(_("{}(최종)").format(HeroSkills.SwordIllusion), 0, 250+10*vEhc.getV(0,0), 5, cooltime=-1).wrap(core.DamageSkillWrapper)

        ######   Skill Wrapper   ######
        ComboAttack = ComboAttackWrapper(core.BuffSkill(_("콤보어택"), 0, 999999 * 1000), ComboDeathFaultBuff, vEhc, passive_level)
        IncreaseCombo = ComboAttack.stackController(1)
        
        #Final attack type
        ComboInstinct.onAfter(ComboAttack.toggleController(True))
        ComboInstinct.onEventEnd(ComboAttack.toggleController(False))
        InstinctFringeUse = core.OptionalElement(ComboInstinct.is_active, ComboInstinctFringe, name = _("{} 여부").format(HeroSkills.InstinctualCombo))
    
        # Raging blow. 레이징 블로우.
        RagingBlowEnrage.onAfters([InstinctFringeUse, RagingBlowEnrageFinalizer, AdvancedFinalAttack, IncreaseCombo])

        RisingRage.onAfters([AdvancedFinalAttack, IncreaseCombo])
    
        Puncture.onBefore(ComboAttack.stackController(-1))
        Puncture.onAfters([PunctureBuff, PunctureDot, AdvancedFinalAttack])
    
        ComboDeathFault.onBefores([ComboDeathFaultBuff, ComboAttack.stackController(-6)])  # TODO: It is necessary to check how the combo counter is applied to the death fault damage. 데스폴트 데미지에 콤보 카운터 어떻게 적용되는지 확인 필요.
        ComboDeathFault.onAfter(AdvancedFinalAttack)
        # 6 or more Combo Orbs
        ComboDeathFault.onConstraint(core.ConstraintElement(_("콤보 6개 이상"), ComboAttack, partial(ComboAttack.judge, 6, 1)))

        SwordIllusionInit.onAfter(core.RepeatElement(SwordIllusion, 12))
        SwordIllusionInit.onAfter(core.RepeatElement(SwordIllusionFinal, 5))
        SwordIllusion.onAfter(AdvancedFinalAttack)
        SwordIllusion.onAfter(IncreaseCombo)
        SwordIllusionFinal.onAfter(AdvancedFinalAttack)
        SwordIllusionFinal.onAfter(IncreaseCombo)

        Panic.onBefore(ComboAttack.stackController(-2))
        Panic.onAfters([PanicBuff, AdvancedFinalAttack])
        
        # Weapon Aura. 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 3, 2)
        for sk in [RagingBlowEnrageFinalizer, ComboDeathFault, Panic, Puncture, RisingRage]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        return(RagingBlowEnrage,
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_wind_booster(),
                    globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), ComboAttack, Fury, EpicAdventure, Valhalla,
                    PunctureBuff, PunctureDot, AuraWeaponBuff, AuraWeapon, ComboDeathFaultBuff,
                    ComboInstinct, ComboInstinctOff, PanicBuff,
                    globalSkill.soul_contract()] +\
                [Panic, Puncture, ComboDeathFault, SwordIllusionInit, RisingRage] +\
                [SwordOfBurningSoul, MirrorBreak, MirrorSpider] +\
                [RagingBlowEnrage])