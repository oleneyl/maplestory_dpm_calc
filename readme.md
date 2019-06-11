dpmModule
-------------------




- About
  
  dpmModule은 메이플스토리에서의 데미지 기댓값을 계산하기 위한 라이브러리입니다.
  전체 41개 직업군중 데벤, 제논, 아란을 제외한 38개 직업군의 데미지 시뮬레이션을 지원합니다.


Example
========================


  - Basic Usage

    ```python
    import dpmModule
    from dpmModule.util.dpmgenerator import IndividualDPMGenerator
    import dpmModule.character.characterTemplateHigh as template
    gen = IndividualDPMGenerator('나이트로드', template.getU6000CharacterTemplate)
    print(gen.get_dpm(ulevel = 6000))
    ```

  - Advanced Usage

    - 유니온 7천, 240레벨, 유니온 8천급 스펙, 무보엠 레전2줄, 240초

      ```python
      import dpmModule
      from dpmModule.util.dpmgenerator import IndividualDPMGenerator
      import dpmModule.character.characterTemplateHigh as template
      gen = IndividualDPMGenerator('나이트로드', template.getU8000CharacterTemplate)
      gen.set_runtime(240 * 1000)
      print(gen.get_dpm(ulevel = 7000, level = 240, weaponstat = [4,6]))
      ```

  - Parser Config

    - `dpmModule.util.dpmgenerator.IndividualDPMGenerator`

      - `job` : 직업군의 한글명칭입니다. `dpmModule.jobs.jobMap` 에 정의되어 있습니다. 대부분은 통상한글명칭입니다.
      - `template` : 사용할 캐릭터의 상태를 정의합니다. `dpmModule.jobs.characterTemplateHigh` 내의 template중 하나를 사용하면 됩니다. 스펙구간별로 적절한 template이 정의되어 있습니다.

    - `generator.getDpm`
        
      - `vEhc` : (Not supported yet)
      - `ulevel` : 유니온 레벨입니다. 큰 값이 주어질수록 유니온으로부터 더 많은 스텟을 얻습니다. default=6000
      - `weaponstat` : 무보엠의 잠재능력입니다. `[grade, amount]`로 주어집니다. 아래 예시를 참고하세요. default = `[4,9]`

        - `[3,6]` : 유니크(3) 무보엠 합쳐서 유효6줄(6)
        - `[4,7]` : 레전드리(4) 무보엠 합쳐서 유효7줄(7)

      - `level` : 캐릭터 레벨입니다. default=230
      - `printFlag` : True이면 시뮬레이션 로그를 출력합니다. default=False

  - Low API를 사용하여 계산하기

    ```python
    import dpmModule.jobs.nightlord as nightlord
    import dpmModule.character.characterTemplateHigh as template

    character = template()
    nightlord.JobGenerator().package()
    graph = gen.package(target, ulevel = ulevel, weaponstat = weaponstat, vEnhanceGenerateFlag = "njb_style")
    sche = policy.AdvancedGraphScheduler(graph,
        policy.TypebaseFetchingPolicy(priority_list = [
            core.BuffSkillWrapper,
            core.SummonSkillWrapper,
            core.DamageSkillWrapper
        ]), 
        [rules.UniquenessRule()]) #가져온 그래프를 토대로 스케줄러를 생성합니다.
    analytics = core.Analytics(printFlag=printFlag)  #데이터를 분석할 분석기를 생성합니다.
    control = core.Simulator(sche, target, analytics) #시뮬레이터에 스케줄러, 캐릭터, 분석기를 연결하고 생성합니다.
    control.start_simulation(180 * 1000)
    dpm = control.getDPM()
    ```


    
    
