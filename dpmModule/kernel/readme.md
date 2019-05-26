

/kernel
===========


kernel에는 프로그램이 실제로 작동하기 위해 필요한 모듈들이 집합되어 있습니다.
kernel을 제외한 다른 module는 dpmModule을 실제 상황에 적용할 수 있도록 구현한 
코드라면, kernel은 dpmModule의 기본 작동을 안내합니다.


dpmModule의 기본 작동 방식
-------------------------

dpmModule은 다음과 같은 순서로 적동하도록 설계되어 있습니다.

# Define graph builder
# Build graph from builder
# Push graph into scheduler
# Run scheduler by session
# Analyze result from session by analytics

- Graph
  - Graph는 방향을 가지는 link를 0개 이상 가지는 GraphElement들의 연결로서 정의됩니다.



- Graph building seqeunce

  - 먼저 GraphElement를 생성하는 과정에 대해 알아봅니다. GraphElement는 다음과 같은 과정을 거쳐 생성됩니다.
     
    대부분의 GraphElement는 다음과 같은 과정을 거치는 것이 추천됩니다. 일반적인 그래프요소 대신 다음을 사용하는 것이 권장됩니다.

    - TrackableGraphElement() 를 사용합니다.

    
    - GraphElementPrecursor()를 먼저 생성합니다.
    - GraphElementPrecursor.transfer_into_real()을 호출하여 실제 그래프 요소로 빌드 타임에 전환됩니다.

    GraphElementPrecursor는 