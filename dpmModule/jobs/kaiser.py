from enum import Enum

from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, InactiveRule, ConditionRule
from . import globalSkill, jobutils
from .jobbranch import warriors
from .jobclass import nova
from math import ceil
from typing import Any, Dict


# English skill information for Kaiser here https://maplestory.fandom.com/wiki/Kaiser/Skills
class KaiserSkills(Enum):
    # Link Skill
    DragonLink = 'Dragon Link | 커맨드'
    # Beginner
    RealignDefenderMode = 'Realign: Defender Mode | 리셔플스위치: 방어모드'
    RealignAttackerMode = 'Realign: Attacker Mode | 리셔플스위치: 공격모드'
    Transfiguration = 'Transfiguration | 트랜스피규레이션'
    # 1st Job
    DragonSlash = 'Dragon Slash | 드래곤슬래시'
    FlameSurge = 'Flame Surge | 플레임 샷'
    AirLift = 'Air Lift | 더블 리프'
    ScaleSkin = 'Scale Skin | 스킨 프로텍션'
    # 2nd Job
    DragonSlashI = 'Dragon Slash I | 드래곤슬래시 1차 강화'
    ImpactWave = 'Impact Wave | 임팩트 웨이브'
    PiercingBlaze = 'Piercing Blaze | 피어스 러쉬'
    TempestBlades = 'Tempest Blades | 윌 오브 소드'
    BlazeOn = 'Blaze On | 블레이즈 업'
    SwordMastery = 'Sword Mastery | 소드 마스터리'
    InnerBlaze = 'Inner Blaze | 이너 블레이즈'
    DefenderModeI = 'Defender Mode I | 방어모드 1차 강화'
    AttackerModeI = 'Attacker Mode I | 공격모드 1차 강화'
    # 3rd Job
    DragonSlashII = 'Dragon Slash II | 드래곤슬래시 2차 강화'
    WingBeat = 'Wing Beat | 윙비트'
    PressureChain = 'Pressure Chain | 체인풀링'
    FinalForm = 'Final Form | 파이널 피규레이션'
    StoneDragon = 'Stone Dragon | 페트리파이드'
    Cursebite = 'Cursebite | 리게인 스트렝스'
    Catalyze = 'Catalyze | 카탈라이즈'
    SelfRecovery = 'Self Recovery | 셀프 리커버리'
    AdvancedInnerBlaze = 'Advanced Inner Blaze | 어드밴스드 이너 블레이즈'
    DefenderModeII = 'Defender Mode II | 방어모드 2차 강화'
    AttackerModeII = 'Attacker Mode II | 공격모드 2차 강화'
    # 4th Job
    DragonSlashIII = 'Dragon Slash III | 드래곤슬래시 3차 강화'
    GigasWave = 'Gigas Wave | 기가 슬래셔'
    DragonBarrage = 'Dragon Barrage | 블루 스트릭'
    BladeBurst = 'Blade Burst | 소드 스트라이크'
    InfernoBreath = 'Inferno Breath | 인퍼널 브레스'
    AdvancedTempestBlades = 'Advanced Tempest Blades | 어드밴스드 윌 오브 소드'
    GrandArmor = 'Grand Armor | 로버스트 아머'
    UnbreakableWill = 'Unbreakable Will | 언플린칭 커리지'
    ExpertSwordMastery = 'Expert Sword Mastery | 어드밴스드 소드 마스터리'
    NovaWarrior = 'Nova Warrior | 노바의 용사'
    NovaTemperance = 'Nova Temperance | 노바 용사의 의지'
    DefenderModeIII = 'Defender Mode III | 방어모드 3차 강화'
    AttackerModeIII = 'Attacker Mode III | 공격모드 3차 강화'
    # Hypers
    AncestralProminence = 'Ancestral Prominence | 프로미넌스'
    FinalTrance = 'Final Trance | 파이널 트랜스'
    KaisersMajesty = 'Kaiser\'s Majesty | 마제스티 오브 카이저'
    # 5th Job
    NovaGuardians = 'Nova Guardians | 가디언 오브 노바'
    Bladefall = 'Bladefall | 윌 오브 소드: 스트라이크'
    DracoSurge = 'Draco Surge | 드라코 슬래셔'
    DragonBlaze = 'Dragon Blaze | 드래곤 블레이즈'


