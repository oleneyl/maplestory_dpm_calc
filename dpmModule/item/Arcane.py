from . import ItemKernel as it
ExMDF = it.ExMDF

Head = it.Item(name="아케인셰이드 모자", level = 200, main_option=ExMDF(stat_main = 65, stat_sub = 65, att = 7, armor_ignore = 15))
Glove = it.Item(name="아케인셰이드 장갑", level = 200, main_option = ExMDF(stat_main = 40, stat_sub = 40, att = 9))
Shoes = it.Item(name="아케인셰이드 신발", level = 200, main_option = ExMDF(stat_main = 40, stat_sub = 40, att = 9))
Cloak = it.Item(name="아케인셰이드 망토", level = 200, main_option = ExMDF(stat_main = 35, stat_sub = 35, att = 6))
Shoulder = it.Item(name="아케인셰이드 견장", level = 200, main_option = ExMDF(stat_main = 35, stat_sub = 35, att = 20))

_valueMap = [[149, [0,27,40,55,72,92]],
                [216,[0,39,58,79,104,133]],
                [221,[0,40,59,81,106,136]],
                [264,[0,48,70,96,127,163]],
                [276,[0,50,73,101,133,170]],
                [283,[0,51,75,103,136,175]],
                [295,[0,54,78,108,142,182]],
                [302,[0,55,80,110,145,186]],
                [347,[0,63,92,126,167,214]],
                [353,[0,64,94,129,170,218]],
                [140,[0,0,0,0,0,0]],
                [295,[0,18,40,65,95,131]]]

WeaponFactory = it.WeaponFactoryClass(200, _valueMap, modifier = it.ExMDF(stat_main = 100, stat_sub = 100, boss_pdamage = 30, armor_ignore = 20))


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
            item.add_main_option(it.EnhancerFactory.get_armor_starforce_enhancement(200, star))
            if itemkey == "glove": #For glove
                item.add_main_option(it.EnhancerFactory.get_glove_scroll_enhancement(200, elist = scrolls[idx]))
                item.add_main_option(it.EnhancerFactory.get_glove_bonus_starforce_enhancement(star))
            else:
                item.add_main_option(it.EnhancerFactory.get_armor_scroll_enhancement(200, elist = scrolls[idx]))
            
        return package
    
    @staticmethod
    def getWeapon(_type, star, elist, potential = it.ExMDF(), additional_potential = it.ExMDF(), bonusAttIndex = 0, bonusElse = it.ExMDF()):
        
        return WeaponFactory.getWeapon(_type, star = star, elist = elist, potential = potential, additional_potential = additional_potential, bonusAttIndex = bonusAttIndex, bonusElse = bonusElse)

    @staticmethod
    def getBlade(_type, star, elist, potential = it.ExMDF(), additional_potential = it.ExMDF(), bonusElse = it.ExMDF()):

        return WeaponFactory.getBlade(_type, star = star, elist = elist, potential = potential, additional_potential = additional_potential, bonusElse = bonusElse)
    
    @staticmethod
    def getSetOption(rank):
        li = [it.ExMDF(), 
                it.ExMDF(att = 30), 
                it.ExMDF(att = 35, stat_main = 50, stat_sub = 50),
                it.ExMDF(att = 40, armor_ignore = 10),
                it.ExMDF(att = 30, boss_pdamage = 30),
                it.ExMDF(att = 30),
                it.ExMDF(att = 30, armor_ignore = 10)]
        
        retval = li[0]
        for i in range(rank):
            retval += li[i]
        
        return retval
    