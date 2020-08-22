

/kernel
===========


kernel에는 프로그램이 실제로 작동하기 위해 필요한 모듈들이 집합되어 있습니다.
kernel을 제외한 다른 module는 dpmModule을 실제 상황에 적용할 수 있도록 구현한 
코드라면, kernel은 dpmModule의 기본 작동을 안내합니다.

- abstract.py

  - 프로그램 작동에 필요한 Abstract class가 정의되어 있습니다.
  
- graph.py

  - 시뮬레이션 그래프의 내부 동작에 필요한 기능이 정의되어 있습니다.
  
- core.py

  - Maplestory DPM 계산에 필요한 class들이 정의되어 있습니다.
  
- policy.py

  - 시뮬레이션 작동 제어를 위한 class들이 정의되어 있습니다.


dpmModule의 기본 작동 방식
-------------------------

dpmModule은 다음과 같은 순서로 적동하도록 설계되어 있습니다.

# Define graph builder
# Build graph from builder
# Push graph into scheduler
# Run scheduler by session
# Analyze result from session by analytics

- Graph

  - `Graph`는 방향을 가지는 link를 0개 이상 가지는 GraphElement들의 연결로서 정의됩니다.
  - `GraphElement` 는 시뮬레이션에서 action을 수행할 수 있는 연산 단위입니다. 다음과 같은 것들이 `GraphElement` 가 될 수 있습니다.
  
    - 특정한 버프(ex. `메이플용사` 버프)
    - 특정한 스킬(ex. `파이널 블로우` 스킬)
    - 조건(ex. `인피니티` 스킬의 쿨타임 확인)
    - 스택, 게이지(ex. `루미너스` 의 `라크니스 게이지`)
    
- Task
  
  - `Task`는 시뮬레이션이 작동할 때 수행되는 실제의 행동을 의미합니다. 다음과 같은 것들이 `Task`가 될 수 있습니다.
  
    - 특정한 버프의 `사용` (ex. `메이플 용사` 버프의 사용)
    - 특정한 스킬의 `사용` (ex. `파이널 블로우` 스킬의 사용)
    - 조건의 `평가` (ex. `인피니티` 스킬이 사용가능한지 확인)
    - 스택, 게이지의 감소 (ex. `루미너스` 의 `라크니스게이지` 를 100만큼 증가)
    
  - 하나의 `GraphElement` 는 하나의 대표 `Task` 를 가집니다. 이 Task는 `GraphElement.build_task()` 를 통해 얻을 수 있습니다.
  - 어떤 GraphElement가 `사용` 되었다고 말하는 것은 이 대표 `Task` 가 사용된 것을 의미합니다.

    - 버프류 스킬의 대표 Task는 버프의 사용으로 정의되어 있습니다.
    - 공격스킬의 대표 Task는 공격스킬의 사용으로 정의되어 있습니다.
         
  - 그러나, 하나의 `GraphElement` 는 여러개의 관련된  `Task`를 가질 수 있습니다. 
  
    - 버프 스킬의 쿨타임을 감소시키고 싶을 수 있습니다.
    - 공격 스킬의 쿨타임을 초기화시키고 싶을 수 있습니다.
    
  - 이와 같은 다른 Task들을 얻기 위해서는 개개의 GraphElement에 별도로 정의되어 있는 method를 활용하면 됩니다.
  
- Graph Element Cascading

  - 시뮬레이션을 진행할 때, 특정한 행동 뒤에 반드시 뒤따라야 하는 행동들이 존재합니다.
  
    - 파이널 어택류 스킬 : 공격 스킬이 발동된 직후 반드시 발동해야 합니다.
    - 스택형 스킬 : 스킬이 사용된 후 스택을 변화시켜야 합니다.
    - 연계형 스킬 : 스킬이 발동된 후 다른 스킬을 항상 사용해야 합니다.
    
  - 특정 GraphElement 가 사용된 이후, 다른 GraphElement가 사용되도록 하기 위해서 몇 가지 함수들이 지원됩니다. GraphElement `origin` 에 대해
    
    - origin.onAfter(target : GraphElement) : origin이 사용된 직후 target이 사용됩니다.
    - origin.onBefore(target : GraphElement) : origin이 사용되지 직전 target이 사용됩니다.
    - origin.onTick(target : GraphElement) : origin이 주기적으로 발동되는 경우, 주기적 발동 직후 target이 사용됩니다.
  
