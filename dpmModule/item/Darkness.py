from . import ItemKernel as it

Face = it.Item(stat_main = 10, stat_sub = 10, att = 10)#160 // 5
Eye = it.Item(stat_main = 15, stat_sub = 15, att = 3)#160 // 3
Belt = it.Item(stat_main = 50, stat_sub = 50, att = 6)#200 // 3
Pendant = it.Item(stat_main = 10, stat_sub = 10, att = 5)#160 // 5
Pocket = it.Item(stat_main = 20, stat_sub = 10, att = 10)#160
#Heart = it.Item(stat_main = 50, stat_sub = 50, att = 77, boss_pdamage = 30, armor_ignore = 30)
#Badge = it.Item(stat_main = 15, stat_sub = 15, att = 10)
#Ring = it.Item(stat_main = 5, stat_sub = 5, att = 4)
#Ear = it.Item(stat_main = 5, stat_sub = 5, att = 4)

# 블랙하트, 창세의 뱃지, 거대한 공포, 커맨드 포스 이어링 추가필요

class Factory():
    
    @staticmethod
    def getAccesoryDict(star, enhancer, 
                            potential = it.CharacterModifier(), 
                            additional_potential = it.CharacterModifier(), 
                            bonus = it.CharacterModifier(), 
                            hammer = True):
        #Always use 30% enhance scroll. if False, do not apply.
        if not hammer:
            upgrades = [5,3,3,5,0]
        else:
            upgrades = [7,2,2]

        black_face = Face.copy()
        black_eye = Eye.copy()
        black_belt = Belt.copy()
        black_pendant = Pendant.copy()
        black_pocket = Pocket.copy()
        
        item_list = [black_face, black_eye, black_belt, black_pendant, black_pocket]
        level_list = [160,160,200,160,160]
        enhance_list = [5,3,3,5,0]
        
        for idx in range(5):
            item = item_list[idx]
            level = level_list[idx]
            enhance = enhance_list[idx]
            
            item.add_main_option(bonus)
            if idx != 4:
                item.set_potential(potential)
                item.set_additional_potential(additional_potential)
            
            scroll_enhance = it.CharacterModifier()
            for i in range(enhance):
                scroll_enhance += enhancer
                
            item.add_main_option(scroll_enhance)
            item.add_main_option(it.EnhancerFactory.get_armor_starforce_enhancement(level, star))
        
        return {"eye" : black_eye ,
                "face" : black_face,
                "belt" : black_belt,
                "pendant" : black_pendant,
                "pocket" : black_pocket }

    @staticmethod
    def getSetOption(rank):
        li = [it.CharacterModifier(), 
                it.CharacterModifier(stat_main = 10, stat_sub = 10, att = 10, boss_pdamage = 10), 
                it.CharacterModifier(stat_main = 10, stat_sub = 10, att = 10, armor_ignore = 10),
                it.CharacterModifier(stat_main = 15, stat_sub = 15, att = 15, crit_damage = 5),
                it.CharacterModifier(stat_main = 15, stat_sub = 15, att = 15, boss_pdamage = 10)]
        
        retval = li[0]
        for i in range(rank):
            retval += li[i]
        
        return retval        