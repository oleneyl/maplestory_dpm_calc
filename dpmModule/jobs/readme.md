jobs.py
======================


- jobs.py에는 실제 직업들의 스킬 구성과 스킬 메커니즘을 정의한 그래프가 구현되어 있습니다.


파일의 구성
-------------

- 코드 내에는 각 직업이 계산되는 메커니즘이 정의되어 있습니다.
- 코드 파일 내의 `generate` 함수 내에 
- `generate` 함수 내의 코드는 다음과 같이 구성되어 있습니다.

  - `주석` : 코드에 묵시적으로 적용되고 있는 설정에 대한 설명입니다.
  - `스킬 정의` : 스킬 사용에 필요한 값이 하드 코딩되어 있습니다. 실제 계산시에 해당 값을 기반으로 계산이 진행됩니다.
  - `그래프 구성` : `스킬 정의` 영역이 끝나면, 각 스킬의 연결관계를 정의합니다.
  - `return` : 직접적으로 사용할 수 있는 스킬들의 리스트를 리턴합니다.

- `get_passive_skill_list` 함수 내에는 패시브 스킬과 그 효과가 정의되어 있습니다.
- `get_not_implied_skill_list` 함수 내에는 전투 시점에서 적용되는 효과들과 무기상수 / 숙련도가 정의되어 있습니다.
- `get_ruleset` 함수 내에는 DPM 계산 최적화를 위한 규칙이 작성되어 있습니다.
- `apply_complex_option` 함수 내에는 직업 성능 계산을 위해 필요한 특수 값들이 정의되어 있습니다.

나만의 JobGenerator 작성하기
--------------
  - ```warning
    이 안내서는 아직 완벽하지 않습니다. 새로운 JobGenerator를 제작하기보다는 이미 존재하는 직업 파일을 변경하는 것을 추천합니다.
    직접 만들고 싶다면, 막히는 점이 있을때 issue로 물어보십시오.
    ```

  - 시뮬레이션을 위해서는 GraphElement들로 이루어진 그래프를 만들어야 합니다. GraphElement는 다음과 같이 구성됩니다.

    - time - dependency를 담고 있는 변수. 매 시뮬레이션 스텝마다 이 값이 갱신됩니다.
    - buildTask() 함수. 해당 그래프 요소가 실행될 때 일어나는 일을 정의합니다.
    - 자신의 state를 변경할 수 있는 controller 함수. controller를 통해 각 그래프 요소들이 서로의 상태를 변경합니다.
  
  - GraphElement들의 예시는 다음과 같습니다. 보다 자세한 내용은 kernel.core를 참조하십시오.

    - `공격스킬`
    - `버프스킬`
    - `소환스킬`
    - `도트 데미지`
    - `조건`
    - `반복`
    - `제한`

- 각 GraphElement들은 아래와 같은 함수를 통해 다른 GraphElement들과 연결될 수 있습니다.

    - onAfter(), onAfters() 함수의 호출을 통해 해당 GraphElement가 수행된 후에 따라올 작업을 정의할 수 있습니다.
      
      - 예를 들어, 폭풍의 시 이후에는 항상 파이널 어택이 발동합니다. 따라서 다음과 같은 구문이 필요합니다.
        
        ```python
        ArrowOfStorm.onAfter(AdvancedFinalAttack)
        ```

    - onBefore(), onBefores() 함수의 호출을 통해 해당 GraphElement가 수행되기 전에 수행될 작업을 정의할 수 있습니다.

    - onTick() 함수의 호출을 통해 해당 GraphElement가 특정 주기로 호출되도록 할 수 있습니다.

      - 예를 들어, 이프리트의 공격 이후에는 이그나이트가 발동됩니다. 이것은 이프리트의 `소환` 시점이 아니기 때문에 `onAfter` 가 아닌 `onTick` 에 할당해야 합니다.

        ```python 
        Ifritt.onTick(Ignite)
        ```
    - 그밖의 사용자 - 정의된 함수 호출을 통해 해당 GraphElement의 특정 Task 이후에 수행될 작업을 정의할 수 있습니다.

    - 주의 : GraphElement와 연결된 객체는 *반드시* GraphElement여야 합니다. 이는 프로그램의 전체적인 maintainence를 유지하기 위해서 필수적입니다.


- GraphElement들의 연결관계가 정의되면, buildGraph() 함수의 호출을 통해 Task Graph를 Build 할 수 있습니다.

- Task Graph의 build는 다음과 같은 과정을 통해 진행됩니다.

  - 처음에 인자로 개시 대상들을 넘겨줍니다. 넘겨받은 개시 대상 GraphElement들의 buildTask()가 호출됩니다.
  - buildTask() 함수는 자기 자신이 해야할 작업을 정의한 함수를 담고 있는 Task 오브젝트를 생성합니다.
  - 이후, onAfter(), onBefore() 등을 통해 GraphElement와 연결되어있는 Graph들의 buildTask()를 호출하여 
    그들의 buildTask()를 통해 얻은 Task를 자신의 Task와 올바르게 연계합니다.
  - 이와 같은 작업은 재귀적으로 진행되며, 더이상의 연결된 GraphElement가 없을 경우(즉, 모든 탐색이 Graph의 종결점에 도달했을 때) 완료되며
    얻어진 Task를 리턴합니다.
  - 이와 같은 작업을 통해, Unique한 Graph와 Individual한 Task를 얻을 수 있습니다.

- Graph의 연결관계를 사용자가 보다 쉽게 파악하기 위해서, 본 프로그램은 GraphElement들의 내장된 함수인 getLink() 함수를 지원합니다.
  getLink() 함수를 호출하면, [자기 자신, 연결된 GraphElement, 연결형식] 의 리스트를 리턴합니다. getLink() 함수를 재귀적으로 호출함으로서, 특정 GraphElement와 연결된 모든 GraphElement들의 네트워크를 파악할 수 있습니다. 

- Link는 다음과 같은 속성을 가질 수 있습니다. Link의 속성을 통해 어떤 요소가 연결되어 있는지 확인할 수 있습니다.
  
  - `before`
  - `after`
  - `effect`
  - `repeat`
  - `check`
  - `tick`


- generate

  - 실질적인 그래프 빌드를 위해서, jobs 패키지는 characterKernel.JobGenerator 를 활용합니다.
    characterKernel.JobGenerator는 캐릭터 속성을 기반으로 하여 그래프 설정을 빌드해 주는 빌더입니다. 또한 빌더는 빌드된 그래프의 속성을 홀드하고 있으며, 이를 활용하여 빌드된 그래프의 속성을 불러올 수 있습니다.

  - jobGenerator는 아래와 같은 속성을 홀드합니다.

    - `buffrem` : 버프 지속시간입니다. 
    - `jobtype` : 핵심 스텟입니다.
    - `vEhc` : 5차스킬 강화정보를 담고있는 오브젝트 입니다.
    - `SkillNum` : 사용하는 5차 스킬의 개수입니다.
    - `vEnhanceNum` : 가능한 5차 강화스킬의 가짓수입니다.
    - `passiveSkillList` : 패시브 스킬 효과를 담고 있는 리스트 입니다. generate 전까지는 계산되지 않습니다.