- Logical and utility Graph Elements

  - 시뮬레이션의 조건은 정적이지 않습니다. 각각의 조건은 매 시뮬레이션이 진행될 때마다 변화합니다.
  
     - 모든 스킬의 남은 쿨타임
     - 게이지형 스킬의 게이지
     
  - 시뮬레이션의 제작자는 최적화된 시뮬레이션을 위해 논리적 요소를 추가하고자 할 수 있습니다. 이를 위해 본 라이브러리는 `OptionalElement`
  를 지원합니다.
  
    - OptionalElement(disc : function, after : GraphElement, fail = None : GraphElement, name = "Optional Element" : string)
      
      - 본 요소가 사용될 때, disc 함수가 실행되어 True이면 after를 사용하고, False인 경우 fail이 있다면 fail을 사용합니다.
      
  - 이 외에도 시뮬레이션 제작의 편의성을 위해 여러 편의 요소를 지원합니다.
    
    - RepeatElement : 특정 요소를 반복적으로 사용하고자 할 때 사용합니다.
    - TaskHolder : 단순히 특정 Task를 Wrapping하기 위한 GraphElement입니다.
    

- 아래에 실제 Graph Element Cascading의 예시가 제공되어 있습니다.

  - 다크나이트의 다크 임페일이 사용된 이후에는 파이널 어택이 발동합니다.
  
    ```python
    DarkImpail.onAfter(FinalAttack)
    ```

  - 다크나이트의 공격은 두 가지 입니다. 새크리파이스가 켜져 있다면 궁그닐을, 그렇지 않다면 임페일을 사용합니다.

    ```python
    def InfGoungnil():
        return (Sacrifice.is_active() or Reincarnation.is_active()) # Sacrifice가 켜져 있는지 아닌지 판별합니다.
    
    BasicAttack = core.OptionalElement(InfGoungnil, GoungnilDescentNoCooltime, DarkImpail) # 켜져 있다면 궁그닐을, 아니라면 임페일을 사용합니다.
    ```
    
  - 다크나이트의 새크리파이스 스킬의 쿨타임은 비홀더 계열 스킬이 사용될 경우 0.3초씩 감소합니다.
  
    ```python
    # SkillWrapper.controller(time, type)은 대상 스킬의 지속시간 또는 쿨타임을 변화시키는 GraphElement를 리턴합니다.
    # 따라서 Sacrifice.controller(300,'reduce_cooltime') 는 사용시 Sacrifice의 쿨타임을 0.3초 감소시키는 GraphElement입니다.
    
    BiholderDominant.onTick(Sacrifice.controller(300,'reduce_cooltime'))
    BiholderShock.onAfter(Sacrifice.controller(300,'reduce_cooltime'))
    BiholderImpact.onTick(Sacrifice.controller(300,'reduce_cooltime'))
    ```
    
- Graph는 GraphElement들을 모음으로서 생성할 수 있습니다. Graph는 다음과 같이 생성됩니다.

  - 먼저 그래프 요소들을 정의합니다.
  
    ```python
    from dpmModule.kernel.core import GraphElement 
    x = GraphElement('X')
    y = GraphElement('Y')
    z = GraphElement('Z')
    x.onAfter(x)
    ```
    
  - 그래프를 정의하기 위해서는 세 가지가 필요합니다. 
    
    - `실행가능한 그래프 요소`. 이들은 시뮬레이션이 진행될 때 직접적으로 Simulator가 사용할 수 있습니다(X, Y)
    - `실행불가능한 그래프 요소`. 이들은 직접적으로 사용할 수는 없으나, 간접적으로 사용되는 순간이 존재합니다. onAfter과 같은
    method를 통해 `실행가능한 그래프 요소` 들과 연결되어 있습니다.(Z)
    - `기본 그래프 요소` 이 요소는 시뮬레이션이 아무런 다른 사용가능한 요소가 없을 때 default로 사용할 요소입니다(X).
    
    - 현재 존재하는 모든 그래프 요소를 가져오기 위해, 현재까지 생성된 그래프 요소들을 가져옵니다.
      
      ```python
      from dpmModule.kernel.graph import GlobalOperation
      storage = GlobalOperation.export_storage_without_complex_option()
      ```
      
  - 마지막으로, 이 세 값을 모두 모아 그래프를 생성합니다.
  
    ```python
    from dpmModule.kernel.policy import StorageLinkedGraph
    graph = StorageLinkedGraph(X, storage, accessible_elements=[X, Y])
    ```
    
