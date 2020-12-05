from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from .constant import FINAL_DAMAGE_RATIO, MAX_DAMAGE_RESTRICTION, ARMOR_RATE
from ..graph import DynamicVariableInstance, DynamicVariableOperation


class CharacterModifier:
    __slots__ = (
        "crit",
        "crit_damage",
        "pdamage",
        "pdamage_indep",
        "stat_main",
        "stat_sub",
        "pstat_main",
        "pstat_sub",
        "boss_pdamage",
        "armor_ignore",
        "patt",
        "att",
        "stat_main_fixed",
        "stat_sub_fixed",
    )
    """CharacterModifier : Holds information about character modifiing factors ex ) pdamage, stat, att%, etc.AbstractSkill
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

    """

    def __init__(
        self,
        crit: float = 0,
        crit_damage: float = 0,
        pdamage: float = 0,
        pdamage_indep: float = 0,
        stat_main: float = 0,
        stat_sub: float = 0,
        pstat_main: float = 0,
        pstat_sub: float = 0,
        boss_pdamage: float = 0,
        armor_ignore: float = 0,
        patt: float = 0,
        att: float = 0,
        stat_main_fixed: float = 0,
        stat_sub_fixed: float = 0,
    ) -> None:
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

    def __iadd__(self, arg: CharacterModifier) -> CharacterModifier:
        self.crit += arg.crit
        self.crit_damage += arg.crit_damage
        self.pdamage += arg.pdamage
        self.pdamage_indep += (
            arg.pdamage_indep + (self.pdamage_indep * arg.pdamage_indep) * 0.01
        )
        self.stat_main += arg.stat_main
        self.stat_sub += arg.stat_sub
        self.pstat_main += arg.pstat_main
        self.pstat_sub += arg.pstat_sub
        self.boss_pdamage += arg.boss_pdamage
        self.armor_ignore = 100 - 0.01 * (
            (100 - self.armor_ignore) * (100 - arg.armor_ignore)
        )
        self.patt += arg.patt
        self.att += arg.att
        self.stat_main_fixed += arg.stat_main_fixed
        self.stat_sub_fixed += arg.stat_sub_fixed
        return self

    def __add__(self, arg: CharacterModifier) -> CharacterModifier:
        return CharacterModifier(
            crit=(self.crit + arg.crit),
            crit_damage=(self.crit_damage + arg.crit_damage),
            pdamage=(self.pdamage + arg.pdamage),
            pdamage_indep=self.pdamage_indep
            + arg.pdamage_indep
            + (self.pdamage_indep * arg.pdamage_indep) * 0.01,
            stat_main=(self.stat_main + arg.stat_main),
            stat_sub=(self.stat_sub + arg.stat_sub),
            pstat_main=(self.pstat_main + arg.pstat_main),
            pstat_sub=(self.pstat_sub + arg.pstat_sub),
            boss_pdamage=(self.boss_pdamage + arg.boss_pdamage),
            armor_ignore=100
            - 0.01 * ((100 - self.armor_ignore) * (100 - arg.armor_ignore)),
            patt=(self.patt + arg.patt),
            att=(self.att + arg.att),
            stat_main_fixed=(self.stat_main_fixed + arg.stat_main_fixed),
            stat_sub_fixed=(self.stat_sub_fixed + arg.stat_sub_fixed),
        )

    def __sub__(self, arg: CharacterModifier) -> CharacterModifier:
        return CharacterModifier(
            crit=(self.crit - arg.crit),
            crit_damage=(self.crit_damage - arg.crit_damage),
            pdamage=(self.pdamage - arg.pdamage),
            pdamage_indep=(100 + self.pdamage_indep) / (100 + arg.pdamage_indep) * 100
            - 100,
            stat_main=(self.stat_main - arg.stat_main),
            stat_sub=(self.stat_sub - arg.stat_sub),
            pstat_main=(self.pstat_main - arg.pstat_main),
            pstat_sub=(self.pstat_sub - arg.pstat_sub),
            boss_pdamage=(self.boss_pdamage - arg.boss_pdamage),
            armor_ignore=100
            - 100 * (100 - self.armor_ignore) / (100 - arg.armor_ignore),
            patt=(self.patt - arg.patt),
            att=(self.att - arg.att),
            stat_main_fixed=(self.stat_main_fixed - arg.stat_main_fixed),
            stat_sub_fixed=(self.stat_sub_fixed - arg.stat_sub_fixed),
        )

    def copy(self) -> CharacterModifier:
        return CharacterModifier(
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
            stat_sub_fixed=self.stat_sub_fixed,
        )

    def extend(self) -> ExtendedCharacterModifier:
        return ExtendedCharacterModifier(
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
            stat_sub_fixed=self.stat_sub_fixed,
        )

    def get_damage_factor(self, armor: float = ARMOR_RATE) -> float:
        """Caution : Use this function only if you summed up every modifiers."""
        real_crit = min(100, self.crit)
        stat = (
            4 * self.stat_main * (1 + 0.01 * self.pstat_main)
            + self.stat_sub * (1 + 0.01 * self.pstat_sub)
        ) + (4 * self.stat_main_fixed + self.stat_sub_fixed)
        adap = self.att * (1 + 0.01 * self.patt)
        factor = (
            (1 + 0.0001 * max(0, real_crit) * (self.crit_damage + 35))
            * (1 + 0.01 * (max(self.pdamage + self.boss_pdamage, 0)))
            * (1 + 0.01 * self.pdamage_indep)
        )
        ignorance = max((100 - armor * (1 - 0.01 * self.armor_ignore)) * 0.01, 0)
        return stat * adap * factor * ignorance * 0.01

    # TODO: Parameter armor is not used.
    def get_status_factor(self, armor: float = ARMOR_RATE) -> float:
        """Caution : Use this function only if you summed up every modifiers."""
        stat = (
            4 * self.stat_main * (1 + 0.01 * self.pstat_main)
            + self.stat_sub * (1 + 0.01 * self.pstat_sub)
        ) + (4 * self.stat_main_fixed + self.stat_sub_fixed)
        adap = self.att * (1 + 0.01 * self.patt)
        factor = (1 + 0.01 * self.pdamage) * (1 + 0.01 * self.pdamage_indep)
        return stat * adap * factor * 0.01

    def calculate_damage(
        self, damage: float, hit: float, spec: str, armor: float = ARMOR_RATE
    ) -> Tuple[float, float]:
        """Return : (damage, loss) tuple
        숙련도는 90~100으로 가정함(5% deviation)
        """

        def restricted_damage(
            x1: float, x2: float, y1: float, y2: float, M: float
        ) -> float:
            """Calculated expected value of min(M, xy) in [x1~x2, y1~y2]"""
            normalizer = (x2 - x1) * (y2 - y1)
            basis = (x1 + x2) / 2 * (y1 + y2) / 2

            if M > x2 * y2:
                return basis
            else:
                if M > x1 * y2 and M > x2 * y1:
                    x_p = M / y2
                    # Case 1
                    excess = (
                        M * y2 * (x2 - x_p)
                        - (y2 * y2 / 4) * (x2 * x2 - x_p * x_p)
                        - (M * M / 2) * math.log(x2 / x_p)
                    )
                    return basis + excess / normalizer

                elif x1 * y2 > M > x2 * y1:
                    # Case 2
                    x_p = x1
                    # Case 1
                    excess = (
                        M * y2 * (x2 - x_p)
                        - (y2 * y2 / 4) * (x2 * x2 - x_p * x_p)
                        - (M * M / 2) * math.log(x2 / x_p)
                    )
                    return basis + excess / normalizer

                elif x1 * y2 < M < x2 * y1:
                    # Case 3 -> change to Case 2
                    return restricted_damage(y1, y2, x1, x2, M)

                elif M > x1 * y1:
                    x_p = M / y1
                    excess = (
                        M * y1 * (x_p - x1)
                        - (y1 * y1 / 4) * (x_p * x_p - x1 * x1)
                        - (M * M / 2) * math.log(x_p / x1)
                    )
                    return M + excess / normalizer

                else:
                    return M

        # Optimized
        real_crit = min(100, self.crit)
        stat = (
            4 * self.stat_main * (1 + 0.01 * self.pstat_main)
            + self.stat_sub * (1 + 0.01 * self.pstat_sub)
        ) + (4 * self.stat_main_fixed + self.stat_sub_fixed)
        adap = self.att * (1 + 0.01 * self.patt)
        factor_crit_removed = (
            1 + 0.01 * (max(self.pdamage + self.boss_pdamage, 0))
        ) * (1 + 0.01 * self.pdamage_indep)
        ignorance = max((100 - armor * (1 - 0.01 * self.armor_ignore)) * 0.01, 0)
        expert_max = 100 / 95
        expert_min = 90 / 95

        if spec == "dot":
            real_crit = 0
            factor_crit_removed = 1
            ignorance = 1
            expert_min = expert_max

        factor_aggregated = (
            stat * adap * factor_crit_removed * ignorance * damage * 0.0001
        )

        max_crit_factor = 1 + 0.0001 * max(0, real_crit) * (self.crit_damage + 50)
        min_crit_factor = 1 + 0.0001 * max(0, real_crit) * (self.crit_damage + 20)

        max_damage_factor = factor_aggregated * expert_max * FINAL_DAMAGE_RATIO
        min_damage_factor = factor_aggregated * expert_min * FINAL_DAMAGE_RATIO

        real_damage = (
            hit
            * (max_crit_factor + min_crit_factor)
            / 2
            * (max_damage_factor + min_damage_factor)
            / 2
        )  # W/O restriction
        res_damage = hit * restricted_damage(
            min_damage_factor,
            max_damage_factor,
            min_crit_factor,
            max_crit_factor,
            MAX_DAMAGE_RESTRICTION,
        )  # W/ restriction

        return (res_damage, real_damage - res_damage)

    def log(self) -> str:
        txt = "crit rate : %.1f, crit damage : %.1f\n" % (self.crit, self.crit_damage)
        txt += "pdamage : %.1f, pdamage_indep : %.1f\n" % (
            self.pdamage,
            self.pdamage_indep,
        )
        txt += "stat_main : %.1f, stat_sub : %.1f\n" % (self.stat_main, self.stat_sub)
        txt += "pstat_main : %.1f, pstat_sub : %.1f\n" % (
            self.pstat_main,
            self.pstat_sub,
        )
        txt += "stat_main_fixed : %.1f, stat_sub_fixed : %.1f\n" % (
            self.stat_main_fixed,
            self.stat_sub_fixed,
        )
        txt += "boss_pdamage : %.1f, armor_ignore : %.1f\n" % (
            self.boss_pdamage,
            self.armor_ignore,
        )
        txt += "att : %.1f, patt : %.1f\n" % (self.att, self.patt)
        txt += "damageFactor : %.1f\n" % (self.get_damage_factor())
        return txt

    def __repr__(self) -> str:
        return self.log()

    def abstract_log_list(
        self, lang: str = "ko"
    ) -> List[Tuple[str, float, Optional[str]]]:
        crit_rate_formal = (math.floor(self.crit * 10)) / 10
        if crit_rate_formal < 0:
            crit_rate_formal = "미발동"
        el: List[Tuple[str, float, Optional[str]]]
        if lang == "ko":
            el = [
                ("크리티컬 확률", crit_rate_formal, "%"),
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
                ("방무", math.floor(self.armor_ignore * 10) / 10, "%"),
            ]
        elif lang == "en":
            el = [
                ("crit rate", self.crit),
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
                ("armor ignorance", self.armor_ignore),
            ]
        else:
            raise TypeError("lang must be ko or en, lang: " + str(lang))
        retel = []
        for i in el:
            if i[1] != 0:
                retel.append(i)
        return retel

    def as_dict(self) -> Dict[str, float]:
        return {
            "crit": self.crit,
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
            "stat_sub_fixed": self.stat_sub_fixed,
        }

    # TODO: Not used method.
    def _dynamic_variable_hint(
        self, character_modifier: CharacterModifier
    ) -> Optional[DynamicCharacterModifier]:
        if not isinstance(character_modifier, DynamicCharacterModifier):
            return DynamicCharacterModifier(
                crit=character_modifier.crit,
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
                stat_sub_fixed=character_modifier.stat_sub_fixed,
            )
        else:
            return None


