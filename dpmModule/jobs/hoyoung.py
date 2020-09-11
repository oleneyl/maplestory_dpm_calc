from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConditionRule
from . import globalSkill
from .jobbranch import thieves
from math import ceil
#TODO : 5차 신스킬 적용

# 이 코드는 dualblade.py를 카피하여 수정했습니다. 아직 미완성입니다!

# 하이퍼 패시브 미적용

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
        self._combat = 0

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 40)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self._combat
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
        passive_level = chtr.get_base_modifier().passive_level + self._combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -5+0.5*ceil(passive_level/2))    #오더스 기본적용!
        SpiritAffinity = core.BuffSkill("정령친화", 0, 999999).wrap(core.BuffSkillWrapper) # 더미
        return [WeaponConstant, Mastery, SpiritAffinity]
    
    '''
    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule('써든레이드', '파이널 컷', check_final_cut_time), RuleSet.BASE)
        return ruleset
    '''

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):

        passive_level = chtr.get_base_modifier().passive_level + self._combat
        SUMMON_REMAIN = 1 + chtr.summonRemain + 0.1
        
        # 1차
        #부채 타격 가정
        Humanity_As_You_Will_Fan = core.DamageSkill("여의선 : 인", 0, 530 + 5*passive_level, 5, modifier = core.CharacterModifier(pdamage_indep = 10)).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Talisman_Evil_Sealing_Gourd = core.DamageSkill("마봉 호로부", 0, 1000 + 10 * passive_level, 6, cooltime = -1, modifier = core.CharacterModifier(boss_pdamage = 20)).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)

        # 2차
        Earth_Ground_Shattering_Wave = core.DamageSkill("토파류 : 지", 0, 385 + 5*passive_level, 4).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Ground_Shattering_Wave_CT = core.DamageSkill("토파류 : 허/실", 0, 385 + 5*passive_level, 4).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)

        # 스킬 설명에 확률이 명시되어 있지 않음.
        TALISMAN_PROBABLITY = 1
        
        # 벞지 & 소환수 지속시간 둘다 적용
        Talisman_Clone = core.BuffSkill("환영 분신부", 0, 200*1000).wrap(core.BuffSkillWrapper)
        Talisman_Clone_Attack = core.DamageSkill("환영 분신부 (공격)", 0, 460 + 5*passive_level, 2 * 3 * TALISMAN_PROBABLITY, cooltime = 1500).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        # 다른 공격스킬에 onAfter로 연결
        Talisman_Clone_Attack_Opt = core.OptionalElement(Talisman_Clone_Attack.is_usable(), Talisman_Clone_Attack)

        Booster = core.BuffSkill("부채 가속", 0, 200*1000).wrap(core.BuffSkillWrapper)

        # 3차

        Heaven_Iron_Fan_Gale = core.DamageSkill("파초풍 : 천", 0, 265 + 2*passive_level, 5).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Iron_Fan_Gale_CT = core.DamageSkill("파초풍 : 허/실", 0, 265 + 2*passive_level, 5).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)

        Earth_Stone_Tremor = core.DamageSkill("지진쇄 : 지", 0, 390 + 5*passive_level, 6, cooltime = 6000).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Stone_Tremor_CT = core.DamageSkill("지진쇄 : 허/실", 0, 390 + 5*passive_level, 6, cooltime = -1).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)

        Talisman_Seeking_Ghost_Flame = core.SummonSkill("추적 귀화부", 0, 1800, 390 + 5*passive_level, 5, 40*1000*SUMMON_REMAIN).setV(vEhc, 0, 0, False).wrap(core.SummonSkillWrapper)

        Scroll_Degeneration = core.DamageSkill("권술 : 미생강변", 0, 850 + (6+4)*self._combat, 8, modifier = core.CharacterModifier(boss_pdamage = 20)).setV(vEhc, 0, 0, False).wrap(core.SummonSkillWrapper)
        Scroll_Degeneration_Debuff = core.BuffSkill("권술 : 미생강변 (디버프)", 0, 60*1000, armor_ignore = 20).wrap(core.BuffSkillWrapper)

        # 4차
        Heaven_Consuming_Flames = core.DamageSkill("멸화염 : 천", 0, 340 + self._combat, 6, cooltime = 8000).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Consuming_Flames_CT = core.DamageSkill("멸화염 : 허/실", 0, 340 + self._combat, 6).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)

        Humanity_Gold_Banded_Cudgel_1 = core.DamageSkill("금고봉 : 인 (1타)", 0, 260 + 3*self._combat, 10, cooltime = 11000, modifier = core.CharacterModifier(boss_pdamage = 30)).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Humanity_Gold_Banded_Cudgel_2 = core.DamageSkill("금고봉 : 인 (2타)", 0, 420 + self._combat, 8, modifier = core.CharacterModifier(boss_pdamage = 30)).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        
        Thousand_Ton_Stone = core.DamageSkill("둔갑 천근석", 0, 275 + 3*self._combat, 6, cooltime = 500).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Thousand_Ton_Stone_DOT = core.DotSkill("둔갑 천근석 (출혈)", 0, 1000, 270 + self._combat, 1, 10000, cooltime = -1).setV(vEhc, 0, 0, False).wrap(core.SummonSkillWrapper)
        Thousand_Ton_Stone.onAfter(Thousand_Ton_Stone_DOT)

        Scroll_Star_Vortex = core.SummonSkill("권술 : 흡성와류", 0, 0, 240 + 4*self._combat, 6, 40000 * SUMMON_REMAIN).setV(vEhc, 0, 0, False).wrap(core.SummonSkillWrapper)

        # 벞지 & 소환수 지속시간 둘다 적용
        Scroll_Butterfly_Dream = core.BuffSkill("권술 : 호접지몽", 0, 100*1000, pdamage_indep = 10).wrap(core.BuffSkillWrapper)
        Scroll_Butterfly_Dream_Attack = core.DamageSkill("권술 : 호접지몽 (공격)", 0, 275 + 3 * self._combat, 5, cooltime = 1000).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)
        Scroll_Butterfly_Dream_Attack_Opt = core.OptionalElement(Scroll_Butterfly_Dream_Attack.is_usable(), Scroll_Butterfly_Dream_Attack)
        # 하이퍼 액티브
        Sage_TaiYus_Miracle_Tonic = core.BuffSkill("선기 : 영약 태을선단", 0, 12*1000, cooltime = 100*1000, rem = False, red = False).wrap(core.BuffSkillWrapper)
        # 몽유도원은 딜스킬이 아님 Sage_Dream_of_ShangriLa = 
        Sage_TaiYu_Clone = core.DamageSkill("선기 : 분신 둔갑 태을선인", 0, 800, 8, cooltime = 200*1000, red = False)

        # 5차 (베놈 버스트 생략)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 0, 0)

        # 그란디스 여신의 축복 (아니마)
        # 아니마 신직업 등장시 공용코드화 할것
        AnimaGoddessBless = AnimaGoddessBlessWrapper(vEhc, 0, 0)

        # 환영 분신부를 대체하는 스킬 (알고리즘 구현 필요)
        Sage_Clone_Rampage = core.BuffSkill("선기 : 극대 분신난무", 0, (vEhc.getV(0, 0)/2 + 20)*1000, cooltime = 200*1000).wrap(core.BuffSkillWrapper)
        Sage_Clone_Rampage_Attack = core.DamageSkill("선기 : 극대 분신난무 (공격)", 0, vEhc.getV(0, 0) * 16 + 400, 2 * 12 * TALISMAN_PROBABLITY, cooltime = 12*1000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        Scroll_Tiger_of_Songyu = core.BuffSkill("권술 : 산령소환", 0, (vEhc.getV(0, 0)/2 +45)*1000, cooltime = 200*1000).wrap(core.BuffSkillWrapper)
        Scroll_Tiger_of_Songyu_Hit1 = core.DamageSkill("권술 : 산령소환 (발동)", 0, vEhc.getV(0, 0) * 36 + 900, 8).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Scroll_Tiger_of_Songyu_Hit2 = core.DamageSkill("권술 : 산령소환 (연계성공)", 0, vEhc.getV(0, 0)*14 + 350, 4, cooltime = 3500).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        # 스킬발동 직후 연계발동 방지
        Scroll_Tiger_of_Songyu.onAfters([Scroll_Tiger_of_Songyu_Hit1, Scroll_Tiger_of_Songyu_Hit2.controller(3500)])
        Scroll_Tiger_of_Songyu_Hit2_Opt = core.OptionalElement(Scroll_Tiger_of_Songyu_Hit2.is_available(), Scroll_Tiger_of_Songyu_Hit2)

        # TODO: 지속시간 동안 천/지/인 속성 스킬 및 허/실 스킬의 데미지 20% 증가
        Sage_Wrath_of_Gods = core.BuffSkill("선기 : 강림 괴력난신", 0, 30*1000, cooltime= 200*1000, pdamage = vEhc.getV(0, 0)*2+20).wrap(core.BuffSkillWrapper)
        # 지속시간 중 공격을 5회 적중시킬 때마다 발동
        Sage_Wrath_of_Gods_Attack = core.DamageSkill("선기 : 강림 괴력난신 (신들의 일격)", 0, vEhc.getV(0, 0)*34 + 850, 8, cooltime = 3000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Sage_Wrath_of_Gods_End = core.DamageSkill("선기 : 강림 괴력난신 (신들의 강림)", 0, vEhc.getV(0, 0)*40+1000, 15*6, cooltime = -1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        # 버프 종료 직전에 막타 발동
        Sage_Wrath_of_Gods.onAfter(Sage_Wrath_of_Gods_End.controller(30*1000-1))

        # TODO: 액티브 효과 지속 중 속성 연계 3단계 달성 시 천/지/인 도술 중 한 속성 도술의 재사용 대기시간이 초기화되며 속성 선택 시 재사용 대기시간 중인 스킬이 있는 속성이 우선된다.
        Sage_Elemental_Clone_Attack = core.BuffSkill("선기 : 천지인 환영", 0, 30*1000, cooltime = 100*1000).wrap(core.BuffSkillWrapper)
        Sage_Elemental_Clone_Attack_Passive = core.DamageSkill("선기 : 천지인 환영 (패시브)", 0, 625 + 25*vEhc.getV(0, 0), 6, cooltime = 5000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Sage_Elemental_Clone_Attack_Passive_Opt = core.OptionalElement(Sage_Elemental_Clone_Attack_Passive.is_available(), Sage_Elemental_Clone_Attack_Passive)
        Sage_Elemental_Clone_Attack_Active = core.DamageSkill("선기 : 천지인 환영 (액티브)", 0, 625 + 25*vEhc.getV(0, 0), 6*2, cooltime = 2000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        Sage_Elemental_Clone_Attack_Active_Opt = core.OptionalElement(Sage_Elemental_Clone_Attack_Active.is_available(), Sage_Elemental_Clone_Attack_Active)
        Sage_Elemental_Clone_Attack_Opt = core.OptionalElement(Sage_Elemental_Clone_Attack.is_active(), Sage_Elemental_Clone_Attack_Active_Opt, Sage_Elemental_Clone_Attack_Passive_Opt)


        return(globalSkill.maple_heros(chtr.level, name = "아니마의 용사", combat_level=self._combat))
