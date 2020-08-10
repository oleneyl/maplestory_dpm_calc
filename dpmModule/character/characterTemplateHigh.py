from .characterKernel import ItemedCharacter as ichar
from .characterKernel import LinkSkill
from .characterTemplate import AbstractTemplateGenerator, register_template_generator
from ..item import Arcane, Absolab, Empress, RootAbyss, BossAccesory, Default, Else, Meister, Darkness
from ..item.ItemKernel import CharacterModifier as MDF
from ..item import ItemKernel as it
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
def getU4000CharacterTemplate(_type):
    ''' CharacterTemplate : set items w/o weapon-type potentials.
    무기류 유닠1줄 + 10성 + 2추옵
    방어구/장신구 에픽6% + 10성 + 추옵 50급
    
    카루타 + 여제 + 보장
    '''
    #Temporal union object..
    link = LinkSkill.get_full_link()
    template = ichar(modifierlist = [link], level = 215)
    
    template.add_summary("에디셔널 잠재능력: 없음")

    weaponAPtnl = MDF()
    subAPtnl = MDF()
    emblemAPtnl = MDF()

    template.add_summary("방어구/장신구: 에픽9%, 추옵 60급, 스타포스 10성")    
    armorPtnl = MDF(pstat_main = 9)
    armorBonus = MDF(pstat_main = 6, pstat_sub = 6)
    armorStar = 10
    
    accPtnl = MDF(pstat_main = 9)
    accBonus = MDF(stat_main = 60)
    accStar = 10
    
    template.add_summary("무기: 스타포스 10성, 3추옵")
    weaponStar = 10
    bonusAttIndex = 3

    template.add_summary("장신구: 보장9셋")
    template.add_summary("방어구: 여제5셋, 카루타 4셋")
    BossAccesorySet = BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar)
    RootAbyssSet = RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    
    EmpressSet = Empress.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    
    template.add_summary("기타: 킹오루, 우르스 격파왕, 하트X, 펫공 X")

    template.set_items({
        "head": EmpressSet["head"],
        "glove": EmpressSet["glove"],
        "top": RootAbyssSet["top"],
        "bottom": RootAbyssSet["bottom"],
        "shoes": EmpressSet["shoes"],
        "cloak": EmpressSet["cloak"],
        "eye": BossAccesorySet["eye"],
        "face": BossAccesorySet["face"],
        "ear": BossAccesorySet["ear"],
        "belt": BossAccesorySet["belt"],
        "ring1": BossAccesorySet["ring1"],
        "ring2": BossAccesorySet["ring2"],
        "ring3": Default.getEventRing(potential = accPtnl),
        "ring4": Default.getEventRing(potential = accPtnl),
        "shoulder": EmpressSet["shoulder"],
        "pendant1": BossAccesorySet["pendant1"],
        "pendant2": BossAccesorySet["pendant2"],
        "pocket": BossAccesorySet["pocket"],
        "badge": BossAccesorySet["badge"],
        "weapon": RootAbyss.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ),
        "subweapon": Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=RootAbyss.Factory),
        "emblem": Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl),
        "medal": Else.get_medal(7),
        "heart": it.Item(),
        "title": Else.KingOfRootAbyss.copy(),
        "pet": it.Item(),
    })
    
    template.apply_modifiers([Empress.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(4), BossAccesory.Factory.getSetOption(9)])
    
    template.add_summary("아케인포스: 240")
    template.apply_modifiers([MDF(stat_main_fixed = 2400)])
    
    return template

