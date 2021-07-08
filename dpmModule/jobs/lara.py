from ..kernel import core
from ..character import characterKernel as ck
from ..execution.rules import RuleSet
from ..status.ability import Ability_tool
from . import globalSkill, jobutils
from .jobclass import anima
from .jobbranch import magicians
from math import ceil
from typing import Any, Dict

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        ### Incomplete ###
        super(JobGenerator, self).__init__()
        self.jobtype = "INT"
        self.jobname = "라라"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'buff_rem', 'mess')  # TODO: 최적화 필요
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        ### Incomplete ###
        return core.CharacterModifier(armor_ignore=20, pdamage=40)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        ### Incomplete ###
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
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=95 + ceil(passive_level / 2))
        return [WeaponConstant, Mastery]

    
    def get_ruleset(self):
        ruleset = RuleSet()
        return ruleset


    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        """
        TODO: 하이퍼 패시브 분배, 딜사이클 작성
        """

        passive_level = chtr.get_base_modifier().passive_level + self.combat

        ### 1차 스킬 ###

        LaraAttack = core.DamageSkill("정기 뿌리기", 510, 80+50+160, 4).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        MountainAtack = core.DamageSkill("산 꼬마", 0, 105+45+160+5*passive_level, (0.4)*3, cooltime=-1).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)  # 오버로드 마나 미적용

        ### 2차 스킬 ###
        # TODO: 발현: 햇살 가득 안은 터 패시브 효과 확인필요
        # TODO: 최대 타격 후 종료해야 함
        Eruption = core.DamageSkill("용맥 분출", 0, 0, 0, 300).wrap(core.DamageSkillWrapper)  # TODO: 딜레이 확인, 소환수 지속시간 증가 미적용, 소환수 지속시간 증가 2%당 분출 스킬의 데미지 1% 증가
        Eruption_River = core.SummonSkill("분출 : 너울이는 강", 0, 2000, 215+120+128, 4+1, (8+1)*2000).setV(vEhc, 0, 2).wrap(core.SummonSkillWrapper)
        Eruption_Wind = core.SummonSkill("분출 : 돌개바람", 0, 3200, 63+35+152, 5, (8+1)*2000).setV(vEhc, 0, 2).wrap(core.SummonSkillWrapper)
        Eruption_Sun_Giant = core.DamageSkill("분출 : 해돋이 우물 (거인)", 0, 120+247, 6).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        Eruption_Sun = core.SummonSkill("분출 : 해돋이 우물", 0, 1000, 85+48+117, 1, (8+1)*2000).setV(vEhc, 0, 2).wrap(core.SummonSkillWrapper)
        Eruption_Sun_Bullet = core.DamageSkill("분출 : 해돋이 우물 (화산탄)", 0, 75+157, 3).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        Eruption_Sun_Bullet_2 = core.DamageSkill("분출 : 해돋이 우물 (화산탄 다중히트)", 0, (75+157)*0.9, 3*4).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        Eruption_Sun_DOT = core.DotSkill("분출 : 해돋이 우물 (도트)", 0, 1000, 60+50, 1, 8*1000).setV(vEhc, 0, 2).wrap(core.SummonSkillWrapper)

        MountainSeed = core.StackableSummonSkillWrapper(
            core.SummonSkill("산의 씨앗", 0, 1000, 55+75+170+5*passive_level, 1, 10000+20000).setV(vEhc, 0, 2).wrap(core.SummonSkillWrapper),  # TODO: 공격 주기 확인
            max_stack=4
        )

        Booster = core.BuffSkill("지팡이 가속", 0, 180000).wrap(core.BuffSkillWrapper)

        ### 3차 스킬 ###
        Expression_Wind = core.BuffSkill("발현 : 바람 그네", 720, 20000+60000).wrap(core.BuffSkillWrapper)  # TODO: 재진입시 지속시간 초기화 여부 확인
        Expression_Sun = core.BuffSkill("발현 : 햇살 가득 안은 터", 690, 20000+60000, pdamage=15).wrap(core.BuffSkillWrapper)  # TODO: 해돋이 우물 데미지 증가 패시브 적용해야 함, 적용 범위 확인필요
        WakeUp = core.DamageSkill("잠 깨우기", 540, 105+160+5*passive_level, 4, cooltime=11000).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        WakeUp_Add = core.DamageSkill("잠 깨우기(추가타)", 540, (105+160+5*passive_level)*0.6, 4*(6+9)/2, cooltime=-1).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)  # 추가타: 6~9회
        TrackTeleport = core.DamageSkill("용맥의 자취", 90, 500+55+2*passive_level, 2, cooltime=6000).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        Echo = core.BuffSkill("용맥의 메아리", 0, 20000, pdamage_indep=5, red=False).wrap(core.BuffSkillWrapper)  # TODO: 용맥 구현 필요

        ### 4차 스킬 ###
        Absorption = core.DamageSkill("용맥 흡수", 0, 0, 0, 300).wrap(core.DamageSkillWrapper)  # TODO: 딜레이 확인
        Absorption_River_Buff = core.BuffSkill("흡수 : 강 웅덩이 물벼락 (버프)", 0, (45+self.combat)*1000).wrap(core.BuffSkillWrapper)
        Absorption_River = core.DamageSkill("흡수 : 강 웅덩이 물벼락", 0, 450+self.combat, 6, 2500).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        Absorption_Wind_Buff = core.BuffSkill("흡수 : 소소리 바람 (버프)", 0, (45+self.combat)*1000).wrap(core.BuffSkillWrapper)
        Absorption_Wind = core.DamageSkill("흡수 : 소소리 바람", 0, 195+2*self.combat, 2, 2500).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        Absorption_Sun_Buff = core.BuffSkill("흡수 : 햇빛 맹아리 (버프)", 0, (45+self.combat)*1000).wrap(core.BuffSkillWrapper)
        Absorption_Sun = core.DamageSkill("흡수 : 햇빛 맹아리", 0, 180+5*self.combat, 5*6, 2500).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)

        Switch = core.DamageSkill("용맥 변환", 0, 0, 0, 3000).wrap(core.DamageSkillWrapper)
        Eruption_River_Enhanced = core.DamageSkill("분출 : 너울이는 강 (큰 너울)", 0, 530, 8).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)  # TODO: 일반 너울 스킬과 동기화

        ### 하이퍼 액티브 ###
        TangledVine = core.DamageSkill("넝쿨 타래", 840, 700, 6, 180*1000).setV(vEhc, 0, 2).wrap(core.DamageSkillWrapper)
        ArtificialEarthVein = core.StackableDamageSkillWrapper(core.DamageSkill("자유로운 용맥", 300, 0, 0, 1500), 3)
        HomeOfSpirits = core.BuffSkill("아름드리 나무", 660, 30000, 180*1000, armor_ignore=15, boss_pdamage=30, crit_damage=10).wrap(core.BuffSkillWrapper)

        ### V Skills ###
        OverloadMana = magicians.OverloadManaBuilder(vEhc, 0, 0)
        AnimaGoddessBless = anima.AnimaGoddessBlessWrapper(vEhc, 0, 0)  # TODO: 용맥의 메아리 발동시 최종데미지 증가효과 구현

        BigEruption = core.DamageSkill("큰 기지개", 870, 500+20*vEhc.getV(0, 0), 5*1*5, 60000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        BigEruption_Add = core.DamageSkill("큰 기지개 (추가타)", 0, (500+20*vEhc.getV(0, 0))*0.7, 5*(7-1)*5, -1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        CombinationBlow = core.DamageSkill("해 강 산 바람", 840, 0, 0, 180*1000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        CombinationBlow_Spirit = core.DamageSkill("해 강 산 바람 (토지령)", 0, 800+32*vEhc.getV(0, 0), 10*3, -1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        CombinationBlow_Explosion = core.DamageSkill("해 강 산 바람 (폭발)", 0, 1000+40*vEhc.getV(0, 0), 15*7, -1).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        AdvancedLaraAttack = core.DamageSkill("용솟음치는 정기", 630, 425+17*vEhc.getV(0, 0), 8*5, 20000).isV(vEhc, 0, 0).wrap(core.DamageSkillWrapper)
        BurstUp = core.SummonSkill("산등성이 굽이굽이", 960, 500, 250+10*vEhc.getV(0, 0), 3*4, 500*20).isV(vEhc, 0, 0).wrap(core.SummonSkillWrapper)
        overload_mana_builder = magicians.OverloadManaBuilder(vEhc, 1, 5)

        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        ### TODO: Skill Wrapper ###

        # Overload Mana
        
        for sk in []:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()

        return (
            LaraAttack,
            [
                globalSkill.maple_heros(chtr.level, name="아니마의 용사", combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                globalSkill.soul_contract()
            ]
            + []
            + []
            + [LaraAttack]
        )
