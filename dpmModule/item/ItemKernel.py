import json
#issue : Need to import CharacterModifier.
from ..kernel.core import CharacterModifier
MDF = CharacterModifier

class Item():
    '''Class Item : Holds informations about Item
    Items will hold information about given item.
    
    - parameters
    
      .name : Item's name. Need not be unique.
      .stat_main : Main stat
      .stat_sub : Sub stat
      .att : AD(or MA) valule
      .patt : Ad(or MA) %
      .pdamage : Damage increment %
      .armor_ignore : Armor ignorant %
      
      .potential : Potential Value.(CharacterModifier)
      .add_potential : Additional Potential Value. (CharacterModifier)
    '''
    def __init__(self, name = 'DEFAULT', level = 150, stat_main = 0, stat_sub = 0, att = 0, patt = 0, pdamage = 0, armor_ignore = 0, pstat_main = 0, pstat_sub = 0, potential = CharacterModifier(), additional_potential = CharacterModifier()):
        #Prototypical option
        self.name = name
        #Main options
        self.stat_main = stat_main
        self.stat_sub = stat_sub
        self.att = att
        self.patt = patt
        self.pdamage = pdamage
        self.armor_ignore = armor_ignore
        
        self.pstat_main = pstat_main
        self.pstat_sub = pstat_sub
        
        self.potential = potential
        self.additional_potential = additional_potential
        
        self.level = level

    def get_modifier(self):
        #Returns (CharacterModifier, CharacterModifier) tuple
        myModifier = CharacterModifier(stat_main = self.stat_main, stat_sub = self.stat_sub, att = self.att, patt = self.patt, pdamage = self.pdamage, armor_ignore = self.armor_ignore)
        return myModifier, self.potential + self.additional_potential
        
    def add_main_option(self, mf : CharacterModifier):
        self.stat_main += mf.stat_main
        self.stat_sub += mf.stat_sub
        self.att += mf.att
        self.patt += mf.patt
        self.pdamage += mf.pdamage
        self.armor_ignore += mf.armor_ignore
        
        self.pstat_main += mf.pstat_main
        self.pstat_sub += mf.pstat_sub
    
    def set_main_option(self, mf : CharacterModifier):
        self.stat_main = mf.stat_main
        self.stat_sub = mf.stat_sub
        self.att = mf.att
        self.patt = mf.patt
        self.pdamage = mf.pdamage
        self.armor_ignore = mf.armor_ignore
        
        self.pstat_main = mf.pstat_main
        self.pstat_sub = mf.pstat_sub
        
    def set_potential(self, mdf : CharacterModifier):
        self.potential = mdf.copy()
        
    def set_additional_potential(self, mdf : CharacterModifier):
        self.additional_potential = mdf.copy()
        
    def copy(self):
        return Item(stat_main = self.stat_main, \
        stat_sub = self.stat_sub, att = self.att, patt = self.patt, pdamage = self.pdamage,\
        armor_ignore = self.armor_ignore, pstat_main = self.pstat_main, pstat_sub = self.pstat_sub, \
        potential = self.potential, \
        additional_potential = self.additional_potential)
        
    def as_dict(self):
        return {"main" : {"stat_main" : self.stat_main, "stat_sub" : self.stat_sub, "att" : self.att, "armor_ignore" : self.armor_ignore, "pstat_main" : self.pstat_main, "pstat_sub" : self.pstat_sub},
                "potential" : self.potential.as_dict(),
                "additional_potential" : self.additional_potential.as_dict()}
        
