from enum import Enum

from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill, jobutils
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict


# English skill information for Darkknight here https://maplestory.fandom.com/wiki/Dark_Knight/Skills
class DarkKnightSkills(Enum):
    # Link Skill
    InvincibleBelief = 'Invincible Belief | 인빈서블 빌리프'
    # 1st Job
    SlashBlast = 'Slash Blast | 슬래시 블러스트'
    WarLeap = 'War Leap | 워리어 리프'
    LeapAttack = 'Leap Attack | 리프 어택'
    IronBody = 'Iron Body | 아이언 바디'
    WarriorMastery = 'Warrior Mastery | 워리어 마스터리'
    # 2nd Job
    PiercingDrive = 'Piercing Drive | 피어싱 쓰루'
    EvilEye = 'Evil Eye | 비홀더'
    SpearSweep = 'Spear Sweep | 스피어 풀링'
    WeaponBooster = 'Weapon Booster | 웨폰 부스터'
    IronWill = 'Iron Will | 아이언 월'
    HyperBody = 'Hyper Body | 하이퍼 바디'
    WeaponMastery = 'Weapon Mastery | 웨폰 마스터리'
    FinalAttack = 'Final Attack | 파이널 어택'
    PhysicalTraining = 'Physical Training | 피지컬 트레이닝'
    # 3rd Job
    LaManchaSpear = 'La Mancha Spear | 라만차 스피어'
    Rush = 'Rush | 돌진'
    EvilEyeofDomination = 'Evil Eye of Domination | 비홀더 도미넌트'
    EvilEyeShock = 'Evil Eye Shock | 비홀더 쇼크'
    UpwardCharge = 'Upward Charge | 어퍼 차지'
    CrossSurge = 'Cross Surge | 크로스 오버 체인'
    LordofDarkness = 'Lord of Darkness | 로드 오브 다크니스'
    Endure = 'Endure | 인듀어'
    HexoftheEvilEye = 'Hex of the Evil Eye | 비홀더스 버프'
    # 4th Job
    GungnirsDescent = 'Gungnir\'s Descent | 궁그닐 디센트'
    MagicCrash = 'Magic Crash | 매직 크래쉬'
    DarkImpale = 'Dark Impale | 다크 임페일'
    PowerStance = 'Power Stance | 스탠스'
    Sacrifice = 'Sacrifice | 새크리파이스'
    FinalPact = 'Final Pact | 리인카네이션'
    BarricadeMastery = 'Barricade Mastery | 어드밴스드 웨폰 마스터리'
    RevengeoftheEvilEye = 'Revenge of the Evil Eye | 비홀더스 리벤지'
    # Hypers
    FinalPactCriticalChance = 'Final Pact - Critical Chance | 리인카네이션-크리티컬 레이트'
    NightshadeExplosion = 'Nightshade Explosion | 다크 신서시스'
    EpicAdventure = 'Epic Adventure | 에픽 어드벤처'
    DarkThirst = 'Dark Thirst | 다크 서스트'
    # 5th Job
    SpearofDarkness = 'Spear of Darkness | 다크 스피어'
    RadiantEvil = 'Radiant Evil | 비홀더 임팩트'
    CalamitousCyclone = 'Calamitous Cyclone | 피어스 사이클론'
    DarknessAura = 'Darkness Aura | 다크니스 오라'


