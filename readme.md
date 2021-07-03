dpmModule
========================


  - requirements
    - Python >= 3.7
    - argparse

  - Demo
    
    - https://maplestats.com

  - download
    ```bash
    pip install dpmModule
    ```
    
    ```bash
    git clone https://github.com/oleneyl/maplestory_dpm_calc
    ```

About 
------------
  dpmModule은 메이플스토리에서 데미지와 관련된 계산(기댓값, DPM, 최적잠재 등) 을 쉽게 계산하기
  위한 라이브러리입니다. 전체 43개 직업군중 데벤, 제논을 제외한 41개 직업군의 데미지 시뮬레이션을 지원합니다.

Introduction
--------------
- [설명 동영상](https://www.youtube.com/watch?v=Jwbmalo1XJQ)

Document
--------------
  - [튜토리얼tutorial](dpmModule/kernel/readme.md)
  - [작동 원리mechanism](dpmModule/kernel/track.md)
  - [Benchmark](dpmModule/benchmark_log.md)
  - [직업 구현](dpmModule/jobs/readme.md)
  - [캐릭터 구현, 아이템 구현, 캐릭터 설정](dpmModule/character/readme.md)

Dev Tool
--------------
https://github.com/oleneyl/maplestory_dpm_calc_web_tool

- Slack Channel
  - https://github.com/oleneyl/maplestory_dpm_calc/issues/98

Example
-----------------------

  - CLI Usage

    ```bash
    python3 test.py --job [직업명] --ulevel [유니온 레벨]
    ```

  - Basic Python Usage

    ```python
    import dpmModule
    from dpmModule.util.dpmgenerator import IndividualDPMGenerator
    gen = IndividualDPMGenerator('나이트로드')
    gen.set_runtime(1800 * 1000)
    ulevel = 8000
    print(gen.get_dpm(spec_name=str(ulevel), ulevel=ulevel))
    
    # Result
    806902750018.9082  #Can be different by version
    ```

  - Parser Config

    - `dpmModule.util.dpmgenerator.IndividualDPMGenerator`

      - `job` : 직업군의 한글명칭입니다. `dpmModule.jobs.jobMap` 에 정의되어 있습니다. 대부분은 통상한글명칭입니다.

        - 지원되는 직업명 : `아크메이지불/독`
`아크메이지썬/콜`
`비숍`
`히어로`
`팔라딘`
`신궁`
`윈드브레이커`
`소울마스터`
`루미너스`
`배틀메이지`
`메카닉`
`메르세데스`
`데몬슬레이어`
`다크나이트`
`와일드헌터`
`플레임위자드`
`섀도어`
`캐논슈터`
`미하일`
`듀얼블레이드`
`카이저`
`캡틴`
`엔젤릭버스터`
`팬텀`
`나이트로드`
`은월`
`바이퍼`
`나이트워커`
`스트라이커`
`에반`
`보우마스터`
`제로`
`키네시스`
`일리움`
`패스파인더`
`카데나`
`아크`
`블래스터`
`아란`
`아델`
`호영`

      - `template` : 사용할 캐릭터의 상태를 정의합니다. `dpmModule.jobs.characterTemplateHigh` 내의 template중 하나를 사용하면 됩니다. 스펙구간별로 적절한 template이 정의되어 있습니다.

    - `generator.get_dpm`        
      - `ulevel` : 유니온 레벨입니다. 큰 값이 주어질수록 유니온으로부터 더 많은 스텟을 얻습니다.
      - `printFlag` : True이면 시뮬레이션 로그를 출력합니다. default=False
      - `statistics`: True이면 통계치를 제공합니다. default=False
      - `spec_name`: 캐릭터 세팅에 사용할 아이템 스펙 템플릿입니다. `dpmModule/character/configs` 를 참고하세요.
      - `cdr`: 적용할 쿨타임 감소 (초) 입니다.

  - Low API를 사용하여 계산하기

    ```python
    import dpmModule.jobs.nightlord as nightlord
    from dpmModule.kernel import core
    from dpmModule.kernel import policy
    from dpmModule.execution import rules
    from dpmModule.character.characterTemplate import TemplateGenerator
    from dpmModule.status.ability import Ability_grade
    from dpmModule.execution import rules

    gen = nightlord.JobGenerator()
    target, weapon_stat = TemplateGenerator().get_template_and_weapon_stat(gen=gen, spec_name='6000')
    # 유니온 6천급 캐릭터 세팅

    v_builder = core.NjbStyleVBuilder(skill_core_level=25, each_enhanced_amount=17) #스킬코어 25렙, 3중코어코강

    graph = gen.package(
      target, v_builder, ulevel=6000, weaponstat=weapon_stat, ability_grade=Ability_grade(4, 1),
      farm=False, options={}
    ) # 유니온 레벨 6천, 어빌은 레전-에픽, 농장 없음

    sche = policy.AdvancedGraphScheduler(graph,
        policy.TypebaseFetchingPolicy(priority_list = [
            core.BuffSkillWrapper,
            core.SummonSkillWrapper,
            core.DamageSkillWrapper
        ]), 
        [rules.UniquenessRule()] + gen.get_predefined_rules(rules.RuleSet.BASE)
      ) # 버프, 소환수, 쿨타임 스킬 순으로 사용. 단, BASE predefined rule이 있으면 사용

    analytics = core.Analytics(printFlag=False) # 로그를 최소한으로 출력
    control = core.Simulator(sche, target, analytics) 
    control.start_simulation(180 * 1000) # 3분간 시뮬레이션 진행

    dpm = analytics.getDPM() # dpm 출력
    print(dpm)
    ```

    - 자세한 사용 방법은 dpmModule의 readme를 참조하십시오.
