import json
from ..kernel.core import ExtendedCharacterModifier as ExMDF

class Item():
    '''Class Item : Holds informations about Item
    Items will hold information about given item.
    
    - parameters
    
      .name : Item's name. Need not be unique.
      .level : Item's required level.
      .main_option : Main Option.(ExtendedCharacterModifier)
      
      .potential : Potential Value.(ExtendedCharacterModifier)
      .add_potential : Additional Potential Value. (ExtendedCharacterModifier)
    '''
    def __init__(self, name, level, main_option: ExMDF, potential = ExMDF(), additional_potential = ExMDF()):
        #Prototypical option
        self.name = name
        #Main options
        self.main_option = main_option.copy()
        self.potential = potential.copy()
        self.additional_potential = additional_potential.copy()

        #Weapon base att
        self.weapon_base_att = None
        
        self.level = level

    def get_modifier(self):
        return self.main_option + self.potential + self.additional_potential
        
    def add_main_option(self, mf : ExMDF):
        self.main_option += mf
    
    def set_main_option(self, mf : ExMDF):
        self.main_option = mf.copy()
    
    def set_weapon_base_att(self, att: int):
        self.weapon_base_att = att
        
    def set_potential(self, mdf : ExMDF):
        self.potential = mdf.copy()
        
    def set_additional_potential(self, mdf : ExMDF):
        self.additional_potential = mdf.copy()
        
    def copy(self):
        return Item(name = self.name, level = self.level, main_option = self.main_option, potential = self.potential, additional_potential = self.additional_potential)
        
    def as_dict(self):
        potential_dict = self.potential.as_dict()
        additional_potential_dict = self.additional_potential.as_dict()
        return {"main" : self.main_option.as_dict(),
                "potential" : potential_dict,
                "additional_potential" : additional_potential_dict}
        
    def log(self):
        txt = "name : %s, level : %d\n"%(self.name, self.level)
        txt += "==main option==\n"
        txt += self.main_option.log()
        txt += "==potential==\n"
        txt += self.potential.log()
        txt += "==additional_potential==\n"
        txt += self.additional_potential.log()
        return txt