def getU5000CharacterTemplate(_type):
    #Temporal union object..
    link = LinkSkill.get_full_link()
    template = ichar(modifierlist = [link], level = 230)

    weaponAPtnl = MDF(att = 3)
    subAPtnl = MDF()
    emblemAPtnl = MDF()

    template.add_summary("방어구/장신구: 에픽9%, 추옵 70급, 스타포스 10성, 에디 공10")   
    armorAPtnl = MDF(att = 10)    
    armorPtnl = MDF(pstat_main = 9)
    armorBonus = MDF(pstat_main = 5, pstat_sub = 5, stat_main = 20)
    armorStar = 10
    
    accAPtnl = MDF(att = 10)    
    accPtnl = MDF(pstat_main = 9)
    accBonus = MDF(stat_main = 70)
    accStar = 10
    
    template.add_summary("무기: 스타포스 12성, 2추옵")
    weaponStar = 12
    bonusAttIndex = 2
    template.add_summary("장신구: 보장9셋")
    template.add_summary("방어구: 앱솔5셋, 카루타 3셋")
    BossAccesorySet = BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, enhance = 30, additional_potential = accAPtnl)
    RootAbyssSet = RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, enhance = 30, additional_potential = armorAPtnl)
    
    AbsolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, enhance = 30, additional_potential = armorAPtnl)

    template.add_summary("기타: 킹오루, 우르스 격파왕, 하트 공30, 펫공 30")

    template.set_items({
        "head": AbsolabSet["head"],
        "glove": AbsolabSet["glove"],
        "top": RootAbyssSet["top"],
        "bottom": RootAbyssSet["bottom"],
        "shoes": AbsolabSet["shoes"],
        "cloak": AbsolabSet["cloak"],
        "eye": BossAccesorySet["eye"],
        "face": BossAccesorySet["face"],
        "ear": BossAccesorySet["ear"],
        "belt": BossAccesorySet["belt"],
        "ring1": BossAccesorySet["ring1"],
        "ring2": BossAccesorySet["ring2"],
        "ring3": Default.getEventRing(potential = accPtnl),
        "ring4": Default.getEventRing(potential = accPtnl),
        "shoulder": AbsolabSet["shoulder"],
        "pendant1": BossAccesorySet["pendant1"],
        "pendant2": BossAccesorySet["pendant2"],
        "pocket": BossAccesorySet["pocket"],
        "badge": BossAccesorySet["badge"],
        "weapon": Absolab.Factory.getWeapon(_type, elist = [0,0,0,9], bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ),
        "subweapon": Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=Absolab.Factory),
        "emblem": Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl),
        "medal": Else.get_medal(7),
        "heart": Else.get_heart(30),
        "title": Else.KingOfRootAbyss.copy(),
        "pet": Else.get_pet(30),
    })
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("아케인포스: 540")
    template.apply_modifiers([MDF(stat_main_fixed = 5400)])
    
    
    return template

def getU6000CharacterTemplate(_type):
    #Temporal union object..
    link = LinkSkill.get_full_link()
    template = ichar(modifierlist = [link], level = 240)
    
    template.add_summary("에디: 공10, 무기류 공6%")


    weaponAPtnl = MDF(patt = 6)
    subAPtnl = MDF(patt = 6)
    emblemAPtnl = MDF(patt = 6)

    template.add_summary("방어구/장신구: 유니크15%, 추옵 90급, 스타포스 17성")    
    template.add_summary("장갑: 크뎀1줄")
    armorAPtnl = MDF(att = 10)
    armorPtnl = MDF(pstat_main = 15)
    armorBonus = MDF(pstat_main = 5, pstat_sub = 5, stat_main = 40)
    armorStar = 17
    
    accAPtnl = MDF(att = 10)
    accPtnl = MDF(pstat_main = 15)
    accBonus = MDF(stat_main = 90)
    accStar = 17
    
    template.add_summary("무기: 스타포스 17성, 2추옵")
    weaponStar = 17
    bonusAttIndex = 2

    template.add_summary("장신구: 보장9셋")
    template.add_summary("방어구: 앱솔5셋, 카루타 3셋")
    BossAccesorySet = BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, enhance = 30, star = accStar, additional_potential = accAPtnl)
    RootAbyssSet = RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, enhance = 30, star = armorStar, additional_potential = armorAPtnl)
    
    AbsolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, enhance = 30, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl)
    AbsolabSet["glove"].set_potential(MDF(crit_damage = 8))

    template.add_summary("기타: 핑아, 우르스 격파왕, 하트 공50, 펫공 40")

    template.set_items({
        "head": AbsolabSet["head"],
        "glove": AbsolabSet["glove"],
        "top": RootAbyssSet["top"],
        "bottom": RootAbyssSet["bottom"],
        "shoes": AbsolabSet["shoes"],
        "cloak": AbsolabSet["cloak"],
        "eye": BossAccesorySet["eye"],
        "face": BossAccesorySet["face"],
        "ear": BossAccesorySet["ear"],
        "belt": BossAccesorySet["belt"],
        "ring1": BossAccesorySet["ring1"],
        "ring2": BossAccesorySet["ring2"],
        "ring3": Default.getEventRing(potential = accPtnl),
        "ring4": Default.getEventRing(potential = accPtnl),
        "shoulder": AbsolabSet["shoulder"],
        "pendant1": BossAccesorySet["pendant1"],
        "pendant2": BossAccesorySet["pendant2"],
        "pocket": BossAccesorySet["pocket"],
        "badge": BossAccesorySet["badge"],
        "weapon": Absolab.Factory.getWeapon(_type, elist = [0,0,0,9], bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ),
        "subweapon": Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=Absolab.Factory),
        "emblem": Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl),
        "medal": Else.get_medal(7),
        "heart": Else.get_heart(50),
        "title": Else.PingkbinAndMe.copy(),
        "pet": Else.get_pet(40),
    })
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("아케인포스: 780")
    template.apply_modifiers([MDF(stat_main_fixed = 7800)])
    
    
    return template