class DynamicCharacterModifier(DynamicVariableInstance, CharacterModifier):
    def __init__(self, **kwargs) -> None:
        DynamicVariableInstance.__init__(self)
        parsed_kwargs = {
            k: DynamicVariableOperation.wrap_argument(a) for k, a in kwargs.items()
        }
        for k, a in parsed_kwargs.items():
            self.add_next_instance(a)
            a.inherit_namespace(k)
        CharacterModifier.__init__(self, **parsed_kwargs)

    def evaluate_override(self) -> CharacterModifier:
        return CharacterModifier(
            crit=self.crit.evaluate(),
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
            stat_sub_fixed=self.stat_sub_fixed.evaluate(),
        )


class SkillModifier:
    def __init__(
        self,
        buff_rem: float = 0,
        summon_rem: float = 0,
        cooltime_reduce: float = 0,
        pcooltime_reduce: float = 0,
        reuse_chance: float = 0,
    ) -> None:
        self.buff_rem: float = buff_rem
        self.summon_rem: float = summon_rem
        self.cooltime_reduce: float = cooltime_reduce
        self.pcooltime_reduce: float = pcooltime_reduce
        self.reuse_chance: float = reuse_chance

    def copy(self) -> SkillModifier:
        return SkillModifier(
            buff_rem=self.buff_rem,
            summon_rem=self.summon_rem,
            cooltime_reduce=self.cooltime_reduce,
            pcooltime_reduce=self.pcooltime_reduce,
            reuse_chance=self.reuse_chance,
        )

    def __add__(self, arg: SkillModifier) -> SkillModifier:
        return SkillModifier(
            buff_rem=self.buff_rem + arg.buff_rem,
            summon_rem=self.summon_rem + arg.summon_rem,
            cooltime_reduce=self.cooltime_reduce + arg.cooltime_reduce,
            pcooltime_reduce=self.pcooltime_reduce + arg.pcooltime_reduce,
            reuse_chance=self.reuse_chance + arg.reuse_chance,
        )


