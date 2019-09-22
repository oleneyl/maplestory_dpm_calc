from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, SynchronizeRule
from . import globalSkill
#TODO : 도트데미지 적용 / 포이즌노바 / 퓨리오브 이프리트

#Infinity Graph Element
class InfinityWrapper(core.BuffSkillWrapper):
    def __init__(self, serverlag = 3):
        skill = core.BuffSkill("인피니티", 960, 40000, cooltime = 180 * 1000, rem = True, red = True)
        super(InfinityWrapper, self).__init__(skill)
        self.passedTime = 0
        self.serverlag = serverlag
        
    def spend_time(self, time):
        if self.onoff:
            self.passedTime += time
        super(InfinityWrapper, self).spend_time(time)
            
    def get_modifier(self):
        if self.onoff:
            return core.CharacterModifier(pdamage_indep = (70 + 4 * (self.passedTime // ((3+self.serverlag)*1000))) )
        else:
            return core.CharacterModifier()
        
    def _use(self, rem = 0, red = 0):
        self.passedTime = 0
        return super(InfinityWrapper, self)._use(rem = rem, red = red)

'''This function is recommended.
'''

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = True
        self.jobtype = "int"
        self.vEnhanceNum = 13
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'crit', 'boss_pdamage')
        self.preEmptiveSkills = 2

    def apply_complex_options(self, chtr):
        chtr.buff_rem += 50
        chtr.add_property_ignorance(10)

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(SynchronizeRule('소울 컨트랙트', '인피니티', 10000, 1), RuleSet.BASE)
        return ruleset

    def get_passive_skill_list(self):
        HighWisdom = core.InformedCharacterModifier("하이 위즈덤", stat_main = 40)
        SpellMastery = core.InformedCharacterModifier("스펠 마스터리", att = 10)
        MagicCritical = core.InformedCharacterModifier("매직 크리티컬", crit = 30, crit_damage = 13)
        ElementAmplication = core.InformedCharacterModifier("엘리멘트 엠플리피케이션", pdamage = 50)
        
        ElementalReset = core.InformedCharacterModifier("엘리멘탈 리셋", pdamage_indep = 40)
        
        MasterMagic = core.InformedCharacterModifier("마스터 매직", att = 30)
        ArcaneAim = core.InformedCharacterModifier("아케인 에임", armor_ignore = 20)
        
        return [HighWisdom, SpellMastery, MagicCritical, ElementalReset, 
                                    MasterMagic, ElementAmplication, ArcaneAim]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -2.5)
        ExtremeMagic = core.InformedCharacterModifier("익스트림 매직", pdamage_indep = 20)
        ArcaneAim = core.InformedCharacterModifier("아케인 (실시간)", pdamage = 40)
        PerventDrain = core.InformedCharacterModifier("퍼번트 드레인", pdamage_indep = 25)
        
        return [WeaponConstant, Mastery, ExtremeMagic, PerventDrain, ArcaneAim]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        포이즌 노바 4히트
        
        V 코어 강화 순위
        
        쓸윈/쓸샾/(쓸오더)/도퍼/노바/언스/오버마나
        이럽/패럴/헤이즈/이그나이트/오라/메테/이프/메기/텔마
        
        소울 컨트랙트를 인피니티 마지막과 맞춤
        언스테이블 메모라이즈를 사용하지 않음
        
        극딜형 스킬은 쿨마다 사용함
        
        '''
        #Buff skills
        Meditation = core.BuffSkill("메디테이션", 0, 240000, att = 30, rem = True, red = True).wrap(core.BuffSkillWrapper)
        EpicAdventure = core.BuffSkill("에픽 어드벤처", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        OverloadMana = core.BuffSkill("오버로드 마나", 0, 99999 * 10000, pdamage_indep = 8+int(0.1*vEhc.getV(1,5))).isV(vEhc,1,5).wrap(core.BuffSkillWrapper)
        
        #Damage Skills
        #Full speed, No Combat Orders
        Paralyze = core.DamageSkill("패럴라이즈", 600, 250 + 3*combat, 7, modifier = core.CharacterModifier(pdamage = 10)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        #Need to connect Both Skill by cascade.
        FlameHeize = core.DamageSkill("플레임 헤이즈", 1080, 504 + 8*combat, 6, cooltime = 4 * 1000).setV(vEhc, 2, 2, True).wrap(core.DamageSkillWrapper)
        MistEruption = core.DamageSkill("미스트 이럽션", 780, 776.25 +12.25*combat, 8, modifier = core.CharacterModifier(pdamage = 10, armor_ignore = 52)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        DotPunisher = core.DamageSkill("도트 퍼니셔", 870, (400+vEhc.getV(0,0)*15), 5*(1+19*0.75), cooltime = 25 * 1000).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)#=775*(1+0.75*19)*5
        PoisonNova = core.DamageSkill("포이즌 노바", 750, 500 + 20*vEhc.getV(2,1), 6, cooltime = 25*1000).isV(vEhc,2,1).wrap(core.DamageSkillWrapper)
        PoisonNovaErupt = core.DamageSkill("포이즌 노바(폭발)", 0, 400 + 18*vEhc.getV(2,1), 6 * (3 + 0.50)).isV(vEhc,2,1).wrap(core.DamageSkillWrapper)   #4히트
    
        Meteor = core.DamageSkill("메테오", 870, 935+combat*10, 4, cooltime = 45 * 1000).setV(vEhc, 5, 2, True).wrap(core.DamageSkillWrapper)
        MegidoFlame = core.DamageSkill("메기도 플레임", 690, 700, 9, cooltime = 50 * 1000).setV(vEhc, 8, 2, True).wrap(core.DamageSkillWrapper)
        
        #Summoning skill
        Ifritt = core.SummonSkill("이프리트", 900, 3030, 450+6*combat, 1, 999999999).setV(vEhc, 6, 2, False).wrap(core.SummonSkillWrapper)
        FireAura = core.SummonSkill("파이어 오라", 0, 3000, 400, 2, 999999999).setV(vEhc, 4, 2, True).wrap(core.SummonSkillWrapper)
        FuryOfIfritt = core.SummonSkill("퓨리 오브 이프리트", 1000, 300, 200+8*vEhc.getV(3,2), 6, 21*300, cooltime = 75000).isV(vEhc,2,1).wrap(core.SummonSkillWrapper)
        
        #FinalAttack
        MeteorPassive = core.DamageSkill("메테오(패시브)", 0, (220+4*combat) * (0.6+0.01*combat), 1).setV(vEhc, 5, 2, True).wrap(core.DamageSkillWrapper)
        Ignite = core.DamageSkill("이그나이트", 0, 110*0.5, 3).setV(vEhc, 3, 4, False).wrap(core.DamageSkillWrapper)
        #Ignite : Need Wrapper
        
        ParalyzeDOT = core.DotSkill("도트(패럴라이즈)", 240, 10000).wrap(core.SummonSkillWrapper)
        MistDOT = core.DotSkill("도트(포이즌 미스트)", 240, 12000).wrap(core.SummonSkillWrapper)
        HeizeFlameDOT = core.DotSkill("도트(헤이즈 플레임)", 200, 20000).wrap(core.SummonSkillWrapper)
        TeleportMasteryDOT = core.DotSkill("도트(텔레포트 마스터리)", 49, 8000).wrap(core.SummonSkillWrapper)
        MegidoFlameDOT = core.DotSkill("도트(메기도 플레임)", 700, 60000).wrap(core.SummonSkillWrapper)
        DotPunisherDOT = core.DotSkill("도트(도트 퍼니셔)", 200+3*vEhc.getV(0,0), 16000).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        PoisonNovaDOT = core.DotSkill("도트(포이즌 노바)", 300+12*vEhc.getV(2,1), 20000).isV(vEhc,2,1).wrap(core.SummonSkillWrapper)
        
        
        Infinity = InfinityWrapper()
        
        Paralyze.onAfters([MeteorPassive, Ignite, ParalyzeDOT.controller(1)])
        
        FlameHeize.onAfters([MeteorPassive, Ignite, MistEruption, HeizeFlameDOT.controller(1)])
        
        DotPunisher.onAfters([core.RepeatElement(MeteorPassive, 20),core.RepeatElement(Ignite, 20), DotPunisherDOT.controller(1)])
        Meteor.onAfter(Ignite)
        MegidoFlame.onAfters([Ignite, MeteorPassive, MegidoFlameDOT.controller(1)])
        
        Ifritt.onTicks([Ignite, MeteorPassive])
        FuryOfIfritt.onAfters([core.RepeatElement(Ignite, 21)])
        PoisonNova.onAfter(PoisonNovaErupt)
        PoisonNova.onAfter(PoisonNovaDOT.controller(1))

        # 극딜기 싱크로
        SoulContract = globalSkill.soul_contract()
        #SoulContract.set_disabled_and_time_left(30000)       

        return (Paralyze, 
                [Infinity, Meditation, EpicAdventure, OverloadMana.ensure(vEhc,1,5),
                globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster(),
                SoulContract] +\
                [DotPunisher.ensure(vEhc,0,0), Meteor, MegidoFlame, FlameHeize, PoisonNova.ensure(vEhc,2,1)] +\
                [Ifritt, FireAura, FuryOfIfritt.ensure(vEhc,3,2),
                    ParalyzeDOT, MistDOT, HeizeFlameDOT, TeleportMasteryDOT, MegidoFlameDOT, DotPunisherDOT.ensure(vEhc,0,0), PoisonNovaDOT.ensure(vEhc,2,1)] +\
                [] +\
                [Paralyze])