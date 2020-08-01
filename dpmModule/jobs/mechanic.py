"""Advisor : 새틀라이트(유니온)
"""

from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, ConcurrentRunRule, ReservationRule
from . import globalSkill
from .jobclass import resistance
from .jobbranch import pirates
from . import jobutils

# TODO: 워머신 타이탄 추가 (로봇 마스터리 적용)
# TODO: [메탈아머 전탄발사] : 호밍 미사일 리로드 지속시간이 4초에서 2초로 감소되고 지속시간이 좀 더 정확하게 적용됩니다.

######   Passive Skill   ######

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.buffrem = False
        self.vEnhanceNum = 14
        self.jobtype = "dex"
        self.ability_list = Ability_tool.get_ability_set('passive_level', 'boss_pdamage', 'crit')
        self.preEmptiveSkills = 1
        
    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(armor_ignore = 20, pdamage = 28+20)

    def get_passive_skill_list(self):
        
        HiddenPiece = core.InformedCharacterModifier("히든 피스",pdamage = 10)
        MechanicMastery = core.InformedCharacterModifier("메카닉 마스터리",att = 20, crit = 10, crit_damage = 5)
        PhisicalTraining = core.InformedCharacterModifier("피지컬 트레이닝",stat_main = 30, stat_sub = 30)
        
        OverTunning = core.InformedCharacterModifier("오버 튜닝",pdamage_indep = 20, crit=20, armor_ignore=30)
        MetalArmorExtreme=core.InformedCharacterModifier("메탈아머 익스트림",att=55)
        LoadedDicePassive = pirates.LoadedDicePassiveWrapper(self.vEhc, 1, 2)
        
        return [HiddenPiece, MechanicMastery, PhisicalTraining, LoadedDicePassive, MetalArmorExtreme, OverTunning]

    def get_not_implied_skill_list(self):
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 50)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -7.5)

        MetalArmorTank = core.InformedCharacterModifier("메탈아머:탱크",crit=30)
        
        return [WeaponConstant, Mastery, MetalArmorTank]

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(ConcurrentRunRule('메탈아머 전탄발사(시전)', '봄버 타임'), RuleSet.BASE)
        ruleset.add_rule(ConcurrentRunRule('봄버 타임', '소울 컨트랙트'), RuleSet.BASE)
        ruleset.add_rule(ReservationRule('소울 컨트랙트', '봄버 타임'), RuleSet.BASE)
        return ruleset
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        코강 순서:
        매시브-호밍-디스토션-마그네틱필드-RM7-RM1
        '''
        #Constants
        ROBOT_SUMMON_REMAIN = 1 + chtr.summonRemain + 0.4

        #Buff skills
        Booster = core.BuffSkill("부스터", 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper)    #딜레이 모름
        WillOfLiberty = core.BuffSkill("윌 오브 리버티", 0, 60*1000, cooltime = 120*1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        MassiveFire = core.DamageSkill("매시브 파이어", 600, 285, 6+1, modifier = core.CharacterModifier(pdamage=10)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        MassiveFire2 = core.DamageSkill("매시브 파이어(2)", 0, 350, 1, modifier = core.CharacterModifier(pdamage=10)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        
        #로디드 데미지 고정.
        LuckyDice = core.BuffSkill("로디드 다이스", 0, 180*1000, pdamage = 40*1/72 + 30*1/6 + 20*(59/72)).isV(vEhc,1,2).wrap(core.BuffSkillWrapper)
        
        #로봇들 :: 로봇당 총뎀6%, 어빌리티 적용 시 7%
        
        Robolauncher = core.SummonSkill("로봇 런처(:RM7)", 630, 1000, (250+135)*(2.08+combat*0.03), 1, 60*1000*ROBOT_SUMMON_REMAIN).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper)
        RobolauncherFinal = core.DamageSkill("로봇 런처(:RM7)(폭발)", 0, 400*(2.08+combat*0.03), 1, cooltime = -1).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        RobolauncherBuff = core.BuffSkill("로봇 런처(:RM7)(버프)", 0, 60*1000*ROBOT_SUMMON_REMAIN, cooltime = -1, pdamage = 7).wrap(core.BuffSkillWrapper)
        #MagneticField = core.SummonSkill("마그네틱 필드", ?, ?, 200, 60*1000, cooltime = 180*1000) 자폭 550% V.getEhc(2, vEnhance[0])
        
        SupportWaver = core.SummonSkill("서포트 웨이버", 630, 80000*ROBOT_SUMMON_REMAIN, 0, 0, 80*1000*ROBOT_SUMMON_REMAIN).wrap(core.SummonSkillWrapper)
        SupportWaverBuff = core.BuffSkill("서포트 웨이버(버프)", 0, 80*1000*ROBOT_SUMMON_REMAIN, pdamage_indep=16, pdamage = 7, cooltime = -1, armor_ignore=10).wrap(core.BuffSkillWrapper)
        SupportWaverFinal = core.DamageSkill("서포트 웨이버(폭발)", 0, 1100*(2.08+combat*0.03), 1, cooltime = -1).wrap(core.DamageSkillWrapper)
        
        RoboFactory = core.SummonSkill("로봇 팩토리", 630, 3000, 500*(2.08+combat*0.03), 3, 30*1000*ROBOT_SUMMON_REMAIN, cooltime=60*1000).setV(vEhc, 5, 2, False).wrap(core.SummonSkillWrapper)
        RoboFactoryBuff = core.BuffSkill("로봇 팩토리(버프)", 0, 30*1000*ROBOT_SUMMON_REMAIN, cooltime = -1, pdamage = 7).wrap(core.BuffSkillWrapper)
        RoboFactoryFinal = core.DamageSkill("로봇 팩토리(폭발)", 0, 1000*(2.08+combat*0.03), 1).setV(vEhc, 5, 2, False).wrap(core.DamageSkillWrapper)
        
        BomberTime = core.BuffSkill("봄버 타임", 990, 10*1000, cooltime = 100*1000).wrap(core.BuffSkillWrapper)
        DistortionField = core.SummonSkill("디스토션 필드", 690, 4000/15, 350, 2, 4000-1, cooltime = 8000).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper)
    
        #오버드라이브 (앱솔 가정)
        #TODO: 템셋을 읽어서 무기별로 다른 수치 적용하도록 만들어야 함.
        WEAPON_ATT = jobutils.get_weapon_att("건")
        Overdrive, OverdrivePenalty = pirates.OverdriveWrapper(vEhc, 5, 5, WEAPON_ATT)
    
        RegistanceLineInfantry = core.SummonSkill("레지스탕스 라인 인팬트리", 360, 1000, (215+8*vEhc.getV(3, 3))*(2.08+combat*0.03), 9, 10*1000, cooltime = 25000).isV(vEhc,3, 3).wrap(core.SummonSkillWrapper) # 메카닉은 인팬트리에 로봇 마스터리 최종뎀이 적용됨
        MultipleOptionGattling = core.SummonSkill("멀티플 옵션(개틀링)", 780, 1901, (200+8*vEhc.getV(2,1))*(2.08+combat*0.03), 6, (75+2*vEhc.getV(2,1))*1000, cooltime = 200 * 1000).isV(vEhc,2,1).wrap(core.SummonSkillWrapper) # 원래 공격주기는 1500이나, 미사일로 인해 손실되는 타수를 보정하기 위해 1901로 기입함.
        MultipleOptionMissle = core.SummonSkill("멀티플 옵션(미사일)", 0, 8000, (350+10*vEhc.getV(2,1))*(2.08+combat*0.03), 24, (75+2*vEhc.getV(2,1))*1000, cooltime = -1).isV(vEhc,2,1).wrap(core.SummonSkillWrapper)
        
        MicroMissle = core.DamageSkill("마이크로 미사일 컨테이너", 540, 375+17*vEhc.getV(0,0), (30 + vEhc.getV(0,0) // 3) * 5, cooltime = 25000).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        BusterCall_ = core.DamageSkill("메탈아머 전탄발사", 8500/37, 400+16*vEhc.getV(4,4), 11).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)
        BusterCallInit = core.DamageSkill("메탈아머 전탄발사(시전)", 1500, 0, 0, cooltime = 200*1000).wrap(core.DamageSkillWrapper) # 선딜레이 1.5초
        BusterCallBuff = core.BuffSkill("메탈아머 전탄발사(버프)", 0, 8500, cooltime = 200*1000).isV(vEhc,4,4).wrap(core.BuffSkillWrapper) # spentime에 넣으면 됨.
        BusterCallEnd = core.DamageSkill("메탈아머 전탄발사(하차)", 1500, 0, 0).wrap(core.DamageSkillWrapper)
        
        MassiveFire.onAfter(MassiveFire2)
        #### 호밍 미사일 정의 ####
        HommingMissle_ = core.DamageSkill("호밍 미사일", 0, 500*0.6, 9+1+combat*1).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        HommingMissle_B = core.DamageSkill("호밍 미사일(봄버)", 0, 500*0.6, 9+1+combat*1+6).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        HommingMissle_Bu = core.DamageSkill("호밍 미사일(전탄)", 0, 500, 9+1+combat*1+7).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        HommingMissle_B_Bu = core.DamageSkill("호밍 미사일(봄버)(전탄)", 0, 500, 9+1+combat*1+6+7).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        
        HommingMissleHolder = core.SummonSkill("호밍 미사일(더미)", 0, 660, 0, 0, 99999 * 100000).wrap(core.SummonSkillWrapper)
        
        def judgeLefttime(target, to, end):
            delta = (target.skill.cooltime - target.cooltimeLeft)
            if delta <= end and delta > to:
                return False
            else:
                return True
        
        MultipleOptionGattling.onAfter(MultipleOptionMissle)
        
        IsBuster_B = core.OptionalElement(BusterCallBuff.is_active, HommingMissle_B_Bu, HommingMissle_B)
        IsBuster = core.OptionalElement(BusterCallBuff.is_active, HommingMissle_Bu, HommingMissle_)
        IsBomber = core.OptionalElement(BomberTime.is_active, IsBuster_B, IsBuster)
        HommingMissle = core.OptionalElement(partial(judgeLefttime, BusterCallBuff, 14000, 16000), IsBomber)
        
        HommingMissleHolder.onTick(HommingMissle)
        
        BusterCall = core.RepeatElement(BusterCall_, 37)
        BusterCall.onAfter(BusterCallEnd)
        BusterCallInit.onAfters([BusterCall, BusterCallBuff])
        
        Robolauncher.onAfter(RobolauncherFinal.controller(60*1000*ROBOT_SUMMON_REMAIN))
        Robolauncher.onAfter(RobolauncherBuff.controller(1))
        
        SupportWaver.onAfter(SupportWaverFinal.controller(80*1000*ROBOT_SUMMON_REMAIN))
        SupportWaver.onAfter(SupportWaverBuff.controller(1))
        
        RoboFactory.onAfter(RoboFactoryFinal.controller(30*1000*ROBOT_SUMMON_REMAIN))
        RoboFactory.onAfter(RoboFactoryBuff.controller(1))

        BusterCallBuff.protect_from_running()
        
        return(MassiveFire,
                [globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(),
                    Booster, WillOfLiberty, LuckyDice, SupportWaverBuff, RobolauncherBuff, RoboFactoryBuff, BomberTime, Overdrive, OverdrivePenalty,
                    globalSkill.soul_contract()] +\
                [MicroMissle, BusterCallInit] +\
                [HommingMissleHolder, RegistanceLineInfantry, SupportWaver, Robolauncher, RoboFactory, DistortionField, MultipleOptionGattling, MultipleOptionMissle] +\
                [BusterCallBuff] +\
                [MassiveFire])