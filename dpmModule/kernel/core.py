import math
from collections import defaultdict
from functools import partial
from typing import Any, Callable, Dict, Optional, List, Tuple, Union

from .abstract import AbstractVEnhancer, AbstractVBuilder
from .graph import EvaluativeGraphElement, DynamicVariableOperation, DynamicVariableInstance, \
    AbstractDynamicVariableInstance

NOTWANTTOEXECUTE = 99999999
MAX_DAMAGE_RESTRICTION = 10000 * 10000 * 100


def infinite_time() -> int:
    return NOTWANTTOEXECUTE


class CharacterModifier:
    __slots__ = 'crit', 'crit_damage', 'pdamage', 'pdamage_indep', 'stat_main', 'stat_sub', 'pstat_main', 'pstat_sub', 'boss_pdamage', 'armor_ignore', 'patt', 'att', 'stat_main_fixed', 'stat_sub_fixed'
    '''CharacterModifier : Holds information about character modifiing factors ex ) pdamage, stat, att%, etc.AbstractSkill
    - parameters
      
      .crit : Additional critical value
      .crit_damage : Critical damage increment %
      
      .pdamage : Damage increment %
      .pdamage_indep : Total Damage Increment %.
      
      .stat_main : Main stat increment
      .stat_sub : Sub stat increment
      
      .stat_main : Main stat increment %
      .stat_sub : Sub stat increment %
      
      .boss_pdamage : Boss Attack Damage increment%
      .armor_ignore : Armor Ignorance %
      
      .att : AD increment
      .patt : AD increment %
      
      * Additional parameters can be involved with inherit this class.  
    
    '''

    def __init__(self, crit: float = 0, crit_damage: float = 0, pdamage: float = 0, pdamage_indep: float = 0,
                 stat_main: float = 0, stat_sub: float = 0, pstat_main: float = 0, pstat_sub: float = 0,
                 boss_pdamage: float = 0, armor_ignore: float = 0, patt: float = 0, att: float = 0,
                 stat_main_fixed: float = 0, stat_sub_fixed: float = 0) -> None:
        self.crit: float = crit
        self.crit_damage: float = crit_damage

        self.pdamage: float = pdamage
        self.pdamage_indep: float = pdamage_indep

        self.stat_main: float = stat_main
        self.stat_sub: float = stat_sub

        self.pstat_sub: float = pstat_sub
        self.pstat_main: float = pstat_main

        self.boss_pdamage: float = boss_pdamage
        self.armor_ignore: float = armor_ignore

        self.att: float = att
        self.patt: float = patt

        self.stat_main_fixed: float = stat_main_fixed
        self.stat_sub_fixed: float = stat_sub_fixed

    def __iadd__(self, arg: 'CharacterModifier') -> 'CharacterModifier':
        self.crit += arg.crit
        self.crit_damage += arg.crit_damage
        self.pdamage += arg.pdamage
        self.pdamage_indep += arg.pdamage_indep + (self.pdamage_indep * arg.pdamage_indep) * 0.01
        self.stat_main += arg.stat_main
        self.stat_sub += arg.stat_sub
        self.pstat_main += arg.pstat_main
        self.pstat_sub += arg.pstat_sub
        self.boss_pdamage += arg.boss_pdamage
        self.armor_ignore = 100 - 0.01 * ((100 - self.armor_ignore) * (100 - arg.armor_ignore))
        self.patt += arg.patt
        self.att += arg.att
        self.stat_main_fixed += arg.stat_main_fixed
        self.stat_sub_fixed += arg.stat_sub_fixed
        return self

    def __add__(self, arg: 'CharacterModifier') -> 'CharacterModifier':
        return CharacterModifier(crit=(self.crit + arg.crit),
                                 crit_damage=(self.crit_damage + arg.crit_damage),
                                 pdamage=(self.pdamage + arg.pdamage),
                                 pdamage_indep=self.pdamage_indep + arg.pdamage_indep + (self.pdamage_indep * arg.pdamage_indep) * 0.01,
                                 stat_main=(self.stat_main + arg.stat_main),
                                 stat_sub=(self.stat_sub + arg.stat_sub),
                                 pstat_main=(self.pstat_main + arg.pstat_main),
                                 pstat_sub=(self.pstat_sub + arg.pstat_sub),
                                 boss_pdamage=(self.boss_pdamage + arg.boss_pdamage),
                                 armor_ignore=100 - 0.01 * ((100 - self.armor_ignore) * (100 - arg.armor_ignore)),
                                 patt=(self.patt + arg.patt), att=(self.att + arg.att),
                                 stat_main_fixed=(self.stat_main_fixed + arg.stat_main_fixed),
                                 stat_sub_fixed=(self.stat_sub_fixed + arg.stat_sub_fixed))

    def __sub__(self, arg: 'CharacterModifier') -> 'CharacterModifier':
        return CharacterModifier(crit=(self.crit - arg.crit),
                                 crit_damage=(self.crit_damage - arg.crit_damage),
                                 pdamage=(self.pdamage - arg.pdamage),
                                 pdamage_indep=(100 + self.pdamage_indep) / (100 + arg.pdamage_indep) * 100 - 100,
                                 stat_main=(self.stat_main - arg.stat_main),
                                 stat_sub=(self.stat_sub - arg.stat_sub),
                                 pstat_main=(self.pstat_main - arg.pstat_main),
                                 pstat_sub=(self.pstat_sub - arg.pstat_sub),
                                 boss_pdamage=(self.boss_pdamage - arg.boss_pdamage),
                                 armor_ignore=100 - 100 * (100 - self.armor_ignore) / (100 - arg.armor_ignore),
                                 patt=(self.patt - arg.patt), att=(self.att - arg.att),
                                 stat_main_fixed=(self.stat_main_fixed - arg.stat_main_fixed),
                                 stat_sub_fixed=(self.stat_sub_fixed - arg.stat_sub_fixed))

    def copy(self) -> 'CharacterModifier':
        return CharacterModifier(crit=self.crit,
                                 crit_damage=self.crit_damage,
                                 pdamage=self.pdamage,
                                 pdamage_indep=self.pdamage_indep,
                                 stat_main=self.stat_main,
                                 stat_sub=self.stat_sub,
                                 pstat_main=self.pstat_main,
                                 pstat_sub=self.pstat_sub,
                                 boss_pdamage=self.boss_pdamage,
                                 armor_ignore=self.armor_ignore,
                                 patt=self.patt,
                                 att=self.att,
                                 stat_main_fixed=self.stat_main_fixed,
                                 stat_sub_fixed=self.stat_sub_fixed)

    def extend(self) -> 'ExtendedCharacterModifier':
        return ExtendedCharacterModifier(crit=self.crit,
                                         crit_damage=self.crit_damage,
                                         pdamage=self.pdamage,
                                         pdamage_indep=self.pdamage_indep,
                                         stat_main=self.stat_main,
                                         stat_sub=self.stat_sub,
                                         pstat_main=self.pstat_main,
                                         pstat_sub=self.pstat_sub,
                                         boss_pdamage=self.boss_pdamage,
                                         armor_ignore=self.armor_ignore,
                                         patt=self.patt,
                                         att=self.att,
                                         stat_main_fixed=self.stat_main_fixed,
                                         stat_sub_fixed=self.stat_sub_fixed)

    def get_damage_factor(self, armor: int = 300) -> float:
        """Caution : Use this function only if you summed up every modifiers.
        """
        real_crit = min(100, self.crit)
        stat = (4 * self.stat_main * (1 + 0.01 * self.pstat_main) + self.stat_sub * (1 + 0.01 * self.pstat_sub)) + (4 * self.stat_main_fixed + self.stat_sub_fixed)
        adap = self.att * (1 + 0.01 * self.patt)
        factor = (1 + 0.0001 * max(0, real_crit) * (self.crit_damage + 35)) * (1 + 0.01 * (max(self.pdamage + self.boss_pdamage, 0))) * (1 + 0.01 * self.pdamage_indep)
        ignorance = max((100 - armor * (1 - 0.01 * self.armor_ignore)) * 0.01, 0)
        return stat * adap * factor * ignorance * 0.01

    # TODO: Parameter armor is not used.
    def get_status_factor(self, armor: int = 300) -> float:
        """Caution : Use this function only if you summed up every modifiers.
        """
        stat = (4 * self.stat_main * (1 + 0.01 * self.pstat_main) + self.stat_sub * (1 + 0.01 * self.pstat_sub)) + (4 * self.stat_main_fixed + self.stat_sub_fixed)
        adap = self.att * (1 + 0.01 * self.patt)
        factor = (1 + 0.01 * self.pdamage) * (1 + 0.01 * self.pdamage_indep)
        return stat * adap * factor * 0.01

    def calculate_damage(self, damage: int, hit: int, spec: str, armor: int = 300) -> Tuple[float, float]:
        """Return : (damage, loss) tuple
        숙련도는 90~100으로 가정함(5% deviation)
        """

        def restricted_damage(x1: float, x2: float, y1: float, y2: float, M: float) -> float:
            """Calculated expected value of min(M, xy) in [x1~x2, y1~y2]
            """
            normalizer = (x2 - x1) * (y2 - y1)
            basis = (x1 + x2) / 2 * (y1 + y2) / 2

            if M > x2 * y2:
                return basis
            else:
                if M > x1 * y2 and M > x2 * y1:
                    x_p = M / y2
                    # Case 1
                    excess = M * y2 * (x2 - x_p) - (y2 * y2 / 4) * (x2 * x2 - x_p * x_p) - (M * M / 2) * math.log(x2 / x_p)
                    return basis + excess / normalizer

                elif x1 * y2 > M > x2 * y1:
                    # Case 2
                    x_p = x1
                    # Case 1
                    excess = M * y2 * (x2 - x_p) - (y2 * y2 / 4) * (x2 * x2 - x_p * x_p) - (M * M / 2) * math.log(x2 / x_p)
                    return basis + excess / normalizer

                elif x1 * y2 < M < x2 * y1:
                    # Case 3 -> change to Case 2
                    return restricted_damage(y1, y2, x1, x2, M)

                elif M > x1 * y1:
                    x_p = M / y1
                    excess = M * y1 * (x_p - x1) - (y1 * y1 / 4) * (x_p * x_p - x1 * x1) - (M * M / 2) * math.log(x_p / x1)
                    return M + excess / normalizer

                else:
                    return M

        # Optimized
        real_crit = min(100, self.crit)
        stat = (4 * self.stat_main * (1 + 0.01 * self.pstat_main) + self.stat_sub * (1 + 0.01 * self.pstat_sub)) + (4 * self.stat_main_fixed + self.stat_sub_fixed)
        adap = self.att * (1 + 0.01 * self.patt)
        factor_crit_removed = (1 + 0.01 * (max(self.pdamage + self.boss_pdamage, 0))) * (1 + 0.01 * self.pdamage_indep)
        ignorance = max((100 - armor * (1 - 0.01 * self.armor_ignore)) * 0.01, 0)
        expert_max = 100 / 95
        expert_min = 90 / 95

        if spec == "dot":
            real_crit = 0
            factor_crit_removed = 1
            ignorance = 1
            expert_min = expert_max

        factor_aggregated = stat * adap * factor_crit_removed * ignorance * damage * 0.0001

        max_crit_factor = (1 + 0.0001 * max(0, real_crit) * (self.crit_damage + 50))
        min_crit_factor = (1 + 0.0001 * max(0, real_crit) * (self.crit_damage + 20))

        max_damage_factor = factor_aggregated * expert_max
        min_damage_factor = factor_aggregated * expert_min

        real_damage = hit * (max_crit_factor + min_crit_factor) / 2 * (
                    max_damage_factor + min_damage_factor) / 2  # W/O restriction
        res_damage = hit * restricted_damage(min_damage_factor, max_damage_factor, min_crit_factor, max_crit_factor, MAX_DAMAGE_RESTRICTION)  # W/ restriction

        return (res_damage, real_damage - res_damage)

    def log(self) -> str:
        txt = "crit rate : %.1f, crit damage : %.1f\n" % (self.crit, self.crit_damage)
        txt += "pdamage : %.1f, pdamage_indep : %.1f\n" % (self.pdamage, self.pdamage_indep)
        txt += "stat_main : %.1f, stat_sub : %.1f\n" % (self.stat_main, self.stat_sub)
        txt += "pstat_main : %.1f, pstat_sub : %.1f\n" % (self.pstat_main, self.pstat_sub)
        txt += "stat_main_fixed : %.1f, stat_sub_fixed : %.1f\n" % (self.stat_main_fixed, self.stat_sub_fixed)
        txt += "boss_pdamage : %.1f, armor_ignore : %.1f\n" % (self.boss_pdamage, self.armor_ignore)
        txt += "att : %.1f, patt : %.1f\n" % (self.att, self.patt)
        txt += "damageFactor : %.1f\n" % (self.get_damage_factor())
        return txt

    def __repr__(self) -> str:
        return self.log()

    def abstract_log_list(self, lang: str = "ko") -> List[Tuple[str, float, Optional[str]]]:
        crit_rate_formal = (math.floor(self.crit * 10)) / 10
        if crit_rate_formal < 0:
            crit_rate_formal = "미발동"
        el: List[Tuple[str, float, Optional[str]]]
        if lang == "ko":
            el = [("크리티컬 확률", crit_rate_formal, "%"),
                  ("크리티컬 데미지", math.floor(self.crit_damage * 10) / 10, "%"),
                  ("주스텟", math.floor(self.stat_main * 10) / 10),
                  ("부스텟", math.floor(self.stat_sub * 10) / 10),
                  ("총 데미지", math.floor(self.pdamage * 10) / 10, "%"),
                  ("보스 공격력", math.floor(self.boss_pdamage * 10) / 10, "%"),
                  ("주스텟퍼", math.floor(self.pstat_main * 10) / 10, "%"),
                  ("부스텟퍼", math.floor(self.pstat_sub * 10) / 10, "%"),
                  ("최종뎀", math.floor(self.pdamage_indep * 10) / 10, "%"),
                  ("공격력", math.floor(self.att * 10) / 10),
                  ("공퍼", math.floor(self.patt * 10) / 10, "%"),
                  ("방무", math.floor(self.armor_ignore * 10) / 10, "%")]
        elif lang == "en":
            el = [("crit rate", self.crit),
                  ("crit damage", self.crit_damage),
                  ("main stat", self.stat_main),
                  ("sub stat", self.stat_sub),
                  ("total damageP", self.pdamage),
                  ("boss damageP", self.boss_pdamage),
                  ("main statP", self.pstat_main),
                  ("sub statP", self.pstat_sub),
                  ("final damageP", self.pdamage_indep),
                  ("AD/MD", self.att),
                  ("AD/MD P", self.patt),
                  ("armor ignorance", self.armor_ignore)]
        else:
            raise TypeError('lang must be ko or en, lang: ' + str(lang))
        retel = []
        for i in el:
            if i[1] != 0:
                retel.append(i)
        return retel

    def as_dict(self) -> Dict[str, float]:
        return {"crit": self.crit,
                "crit_damage": self.crit_damage,
                "pdamage": self.pdamage,
                "pdamage_indep": self.pdamage_indep,
                "stat_main": self.stat_main,
                "stat_sub": self.stat_sub,
                "pstat_main": self.pstat_main,
                "pstat_sub": self.pstat_sub,
                "boss_pdamage": self.boss_pdamage,
                "armor_ignore": self.armor_ignore,
                "patt": self.patt,
                "att": self.att,
                "stat_main_fixed": self.stat_main_fixed,
                "stat_sub_fixed": self.stat_sub_fixed}

    # TODO: Not used method.
    def _dynamic_variable_hint(self, character_modifier: 'CharacterModifier') -> Optional['DynamicCharacterModifier']:
        if not isinstance(character_modifier, DynamicCharacterModifier):
            return DynamicCharacterModifier(crit=character_modifier.crit,
                                            crit_damage=character_modifier.crit_damage,
                                            pdamage=character_modifier.pdamage,
                                            pdamage_indep=character_modifier.pdamage_indep,
                                            stat_main=character_modifier.stat_main,
                                            stat_sub=character_modifier.stat_sub,
                                            pstat_main=character_modifier.pstat_main,
                                            pstat_sub=character_modifier.pstat_sub,
                                            boss_pdamage=character_modifier.boss_pdamage,
                                            armor_ignore=character_modifier.armor_ignore,
                                            patt=character_modifier.patt,
                                            att=character_modifier.att,
                                            stat_main_fixed=character_modifier.stat_main_fixed,
                                            stat_sub_fixed=character_modifier.stat_sub_fixed)
        else:
            return None


