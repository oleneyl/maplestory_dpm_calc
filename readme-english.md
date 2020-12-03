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
  dpmModule is the library to calculate about the damage(expected deal, DPM, optimized potentials) easily.
  Our damage simulation supports 41 classes exist in KMS, except Xenon and Demon Avenger.


Document
--------------
  - [tutorial](dpmModule/kernel/readme.md)
  - [mechanism](dpmModule/kernel/track.md)
  - [Benchmark](dpmModule/benchmark_log.md)
  - [class design](dpmModule/jobs/readme.md)
  - [character design, item design, character settings](dpmModule/character/readme.md)

Dev Tool
--------------
https://github.com/oleneyl/maplestory_dpm_calc_web_tool

- Slack Channel
  - https://github.com/oleneyl/maplestory_dpm_calc/issues/98

Example
-----------------------

  - CLI Usage

    ```bash
    python3 test.py --job `class name` --ulevel `union level` --level `character level`
    ```

  - Basic Python Usage

    ```python
    import dpmModule
    from dpmModule.util.dpmgenerator import IndividualDPMGenerator
    import dpmModule.character.characterTemplateHigh as template
    gen = IndividualDPMGenerator('나이트로드', template.getU6000CharacterTemplate)
    print(gen.get_dpm(ulevel = 6000))
    
    # Result
    406674153728.34534  #Can be different by version
    ```

  - Advanced Usage

    - Union level 7000, character level 240, 8000-tier spec, two potential lines in weapons, 240 seconds

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

      - `job` : Korean name of classes. Defined in `dpmModule.jobs.jobMap` Most of them are common names. **`test.py` only accepts Korean class name as `--job` argument!**

        - Avaliable classes :

| Korean name | English name |
| - | - |
|`아크메이지불/독` | `Arch Mage (F,P)` |
`아크메이지썬/콜` | `Arch Mage (I,L)` |
`비숍` | `Bishop` |
`히어로` | `Hero` |
`팔라딘` | `Paladin` |
`신궁` | `Marksman` |
`윈드브레이커` | `Wind Archer` |
`소울마스터` | `Dawn Warrior` |
`루미너스` | `Luminous` |
`배틀메이지` | `Battle Mage` |
`메카닉` | `Mechanic` |
`메르세데스` | `Mercedes` |
`데몬슬레이어` | `Demon Slayer` |
`다크나이트` | `Dark Knight` |
`와일드헌터` | `Wind Hunter` |
`플레임위자드` | `Blaze Wizard` |
`섀도어` | `Shadower` |
`캐논슈터` | `Cannoneer` |
`미하일` | `Mihile` |
`듀얼블레이드` | `Dual Blade` |
`카이저` | `Kaiser` |
`캡틴` | `Corsair` |
`엔젤릭버스터` | `Angelic Buster` |
`팬텀` | `Phantom` |
`나이트로드` | `Night Lord` |
`은월` | `Shade` |
`바이퍼` | `Buccaneer` |
`나이트워커` | `Night Walker` |
`스트라이커` | `Thunder Breaker` |
`에반` | `Evan` |
`보우마스터` | `Bowmaster` |
`제로` | `Zero` |
`키네시스` | `Kinesis` |
`일리움` | `Illium` |
`패스파인더` | `Pathfinder` |
`카데나` | `Cadena` |
`아크` | `Ark` |
`블래스터` | `Blaster` |
`아란` | `Aran` |
`아델` | `Adele` |
`호영` | `Hoyoung` |

      - `template` : Defines the status of the character. You may use one of the templates in `dpmModule.jobs.characterTemplateHigh`. The appropriate templates are defined for each spec tier.

    - `generator.getDpm`
        
      - `vEhc` : (Not supported yet)
      - `ulevel` : Union level. The larger the value is given, the more stats you get from the union. default=6000
      - `weaponstat` : The potentials of weapon, subweapon and emblem. Given in the form of `[grade, amount]`. Please see the examples below. default = `[4,9]`

        - `[3,6]` : Unique(3), six valid lines(6)
        - `[4,7]` : Legendary(4), sevel valid lines(7)

      - `level` : Character level. default=230
      - `printFlag` : If it's True, print the simulation log. default=False

  - Calculate using Low API

    ```python
    import dpmModule.jobs.nightlord as nightlord
    from dpmModule.kernel import core
    from dpmModule.kernel import policy
    from dpmModule.execution import rules
    from dpmModule.character.characterTemplate import get_template_generator

    character = get_template_generator('high_standard').get_template(6000) # Set with a union 6000 character with high spec
    generator = nightlord.JobGenerator()
    v_builder = core.NjbStyleVBuilder(skill_core_level=25, each_enhanced_amount=17) # V core level: 25, 3 stacks enhancement

    graph = generator.package(character, v_builder)

    sche = policy.AdvancedGraphScheduler(graph,
        policy.TypebaseFetchingPolicy(priority_list = [
            core.BuffSkillWrapper,
            core.SummonSkillWrapper,
            core.DamageSkillWrapper
        ]), 
        [rules.UniquenessRule()]) # Use skills in the following order: Buff, Summon, Damage

    analytics = core.Analytics(printFlag=False) # Minimal log output
    control = core.Simulator(sche, character, analytics) 
    control.start_simulation(180 * 1000) # 3 minutes simulation
    
    dpm = control.getDPM() # print dpm
    print(dpm)
    ```

    - See dpmModule's readme for more detailed explanations.



