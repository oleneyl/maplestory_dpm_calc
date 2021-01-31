

/kernel
===========


The kernel contains a set of modules needed for a program to actually work. kernel에는 프로그램이 실제로 작동하기 위해 필요한 모듈들이 집합되어 있습니다.
Modules other than kernel are implemented so that dpmModule can be applied to actual situations. kernel을 제외한 다른 module는 dpmModule을 실제 상황에 적용할 수 있도록 구현한 
As for code, the kernel guides you through the basic operation of dpmModule. 코드라면, kernel은 dpmModule의 기본 작동을 안내합니다.

- abstract.py

  - Abstract class required for program operation is defined. 프로그램 작동에 필요한 Abstract class가 정의되어 있습니다.
  
- graph.py

  - The functions required for the internal operation of the simulation graph are defined. 시뮬레이션 그래프의 내부 동작에 필요한 기능이 정의되어 있습니다.
  
- policy.py

  - Classes for controlling simulation operation are defined. 시뮬레이션 작동 제어를 위한 class들이 정의되어 있습니다.

- core

  - This is a sub-module that defines the classes required for Maplestory DPM calculation. Maplestory DPM 계산에 필요한 class들이 정의되어 있는 하위 모듈입니다.
    
    - callback.py: The callback function is defined. 콜백 함수가 정의되어 있습니다.

    - constant.py: The constants such as Mc Dem, Bangmu, halved or final dem are defined. 맥뎀, 방무, 반감여부, 최종뎀 등의 상수가 정의되어 있습니다.

    - graph_element.py: Defined for `GraphElement`. `GraphElement`에 대해 정의되어 있습니다.

    - modifier.py: Defines `CharacterModifier`, `SkillModifier` and other functions that change character specifications. 캐릭터의 스펙을 변경하는 `CharacterModifier`, `SkillModifier`와 기타 기능들이 정의되어 있습니다.

    - result_object.py: A `ResultObject` representing the result of each action is defined. 각 동작의 결과를 나타내는 `ResultObject`가 정의되어 있습니다.

    - simulator.py: DPM calculation simulator and analyzer are defined. DPM 연산 시뮬레이터와 분석기가 정의되어 있습니다.

    - skill.py: Defines `AbstractSkill` and `DamageSkill`, `SummonSkill`, and `BuffSkill` based on it. `AbstractSkill`과 그것을 바탕으로 한 `DamageSkill`, `SummonSkill`, `BuffSkill` 등이 정의되어 있습니다.

    - skill_wrapper.py: Defines `AbstractSkillWrapper`, each skill wrapper based on it, and applied special wrappers. `AbstractSkillWrapper`과 그것을 바탕으로 한 각각 Skill의 wrapper, 그리고 응용된 특수 wrapper들이 정의되어 있습니다.

    - vmatrix.py: Defined for strengthening the V matrix core. V 매트릭스 코어강화에 대해 정의되어 있습니다.


Basic how dpmModule works | dpmModule의 기본 작동 방식
-------------------------

dpmModule is designed to operate in the following order. dpmModule은 다음과 같은 순서로 적동하도록 설계되어 있습니다.

# Define graph builder
# Build graph from builder
# Push graph into scheduler
# Run scheduler by session
# Analyze result from session by analytics

- Graph

  - -`Graph` is defined as the connection of GraphElements that have 0 or more links with direction. `Graph`는 방향을 가지는 link를 0개 이상 가지는 GraphElement들의 연결로서 정의됩니다.
  - `GraphElement` is an operation unit that can perform action in simulation. The following things can be `GraphElement`. `GraphElement` 는 시뮬레이션에서 action을 수행할 수 있는 연산 단위입니다. 다음과 같은 것들이 `GraphElement` 가 될 수 있습니다.
  
    - Specific buff (ex.'Maple Warrior' buff). 특정한 버프(ex. `메이플용사` 버프).
    - Specific skills (ex.'Final Blow' skill). 특정한 스킬(ex. `파이널 블로우` 스킬).
    - Conditions (ex.Check the cooldown of the'Infinity' skill). 조건(ex. `인피니티` 스킬의 쿨타임 확인).
    - Stack, gauge (ex.'Lacness gauge' of'Luminous'). 스택, 게이지(ex. `루미너스` 의 `라크니스 게이지`).
    
