from .. import jobs as maplejobs
from ..kernel.core import DirectVBuilder
from ..kernel import core
from ..character.characterKernel import GearedCharacter as GChar
from dpmModule.kernel import policy
from dpmModule.execution import rules


def getpassiveInformation(enjob: str):
    gen = maplejobs.getGenerator(maplejobs.getKoJobName(enjob)).JobGenerator()
    template = GChar(gen)

    # 1레벨
    no_enhancer = DirectVBuilder([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    graph_bare = gen.package_bare(template, v_builder=no_enhancer)
    vEhc = no_enhancer.build_enhancer(template, gen)

    scheduler = policy.AdvancedGraphScheduler(
        graph_bare,
        policy.TypebaseFetchingPolicy(priority_list=[
            core.BuffSkillWrapper,
            core.SummonSkillWrapper,
            core.DamageSkillWrapper
        ]),
        [rules.UniquenessRule()])
    scheduler.initialize(0)
    buffs = [{'name': wrp.skill.name, 'stat': wrp.skill.static_character_modifier.as_dict()} for wrp, tf in
             scheduler._buffMdfCalcZip if (not tf)]

    gen.build_passive_skill_list(vEhc, template)
    passive_skill_direct = [info.as_dict() for info in gen.get_passive_skill_list(vEhc, template)]

    passive_skill_indirect = [info.as_dict() for info in gen.get_not_implied_skill_list(vEhc, template)]

    return {"passive_direct": passive_skill_direct, "passive_indirect": passive_skill_indirect, "static_buff": buffs}


def extract_skill_info(enjob: str):
    gen = maplejobs.getGenerator(maplejobs.getKoJobName(enjob)).JobGenerator()
    template = GChar(gen)

    # 1레벨
    no_enhancer = DirectVBuilder([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    graph_bare = gen.package_bare(template, v_builder=no_enhancer)

    # 25레벨
    gen = maplejobs.getGenerator(maplejobs.getKoJobName(enjob)).JobGenerator()
    graph_full = gen.package_bare(template, useFullCore=True)

    vEhc = no_enhancer.build_enhancer(template, gen)
    info_vskill = vEhc.get_priority()

    info_bare = graph_bare.get_detailed_skill_info(expl_level=0)
    info_full = graph_full.get_detailed_skill_info(expl_level=0)

    return {"bare": info_bare, "full": info_full, "vskill": info_vskill}


def extract_every_skill_info(enjob: str):
    print(enjob)
    gen = maplejobs.getGenerator(maplejobs.getKoJobName(enjob)).JobGenerator()
    template = GChar(gen)

    # 1 levels | 1레벨
    no_enhancer = DirectVBuilder([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                 [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    graph_bare = gen.package_bare(template, v_builder=no_enhancer)

    # 25 levels | 25레벨
    gen = maplejobs.getGenerator(maplejobs.getKoJobName(enjob)).JobGenerator()
    graph_full = gen.package_bare(template, v_builder=no_enhancer)

    vEhc = no_enhancer.build_enhancer(template, gen)
    gen.build(vEhc, template)
    info_vskill = vEhc.get_priority()

    info_bare = graph_bare.get_whole_skill_info(expl_level=0)
    info_full = graph_full.get_whole_skill_info(expl_level=0)

    gen.build_passive_skill_list(vEhc, template)
    passive_skill_direct = [
        [info.name, "\n".join([val[0] + ":" + "".join([str(x) for x in val[1:]]) for val in info.abstract_log_list()])]
        for info in gen.get_passive_skill_list(vEhc, template)]
    passive_skill_indirect = [
        [info.name, "\n".join([val[0] + ":" + "".join([str(x) for x in val[1:]]) for val in info.abstract_log_list()])]
        for info in gen.get_not_implied_skill_list(vEhc, template)]

    return {"bare": info_bare, "full": info_full, "vskill": info_vskill, "passive_direct": passive_skill_direct,
            "passive_indirect": passive_skill_indirect}
