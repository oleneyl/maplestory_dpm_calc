from .graph import EvaluativeGraphElement, DynamicVariableOperation, DynamicVariableInstance, AbstractDynamicVariableInstance
from .abstract import AbstractScenarioGraph, AbstractVEnhancer, AbstractVBuilder
from functools import partial
import math

NOTWANTTOEXECUTE = 99999999
MAX_DAMAGE_RESTRICTION = 10000 * 10000 * 100

def infinite_time():
    return NOTWANTTOEXECUTE

class CharacterModifier(object):
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
    def __init__(self,  crit = 0, crit_damage = 0, pdamage = 0, pdamage_indep = 0, stat_main = 0, stat_sub = 0, pstat_main = 0, pstat_sub = 0, boss_pdamage = 0, armor_ignore = 0, patt = 0, att = 0, stat_main_fixed = 0, stat_sub_fixed = 0):
        self.crit = crit
        self.crit_damage = crit_damage        
        
        self.pdamage = pdamage
        self.pdamage_indep = pdamage_indep
        
        self.stat_main = stat_main
        self.stat_sub = stat_sub
        
        self.pstat_sub = pstat_sub
        self.pstat_main = pstat_main
        
        self.boss_pdamage = boss_pdamage
        self.armor_ignore = armor_ignore
        
        self.att = att
        self.patt = patt
        
        self.stat_main_fixed = stat_main_fixed
        self.stat_sub_fixed = stat_sub_fixed

    def __iadd__(self, arg):
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

    def __sub__(self, arg):
        return CharacterModifier(crit = (self.crit - arg.crit),   \
                        crit_damage = (self.crit_damage - arg.crit_damage) , \
                        pdamage = (self.pdamage - arg.pdamage), \
                        pdamage_indep = (100 + self.pdamage_indep) / (100 + arg.pdamage_indep) * 100 - 100, \
                        stat_main = (self.stat_main - arg.stat_main),\
                        stat_sub = (self.stat_sub - arg.stat_sub), \
                        pstat_main = (self.pstat_main - arg.pstat_main), \
                        pstat_sub = (self.pstat_sub - arg.pstat_sub), \
                        boss_pdamage = (self.boss_pdamage - arg.boss_pdamage),\
                        armor_ignore = 100 - 100 * (100 - self.armor_ignore) / (100 - arg.armor_ignore), \
                        patt = (self.patt - arg.patt), \
                        att = (self.att - arg.att), \
                        stat_main_fixed = (self.stat_main_fixed - arg.stat_main_fixed), \
                        stat_sub_fixed = (self.stat_sub_fixed - arg.stat_sub_fixed))

    def copy(self):
        return CharacterModifier(crit = self.crit, crit_damage = self.crit_damage, pdamage = self.pdamage, 
                    pdamage_indep = self.pdamage_indep, stat_main = self.stat_main, stat_sub = self.stat_sub, 
                    pstat_main = self.pstat_main, pstat_sub = self.pstat_sub, boss_pdamage = self.boss_pdamage, 
                    armor_ignore = self.armor_ignore, patt = self.patt, att = self.att, stat_main_fixed = self.stat_main_fixed, stat_sub_fixed = self.stat_sub_fixed)
        
    def get_damage_factor(self, armor = 300):
        '''Caution : Use this function only if you summed up every modifiers.
        '''
        real_crit = min(100, self.crit)
        stat = (4 * self.stat_main * (1 + 0.01 * self.pstat_main) + self.stat_sub * (1 + 0.01 * self.pstat_sub)) + (4 * self.stat_main_fixed + self.stat_sub_fixed )
        adap = self.att * (1 + 0.01 * self.patt)
        factor = (1 + 0.0001 * max(0, real_crit) * (self.crit_damage + 35)) * (1 + 0.01 * (max(self.pdamage + self.boss_pdamage, 0))) * (1 + 0.01 * self.pdamage_indep)
        ignorance = max((100 - armor * (1 - 0.01* self.armor_ignore)) * 0.01, 0)
        return stat * adap * factor * ignorance * 0.01

    def get_status_factor(self, armor = 300):
        '''Caution : Use this function only if you summed up every modifiers.
        '''
        stat = (4 * self.stat_main * (1 + 0.01 * self.pstat_main) + self.stat_sub * (1 + 0.01 * self.pstat_sub)) + (4 * self.stat_main_fixed + self.stat_sub_fixed )
        adap = self.att * (1 + 0.01 * self.patt)
        factor = (1 + 0.01 * (self.pdamage)) * (1 + 0.01 * self.pdamage_indep)
        return stat * adap * factor * 0.01
    
    def calculate_damage(self, damage, hit, spec, armor = 300):
        '''Return : (damage, loss) tuple
        숙련도는 90~100으로 가정함(5% deviation)
        '''
        def restricted_damage(x1, x2, y1, y2, M):
            '''Calculated expected value of min(M, xy) in [x1~x2, y1~y2]
            '''
            normalizer = (x2 - x1) * (y2 - y1)
            basis = (x1 + x2) / 2 * (y1 + y2) / 2
            
            if M > x2 * y2:
                return basis
            else:
                if M > x1 * y2 and M > x2 * y1:
                    x_p = M / y2
                    # Case 1
                    excess = M * y2 * (x2 - x_p) - (y2 * y2 / 4) *(x2 * x2 - x_p * x_p) - (M * M / 2) * math.log(x2 / x_p)
                    
                    return basis + excess / normalizer
                elif M < x1 * y2 and M > x2 * y1:
                    # Case 2
                    x_p = x1
                    # Case 1
                    excess = M * y2 * (x2 - x_p) - (y2 * y2 / 4) *(x2 * x2 - x_p * x_p) - (M * M / 2) * math.log(x2 / x_p)
                    return basis + excess / normalizer

                elif M > x1 * y2 and M < x2 * y1:
                    # Case 3 -> change to Case 2
                    return restricted_damage(y1, y2, x1, x2, M)
                    
                elif M > x1 * y1:
                    x_p = M / y1
                    excess = M * y1 * (x_p - x1) - (y1 * y1 / 4) * (x_p * x_p - x1 * x1) - (M * M / 2) * math.log(x_p / x1)
                    return M + excess / normalizer

                else:
                    return M

        #Optimized
        real_crit = min(100, self.crit)
        stat = (4 * self.stat_main * (1 + 0.01 * self.pstat_main) + self.stat_sub * (1 + 0.01 * self.pstat_sub)) + (4 * self.stat_main_fixed + self.stat_sub_fixed )
        adap = self.att * (1 + 0.01 * self.patt)
        factor_crit_removed = (1 + 0.01 * (max(self.pdamage + self.boss_pdamage, 0))) * (1 + 0.01 * self.pdamage_indep)
        ignorance = max((100 - armor * (1 - 0.01* self.armor_ignore)) * 0.01, 0)
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

        real_damage = hit * (max_crit_factor + min_crit_factor) / 2 * (max_damage_factor + min_damage_factor) / 2 # W/O restriction
        res_damage = hit * restricted_damage(min_damage_factor, max_damage_factor, min_crit_factor, max_crit_factor, MAX_DAMAGE_RESTRICTION)  # W/ restriction

        return (res_damage, real_damage - res_damage)

    def log(self):
        txt = ("crit rate : %.1f, crit damage %.1f\n")%(self.crit, self.crit_damage)
        txt += "pdamage : %.1f, pdamage_indep %.1f\n"%(self.pdamage, self.pdamage_indep)
        txt += "stat_main : %.1f, stat_sub %.1f\n"%(self.stat_main, self.stat_sub)
        txt += "pstat_main : %.1f, pstat_sub %.1f\n"%(self.pstat_main, self.pstat_sub)
        txt += "stat_main_fixed : %.1f, stat_sub_fixed %.1f\n"%(self.stat_main_fixed, self.stat_sub_fixed)
        txt += "boss_pdamage : %.1f, armor_ignore %.1f\n"%(self.boss_pdamage, self.armor_ignore)
        txt += "att : %.1f, patt %.1f\n"%(self.att, self.patt)
        txt += "Fixed stat : main %.1f, sub %.1f\n"%(self.stat_main_fixed, self.stat_sub_fixed)
        txt += "damageFactor : %.1f"%(self.get_damage_factor())
        return txt
    
    def __repr__(self):
        return self.log()
    
    def abstract_log_list(self, lang = "ko"):
        crit_rate_formal = (math.floor(self.crit*10))/10
        if crit_rate_formal < 0 :
            crit_rate_formal = "미발동"
        if lang == "ko":
            el = [("크리티컬 확률", crit_rate_formal, "%"),
                        ("크리티컬 데미지", math.floor(self.crit_damage*10)/10,"%"),
                        ("주스텟", math.floor(self.stat_main*10)/10),
                        ("부스텟", math.floor(self.stat_sub*10)/10),
                        ("총 데미지", math.floor(self.pdamage*10)/10,"%"),
                        ("보스 공격력", math.floor(self. boss_pdamage*10)/10,"%"),
                        ("주스텟퍼", math.floor(self.pstat_main*10)/10,"%"),
                        ("부스텟퍼", math.floor(self.pstat_sub*10)/10,"%"),
                        ("최종뎀", math.floor(self.pdamage_indep*10)/10,"%"),
                        ("공격력", math.floor(self.att*10)/10),
                        ("공퍼", math.floor(self.patt*10)/10,"%"),
                        ("방무", math.floor(self.armor_ignore*10)/10,"%")]
        elif lang == "en":
            el = [("crit rate", self.crit),
                        ("crit damage", self.crit_damage),
                        ("main stat", self.stat_main),
                        ("sub stat", self.stat_sub),
                        ("total damageP", self.pdamage),
                        ("boss damageP", self. boss_pdamage),
                        ("main statP", self.pstat_main),
                        ("sub statP", self.pstat_sub),
                        ("final damageP", self.pdamage_indep),
                        ("AD/MD", self.att),
                        ("AD/MD P", self.patt),
                        ("armor ignorance", self.armor_ignore)]
        retel = []
        for i in el:
            if i[1] != 0: retel.append(i)
        return retel
        
    def __add__(self, arg):
        return CharacterModifier(crit = (self.crit + arg.crit), \
                        crit_damage = (self.crit_damage + arg.crit_damage) , \
                        pdamage = (self.pdamage + arg.pdamage), \
                        pdamage_indep = (self.pdamage_indep + arg.pdamage_indep + (self.pdamage_indep * arg.pdamage_indep) * 0.01), \
                        stat_main = (self.stat_main + arg.stat_main),\
                        stat_sub = (self.stat_sub + arg.stat_sub), \
                        pstat_main = (self.pstat_main + arg.pstat_main), \
                        pstat_sub = (self.pstat_sub + arg.pstat_sub), \
                        boss_pdamage = (self.boss_pdamage + arg.boss_pdamage),\
                        armor_ignore = 100 - 0.01 * ((100 - self.armor_ignore) * (100 - arg.armor_ignore)), \
                        patt = (self.patt + arg.patt), \
                        att = (self.att + arg.att), \
                        stat_main_fixed = (self.stat_main_fixed + arg.stat_main_fixed), \
                        stat_sub_fixed = (self.stat_sub_fixed + arg.stat_sub_fixed))
    
    def as_dict(self, js_flag = False):
        if js_flag:
            return {"crit" : self.crit,
                            "crit_damage" : self.crit_damage,
                            "pdamage" : self.pdamage,
                            "pdamage_indep" : self.pdamage_indep,
                            "stat_main" : self.stat_main,
                            "stat_sub" : self.stat_sub,
                            "pstat_main":self.pstat_main,
                            "pstat_sub" : self.pstat_sub,
                            "boss_pdamage":self.boss_pdamage,
                            "armor_ignore":self.armor_ignore,
                            "patt":self.patt,
                            "att":self.att,
                            "stat_main_fixed":self.stat_main_fixed,
                            "stat_sub_fixed":self.stat_sub_fixed}        
        else:
            return {"crit" : self.crit,
                            "crit_damage" : self.crit_damage,
                            "pdamage" : self.pdamage,
                            "pdamage_indep" : self.pdamage_indep,
                            "stat_main" : self.stat_main,
                            "stat_sub" : self.stat_sub,
                            "pstat_main":self.pstat_main,
                            "pstat_sub" : self.pstat_sub,
                            "boss_pdamage":self.boss_pdamage,
                            "armor_ignore":self.armor_ignore,
                            "patt":self.patt,
                            "att":self.att,
                            "stat_main_fixed":self.stat_main_fixed,
                            "stat_sub_fixed":self.stat_sub_fixed}

    def _dynamic_variable_hint(self, character_modifier):
        if not isinstance(character_modifier, DynamicCharacterModifier):
            return DynamicCharacterModifier(crit = character_modifier.crit, crit_damage = character_modifier.crit_damage, pdamage = character_modifier.pdamage, 
                    pdamage_indep = character_modifier.pdamage_indep, stat_main = character_modifier.stat_main, stat_sub = character_modifier.stat_sub, 
                    pstat_main = character_modifier.pstat_main, pstat_sub = character_modifier.pstat_sub, boss_pdamage = character_modifier.boss_pdamage, 
                    armor_ignore = character_modifier.armor_ignore, patt = character_modifier.patt, att = character_modifier.att, stat_main_fixed = character_modifier.stat_main_fixed, stat_sub_fixed = character_modifier.stat_sub_fixed)
        else:
            return None

