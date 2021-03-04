
dpmModule :: Maplestory Damage simulation library
===================================================================


Structure
-------------

  - `kernel` : Abstract class, base class. 
  - `character` : Character related code. Character creation, character stats, hyper stats, legion, card effect, link skills, pre-defined character loading. 
  - `item` : Item related code. Item creation, Empress / CRA / Absolab / Arcane / Guarantee / Jet Black / Meister set. 
  - `jobs` : Job-related code. Skill by job group, passive skill, number of cores, skill mechanisms, skill linkage order. 
  - `execution` : Simulation rules. 시뮬레이션 규칙.
  - `status` : Ability. 어빌리티.
  - `util` : Utility code. Fast DPM calculation, optimal hyper/legion calculation. 
  - `test` : Test. 테스트.


Principle
---------------

The calculation process of dpmModule is as follows.

1. character creation 
  
  - Create a target character for the DPM calculation to be performed on. To create a character, you can use `dpmModule.character`. 
  - There are two main ways to create a character. 

    - How to use `dpmModule.character.get_template_generator` function. 
    - How to create a `dpmModule.character.ItemedCharacter` instance and directly utilize a function to create a character. 

  - Please read the README inside dpmModule.character for more details. 

2. Create Skill Graph

  - Skill graph is a graph that defines the order and properties of the tasks the character will perform. On the graph: 
    
    - Skills you can use.
    - Skills that are used after the skill is used. 
    - Interactions between skills or cannot overlap each other. 

    All of these should be defined.

  - If you want to create a skill graph from scratch, read the README of `dpmModule.character.kernel`. 

  - If you want to newly implement the skill mechanism of a certain job, after inheriting `dpmModule.character.characterKernel.JobGenerator`
    Rewrite empty functions. Read the README inside dpmModule.jobs for more details.

  - The program includes the basic skill mechanisms of most existing jobs. If you want to use them, you can use them via import.
    For example, if you want to use Nightlord’s skill configuration. 
    
    ```python
    import dpmModule.jobs.nightlord as nightlord

    character = ... # Create some character
    gen = nightlord.JobGenerator()
    v_builder = core.NJBStyleVBuilder(skill_core_level=25, each_enhanced_amount=17)
    graph = gen.package(character, v_builder)
    ```

    You can use it with. 

3. Create Scheduler

  - Scheduler is an object that operates the graph created in ```2```. Scheduler may be different depending on its implementation, but
    It usually requires three factors.

    - Graph created in ```2```. 
    - Policy to select elements from graph. 
    - Rules that decide whether to use the elements suggested by the policy. 

    Scheduler is not yet available in a variety of ways. The schedulers that are provided by default and recommended for use are as follows. 

    ```python
    sche = policy.AdvancedGraphScheduler(graph,
    policy.TypebaseFetchingPolicy(priority_list = [
        core.BuffSkillWrapper,
        core.SummonSkillWrapper,
        core.DamageSkillWrapper
    ]),  # TypebaseFetchingPolicy allows suggestions in the order appropriate for a given priority_list. That is, under this
    # policy, the buff is used first if the buff can't use it, it will use the pet, if neither can it will use the attack skill.
    [rules.UniquenessRule()])  # Policy only judges whether it is available or not. In real life, buffs are always available, but when they are already on
    # No need to use. UniquenessRule() restricts buffs and summoning skills from being used when they are already in use.
    ```

    - Please refer to `dpmModule.execution` for rules and policies. 

4. Analytics creation

  During the simulation, you create objects to monitor the simulation. It is basically defined in `core.Analytics`.
  If you want to get additional information, just inherit that class. 

  ```python
  analytics = core.Analytics(printFlag=False)
  ```

5. Simulator creation

  Create a Simulator object that runs a simulation based on the previously defined objects. 

  ```python
  control = core.Simulator(scheduler, character, analytics)
  ```

6. Simulation run

  Run the Simulator. Use the built-in function of control or take the output from the way it was defined in analytics. 

  ```python
  control.start_simulation(180*1000) # runtime = 180 * 1000 ms

  data = control.get_results() # raw 시뮬레이션 출력
  meta = control.get_metadata() # 시뮬레이션의 메타데이터
  skill = control.get_skill_info() # 시뮬레이션에 사용된 스킬 정보
  dpm = control.getDPM() # 측정된 DPM(damage per minute)
  unres_dpm = control.get_unrestricted_DPM() # 최대 데미지 제한을 받지 않은 DPM