- 생성된 그래프를 동작시키기 위해서는 두 가지가 필요합니다.

  - `GraphElement`가 사용될 우선순위를 정하는 `Policy`
  - 우선순위 내에서 해당 `GraphElement`가 사용가능한지를 판별하는 `Rule`
  
  - Policy는 `dpmModule.kernel.graph.FetchingPolicy`를 상속하여 정의할 수 있습니다.
  - 기본적으로 GraphElement의 속성에 따라서 우선순위를 정하는 TypebaseFetchingPolicy를 지원합니다.
  - 버프를 먼저 사용하고, 소환수를 키고, 공격스킬을 사용하는 Policy를 채택하고자 할 경우 다음과 같이 진행합니다.
  
    ```python
    from dpmModule.kernel.policy import TypebaseFetchingPolicy
    from dpmModule.kernel import core
    my_policy = TypebaseFetchingPolicy(priority_list = [
        core.BuffSkillWrapper,
        core.SummonSkillWrapper,
        core.DamageSkillWrapper
    ])
    ```
    
  - Rule은 `dpmModule.kernel.graph.AbstractRule` 을 상속하여 정의할 수 있습니다.
  - 기본적으로 `dpmModule.execution.rules`에 몇 가지 유용한 Rule이 정의되어 있습니다.
  
    - `UniquenessRule` : 제일 기본적이고 필수적인 Rule입니다. 주어진 Element가 on 상태이면 사용을 금지합니다.
    
    - `ConcurrentRunRule` : 두 GraphElement A,B에 대해, A가 B가 사용중일 때만 사용하도록록 강제합니다. 극딜기를 함께 사용하도록
    할 때 유용합니다.
    
    - `ReservationRule` : 두 GraphElement A,B에 대해, B가 A가 사용가능할 때만 사용하도록록 강제합니다. 극딜기를 함께 사용하도록
    할 때 유용합니다.
    
    - `MutualRule` : 두 GraphElement A,B에 대해, 둘이 함께 사용될 수 없도록 강제합니다.
    
    - 이 외에도 다양한 Rule이 있습니다.
    - 아무런 Rule도 사용하려 하지 않을 경우 `UniquenessRule`만 적용합니다.
    
  - Rule과 Policy가 정의되었다면, Scheduler를 생성할 수 있습니다. Scheduler는 주어진 Rule과 Policy를 바탕으로, 다음에 사용되어야 할
  Task를 제시합니다.
  
    ```python
    from dpmModule.kernel.policy import AdvancedGraphScheduler
    scheduler = AdvancedGraphScheduler(graph, fetching_policy=policy, rules=rules)
    ```
    
- 마지막으로, 시뮬레이션을 진행하는 단계입니다. 시뮬레이션은 Simulator 객체를 통해 진행할 수 있습니다. Simulator는 
  - Scheduler로부터 다음에 실행될 Task를 받아온 후,
  - Task를 실행하고,
  - Task에 정의되어 있는 delay만큼 시간을 spend하며
  - 그 결과를 시뮬레이션 종료 전까지 저장, 분석합니다.
  
  - 시뮬레이션의 분석은 Analytics가 담당하고 있습니다. 예시 코드는 다음과 같습니다.
  
  ```python
  from dpmModule.kernel import core
  
  analytics = core.Analytics()  #데이터를 분석할 분석기를 생성합니다.
  control = core.Simulator(scheduler, character, analytics) #시뮬레이터에 스케줄러, 캐릭터, 애널리틱을 연결하고 생성합니다.
  # 캐릭터에 대해서는 본문에서는 아직 다루지 않았습니다. 이는 Simulator가 DPM 계산만을 위해 정의된 객체이기 때문입니다.
  control.start_simulation(3600*1000) # 1시간
  ```