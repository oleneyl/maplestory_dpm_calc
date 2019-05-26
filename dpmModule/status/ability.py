from ..kernel import core

MDF = core.CharacterModifier
ExMDF = core.ExtendedCharacterModifier

class Ability_grade:
    '''
    0 : 노말
    1 : 레어
    2 : 에픽
    3 : 유니크
    4 : 레전
    '''
    def __init__(self, level, nth = 1):
        self.level_list = [level, 0, 0]
        if nth > 1:
            self.level_list[1] = level - 1
        if nth > 2:
            self.level_list[2] = level - 1


class Ability_option:
    '''level_to_mdf : 
    '''
    def __init__(self, level_to_mdf):
        self.level_to_mdf = level_to_mdf
        
    def mdf_of_level(self, level):
        return self.level_to_mdf[level]
        
    def copy(self):
        return Ability_option([i.copy() for i in self.level_to_mdf])


class Ability_tool:
    attack = Ability_option([ExMDF(), ExMDF(att = 3), ExMDF(att = 12), ExMDF(att = 21), ExMDF(att = 30)])
    buff_rem = Ability_option([ ExMDF(), ExMDF(buff_rem = 13), ExMDF(buff_rem = 25), ExMDF(buff_rem = 37), ExMDF(buff_rem = 50) ])
    boss_pdamage = Ability_option([ ExMDF(boss_pdamage = i*5) for i in range(5)])
    crit = Ability_option([ExMDF(), ExMDF(), ExMDF(crit = 10), ExMDF(crit=20), ExMDF(crit=30)])
    speed = Ability_option([ExMDF() for i in range(5)])
    multiple_target = Ability_option([ExMDF() for i in range(5)])
    empty = Ability_option([ExMDF() for i in range(5)])
    reuse = Ability_option([ExMDF() for i in range(5)])
    mess = Ability_option([ExMDF() for i in range(5)])
    
    @staticmethod
    def get_ability_set(*names):
        _names = names
        if len(_names) > 3:
            raise TypeError("get_ability_set max length : 3")
            
        def pick_ability(name):
            if name == "attack":
                return Ability_tool.attack.copy()
            if name == "buff_rem":
                return Ability_tool.buff_rem.copy()
            if name == "boss_pdamage":
                return Ability_tool.boss_pdamage.copy()
            if name == "crit":
                return Ability_tool.crit.copy()
            if name == "speed":
                return Ability_tool.speed.copy()
            if name == "multiple_target":
                return Ability_tool.multiple_target.copy()
            if name == "reuse":
                return Ability_tool.reuse.copy()          
            if name == "mess":
                return Ability_tool.mess.copy()
            if name == "passive_level":
                return Ability_tool.empty.copy()                
            if name == None:
                return Ability_tool.empty.copy()
        
        abilities = [pick_ability(name) for name in names]
        while len(abilities) < 3:
            abilities.append(Ability_tool.empty.copy())
        
        return abilities
        
    @staticmethod
    def adjusted_ability(grade, first_option, second_option, third_option):
        return_ability = ExMDF()
        return_ability += first_option.mdf_of_level(grade.level_list[0])
        return_ability += second_option.mdf_of_level(grade.level_list[1])
        return_ability += third_option.mdf_of_level(grade.level_list[2])
        return return_ability