class ExtendedCharacterModifier(CharacterModifier):
    def __init__(
        self,
        buff_rem: float = 0,
        summon_rem: float = 0,
        cooltime_reduce: float = 0,
        pcooltime_reduce: float = 0,
        reuse_chance: float = 0,
        prop_ignore: float = 0,
        additional_target: int = 0,
        passive_level: int = 0,
        **kwargs
    ) -> None:
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
        txt += "cooltime_reduce : %.1f, pcooltime_reduce : %.1f\n" % (
            self.cooltime_reduce,
            self.pcooltime_reduce,
        )
        txt += "reuse_chance : %.1f, prop_ignore : %.1f\n" % (
            self.reuse_chance,
            self.prop_ignore,
        )
        txt += "additional_target : %d, passive_level : %d\n" % (
            self.additional_target,
            self.passive_level,
        )
        return txt

    def copy(self) -> ExtendedCharacterModifier:
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
            stat_sub_fixed=self.stat_sub_fixed,
        )

    def degenerate(self) -> CharacterModifier:
        return super(ExtendedCharacterModifier, self).copy()

    def to_skill_modifier(self) -> SkillModifier:
        return SkillModifier(
            buff_rem=self.buff_rem,
            summon_rem=self.summon_rem,
            cooltime_reduce=self.cooltime_reduce,
            pcooltime_reduce=self.pcooltime_reduce,
            reuse_chance=self.reuse_chance,
        )

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
            "passive_level": self.passive_level,
        }

    def __iadd__(self, arg: ExtendedCharacterModifier) -> ExtendedCharacterModifier:
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
        self.pdamage_indep += (
            arg.pdamage_indep + (self.pdamage_indep * arg.pdamage_indep) * 0.01
        )
        self.stat_main += arg.stat_main
        self.stat_sub += arg.stat_sub
        self.pstat_main += arg.pstat_main
        self.pstat_sub += arg.pstat_sub
        self.boss_pdamage += arg.boss_pdamage
        self.armor_ignore = 100 - 0.01 * (
            (100 - self.armor_ignore) * (100 - arg.armor_ignore)
        )
        self.patt += arg.patt
        self.att += arg.att
        self.stat_main_fixed += arg.stat_main_fixed
        self.stat_sub_fixed += arg.stat_sub_fixed
        return self

    def __add__(self, arg: ExtendedCharacterModifier) -> ExtendedCharacterModifier:
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
            pdamage_indep=(
                self.pdamage_indep
                + arg.pdamage_indep
                + (self.pdamage_indep * arg.pdamage_indep) * 0.01
            ),
            stat_main=(self.stat_main + arg.stat_main),
            stat_sub=(self.stat_sub + arg.stat_sub),
            pstat_main=(self.pstat_main + arg.pstat_main),
            pstat_sub=(self.pstat_sub + arg.pstat_sub),
            boss_pdamage=(self.boss_pdamage + arg.boss_pdamage),
            armor_ignore=100
            - 0.01 * ((100 - self.armor_ignore) * (100 - arg.armor_ignore)),
            patt=(self.patt + arg.patt),
            att=(self.att + arg.att),
            stat_main_fixed=(self.stat_main_fixed + arg.stat_main_fixed),
            stat_sub_fixed=(self.stat_sub_fixed + arg.stat_sub_fixed),
        )

    def __sub__(self, arg: ExtendedCharacterModifier) -> ExtendedCharacterModifier:
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
            pdamage_indep=(100 + self.pdamage_indep) / (100 + arg.pdamage_indep) * 100
            - 100,
            stat_main=(self.stat_main - arg.stat_main),
            stat_sub=(self.stat_sub - arg.stat_sub),
            pstat_main=(self.pstat_main - arg.pstat_main),
            pstat_sub=(self.pstat_sub - arg.pstat_sub),
            boss_pdamage=(self.boss_pdamage - arg.boss_pdamage),
            armor_ignore=100
            - 100 * (100 - self.armor_ignore) / (100 - arg.armor_ignore),
            patt=(self.patt - arg.patt),
            att=(self.att - arg.att),
            stat_main_fixed=(self.stat_main_fixed - arg.stat_main_fixed),
            stat_sub_fixed=(self.stat_sub_fixed - arg.stat_sub_fixed),
        )


class InformedCharacterModifier(ExtendedCharacterModifier):
    __slots__ = "name"

    def __init__(self, name: str, **kwargs) -> None:
        super(InformedCharacterModifier, self).__init__(**kwargs)
        self.name: str = name

    def as_dict(self) -> Dict[str, Any]:
        ret_dict: Dict[str, Any] = super(InformedCharacterModifier, self).as_dict()
        ret_dict["name"] = self.name
        return ret_dict

    @staticmethod
    def from_extended_modifier(
        name: str, extended_modifier: ExtendedCharacterModifier
    ) -> InformedCharacterModifier:
        return InformedCharacterModifier(
            name,
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
            stat_sub_fixed=extended_modifier.stat_sub_fixed,
        )


class VSkillModifier:
    @staticmethod
    def get_reinforcement(incr: int, lv: int, crit: bool = False) -> CharacterModifier:
        armor = 0
        if lv >= 40:
            armor = 20
        if lv >= 20 and crit:
            return CharacterModifier(
                crit=5, pdamage_indep=(lv * incr), armor_ignore=armor
            )
        else:
            return CharacterModifier(
                crit=0, pdamage_indep=(lv * incr), armor_ignore=armor
            )
