from .core.skill import load_skill
from .core.skill import DamageSkill, BuffSkill, SummonSkill, DotSkill
from .core.skill_wrapper import DamageSkillWrapper, BuffSkillWrapper, SummonSkillWrapper, DotSkillWrapper
import yaml
import copy

class AbstractConfigurationLoader:
    def __init__(self, conf):
        if isinstance(conf, str):
            with open(conf, encoding='utf-8') as f:
                if conf.split('.')[-1] == 'json':
                    conf = json.load(f)
                elif conf.split('.')[-1] == 'yml':
                    conf = yaml.safe_load(f)
        
        self.conf = conf

    def get_constant(self, key):
        return self.conf["constant"][key]


class SkillConfigLoader(AbstractConfigurationLoader):
    def __init__(self, conf):
        super(SkillConfigLoader, self).__init__(conf)
        self._default_background_information = {}

    def set_v_enhancer(self, v_enhancer):
        self.v_enhancer = v_enhancer
        return self

    def register_background_information(self, **kwargs):
        for k, v in kwargs.items():
            self._default_background_information[k] = v

        return self

    def register_default_skill_info(self, combat, character, v_enhancer):
        self.register_background_information(
            combat=combat,
            passive_level=character.get_base_modifier().passive_level + combat,
        )
        self.set_v_enhancer(v_enhancer)

    def load_skill(self, skill_name, background_information={}):
        skill_conf = copy.deepcopy(self.conf['skills'][skill_name])
        if 'name' not in skill_conf:
            skill_conf['name'] = skill_name

        if skill_conf.get('tier', -1) == 5:
            lv = self.v_enhancer.getV(skill_conf['use_priority'], skill_conf['upgrade_priority'])
            background_information['lv'] = lv

        for k, v in self._default_background_information.items():
            background_information[k] = v

        skill = load_skill(skill_conf, background_information)

        if skill_conf.get('enhanced_by_v', False):
            skill = skill.setV(
                self.v_enhancer,
                skill_conf['upgrade_priority'],
                skill_conf['v_increment'],
                skill_conf['v_crit']
            )

        return skill

    def load_skill_wrapper(self, skill_name):
        background_information = {k: v for k, v in self.conf.get('constant', {}).items()}
        for k, v in self._default_background_information.items():
            background_information[k] = v

        skill = self.load_skill(skill_name, background_information=background_information)
        if isinstance(skill, DamageSkill):
            return skill.wrap(DamageSkillWrapper)
        elif isinstance(skill, BuffSkill):
            return skill.wrap(BuffSkillWrapper)
        elif isinstance(skill, DotSkill):
            return skill.wrap(DotSkillWrapper)
        elif isinstance(skill, SummonSkill):
            return skill.wrap(SummonSkillWrapper)
