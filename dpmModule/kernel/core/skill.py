from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Type, TypeVar

from ..graph import EvaluativeGraphElement
from .constant import NOTWANTTOEXECUTE
from .modifier import CharacterModifier

if TYPE_CHECKING:
    from ..abstract import AbstractVEnhancer
    from .skill_wrapper import AbstractSkillWrapper
    from .vmatrix import BasicVEnhancer

    T = TypeVar("T", bound=AbstractSkillWrapper)


class AbstractSkill(EvaluativeGraphElement):
    """Skill must have information about it's name, it's using - delay, skill using cooltime.
    Basic functions

    Can be re - implemented, but not mandate :
    - dump_json : returns JSON for it's state.
    - load_json : from given JSON, set it's state.
    - get_info : return it's status as JSON.
    """

    def __init__(
        self,
        name: str,
        delay: float,
        cooltime: float = 0,
        rem: bool = False,
        red: bool = True,
    ) -> None:
        super(AbstractSkill, self).__init__(namespace=name)
        self.spec: str = "graph control"
        with self.dynamic_range():
            self.rem: bool = rem
            self.red: bool = red
            self.name: str = name
            self.delay: float = delay
            self.cooltime: float = cooltime
            self.explanation: Optional[str] = None

            if self.cooltime == -1:
                self.cooltime = NOTWANTTOEXECUTE

    def _change_time_into_string(
        self, float_or_infinite: float, divider: int = 1, lang: str = "ko"
    ) -> str:
        lang_to_inf_dict = {"ko": "무한/자동발동불가", "en": "Infinite"}
        if abs(float_or_infinite - NOTWANTTOEXECUTE / divider) < 10000 / divider:
            return lang_to_inf_dict[lang]
        else:
            return "%.1f" % float_or_infinite

    def _parse_list_info_into_string(self, li: List[Tuple[str, str]]) -> str:
        return "\n".join(
            [
                ":".join([i[0], "".join([str(j) for j in i[1:]])])
                for i in li
                if len(str(i[1])) > 0
            ]
        )

    def set_explanation(self, strs: str) -> None:
        self.explanation = strs

    def get_explanation(self, lang: str = "ko", expl_level: int = 2) -> str:
        """level 0 / 1 / 2"""
        if self.explanation is not None:
            return self.explanation
        else:
            return self._get_explanation_internal(lang=lang, expl_level=expl_level)

    def _get_explanation_internal(
        self, detail: bool = False, lang: str = "ko", expl_level: int = 2
    ) -> str:
        if lang == "en":
            li = [("skill name", self.name), ("type", "AbstractSkill(Not implemented)")]
        elif lang == "ko":
            li = [("스킬 이름", self.name), ("분류", "템플릿(상속되지 않음)")]

        return self._parse_list_info_into_string(li)

    def get_info(self, expl_level: int = 2) -> Dict[str, str]:
        my_json = {
            "name": self.name,
            "delay": self._change_time_into_string(self.delay),
            "cooltime": self._change_time_into_string(self.cooltime),
            "expl": self.get_explanation(expl_level=expl_level),
        }
        return my_json

    def wrap(self, wrapper: Type[T], name: str = None) -> T:
        if name is None:
            return wrapper(self)
        else:
            return wrapper(self, name=name)

    def isV(self, enhancer: BasicVEnhancer, use_index: int, upgrade_index: int):
        """Speed hack"""
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

    def __init__(
        self,
        name: str,
        delay: float,
        remain: float,
        cooltime: float = 0,
        crit: float = 0,
        crit_damage: float = 0,
        pdamage: float = 0,
        stat_main: float = 0,
        stat_sub: float = 0,
        pstat_main: float = 0,
        pstat_sub: float = 0,
        boss_pdamage: float = 0,
        pdamage_indep: float = 0,
        armor_ignore: float = 0,
        patt: float = 0,
        att: float = 0,
        stat_main_fixed: int = 0,
        stat_sub_fixed: int = 0,
        rem: bool = False,
        red: bool = False,
    ) -> None:
        super(BuffSkill, self).__init__(
            name, delay, cooltime=cooltime, rem=rem, red=red
        )
        with self.dynamic_range():
            self.spec: str = "buff"
            self.remain: float = remain
            # Build StaticModifier from given arguments
            self.static_character_modifier = CharacterModifier(
                crit=crit,
                crit_damage=crit_damage,
                pdamage=pdamage,
                pdamage_indep=pdamage_indep,
                stat_main=stat_main,
                stat_sub=stat_sub,
                pstat_main=pstat_main,
                pstat_sub=pstat_sub,
                boss_pdamage=boss_pdamage,
                armor_ignore=armor_ignore,
                patt=patt,
                att=att,
                stat_main_fixed=stat_main_fixed,
                stat_sub_fixed=stat_sub_fixed,
            )

    def _get_explanation_internal(
        self, detail: bool = False, lang: str = "ko", expl_level: int = 2
    ) -> str:
        if lang == "ko":
            li = [
                ("스킬 이름", self.name),
                ("분류", "버프"),
                ("딜레이", "%.1f" % self.delay, "ms"),
                (
                    "지속 시간",
                    self._change_time_into_string(self.remain / 1000, divider=1000),
                    "s",
                ),
                (
                    "쿨타임",
                    self._change_time_into_string(self.cooltime / 1000, divider=1000),
                    "s",
                ),
                ("쿨타임 감소 가능 여부", self.red),
                ("지속시간 증가 여부", self.rem),
                (
                    "효과",
                    ", ".join(
                        [
                            (str(i[0]) + "+" + "".join([str(j) for j in i[1:]]))
                            for i in self.static_character_modifier.abstract_log_list()
                        ]
                    ).replace("+미발동", " 미발동"),
                ),
            ]
            if expl_level < 2:
                li = [li[3], li[7]]
        elif lang == "en":
            li = []

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

    def __init__(
        self,
        name: str,
        delay: float,
        damage: float,
        hit: float,
        cooltime: float = 0,
        modifier: CharacterModifier = CharacterModifier(),
        red: bool = False,
    ) -> None:
        super(DamageSkill, self).__init__(
            name, delay, cooltime=cooltime, rem=False, red=red
        )
        with self.dynamic_range():
            self.spec: str = "damage"
            self.damage: float = damage
            self.hit: float = hit
            # Issue : Will we need this option really?
            self._static_skill_modifier: CharacterModifier = modifier

    def _get_explanation_internal(
        self, detail: bool = False, lang: str = "ko", expl_level: int = 2
    ) -> str:
        if lang == "ko":
            li = [
                ("스킬 이름", self.name),
                ("분류", "공격기"),
                ("딜레이", "%.1f" % self.delay, "ms"),
                ("퍼뎀", "%.1f" % self.damage, "%"),
                ("타격수", self.hit),
                (
                    "쿨타임",
                    self._change_time_into_string(self.cooltime / 1000, divider=1000),
                    "s",
                ),
                ("쿨타임 감소 가능 여부", self.red),
                ("지속시간 증가 여부", self.rem),
                (
                    "추가효과",
                    ", ".join(
                        [
                            (str(i[0]) + "+" + "".join([str(j) for j in i[1:]]))
                            for i in self._static_skill_modifier.abstract_log_list()
                        ]
                    ).replace("+미발동%", " 미발동"),
                ),
            ]
            if expl_level < 2:
                li = li[3:5] + [li[8]]
        elif lang == "en":
            li = []

        return self._parse_list_info_into_string(li)

    def setV(
        self, v_enhancer: AbstractVEnhancer, index: int, incr: int, crit: bool = False
    ) -> DamageSkill:
        self._static_skill_modifier = (
            self._static_skill_modifier
            + v_enhancer.get_reinforcement_with_register(index, incr, crit, self)
        )
        return self

    def get_modifier(self) -> CharacterModifier:
        return self._static_skill_modifier

    def copy(self) -> DamageSkill:
        return DamageSkill(
            self.name,
            self.delay,
            self.damage,
            self.hit,
            cooltime=self.cooltime,
            modifier=self._static_skill_modifier,
            red=self.red,
        )