- Task
  
  - `Task` means the actual action performed when the simulation is running. The following things can be `Task`. `Task`는 시뮬레이션이 작동할 때 수행되는 실제의 행동을 의미합니다. 다음과 같은 것들이 `Task`가 될 수 있습니다.
  
    - 'Use' of a specific buff (ex.Use of the'Maple Warrior' buff). 특정한 버프의 `사용` (ex. `메이플 용사` 버프의 사용).
    - 'Use' of specific skills (ex. use of'Final Blow' skill). 특정한 스킬의 `사용` (ex. `파이널 블로우` 스킬의 사용).
    - 'Evaluation' of the condition (ex.Check if the'Infinity' skill is available). 조건의 `평가` (ex. `인피니티` 스킬이 사용가능한지 확인).
    - Decrease of stack and gauge (ex.Increase the `Largeness Gauge` of `Luminous` by 100). 스택, 게이지의 감소 (ex. `루미너스` 의 `라크니스게이지` 를 100만큼 증가).
    
  - One `GraphElement` has one representative `Task`. This task can be obtained through `GraphElement.build_task()`. 하나의 `GraphElement` 는 하나의 대표 `Task` 를 가집니다. 이 Task는 `GraphElement.build_task()` 를 통해 얻을 수 있습니다.
  - To say that a GraphElement is `used` means that this representative `Task` is used. 어떤 GraphElement가 `사용` 되었다고 말하는 것은 이 대표 `Task` 가 사용된 것을 의미합니다.

    - The representative task of buff skills is defined as the use of buffs. 버프류 스킬의 대표 Task는 버프의 사용으로 정의되어 있습니다.
    - The representative task of attack skill is defined as the use of attack skill. 공격스킬의 대표 Task는 공격스킬의 사용으로 정의되어 있습니다.
         
  - However, one `GraphElement` can have multiple related `Tasks`. 그러나, 하나의 `GraphElement` 는 여러개의 관련된  `Task`를 가질 수 있습니다. 
  
    - You may want to reduce the cooldown of buff skills. 버프 스킬의 쿨타임을 감소시키고 싶을 수 있습니다.
    - You may want to reset the cooldown of the attack skill. 공격 스킬의 쿨타임을 초기화시키고 싶을 수 있습니다.
    
  - To obtain these other tasks, you can use a method defined separately for each GraphElement. 이와 같은 다른 Task들을 얻기 위해서는 개개의 GraphElement에 별도로 정의되어 있는 method를 활용하면 됩니다.
  
- Graph Element Cascading

  - When running a simulation, there are actions that must be followed after certain actions. 시뮬레이션을 진행할 때, 특정한 행동 뒤에 반드시 뒤따라야 하는 행동들이 존재합니다.
  
    - Final Attack Skills: Must be activated immediately after the attack skill is activated. 파이널 어택류 스킬 : 공격 스킬이 발동된 직후 반드시 발동해야 합니다.
    - Stack type skill: After the skill is used, the stack must be changed. 스택형 스킬 : 스킬이 사용된 후 스택을 변화시켜야 합니다.
    - Linked skill: You must always use another skill after the skill is activated. 연계형 스킬 : 스킬이 발동된 후 다른 스킬을 항상 사용해야 합니다.
    
  - After a specific GraphElement is used, several functions are supported to allow other GraphElements to be used. About GraphElement `origin`. 특정 GraphElement 가 사용된 이후, 다른 GraphElement가 사용되도록 하기 위해서 몇 가지 함수들이 지원됩니다. GraphElement `origin` 에 대해.
    
    - origin.onAfter(target: GraphElement): target is used immediately after origin is used. origin.onAfter(target : GraphElement) : origin이 사용된 직후 target이 사용됩니다.
    - origin.onBefore(target: GraphElement): The target is used just before origin is not used. origin.onBefore(target : GraphElement) : origin이 사용되지 직전 target이 사용됩니다.
    - origin.onTick(target: GraphElement): If origin is activated periodically, the target is used immediately after the periodic activation. origin.onTick(target : GraphElement) : origin이 주기적으로 발동되는 경우, 주기적 발동 직후 target이 사용됩니다.
  
