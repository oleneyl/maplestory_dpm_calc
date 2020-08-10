from .characterKernel import ItemedCharacter as ichar
from ..item import Arcane, Absolab, Empress, RootAbyss, BossAccesory, Default, Else
from ..item.ItemKernel import CharacterModifier as MDF
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
    
    template = ichar(modifierlist = [unionModifier])

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
    
    
    template = ichar(modifierlist = [unionModifier])

    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar))
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.getSubweapon(potential = subPtnl, additional_potential = subAPtnl))
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
    
    template = ichar(modifierlist = [], level = 240)

    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, additional_potential = etcAddPtnl, bonus = accBonus, star = accStar, enhance = 30))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, additional_potential = etcAddPtnl, bonus = armorBonus, star = armorStar, enhance = 30))
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, additional_potential = etcAddPtnl, bonus = armorBonus, star = armorStar, enhance = 30)
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.getSubweapon(potential = MDF(), additional_potential = subAPtnl))
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
    
    template = ichar(modifierlist = [], level = 230)

    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, additional_potential = etcAddPtnl, bonus = accBonus, star = accStar))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, additional_potential = etcAddPtnl, bonus = armorBonus, star = armorStar))
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, additional_potential = etcAddPtnl, bonus = armorBonus, star = armorStar)
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.getSubweapon(potential = MDF(), additional_potential = subAPtnl))
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
    template = ichar(modifierlist = [], level = 210)
    
    template.add_summary("에디셔널 잠재능력 없음")

    weaponAPtnl = MDF()
    subAPtnl = MDF()
    emblemAPtnl = MDF()

    template.add_summary("방어구/장신구 에픽6%, 추옵 50급, 스타포스 10성")    
    armorPtnl = MDF(pstat_main = 6)
    armorBonus = MDF(pstat_main = 5, pstat_sub = 5)
    armorStar = 10
    
    accPtnl = MDF(pstat_main = 6)
    accBonus = MDF(stat_main = 50)
    accStar = 10
    
    template.add_summary("무기 스타포스 10성, 2추옵")
    weaponStar = 10
    bonusAttIndex = 2

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
    template.add_item_with_id("subweapon", Default.getSubweapon(potential = MDF(), additional_potential = subAPtnl))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", RootAbyss.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)
    
    template.add_summary("킹오뤁 / 공마3훈장 / 하트X / 펫공 X")
    template.add_item_with_id("medal", Else.get_medal(3))
    template.add_item_with_id("title", Else.KingOfRootAbyss.copy())
    #template.add_item_with_id("heart", Else.get_heart())
    #template.add_item_with_id("pet", Else.get_pet())
    
    template.apply_modifiers([Empress.Factory.getSetOption(4), RootAbyss.Factory.getSetOption(4), BossAccesory.Factory.getSetOption(9)])
    
    template.add_summary("아케인포스 200")
    template.apply_modifiers([MDF(stat_main_fixed = 2000)])
    
    return template

