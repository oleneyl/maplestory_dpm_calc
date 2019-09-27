from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 9
        self.jobtype = "str"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'mess')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(crit = 20)

    def get_passive_skill_list(self):        
        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트",patt = 10)
        
        PhisicalTraiging = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        SwordMastery = core.InformedCharacterModifier("소드 마스터리",pdamage_indep = 15)
        InvigoratePassive = core.InformedCharacterModifier("격려(패시브)",att = 20)
        Intension = core.InformedCharacterModifier("인텐션",stat_main = 60, crit = 20, pdamage_indep = 10)
        ShiningCharge = core.InformedCharacterModifier("샤이닝 차지(패시브)",pdamage = 60)
        CombatMastery = core.InformedCharacterModifier("컴뱃 마스터리",armor_ignore = 40)
        AdvancedSowrdMastery = core.InformedCharacterModifier("어드밴스드 소드 마스터리",att = 30, crit = 15, crit_damage = 10)
        AdvancedFinalAttackPassive = core.InformedCharacterModifier("어드밴스드 파이널 어택(패시브)",att = 30)

        return [ElementalExpert, PhisicalTraiging, SwordMastery,
                            InvigoratePassive, Intension, ShiningCharge, CombatMastery, AdvancedSowrdMastery,
                            AdvancedFinalAttackPassive]

    def get_not_implied_skill_list(self):
        PARTYPEOPLE = 1        
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)
        
        SoulLink = core.InformedCharacterModifier("소울 링크",pdamage = 5*PARTYPEOPLE)
        SoulRage = core.InformedCharacterModifier("소울 레이지", pdamage_indep = 30, crit_damage = 8)
        
        return [WeaponConstant, Mastery, SoulLink, SoulRage]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        파티원 1명
        
        하이퍼 : 샤이닝 크로스 리인포스 / 인스톨 / 보너스 어택
        소울 어썰트 - 리인포스, 보너스 어택
        
        소울어썰트-샤이닝크로스-로얄가드-파택-데들리차지
        
        샤이닝 크로스는 십자가가 항상 남아있도록 유지함
        
        로얄 가드는 6초마다 사용하며 다른 스킬로 인해 약간 나중에 사용할 수도 있음. 로얄 가드 5중첩 버프를 상시 유지하도록 가정.
        '''
        
        GuardOfLight = core.BuffSkill("빛의 수호", 900, 30000, rem = True, red = True, cooltime = 180000, pdamage = 20).wrap(core.BuffSkillWrapper)
        
        LoyalGuardBuff = core.BuffSkill("로얄 가드", 0, 12000, att = 45).wrap(core.BuffSkillWrapper)  #10->15->20->30->45
        
        LoyalGuard_1 = core.DamageSkill("로얄 가드(1)", 630, 150+chtr.level*3, 2, cooltime = 6000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_2 = core.DamageSkill("로얄 가드(2)", 630, 200+chtr.level*3, 3, cooltime = 6000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_3 = core.DamageSkill("로얄 가드(3)", 630, 250+chtr.level*3, 4, cooltime = 6000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_4 = core.DamageSkill("로얄 가드(4)", 630, 250+chtr.level*3, 5, cooltime = 6000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        LoyalGuard_5 = core.DamageSkill("로얄 가드(5)", 630, 250+chtr.level*3, 7, cooltime = 6000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
        
        SoulAttack = core.BuffSkill("소울 어택", 0, 10000, cooltime = -1, pdamage_indep = 25, crit = 20).wrap(core.BuffSkillWrapper)
        
        FinalAttack = core.DamageSkill("파이널 어택", 0, 185*2, 0.75).setV(vEhc, 3, 4, False).wrap(core.DamageSkillWrapper)
        Booster = core.BuffSkill("부스터", 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        Invigorate = core.BuffSkill("격려", 0, 180000, rem = True, att = 30).wrap(core.BuffSkillWrapper)
        
        SoulAssult = core.DamageSkill("소울 어썰트", 600, 280, 8+1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)   #암흑 20%
        
        ShiningCross = core.DamageSkill("샤이닝 크로스", 640, 440, 4 + 1, cooltime = 7000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)   #암흑 30% 10초
        ShiningCrossInstall = core.SummonSkill("샤이닝 크로스(인스톨)", 0, 1200, 75, 4+1, 7000, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper)    #100% 암흑 5초
        
        #하이퍼
        SacredCube = core.BuffSkill("세이크리드 큐브", 90, 30000, cooltime = 210000, pdamage = 10).wrap(core.BuffSkillWrapper)
        DeadlyCharge = core.DamageSkill("데들리 차지", 810, 600, 10, cooltime = 15000).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        DeadlyChargeBuff = core.BuffSkill("데들리 차지(디버프)", 0, 10000, cooltime = -1, pdamage_indep = 10).wrap(core.BuffSkillWrapper)
        QueenOfTomorrow = core.BuffSkill("퀸 오브 투모로우", 0, 60000, cooltime = 120000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        CygnusPalanks = core.DamageSkill("시그너스 팔랑크스", 780, 450 + 18*vEhc.getV(3,3), 40 + vEhc.getV(3,3), cooltime = 30 * 1000).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        RoIias = core.BuffSkill("로 아이아스", 840, 75+3*vEhc.getV(0,0), red = True, cooltime = 300*1000, pdamage_indep = 5 + (35+3*int(vEhc.getV(0,0)*0.2))//2).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        ClauSolis = core.DamageSkill("클라우 솔리스", 900, 700+28*vEhc.getV(4,4), 7, red = True, cooltime = 12000).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)    #로얄가드 버프지속시간 6초 증가. 100% 암흑 5초
        ClauSolisSummon = core.SummonSkill("클라우 솔리스(소환)", 0, 5000, 350+14*vEhc.getV(4,4), 7, 9000, cooltime = -1).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)   #100% 암흑 5초
    
        SwordOfSoullight = core.BuffSkill("소드 오브 소울라이트", 1050, 30000, red = True, cooltime = 180*1000, patt = 15+int(0.5*vEhc.getV(1,1)), crit = 100, armor_ignore = 100).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)
        SoullightSlash = core.DamageSkill("소울 라이트 슬래시", 600, 650+26*vEhc.getV(1,1), 7).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        ##### Build Graph
        
        BasicAttack = core.OptionalElement(SwordOfSoullight.is_active, SoullightSlash, SoulAssult)
        BasicAttackWrapper = core.DamageSkill('기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)
        ClauSolis.onAfter(ClauSolisSummon)
        DeadlyCharge.onAfter(DeadlyChargeBuff)
        
        SoullightSlash.onAfter(FinalAttack)
        SoulAssult.onAfter(FinalAttack)
        
        ShiningCross.onAfter(ShiningCrossInstall)
        ShiningCross.onAfter(FinalAttack)
        
        LoyalGuard_5.onAfter(FinalAttack)
        
        ShiningCrossInstall.onTick(SoulAttack.controller(5000,"set_enabled_and_time_left"))
        ClauSolis.onAfter(SoulAttack.controller(5000,"set_enabled_and_time_left"))
        ClauSolis.onAfter(FinalAttack)
        ClauSolisSummon.onTick(SoulAttack.controller(5000,"set_enabled_and_time_left"))
    

        # 오라 웨폰
        auraweapon_builder = globalSkill.AuraWeaponBuilder(vEhc, 2, 2)
        for sk in [SoullightSlash, SoulAssult]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeaponCooltimeDummy = auraweapon_builder.get_buff()
        
        return(BasicAttackWrapper, 
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    GuardOfLight, LoyalGuardBuff, SoulAttack, Booster, Invigorate, SacredCube, 
                    DeadlyChargeBuff, QueenOfTomorrow, AuraWeaponBuff, RoIias, SwordOfSoullight,
                    globalSkill.soul_contract()] +\
                [CygnusPalanks, LoyalGuard_5, ShiningCross, DeadlyCharge, ClauSolis] +\
                [ShiningCrossInstall, ClauSolisSummon] +\
                [AuraWeaponCooltimeDummy] +\
                [BasicAttackWrapper])