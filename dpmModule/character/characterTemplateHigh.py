from .characterKernel import ItemedCharacter as ichar
from .characterTemplate import AbstractTemplateGenerator, register_template_generator
from ..item import Arcane, Absolab, Empress, RootAbyss, BossAccesory, Default, Else, Meister, Darkness
from ..item.ItemKernel import ExMDF
from ..item import ItemKernel as it
from .cdr import apply_cdr
# Define UnionCharacter : Character that is oftenly used for union.
'''
캐릭터 템플릿

- U4000
  에픽9%, 무기류 유니크 2줄, 유니온 4000, 레벨 220, 추옵 70급, 무기 1추, 카루타+여제 에디없음

- U5000
  에픽12%, 무기류 유니크 2줄, 유니온 5000, 레벨 225, 추옵 70급, 무기 1추, 카루타+앱솔, 에디 공10

- U6000
  에픽12%, 무기류 레전 5줄, 유니온 6000, 레벨 230, 추옵 80급, 무기 1추, 카루타+앱솔, 에디 공10

- U6500
  유닠15%, 무기류 레전 6줄, 유니온 6500, 레벨 235, 추옵 90급, 무기 1추, 카루타+앱솔, 에디 공20

- U7000
  레전21%, 무기류 레전 7줄, 유니온 7000, 레벨 240, 추옵 100급, 무기 1추, 카루타+앱솔+아케인, 에디 공20

- U7500
  레전24%, 무기류 레전 9줄, 유니온 7500, 레벨 245, 추옵 110급, 무기 1추, 카루타+앱솔+아케인, 에디 유닠2줄

- U8000
  레전27%, 무기류 레전 3줄, 유니온 8000, 레벨 250, 추옵 120급, 무기 1추, 카루타+아케인, 에디 레전2줄
  
- U8500(엔드스펙)
  레전33%, 무기류 레전3줄, 유니온 8500, 레벨 255, 추옵 130급, 무기 1추, 카루타+아케인, 에디 레전3줄
  
'''

'''
Pre - generated characters
'''
def getU4000CharacterTemplate(_type, cdr = 0):
    ''' CharacterTemplate : set items w/o weapon-type potentials.
    무기류 유닠1줄 + 10성 + 2추옵
    방어구/장신구 에픽6% + 10성 + 추옵 50급
    
    카루타 + 여제 + 보장
    '''
    #Temporal union object..
    template = ichar(level = 215)
    
    template.add_summary("에디셔널 잠재능력: 없음")

    weaponAPtnl = ExMDF()
    subAPtnl = ExMDF()
    emblemAPtnl = ExMDF()

    template.add_summary("방어구/장신구: 에픽9%, 추옵 60급, 스타포스 10성")    
    armorPtnl = ExMDF(pstat_main = 9)
    armorBonus = ExMDF(pstat_main = 6, pstat_sub = 6)
    armorStar = 10
    
    accPtnl = ExMDF(pstat_main = 9)
    accBonus = ExMDF(stat_main = 60)
    accStar = 10
    
    template.add_summary("무기: 스타포스 10성, 3추옵")
    weaponStar = 10
    bonusAttIndex = 3

    template.add_summary("장신구: 보장9셋")
    template.add_summary("방어구: 여제5셋, 카루타 4셋")
    bossAccesorySet = BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, enhance = 70)
    rootAbyssSet = RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, enhance = 70)
    
    empressSet = Empress.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, enhance = 70)
    
    template.add_summary("기타: 킹오루, 우르스 격파왕, 하트X, 펫공 X")

    template.set_items({
        "head": empressSet["head"],
        "glove": empressSet["glove"],
        "top": rootAbyssSet["top"],
        "bottom": rootAbyssSet["bottom"],
        "shoes": empressSet["shoes"],
        "cloak": empressSet["cloak"],
        "eye": bossAccesorySet["eye"],
        "face": bossAccesorySet["face"],
        "ear": bossAccesorySet["ear"],
        "belt": bossAccesorySet["belt"],
        "ring1": bossAccesorySet["ring1"],
        "ring2": bossAccesorySet["ring2"],
        "ring3": Default.getEventRing(potential = accPtnl),
        "ring4": Default.getEventRing(potential = accPtnl),
        "shoulder": empressSet["shoulder"],
        "pendant1": bossAccesorySet["pendant1"],
        "pendant2": bossAccesorySet["pendant2"],
        "pocket": bossAccesorySet["pocket"],
        "badge": bossAccesorySet["badge"],
        "weapon": RootAbyss.Factory.getWeapon(_type, elist = [0,0,0,9], bonusAttIndex = bonusAttIndex, star = weaponStar, potential = ExMDF(), additional_potential = weaponAPtnl ),
        "subweapon": Default.get_subweapon_covering_exception(_type, elist = [0,0,0,9], star=weaponStar, potential = ExMDF(), additional_potential = subAPtnl, factory_hook=RootAbyss.Factory),
        "emblem": Default.getEmblem(potential = ExMDF(), additional_potential = emblemAPtnl),
        "medal": Else.get_medal(7),
        "heart": Else.get_heart(8),
        "title": Else.KingOfRootAbyss.copy(),
        "pet": Else.get_pet(0),
    })
    
    template.apply_modifiers([Empress.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(4), BossAccesory.Factory.getSetOption(9)])
    
    template.add_summary("아케인포스: 240")
    template.apply_modifiers([ExMDF(stat_main_fixed = 2400)])
    
    return template