def getU5000CharacterTemplate(_type):
    #Temporal union object..
    template = ichar(modifierlist = [], level = 220)
    
    template.add_summary("에디셔널 잠재능력 없음")

    weaponAPtnl = MDF()
    subAPtnl = MDF()
    emblemAPtnl = MDF()

    template.add_summary("방어구/장신구 에픽9%, 추옵 70급, 스타포스 10성")    
    armorPtnl = MDF(pstat_main = 9)
    armorBonus = MDF(pstat_main = 5, pstat_sub = 5, stat_main = 20)
    armorStar = 10
    
    accPtnl = MDF(pstat_main = 9)
    accBonus = MDF(stat_main = 70)
    accStar = 10
    
    template.add_summary("무기 스타포스 12성, 1추옵")
    weaponStar = 12
    bonusAttIndex = 1

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
    template.add_item_with_id("subweapon", Default.getSubweapon(potential = MDF(), additional_potential = subAPtnl))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", RootAbyss.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)

    template.add_summary("킹오뤁 / 공마3훈장 / 하트X / 펫공 X")
    template.add_item_with_id("medal", Else.get_medal(3))
    template.add_item_with_id("title", Else.KingOfRootAbyss.copy())
    #template.add_item_with_id("heart", Else.get_heart())
    #template.add_item_with_id("pet", Else.get_pet())
    
    template.apply_modifiers([Empress.Factory.getSetOption(4), RootAbyss.Factory.getSetOption(4), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("아케인포스 350")
    template.apply_modifiers([MDF(stat_main_fixed = 3500)])
    
    
    return template

def getU6000CharacterTemplate(_type):
    #Temporal union object..
    template = ichar(modifierlist = [], level = 225)
    
    template.add_summary("에디 공10, 무기류 공3%")

    weaponAPtnl = MDF(patt = 3)
    subAPtnl = MDF(patt = 3)
    emblemAPtnl = MDF(patt = 3)

    template.add_summary("방어구/장신구 에픽12%, 추옵 90급, 스타포스 10성")    
    armorAPtnl = MDF(att = 10)
    armorPtnl = MDF(pstat_main = 12)
    armorBonus = MDF(pstat_main = 5, pstat_sub = 5, stat_main = 40)
    armorStar = 10
    
    accAPtnl = MDF(att = 10)
    accPtnl = MDF(pstat_main = 12)
    accBonus = MDF(stat_main = 90)
    accStar = 10
    
    template.add_summary("무기 스타포스 17성, 1추옵")
    weaponStar = 17
    bonusAttIndex = 1

    template.add_summary("장신구 : 보장9셋, 방어구 : 앱솔5셋 + 카루타 3셋")
    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, additional_potential = accAPtnl))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl))
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.getSubweapon(potential = MDF(), additional_potential = subAPtnl))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Absolab.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)

    template.add_summary("킹오뤁 / 공마3훈장 / 하트 X / 펫공 20")
    template.add_item_with_id("medal", Else.get_medal(3))
    template.add_item_with_id("title", Else.KingOfRootAbyss.copy())
    #template.add_item_with_id("heart", Else.get_heart())
    template.add_item_with_id("pet", Else.get_pet(20))
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("아케인포스 650")
    template.apply_modifiers([MDF(stat_main_fixed = 6500)])
    
    
    return template
    
def getU6500CharacterTemplate(_type):
    #Temporal union object..
    template = ichar(modifierlist = [], level = 230)
    
    template.add_summary("에디 공10, 무기류 공6%")

    weaponAPtnl = MDF(patt = 6)
    subAPtnl = MDF(patt = 6)
    emblemAPtnl = MDF(patt = 6)

    template.add_summary("방어구/장신구 에픽12%, 추옵 100급, 스타포스 10성")    
    armorAPtnl = MDF(att = 10)
    armorPtnl = MDF(pstat_main = 12)
    armorBonus = MDF(pstat_main = 5, pstat_sub = 5, stat_main = 50)
    armorStar = 10
    
    accAPtnl = MDF(att = 10)
    accPtnl = MDF(pstat_main = 12)
    accBonus = MDF(stat_main = 100)
    accStar = 10
    
    template.add_summary("무기 스타포스 17성, 1추옵")
    weaponStar = 17
    bonusAttIndex = 1

    template.add_summary("장신구 : 보장9셋, 방어구 : 앱솔5셋 + 카루타 3셋")
    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, additional_potential = accAPtnl))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl))
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.getSubweapon(potential = MDF(), additional_potential = subAPtnl))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Absolab.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)

    template.add_summary("킹오뤁 / 공마5훈장 / 하트 X / 펫공 40")
    template.add_item_with_id("medal", Else.get_medal(5))
    template.add_item_with_id("title", Else.KingOfRootAbyss.copy())
    #template.add_item_with_id("heart", Else.get_heart())
    template.add_item_with_id("pet", Else.get_pet(60))
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("아케인포스 700")
    template.apply_modifiers([MDF(stat_main_fixed = 7000)])
    
    return template
    
