import os

from typing import Any, Dict

from . import globalSkill
from ..kernel import core
from .jobclass import adventurer
from .jobbranch import magicians
from ..character import characterKernel
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, SynchronizeRule, InactiveRule, DisableRule


class PrayWrapper(core.BuffSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        super(PrayWrapper, self).__init__(core.BuffSkill("프레이", 360, 1000 * (30 + vEhc.getV(num1, num2) // 2), cooltime=180 * 1000, red=True).isV(vEhc, num1, num2))
        self.enable_referring_runtime_context()
        self.stat = None
        self.modifierInvariantFlag = False

    def _use(self, skill_modifier, runtime_context_modifier):
        self.stat = runtime_context_modifier.stat_main * (1 + 0.01 * runtime_context_modifier.pstat_main) + runtime_context_modifier.stat_main_fixed
        return super(PrayWrapper, self)._use(skill_modifier)

    def get_modifier(self):
        if self.is_active():
            return core.CharacterModifier(pdamage_indep=5 + min(self.stat // 2500, 45))
        else:
            return self.disabledModifier


class JobGenerator(characterKernel.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
<<<<<<< HEAD
        self.buffrem = (0, 40)
        self.jobtype = "INT"
        self.jobname = "비숍"
        self.vEnhanceNum = 8
=======
        self.load(os.path.join(os.path.dirname(__file__), 'configs', 'bishop.json'))
>>>>>>> Migrate to json
        self.ability_list = Ability_tool.get_ability_set('buff_rem', 'crit', 'boss_pdamage')

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(SynchronizeRule('소울 컨트랙트', '인피니티', 35000, -1), RuleSet.BASE)
        ruleset.add_rule(SynchronizeRule('프레이', '인피니티', 45000, -1), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('언스테이블 메모라이즈', '인피니티'), RuleSet.BASE)
        ruleset.add_rule(DisableRule('힐'), RuleSet.BASE)
        return ruleset

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=43)

    def get_passive_skill_list(self, vEhc, chtr : characterKernel.AbstractCharacter, options: Dict[str, Any]):
        default_list = super(JobGenerator, self).get_passive_skill_list(vEhc, chtr, options)
        UnstableMemorizePassive = adventurer.UnstableMemorizePassiveWrapper(vEhc, 4, 4)
        default_list += [UnstableMemorizePassive]

        return default_list

    def generate(self, vEhc, chtr : characterKernel.AbstractCharacter, options: Dict[str, Any]):
        '''리브라 ON
        서버렉 3초
        피스메이커 3히트

        언스테이블 메모라이즈는 인피니티가 꺼져있을때 사용
        프레이는 인피가 종료될 때 같이 종료되도록 맞추어서 사용
        소울 컨트랙트는 인피 마지막과 맞춰서 사용
        리브라는 쿨마다 사용
        '''
        # Buff skills
        Booster = self.load_skill_wrapper("부스터")
        AdvancedBless = self.load_skill_wrapper("어드밴스드 블레스")
        Heal = self.load_skill_wrapper("힐")
        Infinity = adventurer.InfinityWrapper(self.combat)
        EpicAdventure = self.load_skill_wrapper("에픽 어드벤처")

        Pray = PrayWrapper(vEhc, 2, 2)

        # Damage Skills
        AngelRay = self.load_skill_wrapper("엔젤레이", vEhc)

        HeavensDoor = self.load_skill_wrapper("헤븐즈도어")

        PeaceMakerInit = self.load_skill_wrapper("피스메이커(시전)", vEhc)
        PeaceMaker = self.load_skill_wrapper("피스메이커", vEhc)
        PeaceMakerFinal = self.load_skill_wrapper("피스메이커(폭발)", vEhc)
        PeaceMakerFinalBuff = self.load_skill_wrapper("피스메이커(버프)", vEhc)
        DivinePunishmentInit = self.load_skill_wrapper("디바인 퍼니시먼트(개시)", vEhc)
        DivinePunishmentTick = self.load_skill_wrapper("디바인 퍼니시먼트(키다운)", vEhc)

        # Summoning skill
        Bahamutt = self.load_skill_wrapper("바하뮤트", vEhc)  # 최종뎀25%스택, 리브라 종료시 자동소환 되므로 딜레이 0
        AngelOfLibra = self.load_skill_wrapper("엔젤 오브 리브라", vEhc)  # 최종뎀50%스택
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)

        # Unstable Memorize skills
        EnergyBolt = self.load_skill_wrapper("에너지 볼트")
        HolyArrow = self.load_skill_wrapper("홀리 애로우")
        ShiningRay = self.load_skill_wrapper("샤이닝 레이")
        HolyFountain = self.load_skill_wrapper("홀리 파운틴")
        Dispell = self.load_skill_wrapper("디스펠")
        DivineProtection = self.load_skill_wrapper("디바인 프로텍션")
        Genesis = self.load_skill_wrapper("제네시스")
        BigBang = self.load_skill_wrapper("빅뱅")
        Resurrection = self.load_skill_wrapper("리저렉션")

        VengenceOfAngel_Delay = self.load_skill_wrapper("벤전스 오브 엔젤(딜레이)")

        ######   Wrappers    ######
        # Unstable Memorize
        UnstableMemorize = adventurer.UnstableMemorizeWrapper(vEhc, 4, 4, chtr.get_skill_modifier())
        UnstableMemorize.onAfter(VengenceOfAngel_Delay)  # 벤전스 OFF(딜레이 0) - 언스테이블 - 벤전스 ON(딜레이 480)

        for sk, weight in [(EnergyBolt, 1), (HolyArrow, 10), (Heal, 10), (ShiningRay, 10),
                           (HolyFountain, 10), (Dispell, 25), (DivineProtection, 10), (AngelRay, 25), (Genesis, 25),
                           (BigBang, 25), (Resurrection, 25), (Infinity, 25), (Bahamutt, 25), (HeavensDoor, 10), (EpicAdventure, 10)]:
            UnstableMemorize.add_skill(sk, weight)

        # Sacred Mark Control
        SacredMark = core.StackSkillWrapper(core.BuffSkill("소환수 표식", 0, 999999 * 1000), 50)
        Bahamutt.onTick(SacredMark.stackController(25, name="표식(25%)", dtype="set"))
        AngelOfLibra.onTick(SacredMark.stackController(50, name="표식(50%)", dtype="set"))

        for sk in [HolyArrow, ShiningRay, Genesis, BigBang, AngelRay, PeaceMaker, PeaceMakerFinal, DivinePunishmentTick]:
            sk.onJustAfter(SacredMark.stackController(0, name="표식(소모)", dtype="set"))
            sk.add_runtime_modifier(SacredMark, lambda skill: core.CharacterModifier(pdamage_indep=skill.stack))

        # Peace Maker
        PeaceMakerRepeat = core.RepeatElement(PeaceMaker, self.conf["constant"]["PEACEMAKER_HIT"])
        PeaceMakerInit.onAfter(PeaceMakerRepeat)
        PeaceMakerRepeat.onAfter(PeaceMakerFinal)
        PeaceMakerFinal.onAfter(PeaceMakerFinalBuff)

        # Libra - Bahamutt exclusive
        AngelOfLibra.onAfter(Bahamutt.controller(1))
        Bahamutt.onConstraint(core.ConstraintElement("리브라와 동시사용 불가", AngelOfLibra, AngelOfLibra.is_not_active))

        # Divine Punishment
        DivinePunishmentInit.onAfter(core.RepeatElement(DivinePunishmentTick, 33))

        # Overload Mana
        overload_mana_builder = magicians.OverloadManaBuilder(vEhc, 1, 4)
        for sk in [AngelRay, Genesis, BigBang, HeavensDoor,
                   AngelOfLibra, PeaceMaker, PeaceMakerFinal, DivinePunishmentTick,
                   EnergyBolt, HolyArrow, ShiningRay]:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()

        return (AngelRay,
                [Booster, SacredMark, Infinity, PeaceMakerFinalBuff, Pray, EpicAdventure, OverloadMana,
                 globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_wind_booster(), AdvancedBless, Heal,
                 globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract(),
                 PeaceMakerInit,
                 AngelOfLibra, Bahamutt, HeavensDoor, DivinePunishmentInit, MirrorBreak, MirrorSpider,
                 UnstableMemorize,
                 AngelRay])