class DynamicCharacterModifier(DynamicVariableInstance, CharacterModifier):
    def __init__(self, **kwargs) -> None:
        DynamicVariableInstance.__init__(self)
        parsed_kwargs = {k: DynamicVariableOperation.wrap_argument(a) for k, a in kwargs.items()}
        for k, a in parsed_kwargs.items():
            self.add_next_instance(a)
            a.inherit_namespace(k)
        CharacterModifier.__init__(self, **parsed_kwargs)

    def evaluate_override(self) -> CharacterModifier:
        return CharacterModifier(crit=self.crit.evaluate(),
                                 crit_damage=self.crit_damage.evaluate(),
                                 pdamage=self.pdamage.evaluate(),
                                 pdamage_indep=self.pdamage_indep.evaluate(),
                                 stat_main=self.stat_main.evaluate(),
                                 stat_sub=self.stat_sub.evaluate(),
                                 pstat_main=self.pstat_main.evaluate(),
                                 pstat_sub=self.pstat_sub.evaluate(),
                                 boss_pdamage=self.boss_pdamage.evaluate(),
                                 armor_ignore=self.armor_ignore.evaluate(),
                                 patt=self.patt.evaluate(),
                                 att=self.att.evaluate(),
                                 stat_main_fixed=self.stat_main_fixed.evaluate(),
                                 stat_sub_fixed=self.stat_sub_fixed.evaluate())


class SkillModifier:
    def __init__(self, buff_rem: float = 0, summon_rem: float = 0, cooltime_reduce: float = 0,
                 pcooltime_reduce: float = 0, reuse_chance: float = 0) -> None:
        self.buff_rem: float = buff_rem
        self.summon_rem: float = summon_rem
        self.cooltime_reduce: float = cooltime_reduce
        self.pcooltime_reduce: float = pcooltime_reduce
        self.reuse_chance: float = reuse_chance

    def copy(self) -> 'SkillModifier':
        return SkillModifier(buff_rem=self.buff_rem, summon_rem=self.summon_rem, cooltime_reduce=self.cooltime_reduce,
                             pcooltime_reduce=self.pcooltime_reduce, reuse_chance=self.reuse_chance)

    def __add__(self, arg: 'SkillModifier') -> 'SkillModifier':
        return SkillModifier(
            buff_rem=self.buff_rem + arg.buff_rem,
            summon_rem=self.summon_rem + arg.summon_rem,
            cooltime_reduce=self.cooltime_reduce + arg.cooltime_reduce,
            pcooltime_reduce=self.pcooltime_reduce + arg.pcooltime_reduce,
            reuse_chance=self.reuse_chance + arg.reuse_chance)


class ExtendedCharacterModifier(CharacterModifier):
    def __init__(self, buff_rem: float = 0, summon_rem: float = 0, cooltime_reduce: float = 0, pcooltime_reduce: float = 0,
                 reuse_chance: float = 0, prop_ignore: float = 0, additional_target: int = 0, passive_level: int = 0, **kwargs) -> None:
        super(ExtendedCharacterModifier, self).__init__(**kwargs)
        self.buff_rem: float = buff_rem
        self.summon_rem: float = summon_rem
        self.cooltime_reduce: float = cooltime_reduce
        self.pcooltime_reduce: float = pcooltime_reduce
        self.reuse_chance: float = reuse_chance
        self.prop_ignore: float = prop_ignore
        self.additional_target: int = additional_target
        self.passive_level: int = passive_level

    def log(self) -> str:
        txt = super(ExtendedCharacterModifier, self).log()
        txt += "buff_rem : %.1f, summon_rem : %.1f\n" % (self.buff_rem, self.summon_rem)
        txt += "cooltime_reduce : %.1f, pcooltime_reduce : %.1f\n" % (self.cooltime_reduce, self.pcooltime_reduce)
        txt += "reuse_chance : %.1f, prop_ignore : %.1f\n" % (self.reuse_chance, self.prop_ignore)
        txt += "additional_target : %d, passive_level : %d\n" % (self.additional_target, self.passive_level)
        return txt

    def copy(self) -> 'ExtendedCharacterModifier':
        return ExtendedCharacterModifier(
            buff_rem=self.buff_rem,
            summon_rem=self.summon_rem,
            cooltime_reduce=self.cooltime_reduce,
            pcooltime_reduce=self.pcooltime_reduce,
            reuse_chance=self.reuse_chance,
            prop_ignore=self.prop_ignore,
            additional_target=self.additional_target,
            passive_level=self.passive_level,
            crit=self.crit,
            crit_damage=self.crit_damage,
            pdamage=self.pdamage,
            pdamage_indep=self.pdamage_indep,
            stat_main=self.stat_main,
            stat_sub=self.stat_sub,
            pstat_main=self.pstat_main,
            pstat_sub=self.pstat_sub,
            boss_pdamage=self.boss_pdamage,
            armor_ignore=self.armor_ignore,
            patt=self.patt,
            att=self.att,
            stat_main_fixed=self.stat_main_fixed,
            stat_sub_fixed=self.stat_sub_fixed
        )

    def degenerate(self) -> CharacterModifier:
        return super(ExtendedCharacterModifier, self).copy()

    def to_skill_modifier(self) -> SkillModifier:
        return SkillModifier(buff_rem=self.buff_rem, summon_rem=self.summon_rem, cooltime_reduce=self.cooltime_reduce,
                             pcooltime_reduce=self.pcooltime_reduce, reuse_chance=self.reuse_chance)

    def as_dict(self) -> Dict[str, float]:
        ret_dict = super(ExtendedCharacterModifier, self).as_dict()
        return {
            **ret_dict,
            "buff_rem": self.buff_rem,
            "summon_rem": self.summon_rem,
            "cooltime_reduce": self.cooltime_reduce,
            "pcooltime_reduce": self.pcooltime_reduce,
            "reuse_chance": self.reuse_chance,
            "prop_ignore": self.prop_ignore,
            "additional_target": self.additional_target,
            "passive_level": self.passive_level
        }

    def __iadd__(self, arg: 'ExtendedCharacterModifier') -> 'ExtendedCharacterModifier':
        self.buff_rem += arg.buff_rem
        self.summon_rem += arg.summon_rem
        self.cooltime_reduce += arg.cooltime_reduce
        self.pcooltime_reduce += arg.pcooltime_reduce
        self.reuse_chance += arg.reuse_chance
        self.prop_ignore += arg.prop_ignore
        self.additional_target += arg.additional_target
        self.passive_level += arg.passive_level
        self.crit += arg.crit
        self.crit_damage += arg.crit_damage
        self.pdamage += arg.pdamage
        self.pdamage_indep += arg.pdamage_indep + (self.pdamage_indep * arg.pdamage_indep) * 0.01
        self.stat_main += arg.stat_main
        self.stat_sub += arg.stat_sub
        self.pstat_main += arg.pstat_main
        self.pstat_sub += arg.pstat_sub
        self.boss_pdamage += arg.boss_pdamage
        self.armor_ignore = 100 - 0.01 * ((100 - self.armor_ignore) * (100 - arg.armor_ignore))
        self.patt += arg.patt
        self.att += arg.att
        self.stat_main_fixed += arg.stat_main_fixed
        self.stat_sub_fixed += arg.stat_sub_fixed
        return self

    def __add__(self, arg: 'ExtendedCharacterModifier') -> 'ExtendedCharacterModifier':
        return ExtendedCharacterModifier(
            buff_rem=(self.buff_rem + arg.buff_rem),
            summon_rem=(self.summon_rem + arg.summon_rem),
            cooltime_reduce=(self.cooltime_reduce + arg.cooltime_reduce),
            pcooltime_reduce=(self.pcooltime_reduce + arg.pcooltime_reduce),
            reuse_chance=(self.reuse_chance + arg.reuse_chance),
            prop_ignore=(self.prop_ignore + arg.prop_ignore),
            additional_target=(self.additional_target + arg.additional_target),
            passive_level=(self.passive_level + arg.passive_level),
            crit=(self.crit + arg.crit),
            crit_damage=(self.crit_damage + arg.crit_damage),
            pdamage=(self.pdamage + arg.pdamage),
            pdamage_indep=(self.pdamage_indep + arg.pdamage_indep + (self.pdamage_indep * arg.pdamage_indep) * 0.01),
            stat_main=(self.stat_main + arg.stat_main),
            stat_sub=(self.stat_sub + arg.stat_sub),
            pstat_main=(self.pstat_main + arg.pstat_main),
            pstat_sub=(self.pstat_sub + arg.pstat_sub),
            boss_pdamage=(self.boss_pdamage + arg.boss_pdamage),
            armor_ignore=100 - 0.01 * ((100 - self.armor_ignore) * (100 - arg.armor_ignore)),
            patt=(self.patt + arg.patt),
            att=(self.att + arg.att),
            stat_main_fixed=(self.stat_main_fixed + arg.stat_main_fixed),
            stat_sub_fixed=(self.stat_sub_fixed + arg.stat_sub_fixed))

    def __sub__(self, arg: 'ExtendedCharacterModifier') -> 'ExtendedCharacterModifier':
        return ExtendedCharacterModifier(
            buff_rem=(self.buff_rem - arg.buff_rem),
            summon_rem=(self.summon_rem - arg.summon_rem),
            cooltime_reduce=(self.cooltime_reduce - arg.cooltime_reduce),
            pcooltime_reduce=(self.pcooltime_reduce - arg.pcooltime_reduce),
            reuse_chance=(self.reuse_chance - arg.reuse_chance),
            prop_ignore=(self.prop_ignore - arg.prop_ignore),
            additional_target=(self.additional_target - arg.additional_target),
            passive_level=(self.passive_level - arg.passive_level),
            crit=(self.crit - arg.crit),
            crit_damage=(self.crit_damage - arg.crit_damage),
            pdamage=(self.pdamage - arg.pdamage),
            pdamage_indep=(100 + self.pdamage_indep) / (100 + arg.pdamage_indep) * 100 - 100,
            stat_main=(self.stat_main - arg.stat_main),
            stat_sub=(self.stat_sub - arg.stat_sub),
            pstat_main=(self.pstat_main - arg.pstat_main),
            pstat_sub=(self.pstat_sub - arg.pstat_sub),
            boss_pdamage=(self.boss_pdamage - arg.boss_pdamage),
            armor_ignore=100 - 100 * (100 - self.armor_ignore) / (100 - arg.armor_ignore),
            patt=(self.patt - arg.patt),
            att=(self.att - arg.att),
            stat_main_fixed=(self.stat_main_fixed - arg.stat_main_fixed),
            stat_sub_fixed=(self.stat_sub_fixed - arg.stat_sub_fixed))