def getU7000CharacterTemplate(_type):
    #Temporal union object..
    link = LinkSkill.get_full_link()
    template = ichar(modifierlist = [link], level = 250)
    
    template.add_summary("에디: 2줄, 무기류 공21%")

    weaponAPtnl = MDF(patt = 21)
    subAPtnl = MDF(patt = 21)
    emblemAPtnl = MDF(patt = 21)

    template.add_summary("방어구/장신구: 유닉21%, 추옵 110급, 스타포스 18성")
    template.add_summary("장갑: 크뎀1줄")
    armorAPtnl = MDF(att = 11, pstat_main = 4)
    armorPtnl = MDF(pstat_main = 21)
    armorBonus = MDF(pstat_main = 5, pstat_sub = 5, stat_main = 60)
    armorStar = 18
    
    accAPtnl = MDF(att = 11, pstat_main = 4)
    accPtnl = MDF(pstat_main = 21)
    accBonus = MDF(stat_main = 110)
    accStar = 18
    
    template.add_summary("무기: 스타포스 17성, 1추옵")
    weaponStar = 17
    bonusAttIndex = 1

    template.add_summary("장신구: 보장7셋, 마이, 칠요")
    template.add_summary("방어구: 앱솔5셋, 카루타 2셋, 1아케인(무기)")
    BossAccesorySet = BossAccesory.Factory.getBetter11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, additional_potential = accAPtnl)
    RootAbyssSet = RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl)
    
    BossAccesorySurprise = BossAccesory.Factory.getBetter11SetDict(potential = accPtnl, 
                                                                bonus = accBonus, 
                                                                star = 0, 
                                                                additional_potential = accAPtnl)
    
    BossAccesorySurprise["pendant1"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(130, 12))
    BossAccesorySurprise["pendant2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    
    MeisterSet = Meister.Factory.getAccesoryDict(3, potential = accPtnl,  
                                                        bonus = accBonus,
                                                        additional_potential = accAPtnl,
                                                        star = 0)
    MeisterSet["ring3"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))

    AbsolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, additional_potential = armorAPtnl, 
                                                        bonus = armorBonus, star = armorStar)
    AbsolabSet["glove"].set_potential(MDF(crit_damage = 8))
    
    WeeklySet = Else.get_weekly_set()
    
    template.add_summary("기타: 핑아, 하트 공95, 펫공 80")

    template.set_items({
        "head": AbsolabSet["head"],
        "glove": AbsolabSet["glove"],
        "top": RootAbyssSet["top"],
        "bottom": RootAbyssSet["bottom"],
        "shoes": AbsolabSet["shoes"],
        "cloak": AbsolabSet["cloak"],
        "eye": BossAccesorySet["eye"],
        "face": BossAccesorySet["face"],
        "ear": BossAccesorySet["ear"],
        "belt": BossAccesorySet["belt"],
        "ring1": BossAccesorySet["ring1"],
        "ring2": BossAccesorySet["ring2"],
        "ring3": MeisterSet["ring3"],
        "ring4": Default.getEventRing(potential = accPtnl),
        "shoulder": AbsolabSet["shoulder"],
        "pendant1": BossAccesorySurprise["pendant1"],
        "pendant2": BossAccesorySurprise["pendant2"],
        "pocket": BossAccesorySet["pocket"],
        "badge": WeeklySet["badge"],
        "weapon": Arcane.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ),
        "subweapon": Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=Arcane.Factory),
        "emblem": Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl),
        "medal": WeeklySet["medal"],
        "heart": Else.get_heart(95, accPtnl, accAPtnl),
        "title": Else.PingkbinAndMe.copy(),
        "pet": Else.get_pet(80),
    })
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(2), BossAccesory.Factory.getSetOption(7)])

    template.add_summary("아케인포스: 960")
    template.apply_modifiers([MDF(stat_main_fixed = 9600)])
    
    
    return template    


