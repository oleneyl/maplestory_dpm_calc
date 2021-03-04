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

Introduction
--------------
- [Explanation Video](https://www.youtube.com/watch?v=Jwbmalo1XJQ)

Document
--------------
  - [Tutorial](dpmModule/kernel/readme-en.md)
  - [Principle of Operation](dpmModule/kernel/track-en.md)
  - [Benchmark](dpmModule/benchmark_log-en.md)
  - [Job implementation](dpmModule/jobs/readme-en.md)
  - [Character implementation, item implementation, character setting](dpmModule/character/readme-en.md)

Dev Tool
--------------
https://github.com/oleneyl/maplestory_dpm_calc_web_tool

- Slack Channel
  - https://github.com/oleneyl/maplestory_dpm_calc/issues/98

Example
-----------------------

  - CLI Usage

    ```bash
    python3 test.py --job [Job name] --ulevel [Legion level] --level [Character level]
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

    - Union 7,000, level 240, Union 8,000 level specification, 2 lines of Mubom region, 240 seconds.

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

      - `job` : It is the Korean name of the job if running in Korean, else English. It is defined in `dpmModule.jobs.jobMap`. Most are usually Korean names. 

        - Supported job name running in Korean: `아크메이지불/독`
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
        - Supported job name running in English:
`Hero`
`Paladin`
`Dark Knight`
`Archmage F/P`
`Archmage I/L`
`Bishop`
`Bowmaster`
`Marksman`
`Pathfinder`
`Nightlord`
`Shadower`
`Dual Blade`
`Buccaneer`
`Corsair`
`Cannoneer`
`Dawn Warrior`
`Blaze Wizard`
`Wind Archer`
`Night Walker`
`Thunder Breaker`
`Mihile`
`Aran`
`Evan`
`Mercedes`
`Phantom`
`Shade`
`Luminous`
`Demon Slayer`
`Demon Avenger`
`Battle Mage`
`Wild Hunter`
`Mechanic`
`Xenon`
`Blaster`
`Kaiser`
`Kain`
`Cadena`
`Angelicbuster`
`Zero`
`Kinesis`
`Adele`
`Ilium`
`Ark`
`Hoyoung`

      - `template` : Defines the state of the character to be used. You can use one of the templates in `dpmModule.jobs.characterTemplateHigh`. An appropriate template is defined for each specification section.

    - `generator.getDpm`
        
      - `vEhc` : (Not supported yet)
      - `ulevel` : Legion level. The larger value given, the more stats you get from the legion. 
      - `weaponstat` : This is the potential of WSE. It is given as `[grade, amount]`. See the example below. 

        - `[3,6]` : Unique (3) effective 6 lines (6)
        - `[4,7]` : Legendary (4) effective 7 lines (7)

      - `level` : Character level. default=230
      - `printFlag` : If true, output the simulation log. 

  - Computing using the Low API. 

    ```python
    import dpmModule.jobs.nightlord as nightlord
    from dpmModule.kernel import core
    from dpmModule.kernel import policy
    from dpmModule.execution import rules
    from dpmModule.character.characterTemplate import get_template_generator

    character = get_template_generator('high_standard').get_template(6000) # High-spec standard Union 6,000 characters set. 
    generator = nightlord.JobGenerator()
    v_builder = core.NjbStyleVBuilder(skill_core_level=25, each_enhanced_amount=17) # Skill Core Level 25, Triple Core Kogang. 

    graph = generator.package(character, v_builder)

    sche = policy.AdvancedGraphScheduler(graph,
        policy.TypebaseFetchingPolicy(priority_list = [
            core.BuffSkillWrapper,
            core.SummonSkillWrapper,
            core.DamageSkillWrapper
        ]), 
        [rules.UniquenessRule()]) # Use in order of buff, pet, and cooldown skill. 

    analytics = core.Analytics(printFlag=False) # Minimal log output. 
    control = core.Simulator(sche, character, analytics) 
    control.start_simulation(180 * 1000) # 3 minutes simulation. 
    
    dpm = control.getDPM() # dpm output.
    print(dpm)
    ```

    - Please refer to dpmModule's readme for detailed usage instructions. 
