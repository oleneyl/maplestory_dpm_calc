from ..kernel import core
from ..character import characterKernel as ck
from ..execution.rules import RuleSet
from ..status.ability import Ability_tool
from . import globalSkill, jobutils
from .jobclass import anima
from .jobbranch import magicians
from math import ceil
from typing import Any, Dict

'''
References
https://m.blog.naver.com/oe135/222414521675
https://m.blog.naver.com/oe135/222425101153
'''


class EchoWrapper(core.BuffSkillWrapper):
    def __init__(self, anima_goddess, vlevel):
        super(EchoWrapper, self).__init__(core.BuffSkill("용맥의 메아리", 0, 20000, -1, red=False))
        #self.set_name_style("+%d")
        self.anima_goddess = anima_goddess
        self.extra = 1 + vlevel // 6

    def get_modifier(self):  # 그란디스 여신의 축복 활성화시 용맥의 메아리 최종데미지 증가 (기본 6% + 6레벨당 1%)
        return core.CharacterModifier(pdamage_indep=5 + self.extra * self.anima_goddess.is_active())


class RiverWrapper(core.SummonSkillWrapper):
    def __init__(self, skill):
        super(RiverWrapper, self).__init__(skill)

    def _useTick(self) -> core.ResultObject:
        self.tick += self.get_delay()
        if (self.tick // self.get_delay()) % 3 == 2:  # TODO: 큰 너울 최초 발동 타이밍 확인필요
            return core.ResultObject(
                0,
                self.get_modifier(),
                580,
                8,
                sname="분출 : 너울이는 강 (큰 너울)",
                spec=self.skill.spec,
            )
        return core.ResultObject(
            0,
            self.get_modifier(),
            215 + 120 + 128,
            4 + 1,
            sname="분출 : 너울이는 강 (너울)",
            spec=self.skill.spec,
        )


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        ### Incomplete ###
        super(JobGenerator, self).__init__()
        self.jobtype = "INT"
        self.jobname = "라라"
        self.ability_list = Ability_tool.get_ability_set('passive_level', 'boss_pdamage', 'mess')  # TODO: 최적화 필요
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        ### Incomplete ###
        return core.CharacterModifier(armor_ignore=20, pdamage=40)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        SpiritAffinity = core.InformedCharacterModifier("정령친화", summon_rem=10)
        WandMastery = core.InformedCharacterModifier("지팡이 숙련", att=35)
        PhysicalTraining = core.InformedCharacterModifier("신체 단련", stat_main=40)
        Exercise = core.InformedCharacterModifier("무구", pdamage=20, crit=20, boss_pdamage=10)
        WandExpert = core.InformedCharacterModifier("고급 지팡이 숙련", att=50+passive_level, pdamage_indep=30+passive_level//2)
        Insight = core.InformedCharacterModifier("혜안", crit=20+passive_level, crit_damage=20+passive_level, pdamage_indep=45+passive_level, armor_ignore=40+passive_level)
        Relaxation = core.InformedCharacterModifier("유유", att=50+2*passive_level)
        return [SpiritAffinity, WandMastery, PhysicalTraining, Exercise, WandExpert, Insight, Relaxation]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=95 + ceil(passive_level / 2))
        return [WeaponConstant, Mastery]

    
    def get_ruleset(self):
        ruleset = RuleSet()
        return ruleset


    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        """
        TODO: 딜사이클 작성
        분출 : 너울이는 강, 분출 : 돌개바람, 흡수 : 햇빛 맹아리

        분출/흡수 - 리인포스
        분출/흡수 - 보스 킬러
        정기 뿌리기 - 보스 킬러
        산 에움 - 엑스트라 실드
        잠 깨우기 - 쿨타임 리듀스
        """

        HYPER_MODIFIER = core.CharacterModifier(pdamage=10, boss_pdamage=15)

        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ### 1차 스킬 ###

        LaraAttack = core.DamageSkill("정기 뿌리기", 510, 80+50+175, 4, modifier=core.CharacterModifier(boss_pdamage=15)).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        MountainKid = core.DamageSkill("산 꼬마", 0, 105+45+160+5*passive_level, (0.4+0.3)*3, cooltime=-1).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)  # 오버로드 마나 미적용

        ### 2차 스킬 ###
        # TODO: 최대 타격 후 종료해야 함
        ERUPTION_MODIFIER = HYPER_MODIFIER + core.CharacterModifier(pdamage=chtr.get_base_modifier().summon_rem//2)
        Eruption = core.DamageSkill("용맥 분출", 450, 0, 0, 300).wrap(core.DamageSkillWrapper)
        Eruption_River = RiverWrapper(core.SummonSkill("분출 : 너울이는 강", 0, 2000, 0, 0, (8+1)*2000, rem=False, modifier=ERUPTION_MODIFIER).setV(vEhc, 0, 2))
        Eruption_Wind = core.SummonSkill("분출 : 돌개바람", 0, 480, 63+35+157, 5, 10000, rem=False, modifier=ERUPTION_MODIFIER).setV(vEhc, 0, 2).wrap(core.SummonSkillWrapper)  # 최대 5회 생성
        Eruption_Sun_Giant = core.DamageSkill("분출 : 해돋이 우물 (거인)", 0, 120+48+247, 6, modifier=ERUPTION_MODIFIER).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        Eruption_Sun = core.SummonSkill("분출 : 해돋이 우물", 0, 1000, 85+48+117, 1, (8+1)*2000, rem=False, modifier=ERUPTION_MODIFIER).setV(vEhc, 0, 2).wrap(core.SummonSkillWrapper)
        Eruption_Sun_Bullet = core.DamageSkill("분출 : 해돋이 우물 (화산탄)", 0, 75+48+157, 3, modifier=ERUPTION_MODIFIER).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        Eruption_Sun_Bullet_2 = core.DamageSkill("분출 : 해돋이 우물 (화산탄 다중히트)", 0, (75+48+157)*0.9, 3*4, modifier=ERUPTION_MODIFIER).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        Eruption_Sun_DOT = core.DotSkill("분출 : 해돋이 우물 (도트)", 0, 1000, 60+48+50, 1, 8*1000).setV(vEhc, 0, 2).wrap(core.SummonSkillWrapper)  # TODO: 소환수 지속시간 -> 데미지 증가 적용여부 확인필요

        # 자동 시전 모드
        # TODO: 정확한 수치 확인필요
        MountainSeed = core.StackableSummonSkillWrapper(
            core.SummonSkill("산의 씨앗", 0, 2000, 55+75+170+5*passive_level, 1, 10000+20000, 7000).setV(vEhc, 0, 2).wrap(core.SummonSkillWrapper),  # TODO: 공격 주기 확인
            max_stack=4
        )

        Booster = core.BuffSkill("지팡이 가속", 0, 180000).wrap(core.BuffSkillWrapper)

        ### 3차 스킬 ###
        Expression_Wind = core.BuffSkill("발현 : 바람 그네", 720, 20000+60000).wrap(core.BuffSkillWrapper)
        Expression_Sun = core.BuffSkill("발현 : 햇살 가득 안은 터", 690, 20000+60000, pdamage=25).wrap(core.BuffSkillWrapper)
        WakeUp = core.DamageSkill("잠 깨우기", 540, 105+45+passive_level, 4, cooltime=11000*0.8).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)  # 하이퍼 쿨감 20% 감소
        WakeUp_Add = core.DamageSkill("잠 깨우기(추가타)", 540, (105+45+passive_level)*0.6, 4*(6+9)/2, cooltime=-1).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)  # 추가타: 6~9회
        TrackTeleport = core.DamageSkill("용맥의 자취", 90, 500+55+2*passive_level, 2, cooltime=6000).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)

        ### 4차 스킬 ###
        Absorption = core.DamageSkill("용맥 흡수", 300, 0, 0, 300).wrap(core.DamageSkillWrapper)
        Absorption_River_Buff = core.BuffSkill("흡수 : 강 웅덩이 물벼락 (버프)", 0, (60+self.combat)*1000).wrap(core.BuffSkillWrapper)
        Absorption_River = core.DamageSkill("흡수 : 강 웅덩이 물벼락", 0, 500+self.combat, 6, 2500, modifier=HYPER_MODIFIER).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        Absorption_Wind_Buff = core.BuffSkill("흡수 : 소소리 바람 (버프)", 0, (60+self.combat)*1000).wrap(core.BuffSkillWrapper)
        Absorption_Wind = core.DamageSkill("흡수 : 소소리 바람", 0, 215+2*self.combat, 2, 2500, modifier=HYPER_MODIFIER).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        Absorption_Sun_Buff = core.BuffSkill("흡수 : 햇빛 맹아리 (버프)", 0, (45+self.combat)*1000).wrap(core.BuffSkillWrapper)
        Absorption_Sun = core.DamageSkill("흡수 : 햇빛 맹아리", 0, 200+5*self.combat, 5*6, 2500, modifier=HYPER_MODIFIER).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)

        Switch = core.DamageSkill("용맥 변환", 240, 0, 0, 3000+7000).wrap(core.DamageSkillWrapper)  # 성공시 쿨타임 10초

        ### 하이퍼 액티브 ###
        FreeDragonVein = core.StackableDamageSkillWrapper(core.DamageSkill("자유로운 용맥", 240, 0, 0, 1500), 3)
        TangledVine = core.DamageSkill("넝쿨 타래", 840, 700, 6, 180*1000).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        HomeOfSpirits = core.BuffSkill("아름드리 나무", 660, 30000, 180*1000, armor_ignore=15, boss_pdamage=30, crit_damage=10).wrap(core.BuffSkillWrapper)

        ### V Skills ###
        AnimaGoddessBless = anima.AnimaGoddessBlessWrapper(vEhc, 0, 0)

        BigEruption = core.DamageSkill("큰 기지개", 870, 500+20*vEhc.getV(0, 0), 5*1*5, 60000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        BigEruption_Add = core.DamageSkill("큰 기지개 (추가타)", 0, (500+20*vEhc.getV(0, 0))*0.7, 5*(7-1)*5, -1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        CombinationBlow = core.DamageSkill("해 강 산 바람", 840, 0, 0, 180*1000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        CombinationBlow_Spirit = core.DamageSkill("해 강 산 바람 (토지령)", 0, 700+28*vEhc.getV(0, 0), 10*3, -1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        CombinationBlow_Explosion = core.DamageSkill("해 강 산 바람 (폭발)", 0, 850+34*vEhc.getV(0, 0), 15*7, -1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        AdvancedLaraAttack = core.DamageSkill("용솟음치는 정기", 630, 425+17*vEhc.getV(0, 0), 8*5, 20000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        BURSTUP_DELAY = 390  # 무릉 뒷마당 평균 딜레이 390ms로 추정
        BurstUp = core.SummonSkill("산등성이 굽이굽이", 960, BURSTUP_DELAY, 250+10*vEhc.getV(0, 0), 3*4, BURSTUP_DELAY*20).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)

        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        ### TODO: Skill Wrapper ###

        # 평타
        LaraAttack.onAfter(MountainKid)
        WakeUp.onAfter(WakeUp_Add)

        # 극딜 순서: 해 강 산 바람->산등성이 굽이굽이->큰 기지개->용솟음치는 정기
        CombinationBlow.onAfter(CombinationBlow_Spirit)
        CombinationBlow_Spirit.onAfter(CombinationBlow_Explosion)
        BigEruption.onAfter(core.RepeatElement(BigEruption_Add, 4))

        # 메아리
        Echo = EchoWrapper(AnimaGoddessBless, vEhc.getV(0, 0))
        Eruption.onAfter(Echo)
        Absorption.onAfter(Echo)
        
        # 분출
        Eruption_River.onBefore(Eruption)
        Eruption_Wind.onBefore(Eruption)
        Eruption_Sun.onBefore(Eruption)

        Eruption_Sun.onAfter(Eruption_Sun_Giant)
        Eruption_Sun.onTick(Eruption_Sun_Bullet)
        Eruption_Sun.onTick(Eruption_Sun_Bullet_2)
        Eruption_Sun_Bullet.onAfter(Eruption_Sun_DOT)
        
        # 흡수
        Absorption_Sun.onBefore(Absorption)
        Absorption_River.onBefore(Absorption)
        Absorption_Wind.onBefore(Absorption)

        LaraAttack.onAfter(core.OptionalElement(Absorption_Sun_Buff.is_active, Absorption_Sun))
        LaraAttack.onAfter(core.OptionalElement(Absorption_River_Buff.is_active, Absorption_River))
        LaraAttack.onAfter(core.OptionalElement(Absorption_Wind_Buff.is_active, Absorption_Wind))

        # TODO: Overload Mana (스인미 제외)

        overload_mana_builder = magicians.OverloadManaBuilder(vEhc, 1, 5)
        for sk in [LaraAttack, MountainKid, Eruption_River, Eruption_Wind, Eruption_Sun,
                   Eruption_Sun_Giant, Eruption_Sun_Bullet, Eruption_Sun_Bullet_2,
                   MountainSeed, WakeUp, WakeUp_Add, Absorption_Sun, Absorption_Wind, Absorption_River,
                   TangledVine, BigEruption, BigEruption_Add, CombinationBlow_Spirit, CombinationBlow_Explosion,
                   AdvancedLaraAttack, BurstUp]:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()

        return (
            LaraAttack,
            [
                Booster,
                OverloadMana,
                Expression_Wind,
                Expression_Sun,
                globalSkill.maple_heros(chtr.level, name="아니마의 용사", combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                TangledVine,
                HomeOfSpirits,
                globalSkill.soul_contract(),
                AnimaGoddessBless,
                CombinationBlow,
                BurstUp,
                BigEruption,
                AdvancedLaraAttack,
            ]
            + [WakeUp, MountainKid, Eruption_River, Eruption_Wind, Absorption_Sun_Buff]
            + [MirrorBreak, MirrorSpider, MountainSeed]
            + [LaraAttack]
        )