class InformedCharacterModifier(ExtendedCharacterModifier):
    __slots__ = "name"

    def __init__(self, name: str, **kwargs) -> None:
        super(InformedCharacterModifier, self).__init__(**kwargs)
        self.name: str = name

    def as_dict(self) -> Dict[str, Any]:
        ret_dict: Dict[str, Any] = super(InformedCharacterModifier, self).as_dict()
        ret_dict['name'] = self.name
        return ret_dict

    @staticmethod
    def from_extended_modifier(name: str, extended_modifier: ExtendedCharacterModifier) -> 'InformedCharacterModifier':
        return InformedCharacterModifier(name,
                                         buff_rem=extended_modifier.buff_rem,
                                         summon_rem=extended_modifier.summon_rem,
                                         cooltime_reduce=extended_modifier.cooltime_reduce,
                                         pcooltime_reduce=extended_modifier.pcooltime_reduce,
                                         reuse_chance=extended_modifier.reuse_chance,
                                         prop_ignore=extended_modifier.prop_ignore,
                                         additional_target=extended_modifier.additional_target,
                                         passive_level=extended_modifier.passive_level,
                                         crit=extended_modifier.crit,
                                         crit_damage=extended_modifier.crit_damage,
                                         pdamage=extended_modifier.pdamage,
                                         pdamage_indep=extended_modifier.pdamage_indep,
                                         stat_main=extended_modifier.stat_main,
                                         stat_sub=extended_modifier.stat_sub,
                                         pstat_main=extended_modifier.pstat_main,
                                         pstat_sub=extended_modifier.pstat_sub,
                                         boss_pdamage=extended_modifier.boss_pdamage,
                                         armor_ignore=extended_modifier.armor_ignore,
                                         patt=extended_modifier.patt,
                                         att=extended_modifier.att,
                                         stat_main_fixed=extended_modifier.stat_main_fixed,
                                         stat_sub_fixed=extended_modifier.stat_sub_fixed)


class VSkillModifier:
    @staticmethod
    def get_reinforcement(incr: int, lv: int, crit: bool = False) -> CharacterModifier:
        armor = 0
        if lv >= 40:
            armor = 20
        if lv >= 20 and crit:
            return CharacterModifier(crit=5, pdamage_indep=(lv * incr), armor_ignore=armor)
        else:
            return CharacterModifier(crit=0, pdamage_indep=(lv * incr), armor_ignore=armor)


class AbstractSkill(EvaluativeGraphElement):
    """Skill must have information about it's name, it's using - delay, skill using cooltime.
    Basic functions

    Can be re - implemented, but not mandate :
    - dump_json : returns JSON for it's state.
    - load_json : from given JSON, set it's state.
    - get_info : return it's status as JSON.
    """

    def __init__(self, name: str, delay: int, cooltime: int = 0, rem: bool = False, red: bool = True) -> None:
        super(AbstractSkill, self).__init__(namespace=name)
        self.spec: str = "graph control"
        with self.dynamic_range():
            self.rem: bool = rem
            self.red: bool = red
            self.name: str = name
            self.delay: int = delay
            self.cooltime: int = cooltime
            self.explanation: Optional[str] = None

            if self.cooltime == -1:
                self.cooltime = NOTWANTTOEXECUTE

    def _change_time_into_string(self, float_or_Infinite: float, divider: int = 1, lang: str = "ko") -> str:
        lang_to_inf_dict = {"ko": "무한/자동발동불가", "en": "Infinite"}
        if abs(float_or_Infinite - NOTWANTTOEXECUTE / divider) < 10000 / divider:
            return lang_to_inf_dict[lang]
        else:
            return "%.1f" % float_or_Infinite

    def _parse_list_info_into_string(self, li: List[Tuple[str, str]]) -> str:
        return "\n".join([":".join([i[0], "".join([str(j) for j in i[1:]])]) for i in li if len(str(i[1])) > 0])

    def set_explanation(self, strs: str) -> None:
        self.explanation = strs

    def get_explanation(self, lang: str = "ko", expl_level: int = 2) -> str:
        """level 0 / 1 / 2
        """
        if self.explanation is not None:
            return self.explanation
        else:
            return self._get_explanation_internal(lang=lang, expl_level=expl_level)

    def _get_explanation_internal(self, detail: bool = False, lang: str = "ko", expl_level: int = 2) -> str:
        if lang == "en":
            li = [("skill name", self.name),
                  ("type", "AbstractSkill(Not implemented)")]
        elif lang == "ko":
            li = [("스킬 이름", self.name),
                  ("분류", "템플릿(상속되지 않음)")]
        else:
            li = []

        return self._parse_list_info_into_string(li)

    def get_info(self, expl_level: int = 2) -> Dict[str, str]:
        my_json = {"name": self.name, "delay": self._change_time_into_string(self.delay),
                   "cooltime": self._change_time_into_string(self.cooltime),
                   "expl": self.get_explanation(expl_level=expl_level)}
        return my_json

    def wrap(self, wrapper: 'type(AbstractSkillWrapper)', name: str = None) -> 'AbstractSkillWrapper':
        if name is None:
            return wrapper(self)
        else:
            return wrapper(self, name=name)

    def isV(self, enhancer: 'BasicVEnhancer', use_index, upgrade_index) -> 'AbstractSkill':
        """Speed hack
        """
        enhancer.add_v_skill(self, use_index, upgrade_index)
        return self


class BuffSkill(AbstractSkill):
    """BuffSkill : Implements AbstractSkill, which contains baisc information about Skill.
    Basic Templates for generating buff skill.
    - parameters

      .remain : Buff remainance
      .buff_remAvailFlag : Boolean whether buff remainance option could be applied or not. (Default : True)
      .static_character_modifier : Contains static - modifier.

      * go to CharacterModifier for find more detail about parameters.

    - methods

      Buff skill only need to return modifier, nothing else.

      .get_modifier() : returns CharacterModifier for Character.

    """

    def __init__(self, name: str, delay: int, remain: int, cooltime: int = 0, crit: float = 0, crit_damage: float = 0,
                 pdamage: float = 0, stat_main: int = 0, stat_sub: int = 0, pstat_main: int = 0, pstat_sub: int = 0,
                 boss_pdamage: float = 0, pdamage_indep: float = 0, armor_ignore: float = 0, patt: int = 0, att: int = 0,
                 stat_main_fixed: int = 0, stat_sub_fixed: int = 0, rem: bool = False, red: bool = False) -> None:
        super(BuffSkill, self).__init__(name, delay, cooltime=cooltime, rem=rem, red=red)
        with self.dynamic_range():
            self.spec: str = "buff"
            self.remain: int = remain
            # Build StaticModifier from given arguments
            self.static_character_modifier: CharacterModifier = \
                CharacterModifier(crit=crit, crit_damage=crit_damage, pdamage=pdamage, pdamage_indep=pdamage_indep,
                                  stat_main=stat_main, stat_sub=stat_sub, pstat_main=pstat_main, pstat_sub=pstat_sub,
                                  boss_pdamage=boss_pdamage, armor_ignore=armor_ignore, patt=patt, att=att,
                                  stat_main_fixed=stat_main_fixed, stat_sub_fixed=stat_sub_fixed)

    def _get_explanation_internal(self, detail: bool = False, lang: str = "ko", expl_level: int = 2) -> str:
        if lang == "ko":
            li = [("스킬 이름", self.name),
                  ("분류", "버프"),
                  ("딜레이", "%.1f" % self.delay, "ms"),
                  ("지속 시간", self._change_time_into_string(self.remain / 1000, divider=1000), "s"),
                  ("쿨타임", self._change_time_into_string(self.cooltime / 1000, divider=1000), "s"),
                  ("쿨타임 감소 가능 여부", self.red),
                  ("지속시간 증가 여부", self.rem),
                  ("효과", ", ".join([(str(i[0]) + "+" + "".join([str(j) for j in i[1:]])) for i in
                                    self.static_character_modifier.abstract_log_list()]).replace("+미발동", " 미발동"))]
            if expl_level < 2:
                li = [li[3], li[7]]
        elif lang == "en":
            li = []
        else:
            raise TypeError('lang must be ko or en, lang: ' + str(lang))

        return self._parse_list_info_into_string(li)

    def get_modifier(self) -> CharacterModifier:
        """You can override this function if needed(When your buff skill needs complicated calculation)
        * If your buff skill varies with time (e.g. Infinity), following modifier is recommended to calculate in ModifierWrapper.
        """
        return self.static_character_modifier


class DamageSkill(AbstractSkill):
    """DamageSkill : Implement AbstractSkill, which contains baisc information about Skill.
    Basic Template for generating deal skills.
    - methods
      .getSkillDamage() : returns Damage % for Character.
      .get_modifier() : returns CharacterModifier for Character.
    """

    def __init__(self, name: str, delay: int, damage: int, hit: int, cooltime: int = 0,
                 modifier: CharacterModifier = CharacterModifier(), red: bool = False) -> None:
        super(DamageSkill, self).__init__(name, delay, cooltime=cooltime, rem=False, red=red)
        with self.dynamic_range():
            self.spec: str = "damage"
            self.damage: int = damage
            self.hit: int = hit
            self._static_skill_modifier: CharacterModifier = modifier  # Issue : Will we need this option really?

    def _get_explanation_internal(self, detail: bool = False, lang: str = "ko", expl_level: int = 2) -> str:
        if lang == "ko":
            li = [("스킬 이름", self.name),
                  ("분류", "공격기"),
                  ("딜레이", "%.1f" % self.delay, "ms"),
                  ("퍼뎀", "%.1f" % self.damage, "%"),
                  ("타격수", self.hit),
                  ("쿨타임", self._change_time_into_string(self.cooltime / 1000, divider=1000), "s"),
                  ("쿨타임 감소 가능 여부", self.red),
                  ("지속시간 증가 여부", self.rem),
                  ("추가효과", ", ".join([(str(i[0]) + "+" + "".join([str(j) for j in i[1:]])) for i in self._static_skill_modifier.abstract_log_list()]).replace("+미발동%", " 미발동"))]
            if expl_level < 2:
                li = li[3:5] + [li[8]]
        elif lang == 'en':
            li = []
        else:
            raise TypeError('lang must be ko or en, lang: ' + str(lang))

        return self._parse_list_info_into_string(li)

    def setV(self, v_enhancer: AbstractVEnhancer, index: int, incr: int, crit: bool = False) -> 'DamageSkill':
        self._static_skill_modifier = self._static_skill_modifier + v_enhancer.get_reinforcement_with_register(index, incr, crit, self)
        return self

    def get_modifier(self) -> CharacterModifier:
        return self._static_skill_modifier

    def copy(self) -> 'DamageSkill':
        return DamageSkill(self.name, self.delay, self.damage, self.hit, cooltime=self.cooltime,
                           modifier=self._static_skill_modifier, red=self.red)