def getU5000CharacterTemplate(_type, cdr = 0):
    #Temporal union object..
    template = ichar(level = 230)

    weaponAPtnl = ExMDF(att = 3)
    subAPtnl = ExMDF()
    emblemAPtnl = ExMDF()

    template.add_summary("방어구/장신구: 에픽9%, 추옵 70급, 스타포스 10성, 에디 공10")   
    armorAPtnl = ExMDF(att = 10)    
    armorPtnl = ExMDF(pstat_main = 9)
    armorBonus = ExMDF(pstat_main = 5, pstat_sub = 5, stat_main = 20)
    armorStar = 10
    
    accAPtnl = ExMDF(att = 10)    
    accPtnl = ExMDF(pstat_main = 9)
    accBonus = ExMDF(stat_main = 70)
    accStar = 10
    
    template.add_summary("무기: 스타포스 12성, 2추옵")
    weaponStar = 12
    bonusAttIndex = 2
    template.add_summary("장신구: 보장9셋")
    template.add_summary("방어구: 앱솔5셋, 카루타 3셋")
    bossAccesorySet = BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, enhance = 30, additional_potential = accAPtnl)
    rootAbyssSet = RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, enhance = 30, additional_potential = armorAPtnl)
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, enhance = 30, additional_potential = armorAPtnl)

    template.add_summary("기타: 킹오루, 우르스 격파왕, 하트 공30, 펫공 30")

    template.set_items({
        "head": rootAbyssSet["head"],
        "glove": absolabSet["glove"],
        "top": rootAbyssSet["top"],
        "bottom": rootAbyssSet["bottom"],
        "shoes": absolabSet["shoes"],
        "cloak": absolabSet["cloak"],
        "eye": bossAccesorySet["eye"],
        "face": bossAccesorySet["face"],
        "ear": bossAccesorySet["ear"],
        "belt": bossAccesorySet["belt"],
        "ring1": bossAccesorySet["ring1"],
        "ring2": bossAccesorySet["ring2"],
        "ring3": Default.getEventRing(potential = accPtnl),
        "ring4": Default.getEventRing(potential = accPtnl),
        "shoulder": absolabSet["shoulder"],
        "pendant1": bossAccesorySet["pendant1"],
        "pendant2": bossAccesorySet["pendant2"],
        "pocket": bossAccesorySet["pocket"],
        "badge": bossAccesorySet["badge"],
        "weapon": Absolab.Factory.getWeapon(_type, elist = [0,0,0,9], bonusAttIndex = bonusAttIndex, star = weaponStar, potential = ExMDF(), additional_potential = weaponAPtnl ),
        "subweapon": Default.get_subweapon_covering_exception(_type, elist = [0,0,0,9], star=weaponStar, potential = ExMDF(), additional_potential = subAPtnl, factory_hook=Absolab.Factory),
        "emblem": Default.getEmblem(potential = ExMDF(), additional_potential = emblemAPtnl),
        "medal": Else.get_medal(7),
        "heart": Else.get_heart(30),
        "title": Else.KingOfRootAbyss.copy(),
        "pet": Else.get_pet(30),
    })
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("아케인포스: 540")
    template.apply_modifiers([ExMDF(stat_main_fixed = 5400)])
    
    
    return template