- Logical and utility Graph Elements

  - The simulation conditions are not static. Each condition changes with each simulation run. 시뮬레이션의 조건은 정적이지 않습니다. 각각의 조건은 매 시뮬레이션이 진행될 때마다 변화합니다.
  
     - Remaining cooldown of all skills. 모든 스킬의 남은 쿨타임.
     - Gauge-type skill gauge. 게이지형 스킬의 게이지.
     
  - The creator of the simulation may wish to add logical elements for an optimized simulation. For this, this library supports `OptionalElement`. 시뮬레이션의 제작자는 최적화된 시뮬레이션을 위해 논리적 요소를 추가하고자 할 수 있습니다. 이를 위해 본 라이브러리는 `OptionalElement` 를 지원합니다.
  
    - OptionalElement(disc : function, after : GraphElement, fail = None : GraphElement, name = "Optional Element" : string)
      
      - When this element is used, the disc function is executed, and if it is True, it uses after, and if it is False, it uses fail if it exists. 본 요소가 사용될 때, disc 함수가 실행되어 True이면 after를 사용하고, False인 경우 fail이 있다면 fail을 사용합니다.
      
  - In addition to this, several convenience elements are supported for the convenience of simulation production. 이 외에도 시뮬레이션 제작의 편의성을 위해 여러 편의 요소를 지원합니다.
    
    - RepeatElement : It is used when you want to use a specific element repeatedly. 특정 요소를 반복적으로 사용하고자 할 때 사용합니다.
    - TaskHolder : It is simply a GraphElement for wrapping a specific task. 단순히 특정 Task를 Wrapping하기 위한 GraphElement입니다.
    

- An example of actual Graph Element Cascading is provided below. 아래에 실제 Graph Element Cascading의 예시가 제공되어 있습니다.

  - Final Attack is activated after Dark Knight's Dark Impale is used. 다크나이트의 다크 임페일이 사용된 이후에는 파이널 어택이 발동합니다.
  
    ```python
    DarkImpail.onAfter(FinalAttack)
    ```

  - The Dark Knight's attacks are twofold. If Sacrifice is on, it uses Goongnil, otherwise it uses Impale. 다크나이트의 공격은 두 가지 입니다. 새크리파이스가 켜져 있다면 궁그닐을, 그렇지 않다면 임페일을 사용합니다.

    ```python
    def InfGoungnil():
        return (Sacrifice.is_active() or Reincarnation.is_active()) # Determines whether Sacrifice is turned on or not. Sacrifice가 켜져 있는지 아닌지 판별합니다.
    
    BasicAttack = core.OptionalElement(InfGoungnil, GoungnilDescentNoCooltime, DarkImpail) # If it is on, it uses Goongnil, otherwise it uses Impale. 켜져 있다면 궁그닐을, 아니라면 임페일을 사용합니다.
    ```
    
  - The cooldown of Dark Knight's Sacrifice skill decreases by 0.3 seconds when non-holder skills are used. 다크나이트의 새크리파이스 스킬의 쿨타임은 비홀더 계열 스킬이 사용될 경우 0.3초씩 감소합니다.
  
    ```python
    # SkillWrapper.controller(time, type) returns a GraphElement that changes the duration or cooldown of the target skill. SkillWrapper.controller(time, type)은 대상 스킬의 지속시간 또는 쿨타임을 변화시키는 GraphElement를 리턴합니다.
    # Therefore, Sacrifice.controller(300,'reduce_cooltime') is a GraphElement that reduces the cooldown of Sacrifice by 0.3 seconds when used. 따라서 Sacrifice.controller(300,'reduce_cooltime') 는 사용시 Sacrifice의 쿨타임을 0.3초 감소시키는 GraphElement입니다.
    
    BiholderDominant.onTick(Sacrifice.controller(300,'reduce_cooltime'))
    BiholderShock.onAfter(Sacrifice.controller(300,'reduce_cooltime'))
    BiholderImpact.onTick(Sacrifice.controller(300,'reduce_cooltime'))
    ```
    