class DynamicCharacterModifier(DynamicVariableInstance, CharacterModifier):
    def __init__(self, **kwargs):
        DynamicVariableInstance.__init__(self)        
        parsed_kwargs = {k : DynamicVariableOperation.wrap_argument(a) for k, a in kwargs.items()}
        for k, a in parsed_kwargs.items():
            self.add_next_instance(a)
            a.inherit_namespace(k)
        CharacterModifier.__init__(self, **parsed_kwargs)

    def evaluate_override(self):
        return CharacterModifier(crit = self.crit.evaluate(),
                    crit_damage = self.crit_damage.evaluate(), pdamage = self.pdamage.evaluate(), 
                    pdamage_indep = self.pdamage_indep.evaluate(), stat_main = self.stat_main.evaluate(),
                    stat_sub = self.stat_sub.evaluate(), 
                    pstat_main = self.pstat_main.evaluate(), pstat_sub = self.pstat_sub.evaluate(), 
                    boss_pdamage = self.boss_pdamage.evaluate(), 
                    armor_ignore = self.armor_ignore.evaluate(), 
                    patt = self.patt.evaluate(), 
                    att = self.att.evaluate(), stat_main_fixed = self.stat_main_fixed.evaluate(), 
                    stat_sub_fixed = self.stat_sub_fixed.evaluate())
    

class InformedCharacterModifier(CharacterModifier):
    __slots__ = "name"
    def __init__(self, name, crit = 0, crit_damage = 0, pdamage = 0, pdamage_indep = 0, stat_main = 0, stat_sub = 0, pstat_main = 0, pstat_sub = 0, boss_pdamage = 0, armor_ignore = 0, patt = 0, att = 0, stat_main_fixed = 0, stat_sub_fixed = 0):
        super(InformedCharacterModifier, self).__init__(crit = crit, crit_damage = crit_damage, pdamage = pdamage, 
                    pdamage_indep = pdamage_indep, stat_main = stat_main, stat_sub = stat_sub, 
                    pstat_main = pstat_main, pstat_sub = pstat_sub, boss_pdamage = boss_pdamage, 
                    armor_ignore = armor_ignore, patt = patt, att = att, stat_main_fixed = stat_main_fixed, stat_sub_fixed = stat_sub_fixed)
        self.name = name

    def as_dict(self, js_flag = False):
        ret_dict = super(InformedCharacterModifier, self).as_dict(js_flag = js_flag)
        ret_dict['name'] = self.name
        return ret_dict

class ExtendedCharacterModifier(CharacterModifier):
    def __init__(self, buff_rem = 0, summon_rem = 0, cooltime_reduce = 0,prop_ignore = 0, **kwargs):
        super(ExtendedCharacterModifier, self).__init__(**kwargs)
        self.buff_rem = buff_rem
        self.summon_rem = summon_rem
        self.cooltime_reduce = cooltime_reduce
        self.prop_ignore = prop_ignore

    def degenerate(self):
        return super(ExtendedCharacterModifier, self).copy()

    def log(self):
        txt = super(ExtendedCharacterModifier, self).log()
        txt += "buff_rem %.1f, summon_rem %.1f, cooltime_reduce %.1f\n" % (self.buff_rem, self.summon_rem, self.cooltime_reduce)
        return txt
    
    def copy(self):
        return ExtendedCharacterModifier(buff_rem = self.buff_rem, summon_rem = self.summon_rem, cooltime_reduce = self.cooltime_reduce, prop_ignore = self.prop_ignore,
                    crit = self.crit, crit_damage = self.crit_damage, pdamage = self.pdamage, 
                    pdamage_indep = self.pdamage_indep, stat_main = self.stat_main, stat_sub = self.stat_sub, 
                    pstat_main = self.pstat_main, pstat_sub = self.pstat_sub, boss_pdamage = self.boss_pdamage, 
                    armor_ignore = self.armor_ignore, patt = self.patt, att = self.att, stat_main_fixed = self.stat_main_fixed, stat_sub_fixed = self.stat_sub_fixed)        
        
    def __add__(self, arg):
        return ExtendedCharacterModifier(
                        prop_ignore = self.prop_ignore + arg.prop_ignore,
                        buff_rem = (self.buff_rem + arg.buff_rem), 
                        summon_rem = (self.summon_rem + arg.summon_rem),
                        cooltime_reduce = (self.cooltime_reduce + arg.cooltime_reduce),
                        crit = (self.crit + arg.crit), \
                        crit_damage = (self.crit_damage + arg.crit_damage) , \
                        pdamage = (self.pdamage + arg.pdamage), \
                        pdamage_indep = (self.pdamage_indep + arg.pdamage_indep + (self.pdamage_indep * arg.pdamage_indep) * 0.01), \
                        stat_main = (self.stat_main + arg.stat_main),\
                        stat_sub = (self.stat_sub + arg.stat_sub), \
                        pstat_main = (self.pstat_main + arg.pstat_main), \
                        pstat_sub = (self.pstat_sub + arg.pstat_sub), \
                        boss_pdamage = (self.boss_pdamage + arg.boss_pdamage),\
                        armor_ignore = 100 - 0.01 * ((100 - self.armor_ignore) * (100 - arg.armor_ignore)), \
                        patt = (self.patt + arg.patt), \
                        att = (self.att + arg.att), \
                        stat_main_fixed = (self.stat_main_fixed + arg.stat_main_fixed), \
                        stat_sub_fixed = (self.stat_sub_fixed + arg.stat_sub_fixed))        

    def __iadd__(self, arg):
        return ExtendedCharacterModifier(
                        prop_ignore = self.prop_ignore + arg.prop_ignore,
                        buff_rem = (self.buff_rem + arg.buff_rem), 
                        summon_rem = (self.summon_rem + arg.summon_rem),
                        cooltime_reduce = (self.cooltime_reduce + arg.cooltime_reduce),
                        crit = (self.crit + arg.crit), \
                        crit_damage = (self.crit_damage + arg.crit_damage) , \
                        pdamage = (self.pdamage + arg.pdamage), \
                        pdamage_indep = (self.pdamage_indep + arg.pdamage_indep + (self.pdamage_indep * arg.pdamage_indep) * 0.01), \
                        stat_main = (self.stat_main + arg.stat_main),\
                        stat_sub = (self.stat_sub + arg.stat_sub), \
                        pstat_main = (self.pstat_main + arg.pstat_main), \
                        pstat_sub = (self.pstat_sub + arg.pstat_sub), \
                        boss_pdamage = (self.boss_pdamage + arg.boss_pdamage),\
                        armor_ignore = 100 - 0.01 * ((100 - self.armor_ignore) * (100 - arg.armor_ignore)), \
                        patt = (self.patt + arg.patt), \
                        att = (self.att + arg.att), \
                        stat_main_fixed = (self.stat_main_fixed + arg.stat_main_fixed), \
                        stat_sub_fixed = (self.stat_sub_fixed + arg.stat_sub_fixed))  