def getU7000CharacterTemplate(_type):
    #Temporal union object..
    template = ichar(modifierlist = [], level = 235)
    
    template.add_summary("에디 공15, 무기류 공6%")

    weaponAPtnl = MDF(patt = 6)
    subAPtnl = MDF(patt = 6)
    emblemAPtnl = MDF(patt = 6)

    template.add_summary("방어구/장신구 유닉15%, 추옵 100급, 스타포스 17성(방어구만)")
    armorAPtnl = MDF(att = 15)
    armorPtnl = MDF(pstat_main = 15)
    armorBonus = MDF(pstat_main = 5, pstat_sub = 5, stat_main = 50)
    armorStar = 17
    
    accAPtnl = MDF(att = 15)
    accPtnl = MDF(pstat_main = 15)
    accBonus = MDF(stat_main = 100)
    accStar = 10
    
    template.add_summary("무기 스타포스 17성, 1추옵")
    weaponStar = 17
    bonusAttIndex = 1

    template.add_summary("장신구 : 보장9셋, 방어구 : 앱솔5셋 + 카루타 3셋")
    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, additional_potential = accAPtnl))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl))
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.getSubweapon(potential = MDF(), additional_potential = subAPtnl))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Absolab.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)

    template.add_summary("킹오뤁 / 공마5훈장 / 하트 공30 / 펫공 60")
    template.add_item_with_id("medal", Else.get_medal(5))
    template.add_item_with_id("title", Else.KingOfRootAbyss.copy())
    template.add_item_with_id("heart", Else.get_heart(30, accPtnl, accAPtnl))
    template.add_item_with_id("pet", Else.get_pet(60))
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("아케인포스 800")
    template.apply_modifiers([MDF(stat_main_fixed = 8000)])
    
    
    return template    
    
def getU7500CharacterTemplate(_type):
    #Temporal union object..
    template = ichar(modifierlist = [], level = 240)
    
    template.add_summary("에디 공15, 무기류 공9%")

    weaponAPtnl = MDF(patt = 9)
    subAPtnl = MDF(patt = 9)
    emblemAPtnl = MDF(patt = 9)

    template.add_summary("방어구/장신구 레전21%, 추옵 110급, 스타포스 17성")
    template.add_summary("장갑 크뎀1.5줄")
    armorAPtnl = MDF(att = 15)
    armorPtnl = MDF(pstat_main = 21)
    armorBonus = MDF(pstat_main = 6, pstat_sub = 6, stat_main = 50)
    armorStar = 17
    
    accAPtnl = MDF(att = 15)
    accPtnl = MDF(pstat_main = 21)
    accBonus = MDF(stat_main = 110)
    accStar = 17
    
    template.add_summary("무기 스타포스 19성, 1추옵")
    weaponStar = 19
    bonusAttIndex = 1

    template.add_summary("장신구 : 보장9셋, 방어구 : 앱솔5셋 + 카루타 2셋 + 아케인셰이드")
    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, additional_potential = accAPtnl))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl))
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    absolabSet["glove"].set_potential(MDF(crit_damage = 8, stat_main = 9))
    template.add_item_with_id("head", absolabSet["head"])
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.getSubweapon(potential = MDF(), additional_potential = subAPtnl))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Arcane.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)

    template.add_summary("킹오뤁 / 공마10훈장 / 하트 공40 / 펫공 80")
    template.add_item_with_id("medal", Else.get_medal(10))
    template.add_item_with_id("title", Else.KingOfRootAbyss.copy())
    template.add_item_with_id("heart", Else.get_heart(40, accPtnl, accAPtnl))
    template.add_item_with_id("pet", Else.get_pet(80))
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(2), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("아케인포스 900")
    template.apply_modifiers([MDF(stat_main_fixed = 9000)])

    return template        

