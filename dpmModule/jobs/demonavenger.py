from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill

### 데몬어벤져 직업 코드 (작성중)
######   Passive Skill   ######


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.jobtype = "hp"
        self.vEnhanceNum = 15
        self.preEmptiveSkills = 1
        
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'reuse', 'mess')
    
    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 20)

    def get_passive_skill_list(self):

        
        #와일드레이지 : 데미지10%, 링크에 반영되므로 미고려.
        #주스탯 미반영, 추가바람.
        AbyssalRage = core.InformedCharacterModifier("어비셜 레이지", att=40)
        AdvancedDesperadoMastery = core.InformedCharacterModifier("어드밴스드 데스페라도 마스터리",att = 50, crit_damage = 8)
        OverwhelmingPower = core.InformedCharacterModifier("오버휄밍 파워", pdamage=40)
		DefenseExpertise = core.InformedCharacterModifier("디펜스 엑스퍼타이즈", armor_ignore = 30)
		DemonicSharpness = core.InformedCharacterModifier("데모닉 샤프니스", crit=20)

# 최종데미지 (릴리즈 오버로드, 데몬 프렌지)
        ## 이하 내용 데슬 기반
        DeathCurse = core.InformedCharacterModifier("데스 커스",pdamage = 1)
        Outrage = core.InformedCharacterModifier("아웃레이지",att = 50, crit = 20)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        Concentration = core.InformedCharacterModifier("컨센트레이션",pdamage_indep = 25)
        
        
        DarkBindPassive = core.InformedCharacterModifier("다크 바인드(패시브)", armor_ignore = 30)
        
        return [DeathCurse, Outrage, PhisicalTraining, Concentration, AdvancedWeaponMastery, DarkBindPassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)        

        EvilTorture = core.InformedCharacterModifier("이블 토쳐",pdamage_indep = 15, crit = 15) #상태이상에 걸렷을때만.
        
        return [WeaponConstant, Mastery, EvilTorture]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        코강 순서:
        슬래시-임팩트-서버-익스플로전-메타-데빌크라이

        #####하이퍼 #####
        # 데몬슬래시 - 리인포스, 리메인타임 리인포스
        # 데몬 입팩트 - 리인포스, 보너스 어택, 리듀스 포스        
        '''

    

        #Buff skills
        # 펫에 등록한 걸로 가정.
        #Booster = core.BuffSkill("부스터", 600, 180*1000, rem = True).wrap(core.BuffSkillWrapper)
        
        
        #5차스킬 (수정필요)
        AuraWeaponBuff = core.BuffSkill("오라웨폰 버프", 0, (80 +2*vEhc.getV(2,2)) * 1000, cooltime = 180 * 1000, armor_ignore = 15, pdamage_indep = (vEhc.getV(1,1) // 5)).isV(vEhc,2,2).wrap(core.BuffSkillWrapper)  #두 스킬 syncronize 할 것!
        AuraWeaponCooltimeDummy = core.BuffSkill("오라웨폰(딜레이 더미)", 0, 6000, cooltime = -1).wrap(core.BuffSkillWrapper)   # 한 번 발동된 이후에는 6초간 발동되지 않도록 합니다.
    
        CallMastema = core.SummonSkill("콜 마스테마", 690, 5000, 1100, 8, (30+vEhc.getV(4,4))*1000, cooltime = 150*1000).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)
        #CallMastemaAnother = core.SummonSkill("콜 마스테마+", 0, ).wrap(core.BuffSkillWrapper)    #러블리 테리토리..데미지 없음.
        
        ######   Skill Wrapper   ######
        '''딜 사이클 정리
        
        이하 소스는 데몬슬레이어 복붙이므로 처음부터 작성해야 함.
        '''
        

        # 오라 웨폰
        def AuraWeapon_connection_builder(origin_skill, target_skill):
            optional = core.OptionalElement(lambda : (AuraWeaponCooltimeDummy.is_not_active() and AuraWeaponBuff.is_active()), target_skill)
            origin_skill.onAfter(optional)
            target_skill.onAfter(AuraWeaponCooltimeDummy)
            
        AuraWeapon_connection_builder(DemonSlashAWBB1, DemonSlashAWBB1_AuraWeapon)
        AuraWeapon_connection_builder(DemonSlashAWBB2, DemonSlashAWBB2_AuraWeapon)
        AuraWeapon_connection_builder(DemonSlashAWBB3, DemonSlashAWBB3_AuraWeapon)
        AuraWeapon_connection_builder(DemonSlashAWBB4, DemonSlashAWBB4_AuraWeapon)
        AuraWeapon_connection_builder(DemonImpact, DemonImpact_AuraWeapon)
        
        return(BasicAttackWrapper,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    Booster, DevilCryBuff, InfinityForce, Metamorphosis, BlueBlood, DemonFortitude, AuraWeaponBuff, DemonAwakning,
                    globalSkill.soul_contract()] +\
                [Cerberus, DevilCry, SpiritOfRageEnd] +\
                [MetamorphosisSummon, CallMastema, DemonAwakningSummon, SpiritOfRage, Orthros, Orthros_] +\
                [AuraWeaponCooltimeDummy] +\
                [BasicAttackWrapper])