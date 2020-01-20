
dpmModule :: Maplestory Damage simulation library
===================================================================


Structure
-------------

  - `kernel` : 추상 클래스, 기본 클래스
  - `character` : 캐릭터 관련 코드. 캐릭터 생성, 캐릭터 스텟, 하이퍼스텟, 유니온, 카드효과, 링크 효과, 사전-정의된 캐릭터 불러오기.
  - `item` : 아이템 관련 코드. 아이템 생성, 여제/카루타/앱솔/아케인/보장/칠흑/마이스터셋.
  - `jobs` : 직업 관련 코드. 직업군별 스킬, 패시브 스킬, 코어 개수, 스킬 메커니즘, 스킬 연계 순서.
  - `execution` : 시뮬레이션 규칙.
  - `status` : 어빌리티
  - `util` : 편의용 코드. 빠른 DPM 계산, 최적 하이퍼/유니온 계산.


Principle
---------------

dpmModule의 계산 과정은 다음과 같습니다.

1. character 생성
  
  - DPM 계산이 수행될 대상 캐릭터를 생성합니다. 캐릭터를 생성하기 위해서는 `dpmModule.character`를 활용할 수 있습니다.
  - Character를 생성하는 방법은 크게 두 가지로 나뉩니다.

    - `dpmModule.character.get_template_generator` 함수를 사용하는 방법
    - `dpmModule.character.ItemedCharacter` 인스턴스를 생성하고 직접 함수를 활용하여 character를 생성하는 방법

  - 더 자세한 내용은 dpmModule.character 내부의 README를 읽어보십시오.

2. Skill Graph 생성

  - Skill graph란 캐릭터가 수행하게 될 일들의 순서와 속성이 정의된 그래프입니다. 그래프에는 
    
    - 쓸 수 있는 스킬들
    - 해당 스킬을 사용했을 때 뒤따라 사용되는 스킬들
    - 서로 겹칠 수 없거나, 스킬 간의 상호작용들

    이 모두 정의되어 있어야 합니다.

  - 스킬 그래프를 scratch로부터 생성하고 싶다면 `dpmModule.character.kernel` 의 README를 읽어보십시오.

  - 어떤 직업의 스킬 메커니즘을 새롭게 구현하고 싶다면, `dpmModule.character.characterKernel.JobGenerator` 를 상속받은 후 
    비어있는 함수들을 재작성하십시오. 더 자세한 내용은 dpmModule.jobs 내부의 README를 읽어보십시오.

  - 본 프로그램에는 현존하는 대부분의 직업의 기본 스킬 메커니즘이 구현되어 있습니다. 이들을 사용하고 싶다면 import를 통해 사용하면 됩니다.
    예를 들어 나이트로드의 스킬 구성을 사용하고 싶다면
    
    ```python
    import dpmModule.jobs.nightlord as nightlord

    character = ... # Create some character
    gen = nightlord.JobGenerator()
    v_builder = core.NJBStyleVBuilder(skill_core_level=25, each_enhanced_amount=17)
    graph = gen.package(character, v_builder)
    ```

    와 같이 사용하면 됩니다.

3. Scheduler 생성

  - Scheduler란 ```2``` 에서 생성한 그래프를 작동시키는 오브젝트입니다. Scheduler는 그 구현 방식에 따라 다를 수 있겠지만
    보통 세 가지 요소를 요구합니다.

    - ```2``` 에서 생성한 Graph
    - Graph에서 요소를 선택할 Policy
    - Policy가 제안한 요소를 사용할 지 말지 정하는 Rule들

    Scheduler는 아직 다양하게 제공되고 있지는 않습니다. 기본적으로 제공되고 있는, 사용이 추천되는 Scheduler는 다음과 같습니다.

    ```python
    sche = policy.AdvancedGraphScheduler(graph,
    policy.TypebaseFetchingPolicy(priority_list = [
        core.BuffSkillWrapper,
        core.SummonSkillWrapper,
        core.DamageSkillWrapper
    ]), # TypebaseFetchingPolicy는 주어진 priority_list에 알맞은 순서로 제안되도록 합니다. 즉, 이 Policy하에서는 버프를 먼저 사용하고,
    # 버프가 사용할 수 없으면 소환수를 사용하고, 둘 다 모두 사용할 수 없으면 공격스킬을 사용할 것입니다.
    [rules.UniquenessRule()]) # Policy는 사용 가능여부만을 판정합니다. 실 상황에서는, 버프는 항상 사용가능하지만 이미 켜져있을 때는
    # 사용할 필요가 없습니다. UniquenessRule()은 버프와 소환 스킬이 이미 사용중일때는 사용되지 않도록 제한합니다.
    ```

    - Rule과 Policy에 대해서는 `dpmModule.execution`을 찹조하세요.

4. Analytics 생성

  시뮬레이션이 진행되는 동안 시뮬레이션을 모니터링할 오브젝트를 생성합니다. 기본적으로 `core.Analytics`에 정의되어 있습니다.
  추가적인 정보를 얻고 싶다면 해당 클래스를 상속받으십시오.

  ```python
  analytics = core.Analytics(printFlag=False)
  ```

5. Simulator 생성

  앞에서 정의된 오브젝트들을 기반으로 시뮬레이션을 실행해주는 Simulator 객체를 생성합니다.

  ```python
  control = core.Simulator(scheduler, character, analytics)
  ```

6. 시뮬레이션 실행

  Simulator를 동작시킵니다. 결과물은 control의 내장 함수를 사용하거나 analytics에 정의되었던 방식으로부터 가져오십시오.

  ```python
  control.start_simulation(180*1000) # runtime = 180 * 1000 ms

  data = control.get_results() # raw 시뮬레이션 출력
  meta = control.get_metadata() # 시뮬레이션의 메타데이터
  skill = control.get_skill_info() # 시뮬레이션에 사용된 스킬 정보
  dpm = control.getDPM() # 측정된 DPM(damage per minute)
  unres_dpm = control.get_unrestricted_DPM() # 최대 데미지 제한을 받지 않은 DPM