#TODO: Beholder's Revenge main effect added. 비홀더스 리벤지 메인 효과 추가.

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = (7, 7)
        self.jobtype = "STR"
        self.jobname = "다크나이트"
        self.vEnhanceNum = 9
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'reuse', 'boss_pdamage')
        self.preEmptiveSkills = 2

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(boss_pdamage=60, armor_ignore=44)
        
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        WeaponMastery = core.InformedCharacterModifier(DarkKnightSkills.WeaponMastery.value,pdamage = 5)
        PhisicalTraining = core.InformedCharacterModifier(DarkKnightSkills.PhysicalTraining.value,stat_main = 30, stat_sub = 30)
        
        LordOfDarkness = core.InformedCharacterModifier(DarkKnightSkills.LordofDarkness.value,crit=30, crit_damage = 8)
    
        AdvancedWeaponMastery = core.InformedCharacterModifier(DarkKnightSkills.BarricadeMastery.value,att = 30 + passive_level, crit_damage = 15 + passive_level // 3)
        ReincarnationBuff = core.InformedCharacterModifier(f"{DarkKnightSkills.FinalPact.value}(Buff | 패시브)",pdamage_indep = 30 + passive_level, crit = 10 + ceil(passive_level / 3), crit_damage = 15 + passive_level // 3)
        ReincarnationHyper = core.InformedCharacterModifier(DarkKnightSkills.FinalPactCriticalChance.value, crit = 20)
    
        SacrificePassive = core.InformedCharacterModifier(f"{DarkKnightSkills.Sacrifice.value}(Passive | 패시브)",armor_ignore = 30)
        CrossoverChainPassive = core.InformedCharacterModifier(f"{DarkKnightSkills.CrossSurge.value}(Passive | 패시브)", pdamage_indep=50)
        return [WeaponMastery, PhisicalTraining, LordOfDarkness, AdvancedWeaponMastery, ReincarnationBuff, ReincarnationHyper, SacrificePassive, CrossoverChainPassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 49)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=90+ceil(passive_level / 2))
        BiholdersBuff = core.InformedCharacterModifier(DarkKnightSkills.HexoftheEvilEye.value, att=40, crit=10)
        
        return [WeaponConstant, Mastery, BiholdersBuff]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Window use
        Croce Fulpie Assumption
        Beholder-Reinforce
        Reincarnation-Damage, Critical Rate
        Goongnil-Reinforce, Ignor Guard

        Beholder Impact 9 strokes
        Pierce Cyclone 25 strokes
        Dark Sphere 8 Hit

        Impale-Gungnil-Beholder-Final Attack

        창 사용
        크오체 풀피 가정
        비홀더 - 리인포스
        리인카네이션 - 데미지, 크리티컬 레이트
        궁그닐 - 리인포스, 이그노어 가드
        
        비홀더 임팩트 9타
        피어스 사이클론 25타
        다크 스피어 8히트
        
        임페일-궁그닐-비홀더-파이널어택
        '''

        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        #Buff skills
        Booster = core.BuffSkill(DarkKnightSkills.WeaponBooster.value, 0, 180*1000, rem = True).wrap(core.BuffSkillWrapper)  # Pet Buff. 펫버프.
        CrossoverChain = core.BuffSkill(DarkKnightSkills.CrossSurge.value, 0, 200*1000, pdamage_indep = 20).wrap(core.BuffSkillWrapper)  # Pet Buff. 펫버프.
        FinalAttack = core.DamageSkill(DarkKnightSkills.FinalAttack.value, 0, 80, 2*0.4).setV(vEhc, 3, 4, True).wrap(core.DamageSkillWrapper)
        BiholderDominant = core.SummonSkill(DarkKnightSkills.EvilEyeofDomination.value, 0, 10000, 210, 1, 99999*10000, modifier = core.CharacterModifier(pdamage = 150)).setV(vEhc, 2, 3, False).wrap(core.SummonSkillWrapper)
        BiholderShock = core.DamageSkill(DarkKnightSkills.EvilEyeShock.value, 0, 215+300 + 5 * passive_level, 6, cooltime = 12000, red=True, modifier = core.CharacterModifier(pdamage = 150)).setV(vEhc, 2, 3, False).wrap(core.DamageSkillWrapper)
        
        DarkImpail = core.DamageSkill(DarkKnightSkills.DarkImpale.value, 630, 280 + 4 * self.combat, 5 + (30 + self.combat) // 16).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)

        GOUNGNIL_MODIFIER = core.CharacterModifier(armor_ignore = 30 + self.combat) + core.CharacterModifier(armor_ignore = 20, pdamage = 20)
        GoungnilDescentNoCooltime = core.DamageSkill(f"{DarkKnightSkills.GungnirsDescent.value}(Infinite | 무한)", 600, 225 + self.combat, 12, modifier = GOUNGNIL_MODIFIER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        GoungnilDescent = core.DamageSkill(DarkKnightSkills.GungnirsDescent.value, 600, 225 + self.combat, 12, cooltime = 8000, red=True, modifier = GOUNGNIL_MODIFIER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        Sacrifice = core.BuffSkill(DarkKnightSkills.Sacrifice.value, 1080, (30 + self.combat // 2)*1000, rem = True, red = True, cooltime = 70000, armor_ignore = 10 + self.combat // 3, boss_pdamage = 10 + self.combat // 3).wrap(core.BuffSkillWrapper)   # Ignores the cool cool, decreases the cool by 0.3 when attacking the beholder. 궁그닐 쿨 무시, 비홀더 공격시 쿨0.3감소.
        Reincarnation = core.BuffSkill(DarkKnightSkills.FinalPact.value, 0, (40+passive_level)*1000, cooltime = (900 - 7 * passive_level) * 1000, rem = True, red = True, pdamage_indep=30).wrap(core.BuffSkillWrapper)  # Ignore cooldown. 궁그닐 쿨 무시.
        
        # Hypers. 하이퍼.
        DarkThurst = core.BuffSkill(DarkKnightSkills.DarkThirst.value, 900, 30000, cooltime = 120*1000, att = 80).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill(DarkKnightSkills.EpicAdventure.value, 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        # 5th. 5차.
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        DarkSpear = core.DamageSkill(DarkKnightSkills.SpearofDarkness.value, 750, 350+10*vEhc.getV(1,0), 7*10, cooltime = 10000, red = True, modifier = core.CharacterModifier(crit=100, armor_ignore=50)).isV(vEhc,1,0).wrap(core.DamageSkillWrapper)
        BiholderImpact = core.SummonSkill(DarkKnightSkills.RadiantEvil.value, 0, 270, 100+vEhc.getV(0,2), 6, 2880, cooltime = 20000, red = True, modifier = core.CharacterModifier(pdamage = 150)).setV(vEhc, 2, 3, False).isV(vEhc,0,2).wrap(core.SummonSkillWrapper) # 0.3 seconds each with onTick. onTick으로 0.3초씩.
        PierceCyclone = core.DamageSkill(f"{DarkKnightSkills.CalamitousCyclone.value}(Dummy | 더미)", 90, 0, 0, cooltime = 180*1000, red = True).wrap(core.DamageSkillWrapper)
        PierceCycloneTick = core.DamageSkill(DarkKnightSkills.CalamitousCyclone.value, 360, 400+16*vEhc.getV(3,3), 12, modifier = core.CharacterModifier(crit=100, armor_ignore = 50)).isV(vEhc,3,3).wrap(core.DamageSkillWrapper) # 25 strokes. 25타.
        PierceCycloneEnd = core.DamageSkill(f"{DarkKnightSkills.CalamitousCyclone.value}(Ending | 종료)", 900, 300+12*vEhc.getV(3,3), 15*5, modifier = core.CharacterModifier(crit=100, armor_ignore = 50)).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        DarknessAura = core.SummonSkill(DarkKnightSkills.DarknessAura.value, 600, 1530, 400+16*vEhc.getV(0,0), 5, 40000, cooltime=180*1000, red=True).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        DarknessAuraFinal = core.DamageSkill(f"{DarkKnightSkills.DarknessAura.value}(Explosion | 폭발)", 0, 650+25*vEhc.getV(0,0), 13*(1+15//3), cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper) # Adds 1 explosion every 3 health, maximum health 15. 생명력 3마다 폭발 1회 추가, 생명력 최대 15.
        
        ######   Skill Wrapper   ######
    
        #Damage skill
    
        Reincarnation.set_disabled_and_time_left(30000)
        Reincarnation.onAfter(Reincarnation.controller(300*1000, 'reduce_cooltime'))
        
        def InfGoungnil():
            return (Sacrifice.is_active() or Reincarnation.is_active())
        
        DarkImpail.onAfter(FinalAttack)
        GoungnilDescentNoCooltime.onAfter(FinalAttack)
        GoungnilDescent.onAfter(FinalAttack)
        GoungnilDescent.onConstraint(core.ConstraintElement("Sacrifice | 새크리 OFF", Sacrifice, Sacrifice.is_not_active))
        GoungnilDescent.onConstraint(core.ConstraintElement("Final Pact | 리인카 OFF", Reincarnation, Reincarnation.is_not_active))
        BasicAttack = core.OptionalElement(InfGoungnil, GoungnilDescentNoCooltime, DarkImpail)
        BasicAttackWrapped = core.DamageSkill('Basic attack | 기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapped.onAfter(BasicAttack)
        BiholderDominant.onTick(Sacrifice.controller(300,'reduce_cooltime'))
        BiholderShock.onAfter(Sacrifice.controller(300,'reduce_cooltime'))
        BiholderImpact.onTick(Sacrifice.controller(300,'reduce_cooltime'))
        
        PierceCycloneTick.onAfter(FinalAttack)
        PierceCycloneEnd.onAfter(core.RepeatElement(FinalAttack, 5))
        PierceCyclone_ = core.RepeatElement(PierceCycloneTick, 25)
        PierceCyclone_.onAfter(PierceCycloneEnd)
        PierceCyclone.onAfter(PierceCyclone_)

        DarknessAura.onEventEnd(DarknessAuraFinal)

        # Weapon Aura. 오라 웨폰.
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 1)
        for sk in [GoungnilDescent, GoungnilDescentNoCooltime, DarkImpail, PierceCycloneEnd]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()
        
        return(BasicAttackWrapped, 
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    Booster, CrossoverChain, Sacrifice, Reincarnation, EpicAdventure, DarkThurst, AuraWeaponBuff, AuraWeapon,
                    globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()] +\
                [DarknessAura, DarknessAuraFinal, BiholderShock, GoungnilDescent, DarkSpear, PierceCyclone, MirrorBreak, MirrorSpider] +\
                [BiholderDominant, BiholderImpact] +\
                [BasicAttackWrapped])