def getU6000CharacterTemplate(_type, cdr = 0):
    #Temporal union object..
    template = ichar(level = 240)
    
    template.add_summary("에디: 공10, 무기류 공6%")


    weaponAPtnl = ExMDF(patt = 6)
    subAPtnl = ExMDF(patt = 6)
    emblemAPtnl = ExMDF(patt = 6)

    template.add_summary("방어구/장신구: 유니크15%, 추옵 90급, 스타포스 17성")    
    template.add_summary("장갑: 크뎀1줄")
    armorAPtnl = ExMDF(att = 10)
    armorPtnl = ExMDF(pstat_main = 15)
    armorBonus = ExMDF(pstat_main = 5, pstat_sub = 5, stat_main = 40)
    armorStar = 17
    
    accAPtnl = ExMDF(att = 10)
    accPtnl = ExMDF(pstat_main = 15)
    accBonus = ExMDF(stat_main = 90)
    accStar = 17
    
    template.add_summary("무기: 스타포스 17성, 2추옵")
    weaponStar = 17
    bonusAttIndex = 2

    template.add_summary("장신구: 보장9셋")
    template.add_summary("방어구: 앱솔5셋, 카루타 3셋")
    bossAccesorySet = BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, enhance = 30, star = accStar, additional_potential = accAPtnl)
    rootAbyssSet = RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, enhance = 30, star = armorStar, additional_potential = armorAPtnl)
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, enhance = 30, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl)
    absolabSet["glove"].set_potential(ExMDF(crit_damage = 8))

    template.add_summary("기타: 핑아, 우르스 격파왕, 하트 공50, 펫공 40")

    template.set_items({
        "head": rootAbyssSet["head"],
        "glove": absolabSet["glove"],
        "top": rootAbyssSet["top"],
        "bottom": rootAbyssSet["bottom"],
        "shoes": absolabSet["shoes"],
        "cloak": absolabSet["cloak"],
        "eye": bossAccesorySet["eye"],
        "face": bossAccesorySet["face"],
        "ear": bossAccesorySet["ear"],
        "belt": bossAccesorySet["belt"],
        "ring1": bossAccesorySet["ring1"],
        "ring2": bossAccesorySet["ring2"],
        "ring3": Default.getEventRing(potential = accPtnl),
        "ring4": Default.getEventRing(potential = accPtnl),
        "shoulder": absolabSet["shoulder"],
        "pendant1": bossAccesorySet["pendant1"],
        "pendant2": bossAccesorySet["pendant2"],
        "pocket": bossAccesorySet["pocket"],
        "badge": bossAccesorySet["badge"],
        "weapon": Absolab.Factory.getWeapon(_type, elist = [0,0,0,9], bonusAttIndex = bonusAttIndex, star = weaponStar, potential = ExMDF(), additional_potential = weaponAPtnl ),
        "subweapon": Default.get_subweapon_covering_exception(_type, elist = [0,0,0,9], star=weaponStar, potential = ExMDF(), additional_potential = subAPtnl, factory_hook=Absolab.Factory),
        "emblem": Default.getEmblem(potential = ExMDF(), additional_potential = emblemAPtnl),
        "medal": Else.get_medal(7),
        "heart": Else.get_heart(50),
        "title": Else.PingkbinAndMe.copy(),
        "pet": Else.get_pet(40),
    })
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("아케인포스: 780")
    template.apply_modifiers([ExMDF(stat_main_fixed = 7800)])
    
    
    return template