def getU8000CharacterTemplate(_type):
    #Temporal union object..
    link = LinkSkill.get_full_link()
    template = ichar(modifierlist = [link], level = 255)
    
    template.add_summary("에디: 2.5줄, 무기류 공21%")

    weaponAPtnl = MDF(patt = 21)
    subAPtnl = MDF(patt = 21)
    emblemAPtnl = MDF(patt = 21)

    template.add_summary("방어구/장신구: 레전27%, 추옵 120급, 스타포스 22성")
    template.add_summary("장갑: 크뎀2줄")
    armorAPtnl = MDF(att = 10, pstat_main = 6)
    armorPtnl = MDF(pstat_main = 27)
    armorBonus = MDF(pstat_main = 6, pstat_sub = 6, stat_main = 60)
    armorStar = 22
    
    accAPtnl = MDF(att = 10, pstat_main = 6)
    accPtnl = MDF(pstat_main = 27)
    accBonus = MDF(stat_main = 120)
    accStar = 22
    
    template.add_summary("무기: 스타포스 22성, 1추옵")
    weaponStar = 22
    bonusAttIndex = 1

    template.add_summary("장신구: 보장5셋, 마이, 칠요")
    template.add_summary("방어구: 앱솔5셋, 카루타 2셋, 아케인셰이드")
    BossAccesorySet = BossAccesory.Factory.getBetter11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, additional_potential = accAPtnl)
    RootAbyssSet = RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl)
    
    ## 놀장 적용
    BossAccesorySurprise = BossAccesory.Factory.getBetter11SetDict(potential = accPtnl, 
                                                                bonus = accBonus, 
                                                                star = 0, 
                                                                additional_potential = accAPtnl)
    
    BossAccesorySurprise["pendant1"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(130, 12))
    BossAccesorySurprise["pendant2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    BossAccesorySurprise["ring1"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(110, 10))
    
    
    MeisterSet = Meister.Factory.getAccesoryDict(2, potential = accPtnl,  
                                                        bonus = accBonus,
                                                        additional_potential = accAPtnl,
                                                        star = 0)
    MeisterSet["ear"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    MeisterSet["ring2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    
    AbsolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl)
    AbsolabSet["glove"].set_potential(MDF(crit_damage = 16))

    WeeklySet = Else.get_weekly_set()

    template.add_summary("기타: 핑아, 하트 공120, 펫공 120")
    

    template.set_items({
        "head": AbsolabSet["head"],
        "glove": AbsolabSet["glove"],
        "top": RootAbyssSet["top"],
        "bottom": RootAbyssSet["bottom"],
        "shoes": AbsolabSet["shoes"],
        "cloak": AbsolabSet["cloak"],
        "eye": BossAccesorySet["eye"],
        "face": BossAccesorySet["face"],
        "ear": MeisterSet["ear"],
        "belt": BossAccesorySet["belt"],
        "ring1": BossAccesorySurprise["ring1"],
        "ring2": MeisterSet["ring2"],
        "ring3": Default.getEventRing(potential = accPtnl),
        "ring4": Default.getEventRing(potential = accPtnl),
        "shoulder": AbsolabSet["shoulder"],
        "pendant1": BossAccesorySurprise["pendant1"],
        "pendant2": BossAccesorySurprise["pendant2"],
        "pocket": BossAccesorySet["pocket"],
        "badge": WeeklySet["badge"],
        "weapon": Arcane.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ),
        "subweapon": Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=Arcane.Factory),
        "emblem": Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl),
        "medal": WeeklySet["medal"],
        "heart": Else.get_heart(120, accPtnl, accAPtnl),
        "title": Else.PingkbinAndMe.copy(),
        "pet": Else.get_pet(120),
    })
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), 
                                RootAbyss.Factory.getSetOption(2), 
                                BossAccesory.Factory.getSetOption(5)])

    template.add_summary("아케인포스: 1140")
    template.apply_modifiers([MDF(stat_main_fixed = 11400)])

    return template            
    
