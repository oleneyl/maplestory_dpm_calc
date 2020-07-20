from .. import jobs as maplejobs
from ..character.characterKernel import ItemedCharacter as ichar
from ..character.characterKernel import Union, HyperStat
from ..kernel import core
from dpmModule.kernel import policy
from dpmModule.execution import rules
from ..item import Absolab
MDF = core.CharacterModifier

'''
Optimizer

parameter : by POST(To many parameters)
"spec_main"
{ 
    "job", "att", "stat_main", "stat_sub", "buff_rem", "summon_rem", "cooltime_reduce"
}
"spec_sub"
{
    "pdamage", "boss_pdamage", "pdamage_indep", "armor_ignore", "crit", "crit_damage", 
}
"hyper"
{
    "boss_pdamage", "pdamage", "armor_ignore", "crit", "crit_damage", "level"
}
"union"
{
    "boss_pdamage", "armor_ignore", "crit", "crit_damage", "buffrem", total_slot"
}

연산 후 리턴하는 결과물

dpm : DPM
hyper : 하이퍼
union : 유니온

추후 추가 예정. 일단은 MVP부터 생성 필요.
'''

def get_optimal_hyper_from_bare(spec, level):
    ref = spec.copy()
    newHyper = HyperStat.get_hyper_object(ref, level)
    return newHyper

def get_optimal_hyper_union(spec, job, otherspec, hyper, union):
    '''최적화된 하이퍼 / 유니온 값을 계산해서 리턴합니다.
    입력값 : CharacterModifier들
    출력값 : [hyper, union]
    '''
    ref = spec.copy()
    ref = ref - hyper.mdf
    ref = ref - union.mdf
    
    buffremFlag = (union.buff_rem > 0)
    
    newHyper = HyperStat.get_hyper_object(ref, hyper.level)
    ref += newHyper.mdf
    
    newUnion = Union.get_union_object(ref, -1, buffrem = buffremFlag, slot = union.slots)
    
    return {"hyper" : newHyper, "union" : newUnion }


def get_instant_dpm(spec, job, otherspec, useFullCore = True, koJobFlag = False, v_builder = None, seed_rings = False, weaponAtt = None):
    '''주어진 값과 직업값으로부터 dpm을 계산해서 리턴합니다.
    입력값 : CharacterModifier, job, otherspec
    출력값 : float(DPM)
    '''
    
    if koJobFlag:
        koJob = job
    else:
        koJob = maplejobs.getKoJobName(job)
    if koJob is not None:
        try:
            gen = maplejobs.getGenerator(koJob).JobGenerator()
        except Exception as e:
            raise TypeError("Unsupported job type: " + str(job))
    else:
        raise TypeError("Unsupported job type(en): " + str(job))
        
    template = ichar()
    if otherspec is not None:
        if "buffrem" in otherspec:
            template.buff_rem = otherspec["buffrem"]
        if "summonrem" in otherspec:
            template.summonRemain = otherspec["summonrem"]
        if "cooltimereduce" in otherspec:
            template.cooltimeReduce = otherspec["cooltimereduce"]    
    
    template.apply_modifiers([spec])
    graph = gen.package_bare(template, useFullCore = False, v_builder = v_builder)
    sche = policy.AdvancedGraphScheduler(graph,
        policy.TypebaseFetchingPolicy(priority_list = [
            core.BuffSkillWrapper,
            core.SummonSkillWrapper,
            core.DamageSkillWrapper
        ]), 
        [rules.UniquenessRule()] + gen.get_predefined_rules(rules.RuleSet.BASE)) #가져온 그래프를 토대로 스케줄러를 생성합니다.
    analytics = core.Analytics(printFlag=True)  #데이터를 분석할 분석기를 생성합니다.
    control = core.Simulator(sche, template, analytics) #시뮬레이터에 스케줄러, 캐릭터, 애널리틱을 연결하고 생성합니다.
    control.start_simulation(240*1000)
    
    if weaponAtt is None:
        weaponAtt = Absolab.WeaponFactory.getWeapon(maplejobs.weaponList[koJob], star = 17, elist = [0,0,0,9] ).att

    if seed_rings:
        seed_ring_specs = [
            {"name" : "리스크테이커", "effect" : [ [12000 + 6000*i, MDF(patt = 20 + 10*i)] for i in range(4) ]},
            {"name" : "리스트레인트", "effect" : [ [9000 + 2000*i, MDF(patt = 25 + 25*i)] for i in range(4) ]},
            {"name" : "웨폰퍼프", "effect" : [ [9000 + 2000*i, MDF(stat_main = weaponAtt * (i+1))] for i in range(4) ]}, 
            {"name" : "크리데미지", "effect" : [ [9000 + 2000*i, MDF(crit_damage = 7+ 7*i)] for i in range(4) ]}
        ]
        
        return_ring_dpms = []
        
        for spec in seed_ring_specs:
            enhancement = []
            
            enhancement = [control.analytics.deduce_increment_of_temporal_modifier(effect[0], effect[1])
                                for effect in spec["effect"] ]
            return_ring_dpms.append({"name" : spec["name"], "effect" : enhancement})
    
    return_json_object = {"dpm" : control.getDPM(), "loss" : control.get_unrestricted_DPM() - control.getDPM(), "share" : analytics.skill_share()}
    
    if seed_rings:
        return_json_object["seedring"] = return_ring_dpms
    
    return return_json_object
