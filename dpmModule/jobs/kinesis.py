"""
Kinesis.py

Advisor : Gwang-jun
"""
from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill, jobutils
from .jobbranch import magicians
from .jobclass import demon
from typing import Any, Dict


class KinesisStackWrapper(core.StackSkillWrapper):
    def __init__(self, skill, _max, psychicoverjudge, name=None):
        super().__init__(skill, _max, name=name)
        self.psychicoverjudge = psychicoverjudge
        self.set_name_style("pp 변화 : %d")

    def vary(self, d):
        delta = d

        if self.psychicoverjudge() and delta < 0:
            delta = max(abs(delta) // 2, 1) * -1  # BPM의 소모값은 0이 되면 안됨

        result = super(KinesisStackWrapper, self).vary(delta)
        return result

    def charge(self):
        delta = (self._max - self.stack) // 2
        result = super(KinesisStackWrapper, self).vary(delta)
        return result

    def chargeController(self):
        task = core.Task(self, self.charge)
        return core.TaskHolder(task, name="싸이킥 차지")

    def judge_bpm_safe(self, stack):  # BPM 유지를 위해 pp를 최소 2 이상 유지해야함
        return self.stack - stack >= 2

    def judge_ultimate(self, stack):
        if self.psychicoverjudge():
            return self.judge_bpm_safe(stack // 2)
        else:
            return self.judge_bpm_safe(stack)


class LawOfGravityDebuffWrapper(core.SummonSkillWrapper):
    def __init__(self, skill):
        super(LawOfGravityDebuffWrapper, self).__init__(skill)
        self.mobPulled = 0

    def _use(self, skill_modifier):
        self.mobPulled = 0
        return super(LawOfGravityDebuffWrapper, self)._use(skill_modifier)

    def _useTick(self):  # 데미지 계산 -> 끌어당김 판정 -> 다음 틱 계산
        result = super(LawOfGravityDebuffWrapper, self)._useTick()
        self.mobPulled += 6
        return result

    def get_modifier(self):
        modifier = super(LawOfGravityDebuffWrapper, self).get_modifier()
        return modifier + core.CharacterModifier(pdamage_indep=min(self.mobPulled * 3, 40))  # TODO: 2 아니면 3인데 실험 필요함

    def get_delay(self):
        return max(self.skill.delay - (self.mobPulled + 6) * 120, 1200)


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vEnhanceNum = 13
        self.jobtype = "INT"
        self.jobname = "키네시스"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 2
        self.hyperStatPrefixed = 150 # PP 10레벨 투자

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        SuperSensitive = core.InformedCharacterModifier("초감각",crit = 10)
        PsychicForce1Passive = core.InformedCharacterModifier("사이킥 포스1(패시브)",att = 10)
        Inertia1 = core.InformedCharacterModifier("내재 1",att = 10)
        
        PsychicForce2Passive = core.InformedCharacterModifier("사이킥 포스 2(패시브)",att = 10)
        PureForce = core.InformedCharacterModifier("순수한 힘",pdamage = 20)
        Inertia2 = core.InformedCharacterModifier("내재 2",att = 10)
        ESPMastery = core.InformedCharacterModifier("ESP 마스터리",crit = 10, stat_main = 40)
        
        MindEnhance = core.InformedCharacterModifier("정신 강화",patt = 10)
        Accurate = core.InformedCharacterModifier("정밀",crit = 20, crit_damage = 20)
        PsychicChargingPassive = core.InformedCharacterModifier("사이킥 차징(패시브)",boss_pdamage = 30 + self.combat)
        PsychicForce3Passive = core.InformedCharacterModifier("사이킥 포스 3(패시브)",att = 10)
        
        ESPBattleOrder = core.InformedCharacterModifier("ESP 배틀오더",att = 50 + 2*passive_level, pdamage = 20 + passive_level)
        Transcendence = core.InformedCharacterModifier("각성",pdamage_indep = 30 + passive_level)
        SupremeConcentration = core.InformedCharacterModifier("정신집중-유지", buff_rem = 20+passive_level)
        Transport = core.InformedCharacterModifier("전달",armor_ignore = 25 + passive_level)
        Mastery = core.InformedCharacterModifier("숙달",crit_damage = 10 + passive_level)
        
        return [SuperSensitive, PsychicForce1Passive, Inertia1,
                            PsychicForce2Passive, PureForce, Inertia2, ESPMastery,
                            MindEnhance, Accurate, PsychicChargingPassive, PsychicForce3Passive,
                             ESPBattleOrder, Transcendence, SupremeConcentration, Transport, Mastery]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat     
        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 20)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=90+2*passive_level)
        PsychicForce3Passive = core.InformedCharacterModifier("사이킥 포스 3(패시브)", pdamage_indep = 20)
        return [WeaponConstant, Mastery, PsychicForce3Passive]
        
        

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        하이퍼
        싸이킥 그랩 - 보스포인트/리인포스
        싸이킥그라운드-리듀스 가드/퍼시스트
        싸이코브레이크 - 인핸스
        
        코강 순서:
        BPM 메테리얼 그랩 드레인 트레인 텔레키네시스
        
        메테리얼 사용
        불릿 사용하지 않음.
        '''
        DEALCYCLE = options.get("dealcycle", "material")
        SHOT_RATE = options.get("shot_rate", 0.8)
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        ######   Skill   ######

        ULTIMATE_AWAKENING = core.CharacterModifier(crit_damage = 20 + passive_level)
        '''This function is recommended.
        '''
        Booster = core.BuffSkill("부스터", 0, 180000).wrap(core.BuffSkillWrapper)
        PsychicShield = core.BuffSkill("사이킥 실드", 0, 180000).wrap(core.BuffSkillWrapper)

        Ultimate_Material = core.DamageSkill("얼티메이트-메테리얼", 630, 700 + 3*self.combat, 10, modifier = ULTIMATE_AWAKENING).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)#   7
        PsychicDrain = core.SummonSkill("싸이킥 드레인", 540, 500, 150, 1, 15000, cooltime = 5000, rem = False).setV(vEhc, 4, 5, False).wrap(core.SummonSkillWrapper) # 1칸+
        
        PsychicForce3 = core.DamageSkill("싸이킥 포스3", 270, 0, 0).wrap(core.DamageSkillWrapper)
        PsychicForce3Dot = core.DotSkill("싸이킥 포스3(도트)", 0, 1000, 403.125, 1, 30000, cooltime = -1).wrap(core.DotSkillWrapper) # ~20초 평균 퍼뎀
        PsychicGround = core.BuffSkill("싸이킥 그라운드2", 270, 30000 + 15000, rem = False, armor_ignore = 10 + 6*1, pdamage_indep = 10 + 3*1).wrap(core.BuffSkillWrapper)
        PsychicGroundDamage = core.DamageSkill("싸이킥 그라운드2(공격)", 0, 500+10*self.combat, 1).wrap(core.DamageSkillWrapper) # +1
        PsycoBreak = core.BuffSkill("싸이코 브레이크", 630, 30000, pdamage_indep = min(5 * 2 * 2, 15), rem = False).wrap(core.BuffSkillWrapper) #+1
        PsycoBreakDamage = core.DamageSkill("싸이코 브레이크(공격)", 0, 1000 +7*self.combat, 4).wrap(core.DamageSkillWrapper)
        
        TeleKinesis = core.DamageSkill("텔레키네시스", 0, 350, 0.7).setV(vEhc, 5, 3, False).wrap(core.DamageSkillWrapper)
        UltimateBPM = core.SummonSkill("얼티메이트-B.P.M.", 0, 600, 175 + 2*self.combat, 7, 999999999, modifier = ULTIMATE_AWAKENING).setV(vEhc, 0, 2, False).wrap(core.SummonSkillWrapper) #1
        PsychicGrab2 = core.DamageSkill("싸이킥 그랩", 576, 470 + 4*passive_level, 5,  modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper) #+2, 그랩 1번에 스매싱 5회 사용 가능 (510*5+210)/5
        UltimatePsychic = core.DamageSkill("얼티메이트-싸이킥 샷", 1080, 300+3*self.combat, 3*5*2*SHOT_RATE,  modifier = ULTIMATE_AWAKENING + core.CharacterModifier(pdamage = 20)).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper) #5, 그랩 1번에 샷 1회 사용가능 (900+210)
        UltimatePsychicBuff = core.BuffSkill("얼티메이트-싸이킥 샷(디버프)", 0, 10000, rem = True, armor_ignore = 15, cooltime = -1).wrap(core.BuffSkillWrapper)
        
        PsychicCharging = core.BuffSkill("싸이킥 차징", 0, 500, cooltime = (45 - self.combat)*1000, red = True).wrap(core.BuffSkillWrapper) #남은포인트의 50%충전
        
        UltimateTrain = core.SummonSkill("얼티메이트-트레인", 630, 11999 / 17, 180 + 3*self.combat, 6, 12000, modifier = ULTIMATE_AWAKENING).setV(vEhc, 4, 2, False).wrap(core.SummonSkillWrapper) # 220% -> 140% 평균

        #하이퍼
        EverPsychic = core.DamageSkill("에버 싸이킥", 870, 400, 16, cooltime = 120000).wrap(core.DamageSkillWrapper) # 캔슬 통해 딜레 870ms
        EverPsychicFinal = core.DamageSkill("에버 싸이킥(최종)", 0, 1500, 1,  modifier = core.CharacterModifier(armor_ignore = 50, crit = 100)).wrap(core.DamageSkillWrapper)
        #Psycometry = core.DamageSkill()
        PsychicOver = core.BuffSkill("싸이킥 오버", 0, 30000, cooltime = 210000).wrap(core.BuffSkillWrapper) # 소모량 절반 / 포인트 지속증가(초당 1)
        PsychicOverSummon = core.SummonSkill("싸이킥 오버(소환)", 0, 750, 0, 0, 30000, cooltime = -1).wrap(core.SummonSkillWrapper)
        
        #5차
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        AnotherGoddessBuff, AnotherVoid = demon.AnotherWorldWrapper(vEhc, 0, 0)
        AnotherHeal = core.SummonSkill("회복의 축복", 0, 4000/0.25, 0, 0, 40000, cooltime=-1).wrap(core.SummonSkillWrapper)
        
        PsychicTornado = core.SummonSkill("싸이킥 토네이도", 540, 1000, 500+20*vEhc.getV(2,2), 4, 20000, red = True, cooltime = 120000).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)# -15
        PsychicTornadoFinal_1 = core.DamageSkill("싸이킥 토네이도(1)", 540, (200+3*vEhc.getV(2,2))*3, 2, cooltime=-1).wrap(core.DamageSkillWrapper)
        PsychicTornadoFinal_2 = core.DamageSkill("싸이킥 토네이도(2)", 0, (350+10*vEhc.getV(2,2))*3, 10*3, cooltime=-1).wrap(core.DamageSkillWrapper)

        UltimateMovingMatter = core.SummonSkill("얼티메이트-무빙 매터", 480, 25000/64, 500+20*vEhc.getV(0,0), 5, 25000, cooltime = 90000, red=True, modifier = ULTIMATE_AWAKENING).isV(vEhc,0,0).wrap(core.SummonSkillWrapper)# -10
        UltimateMovingMatterFinal = core.DamageSkill("얼티메이트-무빙 매터(최종)", 0, 700+28*vEhc.getV(0,0), 12, modifier = ULTIMATE_AWAKENING).wrap(core.DamageSkillWrapper)
        
        UltimatePsychicBullet = core.DamageSkill("얼티메이트-싸이킥 불릿", 630, 550 + 22*vEhc.getV(3,3), 6, modifier = ULTIMATE_AWAKENING).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)# -2, 딜레이 420ms + 그랩 210ms
        UltimatePsychicBulletBlackhole = core.SummonSkill("얼티메이트-싸이킥 불릿(블랙홀)", 0, 500, 500+20*vEhc.getV(3,3), 3, 500*4, cooltime = -1, modifier = ULTIMATE_AWAKENING).isV(vEhc,3,3).wrap(core.SummonSkillWrapper)# +1
        
        LawOfGravity = core.DamageSkill("로 오브 그래비티", 720, 400+16*vEhc.getV(0,0), 6, cooltime=60000, red=True).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        LawOfGravityDebuff = core.SummonSkill("로 오브 그래비티(디버프)", 0, 3600, 500+20*vEhc.getV(0,0), 8, 22000, cooltime=-1).isV(vEhc,0,0).wrap(LawOfGravityDebuffWrapper)
        LawOfGravityFinal = core.DamageSkill("로 오브 그래비티(폭발)", 0, 600+24*vEhc.getV(0,0), 15, cooltime=-1).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        
        PsychicPoint = KinesisStackWrapper(core.BuffSkill("싸이킥 포인트", 0, 999999999), 30 + 10, PsychicOver.is_active)
        
        ### Build Graph ###

        ### Telekinesis
        for sk in [PsychicGrab2, PsychicGroundDamage, PsycoBreakDamage, PsychicTornadoFinal_1, PsychicTornadoFinal_2, LawOfGravity, LawOfGravityFinal]:
            sk.onAfter(TeleKinesis)
        PsychicTornado.onTick(TeleKinesis)
        LawOfGravityDebuff.onTick(TeleKinesis)

        ### 회복의 축복
        AnotherVoid.onEventElapsed(AnotherHeal, 4000)
        AnotherHeal.onTick(PsychicPoint.stackController(40*0.01*(15+vEhc.getV(0,0)//2)))
        
        ### Tandem skill connection
        PsychicForce3.onAfter(PsychicForce3Dot)
        PsychicGround.onAfter(PsychicGroundDamage)
        PsycoBreak.onAfter(PsycoBreakDamage)
        UltimatePsychic.onAfter(UltimatePsychicBuff)
        EverPsychic.onAfter(EverPsychicFinal)
        PsychicOver.onAfter(PsychicOverSummon)
        PsychicTornado.onAfter(PsychicTornadoFinal_1.controller(20*1000))
        PsychicTornado.onAfter(PsychicTornadoFinal_2.controller(20*1000))
        UltimateMovingMatter.onAfter(UltimateMovingMatterFinal)
        UltimatePsychicBullet.onAfter(UltimatePsychicBulletBlackhole)
        LawOfGravity.onAfter(LawOfGravityDebuff)
        LawOfGravity.onAfter(LawOfGravityFinal.controller(22000))

        ### Psychic point
        Ultimate_Material.onConstraint(core.ConstraintElement("7포인트", PsychicPoint, partial(PsychicPoint.judge_ultimate,7)))
        Ultimate_Material.onBefore(PsychicPoint.stackController(-7))
        
        PsychicForce3.onConstraint(core.ConstraintElement("도트 종료시", PsychicForce3Dot, PsychicForce3Dot.is_not_active))
        PsychicForce3.onBefore(PsychicPoint.stackController(1))
        
        PsychicDrain.onTick(PsychicPoint.stackController(1))
        PsychicGroundDamage.onBefore(PsychicPoint.stackController(1))
        PsycoBreak.onBefore(PsychicPoint.stackController(1))
        
        UltimateBPM.onTick(PsychicPoint.stackController(-1))
        
        UltimatePsychic.onConstraint(core.ConstraintElement("5포인트", PsychicPoint, partial(PsychicPoint.judge_ultimate,5)))
        UltimatePsychic.onBefore(PsychicPoint.stackController(-5))
        
        PsychicGrab2.onBefore(PsychicPoint.stackController(2))

        EverPsychic.onBefore(PsychicPoint.stackController(30 + 10))
        EverPsychic.onAfter(PsychicPoint.stackController(-2)) # 싸이킥 무브 캔슬비용 2pp

        PsychicOverSummon.onTick(PsychicPoint.stackController(1))
        
        PsychicTornado.onConstraint(core.ConstraintElement("15포인트", PsychicPoint, partial(PsychicPoint.judge_ultimate,15)))
        PsychicTornado.onBefore(PsychicPoint.stackController(-15))

        UltimateMovingMatter.onConstraint(core.ConstraintElement("10포인트", PsychicPoint, partial(PsychicPoint.judge_ultimate,10)))
        UltimateMovingMatter.onBefore(PsychicPoint.stackController(-10))
        
        UltimatePsychicBullet.onConstraint(core.ConstraintElement("2포인트", PsychicPoint, partial(PsychicPoint.judge_ultimate,2)))
        UltimatePsychicBullet.onBefore(PsychicPoint.stackController(-3))
        
        UltimatePsychicBulletBlackhole.onTick(PsychicPoint.stackController(1))
        
        PsychicCharging.onConstraint(core.ConstraintElement("5포인트 이하", PsychicPoint, partial(PsychicPoint.judge,5,-1)))
        PsychicCharging.onAfter(PsychicPoint.chargeController())

        UltimateTrain.onConstraint(core.ConstraintElement("15포인트", PsychicPoint, partial(PsychicPoint.judge_ultimate,15)))
        UltimateTrain.onBefore(PsychicPoint.stackController(-15))

        LawOfGravity.onConstraint(core.ConstraintElement("5포인트", PsychicPoint, partial(PsychicPoint.judge_bpm_safe,5)))
        LawOfGravity.onBefore(PsychicPoint.stackController(-5))

        # Overload Mana
        overload_mana_builder = magicians.OverloadManaBuilder(vEhc, 1, 1)
        for sk in [PsychicTornado, PsychicTornadoFinal_1, PsychicTornadoFinal_2, UltimateMovingMatter, UltimateMovingMatterFinal,
                    PsychicGrab2, UltimatePsychic, Ultimate_Material, PsychicDrain, PsychicGroundDamage, PsycoBreakDamage,
                    EverPsychic, EverPsychicFinal, UltimatePsychicBullet, UltimatePsychicBulletBlackhole, UltimateTrain]:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()

        # Scheduling
        TrainConstraint = core.ConstraintElement(
            "트레인 깔려있으면",
            UltimateTrain,
            partial(UltimateTrain.is_time_left, 3000, 1),  # 3000 -> 0으로 조절하면 트레인 비중 낮은 딜사이클이 됨
        )
        if DEALCYCLE == "material":
            UltimatePsychic.protect_from_running()
            Ultimate_Material.onConstraint(TrainConstraint)
        elif DEALCYCLE == "shot":
            Ultimate_Material.onConstraint(core.ConstraintElement("오버", PsychicOver, PsychicOver.is_active))
            Ultimate_Material.onConstraint(TrainConstraint)
            UltimatePsychic.onConstraint(TrainConstraint)
        else:
            raise ValueError(DEALCYCLE)
        
        return (
            PsychicGrab2,
            [
                PsychicPoint,
                globalSkill.maple_heros(chtr.level, name = "이계의 용사", combat_level=self.combat),
                globalSkill.useful_sharp_eyes(),
                globalSkill.useful_combat_orders(),
                globalSkill.useful_wind_booster(),
                OverloadMana,
                Booster,
                PsychicShield,
                PsychicGround,
                PsycoBreak,
                PsychicCharging,
                AnotherGoddessBuff,
                PsychicOver,
                globalSkill.soul_contract()
            ]
            + [
                AnotherHeal,
                PsychicTornadoFinal_1,
                PsychicTornadoFinal_2,
                LawOfGravityFinal,
              ]  # reserved task, use as early as possible
            + [
                PsychicDrain,
                UltimateBPM,
                PsychicTornado,
                UltimateTrain,
                UltimateMovingMatter,
            ]
            + [
                PsychicForce3,
                EverPsychic,
                Ultimate_Material,
                LawOfGravity,
                UltimatePsychic,
                MirrorBreak
            ]
            + [
                UltimatePsychicBuff,
                PsychicOverSummon,
                PsychicForce3Dot,
                AnotherVoid,
                LawOfGravityDebuff,
                MirrorSpider
            ]  # Not used from scheduler
            + [PsychicGrab2]
        )