# TODO: optimize this factor more constructively
class SummonSkill(AbstractSkill):
    def __init__(
        self,
        name: str,
        summondelay: float,
        delay: float,
        damage: float,
        hit: float,
        remain: float,
        cooltime: float = 0,
        modifier: CharacterModifier = CharacterModifier(),
        rem: bool = False,
        red: bool = False,
    ) -> None:
        super(SummonSkill, self).__init__(
            name, delay, cooltime=cooltime, rem=rem, red=red
        )
        with self.dynamic_range():
            self.spec: str = "summon"
            self.summondelay: float = summondelay
            self.damage: float = damage
            self.hit: float = hit
            self.remain: float = remain
            self._static_skill_modifier: CharacterModifier = modifier

    def _get_explanation_internal(
        self, detail: bool = False, lang: str = "ko", expl_level: int = 2
    ) -> str:
        if lang == "ko":
            li = [
                ("스킬 이름", self.name),
                ("분류", "소환기"),
                ("딜레이", "%.1f" % self.summondelay, "ms"),
                ("타격주기", "%.1f" % self.delay, "ms"),
                ("퍼뎀", "%.1f" % self.damage, "%"),
                ("타격수", self.hit),
                (
                    "지속 시간",
                    self._change_time_into_string(self.remain / 1000, divider=1000),
                    "s",
                ),
                (
                    "쿨타임",
                    self._change_time_into_string(self.cooltime / 1000, divider=1000),
                    "s",
                ),
                ("쿨타임 감소 가능 여부", self.red),
                ("지속시간 증가 여부", self.rem),
                (
                    "추가효과",
                    ", ".join(
                        [
                            (str(i[0]) + "+" + "".join([str(j) for j in i[1:]]))
                            for i in self._static_skill_modifier.abstract_log_list()
                        ]
                    ).replace("+미발동%", " 미발동"),
                ),
            ]
            if expl_level < 2:
                li = li[3:7] + [li[10]]
        elif lang == "en":
            li = []

        return self._parse_list_info_into_string(li)

    def get_info(self, expl_level=2) -> Dict[str, str]:
        my_json = {
            "name": self.name,
            "delay": self._change_time_into_string(self.summondelay),
            "cooltime": self._change_time_into_string(self.cooltime),
            "expl": self.get_explanation(expl_level=expl_level),
        }
        return my_json

    def setV(
        self, v_enhancer: AbstractVEnhancer, index: int, incr: int, crit: bool = False
    ) -> SummonSkill:
        self._static_skill_modifier = (
            self._static_skill_modifier
            + v_enhancer.get_reinforcement_with_register(index, incr, crit, self)
        )
        return self

    def get_modifier(self) -> CharacterModifier:
        return self._static_skill_modifier