class EnhancerFactory():
    starforce_90_stat = [0, 2, 4, 6, 8, 10]
    starforce_90_armor_att = [0, 0, 0, 0, 0]
    
    starforce_100_stat = [0, 2, 4, 6, 8, 10, 13, 16, 19]
    starforce_100_armor_att = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    starforce_110_stat = [0, 2, 4, 6, 8, 10, 13, 16, 19, 22, 25]
    starforce_110_armor_att = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

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
        retMDF = ExMDF()
        
        now_star = 0
        while now_star < star:
            if now_star < 5:
                retMDF += ExMDF(stat_main = enhance_list[now_star], stat_sub = enhance_list[now_star])
            else:
                retMDF += ExMDF(att = enhance_list[now_star])
            now_star += 1
        
        return retMDF
    
    @classmethod
    def get_armor_starforce_enhancement(self, level, star):
        if level == 90:
            stli, atli = EnhancerFactory.starforce_90_stat, EnhancerFactory.starforce_90_armor_att
        elif level == 100:
            stli, atli = EnhancerFactory.starforce_100_stat, EnhancerFactory.starforce_100_armor_att
        elif level == 110:
            stli, atli = EnhancerFactory.starforce_110_stat, EnhancerFactory.starforce_110_armor_att
        elif level == 120:
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
            raise TypeError("Level Must be 90, 100, 110, 120, 130, 140, 150, 160, 200")
        return ExMDF(stat_main = stli[min(star, len(stli) - 1)], stat_sub = stli[min(star, len(stli) - 1)], att = atli[min(star, len(atli) - 1)])  
    
    @classmethod    
    def get_glove_scroll_enhancement(self, level, elist):
        if level <= 70:
            idx = 0
        else:
            idx = 1
        att = 0
        for i in range(3):
            att += elist[i] * self.glove_scroll_list[idx][i]
        return ExMDF(att = att)
    
    @classmethod
    def get_armor_scroll_enhancement(self, level, elist):
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
        return ExMDF(stat_main = stat_main, att = att)  

    @classmethod
    def get_glove_bonus_starforce_enhancement(self, star):
        return ExMDF(att = self.glove_starforce_att_list[star])
        
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
            
        att = weapon.main_option.att
        att_init = att
        
        for i in range(1,star + 1):
            if i <= 15:
                att += (att // 50) + 1
            else:
                att += atli[i]
        return ExMDF(stat_main = stli[star], stat_sub = stli[star], att  = (att - att_init))
    
    @classmethod
    def get_glove_starforce_enhancement(self, level, star):
        return EnhancerFactory.get_glove_bonus_starforce_enhancement(star) + EnhancerFactory.get_armor_starforce_enhancement(level, star)
    
    @classmethod
    def get_weapon_scroll_enhancement(self, level, elist):
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
        return ExMDF(stat_main = stat, att = att)

class WeaponFactoryClass():
    '''This is code for writing about weapon factory.
    With Korean, for more readability & fast coding
    '''
    wholeType = ["한손검", "한손도끼", "한손둔기", "두손검", "두손도끼",
                        "두손둔기", "창","튜너", "폴암", "데스페라도", "리볼버", "제로무기",
                        "완드", "스태프", "샤이닝로드", "ESP리미터", "건틀렛",
                        "활", "석궁", "듀얼보우건",
                        "단검", "아대", "블레이드", "케인", "에너지소드", "체인", "부채",
                        "건", "너클", "핸드캐논", "소울슈터"]

    typeMap = {"아대" : 0,
                    "건" : 1, 
                    "소울슈터" : 2, "에너지소드" : 2, "너클" : 2, "리볼버":2,
                    "폴암" : 3,
                    "단검":4, "체인":4, "활":4, "듀얼보우건":4, "부채":4,
                    "한손검":5, "한손둔기":5, "한손도끼":5, "케인":5, "석궁":5,
                    "데스페라도":6, "두손검":6, "두손둔기":6, "두손도끼":6, "창":6, "튜너":6,
                    "핸드캐논":7,
                    "완드":8,"샤이닝로드":8,"ESP리미터":8,"건틀렛":8,
                    "스태프":9,
                    "블레이드":10,
                    "제로무기":11}
                        
    def __init__(self, level, valueMap, modifier = ExMDF()):
        '''_dict : Dictionary for type - {"item" : Item, "bonus" : [0, int, int, int, int, int]}
        '''
        self.level = level
        self.valueMap = valueMap
        self.modifier = modifier
        
    def getWeapon(self, _type, star, elist, potential = ExMDF(), additional_potential = ExMDF(), bonusAttIndex = 0, bonusElse = ExMDF()):
        assert(_type in self.wholeType)
        if _type == '블레이드':
            _type = '단검'
        _att, _bonus = self.getMap(_type)
        item = Item(name = _type, main_option = self.modifier, level = self.level)
        item.set_weapon_base_att(_att)
        item.add_main_option(ExMDF(att = _att))
        item.add_main_option(EnhancerFactory.get_weapon_scroll_enhancement(self.level, elist))
        item.add_main_option(ExMDF(att = _bonus[-1*bonusAttIndex]))
        item.add_main_option(EnhancerFactory.get_weapon_starforce_enhancement(item, self.level, star))
        item.add_main_option(bonusElse)
        item.set_potential(potential)
        item.set_additional_potential(additional_potential)
        return item

    def getBlade(self, _type, star, elist, potential = ExMDF(), additional_potential = ExMDF(), bonusElse = ExMDF()):
        assert(_type == '블레이드')
        def get_blade_modifier():
            if self.modifier.stat_main == 100:
                return ExMDF(stat_main=65)
            if self.modifier.stat_main == 60:
                return ExMDF(stat_main=40)
            if self.modifier.stat_main == 40:
                return ExMDF(stat_main=30)
            raise TypeError("Invalid blade, (Arcane, Absolab, RootAbyss) is allowed.")

        _att, _bonus = self.getMap(_type)
        item = Item(name = "블레이드", main_option = get_blade_modifier(), level = self.level)
        item.add_main_option(ExMDF(att = _att))
        item.add_main_option(EnhancerFactory.get_weapon_scroll_enhancement(self.level, elist))
        item.add_main_option(EnhancerFactory.get_weapon_starforce_enhancement(item, self.level, star))
        item.add_main_option(bonusElse)
        item.set_potential(potential)
        item.set_additional_potential(additional_potential)
        return item

    def getZeroSubweapon(self, _type, potential = ExMDF(), additional_potential = ExMDF(), bonusElse = ExMDF()):
        assert(_type == '제로무기')
        item = Item(name = "제로보조", main_option = self.modifier, level = self.level)
        item.add_main_option(bonusElse)
        item.set_potential(potential)
        item.set_additional_potential(additional_potential)
        return item
    
    def getMap(self, _type):
        return self.valueMap[self.typeMap[_type]]