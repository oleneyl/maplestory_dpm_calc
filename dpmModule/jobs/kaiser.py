from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill, linkSkill
from .jobbranch import warriors

#Combo Instinct - generated sub deal
#TODO: [윌 오브 소드-스트라이크] : 불길 적중 시 드라코슬래셔의 재사용 대기시간이 즉시 초기화되고 이후 3회 드라코 슬래셔의 재사용 대기시간이 적용되지 않는버프가 걸리는 기능이 추가됩니다. 해당 버프는 윌 오브 소드-스트라이크의재사용 대기시간 동안만 유지됩니다.
######   Passive Skill   ######
class MorphGaugeWrapper(core.StackSkillWrapper):
    def __init__(self, skill):
        super(MorphGaugeWrapper, self).__init__(skill, 700)
        self.set_name_style("+%d")
        
    def vary(self, d):
        if not self.is_active() or d<0:
            return super(MorphGaugeWrapper, self).vary(d)
        else:
            return core.ResultObject(0, core.CharacterModifier(), 0, sname = self._id, spec = 'graph control')

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vSkillNum = 5
        self.vEnhanceNum = 13
        self.jobtype = "str"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1
        
    def get_passive_skill_list(self):
        InnerBlaze = core.InformedCharacterModifier("이너 블레이즈",stat_main = 20)
        AdvancedInnerBlaze = core.InformedCharacterModifier("어드밴스드 이너 블레이즈",stat_main = 30)
        # 모프 게이지 단계당 데미지 3% 증가
        IronWill = core.InformedCharacterModifier("아이언 윌",pdamage = 9)
        Catalyze = core.InformedCharacterModifier("카탈라이즈",patt=30, pdamage_indep=20)
        AdvancedWillOfSwordPassive = core.InformedCharacterModifier("어드밴스드 윌 오브 소드(패시브)",att = 20)
        UnflinchingCourage = core.InformedCharacterModifier("언플린칭 커리지",armor_ignore = 40)
        AdvancedSwordMastery = core.InformedCharacterModifier("어드밴스드 소드 마스터리", att = 30, crit_damage = 15, crit=20)
    
        return [InnerBlaze, AdvancedInnerBlaze, Catalyze, 
                AdvancedWillOfSwordPassive, UnflinchingCourage, AdvancedSwordMastery]
                
    def get_not_implied_skill_list(self):        
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 34)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)
        
        ReshuffleSwitchAttack = core.InformedCharacterModifier("리셔플스위치:공격",att = 45, crit = 20, boss_pdamage = 18 + 10)
        
        return [WeaponConstant, Mastery, ReshuffleSwitchAttack]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        모프게이지 3단계(700)
        피규레이션은 벞지 영향을 받음
        
        기가, 체인풀, 소스 +5
        모프 수급량
        어윌소 12*5
        인퍼널40
        프로미넌스 40
        윙비트 공격당 5
        커맨드윙비트 타당 10
        기가슬래셔 12.5
        블루스트릭 1회당 12.5
        
        하이퍼 : 기가 슬래셔 리인포스 / 보너스 어택
        윙비트 : 리인포스, 퍼시스트, 엑스트라 어택
        
        36000/28 = 1290초(조상님)
        
        V강화 : 기가/윙비트/소드 스트라이크/윌오소
        '''

        
        #Buff skills
        RegainStrenth = core.BuffSkill("리게인 스트렝스", 0, 240000, rem = True, pdamage_indep = 15).wrap(core.BuffSkillWrapper)
        BlazeUp = core.BuffSkill("블레이즈 업", 0, 240000, att = 20, rem = True).wrap(core.BuffSkillWrapper)
    
        FinalFiguration = core.BuffSkill("파이널 피규레이션", 0, 60000, pdamage_indep = 15, cooltime = -1).wrap(MorphGaugeWrapper)
        Wingbit_1 = core.SummonSkill("윙비트", 360, 300, 200, 1, 19400, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 3, False).wrap(core.SummonSkillWrapper)  #48타
        Wingbit_2 = core.SummonSkill("윙비트(2)", 360, 300, 200, 1, 19400, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 3, False).wrap(core.SummonSkillWrapper)  #48타
        
        GigaSlasher_ = core.DamageSkill("기가 슬래셔", 540, 330, 9+1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        GigaSlasher_Fig = core.DamageSkill("기가 슬래셔(변신)", 540, 330, 11+1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
    
        AdvancedWillOfSword = core.DamageSkill("어드밴스드 윌 오브 소드(시전)", 180, 0, 0, cooltime = 10000).wrap(core.DamageSkillWrapper)
        
        AdvancedWillOfSword_ = core.DamageSkill("어드밴스드 윌 오브 소드", 0, 400, 4*5, cooltime = 10000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        AdvancedWillOfSword_Fig = core.DamageSkill("어드밴스드 윌 오브 소드(변신)", 0, 400, (4+1)*5, cooltime = 10000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
    
        SwordStrike = core.DamageSkill("소드 스트라이크", 600 , 300, 5).wrap(core.DamageSkillWrapper)#쿨타임 모름, 실전 미사용.
        SwordStrike_ = core.DamageSkill("소드 스트라이크(폭발)", 0, 225, 4).wrap(core.DamageSkillWrapper)
    
        InfernalBreath = core.DamageSkill("인퍼널 브레스", 1170, 300, 8).wrap(core.DamageSkillWrapper)
    
        #하이퍼
        MajestyOfKaiser = core.BuffSkill("마제스티 오브 카이저", 670, 30000, att = 30, cooltime = 90000).wrap(core.BuffSkillWrapper)
        FinalTrance = core.BuffSkill("파이널 트랜스", 0, 60000, cooltime = 300000).wrap(core.BuffSkillWrapper)#딜레이 모름
            
        Phanteon = core.DamageSkill("판테온", 510, 600+24*vEhc.getV(4,4), 8).wrap(core.DamageSkillWrapper)  #사용안함
        GuardianOfNova_1 = core.SummonSkill("가디언 오브 노바(1)", 600, 1290, 450+15*vEhc.getV(2,2), 4, (30+int(0.5*vEhc.getV(2,2)))*1000, cooltime = 120000).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
        GuardianOfNova_2 = core.SummonSkill("가디언 오브 노바(2)", 0, 1290, 250+10*vEhc.getV(2,2), 6, (30+int(0.5*vEhc.getV(2,2)))*1000, cooltime = -1).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
        GuardianOfNova_3 = core.SummonSkill("가디언 오브 노바(3)", 0, 1290, 900+35*vEhc.getV(2,2), 2, (30+int(0.5*vEhc.getV(2,2)))*1000, cooltime = -1).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
    
        WillOfSwordStrikeJudge = core.DamageSkill("윌 오브 소드:(스트라이크)(시전)", 0, 0, 0, cooltime = 30000).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
    
        WillOfSwordStrike = core.DamageSkill("윌 오브 소드: 스트라이크", 0, 500+20*vEhc.getV(3,3), 4*5).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        WillOfSwordStrike_ = core.DamageSkill("윌 오브 소드: 스트라이크(폭발)", 0, 1000+14*vEhc.getV(3,3), 6*5).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        
        WillOfSwordStrike_Fig = core.DamageSkill("윌 오브 소드: 스트라이크(변신)", 0, 500+20*vEhc.getV(3,3), (4+1)*5).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        WillOfSwordStrike_Fig_ = core.DamageSkill("윌 오브 소드:스 트라이크(폭발)(변신)", 0, 1000+40*vEhc.getV(3,3), (6+1)*5).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)  
        
        DrakeSlasher_Dummy = core.DamageSkill("드라코 슬래셔(시전)", 540, 0, 0, cooltime = (7-(vEhc.getV(0,0)//15))*1000).wrap(core.DamageSkillWrapper)
        
        DrakeSlasher = core.DamageSkill("드라코 슬래셔(추가타)", 0, 500+5*vEhc.getV(0,0), 10+1, modifier = core.CharacterModifier(crit=100, armor_ignore=50) + core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        DrakeSlasher_ = core.DamageSkill("드라코 슬래셔", 0, 500+5*vEhc.getV(0,0), 6+1, modifier = core.CharacterModifier(crit=100, armor_ignore=50) + core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        
        DrakeSlasher_Fig = core.DamageSkill("드라코 슬래셔(추가타)(변신)", 0, 500+5*vEhc.getV(0,0), 10+2+1, modifier = core.CharacterModifier(crit=100, armor_ignore=50) + core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        DrakeSlasher_Fig_ = core.DamageSkill("드라코 슬래셔(변신)", 0, 500+5*vEhc.getV(0,0), 6+2+1, modifier = core.CharacterModifier(crit=100, armor_ignore=50) + core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
        
        MorphGauge = FinalFiguration
        FinalFigurationReset = core.DamageSkill("파이널 피규레이션", 0, 0, 0).wrap(core.DamageSkillWrapper)
        FinalFigurationReset.onAfter(FinalFiguration)
        FinalFigurationReset.onAfter(FinalFiguration.stackController(-9999, name = "게이지 리셋"))

        Morph = core.OptionalElement(partial(MorphGauge.judge, 699, 1), FinalFigurationReset, name = "게이지 충전시 변신")
        FinalTrance.onAfter(FinalFiguration)
        
        FinalFigurationTurnedOn = core.ConstraintElement("파이널 피규레이션 여부 확인", FinalFiguration, FinalFiguration.is_not_active)
        FinalTrance.onConstraint(FinalFigurationTurnedOn)
        
        #윙비트
        Wingbit_1.onAfter(Wingbit_2)
        
        #기본공격 --> BasicAttack
        DrakeSlasher.onAfter(DrakeSlasher_)
        DrakeSlasher_Fig.onAfter(DrakeSlasher_Fig_)
        DrakeSlasher_Opt = core.OptionalElement(FinalFiguration.is_active, DrakeSlasher_Fig, DrakeSlasher, name = "변신시")
        DrakeSlasher_Dummy.onAfter(DrakeSlasher_Opt)
        
        GigaSlasher = core.OptionalElement(FinalFiguration.is_active, GigaSlasher_Fig, GigaSlasher_, name = "변신시")
        
        BasicAttack = core.OptionalElement(DrakeSlasher_Dummy.is_available, DrakeSlasher_Dummy, GigaSlasher, name = "드라코 슬래셔 충전시")
        BasicAttackWrapper = core.DamageSkill('기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)
        WillOfSwordStrike.onAfter(WillOfSwordStrike_)
        WillOfSwordStrike_Fig.onAfter(WillOfSwordStrike_Fig_)
        WillOfSwordStrike_Opt = core.OptionalElement(FinalFiguration.is_active, WillOfSwordStrike_Fig, WillOfSwordStrike, name = "변신시")
        WillOfSwordStrikeJudge.onAfter(WillOfSwordStrike_Opt)
        
        AdvancedWillOfSword_Opt = core.OptionalElement(FinalFiguration.is_active, AdvancedWillOfSword_Fig, AdvancedWillOfSword_, name = "변신시")
        
        AdvancedWillOfSword.onAfter(core.OptionalElement(WillOfSwordStrikeJudge.is_available, WillOfSwordStrikeJudge, AdvancedWillOfSword_Opt, name = "윌오소스 사용 가능시"))
        
        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 1, 1)
        for sk in [GigaSlasher_, GigaSlasher_Fig, DrakeSlasher, DrakeSlasher_, DrakeSlasher_Fig, DrakeSlasher_Fig_]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeaponCooltimeDummy = auraweapon_builder.get_buff()
        
        #쿨 초기화
        MajestyOfKaiser.onAfters([WillOfSwordStrike.controller(1)])
        
        #조상님
        GuardianOfNova_1.onAfters([GuardianOfNova_2, GuardianOfNova_3])
        
        #스택량 계산
        for sk, incr in [[DrakeSlasher_Opt, 5],
                            [GigaSlasher, 5],
                            [AdvancedWillOfSword_Opt, 60],
                            [InfernalBreath, 40]]:
            sk.onAfter(MorphGauge.stackController(incr))
            sk.onAfter(Morph)
        
        for sk in [WillOfSwordStrikeJudge, DrakeSlasher_Dummy]:
            sk.protect_from_running()

        Wingbit_1.onTick(MorphGauge.stackController(5))
        Wingbit_2.onTick(MorphGauge.stackController(5))

        #윌오브소드:스트라이크
        #V1.2.324KMS [윌 오브 소드-스트라이크] : 불길 적중 시 드라코슬래셔의 재사용 대기시간이 즉시 초기화되고 이후 3회 드라코 슬래셔의 재사용 대기시간이 적용되지 않는버프가 걸리는 기능이 추가됩니다. 해당 버프는 윌 오브 소드-스트라이크의재사용 대기시간 동안만 유지됩니다.
        DrakeSlasherReset = core.StackSkillWrapper(core.BuffSkill('드라코 슬래셔 - 재사용 초기화', 0, 0), 3)
        judge_reset = core.OptionalElement(lambda:DrakeSlasherReset.judge(1, 1), DrakeSlasher_Dummy.controller(1.0, 'reduce_cooltime_p'))
        DrakeSlasher_Dummy.onAfter(judge_reset)
        DrakeSlasher_Dummy.onAfter(DrakeSlasherReset.stackController(-1))
        WillOfSwordStrikeJudge.onAfter(DrakeSlasherReset.stackController(3))
    
        return(BasicAttackWrapper,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    RegainStrenth, BlazeUp, FinalFiguration, MajestyOfKaiser, FinalTrance, AuraWeaponBuff, AuraWeaponCooltimeDummy,
                    linkSkill.soul_contract()] +\
                [AdvancedWillOfSword] +\
                [Wingbit_1, Wingbit_2, GuardianOfNova_1, GuardianOfNova_2, GuardianOfNova_3] +\
                [WillOfSwordStrikeJudge, DrakeSlasher_Dummy] +\
                [BasicAttackWrapper])