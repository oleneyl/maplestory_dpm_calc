from . import ItemKernel as it

Head = it.Item(name="여제 모자", stat_main = 25, stat_sub = 25, att = 1, armor_ignore = 10, level = 140)
Glove = it.Item(name="여제 장갑", stat_main = 16, stat_sub = 16, att = 5, level = 140)
Shoes = it.Item(name="여제 신발", stat_main = 15, stat_sub = 15, att = 1, level = 140)
Cloak = it.Item(name="여제 망토", stat_main = 7, stat_sub = 7, att = 1, level = 140)
Shoulder = it.Item(name="여제 견장", stat_main = 11, stat_sub = 11, att = 7, level = 140)

_valueMap = [[69, [0,9,13,17,23,29]],
                [100,[0,12,18,25,32,41]],
                [102,[0,13,18,25,33,42]],
                [122,[0,15,22,30,39,51]],
                [128,[0,16,23,31,41,53]],
                [131,[0,16,24,32,42,54]],
                [137,[0,17,25,34,44,57]],
                [140,[0,17,25,34,45,58]],
                [161,[0,20,29,39,52,67]],
                [163,[0,20,29,40,53,67]],
                [None,[0,13,18,25,33,42]],
                [None,[0,13,18,25,33,42]]]#Need blade & Zero weapon

WeaponFactory = it.WeaponFactoryClass(140, _valueMap, modifier = it.ExMDF(stat_main = 35, stat_sub = 20))

class Factory():
    @staticmethod
    def getArmorSetDict(star, enhance, potential = it.ExMDF(), additional_potential = it.ExMDF(), bonus = it.ExMDF(), hammer = True):
        assert(enhance in [100, 70, 30])
        #TODO : Simplyfy this dirty codes.
        if not hammer: 
            upgrades = [11,7,7,7,1]
        else:
            upgrades = [12,8,8,8,2]
         
        if enhance == 100:
            scrolls = [[upgrades[i],0,0] for i in range(5)]
        elif enhance == 70:
            scrolls = [[0,upgrades[i],0] for i in range(5)]
        else:
            scrolls = [[0,0,upgrades[i]] for i in range(5)]
            
        package = {"head" : Head.copy(), "glove" : Glove.copy(), "shoes" : Shoes.copy(), "cloak" : Cloak.copy(), "shoulder" : Shoulder.copy()}
        keylist = ["head", "glove", "shoes", "cloak", "shoulder"]
        for idx, itemkey in zip([0,1,2,3,4], keylist):
            item = package[itemkey]
            item.set_potential(potential)
            item.set_additional_potential(additional_potential)
            if itemkey != "shoulder":
                item.add_main_option(bonus)
            item.add_main_option(it.EnhancerFactory.get_armor_starforce_enhancement(140, star))
            if itemkey == "glove": #For glove
                item.add_main_option(it.EnhancerFactory.get_glove_bonus_starforce_enhancement(star))
                item.add_main_option(it.EnhancerFactory.get_glove_scroll_enhancement(140, elist = scrolls[idx]))
            else:
                item.add_main_option(it.EnhancerFactory.get_armor_scroll_enhancement(140, elist = scrolls[idx]))
            
        return package
        
    @staticmethod
    def getWeapon(_type, star, elist, potential = it.ExMDF(), additional_potential = it.ExMDF(), bonusAttIndex = 0, bonusElse = it.ExMDF()):
        return WeaponFactory.getWeapon(_type, star = star, elist = elist, potential = potential, additional_potential = additional_potential, bonusAttIndex = bonusAttIndex, bonusElse = bonusElse )
        
    @staticmethod
    def getSetOption(rank):
        li = [it.ExMDF(), 
                it.ExMDF(), 
                it.ExMDF(),
                it.ExMDF(att = 15),
                it.ExMDF(stat_main = 20, stat_sub = 20),
                it.ExMDF(att = 30),
                it.ExMDF(att = 10)]
        
        retval = li[0]
        for i in range(rank):
            retval += li[i]
        
        return retval    