def getU7000CharacterTemplate(_type, cdr = 0):
    #Temporal union object..
    template = ichar(level = 250)
    
    template.add_summary("에디: 2줄, 무기류 공21%")

    weaponAPtnl = ExMDF(patt = 21)
    subAPtnl = ExMDF(patt = 21)
    emblemAPtnl = ExMDF(patt = 21)

    template.add_summary("방어구/장신구: 유닉21%, 추옵 110급, 스타포스 18성")
    template.add_summary("장갑: 크뎀1줄")
    armorAPtnl = ExMDF(att = 11, pstat_main = 4)
    armorPtnl = ExMDF(pstat_main = 21)
    armorBonus = ExMDF(pstat_main = 5, pstat_sub = 5, stat_main = 60)
    armorStar = 18
    
    accAPtnl = ExMDF(att = 11, pstat_main = 4)
    accPtnl = ExMDF(pstat_main = 21)
    accBonus = ExMDF(stat_main = 110)
    accStar = 18
    
    template.add_summary("무기: 스타포스 17성, 1추옵")
    weaponStar = 17
    bonusAttIndex = 1

    template.add_summary("장신구: 보장7셋, 마이, 칠요")
    template.add_summary("방어구: 앱솔5셋, 카루타 2셋, 1아케인(무기)")
    bossAccesorySet = BossAccesory.Factory.getBetter11SetDict(potential = accPtnl, bonus = accBonus, enhance = 30, star = accStar, additional_potential = accAPtnl)
    rootAbyssSet = RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, enhance = 30, star = armorStar, additional_potential = armorAPtnl)
    
    bossAccesorySurprise = BossAccesory.Factory.getBetter11SetDict(potential = accPtnl, 
                                                                bonus = accBonus,
                                                                enhance = 30,
                                                                star = 0, 
                                                                additional_potential = accAPtnl)
    
    bossAccesorySurprise["pendant1"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(130, 12))
    bossAccesorySurprise["pendant2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    
    meisterSet = Meister.Factory.getAccesoryDict(3, potential = accPtnl,  
                                                        bonus = accBonus,
                                                        additional_potential = accAPtnl,
                                                        star = 0)
    meisterSet["ring3"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))

    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, additional_potential = armorAPtnl, 
                                                        bonus = armorBonus, star = armorStar, enhance = 30)
    absolabSet["glove"].set_potential(ExMDF(crit_damage = 8))
    
    weeklySet = Else.get_weekly_set()
    
    template.add_summary("기타: 핑아, 하트 공95, 펫공 80")

    template.set_items({
        "head": absolabSet["head"],
        "glove": absolabSet["glove"],
        "top": rootAbyssSet["top"],
        "bottom": rootAbyssSet["bottom"],
        "shoes": absolabSet["shoes"],
        "cloak": absolabSet["cloak"],
        "eye": bossAccesorySet["eye"],
        "face": bossAccesorySet["face"],
        "ear": bossAccesorySet["ear"],
        "belt": bossAccesorySet["belt"],
        "ring1": bossAccesorySet["ring1"],
        "ring2": bossAccesorySet["ring2"],
        "ring3": meisterSet["ring3"],
        "ring4": Default.getEventRing(potential = accPtnl),
        "shoulder": absolabSet["shoulder"],
        "pendant1": bossAccesorySurprise["pendant1"],
        "pendant2": bossAccesorySurprise["pendant2"],
        "pocket": bossAccesorySet["pocket"],
        "badge": weeklySet["badge"],
        "weapon": Arcane.Factory.getWeapon(_type, elist = [0,0,0,9], bonusAttIndex = bonusAttIndex, star = weaponStar, potential = ExMDF(), additional_potential = weaponAPtnl ),
        "subweapon": Default.get_subweapon_covering_exception(_type, elist = [0,0,0,9], star=weaponStar, potential = ExMDF(), additional_potential = subAPtnl, factory_hook=Arcane.Factory),
        "emblem": Default.getEmblem(potential = ExMDF(), additional_potential = emblemAPtnl),
        "medal": weeklySet["medal"],
        "heart": Else.get_heart(95, accPtnl, accAPtnl),
        "title": Else.PingkbinAndMe.copy(),
        "pet": Else.get_pet(80),
    })
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(2), BossAccesory.Factory.getSetOption(7)])

    template.add_summary("아케인포스: 960")
    template.apply_modifiers([ExMDF(stat_main_fixed = 9600)])
    
    
    return template    


