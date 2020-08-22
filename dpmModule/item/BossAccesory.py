from . import ItemKernel as it

#No upgrade

#자쿰 얼장(응축된 힘의 결정석)...(5)
Face110 = it.Item(name="응축된 힘의 결정석", stat_main = 5, stat_sub = 5, att = 5, level = 110)
#자쿰 눈장....(3)
Eye100 = it.Item(name="아쿠아틱 레터 눈장식", stat_main = 6, stat_sub = 6, att = 1, level = 100)
#자쿰 벨트....(3)
Belt150 =  it.Item(name="분노한 자쿰의 벨트", stat_main = 18, stat_sub = 18, att = 1, level = 150)

#매그너스 숄더..(1)
Shoulder120 =  it.Item(name="로얄 블랙메탈 숄더", stat_main = 10, stat_sub = 10, att = 6, level = 120)
#매그너스 뱃지..(0)
Badge130 =  it.Item(name="크리스탈 웬투스 뱃지", stat_main = 10, stat_sub = 10, att = 5, level = 130)

#힐라 -> 미사용, 무시

#파풀 눈장..(5)
Eye145 =  it.Item(name="파풀라투스 마크", stat_main = 8, stat_sub = 8, att = 1, level = 140) # 145제는 140제와 같은 강화 테이블 사용

#반레온보장..(2)
Ring120 =  it.Item(name="고귀한 이피아의 반지", stat_main = 5, stat_sub = 5, att = 2, level = 120)

#혼테일 귀고리...(6)
Ear130 =  it.Item(name="데아 시두스 이어림", stat_main = 5, stat_sub = 5, att = 2, level = 130)
#혼테일 링...(2)
Ring110 =  it.Item(name="실버블라썸 링", stat_main = 5, stat_sub = 5, att = 2, level = 110)
#혼테일 목걸이..(0) -> 알발린상태로 계산 필요

#아카이럼 매커...(2)
Pendant120 =  it.Item(name="매커네이터 펜던트", stat_main = 10, stat_sub = 10, att = 1, level = 120)

#아카이럼 도미...(6 or 0) 파편작 가정
Pendant140 =  it.Item(name="도미네이터 펜던트", stat_main = 5, stat_sub = 5, att = 5, level = 140)
Pendant140Fragment = it.Item(name="도미네이터 펜던트", stat_main = 23, stat_sub = 23, att = 23, level = 140)

#핑크빈 포켓 ... 0
Pocket140 = it.Item(name="핑크빛 성배", stat_main = 5, stat_sub = 5, att = 5, level = 140)
#핑크빈 벨트 ... 3
Belt140 =  it.Item(name="골든 클로버 벨트", stat_main = 15, stat_sub = 15, att = 1, level = 140)
#핑크빈 얼장 ... 5
Eye135 = it.Item(name="블랙빈 마크", stat_main = 7, stat_sub = 7, att = 1, level = 130) # 135제는 130제와 같은 강화 테이블 사용



