from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule, ReservationRule
from . import globalSkill
from .jobclass import heroes
from .jobbranch import thieves

# TODO : [마크 오브 팬텀] : 괴도의 증표를 1개 모으는데 필요한 얼티밋 드라이브 적중 수가 5회에서 7회로 증가됩니다. 템페스트 오브 카드로도 괴도의 증표를 모을 수 있게 됩니다. 얼티밋 드라이브와 같은 횟수를 공격해야 괴도의 증표를 획득 할 수 있습니다.
######   Passive Skill   ######


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 14
        self.jobtype = "luk"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_passive_skill_list(self):
        HighDexterity = core.InformedCharacterModifier("하이 덱스터리티",stat_sub = 40)
        LuckMonopoly = core.InformedCharacterModifier("럭 모노폴리",stat_main = 60)
        LuckOfPhantomtheif = core.InformedCharacterModifier("럭오브팬텀시프",stat_main = 60)
        MoonLight = core.InformedCharacterModifier("문 라이트",att = 40)
        AcuteSence = core.InformedCharacterModifier("어큐트 센스",crit = 35, pdamage_indep = 30)
        CainExpert = core.InformedCharacterModifier("케인 엑스퍼트", att = 40+self.combat, crit_damage = 15, pdamage_indep = 25 + int(self.combat * 0.5))
    
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(self.vEhc, 3, 3)

        return [
                            HighDexterity, LuckMonopoly, LuckOfPhantomtheif, MoonLight, AcuteSence, CainExpert,
                                ReadyToDiePassive]
                                
    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)
        
        return [WeaponConstant, Mastery]

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ReservationRule("소울 컨트랙트", "마크 오브 팬텀"), RuleSet.BASE)
        return ruleset

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        하이퍼 : 
        템오카 - 리인포스 / 쿨리듀스
        얼드 - 리인포스, 이그노어가드
        
        조커 100%
        
        v코어 : 14개
        1티어 :  얼티밋, 느와르, 템와
        2티어 : 탤팬4
        
        펫버프 : 프레이 오브 아리아, 메용, 크오체
        템페스트 오브 카드 사용하지 않음
        '''
        
        #Buff skills
        TalentOfPhantomII = core.BuffSkill("분노(탤팬2)", 0, 180000, rem = True, att = 30).wrap(core.BuffSkillWrapper)
        # 힐+마오팬보다 분노가 허수아비딜은 잘나옴
        # TalentOfPhantomII = core.BuffSkill("힐(탤팬2)", 450, 2*1000, cooltime=10*1000, pdamage_indep=10).wrap(core.BuffSkillWrapper)
        TalentOfPhantomIII = core.BuffSkill("크로스 오버 체인(탤팬3)", 0, 180000, rem = True, pdamage_indep = 20).wrap(core.BuffSkillWrapper)
        FinalCut = core.DamageSkill("탤런트 오브 팬텀시프 IV(파이널 컷)", 870, 2000, 1, cooltime = 90000).setV(vEhc, 3, 2, True).wrap(core.DamageSkillWrapper)
        FinalCutBuff = core.BuffSkill("파이널 컷(버프, 탤팬4)", 0, 60000, cooltime = -1, rem = True, pdamage_indep = 40).wrap(core.BuffSkillWrapper)
        BoolsEye = core.BuffSkill("불스아이(탤팬5)", 600, 30 * 1000, cooltime = 180 * 1000, crit = 20, crit_damage = 10, armor_ignore = 20, pdamage = 20).wrap(core.BuffSkillWrapper)
    
        JudgementBuff = core.BuffSkill("저지먼트(버프)", 0, 999999999, crit = 0).wrap(core.BuffSkillWrapper)    #확률성 크리티컬
        
        Booster = core.BuffSkill("부스터", 0, 240 * 1000, rem = True).wrap(core.BuffSkillWrapper)    #딜레이 모름
        
        MileAiguillesInit = core.BuffSkill("얼티밋 드라이브(개시)", 240, 240).wrap(core.BuffSkillWrapper)
        MileAiguilles = core.DamageSkill("얼티밋 드라이브", 150, 125 + 2*combat, 3, modifier = core.CharacterModifier(pdamage = 20, armor_ignore = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        CarteNoir = core.DamageSkill("느와르 카르트", 0, 270, min(chtr.get_modifier().crit/100 + 0.1, 1)).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        CarteNoir_ = core.DamageSkill("느와르 카르트(저지먼트)", 0, 270, 10).setV(vEhc, 1, 2, True).wrap(core.DamageSkillWrapper)
        
        PrieredAria = core.BuffSkill("프레이 오브 아리아", 0, (240+7*combat)*1000, pdamage = 30+combat, armor_ignore = 30+combat).wrap(core.BuffSkillWrapper)

        # 템오카 안쓰는게 더 높게 나옴
        # TempestOfCardInit = core.DamageSkill("템페스트 오브 카드(시전)", 0, 0, 0, cooltime = 18000*0.8 + 180*56, red = True).wrap(core.DamageSkillWrapper, name = "템오카 시전")
        # TempestOfCard = core.DamageSkill("템페스트 오브 카드", 180, 200+2*combat, 3, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)
    
        HerosOath = core.BuffSkill("히어로즈 오쓰", 0, 60000, cooltime = 120000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc, 3, 3)
        
        # 트와일라이트 미적용 상태
        # Twilight = core.BuffSkill("트와일라이트", 120, 15000, cooltime = 15000, armor_ignore = 20).wrap(core.BuffSkillWrapper)
        # TwilightHit = core.DamageSkill("트와일라이트(공격)", 540, 450, 3, cooltime = -1).wrap(core.DamageSkillWrapper)

        JokerInit = core.DamageSkill("조커(시전)", 720, 0, 0, cooltime = 150000, red = True).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
        JokerDamage = core.DamageSkill("조커", 100*5, 240+9*vEhc.getV(4,4), 30).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)  #14회 반복, 총 420타이므로 30타로 적용
        JokerBuff = core.BuffSkill("조커(버프)", 0, 30000, cooltime = -1, pdamage_indep = (1 + (vEhc.getV(4,4) - 1) // 5) * 2 / 5).isV(vEhc,4,4).wrap(core.BuffSkillWrapper)
        
        BlackJack = core.SummonSkill("블랙잭", 570, 250, 400+16*vEhc.getV(1,1), 1, 5000-1, cooltime = 15000).isV(vEhc,1,1).wrap(core.SummonSkillWrapper)
        BlackJackFinal = core.DamageSkill("블랙잭(최종)", 0, 1200+48*vEhc.getV(1,1), 6, cooltime = -1).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        
        MarkOfPhantom = core.DamageSkill("마크 오브 팬텀", 900, 600+24*vEhc.getV(2,2), 3 * 7, cooltime = 30000).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        MarkOfPhantomEnd = core.DamageSkill("마크 오브 팬텀(최종)", 0, 1200+48*vEhc.getV(2,2), 12).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        
        #### 그래프 빌드
        
        FinalCut.onAfter(FinalCutBuff.controller(1))
        
        Frid = heroes.FridWrapper(vEhc, 0, 0)
        
        CardStack = core.StackSkillWrapper(core.BuffSkill("카드 스택", 0, 99999999), 40, name = "느와르 카르트 스택")
        
        AddCard = CardStack.stackController(1, name = "스택 1 증가")
        Judgement = CarteNoir_
        Judgement.onAfter(CardStack.stackController(-9999, name = "스택 초기화"))
        
        FullStack = core.OptionalElement(partial(CardStack.judge,40, 1), Judgement, name = "풀스택시")

        CarteNoir.onAfter(AddCard)
        CarteNoir.onAfter(FullStack)
        MileAiguilles.onAfter(CarteNoir)
        MileAiguilles.onAfter(MileAiguillesInit.controller(500, 'set_enabled_and_time_left'))
        
        BasicAttack = core.OptionalElement(MileAiguillesInit.is_active, MileAiguilles, MileAiguillesInit, name = "선딜 반영")
        BasicAttackWrapper = core.DamageSkill('기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)
        # TempestOfCardInit.onAfter(core.RepeatElement(TempestOfCard, 56))
        # TempestOfCard.onAfter(CarteNoir)
        
        JokerDamage.onAfter(core.RepeatElement(CarteNoir, 10))    #조커는 느와르를 발동하나, 조커 3타에 1번씩만 들어가므로 30 / 3 = 10
        JokerDamage.onAfter(JokerBuff)
        
        JokerInit.onAfter(core.RepeatElement(JokerDamage, 14))
        JokerInit.onAfter(JokerBuff)
        
        BlackJack.onTick(CarteNoir)
        BlackJack.onAfter(BlackJackFinal.controller(5000))
        
        MarkOfPhantom.onAfter(MarkOfPhantomEnd)

        MileAiguillesInit.protect_from_running()
        
        #이들 정보교환 부분을 굳이 Task exchange로 표현할 필요가 있을까?
        
        return(BasicAttackWrapper,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    TalentOfPhantomII, TalentOfPhantomIII, FinalCutBuff, BoolsEye,
                    JudgementBuff, Booster, PrieredAria, HerosOath, ReadyToDie, JokerBuff, Frid,
                    globalSkill.soul_contract()] +\
                [FinalCut, JokerInit, MarkOfPhantom, BlackJackFinal] +\
                [BlackJack] +\
                [MileAiguillesInit] +\
                [BasicAttackWrapper])