def getU8000CharacterTemplate(_type, cdr = 0):
    #Temporal union object..
    template = ichar(level = 255)
    
    template.add_summary("에디: 2.5줄, 무기류 공21%")

    weaponAPtnl = ExMDF(patt = 21)
    subAPtnl = ExMDF(patt = 21)
    emblemAPtnl = ExMDF(patt = 21)

    template.add_summary("방어구/장신구: 레전27%, 추옵 120급, 스타포스 22성")
    template.add_summary("장갑: 크뎀2줄")
    armorAPtnl = ExMDF(att = 10, pstat_main = 6)
    armorPtnl = ExMDF(pstat_main = 27)
    armorBonus = ExMDF(pstat_main = 6, pstat_sub = 6, stat_main = 60)
    armorStar = 22
    
    accAPtnl = ExMDF(att = 10, pstat_main = 6)
    accPtnl = ExMDF(pstat_main = 27)
    accBonus = ExMDF(stat_main = 120)
    accStar = 22
    
    template.add_summary("무기: 스타포스 22성, 1추옵")
    weaponStar = 22
    bonusAttIndex = 1

    template.add_summary("장신구: 보장5셋, 마이, 칠요")
    template.add_summary("방어구: 앱솔5셋, 카루타 2셋, 아케인셰이드")
    bossAccesorySet = BossAccesory.Factory.getBetter11SetDict(potential = accPtnl, bonus = accBonus, enhance = 30, star = accStar, additional_potential = accAPtnl)
    rootAbyssSet = RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, enhance = 30, star = armorStar, additional_potential = armorAPtnl)
    
    ## 놀장 적용
    bossAccesorySurprise = BossAccesory.Factory.getBetter11SetDict(potential = accPtnl, 
                                                                bonus = accBonus,
                                                                enhance = 30,
                                                                star = 0, 
                                                                additional_potential = accAPtnl)
    
    bossAccesorySurprise["pendant1"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(130, 12))
    bossAccesorySurprise["pendant2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    bossAccesorySurprise["ring1"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(110, 10))
    
    
    meisterSet = Meister.Factory.getAccesoryDict(2, potential = accPtnl,  
                                                        bonus = accBonus,
                                                        additional_potential = accAPtnl,
                                                        star = 0)
    meisterSet["ear"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    meisterSet["ring2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, enhance = 30, star = armorStar, additional_potential = armorAPtnl)
    absolabSet["glove"].set_potential(ExMDF(crit_damage = 16))

    apply_cdr(absolabSet["head"], armorPtnl, cdr)

    weeklySet = Else.get_weekly_set()

    template.add_summary("기타: 핑아, 하트 공120, 펫공 120")
    

    template.set_items({
        "head": absolabSet["head"],
        "glove": absolabSet["glove"],
        "top": rootAbyssSet["top"],
        "bottom": rootAbyssSet["bottom"],
        "shoes": absolabSet["shoes"],
        "cloak": absolabSet["cloak"],
        "eye": bossAccesorySet["eye"],
        "face": bossAccesorySet["face"],
        "ear": meisterSet["ear"],
        "belt": bossAccesorySet["belt"],
        "ring1": bossAccesorySurprise["ring1"],
        "ring2": meisterSet["ring2"],
        "ring3": Default.getEventRing(potential = accPtnl),
        "ring4": Default.getEventRing(potential = accPtnl),
        "shoulder": absolabSet["shoulder"],
        "pendant1": bossAccesorySurprise["pendant1"],
        "pendant2": bossAccesorySurprise["pendant2"],
        "pocket": bossAccesorySet["pocket"],
        "badge": weeklySet["badge"],
        "weapon": Arcane.Factory.getWeapon(_type, elist = [0,0,0,9], bonusAttIndex = bonusAttIndex, star = weaponStar, potential = ExMDF(), additional_potential = weaponAPtnl ),
        "subweapon": Default.get_subweapon_covering_exception(_type, elist = [0,0,0,9], star=weaponStar, potential = ExMDF(), additional_potential = subAPtnl, factory_hook=Arcane.Factory),
        "emblem": Default.getEmblem(potential = ExMDF(), additional_potential = emblemAPtnl),
        "medal": weeklySet["medal"],
        "heart": Else.get_heart(120, accPtnl, accAPtnl),
        "title": Else.PingkbinAndMe.copy(),
        "pet": Else.get_pet(120),
    })
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), 
                                RootAbyss.Factory.getSetOption(2), 
                                BossAccesory.Factory.getSetOption(5)])

    template.add_summary("아케인포스: 1140")
    template.apply_modifiers([ExMDF(stat_main_fixed = 11400)])

    return template            
    
