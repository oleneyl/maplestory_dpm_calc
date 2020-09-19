from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import thieves, pirates
from .jobclass import resistance
from . import jobutils
from math import ceil

class SupplyStackWrapper(core.StackSkillWrapper):
    def __init__(self, skill):
        super(SupplyStackWrapper, self).__init__(skill, 20)
        self.stack = 20
        self.modifierInvariantFlag = False
    
    def get_modifier(self): # 서플러스 서플라이: 서플러스 에너지 1개 당 모든 능력치 1%만큼 증가
        return core.CharacterModifier(pstat_main = self.stack, pstat_sub = self.stack)

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "luk"
        self.jobname = "제논"
        self.vEnhanceNum = None
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier()
        
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        Multilateral1 = core.InformedCharacterModifier("멀티래터럴 I", pdamage = 3)
        Multilateral2 = core.InformedCharacterModifier("멀티래터럴 II", pdamage = 5)
        Multilateral3 = core.InformedCharacterModifier("멀티래터럴 III", pdamage = 7)
        Multilateral4 = core.InformedCharacterModifier("멀티래터럴 IV", pdamage = 10)
        Multilateral5 = core.InformedCharacterModifier("멀티래터럴 V", pdamage = 10)
        Multilateral6 = core.InformedCharacterModifier("멀티래터럴 V", pdamage = 5)

        LinearPerspective = core.InformedCharacterModifier("리니어 퍼스펙티브", crit = 40)
        MinoritySupport = core.InformedCharacterModifier("마이너리티 서포트", stat_main = 20, stat_sub = 20)
        XenonMastery = core.InformedCharacterModifier("제논 마스터리", att = 20)
        XenonExpert = core.InformedCharacterModifier("제논 엑스퍼트", att = 30, crit_damage = 8)
        OffensiveMatrix = core.InformedCharacterModifier("오펜시브 매트릭스", armor_ignore = 30)

        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 3, 4)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 2, 2)


        return []

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 50)
        JobConstant = core.InformedCharacterModifier("직업상수", pdamage_indep = -12.5)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -5 + 0.5 * ceil(passive_level / 2))
        
        return [WeaponConstant, JobConstant, Mastery]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter):
        '''
        TODO: 제논 구현

        '''

        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        # Buff skills
        SupplySurplus = core.BuffSkill("서플러스 서플라이", 0, 999999999).wrap(SupplyStackWrapper)
        InclinePower = core.BuffSkill("인클라인 파워", None, 240000, att = 30).wrap(core.BuffSkillWrapper) # 에너지 -3
        EfficiencyPipeLine = core.BuffSkill("에피션시 파이프라인", None, 240000).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill("제논 부스터", None, 240000).wrap(core.BuffSkillWrapper)
        HybridDefenses = core.BuffSkill("듀얼브리드 디펜시브", None, 240000).wrap(core.BuffSkillWrapper) # 에너지 -7
        VirtualProjection = core.BuffSkill("버추얼 프로젝션", None, 999999999).wrap(core.BuffSkillWrapper)

        ExtraSupply = core.BuffSkill("엑스트라 서플라이", None, 1, cooltime = 30000).wrap(core.BuffSkillWrapper) # 에너지 +10

        OOPArtsCode = core.BuffSkill("오파츠 코드", None, 30000, pdamage_indep = 25, boss_pdamage = 30).wrap(core.BuffSkillWrapper) # 에너지 -20

        # Damage skills

        # 로켓강화 적용됨
        PinpointRocket = core.DamageSkill("핀포인트 로켓", 0, 50+40+40+100, 4, cooltime = 2000).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        
        # 이지스: 피격시에만 발동이라 허수아비 상대로는 미적용해야할듯 (인스턴스 셔크 적용됨)
        AegisSystem = core.DamageSkill("이지스 시스템", 0, 120, 3, modifier = core.CharacterModifier(pdamage = 20), cooltime = 1500).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        # 항상 3중첩 가정?
        Triangulation = core.DamageSkill("트라이앵글 포메이션", 0, 340, 3, cooltime = -1).setV(vEhc, 0, 3, True).wrap(core.DamageSkillWrapper)

        # 하이퍼 뎀퍼, 방무
        PurgeSnipe = core.DamageSkill("퍼지롭 매스커레이드 : 저격", None, 345, 7, modifier = core.CharacterModifier(armor_ignore = 30) + core.CharacterModifier(pdamage = 20, armor_ignore = 10)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        
        # 택1
        # 하이퍼 3종 적용
        Hologram_Penetrate = core.SummonSkill("홀로그램 그래피티 : 관통", None, None, 213*1.1, 1, 20000 + 10000, cooltime = 30000).setV(vEhc, 0, 2, True).wrap(core.SummonSkillWrapper)
        Hologram_ForceField = core.SummonSkill("홀로그램 그래피티 : 역장", None, None, 400*1.1, 1, 20000 + 10000, cooltime = 30000).setV(vEhc, 0, 2, True).wrap(core.SummonSkillWrapper)

        # Hyper skills
        AmaranthGenerator = core.BuffSkill("아마란스 제네레이터", None, 10000, cooltime = 90000, rem = False).wrap(core.BuffSkillWrapper) # 에너지 최대치, 10초간 에너지 소모 없음
        MeltDown = core.DamageSkill("멜트다운 익스플로전", None, 900, 6, red = False, cooltime = 50000).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        MeltDown_Armor = core.BuffSkill("멜트다운 익스플로전 (방무)", 0, 10000, armor_ignore = 30, rem = False).wrap(core.BuffSkillWrapper)
        MeltDown_Damage = core.BuffSkill("멜트다운 익스플로전 (데미지)", 0, 25000, pdamage = 10, rem = False).wrap(core.BuffSkillWrapper)
    
        # V skills
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        LuckyDice = core.BuffSkill("럭키 다이스", 0, 180*1000, pdamage = 20).isV(vEhc,3,4).wrap(core.BuffSkillWrapper)
        ResistanceLineInfantry = resistance.ResistanceLineInfantryWrapper(vEhc, 0, 0)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc,4,4)
        #오버드라이브 (앱솔 가정)
        #TODO: 템셋을 읽어서 무기별로 다른 수치 적용하도록 만들어야 함.
        WEAPON_ATT = jobutils.get_weapon_att("에너지소드")
        Overdrive = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)

        MegaSmasher = core.DamageSkill("메가 스매셔", None, 0, 0, cooltime = 180000).wrap(core.DamageSkillWrapper)
        MegaSmasherTick = core.DamageSkill("메가 스매셔(틱)", None, 300+10*vEhc.getV(4,4), 6).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)
        # TODO: 따로 구현해야 함
        # 초과 에너지 20 충전 가능, 에너지 충전 시간 절반으로 감소, 초과 충전한 에너지 당 최종 데미지 1% 증가
        # 비활성화 시 초과 충전된 에너지 즉시 소멸
        OVERLOAD_TIME = 30
        OverloadMode = core.BuffSkill("오버로드 모드", None, OVERLOAD_TIME * 1000, cooltime = 180000).wrap(core.BuffSkillWrapper)
        # 6번 공격하는 전격 4회 발동
        OverloadHit = core.SummonSkill("오버로드 모드(전류)", 0, None, 180 + 7 * vEhc.getV(4,4), 6*4, OVERLOAD_TIME * 1000).isV(vEhc, 4, 4).wrap(core.SummonSkillWrapper)
        
        # 하이퍼 적용됨
        Hologram_Fusion = core.SummonSkill("홀로그램 그래피티 : 융합", None, None, (250 + 10 * vEhc.getV(4,4))*1.1, 5, 30000 + 10000, cooltime = 100000).isV(vEhc, 4, 4).wrap(core.SummonSkillWrapper)
        #TODO: 제논이 홀로그램 필드 안에 있을 경우 이지스 시스템으로 발사되는 미사일 7개 증가
        Hologram_Fusion_Buff = core.BuffSkill("홀로그램 그래피티 : 융합 (버프)", 0, 30000+10000, pdamage = 5+vEhc.getV(4,4)//2, rem = False).wrap(core.BuffSkillWrapper)
        # 30회 발동
        PhotonRay = core.BuffSkill("포톤 레이", None, 20000, cooltime = 35000).wrap(core.BuffSkillWrapper)
        PhotonRayTick = core.DamageSkill("포톤 레이(캐논)", 0, 350+vEhc.getV(4, 4), 4).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)

        ######   Skill Wrapper   ######

        BasicAttackWrapper = core.DamageSkill("기본 공격", 0, 0, 0).wrap(core.DamageSkillWrapper)
        
        return(BasicAttackWrapper, 
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    globalSkill.useful_wind_booster(), globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()] +\
                [MirrorBreak, MirrorSpider] +\
                [globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat)] +\
                [BasicAttackWrapper])