# TODO: optimize this factor more constructively
class SummonSkill(AbstractSkill):
    def __init__(self, name: str, summondelay: int, delay: int, damage: int, hit: int, remain: int, cooltime: int = 0,
                 modifier: CharacterModifier = CharacterModifier(), rem: bool = False, red: bool = False) -> None:
        super(SummonSkill, self).__init__(name, delay, cooltime=cooltime, rem=rem, red=red)
        with self.dynamic_range():
            self.spec: str = "summon"
            self.summondelay: int = summondelay
            self.damage: int = damage
            self.hit: int = hit
            self.remain: int = remain
            self._static_skill_modifier: CharacterModifier = modifier

    def _get_explanation_internal(self, detail: bool = False, lang: str = "ko", expl_level: int = 2) -> str:
        if lang == "ko":
            li = [("스킬 이름", self.name),
                  ("분류", "소환기"),
                  ("딜레이", "%.1f" % self.summondelay, "ms"),
                  ("타격주기", "%.1f" % self.delay, "ms"),
                  ("퍼뎀", "%.1f" % self.damage, "%"),
                  ("타격수", self.hit),
                  ("지속 시간", self._change_time_into_string(self.remain / 1000, divider=1000), "s"),
                  ("쿨타임", self._change_time_into_string(self.cooltime / 1000, divider=1000), "s"),
                  ("쿨타임 감소 가능 여부", self.red),
                  ("지속시간 증가 여부", self.rem),
                  ("추가효과", ", ".join([(str(i[0]) + "+" + "".join([str(j) for j in i[1:]])) for i in
                                      self._static_skill_modifier.abstract_log_list()]).replace("+미발동%", " 미발동"))]
            if expl_level < 2:
                li = li[3:7] + [li[10]]
        elif lang == "en":
            li = []
        else:
            raise TypeError('lang must be ko or en, lang: ' + str(lang))

        return self._parse_list_info_into_string(li)

    def get_info(self, expl_level=2) -> Dict[str, str]:
        my_json = {"name": self.name, "delay": self._change_time_into_string(self.summondelay),
                   "cooltime": self._change_time_into_string(self.cooltime),
                   "expl": self.get_explanation(expl_level=expl_level)}
        return my_json

    def setV(self, v_enhancer: AbstractVEnhancer, index: int, incr: int, crit: bool = False) -> 'SummonSkill':
        self._static_skill_modifier = self._static_skill_modifier + v_enhancer.get_reinforcement_with_register(index, incr, crit, self)
        return self

    def get_modifier(self) -> CharacterModifier:
        return self._static_skill_modifier


class DotSkill(SummonSkill):
    def __init__(self, name: str, summondelay: int, delay: int, damage: int, hit: int,
                 remain: int, cooltime: int = 0, red: bool = False) -> None:
        super(DotSkill, self).__init__(name, summondelay, delay, damage, hit, remain, cooltime=cooltime, red=red)
        self.spec: str = "dot"

    def _get_explanation_internal(self, detail: bool = False, lang: str = "ko", expl_level: int = 2) -> str:
        if lang == "ko":
            li = [("스킬 이름", self.name),
                  ("분류", "도트뎀"),
                  ("딜레이", "%.1f" % self.summondelay, "ms"),
                  ("타격주기", "%.1f" % self.delay, "ms"),
                  ("퍼뎀", "%.1f" % self.damage, "%"),
                  ("타격수", self.hit),
                  ("지속 시간", self._change_time_into_string(self.remain / 1000, divider=1000), "s"),
                  ("쿨타임", self._change_time_into_string(self.cooltime / 1000, divider=1000), "s"),
                  ("쿨타임 감소 가능 여부", self.red),
                  ("지속시간 증가 여부", self.rem),
                  ("추가효과", ", ".join([(str(i[0]) + "+" + "".join([str(j) for j in i[1:]])) for i in
                                      self._static_skill_modifier.abstract_log_list()]).replace("+미발동%", " 미발동"))]
            if expl_level < 2:
                li = li[3:7] + [li[10]]
        elif lang == en:
            li = []
        else:
            raise TypeError('lang must be ko or en: ' + str(lang))

        return self._parse_list_info_into_string(li)


class Task:
    def __init__(self, ref, ftn) -> None:
        self._ref: 'GraphElement' = ref
        self._ftn: 'Callable[[Optional[Any]], ResultObject]' = ftn
        self._after: 'List[Task]' = []
        self._before: 'List[Task]' = []
        self._justAfter: 'List[Task]' = []

    def __repr__(self) -> str:
        return f'''Task Object from [{self._ref._id}]'''

    def getRef(self) -> 'GraphElement':
        return self._ref

    def do(self, **kwargs) -> 'ResultObject':
        return self._ftn()

    def onAfter(self, afters: 'List[Task]') -> None:
        self._after += afters

    def onBefore(self, befores: 'List[Task]') -> None:
        self._before += befores

    def onJustAfter(self, jafters: 'List[Task]') -> None:
        self._justAfter += jafters

    def copy(self) -> 'Task':
        retTask = Task(self._ref, self._ftn)
        retTask.onAfter(self._after)
        retTask.onBefore(self._before)
        retTask.onJustAfter(self._justAfter)
        return retTask


class ContextReferringTask(Task):
    def do(self, **kwargs) -> 'ResultObject':
        return self._ftn(**kwargs)


class ResultObject:
    def __init__(self, delay: int, mdf: CharacterModifier, damage: int, hit: int, sname: str, spec: str,
                 kwargs={}, cascade=[], callbacks: 'List[Callback]' = []) -> None:
        """Result object must be static; alway to be ensure it is revealed.
        """
        self.delay: int = DynamicVariableOperation.reveal_argument(delay)
        self.damage: int = DynamicVariableOperation.reveal_argument(damage)
        self.hit: int = DynamicVariableOperation.reveal_argument(hit)
        self.mdf: CharacterModifier = DynamicVariableOperation.reveal_argument(mdf)
        self.sname: str = DynamicVariableOperation.reveal_argument(sname)
        self.spec: str = DynamicVariableOperation.reveal_argument(spec)  # buff, deal, summon
        self.kwargs: Dict[Any, Any] = DynamicVariableOperation.reveal_argument(kwargs)
        self.cascade: List[Task] = DynamicVariableOperation.reveal_argument(cascade)
        self.callbacks: List[Callback] = callbacks
        self.time: Optional[float] = None

    def setTime(self, time: float) -> None:
        self.time = time


'''Default Values. Forbidden to editting.
'''
taskTerminater: ResultObject = ResultObject(0, CharacterModifier(), 0, 0, sname='terminator', spec='graph control')


class Callback:
    def __init__(self, task: Task, time: float) -> None:
        self.task: Task = task
        self.time: float = time

    def resolve(self) -> ResultObject:
        return self.task.do()

    def adjust_by_current_time(self, current_time: float) -> 'Callback':
        return Callback(self.task, self.time + current_time)

    @staticmethod
    def from_graph_element(graph_element: 'GraphElement', time: float) -> 'Callback':
        return Callback(graph_element.build_task(None), time)


class AccessibleBossState:
    NO_FLAG: int = 1
    LEVIATE: int = 2
    DISTANCE: int = 4
    INVINSIBLE: int = 8
    IMMUNE: int = 16

    ALWAYS: int = 31

    def __init__(self) -> None:
        pass


class GraphElement:
    """Manage time dependent feature of each execution
    """

    Flag_Skill: int = 1
    Flag_BaseSkill: int = 2
    Flag_BuffSkill: int = 4
    Flag_DamageSkill: int = 8
    Flag_SummonSkill: int = 16
    Flag_Optional: int = 32
    Flag_Repeat: int = 64
    Flag_Constraint: int = 128

    def __init__(self, _id: Union[str, AbstractDynamicVariableInstance]) -> None:
        """
        Initialzie Graph Element.

        Parameters
        ----------
        _id : str or AbstractDynamicVariableInstance
            해당 GraphElement가 부여받게 될 identifier입니다. unique할 필요는 없습니다.

        """
        if isinstance(_id, AbstractDynamicVariableInstance):
            _id = _id.evaluate()
        self._id: str = _id
        self._before: List[GraphElement] = []  # Tasks that must be executed before this el.
        self._after: List[GraphElement] = []  # Tasks that must be executed after this el.
        self._justAfter: List[GraphElement] = []
        self._registered_callback_presets: List[Tuple[str, Tuple[Graphelemet, float]]] = []

        self._result_object_cache: ResultObject = ResultObject(0, CharacterModifier(), 0, 0, sname='Graph Element', spec='graph control')
        self._flag: int = 0
        self.accessible_boss_state: int = AccessibleBossState.NO_FLAG

    # TODO: Not used method.
    def fixAccesibleBossState(self, boss_state: int) -> None:
        self.accessible_boss_state = boss_state

    # TODO: Not used method.
    def removeAccesibleBossState(self, boss_state: int) -> None:
        self.accessible_boss_state &= ~boss_state

    # TODO: Not used method.
    def setAccesibleBossState(self, boss_state: int) -> None:
        self.accessible_boss_state |= boss_state

    def set_flag(self, flag: int) -> None:
        self._flag |= flag

    # TODO: Not used method.
    def toggle_flag(self, flag: int) -> None:
        self._flag ^= flag

    # TODO: Not used method.
    def remove_flag(self, flag: int) -> None:
        self._flag &= ~flag

    def get_link(self) -> 'List[Tuple[GraphElement, GraphElement, str]]':
        """
        주어진 Element가 상호작용하는 다른 Element들을 가져옵니다.

        Returns
        -------
        list of [self, GraphElement, link_type(string)]
        """
        li = []
        for el in self._before:
            li.append((self, el, "before"))
        for el in self._after:
            li.append((self, el, "after"))
        for el in self._justAfter:
            li.append((self, el, "after"))
        for _, context in self._registered_callback_presets:
            li.append((self, context[0], "callback"))
        return li

    def get_explanation(self, lang: str = "ko") -> str:
        """
        해당 그래프 요소에 대한 설명을 받아옵니다.

        이 함수는 상속 과정에서 재정의 되는 것이 좋습니다.

        Parameters
        ----------
        lang
            Language type. Korean : ko, English : en.

        Returns
        -------
        string
        """
        if lang == "ko":
            return "종류:그래프 요소"
        elif lang == "en":
            return "Type:graph Element"

    def _use(self, **kwargs) -> ResultObject:
        """
        해당 그래프 요소를 작동시키고자 할 때 수행해야 하는 작업을 정의합니다.

        이 함수는 상속 과정에서 반드시 재정의되어야 합니다.

        Returns
        ------
        ResultObject
            해당 그래프 요소가 작동하고 난 후의 결과물
        """
        return self._result_object_cache

    def build_task(self, skill_modifier: SkillModifier, **kwargs) -> Task:
        """
        그래프 요소의 실행을 정의하는 Task를 반환합니다.


        Parameters
        ----------
        skill_modifier: SkillModifier

        Returns
        -------
        Task
        """
        task = Task(self, self._use)
        self.sync(task, skill_modifier)
        return task

    def spend_time(self, time: float) -> None:
        """
        시간이 흘렀을 때의 행동을 정의합니다.
        이 함수는 ``Simulator`` 에 의해서 전체 ``GraphElement`` 들이 일괄적으로 처리될 때 호출됩니다.

        Parameters
        ----------
        time : float
            지나간 시간입니다.
        """
        return

    def onAfter(self, el: 'GraphElement') -> None:
        """
        해당 그래프 요소가 실행된 후에 el 요소를 실행하도록 합니다.
        만약 ``onAfter`` 를 통해 chaining된 GraphElement는 해당 그래프 요소가 실행되었다면, 어떠한 경우에 있어서도 chaining됩니다.

        onAfter메서드가 두 번 호출되었다면, 먼저 호출에 포함된 인자가 우선 수행됩니다.

        Parameters
        ----------
        el : GraphElement
            다음에 실행되어야 할 ``GraphElement``
        """
        self._after = [el] + self._after

    def onAfters(self, ellist: 'List[GraphElement]') -> None:
        self._after = self._after + ellist

    def onBefore(self, el: 'GraphElement') -> None:
        """
        해당 그래프 요소가 실행된 후에 el 요소를 실행하도록 합니다.
        만약 ``onBefore`` 를 통해 chaining된 GraphElement는 해당 그래프 요소가 실행되었다면, 어떠한 경우에 있어서도 chaining됩니다.

        onAfter메서드가 두 번 호출되었다면, 먼저 호출에 포함된 인자가 나중에 수행됩니다.

        Parameters
        ----------
        el : GraphElement
            이전에 실행되어야 할 ``GraphElement``
        """
        self._before = self._before + [el]

    def onBefores(self, ellist: 'List[GraphElement]') -> None:
        self._before += ellist

    def sync(self, task: Task, skill_modifier: SkillModifier) -> None:
        """
        주어진 ``el`` 가 자신과 연결된 다른 ``GraphElement`` 와 동일한 연결 구조를 가지도록 합니다.

        Parameters
        ----------
        task : Task
        skill_modifier : SkillModifier
        """
        task.onBefore([el.build_task(skill_modifier) for el in self._before])
        task.onAfter([el.build_task(skill_modifier) for el in self._after])
        task.onJustAfter([el.build_task(skill_modifier) for el in self._justAfter])

    def onJustAfter(self, el: 'GraphElement') -> None:
        self._justAfter += [el] + self._justAfter

    def onJustAfters(self, ellist: 'List[GraphElement]') -> None:
        self._justAfter += ellist

    def ignore(self) -> None:
        return None

    # TODO: Not used method.
    def ensure_condition(self, cond: Callable[[], bool]) -> 'Optional[GraphElement]':
        if cond():
            return self
        else:
            return None

    def ensure(self, ehc: 'AbstractVEnhancer', index_1: int, index_2: int) -> 'Optional[GraphElement]':
        """주어진 ``ehc`` 의 코어 강화가 존재하지 않는다면, ``None`` 을 반환하여 실행되지 못하도록 막습니다.

        Parameters
        ----------
        ehc: AbstractVEnhancer
        index_1 : int
            ``ehc`` 가 첫번째 인자로 받게 될 index
        index_2 : int
            ``ehc`` 가 두번째 인자로 받게 될 index

        """
        if ehc.getV(index_1, index_2) > 0:
            return self
        else:
            return None

    def create_callbacks(self, **kwargs) -> List[Callback]:
        raise NotImplementedError


