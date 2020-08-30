from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConditionRule
from . import globalSkill
from .jobbranch import thieves
from . import jobutils
#TODO : 5차 신스킬 적용

# TODO: 왜 레투다는 5차값이 1,1인데 레투다 패시브는 2,2일까?

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "luk"
        self.jobname = "듀얼블레이드"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 40)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        Karma = core.InformedCharacterModifier("카르마", att = 30)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝", stat_main = 30, stat_sub = 30)
        
        SornsEffect = core.InformedCharacterModifier("쏜즈 이펙트", att = 30)
        DualBladeExpert = core.InformedCharacterModifier("이도류 엑스퍼트", att = 30, pdamage_indep = 20)
        Sharpness = core.InformedCharacterModifier("샤프니스", crit = 35, crit_damage = 13)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 2, 2)
        
        return [Karma, PhisicalTraining, SornsEffect, DualBladeExpert, Sharpness,
                            ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -5)    #오더스 기본적용!   
        return [WeaponConstant, Mastery]

    def get_ruleset(self):
        def check_final_cut_time(final_cut):
            return (final_cut.is_not_usable() and final_cut.is_cooltime_left(80*1000, 1)) # 파컷 직후 써레 1번만 쓰는게 더 효율적임

        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule('써든레이드', '파이널 컷', check_final_cut_time), RuleSet.BASE)
        return ruleset

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        하이퍼 : 팬텀 블로우 - 리인포스, 이그노어 가드, 보너스 어택
        블레이드 퓨리 - 리인포스, 엑스트라 타겟
        
        아수라 41타
        블레이드 토네이도 5타
        카르마 퓨리 사용
        
        코어 16개 유효 : 팬블 / 아수라 / 퓨리 -- 써든레이드 / 어센션 / 히든블레이드
        '''

        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        
        DarkSight = core.BuffSkill("다크 사이트", 0, 1, cooltime = -1).wrap(core.BuffSkillWrapper)#, pdamage_indep = 20 + 10 + int(0.2*vEhc.getV(3,3))).wrap(core.BuffSkillWrapper)
        
        PhantomBlow = core.DamageSkill("팬텀 블로우", 540, 315, 6+1, modifier = core.CharacterModifier(armor_ignore = 44, pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        SuddenRaid = core.DamageSkill("써든레이드", 690, 1150, 3, cooltime = 30000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)    #파컷의 남은 쿨타임 20% 감소
        SuddenRaidDOT = core.DotSkill("써든레이드(도트)", 210, 10000).wrap(core.SummonSkillWrapper)
        
        FinalCut = core.DamageSkill("파이널 컷", 450, 2000, 1, cooltime = 90000, red=True).wrap(core.DamageSkillWrapper)
        FinalCutBuff = core.BuffSkill("파이널 컷(버프)", 0, 60000, rem = True, cooltime = -1, pdamage_indep = 40).wrap(core.BuffSkillWrapper)
        
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        FlashBang = core.DamageSkill("플래시 뱅", 390, 250, 1, cooltime = 60000, red=True).wrap(core.DamageSkillWrapper)  #임의 딜레이.
        FlashBangDebuff = core.BuffSkill("플래시 뱅(디버프)", 0, 50000/2, cooltime = -1, pdamage = 10 * 0.9).wrap(core.BuffSkillWrapper)
        Venom = core.DotSkill("페이탈 베놈", 160*3, 8000).wrap(core.SummonSkillWrapper)
        
        # TODO: 버프 시전 딜레이 적용
        HiddenBladeBuff = core.BuffSkill("히든 블레이드(버프)", 0, 60000, cooltime = 90000, pdamage = 10).wrap(core.BuffSkillWrapper)
        HiddenBlade = core.DamageSkill("히든 블레이드", 0, 140, 1).setV(vEhc, 5, 2, True).wrap(core.DamageSkillWrapper)
        
        Asura = core.DamageSkill("아수라", 810, 0, 0, cooltime = 60000).wrap(core.DamageSkillWrapper)
        AsuraTick = core.DamageSkill("아수라(틱)", 300, 420, 4, modifier =core.CharacterModifier(armor_ignore = 100)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AsuraEnd = core.DamageSkill("아수라(종료)", 360, 0, 0, cooltime = -1).wrap(core.DamageSkillWrapper)
        
        UltimateDarksight = thieves.UltimateDarkSightWrapper(vEhc, 3, 3, 20)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc,4,4)
        
        BladeStorm = core.DamageSkill("블레이드 스톰", 120, 580+23*vEhc.getV(0,0), 7, red = True, cooltime = 90000, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        BladeStormTick = core.DamageSkill("블레이드 스톰(틱)", 210, 350+10*vEhc.getV(0,0), 5, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)  #10000/210 타
        BladeStormEnd = core.DamageSkill("블레이드 스톰(종료)", 120, 0, 0).wrap(core.DamageSkillWrapper)
        
        KarmaFury = core.DamageSkill("카르마 퓨리", 750, 750+30*vEhc.getV(1,1), 7 * 3, red = True, cooltime = 10000, modifier = core.CharacterModifier(armor_ignore = 30)).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        BladeTornado = core.DamageSkill("블레이드 토네이도", 540, 600+24*vEhc.getV(2,2), 7, red = True, cooltime = 12000, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        BladeTornadoSummon = core.SummonSkill("블레이드 토네이도(소환)", 0, 3000/5, 450+18*vEhc.getV(2,2), 6, 3000-1, cooltime=-1, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
        BladeTornadoSummonMirrorImaging = core.SummonSkill("블레이드 토네이도(소환)(미러이미징)", 0, 540, (450+18*vEhc.getV(2,2)) * 0.7, 6, 3000, cooltime=-1, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
        
        ######   Skill Wrapper   ######
    
        SuddenRaid.onAfter(SuddenRaidDOT)
        FinalCut.onAfter(FinalCutBuff.controller(1))
        
        HiddenBladeOpt = core.OptionalElement(HiddenBladeBuff.is_active, HiddenBlade)
        
        FlashBang.onAfter(FlashBangDebuff)
        for sk in [FinalCut, PhantomBlow, SuddenRaid, FlashBang, AsuraTick, BladeStorm, BladeStormTick, BladeTornado, KarmaFury]:
            sk.onAfter(HiddenBladeOpt)
            
        for sk in [PhantomBlow, AsuraTick, BladeStormTick]:
            sk.onAfter(Venom)
        
        AsuraRepeat = core.RepeatElement(AsuraTick, 28)
        Asura.onAfter(AsuraRepeat)
        AsuraRepeat.onAfter(AsuraEnd)

        BladeStormRepeat = core.RepeatElement(BladeStormTick, 48)
        BladeStorm.onAfter(BladeStormRepeat)
        BladeStormRepeat.onAfter(BladeStormEnd)

        BladeTornado.onAfter(BladeTornadoSummon)
        BladeTornado.onAfter(BladeTornadoSummonMirrorImaging)

        SuddenRaid.onAfter(FinalCut.controller(0.2, "reduce_cooltime_p"))

        for sk in [PhantomBlow, SuddenRaid, FinalCut, FlashBang, AsuraTick, 
            BladeStorm, BladeStormTick, KarmaFury, BladeTornado, HiddenBlade]:
            jobutils.create_auxilary_attack(sk, 0.7, nametag = '(미러이미징)')
        
        return(PhantomBlow,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    Booster, DarkSight, FinalCutBuff, EpicAdventure, FlashBangDebuff, HiddenBladeBuff, UltimateDarksight, ReadyToDie,
                    globalSkill.soul_contract()] +\
                [FinalCut, FlashBang, BladeTornado, SuddenRaid, KarmaFury, BladeStorm, Asura] +\
                [SuddenRaidDOT, Venom, BladeTornadoSummon, BladeTornadoSummonMirrorImaging] +\
                [] +\
                [PhantomBlow])