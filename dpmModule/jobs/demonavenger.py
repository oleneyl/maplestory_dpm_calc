from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import warriors
from .jobclass import demon

### 데몬어벤져 직업 코드 (작성중)
# TODO: 스킬별 딜레이 추가, 5차 강화값 적용, 딜사이클
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
        OverwhelmingPower = core.InformedCharacterModifier("오버휄밍 파워", pdamage=30)
        DefenseExpertise = core.InformedCharacterModifier("디펜스 엑스퍼타이즈", armor_ignore = 30)
        DemonicSharpness = core.InformedCharacterModifier("데모닉 샤프니스", crit=20)

        # 메용: 체력+15%로 수정
        MapleHeroesDemon = core.InformedCharacterModifier("메이플 용사(데몬어벤져)", stat_main = 0.15*(25 + level * 5))
        # 최종데미지 (릴리즈 오버로드, 데몬 프렌지)
        InnerStrength = core.InformedCharacterModifier("이너 스트렝스", stat_main = 600)
        DiabolicRecovery = core.InformedCharacterModifier("디아볼릭 리커버리", pstat_main=25)

        HP_RATE = 100
        #최대 HP 대비 소모된 HP 3%(24레벨가지는 4%)당 최종 데미지 1% 증가
        FrenzyPassive = core.InformedCharacterModifier("데몬 프렌지 (최종 데미지)", pdamage_indep = (100 - HP_RATE) // (4 - (self.vEhc.getV(0, 0) // 25)))
        return [AbyssalRage, AdvancedDesperadoMastery, OverwhelmingPower, DefenseExpertise, DemonicSharpness, MapleHeroesDemon, InnerStrength, DiabolicRecovery, FrenzyPassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)
        
        return [WeaponConstant, Mastery]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        코강 순서: 익시드 엑스큐션, 실드 체이싱 -> 문라이트 슬래시(사용하지 않음)
        '''
        '''
        TODO:
        이즈 익시드 페인(익시드 스킬 데미지 20% 증가) - 어떤 스킬에 적용되는 것인지 확인필요

        하이퍼: 익시드 - 리인포스: 익시드 스킬 데미지 20% 증가

        오라 웨폰 - 작성 필요
        이계 여신의 축복 - 이 스킬을 과연 쓰는가?

        데몬 프렌지 - DPM 기준을 어떻게 할것인지?
        블러드 피스트 - 작성 필요
        디멘션 소드 - 작성 필요
        '''
        #V코어 값은 전면 재작성 필요
        
        # TODO: OptionalElement로 변경해야 함
        # 익시드 0~4스택
        Execution = core.DamageSkill("익시드: 엑스큐션", 0, 540, 4, modifier = core.CharacterModifier(armor_ignore = 30)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        # 익시드 5스택 이상
        ExecutionExceed = core.DamageSkill("익시드: 엑스큐션 (강화)", 540, 540, 6, modifier = core.CharacterModifier(armor_ignore = 30)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        # 방어력 2배 무시가 30퍼를 한번 더 계산하는건지, 아니면 60퍼로 적용되는건지 알아볼 필요가 있음.
        # 최대 10회 공격
        # 공격 주기 등 정보를 알아야 젱확히 작성가능
        ShieldChasing = core.SummonSkill("실드 체이싱", 0, 0, 500, 2, 5000-1, cooltime = 6000, modifier = core.CharacterModifier(armor_ignore = 30, pdamage=20), red = True).isV(vEhc,1,1).wrap(core.SummonSkillWrapper)

        ArmorBreak = core.DamageSkill("아머 브레이크", 0, 350, 4, cooltime = 30 * 1000).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        ArmorBreakBuff = core.BuffSkill("아머 브레이크(디버프)", 0, 30*1000, armor_ignore = 30).wrap(core.BuffSkillWrapper)

        ThousandSword = core.Damageskill("사우전드 소드", 0, 500, 8, cooltime = 8*1000).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)

        # 보너스 찬스 70% -> 80%
        EnhancedExceed = core.DamageSkill("인핸스드 익시드", 0, 200, 2*0.8).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)

        #일정 주기로 마족의 피가 바닥에 뿌려져 5초 동안 최대 10명의 적을 일정주기 마다 300+8n%로 2번 공격
        FrenzyDOT = core.DamageSkill("프렌지 장판", 0, 300 + 8 * vEhc.getV(0, 0), 2).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        #BatSwarm = core.SummonSkill("배츠 스웜", 0, 0, 200, 1, 0)

        #BloodImprison = core.DamageSkill("블러디 임프리즌", 0, 800, 3, cooltime = 120*1000)

        #Buff skills
        Exceed = core.BuffSkill("익시드", 0, 99999999).wrap(core.BuffSkillWrapper)
        Exceed = core.StackSkillWrapper(Exceed, 18)
        Exceed.set_name_style("익시드 %d스택")
        Exceed.set_stack(0)

        ForbiddenContract = core.BuffSkill("포비든 컨트랙트", 0, 30*1000, cooltime = 75*1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        DemonicFortitude = core.BuffSkill("데모닉 포티튜드", 0, 60*1000, cooltime=120*1000, pdamage=10).wrap(core.BuffSkillWrapper)

        ReleaseOverload = core.BuffSkill("릴리즈 오버로드", 0, 60*1000, pdamage_indep= 25).wrap(core.BuffSkillWrapper)
        CallMastema = core.SummonSkill("콜 마스테마", 690, 5000, 500 + vEhc.getV(4,4)*20, 8, (30+vEhc.getV(4,4))*1000, cooltime = 150*1000).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)
        #CallMastemaAnother = core.SummonSkill("콜 마스테마+", 0, ).wrap(core.BuffSkillWrapper)    #러블리 테리토리..데미지 없음.
        
        DimensionSword = core.SummonSkill("디멘션 소드", 0, 3000, 1250+14*vEhc.getV(0,0), 8, 40*1000, cooltime = 120*1000, modifier=core.CharacterModifier(armor_ignore=100)).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)
        DimensionSwordReuse = core.SummonSkill("디멘션 소드 (재시전)", 0, 0, 300+vEhc.getV(0,0)*12, 6, 8*1000, cooltime=120*1000, modifier=core.CharacterModifier(armor_ignore=100)).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)
        ######   Skill Wrapper   ######
        # TODO: 딜사이클을 알아야 작성가능
        '''딜 사이클 정리
        
        '''
        
        ArmorBreak.onAfter(ArmorBreakBuff.controller(1))
        Execution.onAfter(EnhancedExceed)
        ExecutionExceed.onAfter(EnhancedExceed)
        ReleaseOverload.onAfter(Exceed.set_stack(0))

        ExceedOpt = core.OptionalElement(Exceed.judge(5, 1), ExecutionExceed, Execution)

        #사우전드 소드 : 사용 시 익시드 오버로드 5 증가
        ThousandSword.onAfter(Exceed.stackController(5))

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 3, 2)
        for sk in [Execution, ExecutionExceed, ShieldChasing, ArmorBreak, ThousandSword]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeaponCooltimeDummy = auraweapon_builder.get_buff()
        
        return(BasicAttackWrapper,
               [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    Booster, DevilCryBuff, InfinityForce, Metamorphosis, BlueBlood, DemonFortitude, AuraWeaponBuff, DemonAwakning,
                    globalSkill.soul_contract()] +\
                [Execution, Cerberus, DevilCry, SpiritOfRageEnd] +\
                [MetamorphosisSummon, CallMastema, DemonAwakningSummon, SpiritOfRage, Orthros, Orthros_] +\
                [AuraWeaponCooltimeDummy] +\
                [BasicAttackWrapper])