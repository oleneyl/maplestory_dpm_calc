from . import ItemKernel as it

Ring = it.Item(name="마이스터링", stat_main = 5, stat_sub = 5, att = 1, level = 140)
Ear = it.Item(name="마이스터 이어링", stat_main = 5, stat_sub = 5, att = 4, level = 140)
Soulder = it.Item(name="마이스터 숄더", stat_main = 13, stat_sub = 13, att = 9, level = 140)


class Factory():
    
    @staticmethod
    def getAccesoryDict(nth_ring, star, enhance = True, potential = it.ExMDF(), additional_potential = it.ExMDF(), bonus = it.ExMDF(), hammer = True):
        #Always use 30% enhance scroll. if False, do not apply.
        if not hammer:
            upgrades = [6,1,1]
        else:
            upgrades = [7,2,2]
        
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