class VSkillModifier():
    @staticmethod
    def get_reinforcement(incr, lv, crit = False):
        armor = 0
        if lv >= 40:
            armor = 20
        if lv >= 20 and crit:
            return CharacterModifier(crit = 5, pdamage_indep = (lv * incr), armor_ignore = armor)
        else:
            return CharacterModifier(crit = 0, pdamage_indep = (lv * incr), armor_ignore = armor)


class AbstractSkill(EvaluativeGraphElement):
    '''Skill must have information about it's name, it's using - delay, skill using cooltime.
    Basic functions
    
    Can be re - implemented, but not mandate : 
    - dump_json : returns JSON for it's state.
    - load_json : from given JSON, set it's state.
    - get_info : return it's status as JSON.
    '''
    
    def __init__(self, name, delay, cooltime = 0, rem = False, red = True):
        super(AbstractSkill, self).__init__(namespace = name)
        self.spec = "graph control"
        with self.dynamic_range():            
            self.rem = rem
            self.red = red
            self.name = name
            self.delay = delay
            self.cooltime = cooltime
            self.explanation = None
    
            if self.cooltime == -1:
                self.cooltime = NOTWANTTOEXECUTE
                
    def _change_time_into_string(self, number_or_Infinite, divider = 1, lang = "ko"):
        lang_to_inf_dict = {"ko" : "무한/자동발동불가", "en" : "Infinite" }
        if abs(number_or_Infinite - NOTWANTTOEXECUTE / divider) < 10000 / divider:
            return lang_to_inf_dict[lang]
        else:
            return "%.1f" % number_or_Infinite
    
    def _parse_list_info_into_string(self, li):
        return "\n".join([   ":".join([i[0], "".join([str(j) for j in i[1:]])]) for i in li if len(str(i[1])) > 0])
    
    def set_explanation(self, strs):
        self.explanation = strs
    
    def get_explanation(self, lang = "ko", expl_level = 2):
        '''level 0 / 1 / 2
        '''
        if self.explanation is not None:
            return self.explanation
        else:
            return self._get_explanation_internal(lang = lang, expl_level = expl_level)
    
    def _get_explanation_internal(self, detail = False, lang = "ko", expl_level = 2):
        if lang == "en":
            li = [("skill name", self.name),
                    ("type", "AbstractSkill(Not implemented)")]
        elif lang == "ko":
            li = [("스킬 이름", self.name),
                    ("분류", "템플릿(상속되지 않음)")]
        
        return self._parse_list_info_into_string(li)
        
    def get_info(self, expl_level = 2):
        my_json = {"name" : self.name, "delay" : self._change_time_into_string(self.delay), "cooltime" : self._change_time_into_string(self.cooltime), "expl" : self.get_explanation(expl_level = expl_level)}
        return my_json  

    def wrap(self, wrapper, name = None):
        if name == None:
            return wrapper(self)
        else:
            return wrapper(self, name = name)

    def isV(self, enhancer, use_index, upgrade_index):
        '''Speed hack
        '''
        enhancer.add_v_skill(self, use_index, upgrade_index)
        return self


class BuffSkill(AbstractSkill):
    '''BuffSkill : Implements AbstractSkill, which contains baisc information about Skill. 
    Basic Templates for generating buff skill.
    - parameters
      
      .remain : Buff remainance
      .buff_remAvailFlag : Boolean whether buff remainance option could be applied or not. (Default : True)
      .static_character_modifier : Contains static - modifier.
      
      * go to CharacterModifier for find more detail about parameters.
      
    - methods
      
      Buff skill only need to return modifier, nothing else.
    
      .get_modifier() : returns CharacterModifier for Character.
    
    '''
    def __init__(self, name, delay, remain,  cooltime = 0, crit = 0, crit_damage = 0, pdamage = 0, stat_main = 0, stat_sub = 0, pstat_main = 0, pstat_sub = 0, boss_pdamage = 0, pdamage_indep = 0, armor_ignore = 0, patt = 0, att = 0, stat_main_fixed = 0, stat_sub_fixed = 0, rem = False, red = False):
        super(BuffSkill, self).__init__(name, delay, cooltime = cooltime, rem = rem, red = red)
        with self.dynamic_range():
            self.spec = "buff"
            self.remain = remain
            #Build StaticModifier from given arguments
            self.static_character_modifier = CharacterModifier(crit = crit, crit_damage = crit_damage, pdamage = pdamage, pdamage_indep = pdamage_indep, stat_main = stat_main, stat_sub = stat_sub, pstat_main = pstat_main, pstat_sub = pstat_sub, boss_pdamage = boss_pdamage, armor_ignore = armor_ignore, patt = patt, att = att, stat_main_fixed = stat_main_fixed, stat_sub_fixed = stat_sub_fixed)

    def _get_explanation_internal(self, detail = False, lang = "ko", expl_level = 2):
        if lang == "ko":
            li = [("스킬 이름",self.name),
                    ("분류","버프"),
                    ("딜레이","%.1f"%self.delay, "ms"),
                    ("지속 시간",self._change_time_into_string(self.remain/1000, divider = 1000), "s"),
                    ("쿨타임",self._change_time_into_string(self.cooltime/1000, divider = 1000), "s"),
                    ("쿨타임 감소 가능 여부", self.red),
                    ("지속시간 증가 여부", self.rem),
                    ("효과", ", ".join(  [(str(i[0]) + "+" + "".join([str(j) for j in i[1:]]) ) for i in self.static_character_modifier.abstract_log_list() ] ).replace("+미발동", " 미발동")) ]     
        
        if expl_level < 2:
            li = [li[3],li[7]]
        
        return self._parse_list_info_into_string(li)

    def get_modifier(self):
        '''You can override this function if needed(When your buff skill needs complicated calculation)
        * If your buff skill varies with time (e.g. Infinity), following modifier is recommended to calculate in ModifierWrapper.
        '''
        return self.static_character_modifier
        

class DamageSkill(AbstractSkill):
    '''DamageSkill : Implement AbstractSkill, which  contains baisc information about Skill. 
    Basic Template for generating deal skills.
    - methods
      .getSkillDamage() : returns Damage % for Character.
      .get_modifier() : returns CharacterModifier for Character.
      
    '''
    def __init__(self, name, delay, damage, hit,  cooltime = 0, modifier = CharacterModifier(), red = 0):
        super(DamageSkill, self).__init__(name, delay, cooltime = cooltime, rem = 0, red = red)
        with self.dynamic_range():
            self.spec = "damage"
            self.damage = damage
            self.hit = hit
            self._static_skill_modifier = modifier #Issue : Will we need this option really?

    def _get_explanation_internal(self, detail = False, lang = "ko", expl_level = 2):
        if lang == "ko":
            li = [("스킬 이름",self.name),
                    ("분류","공격기"),
                    ("딜레이","%.1f"%self.delay, "ms"),
                    ("퍼뎀", "%.1f"%self.damage,"%"),
                    ("타격수", self.hit),
                    ("쿨타임",self._change_time_into_string(self.cooltime/1000, divider = 1000), "s"),
                    ("쿨타임 감소 가능 여부", self.red),
                    ("지속시간 증가 여부", self.rem),
                    ("추가효과", ", ".join(  [(str(i[0]) + "+" + "".join([str(j) for j in i[1:]]) ) for i in self._static_skill_modifier.abstract_log_list() ] ).replace("+미발동%", " 미발동")) ]    
        
        if expl_level < 2:
            li = li[3:5] + [li[8]]
        
        return self._parse_list_info_into_string(li)
        
    def setV(self, v_enhancer, index, incr, crit = False):
        self._static_skill_modifier = self._static_skill_modifier + v_enhancer.get_reinforcement_with_register(index, incr, crit, self)
        return self
        
    def get_modifier(self):
        return self._static_skill_modifier
        
    def copy(self):
        return DamageSkill(self.name, self.delay, self.damage, self.hit, cooltime = self.cooltime, modifier = self._static_skill_modifier, red = self.red)
        

