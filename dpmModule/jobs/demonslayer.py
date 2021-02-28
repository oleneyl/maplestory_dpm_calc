from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule, InactiveRule
from . import globalSkill, jobutils
from .jobbranch import warriors
from .jobclass import demon
from . import jobutils
from math import ceil
from typing import Any, Dict

# TODO: 블블 100% 가정하는 중. 포스 사용을 반영해서 블블 지속시간 시뮬레이션(엄청 어려울듯)


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "STR"
        self.jobname = "데몬슬레이어"
        self.vEnhanceNum = 15
        self.preEmptiveSkills = 1
        self.hyperStatPrefixed = 85  # DF 8레벨 투자

        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'reuse', 'mess')

    def get_ruleset(self):
        '''딜 사이클 정리
        어웨이크닝 ON
        데몬 슬래시 + 데빌 크라이(이블 토쳐 유지)
        어웨이크닝 OFF
        데몬 임팩트 + 서버러스 + 데몬 슬래시 1타(리메인타임)

        나머지는 알아서 시전
        '''
        ruleset = RuleSet()
        ruleset.add_rule(InactiveRule('데몬 슬래시(1타)', '데몬 어웨이크닝'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('데몬 슬래시(1타)', '데몬 슬래시-리메인타임'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('서버러스', '데몬 어웨이크닝'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('데빌 크라이', '데몬 어웨이크닝'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('데몬 베인(개시)', '데몬 어웨이크닝'), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(crit=50, armor_ignore=50, pdamage=50)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        # 데몬스 퓨리 : 보공15%, 링크에 반영되므로 미고려.
        DeathCurse = core.InformedCharacterModifier("데스 커스", pdamage=1)
        Outrage = core.InformedCharacterModifier("아웃레이지", att=50, crit=20)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝", stat_main=30, stat_sub=30)
        Concentration = core.InformedCharacterModifier("컨센트레이션", pdamage_indep=25)
        AdvancedWeaponMastery = core.InformedCharacterModifier("어드밴스드 웨폰 마스터리", att=50+passive_level, crit_damage=15+passive_level//3)

        DarkBindPassive = core.InformedCharacterModifier("다크 바인드(패시브)", armor_ignore=30+self.combat)

        return [DeathCurse, Outrage, PhisicalTraining, Concentration, AdvancedWeaponMastery, DarkBindPassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep=20)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=90+ceil(passive_level/2))

        EvilTorture = core.InformedCharacterModifier("이블 토쳐", pdamage_indep=15, crit=15)  # 상태이상에 걸렸을때만.

        return [WeaponConstant, Mastery, EvilTorture]

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        코강 순서:
        슬래시-임팩트-서버-익스플로전-메타-데빌크라이

        데몬 베인은 어웨이크닝과 따로 사용

        ##### 하이퍼 #####
        # 데몬 슬래시 - 엑스트라 포스, 리인포스, 리메인타임 리인포스
        # 데몬 임팩트 - 리인포스, 보너스 어택
        '''
        buff_rem = chtr.get_base_modifier().buff_rem

        # Buff skills
        Booster = core.BuffSkill("부스터", 0, 180*1000, rem=True).wrap(core.BuffSkillWrapper)  # 펫버프

        # 뒤의 최종뎀 -10%는 리메인타임 패널티 / 최종뎀 43% = 최종강화 30% + 리인포스 10%
        DS_MODIFIER = core.CharacterModifier(pdamage=30+30, pdamage_indep=43) - core.CharacterModifier(pdamage_indep=10)
        AW_MODIFIER = DS_MODIFIER + core.CharacterModifier(armor_ignore=50, boss_pdamage=50)

        DemonSlashRemainTime = core.BuffSkill("데몬 슬래시-리메인타임", 0, 4000, cooltime=-1, pdamage_indep=10).wrap(core.BuffSkillWrapper)

        # 1타만 사용시 딜레이가 2타로 이어질때보다 김.
        DemonSlash1 = core.DamageSkill("데몬 슬래시(1타)", 390, 110+80, 2, modifier=DS_MODIFIER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        DemonSlashAW1 = core.DamageSkill("데몬 슬래시 강화(1타)", 270, 600+80, 3, modifier=AW_MODIFIER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        DemonSlashAW2 = core.DamageSkill("데몬 슬래시 강화(2타)", 270, 600+80, 3, modifier=AW_MODIFIER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        DemonSlashAW3 = core.DamageSkill("데몬 슬래시 강화(3타)", 360, 700+80, 3, modifier=AW_MODIFIER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        DemonSlashAW4 = core.DamageSkill("데몬 슬래시 강화(4타)", 360, 800+80, 3, modifier=AW_MODIFIER).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)

        DemonImpact = core.DamageSkill("데몬 임팩트", 660, 460+4*self.combat, 6+1, modifier=core.CharacterModifier(crit=100, armor_ignore=30+ceil(self.combat/3), boss_pdamage=40+self.combat, pdamage=20)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)

        DevilCry = core.DamageSkill("데빌 크라이", 990, 515+5*self.combat, 7, cooltime=20*1000).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)   # 이블 토쳐 위해 사용필수.
        DevilCryBuff = core.BuffSkill("데빌 크라이(위협)", 0, 20000, cooltime=-1, armor_ignore=15+self.combat//3).wrap(core.BuffSkillWrapper)

        InfinityForce = core.BuffSkill("인피니티 포스", 990, (50+10*(self.combat//5))*1000, cooltime=(200-self.combat)*1000, rem=True, red=True).wrap(core.BuffSkillWrapper)
        Metamorphosis = core.BuffSkill("메타모포시스", 1680, (180+4*self.combat)*1000, rem=True, pdamage=35+self.combat).wrap(core.BuffSkillWrapper)
        MetamorphosisSummon = core.SummonSkill("메타모포시스(소환)", 0, 510, 250+5*self.combat, 1, (180+4*self.combat)*(1+buff_rem/100)*1000, cooltime=-1).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)
        MetamorphosisSummon_BB = core.DamageSkill("메타모포시스(블블)", 0, (250+5*self.combat)*0.9, 1, cooltime=-1).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)

        # 블루블러드는 소환수 적용이 안됨.
        BlueBlood = core.BuffSkill("블루 블러드", 750, 60000, cooltime=120000-60000).wrap(core.BuffSkillWrapper)  # 모든 공격에 최종데미지의 90%로 추가타 발생. 포스50수급시 -3초, 인피니티 포스시 4초마다 2초 감소, 모든 스킬 포스소모량 20%감소.
        Cerberus = core.DamageSkill("서버러스", 690, 450, 6, cooltime=5000, modifier=core.CharacterModifier(boss_pdamage=50, armor_ignore=50)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)  # 포스50 추가흡수
        CerberusAuto = core.DamageSkill("서버러스(자동)", 0, 450, 6, cooltime=-1, modifier=core.CharacterModifier(boss_pdamage=50, armor_ignore=50)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)  # 포스50 추가흡수
        DemonFortitude = core.BuffSkill("데몬 포티튜드", 0, 60000, cooltime=120000).wrap(core.BuffSkillWrapper)

        CallMastema = demon.CallMastemaWrapper(vEhc, 4, 4)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        DemonAwakning = core.BuffSkill("데몬 어웨이크닝", 870, (35+vEhc.getV(0, 0))*1000, cooltime=120*1000, red=True, crit=(50+vEhc.getV(0, 0)//2)).isV(vEhc, 0, 0).wrap(core.BuffSkillWrapper)
        DemonAwakningSummon = core.SummonSkill("데몬 어웨이크닝(더미)", 0, 8000, 0, 0, (35+vEhc.getV(0, 0))*1000, cooltime=-1).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)

        SpiritOfRage = core.SummonSkill("요르문간드", 810, 1080, (850+34*vEhc.getV(3, 3)), 12, (10+vEhc.getV(3, 3)//5)*1000, cooltime=(120-vEhc.getV(3, 3)//2)*1000, red=True, modifier=core.CharacterModifier(crit=100, armor_ignore=50)).isV(vEhc, 3, 3).wrap(core.SummonSkillWrapper)
        SpiritOfRageEnd = core.DamageSkill("요르문간드(종료)", 0, 900+36*vEhc.getV(3, 3), 15, cooltime=-1).isV(vEhc, 3, 3).wrap(core.DamageSkillWrapper)
        Orthros = core.SummonSkill("오르트로스(네메아)", 510, 2000, 400+16*vEhc.getV(1, 1), 12, 40000, cooltime=120*1000, red=True, modifier=core.CharacterModifier(crit=100, armor_ignore=50)).isV(vEhc, 1, 1).wrap(core.SummonSkillWrapper)
        Orthros_ = core.SummonSkill("오르트로스(게리온)", 0, 3000, 900+36*vEhc.getV(1, 1), 10, 40000, cooltime=-1, modifier=core.CharacterModifier(crit=100, armor_ignore=50)).isV(vEhc, 1, 1).wrap(core.SummonSkillWrapper)

        DemonBaneInit = core.DamageSkill("데몬 베인(개시)", 240, 0, 0, cooltime=240*1000, red=True).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        DemonBaneTick = core.DamageSkill("데몬 베인(1)", 3760/16, 325+13*vEhc.getV(0, 0), 6, cooltime=-1, modifier=core.CharacterModifier(crit=50, armor_ignore=30)).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)  # 3760ms 16회
        DemonBane2Pre = core.DamageSkill("데몬 베인(2)(선딜)", 600, 0, 0, cooltime=-1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        DemonBane2Tick = core.DamageSkill("데몬 베인(2)", 2400/21, 650+26*vEhc.getV(0, 0), 7, cooltime=-1, modifier=core.CharacterModifier(crit=50, armor_ignore=30)).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)  # 2400ms 21회
        DemonBane2After = core.DamageSkill("데몬 베인(2)(후딜)", 240, 0, 0, cooltime=-1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)

        ######   Skill Wrapper   ######

        DemonSlashAW1.onAfter(DemonSlashAW2)
        DemonSlashAW2.onAfter(DemonSlashAW3)
        DemonSlashAW3.onAfter(DemonSlashAW4)

        BasicAttack = core.OptionalElement(DemonAwakning.is_active, DemonSlashAW1, DemonImpact, name="어웨이크닝 ON")
        BasicAttackWrapper = core.DamageSkill('기본 공격', 0, 0, 0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapper.onAfter(BasicAttack)

        DevilCry.onAfter(DevilCryBuff)

        DemonAwakning.onAfter(DemonAwakningSummon)
        DemonAwakningSummon.onTick(CerberusAuto)

        SpiritOfRage.onEventEnd(SpiritOfRageEnd)
        Orthros.onAfter(Orthros_)

        DemonBaneInit.onAfter(core.RepeatElement(DemonBaneTick, 16))
        DemonBaneInit.onAfter(DemonBane2Pre)
        DemonBaneInit.onAfter(core.RepeatElement(DemonBane2Tick, 21))
        DemonBaneInit.onAfter(DemonBane2After)

        Metamorphosis.onAfter(MetamorphosisSummon)
        MetamorphosisSummon.onTick(MetamorphosisSummon_BB)

        # 리메인타임
        # TODO: 리메인타임 ON일때만 데몬 슬래시 최종뎀 -10% 해야함. 현재 항상 적용중. add_runtime_modifier를 사용하면 블블 추가타에 적용이 안됨.
        for sk in [DemonSlashAW1, DemonSlashAW2, DemonSlashAW3, DemonSlashAW4, DemonSlash1]:
            sk.onAfter(DemonSlashRemainTime)

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 3, 2)
        for sk in [DemonSlashAW1, DemonSlashAW2, DemonSlashAW3, DemonSlashAW4, DevilCry, DemonImpact, Cerberus, DemonBaneTick, DemonBane2Tick]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        # 블블 추가타 적용
        for sk in [DemonSlashAW1, DemonSlashAW2, DemonSlashAW3, DemonSlashAW4, DemonImpact, DemonBaneTick, DemonBane2Tick, DevilCry, Cerberus, CerberusAuto, AuraWeapon]:
            jobutils.create_auxilary_attack(sk, 0.9, nametag='(블루 블러드)')

        return(BasicAttackWrapper,
               [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                Booster, DemonSlashRemainTime, DevilCryBuff, InfinityForce, Metamorphosis, BlueBlood, DemonFortitude, AuraWeaponBuff, AuraWeapon, DemonAwakning,
                *demon.AnotherWorldWrapper(vEhc, 0, 0), globalSkill.soul_contract()] +
               [Cerberus, DevilCry, DemonSlash1, SpiritOfRageEnd] +
               [MetamorphosisSummon, CallMastema, DemonAwakningSummon, SpiritOfRage, Orthros, Orthros_, DemonBaneInit, MirrorBreak, MirrorSpider] +
               [BasicAttackWrapper])
