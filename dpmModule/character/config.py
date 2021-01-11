from ..kernel import core
import json
import yaml
import copy
import math


def _get_loaded_object_with_mapping(conf, loadable, **kwargs):
    global_variables = globals()
    global_variables.update(kwargs)
    global_variables["math"] = math
    exported_conf = {}
    for k, v in conf.items():
        if isinstance(v, str) and k != "name":
            assert "import" not in v
            exported_conf[k] = eval(v, global_variables)
        else:
            exported_conf[k] = v
    return loadable.load(exported_conf)


class ConfigLoader:
    def __init__(self, gen, conf_path: str) -> None:
        with open(conf_path, encoding="utf-8") as f:
            if conf_path.split(".")[-1] == "json":
                self.conf = json.load(f)
            elif conf_path.split(".")[-1] == "yml":
                self.conf = yaml.safe_load(f)
            else:
                raise ValueError(conf_path)

        self.chtr = gen.chtr
        self.vEhc = gen.vEhc
        self.background_information = {
            **gen.options,
            **self.conf.get("constant", {}),
            "combat": gen.combat,
            "passive_level": gen.combat + gen.chtr.get_base_modifier().passive_level,
        }

    def get_conf(self):
        return self.conf

    def get_constant(self, key: str):
        return self.conf["constant"].get(key)

    def load_passive_skill_list(self):
        return [
            _get_loaded_object_with_mapping(
                opt,
                core.InformedCharacterModifier,
                **self.background_information,
            )
            for opt in self.conf["passive_skill_list"]
        ]

    def load_not_implied_skill_list(self):
        return [
            _get_loaded_object_with_mapping(
                opt,
                core.InformedCharacterModifier,
                **self.background_information,
            )
            for opt in self.conf["not_implied_skill_list"]
        ]

    def _load_skill(self, skill_name, background_information={}):
        skill_conf = copy.deepcopy(self.conf["skills"][skill_name])
        if "name" not in skill_conf:
            skill_conf["name"] = skill_name

        if skill_conf.get("tier", -1) == 5:
            lv = self.vEhc.getV(
                skill_conf["use_priority"], skill_conf["upgrade_priority"]
            )
            background_information["lv"] = lv

        skill = core.load_skill(skill_conf, background_information)

        if skill_conf.get("enhanced_by_v", False):
            skill = skill.setV(
                self.vEhc,
                skill_conf["upgrade_priority"],
                skill_conf["v_increment"],
                skill_conf["v_crit"],
            )

        return skill

    def load_skill_wrapper(self, skill_name):
        skill = self._load_skill(
            skill_name, background_information=self.background_information.copy()
        )
        if isinstance(skill, core.DamageSkill):
            return skill.wrap(core.DamageSkillWrapper)
        elif isinstance(skill, core.BuffSkill):
            return skill.wrap(core.BuffSkillWrapper)
        elif isinstance(skill, core.DotSkill):
            return skill.wrap(core.DotSkillWrapper)
        elif isinstance(skill, core.SummonSkill):
            return skill.wrap(core.SummonSkillWrapper)