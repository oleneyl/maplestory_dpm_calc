from . import ItemKernel as it
ExMDF = it.ExMDF

_valueMap = [[172, [0,31,46,63,83,106]],
                [249,[0,45,66,91,120,154]],
                [255,[0,46,68,93,123,157]],
                [304,[0,55,81,111,146,187]],
                [318,[0,58,84,116,153,196]],
                [326,[0,59,87,119,157,201]],
                [340,[0,62,90,124,164,210]],
                [348,[0,63,92,127,167,215]],
                [400,[0,72,106,146,192,246]],
                [406,[0,74,108,148,195,250]],
                [140,[0,0,0,0,0,0]], # blade: arcaneshade
                [337,[0,21,46,75,110,151]]]

WeaponFactory = it.WeaponFactoryClass(200, _valueMap, modifier = it.ExMDF(stat_main = 150, stat_sub = 150, boss_pdamage = 30, armor_ignore = 20))


class Factory():
    @staticmethod
    def getWeapon(_type, star, elist, potential = it.ExMDF(), additional_potential = it.ExMDF(), bonusAttIndex = 0, bonusElse = it.ExMDF()):
        
        return WeaponFactory.getWeapon(_type, star = star, elist = elist, potential = potential, additional_potential = additional_potential, bonusAttIndex = bonusAttIndex, bonusElse = bonusElse)

    @staticmethod
    def getBlade(_type, star, elist, potential = it.ExMDF(), additional_potential = it.ExMDF(), bonusElse = it.ExMDF()):
        
        return WeaponFactory.getBlade(_type, star = star, elist = elist, potential = potential, additional_potential = additional_potential, bonusElse = bonusElse)
    
    @staticmethod
    def getZeroSubweapon(_type, potential = it.ExMDF(), additional_potential = it.ExMDF(), bonusElse = it.ExMDF()):

        return WeaponFactory.getZeroSubweapon(_type, potential = potential, additional_potential = additional_potential, bonusElse = bonusElse)

    