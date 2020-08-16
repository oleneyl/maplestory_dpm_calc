from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import bowmen

#TODO : 5차 신스킬 적용
#TODO : 윈드 오브 프레이 추가

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.jobtype = "dex"
        self.vEnhanceNum = 11
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

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
        MortalBlow = core.InformedCharacterModifier("모탈 블로우",pdamage = 80/10)   #확률성을 변형적용... 패치 필요할듯

        ArmorPiercing = core.InformedCharacterModifier("아머 피어싱",pdamage_indep = 100/8, armor_ignore = 50/8) # 가동률 약 1/8, 잠재 쿨감 1초당 분모 0.5씩 빼야함
        
        return [WeaponConstant, Mastery,  MortalBlow, ExtremeArchery, ArmorPiercing]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        잔영의시 : 500ms마다 타격(초당 2회)
        애로우 레인 : 떨어질 때마다 6번씩( = 2500/6 ~ 420ms)
                
        코강 순서:
        폭시-파택-언카블-퀴버-플래터-피닉스

        하이퍼: 폭풍의 시 3종 / 샤프 아이즈-이그노어 가드, 크리티컬 레이트
                
        '''
        ######   Skill   ######
        #Buff skills
        SoulArrow = core.BuffSkill("소울 애로우", 0, 300 * 1000, att = 30).wrap(core.BuffSkillWrapper) # 펫버프
        AdvancedQuibber = core.BuffSkill("어드밴스드 퀴버", 0, 30 * 1000, crit_damage = 8).wrap(core.BuffSkillWrapper)   #쿨타임 무시 가능, 딜레이 없앰
        SharpEyes = core.BuffSkill("샤프 아이즈", 690, 300 * 1000, crit = 20 + 5 + combat*1, crit_damage = 15 + combat*1, armor_ignore = 5).wrap(core.BuffSkillWrapper)
        ElusionStep = core.BuffSkill("일루젼 스탭", 0, 300 * 1000, rem = True, stat_main = 80).wrap(core.BuffSkillWrapper) # 펫버프
        Preparation = core.BuffSkill("프리퍼레이션", 900, 30 * 1000, cooltime = 90 * 1000, att = 50, boss_pdamage = 20).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        #ArmorPiercing = core.BuffSkill("아머 피어싱", ?, ?) #쿨 9초, 적 방어율만큼 최종뎀 1회 한정 증가, 방무 50%, 타격마다 1초 감소, 쿨타임 최대 감소량 1초
        
        #Damage Skills
        AdvancedQuibberAttack = core.DamageSkill("마법 화살", 0, 260, 0.6).setV(vEhc, 3, 2, True).wrap(core.DamageSkillWrapper)
        AdvancedQuibberAttack_ArrowRain = core.DamageSkill("마법 화살(애로우 레인)", 0, 260, 1).setV(vEhc, 3, 2, True).wrap(core.DamageSkillWrapper)
        AdvancedFinalAttack = core.DamageSkill("어드밴스드 파이널 어택", 0, 210, 0.7).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        
        ArrowOfStorm = core.DamageSkill("폭풍의 시", 120, 350*0.75, 1+1, modifier = core.CharacterModifier(pdamage = 30, boss_pdamage = 10)).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)  #오더스 적용 필요, 아머 피어싱, 
        ArrowFlatter = core.SummonSkill("애로우 플래터", 600, 210, 85+90+combat*3, 1, 30 * 1000, modifier = core.CharacterModifier(pdamage = 30)).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper) # 딜레이 모름
        # 작성중
        #GrittyGust = core.DamageSkill("윈드 오브 프레이", ?, 500, 81, cooltime = 15 * 1000, red = true).setV(vEhc, 0, 2, True).wrap(core.DamageSkillWrapper)
        #GrittyGustDOT = core.SummonSkill("윈드 오브 프레이(도트)", 0, 1000, 200, 1, 10*1000, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        
        ArrowRainBuff = core.BuffSkill("애로우 레인(버프)", 810, (40+vEhc.getV(0,0))*1000, cooltime = 120 * 1000, red = True, pdamage = 15+(vEhc.getV(0,0)//2)).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        ArrowRain = core.SummonSkill("애로우 레인", 0, 1440, 600+vEhc.getV(0,0)*24, 8, (40+vEhc.getV(0,0))*1000, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper) # 5초마다 3.5회 공격, 대략 1440ms당 1회
        
        #Summon Skills
        Pheonix = core.SummonSkill("피닉스", 0, 2670, 390, 1, 220 * 1000).setV(vEhc, 5, 3, True).wrap(core.SummonSkillWrapper) # 이볼브가 끝나면 자동으로 소환되므로 딜레이 0
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 4, 4)
        Evolve = core.SummonSkill("이볼브", 600, 3330, 450+vEhc.getV(5,5)*15, 7, 40*1000, cooltime = (121-int(0.5*vEhc.getV(5,5)))*1000).isV(vEhc,5,5).wrap(core.SummonSkillWrapper)
        
        #잔영의시 미적용
        QuibberFullBurstBuff = core.BuffSkill("퀴버 풀버스트(버프)", 0, 30 * 1000, cooltime = 120 * 1000, red = True, patt=(5+int(vEhc.getV(2,2)*0.5))).wrap(core.BuffSkillWrapper)
        QuibberFullBurst = core.SummonSkill("퀴버 풀버스트", 780, 2 * 1000 / 6, 750 + 30 * vEhc.getV(2,2), 3, 30 * 1000, cooltime = -1).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
        QuibberFullBurstDOT = core.DotSkill("독화살", 220, 30*1000).wrap(core.SummonSkillWrapper)
    
        ImageArrow = core.SummonSkill("잔영의 시", 720, 270, 400+16*vEhc.getV(1,1), 3, 3000, cooltime=30000, red = True).isV(vEhc,1,1).wrap(core.SummonSkillWrapper) # 11 * 3타
        ImageArrowPassive = core.DamageSkill("잔영의 시(패시브)", 0, 400+16*vEhc.getV(1,1), 3 * 2 * 0.1).isV(vEhc,1,1).wrap(core.DamageSkillWrapper) # 10회당 1번 생성, 생성당 3타씩 2회 공격
    
        ######   Skill Wrapper   ######
        #GrittyGust.onAfter(GrittyGustDOT)
        #이볼브 연계 설정
        Evolve.onAfter(Pheonix.controller(1))
        Pheonix.onConstraint(core.ConstraintElement("이볼브 사용시 사용 금지", Evolve, Evolve.is_not_active))
            
    
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 3, 3, 22.5) #Maybe need to sync
    
        ArrowOfStorm.onAfter(AdvancedQuibberAttack)
        ArrowOfStorm.onAfter(AdvancedFinalAttack)
        ArrowOfStorm.onAfter(ImageArrowPassive)
        
        ArrowRain.onTicks([AdvancedFinalAttack, AdvancedQuibberAttack_ArrowRain])
        ImageArrow.onTicks([AdvancedFinalAttack, AdvancedQuibberAttack])
        
        ArrowRainBuff.onAfter(ArrowRain)
        QuibberFullBurstBuff.onAfter(QuibberFullBurstDOT)
        QuibberFullBurstBuff.onAfter(QuibberFullBurst)

        ImageArrowPassive.onConstraint(core.ConstraintElement("액티브 OFF", ImageArrow, ImageArrow.is_not_active))
    
        ### Exports ###
        return(ArrowOfStorm,
                [globalSkill.maple_heros(chtr.level),
                    SoulArrow, AdvancedQuibber, SharpEyes, ElusionStep, Preparation, EpicAdventure, ArrowRainBuff, CriticalReinforce, QuibberFullBurstBuff, 
                    globalSkill.soul_contract()] +\
                [] +\
                [Evolve, ArrowFlatter, ArrowRain, Pheonix, GuidedArrow, QuibberFullBurst, ImageArrow] +\
                [] +\
                [ArrowOfStorm])