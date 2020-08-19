"""
Advisor : 저격장(레드)
https://github.com/oleneyl/maplestory_dpm_calc/issues/247
"""

from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule
from . import globalSkill
from .jobbranch import bowmen

class ArmorPiercingWrapper(core.BuffSkillWrapper):
    '''
    아머 피어싱 - 적 방어율만큼 최종뎀 추가, 방무+50%. 쿨타임 9초, 공격마다 1초씩 감소, 최소 재발동 대기시간 1초
    '''
    def __init__(self, combat):
        self.piercingModifier = core.CharacterModifier(pdamage_indep = 300 * (1 + combat * 0.05), armor_ignore = 50 * (1 + combat * 0.02))
        self.emptyModifier = core.CharacterModifier()
        skill = core.BuffSkill("아머 피어싱", 0, 0, 9000)
        super(ArmorPiercingWrapper, self).__init__(skill)

    def check(self):
        if self.available:
            self.cooltimeLeft = self.skill.cooltime # TODO: 쿨감 적용 어떻게???
            self.available = False
            return self.piercingModifier

        if self.cooltimeLeft > 1000:
            self.cooltimeLeft = max(self.cooltimeLeft - 1000, 1000)
        
        return self.emptyModifier

class ArrowOfStormWrapper(core.DamageSkillWrapper):
    def __init__(self, skill, armorPiercing, combat):
        super(ArrowOfStormWrapper, self).__init__(skill)
        self.armorPiercing = armorPiercing
        self.combat = combat
        self.lastUsed = -9999
        self.currentTime = 0

    def spend_time(self, time):
        self.currentTime += time
        super(ArrowOfStormWrapper, self).spend_time(time)
        
    def _use(self, rem = 0, red = 0):
        '''
        아머 피어싱 적용.
        현재 시간 > 마지막 시전 시간 + 딜레이 인 경우에 선딜을 추가함.
        딜레이가 0인 버프가 끼어들 수 있기에 정확한 구현은 아님.
        '''
        modifier = self.get_modifier()
        modifier += self.armorPiercing.check()
        
        delay = self.skill.delay
        if self.currentTime > self.lastUsed:
            delay += 540
        self.lastUsed = self.currentTime + delay

        return core.ResultObject(delay, modifier, self.skill.damage, self.skill.hit, sname = self.skill.name, spec = self.skill.spec)

class GuidedArrowWrapper(bowmen.GuidedArrowWrapper):
    def __init__(self, vEhc, num1, num2, armorPiercing, combat):
        super(GuidedArrowWrapper, self).__init__(vEhc, num1, num2)
        self.armorPiercing = armorPiercing
        self.combat = combat
            
    def _useTick(self):
        if self.onoff and self.tick <= 0:
            self.tick += self.skill.delay

            modifier = self.get_modifier()
            modifier += self.armorPiercing.check()
            
            return core.ResultObject(0, modifier, self.skill.damage, self.skill.hit, sname = self.skill.name, spec = self.skill.spec)
        else:
            return core.ResultObject(0, self.disabledModifier, 0, 0, sname = self.skill.name, spec = self.skill.spec)

