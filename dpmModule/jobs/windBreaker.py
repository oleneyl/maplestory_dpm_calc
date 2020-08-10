from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import bowmen
from .jobclass import cygnus
#TODO : 5차 신스킬 적용

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 10
        self.jobtype = "dex"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self._use_critical_reinforce = True

    def get_passive_skill_list(self):
        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트", patt = 10)
        ElementalHarmony = core.InformedCharacterModifier("엘리멘탈 하모니", stat_main = self.chtr.level // 2)
        
        WhisperOfWind = core.InformedCharacterModifier("위스퍼 오브 윈드",att = 20)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝", stat_main = 30, stat_sub = 30)
        
        WindBlessingPassive = core.InformedCharacterModifier("윈드 블레싱(패시브)",pstat_main = 15, patt = 10 + self.combat*1)
        BowExpert = core.InformedCharacterModifier("보우 엑스퍼트", att = 30 + self.combat*1, crit_damage = 20, pdamage_indep = 25 + self.combat*1, boss_pdamage = 40 + self.combat*1)
        return [ElementalExpert, ElementalHarmony, WhisperOfWind, PhisicalTraining, BowExpert, WindBlessingPassive]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5 + self.combat*0.5)
        
        return [WeaponConstant, Mastery]

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage = 45, armor_ignore = 15)

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        코강 순서:
        천노-윔-브링어
        
        트라이플링 윔 평균치로 계산
        
        '''
        #Buff skills
        Storm = core.BuffSkill("엘리멘트(스톰)", 0, 200 * 1000, pdamage = 10, rem = True).wrap(core.BuffSkillWrapper)#딜레이 모름
        SylphsAid = core.BuffSkill("실프스 에이드", 0, 200 * 1000, att = 20, crit = 10, rem = True).wrap(core.BuffSkillWrapper)#딜레이 모름
        Albatross = core.BuffSkill("알바트로스 맥시멈", 0, 200 * 1000, att = 50 + combat*1, pdamage = 25, armor_ignore = 15, crit = 25, rem = True).wrap(core.BuffSkillWrapper)  #900 -> 690
        SharpEyes = core.BuffSkill("샤프 아이즈", 660, 300 * 1000, crit = 20 + combat*1, crit_damage = 15 + combat*1, rem = True).wrap(core.BuffSkillWrapper)
        GloryOfGuardians = core.BuffSkill("글로리 오브 가디언즈", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        StormBringerDummy = core.BuffSkill("스톰 브링어(버프)", 660, 200 * 1000).wrap(core.BuffSkillWrapper)  #딜레이 계산 필요
        # 하이퍼: 데미지 증가, 확률 10% 증가, 타수 증가
        TriflingWhim = core.DamageSkill("트라이플링 윔", 0, (290+3*combat)*0.8+(390+3*combat)*0.2, 2*(0.5+0.1), modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        StormBringer = core.DamageSkill("스톰 브링어", 0, 500, 0.3).setV(vEhc, 2, 2, True).wrap(core.DamageSkillWrapper)
    
        # 핀포인트 피어스
        PinPointPierce = core.DamageSkill("핀포인트 피어스", 900, 340, 2, cooltime=30 * 1000).wrap(core.DamageSkillWrapper)
        PinPointPierceDebuff = core.BuffSkill("핀포인트 피어스(버프)", 0, 30 * 1000, cooltime=-1, pdamage=15, armor_ignore=15).wrap(core.BuffSkillWrapper)

        #Damage Skills
        SongOfHeaven = core.DamageSkill("천공의 노래", 120, 345 +combat*3, 1, modifier = core.CharacterModifier(pdamage = 127.36, boss_pdamage = 30)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)# 코강렙 20이상 가정.
        
        CygnusPalanks = core.SummonSkill("시그너스 팔랑크스", 780, 120 * 5, 450 + 18*vEhc.getV(0,0), 5, 120 * (40 + vEhc.getV(0,0)), cooltime = 30 * 1000).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        
        Mercilesswind = core.DamageSkill("아이들 윔", 600, (500 + 20*vEhc.getV(4,4)) * 0.775, 10 * 3, cooltime = 10 * 1000).isV(vEhc,4,4).wrap(core.DamageSkillWrapper) #도트 데미지 9초간 초당 1000%
        MercilesswindDOT = core.DotSkill("아이들 윔(도트)", (500 + 20*vEhc.getV(4,4)), 9000).wrap(core.SummonSkillWrapper)
    
        #Summon Skills
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 5, 5)
        HowlingGail = core.SummonSkill("하울링 게일", 780, 10 * 1000 / 33, 250 + 10*vEhc.getV(1,1), 2 * 3, 10000, cooltime = 20 * 1000).isV(vEhc,1,1).wrap(core.SummonSkillWrapper) #딜레이 모름, 64���
        WindWall = core.SummonSkill("윈드 월", 720, 2000, (550 + vEhc.getV(2,2)*22) / 2, 5*3 , 45 * 1000, cooltime = 90 * 1000).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
        
        ######   Skill Wrapper   #####
        
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 3, 3, 55) #Maybe need to sync
    
        #Damage
        SongOfHeaven.onAfters([TriflingWhim, StormBringer])
        CygnusPalanks.onTicks([core.RepeatElement(TriflingWhim,5), core.RepeatElement(StormBringer,5)])
        PinPointPierce.onAfters([PinPointPierceDebuff, TriflingWhim, StormBringer])
        #Summon
        HowlingGail.onTicks([core.RepeatElement(TriflingWhim, 2), core.RepeatElement(StormBringer, 2)])

        return(SongOfHeaven, 
                [globalSkill.maple_heros(chtr.level, combat_level=combat), 
                    Storm, SylphsAid, Albatross, SharpEyes, GloryOfGuardians, StormBringerDummy, CriticalReinforce,
                    PinPointPierceDebuff,
                    globalSkill.soul_contract()] +\
                [Mercilesswind]+\
                [GuidedArrow, HowlingGail, WindWall, MercilesswindDOT, CygnusPalanks, PinPointPierce]+\
                []+\
                [SongOfHeaven])