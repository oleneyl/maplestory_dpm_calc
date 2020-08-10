from . import ItemKernel as it

#TODO : 이런 프로세스들을 좀 더 factorization 할 수는 없을까..

EventRing = it.Item(stat_main = 30, stat_sub = 30, att = 20)
def getEventRing(potential = it.CharacterModifier(), additional_potential = it.CharacterModifier()):
    item = EventRing.copy()
    item.set_potential(potential)
    item.set_additional_potential(additional_potential)
    return item

Subweapon = it.Item(stat_main = 10, stat_sub = 10, att = 3)
def getSubweapon(potential = it.CharacterModifier(), additional_potential = it.CharacterModifier()):
    item = Subweapon.copy()
    item.set_potential(potential)
    item.set_additional_potential(additional_potential)
    return item
    
Emblem = it.Item(stat_main = 10, stat_sub = 10, att = 2)
def getEmblem(potential = it.CharacterModifier(), additional_potential = it.CharacterModifier()):
    item = Subweapon.copy()
    item.set_potential(potential)
    item.set_additional_potential(additional_potential)
    return item

def get_subweapon_covering_exception(_type, potential = it.CharacterModifier(), additional_potential = it.CharacterModifier(), factory_hook=None, star=17):
    if _type == '블레이드':
        return factory_hook.getBlade(_type, star=star, potential = potential, additional_potential = additional_potential)
    else:
        return getSubweapon(potential=potential, additional_potential=additional_potential)