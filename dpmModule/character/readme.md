Job generating Code

직업을 시뮬레이션하기 위해서 우리는 class JobGenerator를 활용합니다. Jobgenerator는 다음과 같은 과정을 통해 직업을 생성합니다.

기본적으로 generator는 SimluationGraph를 리턴하는것이 목적입니다.

JobGenerator.package OR .package_bare (chtr : ck.Character, vEhc : jt.VEnhancer, kwargs)
* package는 직업 시뮬레이션에 관련된 정보를 연산하기 위해서 호출되는 함수입니다. 
* package는 직업 그래프를 생성하고, 직업이 기본적으로 가지고 있는 성능을 적용하고, 하이퍼/유니온 스펙을 최적화하는 등
* 부차적인 모든 작업을 자동으로 수행합니다.

|
---------|
         JobGenerator.build( chtr )
         * build 함수는 오로지 그래프만을 생성하는것이 목적입니다.
         * build 함수는 내부적으로는 generate()를 호출하는것과 큰 차이가 없습니다.
         |
         -------|
                JobGenerator.generate(chtr, vEhc, kwargs)
                * generate에서는 실제로 jt.ScheduleGraph()를 생성하고, 내부 함수를 이용하여 Graph를 빌드하여 리턴합니다.
         |------|
         |
|--------|

return : ScheduleGraph



실제 DPM을 연산하는 과정

실제 DPM을 계산하는 방법은 다음과 같습니다.
1. 캐릭터를 생성합니다. ck.Character 또는 ck.ItemedCharacter 를 사용합니다.
2. 캐릭터에 아이템과 같은 최적화 - 불가능한 설정값을 적용합니다. 복잡한 설정값을 단순화하기 위해
   ct.UxxxxTemplate와 같은 template code를 지원합니다. template에 직업을 대입하면 손쉽게 직업에 알맞은
   스펙을 가진 캐릭터를 생성할 수 있습니다.
3. 캐릭터를 생성했다면, 직업에 알맞는 JobGenerator를 가져옵니다. jobs.__init__에 구현되어 있는 Map을 
   활용합니다.
4. 생성된 캐릭터와 VEnhancer를 JobGenerator.package 또는 package_bare 에 인자로 넘겨 그래프를 얻습니다.
5. 그래프를 작동시키기 위한 jt.Simulator, jt.Scheduler, jt.Analytics 를 생성하고 Simulator 연결합니다.
6. Sim.startSimulation()을 통해 시뮬레이션을 시작합니다.


- Simulator의 내부 구조
  
  - Simulator ---- character
                |- analytics
                |- scheduler  --
                               |- graph

  Simulator는 매 작동마다 scheduler로부터 다음 Task를 받아옵니다. scheduler는 내장하고 있는 graph로부터 다음에 실행되어야 하는 Task를 체크하여 리턴합니다.
  Task를 실행하면 ResultObject가 리턴됩니다. ResultObject와 character의 정보를 analytics에 넘기면 analytics에서 해당 정보로부터 필요한 값을 추출하여 저장하고, 나중에 출력합니다.
         