class Potential():
    def __init__(self):
        self.stat_main = 0
        self.stat_sub = 0
        self.pstat_main = 0
        self.pstat_sub = 0
        
        self.att = 0
        self.patt = 0
        self.pdamage = 0
        self.boss_pdamage = 0
        self.armor_ignore = 0
        
        self.crit = 0
        self.crit_damage = 0
    
    def dump(self):
        dump = str(self.stat_main) + "," + str(self.stat_sub) + "," + str(self.pstat_main) + "," + str(self.pstat_sub) + "," + str(self.att) + "," + str(self.patt) + "," + self.pdamage + "," + self.boss_pdamage + "," + self.armor_ignore + "," + self.crit
        return dump
        
    def load(self, dump_string):
        vals = dump_string.split(",")
        self.stat_main = int(vals[0])
        self.stat_sub = int(vals[1])
        self.pstat_main = int(vals[2])
        self.pstat_sub = int(vals[3])
        
        self.att = int(vals[4])
        self.patt = int(vals[5])
        self.pdamage = int(vals[6])
        self.boss_pdamage = int(vals[7])
        self.armor_ignore = int(vals[8])
        
        self.crit = int(vals[9])
        
    def get_modifier(self):
        return CharacterModifier(stat_main = self.stat_main, stat_sub = self.stat_sub, pstat_main = self.pstat_main, pstat_sub = self.pstat_sub, att = self.att, patt = self.patt, pdamage = self.pdamage, boss_pdamage = self.boss_pdamage, armor_ignore = self.armor_ignore, crit = self.crit, crit_damage = self.crit_damage)