- Graph can be created as a collection of GraphElements. Graph is created like this: Graph는 GraphElement들을 모음으로서 생성할 수 있습니다. Graph는 다음과 같이 생성됩니다.

  - First, define the graph elements. 먼저 그래프 요소들을 정의합니다.
  
    ```python
    from dpmModule.kernel.core import GraphElement 
    x = GraphElement('X')
    y = GraphElement('Y')
    z = GraphElement('Z')
    x.onAfter(x)
    ```
    
  - To define the graph, you need three things. 그래프를 정의하기 위해서는 세 가지가 필요합니다. 
    
    - `Executable graph element`. These can be used directly by the Simulator when the simulation is running (X, Y). `실행가능한 그래프 요소`. 이들은 시뮬레이션이 진행될 때 직접적으로 Simulator가 사용할 수 있습니다(X, Y).
    - `Non-executable graph element`. These cannot be used directly, but there are moments when they are used indirectly. such as onAfter. It is connected to'executable graph elements' through method (Z). `실행불가능한 그래프 요소`. 이들은 직접적으로 사용할 수는 없으나, 간접적으로 사용되는 순간이 존재합니다. onAfter과 같은. method를 통해 `실행가능한 그래프 요소` 들과 연결되어 있습니다.(Z).
    - `Default Graph Element` This element is the element that the simulation will use by default when there are no other available elements (X). `기본 그래프 요소` 이 요소는 시뮬레이션이 아무런 다른 사용가능한 요소가 없을 때 default로 사용할 요소입니다(X).
    
    - In order to get all existing graph elements, the graph elements created so far are imported. 현재 존재하는 모든 그래프 요소를 가져오기 위해, 현재까지 생성된 그래프 요소들을 가져옵니다.
      
      ```python
      from dpmModule.kernel.graph import GlobalOperation
      storage = GlobalOperation.export_storage_without_complex_option()
      ```
      
  - Finally, we put all three of these values together to create a graph. 마지막으로, 이 세 값을 모두 모아 그래프를 생성합니다.
  
    ```python
    from dpmModule.kernel.policy import StorageLinkedGraph
    graph = StorageLinkedGraph(X, storage, accessible_elements=[X, Y])
    ```
    
