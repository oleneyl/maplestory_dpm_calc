from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from .constant import FINAL_DAMAGE_RATIO, MAX_DAMAGE_RESTRICTION, ARMOR_RATE
from ..graph import DynamicVariableInstance, DynamicVariableOperation
from .modifier import SkillModifier

class CharacterStatus(object):
    __slots__ = (
        "crit",
        "crit_damage",
        "pdamage",
        "pdamage_indep",
        "stat",
        "stat_rate",
        "boss_pdamage",
        "armor_ignore",
        "att",
        "matt",
        "att_rate",
        "matt_rate",
        "stat_fixed",
        "MHP"
    )
    """CharacterStatus : Holds information about character modifiing factors ex ) pdamage, stat, att%, etc.AbstractSkill
    - parameters

      .crit : Additional critical value
      .crit_damage : Critical damage increment %

      .pdamage : Damage increment %
      .pdamage_indep : Total Damage Increment %.

      .stat : stat, [STR, DEX, INT, LUK]

      .stat_rate : stat increment %, [STR, DEX, INT, LUK]

      .boss_pdamage : Boss Attack Damage increment%
      .armor_ignore : Armor Ignorance %

      .att : AD increment
      .patt : AD increment %

      .MHP : MHP

      * Additional parameters can be involved with inherit this class.

    """

    STAT_ORDER = {
        'STR': 0,
        'DEX': 1,
        'INT': 2,
        'LUK': 3
    }

    def __init__(
        self,
        crit: float = 0,
        crit_damage: float = 0,
        pdamage: float = 0,
        pdamage_indep: float = 0,
        stat: Optional[List] = None,
        stat_rate: Optional[List] = None,
        stat_fixed: Optional[List] = None,
        MHP: float = 0,
        boss_pdamage: float = 0,
        armor_ignore: float = 0,

        att: float = 0,
        matt: float = 0,
        att_rate: float = 0,
        matt_rate: float = 0,

        STR: float = 0,
        DEX: float = 0,
        INT: float = 0,
        LUK: float = 0,

        STR_rate: float = 0,
        DEX_rate: float = 0,
        INT_rate: float = 0,
        LUK_rate: float = 0,

        STR_fixed: float = 0,
        DEX_fixed: float = 0,
        INT_fixed: float = 0,
        LUK_fixed: float = 0
    ) -> None:
        self.crit: float = crit
        self.crit_damage: float = crit_damage

        self.pdamage: float = pdamage
        self.pdamage_indep: float = pdamage_indep

        if stat is not None:
            assert len(stat) == 4
            self.stat: list = stat
        else:
            self.stat = [STR, DEX, INT, LUK]

        if stat_rate is not None:
            assert len(stat_rate) == 4
            self.stat_rate: list = stat_rate
        else:
            self.stat_rate = [STR_rate, DEX_rate, INT_rate, LUK_rate]

        if stat_fixed is not None:
            assert len(stat_fixed) == 4
            self.stat_fixed: list = stat_fixed
        else:
            self.stat_fixed = [STR_fixed, DEX_fixed, INT_fixed, LUK_fixed]

        self.MHP: float = MHP

        self.boss_pdamage: float = boss_pdamage
        self.armor_ignore: float = armor_ignore

        self.att: float = att
        self.matt: float = matt
        self.att_rate: float = att_rate
        self.matt_rate: float = matt_rate

    def __getattr__(self, name):
        if '_' in name:
            prefix, category = name.split('_')
            if category == 'rate':
                return self.stat_rate[CharacterStatus.STAT_ORDER[prefix]]
            if category == 'fixed':
                return self.stat_fixed[CharacterStatus.STAT_ORDER[prefix]]
        else:
            if name in CharacterStatus.STAT_ORDER:
                return self.stat[CharacterStatus.STAT_ORDER[name]]
            else:
                raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in CharacterStatus.STAT_ORDER:
            self.stat[CharacterStatus.STAT_ORDER[name]] = value
        else:
            super(CharacterStatus, self).__setattr__(name, value)

    def __iadd__(self, arg: CharacterStatus) -> CharacterStatus:
        self.crit += arg.crit
        self.crit_damage += arg.crit_damage
        self.pdamage += arg.pdamage
        self.pdamage_indep += (
            arg.pdamage_indep + (self.pdamage_indep * arg.pdamage_indep) * 0.01
        )

        for i in range(4):
            self.stat[i] += arg.stat[i]
            self.stat_rate[i] += arg.stat_rate[i]
            self.stat_fixed[i] += arg.stat_fixed[i]

        self.MHP += arg.MHP

        self.boss_pdamage += arg.boss_pdamage
        self.armor_ignore = 100 - 0.01 * (
            (100 - self.armor_ignore) * (100 - arg.armor_ignore)
        )

        self.att += arg.att
        self.matt += arg.matt
        self.att_rate += arg.att_rate
        self.matt_rate += arg.matt_rate

        return self

    def __add__(self, arg: CharacterStatus) -> CharacterStatus:
        status = self.copy()
        status += arg
        return status

    def __sub__(self, arg: CharacterStatus) -> CharacterStatus:
        return CharacterStatus(
            crit=(self.crit - arg.crit),
            crit_damage=(self.crit_damage - arg.crit_damage),
            pdamage=(self.pdamage - arg.pdamage),
            pdamage_indep=(100 + self.pdamage_indep) / (100 + arg.pdamage_indep) * 100
            - 100,
            stat=[self.stat[i] - arg.stat[i] for i in range(4)],
            stat_rate=[self.stat_rate[i] - arg.stat_rate[i] for i in range(4)],
            stat_fixed=[self.stat_fixed[i] - arg.stat_fixed[i] for i in range(4)],
            MHP=(self.MHP - arg.MHP),
            boss_pdamage=(self.boss_pdamage - arg.boss_pdamage),
            armor_ignore=100
            - 100 * (100 - self.armor_ignore) / (100 - arg.armor_ignore),
            att=self.att - arg.att,
            matt=self.matt - arg.matt,
            att_rate=self.att_rate - arg.att_rate,
            matt_rate=self.matt_rate - arg.matt_rate,
        )

    def copy(self) -> CharacterStatus:
        return CharacterStatus(
            crit=self.crit,
            crit_damage=self.crit_damage,
            pdamage=self.pdamage,
            pdamage_indep=self.pdamage_indep,

            stat=[i for i in self.stat],
            stat_rate=[i for i in self.stat_rate],
            stat_fixed=[i for i in self.stat_fixed],
            MHP=self.MHP,

            boss_pdamage=self.boss_pdamage,
            armor_ignore=self.armor_ignore,

            att=self.att,
            matt=self.matt,
            att_rate=self.att_rate,
            matt_rate=self.matt_rate
        )

    def extend(self) -> ExtendedCharacterStatus:
        return ExtendedCharacterStatus(
            crit=self.crit,
            crit_damage=self.crit_damage,
            pdamage=self.pdamage,
            pdamage_indep=self.pdamage_indep,
            stat=[i for i in self.stat],
            stat_rate=[i for i in self.stat_rate],
            stat_fixed=[i for i in self.stat_fixed],
            MHP=self.MHP,
            boss_pdamage=self.boss_pdamage,
            armor_ignore=self.armor_ignore,
            att=self.att,
            matt=self.matt,
            att_rate=self.att_rate,
            matt_rate=self.matt_rate
        )

    def log(self) -> str:
        txt = "crit rate : %.1f, crit damage : %.1f\n" % (self.crit, self.crit_damage)
        txt += "pdamage : %.1f, pdamage_indep : %.1f\n" % (
            self.pdamage,
            self.pdamage_indep,
        )
        txt += "stat : %s\n" % '.'.join(map(str, self.stat))
        txt += "stat_rate : %s\n" % '.'.join(map(str, self.stat_rate))
        txt += "stat_fixed : %s\n" % '.'.join(map(str, self.stat_fixed))
        txt += "att : %s\n" % '.'.join(map(str, self.att))

        txt += "MHP : %.1f\n" % (self.MHP)
        txt += "att : %.1f, att_rate : %.1f\n" % (self.att, self.att_rate)
        txt += "matt : %.1f, matt_rate : %.1f\n" % (self.matt, self.matt_rate)
        return txt

    def as_dict(self) -> Dict[str, float]:
        return {
            "crit": self.crit,
            "crit_damage": self.crit_damage,
            "pdamage": self.pdamage,
            "pdamage_indep": self.pdamage_indep,
            "stat": self.stat,
            "stat_rate": self.stat_rate,
            "stat_fixed": self.stat_fixed,
            "MHP": self.MHP,
            "boss_pdamage": self.boss_pdamage,
            "armor_ignore": self.armor_ignore,
            "att": self.att,
            "matt": self.matt,
            "att_rate": self.att_rate,
            "matt_rate": self.matt_rate
        }