class EnhancerFactory():
    starforce_120_stat = [0, 2, 4, 6, 8, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40]
    starforce_120_armor_att = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]    
    
    starforce_130_stat = [0, 2, 4, 6, 8, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 47, 54, 61, 68, 75]
    starforce_130_armor_att = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 15, 24, 34, 45]    
    
    starforce_140_stat = [0, 2, 4, 6, 8, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 49, 58, 67, 76, 85, 94, 103]
    starforce_140_armor_att = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 17, 27, 38, 50, 63, 78]
    
    starforce_150_stat = [0, 2, 4, 6, 8, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 51, 62, 73, 84, 95, 106, 117]
    starforce_150_armor_att = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 19, 30, 42, 55, 69, 85]
    
    starforce_160_stat = [0, 2, 4, 6, 8, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 53, 66, 79, 92, 105, 118, 131]
    starforce_160_armor_att = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 21, 33, 46, 60, 75, 92]
    
    starforce_200_stat = [0, 2, 4, 6, 8, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 55, 70, 85, 100, 115, 130, 145]
    starforce_200_armor_att = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 25, 39, 54, 70, 87, 106]
    
    armor_scroll_list = [[1,2,3],[2,3,5],[3,4,7]]
    glove_scroll_list = [[0,1,2],[1,2,3]]
    glove_starforce_att_list = [0,0,0,0,0,1,1,2,2,3,3,4,4,5,6,7,7,7,7,7,7,7,7,7]
    
    starforce_130_weapon_att_delta = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6,7,7,8,9]
    starforce_140_weapon_att_delta = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,8,9,10,11,12]
    starforce_150_weapon_att_delta = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,9,9,10,11,12,13]
    starforce_160_weapon_att_delta = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,9,10,11,12,13,14]
    starforce_200_weapon_att_delta = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,13,13,14,14,15,16,17]
    
    weapon_scroll_stat = [[0,0,1,2], [0,1,2,3], [1,2,3,4]] 
    weapon_scroll_att = [[1,2,3,5],[2,3,5,7],[3,5,7,9]]
    
    surprise_starforce_70_delta = [1,2,4,7,11,1,2,3,4,5,6,8]
    surprise_starforce_80_delta = [2,3,5,8,12,2,3,4,5,6,7,9]
    surprise_starforce_90_delta = [4,5,7,10,14,3,4,5,6,7,8,10]
    surprise_starforce_100_delta = [7,8,10,13,17,4,5,6,0,0,0,0]
    surprise_starforce_110_delta = [12,13,15,18,22,6,7,8,9,10,0,0]
    surprise_starforce_120_delta = [12,13,15,18,22,6,7,8,9,10,11,13]
    surprise_starforce_130_delta = [14,15,17,20,24,7,8,9,10,11,12,14]
    surprise_starforce_140_delta = [17,18,20,23,27,8,9,10,11,12,13,15]
    surprise_starforce_150_delta = [19,20,22,25,29,9,10,11,12,13,14,16]
    
    
    
    def __init__(self):
        thisis = "Factory Class"
    
    @classmethod
    def get_surprise_enhance_list_direct(self, level):
        if level < 80:
            return EnhancerFactory.surprise_starforce_70_delta
        else:
            if level % 10 != 0:
                raise TypeError("given parameter level must be multiple of 10")
            if level == 80:
                return EnhancerFactory.surprise_starforce_80_delta
            if level == 90:
                return EnhancerFactory.surprise_starforce_90_delta
            if level == 100:
                return EnhancerFactory.surprise_starforce_100_delta
            if level == 110:
                return EnhancerFactory.surprise_starforce_110_delta
            if level == 120:
                return EnhancerFactory.surprise_starforce_120_delta
            if level == 130:
                return EnhancerFactory.surprise_starforce_130_delta
            if level == 140:
                return EnhancerFactory.surprise_starforce_140_delta
            if level == 150:
                return EnhancerFactory.surprise_starforce_150_delta

    @classmethod
    def get_surprise_enhance_list(self, level):
        '''This function ensures class variable safety.
        '''
        if level < 80:
            return [i for i in  EnhancerFactory.surprise_starforce_70_delta]
        else:
            if level % 10 != 0:
                return [i for i in EnhancerFactory.get_surprise_enhance_list_direct(level)]
            else:
                low_list = EnhancerFactory.get_surprise_enhance_list_direct((level // 10) * 10 )
                high_list = EnhancerFactory.get_surprise_enhance_list_direct((level // 10) * 10 )
                retli = []
                for i in range(5):
                    retli.append(  (low_list[i] + high_list[i]) // 2)
                for i in range(7):
                    retli.append( low_list[i + 5] )
                return retli
                
    
    @classmethod
    def get_surprise_enhancement(self, level, star):
        enhance_list = EnhancerFactory.get_surprise_enhance_list(level)
        retMDF = MDF()
        
        now_star = 0
        while now_star < star:
            if now_star < 5:
                retMDF += MDF(stat_main = enhance_list[now_star], stat_sub = enhance_list[now_star])
            else:
                retMDF += MDF(att = enhance_list[now_star])
            now_star += 1
        
        return retMDF
    
    @classmethod
    def get_armor_starforce_enhancement(self, level, star):
        if level == 120:
            stli, atli = EnhancerFactory.starforce_120_stat, EnhancerFactory.starforce_120_armor_att
        elif level == 130:
            stli, atli = EnhancerFactory.starforce_130_stat, EnhancerFactory.starforce_130_armor_att
        elif level == 140:
            stli, atli = EnhancerFactory.starforce_140_stat, EnhancerFactory.starforce_140_armor_att
        elif level == 150:
            stli, atli = EnhancerFactory.starforce_150_stat, EnhancerFactory.starforce_150_armor_att
        elif level == 160:
            stli, atli = EnhancerFactory.starforce_160_stat, EnhancerFactory.starforce_160_armor_att
        elif level == 200:
            stli, atli = EnhancerFactory.starforce_200_stat, EnhancerFactory.starforce_200_armor_att            
        else:
            raise TypeError("Level Must be 120, 130, 140, 150, 160, 200")
        return CharacterModifier(stat_main = stli[star], stat_sub = stli[star], att = atli[star])  
    
    @classmethod    
    def get_glove_scroll_enhancement(self, level, elist = [0, 0, 0]):
        if level <= 70:
            idx = 0
        else:
            idx = 1
        att = 0
        for i in range(3):
            att += elist[i] * self.glove_scroll_list[idx][i]
        return CharacterModifier(att = att)
    
    @classmethod
    def get_armor_scroll_enhancement(self, level, elist = [0,0,0]):
        if level <= 70:
            idx = 0
        elif level <= 110:
            idx = 1
        else:
            idx = 2        
        stat_main = 0
        for i in range(3):
            stat_main += elist[i] * self.armor_scroll_list[idx][i]
        att = 0
        if elist[0] + elist[1] + elist[2] >= 4: att = 1
        return CharacterModifier(stat_main = stat_main, att = att)  

    @classmethod
    def get_glove_bonus_starforce_enhancement(self, level, star):
        return CharacterModifier(att = self.glove_starforce_att_list[star])
        
    @classmethod
    def get_weapon_starforce_enhancement(self, weapon, level, star):
        if level == 130:
            stli, atli = EnhancerFactory.starforce_130_stat, EnhancerFactory.starforce_130_weapon_att_delta
        elif level == 140:
            stli, atli = EnhancerFactory.starforce_140_stat, EnhancerFactory.starforce_140_weapon_att_delta
        elif level == 150:
            stli, atli = EnhancerFactory.starforce_150_stat, EnhancerFactory.starforce_150_weapon_att_delta
        elif level == 160:
            stli, atli = EnhancerFactory.starforce_160_stat, EnhancerFactory.starforce_160_weapon_att_delta
        elif level == 200:
            stli, atli = EnhancerFactory.starforce_200_stat, EnhancerFactory.starforce_200_weapon_att_delta            
        else:
            raise TypeError("Level Must be 130, 140, 150, 160, 200")
            
        att = weapon.att
        att_init = att
        
        for i in range(1,star + 1):
            if i <= 15:
                att += (att // 50) + 1
            else:
                att += atli[i]
        return CharacterModifier(stat_main = stli[star], stat_sub = stli[star], att  = (att - att_init))
    
    @classmethod
    def get_glove_starforce_enhancement(self, level, star):
        return EnhancerFactory.get_glove_bonus_starforce_enhancement(level, star) + EnhancerFactory.get_armor_starforce_enhancement(level, star)
    
    @classmethod
    def get_weapon_scroll_enhancement(self, level, elist = [0,0,0,0]):
        if level <= 70:
            idx = 0
        elif level <= 110:
            idx = 1
        else:
            idx = 2
            
        stat, att = 0, 0
        for i in range(4):
            att += elist[i] * self.weapon_scroll_att[idx][i]
            stat += elist[i] * self.weapon_scroll_stat[idx][i]
        return CharacterModifier(stat_main = stat, att = att)

class WeaponFactoryClass():
    '''This is code for writing about weapon factory.
    With Korean, for more readability & fast coding
    '''
    wholeType = ["한손검", "한손도끼", "한손둔기", "두손검", "두손도끼",
                        "두손둔기", "창", "폴암", "데스페라도", "리볼버", "제로무기",
                        "완드", "스태프", "샤이닝로드", "ESP리미터", "건틀렛",
                        "활", "석궁", "듀얼보우건",
                        "단검", "아대", "블레이드", "케인", "에너지소드", "체인", 
                        "건", "너클", "핸드캐논", "소울슈터"]

    typeMap = {"아대" : 0,
                    "건" : 1, 
                    "소울슈터" : 2, "에너지소드" : 2, "너클" : 2, "리볼버":2,
                    "폴암" : 3,
                    "단검":4, "체인":4, "활":4, "듀얼보우건":4, 
                    "한손검":5, "한손둔기":5, "한손도끼":5, "케인":5, "석궁":5,
                    "데스페라도":6, "두손검":6, "두손둔기":6, "두손도끼":6, "창":6,
                    "핸드캐논":7,
                    "완드":8,"샤이닝로드":8,"ESP리미터":8,"건틀렛":8,
                    "스태프":9,
                    "블레이드":10,
                    "제로무기":11}
                        
    def __init__(self, level, valueMap, modifier = CharacterModifier()):
        '''_dict : Dictionary for type - {"item" : Item, "bonus" : [0, int, int, int, int, int]}
        '''
        self.level = level
        self.valueMap = valueMap
        self.modifier = modifier
        
    def getWeapon(self, _type, star = 0, elist = [0,0,0,0], potential = CharacterModifier(), additional_potential = CharacterModifier(), bonusAttIndex = 0, bonusElse = CharacterModifier()):
        assert(_type in self.wholeType)
        _att, _bonus = self.getMap(_type)
        item = Item(att = _att)
        item.add_main_option(self.modifier)
        item.add_main_option(EnhancerFactory.get_weapon_scroll_enhancement(self.level, elist))
        item.add_main_option(CharacterModifier(att = _bonus[-1*bonusAttIndex]))
        item.add_main_option(EnhancerFactory.get_weapon_starforce_enhancement(item, self.level, star))
        item.add_main_option(bonusElse)
        item.set_potential(potential)
        item.set_additional_potential(additional_potential)        
        return item
    
    def getMap(self, _type):
        return self.valueMap[self.typeMap[_type]]