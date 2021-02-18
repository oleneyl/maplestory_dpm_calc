from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ConditionRule, RuleSet, InactiveRule
from . import globalSkill, jobutils
from .jobclass import cygnus
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 10
        self.jobtype = "STR"
        self.jobname = "소울마스터"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule('엘리시온', '셀레스티얼 댄스', lambda sk: sk.is_not_active() and sk.is_cooltime_left(30000, 1)), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('셀레스티얼 댄스', '엘리시온'), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage = 20)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ElementalExpert = core.InformedCharacterModifier("엘리멘탈 엑스퍼트", patt = 10)
        ElementalHarmony = core.InformedCharacterModifier("엘리멘탈 하모니", stat_main = chtr.level // 2)
        
        SwordOfLight = core.InformedCharacterModifier("소드 오브 라이트",att = 20)
        Soul = core.InformedCharacterModifier("소울",armor_ignore = 10)
        InnerTrust = core.InformedCharacterModifier("이너 트러스트",att = 20)
        BodyAndSoul = core.InformedCharacterModifier("바디 앤 소울",stat_main = 40, stat_sub = 20)
        InnerShout = core.InformedCharacterModifier("이너 샤우트",att = 30, stat_main = 40)
        
        SoulPledge = core.InformedCharacterModifier("소울 플레지",stat_main = 30+passive_level, stat_sub = 30+passive_level, crit = 10)
        SwordExpert = core.InformedCharacterModifier("소드 엑스퍼트",att = 50+passive_level, crit_damage = 15+passive_level//3)
        Unforseeable = core.InformedCharacterModifier("언포시어블",armor_ignore = 30+2*passive_level, boss_pdamage = 15+passive_level)
        
        return [ElementalHarmony, ElementalExpert, SwordOfLight, Soul, InnerTrust,
                            BodyAndSoul, InnerShout, SoulPledge, SwordExpert, Unforseeable]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 34)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=90+ceil(passive_level/2))
        TrueSightHyper = core.InformedCharacterModifier("트루 사이트(하이퍼)", prop_ignore = 10)
        
        return [WeaponConstant, Mastery, TrueSightHyper]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        하이퍼 : 
        트루사이트 : 내성무시 / 방무
        보스전 딜스킬 : 리인포스 / 이그노어 가드 / 보스킬러
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        FallingMoon = core.CharacterModifier(pdamage_indep = -10+passive_level//3)

        #Buff skills
        NimbleFinger = core.BuffSkill("님블 핑거", 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper) # 펫버프
        TrueSight = core.BuffSkill("트루 사이트", 600, 30 * 1000, armor_ignore = 10+10, pdamage_indep = 5).wrap(core.BuffSkillWrapper) # 내성무시는 not_implied_skill_list에 있음
        SolunaTime = core.BuffSkill("솔루나 타임", 0, (200+6*self.combat) * 1000, rem = True, crit = 35 + passive_level // 2, pdamage_indep = 25, att = 45+passive_level+passive_level//2).wrap(core.BuffSkillWrapper)  # 딜레이 없음
        SoulForge = core.BuffSkill("소울 포지", 0, 180 * 1000, att = 50, rem = True).wrap(core.BuffSkillWrapper) # 펫버프
        GloryOfGuardians = core.BuffSkill("글로리 오브 가디언즈", 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
    
        #Damage Skills
        SpeedingDance = core.DamageSkill("댄스오브 문/스피딩 선셋", (360+330+270+270)/4, 400+4*self.combat, 4 * 2, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20) + FallingMoon).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        CygnusPhalanx = cygnus.PhalanxChargeWrapper(vEhc, 4, 4)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        SelestialDanceInit = core.BuffSkill("셀레스티얼 댄스", 570, (40+vEhc.getV(0,0))*1000, cooltime = 150 * 1000, red = True).isV(vEhc,0,0).wrap(core.BuffSkillWrapper)
        SelestialDanceSummon = core.SummonSkill("셀레스티얼 댄스(추가타)", 0, 5000, (1200 + 40 * vEhc.getV(0,0)), 3, (40 + vEhc.getV(0,0)) * 1000, cooltime = -1).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)
        SelestialDanceAttack = core.DamageSkill("댄스오브 문/스피딩 선셋(셀레스티얼)", 0, (400+4*self.combat)*0.01*(30+vEhc.getV(0,0)), 4 * 2, modifier = core.CharacterModifier(pdamage = 20, boss_pdamage = 20, armor_ignore = 20) + FallingMoon).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)    #직접사용 X
        
        #엘리시온 38타 / 3타
        Elision = core.BuffSkill("엘리시온", 750, 30 * 1000, cooltime = 180 * 1000, red=True).isV(vEhc,1,1).wrap(core.BuffSkillWrapper)    #시전딜레이 750ms
        ElisionBreak = core.SummonSkill("엘리시온(균열)", 0, 10000, 520 + 21*vEhc.getV(1,1), 5 * 6 * 2, 30000, cooltime=-1, modifier = FallingMoon).isV(vEhc,1,1).wrap(core.SummonSkillWrapper)    #3회 발동
        ElisionBreakEnd = core.DamageSkill("엘리시온(균열)(종료)", 0, 150 + 6*vEhc.getV(1,1), 5 * 6 * 2, cooltime=-1, modifier = FallingMoon).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        ElisionStyx = core.DamageSkill("크로스 더 스틱스(엘리시온)", 750, 580/2, 5 * 5 * 2, modifier = FallingMoon).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)  #40회 반복
        
        #소울 이클립스
        SoulEclipse = core.SummonSkill("소울 이클립스", 270, 1000, 450 + 18 * vEhc.getV(3,3), 7, 30 * 1000, cooltime = 180 * 1000, red=True).isV(vEhc,3,3).wrap(core.SummonSkillWrapper)
        SolunaDivide = core.DamageSkill("솔루나 디바이드", 750 - 300, 1250 + 50 * vEhc.getV(3,3), 15 * 5, cooltime = -1).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)  # 다른 스킬 도중 사용 가능, 평균 딜레이만큼 뺌

        FlareSlash = core.DamageSkill("플레어 슬래시", 0, 550+22*vEhc.getV(0,0), 7*2, cooltime=12000, modifier=FallingMoon).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
        
        #Final attack type
        SelestialDanceInit.onAfter(SelestialDanceSummon)
        
        SelecstialDanceOption = core.OptionalElement(SelestialDanceInit.is_active, SelestialDanceAttack)
        
        SpeedingDance.onAfter(SelecstialDanceOption)
        
        Elision.onAfter(ElisionBreak)
        Elision.onEventEnd(ElisionBreakEnd)
    
        SoulEclipse.onAfter(SolunaDivide.controller(30*1000))

        # 엘리시온 분기
        BasicAttack = core.OptionalElement(Elision.is_active, ElisionStyx, SpeedingDance, name = "기본공격(엘리시온 여부 판단)")
        BasicAttackWrapper = core.DamageSkill('기본 공격', 0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)

        # 플레어 슬래시
        SpeedingDance.onAfter(FlareSlash.controller(300, "reduce_cooltime"))
        SelestialDanceAttack.onAfter(FlareSlash.controller(900, "reduce_cooltime"))
        ElisionStyx.onAfter(FlareSlash.controller(1200, "reduce_cooltime"))

        UseFlareSlash = core.OptionalElement(FlareSlash.is_available, FlareSlash, name="플레어 슬래시 쿨타임 체크")
        SpeedingDance.onAfter(UseFlareSlash)
        ElisionStyx.onAfter(UseFlareSlash)
        FlareSlash.protect_from_running()

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 2, modifier=FallingMoon, hit=6*2)
        for sk in [SpeedingDance, ElisionStyx]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        return(BasicAttackWrapper,
                [globalSkill.maple_heros(chtr.level, name = "시그너스 나이츠", combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    NimbleFinger, TrueSight, SolunaTime, SoulForge, cygnus.CygnusBlessWrapper(vEhc, 0, 0, chtr.level),
                    GloryOfGuardians, AuraWeaponBuff, AuraWeapon, globalSkill.soul_contract(), SelestialDanceInit, Elision, ElisionBreak,
                    ] +\
                [FlareSlash, CygnusPhalanx, SolunaDivide] +\
                [SelestialDanceSummon, SoulEclipse, MirrorBreak, MirrorSpider] +\
                [BasicAttackWrapper])