from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule
from . import globalSkill
from .jobbranch import bowmen

#TODO : 5차 신스킬 적용
class ArrowOfStormWrapper(core.DamageSkillWrapper):
    '''
    모탈 블로우 - 9회 공격 후 다음 공격은 데미지+80%
    아머 피어싱 - 적 방어율만큼 최종뎀 추가, 방무+50%. 쿨타임 9초, 공격마다 1초씩 감소, 최소 재발동 대기시간 1초
    '''
    def __init__(self, skill):
        super(ArrowOfStormWrapper, self).__init__(skill)
        self.mortalBlowCount = 0
        self.armorPiercingCooltime = 0

    def spend_time(self, time):
        self.armorPiercingCooltime -= time
        super(ArrowOfStormWrapper, self).spend_time(time)
        
    def _use(self, rem = 0, red = 0):
        modifier = self.get_modifier()
        if self.mortalBlowCount >= 9:
            modifier += core.CharacterModifier(pdamage = 80)
            self.mortalBlowCount = 0
        else:
            self.mortalBlowCount += 1

        if self.armorPiercingCooltime <= 0:
            modifier += core.CharacterModifier(pdamage_indep = 300, armor_ignore = 50) # 적 방어율 300 가정
            self.armorPiercingCooltime = 9000 * (1 - 0.01 * red)
        elif self.armorPiercingCooltime > 1000:
            self.armorPiercingCooltime = max(self.armorPiercingCooltime - 1000, 1000)
        
        return core.ResultObject(self.skill.delay, modifier, self.skill.damage, self.skill.hit, sname = self.skill.name, spec = self.skill.spec)

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.jobtype = "dex"
        self.vEnhanceNum = 11
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage = 18)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule("프리퍼레이션", "퀴버 풀버스트"), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule("소울 컨트랙트", "퀴버 풀버스트"), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self):
        CriticalShot = core.InformedCharacterModifier("크리티컬 샷",crit = 40)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        
        MarkmanShip = core.InformedCharacterModifier("마크맨쉽",armor_ignore = 25, patt = 25)

        CrossBowExpert = core.InformedCharacterModifier("보우 엑스퍼트",att=60+self.combat*1, crit_damage =8)
        AdvancedFinalAttackPassive = core.InformedCharacterModifier("어드밴스드 파이널 어택(패시브)",att = 20) #오더스 적용필요
        
        return [CriticalShot, PhisicalTraining,MarkmanShip, 
                            CrossBowExpert, AdvancedFinalAttackPassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5)

        ExtremeArchery = core.InformedCharacterModifier("익스트림 아처리",att = 40, pdamage_indep = 30)
        
        return [WeaponConstant, Mastery, ExtremeArchery]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        잔영의시 : 500ms마다 타격(초당 2회)
        애로우 레인 : 떨어질 때마다 6번씩( = 2500/6 ~ 420ms)
                
        코강 순서:
        폭시-파택-언카블-퀴버-플래터-피닉스

        하이퍼: 폭풍의 시 3종 / 샤프 아이즈-이그노어 가드, 크리티컬 레이트
        
        프리퍼레이션, 엔버링크를 120초 주기에 맞춰 사용
        '''
        ######   Skill   ######
        #Buff skills
        SoulArrow = core.BuffSkill("소울 애로우", 0, 300 * 1000, att = 30).wrap(core.BuffSkillWrapper) # 펫버프
        AdvancedQuibber = core.BuffSkill("어드밴스드 퀴버", 0, 30 * 1000, crit_damage = 8).wrap(core.BuffSkillWrapper)   #쿨타임 무시 가능, 딜레이 없앰
        SharpEyes = core.BuffSkill("샤프 아이즈", 690, 300 * 1000, crit = 20 + 5 + combat*1, crit_damage = 15 + combat*1, armor_ignore = 5).wrap(core.BuffSkillWrapper)
        ElusionStep = core.BuffSkill("일루젼 스탭", 0, 300 * 1000, rem = True, stat_main = 80).wrap(core.BuffSkillWrapper) # 펫버프
        Preparation = core.BuffSkill("프리퍼레이션", 900, 30 * 1000, cooltime = 90 * 1000, att = 50, boss_pdamage = 20).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        #Damage Skills
        AdvancedQuibberAttack = core.DamageSkill("어드밴스드 퀴버", 0, 260, 0.6).setV(vEhc, 3, 2, True).wrap(core.DamageSkillWrapper)
        AdvancedQuibberAttack_ArrowRain = core.DamageSkill("어드밴스드 퀴버(애로우 레인)", 0, 260, 1).setV(vEhc, 3, 2, True).wrap(core.DamageSkillWrapper)
        AdvancedFinalAttack = core.DamageSkill("어드밴스드 파이널 어택", 0, 210, 0.7).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        
        ArrowOfStorm = ArrowOfStormWrapper(core.DamageSkill("폭풍의 시", 120, (350+combat*3)*0.75, 1+1, modifier = core.CharacterModifier(pdamage = 30, boss_pdamage = 10)).setV(vEhc, 0, 2, True))
        ArrowFlatter = core.SummonSkill("애로우 플래터", 600, 210, 85+90+combat*3, 1, 30 * 1000, modifier = core.CharacterModifier(pdamage = 30)).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper) # 딜레이 모름
        
        GrittyGust = core.DamageSkill("윈드 오브 프레이", 720, 500, 8, cooltime = 15 * 1000).setV(vEhc, 6, 2, True).wrap(core.DamageSkillWrapper)
        GrittyGustDOT = core.DotSkill("윈드 오브 프레이(도트)", 200, 10*1000).wrap(core.SummonSkillWrapper)
        
        ArrowRainBuff = core.BuffSkill("애로우 레인(버프)", 810, (40+vEhc.getV(0,0))*1000, cooltime = 120 * 1000, red = True, pdamage = 15+(vEhc.getV(0,0)//2)).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        ArrowRain = core.SummonSkill("애로우 레인", 0, 1440, 600+vEhc.getV(0,0)*24, 8, (40+vEhc.getV(0,0))*1000, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper) # 5초마다 3.5회 공격, 대략 1440ms당 1회
        
        #Summon Skills
        Pheonix = core.SummonSkill("피닉스", 0, 2670, 390, 1, 220 * 1000).setV(vEhc, 5, 3, True).wrap(core.SummonSkillWrapper) # 이볼브가 끝나면 자동으로 소환되므로 딜레이 0
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 4, 4)
        Evolve = core.SummonSkill("이볼브", 600, 3330, 450+vEhc.getV(5,5)*15, 7, 40*1000, cooltime = (121-int(0.5*vEhc.getV(5,5)))*1000).isV(vEhc,5,5).wrap(core.SummonSkillWrapper)
        
        #잔영의시 미적용
        QuibberFullBurstBuff = core.BuffSkill("퀴버 풀버스트(버프)", 0, 30 * 1000, cooltime = 120 * 1000, red = True, patt=(5+int(vEhc.getV(2,2)*0.5)), crit_damage=8).wrap(core.BuffSkillWrapper) # 독화살 크뎀을 이쪽에 합침
        QuibberFullBurst = core.SummonSkill("퀴버 풀버스트", 780, 2 * 1000 / 6, 750 + 30 * vEhc.getV(2,2), 3, 30 * 1000, cooltime = -1).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
        QuibberFullBurstDOT = core.DotSkill("독화살", 220, 30*1000).wrap(core.SummonSkillWrapper)
    
        ImageArrow = core.SummonSkill("잔영의 시", 720, 240, 400+16*vEhc.getV(1,1), 3, 3000-360, cooltime=30000, red = True).isV(vEhc,1,1).wrap(core.SummonSkillWrapper) # 11 * 3타, 준비 360ms
        ImageArrowPassive = core.DamageSkill("잔영의 시(패시브)", 0, 400+16*vEhc.getV(1,1), 3 * 2 * 0.1).isV(vEhc,1,1).wrap(core.DamageSkillWrapper) # 10회당 1번 생성, 생성당 3타씩 2회 공격
    
        ######   Skill Wrapper   ######
        GrittyGust.onAfter(GrittyGustDOT)

        #이볼브 연계 설정
        Evolve.onAfter(Pheonix.controller(1))
        Pheonix.onConstraint(core.ConstraintElement("이볼브 사용시 사용 금지", Evolve, Evolve.is_not_active))
            
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 3, 3, 22.5) #Maybe need to sync

        ArrowOfStorm.onAfter(AdvancedQuibberAttack)
        ArrowOfStorm.onAfter(AdvancedFinalAttack)
        ArrowOfStorm.onAfter(core.OptionalElement(ImageArrow.is_not_active, ImageArrowPassive, name="잔영의 시 액티브 OFF"))
        
        ArrowRain.onTick(AdvancedQuibberAttack_ArrowRain)
        ImageArrow.onTicks([AdvancedFinalAttack, AdvancedQuibberAttack])
        GuidedArrow.onTick(AdvancedQuibberAttack)
        
        ArrowRainBuff.onAfter(ArrowRain)
        QuibberFullBurstBuff.onAfter(QuibberFullBurstDOT)
        QuibberFullBurstBuff.onAfter(QuibberFullBurst)

        ### Exports ###
        return(ArrowOfStorm,
                [globalSkill.maple_heros(chtr.level),
                    SoulArrow, AdvancedQuibber, SharpEyes, ElusionStep, Preparation, EpicAdventure,
                    ArrowRainBuff, CriticalReinforce, QuibberFullBurstBuff, QuibberFullBurstDOT,
                    globalSkill.soul_contract()] +\
                [] +\
                [Evolve, ArrowFlatter, ArrowRain, Pheonix, GuidedArrow, QuibberFullBurst, ImageArrow] +\
                [] +\
                [ArrowOfStorm])