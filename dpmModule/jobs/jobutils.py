from ..kernel import core
from ..kernel.graph import DynamicVariableOperation
from ..item import RootAbyss, Absolab, Arcane
import math

# DamageSkill Duplicator
def create_auxilary_attack(skill_wrapper, ratio, nametag = '복사'):
    original_skill = skill_wrapper.skill
    copial_skill = core.DamageSkill(name = DynamicVariableOperation.reveal_argument(original_skill.name) + nametag,
        delay = DynamicVariableOperation.wrap_argument(0),
        damage = original_skill.damage * DynamicVariableOperation.wrap_argument(ratio),
        hit = original_skill.hit,
        modifier=original_skill._static_skill_modifier).wrap(core.DamageSkillWrapper)
    
    skill_wrapper.onAfter(copial_skill)

# 스펙 측정시마다 수동으로 변경 필요
def get_weapon_att(WEAPON_NAME, spec = 6000):
    if spec < 5000:
        #파프
        return RootAbyss.WeaponFactory.getWeapon(WEAPON_NAME, star = 0, elist = [0,0,0,0] ).main_option.att
    elif spec < 7000:
        #앱솔
        return Absolab.WeaponFactory.getWeapon(WEAPON_NAME, star = 0, elist = [0,0,0,0] ).main_option.att
    else:
        #아케인
        return Arcane.WeaponFactory.getWeapon(WEAPON_NAME, star = 0, elist = [0,0,0,0] ).main_option.att

def debug_skill(skill_wrapper):
    skill_wrapper.onJustAfter(core.BuffSkill(skill_wrapper._id+"(디버그)", 0, 1, cooltime = -1).wrap(core.BuffSkillWrapper))

def cdr_hat(sec = 0, red = True):
    '''Return InformedCharacterModifier for CDR Hat
    - arguments
      int sec: seconds
      bool red: reduce pstat    
    '''

    '''
    윗잠: 1초 = 9%, 2초 = 12%
    아랫잠: 1초 = 7%
    0초: 없음 / 없음
    1초: 1초 1줄 / 없음
    2초: 2초 1줄 / 없음
    3초: 2초 1줄, 1초 1줄 / 없음
    4초: 2초 1줄, 1초 2줄 / 없음
    5초: 2초 1줄, 1초 2줄 / 1초 1줄
    6초: 2초 2줄, 1초 1줄 / 1초 1줄
    7초: 2초 3줄 / 1초 1줄
    8초: 2초 3줄 / 1초 2줄
    9초: 2초 3줄 / 1초 3줄
    '''
    pstat = [0, 9, 12, 21, 30, 37, 40, 43, 50, 57]
    return core.InformedCharacterModifier("재사용 대기시간 감소 (" + str(sec) + "초)", cooltime_reduce = sec * 1000, pstat_main = -1 * int(red) * pstat[sec])

# TODO: 약칭을 사용 가능하도록 수정필요
# 헬스컷, 마나컷, 리밋 등 효율이 낮거나 스위프트, 오버패스 등 딜 기여가 없는 링은 제외
def seed_ring(name = '리스트레인트', level = 4, val = -1):
    '''
    name = 반지의 정식 명칭
    level = 레벨 (기본 4)
    val = 다른 값을 참조하는 반지에 한해 입력
    - 웨폰퍼프: 무기 순공격력, 레벨퍼프: 레벨, 링오브썸: 스탯 합
    '''
    if name == '리스트레인트':
        return core.BuffSkill("리스트레인트 링", 0, (7+2*level)*1000, cooltime = 180000, patt = 25*level).wrap(core.BuffSkillWrapper)
    if name == '리스트테이커':
        return core.BuffSkill("리스트테이커 링", 0, (6+6*level)*1000, cooltime = 180000, patt = (level+1)*10).wrap(core.BuffSkillWrapper)
    if name == '크라이시스':
        return core.BuffSkill("크라이시스 H/M 링", 0, (7+2*level)*1000, cooltime = 180000, patt = 25*level).wrap(core.BuffSkillWrapper)
    if name == '웨폰퍼프':
        if val == -1:
            raise ValueError
        return core.BuffSkill("웨폰퍼프 링", 0, (7+2*level)*1000, cooltime = 180000, stat_main = level * val).wrap(core.BuffSkillWrapper)
    if name == '레벨퍼프':
        if val == -1:
            raise ValueError
        return core.BuffSkill("레벨퍼프 링", 0, (7+2*level)*1000, cooltime = 180000, stat_main = (2+7*level) * 0.1 * val).wrap(core.BuffSkillWrapper)
    if name == '링오브썸':
        if val == -1:
            raise ValueError
        return core.BuffSkill("링 오브 썸", 0, (7+2*level)*1000, cooltime = 180000, stat_main = math.ceil(level/2) * 0.01 * val).wrap(core.BuffSkillWrapper)
    if name == '듀라빌리티':
        # 데몬어벤져 전용
        return core.BuffSkill("듀라빌리티 링", 0, (6+6*level)*1000, cooltime = 180000, pstat_main = 100).wrap(core.BuffSkillWrapper)
    if name == '얼티메이덤':
        # 현재 구현 불가
        return core.BuffSkill("얼티메이덤 링", 0, (7+2*level)*1000, cooltime = 180000).wrap(core.BuffSkillWrapper)
    if name == '크리데미지':
        return core.BuffSkill("크리데미지 링", 0, (7+2*level)*1000, cooltime = 180000, crit_damage = 7 * level).wrap(core.BuffSkillWrapper)
    if name == '크리디펜스':
        # 크확 100% 가정
        return core.BuffSkill("크리디펜스 링", 0, (7+2*level)*1000, cooltime = 180000, armor_ignore = 25 * level).wrap(core.BuffSkillWrapper)
    raise ValueError

def reboot_passive(level = -1):
    if level == -1:
        raise ValueError
    return core.InformedCharacterModifier("리부트", att = 5, pdamage = level // 2)
