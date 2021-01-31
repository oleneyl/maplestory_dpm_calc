jobs.py
======================


- In jobs.py, there is a graph that defines the skill composition and skill mechanism of real jobs. jobs.py에는 실제 직업들의 스킬 구성과 스킬 메커니즘을 정의한 그래프가 구현되어 있습니다.


Organization of files | 파일의 구성
-----------------------------------

- Within the code, the mechanism by which each job is counted is defined. 코드 내에는 각 직업이 계산되는 메커니즘이 정의되어 있습니다.
- In the `generate` function in the code file. 코드 파일 내의 `generate` 함수 내에.
- The code in the `generate` function is structured as follows. `generate` 함수 내의 코드는 다음과 같이 구성되어 있습니다.

  - `Comment`: This is a description of the setting implicitly applied to the code. `주석` : 코드에 묵시적으로 적용되고 있는 설정에 대한 설명입니다.
  - `Skill Definition`: The values ​​required for skill use are hard-coded. In actual calculation, the calculation is performed based on the corresponding value. `스킬 정의` : 스킬 사용에 필요한 값이 하드 코딩되어 있습니다. 실제 계산시에 해당 값을 기반으로 계산이 진행됩니다.
  - `Graph Composition`: When the `Skill Definition` area is over, the connection relationship of each skill is defined. `그래프 구성` : `스킬 정의` 영역이 끝나면, 각 스킬의 연결관계를 정의합니다.
  - `return`: Returns a list of skills that can be used directly. `return` : 직접적으로 사용할 수 있는 스킬들의 리스트를 리턴합니다.

- Passive skills and their effects are defined in the `get_passive_skill_list` function. `get_passive_skill_list` 함수 내에는 패시브 스킬과 그 효과가 정의되어 있습니다.
- In the `get_not_implied_skill_list` function, the effects applied at the time of battle and the weapon constant / skill level are defined. `get_not_implied_skill_list` 함수 내에는 전투 시점에서 적용되는 효과들과 무기상수 / 숙련도가 정의되어 있습니다.
- In the `get_ruleset` function, rules for optimizing DPM calculations are written. `get_ruleset` 함수 내에는 DPM 계산 최적화를 위한 규칙이 작성되어 있습니다.
- Special values ​​necessary for calculating job performance are defined in the `apply_complex_option` function. `apply_complex_option` 함수 내에는 직업 성능 계산을 위해 필요한 특수 값들이 정의되어 있습니다.

Writing your own JobGenerator | 나만의 JobGenerator 작성하기
------------------------------------------------------------
  - ```warning
    This guide is not yet complete. Rather than creating a new JobGenerator, it is recommended to change the job file that already exists.
    If you want to make it yourself, ask for an issue when there is a blockage.
    이 안내서는 아직 완벽하지 않습니다. 새로운 JobGenerator를 제작하기보다는 이미 존재하는 직업 파일을 변경하는 것을 추천합니다.
    직접 만들고 싶다면, 막히는 점이 있을때 issue로 물어보십시오.
    ```

  - For simulation, you need to create a graph made of GraphElements. GraphElement consists of: 시뮬레이션을 위해서는 GraphElement들로 이루어진 그래프를 만들어야 합니다. GraphElement는 다음과 같이 구성됩니다.

    - time - A variable containing the dependency. This value is updated at every simulation step. dependency를 담고 있는 변수. 매 시뮬레이션 스텝마다 이 값이 갱신됩니다.
    - buildTask() function. Define what happens when that graph element is executed. buildTask() 함수. 해당 그래프 요소가 실행될 때 일어나는 일을 정의합니다.
    - A controller function that can change its own state. Each graph element changes the state of each other through a controller. 자신의 state를 변경할 수 있는 controller 함수. controller를 통해 각 그래프 요소들이 서로의 상태를 변경합니다.
  
  - Examples of GraphElements are as follows. See kernel.core for more details. GraphElement들의 예시는 다음과 같습니다. 보다 자세한 내용은 kernel.core를 참조하십시오.

    - `공격스킬` (Attack Skill)
    - `버프스킬` (Buff Skill)
    - `소환스킬` (Summon Skill)
    - `도트 데미지` (Dot Damage)
    - `조건` (condition)
    - `반복` (Repeat)
    - `제한` (Limit)