class TaskHolder(GraphElement):
    """This class only holds given el(Does not modify any property of el).
    주어진 Task를 수행하는 ``GraphElement`` 입니다. 단순히 ``Task`` 를 감싸기 위한 용도로 사용합니다.
    """

    def __init__(self, task: Task, name: str = None) -> None:
        if name is None:
            name = "연결"
        super(TaskHolder, self).__init__(name)
        self._taskholder: Task = task

    def get_explanation(self, lang: str = "ko") -> str:
        if lang == "ko":
            return "%s" % self._id
        elif lang == "en":
            return "type:el holder\nname:%s" % self._id

    def build_task(self, skill_modifier: SkillModifier, **kwargs) -> Task:
        task = self._taskholder.copy()
        self.sync(task, skill_modifier)
        return task

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        li = super(TaskHolder, self).get_link()
        li.append((self, self._taskholder.getRef(), "effect"))
        return li


def create_task(task_name: str, task_function, task_ref) -> TaskHolder:
    return TaskHolder(Task(task_ref, task_function), task_name)


class OptionalTask(Task):
    def __init__(self, ref, discriminator: Callable[[], bool], task: Task, failtask: Task = None, name: str = 'optionalTask') -> None:
        super(OptionalTask, self).__init__(ref, None)
        self._discriminator: Callable[[], bool] = discriminator
        self._result: Task = task
        self._name: str = name
        self._failtask = failtask  # TODO: Not used attribute.
        self._result_object_cache: ResultObject = ResultObject(0, CharacterModifier(), 0, 0, sname=self._name, spec='graph control', cascade=[self._result])
        self._fail: ResultObject
        if failtask is None:
            self._fail = ResultObject(0, CharacterModifier(), 0, 0, sname=self._name + " fail", spec='graph control')
        else:
            self._fail = ResultObject(0, CharacterModifier(), 0, 0, sname=self._name, spec='graph control', cascade=[failtask])

    def do(self, **kwargs) -> ResultObject:
        if self._discriminator():
            return self._result_object_cache
        else:
            return self._fail


class OptionalElement(GraphElement):
    """조건에 따라서, 다른 Task를 수행하는 ``GraphElement`` 입니다.

    Parameters
    ----------
    disc : function
        조건 판별시에 수행될 함수입니다.
    after : GraphElement
        ``disc()`` 함수 호출의 반환값이 ``True`` 일 때 실행될 ``GraphElement`` 입니다.
    fail : GraphElement(default:None)
        ``disc()`` 함수 호출의 반환값이 ``False`` 일 때 실행될 ``GraphElement`` 입니다. 값이 주어지지 않을 경우 실행되지 않습니다.
    name : string
        ``GraphElement`` 의 이름입니다. Unique할 필요는 없습니다.
    """

    def __init__(self, disc: Callable[[], bool], after: GraphElement, fail: GraphElement = None, name: str = "Optional Element") -> None:
        super(OptionalElement, self).__init__(name)
        self.disc: Callable[[], bool] = disc
        self.after: GraphElement = after
        self.fail: GraphElement = fail
        self.set_flag(self.Flag_Optional)

    def get_explanation(self, lang: str = "ko") -> str:
        if lang == "ko":
            return "종류:조건적 실행\n%s" % self._id
        elif lang == "en":
            return "type:Optional Element\nname:%s" % self._id

    def build_task(self, skill_modifier: SkillModifier, **kwargs) -> Task:
        if self.fail is None:
            fail = None
        else:
            fail = self.fail.build_task(skill_modifier)
        task = OptionalTask(self, self.disc, self.after.build_task(skill_modifier), failtask=fail, name=self._id)
        self.sync(task, skill_modifier)
        return task

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        li = super(OptionalElement, self).get_link()
        li.append((self, self.after, "if-true"))
        if self.fail is not None:
            li.append((self, self.fail, "if-false"))
        return li


class RepeatElement(GraphElement):
    """주어진 ``GraphElement`` 를 반복 시행하고 싶을 때 사용합니다.

    Parameters
    -----------
    target : GraphElement
        반복 수행할 대상
    itr : int
        반복 수행할 횟수
    """

    def __init__(self, target: GraphElement, itr: int, name: str = None) -> None:
        if name is None:
            name = "%d회 반복" % itr
        super(RepeatElement, self).__init__(name)
        self._repeat_target: GraphElement = target
        self.itr: int = itr
        for i in range(itr):
            self.onAfter(target)
        self.set_flag(self.Flag_Repeat)
        self._result_object_cache: ResultObject = ResultObject(0, CharacterModifier(), 0, 0, sname='Repeat Element', spec='graph control')

    def get_explanation(self, lang: str = "ko") -> str:
        if lang == "ko":
            return "종류:반복\n이름:%s\n반복대상:%s\n반복 횟수:%d" % (self._id, self._repeat_target._id, self.itr)
        elif lang == "en":
            return "type:Repeat Element\nname:%s\ntarget:%s\niterations:%d" % (self._id, self._repeat_target._id, self.itr)

    def _use(self) -> ResultObject:
        return self._result_object_cache

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        li = []
        li.append((self, self._repeat_target, "repeat " + str(self.itr)))
        for el in self._after:
            if el != self._repeat_target:
                li.append((self, el, "after"))
        for el in self._before:
            li.append((self, el, "before"))
        return li


class ConstraintElement(GraphElement):
    """특정 요소의 검사를 Graph로 추적하기 위해 사용되는 더미 요소 입니다.

    Parameters
    ----------
    name : str
        ``constraint`` 에 대한 설명입니다.
    ref : GraphElement
        제한조건을 파악하기 위해 참조하는 ``GraphElement`` 입니다.
    cnst : function
        조건을 검사하고자 할 때 실행되는 함수입니다. ``False``가 반환될 경우 제한합니다.
    """

    def __init__(self, name: str, ref: GraphElement, cnst: Callable[[], bool]) -> None:
        super(ConstraintElement, self).__init__(name)
        self._ref = ref
        self._ftn: Callable[[], bool] = cnst
        self.set_flag(self.Flag_Constraint)

    def get_explanation(self, lang: str = "ko") -> str:
        if lang == "ko":
            return "종류:제한\n이름:%s" % self._id
        elif lang == "en":
            return "type:Constraint Element\nname:%s" % self._id

    def check(self) -> bool:
        return self._ftn()

    def build_task(self, **kwargs) -> None:
        raise NotImplementedError("ConstraintElement must not builded.")

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        return [(self, self._ref, "check")]


