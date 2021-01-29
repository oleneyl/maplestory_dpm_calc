from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule
from . import globalSkill
from .jobbranch import pirates
from .jobclass import nova
from . import jobutils
from math import ceil
from typing import Any, Dict

def getAffinityIV(duration): # TODO: 와헌 어나더 바이트처럼 실시간 계산
    """
    어피니티IV의 지속시간은 5000ms
    평균 리차지 주기에 따라 5000ms 사이에 n회, n+1회 공격할 확률을 각각 구한 다음
    리차지가 5000ms동안 전부 실패할 확률을 계산해 가동률을 구합니다.
    """
    count = 5000 // duration
    timeDiv = 5000 - duration * count
    prob = timeDiv / duration
    ratio = (1 - prob) * (1 - 0.5 ** count) + prob * (1 - 0.5 ** (count + 1))
    return core.InformedCharacterModifier("어피니티 IV", pdamage = 30 * ratio)

class JobGenerator(ck.JobGenerator):
    def __init__(self, vEhc = None):
        super(JobGenerator, self).__init__(vEhc = vEhc)
        self.jobtype = "DEX"
        self.jobname = "엔젤릭버스터"
        self.vEnhanceNum = 12
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        
        self.preEmptiveSkills = 2

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('소울 컨트랙트', '스포트라이트'), RuleSet.BASE)
        return ruleset
    
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        SoulShooterMastery = core.InformedCharacterModifier("소울슈터 마스터리", att = 20)
        InnerFire = core.InformedCharacterModifier("이너 파이어", stat_main = 40)
        
        CallOfAncient = core.InformedCharacterModifier("콜 오브 에인션트", att = 40)
        AffinityIII = core.InformedCharacterModifier("어피니티 III", stat_main = 40, pdamage = 20)
        AffinityIV = getAffinityIV(1272.08) # 트리니티 평균 주기가 바뀔 때 마다 변경해 줘야함. 1000 * time(초) / (트리니티 사용 횟수).
        TrinityPassive = core.InformedCharacterModifier("트리니티(패시브)", pdamage_indep = ceil((30 + self.combat) / 3), armor_ignore = ceil((30 + self.combat) / 2))
        SoulShooterExpert = core.InformedCharacterModifier("소울슈터 엑스퍼트", att = 30 + passive_level, crit = 30 + passive_level, crit_damage = 15 + ceil(passive_level / 2))
        
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 1, 2)
        TrinityFusionPassive = core.InformedCharacterModifier("트리니티 퓨전(패시브)", stat_main = 10 + vEhc.getV(0,0))
    
        return [SoulShooterMastery, InnerFire,
                            CallOfAncient, AffinityIII, AffinityIV, TrinityPassive, SoulShooterExpert,
                            LoadedDicePassive, TrinityFusionPassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 70)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -2.5 + 0.5 * ceil(passive_level / 2))
        
        return [WeaponConstant, Mastery]        

    def get_modifier_optimization_hint(self) -> core.CharacterModifier:
        return core.CharacterModifier(boss_pdamage=60, armor_ignore=18.4)
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        어피니티IV 가동률 94.18%
        트리니티 버프 지속시간 갱신불가 적용
        
        하이퍼 : 소울시커-메이크업/리인포스, 피나투라페투치아-쿨리듀스
        트리니티 - 리인포스/스플릿데미지
        
        스포트라이트 히트 3, 공격주기 800ms
        패밀리어 공격속도 2.5초당 1타
        
        시커 1개당 타수
        : 95% 재생성, 최대6회 : 1 + 0.95 + 0.95*0.95 + ... + (6타) = 6.033타
        샤이니 버블 브레스 
        : 지속시간 3초 210ms당 1타(3초당 14타) 버블당 0.4초 버블은 최대8개
        
        코강 : (12개)
        트리니티 / 프라이멀 로어 / 시커
        슈퍼노바 / 피나투라 / 레조넌스
        
        코강 우선순위
        (쓸윈부 / 쓸샾) + (스포트라이트 + 로디드 다이스 + 에너지 버스트 + 오버 드라이브)
        + 트리니티 / 프라이멀 / 시커 / 노바 / 피나투라 / 레조넌스
        
        '''
        
        SPOTLIGHTHIT = options.get('spotlight', 3)
        TRINITY_MDF = core.CharacterModifier(pdamage = 20) + core.CharacterModifier(pdamage = 10*3, armor_ignore = 10*3) # 하이퍼 리인포스 + 3중첩
        
        #Buff skills
        Booster = core.BuffSkill("리리컬 크로스", 0, 200*1000).wrap(core.BuffSkillWrapper)
        
        SoulContract = core.BuffSkill("소울 컨트랙트", 600, 10000, rem = True, red = True, cooltime = 90000, pdamage = 90).wrap(core.BuffSkillWrapper)
        SoulSeekerExpert = core.DamageSkill("소울 시커", 0, 320 * 0.75, 1 * 0.01 * (35+self.combat) * 12.066, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        SoulSeekerExpert_PR = core.DamageSkill("소울 시커(소울 익절트)", 0, 320 * 0.75, 1 * 0.01 * (50+self.combat) * 12.066, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        
        # -70은 스플릿 어택
        TRINITY_DAMAGE = 360 + 12 * (30 + self.combat) - 70
        Trinity_1 = core.DamageSkill("트리니티", 360, TRINITY_DAMAGE, 2+1, modifier = TRINITY_MDF).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Trinity_2 = core.DamageSkill("트리니티(2타)", 360, TRINITY_DAMAGE, 3+1, modifier = TRINITY_MDF).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        Trinity_3 = core.DamageSkill("트리니티(3타)", 360, TRINITY_DAMAGE, 4+1, modifier = TRINITY_MDF).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        
        FinaturaFettuccia = core.DamageSkill("피니투라 페투치아", 1020, 400 + 7*self.combat, 10, red = True, cooltime = 40000*0.75).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        FinaturaFettucciaBuff = core.BuffSkill("피니투라 페투치아(버프)", 0, 20000, cooltime = -1, pdamage_indep=25).wrap(core.BuffSkillWrapper)
        
        SoulGaze = core.BuffSkill("소울 게이즈", 1080, (180 + 5 * self.combat) * 1000, rem = True, crit_damage = 45 + self.combat).wrap(core.BuffSkillWrapper)
        
        #하이퍼
        SoulExult = core.BuffSkill("소울 익절트", 1020, 30000, armor_ignore = 30, boss_pdamage = 20, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)
        SuperNova = core.SummonSkill("슈퍼 노바", 600, 840, 600, 3, 12000, cooltime = 60 * 1000).setV(vEhc, 2, 2, True).wrap(core.SummonSkillWrapper)  #840ms 타격(14타)
        FinalContract = core.BuffSkill("파이널 컨트랙트", 0, 30000, cooltime = 120 * 1000, att = 50, crit = 30).wrap(core.BuffSkillWrapper)
        
        #로디드 데미지 고정.
        LuckyDice = core.BuffSkill("로디드 다이스", 0, 180*1000, pdamage = 20).isV(vEhc,1,2).wrap(core.BuffSkillWrapper)
        
        WEAPON_ATT = jobutils.get_weapon_att(chtr)
        Overdrive = pirates.OverdriveWrapper(vEhc, 3, 3, WEAPON_ATT)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        NovaGoddessBless = nova.NovaGoddessBlessWrapper(vEhc, 0, 0)
        Phanteon = nova.PantheonWrapper(vEhc, 0, 0)
    
        EnergyBurst = core.DamageSkill("에너지 버스트", 900, (450+18*vEhc.getV(4,4)) * 3, 15, red = True, cooltime = 120 * 1000).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
        
        SpotLight = core.SummonSkill("스포트라이트", 990, 800, 400+16*vEhc.getV(0,0), 3 * SPOTLIGHTHIT, 30000, cooltime = 120 * 1000, red=True).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        SpotLightBuff = core.BuffSkill("스포트라이트(버프)", 0, 30000, cooltime = -1, crit = (10+int(0.2*vEhc.getV(0,0)))*SPOTLIGHTHIT,
                                                                                pdamage_indep = (3+(vEhc.getV(0,0)//10))*SPOTLIGHTHIT).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        
        MascortFamilier = core.BuffSkill("마스코트 패밀리어", 810, 30+(vEhc.getV(2,1)//5)*1000, red = True, cooltime = 120 * 1000).isV(vEhc,2,1).wrap(core.BuffSkillWrapper)
        MascortFamilierAttack = core.SummonSkill("트윙클 스타/매지컬 벌룬", 0, 2500, 1200, 5, (30+(vEhc.getV(2,1)//5))*1000, cooltime = -1).isV(vEhc,2,1).wrap(core.SummonSkillWrapper)
        ShinyBubbleBreath = core.SummonSkill("샤이니 버블 브레스", 0, 210, 250+10*vEhc.getV(2,1), 7, (3 + 0.4*8)*1000, cooltime = -1).isV(vEhc,2,1).wrap(core.SummonSkillWrapper)

        # 이전 트리니티 딜레이를 150ms만큼 캔슬함. TODO: 트리니티(캔슬) 만들고 퓨전 660ms로 할것
        TrinityFusionInit = core.DamageSkill("트리니티 퓨전(시전)", 660-150, 0, 0, cooltime=(16-vEhc.getV(0,0)//10)*1000, red=True).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        TrinityFusion = core.DamageSkill("트리니티 퓨전", 0, 330+vEhc.getV(0,0), 3, cooltime=-1, modifier = TRINITY_MDF).setV(vEhc, 0, 2, True).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        ### build graph relationships
    
        Trinity_1.onAfter(Trinity_2)
        Trinity_2.onAfter(Trinity_3)
        Trinity_3.onAfter(core.OptionalElement(TrinityFusionInit.is_available, TrinityFusionInit))
        TrinityFusionInit.protect_from_running()

        TrinityFusionInit.onAfter(core.RepeatElement(TrinityFusion, 9))
    
        FinaturaFettuccia.onAfter(FinaturaFettucciaBuff)
        SpotLight.onAfter(SpotLightBuff)
        MascortFamilier.onAfter(MascortFamilierAttack)
        MascortFamilier.onEventEnd(ShinyBubbleBreath)
        
        SoulSeeker = core.OptionalElement(SoulExult.is_active, SoulSeekerExpert_PR, SoulSeekerExpert)
        
        #극딜기 싱크로
        #SoulContract.onConstraint(core.ConstraintElement("익절트와 함께", SoulExult, SoulExult.is_active))
        
        for sk in [Trinity_1, Trinity_2, Trinity_3, TrinityFusion, FinaturaFettuccia, EnergyBurst]:
            sk.onAfter(SoulSeeker)
        
        SuperNova.onTick(SoulSeeker)
        #SuperNova.onConstraint(core.ConstraintElement("익절트와 함께", SoulExult, SoulExult.is_active))

        TandadianRuin, AeonianRise = globalSkill.GenesisSkillBuilder()

        return (
            Trinity_1,
            [
                globalSkill.maple_heros(chtr.level, name = "노바의 용사", combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                globalSkill.useful_wind_booster(),
                Booster,
                SoulGaze,
                LuckyDice,
                NovaGoddessBless,
                MascortFamilier,
                FinalContract,
                SoulExult,
                Overdrive,
                SoulContract,
                FinaturaFettucciaBuff,
                SpotLightBuff,
                TandadianRuin,
            ] +
            [FinaturaFettuccia, EnergyBurst, MirrorBreak, MirrorSpider, AeonianRise] +
            [SuperNova, MascortFamilierAttack, ShinyBubbleBreath, SpotLight, TrinityFusionInit, Phanteon] +
            [Trinity_1]
        )