- Each GraphElement can be connected to other GraphElements through the following functions. 각 GraphElement들은 아래와 같은 함수를 통해 다른 GraphElement들과 연결될 수 있습니다.

    - By calling the onAfter() and onAfters() functions, you can define the actions to follow after the corresponding GraphElement has been performed. onAfter(), onAfters() 함수의 호출을 통해 해당 GraphElement가 수행된 후에 따라올 작업을 정의할 수 있습니다.
      
      - For example, a final attack is always triggered after Storm's Poetry. So you need a syntax like this: 예를 들어, 폭풍의 시 이후에는 항상 파이널 어택이 발동합니다. 따라서 다음과 같은 구문이 필요합니다.
        
        ```python
        ArrowOfStorm.onAfter(AdvancedFinalAttack)
        ```

    - Calls to the onBefore() and onBefores() functions allow you to define what happens before the corresponding GraphElement is performed. onBefore(), onBefores() 함수의 호출을 통해 해당 GraphElement가 수행되기 전에 수행될 작업을 정의할 수 있습니다.

    - By calling the onTick() function, you can make that GraphElement be called at a specific cycle. onTick() 함수의 호출을 통해 해당 GraphElement가 특정 주기로 호출되도록 할 수 있습니다.

      - For example, Ignite triggers after Ifrit's attack. This is not the point of eprit's `summons`, so it should be assigned to `onTick`, not `onAfter`. 예를 들어, 이프리트의 공격 이후에는 이그나이트가 발동됩니다. 이것은 이프리트의 `소환` 시점이 아니기 때문에 `onAfter` 가 아닌 `onTick` 에 할당해야 합니다.

        ```python 
        Ifritt.onTick(Ignite)
        ```
    - Other Users-You can define actions to be performed after a specific Task of the GraphElement through a defined function call. 그밖의 사용자 - 정의된 함수 호출을 통해 해당 GraphElement의 특정 Task 이후에 수행될 작업을 정의할 수 있습니다.

    - Note: Objects connected to GraphElement must *must* be GraphElement This is essential to maintain the overall maintainence of the program. 주의 : GraphElement와 연결된 객체는 *반드시* GraphElement여야 합니다. 이는 프로그램의 전체적인 maintainence를 유지하기 위해서 필수적입니다.


- When the connection relationship of GraphElements is defined, you can build the Task Graph by calling the buildGraph() function. GraphElement들의 연결관계가 정의되면, buildGraph() 함수의 호출을 통해 Task Graph를 Build 할 수 있습니다.

- The build of the Task Graph proceeds through the following process. Task Graph의 build는 다음과 같은 과정을 통해 진행됩니다.

  - Initially, we pass the starting targets as arguments. BuildTask() of the started target GraphElements received is called. 처음에 인자로 개시 대상들을 넘겨줍니다. 넘겨받은 개시 대상 GraphElement들의 buildTask()가 호출됩니다.
  - The buildTask() function creates a Task object that contains a function that defines the task to be done by itself. buildTask() 함수는 자기 자신이 해야할 작업을 정의한 함수를 담고 있는 Task 오브젝트를 생성합니다.
  - After that, by calling buildTask() of graphs connected to GraphElement through onAfter(), onBefore(), etc., the task obtained through their buildTask() is properly linked with the own task. 이후, onAfter(), onBefore() 등을 통해 GraphElement와 연결되어있는 Graph들의 buildTask()를 호출하여 그들의 buildTask()를 통해 얻은 Task를 자신의 Task와 올바르게 연계합니다.
  - This is done recursively, and when there are no more GraphElements connected (i.e. when all traversals have reached the endpoint of the Graph), it completes and returns the resulting Task. 이와 같은 작업은 재귀적으로 진행되며, 더이상의 연결된 GraphElement가 없을 경우(즉, 모든 탐색이 Graph의 종결점에 도달했을 때) 완료되며 얻어진 Task를 리턴합니다.
  - Through such a task, you can get a unique graph and an individual task. 이와 같은 작업을 통해, Unique한 Graph와 Individual한 Task를 얻을 수 있습니다.

- To make it easier for users to understand the connection relationship of Graph, this program supports the built-in function of GraphElements, getLink(). Graph의 연결관계를 사용자가 보다 쉽게 파악하기 위해서, 본 프로그램은 GraphElement들의 내장된 함수인 getLink() 함수를 지원합니다.
  When the getLink() function is called, it returns a list of [self, connected GraphElement, connection type]. By calling the getLink() function recursively, you can find out the network of all GraphElements connected to a specific GraphElement. getLink() 함수를 호출하면, [자기 자신, 연결된 GraphElement, 연결형식] 의 리스트를 리턴합니다. getLink() 함수를 재귀적으로 호출함으로서, 특정 GraphElement와 연결된 모든 GraphElement들의 네트워크를 파악할 수 있습니다. 

- Link can have the following properties: You can see which element is connected through the Link property. Link는 다음과 같은 속성을 가질 수 있습니다. Link의 속성을 통해 어떤 요소가 연결되어 있는지 확인할 수 있습니다.
  
  - `before`
  - `after`
  - `effect`
  - `repeat`
  - `check`
  - `tick`