######   Passive Skill   ######
class MorphGaugeWrapper(core.StackSkillWrapper):
    def __init__(self, skill, final_figuration):
        super(MorphGaugeWrapper, self).__init__(skill, 700)
        self.set_name_style("+%d")
        self.final_figuration = final_figuration
        
    def vary(self, d):
        if self.final_figuration.is_not_active() or d<0:
            return super(MorphGaugeWrapper, self).vary(d)
        else:
            return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname = self._id, spec = 'graph control')

    def get_morph_level(self):
        if self.final_figuration.is_active() or self.stack >= 700:  # Step 3. 3단계.
            return 3
        if self.stack >= 300: # Step 2. 2단계.
            return 2
        if self.stack >= 100: # Step 1. 1단계.
            return 1
        return 0

    def get_modifier(self):  # Iron Will-Increases damage by 3% per morph gauge step. 아이언 윌 - 모프 게이지 단계당 데미지 3% 증가.
        return core.CharacterModifier(pdamage = 3 * self.get_morph_level())

class GigaSlasherWrapper(core.DamageSkillWrapper):
    def __init__(self, skill, final_figuration):
        super(GigaSlasherWrapper, self).__init__(skill)
        self.final_figuration = final_figuration

    def get_hit(self):
        if self.final_figuration.is_active():
            return 11+1
        else:
            return 9+1

class WingbitWrapper(core.SummonSkillWrapper):
    def __init__(self, skill, final_figuration):
        super(WingbitWrapper, self).__init__(skill)
        self.final_figuration = final_figuration

    def get_summon_delay(self):
        if self.final_figuration.is_active():
            return 540
        else:
            return 360

class WillOfSwordSummonWrapper(core.BuffSkillWrapper):
    def __init__(self, skill, final_figuration):
        super(WillOfSwordSummonWrapper, self).__init__(skill)
        self.final_figuration = final_figuration

    def get_delay(self):
        if self.final_figuration.is_active():
            return 600
        else:
            return 150

    def _off(self):
        self.timeLeft = 0
        return self._result_object_cache

    def off(self):
        task = core.Task(self, self._off)
        return core.TaskHolder(task, "종료")

class WillOfSwordWrapper(core.DamageSkillWrapper):
    def __init__(self, skill, final_figuration):
        super(WillOfSwordWrapper, self).__init__(skill)
        self.final_figuration = final_figuration

    def get_hit(self):
        if self.final_figuration.is_active():
            return (4+1)*5
        else:
            return 4*5

class ProminenceWrapper(core.DamageSkillWrapper):
    def __init__(self, skill, final_figuration):
        super(ProminenceWrapper, self).__init__(skill)
        self.final_figuration = final_figuration

    def get_delay(self):
        if self.final_figuration.is_active():
            return 1530
        else:
            return 2220

class WillOfSwordStrikeWrapper(core.DamageSkillWrapper):
    def __init__(self, skill, final_figuration):
        super(WillOfSwordStrikeWrapper, self).__init__(skill)
        self.final_figuration = final_figuration

    def get_delay(self):
        if self.final_figuration.is_active():
            return 600
        else:
            return 150

    def get_hit(self):
        if self.final_figuration.is_active():
            return (4+1)*5
        else:
            return 4*5

class WillOfSwordStrikeExplodeWrapper(core.DamageSkillWrapper):
    def __init__(self, skill, final_figuration):
        super(WillOfSwordStrikeExplodeWrapper, self).__init__(skill)
        self.final_figuration = final_figuration

    def get_hit(self):
        if self.final_figuration.is_active():
            return (6+1)*5
        else:
            return 6*5

