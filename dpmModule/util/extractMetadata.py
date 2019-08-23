from .. import jobs as maplejobs
from ..kernel.core import DirectVBuilder
from ..kernel import core
from ..character.characterKernel import ItemedCharacter as ichar
from dpmModule.kernel import policy
from dpmModule.execution import rules

def getpassiveInformation(enjob):
    gen = maplejobs.getGenerator(maplejobs.getKoJobName(enjob)).JobGenerator()
    template = ichar()
    
    #1레벨
    no_enhancer = DirectVBuilder([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [1,1,1,1,1,1,1,1,1,1,1])
    graph_bare = gen.package_bare(template, v_builder = no_enhancer)

    scheduler = policy.AdvancedGraphScheduler(graph_bare,
            policy.TypebaseFetchingPolicy(priority_list = [
                core.BuffSkillWrapper,
                core.SummonSkillWrapper,
                core.DamageSkillWrapper
            ]), 
            [rules.UniquenessRule()])
    scheduler.initialize(0)
    buffs = [{'name' : wrp.skill.name, 'stat' : wrp.skill.static_character_modifier.as_dict(js_flag = True)} for wrp,tf in scheduler._buffMdfCalcZip if (not tf)]

    gen.build_passive_skill_list()
    passive_skill_direct = [info.as_dict(js_flag = True) for info in gen.get_passive_skill_list()]
    
    passive_skill_indirect = [info.as_dict(js_flag = True) for info in gen.get_not_implied_skill_list()]
    
    return {"passive_direct" : passive_skill_direct, "passive_indirect" : passive_skill_indirect, "static_buff" : buffs}

def extractSkillInfo(enjob):
    gen = maplejobs.getGenerator(maplejobs.getKoJobName(enjob)).JobGenerator()
    template = ichar()
    
    #1레벨
    no_enhancer = DirectVBuilder([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [1,1,1,1,1,1,1,1,1,1,1])
    graph_bare = gen.package_bare(template, v_builder = no_enhancer)

    #25레벨
    gen = maplejobs.getGenerator(maplejobs.getKoJobName(enjob)).JobGenerator()
    graph_full = gen.package_bare(template, useFullCore = True)
    
    info_vskill = gen.vEhc.get_priority()
    
    
    info_bare = graph_bare.get_detailed_skill_info(expl_level = 0)
    info_full = graph_full.get_detailed_skill_info(expl_level = 0)
    
    return {"bare" : info_bare, "full" : info_full , "vskill" : info_vskill}

def extractEverySkillInfo(enjob):
    gen = maplejobs.getGenerator(maplejobs.getKoJobName(enjob)).JobGenerator()
    template = ichar()
    
    #1레벨
    no_enhancer = DirectVBuilder([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [1,1,1,1,1,1,1,1,1,1,1])
    graph_bare = gen.package_bare(template, v_builder = no_enhancer)
    
    #25레벨
    gen = maplejobs.getGenerator(maplejobs.getKoJobName(enjob)).JobGenerator()
    graph_full = gen.package_bare(template, useFullCore = True)
    
    info_vskill = gen.vEhc.get_priority()
    
    info_bare = graph_bare.get_whole_skill_info(expl_level = 0)
    info_full = graph_full.get_whole_skill_info(expl_level = 0)
    
    gen.build_passive_skill_list()
    passive_skill_direct = [[info.name, "\n".join([ val[0] + ":" + "".join([str(x) for x in val[1:]]) for val in info.abstract_log_list() ])] for info in gen.get_passive_skill_list()]
    
    passive_skill_indirect = [[info.name, "\n".join([ val[0] + ":" + "".join([str(x) for x in val[1:]]) for val in info.abstract_log_list() ])] for info in gen.get_not_implied_skill_list()]
    
    return {"bare" : info_bare, "full" : info_full , "vskill" : info_vskill, "passive_direct" : passive_skill_direct, "passive_indirect" : passive_skill_indirect}