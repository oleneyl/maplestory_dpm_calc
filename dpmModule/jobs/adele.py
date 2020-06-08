from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule, InactiveRule
from . import globalSkill
from .jobbranch import warriors
from .jobclass import cygnus
from .jobclass import flora
from . import jobutils

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 10
        self.jobtype = "str"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def apply_complex_options(self, chtr):
        return

    def get_ruleset(self):
        ruleset = RuleSet()
        return ruleset

    def get_passive_skill_list(self):
        # 매직 서킷: 앱솔 기준 15.4
        WEAPON_ATT = jobutils.get_weapon_att("튜너")
        
        MagicCircuit = core.InformedCharacterModifier("매직 서킷", att=WEAPON_ATT * 0.15)  #무기 마력의 25%, 최대치 가정.
        Pace = core.InformedCharacterModifier("패이스", crit_damage=10, patt=10)
        # Link skill : ignored
        # Nobless = core.InformedCharacterModifier("노블레스", boss_pdamage=4)
        Rudiment = core.InformedCharacterModifier("루디먼트", att=30)
        Mastery = core.InformedCharacterModifier("마스터리", att=30)
        Train = core.InformedCharacterModifier("트레인", stat_main=60)
        Accent = core.InformedCharacterModifier("어센트", att=30, pdamage_indep=15, crit=20)
        Expert = core.InformedCharacterModifier("엑스퍼트", att=30)
        Demolition = core.InformedCharacterModifier("데몰리션", pdamage_indep=30, armor_ignore=20)
        Attain = core.InformedCharacterModifier("어테인", att=30, boss_pdamage=10, crit=20)

        return [MagicCircuit, Pace, Rudiment, Mastery, Train, Accent, Expert, Demolition, Attain]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 34)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5)

        return [WeaponConstant, Mastery]


    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''하이퍼스킬
        트리거-리인포스
        트리거-보스킬러
        레조넌스-엑스트라 힐링
        테리토리-퍼시스트
        블로섬-쿨타임 리듀스

        전분 참조 : https://youtu.be/_VBcNu4Bw6c

        게더링-블로섬

        오더의 칼 개수는 5으로 고정( 리스토어 한정 7)
        게더링-블로섬 연계는 게더링 5히트 / 블로섬 3히트를 가정함
        크리에이션은 평균 4자루의 칼이 공격하는 것을 가정함 (= 최종뎀 15% 효과를 받지못함)

        코어 강화 순서
        디바이드 - 오더(그레이브) - 테리토리(트레드) - 블로섬(스콜) - 크리에이션(게더링) - 샤드 - 레조넌스
        인피니트 - 리스토어 - 루인 - 매서풀 - 오라웨폰 - (바오스)

        '''
        GATHERING_HIT = 5
        BLOSSOM_HIT = 3
        CREATION_HIT = 4
        ShardActive = core.DamageSkill("샤드(액티브)", 0, 80+30+115+225, 3 * 5).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper) # 자동사용만, 최종 450*3
        Shard = core.SummonSkill("샤드", 0, 8000, 80+30+115+225, 3 * 5, 99999999).setV(vEhc, 5, 2, False).wrap(core.SummonSkillWrapper) # 8초마다 자동시전

        # Ether = core.StackSkillWrapper('에테르', 300)
        Resonance = core.DamageSkill("레조넌스", 690, (120+125+265) * (1.15**6), 6, cooltime=10*1000).setV(vEhc, 6, 2, False).wrap(core.DamageSkillWrapper) # 클라공속 900ms, 스택 유지를 위해 10초마다 사용함

        ResonanceStack = core.BuffSkill('레조넌스(스택)', 0, 30*1000, cooltime=-1, pdamage_indep=15, armor_ignore=15).wrap(core.BuffSkillWrapper) # 최종뎀 5, 방무 5, 최대3회. 상시 중첩으로 가정

        #12초마다 발동
        Creation = core.SummonSkill('크리에이션', 0, 9500 - 8000, 200+240+270, CREATION_HIT, 99999999).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper) # 직접시전시 270ms 기본공속

        Territory = core.SummonSkill('테리토리', 420, 405, 100+300, 4, 7000+4000, rem=False, cooltime=30*1000).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper) # 27회 타격, 클라공속540ms
        TerritoryEnd = core.DamageSkill('테리토리(종료)', 0, 550+300, 12).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)

        Gathering = core.DamageSkill('게더링', 0, 260+300, 4 * GATHERING_HIT, cooltime=12*1000).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper) # 칼 불러오기. 블라섬과 연계됨, 딜레이 0 가정

        Order = core.SummonSkill('오더', 0, 1140, 240+120, 2 * 5, 99999999).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper) # 15% 에테르 결정, 시전딜레이 없음으로 가정, 공격주기 1140ms(인피니트로부터 추정됨)

        Divide = core.DamageSkill('디바이드', 600, 375, 6, modifier=core.CharacterModifier(pdamage_indep=20, boss_pdamage=20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper) #트리거 스킬, 클라공속 780ms

        Grave = core.DamageSkill('그레이브', 630, 800, 10, cooltime=-1).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper) #한 번만 사용, 클라공속 840ms
        GraveDebuff = core.BuffSkill('그레이브(디버프)', 0, 999999999, pdamage=20, armor_ignore=10, cooltime=-1).wrap(core.BuffSkillWrapper)

        Blossom = core.DamageSkill('블로섬', 300, 650 * 0.75, 8 * BLOSSOM_HIT, cooltime=20*1000*0.75).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper) # 50%결정. 클라공속 600ms

        Marker = core.DamageSkill('마커', 690, 1000 * (4), 3 * (1), cooltime=60*1000).wrap(core.DamageSkillWrapper) # 최종뎀 300% 증가, 임의위치 조각 5개, 1히트, 결정 5개, 클라공속 900ms
        Scool = core.DamageSkill('스콜', 690, 1000, 12, cooltime=180*1000).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper) #바인드. 클라공속 900ms
        WraithOfGod = core.BuffSkill("레이스 오브 갓", 0, 60*1000, pdamage = 10, cooltime = 120 * 1000).wrap(core.BuffSkillWrapper)

        # 5차

        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 4, 4)
        for sk in [Divide]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeaponCooltimeDummy = auraweapon_builder.get_buff()

        MagicCircuitFullDrive = core.BuffSkill("매직 서킷 풀드라이브", 720, (30+vEhc.getV(3,3))*1000, pdamage = (20 + vEhc.getV(3,3)), cooltime = 200*1000).isV(vEhc,3,3).wrap(core.BuffSkillWrapper)

        Ruin = core.DamageSkill('루인(시전)', 780, 0, 0, cooltime=60*1000).isV(vEhc,2,2).wrap(core.DamageSkillWrapper) # 4초에 나누어서 시전되는 것으로 가정
        RuinFirstTick = core.SummonSkill('루인(소환)', 0, 160, 250 + vEhc.getV(2,2)*10, 6, 2000, cooltime=-1).isV(vEhc,2,2).wrap(core.SummonSkillWrapper) # 12번, 2초에 나누어 사용으로 가정
        RuinSecondTick = core.SummonSkill('루인(공격)', 0, 250, 450 + vEhc.getV(2,2)*18, 9, 2000, cooltime=-1).isV(vEhc,2,2).wrap(core.SummonSkillWrapper) # 8번, 2초에 나누어 사용으로 가정

        Infinite = core.SummonSkill('인피니트', 540, 1140, 350 + vEhc.getV(0,0) * 14, 2 * 18, 30000, cooltime=180*1000).isV(vEhc,0,0).wrap(core.SummonSkillWrapper) #매 공격마다 5% 결정생성. 전분 기준 522회 타격 -> 평균 522/20 = 26회 공격(1140ms). 
        Restore = core.BuffSkill('리스토어', 720, 30*1000, pdamage=15+vEhc.getV(1,1), cooltime=180*1000).isV(vEhc,1,1).wrap(core.BuffSkillWrapper) #소드 2개 증가, 에테르획득량 40%증가
        RestoreTick = core.SummonSkill('리스토어(주기공격)', 0, 2970, 900+36*vEhc.getV(1,1), 3, 30*1000, cooltime=-1).isV(vEhc,1,1).wrap(core.SummonSkillWrapper) # 11회 시전
        OrderRestore = core.SummonSkill('오더(리스토어)', 0, 1140, 240+120, 2 * 1, 30*1000, cooltime=-1).setV(vEhc, 1, 2, False).wrap(core.SummonSkillWrapper) # 15% 에테르 결정, 시전딜레이 없음으로 가정, 공격주기 1140ms(인피니트로부터 추정됨)

        # 딜 사이클 정의

        # 게더링-블로섬
        Blossom.onBefore(Gathering)

        Grave.onAfter(GraveDebuff)
        Grave.set_disabled_and_time_left(1)

        # 루인
        Ruin.onAfter(RuinFirstTick)
        Ruin.onAfter(RuinSecondTick.controller(2000))

        # 리스토어
        Restore.onAfter(RestoreTick)
        Restore.onAfter(OrderRestore)

        # 테리토리
        Territory.onAfter(TerritoryEnd)

        # 레조넌스
        Resonance.onAfter(ResonanceStack)

        return(Divide,
                [globalSkill.maple_heros(chtr.level), ResonanceStack, GraveDebuff, WraithOfGod, Restore,
                    AuraWeaponBuff, AuraWeaponCooltimeDummy, MagicCircuitFullDrive, 
                    globalSkill.useful_sharp_eyes(), globalSkill.soul_contract()] +\
                [Resonance, Grave, Blossom, Marker, Ruin] +\
                [Order, Shard, Territory, Infinite, RuinFirstTick, RuinSecondTick, RestoreTick, OrderRestore, Creation] +\
                [] +\
                [Divide])        


        