class DrakeSlasherWrapper(core.DamageSkillWrapper):
    def __init__(self, skill, final_figuration):
        super(DrakeSlasherWrapper, self).__init__(skill)
        self.final_figuration = final_figuration

    def get_hit(self):
        if self.final_figuration.is_active():
            return 10+2+1
        else:
            return 10+1

class DrakeSlasherProjectileWrapper(core.DamageSkillWrapper):
    def __init__(self, skill, final_figuration):
        super(DrakeSlasherProjectileWrapper, self).__init__(skill)
        self.final_figuration = final_figuration

    def get_hit(self):
        if self.final_figuration.is_active():
            return 6+2+1
        else:
            return 6+1

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vSkillNum = 5
        self.vEnhanceNum = 13
        self.jobtype = "STR"
        self.jobname = "카이저"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(InactiveRule(KaiserSkills.InfernoBreath.value, KaiserSkills.FinalForm.value), RuleSet.BASE)
        ruleset.add_rule(InactiveRule(KaiserSkills.KaisersMajesty.value, KaiserSkills.FinalForm.value), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(KaiserSkills.AdvancedTempestBlades.value, KaiserSkills.Bladefall.value, lambda sk: sk.is_cooltime_left(10000, 1)), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self) -> core.CharacterModifier:
        return core.CharacterModifier(pdamage=44, armor_ignore=17)
        
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        InnerBlaze = core.InformedCharacterModifier(KaiserSkills.InnerBlaze.value,stat_main = 20)
        AdvancedInnerBlaze = core.InformedCharacterModifier(KaiserSkills.AdvancedInnerBlaze.value,stat_main = 30)
        Catalyze = core.InformedCharacterModifier(KaiserSkills.Catalyze.value, patt=30, crit=20, pdamage_indep=20)
        AdvancedWillOfSwordPassive = core.InformedCharacterModifier(f"{KaiserSkills.AdvancedTempestBlades.value}(Passive | 패시브)",att = 20 + 2*ceil(passive_level/3))
        UnflinchingCourage = core.InformedCharacterModifier(KaiserSkills.UnbreakableWill.value,armor_ignore = 40 + passive_level)
        AdvancedSwordMastery = core.InformedCharacterModifier(KaiserSkills.ExpertSwordMastery.value, att = 30 + passive_level, crit_damage = 15 + passive_level//3, crit=20 + passive_level//2)
    
        return [InnerBlaze, AdvancedInnerBlaze, Catalyze, 
                AdvancedWillOfSwordPassive, UnflinchingCourage, AdvancedSwordMastery]
                
    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 34)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=90+ceil(passive_level / 2))
        
        ReshuffleSwitchAttack = core.InformedCharacterModifier(KaiserSkills.RealignAttackerMode.value,att = 45, crit = 20, boss_pdamage = 18)
        
        return [WeaponConstant, Mastery, ReshuffleSwitchAttack]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Morph supply and demand
        Awillso 12*5
        Prominence 50
        Infernal 40
        Giga Slasher 5
        1 per wingbeat attack

        Hyper
        Giga Slasher-Reinforce, Bonus Attack
        Wing Beat-Reinforce, Persist, Extra Attack

        Core hardening priority
        Giga Slasher-Wing Beat-Sword Strike-Will of Sword-Infernal Breath-Petrified-Prominence

        모프 수급량
        어윌소 12*5
        프로미넌스 50
        인퍼널 40
        기가슬래셔 5
        윙비트 공격당 1
        
        하이퍼
        기가 슬래셔-리인포스, 보너스 어택
        윙비트-리인포스, 퍼시스트, 엑스트라 어택
        
        코어 강화 우선순위
        기가 슬래셔-윙비트-소드 스트라이크-윌 오브 소드-인퍼널 브레스-페트리파이드-프로미넌스
        '''

        passive_level = chtr.get_base_modifier().passive_level + self.combat
        # Buff skills
        RegainStrenth = core.BuffSkill(KaiserSkills.Cursebite.value, 0, 240000, rem = True, pdamage_indep = 15).wrap(core.BuffSkillWrapper)
        BlazeUp = core.BuffSkill(KaiserSkills.BlazeOn.value, 0, 240000, att = 20, rem = True).wrap(core.BuffSkillWrapper)
        SoulContract = globalSkill.soul_contract()
    
        FinalFiguration = core.BuffSkill(KaiserSkills.FinalForm.value, 0, 60000, pdamage_indep = 15, boss_pdamage = 10, rem = True).wrap(core.BuffSkillWrapper)
        MorphGauge = MorphGaugeWrapper(core.BuffSkill("Morph Gauge | 모프 게이지", 0, 9999999), FinalFiguration)

        Wingbit_1 = WingbitWrapper(core.SummonSkill(KaiserSkills.WingBeat.value, 0, 330, 200, 1, 15900, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 3, True), FinalFiguration) # 48 strokes. 48타.
        Wingbit_2 = WingbitWrapper(core.SummonSkill(f"{KaiserSkills.WingBeat.value}(2)", 0, 330, 200, 1, 15900, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 3, True), FinalFiguration) # 48 strokes. 48타.
        
        GigaSlasher = GigaSlasherWrapper(core.DamageSkill(KaiserSkills.GigasWave.value, 540, 330 + 2*self.combat, 9+1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False), FinalFiguration)
    
        AdvancedWillOfSword_Summon = WillOfSwordSummonWrapper(core.BuffSkill(f"{KaiserSkills.AdvancedTempestBlades.value}(Summon | 소환)", 0, 9999999, cooltime = 10000, red=True), FinalFiguration)
        AdvancedWillOfSword = WillOfSwordWrapper(core.DamageSkill(KaiserSkills.AdvancedTempestBlades.value, 0, 400+3*passive_level, 4*5).setV(vEhc, 3, 2, True), FinalFiguration)

        InfernalBreath = core.DamageSkill(KaiserSkills.InfernoBreath.value, 780, 300 + 4*self.combat, 8, cooltime = (20-self.combat)*1000, red=True).setV(vEhc, 4, 2, True).wrap(core.DamageSkillWrapper)
        InfernalBreath_Tile = core.SummonSkill(f"{KaiserSkills.InfernoBreath.value}(Fire | 바닥)", 0, 1200, 200 + 3*self.combat, 2, 20000, cooltime = -1).setV(vEhc, 4, 2, True).wrap(core.SummonSkillWrapper)

        Petrified = core.SummonSkill(KaiserSkills.StoneDragon.value, 450, 3030, 400, 1, 60000).setV(vEhc, 5, 3, False).wrap(core.SummonSkillWrapper)
    
        # Hyper. 하이퍼.
        MajestyOfKaiser = core.BuffSkill(KaiserSkills.KaisersMajesty.value, 900, 30000, att = 30, cooltime = 90000).wrap(core.BuffSkillWrapper)
        FinalTrance = core.BuffSkill(KaiserSkills.FinalTrance.value, 0, 60000, cooltime = 300000).wrap(core.BuffSkillWrapper) # I don't know the delay. 딜레이 모름.
        Prominence = ProminenceWrapper(core.DamageSkill(KaiserSkills.NovaTemperance.value, 2220, 1000, 15, cooltime = 60000).setV(vEhc, 6, 2, True), FinalFiguration)

        # 5th. 5차.
        Phanteon = nova.PantheonWrapper(vEhc, 4, 4)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        NovaGoddessBless = nova.NovaGoddessBlessWrapper(vEhc, 0, 0, MorphGauge)

        GuardianOfNova_1 = core.SummonSkill(f"{KaiserSkills.NovaGuardians.value}(1)", 600, 45000/46, 450+15*vEhc.getV(2,2), 4, (30+int(0.5*vEhc.getV(2,2)))*1000, cooltime = 120000, red=True).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)  # 46*4 strokes. 46*4타.
        GuardianOfNova_2 = core.SummonSkill(f"{KaiserSkills.NovaGuardians.value}(2)", 0, 45000/34, 250+10*vEhc.getV(2,2), 6, (30+int(0.5*vEhc.getV(2,2)))*1000, cooltime = -1).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)  # 34*6 strokes. 34*6타.
        GuardianOfNova_3 = core.SummonSkill(f"{KaiserSkills.NovaGuardians.value}(3)", 0, 45000/26, 900+35*vEhc.getV(2,2), 2, (30+int(0.5*vEhc.getV(2,2)))*1000, cooltime = -1).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)  # 26*2 strokes. 26*2타.

        WillOfSwordStrike = WillOfSwordStrikeWrapper(core.DamageSkill(KaiserSkills.Bladefall.value, 150, 500+20*vEhc.getV(3,3), 4*5, cooltime = 30000, red=True).isV(vEhc,3,3), FinalFiguration)
        WillOfSwordStrike_Explode = WillOfSwordStrikeExplodeWrapper(core.DamageSkill(f"{KaiserSkills.Bladefall.value}(Explosion | 폭발)", 0, 1000+40*vEhc.getV(3,3), 6*5).isV(vEhc,3,3), FinalFiguration)
        
        DrakeSlasher = DrakeSlasherWrapper(core.DamageSkill(KaiserSkills.DracoSurge.value, 540, 500+5*vEhc.getV(0,0), 10+1, cooltime = (7-(vEhc.getV(0,0)//15))*1000, red=True, modifier = core.CharacterModifier(crit=100, armor_ignore=50) + core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).isV(vEhc,0,0), FinalFiguration)
        DrakeSlasher_Projectile = DrakeSlasherProjectileWrapper(core.DamageSkill(f"{KaiserSkills.DracoSurge.value}(Projectile | 발사)", 0, 500+5*vEhc.getV(0,0), 6+1, cooltime = -1, modifier = core.CharacterModifier(crit=100, armor_ignore=50) + core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).isV(vEhc,0,0), FinalFiguration)

        DragonBlaze = core.SummonSkill(KaiserSkills.DragonBlaze.value, 900, 240, 250+10*vEhc.getV(0,0), 6, 20000, cooltime=120*1000, red=True).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        DragonBlazeAura = core.DamageSkill(f"{KaiserSkills.DragonBlaze.value}(Aura | 불의 기운)", 0, 375+15*vEhc.getV(0,0), 5, cooltime=3600).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        DragonBlazeFireball = core.DamageSkill(f"{KaiserSkills.DragonBlaze.value}(Fireball | 화염구)", 0, 350+14*vEhc.getV(0,0), 3*6, cooltime=10000).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
        
        # Final figure. 파이널 피규레이션.
        FinalFiguration.onAfter(MorphGauge.stackController(-9999, name = "게이지 리셋"))
        FinalFiguration.onConstraint(core.ConstraintElement("게이지 충전시 변신", MorphGauge, partial(MorphGauge.judge, 700, 1)))

        # Final Trance. 파이널 트랜스.
        FinalTrance.onAfter(FinalFiguration.controller(60000, "set_enabled_and_time_left"))
        FinalTrance.onConstraint(core.ConstraintElement("파이널 피규레이션 여부 확인", FinalFiguration, FinalFiguration.is_not_active))
        
        # Wing beat. 윙비트.
        Wingbit_1.onAfter(Wingbit_2)

        # Infernal Breath. 인퍼널 브레스.
        InfernalBreath.onAfter(InfernalBreath_Tile)
        
        # Draco Slasher. 드라코 슬래셔.
        DrakeSlasher.onAfter(DrakeSlasher_Projectile)
        
        # Basic Attack-Draco Slasher / Giga Slasher Branch. 기본공격 - 드라코 슬래셔 / 기가 슬래셔 분기.
        BasicAttack = core.DamageSkill('기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttack.onAfter(core.OptionalElement(DrakeSlasher.is_available, DrakeSlasher, GigaSlasher, name = "드라코 슬래셔 충전시"))
        
        # Advanced Will of Sword. 어드밴스드 윌 오브 소드.
        IsSwordSummoned = core.ConstraintElement("윌 오브 소드 소환시", AdvancedWillOfSword_Summon, AdvancedWillOfSword_Summon.is_active)
        TurnOffSword = AdvancedWillOfSword_Summon.off()
        AdvancedWillOfSword.onConstraint(IsSwordSummoned)
        AdvancedWillOfSword.onJustAfter(TurnOffSword)

        # Will of Sword: Strike. 윌 오브 소드:스트라이크.
        WillOfSwordStrike.onConstraint(IsSwordSummoned)
        WillOfSwordStrike.onJustAfter(TurnOffSword)
        WillOfSwordStrike.onAfter(WillOfSwordStrike_Explode)
        
        DrakeSlasherReset = DrakeSlasher.controller(1.0, 'reduce_cooltime_p')
        DrakeSlasherResetStack = core.StackSkillWrapper(core.BuffSkill(f'{KaiserSkills.DracoSurge.value} - 재사용 초기화', 0, 0), 3)
        DrakeSlasher.onAfter(core.OptionalElement(partial(DrakeSlasherResetStack.judge, 1, 1), DrakeSlasherReset))
        DrakeSlasher.onAfter(DrakeSlasherResetStack.stackController(-1))
        WillOfSwordStrike_Explode.onAfter(DrakeSlasherResetStack.stackController(3))
        WillOfSwordStrike_Explode.onAfter(DrakeSlasherReset)
        
        # Weapon Aura. 오라 웨폰.
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 1, 1)
        for sk in [GigaSlasher, DrakeSlasher, DrakeSlasher_Projectile]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()
        
        # Cooldown reset. 쿨 초기화.
        for sk in [AdvancedWillOfSword_Summon, InfernalBreath, SoulContract]:
            MajestyOfKaiser.onAfter(sk.controller(1, "reduce_cooltime_p"))
        
        # Ancestors. 조상님.
        GuardianOfNova_1.onAfters([GuardianOfNova_2, GuardianOfNova_3])

        # Dragon Blaze. 드래곤 블레이즈.
        UseDragonBlazeAura = core.OptionalElement(lambda: DragonBlaze.is_active() and DragonBlazeAura.is_available(), DragonBlazeAura)
        UseDragonBlazeFireball = core.OptionalElement(lambda: DragonBlaze.is_not_active() and DragonBlazeFireball.is_available(), DragonBlazeFireball)
        for sk in [GigaSlasher, DrakeSlasher, DrakeSlasher_Projectile]:
            sk.onAfter(UseDragonBlazeAura)
            sk.onAfter(UseDragonBlazeFireball)
        DragonBlazeAura.protect_from_running()
        DragonBlazeFireball.protect_from_running()
        
        # Stack amount calculation. 스택량 계산.
        for sk, incr in [[DrakeSlasher, 5],
                            [GigaSlasher, 5],
                            [AdvancedWillOfSword, 60],
                            [InfernalBreath, 40],
                            [Prominence, 50]]:
            sk.onAfter(MorphGauge.stackController(incr))
        
        Wingbit_1.onTick(MorphGauge.stackController(1))
        Wingbit_2.onTick(MorphGauge.stackController(1))
        
        DrakeSlasher.protect_from_running()
    
        return(BasicAttack,
                [globalSkill.maple_heros(chtr.level, name=KaiserSkills.NovaWarrior.value, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), MorphGauge,
                    RegainStrenth, BlazeUp, FinalFiguration, MajestyOfKaiser, FinalTrance, AuraWeaponBuff, AuraWeapon, NovaGoddessBless,
                    SoulContract] +\
                [AdvancedWillOfSword_Summon, WillOfSwordStrike, AdvancedWillOfSword] +\
                [Wingbit_1, Wingbit_2, GuardianOfNova_1, GuardianOfNova_2, GuardianOfNova_3] +\
                [DragonBlaze, DragonBlazeAura, DragonBlazeFireball, DrakeSlasher,
                    InfernalBreath, InfernalBreath_Tile, Petrified, Prominence, Phanteon, MirrorBreak, MirrorSpider] +\
                [BasicAttack])
