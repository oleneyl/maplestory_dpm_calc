from .characterKernel import ItemedCharacter as ichar
from .characterKernel import LinkSkill
from .characterTemplate import AbstractTemplateGenerator, register_template_generator
from ..item import Arcane, Absolab, Empress, RootAbyss, BossAccesory, Default, Else, Meister, Darkness
from ..item.ItemKernel import CharacterModifier as MDF
from ..item import ItemKernel as it
# Define UnionCharacter : Character that is oftenly used for union.
'''
캐릭터 템플릿

- U2000
  에픽6%, 무기류 유니크 1줄, 유니온 2000, 레벨 210, 추옵 50급, 무기 2추, 카루타+여제, 에디없음

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

def getUnionCharacter(_type, armor_pstat_ptnl = 6, acc_pstat_ptnl = 9, weaponStar = 12):
    ''' Explanation TODO..
    '''
    weaponPtnl = MDF(pdamage = 30, patt = 6)
    weaponAPtnl = MDF()
    
    subPtnl = MDF(armor_ignore = 30, patt = 6)
    subAPtnl = MDF()
    emblemPtnl = MDF(patt = 6, armor_ignore = 30)
    emblemAPtnl = MDF()
    
    armorPtnl = MDF(pstat_main = armor_pstat_ptnl)  #6%
    armorBonus = MDF(pstat_main = 6, pstat_sub = 6)
    armorStar = 10
    
    accPtnl = MDF(pstat_main = acc_pstat_ptnl)  #9%
    accBonus = MDF(stat_main = 50)
    accStar = 10
    
    bonusAttIndex = 2

    #Temporal union object..
    unionModifier = MDF(att = 5, pdamage = 21, armor_ignore = 21, stat_main = 5)
    link = LinkSkill.get_full_link()
    
    template = ichar(modifierlist = [unionModifier, link])

    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar))
    
    empressSet = Empress.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    template.add_item_with_id("glove", empressSet["glove"])
    template.add_item_with_id("cloak", empressSet["cloak"])
    template.add_item_with_id("shoes", empressSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.getSubweapon(potential = subPtnl))
    template.add_item_with_id("emblem", Default.getEmblem(potential = emblemPtnl))
    
    template.add_item_with_id("weapon", RootAbyss.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = weaponPtnl, additional_potential = weaponAPtnl ))

    template.apply_modifiers([RootAbyss.Factory.getSetOption(4)])
    return template
    
def getTestCharacter():
    setting = MDF(boss_pdamage = 150, pdamage = 63, armor_ignore = 100, stat_main = 27244, att = 1620, stat_sub=2527, crit = 100, crit_damage = 30)
    template = ichar(modifierlist = [setting])
    return template
    
def getU6000Character(_type, armor_pstat_ptnl = 15, acc_pstat_ptnl = 15, weaponStar = 17):
    ''' Explanation TODO..
    '''
    weaponPtnl = MDF(pdamage = 70, armor_ignore = 30)
    weaponAPtnl = MDF(patt = 6)
    
    subPtnl = MDF(armor_ignore = 40, patt = 9)
    subAPtnl = MDF(patt = 6)
    emblemPtnl = MDF(boss_pdamage = 70)
    emblemAPtnl = MDF(patt = 6)
    
    armorPtnl = MDF(pstat_main = armor_pstat_ptnl)
    armorBonus = MDF(pstat_main = 6, pstat_sub = 6, stat_main = 30)
    armorStar = 17
    
    accPtnl = MDF(pstat_main = acc_pstat_ptnl)
    accBonus = MDF(stat_main = 50, pstat_main = 4, pstat_sub = 4)
    accStar = 17
    
    bonusAttIndex = 2

    #Temporal union object..
    unionModifier = MDF(att = 5, pdamage = 21, armor_ignore = 21, stat_main = 5, crit_damage = 24)
    
    link = LinkSkill.get_full_link()
    
    template = ichar(modifierlist = [unionModifier, link])

    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar))
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=Absolab.Factory))
    template.add_item_with_id("emblem", Default.getEmblem(potential = emblemPtnl, additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Absolab.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = weaponPtnl, additional_potential = weaponAPtnl ))
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3)])
    return template
    

def getDpmStdCharacterTemplate(_type, armor_pstat_ptnl = 15, acc_pstat_ptnl = 15, weaponStar = 17):
    ''' CharacterTemplate : set items w/o weapon-type potentials.
    '''
    weaponAPtnl = MDF(patt = 6)
    
    subAPtnl = MDF(patt = 6)
    
    emblemAPtnl = MDF(patt = 6)
    
    armorPtnl = MDF(pstat_main = armor_pstat_ptnl)
    armorBonus = MDF(pstat_main = 5, pstat_sub = 5, stat_main = 40)
    armorStar = 17
    
    accPtnl = MDF(pstat_main = acc_pstat_ptnl)
    accBonus = MDF(stat_main = 40, pstat_main = 5, pstat_sub = 5)
    accStar = 17
    
    bonusAttIndex = 1

    etcAddPtnl = MDF(att = 10)

    #Temporal union object..
    link = LinkSkill.get_full_link()
    
    template = ichar(modifierlist = [link], level = 240)

    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, additional_potential = etcAddPtnl, bonus = accBonus, star = accStar, enhance = 30))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, additional_potential = etcAddPtnl, bonus = armorBonus, star = armorStar, enhance = 30))
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, additional_potential = etcAddPtnl, bonus = armorBonus, star = armorStar, enhance = 30)
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=Absolab.Factory))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Absolab.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl, elist = [0,0,0,9] ))
    #print(template.itemlist["weapon"].att)
    
    #포스뻥
    template.apply_modifiers([MDF(stat_main_fixed = 96*100)])
    #반감
    template.apply_modifiers([MDF(pdamage_indep = -50)])

    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3), BossAccesory.Factory.getSetOption(9)])
    
    return template
    
def getEpicDpmStdCharacterTemplate(_type, armor_pstat_ptnl = 9, acc_pstat_ptnl = 9, weaponStar = 12):
    ''' CharacterTemplate : set items w/o weapon-type potentials.
    '''

    weaponAPtnl = MDF(patt = 0)
    
    subAPtnl = MDF(patt = 0)
    
    emblemAPtnl = MDF(patt = 0)

    armorPtnl = MDF(pstat_main = armor_pstat_ptnl)
    armorBonus = MDF(pstat_main = 5, pstat_sub = 5, stat_main = 20)
    armorStar = 10
    
    accPtnl = MDF(pstat_main = acc_pstat_ptnl)
    accBonus = MDF(stat_main = 20, pstat_main = 5, pstat_sub = 5)
    accStar = 10
    
    bonusAttIndex = 2

    etcAddPtnl = MDF(att = 10)

    #Temporal union object..
    link = LinkSkill.get_full_link()
    
    template = ichar(modifierlist = [link], level = 230)

    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, additional_potential = etcAddPtnl, bonus = accBonus, star = accStar))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, additional_potential = etcAddPtnl, bonus = armorBonus, star = armorStar))
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, additional_potential = etcAddPtnl, bonus = armorBonus, star = armorStar)
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=Absolab.Factory))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Absolab.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)
    
    #포스뻥
    template.apply_modifiers([MDF(stat_main_fixed = 60*100)])
    #반감
    template.apply_modifiers([MDF(pdamage_indep = -50)])

    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3), BossAccesory.Factory.getSetOption(9)])
    
    return template    

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
    
    template.add_summary("에디셔널 잠재능력 없음")

    weaponAPtnl = MDF()
    subAPtnl = MDF()
    emblemAPtnl = MDF()

    template.add_summary("방어구/장신구 에픽9%, 추옵 60급, 스타포스 10성")    
    armorPtnl = MDF(pstat_main = 9)
    armorBonus = MDF(pstat_main = 6, pstat_sub = 6)
    armorStar = 10
    
    accPtnl = MDF(pstat_main = 9)
    accBonus = MDF(stat_main = 60)
    accStar = 10
    
    template.add_summary("무기 스타포스 10성, 3추옵")
    weaponStar = 10
    bonusAttIndex = 3

    template.add_summary("장신구 : 보장9셋, 방어구 : 여제4셋 + 카루타 4셋")
    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar))
    
    empressSet = Empress.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    template.add_item_with_id("glove", empressSet["glove"])
    template.add_item_with_id("cloak", empressSet["cloak"])
    template.add_item_with_id("shoulder", empressSet["shoulder"])
    template.add_item_with_id("shoes", empressSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=RootAbyss.Factory))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", RootAbyss.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)
    
    template.add_summary("킹오루 / 공마3훈장 / 하트X / 펫공 X")
    template.add_item_with_id("medal", Else.get_medal(3))
    template.add_item_with_id("title", Else.KingOfRootAbyss.copy())
    #template.add_item_with_id("heart", Else.get_heart())
    #template.add_item_with_id("pet", Else.get_pet())
    
    template.apply_modifiers([Empress.Factory.getSetOption(4), RootAbyss.Factory.getSetOption(4), BossAccesory.Factory.getSetOption(9)])
    
    template.add_summary("아케인포스 240")
    template.apply_modifiers([MDF(stat_main_fixed = 2400)])
    
    return template

def getU5000CharacterTemplate(_type):
    #Temporal union object..
    link = LinkSkill.get_full_link()
    template = ichar(modifierlist = [link], level = 230)

    weaponAPtnl = MDF(att = 3)
    subAPtnl = MDF()
    emblemAPtnl = MDF()

    template.add_summary("방어구/장신구 에픽9%, 추옵 70급, 스타포스 10성, 에디 공10")   
    armorAPtnl = MDF(att = 10)    
    armorPtnl = MDF(pstat_main = 9)
    armorBonus = MDF(pstat_main = 5, pstat_sub = 5, stat_main = 20)
    armorStar = 10
    
    accAPtnl = MDF(att = 10)    
    accPtnl = MDF(pstat_main = 9)
    accBonus = MDF(stat_main = 70)
    accStar = 10
    
    template.add_summary("무기 스타포스 12성, 2추옵")
    weaponStar = 12
    bonusAttIndex = 2

    template.add_summary("장신구 : 보장9셋, 방어구 : 앱솔5셋 + 카루타 3셋")
    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, enhance = 30, additional_potential = accAPtnl))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, enhance = 30, additional_potential = armorAPtnl))
    
    empressSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, enhance = 30)
    template.add_item_with_id("glove", empressSet["glove"])
    template.add_item_with_id("cloak", empressSet["cloak"])
    template.add_item_with_id("shoulder", empressSet["shoulder"])
    template.add_item_with_id("shoes", empressSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=Absolab.Factory))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Absolab.Factory.getWeapon(_type, elist = [0,0,0,9], bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)

    template.add_summary("킹오루 / 공마7훈장 / 하트 공30 / 펫공 30")
    template.add_item_with_id("medal", Else.get_medal(7))
    template.add_item_with_id("title", Else.KingOfRootAbyss.copy())
    template.add_item_with_id("heart", Else.get_heart(30))
    template.add_item_with_id("pet", Else.get_pet(30))
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("아케인포스 540")
    template.apply_modifiers([MDF(stat_main_fixed = 5400)])
    
    
    return template

def getU6000CharacterTemplate(_type):
    #Temporal union object..
    link = LinkSkill.get_full_link()
    template = ichar(modifierlist = [link], level = 240)
    
    template.add_summary("에디 공10, 무기류 공6%")


    weaponAPtnl = MDF(patt = 6)
    subAPtnl = MDF(patt = 6)
    emblemAPtnl = MDF(patt = 6)

    template.add_summary("방어구/장신구 유니크15%, 추옵 90급, 스타포스 17성")    
    template.add_summary("장갑 크뎀1줄")
    armorAPtnl = MDF(att = 10)
    armorPtnl = MDF(pstat_main = 12)
    armorBonus = MDF(pstat_main = 5, pstat_sub = 5, stat_main = 40)
    armorStar = 17
    
    accAPtnl = MDF(att = 10)
    accPtnl = MDF(pstat_main = 12)
    accBonus = MDF(stat_main = 90)
    accStar = 17
    
    template.add_summary("무기 스타포스 17성, 2추옵")
    weaponStar = 17
    bonusAttIndex = 2

    template.add_summary("장신구 : 보장9셋, 방어구 : 앱솔5셋 + 카루타 3셋")
    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, enhance = 30, star = accStar, additional_potential = accAPtnl))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, enhance = 30, star = armorStar, additional_potential = armorAPtnl))
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, enhance = 30, bonus = armorBonus, star = armorStar)
    absolabSet["glove"].set_potential(MDF(crit_damage = 8))
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=Absolab.Factory))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Absolab.Factory.getWeapon(_type, elist = [0,0,0,9], bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)

    template.add_summary("핑아 / 공마3훈장 / 하트 공50 / 펫공 40")
    template.add_item_with_id("medal", Else.get_medal(3))
    template.add_item_with_id("title", Else.PingkbinAndMe.copy())
    template.add_item_with_id("heart", Else.get_heart(50))
    template.add_item_with_id("pet", Else.get_pet(40))
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("아케인포스 780")
    template.apply_modifiers([MDF(stat_main_fixed = 7800)])
    
    
    return template

def getU7000CharacterTemplate(_type):
    #Temporal union object..
    link = LinkSkill.get_full_link()
    template = ichar(modifierlist = [link], level = 250)
    
    template.add_summary("에디 2줄, 무기류 공21%")

    weaponAPtnl = MDF(patt = 21)
    subAPtnl = MDF(patt = 21)
    emblemAPtnl = MDF(patt = 21)

    template.add_summary("방어구/장신구 유닉21%, 추옵 110급, 스타포스 18성")
    template.add_summary("장갑 크뎀1줄")
    armorAPtnl = MDF(att = 21)
    armorPtnl = MDF(pstat_main = 21)
    armorBonus = MDF(pstat_main = 5, pstat_sub = 5, stat_main = 60)
    armorStar = 18
    
    accAPtnl = MDF(att = 10, pstat_main = 4)
    accPtnl = MDF(pstat_main = 21)
    accBonus = MDF(stat_main = 110)
    accStar = 18
    
    template.add_summary("무기 스타포스 17성, 1추옵")
    weaponStar = 17
    bonusAttIndex = 1

    template.add_summary("장신구 : 보장7셋 + 마이링 + 칠요, 방어구 : 앱솔5셋 + 카루타 2셋 + 1아케인(무기)")
    template.add_items_with_id(BossAccesory.Factory.getBetter11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, additional_potential = accAPtnl))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl))
    
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
                                                        
                                                        
    template.add_item_with_id("ring3", MeisterSet["ring3"])
    template.add_item_with_id("pendant1", BossAccesorySurprise["pendant1"])
    template.add_item_with_id("pendant2", BossAccesorySurprise["pendant2"])
    

    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, additional_potential = armorAPtnl, 
                                                        bonus = armorBonus, star = armorStar)
    absolabSet["glove"].set_potential(MDF(crit_damage = 8))
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("head", absolabSet["head"])
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=Arcane.Factory))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Arcane.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)

    template.add_summary("핑아 / 공마5훈장 / 하트 공95 / 펫공 80")
    template.add_item_with_id("medal", Else.get_medal(5))
    template.add_item_with_id("title", Else.PingkbinAndMe.copy())
    template.add_item_with_id("heart", Else.get_heart(95, accPtnl, accAPtnl))
    template.add_item_with_id("pet", Else.get_pet(80))
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(2), BossAccesory.Factory.getSetOption(7)])

    template.add_summary("아케인포스 960")
    template.apply_modifiers([MDF(stat_main_fixed = 9600)])
    
    
    return template    


def getU8000CharacterTemplate(_type):
    #Temporal union object..
    link = LinkSkill.get_full_link()
    template = ichar(modifierlist = [link], level = 255)
    
    template.add_summary("에디 2.5줄, 무기류 공15%")

    weaponAPtnl = MDF(patt = 15)
    subAPtnl = MDF(patt = 15)
    emblemAPtnl = MDF(patt = 15)

    template.add_summary("방어구/장신구 레전27%, 추옵 120급, 스타포스 22성")
    template.add_summary("장갑 크뎀2줄")
    armorAPtnl = MDF(att = 11, pstat_main = 7)
    armorPtnl = MDF(pstat_main = 27)
    armorBonus = MDF(pstat_main = 6, pstat_sub = 6, stat_main = 60)
    armorStar = 22
    
    accAPtnl = MDF(att = 11, pstat_main = 7)
    accPtnl = MDF(pstat_main = 27)
    accBonus = MDF(stat_main = 120)
    accStar = 22
    
    template.add_summary("무기 스타포스 22성, 1추옵")
    weaponStar = 22
    bonusAttIndex = 1

    template.add_summary("장신구 : 보장5셋, 방어구 : 앱솔5셋 + 카루타 2셋 + 아케인셰이드")
    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, additional_potential = accAPtnl))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl))
    
    
    ## 놀장 적용
    BossAccesorySurprise = BossAccesory.Factory.getBetter11SetDict(potential = accPtnl, 
                                                                bonus = accBonus, 
                                                                star = 0, 
                                                                additional_potential = accAPtnl)
    
    BossAccesorySurprise["pendant1"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(130, 12))
    BossAccesorySurprise["pendant2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    BossAccesorySurprise["ring2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(120, 10))
    
    
    MeisterSet = Meister.Factory.getAccesoryDict(3, potential = accPtnl,  
                                                        bonus = accBonus,
                                                        additional_potential = accAPtnl,
                                                        star = 0)
    MeisterSet["ring3"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
                                                        
    template.add_item_with_id("ring2", BossAccesorySurprise["ring2"])
    template.add_item_with_id("ring3", MeisterSet["ring3"])
    template.add_item_with_id("pendant1", BossAccesorySurprise["pendant1"])
    template.add_item_with_id("pendant2", BossAccesorySurprise["pendant2"])

    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    absolabSet["glove"].set_potential(MDF(crit_damage = 16))
    template.add_item_with_id("head", absolabSet["head"])
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=Arcane.Factory))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Arcane.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)

    template.add_summary("핑아 / 칠요 / 하트 공120 / 펫공 120")
    
    template.add_items_with_id( Else.get_weekly_set() )
    template.add_item_with_id("title", Else.PingkbinAndMe.copy())
    template.add_item_with_id("heart", Else.get_heart(120, accPtnl, accAPtnl))
    template.add_item_with_id("pet", Else.get_pet(120))
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), 
                                RootAbyss.Factory.getSetOption(2), 
                                BossAccesory.Factory.getSetOption(5)])

    template.add_summary("아케인포스 1140")
    template.apply_modifiers([MDF(stat_main_fixed = 11400)])

    return template            
    
def getU8500CharacterTemplate(_type):
    #Temporal union object..
    link = LinkSkill.get_full_link()
    template = ichar(modifierlist = [link], level = 260)
    
    template.add_summary("에디 레전 3줄, 무기류 공24%")

    weaponAPtnl = MDF(patt = 24)
    subAPtnl = MDF(patt = 24)
    emblemAPtnl = MDF(patt = 24)

    template.add_summary("방어구/장신구 레전33%, 추옵 130급, 스타포스 22성")
    template.add_summary("장갑 크뎀2.5줄")
    armorAPtnl = MDF(att = 14, pstat_main = 7)
    armorPtnl = MDF(pstat_main = 33)
    armorBonus = MDF(pstat_main = 6, pstat_sub = 6, stat_main = 70)
    armorStar = 22
    
    accAPtnl = MDF(att = 14, pstat_main = 7)
    accPtnl = MDF(pstat_main = 33)
    accBonus = MDF(stat_main = 130)
    accStar = 22
    
    template.add_summary("무기 스타포스 22성, 1추옵")
    weaponStar = 22
    bonusAttIndex = 1

    template.add_summary("장신구 : 칠흑셋, 방어구 : 아케인6셋 + 카루타 2셋")
    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, additional_potential = accAPtnl))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl))



    ## 놀장 적용
    BossAccesorySurprise = BossAccesory.Factory.getBetter11SetDict(potential = accPtnl, 
                                                                bonus = accBonus, 
                                                                star = 0, 
                                                                additional_potential = accAPtnl)
    
    BossAccesorySurprise["pendant1"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(130, 12))
    BossAccesorySurprise["pendant2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
    BossAccesorySurprise["ring2"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(120, 10))
    
    
    MeisterSet = Meister.Factory.getAccesoryDict(3, potential = accPtnl,  
                                                        bonus = accBonus,
                                                        additional_potential = accAPtnl,
                                                        star = 0)
    MeisterSet["ring3"].add_main_option(it.EnhancerFactory.get_surprise_enhancement(140, 12))
                                                        
    template.add_item_with_id("ring2", BossAccesorySurprise["ring2"])
    template.add_item_with_id("ring3", MeisterSet["ring3"])
    template.add_item_with_id("pendant1", BossAccesorySurprise["pendant1"])
    template.add_item_with_id("pendant2", BossAccesorySurprise["pendant2"])
    
    template.add_items_with_id(Darkness.Factory.getAccesoryDict(star = accStar,
                                                        bonus = accBonus,
                                                        potential = accPtnl,
                                                        additional_potential = accAPtnl,
                                                        enhancer = it.CharacterModifier(att = 6)
                                                        ))
    
    arcaneSet = Arcane.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    arcaneSet["glove"].set_potential(MDF(crit_damage = 16, stat_main = 9))
    template.add_item_with_id("glove", arcaneSet["glove"])
    template.add_item_with_id("cloak", arcaneSet["cloak"])
    template.add_item_with_id("shoulder", arcaneSet["shoulder"])
    template.add_item_with_id("shoes", arcaneSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.get_subweapon_covering_exception(_type, potential = MDF(), additional_potential = subAPtnl, factory_hook=Arcane.Factory))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Arcane.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)


    template.add_summary("핑아 / 공마10훈장 / 하트 공160 / 펫공 120")
    
    template.add_items_with_id( Else.get_weekly_set() )
    template.add_item_with_id("title", Else.PingkbinAndMe.copy())
    template.add_item_with_id("heart", Else.get_heart(160, accPtnl, accAPtnl))
    template.add_item_with_id("pet", Else.get_pet(120))
    
    template.apply_modifiers([Arcane.Factory.getSetOption(6), 
                                RootAbyss.Factory.getSetOption(2),
                                BossAccesory.Factory.getSetOption(3),
                                Darkness.Factory.getSetOption(4)])

    template.add_summary("아케인포스 1320")
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
            9000 : (4,9)
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