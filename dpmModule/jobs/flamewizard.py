from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ComplexConditionRule, ConcurrentRunRule, RuleSet
from . import globalSkill
from .jobclass import cygnus
from .jobbranch import magicians
from typing import Any, Dict


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "INT"
        self.jobname = "플레임위자드"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore=10, pdamage=50, att=35)

    def get_ruleset(self):
        def soul_contract_rule(soul_contract, ifc, burning_region):
            return (ifc.is_usable() or ifc.is_cooltime_left(90*1000, 1)) and burning_region.is_active()

        ruleset = RuleSet()
        ruleset.add_rule(ComplexConditionRule('소울 컨트랙트', ['인피니티 플레임 서클(개시)', '버닝 리전'], soul_contract_rule), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('인피니티 플레임 서클(개시)', '버닝 리전'), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        ######   Skill   ######
        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트", patt = 10)
        ElementalHarmony = core.InformedCharacterModifier("엘리멘탈 하모니", stat_main = chtr.level // 2)
        
        SpellControl = core.InformedCharacterModifier("주문 연마",att = 10)
        LiberatedMagic = core.InformedCharacterModifier("해방된 마력",pdamage_indep = 30)
        BurningFocus = core.InformedCharacterModifier("약점 분석",crit = 30, crit_damage = 20)
        BriliantEnlightenment = core.InformedCharacterModifier("번뜩이는 깨달음",stat_main = 60)
        PureMagic = core.InformedCharacterModifier("마법의 진리", att = 20 + passive_level, pdamage_indep = 50 + 3*passive_level)

        return [ElementalExpert, ElementalHarmony, SpellControl, LiberatedMagic, BurningFocus, BriliantEnlightenment, PureMagic]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=95+passive_level)
        SpiritOfFlameActive = core.InformedCharacterModifier("스피릿 오브 플레임(이그니션)", prop_ignore = 10)
        
        return [WeaponConstant, Mastery, SpiritOfFlameActive]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        오비탈 - 익스팅션 - 드래곤 슬레이브 - 이그니션 - 인페르노라이즈
        디스차지 여우 사용
        블비탈 4히트
        오비탈 1350타 / 분
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        orbital_per_min = options.get("orbital_per_min", 1350)
        flamewizardDefaultSpeed = 60000 / (orbital_per_min / 6)  #266
        blazingOrbitalHit = 4
        
        #Buff skills
        WordOfFire = core.BuffSkill("북 오브 파이어", 0, 300000, att = 20).wrap(core.BuffSkillWrapper)
        FiresOfCreation = core.BuffSkill("스피릿 오브 플레임", 600, 300 * 1000, armor_ignore = 30+self.combat).wrap(core.BuffSkillWrapper)
        BurningRegion = core.BuffSkill("버닝 리전", 1080, 30 * 1000, cooltime =45 * 1000, rem = True, red=True, pdamage = 60+self.combat).wrap(core.BuffSkillWrapper)
        GloryOfGuardians = core.BuffSkill("글로리 오브 가디언즈", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        Flame = core.BuffSkill("플레임", 0, 8000, att = 40 + passive_level, cooltime=-1).wrap(core.BuffSkillWrapper) # 벞지 적용 안되는 스킬
        
        #Damage Skills
        InfernoRize = core.DamageSkill("인페르노라이즈", 570, 350+3*self.combat, 10, cooltime = 30*1000, modifier = core.CharacterModifier(pdamage_indep = 90 + self.combat), red = True).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        
        #Full speed, No Combat Orders
        OrbitalFlame = core.DamageSkill("오비탈 플레임 IV", 210, 215 + self.combat, 3 * 2 * (210 / flamewizardDefaultSpeed), modifier = core.CharacterModifier(armor_ignore = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        # BlazingExtinction = core.SummonSkill("블레이징 익스팅션", 660, 2500, 310+2*self.combat, 3+1, 10000, cooltime=5000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)
        CygnusPhalanx = cygnus.PhalanxChargeWrapper(vEhc, 2, 1)
        BlazingOrbital = core.DamageSkill("블레이징 오비탈 플레임", 180, 330+13*vEhc.getV(0,0), 6 * blazingOrbitalHit, cooltime = 5000, red = True, modifier = core.CharacterModifier(armor_ignore = 50)).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)    #4타 가정
        
        DragonSlaveTick = core.DamageSkill("드래곤 슬레이브", 280, 500, 6).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)#x7
        DragonSlaveInit = core.DamageSkill("드래곤 슬레이브 개시(더미)", 0, 0, 0, cooltime = 90 * 1000).wrap(core.DamageSkillWrapper)
        DragonSlaveEnd = core.DamageSkill("드래곤 슬레이브 종결", 810, 500, 10).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        
        IgnitionDOT = core.DotSkill("이그니션", 0, 1000, 220*0.01*(100 + 60 + 2*passive_level), 1, 10*1000, cooltime=-1).wrap(core.DotSkillWrapper)

        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        #여우 사용
        SavageFlameStack = core.StackSkillWrapper(core.BuffSkill("플레임 디스차지(스택)", 0, 99999999), 6)
        
        SavageFlame = core.StackDamageSkillWrapper(
            core.DamageSkill("플레임 디스차지", 840, 250 + 10*vEhc.getV(4,4), 8, cooltime = 20*1000, red = True).isV(vEhc,4,4),
            SavageFlameStack,
            lambda sk: (8 + (sk.stack - 2) * 2)
        )
        
        InfinityFlameCircleTick = core.DamageSkill("인피니티 플레임 서클", 180, 500+20*vEhc.getV(3,3), 7, modifier = core.CharacterModifier(crit = 50, armor_ignore = 50)).isV(vEhc,3,3).wrap(core.DamageSkillWrapper) #1틱
        InfinityFlameCircleInit = core.DamageSkill("인피니티 플레임 서클(개시)", 360, 0, 0, cooltime = 15*6*1000).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)

        # 84타
        SalamanderMischeif = core.SummonSkill("샐리맨더 미스칩", 750, 710, 150+6*vEhc.getV(0,0), 7, 60000, cooltime=90000, red=True).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        SalamanderMischeifStack = core.StackSkillWrapper(core.BuffSkill("샐리맨더 미스칩(불씨)", 0, 99999999), 15+vEhc.getV(0,0))
        SalamanderMischeifBuff = core.BuffSkill("샐리맨더 미스칩(버프)", 0, 30000, cooltime=-1, att=15+2*(15+vEhc.getV(0,0))).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        
        ######   Wrappers    ######
    
        DragonSlave = core.RepeatElement(DragonSlaveTick, 7)
        DragonSlave.onAfter(DragonSlaveEnd)
        DragonSlaveInit.onAfter(DragonSlave)
    
        InfinityFlameCircle = core.RepeatElement(InfinityFlameCircleTick, 39)
        
        InfinityFlameCircleInit.onAfter(InfinityFlameCircle)
        
        ApplyDOT = core.OptionalElement(IgnitionDOT.is_not_active, IgnitionDOT, name="도트 갱신")
        for sk in [OrbitalFlame, BlazingOrbital, DragonSlaveTick, InfinityFlameCircleTick]:
            sk.onAfter(Flame)
            sk.onAfter(ApplyDOT)
        IgnitionDOT.onAfter(SavageFlameStack.stackController(1))
        InfernoRize.onAfter(IgnitionDOT.controller(1))
        DragonSlaveEnd.onAfter(IgnitionDOT.controller(1))

        InfernoRize.onConstraint(core.ConstraintElement("이그니션 시간 체크", IgnitionDOT, partial(IgnitionDOT.is_time_left, 9000, 1)))

        SavageFlame.onAfter(SavageFlameStack.stackController(-15))
        SavageFlame.onConstraint(core.ConstraintElement("2스택 이상", SavageFlameStack, partial(SavageFlameStack.judge, 2, 1)))

        SalamanderMischeif.onJustAfter(SalamanderMischeifStack.stackController(-45))
        SalamanderMischeif.onTick(SalamanderMischeifStack.stackController(1))
        SalamanderMischeif.add_runtime_modifier(SalamanderMischeifStack, lambda sk: core.CharacterModifier(pdamage_indep=sk.stack))
        SalamanderMischeif.onEventEnd(SalamanderMischeifBuff)

        # Overload Mana
        overload_mana_builder = magicians.OverloadManaBuilder(vEhc, 1, 2)
        for sk in [OrbitalFlame, InfernoRize, DragonSlaveTick, DragonSlaveEnd, InfinityFlameCircleTick, SavageFlame,
                    SalamanderMischeif, CygnusPhalanx]:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()
        
        return (OrbitalFlame,
                [globalSkill.maple_heros(chtr.level, name = "시그너스 나이츠", combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                     cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level), WordOfFire, FiresOfCreation, BurningRegion, GloryOfGuardians, OverloadMana, Flame, SalamanderMischeifBuff,
                    globalSkill.soul_contract()] +\
                [SalamanderMischeif, CygnusPhalanx, BlazingOrbital, InfinityFlameCircleInit, DragonSlaveInit, SavageFlame,
                    InfernoRize, MirrorBreak, MirrorSpider] +\
                [IgnitionDOT] +\
                [] +\
                [OrbitalFlame])    
    