def getU8500CharacterTemplate(_type, cdr = 0):
    #Temporal union object..
    template = ichar(level = 260)
    
    template.add_summary("에디: 레전 3줄, 무기류 공24%")

    weaponAPtnl = ExMDF(patt = 24)
    subAPtnl = ExMDF(patt = 24)
    emblemAPtnl = ExMDF(patt = 24)

    template.add_summary("방어구/장신구: 레전33%, 추옵 130급, 스타포스 22성")
    template.add_summary("장갑: 크뎀2.5줄")
    armorAPtnl = ExMDF(att = 12, pstat_main = 12)
    armorPtnl = ExMDF(pstat_main = 33)
    armorBonus = ExMDF(pstat_main = 6, pstat_sub = 6, stat_main = 70)
    armorStar = 22
    
    accAPtnl = ExMDF(att = 12, pstat_main = 12)
    accPtnl = ExMDF(pstat_main = 33)
    accBonus = ExMDF(stat_main = 130)
    accStar = 22
    
    template.add_summary("무기: 스타포스 22성, 1추옵")
    weaponStar = 22
    bonusAttIndex = 1

    template.add_summary("장신구: 칠흑셋, 칠요")
    template.add_summary("방어구 : 아케인6셋, 카루타 2셋")

    rootAbyssSet = RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, enhance = 30, star = armorStar, additional_potential = armorAPtnl)

    ## 놀장 적용
    bossAccesorySurprise = BossAccesory.Factory.getBetter11SetDict(potential = accPtnl, 
                                                                bonus = accBonus,
                                                                enhance = 30,
                                                                star = 0, 
                                                                additional_potential = accAPtnl)
    
    bossAccesorySurprise["pendant1"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(130, 12))
    bossAccesorySurprise["pendant2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    bossAccesorySurprise["ring1"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(110, 10))
    
    meisterSet = Meister.Factory.getAccesoryDict(2, potential = accPtnl,  
                                                        bonus = accBonus,
                                                        additional_potential = accAPtnl,
                                                        star = 0)
    meisterSet["ear"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    meisterSet["ring2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    
    darknessSet = Darkness.Factory.getAccesoryDict(star = accStar,
                                                    bonus = accBonus,
                                                    potential = accPtnl,
                                                    additional_potential = accAPtnl,
                                                    enhancer = it.ExMDF(att = 6)
                                                    )
    
    arcaneSet = Arcane.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, enhance = 30, star = armorStar, additional_potential = armorAPtnl)
    arcaneSet["glove"].set_potential(ExMDF(crit_damage = 16, stat_main = 9))

    apply_cdr(arcaneSet["head"], armorPtnl, cdr)
    
    weeklySet = Else.get_weekly_set()

    template.add_summary("기타: 핑아, 하트 공160, 펫공 120")
    
    template.set_items({
        "head": arcaneSet["head"],
        "glove": arcaneSet["glove"],
        "top": rootAbyssSet["top"],
        "bottom": rootAbyssSet["bottom"],
        "shoes": arcaneSet["shoes"],
        "cloak": arcaneSet["cloak"],
        "eye": darknessSet["eye"],
        "face": darknessSet["face"],
        "ear": meisterSet["ear"],
        "belt": darknessSet["belt"],
        "ring1": bossAccesorySurprise["ring1"],
        "ring2": meisterSet["ring2"],
        "ring3": Default.getEventRing(potential = accPtnl),
        "ring4": Default.getEventRing(potential = accPtnl),
        "shoulder": arcaneSet["shoulder"],
        "pendant1": bossAccesorySurprise["pendant1"],
        "pendant2": bossAccesorySurprise["pendant2"],
        "pocket": darknessSet["pocket"],
        "badge": weeklySet["badge"],
        "weapon": Arcane.Factory.getWeapon(_type, elist = [0,0,0,9], bonusAttIndex = bonusAttIndex, star = weaponStar, potential = ExMDF(), additional_potential = weaponAPtnl ),
        "subweapon": Default.get_subweapon_covering_exception(_type, elist = [0,0,0,9], star=weaponStar, potential = ExMDF(), additional_potential = subAPtnl, factory_hook=Arcane.Factory),
        "emblem": Default.getEmblem(potential = ExMDF(), additional_potential = emblemAPtnl),
        "medal": weeklySet["medal"],
        "heart": Else.get_heart(160, accPtnl, accAPtnl),
        "title": Else.PingkbinAndMe.copy(),
        "pet": Else.get_pet(120),
    })
    
    template.apply_modifiers([Arcane.Factory.getSetOption(6), 
                                RootAbyss.Factory.getSetOption(2),
                                BossAccesory.Factory.getSetOption(3),
                                Darkness.Factory.getSetOption(4)])

    template.add_summary("아케인포스: 1320")
    template.apply_modifiers([ExMDF(stat_main_fixed = 13200)])

    template.add_summary("어센틱포스: 10")
    template.apply_modifiers([ExMDF(stat_main_fixed = 500)])
    
    return template

class TemplateGenerator(AbstractTemplateGenerator):
    TEMPLATE_NAME='high_standard'
    def __init__(self):
        super(TemplateGenerator, self).__init__({
            4000 : (2,6),
            5000 : (3,6),
            6000 : (4,9),
            7000 : (4,9),
            8000 : (4,9),
            8500 : (4,9)
        })

    def get_template(self, ulevel):
        if ulevel == 4000:
            return getU4000CharacterTemplate
        elif ulevel == 5000:
            return getU5000CharacterTemplate
        elif ulevel == 6000:
            return getU6000CharacterTemplate
        elif ulevel == 7000:
            return getU7000CharacterTemplate
        elif ulevel == 8000:
            return getU8000CharacterTemplate
        elif ulevel == 8500:
            return getU8500CharacterTemplate
        else:
            raise KeyError(f'given ulevel {ulevel} not exist in {self.TEMPLATE_NAME}')