class AbstractSkillWrapper(GraphElement):
    """특정 스킬의 사용을 제어하는 ``GraphElement`` 입니다. 이 객체의 _use() 함수 호출은
    인게임 내에서 대응되는 스킬의 시전과 동일하게 작용합니다.

    Parameters
    ----------
    skill : AbstractSkill
        제어 대상이 되는 스킬입니다.
    """

    def __init__(self, skill: AbstractSkill, name: str = None) -> None:
        if name is None:
            super(AbstractSkillWrapper, self).__init__(skill.name)
        else:
            super(AbstractSkillWrapper, self).__init__(name)
        self.set_flag(self.Flag_Skill)
        self.skill: AbstractSkill = skill
        self.cooltime_left: int = 0  # indicate how much time left to use this wrapper again.
        self.time_left: int = 0  # indicate how much time left for continuing this wrapper.
        self.constraint: List[ConstraintElement] = []
        self._result_object_cache: ResultObject = ResultObject(0, CharacterModifier(), 0, 0, sname=self.skill.name, spec='graph control')
        if DynamicVariableOperation.reveal_argument(self.skill.cooltime) == NOTWANTTOEXECUTE:
            self.set_disabled_and_time_left(-1)
        self.accessible_boss_state: int = AccessibleBossState.NO_FLAG

        # Context referring
        self._refer_runtime_context: bool = False

    def enable_referring_runtime_context(self) -> None:
        """If this is true, given skill wrapper may use runtime context.
        with this option, you MUST override _use() method with **kwargs argument is enabled.
        given context may passed by **kwargs option.

        이 함수가 호출될 경우, _use() 함수의 실행 시점에서 `runtime_context`를 참조할 수 있습니다.
        """
        self._refer_runtime_context = True

    def protect_from_running(self) -> None:
        """``Scheduler`` 에 의해 이 객체가 선택되는 것을 방지합니다.
        이는 ``onAfter()`` 과 같은 chaining을 통한 실행은 막지 않습니다.
        """
        constraint = ConstraintElement('사용 금지', self, lambda: False)
        self.onConstraint(constraint)

    def get_explanation(self, lang: str = "ko") -> str:
        return self.skill.get_explanation(lang=lang)

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        li = super(AbstractSkillWrapper, self).get_link()
        for el in self.constraint:
            li.append((self, el, "constraint"))
        return li

    # TODO: Not used method.
    def assert_level_is_positive(self, reference_level: int) -> 'Optional[AbstractSkillWrapper]':
        if reference_level > 0:
            return self
        else:
            return None

    # TODO: Not used method. (onConstraint만 사용됨)
    def createConstraint(self, const_name: str, const_ref: GraphElement, const_ftn: Callable[[], bool]) -> None:
        self.onConstraint(ConstraintElement(const_name, const_ref, const_ftn))

    def onConstraint(self, constraint: ConstraintElement) -> None:
        """주어진 제한 조건을 실행 ``constraint`` 목록에 추가합니다.
        해당 제한 조건이 만족되지 않을경우, 이 ``GraphElement``는 ``Scheduler`` 에 의해 실행되지 않습니다.

        이는 ``onAfter()`` 과 같은 chaining을 통한 실행은 막지 않습니다.

        Parameters
        ----------
        constraint : ConstraintElement
        """
        self.constraint.append(constraint)

    def set_disabled(self) -> ResultObject:
        """주어진 요소를 실행 불가 상태로 만듭니다.
        """
        raise NotImplementedError

    def set_disabled_and_time_left(self, time: float) -> ResultObject:
        """주어진 요소를 실행 불가 상태로 만들고, ``time`` 이후에 실행가능하도록 합니다.

        Parameters
        ----------
        time : float(ms)
        """
        raise NotImplementedError

    def reduce_cooltime(self, time: float) -> ResultObject:
        """주어진 요소의 남은 ``cooltime``을  ``time`` 만큼  감소시킵니다.

        Parameters
        ----------
        time : float(ms)
        """
        self.cooltime_left -= time
        return self._result_object_cache

    def reduce_cooltime_p(self, p: float) -> ResultObject:
        """주어진 요소의 남은 ``cooltime``을  ``p`` 만큼 비율로  감소시킵니다.

        Parameters
        ----------
        p : float
            0에서 1 사이의 값이어야 합니다. 1일 경우 모든 쿨타임이 제거됩니다. 0일 경우 아무 일도 일어나지 않습니다.
        """
        self.cooltime_left -= self.cooltime_left * p
        return self._result_object_cache

    def controller(self, time: float, type_: str = 'set_disabled_and_time_left', name: str = None) -> TaskHolder:
        """ ``AbstractSkillWrapper`` 의 시간을 제어하는 그래프 요소를 생성합니다.
        이 메서드는 ``TaskHolder`` 를 반환하므로, 반환된 요소를 다른 ``GraphElement`` 들의 ``onAfter`` 등을 통해 chaining할 수 있습니다.

        Parameters
        ----------
        time : float
            ``reduce_cooltime_p`` 인 경우 0에서 1 사이의 값, 그렇지 않을 경우 ms단위의 시간
        type_ : str
            set_disabled_and_time_left, reduce_cooltime, reduce_cooltime_p, set_enabled_and_time_left
        name : str(default:None)
            반환될 요소의 이름

        Returns
        -------
        element : TaskHolder
            실행될 경우, 해당 ``GraphElement`` 의 잔여 시간을 제어하는 ``TaskHolder``

        """
        if type_ == 'set_disabled':
            _name = "사용 종료"
            task = Task(self, self.set_disabled)
        elif type_ == 'set_disabled_and_time_left':
            if time == -1:
                _name = "사용 불가"
            else:
                _name = ("%.1f초이후 시전" % (time * 1.0 / 1000))
            task = Task(self, partial(self.set_disabled_and_time_left, time))
        elif type_ == 'reduce_cooltime':
            _name = ("쿨-%.1f초" % (time * 1.0 / 1000))
            task = Task(self, partial(self.reduce_cooltime, time))
        elif type_ == 'reduce_cooltime_p':
            _name = "쿨-" + str(int(time * 100)) + "%"
            task = Task(self, partial(self.reduce_cooltime_p, time))
        elif type_ == 'set_enabled_and_time_left':
            _name = ("%.1f초간 시전" % (time * 1.0 / 1000))
            task = Task(self, partial(self.set_enabled_and_time_left, time))
        else:
            raise TypeError("You must specify control type correctly.")
        if name is not None:
            return TaskHolder(task, name=name)
        else:
            return TaskHolder(task, name=_name)

    def _use(self, skill_modifier: SkillModifier, **kwargs) -> ResultObject:
        raise NotImplementedError

    def build_task(self, skill_modifier: SkillModifier) -> Task:
        if self._refer_runtime_context:
            task = self._build_task_with_referring_context(skill_modifier)
        else:
            task = Task(self, partial(self._use, skill_modifier))
        self.sync(task, skill_modifier)
        return task

    def _build_task_with_referring_context(self, skill_modifier: SkillModifier) -> ContextReferringTask:
        def context_referring_function(**kwargs) -> ResultObject:  # Task가 실행시킬 함수
            return self._use(skill_modifier, **kwargs)

        return ContextReferringTask(self, context_referring_function)

    def is_usable(self) -> bool:
        """이 ``GraphElement`` 가 실행가능한지 여부를 반환합니다.
        이 과정에서 ``constraint`` 들은 검사됩니다.
        """
        if len(self.constraint) > 0:
            for cnst in self.constraint:
                if not cnst.check():
                    return False
        return self.is_available()

    def is_available(self) -> bool:
        """이 ``GraphElement`` 가 실행가능한지 여부를 반환합니다.
        이 과정에서 ``constraint`` 들은 검사되지 않습니다.
        """
        return self.cooltime_left <= 0

    def is_not_usable(self) -> bool:
        """이 ``GraphElement`` 가 실행 불가능한지 여부를 반환합니다.
        이 과정에서 ``constraint`` 들은 검사됩니다.
        """
        return not self.is_usable()

    def spend_time(self, time: float) -> None:
        raise NotImplementedError

    def is_active(self) -> bool:
        """이 ``GraphElement`` 가 실행되고 있는지에 대한 여부를 반환합니다.
        지속 시간이 있는 객체에 대해서만 사용합니다.
        """
        return self.time_left > 0

    def is_not_active(self) -> bool:
        return not self.is_active()

    def is_cooltime_left(self, time: float, direction: int) -> bool:
        """남은 쿨타임이 ``time`` 과 비교할 때의 대소를 반환합니다.

        Parameters
        ----------
        time : float
            비교 기준이 되는 시간입니다.

        direction : 1 or -1
            direction > 0 이면 ``time`` 보다 남은 ``cooltime`` 이 길 경우 True입니다.
            direction < 0 이면 ``time`` 보다 남은 ``cooltime`` 이 짧을 경우 True입니다.
        """
        if (self.cooltime_left - time) * direction > 0:
            return True
        else:
            return False

    def is_time_left(self, time: float, direction: int) -> bool:
        """남은 지속시간이  ``time`` 과 비교할 때의 대소를 반환합니다.

        Parameters
        ----------
        time : float
            비교 기준이 되는 시간입니다.

        direction : 1 or -1
            direction > 0 이면 ``time`` 보다 남은 지속시간이 길 경우 True입니다.
            direction < 0 이면 ``time`` 보다 남은 지속시간이 짧을 경우 True입니다.
        """
        if (self.time_left - time) * direction > 0:
            return True
        else:
            return False

    def calculate_cooltime(self, skill_modifier: SkillModifier) -> float:
        """ ``skill_modifier`` 를 바탕으로, 주어진 ``Skill`` 의 실질적 쿨타임을 계산합니다.

        Parameters
        ----------
        skill_modifier : SkillModifier
            현재 스킬을 사용하는 ``Character`` 가 제공한 ``SkillModifier`` 입니다.
        """
        if self.skill.red is False:
            return self.get_cooltime()

        cooltime = self.get_cooltime()
        pcooltime_reduce = skill_modifier.pcooltime_reduce  # 쿨감%
        cooltime_reduce = skill_modifier.cooltime_reduce  # 쿨감+ (ms)

        if cooltime * (1 - 0.01 * pcooltime_reduce) <= 1000:  # 쿨감%부터 적용, 최소 1초까지
            cd = min(cooltime, 1000)
        else:
            cd = cooltime * (1 - 0.01 * pcooltime_reduce)

        if cd - cooltime_reduce <= 10000:
            cooltime_cap = min(10000, cd)
            cdr_left = (cooltime_reduce - (cd - cooltime_cap)) / 1000  # 10초 이하에서 쿨감되는 수치 계산
            cdr_applied = cooltime_cap * (1 - cdr_left * 0.05)  # 1초당 5%씩 감소
        else:
            cdr_applied = cd - cooltime_reduce

        return max(cdr_applied, min(cd, 5000))  # 5초까지 감소, 단 이미 스킬쿨이 5초 아래였을 경우 그대로 사용

    def get_cooltime(self) -> int:
        return self.skill.cooltime

    def onEventElapsed(self, graph_element: GraphElement, elapsed_time: float) -> None:
        """Invoke graph_element, after elapsed elapsed_time.
        Delay may considered as elapsed_time.
        """
        self._registered_callback_presets.append(('onEventElapsed', (graph_element, elapsed_time)))

    def onEventEnd(self, graph_element: GraphElement) -> None:
        """Invoke graph_element, after event ended.
        This only meaningful for duration-involved elements.
        """
        self._registered_callback_presets.append(('onEventEnd', (graph_element, 0)))

    def create_callbacks(self, duration=0, **kwargs) -> List[Callback]:
        """해당 object가 _use될 때 발생시키고자 하는 콜백들을 생성합니다.
        """
        callbacks = []
        for preset_type, context in self._registered_callback_presets:
            if preset_type == 'onEventEnd':
                assert duration > 0, 'duration may larger than 0 to use onEventEnd callback.'
                element = context[0]
                callbacks.append(Callback.from_graph_element(element, duration))
            elif preset_type == 'onEventElapsed':
                element, elapsed_time = context
                callbacks.append(Callback.from_graph_element(element, elapsed_time))

        return callbacks


class BuffSkillWrapper(AbstractSkillWrapper):
    def __init__(self, skill: BuffSkill, name: str = None) -> None:
        self._disabled_result_object_cache: ResultObject = ResultObject(0, CharacterModifier(), 0, 0, sname=skill.name, spec='graph control')
        super(BuffSkillWrapper, self).__init__(skill, name=name)
        self.set_flag(self.Flag_BuffSkill)
        self.disabled_modifier: CharacterModifier = CharacterModifier()
        self.modifier_invariant_flag: bool = True
        self.unique_flag: bool = True
        self.accessible_boss_state: int = AccessibleBossState.ALWAYS

    def set_enabled_and_time_left(self, time: float):
        """This function must be used carefully.. You must be sure about this skill's cooltime calculation i.e. -1
        """
        self.time_left = time
        self.cooltime_left = self.skill.cooltime

        mdf = self.get_modifier()
        return ResultObject(0, mdf, 0, 0, sname=self.skill.name, spec=self.skill.spec, kwargs={"remain": time})

    def set_disabled(self) -> ResultObject:
        self.time_left = 0
        return self._disabled_result_object_cache

    def set_disabled_and_time_left(self, time: float) -> ResultObject:
        self.time_left = 0
        self.cooltime_left = time
        if time == -1:
            self.cooltime_left = NOTWANTTOEXECUTE
        return self._disabled_result_object_cache

    def spend_time(self, time: float) -> None:  # TODO : can make this process more faster.. maybe
        self.time_left -= time
        self.cooltime_left -= time

    def _use(self, skill_modifier: SkillModifier) -> ResultObject:
        self.time_left = self.skill.remain * (1 + 0.01 * skill_modifier.buff_rem * self.skill.rem)
        self.cooltime_left = self.calculate_cooltime(skill_modifier)
        delay = self.get_delay()
        callbacks = self.create_callbacks(duration=self.time_left)
        return ResultObject(delay,
                            CharacterModifier(),
                            0,
                            0,
                            sname=self.skill.name,
                            spec=self.skill.spec,
                            kwargs={"remain": self.skill.remain * (1 + 0.01 * skill_modifier.buff_rem * self.skill.rem)},
                            callbacks=callbacks)

    def get_delay(self) -> int:
        return self.skill.delay

    def get_modifier(self) -> CharacterModifier:
        if self.is_active():
            return self.skill.get_modifier()
        else:
            return self.disabled_modifier

    def get_modifier_forced(self) -> CharacterModifier:
        return self.skill.get_modifier()


class StackSkillWrapper(BuffSkillWrapper):
    def __init__(self, skill: BuffSkill, max_: int, name: str = None) -> None:
        super(StackSkillWrapper, self).__init__(skill, name=name)
        self.stack: int = 0
        self._max: int = max_
        self._style: Optional[int] = None
        self.modifier_invariant_flag: bool = False

    def set_name_style(self, style) -> None:
        self._style = style

    def vary(self, d: int) -> ResultObject:
        self.stack = max(min((self.stack + d), self._max), 0)
        return ResultObject(0, CharacterModifier(), 0, 0, sname=self.skill.name, spec='graph control')

    def set_stack(self, d: int) -> ResultObject:
        self.stack = d
        return ResultObject(0, CharacterModifier(), 0, 0, sname=self.skill.name, spec='graph control')

    def get_modifier(self) -> CharacterModifier:
        return CharacterModifier()

    def stackController(self, d: int, name: str = None, dtype: str = 'vary') -> TaskHolder:
        if dtype == 'vary':
            task = Task(self, partial(self.vary, d))
        elif dtype == 'set':
            task = Task(self, partial(self.set_stack, d))
        else:
            raise TypeError('dtype must be vary or set, dtype: ' + str(dtype))
        if self._style is not None and name is None:
            name = self._style % d
        return TaskHolder(task, name=name)

    def judge(self, stack: int, direction: int) -> bool:
        return (self.stack - stack) * direction >= 0