#TODO : 5차 신스킬 적용
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
        잔영의 시 : 액티브 13*3타, 패시브 3.5*3타. 패시브는 쿨타임동안 10~11회 사용
        애로우 레인 : 1줄기, 떨어질 때 마다 3.5회 타격
                
        코강 순서:
        폭시-파택-언카블-퀴버-플래터-피닉스

        하이퍼: 폭풍의 시 3종 / 샤프 아이즈-이그노어 가드, 크리티컬 레이트
        
        프리퍼레이션, 엔버링크를 120초 주기에 맞춰 사용
        '''
        MortalBlow = core.CharacterModifier(pdamage = 80/10) # 반응하는 스킬이 정해져있음. Issue # 247 참고.

        ######   Skill   ######
        #Buff skills
        SoulArrow = core.BuffSkill("소울 애로우", 0, 300 * 1000, att = 30).wrap(core.BuffSkillWrapper) # 펫버프
        AdvancedQuibber = core.BuffSkill("어드밴스드 퀴버", 0, 30 * 1000, crit_damage = 8).wrap(core.BuffSkillWrapper)   #쿨타임 무시 가능, 딜레이 없앰
        SharpEyes = core.BuffSkill("샤프 아이즈", 690, 300 * 1000, crit = 20 + 5 + combat*1, crit_damage = 15 + combat*1, armor_ignore = 5).wrap(core.BuffSkillWrapper)
        ElusionStep = core.BuffSkill("일루젼 스탭", 0, 300 * 1000, rem = True, stat_main = 80).wrap(core.BuffSkillWrapper) # 펫버프
        Preparation = core.BuffSkill("프리퍼레이션", 900, 30 * 1000, cooltime = 90 * 1000, att = 50, boss_pdamage = 20).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)

        ArmorPiercing = ArmorPiercingWrapper(combat)
    
        #Damage Skills
        AdvancedQuibberAttack = core.DamageSkill("어드밴스드 퀴버", 0, 260, 0.6, modifier=MortalBlow).setV(vEhc, 3, 2, True).wrap(core.DamageSkillWrapper)
        AdvancedQuibberAttack_ArrowRain = core.DamageSkill("어드밴스드 퀴버(애로우 레인)", 0, 260, 1, modifier=MortalBlow).setV(vEhc, 3, 2, True).wrap(core.DamageSkillWrapper)
        AdvancedFinalAttack = core.DamageSkill("어드밴스드 파이널 어택", 0, 210, 0.7).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        
        ArrowOfStorm = ArrowOfStormWrapper(core.DamageSkill("폭풍의 시", 120, (350+combat*3)*0.75, 1+1, modifier = core.CharacterModifier(pdamage = 30, boss_pdamage = 10) + MortalBlow).setV(vEhc, 0, 2, True), ArmorPiercing, combat)
        ArrowFlatter = core.SummonSkill("애로우 플래터", 600, 210, 85+90+combat*3, 1, 30 * 1000, modifier = core.CharacterModifier(pdamage = 30)).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper) # 딜레이 모름
        
        GrittyGust = core.DamageSkill("윈드 오브 프레이", 720, 500, 8, cooltime = 15 * 1000, modifier=MortalBlow).setV(vEhc, 6, 2, True).wrap(core.DamageSkillWrapper)
        GrittyGustDOT = core.DotSkill("윈드 오브 프레이(도트)", 200, 10*1000).wrap(core.SummonSkillWrapper)
        
        ArrowRainBuff = core.BuffSkill("애로우 레인(버프)", 810, (40+vEhc.getV(0,0))*1000, cooltime = 120 * 1000, red = True, pdamage = 15+(vEhc.getV(0,0)//2)).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        ArrowRain = core.SummonSkill("애로우 레인", 0, 1440, 600+vEhc.getV(0,0)*24, 8, (40+vEhc.getV(0,0))*1000, cooltime = -1, modifier=MortalBlow).isV(vEhc,0,0).wrap(core.SummonSkillWrapper) # 5초마다 3.5회 공격, 대략 1440ms당 1회
        
        #Summon Skills
        Pheonix = core.SummonSkill("피닉스", 0, 2670, 390, 1, 220 * 1000).setV(vEhc, 5, 3, True).wrap(core.SummonSkillWrapper) # 이볼브가 끝나면 자동으로 소환되므로 딜레이 0
        GuidedArrow = GuidedArrowWrapper(vEhc, 4, 4, ArmorPiercing, combat)
        Evolve = core.SummonSkill("이볼브", 600, 3330, 450+vEhc.getV(5,5)*15, 7, 40*1000, cooltime = (121-int(0.5*vEhc.getV(5,5)))*1000).isV(vEhc,5,5).wrap(core.SummonSkillWrapper)
        
        #잔영의시 미적용
        QuibberFullBurstBuff = core.BuffSkill("퀴버 풀버스트(버프)", 0, 30 * 1000, cooltime = 120 * 1000, red = True, patt=(5+int(vEhc.getV(2,2)*0.5)), crit_damage=8).wrap(core.BuffSkillWrapper) # 독화살 크뎀을 이쪽에 합침
        QuibberFullBurst = core.SummonSkill("퀴버 풀버스트", 780, 2 * 1000 / 6, 750 + 30 * vEhc.getV(2,2), 3, 30 * 1000, cooltime = -1, modifier=MortalBlow).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
        QuibberFullBurstDOT = core.DotSkill("독화살", 220, 30*1000).wrap(core.SummonSkillWrapper)
    
        ImageArrow = core.SummonSkill("잔영의 시", 720, 240, 400+16*vEhc.getV(1,1), 3, 3000, cooltime=30000, red = True).isV(vEhc,1,1).wrap(core.SummonSkillWrapper) # 13 * 3타
        ImageArrowPassive = core.SummonSkill("잔영의 시(패시브)", 0, 2580, 400+16*vEhc.getV(1,1), 3.5*3, 9999999).isV(vEhc,1,1).wrap(core.SummonSkillWrapper) # 3~4 * 3타, 잔시 쿨동안 11회 사용
    
        ######   Skill Wrapper   ######
        GrittyGust.onAfter(GrittyGustDOT)

        #이볼브 연계 설정
        Evolve.onAfter(Pheonix.controller(1))
        Pheonix.onConstraint(core.ConstraintElement("이볼브 사용시 사용 금지", Evolve, Evolve.is_not_active))
            
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 3, 3, 22.5) #Maybe need to sync

        ArrowOfStorm.onAfter(AdvancedQuibberAttack)
        ArrowOfStorm.onAfter(AdvancedFinalAttack)
        
        ArrowRainBuff.onAfter(ArrowRain)
        ArrowRain.onTick(AdvancedQuibberAttack_ArrowRain)

        ImageArrow.onAfter(ImageArrowPassive.controller(3000))
        ImageArrow.onTick(AdvancedFinalAttack)

        GuidedArrow.onTick(AdvancedQuibberAttack)
        
        QuibberFullBurstBuff.onAfter(QuibberFullBurstDOT)
        QuibberFullBurstBuff.onAfter(QuibberFullBurst)

        ArmorPiercing.protect_from_running()

        ### Exports ###
        return(ArrowOfStorm,
                [globalSkill.maple_heros(chtr.level),
                    SoulArrow, AdvancedQuibber, SharpEyes, ElusionStep, Preparation, EpicAdventure, ArmorPiercing,
                    ArrowRainBuff, CriticalReinforce, QuibberFullBurstBuff, QuibberFullBurstDOT, ImageArrowPassive,
                    globalSkill.soul_contract()] +\
                [] +\
                [Evolve, ArrowFlatter, ArrowRain, Pheonix, GuidedArrow, QuibberFullBurst, ImageArrow] +\
                [] +\
                [ArrowOfStorm])