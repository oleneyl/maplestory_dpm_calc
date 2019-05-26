from . import ItemKernel as it

Ring = it.Item(stat_main = 5, stat_sub = 5, att = 1)
Ear = it.Item(stat_main = 5, stat_sub = 5, att = 4)
Soulder = it.Item(stat_main = 13, stat_sub = 13, att = 9)


class Factory():
    
    @staticmethod
    def getAccesoryDict(nth_ring, star = 0, enhance = True, potential = it.CharacterModifier(), additional_potential = it.CharacterModifier(), bonus = it.CharacterModifier(), hammer = True):
        #Always use 30% enhance scroll. if False, do not apply.
        if not hammer:
            upgrades = [6,1,1]
        else:
            upgrades = [7,2,2]
            
        item_level = 140
        
        miester_ring = Ring.copy()
        miester_ear = Ear.copy()
        miester_shoulder = Soulder.copy()
        
        for item, idx in zip([miester_ring, miester_ear, miester_shoulder], [0,1,2]):
            if idx == 1:
                item.add_main_option(bonus)
            item.set_potential(potential)
            item.set_additional_potential(additional_potential)
            item.add_main_option(it.EnhancerFactory.get_armor_starforce_enhancement(140, star))
            if enhance:
                item.add_main_option(it.EnhancerFactory.get_armor_scroll_enhancement(140, [0,0,upgrades[idx]]))
        
        return {"ring"+str(nth_ring) : miester_ring, "ear" : miester_ear, "shoulder" : miester_shoulder }