이 모듈은 특정 직업의 스킬 정보와 스킬 작동 메커니즘 등을 정의합니다.
시뮬레이션 파트에서 제일 핵심적인 부분이라고 할 수 있겠습니다.

시뮬레이션을 위해서는 GraphElement들로 이루어진 그래프를 만들어야 합니다. GraphElement는 다음과 같이 구성됩니다.
- time - dependency를 담고 있는 변수
- buildTask() 함수
- 자신의 state를 변경할 수 있는 controller 함수

각 GraphElement들은 아래와 같은 함수를 통해 다른 GraphElement들과 연결될 수 있습니다.

- onAfter(), onAfters() 함수의 호출을 통해 해당 GraphElement가 수행된 후에 따라올 작업을 정의할 수 있습니다.
- onBefore(), onBefores() 함수의 호출을 통해 해당 GraphElement가 수행되기 전에 수행될 작업을 정의할 수 있습니다.
- onTick()이나 그밖의 사용자 - 정의된 함수 호출을 통해 해당 GraphElement의 특정 Task 이후에 수행될 작업을 정의할 수 있습니다.
- 주의 : GraphElement와 연결된 객체는 *반드시* GraphElement여야 합니다. 이는 프로그램의 전체적인 maintainence를 유지하기 위해서 필수적입니다.

GraphElement들의 연결관계가 정의되면, buildGraph() 함수의 호출을 통해 Task Graph를 Build 할 수 있습니다.
Task Graph의 build는 다음과 같은 과정을 통해 진행됩니다.

- 처음에 인자로 개시 대상들을 넘겨줍니다. 넘겨받은 개시 대상 GraphElement들의 buildTask()가 호출됩니다.
- buildTask() 함수는 자기 자신이 해야할 작업을 정의한 함수를 담고 있는 Task 오브젝트를 생성합니다.
- 이후, onAfter(), onBefore() 등을 통해 GraphElement와 연결되어있는 Graph들의 buildTask()를 호출하여 
  그들의 buildTask()를 통해 얻은 Task를 자신의 Task와 올바르게 연계합니다.
- 이와 같은 작업은 재귀적으로 진행되며, 더이상의 연결된 GraphElement가 없을 경우(즉, 모든 탐색이 Graph의 종결점에 도달했을 때) 완료되며
  얻어진 Task를 리턴합니다.
- 이와 같은 작업을 통해, Unique한 Graph와 Individual한 Task를 얻을 수 있습니다.

Graph의 연결관계를 사용자가 보다 쉽게 파악하기 위해서, 본 프로그램은 GraphElement들의 내장된 함수인 getLink() 함수를 지원합니다.
getLink() 함수를 호출하면, [자기 자신, 연결된 GraphElement, 연결형식] 의 리스트를 리턴합니다. getLink() 함수를 재귀적으로 호출함으로서, 특정 GraphElement
와 연결된 모든 GraphElement들의 네트워크를 파악할 수 있습니다. 

Link는 다음과 같은 속성을 가질 수 있습니다.
"before" : 
"after" : 
"effect" : 
"repeat" :
"check" : constraint
"tick"

* generate *

실질적인 그래프 빌드를 위해서, jobs 패키지는 characterKernel.JobGenerator 를 활용합니다.
characterKernel.JobGenerator는 캐릭터 속성을 기반으로 하여 그래프 설정을 빌드해 주는 빌더입니다. 또한 빌더는 빌드된 그래프의 속성을 홀드하고 있으며, 이를 활용하여 빌드된 그래프의 속성을 불러올 수 있습니다.
jobGenerator는 아래와 같은 속성을 홀드합니다.

.buffrem : 버프 지속시간입니다. 
.jobtype : 핵심 스텟입니다.
.vEhc : 5차스킬 강화정보를 담고있는 오브젝트 입니다.
.vSkillNum : 사용하는 5차 스킬의 개수입니다.
.vEnhanceNum : 가능한 5차 강화스킬의 가짓수입니다.
.passiveSkillList : 패시브 스킬 효과를 담고 있는 리스트 입니다. generate 전까지는 계산되지 않습니다.

* wrapper 속성 *

- BuffSkillWrapper
  
  - modifierInvariantFlag : 리턴하는 modifier가 불변함을 증명합니다. 연산 caching에 활용됩니다.


- buildPassiveSkillList : 패시브 스킬들을 빌드합니다.
- generate : 그래프를 작성합니다. 이 함수는 재작성될 수 있습니다.
- build : 그래프에 관련된 모든 잔작업을 처리합니다. build는 재작성되어서는 안됩니다.


