dpmModule
========================


  - requirements
    - Python >= 3.7
    - argparse

  - Demo
    
    - https://maplestats.com

  - install
    ```bash
    pip install dpmModule
    ```
    
  - install from github
    ```bash
    git clone https://github.com/oleneyl/maplestory_dpm_calc
    cd maplestory_dpm_calc/
    python3 setup.py [develop, install]
    ```

  

About 
------------
  
  dpmModule is a library for easily calculating damage-related calculations (expected value, DPM, optimal potential, etc.) in MapleStory. 
  It supports damage simulation of 41 occupation groups excluding Deven and Xenon out of a total of 43 occupation groups.

  dpmModule은 메이플스토리에서 데미지와 관련된 계산(기댓값, DPM, 최적잠재 등) 을 쉽게 계산하기
  위한 라이브러리입니다. 전체 43개 직업군중 데벤, 제논을 제외한 41개 직업군의 데미지 시뮬레이션을 지원합니다.


Document
--------------
  - [Tutorial | 튜토리얼tutorial](dpmModule/kernel/readme.md)
  - [Principle of Operation | 작동 원리mechanism](dpmModule/kernel/track.md)
  - [Benchmark](dpmModule/benchmark_log.md)
  - [Job implementation | 직업 구현](dpmModule/jobs/readme.md)
  - [Character implementation, item implementation, character setting | 캐릭터 구현, 아이템 구현, 캐릭터 설정](dpmModule/character/readme.md)

Dev Tool
--------------
https://github.com/oleneyl/maplestory_dpm_calc_web_tool

- Slack Channel
  - https://github.com/oleneyl/maplestory_dpm_calc/issues/98

Example
-----------------------

  - CLI Usage

    ```bash
    python3 test.py --job [Job name | 직업명] --ulevel [Legion level | 유니온 레벨] --level [Character level | 캐릭터 레벨]
    ```

  - Basic Python Usage

    ```python
    import dpmModule
    from dpmModule.util.dpmgenerator import IndividualDPMGenerator
    import dpmModule.character.characterTemplateHigh as template
    gen = IndividualDPMGenerator('나이트로드', template.getU6000CharacterTemplate)
    # gen = IndividualDPMGenerator('nightlord', template.getU6000CharacterTemplate)
    print(gen.get_dpm(ulevel = 6000))
    
    # Result
    806902750018.9082  #Can be different by version
    ```

  - Advanced Usage

    - Union 7,000, level 240, Union 8,000 level specification, 2 lines of Mubom region, 240 seconds. 유니온 7천, 240레벨, 유니온 8천급 스펙, 무보엠 레전2줄, 240초.

      ```python
      import dpmModule
      from dpmModule.util.dpmgenerator import IndividualDPMGenerator
      import dpmModule.character.characterTemplateHigh as template
      gen = IndividualDPMGenerator('나이트로드', template.getU8000CharacterTemplate)
       # gen = IndividualDPMGenerator('nightlord', template.getU8000CharacterTemplate)
      gen.set_runtime(240 * 1000)
      print(gen.get_dpm(ulevel = 7000, level = 240, weaponstat = [4,6]))
      ```

  - Parser Config

    - `dpmModule.util.dpmgenerator.IndividualDPMGenerator`

      - `job` : It is the Korean name of the job. It is defined in `dpmModule.jobs.jobMap`. Most are usually Korean names. 직업군의 한글명칭입니다. `dpmModule.jobs.jobMap` 에 정의되어 있습니다. 대부분은 통상한글명칭입니다.

        - Supported job name | 지원되는 직업명 : `아크메이지불/독`
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
`hero`
`paladin`
`darknight`
`archmageFP`
`archmageIL`
`bishop`
`bowmaster`
`marksman`
`pathfinder`
`nightlord`
`shadower`
`dualblade`
`buccaneer`
`corsair`
`cannoneer`
`dawnwarrior`
`blazewizard`
`windarcher`
`nightwalker`
`thunderbreaker`
`mihile`
`aran`
`evan`
`mercedes`
`phantom`
`shade`
`luminous`
`demonslayer`
`demonavenger`
`battlemage`
`wildhunter`
`mechanic`
`xenon`
`blaster`
`kaiser`
`kain`
`cadena`
`angelicbuster`
`zero`
`kinesis`
`adele`
`ilium`
`ark`
`hoyoung`

      - `template` : Defines the state of the character to be used. You can use one of the templates in `dpmModule.jobs.characterTemplateHigh`. An appropriate template is defined for each specification section. 
      사용할 캐릭터의 상태를 정의합니다. `dpmModule.jobs.characterTemplateHigh` 내의 template중 하나를 사용하면 됩니다. 스펙구간별로 적절한 template이 정의되어 있습니다.

    - `generator.getDpm`
        
      - `vEhc` : (Not supported yet)
      - `ulevel` : Legion level. The larger value given, the more stats you get from the legion. 유니온 레벨입니다. 큰 값이 주어질수록 유니온으로부터 더 많은 스텟을 얻습니다. default=6000
      - `weaponstat` : This is the potential of WSE. It is given as `[grade, amount]`. See the example below. 무보엠의 잠재능력입니다. `[grade, amount]`로 주어집니다. 아래 예시를 참고하세요. default = `[4,9]`

        - `[3,6]` : Unique (3) effective 6 lines (6) | 유니크(3) 무보엠 합쳐서 유효6줄(6)
        - `[4,7]` : Legendary (4) effective 7 lines (7) | 레전드리(4) 무보엠 합쳐서 유효7줄(7)

      - `level` : Character level. 캐릭터 레벨입니다. default=230
      - `printFlag` : If true, output the simulation log. True이면 시뮬레이션 로그를 출력합니다. default=False

  - Computing using the Low API. Low API를 사용하여 계산하기

    ```python
    import dpmModule.jobs.nightlord as nightlord
    from dpmModule.kernel import core
    from dpmModule.kernel import policy
    from dpmModule.execution import rules
    from dpmModule.character.characterTemplate import get_template_generator

    character = get_template_generator('high_standard').get_template(6000) # High-spec standard Union 6,000 characters set. 고스펙 기준 유니온 6천인 캐릭터 설정.
    generator = nightlord.JobGenerator()
    v_builder = core.NjbStyleVBuilder(skill_core_level=25, each_enhanced_amount=17) # Skill Core Level 25, Triple Core Kogang. 스킬코어 25렙, 3중코어코강.

    graph = generator.package(character, v_builder)

    sche = policy.AdvancedGraphScheduler(graph,
        policy.TypebaseFetchingPolicy(priority_list = [
            core.BuffSkillWrapper,
            core.SummonSkillWrapper,
            core.DamageSkillWrapper
        ]), 
        [rules.UniquenessRule()]) # Use in order of buff, pet, and cooldown skill. 버프, 소환수, 쿨타임 스킬 순으로 사용.

    analytics = core.Analytics(printFlag=False) # Minimal log output. 로그를 최소한으로 출력.
    control = core.Simulator(sche, character, analytics) 
    control.start_simulation(180 * 1000) # 3 minutes simulation. 3분간 시뮬레이션 진행.
    
    dpm = control.getDPM() # dpm output. dpm 출력.
    print(dpm)
    ```

    - Please refer to dpmModule's readme for detailed usage instructions. 자세한 사용 방법은 dpmModule의 readme를 참조하십시오.
