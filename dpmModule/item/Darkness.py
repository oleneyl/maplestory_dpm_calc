from . import ItemKernel as it
ExMDF = it.ExMDF

Face = it.Item(name="루즈 컨트롤 머신 마크", level=160, main_option=ExMDF(stat_main=10, stat_sub=10, att=10))  #160 // 5
Eye = it.Item(name="마력이 깃든 안대", level=160, main_option=ExMDF(stat_main=15, stat_sub=15, att=3))  #160 // 3
Belt = it.Item(name="몽환의 벨트", level=200, main_option=ExMDF(stat_main=50, stat_sub=50, att=6))  #200 // 3
Pendant = it.Item(name="고통의 근원", level=160, main_option=ExMDF(stat_main=10, stat_sub=10, att=3))  #160 // 5
Ring = it.Item(name="거대한 공포", level=200, main_option=ExMDF(stat_main=5, stat_sub=5, att=4))  #200 // 2
Ear = it.Item(name="커맨드 포스 이어링", level=200, main_option=ExMDF(stat_main=7, stat_sub=7, att=5))  #200 // 6
Pocket = it.Item(name="저주받은 마도서", level=160, main_option=ExMDF(stat_main=20, stat_sub=10, att=10))  #160
Badge = it.Item(name="창세의 뱃지", level=200, main_option=ExMDF(stat_main=15, stat_sub=15, att=10))
Heart = it.Item(name="블랙 하트", level=120, main_option=ExMDF(stat_main=10, stat_sub=10, att=77), potential=ExMDF(boss_pdamage=30, armor_ignore=30))  # 잠재 고정, 15성 강화해줘야 함


class Factory():
    
    @staticmethod
    def getAccesoryDict(star, enhancer, 
                            potential = it.ExMDF(), 
                            additional_potential = it.ExMDF(), 
                            bonus = it.ExMDF(), 
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
        black_ring = Ring.copy()
        black_ear = Ear.copy()
        black_pocket = Pocket.copy()
        black_badge = Badge.copy()
        black_heart = Heart.copy()
        
        item_list = [black_face, black_eye, black_belt, black_pendant, black_ring, black_ear, black_pocket, black_badge, black_heart]
        level_list = [160, 160, 200, 160, 200, 200, 160, 200, 120]
        enhance_list = [5, 3, 3, 5, 2, 6, 0, 0, 0]
        
        # 루컨마, 마깃안, 몽벨, 고근, 거공, 커포
        for idx in range(6):
            item = item_list[idx]
            level = level_list[idx]
            enhance = enhance_list[idx]
            
            item.add_main_option(bonus)

            item.set_potential(potential)
            item.set_additional_potential(additional_potential)
            
            scroll_enhance = it.ExMDF()
            for i in range(enhance):
                scroll_enhance += enhancer
                
            item.add_main_option(scroll_enhance)
            item.add_main_option(it.EnhancerFactory.get_armor_starforce_enhancement(level, star))
        
        # 마도서
        item = item_list[6]
        level = level_list[6]
        enhance = enhance_list[6]
            
        item.add_main_option(bonus)

        # 창뱃
        item = item_list[7]
        level = level_list[7]
        enhance = enhance_list[7]

        # 블랙하트

        item = item_list[8]
        level = level_list[8]
        enhance = enhance_list[8]
            
        item.add_main_option(it.EnhancerFactory.get_armor_starforce_enhancement(level, 15))
        
        return {"eye" : black_eye ,
                "face" : black_face,
                "belt" : black_belt,
                "pendant1" : black_pendant,
                "ring2" : black_ring,  # 고피아 vs 고근
                "ear" : black_ear,
                "pocket" : black_pocket,
                "badge" : black_badge,
                "heart" : black_heart}

    @staticmethod
    def getSetOption(rank):
        li = [it.ExMDF(), 
                it.ExMDF(stat_main=10, stat_sub=10, att=10, boss_pdamage = 10), 
                it.ExMDF(stat_main=10, stat_sub=10, att=10, armor_ignore = 10),
                it.ExMDF(stat_main=15, stat_sub=15, att=15, crit_damage = 5),
                it.ExMDF(stat_main=15, stat_sub=15, att=15, boss_pdamage = 10),
                it.ExMDF(stat_main=15, stat_sub=15, att=15),
                it.ExMDF(stat_main=15, stat_sub=15, att=15, crit_damage = 5)
            ]
        
        retval = li[0]
        for i in range(rank):
            retval += li[i]
        
        return retval