#TODO: optimize this factor more constructively
class SummonSkill(AbstractSkill):
    def __init__(self, name, summondelay, delay, damage, hit, remain, cooltime = 0, modifier = CharacterModifier(), rem = 0, red = 0):
        super(SummonSkill, self).__init__(name, delay, cooltime = cooltime, rem = rem, red = red)
        with self.dynamic_range():
            self.spec = "summon"
            self.summondelay = summondelay
            self.damage = damage
            self.hit = hit
            self.remain = remain
            self._static_skill_modifier = modifier

    def _get_explanation_internal(self, detail = False, lang = "ko", expl_level = 2):
        if lang == "ko":
            li = [("스킬 이름",self.name),
                    ("분류","소환기"),
                    ("딜레이","%.1f"%self.summondelay, "ms"),
                    ("타격주기", "%.1f"%self.delay, "ms"),
                    ("퍼뎀", "%.1f"%self.damage,"%"),
                    ("타격수", self.hit),
                    ("지속 시간", self._change_time_into_string(self.remain/1000, divider = 1000), "s"),
                    ("쿨타임",self._change_time_into_string(self.cooltime/1000, divider = 1000), "s"),
                    ("쿨타임 감소 가능 여부", self.red),
                    ("지속시간 증가 여부", self.rem),
                    ("추가효과", ", ".join(  [(str(i[0]) + "+" + "".join([str(j) for j in i[1:]]) ) for i in self._static_skill_modifier.abstract_log_list() ] ).replace("+미발동%", " 미발동")) ]   
        
        if expl_level < 2:
            li = li[3:7] + [li[10]]
        
        return self._parse_list_info_into_string(li)        

    def get_info(self, expl_level = 2):
        my_json = {"name" : self.name, "delay" : self._change_time_into_string(self.summondelay), "cooltime" : self._change_time_into_string(self.cooltime), "expl" : self.get_explanation(expl_level = expl_level)}
        return my_json 
    
    def setV(self, v_enhancer, index, incr, crit = False):
        self._static_skill_modifier = self._static_skill_modifier + v_enhancer.get_reinforcement_with_register(index, incr, crit, self)
        return self

        
    def get_modifier(self):
        return self._static_skill_modifier

class DotSkill(SummonSkill):
    def __init__(self, name, damage, remain):
        super(DotSkill, self).__init__(name, 0, 1000, damage, 1, remain, cooltime = -1, modifier = CharacterModifier(crit=-9999, armor_ignore=100))
        self.spec = "dot"

    def _get_explanation_internal(self, detail = False, lang = "ko", expl_level = 2):
        if lang == "ko":
            li = [("스킬 이름",self.name),
                    ("분류","도트뎀"),
                    ("딜레이","%.1f"%self.summondelay, "ms"),
                    ("타격주기", "%.1f"%self.delay,"ms"),
                    ("퍼뎀", "%.1f"%self.damage,"%"),
                    ("타격수", self.hit),
                    ("지속 시간", self._change_time_into_string(self.remain/1000, divider = 1000), "s"),
                    ("쿨타임",self._change_time_into_string(self.cooltime/1000, divider = 1000), "s"),
                    ("쿨타임 감소 가능 여부", self.red),
                    ("지속시간 증가 여부", self.rem),
                    ("추가효과", ", ".join(  [(str(i[0]) + "+" + "".join([str(j) for j in i[1:]]) ) for i in self._static_skill_modifier.abstract_log_list() ] ).replace("+미발동%", " 미발동")) ]   
        
        
        if expl_level < 2:
            li = li[3:7] + [li[10]]
            
        return self._parse_list_info_into_string(li)        
        

class EjaculateSkill(SummonSkill):
    def __init__(self, name, delay, damage, hit, remain, modifier = CharacterModifier()):
        super(EjaculateSkill, self).__init__(name, 0, delay, damage, hit, remain, cooltime = -1, modifier = modifier)
        self.spec = "ejac"
        
class Task():
    def __init__(self, ref, ftn):
        self._ref = ref
        self._ftn = ftn
        self._after = []
        self._before = []
        self._justAfter = []
        
    def getRef(self):
        return self._ref
        
    def do(self, **kwargs):
        return self._ftn()
        
    def onAfter(self, afters):
        self._after += afters
        
    def onBefore(self, befores):
        self._before += befores
        
    def onJustAfter(self, jafters):
        self._justAfter += jafters
        
    def copy(self):
        retTask = Task(self._ref, self._ftn)
        retTask.onAfter(self._after)
        retTask.onBefore(self._before)
        retTask.onJustAfter(self._justAfter)
        return retTask

class ContextReferringTask(Task):
    def do(self, **kwargs):
        return self._ftn(**kwargs)

class ResultObject():
    def __init__(self, delay, mdf, damage, hit, sname = 'Not specified', spec = 'Undefined', kwargs = {}, cascade = []):
        """Result object must be static; alway to be ensure it is revealed.
        """
        self.delay = DynamicVariableOperation.reveal_argument(delay)
        self.damage = DynamicVariableOperation.reveal_argument(damage)
        self.hit = DynamicVariableOperation.reveal_argument(hit)
        self.mdf = DynamicVariableOperation.reveal_argument(mdf)
        self.sname = DynamicVariableOperation.reveal_argument(sname)
        self.spec = DynamicVariableOperation.reveal_argument(spec)        #buff, deal, summon
        self.kwargs = DynamicVariableOperation.reveal_argument(kwargs)
        self.cascade = DynamicVariableOperation.reveal_argument(cascade)
        self.time = None
        
    def setTime(self, time):
        self.time = time

'''Default Values. Forbidden to editting.
'''
taskTerminater = ResultObject(0, CharacterModifier(), 0, 0, sname = 'terminator', spec = 'graph control')

class AccessibleBossState:
    NO_FLAG = 1
    LEVIATE = 2
    DISTANCE = 4
    INVINSIBLE = 8
    IMMUNE = 16
    
    ALWAYS = 31
    
    def __init__(self):
        pass

class GraphElement():
    '''class AbstractWrapper
    This clas define graph element's basic behaviors.
    Every graph elements must be connected with GraphElement.
    '''
    Flag_Skill = 1
    Flag_BaseSkill = 2
    Flag_BuffSkill = 4
    Flag_DamageSkill = 8
    Flag_SummonSkill = 16
    Flag_Optional = 32
    Flag_Repeat = 64
    Flag_Constraint = 128
    
    def __init__(self, _id):
        if isinstance(_id, AbstractDynamicVariableInstance):
            _id = _id.evaluate()
        self._id = _id
        self._before = []   #Tasks that must be executed before this task.
        self._after = []    #Tasks that must be executed after this task.
        self._run = []  #Tasks that must be executed if this task runs., deprecated.
        self._justAfter = []
        self._result_object_cache = ResultObject(0, CharacterModifier(), 0, 0, sname = 'Graph Element', spec = 'graph control')
        self._flag = 0
        self.accessible_boss_state = AccessibleBossState.NO_FLAG
        
    def fixAccesibleBossState(self, boss_state):
        self.accessible_boss_state = boss_state
    
    def removeAccesibleBossState(self, boss_state):
        self.accessible_boss_state = self.accessible_boss_state & (~boss_state)
    
    def setAccesibleBossState(self, boss_state):
        self.accessible_boss_state = self.accessible_boss_state | (boss_state)

    def set_flag(self, flag):
        self._flag = self._flag | flag
        
    def toggle_flag(self, flag):
        self._flag = self._flag ^ flag
    
    def remove_flag(self, flag):
        self._flag = self._flag & (~flag)
    
    def get_link(self):
        li = []
        for el in self._before:
            li.append([self, el, "before"])
        for el in self._after:
            li.append([self, el, "after"])
        for el in self._justAfter:
            li.append([self, el, "after"])
        return li

    def get_explanation(self, lang = "ko"):
        if lang == "ko":
            return "종류:그래프 요소"
        elif lang == "en":
            return "Type:graph Element"
        
    def _use(self) -> ResultObject:
        return self._result_object_cache
        
    def build_task(self, **kwargs) -> Task:
        task = Task(self, self._use)
        self.sync(task)
        return task
        
    def spend_time(self, time):
        return

    def onRun(self, el):
        self._run.append(el)
        
    def onRuns(self, ellist : list):
        self._run += ellist
        
    def onAfter(self, el):
        self._after = [el] + self._after 
        
    def onAfters(self, ellist : list):
        self._after = self._after  + ellist
        
    def onBefore(self, el):
        self._before = self._before + [el]
        
    def onBefores(self, ellist : list):
        self._before += ellist
        
    def sync(self, task):
        task.onBefore([el.build_task() for el in self._before])
        task.onAfter([el.build_task() for el in (self._run + self._after)])
        task.onJustAfter([el.build_task() for el in (self._justAfter)])
        
    def onJustAfter(self, task):
        self._justAfter += [task] + self._justAfter
        
    def onJustAfters(self, taskli):
        self._justAfter += taskli       
    
    def ignore(self):
        return None
    
    def ensure_condition(self, cond):
        if cond():
            return self
        else:
            return None
    
    def ensure(self, ehc, index_1, index_2):
        '''Shortcut(Hack)
        '''
        if ehc.getV(index_1, index_2) > 0:
            return self
        else:
            return None
        

class TaskHolder(GraphElement):
    '''This class only holds given task(Do not modify any property of task).
    '''
    def __init__(self, task, name = None):
        if name is None:
            name = "연결"
        super(TaskHolder, self).__init__(name)
        self._taskholder = task
    
    def get_explanation(self, lang = "ko"):
        if lang == "ko":
            return "%s" % self._id
        elif lang == "en":
            return "type:task holder\nname:%s" % self._id
        
    def build_task(self, **kwargs):
        task = self._taskholder.copy()
        self.sync(task)
        return task
        
    def get_link(self):
        li = super(TaskHolder, self).get_link()
        li.append([self, self._taskholder.getRef(), "effect"])
        return li

