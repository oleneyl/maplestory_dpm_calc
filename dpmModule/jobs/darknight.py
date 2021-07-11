from ..kernel import core
from ..character import characterKernel as ck
from ..status.ability import Ability_tool
from . import globalSkill
from .jobbranch import warriors
from math import ceil
from typing import Any, Dict
import os

# TODO: 비홀더스 리벤지 메인 효과 추가


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.load(os.path.join(os.path.dirname(__file__), 'configs', 'darknight.json'))

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(boss_pdamage=60, armor_ignore=44)

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        창 사용
        크오체 풀피 가정
        비홀더 - 리인포스
        리인카네이션 - 데미지, 크리티컬 레이트
        궁그닐 - 리인포스, 이그노어 가드

        비홀더 임팩트 9타
        피어스 사이클론 25타
        다크 스피어 8히트

        임페일-궁그닐-비홀더-파이널어택

        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        HP_RATE = options.get("hp_rate", 100)
        self.passive_level = chtr.get_base_modifier().passive_level + self.combat

        # Buff skills

        Booster = self.load_skill_wrapper("부스터")
        CrossoverChain = self.load_skill_wrapper("크로스 오버 체인") 
        FinalAttack = self.load_skill_wrapper("파이널 어택", vEhc)
        BiholderDominant = self.load_skill_wrapper("비홀더 도미넌트", vEhc)
        BiholderShock = self.load_skill_wrapper("비홀더 쇼크", vEhc)

        DarkImpail = self.load_skill_wrapper("다크 임페일", vEhc)

        GoungnilDescent = self.load_skill_wrapper("궁그닐 디센트", vEhc)
        GoungnilDescentNoCooltime = self.load_skill_wrapper("궁그닐 디센트(무한)", vEhc)

        Sacrifice = self.load_skill_wrapper("새크리파이스")
        Reincarnation = self.load_skill_wrapper("리인카네이션")


        # 하이퍼
        DarkThurst = self.load_skill_wrapper("다크 서스트")
        EpicAdventure = self.load_skill_wrapper("에픽 어드벤처")
        
        # 5차
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        DarkSpear = self.load_skill_wrapper("다크 스피어", vEhc)
        BiholderImpact = self.load_skill_wrapper("비홀더 임팩트", vEhc)
        PierceCyclone = self.load_skill_wrapper("피어스 사이클론(더미)", vEhc)
        PierceCycloneTick = self.load_skill_wrapper("피어스 사이클론", vEhc)
        PierceCycloneEnd = self.load_skill_wrapper("피어스 사이클론(종료)", vEhc)

        DarknessAura = self.load_skill_wrapper("다크니스 오라", vEhc)
        DarknessAuraFinal = self.load_skill_wrapper("다크니스 오라(폭발)", vEhc)

        ######   Skill Wrapper   ######

        # Damage skill

        Reincarnation.set_disabled_and_time_left(30000)
        Reincarnation.onAfter(Reincarnation.controller(300*1000, 'reduce_cooltime'))

        def InfGoungnil():
            return (Sacrifice.is_active() or Reincarnation.is_active())

        DarkImpail.onAfter(FinalAttack)
        GoungnilDescentNoCooltime.onAfter(FinalAttack)
        GoungnilDescent.onAfter(FinalAttack)
        GoungnilDescent.onConstraint(core.ConstraintElement("새크리 OFF", Sacrifice, Sacrifice.is_not_active))
        GoungnilDescent.onConstraint(core.ConstraintElement("리인카 OFF", Reincarnation, Reincarnation.is_not_active))
        BasicAttack = core.OptionalElement(InfGoungnil, GoungnilDescentNoCooltime, DarkImpail)
        BasicAttackWrapped = core.DamageSkill('기본 공격', 0, 0, 0).wrap(core.DamageSkillWrapper)
        BasicAttackWrapped.onAfter(BasicAttack)
        BiholderDominant.onTick(Sacrifice.controller(300, 'reduce_cooltime'))
        BiholderShock.onAfter(Sacrifice.controller(300, 'reduce_cooltime'))
        BiholderImpact.onTick(Sacrifice.controller(300, 'reduce_cooltime'))

        PierceCycloneTick.onAfter(FinalAttack)
        PierceCycloneEnd.onAfter(core.RepeatElement(FinalAttack, 5))
        PierceCyclone_ = core.RepeatElement(PierceCycloneTick, 25)
        PierceCyclone_.onAfter(PierceCycloneEnd)
        PierceCyclone.onAfter(PierceCyclone_)

        DarknessAura.onEventEnd(DarknessAuraFinal)

        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 2, 1)
        for sk in [GoungnilDescent, GoungnilDescentNoCooltime, DarkImpail, PierceCycloneEnd]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()

        return(
            BasicAttackWrapped,
            [
                globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                Booster, CrossoverChain, Sacrifice, Reincarnation, EpicAdventure, DarkThurst, AuraWeaponBuff, AuraWeapon,
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()
            ]
            + [DarknessAura, DarknessAuraFinal, BiholderShock, GoungnilDescent, DarkSpear, PierceCyclone, MirrorBreak, MirrorSpider]
            + [BiholderDominant, BiholderImpact]
            + [BasicAttackWrapped]
        )