class DynamicCharacterStatus(DynamicVariableInstance, CharacterStatus):
    def __init__(self, **kwargs) -> None:
        DynamicVariableInstance.__init__(self)
        parsed_kwargs = {
            k: DynamicVariableOperation.wrap_argument(a) for k, a in kwargs.items()
        }
        for k, a in parsed_kwargs.items():
            self.add_next_instance(a)
            a.inherit_namespace(k)
        CharacterStatus.__init__(self, **parsed_kwargs)

    def evaluate_override(self) -> CharacterStatus:
        return CharacterStatus(
            crit=self.crit.evaluate(),
            crit_damage=self.crit_damage.evaluate(),
            pdamage=self.pdamage.evaluate(),
            pdamage_indep=self.pdamage_indep.evaluate(),
            stat=self.stat.evaluate(),
            stat_rate=self.stat_rate.evaluate(),
            stat_fixed=self.stat_fixed.evaluate(),
            MHP=self.MHP.evaluate(),
            boss_pdamage=self.boss_pdamage.evaluate(),
            armor_ignore=self.armor_ignore.evaluate(),
            att=self.att.evaluate(),
            matt=self.matt.evaluate(),
            att_rate=self.att_rate.evaluate(),
            matt_rate=self.matt_rate.evaluate(),
        )


