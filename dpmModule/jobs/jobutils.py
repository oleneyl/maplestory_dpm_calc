from ..item import RootAbyss, Absolab, Arcane

# 스펙 측정시마다 수동으로 변경 필요

def getWeaponATT(WEAPON_NAME, spec = 6000):
    if spec < 5000:
        #파프
        return RootAbyss.WeaponFactory.getWeapon(WEAPON_NAME, star = 0, elist = [0,0,0,0] ).att
    elif spec < 7000:
        #앱솔
        return Absolab.WeaponFactory.getWeapon(WEAPON_NAME, star = 0, elist = [0,0,0,0] ).att
    else:
        #아케인
        return Arcane.WeaponFactory.getWeapon(WEAPON_NAME, star = 0, elist = [0,0,0,0] ).att