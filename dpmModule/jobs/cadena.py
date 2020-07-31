from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import thieves

#TODO : 5차 신스킬 적용
# Refernce : https://m.blog.naver.com/oe135/221095516055
######   Passive Skill   ######

class WeaponVarietyStackWrapper(core.StackSkillWrapper):
    def __init__(self, _max, prof_agent, final_attack_wrp):
        super(WeaponVarietyStackWrapper , self).__init__(core.BuffSkill("웨폰 버라이어티 스택", 0, 99999999), _max)
        self.stackLog = []
        self.currentAttack = None
        self.currentAttackTime = 0
        self.final_attack_wrp = final_attack_wrp
        self.final_attack_task = self.final_attack_wrp.build_task()
        self.modifierInvariantFlag = False
        self.prof_agent = prof_agent
        
    def vary(self, target, stack):
        if stack and (target not in self.stackLog):
            self.stackLog.append(target)
        
        res = core.ResultObject(0, core.CharacterModifier(), 0, sname = self.skill.name, spec = 'graph control')
        if self.currentAttack != target:
            if self.currentAttackTime < 0:
                res.cascade = [self.final_attack_task]
                self.currentAttackTime = 250
            
        return res	
    
    def spend_time(self, time):
        super(WeaponVarietyStackWrapper, self).spend_time(time)
        self.currentAttackTime -= time
        
    def get_modifier(self):
        multiplier = 11
        if self.prof_agent.is_active():
            multiplier *= 2
        return core.CharacterModifier(pdamage_indep = len(self.stackLog) * multiplier)
    
    def stackController(self, d, stack=True, name = None):
        task = core.Task(self, partial(self.vary, d, stack))
        if self._style is not None and name is None:
            name = self._style % (d)
        return core.TaskHolder(task, name = name)

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 11
        self.jobtype = "luk"
        self.ability_list = Ability_tool.get_ability_set('reuse', 'boss_pdamage', 'mess')
        self.preEmptiveSkills = 1
        
    def get_passive_skill_list(self):
        CollectingForLeap = core.InformedCharacterModifier("콜렉팅 포리프", stat_main = 50)
        
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝", stat_main = 30, stat_sub = 30)
        QuickserviceMind = core.InformedCharacterModifier("퀵서비스 마인드", att = 10, crit_damage  =5, crit = 10)
        Weakpoint = core.InformedCharacterModifier("위크포인트 컨버징 어택", crit=4, crit_damage=20) # 모법링크, 패시브 출혈 2스택
        
        BasicDetection = core.InformedCharacterModifier("베이직 디텍션", armor_ignore = 20)
        
        WeaponMastery = core.InformedCharacterModifier("웨폰 엑스퍼트", att = 30, crit = 30, crit_damage = 15)
        QuickserviceMind_II = core.InformedCharacterModifier("퀵서비스 마인드 II", att = 30, crit_damage  =5, crit = 10)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(self.vEhc, 2, 3)
        
        return [CollectingForLeap, PhisicalTraining,
                                    QuickserviceMind, Weakpoint, BasicDetection, WeaponMastery, QuickserviceMind_II, ReadyToDiePassive]

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 20, crit_damage = 20, pdamage = 20)
                              
    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)	#오더스 기본적용!
        
        return [WeaponConstant, Mastery]		                      

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        논체인아츠-리인포스, 보스킬러
        체인아츠스트로크-넥스트어택 리인포스, 리인포스
        
        체인아츠:테이크다운:쿨리듀스
        
        아직적용 안함.
        
        코강순서:
        스트로크,버라이어티,허슬 - 니들배트 - 브릭 - 샷건/봄 - 에이전트 - 시미터/클로 - 나이프/윙대거 - 테이크다운
        
        스킬강화순서:
        퓨리-오드-버스트-멜-레투다
        
        
        서먼 스로잉 윙대거 3타 후 폭발
        
        시미터, 샷건, 나이프, 봄, 니들배트, 윙대거는 최종뎀 15%를 받고 있음.
        
        봄-브릭 / 샷건-클로 / 나이프 / 윙대거 - 배트 / 메일스트롬 4초당 1회 
        '''

        #버프
        Booster = core.BuffSkill("부스터", 0, 200000).wrap(core.BuffSkillWrapper)
        SpecialPotion = core.BuffSkill("상인단 특제 비약", 0, 60*1000, pdamage = 10, crit = 10, cooltime = 120*1000).wrap(core.BuffSkillWrapper)
        
        ProfessionalAgent= core.BuffSkill("프로페셔널 에이전트", 570, 30000, cooltime = 200000).wrap(core.BuffSkillWrapper)
        ProfessionalAgentAdditionalDamage = core.DamageSkill("프로페셔널 에이전트(공격)", 0, 255, 2).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        #웨폰버라이어티 추가타	
        WeaponVarietyAttackSkill = core.DamageSkill("웨폰 버라이어티", 0, 350, 4).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        WeaponVarietyAttack = WeaponVarietyStackWrapper(11, ProfessionalAgent, WeaponVarietyAttackSkill)
        
        
        #체인아츠
        ChainArts_Stroke_1 = core.DamageSkill("체인아츠:스트로크(1타)", 240, 150, 2, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        ChainArts_Stroke_2 = core.DamageSkill("체인아츠:스트로크(2타)", 390, 400, 5, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        ChainArts_Chais = core.DamageSkill("체인아츠:체이스", 0, 100, 1).wrap(core.DamageSkillWrapper)

        #ChainArts_ToughHustleInit = core.DamageSkill("체인아츠:터프허슬", 0, 0, 0, cooltime = 50000).setV(vEhc, 0, 2, False) #지속형		
        #ChainArts_ToughHustle = core.DamageSkill("체인아츠:터프허슬", 5000000, 600, 2).setV(vEhc, 0, 2, False) #지속형, 6초, 미사용
        
        # ChainArts_takedown = core.DamageSkill("체인아츠:테이크다운", 5360, 990, 15, cooltime = 150*1000, modifier = core.CharacterModifier(armor_ignore = 80)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        # ChainArts_takedown_wave = core.DamageSkill("체인아츠:테이크다운(파동)", 0, 600, 16, modifier = core.CharacterModifier(armor_ignore = 80)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        # ChainArts_takedown_final = core.DamageSkill("체인아츠:테이크다운(최종)", 0, 5000, 1, modifier = core.CharacterModifier(armor_ignore = 80)).setV(vEhc, 7, 2, False).wrap(core.DamageSkillWrapper)
        # ChainArts_takedown_bind = core.BuffSkill("체인아츠:테이크다운(바인드)", 0, 15000, crit=2, crit_damage = 10, cooltime = -1).wrap(core.BuffSkillWrapper)
        #논체인아츠 스킬
        
        SummonCuttingSimiter = core.DamageSkill("서먼 커팅 시미터", 360, 425, 5, cooltime = 4000, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20, pdamage_indep = 15)).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        SummonStretchingClaw = core.DamageSkill("서먼 스트레칭 클로", 330, 455, 4, cooltime = 3000, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20)).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper) #660을 샷건과 분배
        
        SummonThrowingWingdagger = core.DamageSkill("서먼 스로잉 윙대거", 0, 0, 0, cooltime = 10000, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20)).wrap(core.DamageSkillWrapper)
        SummonThrowingWingdaggerInit = core.SummonSkill("서먼 스로잉 윙대거(시전)", 600, 300, 425, 1, 300*3, cooltime= -1, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20, pdamage_indep = 15)).setV(vEhc, 6, 2, False).wrap(core.SummonSkillWrapper)
        SummonThrowingWingdaggerEnd = core.DamageSkill("서먼 스로잉 윙대거(폭발)", 0, 670, 3, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20)).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        
        SummonShootingShotgun = core.DamageSkill("서먼 슈팅 샷건", 330, 510, 7, cooltime = 5000, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20, pdamage_indep = 15)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)	#660을 클로와 분배
        SummonSlachingKnife = core.DamageSkill("서먼 슬래싱 나이프", 570, 435, 8, cooltime = 10000, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20, pdamage_indep = 15)).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper)
        SummonSlachingKnife_Horror = core.BuffSkill("서먼 슬래싱 나이프(공포)", 0, 10000, armor_ignore = 30, crit=2, crit_damage = 10, cooltime = -1).wrap(core.BuffSkillWrapper)
        
        SummonReleasingBoom = core.DamageSkill("서먼 릴리징 봄", 420, 535, 6, cooltime = 8000, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20, pdamage_indep = 15)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        SummonStrikingBrick = core.DamageSkill("서먼 스트라이킹 브릭", 720, 485, 7, cooltime = 8000, modifier = core.CharacterModifier(boss_pdamage = 20, pdamage = 20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        SummonBeatingNeedlebat_1 = core.DamageSkill("서먼 비팅 니들배트(1타)", 360, 450, 6, modifier = core.CharacterModifier(pdamage = 40 + 20, boss_pdamage = 20, pdamage_indep = 15), cooltime = 12000).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        SummonBeatingNeedlebat_2 = core.DamageSkill("서먼 비팅 니들배트(2타)", 420, 555, 7, modifier = core.CharacterModifier(pdamage = 40 + 20, boss_pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        SummonBeatingNeedlebat_3 = core.DamageSkill("서먼 비팅 니들배트(3타)", 600, 715, 8, modifier = core.CharacterModifier(pdamage = 50 + 20, boss_pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        SummonBeatingNeedlebat_Honmy = core.BuffSkill("서먼 비팅 니들배트(혼미)", 0, 15000, crit=2, crit_damage = 10, cooltime = -1).wrap(core.BuffSkillWrapper)
          
        VenomBurst = core.SummonSkill("베놈 버스트", 0, 1000, 160+6*vEhc.getV(4,4), 1, 99999999).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)
        VenomBurst_Poison = core.BuffSkill("베놈 버스트(중독)", 0, 99999999, crit=2, crit_damage = 10, cooltime = -1).isV(vEhc,4,4).wrap(core.BuffSkillWrapper)
        
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 2, 3)
        
        ChainArts_Fury = core.BuffSkill("체인아츠:퓨리", 540, (35+vEhc.getV(0,0))*1000, cooltime = (180-vEhc.getV(0,0))*1000 ).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        ChainArts_Fury_Damage = core.DamageSkill("체인아츠:퓨리(공격)", 0, 250+10*vEhc.getV(0,0), 6).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        ChainArts_Fury_Dummy = core.BuffSkill("체인아츠:퓨리(재사용대기)", 0, 600, cooltime = -1).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        
        AD_Odnunce = core.SummonSkill("A.D 오드넌스", 450, 330, 225+9*vEhc.getV(1,1), 5, 10000, cooltime = 25000).isV(vEhc,1,1).wrap(core.SummonSkillWrapper)
        AD_Odnunce_Final = core.DamageSkill("A.D 오드넌스(막타)", 0, 750+30*vEhc.getV(1,1), 8, cooltime = -1).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        
        ChainArts_maelstorm = core.SummonSkill("체인아츠:메일스트롬", 720, 800, 300+12*vEhc.getV(3,2), 4, 8000, cooltime = -1).isV(vEhc,3,2).wrap(core.SummonSkillWrapper)
        ChainArts_maelstorm_slow = core.BuffSkill("체인아츠:메일스트롬(중독)", 0, 14000, crit=2, crit_damage = 10, cooltime = -1).isV(vEhc,3,2).wrap(core.BuffSkillWrapper)
        ######   Skill Wrapper   ######

        #기본 연계 연결
        #ChainArts_ToughHustleInit.onAfter(ChainArts_ToughHustle) 터프허슬 미사용
        # ChainArts_takedown.onAfter(ChainArts_takedown_bind)
        # ChainArts_takedown_bind.onAfters([ChainArts_takedown_wave, ChainArts_takedown_final])
        
        SummonThrowingWingdagger.onAfter(SummonThrowingWingdaggerInit)
        SummonThrowingWingdaggerInit.onAfter(SummonThrowingWingdaggerEnd)	#타이밍 변경 필요
        
        SummonSlachingKnife.onAfter(SummonSlachingKnife_Horror)
        
        SummonBeatingNeedlebat_1.onAfter(SummonBeatingNeedlebat_2)
        SummonBeatingNeedlebat_2.onAfter(SummonBeatingNeedlebat_3)
        SummonBeatingNeedlebat_3.onAfter(SummonBeatingNeedlebat_Honmy)
        
        VenomBurst.onAfter(VenomBurst_Poison)
        
        ChainArts_Fury_Use = core.OptionalElement(lambda : ChainArts_Fury_Dummy.is_not_active() and ChainArts_Fury.is_active(), ChainArts_Fury_Dummy)
        ChainArts_Fury_Dummy.onAfter(ChainArts_Fury_Damage)
        
        AD_Odnunce.onAfter(AD_Odnunce_Final.controller(10000))
        ChainArts_maelstorm.onAfter(ChainArts_maelstorm_slow)
        
        #_VenomBurst = core.DamageSkill("베놈 버스트", ??) ## 패시브 50%확률로 10초간 160+6*vlevel dot. 사용시 도트뎀 모두 피해 + (500+20*vlevel) * 5. 어차피 안쓰는 스킬이므로 작성X

        #조건부 파이널어택으로 설정함.
        ProfessionalAgent_Attack = core.OptionalElement(ProfessionalAgent.is_active, ProfessionalAgentAdditionalDamage, name= " 프로페셔널 에이전트 추가타")
    
    
        # 웨폰 버라이어티 호출
        SummonCuttingSimiter.onAfter(WeaponVarietyAttack.stackController(SummonCuttingSimiter))
        SummonStretchingClaw.onAfter(WeaponVarietyAttack.stackController(SummonStretchingClaw))
        SummonThrowingWingdaggerInit.onAfter(WeaponVarietyAttack.stackController(SummonThrowingWingdaggerInit))
        
        SummonShootingShotgun.onAfter(WeaponVarietyAttack.stackController(SummonShootingShotgun))
        SummonSlachingKnife.onAfter(WeaponVarietyAttack.stackController(SummonSlachingKnife))
        SummonReleasingBoom.onAfter(WeaponVarietyAttack.stackController(SummonReleasingBoom))
        
        SummonStrikingBrick.onAfter(WeaponVarietyAttack.stackController(SummonStrikingBrick))
        SummonBeatingNeedlebat_1.onAfter(WeaponVarietyAttack.stackController(SummonBeatingNeedlebat_1))
        
        #ChainArts_ToughHustle.onAfter(WeaponVarietyAttack.stackController(ChainArts_ToughHustle, False))
        
        #카데나 딜 사이클들.
        
        #샷건-클로
        ShootgunClawCombo = core.DamageSkill('샷건-클로', 0, 0, 0).wrap(core.DamageSkillWrapper)
        for i in [ChainArts_Stroke_1, SummonShootingShotgun, SummonStretchingClaw]:
            ShootgunClawCombo.onAfter(i)
        
        for c in [core.ConstraintElement('샷건', SummonShootingShotgun, SummonShootingShotgun.is_available),
                    core.ConstraintElement('클로', SummonStretchingClaw, SummonStretchingClaw.is_available)]:
            ShootgunClawCombo.onConstraint(c)
        
        #시미터 - 체이스
        SimiterChaseCombo = core.DamageSkill('시미터 - 체이스', 0, 0, 0).wrap(core.DamageSkillWrapper)
        for i in [ChainArts_Stroke_1, SummonCuttingSimiter, ChainArts_Chais]:
            SimiterChaseCombo.onAfter(i)
            
        for c in [core.ConstraintElement('시미터', SummonCuttingSimiter, SummonCuttingSimiter.is_available)]:
            SimiterChaseCombo.onConstraint(c)
            
        # 나이프
        KnifeCombo = core.DamageSkill("나이프", 0, 0, 0).wrap(core.DamageSkillWrapper)
        for i in [ChainArts_Stroke_1, SummonSlachingKnife]:
            KnifeCombo.onAfter(i)

        for c in [core.ConstraintElement('나이프', SummonSlachingKnife, SummonSlachingKnife.is_available)]:
            KnifeCombo.onConstraint(c)
            
        # 봄-브릭
        BommBrickCombo = core.DamageSkill("봄-브릭", 0, 0, 0).wrap(core.DamageSkillWrapper)
        for i in [ChainArts_Stroke_1, SummonReleasingBoom, SummonStrikingBrick]:
            BommBrickCombo.onAfter(i)
            
        for c in [core.ConstraintElement('봄', SummonReleasingBoom, SummonReleasingBoom.is_available),
                    core.ConstraintElement('브릭', SummonStrikingBrick, SummonStrikingBrick.is_available)]:
            BommBrickCombo.onConstraint(c)	
        
        #평타
        NormalAttack = core.DamageSkill("평타", 0, 0, 0).wrap(core.DamageSkillWrapper)
        for i in [ChainArts_Stroke_1, ChainArts_Stroke_2]:
            NormalAttack.onAfter(i)
            
        #윙대거-배트
        WingDaggerBatCombo = core.DamageSkill("윙대거-배트", 0, 0, 0).wrap(core.DamageSkillWrapper)
        for i in [ChainArts_Stroke_1, SummonThrowingWingdaggerInit, ChainArts_Stroke_1
                  , SummonBeatingNeedlebat_1]:
            WingDaggerBatCombo.onAfter(i)

        for c in [core.ConstraintElement('윙대거', SummonThrowingWingdagger, SummonThrowingWingdagger.is_available),
                    core.ConstraintElement('배트', SummonBeatingNeedlebat_1, SummonBeatingNeedlebat_1.is_available)]:
            WingDaggerBatCombo.onConstraint(c)	
        
        # 메일스트롬은 2타 후 없으면 시전
        MaleStrom = core.OptionalElement(ChainArts_maelstorm.is_not_active, ChainArts_maelstorm, name = '메일스트롬')
        ChainArts_Stroke_2.onAfter(MaleStrom)	
        
        #체인아츠 - 퓨리 연동
        for s in [ChainArts_Stroke_1, ChainArts_Stroke_2,
                                SummonCuttingSimiter, SummonStretchingClaw, SummonThrowingWingdagger, SummonShootingShotgun, SummonSlachingKnife, 
                                SummonReleasingBoom, SummonStrikingBrick, SummonBeatingNeedlebat_1]:
            s.onAfter(ChainArts_Fury_Use)
            
        for s in [SummonCuttingSimiter, SummonStretchingClaw, SummonThrowingWingdagger, SummonShootingShotgun, SummonSlachingKnife, 
                    SummonReleasingBoom, SummonStrikingBrick, SummonBeatingNeedlebat_1, SummonBeatingNeedlebat_2, SummonBeatingNeedlebat_3,
                        ChainArts_maelstorm, ChainArts_Fury_Damage]:
            s.onAfter(ProfessionalAgent_Attack)
        
        for s in [ChainArts_Fury_Dummy, SummonShootingShotgun, SummonStretchingClaw,
                        SummonCuttingSimiter, SummonSlachingKnife,
                            SummonReleasingBoom, SummonStrikingBrick,
                                SummonBeatingNeedlebat_1, SummonThrowingWingdagger]:
            s.protect_from_running()

        return(NormalAttack,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    WeaponVarietyAttack, Booster, SpecialPotion, ProfessionalAgent,
                    ReadyToDie, ChainArts_Fury, 
                    SummonSlachingKnife_Horror, SummonBeatingNeedlebat_Honmy, VenomBurst_Poison, ChainArts_maelstorm_slow,
                    globalSkill.soul_contract()] +\
                [AD_Odnunce_Final,
                    WingDaggerBatCombo, BommBrickCombo, ShootgunClawCombo, SimiterChaseCombo, KnifeCombo] +\
                [SummonThrowingWingdaggerInit, VenomBurst, AD_Odnunce, ChainArts_maelstorm] +\
                [ChainArts_Fury_Dummy, SummonShootingShotgun, SummonStretchingClaw,
                        SummonCuttingSimiter, SummonSlachingKnife,
                            SummonReleasingBoom, SummonStrikingBrick,
                                SummonBeatingNeedlebat_1, SummonThrowingWingdagger] +\
                [NormalAttack])