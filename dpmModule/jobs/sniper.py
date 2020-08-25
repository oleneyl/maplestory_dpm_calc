from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, MutualRule, ConcurrentRunRule, ReservationRule
from . import globalSkill
from .jobbranch import bowmen
#TODO : 5차 신스킬 적용    


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 10
        self.jobtype = "dex"
        self.jobname = "신궁"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 50)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(MutualRule('스플릿 애로우', '트루 스나이핑'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('에픽 어드벤처', '크리티컬 리인포스'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('불스아이', '크리티컬 리인포스'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('소울 컨트랙트', '크리티컬 리인포스'), RuleSet.BASE)
        ruleset.add_rule(ReservationRule('크리티컬 리인포스', '스플릿 애로우'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('스플릿 애로우', '소울 컨트랙트'), RuleSet.BASE)

        return ruleset

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        CriticalShot = core.InformedCharacterModifier("크리티컬 샷",crit = 40)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        
        MarkmanShip = core.InformedCharacterModifier("마크맨쉽",armor_ignore = 25, pdamage = 15)

        CrossBowExpert = core.InformedCharacterModifier("크로스보우 엑스퍼트",att= 30+self.combat*1, crit_damage = 8)
        
        return [CriticalShot, PhisicalTraining, MarkmanShip, 
                CrossBowExpert]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 35)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5 + 0.5 * self.combat)

        MortalBlow = core.InformedCharacterModifier("모탈 블로우",pdamage = 2)        
        ExtremeArchery = core.InformedCharacterModifier("익스트림 아처리:석궁",crit_damage = 20)

        return [WeaponConstant, Mastery, MortalBlow, ExtremeArchery]
        

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        거리 400
        
        스나, 피어싱, 롱레트, 프리저
        '''
        distance = 400

        WEAKNESS_FINDING = core.CharacterModifier(armor_ignore = 50 + self.combat * 1)
        DISTANCING_SENSE = core.CharacterModifier(pdamage_indep = 40 + self.combat * 2)
        LASTMAN_STANDING = core.CharacterModifier(pdamage_indep = 20 + self.combat * 2)
        PASSIVE_MODIFIER = WEAKNESS_FINDING + DISTANCING_SENSE + LASTMAN_STANDING
        
        #Buff skills
        SoulArrow = core.BuffSkill("소울 애로우", 0, 300 * 1000, att = 30, rem = True).wrap(core.BuffSkillWrapper)
        ElusionStep = core.BuffSkill("일루젼 스탭", 0, (300+combat*16) * 1000, stat_main = 40 + combat*1, rem = True).wrap(core.BuffSkillWrapper)
        SharpEyes = core.BuffSkill("샤프 아이즈", 660, 300 * 1000, crit = 20 + combat*1, crit_damage = 15 + combat*1, rem = True).wrap(core.BuffSkillWrapper)
        #크리티컬 리인포스 - >재정의 필요함..
        
        BoolsEye = core.BuffSkill("불스아이", 960, 30 * 1000, cooltime = 90 * 1000, crit = 20, crit_damage = 10, armor_ignore = 20, pdamage = 20).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        #Damage Skills
        # 롱레인지 트루샷: 나무위키피셜 DPM 떨어지므로 보류

        Snipping = core.DamageSkill("스나이핑", 630, 465+combat*5, 9 + 1, modifier = core.CharacterModifier(crit = 100, armor_ignore = 20 + combat * 1, pdamage = 20, boss_pdamage = 10) + PASSIVE_MODIFIER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        TrueSnippingTick = core.DamageSkill("트루 스나이핑(타격)", 690, 950+vEhc.getV(2,2)*30, 14+1, modifier = core.CharacterModifier(pdamage = 100, armor_ignore = 100) + PASSIVE_MODIFIER).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        TrueSnipping = core.DamageSkill("트루 스나이핑", 120, 0, 0, cooltime = 180 * 1000).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        
        ChargedArrow = core.DamageSkill("차지드 애로우", 0, 750 + vEhc.getV(1,1)*30, 10+1, cooltime = -1, modifier = PASSIVE_MODIFIER).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        ChargedArrowHold = core.SummonSkill("차지드 애로우(더미)", 0, 10000, 0, 0, 9999999, cooltime = -1).isV(vEhc,1,1).wrap(core.SummonSkillWrapper) # TODO: 공격 주기에 쿨감 적용해야 함
        #Summon Skills
        Freezer = core.SummonSkill("프리저", 900, 3030, 390, 1, 220 * 1000).setV(vEhc, 3, 3, False).wrap(core.SummonSkillWrapper)
        GuidedArrow = bowmen.GuidedArrowWrapper(vEhc, 4, 4)
        
        Evolve = core.SummonSkill("이볼브", 600, 3330, 450+vEhc.getV(5,5)*15, 7, 40*1000, cooltime = (int(121-0.5*vEhc.getV(5,5)))*1000).isV(vEhc,5,5).wrap(core.SummonSkillWrapper)
        
        SplitArrow = core.DamageSkill("스플릿 애로우(공격)", 0, 600 + vEhc.getV(0,0) * 24, 5+1, modifier = PASSIVE_MODIFIER).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        SplitArrowBuff = core.BuffSkill("스플릿 애로우", 810, 60 * 1000, 120 * 1000).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        #TODO : 스플릿애로우 계산
        
        FinalAttack = core.DamageSkill("파이널 어택", 0, 150, 0.4, modifier = PASSIVE_MODIFIER).setV(vEhc, 4, 2, True).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
        
        #이볼브 연계 설정
        Evolve.onAfter(Freezer.controller(1))
        Freezer.onConstraint(core.ConstraintElement("이볼브 사용시 사용 금지", Evolve, Evolve.is_not_active))
        
        CriticalReinforce = bowmen.CriticalReinforceWrapper(vEhc, chtr, 3, 3, 20+20) # 샤프 아이즈 20 + 불스아이 20. 불스아이를 항상 크리인에 맞춰쓰므로 가동률 고려 X
    
        SplitArrowOption = core.OptionalElement(SplitArrowBuff.is_active, SplitArrow, name = "스플릿 애로우 여부 확인")
        Snipping.onAfter(SplitArrowOption)
    
        TrueSnippingDeal = core.RepeatElement(TrueSnippingTick, 7)
        TrueSnipping.onBefore(ChargedArrowHold.controller(10000, name = "차징 유예"))
        TrueSnipping.onAfter(TrueSnippingDeal)
        
        ChargedArrowHold.onTick(Snipping) # 완충시 스나이핑 즉시 발사됨
        ChargedArrowHold.onTick(ChargedArrow)

        for sk in [Snipping, TrueSnippingTick, ChargedArrow]:
            sk.onAfter(FinalAttack)
        
        ChargedArrowHold.set_disabled_and_time_left(5000) # 최초 차징 시간
        
        return(Snipping,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_wind_booster(),
                    SoulArrow, ElusionStep, SharpEyes, BoolsEye, EpicAdventure, CriticalReinforce, SplitArrowBuff,
                        globalSkill.soul_contract()] +\
                [TrueSnipping, ChargedArrowHold, ChargedArrow] +\
                [Evolve,Freezer, GuidedArrow] +\
                [] +\
                [Snipping])