
dpmModule :: Maplestory Damage simulation library
===================================================================


Structure
-------------

  - `kernel` : Abstract class, base class. 추상 클래스, 기본 클래스.
  - `character` : Character related code. Character creation, character stats, hyper stats, legion, card effect, link skills, pre-defined character loading. 캐릭터 관련 코드. 캐릭터 생성, 캐릭터 스텟, 하이퍼스텟, 유니온, 카드효과, 링크 효과, 사전-정의된 캐릭터 불러오기.
  - `item` : Item related code. Item creation, Empress / CRA / Absolab / Arcane / Guarantee / Jet Black / Meister set. 아이템 관련 코드. 아이템 생성, 여제/카루타/앱솔/아케인/보장/칠흑/마이스터셋.
  - `jobs` : Job-related code. Skill by job group, passive skill, number of cores, skill mechanisms, skill linkage order. 직업 관련 코드. 직업군별 스킬, 패시브 스킬, 코어 개수, 스킬 메커니즘, 스킬 연계 순서.
  - `execution` : Simulation rules. 시뮬레이션 규칙.
  - `status` : Ability. 어빌리티.
  - `util` : Utility code. Fast DPM calculation, optimal hyper/legion calculation. 편의용 코드. 빠른 DPM 계산, 최적 하이퍼/유니온 계산.
  - `test` : Test. 테스트.


Principle
---------------

The calculation process of dpmModule is as follows.
dpmModule의 계산 과정은 다음과 같습니다.

1. character creation | character 생성
  
  - Create a target character for the DPM calculation to be performed on. To create a character, you can use `dpmModule.character`. DPM 계산이 수행될 대상 캐릭터를 생성합니다. 캐릭터를 생성하기 위해서는 `dpmModule.character`를 활용할 수 있습니다.
  - There are two main ways to create a character. Character를 생성하는 방법은 크게 두 가지로 나뉩니다.

    - How to use `dpmModule.character.get_template_generator` function. `dpmModule.character.get_template_generator` 함수를 사용하는 방법.
    - How to create a `dpmModule.character.ItemedCharacter` instance and directly utilize a function to create a character. `dpmModule.character.ItemedCharacter` 인스턴스를 생성하고 직접 함수를 활용하여 character를 생성하는 방법.

  - Please read the README inside dpmModule.character for more details. 더 자세한 내용은 dpmModule.character 내부의 README를 읽어보십시오.

2. Create Skill Graph | Skill Graph 생성

  - Skill graph is a graph that defines the order and properties of the tasks the character will perform. On the graph: Skill graph란 캐릭터가 수행하게 될 일들의 순서와 속성이 정의된 그래프입니다. 그래프에는:
    
    - Skills you can use. 쓸 수 있는 스킬들.
    - Skills that are used after the skill is used. 해당 스킬을 사용했을 때 뒤따라 사용되는 스킬들.
    - Interactions between skills or cannot overlap each other. 서로 겹칠 수 없거나, 스킬 간의 상호작용들.

    All of these should be defined.이 모두 정의되어 있어야 합니다.

  - If you want to create a skill graph from scratch, read the README of `dpmModule.character.kernel`. 스킬 그래프를 scratch로부터 생성하고 싶다면 `dpmModule.character.kernel` 의 README를 읽어보십시오.

  - If you want to newly implement the skill mechanism of a certain job, after inheriting `dpmModule.character.characterKernel.JobGenerator`
    Rewrite empty functions. Read the README inside dpmModule.jobs for more details. 어떤 직업의 스킬 메커니즘을 새롭게 구현하고 싶다면, `dpmModule.character.characterKernel.JobGenerator` 를 상속받은 후 
    비어있는 함수들을 재작성하십시오. 더 자세한 내용은 dpmModule.jobs 내부의 README를 읽어보십시오.

  - The program includes the basic skill mechanisms of most existing jobs. If you want to use them, you can use them via import.
    For example, if you want to use Nightlord’s skill configuration. 본 프로그램에는 현존하는 대부분의 직업의 기본 스킬 메커니즘이 구현되어 있습니다. 이들을 사용하고 싶다면 import를 통해 사용하면 됩니다.
    예를 들어 나이트로드의 스킬 구성을 사용하고 싶다면
    
    ```python
    import dpmModule.jobs.nightlord as nightlord

    character = ... # Create some character
    gen = nightlord.JobGenerator()
    v_builder = core.NJBStyleVBuilder(skill_core_level=25, each_enhanced_amount=17)
    graph = gen.package(character, v_builder)
    ```

    You can use it with. 와 같이 사용하면 됩니다.

