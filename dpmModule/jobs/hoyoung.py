from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConditionRule
from . import globalSkill
from .jobbranch import thieves
from math import ceil
'''
이 코드는 아직 미완성입니다.

TODO : 스킬 딜레이, 딜사이클

TODO: 하이퍼 패시브 적용
    천지인 리인포스, 보스 킬러
    추적 귀화부 헤이스트
    흡성와류 헤이스트
    호접지몽 보스킬러

TODO: 작성 완료 후 다른 직업들과 비슷한 스타일로 순서 재정리

TODO: 하이퍼 & 5차는 클라기준 공속이므로 확인필요

TODO: 환영 분신부, 권술 : 호접지몽은 벞지, 소환수 동시적용
'''

def AnimaGoddessBlessWrapper(vEhc, num1, num2):
    AnimaGoddessBless = core.BuffSkill("그란디스 여신의 축복 (아니마)", 0, 40*1000, cooltime = 240*1000, pdamage = 10 + vEhc.getV(num1, num2), rem = False).wrap(core.BuffSkillWrapper)
    return AnimaGoddessBless

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "luk"
        self.jobname = "호영"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'buff_rem', 'mess')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 40)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        FiendSeal = core.InformedCharacterModifier("괴이봉인", patt = 10, pdamage_indep = 10)
        RitualFanMastery = core.InformedCharacterModifier("부채 숙련", att = 25)
        ThirdEye = core.InformedCharacterModifier("심안", crit = 30, crit_damage = 10)
        FortuneFitness = core.InformedCharacterModifier("신체 단련", stat_main = 60)
        Asura = core.InformedCharacterModifier("수라", att = 50, crit = 10, crit_damage = 20, boss_pdamage = 20, armor_ignore = 20)
        AdvancedRitualFanMastery = core.InformedCharacterModifier("고급 부채 숙련", att = 40 + passive_level, pdamage_indep = 35 + passive_level)
        Enlightenment = core.InformedCharacterModifier("득도", pdamage = 10 + ceil(passive_level/2))
        DragonsEye = core.InformedCharacterModifier("점정", att = 10 + passive_level, pdamage_indep = 10 + passive_level, crit = 10 + passive_level, crit_damage = 10 + passive_level, armor_ignore = 10 + passive_level)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 0, 0)

        return [FiendSeal, RitualFanMastery, ThirdEye, FortuneFitness, Asura, AdvancedRitualFanMastery, Enlightenment, DragonsEye, ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -5+0.5*ceil(passive_level/2))    #오더스 기본적용!
        SpiritAffinity = core.BuffSkill("정령친화", 0, 999999).wrap(core.BuffSkillWrapper) # 더미
        return [WeaponConstant, Mastery, SpiritAffinity]
    
    '''
    def get_ruleset(self):
        return ruleset
    '''

    def generate(self, vEhc, chtr : ck.AbstractCharacter):

        passive_level = chtr.get_base_modifier().passive_level + self.combat
        SUMMON_REMAIN = 1 #+ chtr.get_base_modifier().summon_rem + 0.1
        BASIC_HYPER = core.CharacterModifier(pdamage = 10, boss_pdamage = 15)
        
        # 1차
        #부채 타격 가정
        YeoUiSeon = core.DamageSkill("여의선 : 인", 540, 525 + 5*passive_level, 5, modifier = BASIC_HYPER + core.CharacterModifier(pdamage_indep = 10)).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        MaBong = core.DamageSkill("마봉 호로부", 360, 1000 + 10 * passive_level, 6, cooltime = -1, modifier = core.CharacterModifier(boss_pdamage = 20)).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)

        # 2차
        Topa = core.DamageSkill("토파류 : 지", 540, 385 + 5*passive_level, 4, modifier = BASIC_HYPER).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Topa_Clone = core.DamageSkill("토파류 : 허/실", 0, 385 + 5*passive_level, 4, cooltime = -1, modifier = BASIC_HYPER).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Topa.onAfter(Topa_Clone)

        # 스킬 설명에 확률이 명시되어 있지 않음.
        TALISMAN_PROBABLITY = 1
        
        # 벞지 & 소환수 지속시간 둘다 적용
        Talisman_Clone = core.BuffSkill("환영 분신부", 690, 200*1000).wrap(core.BuffSkillWrapper)
        Talisman_Clone_Attack = core.DamageSkill("환영 분신부 (공격)", 0, 460 + 5*passive_level, 2 * 3 * TALISMAN_PROBABLITY, cooltime = 1500).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        # 다른 공격스킬에 onAfter로 연결
        Talisman_Clone_Attack_Opt = core.OptionalElement(lambda : Talisman_Clone.is_active() and Talisman_Clone_Attack.is_usable(), Talisman_Clone_Attack)

        # 펫버프로 이용가능
        Booster = core.BuffSkill("부채 가속", 450, 200*1000).wrap(core.BuffSkillWrapper)

        # 3차

        Pacho = core.DamageSkill("파초풍 : 천", 510, 265 + 2*passive_level, 5, modifier = BASIC_HYPER).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Pacho_Clone = core.DamageSkill("파초풍 : 허/실", 0, 265 + 2*passive_level, 5, modifier = BASIC_HYPER, cooltime = -1).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Pacho.onAfter(Pacho_Clone)

        EarthQuake = core.DamageSkill("지진쇄 : 지", 510, 390 + 5*passive_level, 6, modifier = BASIC_HYPER, cooltime = 6000).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        EarthQuake_Clone = core.DamageSkill("지진쇄 : 허/실", 0, 390 + 5*passive_level, 6, modifier = BASIC_HYPER, cooltime = -1).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        EarthQuake.onAfter(EarthQuake_Clone)

        Talisman_Seeker = core.SummonSkill("추적 귀화부", 480, 1800 * 0.75, 390 + 5*passive_level, 5, 40*1000*SUMMON_REMAIN).setV(vEhc, 0, 0, False).wrap(core.SummonSkillWrapper)

        Misaeng = core.DamageSkill("권술 : 미생강변", 540, 850 + (6+4)*self.combat, 8, modifier = core.CharacterModifier(boss_pdamage = 20)).setV(vEhc, 0, 0, False).wrap(core.SummonSkillWrapper)
        Misaeng_Debuff = core.BuffSkill("권술 : 미생강변 (디버프)", 0, 60*1000, armor_ignore = 20).wrap(core.BuffSkillWrapper)
        # 미생강변 발동을 디버프에 위임
        Misaeng.protect_from_running()
        Misaeng_Debuff.onAfter(Misaeng)

        # 4차
        Flames = core.DamageSkill("멸화염 : 천", 420, 340 + self.combat, 6, modifier = BASIC_HYPER, cooltime = 8000).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Flames_Clone = core.DamageSkill("멸화염 : 허/실", 420, 340 + self.combat, 6, modifier = BASIC_HYPER, cooltime = -1).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Flames.onAfter(Flames_Clone)

        GeumGoBong = core.DamageSkill("금고봉 : 인 (1타)", 450, 260 + 3*self.combat, 10, cooltime = 11000, modifier = BASIC_HYPER + core.CharacterModifier(boss_pdamage = 30)).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        GeumGoBong_2 = core.DamageSkill("금고봉 : 인 (2타)", 0, 420 + self.combat, 8, cooltime = -1, modifier = BASIC_HYPER + core.CharacterModifier(boss_pdamage = 30)).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        GeumGoBong.onAfter(GeumGoBong_2)

        # 추정치 딜레이 (점프부터 이펙트 완전소멸까지 프레임 분석)
        Thousand_Ton_Stone = core.DamageSkill("둔갑 천근석", 1530, 275 + 3*self.combat, 6, cooltime = 500).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Thousand_Ton_Stone_DOT = core.DotSkill("둔갑 천근석 (출혈)", 0, 1000, 270 + self.combat, 1, 10000, cooltime = -1).setV(vEhc, 0, 0, False).wrap(core.SummonSkillWrapper)
        Thousand_Ton_Stone.onAfter(Thousand_Ton_Stone_DOT)

        Waryu = core.SummonSkill("권술 : 흡성와류", 750, 1000 * 0.8, 240 + 4*self.combat, 6, 40000).setV(vEhc, 0, 0, False).wrap(core.SummonSkillWrapper)
        
        # TODO: 벞지 & 소환수 지속시간 둘다 적용
        Butterfly_Dream = core.BuffSkill("권술 : 호접지몽", 450, 100*1000, pdamage_indep = 10).wrap(core.BuffSkillWrapper)
        Butterfly_Dream_Attack = core.DamageSkill("권술 : 호접지몽 (공격)", 0, 275 + 3 * self.combat, 5, modifier = core.CharacterModifier(boss_pdamage = 20), cooltime = 1000).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Butterfly_Dream_Attack_Opt = core.OptionalElement(Butterfly_Dream_Attack.is_usable(), Butterfly_Dream_Attack)

        '''
        하이퍼 액티브
        몽유도원은 딜스킬이 아님
        TODO: 태을선인의 딜사이클 포함여부 확인
        '''

        Miracle_Tonic = core.BuffSkill("선기 : 영약 태을선단", 540, 12*1000, cooltime = 100*1000, rem = False, red = False).wrap(core.BuffSkillWrapper)
        

        # 5차 공용 (베놈 버스트 생략)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 0, 0)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # 그란디스 여신의 축복 (아니마)
        # 아니마 신직업 등장시 공용코드화 할것
        AnimaGoddessBless = AnimaGoddessBlessWrapper(vEhc, 0, 0)

        # 환영 분신부를 대체하는 스킬 (알고리즘 구현 필요)
        # 환영 분신부 지속중에만 사용가능, 발동 중에는 환영 분신부의 지속시간이 감소하지 않음
        Clone_Rampage = core.BuffSkill("선기 : 극대 분신난무", 900, 30*1000, cooltime = 200*1000).wrap(core.BuffSkillWrapper)
        Clone_Rampage_Attack = core.DamageSkill("선기 : 극대 분신난무 (공격)", 0, vEhc.getV(0, 0) * 16 + 400, 2 * 12 * TALISMAN_PROBABLITY, cooltime = 12*1000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        # TODO: 연계 딜사이클 만들것
        Summon_Sanryung = core.BuffSkill("권술 : 산령소환", 900, (vEhc.getV(0, 0)/2 +45)*1000, cooltime = 200*1000).wrap(core.BuffSkillWrapper)
        Summon_Sanryung_Hit1 = core.DamageSkill("권술 : 산령소환 (발동)", 0, vEhc.getV(0, 0) * 36 + 900, 8).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Summon_Sanryung_Hit2 = core.DamageSkill("권술 : 산령소환 (연계성공)", 0, vEhc.getV(0, 0)*14 + 350, 4, cooltime = 3000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        Summon_Sanryung.onAfter(Summon_Sanryung_Hit1)
        Summon_Sanryung_Hit2_Opt = core.OptionalElement(lambda : Summon_Sanryung.is_active() and Summon_Sanryung_Hit2.is_available(), Summon_Sanryung_Hit2)

        NanSin = core.BuffSkill("선기 : 강림 괴력난신", 900, 30*1000, cooltime= 200*1000, pdamage = vEhc.getV(0, 0)*2+20).wrap(core.BuffSkillWrapper)
        # 지속시간 중 공격을 12회 적중시킬 때마다 발동
        NanSin_Attack = core.DamageSkill("선기 : 강림 괴력난신 (신들의 일격)", 0, vEhc.getV(0, 0)*34 + 850, 8, cooltime = 1500).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        NanSin_Final = core.DamageSkill("선기 : 강림 괴력난신 (신들의 강림)", 0, vEhc.getV(0, 0)*40+1000, 15*6, cooltime = -1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        
        NanSin_Attack_Opt = core.OptionalElement(lambda : NanSin_Attack.is_available() and NanSin.is_active(), NanSin_Attack)
        # 버프 종료 직전에 막타 발동
        NanSin.onAfter(NanSin_Final.controller(30*1000-1))

        '''
        TODO:
            허/실 스킬을 제외한 직접 공격하는 호영의 스킬 적중 시 분신이 등장하여 현재 연계하지 않은 속성 공격을 하고 속성 연계를 완성시킨다.
            액티브 효과 지속 중 속성 연계 3단계 달성 시 천/지/인 도술 중 한 속성 도술의 재사용 대기시간이 초기화되며 속성 선택 시 재사용 대기시간 중인 스킬이 있는 속성이 우선된다.
        '''
        Elemental_Clone_Passive = core.DamageSkill("선기 : 천지인 환영 (패시브)", 0, 625 + 25*vEhc.getV(0, 0), 6, cooltime = 5000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Elemental_Clone_Passive_Opt = core.OptionalElement(Elemental_Clone_Passive.is_usable(), Elemental_Clone_Passive)

        Elemental_Clone = core.BuffSkill("선기 : 천지인 환영", 720, 30*1000, cooltime = 100*1000).wrap(core.BuffSkillWrapper)
        Elemental_Clone_Active = core.DamageSkill("선기 : 천지인 환영 (액티브)", 0, 625 + 25*vEhc.getV(0, 0), 6*2, cooltime = 2000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Elemental_Clone_Active_Opt = core.OptionalElement(Elemental_Clone_Active.is_available(), Elemental_Clone_Active)

        Elemental_Clone_Opt = core.OptionalElement(Elemental_Clone.is_active(), Elemental_Clone_Active_Opt, Elemental_Clone_Passive_Opt)

        # 딜사이클
        BasicCombo = core.DamageSkill("기본 공격", 0,0,0).wrap(core.DamageSkillWrapper)
        # 깡토파류
        BasicCombo.onAfter(Topa)

        # 괴력난신 지속시간 동안 천/지/인 속성 스킬 및 허/실 스킬의 데미지 20% 증가
        for sk in [YeoUiSeon, Topa, Topa_Clone, Pacho, Pacho_Clone, EarthQuake, EarthQuake_Clone, Flames, Flames_Clone, GeumGoBong, GeumGoBong_2]:
            sk.add_runtime_modifier(NanSin, lambda : core.CharacterModifier(pdamage = 20))


        return(BasicCombo,
            [globalSkill.maple_heros(chtr.level, name = "아니마의 용사", combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                Booster,
                globalSkill.soul_contract()] +\
            [MirrorBreak, MirrorSpider] +\
            [] +\
            [BasicCombo])
