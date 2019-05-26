import json
#issue : Need to import CharacterModifier.

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
      
      .potential : Potential Value.
      .add_potential : Additional Potential Value.
    '''
    def __init__(self, name, stat_main = 0, stat_sub = 0, att = 0, patt = 0, pdamage = 0, armor_ignore = 0, pstat_main = 0, pstat_sub = 0, potential = Potential(), add_potential = Potential()):
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
        self.add_potential = add_potential
        
    def dump(self):
        """
        Status information. [name],[potential],[add_potential],[enhancement],[stars]
        information
        potential
        add_potential
        """
        dump = self.name
        if self.potential is None:
            dump += ",0"
        else:
            dump += ",1"
            
        if self.add_potential is None:
            dump += ",0"
        else:
            dump += ",1"
        dump += "\n"
        
        dump += str(self.stat_main) + "," + str(self.stat_sub) + "," + str(self.att) + "," + str(self.patt) + "," + str(self.pdamage) + "," + str(self.armor_ignore) + "\n"
        if self.potential is not None:
            dump += self.potential.dump()
            if self.add_potential is not None:
                dump += self.add_potential.dump()
                
        return dump
    
    def load(self, dump_string):
        lines = dump_string.split("\n")
        
        prototype = lines[0].split(",")
        self.name = prototype[0]
        
        vals = lines[1].split(",")
        self.stat_main = int(vals[0])
        self.stat_sub = int(vals[1])
        self.att = int(vals[2])
        self.patt = int(vals[3])
        self.pdamage = int(vals[4])
        self.armor_ignore = int(vals[5])

        if int(prototype[1]) == 1:
            self.potential = Potential()
            self.potential.dump(lines[2])
            
            if int(prototype[2]) == 1:
                self.add_potential = Potential()
                self.add_potential.dump(lines[3])
    
    def get_modifier(self):
        #Returns (CharacterModifier, CharacterModifier) tuple
        myModifier = CharacterModifier(stat_main = self.stat_main, stat_sub = self.stat_sub, att = self.att, patt = self.patt, pdamage = self.pdamage, armor_ignore = self.armor_ignore)
        return myModifier, self.potential.get_modifier() + self.add_potential.get_modifier()
        
    def addOption(self, mf):
        self.stat_main += mf.stat_main
        self.stat_sub += mf.stat_sub
        self.att += mf.att
        self.patt += mf.patt
        self.pdamage += mf.pdamage
        self.armor_ignore += mf.armor_ignore
        
        self.pstat_main += mf.pstat_main
        self.pstat_sub += mf.pstat_sub
        
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


        
class ItemedCharacter(Character):
    def __init__(self, modifierlist = [], level = 230):
        super(ItemedCharacter, self).__init__(modifierlist, level)
        
        self.itemlist["armor"] = {}     #7 items
        
        self.itemlist["armor"]["head"] = Item("default")
        self.itemlist["armor"]["glove"] = Item("default")
        self.itemlist["armor"]["top"] = Item("default")
        self.itemlist["armor"]["bottom"] = Item("default")
        self.itemlist["armor"]["shoes"] = Item("default")
        self.itemlist["armor"]["cloak"] = Item("default")
        self.itemlist["armor"]["head"] = Item("default")

        self.itemlist["accessory"] = {} #11 items
        
        self.itemlist["accessory"]["eye"] = Item("default")
        self.itemlist["accessory"]["face"] = Item("default")
        self.itemlist["accessory"]["ear"] = Item("default")
        self.itemlist["accessory"]["belt"] = Item("default")
        self.itemlist["accessory"]["ring1"] = Item("default")
        self.itemlist["accessory"]["ring2"] = Item("default")
        self.itemlist["accessory"]["ring3"] = Item("default")
        self.itemlist["accessory"]["ring4"] = Item("default")
        self.itemlist["accessory"]["shoulder"] = Item("default")
        self.itemlist["accessory"]["pendant1"] = Item("default")
        self.itemlist["accessory"]["pendant2"] = Item("default")
                
        self.itemlist["weapon"] = {}    # 3 items
        
        self.itemlist["weapon"]["weapon"] = Item("default")
        self.itemlist["weapon"]["subweapon"] = Item("default")
        self.itemlist["weapon"]["emblem"] = Item("default")
        
        self.itemlist["else"] = {}      #3 items
        
        self.itemlist["else"]["badge"] = Item("default")
        self.itemlist["else"]["medal"] = Item("default")
        self.itemlist["else"]["heart"] = Item("default")
        
    def loadItem(self, _type, attr, dump):
        if _type in self.itemlist:
            if attr in self.itemlist[_type]:
                self.itemlist[_type][attr].load(dump)
                return True
            else:
                return False
        else:
            return False
            
    def dumpItem(self, _type, attr):
        if _type in self.itemlist:
            if attr in self.itemlist[_type]:
                return True, self.itemlist[_type][attr].dump()
            else:
                #print("No attr exist %s" % attr)
                return False, None
        else:
            #print("No type exist %s" % _type)
            return False, None
            
    def load(self, dumpstr):
        dumpobj = json.loads(dumpstr)
        
        for _type in dumpobj:
            for attr in dumpobj[_type]:
                self.loadItem(_type, attr, dumpobj[_type][attr])

    def dump(self):
        dumpobj = {}
        for _type in self.itemlist:
            dumpobj[_type] = {}
            for attr in self.itemlist[_type]:
                dumpobj[_type][attr] = self.dumpItem(_type, attr)[1]
        
        return json.dumps(dumpobj)