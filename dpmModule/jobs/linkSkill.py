from ..kernel import core

# 모법
def empirical_knowledge():
    EmpiricalKnowledge = core.InformedCharacterModifier("임피리컬 널리지", pdamage=9, armor_ignore=9)
    return EmpiricalKnowledge
    
# 모궁
def adventurer_curious():
    AdventurerCurious = core.InformedCharacterModifier("어드벤처러 큐리어스", crit=10)
    return AdventurerCurious

# 모도
def thief_kerning():
    ThiefKerning = core.InformedCharacterModifier("시프 커닝", pdamage=18/2)
    return ThiefKerning

# 시그
def cygnus_bless():
    CygnusBless = core.InformedCharacterModifier("시그너스 블레스", att=25)
    return CygnusBless
    
# 미하일
def knights_watch():
    KnightsWatch = core.BuffSkill("빛의 수호", 900, 110 * 1000, cooltime = 180 * 1000, rem = True, red = True).wrap(core.BuffSkillWrapper)
    return KnightsWatch

# 레지
def spirit_of_freedom():
    SpiritOfFreedom = core.InformedCharacterModifier("스피릿 오브 프리덤")
    return SpiritOfFreedom

# 제논
def hybrid_logic():
    HybridLogic = core.InformedCharacterModifier("하이브리드 로직", pstat_main=10, pstat_sub=10)
    return HybridLogic

# 데슬
def demons_fury():
    DemonsFury = core.InformedCharacterModifier("데몬스 퓨리", boss_pdamage=15)
    return DemonsFury

# 데벤
def wild_rage():
    WildRage = core.InformedCharacterModifier("와일드 레이지", pdamage=10)
    return WildRage

# 루미
def permeate():
    Permeate = core.InformedCharacterModifier("퍼미에이트", armor_ignore=15)
    return Permeate

# 팬텀
def deadly_instinct():
    DeadlyInstinct = core.InformedCharacterModifier("데들리 인스팅트", crit=15)
    return DeadlyInstinct

# 카이저
def iron_will(): # 데벤만 사용할것!!
    IronWill = core.InformedCharacterModifier("아이언 윌", pstat_main=15)
    return IronWill

# 카데나
def intensive_insult():
    IntensiveInsult = core.InformedCharacterModifier("인텐시브 인썰트", pdamage=12)
    return IntensiveInsult

# 엔버, 기본 90초, 직업별 딜사이클에 따라 쿨타임 조절가능
def soul_contract(Cool = 90*1000):
    SoulContract = core.BuffSkill("소울 컨트랙트", 900, 10*1000, cooltime = Cool, pdamage = 45, rem = True, red = True).wrap(core.BuffSkillWrapper)
    return SoulContract

# 아델
def nobless(party_count = 1):
    Nobless = core.InformedCharacterModifier("노블레스", pdamage=min(8, party_count * 2), boss_pdamage=4)
    return Nobless

# 일리움
def tide_of_battle():
    TideOfBattle = core.InformedCharacterModifier("전투의 흐름", pdamage=12)
    return TideOfBattle

# 아크
def solus():
    Solus = core.InformedCharacterModifier("무아", pdamage=11)
    return Solus

# 제로
def rhinne_protection():
    RhinneProtection = core.InformedCharacterModifier("륀느의 가호", armor_ignore=10)
    return RhinneProtection

# 키네
def judgement():
    Judgement = core.InformedCharacterModifier("판단", crit_damage=4)
    return Judgement

# 호영
def bravado():
    Bravado = core.InformedCharacterModifier("자신감", armor_ignore=10)
    return Bravado