class DotSkill(SummonSkill):
    def __init__(
        self,
        name: str,
        summondelay: float,
        delay: float,
        damage: float,
        hit: float,
        remain: float,
        cooltime: float = 0,
        red: bool = False,
    ) -> None:
        super(DotSkill, self).__init__(
            name, summondelay, delay, damage, hit, remain, cooltime=cooltime, red=red
        )
        self.spec: str = "dot"

    def _get_explanation_internal(
        self, detail: bool = False, lang: str = "ko", expl_level: int = 2
    ) -> str:
        if lang == "ko":
            li = [
                ("스킬 이름", self.name),
                ("분류", "도트뎀"),
                ("딜레이", "%.1f" % self.summondelay, "ms"),
                ("타격주기", "%.1f" % self.delay, "ms"),
                ("퍼뎀", "%.1f" % self.damage, "%"),
                ("타격수", self.hit),
                (
                    "지속 시간",
                    self._change_time_into_string(self.remain / 1000, divider=1000),
                    "s",
                ),
                (
                    "쿨타임",
                    self._change_time_into_string(self.cooltime / 1000, divider=1000),
                    "s",
                ),
                ("쿨타임 감소 가능 여부", self.red),
                ("지속시간 증가 여부", self.rem),
                (
                    "추가효과",
                    ", ".join(
                        [
                            (str(i[0]) + "+" + "".join([str(j) for j in i[1:]]))
                            for i in self._static_skill_modifier.abstract_log_list()
                        ]
                    ).replace("+미발동%", " 미발동"),
                ),
            ]
            if expl_level < 2:
                li = li[3:7] + [li[10]]
        elif lang == "en":
            li = []

        return self._parse_list_info_into_string(li)


def _map_background_information(conf, **kwargs):
    global_variables = globals()
    global_variables.update(kwargs)
    exported_conf = {}
    for k, v in conf.items():
        if isinstance(v, str) and k != 'name':
            assert 'import' not in v
            exported_conf[k] = eval(v, global_variables)
        else:
            exported_conf[k] = v
    return exported_conf


def load_skill(skill_conf, background_information):
    if 'modifier' in skill_conf:
        skill_conf['modifier'] = CharacterModifier.load(skill_conf['modifier'])

    skill_object_type = {
        'DamageSkill': DamageSkill,
        'SummonSkill': SummonSkill,
        'BuffSkill': BuffSkill
    }

    SkillObject = skill_object_type[skill_conf['type']]
    
    argument_space = SkillObject.__init__.__code__.co_varnames
    filtered_skill_conf = {k: v for k, v in skill_conf.items() if k in argument_space}
    filtered_skill_conf = _map_background_information(filtered_skill_conf, **background_information)
    return SkillObject(**filtered_skill_conf)