def create_task(task_name, task_function, task_ref):
    return TaskHolder(Task(task_ref, task_function), task_name)

class OptionalTask(Task):
    def __init__(self, ref, discriminator, task, failtask = None, name='optionalTask'):
        super(OptionalTask, self).__init__(ref, None)
        self._discriminator = discriminator
        self._result = task
        self._name = name
        self._failtask = failtask
        self._result_object_cache = ResultObject(0, CharacterModifier(), 0, 0, sname = self._name, spec = 'graph control', cascade = [self._result])
        if failtask == None:
            self._fail = ResultObject(0, CharacterModifier(), 0, 0, sname = self._name + " fail", spec = 'graph control')
        else:
            self._fail = ResultObject(0, CharacterModifier(), 0, 0, sname = self._name, spec = 'graph control', cascade = [failtask])

    def do(self, **kwargs):
        if(self._discriminator()):
            return self._result_object_cache
        else:
            return self._fail

class OptionalElement(GraphElement):
    def __init__(self, disc, after, fail = None, name = "Optional Element"):
        super(OptionalElement, self).__init__(name)
        self.disc = disc
        self.after = after
        self.fail = fail
        self.set_flag(self.Flag_Optional)
        
    def get_explanation(self, lang = "ko"):
        if lang == "ko":
            return "종류:조건적 실행\n%s" % self._id
        elif lang == "en":
            return "type:Optional Element\nname:%s" % self._id
        
    def build_task(self, **kwargs):
        if self.fail == None:
            fail = None
        else:
            fail = self.fail.build_task()
        task = OptionalTask(self, self.disc, self.after.build_task(), failtask = fail, name = self._id)
        self.sync(task)
        return task
        
    def get_link(self):
        li = super(OptionalElement, self).get_link()
        li.append([self, self.after, "if-true"])
        if self.fail is not None:
            li.append([self, self.fail, "if-false"])
        return li

class RepeatElement(GraphElement):
    def __init__(self, target, itr, name = None):
        if name is None:
            name = "%d회 반복" % itr
        super(RepeatElement, self).__init__(name)
        self._repeat_target = target
        self.itr = itr
        for i in range(itr):
            self.onAfter(target)
        self.set_flag(self.Flag_Repeat)
        self._result_object_cache = ResultObject(0, CharacterModifier(), 0, 0, sname = 'Repeat Element', spec = 'graph control')

    def get_explanation(self, lang = "ko"):
        if lang == "ko":
            return "종류:반복\n이름:%s\n반복대상:%s\n반복 횟수:%d" % (self._id, self._repeat_target._id, self.itr)
        elif lang == "en":
            return "type:Repeat Element\nname:%s\ntarget:%s\niterations:%d" % (self._id, self._repeat_target._id, self.itr)
            
    def _use(self):
        return self._result_object_cache
    
    def get_link(self):
        li = []
        li.append([self, self._repeat_target, "repeat "+str(self.itr)])
        for el in self._after:
            if el != self._repeat_target:
                li.append([self, el, "after"])
        for el in self._before:
            li.append([self, el, "before"])
        return li

class ConstraintElement(GraphElement):
    def __init__(self, name, ref, cnst):
        super(ConstraintElement, self).__init__(name)
        self._ref = ref
        self._ftn = cnst
        self.set_flag(self.Flag_Constraint)

    def get_explanation(self, lang = "ko"):
        if lang == "ko":
            return "종류:제한\n이름:%s" % self._id
        elif lang == "en":
            return "type:Constraint Element\nname:%s" % (self._id)
        
    def check(self):
        return self._ftn()
    
    def build_task(self):
        raise NotImplementedError("ConstraintElement must not builded.")
    
    def get_link(self):
        return [[self, self._ref, "check"]]
        
class AbstractSkillWrapper(GraphElement):
    def __init__(self, skill, name = None):
        if name is None:
            super(AbstractSkillWrapper, self).__init__(skill.name)
        else:
            super(AbstractSkillWrapper, self).__init__(name)
        self.set_flag(self.Flag_Skill)
        self.skill = skill
        self.available = True   # indicate whether this wrapper is usable.
        self.cooltimeLeft = 0   # indicate how much tiume left for use again this wrapper.
        self.timeLeft = 0       # indicate how much time left for continuing this wrapper.
        self.constraint = []
        self._result_object_cache = ResultObject(0, CharacterModifier(), 0, 0, sname = self.skill.name, spec = 'graph control')
        if DynamicVariableOperation.reveal_argument(self.skill.cooltime) == NOTWANTTOEXECUTE:
            self.set_disabled_and_time_left(-1)
        self.accessible_boss_state = AccessibleBossState.NO_FLAG

        # Context referring
        self._refer_runtime_context = False

    def enable_referring_runtime_context(self):
        '''If this is true, given skill wrapper may use runtime context.
        with this option, you MUST override _use() method with **kwargs argument is enabled.
        given context may passed by **kwargs option.
        '''
        self._refer_runtime_context = True

    def protect_from_running(self):
        constraint = ConstraintElement('사용 금지', self, lambda:False)
        self.onConstraint(constraint)

    def get_explanation(self, lang = "ko"):
        return self.skill.get_explanation(lang = lang)
    
    def get_link(self):
        li = super(AbstractSkillWrapper, self).get_link()
        for el in self.constraint:
            li.append([self, el, "abstract"])
        return li
        
    def assert_level_is_positive(self, reference_level):
        if reference_level > 0:
            return self
        else:
            return None
    
    def createConstraint(self, const_name, const_ref, const_ftn):
        self.onConstraint(ConstraintElement(const_name, const_ref, const_ftn))
        
    def onConstraint(self, constraint):
        self.constraint.append(constraint)
        
    def set_disabled_and_time_left(self, time):
        raise NotImplementedError
    
    def reduce_cooltime(self, time):
        self.cooltimeLeft -= time
        return self._result_object_cache

    def reduce_cooltime_p(self, p):
        self.cooltimeLeft -= self.cooltimeLeft * p
        return self._result_object_cache
    
    def controller(self, time, type_ = 'set_disabled_and_time_left', name = None):
        if type_ == 'set_disabled_and_time_left':
            if time == -1:
                _name = ("사용 불가")
            else:
                _name = ("%.1f초이후 시전" %(time*1.0/1000))
            task = Task(self, partial(self.set_disabled_and_time_left, time))
        elif type_ == 'reduce_cooltime':
            _name = ("쿨-%.1f초" %(time*1.0/1000))
            task = Task(self, partial(self.reduce_cooltime, time))
        elif type_ == 'reduce_cooltime_p':
            _name = "쿨-"+str(int(time*100))+"%"
            task = Task(self, partial(self.reduce_cooltime_p, time))
        elif type_ == 'set_enabled_and_time_left':
            _name = ("%.1f초간 시전" %(time*1.0/1000))
            task = Task(self, partial(self.set_enabled_and_time_left, time))
        else:
            raise TypeError("You must specify control type correctly.")
        if name is not None:
            return TaskHolder(task, name = name)
        else:
            return TaskHolder(task, name = _name)

    def _use(self, ftn, rem = 0, red = 0, **kwargs) -> ResultObject:
        raise NotImplementedError
        
    def build_task(self, rem = 0, red = 0) -> Task:
        if self._refer_runtime_context:
            task = self._build_task_with_referring_context(rem=rem, red=red)
        else:
            task = Task(self, partial(self._use, rem, red))
        self.sync(task)
        return task

    def _build_task_with_referring_context(self, rem = 0, red = 0):
        def context_referring_function(**kwargs):   # Task가 실행시킬 함수
            return self._use(rem=rem, red=red, **kwargs)
        
        return ContextReferringTask(self, context_referring_function)
        
    def is_usable(self):
        if len(self.constraint) > 0:
            for cnst in self.constraint:
                if not cnst.check():
                    return False
        return self.available

    def is_available(self):
        return self.available
    
    def is_not_usable(self):
        return (not self.is_usable())
        
    def spend_time(self, time):
        raise NotImplementedError
        self.time -= time
        self.cooltimeLeft -= time
        
    def is_active(self):
        return self.onoff

    def is_not_active(self):
        return (not self.onoff)
        
    def is_cooltime_left(self, time, direction):
        if (self.cooltimeLeft - time)*direction > 0: return True
        else : return False
        
    def is_time_left(self, time, direction):
        if (self.timeLeft - time) * direction > 0 : return True
        else: return False

