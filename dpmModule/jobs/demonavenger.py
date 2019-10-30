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
        
        ReleaseOverload = core.InformedCharacterModifier("릴리즈 오버로드", pdamage_indep = 25)
        # 메용: 체력+15%로 수정
        MapleHeroesDemon = core.InformedCharacterModifier("메이플 용사(데몬어벤져)", stat_main = 0.15*(25 + level * 5))
# 최종데미지 (릴리즈 오버로드, 데몬 프렌지)
        ## 이하 내용 데슬 기반
        
        return [DeathCurse, Outrage, PhisicalTraining, Concentration, AdvancedWeaponMastery, DarkBindPassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)
        
        return [WeaponConstant, Mastery, EvilTorture]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        코강 순서:
        '''
'''
        TODO: 이너 스트렝스, 디아볼릭 리커버리
        이즈 익시드 페인(익시드 스킬 데미지 20% 증가)
        메용 패시브: HP 15%

        하이퍼: 익시드 - 리인포스: 익시드 스킬 데미지 20% 증가
        하이퍼: 실드 체이싱-엑스트라 타겟 : 영구적으로 실드 체이싱의 방패 1개 당 최대 공격 횟수 2 증가

        하이퍼: 포비든 컨트랙트: 30초간 데미지 10%, 쿨타임 75초

        하이퍼: 사우전드 소드 : 이 스킬을 보스전에서 쓰나? 최대 HP의 15% 소비, 최대 14명의 적 500% 데미지로 8번 공격. 사용 시 익시드 오버로드 5 증가. 재사용 대기시간 8초
        오라 웨폰
        이계 여신의 축복 - 이 스킬을 과연 쓰는가?

        데몬 프렌지 - DPM 기준을 어떻게 할것인지?
        블러드 피스트 - 이 스킬을 과연 쓰는가?
        디멘션 소드 - 이 스킬을 과연 쓰는가?
        '''

        #V코어 관련부분은 전면 재작성 필요


        Execution = core.DamageSkill("익시드: 엑스큐션", 0, 540, 4, modifier = core.CharacterModifier(armor_ignore = 30)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        ExecutionExceed = core.DamageSkill("익시드: 엑스큐션 (강화)", 0, 540, 6, modifier = core.CharacterModifier(armor_ignore = 30)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        # 방어력 2배 무시가 30퍼를 한번 더 계산하는건지, 아니면 60퍼로 적용되는건지 알아볼 필요가 있음.
        ShieldChasing = core.DamageSkill("실드 체이싱", 0, 500, 2 * 8, cooltime = 6 * 1000, red = True, modifier = core.CharacterModifier(armor_ignore = 30, pdamage = 20)).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        ArmorBreak = core.DamageSkill("아머 브레이크", 0, 350, 4, cooltime = 30 * 1000).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        ArmorBreakBuff = core.BuffSkill("아머 브레이크(디버프)", 0, 30*1000, armor_ignore = 30, cooltime=99999*1000).wrap(core.BuffSkillWrapper)

        ThousandSword = core.Damageskill("사우전드 소드", 0, 500, 8, cooltime = 8*1000).setV(vEhc, 0, 0, False).wrap(core.DamageSkillWrapper)

        # 보너스 찬스 70% -> 80%
        EnhancedExceed = core.DamageSkill("인핸스드 익시드", 0, 200, 2*0.8).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)

        FrenzyDOT = core.DamageSkill("프렌지 장판", 0, 300 + 8 * vEhc.getV(0, 0), 2).setV(vEhc, 0, 0, True).wrap(core.DamageSkillWrapper)

        #Buff skills
        Exceed = core.BuffSkill("익시드", 0, 99999999)
        Exceed = core.StackSkillWrapper(Exceed, 18)
        Exceed.set_name_style("익시드 %d스택")
        Exceed.set_stack(0)

        ForbiddenContract = core.BuffSkill("포비든 컨트랙트", 0, 30*1000, cooltime = 75*1000, pdamage = 10)
        DemonicFortitude = core.BuffSkill("데모닉 포티튜드", 0, 60*1000, cooltime=120*1000, pdamage=10)

        ReleaseOverload = core.BuffSkill("릴리즈 오버로드", 0, 60*1000, pdamage_indep= 25)
        CallMastema = core.SummonSkill("콜 마스테마", 690, 5000, 1100, 8, (30+vEhc.getV(4,4))*1000, cooltime = 150*1000).isV(vEhc,4,4).wrap(core.SummonSkillWrapper)
        #CallMastemaAnother = core.SummonSkill("콜 마스테마+", 0, ).wrap(core.BuffSkillWrapper)    #러블리 테리토리..데미지 없음.
        
        ######   Skill Wrapper   ######
        '''딜 사이클 정리
        
        '''
        
        ArmorBreak.onAfter(ArmorBreakBuff.controller(1))
        Execution.onAfter(EnhancedExceed)
        ExecutionExceed.onAfter(EnhancedExceed)

        ThousandSword.onAfter(Exceed.stackController(5))

        # 오라 웨폰
        
        return(BasicAttackWrapper,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    Booster, DevilCryBuff, InfinityForce, Metamorphosis, BlueBlood, DemonFortitude, AuraWeaponBuff, DemonAwakning,
                    globalSkill.soul_contract()] +\
                [Cerberus, DevilCry, SpiritOfRageEnd] +\
                [MetamorphosisSummon, CallMastema, DemonAwakningSummon, SpiritOfRage, Orthros, Orthros_] +\
                [AuraWeaponCooltimeDummy] +\
                [BasicAttackWrapper])