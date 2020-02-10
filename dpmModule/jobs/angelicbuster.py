from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import pirates

class JobGenerator(ck.JobGenerator):
    def __init__(self, vEhc = None):
        super(JobGenerator, self).__init__(vEhc = vEhc)
        self.jobtype = "dex"
        self.vEnhanceNum = 12
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        
        self.preEmptiveSkills = 2
    
    def get_passive_skill_list(self):
        vEhc = self.vEhc
        SoulShooterMastery = core.InformedCharacterModifier("소울슈터 마스터리", att = 20)
        InnerFire = core.InformedCharacterModifier("이너 파이어", stat_sub = 40)
        
        CallOfAncient = core.InformedCharacterModifier("콜 오브 에인션트", att = 40)
        AffinityIII = core.InformedCharacterModifier("어피니티 III", stat_main = 40, pdamage = 20)
        AffinityIV = core.InformedCharacterModifier("어피니티 IV", pdamage = 30)
        TrinityPassive = core.InformedCharacterModifier("트리니티(패시브)", pdamage_indep = 10, armor_ignore = 15)
        SoulShooterExpert = core.InformedCharacterModifier("소울슈터 엑스퍼트", att = 30, crit = 30, crit_damage = 15)
        
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 1, 2)
    
        return [SoulShooterMastery, InnerFire,
                            CallOfAncient, AffinityIII, AffinityIV, TrinityPassive, SoulShooterExpert,
                            LoadedDicePassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -2.5)        
        
        return [WeaponConstant, Mastery]        
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        트리니티 버프는 2.8중첩으로 계산
        
        하이퍼 : 소울시커-메이크업, 피나투라페투치아-인핸스/쿨리듀스
        트리니티 - 리인포스/스플릿데미지
        
        스포트라이트 히트 3, 공속 1500ms
        패밀리어 공격속도 2.5초당 1타
        
        95% 재생성, 최대6회 : 1 + 0.95 + 0.95*0.95 + ... + (6타) = 6.03타
        
        어피니티IV의 리차지시 50%로성공을 항시적용
        샤이니 버블 브레스 
        : 지속시간 3초 210ms당 1타(3초당 14타) 버블당 0.4초 버블은 최대8개
        
        코강 : (12개)
        트리니티 / 프라이멀 로어 / 시커
        슈퍼노바 / 피나투라 / 레조넌스
        
        코강 우선순위
        (쓸윈부 / 쓸샾) + (스포트라이트 + 로디드 다이스 + 에너지 버스트 + 오버 드라이브)
        + 트리니티 / 프라이멀 / 시커 / 노바 / 피나투라 / 레조넌스
        
        '''
        
        SPOTLIGHTHIT = 3
        
        #Buff skills
        Booster = core.BuffSkill("리리컬 크로스", 0, 200*1000).wrap(core.BuffSkillWrapper)
        
        SoulContract = core.BuffSkill("소울 컨트랙트", 600, 10000, rem = True, red = True, cooltime = 90000, pdamage = 90).wrap(core.BuffSkillWrapper)
        SoulSeekerExpert = core.DamageSkill("소울 시커", 0, 320 * 0.75, 1 * 0.35 * 6.03).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        SoulSeekerExpert_PR = core.DamageSkill("소울 시커(프라이멀 로어)", 0, 320 * 0.75, 1 * 0.5 * 6.03).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        
        Trinity_1 = core.DamageSkill("트리니티", 470, 650, 2+1, modifier = core.CharacterModifier(pdamage =20, armor_ignore=20) +core.CharacterModifier(pdamage =28, armor_ignore=28)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper, name = "트리니티(1타)")
        Trinity_2 = core.DamageSkill("트리니티(2타)", 470, 650, 3+1, modifier = core.CharacterModifier(pdamage =20, armor_ignore=20) +core.CharacterModifier(pdamage =28, armor_ignore=28)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper, name = "트리니티(2타)")
        Trinity_3 = core.DamageSkill("트리니티(3타)", 470-340, 650, 4+1, modifier = core.CharacterModifier(pdamage =20, armor_ignore=20) +core.CharacterModifier(pdamage =28, armor_ignore=28)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper, name = "트리니티(3타)")
        
        FinaturaFettuccia = core.DamageSkill("피나투라 페투치아", 1020, 4000, 1, red = True, cooltime = 40000*0.75).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        FinaturaFettucciaBuff = core.BuffSkill("피나투라 페투치아(버프)", 0, 20000, cooltime = -1, pdamage_indep=25, armor_ignore=15).wrap(core.BuffSkillWrapper)
        
        SoulGaze = core.BuffSkill("소울 게이즈", 1080, 180000, rem = True, crit_damage = 45).wrap(core.BuffSkillWrapper)
        
        #하이퍼
        SoulExult = core.BuffSkill("소울 익절트", 1020, 30000, armor_ignore = 30, boss_pdamage = 20, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)
        SuperNova = core.SummonSkill("슈퍼 노바", 600, 840, 600, 3, 12000, cooltime = 60 * 1000).setV(vEhc, 2, 2, True).wrap(core.SummonSkillWrapper)  #840ms 타격(14타)
        FinalContract = core.BuffSkill("파이널 컨트랙트", 0, 30000, cooltime = 120 * 1000, att = 50, crit = 30).wrap(core.BuffSkillWrapper)
        
        #로디드 데미지 고정.
        LuckyDice = core.BuffSkill("럭키 다이스", 0, 180*1000, pdamage = 20).isV(vEhc,1,2).wrap(core.BuffSkillWrapper)
        
        #오버드라이브 (앱솔 가정)
        #TODO: 템셋을 읽어서 무기별로 다른 수치 적용하도록 만들어야 함.
        WEAPON_ATT = 154
        OverdriveBuff = pirates.OverdriveWrapper(vEhc, WEAPON_ATT, 3, 3)
        Overdrive = OverdriveBuff.Overdrive
        OverdrivePenalty = OverdriveBuff.OverdrivePenalty
    
        EnergyBurst = core.DamageSkill("에너지 버스트", 900, (600+20*vEhc.getV(4,4)) * 3, 12, red = True, cooltime = 120 * 1000).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
        
        SpotLight = core.SummonSkill("스포트라이트", 990, 1800, 400+16*vEhc.getV(0,0), 3 * SPOTLIGHTHIT, 30000, cooltime = 120 * 1000).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        SpotLightBuff = core.BuffSkill("스포트라이트(버프)", 0, 30000, cooltime = -1, crit = (10+int(0.2*vEhc.getV(0,0)))*SPOTLIGHTHIT,
                                                                                pdamage_indep = (3+(vEhc.getV(0,0)//10))*SPOTLIGHTHIT).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        
        MascortFamilier = core.BuffSkill("마스코트 패밀리어", 1080, 30+(vEhc.getV(2,1)//5)*1000, red = True, cooltime = 120 * 1000).isV(vEhc,2,1).wrap(core.BuffSkillWrapper)
        MascortFamilierAttack = core.SummonSkill("트윙클 스타/매지컬 벌룬", 0, 2500, 1200, 5, (30+(vEhc.getV(2,1)//5))*1000, cooltime = -1).isV(vEhc,2,1).wrap(core.SummonSkillWrapper)
        ShinyBubbleBreath = core.SummonSkill("샤이니 버블 브레스", 0, 210, 250+10*vEhc.getV(2,1), 7, (3 + 0.4*8)*1000, cooltime = -1).isV(vEhc,2,1).wrap(core.SummonSkillWrapper)
        ### build graph relationships
    
        Trinity_1.onAfter(Trinity_2)
        Trinity_2.onAfter(Trinity_3)
    
        FinaturaFettuccia.onAfter(FinaturaFettucciaBuff)
        SpotLight.onAfter(SpotLightBuff)
        MascortFamilier.onAfter(MascortFamilierAttack)
        MascortFamilier.onAfter(ShinyBubbleBreath.controller((30+(vEhc.getV(2,1)//5))*1000))
        
        SoulSeeker = core.OptionalElement(SoulExult.is_active, SoulSeekerExpert_PR, SoulSeekerExpert)
        
        #극딜기 싱크로
        #SoulContract.onConstraint(core.ConstraintElement("익절트와 함께", SoulExult, SoulExult.is_active))
        
        for sk in [Trinity_1, Trinity_2, Trinity_3, FinaturaFettuccia, EnergyBurst]:
            sk.onAfter(SoulSeeker)
        
        SuperNova.onTick(SoulSeeker)
        #SuperNova.onConstraint(core.ConstraintElement("익절트와 함께", SoulExult, SoulExult.is_active))
        Overdrive.onAfter(OverdrivePenalty.controller(30*1000))
        
    
        return (Trinity_1,
                [Booster, SoulGaze, LuckyDice, FinalContract,
                    SoulExult, SoulContract,Overdrive, OverdrivePenalty,
                    FinaturaFettucciaBuff, SpotLightBuff, MascortFamilier,
                    globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster()] +\
                [FinaturaFettuccia, EnergyBurst] +\
                [SuperNova, MascortFamilierAttack, ShinyBubbleBreath, SpotLight] +\
                [] +\
                [Trinity_1])