class DamageSkillWrapper(AbstractSkillWrapper):
    def __init__(self, skill: DamageSkill, modifier: CharacterModifier = CharacterModifier(), name: str = None):
        super(DamageSkillWrapper, self).__init__(skill, name=name)
        self.modifier: CharacterModifier = modifier
        self._runtime_modifier_list: List[Tuple[AbstractSkillWrapper, Any]] = []
        self.accessible_boss_state: int = AccessibleBossState.NO_FLAG

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        li = super(DamageSkillWrapper, self).get_link()
        for sk, _ in self._runtime_modifier_list:
            li.append((self, sk, "modifier"))
        return li

    def set_disabled_and_time_left(self, time: float) -> ResultObject:
        self.cooltime_left = time
        if time == -1:
            self.cooltime_left = NOTWANTTOEXECUTE
        return ResultObject(0, CharacterModifier(), 0, 0, sname=self.skill.name, spec='graph control')

    def spend_time(self, time: float) -> None:
        self.cooltime_left -= time

    def _use(self, skill_modifier: SkillModifier) -> ResultObject:
        self.cooltime_left = self.calculate_cooltime(skill_modifier)
        callbacks = self.create_callbacks()
        return ResultObject(self.get_delay(),
                            self.get_modifier(),
                            self.get_damage(),
                            self.get_hit(),
                            sname=self.skill.name,
                            spec=self.skill.spec,
                            callbacks=callbacks)

    def get_delay(self) -> int:
        return self.skill.delay

    def get_damage(self) -> int:
        return self.skill.damage

    def get_hit(self) -> int:
        return self.skill.hit

    def get_modifier(self) -> CharacterModifier:
        modifier = self.skill.get_modifier() + self.modifier
        for skill, fn in self._runtime_modifier_list:
            modifier += fn(skill)
        return modifier

    def add_runtime_modifier(self, skill: AbstractSkillWrapper, fn) -> None:
        self._runtime_modifier_list.append((skill, fn))


class StackDamageSkillWrapper(DamageSkillWrapper):
    def __init__(self, skill: DamageSkill, stack_skill: AbstractSkillWrapper, fn,
                 modifier: CharacterModifier = CharacterModifier(), name: str = None) -> None:
        super(StackDamageSkillWrapper, self).__init__(skill, modifier=modifier, name=name)
        self.stack_skill: AbstractSkillWrapper = stack_skill
        self.fn = fn

    def get_damage(self) -> int:
        stack = self.fn(self.stack_skill)
        if stack <= 0:
            return 0
        return self.skill.damage

    def get_hit(self) -> int:
        stack = self.fn(self.stack_skill)
        return self.skill.hit * stack


class SummonSkillWrapper(AbstractSkillWrapper):
    def __init__(self, skill: SummonSkill, modifier: CharacterModifier = CharacterModifier(), name: str = None) -> None:
        super(SummonSkillWrapper, self).__init__(skill, name=name)
        self.tick: int = 0
        self.modifier: CharacterModifier = modifier
        self._runtime_modifier_list: List[Tuple[AbstractSkillWrapper, function]] = []
        self.disabled_modifier: CharacterModifier = CharacterModifier()
        self._on_tick: List[GraphElement] = []
        self.unique_flag: bool = True
        self.accessible_boss_state: int = AccessibleBossState.NO_FLAG
        self.is_periodic: bool = True

    def get_link(self) -> List[Tuple[GraphElement, GraphElement, str]]:
        li = super(SummonSkillWrapper, self).get_link()
        for el in self._on_tick:
            li.append((self, el, "tick"))
        for sk, _ in self._runtime_modifier_list:
            li.append((self, sk, "modifier"))
        return li

    def set_disabled(self) -> ResultObject:
        self.time_left = 0
        self.tick = 0
        return ResultObject(0, CharacterModifier(), 0, 0, sname=self.skill.name, spec='graph control')

    def set_disabled_and_time_left(self, time: float) -> ResultObject:
        self.cooltime_left = time
        self.time_left = -1
        self.tick = 0
        if time == -1:
            self.cooltime_left = NOTWANTTOEXECUTE
        return ResultObject(0, CharacterModifier(), 0, 0, sname=self.skill.name, spec='graph control')

    def need_count(self) -> bool:
        if self.is_active() and (self.tick < 0):
            return True
        else:
            return False

    def spend_time(self, time: float) -> None:
        self.time_left -= time
        self.cooltime_left -= time
        self.tick -= time

    # _use only alloted for start.
    def _use(self, skill_modifier: SkillModifier) -> ResultObject:
        self.tick = 0
        self.time_left = self.skill.remain * (1 + 0.01 * skill_modifier.summon_rem * self.skill.rem)
        self.cooltime_left = self.calculate_cooltime(skill_modifier)
        callbacks = self.create_callbacks(duration=self.time_left)
        return ResultObject(self.get_summon_delay(),
                            self.disabled_modifier,
                            0,
                            0,
                            sname=self.skill.name,
                            spec=self.skill.spec,
                            callbacks=callbacks)

    def _use_tick(self) -> ResultObject:
        if self.is_active() and self.tick <= 0:
            self.tick += self.get_delay()
            return ResultObject(0, self.get_modifier(), self.get_damage(), self.get_hit(), sname=self.skill.name, spec=self.skill.spec)
        else:
            return ResultObject(0, self.disabled_modifier, 0, 0, sname=self.skill.name, spec=self.skill.spec)

    def build_periodic_task(self, skill_modifier: SkillModifier) -> Task:
        task = Task(self, self._use_tick)
        task.onAfter([el.build_task(skill_modifier) for el in self._on_tick])
        return task

    def onTick(self, el: GraphElement) -> None:
        self._on_tick.append(el)

    def onTicks(self, ellist: List[GraphElement]) -> None:
        self._on_tick += ellist

    def get_summon_delay(self) -> int:
        return self.skill.summondelay

    def get_delay(self) -> int:
        return self.skill.delay

    def get_damage(self) -> int:
        return self.skill.damage

    def get_hit(self) -> int:
        return self.skill.hit

    def get_modifier(self) -> CharacterModifier:
        modifier = self.skill.get_modifier() + self.modifier
        for skill, fn in self._runtime_modifier_list:
            modifier += fn(skill)
        return modifier

    def add_runtime_modifier(self, skill: AbstractSkillWrapper, fn) -> None:
        self._runtime_modifier_list.append((skill, fn))


class Simulator(object):
    __slots__ = 'scheduler', 'character', 'analytics', '_modifier_cache_and_time', '_default_modifier'

    def __init__(self, scheduler: 'AdvancedGraphScheduler', chtr: 'AbstractCharacter', analytics: 'Analytics'):
        self.scheduler: AdvancedGraphScheduler = scheduler
        self.character: AbstractCharacter = chtr
        self.analytics: Analytics = analytics

        # TODO: Not used attribute.
        # Buff modifier를 시간별도 캐싱하여 연산량을 줄입니다.
        self._modifier_cache_and_time: List[Union[int, CharacterModifier]] = [-1, CharacterModifier()]

        self._default_modifier: CharacterModifier = CharacterModifier()

    def set_default_modifier(self, modifier: CharacterModifier) -> None:
        self._default_modifier = modifier

    def get_default_modifier(self) -> CharacterModifier:
        return self._default_modifier

    def get_skill_info(self) -> Dict[str, Any]:
        return self.analytics.get_skill_info()

    def get_results(self) -> List[Dict[str, Any]]:
        return self.analytics.get_results()

    def get_metadata(self) -> Dict[str, float]:
        mod = self.character.get_buffed_modifier()
        return self.analytics.get_metadata(mod)

    def getDPM(self, restricted: bool = True) -> float:
        if not restricted:
            return self.get_unrestricted_DPM()
        else:
            return self.analytics.total_damage / self.scheduler.total_time_initial * 60000

    def get_unrestricted_DPM(self) -> float:
        return self.analytics.total_damage_without_restriction / self.scheduler.total_time_initial * 60000

    # TODO: Not used method.
    def getTotalDamage(self) -> float:
        return self.analytics.total_damage

    def start_simulation(self, time: int) -> None:
        self._modifier_cache_and_time = [-1, CharacterModifier()]
        self.scheduler.initialize(time)
        self.analytics.set_total_runtime(time)
        self.analytics.chtrmdf = self.character.get_modifier()
        self.character.generate_modifier_cache()  # 캐릭터의 Modifier를 매번 재계산 할 필요가 없으므로 (캐릭터의 상태는 시뮬레이션 도중 변화하지 않음) 캐싱하여 연산 자원을 절약합니다.
        while not self.scheduler.is_simulation_end():
            task = self.scheduler.dequeue()
            try:
                self.run_task_recursive(task)
            except Exception as e:
                print(task._ref._id)
                print("error raised")
                print("---")
                raise e

    def parse_result(self, result: ResultObject) -> None:
        runtime_context_modifier = self.scheduler.get_buff_modifier() + self.get_default_modifier()
        result.setTime(self.scheduler.get_current_time())

        if result.damage > 0:
            result.mdf += runtime_context_modifier

        self.analytics.analyze(self.character, result)

    def run_task_recursive(self, task: Task) -> None:
        for t in reversed(task._before):
            self.run_task_recursive(t)

        runtime_context_modifier = self.scheduler.get_buff_modifier() + self.get_default_modifier()
        result = task.do(runtime_context_modifier=runtime_context_modifier + self.character.get_modifier())
        self.parse_result(result)

        for t in task._justAfter:
            self.run_task_recursive(t)

        if result.delay > 0:
            time_to_spend = result.delay
            while True:
                callback, time_to_spend = self.scheduler.apply_result(result, time_to_spend)
                if self.scheduler.is_simulation_end():
                    return
                if callback:
                    result = callback.resolve()
                    self.parse_result(result)
                else:
                    break

            while True:
                tick = self.scheduler.get_delayed_task()
                if tick is not None:
                    self.run_task_recursive(tick)
                else:
                    break

        for t in reversed(result.cascade + task._after):
            self.run_task_recursive(t)