- Two things are needed to operate the created graph. 생성된 그래프를 동작시키기 위해서는 두 가지가 필요합니다.

  - A `Policy` that sets the priority to use `GraphElement`. `GraphElement`가 사용될 우선순위를 정하는 `Policy`.
  - A `Rule` that determines whether the `GraphElement` is available within the priority. 우선순위 내에서 해당 `GraphElement`가 사용가능한지를 판별하는 `Rule`.
  
  - Policy can be defined by inheriting `dpmModule.kernel.graph.FetchingPolicy`. Policy는 `dpmModule.kernel.graph.FetchingPolicy`를 상속하여 정의할 수 있습니다.
  - Basically, we support TypebaseFetchingPolicy, which determines the priority according to the properties of GraphElement. 기본적으로 GraphElement의 속성에 따라서 우선순위를 정하는 TypebaseFetchingPolicy를 지원합니다.
  - If you want to use the buff first, increase your pet, and adopt a policy that uses attack skills, proceed as follows. 버프를 먼저 사용하고, 소환수를 키고, 공격스킬을 사용하는 Policy를 채택하고자 할 경우 다음과 같이 진행합니다.
  
    ```python
    from dpmModule.kernel.policy import TypebaseFetchingPolicy
    from dpmModule.kernel import core
    my_policy = TypebaseFetchingPolicy(priority_list = [
        core.BuffSkillWrapper,
        core.SummonSkillWrapper,
        core.DamageSkillWrapper
    ])
    ```
    
  - Rule can be defined by inheriting `dpmModule.kernel.graph.AbstractRule`. Rule은 `dpmModule.kernel.graph.AbstractRule` 을 상속하여 정의할 수 있습니다.
  - Basically, some useful rules are defined in `dpmModule.execution.rules`. 기본적으로 `dpmModule.execution.rules`에 몇 가지 유용한 Rule이 정의되어 있습니다.
  
    - `UniquenessRule` : This is the most basic and essential rule. If the given element is on, use is prohibited. 제일 기본적이고 필수적인 Rule입니다. 주어진 Element가 on 상태이면 사용을 금지합니다.
    
    - `ConcurrentRunRule` : For both GraphElements A and B, force A to use only when B is in use. This is useful when you want to use extreme deals together. 두 GraphElement A,B에 대해, A가 B가 사용중일 때만 사용하도록록 강제합니다. 극딜기를 함께 사용하도록 할 때 유용합니다.
    
    - `ReservationRule` : For both GraphElements A and B, force B to use only when A is available. This is useful when you want to use extreme deals together. 두 GraphElement A,B에 대해, B가 A가 사용가능할 때만 사용하도록록 강제합니다. 극딜기를 함께 사용하도록 할 때 유용합니다.
    
    - `MutualRule` : For two GraphElements A and B, it forces them not to be used together. 두 GraphElement A,B에 대해, 둘이 함께 사용될 수 없도록 강제합니다.
    
    - In addition to this, there are various rules. 이 외에도 다양한 Rule이 있습니다.
    - If you do not want to use any rule, only `UniquenessRule` is applied. 아무런 Rule도 사용하려 하지 않을 경우 `UniquenessRule`만 적용합니다.
    
  - If Rule and Policy are defined, you can create Scheduler. Scheduler presents the next task to be used based on the given rule and policy. Rule과 Policy가 정의되었다면, Scheduler를 생성할 수 있습니다. Scheduler는 주어진 Rule과 Policy를 바탕으로, 다음에 사용되어야 할 Task를 제시합니다.
  
    ```python
    from dpmModule.kernel.policy import AdvancedGraphScheduler
    scheduler = AdvancedGraphScheduler(graph, fetching_policy=policy, rules=rules)
    ```
    
- Finally, it is the stage of the simulation. Simulation can be done through the Simulator object. 마지막으로, 시뮬레이션을 진행하는 단계입니다. 시뮬레이션은 Simulator 객체를 통해 진행할 수 있습니다. Simulator는 
  - After receiving the next task to be executed from the scheduler, Scheduler로부터 다음에 실행될 Task를 받아온 후,
  - Run the task, Task를 실행하고,
  - Spend time as much as the delay defined in the task. Task에 정의되어 있는 delay만큼 시간을 spend하며.
  - The results are saved and analyzed until the end of the simulation. 그 결과를 시뮬레이션 종료 전까지 저장, 분석합니다.
  
  - Analytics is responsible for the analysis of the simulation. Example code is as follows: 시뮬레이션의 분석은 Analytics가 담당하고 있습니다. 예시 코드는 다음과 같습니다.
  
  ```python
  from dpmModule.kernel import core
  
  analytics = core.Analytics()  # Create an analyzer to analyze the data. 데이터를 분석할 분석기를 생성합니다.
  control = core.Simulator(scheduler, character, analytics) # Connect and create schedulers, characters, and analytics to the simulator. 시뮬레이터에 스케줄러, 캐릭터, 애널리틱을 연결하고 생성합니다.
  # The character has not yet been covered in the text. This is because the Simulator is an object defined only for DPM calculations. 캐릭터에 대해서는 본문에서는 아직 다루지 않았습니다. 이는 Simulator가 DPM 계산만을 위해 정의된 객체이기 때문입니다.
  control.start_simulation(3600*1000) # 1 hours. 1시간.
  ```