def getU8000CharacterTemplate(_type):
    #Temporal union object..
    template = ichar(modifierlist = [], level = 245)
    
    template.add_summary("에디 공20, 무기류 공15%")

    weaponAPtnl = MDF(patt = 15)
    subAPtnl = MDF(patt = 15)
    emblemAPtnl = MDF(patt = 15)

    template.add_summary("방어구/장신구 레전24%, 방어구 추옵 120급, 장신구 추옵 110급, 스타포스 18성")
    template.add_summary("장갑 크뎀1.5줄")
    armorAPtnl = MDF(att = 20)
    armorPtnl = MDF(pstat_main = 24)
    armorBonus = MDF(pstat_main = 6, pstat_sub = 6, stat_main = 60)
    armorStar = 18
    
    accAPtnl = MDF(att = 20)
    accPtnl = MDF(pstat_main = 24)
    accBonus = MDF(stat_main = 110)
    accStar = 18
    
    template.add_summary("무기 스타포스 22성, 1추옵")
    weaponStar = 20
    bonusAttIndex = 1

    template.add_summary("장신구 : 보장9셋, 방어구 : 앱솔5셋 + 카루타 2셋 + 아케인셰이드")
    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, additional_potential = accAPtnl))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl))
    
    
    absolabSet = Absolab.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    absolabSet["glove"].set_potential(MDF(crit_damage = 8, stat_main = 9))
    template.add_item_with_id("head", absolabSet["head"])
    template.add_item_with_id("glove", absolabSet["glove"])
    template.add_item_with_id("cloak", absolabSet["cloak"])
    template.add_item_with_id("shoulder", absolabSet["shoulder"])
    template.add_item_with_id("shoes", absolabSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.getSubweapon(potential = MDF(), additional_potential = subAPtnl))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Arcane.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)

    template.add_summary("킹오뤁 / 공마10훈장 / 하트 공60 / 펫공 80")
    template.add_item_with_id("medal", Else.get_medal(10))
    template.add_item_with_id("title", Else.KingOfRootAbyss.copy())
    template.add_item_with_id("heart", Else.get_heart(60, accPtnl, accAPtnl))
    template.add_item_with_id("pet", Else.get_pet(80))
    
    template.apply_modifiers([Absolab.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(2), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("아케인포스 1000")
    template.apply_modifiers([MDF(stat_main_fixed = 10000)])

    return template            
    
def getU8200CharacterTemplate(_type):
    #Temporal union object..
    template = ichar(modifierlist = [], level = 250)
    
    template.add_summary("에디 공22, 무기류 공21%")

    weaponAPtnl = MDF(patt = 21)
    subAPtnl = MDF(patt = 21)
    emblemAPtnl = MDF(patt = 21)

    template.add_summary("방어구/장신구 레전27%, 방어구 추옵 130급, 장신구 추옵 110급, 스타포스 20성")
    template.add_summary("장갑 크뎀2줄")
    armorAPtnl = MDF(att = 22)
    armorPtnl = MDF(pstat_main = 27)
    armorBonus = MDF(pstat_main = 6, pstat_sub = 6, stat_main = 70)
    armorStar = 20
    
    accAPtnl = MDF(att = 22)
    accPtnl = MDF(pstat_main = 27)
    accBonus = MDF(stat_main = 110)
    accStar = 20
    
    template.add_summary("무기 스타포스 20성, 1추옵")
    weaponStar = 20
    bonusAttIndex = 1

    template.add_summary("장신구 : 보장9셋, 방어구 : 아케인5셋 + 카루타 3셋")
    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, additional_potential = accAPtnl))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl))
    
    arcaneSet = Arcane.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    arcaneSet["glove"].set_potential(MDF(crit_damage = 16))
    template.add_item_with_id("glove", arcaneSet["glove"])
    template.add_item_with_id("cloak", arcaneSet["cloak"])
    template.add_item_with_id("shoulder", arcaneSet["shoulder"])
    template.add_item_with_id("shoes", arcaneSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.getSubweapon(potential = MDF(), additional_potential = subAPtnl))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Arcane.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)
    
    template.apply_modifiers([Arcane.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("킹오뤁 / 공마10훈장 / 하트 공80 / 펫공 100")
    template.add_item_with_id("medal", Else.get_medal(10))
    template.add_item_with_id("title", Else.KingOfRootAbyss.copy())
    template.add_item_with_id("heart", Else.get_heart(80, accPtnl, accAPtnl))
    template.add_item_with_id("pet", Else.get_pet(100))

    template.add_summary("아케인포스 1100")
    template.apply_modifiers([MDF(stat_main_fixed = 11000)])
    
    return template                

def getU8500CharacterTemplate(_type):
    #Temporal union object..
    template = ichar(modifierlist = [], level = 255)
    
    template.add_summary("에디 공12 + 7%, 무기류 공24%")

    weaponAPtnl = MDF(patt = 24)
    subAPtnl = MDF(patt = 24)
    emblemAPtnl = MDF(patt = 24)

    template.add_summary("방어구/장신구 레전33%, 방어구 추옵 140급, 장신구 추옵 110급, 스타포스 22성")
    template.add_summary("장갑 크뎀2.5줄")
    armorAPtnl = MDF(att = 12, pstat_main = 7)
    armorPtnl = MDF(pstat_main = 33)
    armorBonus = MDF(pstat_main = 6, pstat_sub = 6, stat_main = 80)
    armorStar = 22
    
    accAPtnl = MDF(att = 12, pstat_main = 7)
    accPtnl = MDF(pstat_main = 33)
    accBonus = MDF(stat_main = 110)
    accStar = 22
    
    template.add_summary("무기 스타포스 22성, 1추옵")
    weaponStar = 22
    bonusAttIndex = 1

    template.add_summary("장신구 : 보장9셋, 방어구 : 아케인5셋 + 카루타 3셋")
    template.add_items_with_id(BossAccesory.Factory.get11SetDict(potential = accPtnl, bonus = accBonus, star = accStar, additional_potential = accAPtnl))
    template.add_items_with_id(RootAbyss.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar, additional_potential = armorAPtnl))
    
    arcaneSet = Arcane.Factory.getArmorSetDict(potential = armorPtnl, bonus = armorBonus, star = armorStar)
    arcaneSet["glove"].set_potential(MDF(crit_damage = 16, stat_main = 9))
    template.add_item_with_id("glove", arcaneSet["glove"])
    template.add_item_with_id("cloak", arcaneSet["cloak"])
    template.add_item_with_id("shoulder", arcaneSet["shoulder"])
    template.add_item_with_id("shoes", arcaneSet["shoes"])
    template.add_item_with_id("ring3", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("ring4", Default.getEventRing(potential = accPtnl))
    template.add_item_with_id("subweapon", Default.getSubweapon(potential = MDF(), additional_potential = subAPtnl))
    template.add_item_with_id("emblem", Default.getEmblem(potential = MDF(), additional_potential = emblemAPtnl))
    
    template.add_item_with_id("weapon", Arcane.Factory.getWeapon(_type, bonusAttIndex = bonusAttIndex, star = weaponStar, potential = MDF(), additional_potential = weaponAPtnl ))
    #print(template.itemlist["weapon"].att)

    template.add_summary("킹오뤁 / 공마10훈장 / 하트 공100 / 펫공 120")
    template.add_item_with_id("medal", Else.get_medal(10))
    template.add_item_with_id("title", Else.KingOfRootAbyss.copy())
    template.add_item_with_id("heart", Else.get_heart(100, accPtnl, accAPtnl))
    template.add_item_with_id("pet", Else.get_pet(120))
    
    template.apply_modifiers([Arcane.Factory.getSetOption(5), RootAbyss.Factory.getSetOption(3), BossAccesory.Factory.getSetOption(9)])

    template.add_summary("아케인포스 1320")
    template.apply_modifiers([MDF(stat_main_fixed = 13200)])
    
    return template           