def getU8500CharacterTemplate(_type):
    #Temporal union object..
    link = LinkSkill.get_full_link()
    template = ichar(modifierlist = [link], level = 260)
    
    template.add_summary("에디: 레전 3줄, 무기류 공24%")

    weaponAPtnl = MDF(patt = 24)
    subAPtnl = MDF(patt = 24)
    emblemAPtnl = MDF(patt = 24)

    template.add_summary("방어구/장신구: 레전33%, 추옵 130급, 스타포스 22성")
    template.add_summary("장갑: 크뎀2.5줄")
    armorAPtnl = MDF(att = 12, pstat_main = 12)
    armorPtnl = MDF(pstat_main = 33)
    armorBonus = MDF(pstat_main = 6, pstat_sub = 6, stat_main = 70)
    armorStar = 22
    
    accAPtnl = MDF(att = 12, pstat_main = 12)
    accPtnl = MDF(pstat_main = 33)
    accBonus = MDF(stat_main = 130)
    accStar = 22
    
    template.add_summary("무기: 스타포스 22성, 1추옵")
    weaponStar = 22
    bonusAttIndex = 1

    template.add_summary("장신구: 칠흑셋, 칠요")
    template.add_summary("방어구 : 아케인6셋, 카루타 2셋")

    RootAbyssSet = RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl)

    ## 놀장 적용
    BossAccesorySurprise = BossAccesory.Factory.getBetter11SetDict(potential = accPtnl, 
                                                                bonus = accBonus, 
                                                                star = 0, 
                                                                additional_potential = accAPtnl)
    
    BossAccesorySurprise["pendant1"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(130, 12))
    BossAccesorySurprise["pendant2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    BossAccesorySurprise["ring1"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(110, 10))
    
    MeisterSet = Meister.Factory.getAccesoryDict(2, potential = accPtnl,  
                                                        bonus = accBonus,
                                                        additional_potential = accAPtnl,
                                                        star = 0)
    MeisterSet["ear"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    MeisterSet["ring2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    
    DarknessSet = Darkness.Factory.getAccesoryDict(star = accStar,
                                                    bonus = accBonus,
                                                    potential = accPtnl,
                                                    additional_potential = accAPtnl,
                                                    enhancer = it.CharacterModifier(att = 6)
                                                    )
    
    ArcaneSet = Arcane.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl)
    ArcaneSet["glove"].set_potential(MDF(crit_damage = 16, stat_main = 9))
    
    WeeklySet = Else.get_weekly_set()

    template.add_summary("기타: 핑아, 하트 공160, 펫공 120")
    
    template.set_items({
        "head": ArcaneSet["head"],
        "glove": ArcaneSet["glove"],
        "top": RootAbyssSet["top"],
        "bottom": RootAbyssSet["bottom"],
        "shoes": ArcaneSet["shoes"],
        "cloak": ArcaneSet["cloak"],
        "eye": DarknessSet["eye"],
        "face": DarknessSet["face"],
        "ear": MeisterSet["ear"],
        "belt": DarknessSet["belt"],
        "ring1": BossAccesorySurprise["ring1"],
        "ring2": MeisterSet["ring2"],
        "ring3": Default.getEventRing(potential = accPtnl),
        "ring4": Default.getEventRing(potential = accPtnl),
        "shoulder": ArcaneSet["shoulder"],
        "pendant1": BossAccesorySurprise["pendant1"],
        "pendant2": BossAccesorySurprise["pendant2"],
        "pocket": DarknessSet["pocket"],
        "badge": WeeklySet["badge"],
        "weapon": Arcane.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ),
        "subweapon": Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=Arcane.Factory),
        "emblem": Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl),
        "medal": WeeklySet["medal"],
        "heart": Else.get_heart(160, accPtnl, accAPtnl),
        "title": Else.PingkbinAndMe.copy(),
        "pet": Else.get_pet(120),
    })
    
    template.apply_modifiers([Arcane.Factory.getSetOption(6), 
                                RootAbyss.Factory.getSetOption(2),
                                BossAccesory.Factory.getSetOption(3),
                                Darkness.Factory.getSetOption(4)])

    template.add_summary("아케인포스: 1320")
    template.apply_modifiers([MDF(stat_main_fixed = 13200)])
    
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