class BuffSkillWrapper(AbstractSkillWrapper):
    def __init__(self, skill : BuffSkill, name = None):
        self._disabledResultobjectCache = ResultObject(0, CharacterModifier(), 0, 0, sname = skill.name, spec = 'graph control')
        super(BuffSkillWrapper, self).__init__(skill, name = name)
        self.set_flag(self.Flag_BuffSkill)
        self.onoff = False
        self._end = []
        self.disabledModifier = CharacterModifier()
        self.modifierInvariantFlag = True
        self.accessible_boss_state = AccessibleBossState.ALWAYS
        
    def set_enabled_and_time_left(self, time):
        '''This function must be carefull.. You must sure about this skill's cooltime calculation i.e. -1
        '''
        self.timeLeft = time
        if not self.onoff:
            self.cooltimeLeft = self.skill.cooltime
            self.onoff = True
        
        if self.cooltimeLeft > 0:
            self.available = False
        mdf = self.get_modifier()
        return ResultObject(0, mdf, 0, 0, sname = self.skill.name, spec = 'buff', kwargs = {"remain" : time})
        
    def set_disabled_and_time_left(self, time):
        self.timeLeft = 0
        self.cooltimeLeft = time
        self.available = False
        self.onoff = False
        if time == -1: self.cooltimeLeft = NOTWANTTOEXECUTE
        return self._disabledResultobjectCache
        
    def spend_time(self, time : int) -> None :  #TODO : can make this process more faster.. maybe
        self.timeLeft -= time
        self.cooltimeLeft -= time
        if self.timeLeft < 0:
            self.onoff = False
        if self.cooltimeLeft < 0:
            self.available = True
    
    def _use(self, rem = 0, red = 0) -> ResultObject:
        self.timeLeft = self.skill.remain * (1 + 0.01*rem * self.skill.rem)
        self.cooltimeLeft = self.skill.cooltime * (1 - 0.01*red* self.skill.red)
        self.onoff = True
        if self.cooltimeLeft > 0:
            self.available = False
        delay = self.skill.delay
        #mdf = self.get_modifier()
        return ResultObject(delay, CharacterModifier(), 0, 0, sname = self.skill.name, spec = self.skill.spec, kwargs = {"remain" : self.skill.remain * (1+0.01*rem*self.skill.rem)})

    def get_modifier(self) -> CharacterModifier:
        if self.onoff:
            return self.skill.get_modifier()
        else:
            return self.disabledModifier

    def get_modifier_forced(self):
        return self.skill.get_modifier()

    def onEnd(self, task):
        self._end.append(task)
        
    def onEnds(self, tasklist):
        self._end += tasklist

class StackSkillWrapper(BuffSkillWrapper):
    def __init__(self, skill, max_, modifier = CharacterModifier(), name = None):
        super(StackSkillWrapper, self).__init__(skill, name = name)
        self.stack = 0
        self._max = max_
        self._style = None
        self.modifierInvariantFlag = False
    
    def set_name_style(self, style):
        self._style = style
        
    def vary(self, d):
        self.stack = max(min((self.stack + d), self._max), 0)
        return ResultObject(0, CharacterModifier(), 0, 0, sname = self.skill.name, spec = 'graph control')
    
    def set_stack(self, d):
        self.stack = d
        return ResultObject(0, CharacterModifier(), 0, 0, sname = self.skill.name, spec = 'graph control')

    def get_modifier(self):
        return CharacterModifier()
    
    def stackController(self, d, name = None, dtype='vary'):
        if dtype=='vary':
            task = Task(self, partial(self.vary, d))
        elif dtype=='set':
            task = Task(self, partial(self.set_stack, d))
        if self._style is not None and name is None:
            name = self._style % (d)
        return TaskHolder(task, name = name)
        
    def judge(self, stack, direction):
        if (self.stack-stack)*direction>=0:return True
        else: return False

class TimeStackSkillWrapper(AbstractSkillWrapper):
    def __init__(self, skill, max_, modifier = CharacterModifier(), name = None):
        super(TimeStackSkillWrapper, self).__init__(skill, name = name)
        self.stack = 0
        self._max = max_
        self.queue = []
        
    def addStack(self, vary, left):
        self.queue.append([vary, left])
        return ResultObject(0, CharacterModifier(), 0, 0, sname = self.skill.name, spec = 'graph control')

    def stackController(self, vary, left, name = None):
        task = Task(self, partial(self.addStack, vary, left))
        return TaskHolder(task, name = name)
        
    def spend_time(self, time):
        queue = []
        for el in self.queue:
            el[1] -= time
            if el[1] > 0:
                queue.append(el)
        self.queue = queue
    
    def getStack(self):
        total = 0 
        for el in self.queue:
            total += el[0]
        return max(min(total, self._max), 0)
        
    def get_modifier(self):
        return CharacterModifier()
        
class DamageSkillWrapper(AbstractSkillWrapper):
    def __init__(self, skill : DamageSkill, modifier = CharacterModifier(), name = None):
        super(DamageSkillWrapper, self).__init__(skill, name = name)
        self.modifier = modifier
        self.accessible_boss_state = AccessibleBossState.NO_FLAG

    def set_disabled_and_time_left(self, time):
        self.cooltimeLeft = time
        if time == -1: self.cooltimeLeft = NOTWANTTOEXECUTE
        self.available = False
        return ResultObject(0, CharacterModifier(), 0, 0, sname = self.skill.name, spec = 'graph control')
        
    def spend_time(self, time : int) -> None:
        self.cooltimeLeft -= time
        if self.cooltimeLeft < 0:
            self.available = True
        
    def _use(self, rem = 0, red = 0):
        self.cooltimeLeft = self.skill.cooltime * (1-0.01*red*self.skill.red)
        if self.cooltimeLeft > 0:
            self.available = False
        return ResultObject(self.skill.delay, self.get_modifier(), self.skill.damage, self.skill.hit, sname = self.skill.name, spec = self.skill.spec)
        #return delay, mdf, dmg, self.cascade
        
    def get_modifier(self) -> CharacterModifier:
        return self.skill.get_modifier() + self.modifier

        
class SummonSkillWrapper(AbstractSkillWrapper):
    def __init__(self, skill : SummonSkill, modifier = CharacterModifier(), name = None):
        super(SummonSkillWrapper, self).__init__(skill, name = name)
        self.tick = 0
        self.onoff = False
        self.modifier = modifier
        self.disabledModifier = CharacterModifier()
        self._onTick = []
        self.accessible_boss_state = AccessibleBossState.NO_FLAG
        self.is_periodic = True
    
    def get_link(self):
        li = super(SummonSkillWrapper, self).get_link()
        for el in self._onTick:
            li.append([self, el, "tick"])
        return li
        
    def set_disabled_and_time_left(self, time):
        self.onoff = False
        self.available = False
        self.cooltimeLeft = time
        self.timeLeft = -1
        self.tick = 0
        if time == -1: self.cooltimeLeft = NOTWANTTOEXECUTE
        return ResultObject(0, CharacterModifier(), 0, 0, sname = self.skill.name, spec = 'graph control')
        
    def need_count(self):
        if self.onoff and (self.tick < 0):
            return True
        else:
            return False
        
    def spend_time(self, time : int) -> None:
        self.timeLeft -= time
        self.cooltimeLeft -= time
        self.tick -= time
        if self.timeLeft < 0:
            self.onoff = False
        if self.cooltimeLeft < 0:
            self.available = True
    
    #_use only alloted for start.
    def _use(self, rem = 0, red = 0):
        self.tick = 0
        self.onoff = True
        self.cooltimeLeft = self.skill.cooltime * (1-0.01*red*self.skill.red)
        self.timeLeft = self.skill.remain * (1+0.01*rem*self.skill.rem)
        if self.cooltimeLeft > 0:
            self.available = False
        return ResultObject(self.skill.summondelay, self.disabledModifier, 0, 0, sname = self.skill.name, spec = self.skill.spec)
    
    def _useTick(self):
        if self.onoff and self.tick <= 0:
            self.tick += self.skill.delay
            return ResultObject(0, self.get_modifier(), self.skill.damage, self.skill.hit, sname = self.skill.name, spec = self.skill.spec)
        else:
            return ResultObject(0, self.disabledModifier, 0, 0, sname = self.skill.name, spec = self.skill.spec)    
    
    def build_periodic_task(self):
        task = Task(self, self._useTick)
        task.onAfter([el.build_task() for el in self._onTick])
        return task
    
    def onTick(self, task):
        self._onTick.append(task)
        
    def onTicks(self, tasklist):
        self._onTick += tasklist
    
    def get_modifier(self):
        retMdf = self.skill.get_modifier() + self.modifier
        return retMdf        
    
