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

'''
Advisor: Monolith
'''
# TODO: 하이퍼스탯으로 스탠스 10% 확보 필요 

class SupplyStackWrapper(core.StackSkillWrapper):
    def __init__(self, skill, amaranth_generator):
        super(SupplyStackWrapper, self).__init__(skill, 20)
        self.stack = 20
        self.modifierInvariantFlag = False
        self.set_name_style("서플라이 변화 : %d")
        self.amaranth_generator = amaranth_generator
    
    # 아마란스 활성화시 에너지 소모 없음 
    def vary(self, d):
        delta = d
        if self.amaranth_generator.is_active():
            delta = max(0, delta)
        result = super().vary(delta)
        return result
    
    def get_modifier(self):
        '''
        서플러스 서플라이: 서플러스 에너지 1개 당 모든 능력치 1%만큼 증가, 20 초과시 초과 에너지당 최종 데미지 1% 증가
        '''
        return core.CharacterModifier(pstat_main = self.stack, pstat_sub = self.stack, pdamage_indep = max(0, self.stack - 20))
    
    def chargeController(self):
        return core.TaskHolder(core.Task(self, partial(self.set_stack, self._max - self.stack)), name = "서플라이 차지")
    
    def begin_overload(self):
        self._max = 40
        return self._result_object_cache
    
    def beginOverloadMode(self):
        return core.TaskHolder(core.Task(self, self.begin_overload), name="오버로드 모드 시작")

    def end_overload(self):
        self.stack = min(20, self.stack)
        self._max = 20
        return self._result_object_cache
    
    def endOverloadMode(self):
        return core.TaskHolder(core.Task(self, self.end_overload), name="오버로드 모드 종료")

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "luk"
        self.jobname = "제논"
        self.vEnhanceNum = None
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pstat_main = 20, pstat_sub = 20)
        
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        '''
        효율성을 위해 합쳐진 코드 사용 (합계 40%)
        Multilateral1 = core.InformedCharacterModifier("멀티래터럴 I", pdamage = 3)
        Multilateral2 = core.InformedCharacterModifier("멀티래터럴 II", pdamage = 5)
        Multilateral3 = core.InformedCharacterModifier("멀티래터럴 III", pdamage = 7)
        Multilateral4 = core.InformedCharacterModifier("멀티래터럴 IV", pdamage = 10)
        Multilateral5 = core.InformedCharacterModifier("멀티래터럴 V", pdamage = 10)
        Multilateral6 = core.InformedCharacterModifier("멀티래터럴 VI", pdamage = 5)
        '''
        Multilateral = core.InformedCharacterModifier("멀티래터럴", pdamage = 40)

        LinearPerspective = core.InformedCharacterModifier("리니어 퍼스펙티브", crit = 40)
        MinoritySupport = core.InformedCharacterModifier("마이너리티 서포트", stat_main = 20, stat_sub = 20)
        XenonMastery = core.InformedCharacterModifier("제논 마스터리", att = 20)
        HybridDefensesPassive = core.InformedCharacterModifier("듀얼브리드 디펜시브(패시브)", stat_main = 10, stat_sub = 10)
        XenonExpert = core.InformedCharacterModifier("제논 엑스퍼트", att = 30 + passive_level, crit_damage = 8)
        OffensiveMatrix = core.InformedCharacterModifier("오펜시브 매트릭스", armor_ignore = 30 + passive_level)

        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(vEhc, 3, 4)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 2, 2)

        return [Multilateral, LinearPerspective, MinoritySupport, XenonMastery, HybridDefensesPassive, XenonExpert, OffensiveMatrix,
        LoadedDicePassive, ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 50)
        JobConstant = core.InformedCharacterModifier("직업상수", pdamage_indep = -12.5)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -5 + 0.5 * ceil(passive_level / 2))
        
        return [WeaponConstant, JobConstant, Mastery]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter):
        '''
        TODO: 딜사이클 최적화, return문 정리
        하이퍼 스킬: 홀로그램 3종, 퍼지롭 뎀증 + 방무
        '''

        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        # Buff skills
        # 펫버프: 인클라인, 에피션시, 부스터
        InclinePower = core.BuffSkill("인클라인 파워", 0, 240000, att = 30, rem = True).wrap(core.BuffSkillWrapper)
        EfficiencyPipeLine = core.BuffSkill("에피션시 파이프라인", 0, 240000, rem = True).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill("제논 부스터", 0, 240000, rem = True).wrap(core.BuffSkillWrapper)
        HybridDefenses = core.BuffSkill("듀얼브리드 디펜시브", 0, 999999999).wrap(core.BuffSkillWrapper)
        VirtualProjection = core.BuffSkill("버추얼 프로젝션", 0, 999999999).wrap(core.BuffSkillWrapper)

        # 위컴알에 딜레이 없음
        ExtraSupply = core.BuffSkill("엑스트라 서플라이", 0, 1, cooltime = 30000).wrap(core.BuffSkillWrapper)

        OOPArtsCode = core.BuffSkill("오파츠 코드", 990, (30+self.combat//2)*1000, pdamage_indep = 25 + self.combat//2, boss_pdamage = 30 + self.combat).wrap(core.BuffSkillWrapper)

        # Damage skills

        # 로켓강화 적용됨
        PinpointRocket = core.DamageSkill("핀포인트 로켓", 0, 50+40+40+100, 4, cooltime = 2000).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        
        # 이지스: 현재 미적용
        # 타수는 Skill Wrapper 쪽으로 이관 
        AegisSystem = core.DamageSkill("이지스 시스템", 0, 120, 1, modifier = core.CharacterModifier(pdamage = 20 + passive_level // 3), cooltime = 1500).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)

        # 30%확률로 중첩 쌓임, 3중첩 쌓은 후 공격시 터지면서 사라지도록
        Triangulation = core.DamageSkill("트라이앵글 포메이션", 0, 340, 3).setV(vEhc, 0, 3, True).wrap(core.DamageSkillWrapper)

        PurgeSnipe = core.DamageSkill("퍼지롭 매스커레이드 : 저격", 690, 345 + 2*self.combat, 7, modifier = core.CharacterModifier(armor_ignore = 30 + self.combat) + core.CharacterModifier(pdamage = 20, armor_ignore = 10)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        
        # 관통 기준
        # 하이퍼 3종 적용
        Hologram_Penetrate = core.SummonSkill("홀로그램 그래피티 : 관통", 720, 30000/116, 213+3*self.combat, 1, 20000 + 10000, cooltime = 30000 - 1000 * ceil(self.combat/3), modifier = core.CharacterModifier(pdamage = 10)).setV(vEhc, 0, 2, True).wrap(core.SummonSkillWrapper)
        Hologram_ForceField = core.SummonSkill("홀로그램 그래피티 : 역장", 720, 30000/64, 400+5*self.combat, 1, 20000 + 10000, cooltime = 30000 - 1000 * ceil(self.combat/3), modifier = core.CharacterModifier(pdamage = 10)).setV(vEhc, 0, 2, True).wrap(core.SummonSkillWrapper)

        '''
        BladeDancingPrepare = core.DamageSkill("블레이드 댄싱 (준비)", 720 + 420, 0, 0).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        BladeDancing = core.DamageSkill("블레이드 댄싱", 480, 140+4*self.combat, 1).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        BladeDancingEnd = core.DamageSkill("블레이드 댄싱(종료)", 300, 0, 0).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        '''

        # Hyper skills
        AmaranthGenerator = core.BuffSkill("아마란스 제네레이터", 900, 10000, cooltime = 90000, rem = False).wrap(core.BuffSkillWrapper) # 에너지 최대치, 10초간 에너지 소모 없음
        MeltDown = core.DamageSkill("멜트다운 익스플로전", 3150, 900, 6, red = False, cooltime = 50000).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
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
        
        MegaSmasher = core.SummonSkill("메가 스매셔", 0, 250, 0, 1, 16000, cooltime = 180000, rem = False).wrap(core.SummonSkillWrapper)
        MegaSmasherTick = core.DamageSkill("메가 스매셔(틱)", 0, 300+10*vEhc.getV(4,4), 6).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)
        
        OVERLOAD_TIME = 50
        OverloadMode = core.BuffSkill("오버로드 모드", 720, OVERLOAD_TIME * 1000, cooltime = 180000).wrap(core.BuffSkillWrapper)
        # 첫 공격은 항상 5100ms 후에 시작
        # 공격 주기는 3600ms~10800ms 중 랜덤
        OverloadHit = core.SummonSkill("오버로드 모드(전류)", 0, (3600+10800)/2, 180 + 7 * vEhc.getV(4,4), 6*4, OVERLOAD_TIME * 1000 - 5100, cooltime = -1).isV(vEhc, 4, 4).wrap(core.SummonSkillWrapper)
        OverloadHit_copy = core.SummonSkill("오버로드 모드(전류)(버추얼 프로젝션)", 0, (3600+10800)/2, (180 + 7 * vEhc.getV(4,4))*0.7, 6*4, OVERLOAD_TIME * 1000 - 5100, cooltime = -1).isV(vEhc, 4, 4).wrap(core.SummonSkillWrapper)
        
        # 하이퍼 적용됨
        Hologram_Fusion = core.SummonSkill("홀로그램 그래피티 : 융합", 930, (30000 + 10000)/176, 250 + 10 * vEhc.getV(4,4), 5, 30000 + 10000, cooltime = 100000, modifier = core.CharacterModifier(pdamage = 10)).isV(vEhc, 4, 4).wrap(core.SummonSkillWrapper)
        Hologram_Fusion_Buff = core.BuffSkill("홀로그램 그래피티 : 융합 (버프)", 0, 30000+10000, pdamage = 5+vEhc.getV(4,4)//2, rem = False).wrap(core.BuffSkillWrapper)
        
        # 30회 발동, 발사 딜레이 생략, 퍼지롭으로 충전
        PhotonRay = core.BuffSkill("포톤 레이", 300, 20000, cooltime = 35000).wrap(core.BuffSkillWrapper)
        PhotonRayHit = core.DamageSkill("포톤 레이(캐논)", 0, 350+vEhc.getV(4, 4), 4 * 30).isV(vEhc, 4, 4).wrap(core.DamageSkillWrapper)

        ######   Skill Wrapper   ######
        SupplySurplus = SupplyStackWrapper(core.BuffSkill("서플러스 서플라이", 0, 999999999), AmaranthGenerator)

        SupplyCharger = core.SummonSkill("서플라이 충전", 0, 4000, 0, 0, 9999999999).wrap(core.SummonSkillWrapper)
        SupplyCharger.onTick(SupplySurplus.stackController(1))

        PinpointRocketOpt = core.OptionalElement(PinpointRocket.is_active, PinpointRocket)

        # 홀로그램 융합 활성화시 10개, 아니면 3개
        AegisSystemOpt_ = core.OptionalElement(Hologram_Fusion_Buff.is_active, core.RepeatElement(AegisSystem, 10), core.RepeatElement(AegisSystem, 3))
        AegisSystemOpt = core.OptionalElement(AegisSystem.is_active, AegisSystemOpt_)

        InclinePower.onAfter(SupplySurplus.stackController(-3))
        HybridDefenses.onAfter(SupplySurplus.stackController(-7))
        ExtraSupply.onAfter(SupplySurplus.stackController(10))
        OOPArtsCode.onAfter(SupplySurplus.stackController(-20))

        chargeController = SupplySurplus.chargeController()
        AmaranthGenerator.onAfter(chargeController)

        TriangulationStack = core.StackSkillWrapper(core.BuffSkill("트라이앵글 스택", 0, 99999999), 3)
        TriangulationTrigger = core.OptionalElement(lambda : TriangulationStack.judge(3, 1), Triangulation, TriangulationStack.stackController(0.3))
        Triangulation.onAfter(TriangulationStack.stackController(0, dtype = 'set'))

        MegaSmasher.onTick(MegaSmasherTick)

        BeginOverloadMode = SupplySurplus.beginOverloadMode()
        EndOverloadMode = SupplySurplus.endOverloadMode()
        EndOverloadModeHolder = core.DamageSkill("오버로드 모드 종료 (홀더)", 0, 0, 0, cooltime = -1).wrap(core.DamageSkillWrapper)
        EndOverloadModeHolder.onAfter(EndOverloadMode)

        OverloadMode.onAfter(BeginOverloadMode)
        OverloadMode.onAfter(EndOverloadModeHolder.controller(OVERLOAD_TIME * 1000))

        OverloadMode.onAfter(OverloadHit.controller(5100))
        OverloadMode.onAfter(OverloadHit_copy.controller(5100))

        # 퍼지롭 15회 사용 후 포톤레이 발동, 최적화 필요
        PhotonRay.onAfter(PhotonRayHit.controller(690*15))

        for sk in [PurgeSnipe, MeltDown, MegaSmasherTick, OverloadHit]:
            sk.onAfter(TriangulationTrigger)
            sk.onAfter(PinpointRocketOpt)
            jobutils.create_auxilary_attack(sk, 0.7, nametag = "(버추얼 프로젝션)")
        
        MeltDown.onAfter(MeltDown_Armor)
        MeltDown.onAfter(MeltDown_Damage)
        
        for sk in [Hologram_Penetrate, Hologram_ForceField, Hologram_Fusion]:
            sk.onTick(PinpointRocketOpt)
        
        for sk in [PinpointRocket, Triangulation, MegaSmasherTick, MeltDown_Armor, MeltDown_Damage, Hologram_Fusion_Buff, PhotonRayHit]:
            sk.protect_from_running()
        
        return(PurgeSnipe, 
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    globalSkill.useful_wind_booster(), globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract(),
                    SupplySurplus, SupplyCharger, InclinePower, EfficiencyPipeLine, Booster, HybridDefenses, VirtualProjection, ExtraSupply] +\
                [Hologram_Penetrate, AmaranthGenerator, MirrorBreak, MirrorSpider, MegaSmasher, MegaSmasherTick, ResistanceLineInfantry, LuckyDice, ReadyToDie, Overdrive,
                OverloadMode, Hologram_Fusion, Hologram_Fusion_Buff, OverloadHit, OverloadHit_copy, PhotonRay, PhotonRayHit] +\
                [PinpointRocket, Triangulation, OOPArtsCode] +\
                [PurgeSnipe])