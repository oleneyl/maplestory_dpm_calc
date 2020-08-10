from . import ItemKernel as it

Head = it.Item(stat_main = 45, stat_sub = 45, att = 3, armor_ignore = 10)
Glove = it.Item(stat_main = 20, stat_sub = 20, att = 5)
Shoes = it.Item(stat_main = 20, stat_sub = 20, att = 5)
Cloak = it.Item(stat_main = 15, stat_sub = 15, att = 2)
Shoulder = it.Item(stat_main = 14, stat_sub = 14, att = 10)

# 업횟 11+1
# 일반적인 템셋에서 카벨 모자를 사용할 직업은 제로뿐이므로 앱솔/아케인 무기 착용으로 가정
#ChaosVellumHelm = it.Item(stat_main = 23, stat_sub = 23, att = 1, boss_pdamage = 30)

_valueMap = [[103, [0,16,23,32,42,53]],
                [150,[0,23,33,46,60,77]],
                [154,[0,24,34,47,62,79]],
                [184,[0,28,41,56,74,95]],
                [192,[0,29,43,59,77,99]],
                [197,[0,30,44,60,79,101]],
                [205,[0,31,46,63,82,106]],
                [105,[0,32,47,64,84,108]],
                [241,[0,37,54,73,97,124]],
                [245,[0,37,54,75,98,126]],
                [97,[0,13,18,25,33,42]],
                [203,[0,11,23,38,56,76]]]#Need blade & Zero weapon

WeaponFactory = it.WeaponFactoryClass(160, _valueMap, modifier = it.CharacterModifier(stat_main = 40, stat_sub = 40, pdamage = 30, armor_ignore = 10))


class Factory():
    @staticmethod
    def getArmorSet(star = 0, enhance = 30, potential = it.CharacterModifier(), additional_potential = it.CharacterModifier(), bonus = it.CharacterModifier(), hammer = True):
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
            
        retli = [ Head.copy(), Glove.copy(), Shoes.copy(), Cloak.copy(), Shoulder.copy()]
        for idx, item in zip([0,1,2,3,4],retli):
            item.set_potential(potential)
            item.set_additional_potential(additional_potential)
            item.add_main_option(bonus)
            item.add_main_option(it.EnhancerFactory.get_armor_starforce_enhancement(160, star))
            if idx != 1:
                item.add_main_option(it.EnhancerFactory.get_armor_scroll_enhancement(160, elist = scrolls[idx]))
            else: #For glove
                item.add_main_option(it.EnhancerFactory.get_glove_scroll_enhancement(160, elist = scrolls[idx]))
                item.add_main_option(it.EnhancerFactory.getGloveStarforceEnhancement(star))
            
        return retli

    @staticmethod
    def getArmorSetDict(star = 0, enhance = 30, potential = it.CharacterModifier(), additional_potential = it.CharacterModifier(), bonus = it.CharacterModifier(), hammer = True):
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
            item.add_main_option(bonus)
            item.add_main_option(it.EnhancerFactory.get_armor_starforce_enhancement(160, star))
            if itemkey == "glove":
                item.add_main_option(it.EnhancerFactory.get_armor_scroll_enhancement(160, elist = scrolls[idx]))
            else: #For glove
                item.add_main_option(it.EnhancerFactory.get_glove_scroll_enhancement(160, elist = scrolls[idx]))
                item.add_main_option(it.EnhancerFactory.get_glove_bonus_starforce_enhancement(star))
            
        return package
    
    @staticmethod
    def getWeapon(_type, star = 0, elist = [0,0,0,9], potential = it.CharacterModifier(), additional_potential = it.CharacterModifier(), bonusAttIndex = 0, bonusElse = it.CharacterModifier()):
        
        return WeaponFactory.getWeapon(_type, star = star, elist = elist, potential = potential, additional_potential = additional_potential, bonusAttIndex = bonusAttIndex, bonusElse = bonusElse)

    @staticmethod
    def getBlade(_type, star = 0, elist = [0,0,0,0], potential = it.CharacterModifier(), additional_potential = it.CharacterModifier(), bonusElse = it.CharacterModifier()):

        return WeaponFactory.getBlade(_type, star = star, elist = elist, potential = potential, additional_potential = additional_potential, bonusElse = bonusElse)
    
    @staticmethod
    def getSetOption(rank):
        li = [it.CharacterModifier(), 
                it.CharacterModifier(att = 20), 
                it.CharacterModifier(att=25, stat_main = 30, stat_sub = 30),
                it.CharacterModifier(att = 30, armor_ignore = 10),
                it.CharacterModifier(att = 20, boss_pdamage = 30),
                it.CharacterModifier(att = 20),
                it.CharacterModifier(att = 20, armor_ignore = 10)]
        
        retval = li[0]
        for i in range(rank):
            retval += li[i]
        
        return retval
    