class ScheduleGraph(AbstractScenarioGraph):
    def __init__(self, collection = None):
        super(ScheduleGraph, self).__init__()
        self._vEhc = None
        
        self.default_task = None
        
        self._rem = 0
        self._red = 0
        
        self.buff = []
        self.damage = []
        self.summon = []
        self.spend = []
        
        self.tick = []
        
        self.node = []  #Show direct view of graph!

    def get_accessibles(self):
        wrps = []
        for wrp, _ in (self.buff + self.damage + self.summon + self.spend + [self.default_task]):
            wrps.append(wrp)
        return wrps

    def set_v_enhancer(self, vEhc):
        self._vEhc = vEhc

    def add_timer(self, timer):
        self.spend.append([timer, timer.build_task()])

    @staticmethod
    def generateNode(graph, task):
        pass
    
    def get_network_information(self, style = "total"):
        '''get_network_information (param style : String)
        Return network information list as given style.
        '''
        
        if style == "buff":
            return self.get_single_network_information(self.buff, is_list = True)
        elif style == "damage":
            return self.get_single_network_information(self.damage + [self.default_task], is_list = True)
        elif style == "summon":
            return self.get_single_network_information(self.summon, is_list = True)
        elif style == "tick":
            return self.get_single_network_information(self.tick, is_list = True)
        elif style == "merged":
            return self.get_single_network_information(self.buff + self.damage + self.summon + self.spend + self.tick + [self.default_task], is_list = True)

    def get_default_buff_modifier(self):
        mdf = CharacterModifier()
        for wrp, _ in self.buff:
            if wrp.skill.cooltime == 0:
                mdf = mdf + wrp.skill.get_modifier()
        return mdf
        
    def build_graph(self, chtr, buffli, damageli, summonli, spendli, default_skill_wrapper):
        self.default_task = [default_skill_wrapper, default_skill_wrapper.build_task()]
        
        rem = chtr.buff_rem
        red = chtr.cooltimeReduce
        
        self._rem = rem
        self._red = red
        
        for wrp in buffli:
            if wrp is not None:
                self.buff.append([wrp, wrp.build_task(rem = rem, red = red)])
        for wrp in damageli:
            if wrp is not None:
                self.damage.append([wrp, wrp.build_task(rem = rem, red = red)])
        for wrp in summonli:
            if wrp is not None:
                self.summon.append([wrp, wrp.build_task(rem = rem, red = red)])
                self.tick.append([wrp, wrp.build_periodic_task()])
        for wrp in spendli:
            if wrp is not None:
                self.spend.append([wrp, wrp.build_task(rem = rem, red = red)])
                #self.tick.append([wrp, wrp.build_periodic_task()])
    
    def rebuild(self):
        for skill_list in [self.buff, self.damage, self.summon, self.spend]:
            for i, wx in enumerate(skill_list):
                skill_list[i][1] = wx.build_task(rem = self._rem, red = self._red)
    
    def initialize(self):
        pass
    
    def get_whole_skill_info(self, expl_level = 0):
        return{
            #"basic" : [self.default_task[0].skill.get_info(expl_level = expl_level)],
            "buff" : self.get_network_information(style = 'buff'),
            "damage" : self.get_network_information(style = 'damage'),
            "summon" : self.get_network_information(style = 'summon'),
            "spend" : self.get_network_information(style = 'spend'),
        }
    
    def get_detailed_skill_info(self, expl_level = 0):
        '''get_skill_info와 달리, 이 action은 더 자세한 정보를 리턴합니다.
        '''
        return{
            #"basic" : [self.default_task[0].skill.get_info(expl_level = expl_level)],
            "buff" : [s[0].skill.get_info(expl_level = expl_level) for s in self.buff],
            "damage" : [s[0].skill.get_info(expl_level = expl_level) for s in self.damage],
            "summon" : [s[0].skill.get_info(expl_level = expl_level) for s in self.summon],
            "spend" : [s[0].skill.get_info(expl_level = expl_level) for s in self.spend],
        }
    
    def spend_time(self, time):
        for wrp, _ in (self.buff + self.damage + self.summon + self.spend):
            wrp.spend_time(time)
    
    def get_skill_info(self):
        retli = {}
        snames = []
        for sk, name in self.buff + self.damage + self.summon + self.tick:
            if sk.skill.cooltime > 0: cooltime = 1
            else: cooltime = 0
            retli[sk._id] = {"cooltime" : cooltime, "type" : sk.skill.spec}
            if sk._id not in snames:
                snames.append(sk._id)
        
        return {"dict" : retli, "li" : snames}
            
class Simulator(object):
    __slots__ = 'scheduler', 'character', 'analytics', '_modifier_cache_and_time', '_default_modifier'
    def __init__(self, scheduler, chtr, analytics):
        self.scheduler = scheduler
        self.character = chtr
        self.analytics = analytics
        
        #vEnhancer를 Analytics에서 확인할 수 있도록 합니다.
        self.analytics.set_v_enhancer(self.scheduler.graph._vEhc.copy())
        
        #Buff modifier를 시간별도 캐싱하여 연산량을 줄입니다.
        self._modifier_cache_and_time = [-1,CharacterModifier()]

        self._default_modifier = CharacterModifier()

    def set_default_modifier(self, modifier):
        self._default_modifier = modifier

    def get_default_modifier(self):
        return self._default_modifier
    
    def get_skill_info(self):
        return self.analytics.get_skill_info()
        
    def get_results(self):
        return self.analytics.get_results()

    def get_metadata(self):
        mod = self.character.get_buffed_modifier()
        return self.analytics.get_metadata(mod)
        
    def getDPM(self, restricted = True):
        if not restricted:
            return self.get_unrestricted_DPM()
        else:
            return self.analytics.total_damage / (self.scheduler.total_time_initial) * 60000

    def get_unrestricted_DPM(self):
        return self.analytics.total_damage_without_restriction / (self.scheduler.total_time_initial) * 60000

    def getTotalDamage(self):
        return self.analytics.total_damage
    
    def start_simulation(self, time):
        self._modifier_cache_and_time = [-1, CharacterModifier()]
        self.scheduler.initialize(time)
        self.analytics.set_total_runtime(time)
        self.analytics.chtrmdf = self.character.get_modifier()
        self.character.generate_modifier_cache()             # 캐릭터의 Modifier를 매번 재계산 할 필요가 없으므로( 캐릭터의 상태는 시뮬레이션 도중 변화하지 않음) 캐싱하여 연산 자원을 절약합니다.
        while not self.scheduler.is_simulation_end():
            task = self.scheduler.dequeue()
            try:
                self.run_task(task)    
            except Exception as e:
                print(task._ref._id)
                print("error raised")
                print("---")
                raise e
    
    #recursive call
    def generate_task_stackStack(self, task):
        return (task._after + [task] + task._before)
    
    def run_task(self, task):
        self.run_task_recursive(task)
        
    def run_individual_task(self, task):
        '''
        try:
            print(task._ref._id)
        except:
            print(task)
            print(task.skill.name)
            raise AttributeError
        '''
        dt = 0
        stack = task._before
        while len(stack) != 0:
            dt += self.run_individual_task(stack.pop())

        runtime_context_modifier = self.scheduler.get_buff_modifier() + self.get_default_modifier()
        result = task.do(runtime_context_modifier=runtime_context_modifier + self.character.get_modifier())
        if result.damage > 0:
            result.mdf += runtime_context_modifier
        result.setTime(self.scheduler.get_current_time())
        self.analytics.analyze(self.character, result)
        dt += result.delay
        
        stack = task._after + result.cascade
        while len(stack) != 0:
            dt += self.run_individual_task(stack.pop())
        return dt

    def run_task_recursive(self, task):
        stack = task._before + []
        while len(stack) != 0:
            self.run_task_recursive(stack.pop())
        
        runtime_context_modifier = self.scheduler.get_buff_modifier() + self.get_default_modifier()
        result = task.do(runtime_context_modifier=runtime_context_modifier + self.character.get_modifier())
        
        if result.damage > 0:
            result.mdf += runtime_context_modifier

        result.setTime(self.scheduler.get_current_time())
        self.analytics.analyze(self.character, result)
        
        stk = task._justAfter + []
        while len(stk) != 0:
            self.run_task_recursive(stk.pop())
        
        if result.delay > 0:
            self.scheduler.spend_time(result.delay)
            while True:
                tick = self.scheduler.get_delayed_task()
                if tick != None:
                    self.run_task_recursive(tick)
                else:
                    break
        
        stack = result.cascade + task._after
        while len(stack) != 0:
            self.run_task_recursive(stack.pop())

