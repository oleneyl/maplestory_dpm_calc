from ..kernel import core
from ..kernel.graph import DynamicVariableOperation
from ..item import RootAbyss, Absolab, Arcane, Genesis
import math


def create_auxilary_attack(skill_wrapper, ratio = 1, nametag='(복사)'):
    '''
    create_auxilary_attack: DamageSkill Duplicator
    Easy Shadow Partner Function
    - parameters
      .skill_wrapper : target DamageSkillWrapper
      .ratio : copy skill's damage ratio
      .nametag : skill copier's name
    '''
    original_skill = skill_wrapper.skill
    copial_skill = core.DamageSkill(name = DynamicVariableOperation.reveal_argument(original_skill.name) + nametag,
        delay = DynamicVariableOperation.wrap_argument(0),
        damage = original_skill.damage * DynamicVariableOperation.wrap_argument(ratio),
        hit = original_skill.hit,
        modifier=original_skill._static_skill_modifier).wrap(core.DamageSkillWrapper)
    
    skill_wrapper.onJustAfter(copial_skill)

# TODO: 스펙 측정시마다 수동으로 변경 필요
def get_weapon_att(WEAPON_NAME, spec = 6000):
    if spec < 5000:
        #파프
        return RootAbyss.WeaponFactory.getWeapon(WEAPON_NAME, star = 0, elist = [0,0,0,0] ).main_option.att
    elif spec < 7000:
        #앱솔
        return Absolab.WeaponFactory.getWeapon(WEAPON_NAME, star = 0, elist = [0,0,0,0] ).main_option.att
    elif spec < 8500:
        #아케인
        return Arcane.WeaponFactory.getWeapon(WEAPON_NAME, star = 0, elist = [0,0,0,0] ).main_option.att
    else:
        return Genesis.WeaponFactory.getWeapon(WEAPON_NAME, star = 0, elist = [0,0,0,0] ).main_option.att

def debug_skill(skill_wrapper):
    skill_wrapper.onJustAfter(core.BuffSkill(skill_wrapper._id+"(디버그)", 0, 1, cooltime = -1).wrap(core.BuffSkillWrapper))

# 리부트 패시브
def reboot_passive(level = -1):
    if level == -1:
        raise ValueError
    return core.InformedCharacterModifier("리부트", att = 5, pdamage = level // 2)

'''
윗잠: 1초 = 9%, 2초 = 12%
아랫잠: 1초 = 7%
0초: 없음 / 없음
1초: 1초 1줄 / 없음
2초: 2초 1줄 / 없음
3초: 2초 1줄, 1초 1줄 / 없음
4초: 2초 1줄, 1초 2줄 / 없음
5초: 2초 1줄, 1초 2줄 / 1초 1줄 (리부트: 2초 2줄, 1초 1줄)
6초: 2초 2줄, 1초 1줄 / 1초 1줄 (리부트: 2초 3줄)
7초: 2초 3줄 / 1초 1줄
8초: 2초 3줄 / 1초 2줄
9초: 2초 3줄 / 1초 3줄
'''
def cdr_hat(sec: int = 0, stat_red = True, is_reboot = False):
    '''
    Return InformedCharacterModifier for CDR Hat
    - arguments
      int sec: seconds
      bool stat_red: True if reduce pstat
      bool is_reboot: True if Reboot environment
    '''
    pstat = [0, 9, 12, 21, 30, 37, 40, 43, 50, 57]
    pstatr = [0, 9, 12, 21, 30, 33, 36]
    
    # 리부트: 최대 6초
    if is_reboot:
        if sec > 6:
            raise ValueError
        return core.InformedCharacterModifier("재사용 대기시간 감소 (" + str(sec) + "초)", cooltime_reduce = sec * 1000, pstat_main = -1 * stat_red * pstatr[sec])
    
    # 본섭: 최대 9초
    if sec > 9:
        raise ValueError
    return core.InformedCharacterModifier("재사용 대기시간 감소 (" + str(sec) + "초)", cooltime_reduce = sec * 1000, pstat_main = -1 * stat_red * pstat[sec])

# TODO: 약칭을 사용 가능하도록 수정필요
# 헬스컷, 마나컷, 리밋 등 효율이 낮거나 스위프트, 오버패스 등 딜 기여가 없는 링은 제외

'''
시드링 (기본 4레벨)

TODO: 링오브썸, 듀라빌리티, 얼티메이덤
'''

def restraint_ring(level: int = 4):
    return core.BuffSkill("리스트레인트 링", 0, (7+2*level)*1000, cooltime = 180000, patt = 25*level).wrap(core.BuffSkillWrapper)

def risktaker_ring(level: int = 4):
    return core.BuffSkill("리스트테이커 링", 0, (6+6*level)*1000, cooltime = 180000, patt = (level+1)*10).wrap(core.BuffSkillWrapper)

def crisis_ring(level: int = 4):
    return core.BuffSkill("크라이시스 H/M 링", 0, (7+2*level)*1000, cooltime = 180000, patt = 25*level).wrap(core.BuffSkillWrapper)

def weaponpuff_ring(level: int = 4, weapon_att: int = -1):
    if weapon_att == -1:
        raise ValueError
    return core.BuffSkill("웨폰퍼프 링", 0, (7+2*level)*1000, cooltime = 180000, stat_main = level * weapon_att).wrap(core.BuffSkillWrapper)

def levelpuff_ring(level: int = 4, chtr_level: int = -1):
    if chtr_level == -1:
        raise ValueError
    return core.BuffSkill("레벨퍼프 링", 0, (7+2*level)*1000, cooltime = 180000, stat_main = (2+7*level) * 0.1 * chtr_level).wrap(core.BuffSkillWrapper)

def crit_damage_ring(level: int = 4):
    return core.BuffSkill("크리데미지 링", 0, (7+2*level)*1000, cooltime = 180000, crit_damage = 7 * level).wrap(core.BuffSkillWrapper)

def crit_defense_ring(level: int = 4):
    # 크확 100% 가정
    return core.BuffSkill("크리디펜스 링", 0, (7+2*level)*1000, cooltime = 180000, armor_ignore = 25 * level).wrap(core.BuffSkillWrapper)
