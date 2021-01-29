from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule
from . import globalSkill
from .jobclass import resistance
from .jobbranch import magicians
from math import ceil
from typing import Any, Dict

class GrimReaperWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2, masterOfDeath):
        skill = core.SummonSkill("그림 리퍼", 540, 4000, 800+32*vEhc.getV(num1,num2), 12, 30*1000, cooltime=100*1000).isV(vEhc,num1,num2)
        super(GrimReaperWrapper, self).__init__(skill)
        self.masterOfDeath = masterOfDeath

    def _useTick(self):
        if self.is_active() and self.tick <= 0 and self.masterOfDeath.is_not_active():
            self.timeLeft += 2000
        return super(GrimReaperWrapper, self)._useTick()

    def get_delay(self):
        if self.masterOfDeath.is_active():
            return self.skill.delay / 2
        else:
            return self.skill.delay

class BlowSkillWrapper(core.DamageSkillWrapper):
    def __init__(self, skill):
        super(BlowSkillWrapper, self).__init__(skill)
        self.masterOfDeath = None

    def get_hit(self):
        if self.masterOfDeath.is_active():
            return self.skill.hit + 1
        else:
            return self.skill.hit

    def registerMOD(self, skill):
        self.masterOfDeath = skill

class Roulette():
    def __init__(self, prob):
        self.stack = 0
        self.prob = prob

    def draw(self):
        self.stack += self.prob
        if self.stack >= 1:
            self.stack -= 1
            return True
        return False

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "INT"
        self.jobname = "배틀메이지"
        self.vEnhanceNum = 10
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'reuse')
        self.preEmptiveSkills = 2

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=52)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('마스터 오브 데스', '그림 리퍼'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('소울 컨트랙트', '유니온 오라'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('메이플월드 여신의 축복', '유니온 오라'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('어비셜 라이트닝', '유니온 오라'), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        ArtOfStaff = core.InformedCharacterModifier("아트 오브 스태프",att = 20, crit = 15)
        StaffMastery = core.InformedCharacterModifier("스태프 마스터리",att = 30, crit = 20)
        HighWisdom =  core.InformedCharacterModifier("하이 위즈덤",stat_main = 40)
        BattleMastery = core.InformedCharacterModifier("배틀 마스터리",pdamage_indep = 15, crit_damage = 20)
        DarkAuraPassive = core.InformedCharacterModifier("다크 오라(패시브)", patt=15)
        
        StaffExpert = core.InformedCharacterModifier("스태프 엑스퍼트",att = 30 + passive_level, crit_damage = 20 + ceil(passive_level / 2))
        SpellBoost = core.InformedCharacterModifier("스펠 부스트", patt = 25 + passive_level // 2, pdamage = 10 + ceil(passive_level / 3), armor_ignore = 30 + passive_level)
        
        return [ArtOfStaff, StaffMastery, HighWisdom, BattleMastery, DarkAuraPassive, StaffExpert, SpellBoost]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수")
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -2.5 + 0.5 * ceil(passive_level / 2))
        
        DebuffAura = core.InformedCharacterModifier("디버프 오라", armor_ignore = 20, pdamage_indep = 10, prop_ignore = 10)
        BattleRage = core.InformedCharacterModifier("배틀 레이지",pdamage = 40 + self.combat, crit_damage = 8 + self.combat // 6, crit=20 + ceil(self.combat / 3))
        return [WeaponConstant, Mastery, DebuffAura, BattleRage]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        오라스위칭 미사용
        디버프 오라 사용
        알터 히트율 100%, 50초마다 40초간 유지되는 2개 알터 사용
        어비셜 라이트닝 명계의 통로 미사용

        하이퍼 :
        다크 제네시스-쿨타임 리듀스
        다크 오라-보스 킬러
        디버프 오라-엘리멘탈 리셋
        쉘터-쿨타임 리듀스, 퍼시스트
        
        코강 순서 : 
        닼라-피블-데스-킹바-닼제네-배틀스퍼트
        
        좌우텔 분당 83회
        
        마스터 오브 데스는 리퍼와 같이 사용함
        알터는 쿨마다 사용함
        메여축, 어비셜 라이트닝은 유니온 오라와 같이 사용함
        '''

        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper)
        MarkStack = core.StackSkillWrapper(core.BuffSkill("징표 스택", 0, 99999*10000), 1)

        #Damage Skills
        DarkLightning = core.DamageSkill("다크 라이트닝", 0, 225, 4, modifier = core.CharacterModifier(pdamage = 60 + self.combat)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper) #캔슬
        DarkLightningMark = core.DamageSkill("다크 라이트닝(징표)", 0, 350, 4, modifier = core.CharacterModifier(boss_pdamage=20, pdamage = 60 + self.combat)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        #좌우텔 분당 83회 기준.
        FinishBlow = core.DamageSkill("피니쉬 블로우", 720, 330 + 3 * self.combat, 6, modifier = core.CharacterModifier(crit=25 + ceil(self.combat / 2), armor_ignore=2 * ceil((30 + self.combat)/3))).setV(vEhc, 1, 2, False).wrap(BlowSkillWrapper)
        ReaperScythe = core.DamageSkill("사신의 낫", 720, 300, 12, modifier = core.CharacterModifier(crit=50, armor_ignore=50)).setV(vEhc, 1, 2, False).wrap(BlowSkillWrapper)
        
        DarkGenesis = core.DamageSkill("다크 제네시스", 690, 520 + 10 * self.combat, 8, cooltime = 14*1000, red=True).setV(vEhc, 4, 2, True).wrap(core.DamageSkillWrapper)
        DarkGenesisFinalAttack = core.DamageSkill("다크 제네시스(추가타)", 0, 220 + 4 * self.combat, 1).setV(vEhc, 4, 2, True).wrap(core.DamageSkillWrapper)

        Death = core.DamageSkill("데스", 0, 200+chtr.level, 12, cooltime = 5000).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        #Hyper
        MasterOfDeath = core.BuffSkill("마스터 오브 데스", 1020, 30*1000, cooltime = 200*1000, red=False).wrap(core.BuffSkillWrapper)
        BattlekingBar = core.DamageSkill("배틀킹 바", 180, 650, 2, cooltime = 13*1000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        BattlekingBar2 = core.DamageSkill("배틀킹 바(2타)", 240, 650, 5).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        WillOfLiberty = core.BuffSkill("윌 오브 리버티", 0, 60*1000, cooltime = 120*1000, pdamage = 10).wrap(core.BuffSkillWrapper)

        #5th
        RegistanceLineInfantry = resistance.ResistanceLineInfantryWrapper(vEhc, 4, 4)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        UnionAura = core.BuffSkill("유니온 오라", 810, (vEhc.getV(1,1)//3+30)*1000, cooltime = 100*1000, pdamage=20, boss_pdamage=10, att=vEhc.getV(1,1)*2).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)
        BlackMagicAlter = core.SummonSkill("블랙 매직 알터", 690, 1220, 800+32*vEhc.getV(0,0), 4, 40*1000, cooltime = 50*1000).isV(vEhc,0,0).wrap(core.SummonSkillWrapper) # 2개 충전할때 마다 사용
        GrimReaper = GrimReaperWrapper(vEhc, 2, 2, MasterOfDeath)
        AbyssyalLightning = core.BuffSkill("어비셜 라이트닝", 540, 35000, cooltime=200*1000, red=True).wrap(core.BuffSkillWrapper)
        AbyssyalDarkLightning = core.DamageSkill("어비셜 라이트닝(칠흑의 번개)", 0, 1100, 5*3, modifier=core.CharacterModifier(crit=100, armor_ignore=20, pdamage_indep=-20)).wrap(core.DamageSkillWrapper)
        
        #Build Graph
        """
        스킬간 발동관계 참고 링크
        http://www.inven.co.kr/board/maple/2295/19973
        http://www.inven.co.kr/board/maple/2295/4339
        """
        # 데스
        UseDeath = core.OptionalElement(Death.is_available, Death, name = "데스 쿨타임 확인")
        for sk in [FinishBlow, ReaperScythe, BattlekingBar, BattlekingBar2, DarkGenesis, DarkGenesisFinalAttack]:
            sk.onAfter(UseDeath)

        Death.protect_from_running()

        # 다크 라이트닝
        AddMark = MarkStack.stackController(1, "징표 생성")
        UseMark = core.OptionalElement(partial(MarkStack.judge, 1, 1), DarkLightningMark, name = '징표 사용여부 결정')
        DarkLightningMark.onAfter(MarkStack.stackController(-1, "징표 사용"))
        DarkLightning.onAfter(AddMark)
        AbyssyalDarkLightning.onAfter(AddMark)

        UseDarkLightning = core.OptionalElement(AbyssyalLightning.is_active, AbyssyalDarkLightning, DarkLightning)

        # 다크 제네시스
        FinalAttackRoulette = Roulette((60 + 2 * self.combat) * 0.01)
        FinalAttack = core.OptionalElement(lambda: DarkGenesis.is_not_usable() and FinalAttackRoulette.draw(), DarkGenesisFinalAttack, name = "다크 제네시스 추가타 검증")
        DarkGenesis.onJustAfter(UseMark)
        DarkGenesis.onAfter(UseDarkLightning)
        DarkGenesisFinalAttack.onJustAfter(UseMark)
        
        # 피니시 블로우
        FinishBlow.registerMOD(MasterOfDeath) # 마스터 오브 데스 스킬 등록
        FinishBlow.onJustAfter(UseMark)
        FinishBlow.onAfter(UseDarkLightning)
        FinishBlow.onAfter(FinalAttack)
        ReaperScythe.registerMOD(MasterOfDeath)
        ReaperScythe.onJustAfter(UseMark)
        ReaperScythe.onAfter(UseDarkLightning)
        ReaperScythe.onAfter(FinalAttack)
        BasicAttack = core.DamageSkill('기본공격', 0, 0, 0).wrap(core.DamageSkillWrapper)
        BasicAttack.onAfter(core.OptionalElement(UnionAura.is_active, ReaperScythe, FinishBlow, name = "유니온오라 여부"))
        
        # 마스터 오브 데스
        ReduceDeath = core.OptionalElement(MasterOfDeath.is_active, Death.controller(500, 'reduce_cooltime'), name="마스터 오브 데스 ON")
        DarkGenesisFinalAttack.onAfter(ReduceDeath)
        DarkGenesis.onAfter(ReduceDeath)
        ReaperScythe.onAfter(ReduceDeath)
        DarkLightning.onAfter(ReduceDeath)
        BlackMagicAlter.onTick(ReduceDeath)
        GrimReaper.onTick(ReduceDeath)
        AbyssyalDarkLightning.onAfter(ReduceDeath)
        Death.add_runtime_modifier(MasterOfDeath, lambda sk: core.CharacterModifier(pdamage_indep = 50 * sk.is_active()))
        
        # 배틀킹 바
        BattlekingBar.onJustAfter(UseMark)
        BattlekingBar.onAfter(FinalAttack)
        BattlekingBar.onAfter(BattlekingBar2)
        BattlekingBar2.onJustAfter(UseMark)
        BattlekingBar2.onAfter(UseDarkLightning)
        BattlekingBar2.onAfter(FinalAttack)
        
        # 블랙 매직 알터
        BlackMagicAlter.onTick(FinalAttack) # TODO: onTick 실행순서 바꿀 시 AddMark -> FinalAttack 순으로 터지는 것을 유지해야 함
        BlackMagicAlter.onTick(AddMark)

        # 오버로드 마나
        overload_mana_builder = magicians.OverloadManaBuilder(vEhc, 0, 0)
        for sk in [FinishBlow, Death, DarkLightning, DarkGenesis, BattlekingBar, BattlekingBar2, BlackMagicAlter, ReaperScythe,
                    AbyssyalDarkLightning, RegistanceLineInfantry]:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()

        TandadianRuin, AeonianRise = globalSkill.GenesisSkillBuilder()

        return(BasicAttack,
                [Booster, globalSkill.maple_heros(chtr.level, combat_level=self.combat), OverloadMana,
                globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), WillOfLiberty, MasterOfDeath, UnionAura, AbyssyalLightning,
                globalSkill.soul_contract(), TandadianRuin] +\
                [DarkGenesis, BattlekingBar] +\
                [RegistanceLineInfantry, Death, BlackMagicAlter, GrimReaper, MirrorBreak, MirrorSpider, AeonianRise] +\
                [] +\
                [BasicAttack])
