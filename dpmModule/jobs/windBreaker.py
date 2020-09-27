from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import bowmen
from .jobclass import cygnus
from math import ceil

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "dex"
        self.jobname = "윈드브레이커"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트", patt = 10)
        ElementalHarmony = core.InformedCharacterModifier("엘리멘탈 하모니", stat_main = chtr.level // 2)
        
        WhisperOfWind = core.InformedCharacterModifier("위스퍼 오브 윈드", att = 20)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝", stat_main = 30, stat_sub = 30)
        
        WindBlessingPassive = core.InformedCharacterModifier("윈드 블레싱(패시브)", pstat_main = 15+passive_level//3, patt = 10 + ceil(passive_level/3))
        BowExpert = core.InformedCharacterModifier("보우 엑스퍼트", att = 30 + passive_level, crit_damage = 20+passive_level//2, pdamage_indep = 25 + passive_level//3, boss_pdamage = 40 + passive_level)
        return [ElementalExpert, ElementalHarmony, WhisperOfWind, PhisicalTraining, BowExpert, WindBlessingPassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5 + 0.5*ceil(passive_level / 2))
        
        return [WeaponConstant, Mastery]

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage = 45, armor_ignore = 15)

    def generate(self, vEhc, chtr : ck.AbstractCharacter):
        '''
        코강 순서:
        천노-윔-브링어

        하이퍼:
        트라이플링 윔-리인포스, 인핸스, 더블찬스
        천공의 노래-리인포스, 보스 킬러

        하울링게일 58회, 볼텍스 스피어 17회 타격
        
        트라이플링 윔 평균치로 계산
        
        '''
        base_modifier = chtr.get_base_modifier()
        additional_target = base_modifier.additional_target
        passive_level = base_modifier.passive_level + self.combat
        #Buff skills
        Storm = core.BuffSkill("엘리멘트(스톰)", 0, 200 * 1000, pdamage = 10, rem = True).wrap(core.BuffSkillWrapper) #딜레이 모름
        SylphsAid = core.BuffSkill("실프스 에이드", 0, 200 * 1000, att = 20, crit = 10, rem = True).wrap(core.BuffSkillWrapper) #딜레이 모름
        Albatross = core.BuffSkill("알바트로스 맥시멈", 0, 200 * 1000, att = 50 + passive_level, pdamage = 25+2*(passive_level//3), armor_ignore = 15+passive_level//3, crit = 25+passive_level//2, rem = True).wrap(core.BuffSkillWrapper)  #900 -> 690
        SharpEyes = core.BuffSkill("샤프 아이즈", 660, (300+10*self.combat) * 1000, crit = 20 + ceil(self.combat/2), crit_damage = 15 + ceil(self.combat/2), rem = True).wrap(core.BuffSkillWrapper)
        GloryOfGuardians = core.BuffSkill("글로리 오브 가디언즈", 0, 60 * 1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        StormBringerDummy = core.BuffSkill("스톰 브링어(버프)", 0, 200 * 1000).wrap(core.BuffSkillWrapper)  #딜레이 계산 필요
        # 하이퍼: 데미지 증가, 확률 10% 증가, 타수 증가
        whim_proc = (50 + 10 + passive_level//2) * 0.01
        advanced_proc = (20 + passive_level//3) * 0.01
        TriflingWhim = core.DamageSkill("트라이플링 윔", 0,
            (290 + passive_level*3) * (1 - advanced_proc) + (390 + passive_level*3) * advanced_proc, 2 * whim_proc, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        StormBringer = core.DamageSkill("스톰 브링어", 0, 500, 0.3).setV(vEhc, 2, 2, True).wrap(core.DamageSkillWrapper)
    
        # 핀포인트 피어스
        PinPointPierce = core.DamageSkill("핀포인트 피어스", 690, 340, 2, cooltime = 30 * 1000).wrap(core.DamageSkillWrapper)
        PinPointPierceDebuff = core.BuffSkill("핀포인트 피어스(버프)", 0, 30 * 1000, cooltime = -1, pdamage = 15, armor_ignore = 15).wrap(core.BuffSkillWrapper)

        #Damage Skills
        # 하이퍼: 데미지 증가, 보스 데미지 증가
        target_pdamage = ((120 + self.combat // 2) / 100) ** (4 + additional_target) * 100 - 100 # 코강렙 20이상 가정.
        SongOfHeaven = core.DamageSkill("천공의 노래", 120, 345 + self.combat*3, 1, modifier = core.CharacterModifier(pdamage = target_pdamage + 20, boss_pdamage = 30)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        CygnusPalanks = core.SummonSkill("시그너스 팔랑크스", 600, 120 * 5, 450 + 18*vEhc.getV(0,0), 5, 120 * (40 + vEhc.getV(0,0)), cooltime = 30 * 1000, red=True).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        
        Mercilesswind = core.DamageSkill("아이들 윔", 600, (500 + 20*vEhc.getV(4,4)) * 0.775, 10 * 3, cooltime = 10 * 1000, red=True).isV(vEhc,4,4).wrap(core.DamageSkillWrapper) #도트 데미지 9초간 초당 1000%
        MercilesswindDOT = core.DotSkill("아이들 윔(도트)", 0, 1000, 500 + 20*vEhc.getV(4,4), 1, 9000, cooltime = -1).wrap(core.SummonSkillWrapper)
    
        #Summon Skills
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 5, 5)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0) # TODO: 윔 발생여부 확인할것
        HowlingGail = core.SummonSkill("하울링 게일", 630, 150, 250 + 10*vEhc.getV(1, 1), 3, 150*58-1, cooltime = 20 * 1000).isV(vEhc, 1, 1).wrap(core.SummonSkillWrapper) #58타
        WindWall = core.SummonSkill("윈드 월", 720, 2000, 550 + vEhc.getV(2, 2)*22, 5, 45 * 1000, cooltime = 90 * 1000, red=True).isV(vEhc, 2, 2).wrap(core.SummonSkillWrapper)
        WindWallExceed = core.SummonSkill("윈드 월(초과)", 720, 2000, (550 + vEhc.getV(2, 2)*22) / 2, 5 * 2 , 45 * 1000, cooltime=-1).isV(vEhc, 2, 2).wrap(core.SummonSkillWrapper)
        VortexSphere = core.SummonSkill("볼텍스 스피어", 720, 180, 400+16*vEhc.getV(0,0), 6, 180*17-1, cooltime=35000, red=True).isV(vEhc,0,0).wrap(core.SummonSkillWrapper) # 17타
        
        ######   Skill Wrapper   #####
        
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 3, 3, 10 + 25+passive_level//2 + 20+ceil(self.combat/2)) # 실프스 에이드 + 알바트로스 맥시멈 + 샤프 아이즈

        WindWall.onAfter(WindWallExceed)
    
        #Damage
        SongOfHeaven.onAfters([TriflingWhim, StormBringer])
        PinPointPierce.onAfters([PinPointPierceDebuff, TriflingWhim, StormBringer])
        MirrorBreak.onAfters([TriflingWhim, StormBringer])
        #Summon
        CygnusPalanks.onTicks([core.RepeatElement(TriflingWhim, 5), core.RepeatElement(StormBringer, 5)])
        HowlingGail.onTicks([TriflingWhim, StormBringer])
        VortexSphere.onTicks([TriflingWhim, StormBringer])

        Mercilesswind.onAfter(MercilesswindDOT)

        return(SongOfHeaven, 
                [globalSkill.maple_heros(chtr.level, name = "시그너스 나이츠", combat_level=self.combat), globalSkill.useful_combat_orders(),
                    Storm, SylphsAid, Albatross, SharpEyes, GloryOfGuardians, StormBringerDummy, CriticalReinforce, cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level),
                    PinPointPierceDebuff,
                    globalSkill.soul_contract()] +\
                [Mercilesswind]+\
                [GuidedArrow, HowlingGail, VortexSphere, WindWall, WindWallExceed, MercilesswindDOT, CygnusPalanks, PinPointPierce, MirrorBreak, MirrorSpider]+\
                []+\
                [SongOfHeaven])