class Analytics():
    def __init__(self, printFlag = False):
        self.total_damage = 0
        self.total_damage_without_restriction = 0
        self.logList = []
        self.meta_save = {}
        self.print_calculation_progress = printFlag
        self.skillList = {}
        self.chtrmdf = CharacterModifier()
        self._vEhc = None
        
    def set_v_enhancer(self, vEhc):
        self._vEhc = vEhc
        
    def set_total_runtime(self, time):
        self.totalTime = time
    
    def analyze(self, chtr, result):
        self.add_damage_from_result_with_log(chtr.get_modifier(), result)

    def log(self, txt):
        if self.print_calculation_progress:
            print(txt)

    def get_skill_info(self):
        return {"dict" : self.skillList, "li" : list(self.skillList.keys())}    
    
    def get_metadata(self, mod):
        meta = {"stat_main" : mod.stat_main,
                "stat_sub" : mod.stat_sub,
                "stat_main_fixed" : mod.stat_main_fixed,
                "pstat_main" : mod.pstat_main,
                "att" : mod.att,
                "patt" : mod.patt,
                "pdamage" : mod.pdamage + mod.boss_pdamage,
                "boss_pdamage" : mod.boss_pdamage,
                "armor_ignore" : mod.armor_ignore,
                "pdamage_indep" : mod.pdamage_indep,
                "effective_status" : mod.get_status_factor(),
                "crit_damage" : mod.crit_damage,
                "crit" : mod.crit
        }
                
        return meta
        
    def statistics(self):
        self.log("Total damage %.1f in %d second" % (self.total_damage, self.totalTime / 1000) )
        countDict = {}
        damageDict = {}
        for log in self.logList:
            if log["result"].sname not in countDict:
                countDict[log["result"].sname] = 0
                damageDict[log["result"].sname] = 0
            countDict[log["result"].sname] += 1
            damageDict[log["result"].sname] += log["deal"]
        
        for i in countDict:
            self.log("SKILL %s Used %d" % (i, countDict[i]))

        for i in damageDict:         
            if damageDict[i] > 0:   
                self.log("SKILL %s share is %f,  %.4f percent" % (i, damageDict[i], damageDict[i] / self.total_damage * 100))
        #self.log("Percent damage per second is %.2f" % (100*self.total_damage / self.character.get_modifier().get_damage_factor() / self.totalTimeInitial * 1000))

    def skill_share(self):
        damageDict = {}
        for log in self.logList:
            if log["deal"] > 0:
                if log["result"].sname not in damageDict:
                    damageDict[log["result"].sname] = 0
                damageDict[log["result"].sname] += log["deal"]
            
        return damageDict

        
    def get_results(self):
        retli = []
        for log in self.logList:
            retli.append({"time" : log["time"], 
                        "sname" : log["result"].sname, 
                        "deal" : log["deal"], 
                        "spec" : log["result"].spec, 
                        "else" : log["result"].kwargs})
        return retli
    
    def analyzeVEfficiency(self):
        '''V Core 각각의 효율을 계산합니다!
        '''
        
        damage_list_v_skill = []    #5차 스킬의 데미지를 저장합니다.
        damage_list_enhanced_skill = [] #강화 스킬의 데미지를 저장합니다.
        
        return
        
    def add_damage_from_result_with_log(self, charmdf, result):
        mdf = 0
        if result.damage > 0:
            mdf = charmdf + result.mdf
            
            deal, loss = mdf.calculate_damage(result.damage, result.hit, result.spec)
            free_deal = deal + loss
            
            #free_deal = mdf.get_damage_factor() * result.damage * 0.01
            #deal = min(result.hit * MAX_DAMAGE_RESTRICTION, free_deal)
        else: 
            deal = 0
            free_deal = 0
            
        if deal > 0:
            self.total_damage += deal
            self.total_damage_without_restriction += free_deal
        
        
        #For speed acceleration
        if self.print_calculation_progress:
            self.log('At Time %.1f, Skill [%s] ... Damage [%.1f] ... Loss [%.1f] ... Delay [%.1f]' % (result.time, result.sname, deal, free_deal - deal, result.delay))
            self.log(f'{result.mdf}')
        if deal > 0:
            self.logList.append({"result":result, "time" : (result.time), "deal" : deal, "loss" : free_deal - deal})
        else:
            self.logList.append({"result":result, "time" : (result.time), "deal" : 0, "loss" : 0})
        if result.sname not in self.skillList:
            self.skillList[result.sname] = {}
            
    def deduce_increment_of_temporal_modifier(self, continue_time_length, temporal_modifier,
                                            search_time_scan_rate = 1000):
        
        def search_time_index(time, hoping_rate_init = 100):
            hoping_rate = hoping_rate_init
            time_index = 0
            while True:
                if time_index >= len(self.logList):
                    time_index = len(self.logList) -1
                    break                
                if self.logList[time_index]["time"] < time:
                    time_index += hoping_rate
                else:
                    if self.logList[time_index - 1]["time"] <= time:
                        break
                    else:
                        hoping_rate = max(1, hoping_rate // 2)
                        time_index -= hoping_rate
                        time_index = max(0, time_index)
                        if time_index == 0:
                            return 0
                        
            return time_index
        
        def get_damage_sum_in_time_interval(time_start, time_length):
            damage_sum = 0
            time_log_index = max(0, search_time_index(time_start))
            #print("start_time_index", time_log_index, time_start)
                
            while self.logList[time_log_index]["time"] <= time_start + time_length and self.logList[time_log_index]["time"] >= time_start:
                damage_sum += self.logList[time_log_index]["deal"]
                time_log_index += 1
                if time_log_index >= len(self.logList):
                    break
            
            for t in range(time_log_index, time_log_index + 20):
                if t < len(self.logList):
                    if self.logList[t]["time"] <= time_start + time_length and self.logList[t]["time"] >= time_start:
                        damage_sum += self.logList[time_log_index]["deal"] 
            
            #print("end_time_index", time_log_index)
            
            #print("log",time_start, time_length, damage_sum)
            return damage_sum
        
        # search_time_scan_rate : 기록되어 있는 로그를 스캔할 시간주기입니다. 기본값 : 1000(ms)
        
        # scanning algorithm
        maximal_time_loc = 0
        damage_log_queue = [get_damage_sum_in_time_interval(i*search_time_scan_rate, search_time_scan_rate) for i in range(continue_time_length // search_time_scan_rate)]
        maximal_damage = sum(damage_log_queue)
        
        scanning_end_time = (continue_time_length // search_time_scan_rate)*search_time_scan_rate
        
        while scanning_end_time < self.totalTime:
            damage_log_queue.pop(0)
            damage_log_queue.append(get_damage_sum_in_time_interval(scanning_end_time, search_time_scan_rate))
            if sum(damage_log_queue) > maximal_damage:
                maximal_time_loc = scanning_end_time - continue_time_length
                maximal_damage = sum(damage_log_queue)
            scanning_end_time += search_time_scan_rate
        
        #Now we know when damage is maximized. We now apply our modifier into this.
        
        total_damage = 0
        for log in self.logList:
            result = log["result"]
            if result.damage > 0:
                mdf = self.chtrmdf + result.mdf
                if log["time"] >= maximal_time_loc and log["time"] < maximal_time_loc + continue_time_length:
                    mdf += temporal_modifier
                deal, loss = mdf.calculate_damage(result.damage, result.hit, result.spec)
                total_damage += deal
        
        simple_increment = ((self.chtrmdf + temporal_modifier).get_damage_factor() / (self.chtrmdf.get_damage_factor()) - 1) * (continue_time_length / self.totalTime)
        
        return {"damage" : (total_damage - self.total_damage) * (60000 / self.totalTime) , "increment" : (total_damage / self.total_damage) - 1, "simple_increment" : simple_increment}



class BasicVEnhancer(AbstractVEnhancer):
    def __init__(self):
        #### value list ####
        self.enhance_list = []
        self.v_skill_list = []
        self.core_number = None
        
        #### analytics list ####
        self.enhancer_priority = []  # 5차의 강화스킬 순서
        self.v_skill_priority = [] # 5차의 사용스킬 순서
    
    def get_priority(self):
        v_skill_list_sorted = [[] for i in range(20)]  #20 is magic number
        for vskill in self.v_skill_priority:
            v_skill_list_sorted[vskill["useIdx"]].append(vskill)
        
        return {"enhance" : [{"name" : skills[0].name.split('(')[0]} for skills in self.enhancer_priority if len(skills) > 0],
                "vskill" : [{"name" : skills[0]["target"].name.split('(')[0]} for skills in v_skill_list_sorted if len(skills) > 0]}
    
    def set_state_direct(self, li):
        self.enhance_list = li
        self.enhancer_priority = [[] for i in li]

    def set_vlevel_direct(self, li):
        self.v_skill_list = li

    def get_reinforcement_with_register(self, index, incr, crit, target):
        self.enhancer_priority[index].append(target)
        
        if index >= len(self.enhance_list):
            return CharacterModifier()
        else:
            return VSkillModifier.get_reinforcement(incr, self.enhance_list[index], crit)

    def getV(self, use_index, upgrade_index):
        if use_index <= len(self.v_skill_list):
            return self.v_skill_list[upgrade_index]
    
    def add_v_skill(self, target, use_index, upgrade_index):
        self.v_skill_priority.append({"target" : target, "useIdx" : use_index, "upgIdx" : upgrade_index})
        
    def copy(self):
        retval = BasicVEnhancer()
        retval.set_state_direct(self.enhance_list)
        retval.set_vlevel_direct(self.v_skill_list)
        return retval

    def __repr__(self):
        return "VEnhancer :: dpmModule.jobs.template\nVEnhance : %s\nVSkill : %s" % (str(self.enhance_list), str(self.v_skill_list))


class DirectVBuilder(AbstractVBuilder):
    def __init__(self, direct_enhance_state, direct_v_state):
        self.direct_enhance_state = direct_enhance_state
        self.direct_v_state = direct_v_state

    def build_enhancer(self, character, generator):
        enhancer = BasicVEnhancer()
        enhancer.set_state_direct(self.direct_enhance_state)
        enhancer.set_vlevel_direct(self.direct_v_state)
        return enhancer

class AlwaysMaximumVBuilder(AbstractVBuilder):
    def __init__(self):
        pass

    def build_enhancer(self, character, generator):
        enhancer = BasicVEnhancer()
        enhancer.set_state_direct([60 for i in range(15)])
        enhancer.set_vlevel_direct([30 for i in range(15)])        
        return enhancer

class NjbStyleVBuilder(AbstractVBuilder):
    def __init__(self, skill_core_level = 25, each_enhanced_amount = 17):
        self.skill_core_level = skill_core_level
        self.each_enhanced_amount = each_enhanced_amount

    def build_enhancer(self, character, generator):
        level = character.level
        cores = generator.vSkillNum
        return self.set_state_from_level_and_skill_cores(level, cores, self.skill_core_level, self.each_enhanced_amount)

    def set_state_from_level_and_skill_cores(self, level, skill_cores, skill_core_level, each_enhanced_amount):
        total_core_slots = 6 + (level - 200) // 5
        available_core_slots = max(total_core_slots - skill_cores, 0)
        level_bonus = level - 200
        
        enhance_state_will_be_setted = [0 for i in range(16)]
        
        if available_core_slots < 3 :
            for i in range(available_core_slots):
                for j in range(3):
                    enhance_state_will_be_setted[j] += 17
        else:
            for i in range(available_core_slots):
                enhance_state_will_be_setted[i] = 50
        
        while level_bonus > 0:
            chance_for_upgrade = min(level_bonus, 5)
            target_upgrade_skill_index = 0
            
            enhancement_left = 3 #하나의 코어는 3개의 스킬을 강화합니다.
            while target_upgrade_skill_index < len(enhance_state_will_be_setted) and enhancement_left > 0:
                if enhance_state_will_be_setted[target_upgrade_skill_index] < 60 : 
                    maximum_upgrade_level_available = 60 - enhance_state_will_be_setted[target_upgrade_skill_index]
                    actual_chance_for_upgrade = min(chance_for_upgrade, maximum_upgrade_level_available)
                    enhance_state_will_be_setted[target_upgrade_skill_index] += actual_chance_for_upgrade
                    enhancement_left -= 1
                    
                target_upgrade_skill_index += 1
                
            level_bonus -= chance_for_upgrade
            
        enhancer = BasicVEnhancer()
        enhancer.set_state_direct(enhance_state_will_be_setted)
        enhancer.set_vlevel_direct( [(i < skill_cores) * skill_core_level for i in range(10)] )
        return enhancer