3. Create Scheduler | Scheduler 생성

  - Scheduler is an object that operates the graph created in ```2```. Scheduler may be different depending on its implementation, but
    It usually requires three factors. Scheduler란 ```2``` 에서 생성한 그래프를 작동시키는 오브젝트입니다. Scheduler는 그 구현 방식에 따라 다를 수 있겠지만
    보통 세 가지 요소를 요구합니다.

    - Graph created in ```2```. ```2``` 에서 생성한 Graph.
    - Policy to select elements from graph. Graph에서 요소를 선택할 Policy.
    - Rules that decide whether to use the elements suggested by the policy. Policy가 제안한 요소를 사용할 지 말지 정하는 Rule들.

    Scheduler is not yet available in a variety of ways. The schedulers that are provided by default and recommended for use are as follows. Scheduler는 아직 다양하게 제공되고 있지는 않습니다. 기본적으로 제공되고 있는, 사용이 추천되는 Scheduler는 다음과 같습니다.

    ```python
    sche = policy.AdvancedGraphScheduler(graph,
    policy.TypebaseFetchingPolicy(priority_list = [
        core.BuffSkillWrapper,
        core.SummonSkillWrapper,
        core.DamageSkillWrapper
    ]),  # TypebaseFetchingPolicy allows suggestions in the order appropriate for a given priority_list. That is, under this
    # policy, the buff is used first if the buff can't use it, it will use the pet, if neither can it will use the attack skill.
    # TypebaseFetchingPolicy는 주어진 priority_list에 알맞은 순서로 제안되도록 합니다. 즉, 이 Policy하에서는 버프를 먼저 사용하고,
    # 버프가 사용할 수 없으면 소환수를 사용하고, 둘 다 모두 사용할 수 없으면 공격스킬을 사용할 것입니다.
    [rules.UniquenessRule()])  # Policy only judges whether it is available or not. In real life, buffs are always available, but when they are already on
    # No need to use. UniquenessRule() restricts buffs and summoning skills from being used when they are already in use.
    # Policy는 사용 가능여부만을 판정합니다. 실 상황에서는, 버프는 항상 사용가능하지만 이미 켜져있을 때는
    # 사용할 필요가 없습니다. UniquenessRule()은 버프와 소환 스킬이 이미 사용중일때는 사용되지 않도록 제한합니다.
    ```

    - Please refer to `dpmModule.execution` for rules and policies. Rule과 Policy에 대해서는 `dpmModule.execution`을 찹조하세요.

4. Analytics creation | Analytics 생성

  During the simulation, you create objects to monitor the simulation. It is basically defined in `core.Analytics`.
  If you want to get additional information, just inherit that class. 시뮬레이션이 진행되는 동안 시뮬레이션을 모니터링할 오브젝트를 생성합니다. 기본적으로 `core.Analytics`에 정의되어 있습니다.
  추가적인 정보를 얻고 싶다면 해당 클래스를 상속받으십시오.

  ```python
  analytics = core.Analytics(printFlag=False)
  ```

5. Simulator creation | Simulator 생성

  Create a Simulator object that runs a simulation based on the previously defined objects. 앞에서 정의된 오브젝트들을 기반으로 시뮬레이션을 실행해주는 Simulator 객체를 생성합니다.

  ```python
  control = core.Simulator(scheduler, character, analytics)
  ```

6. Simulation run | 시뮬레이션 실행

  Run the Simulator. Use the built-in function of control or take the output from the way it was defined in analytics. Simulator를 동작시킵니다. 결과물은 control의 내장 함수를 사용하거나 analytics에 정의되었던 방식으로부터 가져오십시오.

  ```python
  control.start_simulation(180*1000) # runtime = 180 * 1000 ms

  data = control.get_results() # raw 시뮬레이션 출력
  meta = control.get_metadata() # 시뮬레이션의 메타데이터
  skill = control.get_skill_info() # 시뮬레이션에 사용된 스킬 정보
  dpm = control.getDPM() # 측정된 DPM(damage per minute)
  unres_dpm = control.get_unrestricted_DPM() # 최대 데미지 제한을 받지 않은 DPM