class Factory():
    @staticmethod
    def get11SetDict(star, enhance, potential = it.CharacterModifier(), additional_potential = it.CharacterModifier(), bonus = it.CharacterModifier(), hammer = True):
        package = [Eye100.copy(), Face110.copy(), Ear130.copy(), Ring110.copy(), Ring120.copy(), \
                    Pendant120.copy(), Pendant140.copy(), Belt140.copy(), Pocket140.copy(), \
                    Badge130.copy(), Shoulder120.copy()]

        package = {"eye" : Eye100.copy(), "face" : Face110.copy(), "ear" : Ear130.copy(), "ring1" : Ring110.copy(), \
                    "ring2" : Ring120.copy(), "pendant1" : Pendant120.copy(), "pendant2" : Pendant140.copy(), \
                    "belt" : Belt140.copy(), "pocket" : Pocket140.copy(), \
                    "badge" : Badge130.copy(), "shoulder" : Shoulder120.copy()}
        keylist = ["eye", "face", "ear", "ring1", "ring2", "pendant1", "pendant2", "belt", "pocket", "badge", "shoulder"]

        upgrades = [3, 5, 6, 2, 2, 2, 6, 3, 0, 0, 2]
        if hammer:            
            upgrades = [i+1 for i in upgrades]
            
        #TODO : Simplyfy this dirty codes.
        if enhance == 100:
            scrolls = [[upgrades[i],0,0] for i in range(11)]
        elif enhance == 70:
            scrolls = [[0,upgrades[i],0] for i in range(11)]
        elif enhance == 30:
            scrolls = [[0,0,upgrades[i]] for i in range(11)]
        else:
            raise TypeError("enhance must be 100, 70, or 30.")                    
                    
        for idx, itemkey in zip([i for i in range(11)], keylist):
            item = package[itemkey]
            item = package[itemkey]
            if itemkey not in ["ring1", "ring2", "shoulder", "badge"]:
                item.add_main_option(bonus)
            if itemkey not in ["pocket", "badge"]:
                item.set_potential(potential)
                item.set_additional_potential(additional_potential)
                item.add_main_option(it.EnhancerFactory.get_armor_starforce_enhancement(item.level, star))
                item.add_main_option(it.EnhancerFactory.get_armor_scroll_enhancement(item.level, elist = scrolls[idx]))
            
        return package
    
    @staticmethod    
    def getBetter11SetDict(star, enhance, potential = it.CharacterModifier(), additional_potential = it.CharacterModifier(), bonus = it.CharacterModifier(), hammer = True):
        package = {"eye" : Eye145.copy(), "face" : Face110.copy(), "ear" : Ear130.copy(), "ring1" : Ring110.copy(), \
                    "ring2" : Ring120.copy(), "pendant1" : Pendant120.copy(), "pendant2" : Pendant140Fragment.copy(), \
                    "belt" : Belt140.copy(), "pocket" : Pocket140.copy(), \
                    "badge" : Badge130.copy(), "shoulder" : Shoulder120.copy()}
        keylist = ["eye", "face", "ear", "ring1", "ring2", "pendant1", "pendant2", "belt", "pocket", "badge", "shoulder"]

        upgrades = [5, 5, 6, 2, 2, 2, 0, 3, 0, 0, 2]
        if hammer:            
            upgrades = [i+1 for i in upgrades]
            
        #TODO : Simplyfy this dirty codes.
        if enhance == 100:
            scrolls = [[upgrades[i],0,0] for i in range(11)]
        elif enhance == 70:
            scrolls = [[0,upgrades[i],0] for i in range(11)]
        elif enhance == 30:
            scrolls = [[0,0,upgrades[i]] for i in range(11)]
        else:
            raise TypeError("enhance must be 100, 70, or 30.")                    
                    
        for idx, itemkey in zip([i for i in range(11)], keylist):
            item = package[itemkey]
            if itemkey not in ["ring1", "ring2", "shoulder", "badge"]:
                item.add_main_option(bonus)
            if itemkey not in ["pocket", "badge"]:
                item.set_potential(potential)
                item.set_additional_potential(additional_potential)
                item.add_main_option(it.EnhancerFactory.get_armor_starforce_enhancement(item.level, star))
                item.add_main_option(it.EnhancerFactory.get_armor_scroll_enhancement(item.level, elist = scrolls[idx]))
            
        return package
        
    @staticmethod
    def getSetOption(rank):
        li = [it.CharacterModifier(), 
                it.CharacterModifier(), 
                it.CharacterModifier(stat_main = 10, stat_sub = 10, att = 5), 
                it.CharacterModifier(), 
                it.CharacterModifier(stat_main = 10, stat_sub = 10, att = 5), 
                it.CharacterModifier(), 
                it.CharacterModifier(att = 10, stat_main = 10, stat_sub = 10, armor_ignore = 10), 
                it.CharacterModifier(), 
                it.CharacterModifier(att = 10, stat_main = 15, stat_sub = 15, boss_pdamage = 10)]
        
        retval = li[0]
        for i in range(rank):
            retval += li[i]
        
        return retval