class Analytics:
    def __init__(self, printFlag: bool = False) -> None:
        self.total_time: float = 0
        self.total_damage: float = 0
        self.total_damage_without_restriction: float = 0
        self.log_list: List[Dict[str, Any]] = []
        self.meta_save = {}  # TODO: Not used attribute.
        self.print_calculation_progress: bool = printFlag
        self.skill_list: Dict[str, Dict] = {}
        self.chtrmdf: CharacterModifier = CharacterModifier()

    def set_total_runtime(self, time: float) -> None:
        self.total_time = time

    def analyze(self, chtr: 'AbstractCharacter', result: ResultObject) -> None:
        self.add_damage_from_result_with_log(chtr.get_modifier(), result)

    def get_skill_info(self) -> Dict[str, Any]:
        return {"dict": self.skill_list, "li": list(self.skill_list.keys())}

    def get_metadata(self, mod: CharacterModifier) -> Dict[str, float]:
        meta = {"stat_main": mod.stat_main,
                "stat_sub": mod.stat_sub,
                "stat_main_fixed": mod.stat_main_fixed,
                "pstat_main": mod.pstat_main,
                "att": mod.att,
                "patt": mod.patt,
                "pdamage": mod.pdamage + mod.boss_pdamage,
                "boss_pdamage": mod.boss_pdamage,
                "armor_ignore": mod.armor_ignore,
                "pdamage_indep": mod.pdamage_indep,
                "effective_status": mod.get_status_factor(),
                "crit_damage": mod.crit_damage,
                "crit": mod.crit
                }

        return meta

    def statistics(self) -> None:
        print("Total damage %.1f in %d second" % (self.total_damage, self.total_time / 1000))
        print(f"Loss {self.total_damage_without_restriction - self.total_damage:.1f}")

        def getSkillNames(log_list) -> List[str]:
            return sorted(set(map(lambda log: log["result"].sname, log_list)))

        print("\n===Buff Skills===")
        buffList = list(filter(lambda log: log["result"].spec == "buff", self.log_list))
        names = getSkillNames(buffList)
        for name in names:
            skillLog = list(filter(lambda log: log["result"].sname == name, buffList))
            use = len(skillLog)
            delay = sum(map(lambda log: log["result"].delay, skillLog))
            print(f"{name} Used {use} Delay {delay}")

        shareDict = defaultdict(int)

        print("\n===Damage Skills===")
        damageList = list(filter(lambda log: log["result"].spec == "damage", self.log_list))
        names = getSkillNames(damageList)
        for name in names:
            skillLog = list(filter(lambda log: log["result"].sname == name, damageList))
            use = len(skillLog)
            hit = sum(map(lambda log: log["result"].hit, skillLog))
            damage = sum(map(lambda log: log["deal"], skillLog))
            loss = sum(map(lambda log: log["loss"], skillLog))
            delay = sum(map(lambda log: log["result"].delay, skillLog))
            share = damage / self.total_damage * 100
            shareDict[name.split('(')[0]] += share
            print(f"{name} Used {use} Delay {delay}")
            print(f"Hit {hit} Damage {damage:.1f} Loss {loss:.1f}")
            print(f"Share {share:.4f}%")

        print("\n===Summon/DoT Skills===")
        summonList = list(filter(lambda log: log["result"].spec in ["summon", "dot"], self.log_list))
        names = getSkillNames(summonList)
        for name in names:
            skillLog = list(filter(lambda log: log["result"].sname == name, summonList))
            summon = len(list(filter(lambda log: log["deal"] == 0, skillLog)))
            use = len(skillLog) - summon
            hit = sum(map(lambda log: log["result"].hit, skillLog))
            damage = sum(map(lambda log: log["deal"], skillLog))
            loss = sum(map(lambda log: log["loss"], skillLog))
            delay = sum(map(lambda log: log["result"].delay, skillLog))
            share = damage / self.total_damage * 100
            shareDict[name.split('(')[0]] += share
            print(f"{name} Summoned {summon} Delay {delay}")
            print(f"Used {use} Hit {hit}")
            print(f"Damage {damage:.1f} Loss {loss:.1f}")
            print(f"Share {share:.4f}%")

        print("\n===Skill Share===")
        for name, share in sorted(shareDict.items(), key=lambda x: x[1], reverse=True):
            if share > 0:
                print(f"{name}, {share:.4f}%")

        # self.log("Percent damage per second is %.2f" % (100*self.total_damage / self.character.get_modifier().get_damage_factor() / self.totalTimeInitial * 1000))

    def skill_share(self) -> Dict[str, int]:
        damageDict = {}
        for log in self.log_list:
            if log["deal"] > 0:
                if log["result"].sname not in damageDict:
                    damageDict[log["result"].sname] = 0
                damageDict[log["result"].sname] += log["deal"]

        return damageDict

    def get_results(self) -> List[Dict[str, Any]]:
        retli = []
        for log in self.log_list:
            retli.append({"time": log["time"],
                          "sname": log["result"].sname,
                          "deal": log["deal"],
                          "spec": log["result"].spec,
                          "else": log["result"].kwargs})
        return retli

    # TODO: Not used method.
    def analyzeVEfficiency(self) -> None:
        """V Core 각각의 효율을 계산합니다!
        """
        damage_list_v_skill = []  # 5차 스킬의 데미지를 저장합니다.
        damage_list_enhanced_skill = []  # 강화 스킬의 데미지를 저장합니다.

        return

    def add_damage_from_result_with_log(self, charmdf: CharacterModifier, result: ResultObject) -> None:
        if result.damage > 0:
            mdf = charmdf + result.mdf

            deal, loss = mdf.calculate_damage(result.damage, result.hit, result.spec)
            free_deal = deal + loss

            # free_deal = mdf.get_damage_factor() * result.damage * 0.01
            # deal = min(result.hit * MAX_DAMAGE_RESTRICTION, free_deal)
        else:
            deal = 0
            free_deal = 0

        if deal > 0:
            self.total_damage += deal
            self.total_damage_without_restriction += free_deal

        # For speed acceleration
        if self.print_calculation_progress:
            print('At Time %.1f, Skill [%s] ... Damage [%.1f] ... Loss [%.1f] ... Delay [%.1f] ... Spec [%s]' % (
                result.time, result.sname, deal, free_deal - deal, result.delay, result.spec))
            print(f'{result.mdf}')
        if deal > 0:
            self.log_list.append({"result": result, "time": result.time, "deal": deal, "loss": free_deal - deal})
        else:
            self.log_list.append({"result": result, "time": result.time, "deal": 0, "loss": 0})
        if result.sname not in self.skill_list:
            self.skill_list[result.sname] = {}

    def deduce_increment_of_temporal_modifier(self, continue_time_length: int, temporal_modifier: CharacterModifier,
                                              search_time_scan_rate: int = 1000) -> Dict[str, float]:
        def search_time_index(time: float, hoping_rate_init: int = 100) -> int:
            hoping_rate = hoping_rate_init
            time_index = 0
            while True:
                if time_index >= len(self.log_list):
                    time_index = len(self.log_list) - 1
                    break
                if self.log_list[time_index]["time"] < time:
                    time_index += hoping_rate
                else:
                    if self.log_list[time_index - 1]["time"] <= time:
                        break
                    else:
                        hoping_rate = max(1, hoping_rate // 2)
                        time_index -= hoping_rate
                        time_index = max(0, time_index)
                        if time_index == 0:
                            return 0

            return time_index

        def get_damage_sum_in_time_interval(time_start: int, time_length: int) -> int:
            damage_sum = 0
            time_log_index = max(0, search_time_index(time_start))
            # print("start_time_index", time_log_index, time_start)

            while time_start <= self.log_list[time_log_index]["time"] <= time_start + time_length:
                damage_sum += self.log_list[time_log_index]["deal"]
                time_log_index += 1
                if time_log_index >= len(self.log_list):
                    break

            for t in range(time_log_index, time_log_index + 20):
                if t < len(self.log_list):
                    if time_start + time_length >= self.log_list[t]["time"] >= time_start:
                        damage_sum += self.log_list[time_log_index]["deal"]

            # print("end_time_index", time_log_index)

            # print("log",time_start, time_length, damage_sum)
            return damage_sum

        # search_time_scan_rate : 기록되어 있는 로그를 스캔할 시간주기입니다. 기본값 : 1000(ms)

        # scanning algorithm
        maximal_time_loc = 0
        damage_log_queue = [get_damage_sum_in_time_interval(i * search_time_scan_rate, search_time_scan_rate) for i in
                            range(continue_time_length // search_time_scan_rate)]
        maximal_damage = sum(damage_log_queue)

        scanning_end_time = (continue_time_length // search_time_scan_rate) * search_time_scan_rate

        while scanning_end_time < self.total_time:
            damage_log_queue.pop(0)
            damage_log_queue.append(get_damage_sum_in_time_interval(scanning_end_time, search_time_scan_rate))
            if sum(damage_log_queue) > maximal_damage:
                maximal_time_loc = scanning_end_time - continue_time_length
                maximal_damage = sum(damage_log_queue)
            scanning_end_time += search_time_scan_rate

        # Now we know when damage is maximized. We now apply our modifier into this.

        total_damage = 0
        for log in self.log_list:
            result = log["result"]
            if result.damage > 0:
                mdf = self.chtrmdf + result.mdf
                if maximal_time_loc <= log["time"] < maximal_time_loc + continue_time_length:
                    mdf += temporal_modifier
                deal, loss = mdf.calculate_damage(result.damage, result.hit, result.spec)
                total_damage += deal

        simple_increment = ((self.chtrmdf + temporal_modifier).get_damage_factor() / (
            self.chtrmdf.get_damage_factor()) - 1) * (continue_time_length / self.total_time)

        return {"damage": (total_damage - self.total_damage) * (60000 / self.total_time),
                "increment": (total_damage / self.total_damage) - 1, "simple_increment": simple_increment}


class BasicVEnhancer(AbstractVEnhancer):
    def __init__(self) -> None:
        #### value list ####
        self.enhance_list: List[int] = []
        self.v_skill_list: List[int] = []
        self.core_float = None  # TODO: Not used attribute.

        #### analytics list ####
        self.enhancer_priority: List[List[AbstractSkill]] = []  # 5차의 강화스킬 순서
        self.v_skill_priority: List[Dict[str, Any]] = []  # 5차의 사용스킬 순서

    def get_priority(self) -> Dict[str, List[Dict[str, Any]]]:
        v_skill_list_sorted: List[List[Dict[str, Any]]] = [[] for i in range(20)]  # 20 is magic float
        for vskill in self.v_skill_priority:
            v_skill_list_sorted[vskill["useIdx"]].append(vskill)

        return {
            "enhance": [{"name": skills[0].name.split('(')[0]} for skills in self.enhancer_priority if len(skills) > 0],
            "vskill": [{"name": skills[0]["target"].name.split('(')[0]} for skills in v_skill_list_sorted if len(skills) > 0]}

    def set_state_direct(self, li: List[int]) -> None:
        self.enhance_list = li
        self.enhancer_priority = [[] for i in li]

    def set_vlevel_direct(self, li: List[int]) -> None:
        self.v_skill_list = li

    def get_reinforcement_with_register(self, index: int, incr, crit: bool, target: AbstractSkill) -> CharacterModifier:
        self.enhancer_priority[index].append(target)

        if index >= len(self.enhance_list):
            return CharacterModifier()
        else:
            return VSkillModifier.get_reinforcement(incr, self.enhance_list[index], crit)

    def getV(self, use_index: int, upgrade_index: int) -> int:
        if use_index <= len(self.v_skill_list):
            return self.v_skill_list[upgrade_index]

    def add_v_skill(self, target: AbstractSkill, use_index: int, upgrade_index: int) -> None:
        self.v_skill_priority.append({"target": target, "useIdx": use_index, "upgIdx": upgrade_index})

    def copy(self) -> 'BasicVEnhancer':
        retval = BasicVEnhancer()
        retval.set_state_direct(self.enhance_list)
        retval.set_vlevel_direct(self.v_skill_list)
        return retval

    def __repr__(self) -> str:
        return "VEnhancer :: dpmModule.jobs.template\nVEnhance : %s\nVSkill : %s" % (
        str(self.enhance_list), str(self.v_skill_list))


class DirectVBuilder(AbstractVBuilder):
    def __init__(self, direct_enhance_state: List[int], direct_v_state: List[int]) -> None:
        super().__init__()
        self.direct_enhance_state: List[int] = direct_enhance_state
        self.direct_v_state: List[int] = direct_v_state

    def build_enhancer(self, character, generator) -> BasicVEnhancer:
        enhancer = BasicVEnhancer()
        enhancer.set_state_direct(self.direct_enhance_state)
        enhancer.set_vlevel_direct(self.direct_v_state)
        return enhancer


class AlwaysMaximumVBuilder(AbstractVBuilder):
    def __init__(self) -> None:
        super().__init__()

    # TODO: character, generator are not used.
    def build_enhancer(self, character, generator) -> BasicVEnhancer:
        enhancer = BasicVEnhancer()
        enhancer.set_state_direct([60 for i in range(15)])
        enhancer.set_vlevel_direct([30 for i in range(15)])
        return enhancer


class NjbStyleVBuilder(AbstractVBuilder):
    def __init__(self, skill_core_level: int = 25, each_enhanced_amount: int = 17) -> None:
        super().__init__()
        self.skill_core_level: int = skill_core_level
        self.each_enhanced_amount: int = each_enhanced_amount

    def build_enhancer(self, character: 'AbstractCharacter', generator: 'JobGenerator') -> BasicVEnhancer:
        level = character.level
        cores = generator.vSkillNum
        return self.set_state_from_level_and_skill_cores(level, cores, self.skill_core_level, self.each_enhanced_amount)

    # TODO: each_enhanced_amount is not used.
    def set_state_from_level_and_skill_cores(self, level: int, skill_cores: int, skill_core_level: int,
                                             each_enhanced_amount) -> BasicVEnhancer:
        total_core_slots = 6 + (level - 200) // 5
        available_core_slots = max(total_core_slots - skill_cores, 0)
        level_bonus = level - 200

        enhance_state_will_be_setted = [0 for i in range(16)]

        if available_core_slots < 3:
            for i in range(available_core_slots):
                for j in range(3):
                    enhance_state_will_be_setted[j] += 17
        else:
            for i in range(available_core_slots):
                enhance_state_will_be_setted[i] = 50

        while level_bonus > 0:
            chance_for_upgrade = min(level_bonus, 5)
            target_upgrade_skill_index = 0

            enhancement_left = 3  # 하나의 코어는 3개의 스킬을 강화합니다.
            while target_upgrade_skill_index < len(enhance_state_will_be_setted) and enhancement_left > 0:
                if enhance_state_will_be_setted[target_upgrade_skill_index] < 60:
                    maximum_upgrade_level_available = 60 - enhance_state_will_be_setted[target_upgrade_skill_index]
                    actual_chance_for_upgrade = min(chance_for_upgrade, maximum_upgrade_level_available)
                    enhance_state_will_be_setted[target_upgrade_skill_index] += actual_chance_for_upgrade
                    enhancement_left -= 1

                target_upgrade_skill_index += 1

            level_bonus -= chance_for_upgrade

        enhancer = BasicVEnhancer()
        enhancer.set_state_direct(enhance_state_will_be_setted)
        enhancer.set_vlevel_direct([(i < skill_cores) * skill_core_level for i in range(10)])
        return enhancer
