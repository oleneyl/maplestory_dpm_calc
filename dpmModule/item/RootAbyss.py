from . import ItemKernel as it

## Armors ##
#No upgrade
Top = it.Item(name="이글아이 아머", stat_main = 30, stat_sub = 30, att = 2, armor_ignore = 5, level = 150)
Bottom = it.Item(name="트릭스터 팬츠", stat_main = 30, stat_sub = 30, att = 2, armor_ignore = 5, level = 150)
Head = it.Item(name="하이네스 햇", stat_main = 40, stat_sub = 40, att = 2, armor_ignore = 10, level = 150)

_valueMap = [[86, [0,11,16,21,28,36]],
                [125,[0,15,22,31,40,52]],
                [128,[0,16,23,31,41,53]],
                [153,[0,19,27,38,49,63]],
                [160,[0,20,29,39,52,66]],
                [164,[0,20,29,40,53,68]],
                [171,[0,21,31,42,55,71]],
                [175,[0,21,31,43,56,72]],
                [201,[0,25,36,49,65,83]],
                [204,[0,25,36,50,66,84]],
                [81,[0,13,18,25,33,42]],
                [169,[0,9,20,32,47,64]]]#Need blade & Zero weapon

WeaponFactory = it.WeaponFactoryClass(150, _valueMap, modifier = it.CharacterModifier(stat_main = 40, stat_sub = 40, pdamage = 30, armor_ignore = 10))


class Factory():
    @staticmethod
    def getArmorSetDict(star, enhance, potential = it.CharacterModifier(), additional_potential = it.CharacterModifier(), bonus = it.CharacterModifier(), hammer = True):
        if not hammer: 
            upgrades = [11,7,7]
        else:
            upgrades = [12,8,8]
        #TODO : Simplyfy this dirty codes.
        if enhance == 100:
            scrolls = [[upgrades[i],0,0] for i in range(3)]
        elif enhance == 70:
            scrolls = [[0,upgrades[i],0] for i in range(3)]
        elif enhance == 30:
            scrolls = [[0,0,upgrades[i]] for i in range(3)]
        else:
            raise TypeError("enhance must be 100, 70, or 30.")
            
        package = {"head" : Head.copy(), "top" : Top.copy(), "bottom" : Bottom.copy()}
        keylist = ["head", "top", "bottom"]
        for idx, itemkey in zip([0,1,2], keylist):
            item = package[itemkey]
            item.set_potential(potential)
            item.set_additional_potential(additional_potential)
            item.add_main_option(bonus)
            item.add_main_option(it.EnhancerFactory.get_armor_starforce_enhancement(150, star))
            item.add_main_option(it.EnhancerFactory.get_armor_scroll_enhancement(150, elist = scrolls[idx]))
            
        return package
    
    @staticmethod
    def getWeapon(_type, star, elist, potential = it.CharacterModifier(), additional_potential = it.CharacterModifier(), bonusAttIndex = 0, bonusElse = it.CharacterModifier()):
        
        return WeaponFactory.getWeapon(_type, star = star, elist = elist, potential = potential, additional_potential = additional_potential, bonusAttIndex = bonusAttIndex, bonusElse = bonusElse)

    @staticmethod
    def getBlade(_type, star, elist, potential = it.CharacterModifier(), additional_potential = it.CharacterModifier(), bonusElse = it.CharacterModifier()):

        return WeaponFactory.getBlade(_type, star = star, elist = elist, potential = potential, additional_potential = additional_potential, bonusElse = bonusElse)

    @staticmethod
    def getSetOption(rank):
        li = [it.CharacterModifier(), 
                it.CharacterModifier(stat_main=20, stat_sub=20), 
                it.CharacterModifier(att=50),
                it.CharacterModifier(boss_pdamage=30)]
        
        retval = li[0]
        for i in range(rank):
            retval += li[i]
        
        return retval