- generate

  - For practical graph building, the jobs package utilizes characterKernel.JobGenerator. 실질적인 그래프 빌드를 위해서, jobs 패키지는 characterKernel.JobGenerator 를 활용합니다.
    characterKernel.JobGenerator is a builder that builds graph settings based on character properties. In addition, the builder holds the properties of the built graph, and can use them to call the properties of the built graph. characterKernel.JobGenerator는 캐릭터 속성을 기반으로 하여 그래프 설정을 빌드해 주는 빌더입니다. 또한 빌더는 빌드된 그래프의 속성을 홀드하고 있으며, 이를 활용하여 빌드된 그래프의 속성을 불러올 수 있습니다.

  - jobGenerator holds the following properties. jobGenerator는 아래와 같은 속성을 홀드합니다.

    - `buffrem` : The duration of the buff. 버프 지속시간입니다. 
    - `jobtype` : This is the core stat. 핵심 스텟입니다.
    - `vEhc` : It is an object that contains the 5th skill enhancement information. 5차스킬 강화정보를 담고있는 오브젝트 입니다.
    - `SkillNum` : The number of 5th skills to use. 사용하는 5차 스킬의 개수입니다.
    - `vEnhanceNum` : This is the number of possible 5th enhancement skills. 가능한 5차 강화스킬의 가짓수입니다.
    - `passiveSkillList` : This is a list of passive skill effects. It doesn't count until generate. 패시브 스킬 효과를 담고 있는 리스트 입니다. generate 전까지는 계산되지 않습니다.

Other files | 기타 파일
-----------------------

In addition to the job code, there are `globalSkill.py` and `jobutils.py` in the jobs module. jobs 모듈 내에는 직업 코드 이외에도 `globalSkill.py`와 `jobutils.py`가 존재합니다.

- `globalSkill.py` : Includes common skills used by several professions. 여러 직업군이 사용하는 공용 스킬을 포함합니다.
  - Maple Warrior | 메이플 용사
  - Soul Contract | 소울 컨트랙트
  - Common 5th skill (useful skill, Spider in Mirror, Maple World Goddess' blessing, etc.) | 공용 5차 스킬 (쓸만한 스킬, 스파이더 인 미러, 메이플월드 여신의 축복 등)
  - Genesis weapon skill | 제네시스 무기 스킬
- `jobutils.py` : Contains special logic required for some classes. 일부 직업에 필요한 특수 로직을 포함하고 있습니다.
  - Skill replication | 스킬 복제
  - Weapon attack power | 무기 공격력
  - Debug | 디버그

There are `jobbranch` and `jobclass` as submodules of jobs. Here, common skills for each class and class are stored. jobs의 하위 모듈로는 `jobbranch`와 `jobclass`가 존재합니다. 여기에는 각각 직업 계열과 직업군별 공용 스킬이 저장되어 있습니다.

Skills that are used only by a specific class and class are included in the class code. 특정 직업 계열 및 직업군만 사용하는 스킬들은 직업군 코드에 포함되어 있습니다.

The skills of a single class are implemented in the script for that class. (Zero, Kinesis, Hoyoung). 단일 직업군의 스킬은 해당 직업의 스크립트에 구현되어 있습니다. (제로, 키네시스, 호영).

- The jobbranch module includes: jobbranch 모듈은 다음을 포함합니다.
  - `warriors.py` : This is a common skill for warriors. 전사 공용 스킬입니다.
  - `magicians.py` : This is a common skill for wizards. 마법사 공용 스킬입니다.
  - `bowmen.py` : This is a common archer skill. 궁수 공용 스킬입니다.
  - `thieves.py` : This is a common skill for thieves. (Excluding Venom Burst). 도적 공용 스킬입니다. (베놈 버스트 제외).
  - `pirates.py` : This is a common skill for pirates. 해적 공용 스킬입니다.
- The jobclass module contains: jobclass 모듈은 다음을 포함합니다.
  - `adventurer.py` : This is a common skill for adventurers. 모험가 공용 스킬입니다.
  - `cygnus.py` : This is a common skill for the Knights of Cygnus. 시그너스 기사단 공용 스킬입니다.
  - `heroes.py` : This is a common skill for heroes. 영웅 공용 스킬입니다.
  - `resistance.py` : Resistance (excluding daemons) is a common skill. 레지스탕스(데몬 제외) 공용 스킬입니다.
  - `demon.py` : Demon common skill. 데몬 공용 스킬입니다.
  - `nova.py` : Nova common skill. 노바 공용 스킬입니다.
  - `flora.py` : This is a common skill for Lef. 레프 공용 스킬입니다.
