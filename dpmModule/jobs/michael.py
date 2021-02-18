from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill, jobutils
from .jobclass import cygnus
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict
# 미하일 영메 적용여부에 대해 고민해볼 필요 있음


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 9
        self.jobtype = "STR"
        self.jobname = "미하일"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'mess')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(crit=20, pdamage=30, armor_ignore=12)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트",patt = 10)
        
        PhisicalTraiging = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        SwordMastery = core.InformedCharacterModifier("소드 마스터리",pdamage_indep = 15)
        InvigoratePassive = core.InformedCharacterModifier("격려(패시브)",att = 20)
        Intension = core.InformedCharacterModifier("인텐션",stat_main = 60, crit = 20, pdamage_indep = 10)
        ShiningCharge = core.InformedCharacterModifier("샤이닝 차지(패시브)",pdamage = 60)
        CombatMastery = core.InformedCharacterModifier("컴뱃 마스터리",armor_ignore = 40+2*passive_level)
        AdvancedSowrdMastery = core.InformedCharacterModifier("어드밴스드 소드 마스터리",att = 30+passive_level, crit = 15+passive_level//3, crit_damage = 10)
        AdvancedFinalAttackPassive = core.InformedCharacterModifier("어드밴스드 파이널 어택(패시브)",att = 30+passive_level)

        return [ElementalExpert, PhisicalTraiging, SwordMastery,
                            InvigoratePassive, Intension, ShiningCharge, CombatMastery, AdvancedSowrdMastery,
                            AdvancedFinalAttackPassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        PARTYPEOPLE = 1        
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=90+ceil(passive_level/2))
        
        SoulLink = core.InformedCharacterModifier("소울 링크",pdamage = 5*PARTYPEOPLE)
        SoulRage = core.InformedCharacterModifier("소울 레이지", pdamage_indep = 30+self.combat, crit_damage = 8)
        
        return [WeaponConstant, Mastery, SoulLink, SoulRage]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        파티원 1명
        
        하이퍼
        샤이닝 크로스 - 리인포스 / 인스톨 / 보너스 어택
        소울 어썰트 - 리인포스 / 보너스 어택
        
        소울어썰트-샤이닝크로스-로얄가드-파택-데들리차지
        
        샤이닝 크로스는 십자가가 항상 남아있도록 유지함
        
        로얄 가드는 6초마다 사용하며 다른 스킬로 인해 약간 나중에 사용할 수도 있음. 로얄 가드 5중첩 버프를 상시 유지하도록 가정.
        '''
        USE_ROYAL_GUARD = options.get("royal_guard", True)

        passive_level = chtr.get_base_modifier().passive_level + self.combat

        # Buff skills
        GuardOfLight = core.BuffSkill("빛의 수호", 900, 30000, rem = True, red = True, cooltime = 180000, pdamage = 20).wrap(core.BuffSkillWrapper)
        Booster = core.BuffSkill("부스터", 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        Invigorate = core.BuffSkill("격려", 0, 180000, rem = True, att = 30).wrap(core.BuffSkillWrapper)
        SoulAttack = core.BuffSkill("소울 어택", 0, 10000, cooltime = -1, pdamage_indep = 25, crit = 20).wrap(core.BuffSkillWrapper)
        
        # Damage skills
        LoyalGuard_1 = core.DamageSkill("로얄 가드(1)", 120+450, 275+chtr.level, 4, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_2 = core.DamageSkill("로얄 가드(2)", 120+450, 340+chtr.level, 5, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_3 = core.DamageSkill("로얄 가드(3)", 120+450, 440+chtr.level, 6, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_4 = core.DamageSkill("로얄 가드(4)", 120+450, 480+chtr.level, 7, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_5 = core.DamageSkill("로얄 가드(5)", 120+450, 565+chtr.level, 9, cooltime = 6000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuardBuff = core.BuffSkill("로얄 가드(버프)", 0, 12000, att = 45).wrap(core.BuffSkillWrapper)  #10->15->20->30->45
        
        SoulAssult = core.DamageSkill("소울 어썰트", 540, 210+3*self.combat, 11+1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)   #암흑 20%
        
        FinalAttack = core.DamageSkill("파이널 어택", 0, 95+passive_level, 4*0.01*(75+passive_level)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        
        ShiningCross = core.DamageSkill("샤이닝 크로스", 540, 440+3*self.combat, 4+1, cooltime = 12000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)   #암흑 30% 10초
        ShiningCrossInstall = core.SummonSkill("샤이닝 크로스-인스톨", 0, 1200, 75, 4+1, 12000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)    #100% 암흑 5초
        
        # Hyper
        SacredCube = core.BuffSkill("세이크리드 큐브", 90, 30000, cooltime = 210000, pdamage = 10).wrap(core.BuffSkillWrapper)
        DeadlyCharge = (
            core.DamageSkill(
                "데들리 차지",
                delay=30 if USE_ROYAL_GUARD else 810,
                damage=600,
                hit=10,
                cooltime = 15000,
            )
            .setV(vEhc, 4, 2, False)
            .wrap(core.DamageSkillWrapper)
        )
        DeadlyChargeBuff = core.BuffSkill("데들리 차지(디버프)", 0, 10000, cooltime = -1, pdamage = 10).wrap(core.BuffSkillWrapper)
        QueenOfTomorrow = core.BuffSkill("퀸 오브 투모로우", 0, 60000, cooltime = 120000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        # 5th
        CygnusPhalanx = cygnus.PhalanxChargeWrapper(vEhc, 3, 3)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        RoIias = core.BuffSkill("로 아이아스", 840, (75+3*vEhc.getV(0,0))*1000, cooltime = 300*1000, red = True, pdamage_indep = 5 + (35+3*(vEhc.getV(0,0)//4))//2).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        ClauSolis = core.DamageSkill("클라우 솔라스", 690, 700+28*vEhc.getV(4,4), 7, cooltime = 12000, red = True).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)    #로얄가드 버프지속시간 6초 증가. 100% 암흑 5초
        ClauSolisSummon = core.SummonSkill("클라우 솔라스(소환)", 0, 5000, 350+14*vEhc.getV(4,4), 7, 7000, cooltime = -1).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)   #100% 암흑 5초
    
        SwordOfSoullight = core.BuffSkill("소드 오브 소울 라이트", 810, 35000, cooltime = 180*1000, red = True, patt = 15 + vEhc.getV(1,1)//2, crit = 100, armor_ignore = 100).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)
        SoullightSlash = core.DamageSkill("소울 라이트 슬래시", 630, 400+16*vEhc.getV(1,1), 12).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        LightForceRay = core.DamageSkill("라이트 포스레이", 720, 850+34*vEhc.getV(1,1), 12*6, cooltime=-1).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)  # TODO: 공속 적용 여부 확인 (base delay 930)
        SwordOfSoullightSummon = core.SummonSkill("소드 오브 소울 라이트(잔상)", 0, 1800, 450+18*vEhc.getV(0,0), 5, 35000, cooltime=-1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)

        LightOfCourage = core.BuffSkill("라이트 오브 커리지", 570, 25000, cooltime=90*1000, red=True, pdamage=10+vEhc.getV(0,0)//2).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        ##### Build Graph
        
        # 기본 공격
        BasicAttack = core.OptionalElement(SwordOfSoullight.is_active, SoullightSlash, SoulAssult)
        BasicAttackWrapper = core.DamageSkill('기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)
        
        SoullightSlash.onAfter(FinalAttack)
        SoulAssult.onAfter(FinalAttack)
        LoyalGuard_5.onAfter(FinalAttack)

        # 클라우 솔라스
        ClauSolis.onEventElapsed(ClauSolisSummon, 5000)
        ClauSolis.onAfter(SoulAttack.controller(5000,"set_enabled_and_time_left"))
        ClauSolis.onAfter(FinalAttack)
        ClauSolisSummon.onTick(SoulAttack.controller(5000,"set_enabled_and_time_left"))

        # 데들리 차지
        DeadlyCharge.onAfter(DeadlyChargeBuff)
        DeadlyCharge.onAfter(FinalAttack)
        
        # 샤이닝 크로스
        ShiningCross.onAfter(ShiningCrossInstall)
        ShiningCross.onAfter(FinalAttack)
        ShiningCrossInstall.onTick(SoulAttack.controller(5000,"set_enabled_and_time_left"))

        # 소울 오브 소드 라이트
        SwordOfSoullight.onAfter(SwordOfSoullightSummon)
        SwordOfSoullight.onAfter(LightForceRay.controller(1))

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 2)
        for sk in [SoullightSlash, SoulAssult, DeadlyCharge, LoyalGuard_5, ShiningCross]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        # Scheduling
        if USE_ROYAL_GUARD is True:
            DeadlyCharge.onAfter(LoyalGuard_5)
            DeadlyCharge.onConstraint(
                core.ConstraintElement(
                    "로얄 가드로 캔슬 가능할때",
                    LoyalGuard_5,
                    lambda: LoyalGuard_5.is_available(),
                )
            )
        else:
            LoyalGuard_5 = None
            LoyalGuardBuff = None
        
        return(BasicAttackWrapper, 
                [globalSkill.maple_heros(chtr.level, name = "시그너스 나이츠", combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    GuardOfLight, LoyalGuardBuff, SoulAttack, Booster, Invigorate, SacredCube, cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level),
                    DeadlyChargeBuff, QueenOfTomorrow, AuraWeaponBuff, AuraWeapon, RoIias, SwordOfSoullight, SwordOfSoullightSummon, LightOfCourage,
                    globalSkill.soul_contract()] +\
                [CygnusPhalanx, MirrorBreak, MirrorSpider, LightForceRay, DeadlyCharge, LoyalGuard_5, ShiningCross, ClauSolis] +\
                [ShiningCrossInstall, ClauSolisSummon] +\
                [BasicAttackWrapper])