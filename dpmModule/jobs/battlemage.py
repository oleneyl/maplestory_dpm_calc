from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule
from . import globalSkill
from .jobclass import resistance
from .jobbranch import magicians
# TODO: 오버로드 마나를 정말 안쓰는 것인지 확인필요

# TODO: [블랙 매직 알터] : 제단이 설치되어 있지 않을 때 아래 방향키와 함께 사용하면 자신의 위치와 전방에 총 2개의 제단이 한번에 설치되는 기능이 추가됩니다. 설치 개수가 2개를 초과했을 때 초과한 개수에 비례해 저주의 이동속도가 증가하는 기능이 공격 횟수가 증가하는 기능으로 변경됩니다.

######   Passive Skill   ######

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.jobtype = "int"
        self.vEnhanceNum = 10
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'reuse')
        self.preEmptiveSkills = 2

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('마스터 오브 데스', '그림 리퍼'), RuleSet.BASE)
        return ruleset

    def apply_complex_options(self, chtr):
        chtr.add_property_ignorance(10)

    def get_passive_skill_list(self):
        ArtOfStaff = core.InformedCharacterModifier("아트 오브 스태프",att = 20, crit = 15)
        StaffMastery = core.InformedCharacterModifier("스태프 마스터리",att = 30, crit = 20)
        HighWisdom =  core.InformedCharacterModifier("하이 위즈덤",stat_main = 40)
        BattleMastery = core.InformedCharacterModifier("배틀 마스터리",pdamage_indep = 15, crit_damage = 20)
        DarkAuraPassive = core.InformedCharacterModifier("다크 오라(패시브)", patt=15)
        
        #택 1
        #DarkAura = core.InformedCharacterModifier(pdamage = 20, boss_pdamage = 10)
        StaffExpert = core.InformedCharacterModifier("스태프 엑스퍼트",att = 30, crit_damage = 20)
        SpellBoost = core.InformedCharacterModifier("스펠 부스트", patt = 25, pdamage = 10, armor_ignore = 30)
        
        return [ArtOfStaff, StaffMastery, HighWisdom, BattleMastery, DarkAuraPassive, StaffExpert, SpellBoost] #디버프오라 미적용

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수")
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -2.5)
        
        DebuffAura = core.InformedCharacterModifier("디버프 오라", armor_ignore = 20, pdamage_indep = 10)
        BattleRage = core.InformedCharacterModifier("배틀 레이지",pdamage = 40, crit_damage = 8, crit=20)
        return [WeaponConstant, Mastery, DebuffAura, BattleRage ]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        오라스위칭 미사용
        디버프 오라 사용
        알터 히트율 100%, 50초마다 40초간 유지되는 2개 알터 사용
        
        코강 순서 : 
        닼라-피블-데스-킹바-닼제네-배틀스퍼트
        알터 설치시간 3450s
        
        좌우텔 분당 83회
        좌우텔/피블텔
        
        마스터 오브 데스는 리퍼와 같이 사용함
        알터는 쿨마다 사용함
        '''
        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper)    #딜레이 모름
        WillOfLiberty = core.BuffSkill("윌 오브 리버티", 0, 60*1000, cooltime = 120*1000, pdamage = 10).wrap(core.BuffSkillWrapper)

        DarkLightening = core.DamageSkill("다크 라이트닝", 0, 225, 4, modifier = core.CharacterModifier(pdamage = 60)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper) #캔슬
        DarkLighteningMark = core.DamageSkill("다크 라이크닝 (마크)", 0, 350, 4, modifier = core.CharacterModifier(boss_pdamage=20, pdamage = 60)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        MarkStack = core.StackSkillWrapper(core.BuffSkill("마크 스택", 0, 99999*10000), 1)
        
        #배페 좌우텔 분당 86회 기준.
        FinishBlow_ = core.DamageSkill("피니쉬 블로우", 720, 330, 6, modifier = core.CharacterModifier(crit=25, armor_ignore=20) + core.CharacterModifier(pdamage_indep = 8+vEhc.getV(3,3)//10)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        FinishBlow_M = core.DamageSkill("피니쉬 블로우(마오데)", 720, 330, 6+1, modifier = core.CharacterModifier(crit=25, armor_ignore=20) + core.CharacterModifier(pdamage_indep = 8+vEhc.getV(3,3)//10)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        FinishBlow_U = core.DamageSkill("사신의 낫", 720+60, 300, 12, modifier = core.CharacterModifier(crit=25, armor_ignore=20) + core.CharacterModifier(pdamage_indep = 8+vEhc.getV(3,3)//10)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        FinishBlow_M_U = core.DamageSkill("사신의 낫(마오데)", 720+60, 300, 12+1, modifier = core.CharacterModifier(crit=25, armor_ignore=20) + core.CharacterModifier(pdamage_indep = 8+vEhc.getV(3,3)//10)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        # 마스터 오브 데스의 지속시간 중 데스의 최종 데미지 50% 증가
        # 올바르게 작동하는지 확인 필요
        Death = core.SummonSkill("데스", 0, 5000, 200+chtr.level, 12, 99999*100000).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper)
        DeathAfterMOD = core.SummonSkill("데스 (마스터 오브 데스)", 0, 5000, (200+chtr.level) * 0.5, 12, 30*1000, cooltime = -1).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper)
        
        RegistanceLineInfantry = resistance.ResistanceLineInfantryWrapper(vEhc, 4, 4)
        UnionAura = core.BuffSkill("유니온 오라", 810, (vEhc.getV(1,1)//2+25)*1000, cooltime = 100*1000, pdamage=20, boss_pdamage=10, att=50).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)
        BlackMagicAlter = core.SummonSkill("블랙 매직 알터", 690 * 2*2.5, 800, 800+32*vEhc.getV(0,0), 4, 40*1000, cooltime = 50*1000).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)    #가동률 60%
        GrimReaper = core.SummonSkill("그림 리퍼", 720, 4000, 800+32*vEhc.getV(2,2), 12, 62*1000, cooltime=100*1000).isV(vEhc,2,2).wrap(core.SummonSkillWrapper) #공격시 지속2초증가->지속62s
    
        MasterOfDeath = core.BuffSkill("마스터 오브 데스", 1020, 30*1000, cooltime = 200*1000, red=False).wrap(core.BuffSkillWrapper)
        BattlekingBar = core.DamageSkill("배틀킹 바", 200, 650, 2, cooltime = 13*1000, modifier = core.CharacterModifier(pdamage_indep = 8+vEhc.getV(3,3)//10)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        BattlekingBar2 = core.DamageSkill("배틀킹 바(2타)", 250, 650, 5, modifier =  core.CharacterModifier(pdamage_indep = 8+vEhc.getV(3,3)//10)).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        
        DarkGenesis = core.DamageSkill("다크 제네시스", 870, 520, 8, cooltime = 30*1000).wrap(core.DamageSkillWrapper)
        DarkGenesisFinalAttack = core.DamageSkill("다크 제네시스(추가타)", 0, 220, 0.6).wrap(core.DamageSkillWrapper)
        #Damage Skills
        
        FinalAttack = core.OptionalElement(DarkGenesis.is_not_usable, DarkGenesisFinalAttack, name = "다크 제네시스 추가타 검증")
        
        UseStack = MarkStack.stackController(-1, "마크 사용")
        DarkLighteningMark.onAfter(UseStack)
        UseMark = core.OptionalElement(partial(MarkStack.judge, 1, 1), DarkLighteningMark, name ='마크 사용여부 결정')
        
        IsUnion_ = core.OptionalElement(UnionAura.is_active, FinishBlow_U, FinishBlow_, name = "유니온오라 여부(데스 off)")
        IsUnion_M = core.OptionalElement(UnionAura.is_active, FinishBlow_M_U, FinishBlow_M, name = "유니온오라 여부(데스 on)")
        
        FinishBlow_U.onAfter(MasterOfDeath.controller(500, 'reduce_cooltime'))
        FinishBlow_M_U.onAfter(MasterOfDeath.controller(500, 'reduce_cooltime'))
        FinishBlow = core.OptionalElement(MasterOfDeath.is_active, IsUnion_M, IsUnion_, name = "마스터 오브 데스 여부")
        FinishBlow.onAfter(UseMark)
        FinishBlow.onAfter(DarkLightening)
        FinishBlow.onAfter(FinalAttack)
        FinishBlowEndpoint = core.DamageSkill('기본공격', 0, 0, 0).wrap(core.DamageSkillWrapper)
        FinishBlowEndpoint.onAfter(FinishBlow)
        
        # 확인 필요

        MasterOfDeath.onAfter(DeathAfterMOD)

        #DarkLightening.onAfters([MarkStack.stackController(1), UseMark])
        DarkLightening.onAfters([MarkStack.stackController(1), FinalAttack])
        
        BattlekingBar.onAfters([BattlekingBar2, UseMark, FinalAttack])
        BattlekingBar2.onAfter(UseMark)
        
        BlackMagicAlter.onTick(MarkStack.stackController(1))

        # DeathAfterMOD는 처음에 비활성화됨
        DeathAfterMOD.set_disabled_and_time_left(-1)

        # 쓸윈 제거 ([너브 스티뮬레이션] : 공격 속도가 1단계 증가하는 기능이 추가됩니다.)
        return(FinishBlowEndpoint,
                [Booster, WillOfLiberty, MasterOfDeath, UnionAura,
                globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), #globalSkill.useful_wind_booster(),
                globalSkill.soul_contract()] +\
                [DarkGenesis, BattlekingBar] +\
                [RegistanceLineInfantry, Death, DeathAfterMOD, BlackMagicAlter, GrimReaper] +\
                [] +\
                [FinishBlowEndpoint])