class ExtendedCharacterStatus(CharacterStatus):
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
        super(ExtendedCharacterStatus, self).__init__(**kwargs)
        self.buff_rem: float = buff_rem
        self.summon_rem: float = summon_rem
        self.cooltime_reduce: float = cooltime_reduce
        self.pcooltime_reduce: float = pcooltime_reduce
        self.reuse_chance: float = reuse_chance
        self.prop_ignore: float = prop_ignore
        self.additional_target: int = additional_target
        self.passive_level: int = passive_level

    def log(self) -> str:
        txt = super(ExtendedCharacterStatus, self).log()
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

    def copy(self) -> ExtendedCharacterStatus:
        return ExtendedCharacterStatus(
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

            stat=[i for i in self.stat],
            stat_rate=[i for i in self.stat_rate],
            stat_fixed=[i for i in self.stat_fixed],
            MHP=self.MHP,

            boss_pdamage=self.boss_pdamage,
            armor_ignore=self.armor_ignore,

            att=self.att,
            matt=self.matt,
            att_rate=self.att_rate,
            matt_rate=self.matt_rate
        )

    def degenerate(self) -> CharacterStatus:
        return super(ExtendedCharacterStatus, self).copy()

    def to_skill_modifier(self) -> SkillModifier:
        return SkillModifier(
            buff_rem=self.buff_rem,
            summon_rem=self.summon_rem,
            cooltime_reduce=self.cooltime_reduce,
            pcooltime_reduce=self.pcooltime_reduce,
            reuse_chance=self.reuse_chance,
        )

    def as_dict(self) -> Dict[str, float]:
        ret_dict = super(ExtendedCharacterStatus, self).as_dict()
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

    def __iadd__(self, arg: ExtendedCharacterStatus) -> ExtendedCharacterStatus:
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

        for i in range(4):
            self.stat[i] += arg.stat[i]
            self.stat_rate[i] += arg.stat_rate[i]
            self.stat_fixed[i] += arg.stat_fixed[i]

        self.MHP += arg.MHP

        self.boss_pdamage += arg.boss_pdamage
        self.armor_ignore = 100 - 0.01 * (
            (100 - self.armor_ignore) * (100 - arg.armor_ignore)
        )

        self.att += arg.att
        self.matt += arg.matt
        self.att_rate += arg.att_rate
        self.matt_rate += arg.matt_rate
        
        return self

    def __add__(self, arg: ExtendedCharacterStatus) -> ExtendedCharacterStatus:
        status = self.copy()
        status += arg
        return status

    def __sub__(self, arg: ExtendedCharacterStatus) -> ExtendedCharacterStatus:
        return ExtendedCharacterStatus(
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
            stat=[self.stat[i] - arg.stat[i] for i in range(4)],
            stat_rate=[self.stat_rate[i] - arg.stat_rate[i] for i in range(4)],
            stat_fixed=[self.stat_fixed[i] - arg.stat_fixed[i] for i in range(4)],
            MHP=(self.MHP - arg.MHP),
            boss_pdamage=(self.boss_pdamage - arg.boss_pdamage),
            armor_ignore=100
            - 100 * (100 - self.armor_ignore) / (100 - arg.armor_ignore),
            att=self.att - arg.att,
            matt=self.matt - arg.matt,
            att_rate=self.att_rate - arg.att_rate,
            matt_rate=self.matt_rate - arg.matt_rate,
        )


class InformedCharacterStatus(ExtendedCharacterStatus):
    __slots__ = "name"

    def __init__(self, name: str, **kwargs) -> None:
        super(InformedCharacterStatus, self).__init__(**kwargs)
        self.name: str = name

    def as_dict(self) -> Dict[str, Any]:
        ret_dict: Dict[str, Any] = super(InformedCharacterStatus, self).as_dict()
        ret_dict["name"] = self.name
        return ret_dict

    @staticmethod
    def from_extended_modifier(
        name: str, extended_modifier: ExtendedCharacterStatus
    ) -> InformedCharacterStatus:
        return InformedCharacterStatus(
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
            stat_rate_main=extended_modifier.stat_rate_main,
            stat_rate_sub=extended_modifier.stat_rate_sub,
            boss_pdamage=extended_modifier.boss_pdamage,
            armor_ignore=extended_modifier.armor_ignore,
            patt=extended_modifier.patt,
            att=extended_modifier.att,
            stat_main_fixed=extended_modifier.stat_main_fixed,
            stat_sub_fixed=extended_modifier.stat_sub_fixed,
        )

    @classmethod
    def load(cls, conf):
        name = conf['name']
        value_conf = {k: v for k, v in conf.items() if k != 'name'}
        return InformedCharacterStatus(name, **value_conf)


class VSkillModifier:
    @staticmethod
    def get_reinforcement(incr: int, lv: int, crit: bool = False) -> CharacterStatus:
        armor = 0
        if lv >= 40:
            armor = 20
        if lv >= 20 and crit:
            return CharacterStatus(
                crit=5, pdamage_indep=(lv * incr), armor_ignore=armor
            )
        else:
            return CharacterStatus(
                crit=0, pdamage_indep=(lv * incr), armor_ignore=armor
            )
