from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule, InactiveRule
from . import globalSkill, linkSkill
from .jobclass import cygnus
from .jobbranch import warriors

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 10
        self.jobtype = "str"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('엘리시온', '트루 사이트'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('엘리시온', '셀레스티얼 댄스'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('셀레스티얼 댄스', '엘리시온'), RuleSet.BASE)
        return ruleset


    def apply_complex_options(self, chtr):
        chtr.add_property_ignorance(10)

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(crit = 35, pdamage = 55)

    def get_passive_skill_list(self):
        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트",stat_main = self.chtr.level // 2)
        ElementalHarmony = core.InformedCharacterModifier("엘리멘탈 하모니",patt = 10)
        
        SwordOfLight = core.InformedCharacterModifier("소드 오브 라이트",att = 20)
        Soul = core.InformedCharacterModifier("소울",armor_ignore = 10)
        InnerTrust = core.InformedCharacterModifier("이너 트러스트",att = 20)
        BodyAndSoul = core.InformedCharacterModifier("바디 앤 소울",stat_main = 40, stat_sub = 20)
        InnerShout = core.InformedCharacterModifier("이너 샤우트",att = 30, stat_main = 40)
        
        SoulPledge = core.InformedCharacterModifier("소울 플레지",stat_main = 30, stat_sub = 30, crit = 10) #오더스?
        SwordExpert = core.InformedCharacterModifier("소드 엑스퍼트",att = 50, crit_damage = 15) #오더스?
        Unforseeable = core.InformedCharacterModifier("언포시어블",armor_ignore = 30, boss_pdamage = 15) #오더스?
        
        return [ElementalHarmony, ElementalExpert, SwordOfLight, Soul, InnerTrust,
                            BodyAndSoul, InnerShout, SoulPledge, SwordExpert, Unforseeable]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 34)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)
        
        return [WeaponConstant, Mastery]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        하이퍼 : 
        트루사이트 : 내성무시 / 방무
        보스전 딜스킬 : 리인포스 /이그노어 가드/보스킬러
        '''
        MasterOfSword = core.CharacterModifier(crit = 35, pdamage_indep = 12.5, att=45)  #타수2배 , 공격력 90%를 편집함

        #Buff skills
        NimbleFinger = core.BuffSkill("님블 핑거", 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper)    #딜레이 모름
        TrueSight = core.BuffSkill("트루 사이트", 600, 30 * 1000, armor_ignore = 10+10, pdamage_indep = 5).wrap(core.BuffSkillWrapper)   #딜레이 모름, 방10/지속20s/내성10?
        SolunaTime = core.BuffSkill("솔루나 타임", 600, 200 * 1000, rem = True).wrap(core.BuffSkillWrapper)  #딜레이 모름
        SoulForge = core.BuffSkill("소울 포지", 600, 180 * 1000, att = 50, rem = True).wrap(core.BuffSkillWrapper)      #딜레이 모름
        GloryOfGuardians = core.BuffSkill("글로리 오브 가디언즈", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        #Damage Skills
        NormalAttack = core.DamageSkill("댄스오브 문/스피딩 선셋", (360+270)/2, 400, 4 * 2, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20) + MasterOfSword.copy()).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        CygnusPalanks = cygnus.PhalanxChargeWrapper(vEhc, 4, 4)
        
        SelestialDanceSummon = core.SummonSkill("셀레스티얼 댄스(추가타)", 0, 5000, (1200 + 40 * vEhc.getV(0,0)), 3, (40 + vEhc.getV(0,0)) * 1000, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper) #딜레이 모름
        SelestialDanceInit = core.BuffSkill("셀레스티얼 댄스", 700, (40+vEhc.getV(0,0))*1000, cooltime = 150000, red = True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)

        SelestialDanceAttack = core.DamageSkill("댄스오브 문/스피딩 선셋(셀레스티얼)", 0, 400*0.01*(30+vEhc.getV(0,2)), 4 * 2, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20)+MasterOfSword.copy()).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)    #직접사용 X
        
        #엘리시온 38타 / 3타
        ElisionBreak = core.DamageSkill("엘리시온(균열)", 0, 2600 + 104*vEhc.getV(1,1), 12).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)    #3회 발동
        ElisionTick = core.DamageSkill("크로스 더 스틱스(엘리시온에 의해 발동)", 30 * 1000 / 40, 1450, 5 * 2, modifier = MasterOfSword.copy()).isV(vEhc,1,1).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)  #40회 반복
        ElisionBuff = core.BuffSkill("엘리시온", 750, 30 * 1000, cooltime = 180 * 1000).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)    #시전딜레이 750ms
        
        #소울 이클립스
        SoulEclipse = core.SummonSkill("소울 이클립스", 810, 1000, 510 + 8 * vEhc.getV(3,3), 7, 30 * 1000, cooltime = 180 * 1000).isV(vEhc,3,3).wrap(core.SummonSkillWrapper)
        SolunaDivide = core.DamageSkill("솔루나 디바이드", 0, 1250 + 50 * vEhc.getV(3,3), 15 * 5, cooltime = 180 * 1000).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
        
        #Final attack type
        SelestialDanceInit.onAfter(SelestialDanceSummon)
        
        SelecstialDanceOption = core.OptionalElement(SelestialDanceInit.is_active, SelestialDanceAttack)
        
        NormalAttack.onAfter(SelecstialDanceOption)
        
        Elision = core.RepeatElement(ElisionTick, 40)
        Elision.onAfter(core.RepeatElement(ElisionBreak, 4))
        ElisionBuff.onAfter(Elision)
    
        SolunaDivide.set_disabled_and_time_left(-1)
        SoulEclipse.onAfter(SolunaDivide.controller(30*1000))

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 2)
        for sk in [NormalAttack, ElisionTick]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeaponCooltimeDummy = auraweapon_builder.get_buff()

        return(NormalAttack,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    NimbleFinger, TrueSight, SolunaTime, SoulForge, 
                    GloryOfGuardians, AuraWeaponBuff, linkSkill.soul_contract(), ElisionBuff, SelestialDanceInit, 
                    ] +\
                [CygnusPalanks, SolunaDivide] +\
                [SelestialDanceSummon, SoulEclipse] +\
                [AuraWeaponCooltimeDummy] +\
                [NormalAttack])